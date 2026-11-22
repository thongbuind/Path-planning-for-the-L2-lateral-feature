import http.client
import json
import sys
import threading
import time
from pathlib import Path

import pytest

from workbench import evidence
from workbench import server as W

FAKE = [sys.executable, str(Path(__file__).with_name("fake_worker.py"))]


@pytest.fixture
def api(tmp_path):
    W.Handler.app = W.App(tmp_path / "runs", 2, worker=FAKE,
                          catalog=[sys.executable, "-c", "print('{\"scenarios\": []}')"])
    srv = W.Server(("127.0.0.1", 0), W.Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    port = srv.server_port

    def call(method, path, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
        data = json.dumps(body).encode() if body is not None else None
        conn.request(method, path, data, {"Content-Type": "application/json", **(headers or {})})
        resp = conn.getresponse()
        raw = resp.read()
        conn.close()
        return resp.status, (json.loads(raw) if raw and resp.getheader("Content-Type", "").startswith("application/json") else raw)

    call.port = port
    yield call
    W.Handler.app.supervisor.shutdown(2.0)
    srv.shutdown()
    srv.server_close()


def wait_done(call, run_id, timeout=10.0):
    end = time.time() + timeout
    while time.time() < end:
        status, body = call("GET", f"/api/runs/{run_id}")
        state = body.get("state") or body.get("execution", {}).get("state")
        if state in ("COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT"):
            return body
        time.sleep(0.05)
    raise AssertionError(f"{run_id} not finished")


def test_run_survives_a_closed_tab_and_reconnect_resumes(api):
    status, body = api("POST", "/api/runs", {"config": {"mode": "slow", "n": 30}})
    assert status == 201
    run_id = body["run_id"]
    conn = http.client.HTTPConnection("127.0.0.1", api.port, timeout=10)
    conn.request("GET", f"/api/runs/{run_id}/events?from=0")
    resp = conn.getresponse()
    first = json.loads(resp.readline())
    conn.close()
    assert first["seq"] == 1
    done = wait_done(api, run_id)
    assert done["execution"]["state"] == "COMPLETED" and done["execution"]["complete"]
    status, raw = api("GET", f"/api/runs/{run_id}/events?from=3")
    seqs = [json.loads(x)["seq"] for x in raw.decode().splitlines() if x.strip()]
    assert seqs and seqs[0] == 4 and seqs == list(range(4, 4 + len(seqs)))


def test_cancel_and_list(api):
    _, a = api("POST", "/api/runs", {"config": {"mode": "slow", "n": 300}})
    _, b = api("POST", "/api/runs", {"config": {"mode": "ok"}})
    time.sleep(0.3)
    status, body = api("POST", f"/api/runs/{a['run_id']}/cancel", {})
    assert status == 200
    assert wait_done(api, a["run_id"])["execution"]["state"] == "CANCELLED"
    assert wait_done(api, b["run_id"])["execution"]["state"] == "COMPLETED"
    _, listing = api("GET", "/api/runs")
    assert {a["run_id"], b["run_id"]} <= {r["run_id"] for r in listing["runs"]}


def test_idempotency_key(api):
    _, a = api("POST", "/api/runs", {"config": {"mode": "ok"}}, {"Idempotency-Key": "abc"})
    _, b = api("POST", "/api/runs", {"config": {"mode": "ok"}}, {"Idempotency-Key": "abc"})
    assert a == b
    wait_done(api, a["run_id"])


def _reopen(api, config):
    _, first = api("POST", "/api/runs", {"config": config})
    wait_done(api, first["run_id"])
    status, again = api("POST", f"/api/runs/{first['run_id']}/rerun", {})
    assert status == 201
    done = wait_done(api, again["run_id"])
    assert done["execution"]["parent_run_id"] == first["run_id"]
    return done["rerun"]


def test_rerun_with_the_same_behaviour_matches(api):
    check = _reopen(api, {"mode": "ok"})
    assert check["match"] is True and check["reasons"] == []


def test_rerun_with_another_behaviour_is_reported(api):
    check = _reopen(api, {"mode": "ok", "drift": True})
    assert check["match"] is False and check["actual"]["behavior_checksum"] == "other"
    assert check["reasons"]


def test_rerun_needs_an_identity(api):
    _, body = api("POST", "/api/runs", {"config": {"mode": "eval_error"}})
    wait_done(api, body["run_id"])
    assert api("POST", f"/api/runs/{body['run_id']}/rerun", {})[0] == 409
    assert api("POST", "/api/runs/20990101-000000-abcdef/rerun", {})[0] == 404


def test_rerun_of_a_suite_case_uses_its_frozen_file(tmp_path, monkeypatch):
    monkeypatch.setattr(evidence, "ROOT", tmp_path)
    monkeypatch.setattr(evidence, "BENCH", tmp_path / "build" / "benchmark")
    run = tmp_path / "build" / "benchmark" / "run-1"
    (run / "suite").mkdir(parents=True)
    (run / "concrete" / "cases").mkdir(parents=True)
    (run / "concrete" / "cases" / "S1-a.xosc").write_text("<x/>")
    (run / "concrete" / "manifest.json").write_text(json.dumps(
        {"cases": [{"id": "S1-a", "file": "cases/S1-a.xosc", "planner_only": "lcc"}]}))
    (run / "suite" / "manifest.json").write_text(json.dumps(
        {"libraries": [{"pp_version": "a", "sha256": "1"}, {"pp_version": "b", "sha256": "2"}], "git": {"commit": "c"}}))
    (run / "suite" / "results.jsonl").write_text(
        json.dumps({"case": "S1-a", "seed": 2, "case_hash": "x", "behavior_checksum": "y"}) + "\n")
    request = evidence.suite_rerun_request("run-1", "S1-a", 2)
    assert request["recipe"] == {"kind": "file", "path": "build/benchmark/run-1/concrete/cases/S1-a.xosc"}
    assert request["seed"] == 2 and request["planner_only"] == "lcc"
    assert request["expect"]["behavior_checksum"] == "y" and len(request["expect"]["libraries"]) == 2
    with pytest.raises(KeyError):
        evidence.suite_rerun_request("run-1", "S1-a", 3)


def test_case_not_judged_is_neither_pass_nor_fail(tmp_path):
    (tmp_path / "execution.json").write_text("{}")
    (tmp_path / "manifest.json").write_text("{}")
    (tmp_path / "evaluation.json").write_text(json.dumps(
        {"passed": None, "criteria": [{"id": "A", "applicable": True, "passed": True}]}))
    assert evidence.run_summary(tmp_path)["verdict"] == "not_judged"


def test_foreign_origin_is_refused(api):
    status, _ = api("POST", "/api/runs", {"config": {"mode": "ok"}}, {"Origin": "http://evil.example"})
    assert status == 403


def test_files_and_static_are_whitelisted(api):
    _, body = api("POST", "/api/runs", {"config": {"mode": "ok"}})
    wait_done(api, body["run_id"])
    status, data = api("GET", f"/api/runs/{body['run_id']}/files/execution.json")
    assert status == 200 and data["complete"]
    assert api("GET", f"/api/runs/{body['run_id']}/files/supervisor.json")[0] == 404
    assert api("GET", "/api/runs/20990101-000000-abcdef")[0] == 404
    assert api("GET", "/index.html")[0] == 200
    assert api("GET", "/server.py")[0] == 404
    assert api("GET", "/api/catalog") == (200, {"scenarios": []})

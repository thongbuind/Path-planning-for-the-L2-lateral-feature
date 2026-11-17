"""Workbench HTTP API over a fake worker (no planner): SIM-REQ-003, 004, 010, 105."""

import http.client
import json
import sys
import threading
import time
from pathlib import Path

import pytest

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
    conn.close()  # the tab closes
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

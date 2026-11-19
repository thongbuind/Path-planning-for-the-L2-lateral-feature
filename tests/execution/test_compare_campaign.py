"""Comparison of two suite runs or campaigns, and campaigns of the workbench, over a fake worker
(no planner): SIM-REQ-091 to 096."""

import http.client
import json
import sys
import threading
import time
from pathlib import Path

import pytest

from workbench import campaign, compare, evidence
from workbench import server as W

FAKE = [sys.executable, str(Path(__file__).with_name("fake_worker.py"))]
TERMINAL = ("COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT")


@pytest.fixture
def api(tmp_path):
    W.Handler.app = W.App(tmp_path / "runs", 2, worker=FAKE,
                          catalog=[sys.executable, "-c", "print('{\"scenarios\": []}')"])
    srv = W.Server(("127.0.0.1", 0), W.Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    def call(method, path, body=None):
        conn = http.client.HTTPConnection("127.0.0.1", srv.server_port, timeout=10)
        conn.request(method, path, json.dumps(body).encode() if body is not None else None,
                     {"Content-Type": "application/json"})
        resp = conn.getresponse()
        raw = resp.read()
        conn.close()
        return resp.status, (json.loads(raw) if raw and resp.getheader("Content-Type", "").startswith("application/json") else raw)

    call.root = tmp_path
    yield call
    W.Handler.app.supervisor.shutdown(2.0)
    srv.shutdown()
    srv.server_close()


def wait_campaign(call, cid, timeout=20.0):
    end = time.time() + timeout
    while time.time() < end:
        _, body = call("GET", f"/api/campaigns/{cid}")
        if body["state"] == "done":
            return body
        time.sleep(0.05)
    raise AssertionError("campaign not finished")


# ---- campaigns ---------------------------------------------------------------------------

def test_a_matrix_expands_to_its_product_and_is_bounded():
    spec = {"matrix": {"scenarios": [{"sid": "S1", "v": "a"}, {"sid": "S4", "v": "b"}],
                       "fault_sets": [[], [["F04", "a"]]], "vehicles": ["VP-0", "VP-1"], "seeds": [1, 2]}}
    configs = campaign.expand(spec)
    assert len(configs) == 16 and all(c["rate"] == 0 for c in configs)
    assert {c["vehicle"] for c in configs} == {"VP-0", "VP-1"}
    big = {"matrix": {"scenarios": [{"sid": "S1", "v": "a"}], "seeds": list(range(campaign.MAX_RUNS + 1))}}
    with pytest.raises(campaign.CampaignError, match="quá"):
        campaign.expand(big)


@pytest.mark.parametrize("spec", [
    {}, {"items": []}, {"items": ["x"]}, {"matrix": {"scenarios": [{"sid": "x1", "v": "a"}]}},
    {"matrix": {"scenarios": [{"sid": "S1", "v": "a"}], "fault_sets": [[["F4", "a"]]]}},
    {"matrix": {"scenarios": [{"sid": "S1", "v": "a"}], "vehicles": ["car"]}},
    {"matrix": {"scenarios": [{"sid": "S1", "v": "a"}], "seeds": [True]}},
    {"items": [{"mode": "ok"}, {"mode": "ok"}]},
])
def test_a_bad_campaign_is_refused(spec):
    with pytest.raises(campaign.CampaignError):
        campaign.expand(spec)


def test_a_campaign_runs_through_the_one_supervisor_and_reports_each_run(api):
    items = [{"mode": "slow", "n": 8, "k": i} for i in range(5)]
    status, made = api("POST", "/api/campaigns", {"name": "five", "items": items})
    assert status == 201 and made["runs"] == 5
    seen = set()
    end = time.time() + 20
    while time.time() < end:
        _, body = api("GET", f"/api/campaigns/{made['id']}")
        c = body["counts"]
        assert c["running"] <= 2                                      # N_max
        assert c["queued"] + c["running"] + c["completed"] + c["failed"] + c["cancelled"] + c["missing"] == 5
        seen.add(body["state"])
        if body["state"] == "done":
            break
        time.sleep(0.03)
    assert "done" in seen and body["coverage"]["designed"] == 5 and body["coverage"]["scheduled"] == 5
    assert body["counts"]["completed"] == 5 and body["coverage"]["ran"] == 5
    assert body["coverage"]["condition_observed"] is None
    assert {i["state"] for i in body["items"]} == {"COMPLETED"}
    _, listing = api("GET", "/api/campaigns")
    assert [c["id"] for c in listing["campaigns"]] == [made["id"]]


def test_cancelling_a_campaign_leaves_other_runs_alone(api):
    _, outside = api("POST", "/api/runs", {"config": {"mode": "ok"}})
    status, made = api("POST", "/api/campaigns", {"name": "slow", "items": [{"mode": "slow", "n": 400, "k": i} for i in range(4)]})
    assert status == 201
    time.sleep(0.3)
    status, body = api("POST", f"/api/campaigns/{made['id']}/cancel", {})
    assert status == 200 and body["cancelled"] >= 2
    done = wait_campaign(api, made["id"])
    assert done["counts"]["cancelled"] == 4
    end = time.time() + 10
    while time.time() < end:
        state = api("GET", f"/api/runs/{outside['run_id']}")[1]
        if (state.get("state") or state["execution"]["state"]) in TERMINAL:
            break
        time.sleep(0.05)
    assert (state.get("state") or state["execution"]["state"]) == "COMPLETED"


def test_repeat_makes_a_new_campaign_with_the_same_list_and_delete_unpins(api):
    _, made = api("POST", "/api/campaigns", {"name": "a", "items": [{"mode": "ok", "k": 1}, {"mode": "slow", "n": 6, "k": 2}]})
    first = wait_campaign(api, made["id"])
    status, again = api("POST", f"/api/campaigns/{made['id']}/repeat", {})
    assert status == 201 and again["id"] != made["id"]
    second = wait_campaign(api, again["id"])
    assert second["parent_campaign"] == made["id"] and second["name"] == "a (lặp lại)"
    assert {i["run_id"] for i in first["items"]}.isdisjoint({i["run_id"] for i in second["items"]})
    pinned = json.loads((api.root / "runs" / ".pinned.json").read_text())
    assert {i["run_id"] for i in first["items"]} <= set(pinned)       # retention keeps a campaign's runs
    assert api("POST", f"/api/campaigns/{made['id']}/delete", {})[0] == 200
    pinned = json.loads((api.root / "runs" / ".pinned.json").read_text())
    assert not {i["run_id"] for i in first["items"]} & set(pinned)
    assert api("GET", f"/api/campaigns/{made['id']}")[0] == 404


def test_delete_is_refused_while_a_run_is_active(api):
    _, made = api("POST", "/api/campaigns", {"name": "busy", "items": [{"mode": "slow", "n": 400, "k": 1}]})
    time.sleep(0.2)
    assert api("POST", f"/api/campaigns/{made['id']}/delete", {})[0] == 409
    api("POST", f"/api/campaigns/{made['id']}/cancel", {})
    wait_campaign(api, made["id"])


def test_campaign_requests_are_checked(api):
    assert api("POST", "/api/campaigns", {"items": [{"mode": "ok"}]})[0] == 400          # no name
    assert api("POST", "/api/campaigns", {"name": "x", "matrix": {"scenarios": [{"sid": "bad", "v": "a"}]}})[0] == 400
    assert api("GET", "/api/campaigns/20990101-000000-abcdef")[0] == 404
    assert api("POST", "/api/campaigns/20990101-000000-abcdef/cancel", {})[0] == 404


# ---- comparison --------------------------------------------------------------------------

def _suite(root: Path, name: str, records: list[dict], libs=("aaaa", "bbbb"), python="3.13.1", commit="c1", verdict="Không đạt"):
    suite = root / "build" / "benchmark" / name / "suite"
    suite.mkdir(parents=True)
    (suite / "manifest.json").write_text(json.dumps({
        "target": "regression", "finished": "2026-11-18T21:00:00+07:00", "git": {"short": commit, "dirty": False},
        "libraries": [{"pp_version": f"pp {i}", "sha256": s, "build": {"calibration": "cal1"}} for i, s in enumerate(libs)],
        "environment": {"python": python, "numpy": "2.5", "platform": "mac", "machine": "arm64"}, "inputs": {"a": "1"}}))
    (suite / "conclusion.json").write_text(json.dumps({"verdict": verdict, "integrable": True, "runs": len(records),
                                                       "counts": {"BLOCKER": 1, "MAJOR": 0, "MINOR": 0}, "failures": [], "out_of_scope": []}))
    (suite / "summary.json").write_text(json.dumps({"planned": len(records), "verdict": verdict}))
    (suite / "results.jsonl").write_text("\n".join(json.dumps(r) for r in records) + "\n")


def _rec(case, failed=(), oos=(), case_hash="h", checksum="x", values=None, seed=1):
    criteria = [{"id": k, "metric": "m", "value": v[0], "limit": v[1], "passed": False, "applicable": True}
                for k, v in (values or {}).items()]
    return {"case": case, "seed": seed, "failed": list(failed), "failed_out_of_scope": list(oos), "case_hash": case_hash,
            "behavior_checksum": checksum, "result": {"criteria": criteria}}


@pytest.fixture
def suites(tmp_path, monkeypatch):
    monkeypatch.setattr(evidence, "ROOT", tmp_path)
    monkeypatch.setattr(evidence, "BENCH", tmp_path / "build" / "benchmark")
    evidence._cache.clear()
    base = [_rec("S1-a-VP-0-aa", ["PP-SWR-051"], values={"PP-SWR-051": (-0.2, ">= 0")}),                # fixed
            _rec("S1-b-VP-0-bb"),                                                                       # new in cand
            _rec("S4-a-VP-0-cc", ["PP-SWR-094"], values={"PP-SWR-094": (0.15, "<= 0.1")}),              # still, worse
            _rec("S5-a-VP-0-dd", ["PP-SWR-086"], case_hash="old", values={"PP-SWR-086": (-0.5, ">= -0.3")}),
            _rec("S6-a-VP-0-ee", ["PP-SWR-001"], values={"PP-SWR-001": (3.0, "<= 2.5")})]               # only in base
    cand = [_rec("S1-a-VP-0-aa", checksum="y"),
            _rec("S1-b-VP-0-bb", ["PP-SWR-030"], checksum="y", values={"PP-SWR-030": (4.0, "= 0")}),
            _rec("S4-a-VP-0-cc", ["PP-SWR-094"], checksum="y", values={"PP-SWR-094": (0.25, "<= 0.1")}),
            _rec("S5-a-VP-0-dd", ["PP-SWR-086"], case_hash="new", values={"PP-SWR-086": (-0.1, ">= -0.3")}),
            _rec("S7-a-VP-0-ff")]                                                                        # only in cand
    _suite(tmp_path, "base", base)
    _suite(tmp_path, "cand", cand, libs=("aaaa", "cccc"), python="3.13.2", commit="c2")
    return tmp_path


def test_a_suite_comparison_classifies_every_requirement(suites):
    out = compare.compare(compare.load_suite("base"), compare.load_suite("cand"))
    c = out["counts"]
    assert (c["matched"], c["case_changed"], c["only_base"], c["only_cand"]) == (3, 1, 1, 1)
    assert (c["new"], c["fixed"], c["still"]) == (1, 1, 1)
    assert c["behavior_changed"] == 3
    kinds = {r["requirement"]: r["kind"] for r in out["changes"]}
    assert kinds == {"PP-SWR-030": "new", "PP-SWR-094": "still", "PP-SWR-051": "fixed"}
    still = next(r for r in out["changes"] if r["kind"] == "still")
    assert still["base_margin"] == pytest.approx(-0.05) and still["cand_margin"] == pytest.approx(-0.15)
    assert still["delta_margin"] == pytest.approx(-0.10)                  # worse by 10 cm
    assert any("case_hash" in w for w in out["warnings"]) and any("chỉ có ở" in w for w in out["warnings"])
    assert out["case_changed_examples"] == ["S5-a-VP-0-dd seed 1"]
    by_req = {r["id"]: r for r in out["by_requirement"]}
    assert by_req["PP-SWR-030"]["new"] == 1 and by_req["PP-SWR-051"]["fixed"] == 1
    assert {f["id"] for f in out["by_family"]} == {"S1-a", "S1-b", "S4-a"}
    assert next(r for r in out["changes"] if r["kind"] == "new")["key"] == "S1-b-VP-0-bb|1"


def test_the_environments_are_listed_before_the_result(suites):
    out = compare.compare(compare.load_suite("base"), compare.load_suite("cand"))
    diff = {d["key"]: d for d in out["differences"]}
    assert diff["libraries"]["base"] == ["aaaa", "bbbb"] and diff["libraries"]["cand"] == ["aaaa", "cccc"]
    assert diff["commit"]["level"] == "info" and diff["python"]["level"] == "warn"
    assert "target" not in diff and "platform" not in diff
    same = compare.compare(compare.load_suite("base"), compare.load_suite("base"))
    assert same["differences"] == [] and same["counts"]["new"] == same["counts"]["fixed"] == 0


def test_the_compare_api_is_read_only_and_checks_its_input(api, suites):
    status, body = api("GET", "/api/compare?base=suite:base&cand=suite:cand")
    assert status == 200 and body["counts"]["new"] == 1
    assert api("GET", "/api/compare?base=suite:base&cand=suite:nope")[0] == 404
    assert api("GET", "/api/compare?base=base&cand=suite:cand")[0] == 400
    assert api("GET", "/api/compare?base=suite:base&cand=campaign:20990101-000000-abcdef")[0] == 404
    assert api("POST", "/api/compare", {})[0] == 404


def _campaign_runs(root: Path, name: str, rows: list[tuple[dict, list, str]]):
    """A campaign document and its finished bundles: rows of (config, failed criteria ids, behavior checksum)."""
    runs = root / "runs"
    items = []
    for i, (config, failed, checksum) in enumerate(rows):
        rid = f"20261119-10{len(name):02d}{i:02d}-{i:06x}"
        folder = runs / rid
        folder.mkdir(parents=True)
        (folder / "execution.json").write_text(json.dumps({"state": "COMPLETED", "complete": True}))
        crit = [{"id": f, "value": 1.0, "limit": "<= 0.5", "passed": False, "applicable": True} for f in failed]
        (folder / "evaluation.json").write_text(json.dumps({"criteria": crit + [{"id": "PP-SWR-010", "value": 1.0,
                                                            "limit": "= 1", "passed": True, "applicable": True}]}))
        (folder / "manifest.json").write_text(json.dumps({"bundle": {"case_hash": "h", "behavior_checksum": checksum},
                                                          "libraries": [{"pp_version": "p", "sha256": name}]}))
        items.append({"config": config, "label": f"item {i}", "run_id": rid})
    return {"id": f"20261119-1000{len(name):02d}-abcdef", "name": name, "items": items}


def test_two_campaigns_compare_by_configuration(tmp_path):
    c1, c2 = {"scenario": {"sid": "S1", "v": "a"}, "seed": 1, "rate": 0}, {"scenario": {"sid": "S4", "v": "a"}, "seed": 1, "rate": 0}
    base = _campaign_runs(tmp_path, "one", [(c1, ["PP-SWR-051"], "x"), (c2, [], "x")])
    cand = _campaign_runs(tmp_path, "three", [({**c1, "rate": 5}, [], "y"), (c2, ["PP-SWR-094"], "x")])
    out = compare.compare(compare.load_campaign(base, tmp_path / "runs"), compare.load_campaign(cand, tmp_path / "runs"))
    assert out["counts"]["matched"] == 2 and out["counts"]["fixed"] == 1 and out["counts"]["new"] == 1
    assert out["counts"]["behavior_changed"] == 1 and out["counts"]["behavior_same"] == 1       # the pacing is not the identity
    assert out["differences"][0]["key"] == "libraries"


def test_kinds_are_not_mixed(tmp_path, suites):
    camp = _campaign_runs(tmp_path, "one", [({"seed": 1}, [], "x")])
    with pytest.raises(ValueError):
        compare.compare(compare.load_suite("base"), compare.load_campaign(camp, tmp_path / "runs"))


def test_margin_and_family():
    assert compare.margin(0.15, "<= 0.1") == pytest.approx(-0.05)
    assert compare.margin(-0.2, ">= 0") == pytest.approx(-0.2)
    assert compare.margin(3, "= 0") == -3 and compare.margin(0, "= 0") == 0
    assert compare.margin(1, "garbage") is None and compare.margin(None, "<= 1") is None
    assert compare.family("S1b-a-VP-0-693b15015bfa") == "S1b-a"
    assert compare.family("F02-e-S1a-VP-5-29183b65ffaf") == "F02-e"
    assert compare.family("G01-S1c-VP-5-38898514a806") == "G01"

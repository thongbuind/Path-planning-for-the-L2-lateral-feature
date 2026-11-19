"""The live worker (eval.live) under execution.supervisor with stub planner libraries: a complete
bundle, and a planner that crashes in pp_step classified as SUT_EXECUTION (SIM-REQ-006, 020)."""

import json
import os
import sys
import time
from pathlib import Path

from eval import run_bundle
from execution import bundle as B
from execution.supervisor import Settings, Supervisor, TERMINAL
from sim.logging import mcap_writer
from workbench import evidence

ROOT = Path(__file__).resolve().parents[2]
CONFIG = {"scenario": {"sid": "S1", "v": "a"}, "faults": [], "trigger": None, "vehicle": "VP-0", "seed": 1,
          "sim": {}, "acc": None, "rate": 0}


def _wait(sup, run_id):
    end = time.time() + 300
    while time.time() < end:
        status = sup.status(run_id)
        if (status.get("state") or status.get("execution", {}).get("state")) in TERMINAL:
            return sup.s.root / run_id, status
        time.sleep(0.1)
    raise AssertionError("run did not finish")


def _supervisor(tmp_path, library):
    env = dict(os.environ, PP_PLANNER_LIB=str(library), PYTHONDONTWRITEBYTECODE="1")
    return Supervisor(Settings(root=tmp_path / "runs", command=[sys.executable, "-m", "eval.live", "run"],
                               cwd=ROOT, env=env, keep=None, max_bytes=None))


def _run(tmp_path, library):
    sup = _supervisor(tmp_path, library)
    try:
        return _wait(sup, sup.submit({"config": CONFIG}))
    finally:
        sup.shutdown(2.0)


def test_rerun_reproduces_the_checksum_and_stops_on_a_changed_case(tmp_path, build_stub):
    sup = _supervisor(tmp_path, build_stub())
    try:
        folder, _ = _wait(sup, sup.submit({"config": CONFIG}))
        request = evidence.rerun_request(folder)
        again, status = _wait(sup, sup.submit(request, parent=folder.name))
        assert status["execution"]["state"] == "COMPLETED"
        assert evidence.rerun_check(again)["match"] is True

        changed = {**request, "expect": {**request["expect"], "case_hash": "0" * 40}}
        _, status = _wait(sup, sup.submit(changed, parent=folder.name))
        assert status["execution"]["state"] == "FAILED" and status["execution"]["failure"] == "INFRA"
        assert "Ca đã đổi" in status["execution"]["message"]
    finally:
        sup.shutdown(2.0)


def test_complete_bundle_from_the_live_worker(tmp_path, build_stub):
    folder, status = _run(tmp_path, build_stub())
    ex = status["execution"]
    assert ex["state"] == "COMPLETED" and ex["complete"], ex
    assert B.verify(folder) == []
    manifest = status["manifest"]
    assert manifest["run_id"] == folder.name
    assert manifest["bundle"]["case_hash"] == status["resolved-case"]["case_hash"]
    assert manifest["libraries"][0]["pp_version"].startswith("stub_planner ")
    assert manifest["simulator"]["models"] and manifest["simulator"]["checksum_version"].startswith("behavior_checksum/")
    assert (folder / "trace.mcap").is_file() and (folder / "frames.ndjson.gz").is_file()
    # SIM-REQ-028: every listed exception to the sim clock is a field that the trace really has
    domains = manifest["bundle"]["time_domains"]
    assert domains == run_bundle.TIME_DOMAINS and domains["default"] == "sim"
    assert set(domains["exceptions"].values()) <= set(domains["domains"])
    found = set()
    for topic, _, message in mcap_writer.read(folder / "trace.mcap")["messages"]:
        for key in domains["exceptions"]:
            _, wanted_topic, field = key.split()
            if topic == wanted_topic:
                assert field in message, key
                found.add(key)
    assert {"trace.mcap /planner/trajectory stamp_us", "trace.mcap /planner/cycle lane_capture_us"} <= found
    types = [json.loads(line)["type"] for line in __import__("gzip").open(folder / "frames.ndjson.gz")]
    assert types[0] == "state" and "init" in types and "f" in types and "done" in types and types[-1] == "state"


def test_planner_crash_is_sut_execution(tmp_path, build_stub):
    folder, status = _run(tmp_path, build_stub("STUB_CRASH"))
    ex = status["execution"]
    assert ex["state"] == "FAILED" and ex["failure"] == "SUT_EXECUTION" and not ex["complete"], ex
    assert "adapters/sil" in (folder / "worker.log").read_text(errors="replace")
    assert (folder / "resolved-case.json").is_file()  # partial artifacts are kept

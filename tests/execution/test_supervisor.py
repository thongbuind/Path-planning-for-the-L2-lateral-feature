"""Run lifecycle of execution.supervisor with a fake worker (no planner): SIM-REQ-002 to 012,
020 to 024."""

import json
import os
import signal
import sys
import time
from pathlib import Path

import pytest

from execution import bundle as B
from execution.supervisor import Settings, Supervisor, TERMINAL, classify

WORKER = [sys.executable, str(Path(__file__).with_name("fake_worker.py"))]


@pytest.fixture
def sup(tmp_path):
    s = Supervisor(Settings(root=tmp_path / "runs", command=WORKER, max_running=2, cancel_grace_s=0.5,
                            keep=None, max_bytes=None))
    yield s
    s.shutdown(2.0)


def wait(sup, run_id, states=TERMINAL, timeout=10.0):
    end = time.time() + timeout
    while time.time() < end:
        state = sup.status(run_id)
        state = state.get("state") or state.get("execution", {}).get("state")
        if state in states:
            return state
        time.sleep(0.02)
    raise AssertionError(f"{run_id} still {state}")


def execution(sup, run_id):
    return sup.status(run_id)["execution"]


def test_completed_run_leaves_a_complete_verified_bundle(sup):
    run_id = sup.submit({"mode": "ok"})
    assert wait(sup, run_id) == "COMPLETED"
    folder = sup.s.root / run_id
    ex = execution(sup, run_id)
    assert ex["complete"] and ex["missing"] == [] and ex["failure"] is None
    assert B.verify(folder) == []
    assert not list(sup.s.root.glob(B.TMP_PREFIX + "*"))
    lines = [json.loads(x) for x in sup.events(run_id)]
    assert [e["seq"] for e in lines] == list(range(1, len(lines) + 1))
    assert sum(e["type"] == "f" for e in lines) == 10 and lines[-1]["state"] == "COMPLETED"


def test_run_ids_are_unique(sup):
    ids = {sup.submit({"mode": "ok"}) for _ in range(4)}
    assert len(ids) == 4
    for run_id in ids:
        wait(sup, run_id)


def test_observer_leaving_does_not_stop_the_run(sup):
    run_id = sup.submit({"mode": "slow", "n": 10})
    stream = sup.events(run_id)
    next(stream)
    stream.close()  # the tab closed
    assert wait(sup, run_id) == "COMPLETED"


def test_cancel_stops_only_that_run(sup):
    a = sup.submit({"mode": "slow", "n": 200})
    b = sup.submit({"mode": "slow", "n": 10})
    wait(sup, a, {"RUNNING"})
    start = time.time()
    sup.cancel(a)
    assert wait(sup, a) == "CANCELLED"
    assert time.time() - start < sup.s.cancel_grace_s + 1.0
    assert wait(sup, b) == "COMPLETED"
    assert not execution(sup, a)["complete"]


def test_cancel_kills_a_worker_that_ignores_sigterm(sup):
    run_id = sup.submit({"mode": "stubborn"})
    wait(sup, run_id, {"RUNNING"})
    time.sleep(0.2)
    sup.cancel(run_id)
    assert wait(sup, run_id) == "CANCELLED"


@pytest.mark.parametrize("mode, failure", [("crash_sut", "SUT_EXECUTION"), ("crash_sim", "SIM_ERROR"),
                                           ("eval_error", "EVAL_ERROR"), ("stderr", "INFRA")])
def test_failures_are_classified(sup, mode, failure):
    run_id = sup.submit({"mode": mode})
    assert wait(sup, run_id) == "FAILED"
    ex = execution(sup, run_id)
    assert ex["failure"] == failure and not ex["complete"]
    assert set(ex["missing"]) == {"manifest.json", "resolved-case.json", "evaluation.json"}


def test_worker_log_keeps_stderr_and_stray_stdout(sup):
    run_id = sup.submit({"mode": "stderr"})
    wait(sup, run_id)
    log = (sup.s.root / run_id / "worker.log").read_text()
    assert "Traceback" in log and "plain text, not JSON" in log


def test_external_kill_is_infra(sup):
    run_id = sup.submit({"mode": "slow", "n": 200})
    wait(sup, run_id, {"RUNNING"})
    time.sleep(0.2)
    sup._runs[run_id].proc.send_signal(signal.SIGKILL)
    start = time.time()
    assert wait(sup, run_id) == "FAILED"
    assert time.time() - start < 5.0  # T_state
    assert execution(sup, run_id)["failure"] == "INFRA"


def test_timeout(tmp_path):
    s = Supervisor(Settings(root=tmp_path / "runs", command=WORKER, cancel_grace_s=0.3, keep=None, max_bytes=None))
    try:
        run_id = s.submit({"mode": "slow", "n": 200}, timeout_s=0.5)
        assert wait(s, run_id) == "TIMED_OUT"
    finally:
        s.shutdown(2.0)


def test_paused_time_is_not_counted_against_the_timeout(tmp_path):
    s = Supervisor(Settings(root=tmp_path / "runs", command=WORKER, cancel_grace_s=0.3, keep=None, max_bytes=None))
    try:
        run_id = s.submit({"mode": "slow", "n": 10}, timeout_s=1.5)
        wait(s, run_id, {"RUNNING"})
        assert s.control(run_id, {"cmd": "pause"}) == "PAUSED"
        time.sleep(1.6)
        assert s.control(run_id, {"cmd": "resume"}) == "RUNNING"
        assert wait(s, run_id) == "COMPLETED"
    finally:
        s.shutdown(2.0)


def test_queue_respects_max_running(tmp_path):
    s = Supervisor(Settings(root=tmp_path / "runs", command=WORKER, max_running=1, keep=None, max_bytes=None))
    try:
        a = s.submit({"mode": "slow", "n": 10})
        b = s.submit({"mode": "ok"})
        assert s.status(b)["state"] == "QUEUED"
        assert wait(s, a) == "COMPLETED" and wait(s, b) == "COMPLETED"
        c = s.submit({"mode": "slow", "n": 100})
        d = s.submit({"mode": "ok"})
        s.cancel(d)
        assert execution(s, d)["state"] == "CANCELLED"
        s.cancel(c)
        wait(s, c)
    finally:
        s.shutdown(2.0)


def test_reconnect_resumes_after_the_last_seq(sup):
    run_id = sup.submit({"mode": "ok"})
    wait(sup, run_id)
    all_events = [json.loads(x)["seq"] for x in sup.events(run_id)]
    later = [json.loads(x)["seq"] for x in sup.events(run_id, after=5)]
    assert later == [s for s in all_events if s > 5]


def test_idempotency_key_returns_the_same_run(sup):
    a = sup.submit({"mode": "ok"}, idempotency_key="k1")
    assert sup.submit({"mode": "ok"}, idempotency_key="k1") == a
    wait(sup, a)


def test_recovery_finalizes_only_own_stale_folders(tmp_path):
    root = tmp_path / "runs"
    mine = B.Bundle.create(root, "20260101-000000-aaaaaa")
    B.write_json(mine.path("supervisor.json"), {"pid": 999_999_9})
    other = B.Bundle.create(root, "20260101-000000-bbbbbb")  # eval.runner writing, no owner file
    s = Supervisor(Settings(root=root, command=WORKER, keep=None, max_bytes=None))
    try:
        ex = json.loads((root / mine.run_id / "execution.json").read_text())
        assert ex["state"] == "FAILED" and ex["failure"] == "INFRA"
        assert other.tmp.is_dir()
    finally:
        s.shutdown(1.0)


def test_retention_keeps_newest_and_pinned(tmp_path):
    s = Supervisor(Settings(root=tmp_path / "runs", command=WORKER, keep=2, max_bytes=None))
    try:
        first = s.submit({"mode": "ok"})
        wait(s, first)
        s.pin(first)
        ids = [first]
        for _ in range(3):
            ids.append(s.submit({"mode": "ok"}))
            wait(s, ids[-1])
            time.sleep(1.1)  # run ids sort by second
        left = {p.name for p in B.listing(s.s.root)}
        assert first in left and ids[-1] in left and ids[1] not in left
    finally:
        s.shutdown(1.0)


def test_classify_rules():
    kw = dict(cancelled=False, timed_out=False, reported=None, log_tail="", sut_marker="adapters/sil")
    assert classify(0, **kw) == ("COMPLETED", None)
    assert classify(-int(signal.SIGSEGV), **{**kw, "log_tail": "adapters/sil/x.py"}) == ("FAILED", "SUT_EXECUTION")
    assert classify(-int(signal.SIGSEGV), **kw) == ("FAILED", "SIM_ERROR")
    assert classify(-int(signal.SIGKILL), **kw) == ("FAILED", "INFRA")
    assert classify(3, **{**kw, "reported": "EVAL_ERROR"}) == ("FAILED", "EVAL_ERROR")
    assert classify(-9, **{**kw, "cancelled": True}) == ("CANCELLED", None)
    assert classify(-15, **{**kw, "timed_out": True}) == ("TIMED_OUT", None)

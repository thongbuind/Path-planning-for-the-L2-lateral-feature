"""Conformance B0 (Software Qualification Test Specification 11) finds contract faults of
a planner library and survives a library that crashes."""

import pytest

from eval import conformance


@pytest.fixture(scope="module")
def judge(build_stub):
    cache = {}

    def run(*defines):
        if defines not in cache:
            result = conformance.run(build_stub(*defines))
            cache[defines] = {**result, "status": {c["id"]: c["status"] for c in result["checks"]}}
        return cache[defines]
    return run


def failed(result):
    return {k for k, v in result["status"].items() if v == "fail"}


def test_conformant_library_passes_and_is_integrable(judge):
    r = judge()
    assert failed(r) == set()
    assert not r["blocked"] and r["integrable"]
    assert r["status"]["C1.layout"] == "not_checked"  # not observable from the binary


@pytest.mark.parametrize("define, expected, blocked", [
    ("STUB_NO_STEP", {"C1.symbols"}, True),
    ("STUB_NO_TRAJECTORY", {"C2.outputs_every_cycle"}, True),
    ("STUB_ACCEPT_WIDE", {"C2.init_out_of_limits"}, True),
    ("STUB_COUNTER_STUCK", {"C2.counter"}, True),
    ("STUB_NAN", {"C2.finite"}, True),
    ("STUB_GLOBAL_STATE", {"C3.interleaved"}, False),
    ("STUB_OVERRUN", {"C3.memory"}, False),
    ("STUB_CLOCK", {"C3.symbols"}, False),
])
def test_each_fault_is_reported_at_its_level(judge, define, expected, blocked):
    r = judge(define)
    assert expected <= failed(r)
    assert r["blocked"] is blocked
    assert not r["integrable"]


def test_crash_in_the_library_is_a_failure_not_an_evaluator_crash(judge):
    r = judge("STUB_CRASH")
    assert r["blocked"]
    crashed = [c for c in r["checks"] if c["status"] == "fail" and "signal" in c["detail"]]
    assert crashed and all(c["level"] in ("C1", "C2", "C3") for c in crashed)


def test_missing_required_call_skips_the_checks_that_need_it(judge):
    r = judge("STUB_NO_STEP")
    assert r["status"]["C2.counter"] == "not_checked"
    assert r["status"]["C3.symbols"] == "pass"  # read from the file, no call needed


def test_chassis_signals_use_the_can_range_others_the_type_range():
    # Interface Control Document 5.3: what the CAN encoding can deliver after scaling to SI.
    from eval import contract_io as io
    high = io.Sequence("x", 1, extreme=("imu", "high")).frame(0).imu.message
    assert high.yaw_rate_rps == pytest.approx(327.67 * 3.141592653589793 / 180, rel=1e-6)
    assert high.accel_y_mps2 == pytest.approx(32.767, rel=1e-6)
    low = io.Sequence("x", 1, extreme=("speed", "low")).frame(0).speed.message
    assert low.speed_mps == 0.0
    assert io.Sequence("x", 1, extreme=("speed", "high")).frame(0).speed.message.speed_mps \
        == pytest.approx(655.35 / 3.6, rel=1e-6)
    plan = io.Sequence("x", 1, extreme=("longitudinal_plan", "high")).frame(0).longitudinal_plan.message
    assert plan.points[0].v == io.FLT_MAX
    assert high.header.valid  # the header stays valid so the payload is used

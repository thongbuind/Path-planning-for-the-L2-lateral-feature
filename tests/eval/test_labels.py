"""Labels, aspect suites and over-refusal scoring (Software Qualification Test Specification 5.3)."""

from dataclasses import replace

import pytest

import interfaces as I
from eval import aspects, labels, loader, metrics
from sim.harness import PlannerCycle

A, F = I.ActiveFunction, I.InterventionPhase


@pytest.mark.parametrize("scenario, variant, level, expected", [
    ("S1", "a", "L0", "drive"),            # SQTS 5.3 example of L0
    ("S4", "a", "L0", "drive"),
    ("S1", "e", "L1", "drive"),            # 130 km/h: end of the HWA speed range
    ("S1b", "a", "L2", "drive_limited"),   # needs more than aysmax
    ("S14", "a", "L2", "drive_limited"),
    ("S8", "late", "L0", "refuse"),        # PP-SWR-089: ELK must not start
])
def test_labels_of_anchors(scenario, variant, level, expected):
    assert labels.of(loader.load(scenario, variant)) == {"difficulty": level, "expected": expected}


def test_faults_profile_and_view_raise_the_level():
    s1a = loader.load("S1", "a")
    one = loader.with_fault(s1a, "F01", "a")
    assert labels.difficulty(one) == "L3"
    assert labels.difficulty(loader.with_fault(one, "F02", "a")) == "L4"
    assert labels.difficulty(replace(s1a, profile="VP-5")) == "L1"  # 2.5 m wide with mirrors
    assert labels.difficulty(replace(s1a, lane_width=2.5)) == "L1"
    assert labels.difficulty(replace(s1a, hwa_view_gate=True, camera_view_m=20.0)) == "L5"  # 0.8 s < t_view_hwa
    assert labels.difficulty(s1a, swept=True) == "L3"
    # On an S1b host the fault keeps the stricter outcome.
    assert labels.of(loader.with_fault(loader.load("S1b", "a"), "F01", "a"))["expected"] == "drive_limited"


def test_aspects_filter_by_labels():
    assert aspects.members("S1", "a", ["anchor"], {"difficulty": "L0", "expected": "drive"}) == ["B1", "B6", "B7", "B8"]
    assert "B5" in aspects.members("S8", "late", ["anchor"], {"difficulty": "L0", "expected": "refuse"})
    assert "B2" in aspects.members("S4", None, ["protocol"], {"difficulty": "L0", "expected": "drive"})
    assert {"B3", "B5"} <= set(aspects.members("S1b", "a", ["anchor"], {"difficulty": "L2", "expected": "drive_limited"}))
    assert "B4" in aspects.members("F02", None, ["boundary"], {"difficulty": "L3", "expected": "drive"})


OK = {k: True for k in ("lane_model", "object_list", "imu", "steering", "speed", "vehicle_state", "function_requests")}


def _cycle(k, active=A.HWA, valid=True, hwa=I.RequestState.REQUEST, lka=I.RequestState.STANDBY,
           lka_phase=F.NONE, inputs=OK):
    points = tuple(I.TrajectoryPoint(0.1 * i, I.Pose2D(0.0, 0.0, 0.0), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
                   for i in range(I.TRAJECTORY_POINTS))
    traj = I.Trajectory(I.Header(k, 0, True, I.FrameId.BASE_LINK), points, 0.0)
    status = I.PathStatus(I.BasicHeader(k, 0, True), valid, active if valid else A.NONE, lka_phase, F.NONE, False, False)
    reqs = tuple(I.FunctionRequest(s, I.Side.NONE, 0.0, I.ElkReason.NONE, I.CancelReason.NONE)
                 for s in (hwa, lka, I.RequestState.STANDBY))
    fr = I.Received(I.FunctionRequests(I.BasicHeader(k, 0, True), reqs, False), k)
    return PlannerCycle(k * 25_000, traj, status, None, 0, None, fr, None, dict(inputs))


def _score(cycles, outcome="drive"):
    return metrics.over_refusal(cycles, outcome)


def test_hwa_requested_but_not_driven_is_over_refusal():
    cycles = [_cycle(k) for k in range(40)] + [_cycle(k, valid=False) for k in range(40, 60)]
    c = _score(cycles)
    assert c.applicable and not c.passed and c.value == 20 and c.first_fail_s == pytest.approx(1.0)
    assert not _score(cycles, "refuse").applicable  # refuse cases are judged by their own requirement


def test_lost_input_and_one_second_after_are_not_counted():
    bad = {**OK, "lane_model": False}
    cycles = ([_cycle(k) for k in range(40)] + [_cycle(k, valid=False, inputs=bad) for k in range(40, 60)]
              + [_cycle(k, valid=False) for k in range(60, 110)] + [_cycle(k) for k in range(110, 140)])
    c = _score(cycles)
    # Last unusable at cycle 59 (1.475 s): not driving is excused up to 2.475 s, counted from 2.5 s.
    assert c.value == 10 and c.first_fail_s == pytest.approx(2.5)


def test_started_intervention_must_continue_until_completed():
    lka = I.RequestState.REQUEST
    cycles = ([_cycle(k) for k in range(20)]
              + [_cycle(k, active=A.HWA, lka=lka) for k in range(20, 25)]           # not started: judged per case
              + [_cycle(k, active=A.LKA, lka=lka, lka_phase=F.ACTIVE) for k in range(25, 50)]
              + [_cycle(k, active=A.HWA, lka=lka, lka_phase=F.ACTIVE) for k in range(50, 55)]  # dropped: wrong
              + [_cycle(k, active=A.HWA, lka=lka, lka_phase=F.COMPLETED) for k in range(55, 70)])
    c = _score(cycles)
    assert c.value == 5 and c.first_fail_s == pytest.approx(50 * 0.025)


def test_driving_hwa_without_request_is_a_wrong_choice():
    cycles = [_cycle(k) for k in range(20)] + [_cycle(k, hwa=I.RequestState.STANDBY) for k in range(20, 30)]
    assert _score(cycles).value == 9  # the first cycle after the change is excused (PP-SWR-038)


# ---- reaction to faults (PP-SWR-124, 131, 132, 142, 143, 145, 043) ----------------------

def _fc(k, valid=True, inputs=OK, times=None, local=None):
    c = _cycle(k, valid=valid, inputs=inputs)
    return replace(c, t0_local_us=local if local is not None else c.t0_us, input_times=times)


def _ids(criteria):
    return {c.id: c for c in criteria}


def test_chassis_and_ego_motion_loss_must_end_the_path_within_one_cycle():
    imu_bad = {**OK, "imu": False}
    late = [_fc(k) for k in range(10)] + [_fc(k, inputs=imu_bad) for k in range(10, 14)] + [_fc(14)]
    c = _ids(metrics.fault_reaction_criteria(late, 1.0))["PP-SWR-142"]
    assert c.applicable and c.value == 3 and c.first_fail_s == pytest.approx(11 * 0.025)
    good = [_fc(k) for k in range(10)] + [_fc(10, inputs=imu_bad)] + [_fc(k, valid=False, inputs=imu_bad) for k in range(11, 14)]
    assert _ids(metrics.fault_reaction_criteria(good, 1.0))["PP-SWR-142"].passed
    ego_bad = {**OK, "ego_motion": False}
    c = _ids(metrics.fault_reaction_criteria([_fc(k, inputs=ego_bad if k >= 5 else OK) for k in range(8)], 1.0))
    assert c["PP-SWR-143"].value == 2 and not c["PP-SWR-142"].applicable


def test_lane_model_loss_keeps_the_path_for_t_coast_then_ends_it():
    lost = {**OK, "lane_model": False}
    def run(invalid_from):
        return [_fc(k, valid=not (k >= invalid_from), inputs=lost if k >= 10 else OK) for k in range(60)]
    t_coast = 0.5  # 20 cycles
    assert _ids(metrics.fault_reaction_criteria(run(30), t_coast))["PP-SWR-124"].passed
    early = _ids(metrics.fault_reaction_criteria(run(12), t_coast))["PP-SWR-124"]
    late = _ids(metrics.fault_reaction_criteria(run(40), t_coast))["PP-SWR-124"]
    assert not early.passed and not late.passed and late.first_fail_s == pytest.approx(32 * 0.025)


def test_future_or_old_lane_stamp_is_judged_on_its_own_requirement():
    lost = {**OK, "lane_model": False}
    future = [_fc(k, valid=k < 30, inputs=lost if k >= 10 else OK,
                  times={"lane_model": (k * 25_000 + 50_000, k * 25_000, True)}) for k in range(40)]
    c = _ids(metrics.fault_reaction_criteria(future, 0.5))
    assert c["PP-SWR-132"].applicable and c["PP-SWR-132"].passed and not c["PP-SWR-124"].applicable


def test_requests_timeout_needs_none_and_invalid_and_043():
    cycles = [_fc(k, times={"function_requests": (k * 25_000, k * 25_000, True)}) for k in range(10)]
    cycles += [_fc(k, times={"function_requests": (9 * 25_000, 9 * 25_000, True)}) for k in range(10, 16)]
    c = _ids(metrics.fault_reaction_criteria(cycles, 1.0))["PP-SWR-145"]
    # Timeout once t0 - rx > 75 ms: cycle 13 on; from the second such cycle the path must end.
    assert c.value == 2
    status = I.PathStatus(I.BasicHeader(0, 0, True), False, A.HWA, F.NONE, F.NONE, False, False)
    bad = replace(_fc(3), path_status=status)
    assert not _ids(metrics.fault_reaction_criteria([_fc(0), bad], 1.0))["PP-SWR-043"].passed


def test_predicted_or_low_confidence_boundaries_are_not_enough():
    M, P, L = I.LineStatus.MEASURED, I.LineStatus.PREDICTED, I.LineStatus.LOST
    cal = {"conf_ego": 0.6, "conf_inferred": 0.8}
    def with_b(b):
        return replace(_fc(0), lane_boundaries=b)
    assert metrics.lane_usable(with_b(((L, 0.0), (M, 0.7), (L, 0.0), (L, 0.0), (L, 0.0), (L, 0.0))), cal)
    assert not metrics.lane_usable(with_b(((P, 1.0),) * 6), cal)  # reconstructed only
    # L2, R2 measured but below conf_inferred (F21 e): not enough
    assert not metrics.lane_usable(with_b(((M, 0.7), (L, 0.0), (L, 0.0), (M, 0.7), (L, 0.0), (L, 0.0))), cal)
    assert metrics.lane_usable(with_b(((M, 0.9), (L, 0.0), (L, 0.0), (L, 0.0), (L, 0.0), (L, 0.0))), cal)

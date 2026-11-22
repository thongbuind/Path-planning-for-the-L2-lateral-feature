from dataclasses import replace
import json
from math import inf

import pytest

from eval.metrics import Criterion, Result, _Truth, _follow_coast, _score_fault_exposure, evaluate
from interfaces import (
    BasicHeader, CancelReason, ElkReason, FrameId, FunctionRequest,
    FunctionRequests, Header, InterventionPhase, LateralLimits, LccMode, LccStatus, LineStatus,
    PlannerId, Pose2D, Received, RequestState, Side, Trajectory, TrajectoryPoint,
)
from sim.stand_ins.arbitrator import ActiveFunction, SystemStatus
from sim.harness import PlannerCycle, RunLog
from sim.scenario import Scenario
from sim.world.road import Road, Segment
from sim.world.traffic import TrafficSpec

NONE = ActiveFunction.NONE
LKA = ActiveFunction.LKA
ELK = ActiveFunction.ELK
OFF = FunctionRequest(RequestState.OFF, Side.NONE, inf, ElkReason.NONE, CancelReason.NONE)
BEGIN = 50_000
END = 575_000  # Mốc ổn định đầu tiên là 75 ms; từ đó mới tính T_end_hold.


def _log(expect="LKA", *, requested=LKA, active=LKA, end_us=END, completes=True,
         curvature=0.0, offset=lambda _t: 0.0, reason=ElkReason.NONE, traffic=(),
         mode="B", actuator_delay_s=0.05, duration_us=2_000_000, eps_delay_s=None):
    segments = (Segment("straight", 300),)
    scenario = Scenario("synthetic", segments, 3.5, 20.0, hwa_request_s=None,
                        adas_mode=mode, notes={"expect_intervention": expect}, traffic=traffic,
                        eps_delay_s=eps_delay_s)
    log = RunLog(scenario, 1, Road(list(segments), 3.5), 1.9, 2.9, .61, 6.0, 15.0, 0,
                 actuator_delay_s=actuator_delay_s)
    for t in range(0, duration_us + 1, 1_000):
        x, y = 10 + 20 * t * 1e-6, offset(t)
        log.t_us.append(t)
        log.rear.append((x, y, 0.0))
        log.front.append((x + 2.9, y, 0.0))
        log.rear_v_y.append(0.0)
        log.yaw_rate.append(0.0)
        log.speed.append(20.0)
        log.a_y.append(0.0)
        log.eps_controlling.append(BEGIN <= t < end_us and active != NONE)
    for n, t in enumerate(range(0, duration_us + 1, 25_000)):
        counter = n % 256
        hdr = BasicHeader(t, counter, True)
        state = [OFF, OFF, OFF]
        if requested != NONE and BEGIN <= t <= end_us:
            state[int(requested) - 1] = FunctionRequest(
                RequestState.REQUEST, Side.LEFT, 0.6, reason, CancelReason.NONE)
        message = Received(FunctionRequests(hdr, tuple(state), False), t)
        steering = active if BEGIN <= t < end_us else NONE
        phase = [InterventionPhase.NONE, InterventionPhase.NONE]
        if steering != NONE:
            phase[int(steering) - 2] = InterventionPhase.ACTIVE
        elif completes and active != NONE and t == end_us:
            phase[int(active) - 2] = InterventionPhase.COMPLETED
        status = SystemStatus(hdr, True, steering, *phase, False, False)
        points = tuple(TrajectoryPoint(i / 10, Pose2D(2.0 * i, 0.0, 0.0), 20.0, 0.0, 0.0,
                                       20.0 * curvature, curvature, 0.0, 0.0)
                       for i in range(31))
        trajectory = Trajectory(Header(t, counter, True, FrameId.BASE_LINK), points, 3.0, PlannerId.LCC)
        limits = LateralLimits(hdr, 20.0, 0.0, False)
        log.cycles.append(PlannerCycle(t, trajectory, status, limits, 0, function_requests=message))
    return log


def _criteria(result, number):
    return [c for c in result.criteria if c.id == f"PP-SWR-{number:03d}" and c.applicable]


@pytest.mark.parametrize("invalid_at, passed", [(1_200_000, True), (1_100_000, False), (1_400_000, False)])
def test_follow_coast_times_from_exit(invalid_at, passed):
    log = _log(requested=NONE, active=NONE)
    following = []
    for c in log.cycles:
        follow = c.t0_us < 200_000
        c.inputs_ok = {"lane_model": True}
        c.lane_boundaries = ((LineStatus.LOST, 0.0),) * 6
        c.lcc_status = LccStatus(c.path_status.header, c.t0_us < invalid_at,
                                 LccMode.FOLLOW if follow else LccMode.COAST, 0.0, False, False)
        following.append(follow)
    check = _follow_coast(log, _Truth(log), log.cycles, following, {"T_coast": 1.0})
    assert check.applicable and check.passed == passed


def test_fault_never_injected_is_not_judged_as_passed():
    log = _log()
    log.fault_events = {"lka_active": None}
    result = evaluate(log)
    assert result.info["faults_not_injected"] == ["lka_active"]
    assert [i["kind"] for i in result.issues if "chưa được bơm" in i["text"]] == ["not_judged"]
    assert result.passed is not True

    log.fault_events = {"lka_active": BEGIN}
    assert not [i for i in evaluate(log).issues if "chưa được bơm" in i["text"]]


def test_f24_requires_a_changed_frame_seen_during_active_intervention():
    log = _log()
    log.scenario = replace(log.scenario, name="F24-a")
    result = Result(log.scenario.name, 1, [Criterion("PP-SWR-085", "", 0, ">= 0", True),
                                          Criterion("PP-SWR-086", "", -0.4, ">= -0.3", False)], [])
    _score_fault_exposure(result, log)
    assert result.issues[0]["kind"] == "not_judged"
    assert not _criteria(result, 93)

    frame = log.cycles[3]
    frame.input_times = {"lane_model": (1, 2, True)}
    log.fault_frames = {"lane_model": [1]}
    _score_fault_exposure(result, log)
    assert not _criteria(result, 93)[0].passed
    assert result.info["fault_exposure_s"] == pytest.approx(frame.t0_us * 1e-6)


@pytest.mark.parametrize("requested, step", [(NONE, "thiếu REQUEST"), (LKA, "thiếu path")])
def test_expected_intervention_cannot_pass_if_activation_is_missing(requested, step):
    result = evaluate(_log(requested=requested, active=NONE))
    assert not result.passed
    assert len(result.case_failures) == 1 and step in result.case_failures[0]
    assert not _criteria(result, 83) and not _criteria(result, 86)


def test_reports_duration_completion_dwell_and_path_limits():
    result = evaluate(_log())
    assert result.info["interventions"][0]["observed_duration_s"] == pytest.approx((END - BEGIN) * 1e-6)
    assert _criteria(result, 32)[0].passed and _criteria(result, 90)[0].passed
    assert _criteria(result, 84)[0].value == pytest.approx(.8)
    assert all(c.passed for c in _criteria(result, 80))
    assert len(_criteria(result, 110)) == 1 and not _criteria(result, 111)

    early = evaluate(_log(end_us=END - 25_000))
    assert not _criteria(early, 90)[0].passed
    too_much_added = evaluate(_log(curvature=.004))
    assert _criteria(too_much_added, 110)[0].passed
    assert not _criteria(too_much_added, 112)[0].passed
    assert _criteria(too_much_added, 112)[0].value == pytest.approx(1.6)
    assert too_much_added.info["lka_vehicle_r79"]["ay_vehicle_r79_max"] == 0


def test_opposite_dlc_includes_handover():
    result = evaluate(_log(offset=lambda t: -1.0 if t == END + 400_000 else 0.0))
    assert _criteria(result, 85)[0].value == pytest.approx(-.2)
    assert not _criteria(result, 85)[0].passed
    assert _criteria(result, 86)[0].value == pytest.approx(.8)
    assert result.info["interventions"][0]["end_handover_us"] == END + 1_000_000


def test_opposite_dlc_stops_at_next_independent_intervention():
    next_start = END + 300_000
    log = _log(offset=lambda t: -1.0 if t == END + 400_000 else 0.0)
    right = FunctionRequest(RequestState.REQUEST, Side.RIGHT, 0.6, ElkReason.NONE, CancelReason.NONE)
    for c in log.cycles:
        if next_start <= c.t0_us:
            c.path_status = replace(c.path_status, active_function=LKA, lka_phase=InterventionPhase.ACTIVE)
            message = replace(c.function_requests.message, requests=(OFF, right, OFF))
            c.function_requests = Received(message, c.t0_us)
    result = evaluate(log)
    assert result.info["interventions"][0]["end_handover_us"] == next_start
    assert _criteria(result, 85)[0].passed
    assert not result.case_failures
    assert result.info["interventions"][1]["end_us"] is None


def test_no_duration_limit_and_duration_kept_as_information():
    """PP-SWR-083 đã bỏ theo PP-TS-016. Vẫn ghi thời lượng quan sát khi log dừng giữa can thiệp."""
    short = evaluate(_log(end_us=11_000_000))
    assert not _criteria(short, 83) and not short.case_failures
    long = evaluate(_log(end_us=11_000_000, duration_us=10_200_000))
    assert not _criteria(long, 83)
    assert long.info["interventions"][0]["observed_duration_s"] > 10.0


def test_continuity_exemption_applies_only_at_the_initial_tick():
    log = _log()

    def shift(cycle):
        points = tuple(replace(p, pose=replace(p.pose, y=.3)) for p in cycle.trajectory.points)
        cycle.trajectory = replace(cycle.trajectory, points=points)

    for c in log.cycles:
        if c.t0_us < BEGIN:
            shift(c)
    assert _criteria(evaluate(log), 100)[0].passed
    shift(next(c for c in log.cycles if c.t0_us == BEGIN + 25_000))
    assert not _criteria(evaluate(log), 100)[0].passed


@pytest.mark.parametrize("first, last, step, passed", [
    (21, 30, .15, True),
    (21, 30, .25, False),
    (11, 20, .08, True),
    (0, 10, .08, False),
])
def test_continuity_limit_follows_the_time_band(first, last, step, passed):
    log = _log()
    n = next(i for i, c in enumerate(log.cycles) if c.t0_us == 1_000_000)
    c = log.cycles[n]
    points = tuple(replace(p, pose=replace(p.pose, y=step)) if first <= i <= last else p
                   for i, p in enumerate(c.trajectory.points))
    log.cycles[n] = replace(c, trajectory=replace(c.trajectory, points=points))
    criterion = _criteria(evaluate(log), 100)[0]
    assert criterion.passed == passed
    if first == 21 and passed:
        assert criterion.value == pytest.approx(.75)


def test_road_edge_dtle_and_100ms_actuator_delay():
    # PP-SWR-091: EPS thực có trễ 100 ms, VehicleConfig chỉ báo 50 ms.
    result = evaluate(_log("ELK", requested=ELK, active=ELK, reason=ElkReason.ROAD_EDGE,
                           offset=lambda t: .92 if t == BEGIN + 1_000 else 0.0, eps_delay_s=.1))
    assert _criteria(result, 86)[0].value == pytest.approx(-.12)
    assert not _criteria(result, 86)[0].passed
    assert not _criteria(result, 91)[0].passed
    assert _criteria(result, 111)[0].passed and not _criteria(result, 110)


@pytest.mark.parametrize("active, passed", [(NONE, True), (ELK, False)])
def test_late_elk_uses_real_dlc_at_request_receipt(active, passed):
    result = evaluate(_log("late ELK", requested=ELK, active=active,
                           reason=ElkReason.OVERTAKING, offset=lambda _t: 1.2))
    assert result.info["late_elk_request_dlc_m"] == pytest.approx([-.4])
    assert _criteria(result, 89)[0].passed == passed
    assert not result.case_failures


def test_late_fixture_must_actually_cross_the_threshold():
    result = evaluate(_log("late ELK", requested=ELK, active=NONE))
    assert not _criteria(result, 89)
    assert result.case_failures


def test_other_car_gap_is_scored_while_no_impact_is_information():
    result = evaluate(_log("ELK", requested=ELK, active=ELK, reason=ElkReason.OVERTAKING,
                           traffic=(TrafficSpec(1, 11.45, 1.95, 20.0),)))
    assert _criteria(result, 88)[0].value == pytest.approx(.05)
    assert not _criteria(result, 88)[0].passed
    assert result.info["no_impact"]
    assert json.loads(json.dumps(result.to_dict()))["info"]["no_impact"]


def test_other_car_gap_is_not_scored_while_the_car_is_behind():
    result = evaluate(_log("ELK", requested=ELK, active=ELK, reason=ElkReason.OVERTAKING,
                           traffic=(TrafficSpec(1, 11.45 - 20.0, 1.95, 20.0),)))
    assert not _criteria(result, 88)
    assert result.info["no_impact"]


def test_other_car_gap_counts_only_from_when_the_car_is_abreast():
    near = TrafficSpec(1, 11.45 - 20.0, 1.95, 20.0)
    far = TrafficSpec(2, 11.45, 2.40, 20.0)
    result = evaluate(_log("ELK", requested=ELK, active=ELK, reason=ElkReason.OVERTAKING,
                           traffic=(near, far)))
    assert _criteria(result, 88)[0].value == pytest.approx(.5)
    assert _criteria(result, 88)[0].passed


OVERRIDE_US = 1_000_000
INPUTS_OK = {k: True for k in ("lane_model", "imu", "speed", "steering", "ego_motion", "function_requests")}


def _override_log(override: bool, jump_us: int = OVERRIDE_US):
    log = _log(expect="", requested=NONE, active=NONE)
    for n, c in enumerate(log.cycles):
        shift = 0.0 if c.t0_us >= jump_us else 0.3
        points = tuple(replace(p, pose=replace(p.pose, y=shift)) for p in c.trajectory.points)
        on = override and c.t0_us >= OVERRIDE_US
        message = replace(c.function_requests,
                          message=replace(c.function_requests.message, driver_override=on))
        log.cycles[n] = replace(c, trajectory=replace(c.trajectory, points=points),
                                function_requests=message, inputs_ok=dict(INPUTS_OK))
    return log


@pytest.mark.parametrize("override, jump_us, passed", [
    (True, OVERRIDE_US, True),
    (True, OVERRIDE_US + 500_000, True),
    (False, OVERRIDE_US, False),
])
def test_continuity_not_judged_while_the_driver_overrides(override, jump_us, passed):
    result = evaluate(_override_log(override, jump_us))
    assert _criteria(result, 100)[0].passed == passed


def test_mode_a_does_not_grade_planner():
    result = evaluate(_log(active=NONE, mode="A"))
    assert result.passed is None
    assert not result.criteria and not result.case_failures


@pytest.mark.parametrize("eps, judged", [(None, False), (0.05, False), (0.075, True), (0.1, True), (0.15, False)])
def test_091_is_judged_when_the_real_eps_is_slower_up_to_100ms(eps, judged):
    result = evaluate(_log("ELK", requested=ELK, active=ELK, reason=ElkReason.ROAD_EDGE, eps_delay_s=eps))
    assert bool(_criteria(result, 91)) == judged


@pytest.mark.parametrize("index", [2, 10])
def test_non_finite_output_is_an_execution_fault_not_an_evaluator_error(index):
    """Chu kỳ có vô cực không được chiếu lên đường; suite vẫn ghi kết quả lỗi thực thi (PP-PR-026)."""
    log = _log()
    c = log.cycles[index]
    points = tuple(replace(p, pose=replace(p.pose, x=inf)) if i >= 11 else p
                   for i, p in enumerate(c.trajectory.points))
    log.cycles[index] = replace(c, trajectory=replace(c.trajectory, points=points))
    result = evaluate(log)
    assert not result.passed
    execution = [i for i in result.issues if i["kind"] == "execution"]
    assert len(execution) == 1 and "trajectory.points[11].pose.x" in execution[0]["text"]
    assert execution[0]["first_fail_s"] == pytest.approx(index * 0.025)


def test_no_lateral_jerk_targets_without_hwa():
    assert not [t for t in evaluate(_log()).targets if t.id == "PP-SWR-004"]

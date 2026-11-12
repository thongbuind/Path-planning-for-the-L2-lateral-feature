"""Test-side mechanisms of the benchmark framework: faults started by a planner-output event,
traffic speed profiles, repeated driver steering, lane re-indexing on a lane change
(Software Qualification Test Specification 4, 6)."""

import pytest

from interfaces import (
    ActiveFunction, BasicHeader, InitResult, InterventionPhase, PathStatus, PlannerOutputs, Side,
)
from sim.faults.channel import ChannelFault
from sim.faults.lane import LaneFault, LaneFaultInjector
from sim.faults.trigger import NEVER_S
from sim.harness import Harness
from sim.scenario import Scenario
from sim.sensors.lane_camera import CameraPose, LaneCamera
from sim.stand_ins.driver import DriverSpec
from sim.vehicle.profiles import PROFILES
from sim.world.road import Road, Segment
from sim.world.traffic import Traffic, TrafficSpec

import numpy as np

LKA_FROM_S = 0.5


class _LkaAfterHalfSecond:
    """Reports LKA ACTIVE from 0.5 s on; no path."""
    init_result = InitResult.OK

    def __init__(self, _config):
        self.counter = 0

    def step(self, inputs, _ego_motion):
        active = inputs.t0_us >= LKA_FROM_S * 1e6
        phase = InterventionPhase.ACTIVE if active else InterventionPhase.NONE
        status = PathStatus(BasicHeader(inputs.t0_us, self.counter % 256, True), True,
                            ActiveFunction.LKA if active else ActiveFunction.NONE, phase,
                            InterventionPhase.NONE, False, False)
        self.counter += 1
        return PlannerOutputs(path_status=status)


def _scenario(**kw):
    kw.setdefault("duration_s", 1.5)
    return Scenario("framework fixture", (Segment("straight", 400),), 3.5, 20.0, hwa_request_s=None, **kw)


def test_triggered_fault_starts_after_the_event_and_is_logged():
    fault = LaneFault("lose_line", start_s=0.2, duration_s=0.3, lines=(1,), trigger="lka_active")
    log = Harness(_scenario(lane_faults=(fault,)), _LkaAfterHalfSecond, seed=1).run()
    t_event = log.fault_events["lka_active"]
    assert LKA_FROM_S * 1e6 <= t_event < LKA_FROM_S * 1e6 + 25_000
    injected = log.scenario.lane_faults[0]
    assert injected.start_s == pytest.approx(t_event * 1e-6 + 0.2)
    lost = [c for c in log.cycles if c.lane_boundaries is not None and c.lane_boundaries[1][0].name == "LOST"]
    assert lost  # the line was really lost after the event


def test_triggered_fault_without_its_event_is_never_injected():
    fault = ChannelFault("stop", "imu", start_s=0.0, duration_s=0.5, trigger="elk_active")
    log = Harness(_scenario(channel_faults=(fault,)), _LkaAfterHalfSecond, seed=1).run()
    assert log.fault_events == {"elk_active": None}
    assert log.scenario.channel_faults[0].start_s == NEVER_S


def test_unknown_trigger_is_rejected():
    with pytest.raises(ValueError):
        LaneFault("noise", trigger="hwa_active")


def test_traffic_speed_profile_integrates_position():
    spec = TrafficSpec(1, 100.0, 0.0, 10.0, speed_profile=((0.0, 10.0), (10.0, 0.0), (20.0, 0.0), (25.0, 5.0)))
    traffic = Traffic(Road([Segment("straight", 1000.0)], 3.5), (spec,))
    assert traffic.at(10.0)[0].s == pytest.approx(150.0) and traffic.at(10.0)[0].speed == 0.0
    assert traffic.at(15.0)[0].s == pytest.approx(150.0)
    assert traffic.at(27.0)[0].s == pytest.approx(150.0 + 12.5 + 10.0)
    with pytest.raises(ValueError):
        TrafficSpec(1, 0.0, 0.0, 10.0, speed_profile=((1.0, 10.0),))


def test_driver_repeats_steer_again_and_back():
    driver = DriverSpec(steer_start_s=1.0, steer_release_s=2.0, drift_curvature=1e-3, torque_nm=1.0,
                        repeats=((4.0, 1), (6.0, -1)))
    profile = PROFILES["VP-0"]
    straight = driver.command(3_000_000, profile, 15.0, 20.0, 0.0)[0]
    left = driver.command(4_500_000, profile, 15.0, 20.0, 0.0)
    right = driver.command(6_500_000, profile, 15.0, 20.0, 0.0)
    assert left[0] > straight > right[0] and left[2].torque_nm == 1.0 and right[2].torque_nm == -1.0
    with pytest.raises(ValueError):
        DriverSpec(steer_start_s=1.0, steer_release_s=2.0, drift_curvature=1e-3, repeats=((1.5, 1),))


def test_camera_reindexes_lines_and_flags_one_frame_on_lane_change():
    road = Road([Segment("straight", 400.0)], 3.5)
    camera = LaneCamera(road)
    same = camera.capture(0, CameraPose(50.0, 0.3, 0.0, 50.0))
    assert same.lane_change == Side.NONE and same.lines[1].c0 == pytest.approx(1.75 - 0.3, abs=1e-6)
    moved = camera.capture(50_000, CameraPose(52.0, 1.9, 0.0, 52.0))
    assert moved.lane_change == Side.LEFT and camera.lane_index == 1
    # New ego lane: its right line is the old left line, its left line the old L2.
    assert moved.lines[2].c0 == pytest.approx(1.75 - 1.9, abs=1e-6)
    assert moved.lines[1].c0 == pytest.approx(5.25 - 1.9, abs=1e-6)
    assert moved.lines[0].status.name == "LOST"
    after = camera.capture(100_000, CameraPose(54.0, 2.0, 0.0, 54.0))
    assert after.lane_change == Side.NONE


def test_late_lane_change_flag_moves_one_frame():
    road = Road([Segment("straight", 400.0)], 3.5)
    camera = LaneCamera(road)
    late = LaneFaultInjector((LaneFault("lane_change_late"),), np.random.default_rng(1))
    first = late.apply(camera.capture(0, CameraPose(52.0, 1.9, 0.0, 52.0)))
    second = late.apply(camera.capture(50_000, CameraPose(54.0, 2.0, 0.0, 54.0)))
    assert first.lane_change == Side.NONE and second.lane_change == Side.LEFT


def test_evaluator_measures_from_the_lane_the_car_changed_to():
    from eval.metrics import lane_relative
    from types import SimpleNamespace
    road = Road([Segment("straight", 400.0)], 3.5)
    log = SimpleNamespace(road=road, t_us=[0, 1_000_000], rear=[(10.0, 0.0, 0.0), (30.0, 3.4, 0.0)],
                          lane_index_changes=[(1_000_000, 1)])
    import dataclasses
    # A plain namespace: lane_relative uses dataclasses.replace, so give it a dataclass.
    @dataclasses.dataclass
    class _Log:
        road: object
        t_us: list
        rear: list
        lane_index_changes: list
    rel = lane_relative(_Log(road, log.t_us, log.rear, log.lane_index_changes)).road
    assert rel.project(20.0, 0.2).d == pytest.approx(0.2)  # before the change: reference lane
    assert rel.project(40.0, 3.6).d == pytest.approx(0.1)  # after: from the new lane centre
    assert rel.pose_at(40.0, 0.0)[1] == pytest.approx(3.5)


def test_scripted_requests_and_traffic_lateral_from_asam_commands():
    from eval.openx import request_events
    events = request_events({"events": [
        {"at_s": 2.0, "requests": [["REQUEST", "NONE", "NONE"], ["REQUEST", "RIGHT", "NONE"], ["OFF", "NONE", "NONE"]],
         "driver_override": True}]})
    assert events[0].at_us == 2_000_000 and events[0].requests[1].side == Side.RIGHT and events[0].driver_override
    with pytest.raises(ValueError):
        request_events({"events": [{"at_s": 1.0, "requests": []}]})


def test_event_counter_counts_each_start_of_a_phase():
    from sim.faults.trigger import EventCounter
    counter = EventCounter()

    def status(lka):
        return PathStatus(BasicHeader(0, 0, True), True, ActiveFunction.LKA, lka, InterventionPhase.NONE, False, False)
    seq = [InterventionPhase.ACTIVE, InterventionPhase.ACTIVE, InterventionPhase.COMPLETED,
           InterventionPhase.NONE, InterventionPhase.ACTIVE, InterventionPhase.COMPLETED]
    for t, phase in enumerate(seq):
        counter.update(status(phase), t)
    assert counter.times["lka_active"] == [0, 4] and counter.times["lka_completed"] == [2, 5]
    assert counter.times["elk_active"] == []


class _LkaCycles:
    """LKA ACTIVE 0.5-1.0 s, COMPLETED 1.0-1.2 s, again ACTIVE 2.0-2.5 s, COMPLETED 2.5-2.7 s."""
    init_result = InitResult.OK

    def __init__(self, _config):
        self.counter = 0

    def step(self, inputs, _ego_motion):
        t = inputs.t0_us * 1e-6
        phase = InterventionPhase.NONE
        for a, b in ((0.5, 1.0), (2.0, 2.5)):
            if a <= t < b:
                phase = InterventionPhase.ACTIVE
            elif b <= t < b + 0.2:
                phase = InterventionPhase.COMPLETED
        status = PathStatus(BasicHeader(inputs.t0_us, self.counter % 256, True), True,
                            ActiveFunction.LKA if phase else ActiveFunction.NONE, phase,
                            InterventionPhase.NONE, False, False)
        self.counter += 1
        return PlannerOutputs(path_status=status)


def test_driver_repeats_and_scripted_requests_wait_for_their_event():
    from interfaces import CancelReason, ElkReason, FunctionRequest, RequestState
    from sim.stand_ins.scripted import RequestEvent
    inf = float("inf")
    off = FunctionRequest(RequestState.OFF, Side.NONE, inf, ElkReason.NONE, CancelReason.NONE)
    lka = FunctionRequest(RequestState.REQUEST, Side.LEFT, inf, ElkReason.NONE, CancelReason.NONE)
    driver = DriverSpec(steer_start_s=0.1, steer_release_s=0.2, drift_curvature=1e-3,
                        repeats=((0.1, 1.0), (0.1, -2.0)), repeat_trigger="lka_completed")
    events = (RequestEvent(0, (off, lka, off)), RequestEvent(300_000, (off, off, off), trigger="lka_completed"))
    harness = Harness(_scenario(duration_s=3.0, driver=driver, request_events=events), _LkaCycles, seed=1)
    log = harness.run()
    done = log.events["lka_completed"]
    assert [r for r in harness._driver_spec.repeats] == [
        pytest.approx((done[0] * 1e-6 + 0.1, 1.0)), pytest.approx((done[1] * 1e-6 + 0.1, -2.0))]
    assert len(done) == 2 and abs(done[0] - 1_000_000) <= 25_000
    lka_state = [(c.t0_us, c.function_requests.message.requests[1].state) for c in log.cycles
                 if c.function_requests is not None]
    assert any(s == RequestState.REQUEST for t, s in lka_state if t < done[0])
    assert all(s == RequestState.OFF for t, s in lka_state if t > done[0] + 400_000)

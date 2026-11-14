from dataclasses import replace
from math import inf, isinf

import pytest

from interfaces import (
    MAX_OBJECTS, BasicHeader, CancelReason, EgoMotionResponse, ElkReason, FrameId,
    FunctionRequest, Header, InterventionPhase, LaneLine, LaneModel, LaneWidthSource,
    LineStatus, LineType, Object, ObjectList, RequestState, RoadEdge, RoadEdgeType, Side,
)
from sim.messages import DriverSignals
from sim.sensors.object_sensor import UNUSED
from sim.stand_ins.adas_function import AdasFunction, AdasInputs, PathFeedback
from sim.stand_ins.adas_observation import VehicleMotion, clearance
from sim.stand_ins.scripted import RequestEvent, ScriptedFunctionRequests
from sim.vehicle.profiles import PROFILES

VEHICLE = PROFILES["VP-0"].vehicle_config()
WIDTH = 3.5
HALF = VEHICLE.vehicle_width / 2
STANDBY = FunctionRequest(RequestState.STANDBY, Side.NONE, inf, ElkReason.NONE, CancelReason.NONE)
READY = PathFeedback(True)
MOTION = VehicleMotion(20.0, 0.5, 0.0, 0.0, 0.0)
IDENTITY = EgoMotionResponse(True, 0.0, 0.0, 0.0)


def no_motion(_):
    return IDENTITY


def _lane(stamp_us, dlc, side=Side.LEFT, solid=False, variance=(0.0,) * 4):
    left = HALF + dlc if side == Side.LEFT else WIDTH - HALF - dlc
    lines = tuple(LaneLine(y, 0.0, 0.0, 0.0, variance, 0.0, 80.0, 1.0,
                           LineType.SOLID if solid and i in (1, 2) else LineType.DASHED,
                           not (solid and i in (1, 2)), LineStatus.MEASURED, 0.0)
                  for i, y in enumerate((left + WIDTH, left, left - WIDTH, left - 2 * WIDTH)))
    no_edge = RoadEdge(0.0, 0.0, 0.0, 0.0, (0.0,) * 4, 0.0, 0.0, 0.0,
                       RoadEdgeType.UNKNOWN, LineStatus.LOST, 0.0)
    return LaneModel(Header(stamp_us, 0, True, FrameId.BASE_LINK), lines, (no_edge, no_edge),
                     WIDTH, LaneWidthSource.MEASURED, Side.NONE)


def _objects(stamp_us, *objects):
    return ObjectList(Header(stamp_us, 0, True, FrameId.BASE_LINK), len(objects),
                      objects + (UNUSED,) * (MAX_OBJECTS - len(objects)))


def _step(adas, t, dlc=0.15, *, lane=None, motion=MOTION, driver=DriverSignals(),
          feedback=READY, objects=None):
    if lane is None:
        lane = _lane(t, dlc)
    return adas.message(t, AdasInputs(lane, objects, motion, driver, feedback), no_motion, STANDBY)


def _start_lka(adas):
    _step(adas, 0, dlc=0.8)
    _step(adas, 500_000)
    assert _step(adas, 550_000).requests[1].state == RequestState.REQUEST


@pytest.mark.parametrize("side, sign", [(Side.LEFT, 1), (Side.RIGHT, -1)])
def test_clearance_at_front_axle_compensates_capture_motion(side, sign):
    lane = _lane(0, 0.50, side)
    line = lane.lines[1 if side == Side.LEFT else 2]
    motion = replace(MOTION, lateral_velocity_mps=sign * 0.3)
    out = clearance(line, side, EgoMotionResponse(True, 2.0, sign * 0.2, 0.0), VEHICLE, motion)
    assert out.dlc == pytest.approx(0.3)
    assert out.outward_speed == pytest.approx(0.3)
    assert out.tlc == pytest.approx(1.0)


def test_lka_requires_two_distinct_frames_and_passive_driver():
    adas = AdasFunction(VEHICLE, lka_enabled=True, elk_enabled=False)
    _step(adas, 0)
    assert _step(adas, 499_000).requests[1].state == RequestState.STANDBY
    first = _lane(500_000, 0.15)
    assert _step(adas, 500_000, lane=first).requests[1].state == RequestState.STANDBY
    assert _step(adas, 525_000, lane=first).requests[1].state == RequestState.STANDBY
    request = _step(adas, 550_000).requests[1]
    assert request.state == RequestState.REQUEST and request.side == Side.LEFT


def test_near_line_without_drift_stays_in_standby():
    adas = AdasFunction(VEHICLE, lka_enabled=True, elk_enabled=True)
    steady = replace(MOTION, lateral_velocity_mps=0.0)
    for t in (0, 500_000, 550_000, 600_000):
        lka, elk = _step(adas, t, motion=steady, lane=_lane(t, 0.04, solid=True)).requests[1:]
        assert lka.state == elk.state == RequestState.STANDBY
    assert isinf(adas.tlc_s[0])


def test_same_side_lka_is_withdrawn_when_elk_completes_even_if_lka_is_active():
    adas = AdasFunction(VEHICLE, lka_enabled=True, elk_enabled=True)
    _step(adas, 0)
    _step(adas, 500_000, lane=_lane(500_000, 0.20, solid=True))
    lka, elk = _step(adas, 550_000, lane=_lane(550_000, 0.20, solid=True)).requests[1:]
    assert lka.state == elk.state == RequestState.REQUEST
    assert lka.side == elk.side == Side.LEFT and elk.elk_reason == ElkReason.SOLID_LINE
    phases = PathFeedback(True, InterventionPhase.ACTIVE, InterventionPhase.COMPLETED)
    lka, elk = _step(adas, 575_000, feedback=phases, lane=_lane(575_000, 0.20, solid=True)).requests[1:]
    assert lka.state == elk.state == RequestState.STANDBY
    assert _step(adas, 600_000, feedback=phases).requests[1].state == RequestState.STANDBY


def test_completion_is_attributed_to_elk_and_preserves_opposite_side_lka():
    adas = AdasFunction(VEHICLE, lka_enabled=True, elk_enabled=True)
    _start_lka(adas)
    right_drift = replace(MOTION, lateral_velocity_mps=-0.5)
    right = _lane(575_000, 0.15, Side.RIGHT, solid=True)
    lka, elk = _step(adas, 575_000, motion=right_drift, lane=right).requests[1:]
    assert lka.side == Side.LEFT and elk.side == Side.RIGHT
    phases = PathFeedback(True, InterventionPhase.ACTIVE, InterventionPhase.COMPLETED)
    lka, elk = _step(adas, 600_000, motion=right_drift, lane=right, feedback=phases).requests[1:]
    assert lka.state == RequestState.REQUEST and elk.state == RequestState.STANDBY


def test_same_side_lka_withdraws_before_elk_completion_and_then_rearms():
    adas = AdasFunction(VEHICLE, lka_enabled=True, elk_enabled=True)
    _step(adas, 0)
    _step(adas, 500_000, lane=_lane(500_000, 0.20, solid=True))
    lka, elk = _step(adas, 550_000, lane=_lane(550_000, 0.20, solid=True)).requests[1:]
    assert lka.state == elk.state == RequestState.REQUEST
    active = PathFeedback(True, elk_phase=InterventionPhase.ACTIVE)
    for t in (575_000, 600_000, 625_000):
        lka, elk = _step(adas, t, feedback=active).requests[1:]
        assert lka.state == RequestState.STANDBY and elk.state == RequestState.REQUEST
    complete = PathFeedback(True, elk_phase=InterventionPhase.COMPLETED)
    lka, elk = _step(adas, 650_000, feedback=complete).requests[1:]
    assert lka.state == elk.state == RequestState.STANDBY
    assert _step(adas, 2_600_000).requests[1].state == RequestState.STANDBY
    assert _step(adas, 2_650_000).requests[1].state == RequestState.STANDBY
    assert _step(adas, 2_700_000).requests[1].state == RequestState.REQUEST


def test_persistent_drift_rearms_after_completion():
    adas = AdasFunction(VEHICLE, lka_enabled=True, elk_enabled=False)
    _start_lka(adas)
    completed = PathFeedback(True, lka_phase=InterventionPhase.COMPLETED)
    assert _step(adas, 600_000, feedback=completed).requests[1].state == RequestState.STANDBY
    assert _step(adas, 2_550_000).requests[1].state == RequestState.STANDBY
    assert _step(adas, 2_600_000).requests[1].state == RequestState.STANDBY
    assert _step(adas, 2_650_000).requests[1].state == RequestState.REQUEST


def test_lka_held_below_speed_and_cancelled_by_same_side_indicator():
    adas = AdasFunction(VEHICLE, lka_enabled=True, elk_enabled=False)
    _start_lka(adas)
    slow = replace(MOTION, speed_mps=60 / 3.6)
    assert _step(adas, 575_000, motion=slow).requests[1].state == RequestState.REQUEST
    cancelled = _step(adas, 600_000, driver=DriverSignals(indicator=Side.LEFT))
    assert cancelled.requests[1].state == RequestState.OFF
    assert cancelled.requests[1].cancel_reason == CancelReason.INDICATOR
    assert not cancelled.driver_override


def test_torque_override_uses_elapsed_time_and_cooldown():
    adas = AdasFunction(VEHICLE, lka_enabled=True, elk_enabled=False)
    _start_lka(adas)
    torque = DriverSignals(torque_nm=3.0, hands_on=True)
    assert not _step(adas, 575_000, driver=torque).driver_override
    assert not _step(adas, 650_000, driver=torque).driver_override
    overridden = _step(adas, 675_000, driver=torque)
    assert overridden.driver_override and overridden.requests[1].cancel_reason == CancelReason.DRIVER_OVERRIDE
    assert not _step(adas, 700_000).driver_override
    for t in (1_250_000, 1_300_000):
        assert _step(adas, t).requests[1].state == RequestState.STANDBY


@pytest.mark.parametrize("opposite_edge, expected", [(True, RequestState.REQUEST), (False, RequestState.UNAVAILABLE)])
def test_road_edge_needs_opposite_boundary_or_remembered_width(opposite_edge, expected):
    adas = AdasFunction(VEHICLE, lka_enabled=True, elk_enabled=True)

    def edges_only(t):
        lane = _lane(t, 0.15)
        left = RoadEdge(HALF + 0.15, 0.0, 0.0, 0.0, (0.0,) * 4, 0.0, 80.0, 1.0,
                        RoadEdgeType.BARRIER, LineStatus.MEASURED, 0.0)
        right = replace(left, c0=left.c0 - WIDTH, type=RoadEdgeType.GRASS_GRAVEL,
                        status=LineStatus.MEASURED if opposite_edge else LineStatus.LOST)
        return replace(lane, lines=tuple(replace(line, status=LineStatus.LOST) for line in lane.lines),
                       road_edges=(left, right))

    _step(adas, 0, lane=edges_only(0))
    lka, elk = _step(adas, 500_000, lane=edges_only(500_000)).requests[1:]
    assert lka.state == RequestState.UNAVAILABLE
    assert elk.state == expected
    if opposite_edge:
        assert elk.elk_reason == ElkReason.ROAD_EDGE and elk.side == Side.LEFT


def test_jump_frame_cannot_start_lka_without_confirmation():
    adas = AdasFunction(VEHICLE, lka_enabled=True, elk_enabled=False)
    var = (0.03**2, 0.002**2, 0.0, 0.0)
    _step(adas, 0, lane=_lane(0, 0.8, variance=var))
    first = _lane(500_000, 0.15, variance=var)
    assert _step(adas, 500_000, lane=first).requests[1].state != RequestState.REQUEST
    assert _step(adas, 525_000, lane=first).requests[1].state != RequestState.REQUEST
    assert _step(adas, 550_000, lane=_lane(550_000, 0.15, variance=var)).requests[1].state == RequestState.STANDBY
    assert _step(adas, 600_000, lane=_lane(600_000, 0.15, variance=var)).requests[1].state == RequestState.REQUEST


def test_oncoming_elk_waits_for_distinct_object_frames_and_rejects_ghosts():
    adas = AdasFunction(VEHICLE, lka_enabled=False, elk_enabled=True)
    _step(adas, 0)
    real = Object(1, 25.0, 2.7, -20.0, 0.0, 3.14, 4.8, 1.9, 0.95)
    ghost = replace(real, id=2, existence_probability=0.6)
    for t in (500_000, 550_000, 600_000):
        assert _step(adas, t, objects=_objects(t, ghost)).requests[2].state == RequestState.STANDBY
    first = _objects(650_000, real)
    assert _step(adas, 650_000, objects=first).requests[2].state == RequestState.STANDBY
    assert _step(adas, 675_000, objects=first).requests[2].state == RequestState.STANDBY
    assert _step(adas, 700_000, objects=_objects(700_000, real)).requests[2].state == RequestState.STANDBY
    request = _step(adas, 750_000, objects=_objects(750_000, real)).requests[2]
    assert request.state == RequestState.REQUEST and request.elk_reason == ElkReason.ONCOMING


@pytest.mark.parametrize("x, vx, expected", [(0.0, 20.0, RequestState.REQUEST), (-10.0, 22.2, RequestState.STANDBY)])
def test_indicated_lane_change_allows_elk_only_for_qualifying_overtake(x, vx, expected):
    adas = AdasFunction(VEHICLE, lka_enabled=True, elk_enabled=True)
    driver = DriverSignals(indicator=Side.LEFT)
    obj = Object(1, x, 3.5, vx, 0.0, 0.0, 4.8, 1.9, 0.95)
    for t in (500_000, 550_000, 600_000):
        lka, elk = _step(adas, t, driver=driver, objects=_objects(t, obj)).requests[1:]
    assert lka.state == RequestState.STANDBY
    assert elk.state == expected
    if expected == RequestState.REQUEST:
        assert elk.elk_reason == ElkReason.OVERTAKING


def test_scripted_events_are_repeated_with_new_stamp_and_counter():
    elk = FunctionRequest(RequestState.REQUEST, Side.RIGHT, 0.4, ElkReason.SOLID_LINE, CancelReason.NONE)
    event = RequestEvent(50_000, (STANDBY, STANDBY, elk), True)
    scripted = ScriptedFunctionRequests(100_000, (event,))
    assert scripted.message(0).requests[2].state == RequestState.OFF
    first = scripted.message(50_000)
    second = scripted.message(75_000)
    assert first.requests == second.requests == event.requests
    assert first.driver_override and second.driver_override
    assert second.header == BasicHeader(75_000, first.header.counter + 1, True)

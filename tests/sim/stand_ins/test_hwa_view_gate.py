"""HWA view-range gate (ADAS Function Specification 7, 13)."""

from dataclasses import replace

from interfaces import CancelReason, ElkReason, FunctionRequest, RequestState, Side
from sim.sensors.lane_camera import CameraPose, LaneCamera
from sim.stand_ins.hwa_view_gate import HwaViewGate
from sim.world.road import Road, Segment

REQUEST = FunctionRequest(RequestState.REQUEST, Side.NONE, float("inf"), ElkReason.NONE, CancelReason.NONE)


def lane(view_end: float):
    road = Road([Segment("straight", 400.0)], 3.5)
    return LaneCamera(road, view_end_m=view_end).capture(0, CameraPose(50.0, 0.0, 0.0, 50.0))


def test_short_drop_keeps_hwa_and_long_drop_hands_over_then_returns():
    gate, short, long = HwaViewGate(), lane(15.0), lane(80.0)
    assert gate.apply(REQUEST, 0, long, 25.0).state == RequestState.REQUEST
    assert gate.apply(REQUEST, 100_000, short, 25.0).state == RequestState.REQUEST  # 0.6 s preview
    assert gate.apply(REQUEST, 600_000, short, 25.0).state == RequestState.REQUEST  # held 0.5 s
    assert gate.apply(REQUEST, 625_000, short, 25.0).state == RequestState.UNAVAILABLE
    assert gate.apply(REQUEST, 650_000, long, 25.0).state == RequestState.REQUEST


def test_preview_scales_with_speed_and_ignores_other_states():
    gate = HwaViewGate()
    assert gate.preview_s(lane(30.0), 25.0) > 1.0 and gate.preview_s(lane(30.0), 36.0) < 1.0
    standby = replace(REQUEST, state=RequestState.STANDBY)
    assert gate.apply(standby, 0, None, 25.0) == standby

"""Test-side mechanisms of the two-planner product: arbitrator stand-in, LeadTarget sensor and its
faults, lane faults on the drifting side (F24), traffic class (S22, S23)."""

from dataclasses import replace

import numpy as np
import pytest

import interfaces as I
from sim.faults.channel import ChannelFault, ChannelFaultInjector
from sim.faults.lane import LaneFault, _ramp, resolve_side
from sim.sensors.lead_sensor import LeadSensor
from sim.stand_ins.arbitrator import ActiveFunction, Arbitrator
from sim.world.road import Road, Segment
from sim.world.traffic import TrafficState
from tests.sim import fakes


def _lcc_out(t0=0, mode=I.LccMode.NONE, valid=True):
    header = I.BasicHeader(t0, 0, True)
    return I.LccOutputs(fakes.straight_trajectory(t0, 0, valid=valid),
                        I.LccStatus(header, valid, mode, 0.0, False, False), I.LateralLimits(header, 500.0, 0.0, False))


def _ka_out(t0=0, function=I.InterventionFunction.NONE, valid=False, phase=I.InterventionPhase.NONE):
    status = I.InterventionStatus(I.BasicHeader(t0, 0, True), True, function, phase, I.InterventionPhase.NONE, False)
    return I.LkaElkOutputs(fakes.straight_trajectory(t0, 0, I.PlannerId.LKA_ELK, valid=valid), status)


def test_arbitrator_picks_lka_elk_only_while_it_drives_with_a_valid_trajectory():
    arb = Arbitrator()
    lcc = _lcc_out(mode=I.LccMode.LANE)
    trajectory, status = arb.choose(0, lcc, _ka_out())
    assert status.chosen == I.PlannerId.LCC and status.active_function == ActiveFunction.LCC and status.path_valid
    trajectory, status = arb.choose(25_000, lcc, _ka_out(function=I.InterventionFunction.LKA, valid=True,
                                                          phase=I.InterventionPhase.ACTIVE))
    assert trajectory.planner_id == I.PlannerId.LKA_ELK
    assert status.active_function == ActiveFunction.LKA and status.lka_phase == I.InterventionPhase.ACTIVE
    # An active function without a valid Trajectory is not chosen (PP-SWR-180's other side).
    _, status = arb.choose(50_000, lcc, _ka_out(function=I.InterventionFunction.LKA, valid=False))
    assert status.chosen == I.PlannerId.LCC
    assert status.header.counter == 2


def test_arbitrator_reports_none_when_lcc_is_not_driving():
    _, status = Arbitrator().choose(0, _lcc_out(mode=I.LccMode.NONE), _ka_out())
    assert status.active_function == ActiveFunction.NONE and status.path_valid
    _, status = Arbitrator().choose(0, _lcc_out(mode=I.LccMode.NONE, valid=False), None)
    assert not status.path_valid


def test_lead_sensor_reports_the_acc_target_with_its_class_and_gap():
    road = Road([Segment("straight", 500.0)], 3.5)
    car = TrafficState(7, 60.0, 0.0, 0.0, 13.9, 60.0, 0.0, 4.8, 1.9, "TRUCK")
    sensor = LeadSensor(np.random.default_rng(1), front_m=3.9)
    msg = sensor.capture(1_000, (10.0, 0.0, 0.0), (13.9, 0.0), [car], 7)
    assert msg.header.valid and msg.id == 7 and msg.classification == I.LeadClass.TRUCK
    assert msg.x == pytest.approx(50.0, abs=1.5) and msg.gap == pytest.approx(50.0 - 2.4 - 3.9, abs=1.5)
    assert abs(msg.vx_rel) < 1.5
    none = sensor.capture(2_000, (10.0, 0.0, 0.0), (13.9, 0.0), [car], None)
    assert not none.header.valid and none.header.counter == msg.header.counter + 1
    assert not sensor.capture(3_000, (10.0, 0.0, 0.0), (13.9, 0.0), [car], 99).header.valid   # a ghost


def _lead(i=7, cls=I.LeadClass.CAR):
    return I.LeadTarget(I.Header(0, 0, True, I.FrameId.BASE_LINK), i, cls, 30.0, 0.2, 20.0, 0.0, 0.0, 0.0, 0.95)


def test_lead_target_payload_faults_change_only_what_they_name():
    rng = np.random.default_rng(3)
    for fault, check in (
        (ChannelFault("lead_id", "lead_target", value=1.0), lambda m: m.id == 8 and m.x == 30.0),
        (ChannelFault("lead_class", "lead_target", value=3.0), lambda m: m.classification == I.LeadClass.MOTORCYCLE),
        (ChannelFault("lead_noise", "lead_target", value=3.0), lambda m: m.id == 7 and m.x != 30.0),
    ):
        out = ChannelFaultInjector((fault,), rng).deliveries(_lead(), 0, 0)
        assert len(out) == 1 and check(out[0][1])
    with pytest.raises(ValueError):
        ChannelFault("lead_id", "object_list")


def test_drift_side_fault_picks_the_boundary_the_driver_drifts_to_and_ramps():
    fault = LaneFault("c0_jump", start_s=1.0, lines=(1,), edges=(0,), value=0.6, ramp_s=0.5, side="drift")
    left, right = resolve_side(fault, 1 / 500), resolve_side(fault, -1 / 500)
    assert left.lines == (1,) and left.edges == (0,) and left.value == 0.6 and left.side == ""
    assert right.lines == (2,) and right.edges == (1,) and right.value == -0.6        # away from the car
    assert resolve_side(replace(fault, side=""), 1.0) is not None
    assert _ramp(left, 1.0) == 0.0 and _ramp(left, 1.25) == pytest.approx(0.5) and _ramp(left, 3.0) == 1.0
    assert _ramp(replace(left, ramp_s=0.0), 1.0) == 1.0


def test_traffic_class_follows_the_vehicle_category():
    from eval import loader
    assert loader.load("S22", "d").traffic[0].kind == "TRUCK"
    assert loader.load("S23", "a").traffic[0].kind == "MOTORCYCLE"
    assert loader.load("S22", "a").traffic[0].kind == "CAR"

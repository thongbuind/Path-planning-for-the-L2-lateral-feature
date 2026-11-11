"""Stand-in ACC and longitudinal actuator (Software Qualification Test Specification 4.7)."""

from math import sqrt

import pytest

from interfaces import BasicHeader, LateralLimits, LongitudinalMode
from sim.stand_ins.acc import A_MIN, AY_RESERVE, AYSMAX, JERK_MAX, PERIOD_US, Acc, LongitudinalActuator


def limits(v_max, distance, flag=False, valid=True, t=0):
    return LateralLimits(BasicHeader(t, 0, valid), v_max, distance, flag)


def run(acc, v, cycles, limits_fn=None):
    t = 0
    for _ in range(cycles):
        t += PERIOD_US
        if limits_fn:
            acc.on_lateral_limits(limits_fn(t), t)
        acc.step(t, v)
    return acc


def test_cruise_towards_set_speed():
    acc = run(Acc(25.0), 20.0, 80, lambda t: limits(500.0, 0.0))
    assert acc.mode == LongitudinalMode.CRUISE and acc.command > 0.0


def test_curve_ahead_brakes_on_the_envelope():
    # Curve with v_max 20 m/s at 60 m: envelope allows sqrt(v_t^2 + 4 (60 - 12.5)) < 25.
    acc = run(Acc(25.0), 25.0, 80, lambda t: limits(20.0, 60.0))
    assert acc.mode == LongitudinalMode.CURVE_LIMIT and acc.command < 0.0
    v_t = 20.0 * sqrt(1 - AY_RESERVE / AYSMAX)
    assert v_t < 20.0


def test_flag_and_lost_limits_mean_no_acceleration():
    assert run(Acc(30.0), 20.0, 80, lambda t: limits(500.0, 0.0, flag=True)).command <= 0.0
    assert run(Acc(30.0), 20.0, 80).command <= 0.0                       # never received


def test_ignoring_limits_keeps_cruise():
    acc = run(Acc(25.0, read_limits=False), 25.0, 80, lambda t: limits(15.0, 30.0, flag=True))
    assert acc.mode == LongitudinalMode.CRUISE and acc.command == pytest.approx(0.0, abs=1e-9)


def test_jerk_and_deceleration_limits():
    acc = Acc(25.0)
    acc.on_lateral_limits(limits(5.0, 0.0), 0)
    acc.step(PERIOD_US, 25.0)
    assert acc.command == pytest.approx(-JERK_MAX * PERIOD_US * 1e-6)
    run(acc, 25.0, 200, lambda t: limits(5.0, 0.0))
    assert acc.command == pytest.approx(A_MIN)


def test_plan_has_31_points_and_slows_down():
    acc = Acc(25.0)
    acc.on_lateral_limits(limits(15.0, 40.0), 0)
    plan = acc.step(PERIOD_US, 25.0)
    assert len(plan.points) == 31
    assert plan.points[-1].v < plan.points[0].v


def test_actuator_delay_and_lag():
    act = LongitudinalActuator(20.0)
    act.command(0, -2.0)
    for t in range(1_000, 100_000, 1_000):
        act.step(t, 1e-3)
    assert act.accel == 0.0                                            # 0.1 s delay
    for t in range(100_000, 2_100_000, 1_000):
        act.step(t, 1e-3)
    assert act.accel == pytest.approx(-2.0, rel=1e-2) and act.speed < 17.0

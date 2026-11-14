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


# ---- FOLLOW and target choice (4.7) -------------------------------------------------------

from interfaces import FrameId, Header, MAX_OBJECTS, Object, ObjectList  # noqa: E402
from sim.sensors.object_sensor import UNUSED  # noqa: E402
from sim.stand_ins.acc import STANDSTILL_GAP_M, TIME_GAP_S, LeadSelector  # noqa: E402

WIDTH, WHEELBASE = 1.9, 2.9
FRONT = WHEELBASE / 2 + 4.9 / 2


def objects(t_us, *items):
    """items: (id, x, y, vx, length)."""
    objs = [Object(i, x, y, vx, 0.0, 0.0, length, 1.9, 1.0) for i, x, y, vx, length in items]
    return ObjectList(Header(t_us, 0, True, FrameId.BASE_LINK), len(objs),
                      tuple(objs + [UNUSED] * (MAX_OBJECTS - len(objs))))


def test_selector_ignores_adjacent_lane_and_never_moving_objects():
    sel = LeadSelector(WIDTH, WHEELBASE)
    lead = sel.update(0, objects(0, (1, 50.0, 3.5, 20.0, 4.8), (2, 30.0, 0.0, 0.0, 4.8)), None, None, 25.0)
    assert lead is None


def test_selector_takes_nearest_in_corridor_and_cut_in_within_one_second():
    sel = LeadSelector(WIDTH, WHEELBASE)
    lead = sel.update(0, objects(0, (1, 60.0, 0.2, 20.0, 4.8)), None, None, 25.0)
    assert lead.gap == pytest.approx(60.0 - 2.4 - FRONT) and lead.speed == 20.0
    # A car 2.0 m to the side that moves in at 1.2 m/s is inside after 1 s: chosen, nearer.
    cut = Object(3, 30.0, 2.0, 22.0, -1.2, 0.0, 4.8, 1.9, 1.0)
    msg = ObjectList(Header(0, 0, True, FrameId.BASE_LINK), 2,
                     (Object(1, 60.0, 0.2, 20.0, 0.0, 0.0, 4.8, 1.9, 1.0), cut) + (UNUSED,) * (MAX_OBJECTS - 2))
    sel.update(0, msg, None, None, 25.0)  # id 3 seen moving
    lead = sel.update(25_000, msg, None, None, 25.0)
    assert lead.speed == 22.0


def test_follow_settles_on_the_time_gap_behind_a_slower_car():
    acc, act, sel = Acc(30.0, read_limits=False), LongitudinalActuator(25.0), LeadSelector(WIDTH, WHEELBASE)
    lead_x, v_lead, t = 70.0, 20.0, 0  # lead centre ahead of the rear axle
    for _ in range(int(80 / (PERIOD_US * 1e-6))):
        t += PERIOD_US
        lead = sel.update(t, objects(t, (1, lead_x, 0.0, v_lead, 4.8)), None, None, act.speed)
        acc.step(t, act.speed, lead)
        act.command(t, acc.command)
        for k in range(25):
            v = act.step(t + k * 1000, 1e-3)
            lead_x += (v_lead - v) * 1e-3
    gap = lead_x - 2.4 - FRONT
    assert acc.mode == LongitudinalMode.FOLLOW
    assert act.speed == pytest.approx(v_lead, abs=0.1)
    assert gap == pytest.approx(STANDSTILL_GAP_M + TIME_GAP_S * v_lead, abs=1.0)

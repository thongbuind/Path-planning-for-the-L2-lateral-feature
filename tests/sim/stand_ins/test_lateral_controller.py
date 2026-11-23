from dataclasses import replace
from math import cos, exp, isclose, sin, tan

import pytest

from sim.stand_ins.arbitrator import ActiveFunction, SystemStatus
from sim.stand_ins.eps import TAU_S
from sim.stand_ins.hwa_command_limit import PredictedHwaCommandLimit, StaticHwaCommandLimit
from sim.stand_ins.lateral_controller import EgoState, LateralController, sample_trajectory
from sim.stand_ins.lateral_controller import PREVIEW_S
from interfaces import (
    TRAJECTORY_POINTS,
    TRAJECTORY_STEP_S,
    BasicHeader,
    EgoMotionRequest,
    EgoMotionResponse,
    FrameId,
    Header,
    InterventionPhase,
    PlannerId,
    Pose2D,
    Trajectory,
    TrajectoryPoint,
    VehicleConfig,
)

VP0 = VehicleConfig(
    wheelbase=2.9,
    rear_axle_to_cg=1.45,
    vehicle_width=1.9,
    steering_ratio=15.0,
    max_wheel_angle=0.61,
    max_steering_wheel_rate=6.0,
    actuator_delay=0.05,
)
K = 0.0029
SPEED = 25.0
STAMP = 10_000_000


def make_trajectory(pose_at, curvature_at=lambda t: 0.0, valid=True, stamp_us=STAMP):
    points = []
    for k in range(TRAJECTORY_POINTS):
        t = k * TRAJECTORY_STEP_S
        points.append(TrajectoryPoint(
            time_from_start=t,
            pose=pose_at(t),
            longitudinal_velocity_mps=SPEED,
            lateral_velocity_mps=0.0,
            acceleration_mps2=0.0,
            heading_rate_rps=SPEED * curvature_at(t),
            curvature=curvature_at(t),
            front_wheel_angle_rad=0.0,
            rear_wheel_angle_rad=0.0,
        ))
    return Trajectory(Header(stamp_us, 0, valid, FrameId.BASE_LINK), tuple(points), 3.0, PlannerId.LCC)


def straight(offset_y=0.0):
    return make_trajectory(lambda t: Pose2D(SPEED * t, offset_y, 0.0))


def status(path_valid=True, function=ActiveFunction.LCC, valid=True):
    return SystemStatus(BasicHeader(STAMP, 0, valid), path_valid, function,
                      InterventionPhase.NONE, InterventionPhase.NONE, False, False)


def no_motion(_request: EgoMotionRequest) -> EgoMotionResponse:
    return EgoMotionResponse(True, 0.0, 0.0, 0.0)


def controller(trajectory, path_status=None, rx_us=STAMP, make_controller=LateralController):
    c = make_controller(VP0, K)
    c.on_trajectory(trajectory, rx_us)
    c.on_path_status(path_status or status(), rx_us)
    return c


STRAIGHT_STATE = EgoState(SPEED, 0.0, 0.0)


def test_on_straight_path_steers_zero():
    request = controller(straight()).step(STAMP, STRAIGHT_STATE, no_motion)
    assert request.active
    assert request.steering_wheel_angle_rad == pytest.approx(0.0, abs=1e-12)


def test_steady_curve_is_pure_feedforward():
    radius = 500.0
    kappa = 1.0 / radius

    def arc(t):
        s = SPEED * t
        return Pose2D(radius * sin(s / radius), radius * (1 - cos(s / radius)), s / radius)

    c = controller(make_trajectory(arc, lambda t: kappa))
    request = c.step(STAMP, EgoState(SPEED, 0.0, SPEED * kappa), no_motion)
    wheel = (VP0.wheelbase + K * SPEED**2) * kappa
    assert request.steering_wheel_angle_rad == pytest.approx(VP0.steering_ratio * wheel, rel=1e-6)
    assert request.steering_wheel_angle_rad == pytest.approx(0.141, abs=1e-3)


def test_feedforward_curvature_is_read_at_actuator_delay():
    """Độ cong thay đổi sau 0,1 s trong path có pose thẳng để tách riêng feedforward."""
    trajectory = make_trajectory(
        lambda t: Pose2D(SPEED * t, 0.0, 0.0),
        lambda t: 0.0 if t < 0.15 else 0.01,
    )
    assert controller(trajectory).step(STAMP, STRAIGHT_STATE, no_motion).steering_wheel_angle_rad == 0.0

    now = STAMP + 100_000
    c = controller(trajectory, rx_us=now)
    request = c.step(now, STRAIGHT_STATE, no_motion)
    expected = VP0.steering_ratio * (VP0.wheelbase + K * SPEED**2) * 0.005
    assert request.steering_wheel_angle_rad == pytest.approx(expected, rel=1e-6)


def test_slip_angle_is_not_a_heading_error():
    """So hướng path với hướng vận tốc; góc trượt không phải là sai số heading (ICD 6.1)."""
    beta = 0.0045
    v_y = -SPEED * tan(beta)
    trajectory = make_trajectory(lambda t: Pose2D(SPEED * t, v_y * t, -beta))
    request = controller(trajectory).step(STAMP, EgoState(SPEED, v_y, 0.0), no_motion)
    assert request.steering_wheel_angle_rad == pytest.approx(0.0, abs=1e-9)


def test_path_to_the_left_steers_left():
    request = controller(straight(offset_y=0.5)).step(STAMP, STRAIGHT_STATE, no_motion)
    assert request.steering_wheel_angle_rad == pytest.approx(
        VP0.steering_ratio * 0.025 * 0.5, rel=1e-6)


def test_ego_motion_since_stamp_is_compensated():
    now = STAMP + 40_000

    def moved(request):
        assert (request.t1_us, request.t2_us) == (STAMP, now)
        return EgoMotionResponse(True, dx=SPEED * 0.04, dy=0.2, dyaw=0.0)

    request = controller(straight(), rx_us=now).step(now, STRAIGHT_STATE, moved)
    assert request.active
    assert request.steering_wheel_angle_rad == pytest.approx(
        VP0.steering_ratio * 0.025 * -0.2, rel=1e-6)


def test_wheel_angle_is_limited_by_vehicle_config():
    request = controller(straight(offset_y=100.0)).step(STAMP, STRAIGHT_STATE, no_motion)
    assert request.steering_wheel_angle_rad == pytest.approx(
        VP0.steering_ratio * VP0.max_wheel_angle)


@pytest.mark.parametrize("path_status", [
    status(path_valid=False, function=ActiveFunction.NONE),
    status(function=ActiveFunction.NONE),
    status(valid=False),
])
def test_unusable_status_holds_last_command_and_stops_control(path_status):
    c = controller(straight(offset_y=0.5))
    first = c.step(STAMP, STRAIGHT_STATE, no_motion)
    c.on_path_status(path_status, STAMP + 10_000)
    second = c.step(STAMP + 10_000, STRAIGHT_STATE, no_motion)
    assert first.active and not second.active
    assert second.steering_wheel_angle_rad == first.steering_wheel_angle_rad


def test_invalid_trajectory_header_stops_control():
    c = controller(make_trajectory(lambda t: Pose2D(SPEED * t, 0.0, 0.0), valid=False))
    assert not c.step(STAMP, STRAIGHT_STATE, no_motion).active


def test_trajectory_timeout_75_ms():
    c = controller(straight(offset_y=0.5))
    assert c.step(STAMP + 75_000, STRAIGHT_STATE, no_motion).active
    late = c.step(STAMP + 75_001, STRAIGHT_STATE, no_motion)
    assert not late.active
    assert late.steering_wheel_angle_rad != 0.0


def test_missing_messages_and_invalid_ego_motion_stop_control():
    c = LateralController(VP0, K)
    assert not c.step(STAMP, STRAIGHT_STATE, no_motion).active
    c = controller(straight())
    assert not c.step(STAMP, STRAIGHT_STATE, lambda r: EgoMotionResponse(False, 0.0, 0.0, 0.0)).active


def test_sample_trajectory_interpolates_and_rejects_outside_horizon():
    trajectory = straight()
    sample = sample_trajectory(trajectory, 0.25)
    assert isclose(sample.pose.x, SPEED * 0.25)
    assert sample_trajectory(trajectory, 3.0) is not None
    assert sample_trajectory(trajectory, 3.01) is None
    assert sample_trajectory(trajectory, -0.01) is None


@pytest.mark.parametrize("side", [-1, 1])
def test_static_limit_bounds_total_steering(side):
    make = lambda vehicle, gradient: StaticHwaCommandLimit(vehicle, gradient, sustained_ay_mps2=2.8)
    c = controller(straight(offset_y=side * 100.0), make_controller=make)
    request = c.step(STAMP, STRAIGHT_STATE, no_motion)
    expected = side * VP0.steering_ratio * (VP0.wheelbase + K * SPEED ** 2) * 2.8 / SPEED ** 2
    assert request.steering_wheel_angle_rad == pytest.approx(expected)
    assert (c.hwa_command_stats.limited, c.hwa_command_stats.samples) == (1, 1)


@pytest.mark.parametrize("variant", [StaticHwaCommandLimit, PredictedHwaCommandLimit])
@pytest.mark.parametrize("function, override", [(ActiveFunction.LKA, False), (ActiveFunction.ELK, False),
                                               (ActiveFunction.LCC, True)])
def test_limits_only_apply_when_hwa_has_authority(variant, function, override):
    make = lambda vehicle, gradient: variant(vehicle, gradient, sustained_ay_mps2=2.8)
    trajectory = straight(offset_y=100.0)
    c = controller(trajectory, status(function=function), make_controller=make)
    stock = controller(trajectory, status(function=function))
    state = replace(STRAIGHT_STATE, driver_override=override)
    assert c.step(STAMP, state, no_motion) == stock.step(STAMP, state, no_motion)
    assert c.hwa_command_stats.samples == 0


def test_predicted_limit_accounts_for_pending_command_and_recovers_when_over_limit():
    make = lambda vehicle, gradient: PredictedHwaCommandLimit(vehicle, gradient, sustained_ay_mps2=2.8)
    c = controller(straight(offset_y=100.0), make_controller=make)
    first = c.step(STAMP, STRAIGHT_STATE, no_motion)
    gain = SPEED ** 2 / (VP0.wheelbase + K * SPEED ** 2)
    delayed_target = gain * first.steering_wheel_angle_rad / VP0.steering_ratio
    # Lệnh đầu có hiệu lực sớm hơn lệnh thứ hai 10 ms.
    at_application = delayed_target + exp(-0.01 / TAU_S) * (4.0 - delayed_target)
    remaining = PREVIEW_S - VP0.actuator_delay - 0.001
    second = c.step(STAMP + 10_000, replace(STRAIGHT_STATE, yaw_rate_rps=4.0 / SPEED), no_motion)
    target = gain * second.steering_wheel_angle_rad / VP0.steering_ratio
    end = target + exp(-remaining / TAU_S) * (at_application - target)
    assert target < 2.8
    assert end == pytest.approx(2.8)


def test_predicted_limit_clears_hwa_history_during_override():
    make = lambda vehicle, gradient: PredictedHwaCommandLimit(vehicle, gradient, sustained_ay_mps2=2.8)
    trajectory = straight(offset_y=100.0)
    c = controller(trajectory, make_controller=make)
    c.step(STAMP, STRAIGHT_STATE, no_motion)
    c.step(STAMP + 10_000, replace(STRAIGHT_STATE, driver_override=True), no_motion)
    fresh = controller(trajectory, make_controller=make)
    now = STAMP + 20_000
    assert c.step(now, STRAIGHT_STATE, no_motion) == fresh.step(now, STRAIGHT_STATE, no_motion)

"""Unit tests of the stand-in Lateral Controller (Software Qualification Test Specification 4.6)."""

from math import cos, isclose, sin, tan

import pytest

from sim.stand_ins.lateral_controller import EgoState, LateralController, sample_trajectory
from interfaces import (
    TRAJECTORY_POINTS,
    TRAJECTORY_STEP_S,
    ActiveFunction,
    BasicHeader,
    EgoMotionRequest,
    EgoMotionResponse,
    FrameId,
    Header,
    InterventionPhase,
    PathStatus,
    Pose2D,
    Trajectory,
    TrajectoryPoint,
    VehicleConfig,
)

# VP-0, Software Qualification Test Specification 4.4.
VP0 = VehicleConfig(
    wheelbase=2.9,
    rear_axle_to_cg=1.45,
    vehicle_width=1.9,
    steering_ratio=15.0,
    max_wheel_angle=0.61,
    max_steering_wheel_rate=6.0,
    actuator_delay=0.05,
)
K = 0.0029  # rad/(m/s^2), simulator vehicle model
SPEED = 25.0  # m/s
STAMP = 10_000_000  # us


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
    return Trajectory(Header(stamp_us, 0, valid, FrameId.BASE_LINK), tuple(points))


def straight(offset_y=0.0):
    return make_trajectory(lambda t: Pose2D(SPEED * t, offset_y, 0.0))


def status(path_valid=True, function=ActiveFunction.HWA, valid=True):
    return PathStatus(BasicHeader(STAMP, 0, valid), path_valid, function,
                      InterventionPhase.NONE, False, False)


def no_motion(_request: EgoMotionRequest) -> EgoMotionResponse:
    return EgoMotionResponse(True, 0.0, 0.0, 0.0)


def controller(trajectory, path_status=None, rx_us=STAMP):
    c = LateralController(VP0, K)
    c.on_trajectory(trajectory, rx_us)
    c.on_path_status(path_status or status(), rx_us)
    return c


STRAIGHT_STATE = EgoState(SPEED, 0.0, 0.0)


def test_on_straight_path_steers_zero():
    request = controller(straight()).step(STAMP, STRAIGHT_STATE, no_motion)
    assert request.active
    assert request.steering_wheel_angle_rad == pytest.approx(0.0, abs=1e-12)


def test_steady_curve_is_pure_feedforward():
    """R = 500 m at 25 m/s: delta = (L + K v^2) kappa, no feedback error."""
    radius = 500.0
    kappa = 1.0 / radius

    def arc(t):
        s = SPEED * t
        return Pose2D(radius * sin(s / radius), radius * (1 - cos(s / radius)), s / radius)

    c = controller(make_trajectory(arc, lambda t: kappa))
    request = c.step(STAMP, EgoState(SPEED, 0.0, SPEED * kappa), no_motion)
    wheel = (VP0.wheelbase + K * SPEED**2) * kappa  # 0.0094 rad
    assert request.steering_wheel_angle_rad == pytest.approx(VP0.steering_ratio * wheel, rel=1e-6)
    assert request.steering_wheel_angle_rad == pytest.approx(0.141, abs=1e-3)  # about 8.1 deg


def test_feedforward_curvature_is_read_at_actuator_delay():
    """Straight poses with a curvature step after t = 0.1 s isolate the feedforward term."""
    trajectory = make_trajectory(
        lambda t: Pose2D(SPEED * t, 0.0, 0.0),
        lambda t: 0.0 if t < 0.15 else 0.01,
    )
    # now = stamp: kappa at 0.05 s lies between points 0 and 1, both 0.
    assert controller(trajectory).step(STAMP, STRAIGHT_STATE, no_motion).steering_wheel_angle_rad == 0.0

    # now = stamp + 100 ms: kappa at 0.15 s is half way from point 1 (0) to point 2 (0.01).
    now = STAMP + 100_000
    c = controller(trajectory, rx_us=now)
    request = c.step(now, STRAIGHT_STATE, no_motion)
    expected = VP0.steering_ratio * (VP0.wheelbase + K * SPEED**2) * 0.005
    assert request.steering_wheel_angle_rad == pytest.approx(expected, rel=1e-6)


def test_slip_angle_is_not_a_heading_error():
    """Path yaw is the direction of travel (ICD 6.1). A car that slides with v_y and
    moves exactly along the path must not see a heading error from its slip angle."""
    beta = 0.0045  # rear-axle slip in a gentle curve, rad
    v_y = -SPEED * tan(beta)  # direction of travel exactly -beta
    trajectory = make_trajectory(lambda t: Pose2D(SPEED * t, v_y * t, -beta))
    request = controller(trajectory).step(STAMP, EgoState(SPEED, v_y, 0.0), no_motion)
    assert request.steering_wheel_angle_rad == pytest.approx(0.0, abs=1e-9)


def test_path_to_the_left_steers_left():
    request = controller(straight(offset_y=0.5)).step(STAMP, STRAIGHT_STATE, no_motion)
    assert request.steering_wheel_angle_rad == pytest.approx(
        VP0.steering_ratio * 0.025 * 0.5, rel=1e-6)


def test_ego_motion_since_stamp_is_compensated():
    """Ego moved 0.2 m left since the stamp, so the path on y = 0 is now on the right."""
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
    assert late.steering_wheel_angle_rad != 0.0  # last command is held


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

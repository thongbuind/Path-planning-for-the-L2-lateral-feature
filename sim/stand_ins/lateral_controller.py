"""Stand-in Lateral Controller of the evaluation side.

Software Qualification Test Specification 4.6 (`#sim-controller`). It is a closed-loop
test tool, fixed for every planner version. It is not a G1 deliverable: the real
Lateral Controller is out of scope (Software Requirements Specification section 1).

Control law, per front wheel:

    delta = L * kappa_ff + K * v^2 * kappa_ff + k_y * e_y + k_psi * e_psi

- kappa_ff is read at now + actuator_delay, so the controller compensates the delay
  after the planner (PP-ADR-010, PP-ASM-017).
- e_y, e_psi are read at a 0.5 s preview: the path point at now + 0.5 s against the
  ego pose predicted 0.5 s ahead.
- Path yaw is the direction of travel of base_link (Interface Control Document 6.1),
  so e_psi compares it with the car's direction of travel: body heading plus
  atan(v_y / v) at base_link. In a curve the two differ by the rear-axle slip angle.
- K comes from the simulator vehicle model, not from VehicleConfig.

Output is a steering wheel angle request (the stand-in EPS takes an angle).
"""

from dataclasses import dataclass
from math import atan2, cos, isfinite, pi, sin

from interfaces import (
    PATH_STATUS_TIMEOUT_US,
    TRAJECTORY_HORIZON_S,
    TRAJECTORY_STEP_S,
    TRAJECTORY_TIMEOUT_US,
    ActiveFunction,
    EgoMotionQuery,
    EgoMotionRequest,
    PathStatus,
    Pose2D,
    Trajectory,
    VehicleConfig,
)
from sim.messages import SteeringRequest

US_PER_S = 1_000_000

# Fixed values of Software Qualification Test Specification 4.6.
CONTROLLER_PERIOD_US = 10_000  # 100 Hz
PREVIEW_S = 0.5  # Look-ahead for e_y, e_psi

# k_y, k_psi are tuned once and then kept fixed (Software Qualification Test
# Specification 4.6). Start values from the closed-loop prototype, nhóm tự thống nhất.
LATERAL_GAIN_RAD_PER_M = 0.025
HEADING_GAIN = 0.16  # [rad/rad]

_YAW_RATE_EPS = 1e-6  # [rad/s], below this the ego prediction is a straight line
_SLIP_MIN_SPEED_MPS = 1.0  # Below this the direction of travel is not defined well


@dataclass(frozen=True, slots=True)
class EgoState:
    """Ego motion now, as the controller sees it from chassis signals."""

    speed_mps: float  # Longitudinal speed
    lateral_speed_mps: float  # v_y at base_link
    yaw_rate_rps: float


@dataclass(frozen=True, slots=True)
class _PathSample:
    pose: Pose2D
    curvature: float


def wrap_angle(angle: float) -> float:
    """Wrap to [-pi, pi)."""
    return (angle + pi) % (2 * pi) - pi


def to_frame(pose: Pose2D, frame: Pose2D) -> Pose2D:
    """Express `pose` in the frame whose origin and heading are `frame`."""
    dx, dy = pose.x - frame.x, pose.y - frame.y
    c, s = cos(frame.yaw), sin(frame.yaw)
    return Pose2D(c * dx + s * dy, -s * dx + c * dy, wrap_angle(pose.yaw - frame.yaw))


def predict_pose(state: EgoState, horizon_s: float) -> Pose2D:
    """Ego pose after `horizon_s` with constant speed, lateral speed and yaw rate."""
    r = state.yaw_rate_rps
    v, vy = state.speed_mps, state.lateral_speed_mps
    yaw = r * horizon_s
    if abs(r) < _YAW_RATE_EPS:
        return Pose2D(v * horizon_s, vy * horizon_s, yaw)
    x = (v * sin(yaw) + vy * (cos(yaw) - 1.0)) / r
    y = (v * (1.0 - cos(yaw)) + vy * sin(yaw)) / r
    return Pose2D(x, y, yaw)


def sample_trajectory(trajectory: Trajectory, time_s: float) -> _PathSample | None:
    """Linear interpolation in time between two points (Interface Control Document 6.1).

    Returns None outside the 0-3 s horizon.
    """
    if not 0.0 <= time_s <= TRAJECTORY_HORIZON_S:
        return None
    index = time_s / TRAJECTORY_STEP_S
    lower = min(int(index), len(trajectory.points) - 2)
    a, b = trajectory.points[lower], trajectory.points[lower + 1]
    f = index - lower
    pose = Pose2D(
        a.pose.x + f * (b.pose.x - a.pose.x),
        a.pose.y + f * (b.pose.y - a.pose.y),
        wrap_angle(a.pose.yaw + f * wrap_angle(b.pose.yaw - a.pose.yaw)),
    )
    return _PathSample(pose, a.curvature + f * (b.curvature - a.curvature))


class LateralController:
    """Receiver keeps the newest message of each input and runs every 10 ms."""

    def __init__(
        self,
        vehicle: VehicleConfig,
        understeer_gradient: float,
        lateral_gain: float = LATERAL_GAIN_RAD_PER_M,
        heading_gain: float = HEADING_GAIN,
    ) -> None:
        """`understeer_gradient` K [rad/(m/s^2)] comes from the simulator vehicle model."""
        if not isfinite(understeer_gradient):
            raise ValueError("understeer_gradient must be finite")
        self.vehicle = vehicle
        self.understeer_gradient = understeer_gradient
        self.lateral_gain = lateral_gain
        self.heading_gain = heading_gain
        self._trajectory: Trajectory | None = None
        self._trajectory_rx_us = 0
        self._status: PathStatus | None = None
        self._status_rx_us = 0
        self._last_angle = 0.0

    def on_trajectory(self, message: Trajectory, rx_us: int) -> None:
        self._trajectory, self._trajectory_rx_us = message, rx_us

    def on_path_status(self, message: PathStatus, rx_us: int) -> None:
        self._status, self._status_rx_us = message, rx_us

    def step(self, now_us: int, state: EgoState, ego_motion: EgoMotionQuery) -> SteeringRequest:
        angle = self._command(now_us, state, ego_motion)
        if angle is None:
            return SteeringRequest(now_us, self._last_angle, active=False)
        self._last_angle = angle
        return SteeringRequest(now_us, angle, active=True)

    def _usable_trajectory(self, now_us: int) -> Trajectory | None:
        """Path is usable only when both messages are fresh and a function is driving."""
        trajectory, status = self._trajectory, self._status
        if trajectory is None or status is None:
            return None
        if now_us - self._trajectory_rx_us > TRAJECTORY_TIMEOUT_US:
            return None
        if now_us - self._status_rx_us > PATH_STATUS_TIMEOUT_US:
            return None
        if not (trajectory.header.valid and status.header.valid and status.path_valid):
            return None
        if status.active_function == ActiveFunction.NONE:
            return None
        return trajectory

    def _command(self, now_us: int, state: EgoState, ego_motion: EgoMotionQuery) -> float | None:
        trajectory = self._usable_trajectory(now_us)
        if trajectory is None:
            return None
        stamp_us = trajectory.header.stamp_us
        if now_us < stamp_us:
            return None

        # Motion since the path stamp: brings path points into the current base_link.
        motion = ego_motion(EgoMotionRequest(stamp_us, now_us))
        if not motion.valid:
            return None
        ego_now = Pose2D(motion.dx, motion.dy, motion.dyaw)

        elapsed_s = (now_us - stamp_us) / US_PER_S
        feedforward = sample_trajectory(trajectory, elapsed_s + self.vehicle.actuator_delay)
        target = sample_trajectory(trajectory, elapsed_s + PREVIEW_S)
        if feedforward is None or target is None:
            return None

        # Errors of the preview point in the predicted ego frame.
        target_now = to_frame(target.pose, ego_now)
        error = to_frame(target_now, predict_pose(state, PREVIEW_S))

        v = state.speed_mps
        # Path yaw is a direction of travel: compare with the car's, not its body heading.
        slip = atan2(state.lateral_speed_mps, v) if v > _SLIP_MIN_SPEED_MPS else 0.0
        heading_error = wrap_angle(error.yaw - slip)
        kappa = feedforward.curvature
        wheel_angle = (
            self.vehicle.wheelbase * kappa
            + self.understeer_gradient * v * v * kappa
            + self.lateral_gain * error.y
            + self.heading_gain * heading_error
        )
        if not isfinite(wheel_angle):
            return None
        limit = self.vehicle.max_wheel_angle
        wheel_angle = min(limit, max(-limit, wheel_angle))
        return self.vehicle.steering_ratio * wheel_angle

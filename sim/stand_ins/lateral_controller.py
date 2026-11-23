from dataclasses import dataclass
from math import atan2, cos, isfinite, pi, sin

from interfaces import (
    TRAJECTORY_HORIZON_S,
    TRAJECTORY_STEP_S,
    TRAJECTORY_TIMEOUT_US,
    EgoMotionQuery,
    EgoMotionRequest,
    PlannerId,
    Pose2D,
    Trajectory,
    VehicleConfig,
)
from sim.messages import SteeringRequest
from sim.stand_ins.arbitrator import PATH_STATUS_TIMEOUT_US, ActiveFunction, SystemStatus

US_PER_S = 1_000_000

CONTROLLER_PERIOD_US = 10_000
PREVIEW_S = 0.5

LATERAL_GAIN_RAD_PER_M = 0.025
HEADING_GAIN = 0.16

_YAW_RATE_EPS = 1e-6  # Yaw rate dưới ngưỡng này dùng dự báo đường thẳng.
_SLIP_MIN_SPEED_MPS = 1.0  # Ở tốc độ rất nhỏ, hướng chuyển động từ vận tốc không còn ổn định.


@dataclass(frozen=True, slots=True)
class EgoState:
    speed_mps: float
    lateral_speed_mps: float
    yaw_rate_rps: float
    driver_override: bool = False


@dataclass(frozen=True, slots=True)
class _PathSample:
    pose: Pose2D
    curvature: float


@dataclass(slots=True)
class HwaCommandStats:
    samples: int = 0
    limited: int = 0
    squared_tracking_error_m2: float = 0.0
    peak_tracking_error_m: float = 0.0

    def observe(self, tracking_error_m: float, limited: bool) -> None:
        self.samples += 1
        self.limited += int(limited)
        self.squared_tracking_error_m2 += tracking_error_m ** 2
        self.peak_tracking_error_m = max(self.peak_tracking_error_m, abs(tracking_error_m))


def wrap_angle(angle: float) -> float:
    return (angle + pi) % (2 * pi) - pi


def to_frame(pose: Pose2D, frame: Pose2D) -> Pose2D:
    dx, dy = pose.x - frame.x, pose.y - frame.y
    c, s = cos(frame.yaw), sin(frame.yaw)
    return Pose2D(c * dx + s * dy, -s * dx + c * dy, wrap_angle(pose.yaw - frame.yaw))


def predict_pose(state: EgoState, horizon_s: float) -> Pose2D:
    r = state.yaw_rate_rps
    v, vy = state.speed_mps, state.lateral_speed_mps
    yaw = r * horizon_s
    if abs(r) < _YAW_RATE_EPS:
        return Pose2D(v * horizon_s, vy * horizon_s, yaw)
    x = (v * sin(yaw) + vy * (cos(yaw) - 1.0)) / r
    y = (v * (1.0 - cos(yaw)) + vy * sin(yaw)) / r
    return Pose2D(x, y, yaw)


def sample_trajectory(trajectory: Trajectory, time_s: float) -> _PathSample | None:
    """Nội suy theo thời gian giữa hai điểm. Ngoài khoảng 0–3 s của ICD thì trả None."""
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
    def __init__(
        self,
        vehicle: VehicleConfig,
        understeer_gradient: float,
        lateral_gain: float = LATERAL_GAIN_RAD_PER_M,
        heading_gain: float = HEADING_GAIN,
    ) -> None:
        if not isfinite(understeer_gradient):
            raise ValueError("understeer_gradient must be finite")
        self.vehicle = vehicle
        self.understeer_gradient = understeer_gradient
        self.lateral_gain = lateral_gain
        self.heading_gain = heading_gain
        self._trajectory: Trajectory | None = None
        self._trajectory_rx_us = 0
        self._status: SystemStatus | None = None
        self._status_rx_us = 0
        self._last_angle = 0.0
        self.hwa_command_stats = HwaCommandStats()

    def on_trajectory(self, message: Trajectory, rx_us: int) -> None:
        self._trajectory, self._trajectory_rx_us = message, rx_us

    def on_path_status(self, message: SystemStatus, rx_us: int) -> None:
        self._status, self._status_rx_us = message, rx_us

    def step(self, now_us: int, state: EgoState, ego_motion: EgoMotionQuery) -> SteeringRequest:
        angle = self._command(now_us, state, ego_motion)
        if angle is None:
            return SteeringRequest(now_us, self._last_angle, active=False)
        self._last_angle = angle
        return SteeringRequest(now_us, angle, active=True)

    def _usable_trajectory(self, now_us: int) -> Trajectory | None:
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

    def _controlling_hwa(self, state: EgoState) -> bool:
        status, trajectory = self._status, self._trajectory
        return (not state.driver_override and status is not None and trajectory is not None
                and status.active_function == ActiveFunction.LCC and status.chosen == PlannerId.LCC
                and trajectory.planner_id == PlannerId.LCC)

    def _limit_wheel_angle(self, now_us: int, state: EgoState, wheel_angle: float) -> float:
        return wheel_angle

    def _command(self, now_us: int, state: EgoState, ego_motion: EgoMotionQuery) -> float | None:
        trajectory = self._usable_trajectory(now_us)
        if trajectory is None:
            return None
        stamp_us = trajectory.header.stamp_us
        if now_us < stamp_us:
            return None

        motion = ego_motion(EgoMotionRequest(stamp_us, now_us))
        if not motion.valid:
            return None
        ego_now = Pose2D(motion.dx, motion.dy, motion.dyaw)

        elapsed_s = (now_us - stamp_us) / US_PER_S
        feedforward = sample_trajectory(trajectory, elapsed_s + self.vehicle.actuator_delay)
        target = sample_trajectory(trajectory, elapsed_s + PREVIEW_S)
        if feedforward is None or target is None:
            return None

        # Yaw của path là hướng chuyển động, nên so với hướng vận tốc của xe thay vì hướng thân
        # xe.
        target_now = to_frame(target.pose, ego_now)
        error = to_frame(target_now, predict_pose(state, PREVIEW_S))

        v = state.speed_mps
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
        physical_angle = min(limit, max(-limit, wheel_angle))
        if self._controlling_hwa(state):
            bounded = self._limit_wheel_angle(now_us, state, wheel_angle)
            wheel_angle = min(limit, max(-limit, bounded))
            self.hwa_command_stats.observe(error.y, wheel_angle != physical_angle)
        else:
            wheel_angle = physical_angle
        return self.vehicle.steering_ratio * wheel_angle

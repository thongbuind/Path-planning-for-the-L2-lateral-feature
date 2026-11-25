"""Sinh từ interfaces/gen.py và interfaces/schema. ICD 6.1."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from interfaces._validate import check_array, check_enum
from interfaces.conventions import Header, Pose2D


TRAJECTORY_POINTS = 31
TRAJECTORY_STEP_S = 0.1
TRAJECTORY_HORIZON_S = 3.0
TRAJECTORY_TIMEOUT_US = 75000


class PlannerId(IntEnum):
    """Planner đã phát message (PP-SWR-019)."""

    LCC = 0
    LKA_ELK = 1


@dataclass(frozen=True, slots=True)
class TrajectoryPoint:
    time_from_start: float  # [s]
    pose: Pose2D  # base_link tại header.stamp_us; yaw là hướng tiếp tuyến của path.
    longitudinal_velocity_mps: float  # [m/s]
    lateral_velocity_mps: float  # [m/s]; d_dot theo đường tham chiếu; khác v_y của thân xe.
    acceleration_mps2: float  # [m/s^2]
    heading_rate_rps: float  # [rad/s]
    curvature: float  # [1/m]
    front_wheel_angle_rad: float  # [rad]
    rear_wheel_angle_rad: float  # [rad]; Luôn bằng 0.


@dataclass(frozen=True, slots=True)
class Trajectory:
    header: Header  # stamp_us = t0 trong khung BASE_LINK.
    points: tuple[TrajectoryPoint, ...]
    observed_horizon_s: float  # [s]; Thời gian tới lúc path rời phạm vi lane model đã quan sát. Các điểm sau đó được ngoại suy (PP-SWR-018).
    planner_id: PlannerId

    def __post_init__(self) -> None:
        check_array(self, "points", TRAJECTORY_POINTS)
        check_enum(self, "planner_id", PlannerId)

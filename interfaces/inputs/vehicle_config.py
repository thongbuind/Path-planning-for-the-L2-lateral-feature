"""Sinh từ interfaces/gen.py và interfaces/schema. ICD 5.8."""

from __future__ import annotations

from dataclasses import dataclass



MAX_VEHICLE_WIDTH_M = 2.5  # Tính cả gương, QCVN 09:2015/BGTVT 2.1.1.1 b.


@dataclass(frozen=True, slots=True)
class VehicleConfig:
    """Nguồn tham số xe của planner."""

    wheelbase: float  # [m]
    rear_axle_to_cg: float  # [m]
    vehicle_width: float  # [m]; Tính cả gương.
    steering_ratio: float  # [-]
    max_wheel_angle: float  # [rad]
    max_steering_wheel_rate: float  # [rad/s]
    actuator_delay: float  # [s]; Độ trễ danh định của EPS.

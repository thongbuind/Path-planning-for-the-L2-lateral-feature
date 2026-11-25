"""Thông điệp nội bộ của simulator, ngoài hợp đồng planner trong ICD."""

from dataclasses import dataclass

from interfaces import Side


@dataclass(frozen=True, slots=True)
class DriverSignals:
    torque_nm: float = 0.0
    indicator: Side = Side.NONE
    hands_on: bool = False
    esc_enabled: bool = True
    esc_active: bool = False


@dataclass(frozen=True, slots=True)
class SteeringRequest:
    """Khi active là false, góc lệnh giữ giá trị trước đó và EPS chuyển dần quyền lái cho tài xế."""

    stamp_us: int
    steering_wheel_angle_rad: float
    active: bool

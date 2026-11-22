"""Sinh từ interfaces/gen.py và interfaces/schema. ICD 5.7."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from interfaces._validate import check_array, check_enum, check_uint
from interfaces.conventions import Header


LONGITUDINAL_PLAN_POINTS = 31  # Cùng lưới 0,1 s với Trajectory.
LONGITUDINAL_PLAN_TIMEOUT_US = 75000
LONGITUDINAL_PLAN_MAX_DELTA_COUNTER = 4  # Bước counter lớn nhất theo ICD 4: floor((75 + 25) / 25), với thời gian tính bằng ms.
LONGITUDINAL_PLAN_MAX_AGE_US = 45000
LONGITUDINAL_PLAN_V_MAX_MPS = 182.04  # Biên trên của v, theo ESC_Speed tối đa 655,35 km/h (ICD 5.3).
LONGITUDINAL_PLAN_A_MAX_MPS2 = 32.767  # Biên của |a| theo miền AccelX của IMU_Data (ICD 5.3).


class LongitudinalMode(IntEnum):
    OFF = 0
    CRUISE = 1
    FOLLOW = 2
    CURVE_LIMIT = 3


@dataclass(frozen=True, slots=True)
class LongitudinalPoint:
    v: float  # [m/s]
    a: float  # [m/s^2]


@dataclass(frozen=True, slots=True)
class LongitudinalPlan:
    header: Header
    mode: LongitudinalMode
    points: tuple[LongitudinalPoint, ...]
    target_id: int  # 0 khi không có mục tiêu.

    def __post_init__(self) -> None:
        check_enum(self, "mode", LongitudinalMode)
        check_array(self, "points", LONGITUDINAL_PLAN_POINTS)
        check_uint(self.target_id, 32, "target_id")

"""Sinh từ interfaces/gen.py và interfaces/schema. ICD 5.9."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from interfaces._validate import check_enum, check_uint
from interfaces.conventions import Header


LEAD_TARGET_TIMEOUT_US = 150000
LEAD_TARGET_MAX_DELTA_COUNTER = 3  # Bước counter lớn nhất theo ICD 4: floor((150 + 25) / 50), với thời gian tính bằng ms.
LEAD_TARGET_MAX_AGE_US = 250000


class LeadClass(IntEnum):
    """Chỉ dùng CAR và TRUCK cho FOLLOW (PP-SWR-170, 176)."""

    UNKNOWN = 0
    CAR = 1
    TRUCK = 2
    MOTORCYCLE = 3
    OTHER = 4


@dataclass(frozen=True, slots=True)
class LeadTarget:
    """Tâm xe mục tiêu của ACC, trong base_link lúc đo. header.valid = false khi không có xe mục tiêu."""

    header: Header
    id: int  # Ổn định giữa các frame; dùng để so với LongitudinalPlan.target_id.
    classification: LeadClass
    x: float  # [m]
    y: float  # [m]
    gap: float  # [m]; Từ cản trước xe ego tới cản sau xe mục tiêu.
    heading: float  # [rad]; Hướng xe mục tiêu so với trục x của base_link.
    vx_rel: float  # [m/s]; Vận tốc xe mục tiêu trừ vận tốc ego, chiếu lên trục dọc base_link.
    vy_rel: float  # [m/s]; Thành phần ngang của vận tốc tương đối trong base_link.
    existence_probability: float  # [0..1]

    def __post_init__(self) -> None:
        check_uint(self.id, 32, "id")
        check_enum(self, "classification", LeadClass)

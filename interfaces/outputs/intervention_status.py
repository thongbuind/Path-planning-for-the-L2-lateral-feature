"""Sinh từ interfaces/gen.py và interfaces/schema. ICD 6.3."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from interfaces._validate import check_enum
from interfaces.conventions import BasicHeader


INTERVENTION_STATUS_TIMEOUT_US = 75000


class InterventionFunction(IntEnum):
    NONE = 0
    LKA = 1
    ELK = 2


class InterventionPhase(IntEnum):
    NONE = 0
    ACTIVE = 1
    COMPLETED = 2


@dataclass(frozen=True, slots=True)
class InterventionStatus:
    header: BasicHeader
    path_valid: bool  # Đầu vào đủ hợp lệ để dựng path khi có yêu cầu. Cờ có thể true khi chưa can thiệp.
    active_function: InterventionFunction  # NONE khi thiếu yêu cầu hoặc path_valid là false.
    lka_phase: InterventionPhase
    elk_phase: InterventionPhase
    lateral_limit_reached: bool  # Path bị cắt theo giới hạn a_y hoặc jerk khi LKA/ELK hoạt động. Chỉ dùng ghi log.

    def __post_init__(self) -> None:
        check_enum(self, "active_function", InterventionFunction)
        check_enum(self, "lka_phase", InterventionPhase)
        check_enum(self, "elk_phase", InterventionPhase)

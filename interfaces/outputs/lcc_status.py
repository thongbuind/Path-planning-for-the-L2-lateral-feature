"""Sinh từ interfaces/gen.py và interfaces/schema. ICD 6.2."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from interfaces._validate import check_enum
from interfaces.conventions import BasicHeader


LCC_STATUS_TIMEOUT_US = 75000


class LccMode(IntEnum):
    """Cách LCC dựng path (PP-SWR-177)."""

    NONE = 0
    LANE = 1
    INFERRED = 2
    FOLLOW = 3
    COAST = 4


@dataclass(frozen=True, slots=True)
class LccStatus:
    header: BasicHeader
    path_valid: bool
    lcc_mode: LccMode  # NONE khi LCC không ở REQUEST hoặc path_valid là false.
    follow_distance: float  # [m]; Quãng đường từ đầu FOLLOW, bằng 0 ở mode khác. Chỉ dùng để ghi log và hiển thị.
    lateral_limit_reached: bool
    lane_too_narrow: bool

    def __post_init__(self) -> None:
        check_enum(self, "lcc_mode", LccMode)

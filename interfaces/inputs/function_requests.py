"""Sinh từ interfaces/gen.py và interfaces/schema. ICD 5.6."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from interfaces._validate import check_array, check_enum
from interfaces.conventions import BasicHeader, Side


FUNCTIONS = 3  # Thứ tự requests: LCC, LKA, ELK.
FUNCTION_REQUESTS_TIMEOUT_US = 75000
FUNCTION_REQUESTS_MAX_DELTA_COUNTER = 4  # Bước counter lớn nhất theo ICD 4: floor((75 + 25) / 25), với thời gian tính bằng ms.
FUNCTION_REQUESTS_MAX_AGE_US = 45000


class RequestState(IntEnum):
    OFF = 0
    UNAVAILABLE = 1
    STANDBY = 2
    REQUEST = 3
    FAULT = 4


class ElkReason(IntEnum):
    NONE = 0
    SOLID_LINE = 1
    ROAD_EDGE = 2
    ONCOMING = 3
    OVERTAKING = 4


class CancelReason(IntEnum):
    NONE = 0
    DRIVER_OVERRIDE = 1
    INDICATOR = 2
    SPEED = 3
    LANE_QUALITY = 4
    ESC = 5
    FAULT = 6


@dataclass(frozen=True, slots=True)
class FunctionRequest:
    state: RequestState
    side: Side  # Phía xe đang lệch. LCC dùng NONE.
    tlc: float  # [s]; Khối ADAS tính TLC. LCC không dùng giá trị này.
    elk_reason: ElkReason  # ROAD_EDGE chọn mép đường đã quan sát cho ELK. Giá trị khác chỉ dùng ghi log.
    cancel_reason: CancelReason  # Chỉ dùng ghi log.

    def __post_init__(self) -> None:
        check_enum(self, "state", RequestState)
        check_enum(self, "side", Side)
        check_enum(self, "elk_reason", ElkReason)
        check_enum(self, "cancel_reason", CancelReason)


@dataclass(frozen=True, slots=True)
class FunctionRequests:
    header: BasicHeader  # stamp_us theo thời điểm phát.
    requests: tuple[FunctionRequest, ...]
    driver_override: bool

    def __post_init__(self) -> None:
        check_array(self, "requests", FUNCTIONS)

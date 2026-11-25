"""Sinh từ interfaces/gen.py và interfaces/schema. ICD 4."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from interfaces._validate import check_enum, check_uint


COUNTER_MODULO = 256


class FrameId(IntEnum):
    BASE_LINK = 0


class Side(IntEnum):
    NONE = 0
    LEFT = 1
    RIGHT = 2


@dataclass(frozen=True, slots=True)
class Header:
    stamp_us: int  # [us]; Thời điểm mà dữ liệu mô tả, theo đồng hồ bên phát (gPTP).
    counter: int  # Tăng 1 mỗi lần phát, quay vòng tại 256.
    valid: bool  # Hiệu lực của toàn message.
    frame_id: FrameId  # BASE_LINK có gốc tại tâm trục sau; x tiến, y trái, z lên.

    def __post_init__(self) -> None:
        check_uint(self.stamp_us, 64, "stamp_us")
        check_uint(self.counter, 8, "counter")
        check_enum(self, "frame_id", FrameId)


@dataclass(frozen=True, slots=True)
class BasicHeader:
    """Header không có frame_id, dùng cho trạng thái, yêu cầu và chassis signals."""

    stamp_us: int  # [us]
    counter: int
    valid: bool

    def __post_init__(self) -> None:
        check_uint(self.stamp_us, 64, "stamp_us")
        check_uint(self.counter, 8, "counter")


@dataclass(frozen=True, slots=True)
class Pose2D:
    x: float  # [m]
    y: float  # [m]
    yaw: float  # [rad]

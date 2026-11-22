"""Sinh từ interfaces/gen.py và interfaces/schema. ICD 5.5."""

from __future__ import annotations

from dataclasses import dataclass

from interfaces._validate import check_uint


EGO_MOTION_WINDOW_US = 500000  # t1 và t2 trong 0,5 s vừa qua.


@dataclass(frozen=True, slots=True)
class EgoMotionRequest:
    t1_us: int  # [us]
    t2_us: int  # [us]

    def __post_init__(self) -> None:
        check_uint(self.t1_us, 64, "t1_us")
        check_uint(self.t2_us, 64, "t2_us")


@dataclass(frozen=True, slots=True)
class EgoMotionResponse:
    """Chuyển động base_link từ t1 đến t2, có trượt ngang, biểu diễn trong base_link tại t1."""

    valid: bool  # Có thể là false khi bánh xe bị trượt.
    dx: float  # [m]
    dy: float  # [m]
    dyaw: float  # [rad]

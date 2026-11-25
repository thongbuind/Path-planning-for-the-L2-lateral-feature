"""Sinh từ interfaces/gen.py và interfaces/schema. ICD 5.1."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from interfaces._validate import check_array, check_enum
from interfaces.conventions import Header, Side


LANE_LINES = 4  # Thứ tự lines: L2, L1, R1, R2.
ROAD_EDGES = 2  # Thứ tự road_edges: trái, phải.
LANE_MODEL_TIMEOUT_US = 150000
LANE_MODEL_MAX_DELTA_COUNTER = 3  # Bước counter lớn nhất theo ICD 4: floor((150 + 25) / 50), với thời gian tính bằng ms.
LANE_MODEL_MAX_AGE_US = 250000


class LineType(IntEnum):
    DASHED = 0
    SOLID = 1
    DOUBLE = 2
    UNKNOWN = 3


class LineStatus(IntEnum):
    MEASURED = 0
    PREDICTED = 1
    LOST = 2


class RoadEdgeType(IntEnum):
    CURB = 0
    GRASS_GRAVEL = 1
    BARRIER = 2
    GUARDRAIL = 3
    WALL = 4
    UNKNOWN = 5


class LaneWidthSource(IntEnum):
    MEASURED = 0
    REMEMBERED = 1


@dataclass(frozen=True, slots=True)
class LaneLine:
    """y(x) = c0 + c1 x + c2 x² + c3 x³ trong base_link lúc chụp."""

    c0: float  # [m]
    c1: float  # [-]
    c2: float  # [1/m]
    c3: float  # [1/m^2]
    variance: tuple[float, ...]  # Phương sai theo thứ tự c0 tới c3.
    view_range_start: float  # [m]
    view_range_end: float  # [m]
    confidence: float  # [0..1]
    type: LineType
    crossable: bool
    status: LineStatus
    predicted_duration: float  # [s]

    def __post_init__(self) -> None:
        check_array(self, "variance", 4)
        check_enum(self, "type", LineType)
        check_enum(self, "status", LineStatus)


@dataclass(frozen=True, slots=True)
class RoadEdge:
    c0: float  # [m]
    c1: float  # [-]
    c2: float  # [1/m]
    c3: float  # [1/m^2]
    variance: tuple[float, ...]
    view_range_start: float  # [m]
    view_range_end: float  # [m]
    confidence: float  # [0..1]
    type: RoadEdgeType
    status: LineStatus
    predicted_duration: float  # [s]

    def __post_init__(self) -> None:
        check_array(self, "variance", 4)
        check_enum(self, "type", RoadEdgeType)
        check_enum(self, "status", LineStatus)


@dataclass(frozen=True, slots=True)
class LaneModel:
    header: Header  # stamp_us theo thời điểm chụp.
    lines: tuple[LaneLine, ...]
    road_edges: tuple[RoadEdge, ...]
    lane_width: float  # [m]
    lane_width_source: LaneWidthSource
    lane_change: Side  # Đặt sau khi Lane Model đổi ID vạch theo làn mới.

    def __post_init__(self) -> None:
        check_array(self, "lines", LANE_LINES)
        check_array(self, "road_edges", ROAD_EDGES)
        check_enum(self, "lane_width_source", LaneWidthSource)
        check_enum(self, "lane_change", Side)

"""Lane camera and Lane Model (Software Qualification Test Specification 4.5).

Takes the lane geometry within the view range, moves it into base_link at capture
time and fits a cubic to each line of the three lanes. No fault injection yet
(section 6), so this is the noise-free baseline; road edges are not reported.

Numbers of this model, all on the test side:

| Value | Source |
|---|---|
| 20 Hz | Interface Control Document 5.1 |
| Latency capture -> send 100 ms | Nominal; worst case 120 ms is PP-ASM-001 |
| View range 0-80 m | nhóm tự thống nhất, no source yet; to be fixed in the test specification |
| Reported sigma c0 0.03 m, c1 0.002 | F01 a (daytime) of the test specification |
"""

from dataclasses import dataclass
from math import cos, sin

import numpy as np

from interfaces import (
    FrameId,
    Header,
    LaneLine,
    LaneModel,
    LaneWidthSource,
    LineStatus,
    LineType,
    RoadEdge,
    RoadEdgeType,
    Side,
)
from sim.world.road import Road

PERIOD_US = 50_000
LATENCY_US = 100_000
VIEW_START_M = 0.0
VIEW_END_M = 80.0
SIGMA_C0_M = 0.03
SIGMA_C1 = 0.002
CONFIDENCE = 1.0  # Ideal camera
# L2, L1, R1, R2 on a three-lane road with the ego lane in the middle.
LINE_TYPES = (LineType.SOLID, LineType.DASHED, LineType.DASHED, LineType.SOLID)

_LOST_EDGE = RoadEdge(0.0, 0.0, 0.0, 0.0, (0.0,) * 4, 0.0, 0.0, 0.0,
                      RoadEdgeType.UNKNOWN, LineStatus.LOST, 0.0)


@dataclass(frozen=True, slots=True)
class CameraPose:
    """base_link pose in the world at capture time."""

    x: float
    y: float
    yaw: float
    s_hint: float  # Arc length of the car on the road, to cut the road around it


class LaneCamera:
    def __init__(self, road: Road, view_end_m: float = VIEW_END_M) -> None:
        self.road = road
        self.view_end_m = view_end_m
        self._counter = 0

    def _line(self, offset: float, line_type: LineType, pose: CameraPose) -> LaneLine:
        xs, ys = self.road.parallel(offset, pose.s_hint - 10.0, pose.s_hint + self.view_end_m + 20.0)
        c, s = cos(pose.yaw), sin(pose.yaw)
        dx, dy = xs - pose.x, ys - pose.y
        bx = c * dx + s * dy
        by = -s * dx + c * dy
        keep = (bx >= VIEW_START_M) & (bx <= self.view_end_m)
        if np.count_nonzero(keep) < 4:
            return LaneLine(0.0, 0.0, 0.0, 0.0, (0.0,) * 4, 0.0, 0.0, 0.0,
                            line_type, line_type == LineType.DASHED, LineStatus.LOST, 0.0)
        bx, by = bx[keep], by[keep]
        c3, c2, c1, c0 = np.polyfit(bx, by, 3)
        variance = (SIGMA_C0_M ** 2, SIGMA_C1 ** 2, 0.0, 0.0)
        return LaneLine(float(c0), float(c1), float(c2), float(c3), variance,
                        float(bx.min()), float(bx.max()), CONFIDENCE, line_type,
                        line_type == LineType.DASHED, LineStatus.MEASURED, 0.0)

    def capture(self, now_us: int, pose: CameraPose) -> LaneModel:
        lines = tuple(self._line(off, kind, pose)
                      for off, kind in zip(self.road.line_offsets(), LINE_TYPES))
        msg = LaneModel(Header(now_us, self._counter, True, FrameId.BASE_LINK), lines,
                        (_LOST_EDGE, _LOST_EDGE), self.road.lane_width,
                        LaneWidthSource.MEASURED, Side.NONE)
        self._counter = (self._counter + 1) % 256
        return msg

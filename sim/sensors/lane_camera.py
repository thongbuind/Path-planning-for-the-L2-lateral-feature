"""Lane camera and Lane Model (Software Qualification Test Specification 4.5).

Takes the lane geometry within the view range, moves it into base_link at capture
time and fits a cubic to each visible marking and road edge. Lane faults are applied
after capture. The ideal ADAS input uses the same geometry with zero reported variance.

Numbers of this model, all on the test side:

| Value | Source |
|---|---|
| 20 Hz | Interface Control Document 5.1 |
| Latency capture -> send 100 ms | Nominal; worst case 120 ms is PP-ASM-001 |
| View range 0-80 m | nhóm tự thống nhất, no source yet (test specification 4.5); start and end set per scenario |
| Reported sigma c0 0.03 m, c1 0.002 | F01 a (daytime) of the test specification |

Lane change (S17): the lines are indexed around the lane base_link is in. When base_link
passes more than half a lane width from the centre of the current lane, the camera re-indexes
L2, L1, R1, R2 to the new lane and sets `lane_change` to that side in that frame only
(Interface Control Document 5.1). A line beyond the road layout is LOST. On the lane of the
road's reference line the layout is used as it is.
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
from sim.world.road import Marking, Road, RoadEdgeSpec, lane_boundaries

PERIOD_US = 50_000
LATENCY_US = 100_000
VIEW_START_M = 0.0
VIEW_END_M = 80.0
SIGMA_C0_M = 0.03
SIGMA_C1 = 0.002
CONFIDENCE = 1.0  # Ideal camera
_ZERO_VARIANCE = (0.0,) * 4
_LOST_LINE = LaneLine(0.0, 0.0, 0.0, 0.0, _ZERO_VARIANCE, 0.0, 0.0, 0.0,
                      LineType.UNKNOWN, False, LineStatus.LOST, 0.0)
_LOST_EDGE = RoadEdge(0.0, 0.0, 0.0, 0.0, _ZERO_VARIANCE, 0.0, 0.0, 0.0,
                      RoadEdgeType.UNKNOWN, LineStatus.LOST, 0.0)


@dataclass(frozen=True, slots=True)
class CameraPose:
    """base_link pose in the world at capture time."""

    x: float
    y: float
    yaw: float
    s_hint: float  # Arc length of the car on the road, to cut the road around it


class LaneCamera:
    def __init__(self, road: Road, view_end_m: float = VIEW_END_M, *, view_start_m: float = VIEW_START_M,
                 ideal: bool = False) -> None:
        if not 0.0 <= view_start_m < view_end_m:
            raise ValueError("camera view must satisfy 0 <= start < end")
        self.road = road
        self.view_start_m = view_start_m
        self.view_end_m = view_end_m
        self.variance = _ZERO_VARIANCE if ideal else (SIGMA_C0_M ** 2, SIGMA_C1 ** 2, 0.0, 0.0)
        self._counter = 0
        self.lane_index = 0  # lanes to the left of the reference lane (negative: right)

    def _markings(self) -> tuple[Marking | None, ...]:
        """L2, L1, R1, R2 around the current lane."""
        layout = self.road.layout.markings
        if self.lane_index == 0:
            return layout
        centre = self.lane_index * self.road.lane_width
        known = sorted((m for m in layout if m is not None), key=lambda m: m.offset_m)
        left = [m for m in known if m.offset_m > centre]
        right = [m for m in reversed(known) if m.offset_m < centre]
        pick = lambda side, i: side[i] if len(side) > i else None
        return (pick(left, 1), pick(left, 0), pick(right, 0), pick(right, 1))

    def _lane_change(self, pose: CameraPose) -> Side:
        d = self.road.project(pose.x, pose.y, pose.s_hint).d
        w = self.road.lane_width
        if abs(d - self.lane_index * w) <= 0.5 * w:
            return Side.NONE
        new = round(d / w)
        side = Side.LEFT if new > self.lane_index else Side.RIGHT
        self.lane_index = new
        return side

    def _fit(self, offset: float, pose: CameraPose,
             view_end: float | None = None) -> tuple[float, float, float, float, float, float] | None:
        xs, ys = self.road.parallel(offset, pose.s_hint - 10.0, pose.s_hint + self.view_end_m + 20.0)
        return self._fit_points(xs, ys, pose, view_end)

    def _fit_points(self, xs, ys, pose: CameraPose, view_end: float | None):
        end = self.view_end_m if view_end is None else min(self.view_end_m, view_end)
        c, s = cos(pose.yaw), sin(pose.yaw)
        dx, dy = xs - pose.x, ys - pose.y
        bx = c * dx + s * dy
        by = -s * dx + c * dy
        keep = (bx >= self.view_start_m) & (bx <= end)
        if np.count_nonzero(keep) < 4:
            return None
        bx, by = bx[keep], by[keep]
        c3, c2, c1, c0 = np.polyfit(bx, by, 3)
        return float(c0), float(c1), float(c2), float(c3), float(bx.min()), float(bx.max())

    def _line(self, marking: Marking | None, pose: CameraPose, view_end: float | None) -> LaneLine:
        if marking is None:
            return _LOST_LINE
        return self._line_from_fit(marking, self._fit(marking.offset_m, pose, view_end))

    def _line_from_fit(self, marking, fit) -> LaneLine:
        if fit is None:
            return LaneLine(0.0, 0.0, 0.0, 0.0, _ZERO_VARIANCE, 0.0, 0.0, 0.0,
                            marking.type, marking.crossable, LineStatus.LOST, 0.0)
        c0, c1, c2, c3, start, end = fit
        return LaneLine(c0, c1, c2, c3, self.variance, start, end, CONFIDENCE,
                        marking.type, marking.crossable, LineStatus.MEASURED, 0.0)

    def _edge(self, edge: RoadEdgeSpec | None, pose: CameraPose) -> RoadEdge:
        if edge is None:
            return _LOST_EDGE
        fit = self._fit(edge.offset_m, pose)
        if fit is None:
            return _LOST_EDGE
        c0, c1, c2, c3, start, end = fit
        return RoadEdge(c0, c1, c2, c3, self.variance, start, end, CONFIDENCE,
                        edge.type, LineStatus.MEASURED, 0.0)

    def _variable_lines(self, pose: CameraPose, limits):
        geometry = self.road.layout.geometry
        assert geometry is not None
        projection = self.road.project(pose.x, pose.y, pose.s_hint)
        s = projection.s
        new = geometry.lane_index(s, projection.d, self.lane_index)
        change = Side.NONE
        if new != self.lane_index:
            change = Side.LEFT if new > self.lane_index else Side.RIGHT
            self.lane_index = new
        right, left = lane_boundaries(geometry.id_at_index(new))
        low, high = geometry.bounds(s, new)
        lines = []
        for boundary, side, view_end in zip((left + 1, left, right, right - 1),
                                             (1, 1, -1, -1), limits, strict=True):
            paint = geometry.paint_ahead(boundary, s)
            if paint is None:
                lines.append(_LOST_LINE)
                continue
            xs, ys = self.road.marking_parallel(boundary, side, pose.s_hint - 10.0,
                                                pose.s_hint + self.view_end_m + 20.0)
            fit = self._fit_points(xs, ys, pose, view_end)
            lines.append(self._line_from_fit(paint.marking(0.0, side), fit))
        return tuple(lines), high - low, change

    def capture(self, now_us: int, pose: CameraPose,
                view_limits: tuple[float | None, ...] | None = None) -> LaneModel:
        """view_limits: largest view end per line (L2, L1, R1, R2), from view faults."""
        limits = view_limits if view_limits is not None else (None,) * len(self.road.layout.markings)
        if self.road.layout.geometry is None:
            change = self._lane_change(pose)
            lines = tuple(self._line(marking, pose, limit)
                          for marking, limit in zip(self._markings(), limits, strict=True))
            width = self.road.lane_width
        else:
            lines, width, change = self._variable_lines(pose, limits)
        edges = tuple(self._edge(edge, pose) for edge in self.road.layout.edges)
        msg = LaneModel(Header(now_us, self._counter, True, FrameId.BASE_LINK), lines,
                        edges, width,
                        LaneWidthSource.MEASURED, change)
        self._counter = (self._counter + 1) % 256
        return msg

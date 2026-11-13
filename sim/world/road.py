"""Road ground truth: centre line of the ego lane from a curvature profile.

The road is a chain of segments (straight, clothoid, arc), each given by its length
and the curvature at its end. Curvature is positive to the left. Lane markings and
road edges are expressed as offsets from the road reference line.

Lines, left to right, as in Interface Control Document 5.1: L2, L1, R1, R2.
"""

from bisect import bisect_right
from dataclasses import dataclass
from math import cos, isfinite, sin

import numpy as np

from interfaces import LANE_LINES, ROAD_EDGES, LineType, RoadEdgeType

SAMPLE_STEP_M = 0.1  # Integration and storage step along the centre line


@dataclass(frozen=True, slots=True)
class Segment:
    """`kind`: straight, clothoid (curvature changes linearly) or arc (constant)."""

    kind: str
    length: float  # [m]
    curvature_end: float = 0.0  # [1/m], left positive; ignored for straight

    def __post_init__(self) -> None:
        if self.kind not in ("straight", "clothoid", "arc"):
            raise ValueError(f"unknown segment kind {self.kind!r}")
        if not self.length > 0.0:
            raise ValueError("segment length must be positive")


@dataclass(frozen=True, slots=True)
class LaneProjection:
    s: float  # [m] arc length of the foot point on the ego-lane centre
    d: float  # [m] lateral offset from the centre, left positive
    heading: float  # [rad] centre-line heading at s
    curvature: float  # [1/m] centre-line curvature at s


@dataclass(frozen=True, slots=True)
class Marking:
    offset_m: float  # From the ego-lane centre to the near edge of the paint
    type: LineType
    crossable: bool  # From the ego side, including mixed double markings


@dataclass(frozen=True, slots=True)
class RoadEdgeSpec:
    offset_m: float  # From the ego-lane centre to the physical edge
    type: RoadEdgeType


@dataclass(frozen=True, slots=True)
class WidthPolynomial:
    """One OpenDRIVE width record, relative to the start of its lane section."""

    start_m: float
    a: float
    b: float
    c: float
    d: float

    def at(self, section_s):
        ds = section_s - self.start_m
        return ((self.d * ds + self.c) * ds + self.b) * ds + self.a


@dataclass(frozen=True, slots=True)
class LanePaint:
    width: float
    type: LineType
    crossable_from_left: bool
    crossable_from_right: bool

    def marking(self, offset: float, side: int) -> Marking:
        return Marking(offset - side * self.width / 2, self.type,
                       self.crossable_from_right if side > 0 else self.crossable_from_left)


@dataclass(frozen=True, slots=True)
class Lane:
    id: int
    widths: tuple[WidthPolynomial, ...]
    paint: LanePaint | None
    driving: bool

    def width_at(self, section_s):
        if isinstance(section_s, np.ndarray):
            result = np.empty_like(section_s, dtype=float)
            starts = [record.start_m for record in self.widths]
            indices = np.searchsorted(starts, section_s, side="right") - 1
            for i, record in enumerate(self.widths):
                use = indices == i
                result[use] = record.at(section_s[use])
            return result
        i = bisect_right(self.widths, section_s, key=lambda record: record.start_m) - 1
        return self.widths[i].at(section_s)


def lane_boundaries(lane_id: int) -> tuple[int, int]:
    """Boundary IDs in right-to-left order. Boundary zero is at laneOffset."""
    return (lane_id, lane_id + 1) if lane_id < 0 else (lane_id - 1, lane_id)


@dataclass(frozen=True, slots=True)
class LaneSection:
    start_m: float
    offset_m: float
    lanes: tuple[Lane, ...]
    center_paint: LanePaint | None

    def paint(self, boundary: int) -> LanePaint | None:
        if boundary == 0:
            return self.center_paint
        return next((lane.paint for lane in self.lanes if lane.id == boundary), None)

    def boundary_at(self, boundary: int, s):
        side = 1 if boundary > 0 else -1
        local_s = np.maximum(0.0, s - self.start_m) if isinstance(s, np.ndarray) else max(0.0, s - self.start_m)
        width = sum(lane.width_at(local_s) for lane in self.lanes if 0 < side * lane.id <= side * boundary)
        return self.offset_m + side * width

    def bounds(self, lane_id: int, s: float) -> tuple[float, float]:
        right, left = lane_boundaries(lane_id)
        return self.boundary_at(right, s), self.boundary_at(left, s)

    def extent(self, s: float) -> tuple[float, float]:
        ids = [0, *(lane.id for lane in self.lanes)]
        return self.boundary_at(min(ids), s), self.boundary_at(max(ids), s)


@dataclass(frozen=True, slots=True)
class LaneGeometry:
    sections: tuple[LaneSection, ...]
    ego_id: int

    def section_at(self, s: float) -> LaneSection:
        i = bisect_right(self.sections, s, key=lambda section: section.start_m) - 1
        return self.sections[max(0, i)]

    def id_at_index(self, index: int) -> int:
        rank = self.ego_id - (self.ego_id > 0) + index
        return rank + (rank >= 0)

    def index_of(self, lane_id: int) -> int:
        return lane_id - (lane_id > 0) - (self.ego_id - (self.ego_id > 0))

    def lane_index(self, s: float, d: float, current: int) -> int:
        section = self.section_at(s)
        candidates = [lane.id for lane in section.lanes if lane.driving]
        current_id = self.id_at_index(current)
        if current_id in candidates:
            right, left = section.bounds(current_id, s)
            if right <= d <= left:
                return current
        for lane_id in candidates:
            right, left = section.bounds(lane_id, s)
            if right < left and right <= d <= left:
                return self.index_of(lane_id)
        return current if current_id in candidates else 0

    def lane_id(self, section: LaneSection, index: int) -> int:
        lane_id = self.id_at_index(index)
        return lane_id if any(lane.id == lane_id for lane in section.lanes) else self.ego_id

    def bounds(self, s: float, index: int = 0) -> tuple[float, float]:
        section = self.section_at(s)
        return section.bounds(self.lane_id(section, index), s)

    def widening_sides(self, s: float) -> tuple[bool, bool]:
        """Left and right sides that are wider than the entry cross section."""
        entry = self.sections[0]
        section = self.section_at(s)
        entry_r, entry_l = entry.extent(0.0)
        outer_r, outer_l = section.extent(s)
        ego_entry_r, ego_entry_l = entry.bounds(self.ego_id, 0.0)
        ego_r, ego_l = section.bounds(self.ego_id, s)
        eps = 1e-9
        return (max(outer_l - entry_l, ego_l - ego_entry_l) > eps,
                max(entry_r - outer_r, ego_entry_r - ego_r) > eps)

    def paint_ahead(self, boundary: int, s: float) -> LanePaint | None:
        current = self.section_at(s)
        paint = current.paint(boundary)
        if paint is not None:
            return paint
        return next((paint for section in self.sections if section.start_m > s
                     if (paint := section.paint(boundary)) is not None), None)


@dataclass(frozen=True, slots=True)
class RoadLayout:
    markings: tuple[Marking | None, ...]  # L2, L1, R1, R2
    edges: tuple[RoadEdgeSpec | None, ...] = (None, None)  # left, right
    geometry: LaneGeometry | None = None

    def __post_init__(self) -> None:
        if len(self.markings) != LANE_LINES or len(self.edges) != ROAD_EDGES:
            raise ValueError("expected four markings and two road edges")
        if any(bound is not None and not isfinite(bound.offset_m)
               for bound in (*self.markings, *self.edges)):
            raise ValueError("boundary offsets must be finite")
        left, right = self.edges
        if (left is not None and left.offset_m <= 0) or (right is not None and right.offset_m >= 0):
            raise ValueError("road edges must be on their declared sides")


class Road:
    def __init__(self, segments: list[Segment], lane_width: float,
                 layout: RoadLayout | None = None) -> None:
        if not segments:
            raise ValueError("a road needs at least one segment")
        self.lane_width = lane_width
        if layout is None:
            # Legacy three-lane geometry (the old nominal offsets already describe
            # the boundaries seen by the camera).
            types = (LineType.SOLID, LineType.DASHED, LineType.DASHED, LineType.SOLID)
            layout = RoadLayout(tuple(Marking(offset, kind, kind == LineType.DASHED)
                                      for offset, kind in zip(self.line_offsets(), types)))
        self.layout = layout
        kappa_at = []  # curvature at each sample
        k_prev = 0.0
        for seg in segments:
            n = max(1, round(seg.length / SAMPLE_STEP_M))
            if seg.kind == "straight":
                k_end = 0.0
                ks = np.zeros(n)
            elif seg.kind == "arc":
                k_end = seg.curvature_end
                ks = np.full(n, k_end)
            else:
                k_end = seg.curvature_end
                ks = k_prev + (k_end - k_prev) * (np.arange(1, n + 1) / n)
            kappa_at.append(ks)
            k_prev = k_end
        kappa = np.concatenate([[0.0], np.concatenate(kappa_at)])
        n = len(kappa)
        s = np.arange(n) * SAMPLE_STEP_M
        # Heading and position by the midpoint rule on the curvature samples.
        theta = np.zeros(n)
        theta[1:] = np.cumsum(0.5 * (kappa[1:] + kappa[:-1]) * SAMPLE_STEP_M)
        mid = 0.5 * (theta[1:] + theta[:-1])
        x = np.zeros(n)
        y = np.zeros(n)
        x[1:] = np.cumsum(np.cos(mid) * SAMPLE_STEP_M)
        y[1:] = np.cumsum(np.sin(mid) * SAMPLE_STEP_M)
        self.s, self.x, self.y, self.theta, self.kappa = s, x, y, theta, kappa
        self.length = float(s[-1])

    # Lateral offsets of the lane lines from the ego-lane centre: L2, L1, R1, R2.
    def line_offsets(self) -> tuple[float, float, float, float]:
        w = self.lane_width
        return (1.5 * w, 0.5 * w, -0.5 * w, -1.5 * w)

    def pose_at(self, s: float, d: float = 0.0) -> tuple[float, float, float]:
        """World (x, y, heading) of the point at arc length s and offset d."""
        i = int(np.clip(round(s / SAMPLE_STEP_M), 0, len(self.s) - 1))
        ds = s - self.s[i]
        th = self.theta[i]
        x = self.x[i] + ds * cos(th) - d * sin(th)
        y = self.y[i] + ds * sin(th) + d * cos(th)
        return x, y, th + ds * self.kappa[i]

    def parallel(self, d: float, s_from: float, s_to: float) -> tuple[np.ndarray, np.ndarray]:
        """World points of the parallel at offset d between two arc lengths."""
        i0 = int(np.clip(np.floor(s_from / SAMPLE_STEP_M), 0, len(self.s) - 1))
        i1 = int(np.clip(np.ceil(s_to / SAMPLE_STEP_M), 0, len(self.s) - 1)) + 1
        th = self.theta[i0:i1]
        return self.x[i0:i1] - d * np.sin(th), self.y[i0:i1] + d * np.cos(th)

    def marking_parallel(self, boundary: int, side: int, s_from: float,
                         s_to: float) -> tuple[np.ndarray, np.ndarray]:
        """Points on the near edge of a paint line, clipped to sections where it exists."""
        geometry = self.layout.geometry
        assert geometry is not None
        i0 = int(np.clip(np.floor(s_from / SAMPLE_STEP_M), 0, len(self.s) - 1))
        i1 = int(np.clip(np.ceil(s_to / SAMPLE_STEP_M), 0, len(self.s) - 1)) + 1
        stations = self.s[i0:i1]
        section_ids = np.searchsorted([section.start_m for section in geometry.sections], stations,
                                      side="right") - 1
        xs, ys = [], []
        for i, section in enumerate(geometry.sections):
            paint = section.paint(boundary)
            if paint is None:
                continue
            indices = i0 + np.flatnonzero(section_ids == i)
            stations = self.s[indices]
            offset = section.boundary_at(boundary, stations)
            if boundary != 0:
                inner = boundary - (1 if boundary > 0 else -1)
                visible = np.abs(offset - section.boundary_at(inner, stations)) > 1e-9
                indices, offset = indices[visible], offset[visible]
            offset = offset - side * paint.width / 2
            th = self.theta[indices]
            xs.append(self.x[indices] - offset * np.sin(th))
            ys.append(self.y[indices] + offset * np.cos(th))
        if not xs:
            return np.empty(0), np.empty(0)
        return np.concatenate(xs), np.concatenate(ys)

    def project(self, x: float, y: float, s_hint: float | None = None,
                window_m: float = 20.0) -> LaneProjection:
        """Foot of the perpendicular on the ego-lane centre, searched near s_hint."""
        n = len(self.s)
        if s_hint is None:
            lo, hi = 0, n
        else:
            # Scalar min/max: same values as np.clip, without its per-call cost (hot path).
            a = (s_hint - window_m) / SAMPLE_STEP_M
            b = (s_hint + window_m) / SAMPLE_STEP_M
            if a != a or b != b:
                raise ValueError("cannot convert float NaN to integer")
            lo = int(min(max(a, 0), n - 1))
            hi = int(min(max(b, 1), n))
        dx = x - self.x[lo:hi]
        dy = y - self.y[lo:hi]
        i = lo + int((dx * dx + dy * dy).argmin())
        th = self.theta[i]
        ex, ey = x - self.x[i], y - self.y[i]
        along = ex * cos(th) + ey * sin(th)
        d = -ex * sin(th) + ey * cos(th)
        return LaneProjection(float(self.s[i] + along), float(d),
                              float(th + along * self.kappa[i]), float(self.kappa[i]))

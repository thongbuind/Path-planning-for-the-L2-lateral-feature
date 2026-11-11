"""Road ground truth: centre line of the ego lane from a curvature profile.

The road is a chain of segments (straight, clothoid, arc), each given by its length
and the curvature at its end. Curvature is positive to the left. The ego lane is the
middle one of three; lines and road edges are parallels of the ego-lane centre.

Lines, left to right, as in Interface Control Document 5.1: L2, L1, R1, R2.
"""

from dataclasses import dataclass
from math import cos, sin

import numpy as np

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


class Road:
    def __init__(self, segments: list[Segment], lane_width: float) -> None:
        if not segments:
            raise ValueError("a road needs at least one segment")
        self.lane_width = lane_width
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

    def project(self, x: float, y: float, s_hint: float | None = None,
                window_m: float = 20.0) -> LaneProjection:
        """Foot of the perpendicular on the ego-lane centre, searched near s_hint."""
        if s_hint is None:
            lo, hi = 0, len(self.s)
        else:
            lo = int(np.clip((s_hint - window_m) / SAMPLE_STEP_M, 0, len(self.s) - 1))
            hi = int(np.clip((s_hint + window_m) / SAMPLE_STEP_M, 1, len(self.s)))
        dx = x - self.x[lo:hi]
        dy = y - self.y[lo:hi]
        i = lo + int(np.argmin(dx * dx + dy * dy))
        th = self.theta[i]
        ex, ey = x - self.x[i], y - self.y[i]
        along = ex * cos(th) + ey * sin(th)
        d = -ex * sin(th) + ey * cos(th)
        return LaneProjection(float(self.s[i] + along), float(d),
                              float(th + along * self.kappa[i]), float(self.kappa[i]))

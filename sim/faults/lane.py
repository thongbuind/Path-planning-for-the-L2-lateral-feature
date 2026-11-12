"""Lane model faults (Software Qualification Test Specification section 6, F01 to F06, F22).

Applied to each LaneModel frame after the camera model, before it is sent. The lane
model sends no flag for any of them (PP-ASM-009).

| kind | Effect while active |
|---|---|
| noise | c0 += N(0, sigma_c0), c1 += N(0, sigma_c1) per line and frame; reported variance = sigma^2 |
| c0_jump | c0 += value on the chosen lines |
| lose_line | chosen lines LOST, confidence 0 |
| fade_line | confidence falls linearly to 0 over `value` seconds, then LOST |
| c2_error, c3_error | c2 or c3 += value on the chosen lines |
| view_short | camera sees the chosen lines only up to `value` m; the fit uses that shorter window |
| view_flicker | as view_short on every other frame (50 ms camera period) |
| view_extend | view_range_end reported as `value` m with the same polynomial, so the far part is extrapolated |
| lose_all | every line and road edge PREDICTED (predicted_duration counting) for `value` s, then LOST (F05) |
| confidence | confidence set to `value` on the chosen lines and edges (F21 e) |
| lane_change_late | the lane_change flag comes one frame after the re-indexed lines (S17 e) |

`edges` (0 left, 1 right) adds road edges to lose_line, fade_line and confidence.

view_short and view_flicker act on the capture through view_limits(); the others on the frame.
"""

from dataclasses import dataclass, replace

import numpy as np

from interfaces import LaneModel, LineStatus
from sim.faults import trigger

KINDS = ("noise", "c0_jump", "lose_line", "fade_line", "c2_error", "c3_error",
         "view_short", "view_flicker", "view_extend", "lose_all", "confidence", "lane_change_late")
VIEW_LIMIT_KINDS = ("view_short", "view_flicker")
_CAMERA_PERIOD_US = 50_000
ALL_LINES = (0, 1, 2, 3)  # L2, L1, R1, R2
ALL_EDGES = (0, 1)  # left, right


@dataclass(frozen=True, slots=True)
class LaneFault:
    kind: str
    start_s: float = 0.0
    duration_s: float | None = None  # None: until the end of the run
    lines: tuple[int, ...] = ALL_LINES
    value: float = 0.0
    sigma_c0: float = 0.0
    sigma_c1: float = 0.0
    edges: tuple[int, ...] = ()
    trigger: str | None = None  # sim.faults.trigger: start_s counts from this event

    def __post_init__(self) -> None:
        if self.kind not in KINDS:
            raise ValueError(f"unknown lane fault {self.kind!r}")
        trigger.check(self.trigger)

    def active(self, t_s: float) -> bool:
        return t_s >= self.start_s and (self.duration_s is None or t_s < self.start_s + self.duration_s)


class LaneFaultInjector:
    def __init__(self, faults: tuple[LaneFault, ...], rng: np.random.Generator) -> None:
        self.faults = faults
        self.rng = rng
        self._late_flag = None  # lane_change held back by lane_change_late

    def view_limits(self, stamp_us: int) -> tuple[float | None, ...]:
        """Largest view range end of each line at this capture, None when not limited."""
        t_s = stamp_us * 1e-6
        limits: list[float | None] = [None] * len(ALL_LINES)
        odd = (stamp_us // _CAMERA_PERIOD_US) % 2 == 1
        for fault in self.faults:
            if fault.kind not in VIEW_LIMIT_KINDS or not fault.active(t_s):
                continue
            if fault.kind == "view_flicker" and not odd:
                continue
            for i in fault.lines:
                limits[i] = fault.value if limits[i] is None else min(limits[i], fault.value)
        return tuple(limits)

    def apply(self, message: LaneModel) -> LaneModel:
        """Faults act on the capture time of the frame."""
        t_s = message.header.stamp_us * 1e-6
        lines = list(message.lines)
        for fault in self.faults:
            if fault.kind == "noise":
                # Noise is drawn every frame, active or not, so the stream does not depend on timing.
                draws = self.rng.standard_normal((len(lines), 2))
                if not fault.active(t_s):
                    continue
                for i in fault.lines:
                    line = lines[i]
                    if line.status == LineStatus.LOST:
                        continue
                    variance = (fault.sigma_c0 ** 2, fault.sigma_c1 ** 2) + tuple(line.variance[2:])
                    lines[i] = replace(line, c0=line.c0 + fault.sigma_c0 * float(draws[i, 0]),
                                       c1=line.c1 + fault.sigma_c1 * float(draws[i, 1]),
                                       variance=variance)
                continue
            if not fault.active(t_s):
                continue
            for i in fault.lines:
                line = lines[i]
                if fault.kind == "c0_jump":
                    lines[i] = replace(line, c0=line.c0 + fault.value)
                elif fault.kind == "c2_error":
                    lines[i] = replace(line, c2=line.c2 + fault.value)
                elif fault.kind == "c3_error":
                    lines[i] = replace(line, c3=line.c3 + fault.value)
                elif fault.kind == "view_extend":
                    if line.status != LineStatus.LOST:
                        lines[i] = replace(line, view_range_end=max(line.view_range_end, fault.value))
                elif fault.kind == "lose_line":
                    lines[i] = replace(line, status=LineStatus.LOST, confidence=0.0)
                elif fault.kind == "fade_line":
                    left = 1.0 - (t_s - fault.start_s) / fault.value
                    if left <= 0.0:
                        lines[i] = replace(line, status=LineStatus.LOST, confidence=0.0)
                    else:
                        lines[i] = replace(line, confidence=line.confidence * left)
        edges = list(message.road_edges)
        for fault in self.faults:
            if not fault.active(t_s):
                continue
            if fault.kind == "lose_all":
                elapsed = t_s - fault.start_s
                predicted = elapsed < fault.value
                status = LineStatus.PREDICTED if predicted else LineStatus.LOST
                def gone(b):
                    if b.status == LineStatus.LOST:
                        return b
                    return replace(b, status=status, predicted_duration=elapsed if predicted else 0.0,
                                   confidence=b.confidence if predicted else 0.0)
                lines = [gone(b) for b in lines]
                edges = [gone(b) for b in edges]
                continue
            for i in fault.edges:
                edge = edges[i]
                if fault.kind == "lose_line":
                    edges[i] = replace(edge, status=LineStatus.LOST, confidence=0.0)
                elif fault.kind == "fade_line":
                    left = 1.0 - (t_s - fault.start_s) / fault.value
                    edges[i] = (replace(edge, status=LineStatus.LOST, confidence=0.0) if left <= 0.0
                                else replace(edge, confidence=edge.confidence * left))
                elif fault.kind == "confidence" and edge.status != LineStatus.LOST:
                    edges[i] = replace(edge, confidence=fault.value)
            if fault.kind == "confidence":
                for i in fault.lines:
                    if lines[i].status != LineStatus.LOST:
                        lines[i] = replace(lines[i], confidence=fault.value)
        flag = message.lane_change
        if any(f.kind == "lane_change_late" and f.active(t_s) for f in self.faults):
            flag, self._late_flag = (self._late_flag if self._late_flag is not None else type(flag).NONE,
                                     flag if flag != type(flag).NONE else None)
        elif self._late_flag is not None:
            flag, self._late_flag = self._late_flag, None
        return replace(message, lines=tuple(lines), road_edges=tuple(edges), lane_change=flag)

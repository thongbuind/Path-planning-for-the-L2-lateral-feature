"""Tiêm lỗi sau lúc camera chụp và trước khi phát LaneModel. LaneModel không báo cờ lỗi cho planner
(PP-ASM-009).
"""

from dataclasses import dataclass, replace

import numpy as np

from interfaces import LaneModel, LineStatus
from sim.faults import trigger

KINDS = ("noise", "c0_jump", "lose_line", "fade_line", "c2_error", "c3_error",
         "view_short", "view_flicker", "view_extend", "lose_all", "confidence", "lane_change_late")
VIEW_LIMIT_KINDS = ("view_short", "view_flicker")
_CAMERA_PERIOD_US = 50_000
ALL_LINES = (0, 1, 2, 3)
ALL_EDGES = (0, 1)


@dataclass(frozen=True, slots=True)
class LaneFault:
    kind: str
    start_s: float = 0.0
    duration_s: float | None = None  # None kéo dài đến hết run.
    lines: tuple[int, ...] = ALL_LINES
    value: float = 0.0
    sigma_c0: float = 0.0
    sigma_c1: float = 0.0
    edges: tuple[int, ...] = ()
    trigger: str | None = None
    ramp_s: float = 0.0
    # Với side=drift, chọn vạch và mép theo chiều lệch của xe. Dấu value hướng ra xa xe (F24).
    side: str = ""

    def __post_init__(self) -> None:
        if self.ramp_s < 0 or self.side not in ("", "drift"):
            raise ValueError("ramp_s must not be negative; side is empty or drift")
        if self.kind not in KINDS:
            raise ValueError(f"unknown lane fault {self.kind!r}")
        trigger.check(self.trigger)

    def active(self, t_s: float) -> bool:
        return t_s >= self.start_s and (self.duration_s is None or t_s < self.start_s + self.duration_s)


def resolve_side(fault: LaneFault, drift_curvature: float | None) -> LaneFault:
    if fault.side != "drift":
        return fault
    left = drift_curvature is not None and drift_curvature > 0
    return replace(fault, side="", lines=(1,) if left else (2,), edges=(0,) if left else (1,),
                   value=fault.value if left else -fault.value)


def _ramp(fault: LaneFault, t_s: float) -> float:
    if fault.ramp_s <= 0.0:
        return 1.0
    return min(1.0, max(0.0, (t_s - fault.start_s) / fault.ramp_s))


class LaneFaultInjector:
    def __init__(self, faults: tuple[LaneFault, ...], rng: np.random.Generator) -> None:
        self.faults = faults
        self.rng = rng
        self._late_flag = None

    def view_limits(self, stamp_us: int) -> tuple[float | None, ...]:
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
        t_s = message.header.stamp_us * 1e-6
        lines = list(message.lines)
        for fault in self.faults:
            if fault.kind == "noise":
                # Lấy mẫu nhiễu ở mọi frame để đổi thời điểm lỗi không làm lệch chuỗi ngẫu nhiên.
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
                    lines[i] = replace(line, c0=line.c0 + fault.value * _ramp(fault, t_s))
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
                elif fault.kind == "c0_jump" and edge.status != LineStatus.LOST:
                    edges[i] = replace(edge, c0=edge.c0 + fault.value * _ramp(fault, t_s))
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

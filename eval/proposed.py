"""Chỉ chấm tiêu chí đề xuất khi suite trade study liệt kê ID trong proposed và scope."""

import numpy as np

from eval.metrics import AYSMAX, R79_AY_MARGIN, Criterion, Result, Target, _hwa
from sim.harness import RunLog

PATH_AY_PROPOSED = "PP-TS-020/PP-SWR-001"
VEHICLE_AY_R79 = "PP-TS-020/R79-5.6.2.1.1"


def _path_ay(result: Result) -> Criterion:
    current = next((c for c in result.criteria if c.id == "PP-SWR-001"), None)
    limit = AYSMAX + R79_AY_MARGIN
    if current is None:
        return Criterion(PATH_AY_PROPOSED, "a_y lớn nhất của path, HWA [m/s²]", float("nan"),
                         f"<= {limit}", True, applicable=False)
    return Criterion(PATH_AY_PROPOSED, current.metric, current.value, f"<= {limit}",
                     current.value <= limit, applicable=current.applicable)


def _vehicle_ay(result: Result) -> Criterion:
    within = result.info.get("ay_vehicle_r79_within_limits")
    value = result.info.get("ay_vehicle_r79_max")
    sustained, short, short_s = result.info.get("ay_vehicle_r79_limits", [None, None, None])
    return Criterion(VEHICLE_AY_R79, "a_y lớn nhất của xe, lọc theo R79 Annex 8, 2.4, HWA [m/s²]",
                     float("nan") if value is None else float(value),
                     f"<= {sustained}, tới {short} trong tối đa {short_s} s",
                     True if within is None else bool(within), applicable=within is not None)


CRITERIA = {PATH_AY_PROPOSED: _path_ay, VEHICLE_AY_R79: _vehicle_ay}


def criteria(result: Result, ids) -> list[Criterion]:
    unknown = set(ids) - set(CRITERIA)
    if unknown:
        raise ValueError(f"unknown proposed criteria: {sorted(unknown)}")
    return [CRITERIA[i](result) for i in ids]


# PP-TS-021 so a_y thực tế của xe với a_y yêu cầu tại điểm đầu path trên cửa sổ 2 s; chỉ dùng xếp
# hạng.
VEHICLE_OVER_PATH = "PP-TS-021/ay-vehicle-over-path"
OVER_PATH_WINDOW_S = 2.0


def vehicle_over_path(log: RunLog) -> float | None:
    cycles = [c for c in log.cycles if _hwa(c)]
    if not cycles or not log.t_us:
        return None
    t_truth = np.asarray(log.t_us, dtype=float)
    a_truth = np.asarray(log.a_y, dtype=float)
    t = np.array([c.t0_us for c in cycles], dtype=float)
    p0 = [c.trajectory.points[0] for c in cycles]
    path = np.abs(np.array([p.longitudinal_velocity_mps ** 2 * p.curvature for p in p0]))
    index = np.clip(np.searchsorted(t_truth, t), 0, len(t_truth) - 1)
    excess = np.abs(a_truth[index]) - path
    best = None
    start = 0
    total = 0.0
    for end in range(len(t)):
        total += excess[end]
        while t[end] - t[start] > OVER_PATH_WINDOW_S * 1e6:
            total -= excess[start]
            start += 1
        if t[end] - t[start] >= OVER_PATH_WINDOW_S * 1e6 - 30_000:
            mean = total / (end - start + 1)
            best = mean if best is None else max(best, mean)
    return None if best is None else float(best)


TARGETS = {VEHICLE_OVER_PATH: lambda log: Target(
    VEHICLE_OVER_PATH, "a_y xe trừ a_y path, trung bình 2 s lớn nhất, HWA [m/s²]",
    vehicle_over_path(log), "m/s²")}


def targets(log: RunLog, ids) -> list[Target]:
    unknown = set(ids) - set(TARGETS)
    if unknown:
        raise ValueError(f"unknown proposed targets: {sorted(unknown)}")
    return [TARGETS[i](log) for i in ids]

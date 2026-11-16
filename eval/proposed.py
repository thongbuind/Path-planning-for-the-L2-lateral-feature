"""Criteria of requirement texts proposed in a trade study, not yet in the SRS.

A suite lists the ones it judges under `proposed:` and puts their ids in its scope; eval.sweep
adds them to each result. Full and regression runs never compute them, so their reports keep
judging the SRS as it stands. Every criterion here is written from the proposed text or the
regulation it cites, with fixed limits: none reads the calibration of the planner under test.
When the study is decided, the criterion moves into eval.metrics under the SRS id, or is
removed.
"""

import numpy as np

from eval.metrics import AYSMAX, R79_AY_MARGIN, Criterion, Result, Target, _hwa
from sim.harness import RunLog

# PP-TS-020 point 1: proposed PP-SWR-001, path a_y while HWA drives <= aysmax + 0.3 m/s^2
# (R79 5.6.2.1.1). Same measure as PP-SWR-001 of eval.metrics, other limit.
PATH_AY_PROPOSED = "PP-TS-020/PP-SWR-001"
# PP-TS-020 point 2: a_y measured on the vehicle as R79 Annex 8, 2.4 prescribes, within the
# limits of 5.6.2.1.1 (Annex 8, 3.2.2), while HWA drives.
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
    """Criteria of the proposed texts named in `ids`, from an evaluated result."""
    unknown = set(ids) - set(CRITERIA)
    if unknown:
        raise ValueError(f"unknown proposed criteria: {sorted(unknown)}")
    return [CRITERIA[i](result) for i in ids]


# PP-TS-021 point 4, ranking only: how much the vehicle's a_y exceeds the a_y the path asks for.
# Largest 2 s moving mean (the period of R79 5.6.2.1.1) of |a_y of the vehicle| minus |a_y of
# the path at 0 s| (v^2 kappa of point 0), over planner cycles where HWA drives; the vehicle
# a_y is the ground truth at the CG at the cycle time. None when HWA drives less than 2 s.
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
    for end in range(len(t)):               # cycles may have gaps where HWA does not drive
        total += excess[end]
        while t[end] - t[start] > OVER_PATH_WINDOW_S * 1e6:
            total -= excess[start]
            start += 1
        if t[end] - t[start] >= OVER_PATH_WINDOW_S * 1e6 - 30_000:   # a full window, ±1 cycle
            mean = total / (end - start + 1)
            best = mean if best is None else max(best, mean)
    return None if best is None else float(best)


TARGETS = {VEHICLE_OVER_PATH: lambda log: Target(
    VEHICLE_OVER_PATH, "a_y xe trừ a_y path, trung bình 2 s lớn nhất, HWA [m/s²]",
    vehicle_over_path(log), "m/s²")}


def targets(log: RunLog, ids) -> list[Target]:
    """Targets named in `ids`, from the run log."""
    unknown = set(ids) - set(TARGETS)
    if unknown:
        raise ValueError(f"unknown proposed targets: {sorted(unknown)}")
    return [TARGETS[i](log) for i in ids]

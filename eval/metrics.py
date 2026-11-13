"""Pass/fail criteria and metrics measured on ground truth (Software Qualification Test
Specification 8.1, 8.2; definitions of Software Requirements Specification section 4).

Only the ICD inputs and outputs, compute time, calibration values referenced by
requirements and simulator ground truth are used.

Covered so far: PP-SWR-001, 003, 005, 006, 007, 009, 010, 051, 052, 055, 056, 058, 063, 100 to 102,
116, 117, 150; targets PP-SWR-002, 008, 016, 050, 053, 057, 059, 064, 125. A criterion with no situation to judge in a run is reported as
not applicable. Information only: a_y and jerk on the vehicle as R79 Annex 8, 2.4 measures them
(r79_vehicle), until a requirement points to it.
"""

from dataclasses import asdict, dataclass, field
from math import cos, hypot, isfinite, sin

import numpy as np

from eval.calibration import requirement_parameters
from interfaces import (
    FUNCTION_REQUESTS_MAX_AGE_US, FUNCTION_REQUESTS_TIMEOUT_US, PLANNER_PERIOD_US,
    TRAJECTORY_STEP_S, ActiveFunction, ElkReason, FunctionRequest, InterventionPhase, LineStatus, RequestState,
    RoadEdgeType, Side,
)
from sim.harness import PlannerCycle, RunLog, plan_in_range
from sim.stand_ins.eps import HANDOVER_S
from sim.world.road import lane_boundaries
from sim.world.traffic import Traffic

AYSMAX = 2.5  # [m/s^2] PP-SWR-001
HORIZON_TOL_S = 0.1  # [s] PP-SWR-018, one Trajectory step
_PLANNER_CYCLE_US = 25_000  # 40 Hz, tolerance of PP-SWR-145 (one cycle)
LONG_VIEW_M = 126.0  # Largest view range the planner uses (Interface Control Document 5.1)
JERK_MAX_HWA = 5.0  # [m/s^3] PP-SWR-003
JERK_WINDOW_S = 0.5  # Software Requirements Specification 4, "Jerk ngang của path"
CONTINUITY_LATERAL_M = 0.05  # PP-SWR-100
CONTINUITY_HEADING_RAD = 0.005  # PP-SWR-101
CONTINUITY_CURVATURE = 0.0003  # PP-SWR-102
DEVIATION_WINDOW_S = 1.0  # Software Requirements Specification 4, "Lệch ngang của path"
CENTRED_M = 0.1  # PP-SWR-053: centred when the lateral offset is within 0.1 m
RECENTER_MAX_M = 0.5  # PP-SWR-052: HWA starts with the car up to 0.5 m off centre
TRUTH_STEP = 10  # Ground truth samples (1 ms) per offset sample, 10 ms
GRID_STEP_S = float(TRAJECTORY_STEP_S)
BIG_VEHICLE_WIDTH_M = 2.3  # Software Requirements Specification 4, "Xe lớn"
BODY_OVERHANG_M = 1.0  # Software Qualification Test Specification 8.1: car body = rear axle - 1 m .. front axle + 1 m
INTERVENTION_FUNCTIONS = (ActiveFunction.LKA, ActiveFunction.ELK)
INTERVENTION_LIMITS = {ActiveFunction.LKA: (3.0, 1.5, 5.0),
                       ActiveFunction.ELK: (4.0, 3.0, 10.0)}  # PP-SWR-110 to 115
ENTRY_D_M = ENTRY_V_LAT_MPS = 0.1  # PP-SWR-031, 080
MARK_DTLE_MIN_M = -0.3  # PP-SWR-086, 091
EDGE_DTLE_MIN_M = -0.1  # PP-SWR-086, 091
EPS_DELAY_MAX_S = 0.1  # PP-SWR-091
BARRIER_TYPES = (RoadEdgeType.BARRIER, RoadEdgeType.GUARDRAIL)  # PP-SWR-057: physical objects
OTHER_CAR_GAP_MIN_M = 0.3  # PP-SWR-088
LATE_ELK_DLC_M = -0.3  # PP-SWR-089
FUTURE_STAMP_TOLERANCE_US = 10_000  # PP-SWR-132
# PP-SWR-030 over-refusal (Software Qualification Test Specification 5.3): priority, inputs whose
# loss allows path_valid = false (PP-SWR-124, 142, 145), and the time after such an input is
# usable again during which not driving is not counted: upper limit of T_coast (SRS 7).
FUNCTION_PRIORITY = (ActiveFunction.ELK, ActiveFunction.LKA, ActiveFunction.HWA)
INPUTS_FOR_PATH = ("lane_model", "imu", "steering", "speed", "function_requests", "ego_motion")
RECOVERY_GRACE_S = 1.0

# a_y and jerk measured on the vehicle as R79 Annex 8, 2.4 prescribes (Software Qualification
# Test Specification 5.1). Reported as information; no requirement points to it yet.
R79_FILTER_ORDER = 4  # Annex 8, 2.4: fourth order Butterworth
R79_FILTER_HZ = 0.5  # Annex 8, 2.4: cut-off frequency
R79_MIN_RATE_HZ = 100.0  # Annex 8, 2.4: sampling rate at least
R79_AY_TABLE_MAX = 3.0  # 5.6.2.1.3, Table 1, M1: maximum specified aysmax
R79_AY_MARGIN = 0.3  # 5.6.2.1.1: may exceed aysmax by not more than 0.3 m/s^2
R79_AY_SHORT_FACTOR = 1.4  # 5.6.2.1.1: by not more than 40 per cent ...
R79_AY_SHORT_S = 2.0  # ... for time periods of not more than 2 s


@dataclass
class Criterion:
    id: str
    metric: str
    value: float
    limit: str
    passed: bool
    applicable: bool = True
    first_fail_s: float | None = None  # Simulation time of the first failing cycle, where measured


@dataclass
class Target:
    id: str
    metric: str
    value: float
    unit: str


@dataclass
class Result:
    scenario: str
    seed: int
    criteria: list[Criterion]
    targets: list[Target]
    info: dict = field(default_factory=dict)
    case_failures: list[str] = field(default_factory=list)
    scored: bool = True
    # Same failures as case_failures, classified (Software Qualification Test Specification 8.4):
    # {"kind": ISSUE_*, "requirement": id or None, "text": ..., "first_fail_s": s or None}
    issues: list[dict] = field(default_factory=list)

    @property
    def passed(self) -> bool | None:
        if not self.scored:
            return None
        return not self.case_failures and all(c.passed for c in self.criteria if c.applicable)

    def to_dict(self) -> dict:
        return {"scenario": self.scenario, "seed": self.seed, "passed": self.passed,
                "criteria": [asdict(c) for c in self.criteria],
                "targets": [asdict(t) for t in self.targets], "info": self.info,
                "case_failures": self.case_failures, "scored": self.scored, "issues": self.issues}


# Bins of the compute-time histogram [ms], log spaced 1 us to 1 s (10 per decade).
COMPUTE_BINS_MS = np.logspace(-3, 3, 61)

ISSUE_REQUIREMENT = "requirement"  # the planner failed the requirement named
ISSUE_NOT_JUDGED = "not_judged"  # precondition of the case not met on the test side: case not judged
ISSUE_EXECUTION = "execution"  # NaN or infinity in a planner output (execution fault, 8.4)


def add_issue(result: "Result", kind: str, text: str, requirement: str | None = None,
              first_fail_s: float | None = None) -> None:
    result.case_failures.append(text)
    result.issues.append({"kind": kind, "requirement": requirement, "text": text,
                          "first_fail_s": first_fail_s})


_FIELDS: dict[type, tuple[str, ...] | None] = {}  # dataclass field names per type, None if not one


def _nonfinite(value, path: str) -> str | None:
    """Path of the first NaN or infinite float in an output message, or None."""
    if isinstance(value, float):
        return None if isfinite(value) else path
    kind = type(value)
    if kind not in _FIELDS:
        _FIELDS[kind] = tuple(kind.__dataclass_fields__) if hasattr(kind, "__dataclass_fields__") else None
    names = _FIELDS[kind]
    if names is not None:
        for name in names:
            found = _nonfinite(getattr(value, name), f"{path}.{name}")
            if found:
                return found
    elif isinstance(value, (list, tuple)):
        for i, item in enumerate(value):
            found = _nonfinite(item, f"{path}[{i}]")
            if found:
                return found
    return None


def execution_fault(cycles) -> tuple[float, str] | None:
    """First cycle whose sent outputs hold NaN or infinity: (t0 [s], field)."""
    for c in cycles:
        for name in ("trajectory", "path_status", "lateral_limits"):
            message = getattr(c, name)
            found = None if message is None else _nonfinite(message, name)
            if found:
                return c.t0_us * 1e-6, found
    return None


def _valid(c: PlannerCycle) -> bool:
    return (c.trajectory is not None and c.path_status is not None and c.trajectory.header.valid
            and c.path_status.path_valid)


def _hwa(c: PlannerCycle) -> bool:
    return _valid(c) and c.path_status.active_function == ActiveFunction.HWA


class _Truth:
    """Ground-truth base_link pose by time."""

    def __init__(self, log: RunLog) -> None:
        self.log = log
        self.t = np.asarray(log.t_us)
        self.rear = np.asarray(log.rear)
        self.front = np.asarray(log.front)

    def index(self, t_us: int) -> int:
        return int(np.clip(np.searchsorted(self.t, t_us), 0, len(self.t) - 1))

    def rear_at(self, t_us: int) -> tuple[float, float, float]:
        return tuple(self.rear[self.index(t_us)])

    def front_at(self, t_us: int) -> tuple[float, float, float]:
        return tuple(self.front[self.index(t_us)])

    def lateral_velocity(self, i: int, lane_heading: float, *, front: bool = False) -> float:
        heading = self.rear[i][2] - lane_heading
        v_y = self.log.rear_v_y[i]
        if front:
            v_y += self.log.wheelbase * self.log.yaw_rate[i]
        return self.log.speed[i] * sin(heading) + v_y * cos(heading)


def _to_world(pose, x, y, yaw):
    px, py, pyaw = pose
    c, s = cos(pyaw), sin(pyaw)
    return px + c * x - s * y, py + s * x + c * y, pyaw + yaw


def _to_frame(pose, wx, wy, wyaw):
    px, py, pyaw = pose
    c, s = cos(pyaw), sin(pyaw)
    dx, dy = wx - px, wy - py
    return c * dx + s * dy, -s * dx + c * dy, wyaw - pyaw


def _wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


def _points(traj):
    pts = traj.points
    return (np.array([p.time_from_start for p in pts]), np.array([p.pose.x for p in pts]),
            np.array([p.pose.y for p in pts]), np.array([p.pose.yaw for p in pts]),
            np.array([p.curvature for p in pts]), np.array([p.longitudinal_velocity_mps for p in pts]),
            np.array([p.front_wheel_angle_rad for p in pts]))


def _finite_outputs(c: PlannerCycle) -> bool:
    """No NaN or infinity in the sent outputs of the cycle (execution fault, Software
    Qualification Test Specification 8.4; reported by execution_fault). Such a cycle is not
    projected on the road, so the run is still scored (PP-PR-026)."""
    return all(m is None or _nonfinite(m, "") is None for m in (c.trajectory, c.path_status, c.lateral_limits))


def _jerk_max(a_y: np.ndarray) -> float:
    jerk = np.diff(a_y) / GRID_STEP_S
    n = max(1, round(JERK_WINDOW_S / GRID_STEP_S))
    if len(jerk) < n:
        return float(np.max(np.abs(jerk))) if len(jerk) else 0.0
    return float(np.max(np.abs(np.convolve(jerk, np.ones(n) / n, mode="valid"))))


def _view_limit(cur: PlannerCycle, truth: _Truth) -> float:
    """x at t0 in base_link of the end of the view range the lane model reported for the frame
    the planner used (SRS 4, Hai path liên tiếp); inf without a lane model (coasting)."""
    if cur.lane_view is None or cur.lane_view_reported is None:
        return np.inf
    stamp_us = cur.lane_view[0]
    xc, yc, yawc = truth.rear_at(stamp_us)
    x0, y0, _ = truth.rear_at(cur.t0_us)
    travelled = (x0 - xc) * np.cos(yawc) + (y0 - yc) * np.sin(yawc)
    return cur.lane_view_reported - travelled


def _continuity(prev: PlannerCycle, cur: PlannerCycle, truth: _Truth) -> tuple[float, float, float]:
    """Largest lateral, heading and curvature difference between two consecutive paths
    on their common time span within the reported view range of the new cycle, the old
    path moved by the true motion of the car."""
    t_o, x_o, y_o, yaw_o, k_o, _, _ = _points(prev.trajectory)
    t_n, x_n, y_n, yaw_n, k_n, _, _ = _points(cur.trajectory)
    shift = (cur.t0_us - prev.t0_us) * 1e-6
    pose_o, pose_n = truth.rear_at(prev.t0_us), truth.rear_at(cur.t0_us)
    keep = (t_n + shift <= t_o[-1] + 1e-9) & (x_n <= _view_limit(cur, truth))
    if not np.any(keep):
        return 0.0, 0.0, 0.0
    tq = t_n[keep] + shift
    xo, yo = np.interp(tq, t_o, x_o), np.interp(tq, t_o, y_o)
    yo_yaw = np.interp(tq, t_o, np.unwrap(yaw_o))
    ko = np.interp(tq, t_o, k_o)
    wx, wy, wyaw = _to_world(pose_o, xo, yo, yo_yaw)
    fx, fy, fyaw = _to_frame(pose_n, wx, wy, wyaw)
    xn, yn, yawn, kn = x_n[keep], y_n[keep], yaw_n[keep], k_n[keep]
    lateral = -np.sin(yawn) * (fx - xn) + np.cos(yawn) * (fy - yn)
    return (float(np.max(np.abs(lateral))), float(np.max(np.abs(_wrap(fyaw - yawn)))),
            float(np.max(np.abs(ko - kn))))


@dataclass
class _BigVehicles:
    """PP-SWR-055, 056, 058 and targets 057, 059 (Software Requirements Specification 4: Xe lớn,
    Ngang hàng, Khoảng hở tới xe lớn). Offsets are of the path, 0-1 s mean, against the
    true centre, positive away from the big vehicle with the smallest gap."""

    away_055: float = np.inf  # Smallest offset away while 055 applies
    toward_056: float = -np.inf  # Largest offset toward the nearest big vehicle while 056 applies
    away_058: float | None = None  # Offset away when an approaching big vehicle becomes abreast
    clearance_057: float = np.inf  # Smallest true clearance from the car body while abreast
    return_059: float | None = None  # From the end of abreast to the car within 0.1 m of centre


def _barrier_clearance(log: RunLog, cycles, truth: _Truth) -> float | None:
    """PP-SWR-057 for physical barriers (barrier, guardrail) of the road layout: smallest true
    lateral distance from the car body (rear and front axle offsets, half width) to a barrier,
    over the cycles HWA drives. None without a barrier."""
    road = log.road
    sides = [side for i, side in ((0, Side.LEFT), (1, Side.RIGHT))
             if road.layout.edges[i] is not None and road.layout.edges[i].type in BARRIER_TYPES]
    if not sides:
        return None
    best, s_hint = np.inf, None
    for c in cycles:
        if not _hwa(c):
            continue
        for pose in (truth.rear_at(c.t0_us), truth.front_at(c.t0_us)):
            p = road.project(pose[0], pose[1], s_hint)
            s_hint = p.s
            for side in sides:
                sign = 1 if side == Side.LEFT else -1
                best = min(best, sign * (_boundary_offset(road, side, p.s, edge=True) - p.d) - log.vehicle_width / 2)
    return float(best) if np.isfinite(best) else None


def _big_vehicles(log: RunLog, cycles, paths, truth: _Truth, gap_min: float) -> _BigVehicles | None:
    road, w = log.road, log.road.lane_width
    geometry = road.layout.geometry
    specs = [sp for sp in log.scenario.traffic if sp.width >= BIG_VEHICLE_WIDTH_M
             and (geometry is not None or w / 2 < abs(sp.d) < 1.5 * w)]
    if not specs:
        return None
    traffic = Traffic(road._road if geometry is not None else road, tuple(specs))
    half_car = 0.5 * log.vehicle_width
    n_window = round(DEVIATION_WINDOW_S / GRID_STEP_S) + 1
    out = _BigVehicles()
    s_hint = None
    was_abreast = None
    end_us = None
    for c, p in zip(cycles, paths):
        rear, front = truth.rear_at(c.t0_us), truth.front_at(c.t0_us)
        pr = road.project(rear[0], rear[1], s_hint)
        s_hint = pr.s
        pf = road.project(front[0], front[1], s_hint)
        body = (pr.s - BODY_OVERHANG_M, pf.s + BODY_OVERHANG_M)
        gaps = {1: np.inf, -1: np.inf}
        for v in traffic.at(c.t0_us * 1e-6):
            if v.s + 0.5 * v.length >= body[0] and v.s - 0.5 * v.length <= body[1]:
                if geometry is None:
                    side = 1 if v.d > 0 else -1
                    d_truck = v.d
                    car_offsets = (pr.d, pf.d)
                else:
                    index = road._index(v.s)
                    side = geometry.lane_index(v.s, v.d, index) - index
                    if abs(side) != 1:
                        continue
                    d_truck = v.d - road._offset(v.s)
                    car_offsets = (pr.d + road._offset(pr.s), pf.d + road._offset(pf.s))
                gaps[side] = min(gaps[side], abs(d_truck) - 0.5 * v.width - half_car)
                for d_car in car_offsets:
                    out.clearance_057 = min(out.clearance_057,
                                            abs(v.d - d_car) - 0.5 * v.width - half_car)
        abreast = bool(np.isfinite(gaps[1]) or np.isfinite(gaps[-1]))
        if was_abreast and not abreast and _hwa(c):
            end_us = c.t0_us
        if end_us is not None and out.return_059 is None and abs(pr.d) <= CENTRED_M:
            out.return_059 = (c.t0_us - end_us) * 1e-6
        if p is not None and _hwa(c) and abreast:
            near = 1 if gaps[1] < gaps[-1] else -1
            offset_away = -near * float(np.mean(p.d[:n_window]))
            one_side = not np.isfinite(gaps[-near])
            if gaps[near] < gap_min:
                out.toward_056 = max(out.toward_056, -offset_away)
                if one_side:
                    out.away_055 = min(out.away_055, offset_away)
                    if was_abreast is False:
                        out.away_058 = offset_away if out.away_058 is None else min(out.away_058, offset_away)
        was_abreast = abreast if _hwa(c) else None
    if end_us is not None and out.return_059 is None:
        out.return_059 = float("inf")
    return out


@dataclass
class _PathTruth:
    """One valid path against the true lane (Software Requirements Specification 4)."""

    d: np.ndarray  # Lateral offset of each point from the true centre
    ay: np.ndarray  # a_y of the path, v^2 kappa
    ay_need: np.ndarray  # v^2 kappa of the true centre at the point
    in_view: np.ndarray  # Within the range the lane model observed
    ay_need_max: float  # Over 0-3 s, view range only


def _path_truth(c: PlannerCycle, truth: _Truth, road, s_hint: float | None) -> tuple[_PathTruth, float]:
    _, x, y, _, kappa, v, _ = _points(c.trajectory)
    pose = truth.rear_at(c.t0_us)
    d, need = np.zeros(len(x)), np.zeros(len(x))
    hint = road.project(pose[0], pose[1], s_hint).s
    car_s = hint
    # Observed range: from the car at capture time to view_range_end ahead (along the road).
    s_view_end = -np.inf
    if c.lane_view is not None:
        stamp_us, view_end = c.lane_view
        cap = truth.rear_at(stamp_us)
        s_view_end = road.project(cap[0], cap[1], car_s).s + view_end
    s_pts = np.zeros(len(x))
    for k in range(len(x)):
        wx, wy, _ = _to_world(pose, float(x[k]), float(y[k]), 0.0)
        proj = road.project(wx, wy, hint)
        hint = proj.s
        s_pts[k] = proj.s
        d[k] = proj.d
        need[k] = v[k] * v[k] * proj.curvature
    in_view = s_pts <= s_view_end
    ay_need_max = float(np.max(np.abs(need[in_view]))) if np.any(in_view) else 0.0
    return _PathTruth(d, v * v * kappa, need, in_view, ay_need_max), car_s


def _flag_lead(t_event_s: float, t_s: np.ndarray, flags: np.ndarray) -> float:
    """Time the flag has been on at t_event (positive), or minus the wait until it comes on."""
    i = int(np.searchsorted(t_s, t_event_s, side="right")) - 1
    if i >= 0 and flags[i]:
        j = i
        while j > 0 and flags[j - 1]:
            j -= 1
        return float(t_event_s - t_s[j])
    later = np.nonzero(flags[max(i, 0):])[0]
    return -float(t_s[max(i, 0) + later[0]] - t_event_s) if len(later) else -float("inf")


def r79_vehicle(t_s: np.ndarray, a_y: np.ndarray, active: np.ndarray, aysmax: float = AYSMAX) -> dict:
    """Lateral acceleration and jerk at the CG as R79 Annex 8, 2.4 measures them.

    `a_y` is the raw ground-truth lateral acceleration at the CG (body frame; the vehicle
    model has no roll, so nothing needs removing). Filtered over the whole run with a
    causal fourth order Butterworth low-pass at 0.5 Hz, started in steady state; jerk is the
    0.5 s moving average of the time derivative of the filtered signal. Maxima and
    durations count only samples where `active` (HWA drives). Limits of R79 5.6.2.1.1:
    above aysmax + 0.3 only for periods of at most 2 s, never above the short limit.
    """
    from scipy.signal import butter, sosfilt, sosfilt_zi

    sustained = min(aysmax + R79_AY_MARGIN, R79_AY_TABLE_MAX)
    short = min(R79_AY_SHORT_FACTOR * aysmax, R79_AY_TABLE_MAX + R79_AY_MARGIN)
    out = {"ay_vehicle_r79_max": None, "ay_vehicle_r79_over_sustained_s": None,
           "jerk_vehicle_r79_max": None, "ay_vehicle_r79_within_limits": None,
           "ay_vehicle_r79_limits": [sustained, short, R79_AY_SHORT_S]}
    if len(t_s) < 2 or not np.any(active):
        return out
    dt = float(np.median(np.diff(t_s)))
    rate = 1.0 / dt
    if rate < R79_MIN_RATE_HZ:
        raise ValueError(f"ground truth at {rate:.0f} Hz, R79 Annex 8 2.4 needs >= {R79_MIN_RATE_HZ:.0f} Hz")
    sos = butter(R79_FILTER_ORDER, R79_FILTER_HZ, btype="low", fs=rate, output="sos")
    filtered, _ = sosfilt(sos, a_y, zi=sosfilt_zi(sos) * a_y[0])
    n = max(1, round(JERK_WINDOW_S / dt))
    jerk = np.diff(filtered) / dt
    csum = np.concatenate(([0.0], np.cumsum(jerk)))
    window = (csum[n:] - csum[:-n]) / n if len(jerk) >= n else np.array([np.mean(jerk)])
    # A window ends at sample i + n of the signal; judge it where HWA drives at its end.
    window_active = active[n:n + len(window)] if len(jerk) >= n else active[-1:]
    over = active & (np.abs(filtered) > sustained)
    longest = run = 0
    for flag in over:
        run = run + 1 if flag else 0
        longest = max(longest, run)
    ay_max = float(np.max(np.abs(filtered[active])))
    out.update({
        "ay_vehicle_r79_max": ay_max,
        "ay_vehicle_r79_over_sustained_s": longest * dt,
        "jerk_vehicle_r79_max": float(np.max(np.abs(window[window_active]))) if np.any(window_active) else 0.0,
        "ay_vehicle_r79_within_limits": bool(ay_max <= short and longest * dt <= R79_AY_SHORT_S),
    })
    return out


def _cycle_mask_at(times_s: np.ndarray, cycle_t_s: np.ndarray, active: np.ndarray) -> np.ndarray:
    """Ground-truth samples for which the latest planner cycle matches the mask."""
    idx = np.searchsorted(cycle_t_s, times_s, side="right") - 1
    return (idx >= 0) & active[np.clip(idx, 0, len(active) - 1)]


def _steering_rate_rms(log: RunLog, cycle_t_s: np.ndarray, hwa: np.ndarray) -> float | None:
    """Secondary metric of PP-SWR-004 (8.2): RMS steering wheel rate of the simulated car
    [rad/s], true wheel angle times the steering ratio, while HWA drives. None without HWA."""
    if len(log.wheel_angle) != len(log.t_us) or len(log.t_us) < 2 or not len(cycle_t_s):
        return None
    t = np.asarray(log.t_us, dtype=float) * 1e-6
    rate = np.diff(np.asarray(log.wheel_angle)) / np.diff(t) * log.steering_ratio
    mask = _cycle_mask_at(t[1:], cycle_t_s, hwa)
    return float(np.sqrt(np.mean(rate[mask] ** 2))) if np.any(mask) else None


@dataclass(frozen=True)
class _Request:
    start: int
    stop: int
    rx_us: int
    message: FunctionRequest


@dataclass(frozen=True)
class _Intervention:
    function: ActiveFunction
    start: int
    stop: int
    completed: bool
    request: _Request | None


def _phase(cycle: PlannerCycle, function: ActiveFunction) -> InterventionPhase:
    status = cycle.path_status
    if status is None or not status.header.valid:
        return InterventionPhase.NONE
    return status.lka_phase if function == ActiveFunction.LKA else status.elk_phase


EGO_LINES = (1, 2)  # L1, R1 in lines L2, L1, R1, R2


def lane_usable(c, cal: dict | None = None) -> bool:
    """Lane model usable at this cycle: received, valid, in time, with at least one "biên làn
    đủ tin" (Software Requirements Specification 4): L1, R1 MEASURED with confidence >=
    conf_ego; L2, R2 or a road edge MEASURED with confidence >= conf_inferred. PREDICTED is
    not enough."""
    if c.inputs_ok is None or not c.inputs_ok.get("lane_model", True):
        return c.inputs_ok is None
    if c.lane_boundaries is None:
        return True  # log without boundary detail
    cal = cal or {}
    ego, inferred = cal.get("conf_ego", 0.0), cal.get("conf_inferred", 0.0)
    return any(status == LineStatus.MEASURED and conf >= (ego if i in EGO_LINES else inferred)
               for i, (status, conf) in enumerate(c.lane_boundaries))


def over_refusal(cycles, expected_outcome: str | None, init_ok: bool = True, cal: dict | None = None) -> Criterion:
    """PP-SWR-030 in cases labelled drive or drive_limited (Software Qualification Test
    Specification 5.3): at each cycle the function that drives (NONE when path_valid is false)
    must be the one chosen by priority among the functions in REQUEST. LKA and ELK count once
    the planner has started them for the current REQUEST, until their phase is COMPLETED
    (PP-SWR-033, 036); a start of them is judged per case. Not counted: the cycle after the
    choice changes (PP-SWR-038), and while an input needed for a path is unusable and for
    RECOVERY_GRACE_S after (PP-SWR-124, 142, 145)."""
    metric = "Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030"
    if expected_outcome not in ("drive", "drive_limited") or not init_ok or not cycles \
            or any(c.inputs_ok is None for c in cycles):
        return Criterion("PP-SWR-030", metric, float("nan"), "= 0", True, applicable=False)
    started = {ActiveFunction.LKA: False, ActiveFunction.ELK: False}
    grace_us = round(RECOVERY_GRACE_S * 1e6)
    last_bad_us, previous, wrong, judged, first = None, None, 0, 0, None
    for c in cycles:
        now_s = c.t0_us * 1e-6
        if not (all(c.inputs_ok.get(k, True) for k in INPUTS_FOR_PATH) and lane_usable(c, cal)):
            last_bad_us = c.t0_us
        message = c.function_requests.message if c.inputs_ok["function_requests"] else None
        requested = [f for f in FUNCTION_PRIORITY
                     if message is not None and message.requests[int(f) - 1].state == RequestState.REQUEST]
        for f in started:
            if f not in requested or _phase(c, f) == InterventionPhase.COMPLETED:
                started[f] = False
        status = c.path_status
        actual = status.active_function if _valid(c) else ActiveFunction.NONE
        candidates = [f for f in requested if f == ActiveFunction.HWA or started[f]]
        expected = candidates[0] if candidates else ActiveFunction.NONE
        # Starting a requested function of higher priority is a choice by PP-SWR-030, not a refusal.
        starting = (actual in started and actual in requested and not started[actual]
                    and (expected == ActiveFunction.NONE
                         or FUNCTION_PRIORITY.index(actual) < FUNCTION_PRIORITY.index(expected)))
        if actual in started and actual in requested:
            started[actual] = True
        excused = (last_bad_us is not None and c.t0_us - last_bad_us <= grace_us) or expected != previous
        previous = expected
        if excused:
            continue
        judged += 1
        if actual != expected and not starting:
            wrong += 1
            first = now_s if first is None else first
    return Criterion("PP-SWR-030", metric, float(wrong), "= 0", wrong == 0, applicable=judged > 0,
                     first_fail_s=first)


LANE_INVALID_AGE_US = 250_000  # PP-SWR-131
LANE_KEEP_AGE_US = 170_000  # PP-SWR-133
T_COAST_MAX_US = 1_000_000  # SRS 7: upper limit of T_coast


def _usable_requests(c) -> bool:
    rx = c.function_requests
    return (rx is not None and rx.message.header.valid
            and 0 <= c.t0_us - rx.rx_us <= FUNCTION_REQUESTS_TIMEOUT_US
            and -FUTURE_STAMP_TOLERANCE_US <= c.t0_us - rx.message.header.stamp_us
            <= FUNCTION_REQUESTS_MAX_AGE_US)


def _input_age_criteria(cycles, hwa_request_s) -> list:
    """PP-SWR-131: lane model older than 250 ms for longer than T_coast (upper limit) plus a
    cycle leaves no valid path. PP-SWR-133: aged 170-250 ms with both ego lines reported, the
    path stays valid while HWA is requested."""
    stale_since = None
    n131 = ok131 = n133 = ok133 = 0
    for c in cycles:
        lane = c.lane_view
        age = None if lane is None else c.t0_us - lane[0]
        valid = c.path_status is not None and c.path_status.path_valid
        if age is not None and age > LANE_INVALID_AGE_US:
            stale_since = c.t0_us if stale_since is None else stale_since
        elif age is not None:
            stale_since = None
        if stale_since is not None and c.t0_us - stale_since > T_COAST_MAX_US + _PLANNER_CYCLE_US:
            n131 += 1
            ok131 += not valid
        hwa_requested = hwa_request_s is not None and c.t0_us >= hwa_request_s * 1e6
        if (age is not None and LANE_KEEP_AGE_US <= age <= LANE_INVALID_AGE_US and hwa_requested
                and c.lane_view_reported is not None):
            n133 += 1
            ok133 += valid
    share131 = ok131 / n131 if n131 else 1.0
    share133 = ok133 / n133 if n133 else 1.0
    return [
        Criterion("PP-SWR-131", "Tỉ lệ chu kỳ không có path hợp lệ khi lane model quá 250 ms lâu hơn T_coast",
                  share131, "= 1", share131 == 1.0, applicable=n131 > 0),
        Criterion("PP-SWR-133", "Tỉ lệ chu kỳ có path hợp lệ khi lane model có tuổi 170–250 ms",
                  share133, "= 1", share133 == 1.0, applicable=n133 > 0),
    ]


def _request_change_criteria(cycles) -> list:
    """PP-SWR-038: a function leaving REQUEST is no longer active, and HWA entering REQUEST
    alone (no LKA, ELK, no override, valid path) is active, from the first cycle at least one
    cycle after the message was received."""
    checks = []  # (rx_us, function, entering)
    previous = None
    for c in cycles:
        if not _usable_requests(c):
            continue
        rx = c.function_requests
        if previous is not None and rx.rx_us != previous.rx_us:
            for function in (ActiveFunction.HWA, ActiveFunction.LKA, ActiveFunction.ELK):
                was = previous.message.requests[int(function) - 1].state == RequestState.REQUEST
                now = rx.message.requests[int(function) - 1].state == RequestState.REQUEST
                if was != now:
                    checks.append((rx.rx_us, function, now))
        previous = rx
    n = ok = 0
    for rx_us, function, entering in checks:
        c = next((c for c in cycles if c.t0_us >= rx_us + _PLANNER_CYCLE_US), None)
        if c is None or c.path_status is None or not _usable_requests(c):
            continue
        requests = c.function_requests.message
        state = requests.requests[int(function) - 1].state == RequestState.REQUEST
        if state != entering:
            continue                                # changed again since
        active = c.path_status.active_function
        if not entering:
            n += 1
            ok += active != function
        elif (function == ActiveFunction.HWA and not requests.driver_override and c.path_status.path_valid
              and not c.path_status.lane_too_narrow
              and all(requests.requests[int(f) - 1].state != RequestState.REQUEST
                      for f in (ActiveFunction.LKA, ActiveFunction.ELK))):
            n += 1
            ok += active == function
    share = ok / n if n else 1.0
    return [Criterion("PP-SWR-038", "Tỉ lệ thay đổi FunctionRequests thể hiện ở output trong một chu kỳ",
                      share, "= 1", share == 1.0, applicable=n > 0)]


def _yaw_delay_criterion(scenario, criteria) -> list:
    """PP-SWR-138: with an unreported yaw rate delay up to 50 ms, 051 and 100 to 102 hold."""
    if not 0.0 < scenario.yaw_filter_delay_ms <= 50.0:
        return []
    parts = [c for c in criteria if c.id in ("PP-SWR-051", "PP-SWR-100", "PP-SWR-101", "PP-SWR-102")
             and c.applicable]
    ok = all(c.passed for c in parts)
    return [Criterion("PP-SWR-138", "PP-SWR-051 và 100 đến 102 đạt khi yaw rate trễ không báo",
                      float(ok), "= 1", ok, applicable=bool(parts))]


def _stale_requests(cycles) -> bool:
    """FunctionRequests reached the planner older than the ICD max age (outside the contract).
    The planner then has no usable request (PP-SWR-048) and no valid path (PP-SWR-145), so
    the ADAS function cannot send REQUEST; the expected intervention does not apply."""
    for c in cycles:
        rx = c.function_requests
        if (rx is not None and rx.message.header.valid
                and c.t0_us - rx.message.header.stamp_us > FUNCTION_REQUESTS_MAX_AGE_US):
            return True
    return False


def _requests_timeout_share(cycles) -> tuple[float, bool]:
    """PP-SWR-048 with 145: share of cycles past the timeout since the last usable
    FunctionRequests (one cycle of margin) where the planner reports NONE without a path."""
    last = None
    checked = ok = 0
    for c in cycles:
        rx = c.function_requests
        if (rx is not None and rx.message.header.valid
                and 0 <= c.t0_us - rx.rx_us <= FUNCTION_REQUESTS_TIMEOUT_US
                and -FUTURE_STAMP_TOLERANCE_US <= c.t0_us - rx.message.header.stamp_us
                <= FUNCTION_REQUESTS_MAX_AGE_US):
            last = rx.rx_us if last is None else max(last, rx.rx_us)
        if last is None:
            last = c.t0_us                          # as the planner, from its first cycle
        if c.t0_us - last > FUNCTION_REQUESTS_TIMEOUT_US + _PLANNER_CYCLE_US:
            checked += 1
            s = c.path_status
            ok += s is not None and s.active_function == ActiveFunction.NONE and not s.path_valid
    return (ok / checked if checked else 1.0), checked > 0


LANE_MAX_AGE_US = 250_000  # PP-SWR-131
# Criteria measured on the vehicle: not applicable in open loop, where the car follows a
# predefined path (Software Qualification Test Specification 4.1).
VEHICLE_CRITERIA = {"PP-SWR-007", "PP-SWR-051", "PP-SWR-060", "PP-SWR-084", "PP-SWR-085", "PP-SWR-086",
                    "PP-SWR-088", "PP-SWR-091", "PP-SWR-122", "PP-SWR-123", "PP-SWR-148"}


def _after_first(flags: list[bool]) -> list[bool]:
    """A condition counts only once the input was usable at least once (a fault, not the start)."""
    out, seen = [], False
    for bad in flags:
        seen |= not bad
        out.append(bad and seen)
    return out


def _reaction(cycles, condition, requirement, metric, need_none=False) -> Criterion:
    """'... within one cycle': from the second cycle of the condition on, path_valid = false
    (and active_function = NONE)."""
    wrong, first = 0, None
    for i, c in enumerate(cycles):
        if not (condition[i] and i > 0 and condition[i - 1]):
            continue
        status = c.path_status
        still = _valid(c) or (need_none and status is not None and status.active_function != ActiveFunction.NONE)
        if still:
            wrong += 1
            first = c.t0_us * 1e-6 if first is None else first
    return Criterion(requirement, metric, float(wrong), "= 0", wrong == 0, applicable=any(condition),
                     first_fail_s=first)


def _lane_reason(c, cal: dict | None = None) -> str | None:
    """Why the lane model is not usable at this cycle: 132 future stamp, 131 too old, 124
    otherwise (missing, timeout, not valid, every boundary LOST); None when usable."""
    if c.inputs_ok is None or lane_usable(c, cal):
        return None
    times = (c.input_times or {}).get("lane_model")
    t0 = c.t0_local_us if c.t0_local_us is not None else c.t0_us
    if times is not None:
        stamp, rx, valid = times
        if valid and t0 - stamp < -FUTURE_STAMP_TOLERANCE_US:
            return "PP-SWR-132"
        if valid and t0 - stamp > LANE_MAX_AGE_US:
            return "PP-SWR-131"
    return "PP-SWR-124"


def lane_loss_criteria(cycles, t_coast_s: float, cal: dict | None = None) -> list[Criterion]:
    """PP-SWR-124 (131, 132 make the input not valid, then the same rule): when the lane model
    stops being usable, path_valid stays true for T_coast, then false; one cycle tolerance."""
    reasons = [_lane_reason(c, cal) for c in cycles]
    usable_once = _after_first([r is not None for r in reasons])
    tol_us, coast_us = PLANNER_PERIOD_US, round(t_coast_s * 1e6)
    stats = {r: [0, False, None] for r in ("PP-SWR-124", "PP-SWR-131", "PP-SWR-132")}
    i = 0
    while i < len(cycles):
        if not usable_once[i]:
            i += 1
            continue
        start, reason = i, reasons[i]
        coasting = i > 0 and _valid(cycles[i - 1])
        while i < len(cycles) and usable_once[i]:
            dt = cycles[i].t0_us - cycles[start].t0_us
            valid = _valid(cycles[i])
            wrong = (coasting and not valid and dt < coast_us - tol_us) or (valid and dt > coast_us + tol_us)
            st = stats[reason]
            st[1] = True
            if wrong:
                st[0] += 1
                st[2] = cycles[i].t0_us * 1e-6 if st[2] is None else st[2]
            i += 1
    metric = {"PP-SWR-124": "Chu kỳ sai so với T_coast khi lane model không dùng được",
              "PP-SWR-131": "Chu kỳ sai so với T_coast khi lane model quá 250 ms",
              "PP-SWR-132": "Chu kỳ sai so với T_coast khi stamp lane model ở tương lai quá 10 ms"}
    return [Criterion(r, metric[r], float(n), "= 0", n == 0, applicable=judged, first_fail_s=first)
            for r, (n, judged, first) in stats.items()]


def fault_reaction_criteria(cycles, t_coast_s: float, cal: dict | None = None) -> list[Criterion]:
    """PP-SWR-142, 143, 145, 124, 131, 132, 043 (Software Qualification Test Specification 8.1,
    "Phản ứng với lỗi"), from the inputs as the planner got them."""
    if not cycles or any(c.inputs_ok is None for c in cycles):
        return []
    chassis = _after_first([not all(c.inputs_ok[k] for k in ("imu", "speed", "steering")) for c in cycles])
    ego = [not c.inputs_ok.get("ego_motion", True) for c in cycles]

    def requests_timed_out(c) -> bool:
        times = (c.input_times or {}).get("function_requests")
        t0 = c.t0_local_us if c.t0_local_us is not None else c.t0_us
        return times is None or t0 - times[1] > FUNCTION_REQUESTS_TIMEOUT_US

    timeout = _after_first([requests_timed_out(c) for c in cycles])
    not_valid_but_active = [c for c in cycles if c.path_status is not None and not c.path_status.path_valid
                            and c.path_status.active_function != ActiveFunction.NONE]
    return [
        _reaction(cycles, chassis, "PP-SWR-142", "Chu kỳ còn path hợp lệ khi IMU, tốc độ hoặc góc lái không hợp lệ"),
        _reaction(cycles, ego, "PP-SWR-143", "Chu kỳ còn path hợp lệ khi ego-motion không hợp lệ"),
        _reaction(cycles, timeout, "PP-SWR-145", "Chu kỳ còn chức năng hoặc path hợp lệ khi FunctionRequests quá 75 ms",
                  need_none=True),
        *lane_loss_criteria(cycles, t_coast_s, cal),
        Criterion("PP-SWR-043", "Chu kỳ path_valid = false mà active_function khác NONE",
                  float(len(not_valid_but_active)), "= 0", not not_valid_but_active,
                  first_fail_s=not_valid_but_active[0].t0_us * 1e-6 if not_valid_but_active else None),
    ]


def _request_windows(cycles, function):
    """Contiguous usable REQUEST inputs and the time the first frame was received."""
    windows = []
    first = None
    for i, c in enumerate(cycles):
        rx = c.function_requests
        present = (rx is not None and rx.message.header.valid
                   and 0 <= c.t0_us - rx.rx_us <= FUNCTION_REQUESTS_TIMEOUT_US
                   and -FUTURE_STAMP_TOLERANCE_US <= c.t0_us - rx.message.header.stamp_us
                   <= FUNCTION_REQUESTS_MAX_AGE_US)
        message = rx.message.requests[int(function) - 1] if present else None
        if message is not None and message.state == RequestState.REQUEST:
            if first is None:
                first = i, rx.rx_us, message
        elif first is not None:
            windows.append(_Request(first[0], i, first[1], first[2]))
            first = None
    if first is not None:
        windows.append(_Request(first[0], len(cycles), first[1], first[2]))
    return windows


def _intervention_windows(cycles, valid, requests):
    """Intervention path intervals and the phase of the same function at their end."""
    episodes = []
    for function in INTERVENTION_FUNCTIONS:
        start = None
        for i in range(len(cycles) + 1):
            c = cycles[i] if i < len(cycles) else None
            active = (c is not None and valid[i] and c.path_status.active_function == function
                      and _phase(c, function) == InterventionPhase.ACTIVE)
            if active:
                if start is None:
                    start = i
            elif start is not None:
                req = next((r for r in requests[function] if r.start <= start < r.stop), None)
                completed = c is not None and _phase(c, function) == InterventionPhase.COMPLETED
                episodes.append(_Intervention(function, start, i, completed, req))
                start = None
    return sorted(episodes, key=lambda e: e.start)


def _path_at(cycle, t_us, truth):
    t, x, y, yaw, k, v, _ = _points(cycle.trajectory)
    elapsed = (t_us - cycle.trajectory.header.stamp_us) * 1e-6
    wx, wy, heading = _to_world(truth.rear_at(cycle.trajectory.header.stamp_us),
        np.interp(elapsed, t, x), np.interp(elapsed, t, y), np.interp(elapsed, t, np.unwrap(yaw)))
    projected = truth.log.road.project(wx, wy)
    speed = float(np.interp(elapsed, t, v))
    v_lat = speed * sin(heading - projected.heading)
    ay_add = speed**2 * (float(np.interp(elapsed, t, k)) - projected.curvature)
    return projected.d, v_lat, ay_add


def _entry_errors(cycle, t_us, truth):
    if not _finite_outputs(cycle):
        return np.inf, np.inf  # execution fault (8.4); nothing to project
    i = truth.index(t_us)
    rear = truth.rear[i]
    actual = truth.log.road.project(rear[0], rear[1])
    d, v_lat, _ = _path_at(cycle, t_us, truth)
    return abs(d - actual.d), abs(v_lat - truth.lateral_velocity(i, actual.heading))


def _variable_boundary(geometry, s, lane_id, side, *, edge=False):
    right, left = lane_boundaries(lane_id)
    boundary = left if side == Side.LEFT else right
    section = geometry.section_at(s)
    offset = section.boundary_at(boundary, s)
    paint = section.paint(boundary)
    if paint is not None and not edge:
        offset = paint.marking(offset, 1 if side == Side.LEFT else -1).offset_m
    return offset


def _boundary_offset(road, side, s, *, edge=False):
    geometry = road.layout.geometry
    if geometry is not None:
        lane_id = geometry.lane_id(geometry.section_at(s), road._index(s))
        return _variable_boundary(geometry, s, lane_id, side, edge=edge) - road._offset(s)
    index = 0 if side == Side.LEFT else 1
    boundary = road.layout.markings[index + 1]
    if edge or boundary is None:
        boundary = road.layout.edges[index]
    if boundary is None:
        return (1 if side == Side.LEFT else -1) * road.lane_width / 2
    return boundary.offset_m


def _dlc(log, projection, side, *, edge=False):
    sign = 1 if side == Side.LEFT else -1
    return sign * (_boundary_offset(log.road, side, projection.s, edge=edge) - projection.d) - log.vehicle_width / 2


def _opposite(side):
    return Side.RIGHT if side == Side.LEFT else Side.LEFT


def _min_dlc(truth, start_us, stop_us, side, *, edge=False):
    road = truth.log.road
    lo, hi = truth.index(start_us), truth.index(stop_us)
    hint = None
    value = float("inf")
    for x, y, _ in truth.front[lo:hi + 1]:
        p = road.project(x, y, hint)
        hint = p.s
        value = min(value, _dlc(truth.log, p, side, edge=edge))
    return value


def _handover_end_us(truth, stop_us, next_start_us):
    stop = truth.index(stop_us)
    upper = truth.index(next_start_us)
    released = next((int(truth.t[i]) for i in range(stop, upper + 1)
                     if not truth.log.eps_controlling[i]), stop_us)
    return min(released + round(HANDOVER_S * 1e6), next_start_us)


def _end_condition(truth, prev, cur, side, edge, cal):
    i = truth.index(cur.t0_us)
    front, rear = truth.front[i], truth.rear[i]
    road = truth.log.road
    pf = road.project(front[0], front[1])
    pr = road.project(rear[0], rear[1], pf.s)
    if (min(_dlc(truth.log, pf, side, edge=edge), _dlc(truth.log, pf, _opposite(side))) < 0
            or abs(truth.lateral_velocity(i, pf.heading, front=True)) > cal["v_lat_end"]
            or abs(_wrap(rear[2] - pr.heading)) > cal["heading_end"]):
        return False
    return _valid(prev) and abs(_path_at(prev, cur.t0_us, truth)[2]) <= cal["ay_add_end"]


def _target_geometry(truth, episodes):
    """Ground-truth lateral gap while ELK drives and rectangle contact over the encounter."""
    log = truth.log
    if not log.scenario.traffic:
        return None, None
    traffic = Traffic(log.road, log.scenario.traffic)
    target_active = np.zeros(len(truth.t), dtype=bool)
    for e in episodes:
        if e.request and e.request.message.elk_reason in (ElkReason.ONCOMING, ElkReason.OVERTAKING):
            stop = log.cycles[e.stop].t0_us if e.stop < len(log.cycles) else truth.t[-1]
            target_active[truth.index(log.cycles[e.start].t0_us):truth.index(stop) + 1] = True
    ego_length = log.wheelbase + 2 * BODY_OVERHANG_M
    widths = (log.vehicle_width / 2, ego_length / 2)
    min_gap = float("inf")
    contact = False
    hint = None
    for i, (t, rear) in enumerate(zip(truth.t, truth.rear)):
        x, y, yaw = rear
        ex, ey = cos(yaw), sin(yaw)
        x += log.wheelbase / 2 * ex
        y += log.wheelbase / 2 * ey
        if target_active[i]:
            p = log.road.project(x, y, hint)
            hint = p.s
            nx, ny = -sin(p.heading), cos(p.heading)
            ego_span = widths[0] * abs(nx * ey - ny * ex) + widths[1] * abs(nx * ex + ny * ey)
        for target in traffic.at(t * 1e-6):
            tx, ty = cos(target.heading), sin(target.heading)
            dx, dy = target.x - x, target.y - y
            half_w, half_l = target.width / 2, target.length / 2
            if target_active[i]:
                span = half_w * abs(nx * ty - ny * tx) + half_l * abs(nx * tx + ny * ty)
                min_gap = min(min_gap, abs(nx * dx + ny * dy) - ego_span - span)
            if contact or hypot(dx, dy) > hypot(*widths) + hypot(half_l, half_w):
                continue
            # Separating axes of the two rectangles.
            contact = all(abs(ax * dx + ay * dy) <= (
                widths[0] * abs(ax * ey - ay * ex) + widths[1] * abs(ax * ex + ay * ey)
                + half_w * abs(ax * ty - ay * tx) + half_l * abs(ax * tx + ay * ty))
                for ax, ay in ((ex, ey), (-ey, ex), (tx, ty), (-ty, tx)))
    return (min_gap if np.isfinite(min_gap) else None), not contact


def _completion_errors(truth, episode, cal, edge):
    cycles = truth.log.cycles
    side = episode.request.message.side
    since = None
    reached = []
    for i in range(episode.start + 1, min(episode.stop + 1, len(cycles))):
        cur = cycles[i]
        if not _end_condition(truth, cycles[i - 1], cur, side, edge, cal):
            since = None
        elif since is None:
            since = cur.t0_us
        if since is not None and cur.t0_us - since >= round(cal["T_end_hold"] * 1e6):
            reached.append(i)
    completion_late = bool(reached and (not episode.completed or reached[0] != episode.stop))
    premature = episode.completed and episode.stop not in reached
    return bool(reached), completion_late, premature


def _check_late_elk(truth, windows):
    cycles = truth.log.cycles
    late_dlcs = []
    accepted = 0
    for r in windows:
        side = r.message.side
        if side not in (Side.LEFT, Side.RIGHT):
            continue
        index = 1 if side == Side.LEFT else 2
        if truth.log.road.layout.markings[index] is None:
            continue
        front = truth.front_at(r.rx_us)
        dlc = _dlc(truth.log, truth.log.road.project(front[0], front[1]), side)
        if dlc < LATE_ELK_DLC_M:
            late_dlcs.append(dlc)
            accepted += any(_phase(c, ActiveFunction.ELK) == InterventionPhase.ACTIVE
                            for c in cycles[r.start:r.stop])
    return late_dlcs, accepted


PLAN_STEP_S = 0.1  # LongitudinalPlan grid (Interface Control Document 5.7)
FLOAT32_TOL = 1e-3  # [m/s], [m/s^2] float32 transport of the interface
CURRENT_SPEED_TOL_MPS = 0.2  # PP-SWR-154: "tốc độ hiện tại" against the true speed (nhóm tự thống nhất)


SWITCH_WINDOW_S = 0.5  # judged after a request change, after the one exempt cycle of PP-SWR-038
OVERRIDE_START_M = 0.05  # PP-SWR-039, 040
HWA_LOW_SPEED_MPS = 60 / 3.6  # PP-SWR-054
LANE_CHANGE_WINDOW_S = 1.0  # PP-SWR-061: cycles using a frame up to 1 s after the lane model re-indexed


def _state(c, function):
    """RequestState of a function in the usable FunctionRequests of the cycle, else None."""
    if not (c.inputs_ok or {}).get("function_requests") or c.function_requests is None:
        return None
    return c.function_requests.message.requests[int(function) - 1].state


def _inputs_ok(c, cal) -> bool:
    return all((c.inputs_ok or {}).get(k, True) for k in INPUTS_FOR_PATH) and lane_usable(c, cal)


def switch_criteria(log: RunLog, cycles, cal: dict | None = None) -> list[Criterion]:
    """Arbitration and driver override on the outputs (PP-SWR-034, 036, 037, 039 to 042, 054, 061).

    - 034, 041: after COMPLETED while the state stays REQUEST, the phase stays COMPLETED (041)
      and no new intervention starts (034) until the state leaves REQUEST.
    - 036, 037: when an intervening LKA or ELK leaves REQUEST, from the cycle after the exempt one
      (038) and for SWITCH_WINDOW_S, the function driving is HWA if HWA is in REQUEST, else NONE
      (036); with none left, path_valid stays true (037) while the needed inputs are usable.
    - 042: when HWA leaves REQUEST with no function in REQUEST, NONE with path_valid true.
    - 039: while driver_override, point 0 of a valid path within 0.05 m of the car (base_link y).
      040: at the first cycle with driver_override false after true, HWA in REQUEST, the same.
    - 054: HWA in REQUEST and the true speed 0 to 60 km/h: a valid HWA path.
    - 061: continuity of PP-SWR-100 to 102 on cycles using a frame up to 1 s after a lane change."""
    truth = _Truth(log)
    t = np.asarray(log.t_us)
    window_us = round(SWITCH_WINDOW_S * 1e6)
    bad = {k: 0 for k in ("034", "036", "037", "041", "042", "054")}
    seen = {k: 0 for k in bad}
    starts_039, starts_040 = [], []
    # 034, 041
    for f in INTERVENTION_FUNCTIONS:
        hold = False
        for c in cycles:
            state = _state(c, f)
            if state != RequestState.REQUEST:
                hold = False
                continue
            phase = _phase(c, f)
            if hold:
                seen["034"] += 1
                seen["041"] += 1
                bad["034"] += phase == InterventionPhase.ACTIVE
                bad["041"] += phase != InterventionPhase.COMPLETED
            elif phase == InterventionPhase.COMPLETED:
                hold = True
    # 036, 037, 042: windows after a withdrawal
    windows = []  # (start_us, end_us, kind)
    for prev, c in zip(cycles, cycles[1:]):
        for f in INTERVENTION_FUNCTIONS:
            if (_phase(prev, f) == InterventionPhase.ACTIVE and _state(prev, f) == RequestState.REQUEST
                    and _state(c, f) not in (None, RequestState.REQUEST)):
                windows.append((c.t0_us, "036"))
        if _state(prev, ActiveFunction.HWA) == RequestState.REQUEST and \
                _state(c, ActiveFunction.HWA) not in (None, RequestState.REQUEST):
            windows.append((c.t0_us, "042"))
    for start_us, kind in windows:
        judged = [c for c in cycles if start_us + PLANNER_PERIOD_US < c.t0_us <= start_us + PLANNER_PERIOD_US + window_us]
        for c in judged:
            if not _inputs_ok(c, cal):
                continue
            states = {f: _state(c, f) for f in FUNCTION_PRIORITY}
            if any(v is None for v in states.values()):
                continue
            requested = [f for f in FUNCTION_PRIORITY if states[f] == RequestState.REQUEST]
            actual = c.path_status.active_function if _valid(c) else ActiveFunction.NONE
            if kind == "036":
                expected = ActiveFunction.HWA if ActiveFunction.HWA in requested else ActiveFunction.NONE
                # Starting another requested intervention is a new choice (PP-SWR-030), not a fault.
                if actual in INTERVENTION_FUNCTIONS and actual in requested and actual != expected:
                    continue
                seen["036"] += 1
                bad["036"] += actual != expected
                if not requested:
                    seen["037"] += 1
                    bad["037"] += not (c.path_status is not None and c.path_status.path_valid
                                       and c.path_status.active_function == ActiveFunction.NONE)
            elif not requested:
                seen["042"] += 1
                bad["042"] += not (c.path_status is not None and c.path_status.path_valid
                                   and c.path_status.active_function == ActiveFunction.NONE)
    # 039, 040
    was_override = False
    for c in cycles:
        usable = (c.inputs_ok or {}).get("function_requests") and c.function_requests is not None
        override = bool(usable and c.function_requests.message.driver_override)
        if _valid(c) and c.trajectory is not None:
            y0 = abs(c.trajectory.points[0].pose.y)
            if override:
                starts_039.append(y0)
            elif was_override and _hwa(c):
                starts_040.append(y0)
        if usable:
            was_override = override
    # 054
    for c in cycles:
        if _state(c, ActiveFunction.HWA) != RequestState.REQUEST or not _inputs_ok(c, cal):
            continue
        speed = log.speed[int(np.clip(np.searchsorted(t, c.t0_us), 0, len(t) - 1))]
        if 0.0 <= speed <= HWA_LOW_SPEED_MPS:
            seen["054"] += 1
            bad["054"] += not _hwa(c)
    # 061
    lane_changes = [stamp for stamp, _ in getattr(log, "lane_index_changes", [])]
    cont = [0.0, 0.0, 0.0]
    n_061 = 0
    for prev, c in zip(cycles, cycles[1:]):
        if not (_valid(prev) and _valid(c)) or c.path_status.active_function != prev.path_status.active_function:
            continue
        stamp = c.lane_view[0] if c.lane_view is not None else None
        if stamp is None or not any(ch <= stamp <= ch + LANE_CHANGE_WINDOW_S * 1e6 for ch in lane_changes):
            continue
        n_061 += 1
        cont = [max(a, b) for a, b in zip(cont, _continuity(prev, c, truth))]

    def count(rid, metric):
        return Criterion(f"PP-SWR-{rid}", metric, float(bad[rid]), "= 0", bad[rid] == 0, applicable=seen[rid] > 0)
    return [
        count("034", "Chu kỳ bắt đầu lại can thiệp khi chức năng vừa COMPLETED vẫn giữ REQUEST"),
        count("041", "Chu kỳ rời pha COMPLETED khi state vẫn ở REQUEST"),
        count("036", "Chu kỳ sai chức năng sau khi chức năng đang can thiệp rời REQUEST"),
        count("037", "Chu kỳ không có NONE với path hợp lệ sau khi chức năng can thiệp rời REQUEST"),
        count("042", "Chu kỳ không có NONE với path hợp lệ sau khi HWA rời REQUEST"),
        count("054", "Chu kỳ không có path HWA hợp lệ khi HWA ở REQUEST và tốc độ 0–60 km/h"),
        Criterion("PP-SWR-039", "Lệch ngang điểm đầu path so với xe khi driver_override [m]",
                  float(max(starts_039, default=float("nan"))), f"<= {OVERRIDE_START_M}",
                  max(starts_039, default=0.0) <= OVERRIDE_START_M, applicable=bool(starts_039)),
        Criterion("PP-SWR-040", "Lệch ngang điểm đầu path HWA khi hết driver_override [m]",
                  float(max(starts_040, default=float("nan"))), f"<= {OVERRIDE_START_M}",
                  max(starts_040, default=0.0) <= OVERRIDE_START_M, applicable=bool(starts_040)),
        Criterion("PP-SWR-061", "Lệch ngang giữa hai path liên tiếp khi lane model sang làn mới [m]", cont[0],
                  f"<= {CONTINUITY_LATERAL_M}", cont[0] <= CONTINUITY_LATERAL_M, applicable=n_061 > 0),
        Criterion("PP-SWR-061", "Lệch hướng giữa hai path liên tiếp khi lane model sang làn mới [rad]", cont[1],
                  f"<= {CONTINUITY_HEADING_RAD}", cont[1] <= CONTINUITY_HEADING_RAD, applicable=n_061 > 0),
        Criterion("PP-SWR-061", "Lệch độ cong giữa hai path liên tiếp khi lane model sang làn mới [1/m]", cont[2],
                  f"<= {CONTINUITY_CURVATURE}", cont[2] <= CONTINUITY_CURVATURE, applicable=n_061 > 0),
    ]


def longitudinal_criteria(log: RunLog, cycles) -> list[Criterion]:
    """PP-SWR-153 to 156 on the Trajectory and the LongitudinalPlan the planner received.

    153: with a usable plan, every point's v and a lies between the plan value at the same
    index and the value moved by the age of the plan (Interface Control Document 5.7 gives the
    same grid, not the alignment). 154: with the plan lost or past its timeout, v is constant
    and equal to the current speed, a is 0. 155: a valid path stays valid when the plan is lost.
    156: a plan received with v or a out of the ranges of Interface Control Document 5.7 is
    handled as not received, so the Trajectory is that of 154."""
    follow_bad = follow_n = lost_bad = lost_n = drop_bad = drop_n = range_bad = range_n = 0
    t = np.asarray(log.t_us)
    prev_valid = False
    for c in cycles:
        ok = (c.inputs_ok or {}).get("longitudinal_plan")
        valid = _valid(c)
        if ok is None:
            continue
        if not ok:
            if prev_valid:
                drop_n += 1
                drop_bad += not valid
        if valid:
            v = np.array([p.longitudinal_velocity_mps for p in c.trajectory.points])
            a = np.array([p.acceleration_mps2 for p in c.trajectory.points])
            if ok and c.longitudinal_plan is not None:
                plan = c.longitudinal_plan.message
                grid = np.arange(len(plan.points)) * PLAN_STEP_S
                pv = np.array([p.v for p in plan.points])
                pa = np.array([p.a for p in plan.points])
                age = max(0.0, (c.t0_local_us if c.t0_local_us is not None else c.t0_us) - plan.header.stamp_us) * 1e-6
                tq = np.array([p.time_from_start for p in c.trajectory.points])
                inside = True
                for values, ref in ((v, pv), (a, pa)):
                    same, moved = np.interp(tq, grid, ref), np.interp(tq + age, grid, ref)
                    lo, hi = np.minimum(same, moved) - FLOAT32_TOL, np.maximum(same, moved) + FLOAT32_TOL
                    inside &= bool(np.all((values >= lo) & (values <= hi)))
                follow_n += 1
                follow_bad += not inside
            elif not ok:
                speed = log.speed[int(np.clip(np.searchsorted(t, c.t0_us), 0, len(t) - 1))]
                fallback = bool(np.ptp(v) <= FLOAT32_TOL and abs(v[0] - speed) <= CURRENT_SPEED_TOL_MPS
                                and np.all(np.abs(a) <= FLOAT32_TOL))
                rx = c.longitudinal_plan
                if rx is not None and rx.message.header.valid and not plan_in_range(rx.message):
                    range_n += 1
                    range_bad += not fallback
                else:
                    lost_n += 1
                    lost_bad += not fallback
        prev_valid = valid
    return [
        Criterion("PP-SWR-153", "Chu kỳ có v, a của Trajectory không theo LongitudinalPlan", follow_bad, "= 0",
                  follow_bad == 0, applicable=follow_n > 0),
        Criterion("PP-SWR-154", "Chu kỳ mất LongitudinalPlan mà v không giữ tốc độ hiện tại hoặc a khác 0",
                  lost_bad, "= 0", lost_bad == 0, applicable=lost_n > 0),
        Criterion("PP-SWR-155", "Chu kỳ mất LongitudinalPlan làm path hợp lệ thành không hợp lệ", drop_bad, "= 0",
                  drop_bad == 0, applicable=drop_n > 0),
        Criterion("PP-SWR-156", "Chu kỳ LongitudinalPlan ngoài dải mà v không giữ tốc độ hiện tại hoặc a khác 0",
                  range_bad, "= 0", range_bad == 0, applicable=range_n > 0),
    ]


def adas_requests(log: RunLog) -> dict | None:
    """REQUEST episodes of LKA and ELK sent by the ADAS function stand-in, mode A (measured
    inputs) and mode B (ideal inputs), whichever mode drives the planner. Test side: S10 and
    the cases where the ADAS function must not intervene (Software Qualification Test
    Specification 6.3, expect_intervention none). None without the stand-in."""
    if not log.adas:
        return None
    out = {}
    for mode, attr in (("A", "measured_requests"), ("B", "ideal_requests")):
        count, held = 0, False
        for sample in log.adas:
            now = any(r.state == RequestState.REQUEST for r in getattr(sample, attr).requests[1:])
            count += now and not held
            held = now
        out[mode] = count
    return out


def _score_interventions(result, truth, paths, episodes, requests, cal, cycle_times):
    log, cycles = truth.log, truth.log.cycles
    expected = log.scenario.notes.get("expect_intervention")
    if expected == "none":
        # The ADAS function must not request here (ADAS Function Specification 6, 8): a request
        # is a test-side fault, the planner is not judged on its consequence.
        if any(requests.values()):
            add_issue(result, ISSUE_NOT_JUDGED,
                      "Khối Chức năng ADAS chạy thử gửi REQUEST trong ca không được can thiệp")
        return
    if not (expected or episodes or any(requests.values())):
        return
    def issue(kind, text, requirement=None):
        add_issue(result, kind, text, requirement)

    if expected in ("LKA", "ELK"):
        function = ActiveFunction[expected]
        desired = log.scenario.notes.get("departure_side")
        expected_requests = [r for r in requests[function]
                             if desired is None or r.message.side.name.lower() == desired]
        if not expected_requests and not _stale_requests(cycles):  # stale: PP-SWR-048
            side = "" if desired is None else f" (phía {'trái' if desired == 'left' else 'phải'})"
            issue(ISSUE_NOT_JUDGED, f"{expected}: thiếu REQUEST đến planner{side}")
        elif (any(not any(e.request is r and e.function == function for e in episodes)
                  for r in expected_requests)
              or any(_phase(c, function) == InterventionPhase.ACTIVE and not _valid(c) for c in cycles)):
            issue(ISSUE_REQUIREMENT, f"{expected}: có REQUEST nhưng thiếu path can thiệp hợp lệ", "PP-SWR-030")
    late_dlcs, accepted = _check_late_elk(truth, requests[ActiveFunction.ELK])
    if expected == "late ELK":
        if not requests[ActiveFunction.ELK]:
            issue(ISSUE_NOT_JUDGED, "PP-SWR-089: thiếu REQUEST bơm muộn đến planner")
        elif not late_dlcs:
            issue(ISSUE_NOT_JUDGED, "PP-SWR-089: lốp trước chưa qua vạch hơn 0,3 m tại lúc nhận REQUEST")

    starts = []
    opposite_dlcs, completed_dlcs = [], []
    dtle_mark, dtle_edge, dtle_lka = [], [], []
    times_to_complete = {f: [] for f in INTERVENTION_FUNCTIONS}
    end_judged = late_completion = early_completion = n_completed = 0
    details = []
    for i, episode in enumerate(episodes):
        function = episode.function
        if episode.request is None:
            issue(ISSUE_REQUIREMENT, f"{function.name}: path can thiệp thiếu REQUEST tương ứng", "PP-SWR-030")
            continue
        req = episode.request.message
        if req.side not in (Side.LEFT, Side.RIGHT):
            issue(ISSUE_NOT_JUDGED, f"{function.name}: REQUEST thiếu phía can thiệp")
            continue
        start_us = cycles[episode.start].t0_us
        end_seen = episode.stop < len(cycles)
        stop_us = cycles[episode.stop].t0_us if end_seen else int(truth.t[-1])
        next_us = next((cycles[e.start].t0_us for e in episodes[i + 1:]
                        if e.function != function or e.request is not episode.request), int(truth.t[-1]))
        edge = req.elk_reason == ElkReason.ROAD_EDGE
        lka = function == ActiveFunction.LKA
        starts.append(_entry_errors(cycles[episode.start], start_us, truth))
        elapsed_s = (stop_us - episode.request.rx_us) * 1e-6  # information; no duration limit (PP-TS-016)
        handover_us = _handover_end_us(truth, stop_us, next_us)
        opposite_dlcs.append(_min_dlc(truth, start_us, handover_us, _opposite(req.side)))
        dtle = _min_dlc(truth, start_us, stop_us, req.side, edge=edge)
        if lka:
            dtle_lka.append(dtle)
        if edge:
            dtle_edge.append(dtle)
        elif lka or req.elk_reason == ElkReason.SOLID_LINE:
            dtle_mark.append(dtle)
        if episode.completed:
            n_completed += 1
            times_to_complete[function].append((stop_us - start_us) * 1e-6)
            if lka:
                front = truth.front_at(stop_us)
                completed_dlcs.append(_dlc(log, log.road.project(front[0], front[1]), req.side))
        reached, late, early = _completion_errors(truth, episode, cal, edge)
        end_judged += reached
        late_completion += late
        early_completion += early
        details.append({"function": function.name, "side": req.side.name, "reason": req.elk_reason.name,
                        "request_rx_us": episode.request.rx_us, "start_us": start_us,
                        "end_us": stop_us if end_seen else None, "completed": episode.completed,
                        "observed_duration_s": elapsed_s,
                        "end_handover_us": handover_us, "dtle_m": dtle})

    def lower(requirement, metric, values, limit):
        value = float(min(values, default=float("nan")))
        result.criteria.append(Criterion(requirement, metric, value, f">= {limit}",
                                          value >= limit, applicable=bool(values)))

    def upper(requirement, metric, values, limit):
        value = float(max(values, default=float("nan")))
        result.criteria.append(Criterion(requirement, metric, value, f"<= {limit}",
                                          value <= limit, applicable=bool(values)))

    upper("PP-SWR-080", "Lệch vị trí ngang tại điểm đầu [m]", [d for d, _ in starts], ENTRY_D_M)
    upper("PP-SWR-080", "Lệch vận tốc ngang tại điểm đầu [m/s]", [v for _, v in starts], ENTRY_V_LAT_MPS)
    upper("PP-SWR-032", "Lần chưa báo COMPLETED tại tick đủ điều kiện", [late_completion] if end_judged else [], 0)
    upper("PP-SWR-090", "Lần báo COMPLETED khi chưa đủ điều kiện", [early_completion] if n_completed else [], 0)
    lower("PP-SWR-084", "DLC phía trôi khi LKA COMPLETED [m]", completed_dlcs, 0)
    lower("PP-SWR-085", "DLC phía đối diện qua bàn giao EPS [m]", opposite_dlcs, 0)
    lower("PP-SWR-086", "DTLE vạch nhỏ nhất [m]", dtle_mark, MARK_DTLE_MIN_M)
    lower("PP-SWR-086", "DTLE mép đường nhỏ nhất [m]", dtle_edge, EDGE_DTLE_MIN_M)
    # PP-SWR-091: the real EPS of the case is slower than the VehicleConfig value, up to 100 ms (S13).
    eps_delay = getattr(log.scenario, "eps_delay_s", None)
    if eps_delay is not None and log.actuator_delay_s + 1e-9 < eps_delay <= EPS_DELAY_MAX_S + 1e-9:
        lower("PP-SWR-091", "DTLE vạch khi EPS chậm tới 100 ms [m]", dtle_mark, MARK_DTLE_MIN_M)
        lower("PP-SWR-091", "DTLE mép khi EPS chậm tới 100 ms [m]", dtle_edge, EDGE_DTLE_MIN_M)
    upper("PP-SWR-089", "Số ELK REQUEST muộn đã khởi động", [accepted] if late_dlcs else [], 0)
    gap, no_impact = _target_geometry(truth, episodes)
    lower("PP-SWR-088", "Khoảng cách ngang nhỏ nhất tới xe mục tiêu [m]",
          [] if gap is None else [gap], OTHER_CAR_GAP_MIN_M)
    result.info["interventions"] = details
    result.info["late_elk_request_dlc_m"] = late_dlcs
    if no_impact is not None:
        result.info["no_impact"] = no_impact
    if dtle_lka:
        result.targets.append(Target("PP-SWR-087", "DTLE LKA nhỏ nhất", min(dtle_lka), "m"))
    for function in INTERVENTION_FUNCTIONS:
        lka = function == ActiveFunction.LKA
        if times_to_complete[function]:
            result.targets.append(Target("PP-SWR-081" if lka else "PP-SWR-082",
                                         f"Thời lượng path {function.name} tới COMPLETED",
                                         max(times_to_complete[function]), "s"))
        active = np.zeros(len(cycles), dtype=bool)
        for e in episodes:
            if e.function == function:
                active[e.start:e.stop] = True
        active_paths = [p for p, use in zip(paths, active) if use and p is not None]  # None: execution fault
        ay_limit, added_limit, jerk_limit = INTERVENTION_LIMITS[function]
        later = [e for e in episodes if e.function == function][1:]
        if later:  # PP-SWR-035: every new intervention, the limits of the first
            worst = 0
            for e in later:
                ps = [p for p in paths[e.start:e.stop] if p is not None]
                worst += any(float(np.max(np.abs(p.ay))) > ay_limit
                             or float(np.max(np.abs(p.ay - p.ay_need))) > added_limit
                             or _jerk_max(p.ay) > jerk_limit for p in ps)
            result.criteria.append(Criterion("PP-SWR-035", f"Lần {function.name} sau lần đầu vượt giới hạn 110 đến 115",
                                             float(worst), "= 0", worst == 0))
        upper("PP-SWR-110" if lka else "PP-SWR-111", f"a_y lớn nhất của path {function.name} [m/s²]",
              [float(np.max(np.abs(p.ay))) for p in active_paths], ay_limit)
        upper("PP-SWR-112" if lka else "PP-SWR-113", f"a_y thêm vào của path {function.name} [m/s²]",
              [float(np.max(np.abs(p.ay - p.ay_need))) for p in active_paths], added_limit)
        upper("PP-SWR-114" if lka else "PP-SWR-115", f"Jerk lớn nhất của path {function.name} [m/s³]",
              [_jerk_max(p.ay) for p in active_paths], jerk_limit)
        if active_paths:
            t_s = truth.t * 1e-6
            vehicle = r79_vehicle(t_s, np.asarray(log.a_y), _cycle_mask_at(t_s, cycle_times, active))
            result.info[f"{function.name.lower()}_vehicle_r79"] = {
                key: vehicle[key] for key in ("ay_vehicle_r79_max", "jerk_vehicle_r79_max")
            }

    if log.adas:
        for function in INTERVENTION_FUNCTIONS:
            idx = int(function) - 1
            a = next((m.t_us for m in log.adas if m.measured_requests.requests[idx].state == RequestState.REQUEST), None)
            b = next((m.t_us for m in log.adas if m.ideal_requests.requests[idx].state == RequestState.REQUEST), None)
            if a is not None or b is not None:
                result.info[f"{function.name.lower()}_request_timing"] = {
                    "mode_a_us": a, "mode_b_us": b, "a_minus_b_us": None if a is None or b is None else a - b,
                }
    if log.scenario.notes.get("protocol") and episodes:
        ep = episodes[0]
        k = truth.index(cycles[ep.start].t0_us)
        front = truth.front[k]
        lane = log.road.project(front[0], front[1])
        measured = abs(truth.lateral_velocity(k, lane.heading, front=True))
        desired = log.scenario.notes["departure_v_lat_mps"]
        result.info["protocol_v_lat"] = {"target_mps": desired, "at_start_mps": measured,
                                          "within_0_05_mps": abs(measured - desired) <= 0.05}


class _LaneRelativeRoad:
    """The road seen from the lane the car is in (S17 lane change): d and pose_at count from
    the centre of that lane. The lane changes at the arc length where the camera re-indexed
    the lines (RunLog.lane_index_changes), so the truth follows the lane change the driver
    made, as the lane model does."""

    def __init__(self, road, breaks: list[tuple[float, int]]) -> None:
        self._road = road
        self._s = [s for s, _ in breaks]
        self._k = [k for _, k in breaks]

    def __getattr__(self, name):
        return getattr(self._road, name)

    def _index(self, s: float) -> int:
        i = int(np.searchsorted(self._s, s, side="right")) - 1
        return self._k[i] if i >= 0 else 0

    def _offset(self, s: float) -> float:
        index = self._index(s)
        geometry = self._road.layout.geometry
        if geometry is None:
            return index * self._road.lane_width
        low, high = geometry.bounds(s, index)
        return (low + high) / 2

    def project(self, x, y, s_hint=None, window_m=20.0):
        from sim.world.road import LaneProjection
        p = self._road.project(x, y, s_hint, window_m)
        return LaneProjection(p.s, p.d - self._offset(p.s), p.heading, p.curvature)

    def pose_at(self, s, d=0.0):
        return self._road.pose_at(s, d + self._offset(s))


def lane_relative(log: RunLog) -> RunLog:
    """The log with its road seen from the car's lane when the car changed lanes."""
    changes = getattr(log, "lane_index_changes", None)
    if not changes and log.road.layout.geometry is None:
        return log
    from dataclasses import replace
    t = np.asarray(log.t_us)
    breaks = []
    for stamp, k in changes or ():
        x, y, _ = log.rear[int(np.clip(np.searchsorted(t, stamp), 0, len(t) - 1))]
        breaks.append((log.road.project(x, y).s, k))
    return replace(log, road=_LaneRelativeRoad(log.road, sorted(breaks)))


def _widening_dlc(log, road):
    """PP-SWR-060 follows the original lane through the widened cross section."""
    geometry = road.layout.geometry
    request_s = log.scenario.hwa_request_s
    if geometry is None or request_s is None:
        return None
    reference = road._road
    minimum = float("inf")
    first_fail_s = None
    hint = None
    for stamp, (x, y, _) in zip(log.t_us, log.front):
        time_s = stamp * 1e-6
        if time_s < request_s:
            continue
        p = reference.project(x, y, hint)
        hint = p.s
        for side, sign, wide in zip((Side.LEFT, Side.RIGHT), (1, -1), geometry.widening_sides(p.s)):
            if not wide:
                continue
            boundary = _variable_boundary(geometry, p.s, geometry.ego_id, side)
            dlc = sign * (boundary - p.d) - log.vehicle_width / 2
            minimum = min(minimum, dlc)
            if dlc < 0 and first_fail_s is None:
                first_fail_s = time_s
    return Criterion("PP-SWR-060", "DLC nhỏ nhất phía mở rộng của làn thật [m]", minimum, ">= 0",
                     minimum >= 0, applicable=isfinite(minimum), first_fail_s=first_fail_s)


def evaluate(log: RunLog, calibration: dict[str, float] | None = None) -> Result:
    """`calibration`: values of the build under test that requirements point to; by
    default read from the delivered calibration data set."""
    log = lane_relative(log)
    road, truth = log.road, _Truth(log)
    geometry = road.layout.geometry
    cal = calibration if calibration is not None else requirement_parameters()
    cycles = log.cycles
    t_s = np.array([c.t0_us * 1e-6 for c in cycles])
    valid = np.array([_valid(c) for c in cycles])
    hwa = np.array([_hwa(c) for c in cycles])
    requests = {f: _request_windows(cycles, f) for f in INTERVENTION_FUNCTIONS}
    episodes = _intervention_windows(cycles, valid, requests)

    # Execution fault (8.4) first: a cycle with a non-finite output is not projected on the road.
    finite = np.array([_finite_outputs(c) for c in cycles])

    # Truth along every valid path, once.
    paths: list[_PathTruth | None] = []
    s_hint = None
    for c, ok, good in zip(cycles, valid, finite):
        if ok and good:
            p, s_hint = _path_truth(c, truth, road, s_hint)
            paths.append(p)
        else:
            paths.append(None)
    need_max = np.array([p.ay_need_max if p is not None else 0.0 for p in paths])

    # PP-SWR-010, 150: outputs every cycle; PP-SWR-009 same flag in both.
    sent_every_cycle = all(c.trajectory is not None and c.path_status is not None for c in cycles)
    limits_every_cycle = all(c.lateral_limits is not None for c in cycles)
    flag_status = np.array([bool(c.path_status.lateral_limit_reached) if c.path_status else False
                            for c in cycles])
    flag_same = all(c.lateral_limits is None or c.path_status is None
                    or c.lateral_limits.lateral_limit_reached == c.path_status.lateral_limit_reached
                    for c in cycles)

    # PP-SWR-001, 003, 006 while HWA drives; 116, 117 on every valid path; 050 target.
    first: dict[str, float] = {}  # requirement -> time of the first failing cycle [s]

    def mark(requirement: str, time_s: float) -> None:
        first.setdefault(requirement, float(time_s))

    for i, c in enumerate(cycles):
        if c.trajectory is None or c.path_status is None:
            mark("PP-SWR-010", t_s[i])
        if c.lateral_limits is None:
            mark("PP-SWR-150", t_s[i])
        if (c.lateral_limits is not None and c.path_status is not None
                and c.lateral_limits.lateral_limit_reached != c.path_status.lateral_limit_reached):
            mark("PP-SWR-009", t_s[i])

    ay_max = jerk_max = wheel_max = wheel_rate_max = deviation_max = 0.0
    jerk_sq_sum, jerk_count = 0.0, 0  # PP-SWR-004 RMS: jerk of the 0-1 s part of HWA paths
    ay_floor_margin = np.inf  # PP-SWR-006: min of |a_y| - (aysmax - epsilon) where needed > aysmax
    n_window = round(DEVIATION_WINDOW_S / GRID_STEP_S) + 1
    for c, p in zip(cycles, paths):
        if p is None:
            continue
        now_s = c.t0_us * 1e-6
        _, _, _, _, _, _, wheel = _points(c.trajectory)
        wheel_max = max(wheel_max, float(np.max(np.abs(wheel))))
        wheel_rate = np.abs(np.diff(wheel)) / GRID_STEP_S * log.steering_ratio
        wheel_rate_max = max(wheel_rate_max, float(np.max(wheel_rate)))
        if wheel_max > log.max_wheel_angle:
            mark("PP-SWR-116", now_s)
        if wheel_rate_max > log.max_steering_wheel_rate:
            mark("PP-SWR-117", now_s)
        if not _hwa(c):
            continue
        ay_max = max(ay_max, float(np.max(np.abs(p.ay))))
        jerk_max = max(jerk_max, _jerk_max(p.ay))
        near_jerk = np.diff(p.ay[:n_window]) / GRID_STEP_S
        jerk_sq_sum += float(np.sum(near_jerk ** 2))
        jerk_count += len(near_jerk)
        if ay_max > AYSMAX:
            mark("PP-SWR-001", now_s)
        if jerk_max > JERK_MAX_HWA:
            mark("PP-SWR-003", now_s)
        deviation_max = max(deviation_max, float(np.max(np.abs(p.d[:n_window]))))
        # PP-SWR-006 judges the 0-1 s part of the path (SRS 1.2).
        near = np.arange(len(p.ay)) < n_window
        over = near & p.in_view & (np.abs(p.ay_need) > AYSMAX)
        if np.any(over):
            same_side = np.sign(p.ay[over]) == np.sign(p.ay_need[over])
            margin = np.where(same_side, np.abs(p.ay[over]), -np.inf) - (AYSMAX - cal["epsilon_ay"])
            ay_floor_margin = min(ay_floor_margin, float(np.min(margin)))
            if ay_floor_margin < 0.0:
                mark("PP-SWR-006", now_s)

    # PP-SWR-005: path stays valid with HWA while the curve needs more than aysmax.
    first_hwa = int(np.argmax(hwa)) if np.any(hwa) else len(cycles)
    hwa_request_s = log.scenario.hwa_request_s
    requested = t_s >= (hwa_request_s if hwa_request_s is not None else np.inf)
    sharp = np.zeros(len(cycles), dtype=bool)
    for i in range(first_hwa, len(cycles)):
        # A cycle without a path uses the curvature seen by the previous one.
        sharp[i] = (need_max[i] if paths[i] is not None else need_max[i - 1]) > AYSMAX
    judged_005 = sharp & requested
    kept_005 = bool(np.all(hwa[judged_005])) if np.any(judged_005) else True
    if not kept_005:
        mark("PP-SWR-005", t_s[int(np.argmax(judged_005 & ~hwa))])

    # PP-SWR-007 (R79 5.6.2.2.3; Annex 8 3.2.5.2): when a front tyre starts to touch the
    # marking while HWA drives and the curve needs more than aysmax, the flag is already on.
    # Target 064: lead of the flag before the need at the car passes aysmax.
    t0s = np.array([c.t0_us for c in cycles])
    half_lane, half_car = 0.5 * road.lane_width, 0.5 * log.vehicle_width
    crossings = late_007 = 0
    inside = True
    above = False
    leads = []
    need_car_max = 0.0
    s_hint = None
    for k in range(0, len(log.t_us), TRUTH_STEP):
        t_us = log.t_us[k]
        i = int(np.searchsorted(t0s, t_us, side="right")) - 1
        pf = road.project(truth.front[k][0], truth.front[k][1], s_hint)
        s_hint = pf.s
        if geometry is None:
            dlc = min(half_lane - pf.d, half_lane + pf.d) - half_car
        else:
            dlc = min(_dlc(log, pf, Side.LEFT), _dlc(log, pf, Side.RIGHT))
        driving = i >= 0 and hwa[i]
        if dlc < 0.0 and inside and driving and need_max[i] > AYSMAX:
            crossings += 1
            late_007 += 0 if flag_status[i] else 1
            if not flag_status[i]:
                mark("PP-SWR-007", t_us * 1e-6)
        inside = dlc >= 0.0
        need_car = log.speed[k] ** 2 * abs(pf.curvature)
        need_car_max = max(need_car_max, need_car)
        if need_car > AYSMAX and not above and driving:
            leads.append(_flag_lead(t_us * 1e-6, t_s, flag_status))
        above = need_car > AYSMAX

    # Target 008: time from the need ahead falling below aysmax to the flag clearing.
    clear_times = []
    for i in range(1, len(cycles)):
        if valid[i] and valid[i - 1] and need_max[i - 1] >= AYSMAX > need_max[i]:
            for j in range(i, len(cycles)):
                if need_max[j] >= AYSMAX:
                    break
                if not flag_status[j]:
                    clear_times.append(t_s[j] - t_s[i])
                    break

    # PP-SWR-100 to 102: consecutive valid paths.
    cont = [0.0, 0.0, 0.0]
    intervention_starts = {e.start for e in episodes}
    for i in range(1, len(cycles)):
        if valid[i - 1] and valid[i] and finite[i - 1] and finite[i]:
            if i in intervention_starts:
                d, v_lat = _entry_errors(cycles[i - 1], cycles[i].t0_us, truth)
                if d > ENTRY_D_M or v_lat > ENTRY_V_LAT_MPS:
                    continue  # PP-SWR-031: exception only at the first tick
            for j, value in enumerate(_continuity(cycles[i - 1], cycles[i], truth)):
                cont[j] = max(cont[j], value)
                if value > (CONTINUITY_LATERAL_M, CONTINUITY_HEADING_RAD, CONTINUITY_CURVATURE)[j]:
                    mark(("PP-SWR-100", "PP-SWR-101", "PP-SWR-102")[j], t_s[i])

    # PP-SWR-018: observed_horizon_s may not exceed the time the path leaves the reported view
    # range by more than HORIZON_TOL_S; reporting less is the safe side (SRS 1.10).
    horizon_err = -np.inf
    for c, good in zip(cycles, finite):
        if not good or not _valid(c) or c.lane_view is None or c.lane_view_reported is None:
            continue
        t_p, x_p = _points(c.trajectory)[0], _points(c.trajectory)[1]
        x_lim = _view_limit(c, truth)
        out = np.nonzero(x_p > x_lim)[0]
        if len(out) == 0:
            expected = t_p[-1]
        elif out[0] == 0:
            expected = 0.0
        else:
            k = out[0]
            expected = t_p[k - 1] + (t_p[k] - t_p[k - 1]) * (x_lim - x_p[k - 1]) / (x_p[k] - x_p[k - 1])
        horizon_err = max(horizon_err, c.trajectory.observed_horizon_s - expected)

    # PP-SWR-051: DLC on the true lane at the front axle while HWA drives, a_y needed <= aysmax
    # and the true free space each side >= free_space_min (SRS 1.4). Below it, PP-SWR-063.
    free_space = (log.road.lane_width - log.vehicle_width) / 2.0
    lane_wide_enough = free_space >= cal["free_space_min"]
    # The driver steers while overriding (driver_override in FunctionRequests, ADAS Function
    # Specification 8): HWA is not driving then, so PP-SWR-051 is not judged (S9 c, S17).
    overriding = np.array([c.function_requests is not None and bool(c.function_requests.message.driver_override)
                           for c in cycles], dtype=bool)
    judged_051 = hwa & ~overriding & (need_max <= AYSMAX) & (lane_wide_enough or geometry is not None)
    if geometry is None:
        narrow_flags = [bool(c.path_status.lane_too_narrow) for c in cycles if _valid(c)]
        judge_narrow = not lane_wide_enough
    else:
        narrow_flags = []
        for c in cycles:
            if _valid(c):
                x, y, _ = truth.rear_at(c.t0_us)
                station = road.project(x, y).s
                low, high = geometry.bounds(station, road._index(station))
                if (high - low - log.vehicle_width) / 2 < cal["free_space_min"]:
                    narrow_flags.append(bool(c.path_status.lane_too_narrow))
        judge_narrow = True
    narrow_share = float(np.mean(narrow_flags)) if narrow_flags else float("nan")
    dlc_left = dlc_right = np.inf
    offset_max = 0.0
    s_hint = None
    for t_us, front, rear in zip(log.t_us, truth.front, truth.rear):
        i = int(np.searchsorted(t0s, t_us, side="right")) - 1
        if i < 0 or not judged_051[i]:
            continue
        pf = road.project(front[0], front[1], s_hint)
        s_hint = pf.s
        if geometry is None:
            dlc_left = min(dlc_left, half_lane - pf.d - half_car)
            dlc_right = min(dlc_right, half_lane + pf.d - half_car)
        else:
            low, high = geometry.bounds(pf.s, road._index(pf.s))
            if (high - low - log.vehicle_width) / 2 < cal["free_space_min"]:
                continue
            dlc_left = min(dlc_left, _dlc(log, pf, Side.LEFT))
            dlc_right = min(dlc_right, _dlc(log, pf, Side.RIGHT))
        offset_max = max(offset_max, abs(road.project(rear[0], rear[1], s_hint).d))
    dlc_min = float(min(dlc_left, dlc_right))

    # S2: HWA starting off centre (PP-SWR-052; targets 002, 053), on the true car offset.
    start_offset = time_to_centre = None
    ay_add_recentre = 0.0
    judged_052 = kept_052 = False
    if np.any(hwa):
        t_hwa = cycles[first_hwa].t0_us
        idx = [i for i in range(0, len(log.t_us), TRUTH_STEP) if log.t_us[i] >= t_hwa]
        s_hint = None
        t_centred = None
        for i in idx:
            r = truth.rear[i]
            proj = road.project(r[0], r[1], s_hint)
            s_hint = proj.s
            if start_offset is None:
                start_offset = proj.d
            if abs(proj.d) <= CENTRED_M:
                t_centred = log.t_us[i]
                break
        end_us = t_centred if t_centred is not None else cycles[-1].t0_us
        time_to_centre = (end_us - t_hwa) * 1e-6 if t_centred is not None else float("inf")
        window = [i for i in range(first_hwa, len(cycles)) if cycles[i].t0_us <= end_us]
        judged_052 = CENTRED_M < abs(start_offset) <= RECENTER_MAX_M + 0.05
        kept_052 = all(hwa[i] for i in window)
        for i in window:
            if paths[i] is not None:
                ay_add_recentre = max(ay_add_recentre,
                                      float(np.max(np.abs(paths[i].ay - paths[i].ay_need))))

    # PP-SWR-125 (F06): path deviation on 2-3 s over that of a path that follows the wrong
    # lane model exactly (offset c2 x^2 or c3 x^3), worst over frames with the fault.
    curvature_ratio = None
    shape_faults = [f for f in log.scenario.lane_faults if f.kind in ("c2_error", "c3_error")]
    if shape_faults:
        curvature_ratio = 0.0
        far = slice(round(2.0 / GRID_STEP_S), round(3.0 / GRID_STEP_S) + 1)
        for c, p in zip(cycles, paths):
            if p is None or not _hwa(c) or c.lane_view is None:
                continue
            t_capture = c.lane_view[0] * 1e-6
            x = _points(c.trajectory)[1][far]
            wrong = np.zeros(len(x))
            for f in shape_faults:
                if f.active(t_capture):
                    wrong += f.value * (x ** 2 if f.kind == "c2_error" else x ** 3)
            if np.max(np.abs(wrong)) > 0.0:
                ratio = float(np.max(np.abs(p.d[far])) / np.max(np.abs(wrong)))
                curvature_ratio = max(curvature_ratio, ratio)

    # PP-SWR-055, 056, 058; targets 057, 059: big vehicle in an adjacent lane.
    big = _big_vehicles(log, cycles, paths, truth, cal["gap_truck_min"])

    compute_ms = np.array([c.compute_ns for c in cycles]) * 1e-6
    # Histogram for the suite report (Software Qualification Test Specification 10): counts per
    # bin of COMPUTE_BINS_MS, so a suite can pool every cycle of every run.
    compute_hist = np.histogram(np.clip(compute_ms, COMPUTE_BINS_MS[0], COMPUTE_BINS_MS[-1]),
                                               COMPUTE_BINS_MS)[0].tolist() if len(compute_ms) else []
    hwa_requested = [c for c in cycles if hwa_request_s is not None and c.t0_us >= hwa_request_s * 1e6]
    any_hwa = bool(np.any(hwa))
    timeout_share, timeout_judged = _requests_timeout_share(cycles)
    # PP-SWR-017: a lane model with a view range beyond what the planner uses stays valid input.
    long_view = [c for c in cycles if c.lane_view_reported is not None and c.lane_view_reported > LONG_VIEW_M]
    long_view_valid = (sum(c.path_status is not None and c.path_status.path_valid for c in long_view) / len(long_view)
                       if long_view else 1.0)
    criteria = [
        Criterion("PP-SWR-010", "Trajectory và PathStatus mỗi chu kỳ", float(sent_every_cycle),
                  "= 1", sent_every_cycle),
        Criterion("PP-SWR-048", "Tỉ lệ chu kỳ quá timeout từ FunctionRequests dùng được gần nhất có NONE và path không hợp lệ",
                  timeout_share, "= 1", timeout_share == 1.0, applicable=timeout_judged),
        Criterion("PP-SWR-018", "observed_horizon_s trừ thời điểm ra khỏi tầm nhìn, lớn nhất [s]",
                  float(horizon_err), f"<= {HORIZON_TOL_S}", bool(horizon_err <= HORIZON_TOL_S),
                  applicable=bool(np.isfinite(horizon_err))),
        Criterion("PP-SWR-017", "Tỉ lệ chu kỳ có path hợp lệ khi lane model báo tầm nhìn > 126 m",
                  long_view_valid, "= 1", long_view_valid == 1.0, applicable=bool(long_view)),
        Criterion("PP-SWR-150", "LateralLimits mỗi chu kỳ", float(limits_every_cycle), "= 1",
                  limits_every_cycle),
        Criterion("PP-SWR-009", "Cờ giới hạn giống nhau ở PathStatus và LateralLimits",
                  float(flag_same), "= 1", flag_same),
        Criterion("PP-SWR-051", "DLC nhỏ nhất so với làn thật [m]", dlc_min, ">= 0",
                  dlc_min >= 0.0, applicable=bool(np.any(judged_051) if geometry is None else np.isfinite(dlc_min))),
        Criterion("PP-SWR-063", "Tỉ lệ chu kỳ có path hợp lệ báo lane_too_narrow khi khoảng trống thật < free_space_min",
                  narrow_share, "= 1", narrow_share == 1.0,
                  applicable=bool(judge_narrow and narrow_flags)),
        Criterion("PP-SWR-001", "a_y lớn nhất của path, HWA [m/s²]", ay_max, f"<= {AYSMAX}",
                  ay_max <= AYSMAX, applicable=any_hwa),
        Criterion("PP-SWR-003", "Jerk ngang lớn nhất của path, HWA [m/s³]", jerk_max,
                  f"<= {JERK_MAX_HWA}", jerk_max <= JERK_MAX_HWA, applicable=any_hwa),
        Criterion("PP-SWR-005", "Chu kỳ cua gắt mà mất path hoặc HWA",
                  float(np.count_nonzero(judged_005 & ~hwa)), "= 0", kept_005,
                  applicable=bool(np.any(judged_005))),
        Criterion("PP-SWR-006", "a_y path trừ (aysmax − epsilon_ay), 0–1 s, khi a_y cần > aysmax [m/s²]",
                  ay_floor_margin, ">= 0", ay_floor_margin >= 0.0,
                  applicable=bool(np.isfinite(ay_floor_margin))),
        Criterion("PP-SWR-007", "Lần lốp đè vạch khi cua gắt mà cờ chưa bật", float(late_007),
                  "= 0", late_007 == 0, applicable=crossings > 0),
        Criterion("PP-SWR-052", "HWA giữ suốt đoạn đưa về giữa", float(kept_052), "= 1",
                  kept_052, applicable=judged_052),
        Criterion("PP-SWR-055", "Lệch path về phía xa xe lớn, 0–1 s, nhỏ nhất khi khoảng hở < gap_truck_min [m]",
                  big.away_055 if big else float("nan"), "> 0", bool(big and big.away_055 > 0.0),
                  applicable=bool(big and np.isfinite(big.away_055))),
        Criterion("PP-SWR-056", "Lệch path về phía xe lớn gần nhất, 0–1 s, lớn nhất khi khoảng hở < gap_truck_min [m]",
                  big.toward_056 if big else float("nan"), "<= 0", bool(big and big.toward_056 <= 0.0),
                  applicable=bool(big and np.isfinite(big.toward_056))),
        Criterion("PP-SWR-058", "Lệch path về phía xa xe lớn lúc xe lớn tới ngang hàng [m]",
                  big.away_058 if big and big.away_058 is not None else float("nan"), "> 0",
                  bool(big and big.away_058 is not None and big.away_058 > 0.0),
                  applicable=bool(big and big.away_058 is not None)),
        Criterion("PP-SWR-100", "Lệch ngang giữa hai path liên tiếp [m]", cont[0],
                  f"<= {CONTINUITY_LATERAL_M}", cont[0] <= CONTINUITY_LATERAL_M),
        Criterion("PP-SWR-101", "Lệch hướng giữa hai path liên tiếp [rad]", cont[1],
                  f"<= {CONTINUITY_HEADING_RAD}", cont[1] <= CONTINUITY_HEADING_RAD),
        Criterion("PP-SWR-102", "Lệch độ cong giữa hai path liên tiếp [1/m]", cont[2],
                  f"<= {CONTINUITY_CURVATURE}", cont[2] <= CONTINUITY_CURVATURE),
        Criterion("PP-SWR-116", "Góc bánh lớn nhất trên path [rad]", wheel_max,
                  f"<= {log.max_wheel_angle:.3f}", wheel_max <= log.max_wheel_angle),
        Criterion("PP-SWR-117", "Tốc độ quay vô lăng lớn nhất suy ra từ path [rad/s]",
                  wheel_rate_max, f"<= {log.max_steering_wheel_rate}",
                  wheel_rate_max <= log.max_steering_wheel_rate),
    ]
    widening = _widening_dlc(log, road)
    if widening is not None:
        criteria.append(widening)
        if widening.first_fail_s is not None:
            mark(widening.id, widening.first_fail_s)
    criteria += _input_age_criteria(cycles, hwa_request_s) + _request_change_criteria(cycles)
    criteria += _yaw_delay_criterion(log.scenario, criteria)
    targets = [
        Target("PP-SWR-050", "Lệch ngang của path so với tâm làn thật, 0–1 s, lớn nhất",
               deviation_max, "m"),
        Target("PP-SWR-053", "Thời gian đưa xe về giữa (lệch ≤ 0,1 m)",
               time_to_centre if time_to_centre is not None else float("nan"), "s"),
        Target("PP-SWR-002", "a_y thêm vào lớn nhất khi đưa về giữa", ay_add_recentre, "m/s²"),
        Target("PP-SWR-016", "Thời gian tính trung bình", float(np.mean(compute_ms)), "ms"),
        Target("PP-SWR-016", "Thời gian tính p95", float(np.percentile(compute_ms, 95)), "ms"),
        Target("PP-SWR-016", "Thời gian tính p99", float(np.percentile(compute_ms, 99)), "ms"),
        Target("PP-SWR-016", "Thời gian tính lớn nhất", float(np.max(compute_ms)), "ms"),
    ]
    if jerk_count:  # PP-SWR-004 (Software Qualification Test Specification 8.2), path while HWA drives
        targets.append(Target("PP-SWR-004", "Jerk ngang lớn nhất của path khi HWA lái (trung bình 0,5 s)",
                              jerk_max, "m/s³"))
        targets.append(Target("PP-SWR-004", "Jerk ngang RMS của path 0–1 s khi HWA lái",
                              float(np.sqrt(jerk_sq_sum / jerk_count)), "m/s³"))
    wheel_rate_rms = _steering_rate_rms(log, t_s, hwa)
    if wheel_rate_rms is not None:
        targets.append(Target("PP-SWR-004", "Tốc độ quay vô lăng RMS khi HWA lái, vòng kín",
                              wheel_rate_rms, "rad/s"))
    if big is not None and np.isfinite(big.clearance_057):
        targets.append(Target("PP-SWR-057", "Khoảng cách ngang nhỏ nhất từ thân xe tới xe lớn khi ngang hàng",
                              big.clearance_057, "m"))
    barrier = _barrier_clearance(log, cycles, truth)
    if barrier is not None:
        targets.append(Target("PP-SWR-057", "Khoảng cách ngang nhỏ nhất từ thân xe tới rào chắn khi HWA lái",
                              barrier, "m"))
    if big is not None and big.return_059 is not None:
        targets.append(Target("PP-SWR-059", "Thời gian từ lúc hết ngang hàng tới lúc lệch ≤ 0,1 m",
                              big.return_059, "s"))
    if leads:
        targets.insert(0, Target("PP-SWR-064", "Thời gian báo trước nhỏ nhất (âm là báo muộn)",
                                 float(min(leads)), "s"))
    if clear_times:
        targets.insert(0, Target("PP-SWR-008", "Thời gian tắt cờ lớn nhất", float(max(clear_times)), "s"))
    if curvature_ratio is not None:
        targets.insert(0, Target("PP-SWR-125", "Lệch path 2–3 s / lệch của path bám lane model sai",
                                 curvature_ratio, "-"))
    info = {
        "cycles": len(cycles),
        "init_result": log.init_result,
        "first_hwa_s": float(t_s[first_hwa]) if any_hwa else None,
        "hwa_share_after_request": (sum(_hwa(c) for c in hwa_requested) / len(hwa_requested)
                                    if hwa_requested else 0.0),
        "ay_need_max": float(np.max(need_max)) if len(need_max) else 0.0,
        "offset_at_hwa_start_m": start_offset,
        "ay_need_at_car_max": need_car_max,
        "speed_min_mps": float(min(log.speed)) if log.speed else None,
        "decel_max_mps2": (float(-min(np.diff(log.speed)) / 1e-3) if len(log.speed) > 1 else None),
        "vehicle_offset_max_m": offset_max,
        "free_space_each_side_m": free_space,
        "calibration": cal,
        "compute_time_note": "Đồng hồ thật của máy, gồm cả adapter SIL (ctypes)",
    }
    truth_t = np.asarray(log.t_us, dtype=float) * 1e-6
    info.update(r79_vehicle(truth_t, np.asarray(log.a_y, dtype=float),
                            _cycle_mask_at(truth_t, t_s, hwa) if len(cycles) else np.zeros(len(truth_t), bool)))
    for c in criteria:
        if c.applicable and not c.passed:
            c.first_fail_s = first.get(c.id)
    criteria.append(over_refusal(cycles, log.scenario.notes.get("expected_outcome"),
                                 log.init_result == 0, cal))
    criteria.extend(fault_reaction_criteria(cycles, cal.get("T_coast", 1.0), cal))
    result = Result(log.scenario.name, log.seed, criteria, targets, info)
    result.info["compute_hist"] = compute_hist
    result.criteria.extend(longitudinal_criteria(log, cycles))
    result.criteria.extend(switch_criteria(log, cycles, cal))
    adas = adas_requests(log)
    if adas is not None:
        result.info["adas_requests"] = adas
    fault = execution_fault([cycles[k] for k in np.flatnonzero(~finite)[:1]])  # first bad cycle
    if fault is not None:
        add_issue(result, ISSUE_EXECUTION, f"Lỗi thực thi: {fault[1]} không hữu hạn tại t = {fault[0]:.3f} s",
                  first_fail_s=fault[0])
    _score_interventions(result, truth, paths, episodes, requests, cal, t_s)
    # Faults started by a planner-output event (Software Qualification Test Specification 6).
    events = getattr(log, "fault_events", None) or {}
    if events:
        result.info["fault_events_s"] = {k: None if v is None else v * 1e-6 for k, v in events.items()}
        missing = sorted(k for k, v in events.items() if v is None)
        if missing:
            result.info["faults_not_injected"] = missing
    # PP-SWR-062: at an end of the ODD (label L1), every requirement of the run holds.
    from eval import labels
    if labels.difficulty(log.scenario) == "L1":
        failed = [c.id for c in result.criteria if c.applicable and not c.passed] + list(result.case_failures)
        result.criteria.append(Criterion("PP-SWR-062", "Requirement trượt ở biên ODD", float(len(failed)), "= 0",
                                         not failed))
    if getattr(log.scenario, "loop", "closed") == "open":
        for c in result.criteria:
            if c.id in VEHICLE_CRITERIA:
                c.applicable = False
        result.info["loop"] = "open"
    if log.scenario.adas_mode == "A":
        result.scored = False
        result.criteria.clear()
        result.targets.clear()
        result.case_failures.clear()
        result.issues.clear()
    return result

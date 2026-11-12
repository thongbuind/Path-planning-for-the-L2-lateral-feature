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
from math import cos, hypot, sin

import numpy as np

from eval.calibration import requirement_parameters
from interfaces import (
    FUNCTION_REQUESTS_MAX_AGE_US, FUNCTION_REQUESTS_TIMEOUT_US,
    TRAJECTORY_STEP_S, ActiveFunction, ElkReason, FunctionRequest, InterventionPhase, RequestState, Side,
)
from sim.harness import PlannerCycle, RunLog
from sim.stand_ins.eps import HANDOVER_S
from sim.world.traffic import Traffic

AYSMAX = 2.5  # [m/s^2] PP-SWR-001
HORIZON_TOL_S = 0.1  # [s] PP-SWR-018, one Trajectory step
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
MAX_INTERVENTION_S = 10.0  # PP-SWR-083
MARK_DTLE_MIN_M = -0.3  # PP-SWR-086, 091
EDGE_DTLE_MIN_M = -0.1  # PP-SWR-086, 091
OTHER_CAR_GAP_MIN_M = 0.3  # PP-SWR-088
LATE_ELK_DLC_M = -0.3  # PP-SWR-089
FUTURE_STAMP_TOLERANCE_US = 10_000  # PP-SWR-132

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

    @property
    def passed(self) -> bool | None:
        if not self.scored:
            return None
        return not self.case_failures and all(c.passed for c in self.criteria if c.applicable)

    def to_dict(self) -> dict:
        return {"scenario": self.scenario, "seed": self.seed, "passed": self.passed,
                "criteria": [asdict(c) for c in self.criteria],
                "targets": [asdict(t) for t in self.targets], "info": self.info,
                "case_failures": self.case_failures, "scored": self.scored}


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


def _big_vehicles(log: RunLog, cycles, paths, truth: _Truth, gap_min: float) -> _BigVehicles | None:
    road, w = log.road, log.road.lane_width
    specs = [sp for sp in log.scenario.traffic
             if sp.width >= BIG_VEHICLE_WIDTH_M and w / 2 < abs(sp.d) < 1.5 * w]
    if not specs:
        return None
    traffic = Traffic(road, tuple(specs))
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
                side = 1 if v.d > 0 else -1
                gaps[side] = min(gaps[side], abs(v.d) - 0.5 * v.width - half_car)
                for d_car in (pr.d, pf.d):
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
    i = truth.index(t_us)
    rear = truth.rear[i]
    actual = truth.log.road.project(rear[0], rear[1])
    d, v_lat, _ = _path_at(cycle, t_us, truth)
    return abs(d - actual.d), abs(v_lat - truth.lateral_velocity(i, actual.heading))


def _boundary_offset(road, side, *, edge=False):
    index = 0 if side == Side.LEFT else 1
    boundary = road.layout.markings[index + 1]
    if edge or boundary is None:
        boundary = road.layout.edges[index]
    if boundary is None:
        return (1 if side == Side.LEFT else -1) * road.lane_width / 2
    return boundary.offset_m


def _dlc(log, projection, side, *, edge=False):
    sign = 1 if side == Side.LEFT else -1
    return sign * (_boundary_offset(log.road, side, edge=edge) - projection.d) - log.vehicle_width / 2


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


def _score_interventions(result, truth, paths, episodes, requests, cal, cycle_times):
    log, cycles = truth.log, truth.log.cycles
    expected = log.scenario.notes.get("expect_intervention")
    if not (expected or episodes or any(requests.values())):
        return
    issues = result.case_failures
    if expected in ("LKA", "ELK"):
        function = ActiveFunction[expected]
        desired = log.scenario.notes.get("departure_side")
        expected_requests = [r for r in requests[function]
                             if desired is None or r.message.side.name.lower() == desired]
        if not expected_requests:
            side = "" if desired is None else f" (phía {'trái' if desired == 'left' else 'phải'})"
            issues.append(f"{expected}: thiếu REQUEST đến planner{side}")
        elif (any(not any(e.request is r and e.function == function for e in episodes)
                  for r in expected_requests)
              or any(_phase(c, function) == InterventionPhase.ACTIVE and not _valid(c) for c in cycles)):
            issues.append(f"{expected}: có REQUEST nhưng thiếu path can thiệp hợp lệ")
    late_dlcs, accepted = _check_late_elk(truth, requests[ActiveFunction.ELK])
    if expected == "late ELK":
        if not requests[ActiveFunction.ELK]:
            issues.append("PP-SWR-089: thiếu REQUEST bơm muộn đến planner")
        elif not late_dlcs:
            issues.append("PP-SWR-089: lốp trước chưa qua vạch hơn 0,3 m tại lúc nhận REQUEST")

    starts = []
    durations = []
    timed_functions = set()
    censored_functions = set()
    opposite_dlcs, completed_dlcs = [], []
    dtle_mark, dtle_edge, dtle_lka = [], [], []
    times_to_complete = {f: [] for f in INTERVENTION_FUNCTIONS}
    end_judged = late_completion = early_completion = n_completed = 0
    details = []
    for i, episode in enumerate(episodes):
        function = episode.function
        if episode.request is None:
            issues.append(f"{function.name}: path can thiệp thiếu REQUEST tương ứng")
            continue
        req = episode.request.message
        if req.side not in (Side.LEFT, Side.RIGHT):
            issues.append(f"{function.name}: REQUEST thiếu phía can thiệp")
            continue
        start_us = cycles[episode.start].t0_us
        end_seen = episode.stop < len(cycles)
        stop_us = cycles[episode.stop].t0_us if end_seen else int(truth.t[-1])
        next_us = next((cycles[e.start].t0_us for e in episodes[i + 1:]
                        if e.function != function or e.request is not episode.request), int(truth.t[-1]))
        edge = req.elk_reason == ElkReason.ROAD_EDGE
        lka = function == ActiveFunction.LKA
        starts.append(_entry_errors(cycles[episode.start], start_us, truth))
        elapsed_s = (stop_us - episode.request.rx_us) * 1e-6
        if end_seen or elapsed_s >= MAX_INTERVENTION_S:
            durations.append(elapsed_s if end_seen else float("inf"))
            timed_functions.add(function.name)
        else:
            censored_functions.add(function.name)
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

    if expected in censored_functions and expected not in timed_functions:
        issues.append(f"{expected}: ca kết thúc trước khi đủ cửa sổ chấm thời lượng")

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
    upper("PP-SWR-083", "Thời lượng từ REQUEST tới COMPLETED hoặc hủy [s]", durations, MAX_INTERVENTION_S)
    lower("PP-SWR-084", "DLC phía trôi khi LKA COMPLETED [m]", completed_dlcs, 0)
    lower("PP-SWR-085", "DLC phía đối diện qua bàn giao EPS [m]", opposite_dlcs, 0)
    lower("PP-SWR-086", "DTLE vạch nhỏ nhất [m]", dtle_mark, MARK_DTLE_MIN_M)
    lower("PP-SWR-086", "DTLE mép đường nhỏ nhất [m]", dtle_edge, EDGE_DTLE_MIN_M)
    if abs(log.actuator_delay_s - 0.1) <= 1e-7:
        lower("PP-SWR-091", "DTLE vạch với trễ EPS 100 ms [m]", dtle_mark, MARK_DTLE_MIN_M)
        lower("PP-SWR-091", "DTLE mép với trễ EPS 100 ms [m]", dtle_edge, EDGE_DTLE_MIN_M)
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
        active_paths = [p for p, use in zip(paths, active) if use]
        ay_limit, added_limit, jerk_limit = INTERVENTION_LIMITS[function]
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


def evaluate(log: RunLog, calibration: dict[str, float] | None = None) -> Result:
    """`calibration`: values of the build under test that requirements point to; by
    default read from the delivered calibration data set."""
    road, truth = log.road, _Truth(log)
    cal = calibration if calibration is not None else requirement_parameters()
    cycles = log.cycles
    t_s = np.array([c.t0_us * 1e-6 for c in cycles])
    valid = np.array([_valid(c) for c in cycles])
    hwa = np.array([_hwa(c) for c in cycles])
    requests = {f: _request_windows(cycles, f) for f in INTERVENTION_FUNCTIONS}
    episodes = _intervention_windows(cycles, valid, requests)

    # Truth along every valid path, once.
    paths: list[_PathTruth | None] = []
    s_hint = None
    for c, ok in zip(cycles, valid):
        if ok:
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
    ay_max = jerk_max = wheel_max = wheel_rate_max = deviation_max = 0.0
    ay_floor_margin = np.inf  # PP-SWR-006: min of |a_y| - (aysmax - epsilon) where needed > aysmax
    n_window = round(DEVIATION_WINDOW_S / GRID_STEP_S) + 1
    for c, p in zip(cycles, paths):
        if p is None:
            continue
        _, _, _, _, _, _, wheel = _points(c.trajectory)
        wheel_max = max(wheel_max, float(np.max(np.abs(wheel))))
        wheel_rate = np.abs(np.diff(wheel)) / GRID_STEP_S * log.steering_ratio
        wheel_rate_max = max(wheel_rate_max, float(np.max(wheel_rate)))
        if not _hwa(c):
            continue
        ay_max = max(ay_max, float(np.max(np.abs(p.ay))))
        jerk_max = max(jerk_max, _jerk_max(p.ay))
        deviation_max = max(deviation_max, float(np.max(np.abs(p.d[:n_window]))))
        # PP-SWR-006 judges the 0-1 s part of the path (SRS 1.2).
        near = np.arange(len(p.ay)) < n_window
        over = near & p.in_view & (np.abs(p.ay_need) > AYSMAX)
        if np.any(over):
            same_side = np.sign(p.ay[over]) == np.sign(p.ay_need[over])
            margin = np.where(same_side, np.abs(p.ay[over]), -np.inf) - (AYSMAX - cal["epsilon_ay"])
            ay_floor_margin = min(ay_floor_margin, float(np.min(margin)))

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
        dlc = min(half_lane - pf.d, half_lane + pf.d) - half_car
        driving = i >= 0 and hwa[i]
        if dlc < 0.0 and inside and driving and need_max[i] > AYSMAX:
            crossings += 1
            late_007 += 0 if flag_status[i] else 1
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
        if valid[i - 1] and valid[i]:
            if i in intervention_starts:
                d, v_lat = _entry_errors(cycles[i - 1], cycles[i].t0_us, truth)
                if d > ENTRY_D_M or v_lat > ENTRY_V_LAT_MPS:
                    continue  # PP-SWR-031: exception only at the first tick
            for j, value in enumerate(_continuity(cycles[i - 1], cycles[i], truth)):
                cont[j] = max(cont[j], value)

    # PP-SWR-018: observed_horizon_s against the time the path leaves the reported view range.
    horizon_err = 0.0
    for c in cycles:
        if not _valid(c) or c.lane_view is None or c.lane_view_reported is None:
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
        horizon_err = max(horizon_err, abs(c.trajectory.observed_horizon_s - expected))

    # PP-SWR-051: DLC on the true lane at the front axle while HWA drives, a_y needed <= aysmax
    # and the true free space each side >= free_space_min (SRS 1.4). Below it, PP-SWR-063.
    free_space = (log.road.lane_width - log.vehicle_width) / 2.0
    lane_wide_enough = free_space >= cal["free_space_min"]
    judged_051 = hwa & (need_max <= AYSMAX) & lane_wide_enough
    narrow_flags = [bool(c.path_status.lane_too_narrow) for c in cycles if _valid(c)]
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
        dlc_left = min(dlc_left, half_lane - pf.d - half_car)
        dlc_right = min(dlc_right, half_lane + pf.d - half_car)
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
    hwa_requested = [c for c in cycles if hwa_request_s is not None and c.t0_us >= hwa_request_s * 1e6]
    any_hwa = bool(np.any(hwa))
    # PP-SWR-017: a lane model with a view range beyond what the planner uses stays valid input.
    long_view = [c for c in cycles if c.lane_view_reported is not None and c.lane_view_reported > LONG_VIEW_M]
    long_view_valid = (sum(c.path_status is not None and c.path_status.path_valid for c in long_view) / len(long_view)
                       if long_view else 1.0)
    criteria = [
        Criterion("PP-SWR-010", "Trajectory và PathStatus mỗi chu kỳ", float(sent_every_cycle),
                  "= 1", sent_every_cycle),
        Criterion("PP-SWR-018", "Sai lệch lớn nhất của observed_horizon_s [s]", horizon_err,
                  f"<= {HORIZON_TOL_S}", horizon_err <= HORIZON_TOL_S),
        Criterion("PP-SWR-017", "Tỉ lệ chu kỳ có path hợp lệ khi lane model báo tầm nhìn > 126 m",
                  long_view_valid, "= 1", long_view_valid == 1.0, applicable=bool(long_view)),
        Criterion("PP-SWR-150", "LateralLimits mỗi chu kỳ", float(limits_every_cycle), "= 1",
                  limits_every_cycle),
        Criterion("PP-SWR-009", "Cờ giới hạn giống nhau ở PathStatus và LateralLimits",
                  float(flag_same), "= 1", flag_same),
        Criterion("PP-SWR-051", "DLC nhỏ nhất so với làn thật [m]", dlc_min, ">= 0",
                  dlc_min >= 0.0, applicable=bool(np.any(judged_051))),
        Criterion("PP-SWR-063", "Tỉ lệ chu kỳ có path hợp lệ báo lane_too_narrow khi khoảng trống thật < free_space_min",
                  narrow_share, "= 1", narrow_share == 1.0,
                  applicable=bool(not lane_wide_enough and narrow_flags)),
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
    if big is not None and np.isfinite(big.clearance_057):
        targets.append(Target("PP-SWR-057", "Khoảng cách ngang nhỏ nhất từ thân xe tới xe lớn khi ngang hàng",
                              big.clearance_057, "m"))
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
    result = Result(log.scenario.name, log.seed, criteria, targets, info)
    _score_interventions(result, truth, paths, episodes, requests, cal, t_s)
    if log.scenario.adas_mode == "A":
        result.scored = False
        result.criteria.clear()
        result.targets.clear()
        result.case_failures.clear()
    return result

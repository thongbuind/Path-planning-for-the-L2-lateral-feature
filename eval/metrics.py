"""Pass/fail criteria and metrics measured on ground truth (Software Qualification Test
Specification 8.1, 8.2; definitions of Software Requirements Specification section 4).

Only what the planner sends (Trajectory, PathStatus, LateralLimits), its compute time
and the delivered calibration values that requirements point to are used, together
with the simulator's ground truth. Nothing inside the planner is read.

Covered so far: PP-SWR-001, 003, 005, 006, 007, 009, 010, 051, 052, 063, 100 to 102, 116, 117,
150; targets PP-SWR-002, 008, 016, 050, 053, 064, 125. A criterion with no situation to judge in a run is reported as
not applicable. Information only: a_y and jerk on the vehicle as R79 Annex 8, 2.4 measures them
(r79_vehicle), until a requirement points to it.
"""

from dataclasses import asdict, dataclass, field
from math import cos, sin

import numpy as np

from eval.calibration import requirement_parameters
from interfaces import ActiveFunction, TRAJECTORY_STEP_S
from sim.harness import PlannerCycle, RunLog

AYSMAX = 2.5  # [m/s^2] PP-SWR-001
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

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.criteria if c.applicable)

    def to_dict(self) -> dict:
        return {"scenario": self.scenario, "seed": self.seed, "passed": self.passed,
                "criteria": [asdict(c) for c in self.criteria],
                "targets": [asdict(t) for t in self.targets], "info": self.info}


def _valid(c: PlannerCycle) -> bool:
    return (c.trajectory is not None and c.path_status is not None and c.trajectory.header.valid
            and c.path_status.path_valid)


def _hwa(c: PlannerCycle) -> bool:
    return _valid(c) and c.path_status.active_function == ActiveFunction.HWA


class _Truth:
    """Ground-truth base_link pose by time."""

    def __init__(self, log: RunLog) -> None:
        self.t = np.asarray(log.t_us)
        self.rear = np.asarray(log.rear)
        self.front = np.asarray(log.front)

    def rear_at(self, t_us: int) -> tuple[float, float, float]:
        i = int(np.clip(np.searchsorted(self.t, t_us), 0, len(self.t) - 1))
        return tuple(self.rear[i])


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


def _continuity(prev: PlannerCycle, cur: PlannerCycle, truth: _Truth) -> tuple[float, float, float]:
    """Largest lateral, heading and curvature difference between two consecutive paths
    on their common time span, the old path moved by the true motion of the car."""
    t_o, x_o, y_o, yaw_o, k_o, _, _ = _points(prev.trajectory)
    t_n, x_n, y_n, yaw_n, k_n, _, _ = _points(cur.trajectory)
    shift = (cur.t0_us - prev.t0_us) * 1e-6
    pose_o, pose_n = truth.rear_at(prev.t0_us), truth.rear_at(cur.t0_us)
    keep = t_n + shift <= t_o[-1] + 1e-9
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


def _hwa_at(times_s: np.ndarray, cycle_t_s: np.ndarray, hwa: np.ndarray) -> np.ndarray:
    """Ground-truth samples at which the latest planner cycle had HWA driving."""
    idx = np.searchsorted(cycle_t_s, times_s, side="right") - 1
    return (idx >= 0) & hwa[np.clip(idx, 0, len(hwa) - 1)]


def evaluate(log: RunLog, calibration: dict[str, float] | None = None) -> Result:
    """`calibration`: values of the build under test that requirements point to; by
    default read from the delivered calibration data set."""
    road, truth = log.road, _Truth(log)
    cal = calibration if calibration is not None else requirement_parameters()
    cycles = log.cycles
    t_s = np.array([c.t0_us * 1e-6 for c in cycles])
    valid = np.array([_valid(c) for c in cycles])
    hwa = np.array([_hwa(c) for c in cycles])

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
    requested = t_s >= log.scenario.hwa_request_s
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
    for i in range(1, len(cycles)):
        if valid[i - 1] and valid[i]:
            for j, value in enumerate(_continuity(cycles[i - 1], cycles[i], truth)):
                cont[j] = max(cont[j], value)

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

    compute_ms = np.array([c.compute_ns for c in cycles]) * 1e-6
    hwa_requested = [c for c in cycles if c.t0_us >= log.scenario.hwa_request_s * 1e6]
    any_hwa = bool(np.any(hwa))
    criteria = [
        Criterion("PP-SWR-010", "Trajectory và PathStatus mỗi chu kỳ", float(sent_every_cycle),
                  "= 1", sent_every_cycle),
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
                            _hwa_at(truth_t, t_s, hwa) if len(cycles) else np.zeros(len(truth_t), bool)))
    return Result(log.scenario.name, log.seed, criteria, targets, info)

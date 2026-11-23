"""Bên chấm dùng ground truth của simulator và tín hiệu qua ICD (SQTS 8.1–8.2)."""

from dataclasses import asdict, dataclass, field, replace
from math import cos, hypot, isfinite, sin

import numpy as np

from eval.calibration import requirement_parameters
from interfaces import (
    FUNCTION_REQUESTS_MAX_AGE_US, FUNCTION_REQUESTS_TIMEOUT_US, PLANNER_PERIOD_US,
    TRAJECTORY_STEP_S, ElkReason, FunctionRequest, InterventionFunction, InterventionPhase, LccMode, LineStatus,
    PlannerId, RequestState, RoadEdgeType, Side,
)
from sim.harness import PlannerCycle, RunLog, plan_in_range
from sim.stand_ins.arbitrator import ActiveFunction
from sim.stand_ins.eps import HANDOVER_S
from sim.world.road import lane_boundaries
from sim.world.traffic import Traffic

AYSMAX = 2.5
HORIZON_TOL_S = 0.1
_PLANNER_CYCLE_US = 25_000
LONG_VIEW_M = 126.0
JERK_MAX_HWA = 5.0
JERK_WINDOW_S = 0.5
# Giới hạn theo ba khoảng thời gian của path mới. Mỗi hàng gồm lệch ngang [m], hướng [rad] và độ
# cong [1/m] (PP-SWR-100–102).
CONTINUITY_BAND_ENDS_S = (1.0, 2.0)
CONTINUITY_LIMITS = np.array([[0.05, 0.005, 0.0003],
                              [0.1, 0.01, 0.0006],
                              [0.2, 0.02, 0.0012]])
DEVIATION_WINDOW_S = 1.0
CENTRED_M = 0.1
RECENTER_MAX_M = 0.5
TRUTH_STEP = 10
GRID_STEP_S = float(TRAJECTORY_STEP_S)
BIG_VEHICLE_WIDTH_M = 2.3
OTHER_SIDE_OFFSET_M = 0.02
DLC_REVERSAL_MAX_M = 0.1
OFFSET_TOLERANCE_M = 0.02
BODY_OVERHANG_M = 1.0
INTERVENTION_FUNCTIONS = (ActiveFunction.LKA, ActiveFunction.ELK)
INTERVENTION_LIMITS = {ActiveFunction.LKA: (3.0, 1.5, 5.0),
                       ActiveFunction.ELK: (4.0, 3.0, 10.0)}
ENTRY_D_M = ENTRY_V_LAT_MPS = 0.1
ENTRY_KAPPA = 0.0003
MARK_DTLE_MIN_M = -0.3
EDGE_DTLE_MIN_M = -0.1
EPS_DELAY_MAX_S = 0.1
BARRIER_TYPES = (RoadEdgeType.BARRIER, RoadEdgeType.GUARDRAIL)
OTHER_CAR_GAP_MIN_M = 0.3
LATE_ELK_DLC_M = -0.3
FUTURE_STAMP_TOLERANCE_US = 10_000
# PP-SWR-030 cho phép từ chối khi mất đầu vào quy định và trong cửa sổ khôi phục.
FUNCTION_PRIORITY = (ActiveFunction.ELK, ActiveFunction.LKA, ActiveFunction.LCC)
INPUTS_FOR_PATH = ("lane_model", "imu", "steering", "speed", "function_requests", "ego_motion")
RECOVERY_GRACE_S = 1.0

# Lọc a_y tại trọng tâm và tính jerk theo R79 Phụ lục 8, mục 2.4; các chỉ số được báo cáo riêng.
R79_FILTER_ORDER = 4
R79_FILTER_HZ = 0.5
R79_MIN_RATE_HZ = 100.0
R79_AY_TABLE_MAX = 3.0
R79_AY_MARGIN = 0.3
# PP-SWR-001 (SRS 1.26): a_y của path LCC ≤ aysmax + 0,3 m/s² theo R79 5.6.2.1.1.
PATH_AY_MAX_HWA = AYSMAX + R79_AY_MARGIN
R79_AY_SHORT_FACTOR = 1.4
R79_AY_SHORT_S = 2.0


@dataclass
class Criterion:
    id: str
    metric: str
    value: float
    limit: str
    passed: bool
    applicable: bool = True
    first_fail_s: float | None = None


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
    # issues giữ loại lỗi, mã requirement và thời điểm trượt đầu tiên nếu xác định được.
    issues: list[dict] = field(default_factory=list)

    @property
    def passed(self) -> bool | None:
        if not self.scored:
            return None
        if (any(i["kind"] != ISSUE_NOT_JUDGED for i in self.issues)
                or any(c.applicable and not c.passed for c in self.criteria)):
            return False
        return None if self.case_failures else True

    def to_dict(self) -> dict:
        return {"scenario": self.scenario, "seed": self.seed, "passed": self.passed,
                "criteria": [asdict(c) for c in self.criteria],
                "targets": [asdict(t) for t in self.targets], "info": self.info,
                "case_failures": self.case_failures, "scored": self.scored, "issues": self.issues}


COMPUTE_BINS_MS = np.logspace(-3, 3, 61)

ISSUE_REQUIREMENT = "requirement"
ISSUE_NOT_JUDGED = "not_judged"
ISSUE_EXECUTION = "execution"


def add_issue(result: "Result", kind: str, text: str, requirement: str | None = None,
              first_fail_s: float | None = None) -> None:
    result.case_failures.append(text)
    result.issues.append({"kind": kind, "requirement": requirement, "text": text,
                          "first_fail_s": first_fail_s})


_FIELDS: dict[type, tuple[str, ...] | None] = {}


def _nonfinite(value, path: str) -> str | None:
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
    for c in cycles:
        # Kiểm cả đầu ra của planner không được arbitrator chọn.
        for name in ("trajectory", "lateral_limits", "lcc_trajectory", "lcc_status", "ka_trajectory",
                     "intervention_status"):
            message = getattr(c, name, None)
            found = None if message is None else _nonfinite(message, name)
            if found:
                return c.t0_us * 1e-6, found
    return None


def _valid(c: PlannerCycle) -> bool:
    return (c.trajectory is not None and c.path_status is not None and c.trajectory.header.valid
            and c.path_status.path_valid)


def _hwa(c: PlannerCycle) -> bool:
    return _valid(c) and c.path_status.active_function == ActiveFunction.LCC


class _Truth:
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
    """Không chiếu chu kỳ có đầu ra không hữu hạn lên đường; kết quả vẫn ghi lỗi thực thi
    (PP-PR-026).
    """
    return all(m is None or _nonfinite(m, "") is None for m in (c.trajectory, c.path_status, c.lateral_limits))


def _jerk_max(a_y: np.ndarray) -> float:
    jerk = np.diff(a_y) / GRID_STEP_S
    n = max(1, round(JERK_WINDOW_S / GRID_STEP_S))
    if len(jerk) < n:
        return float(np.max(np.abs(jerk))) if len(jerk) else 0.0
    return float(np.max(np.abs(np.convolve(jerk, np.ones(n) / n, mode="valid"))))


def _view_limit(cur: PlannerCycle, truth: _Truth) -> float:
    """Mép tầm nhìn quy về base_link tại t0 theo frame lane model đã dùng. Thiếu lane model thì
    giới hạn là vô cực.
    """
    if cur.lane_view is None or cur.lane_view_reported is None:
        return np.inf
    stamp_us = cur.lane_view[0]
    xc, yc, yawc = truth.rear_at(stamp_us)
    x0, y0, _ = truth.rear_at(cur.t0_us)
    travelled = (x0 - xc) * np.cos(yawc) + (y0 - yc) * np.sin(yawc)
    return cur.lane_view_reported - travelled


def _continuity(prev: PlannerCycle, cur: PlannerCycle, truth: _Truth) -> tuple[float, float, float]:
    """So hai path trong phần trùng thời gian và còn trong tầm nhìn của chu kỳ mới
    (PP-SWR-100–102).
    """
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
    limits = CONTINUITY_LIMITS[np.searchsorted(CONTINUITY_BAND_ENDS_S, t_n[keep] - 1e-9)]
    return (float(np.max(np.abs(lateral) / limits[:, 0])),
            float(np.max(np.abs(_wrap(fyaw - yawn)) / limits[:, 1])),
            float(np.max(np.abs(ko - kn) / limits[:, 2])))


@dataclass
class _BigVehicles:
    """Chấm trung bình offset trên đoạn 0–1 s; dấu dương là tránh xa xe lớn có khoảng hở nhỏ hơn."""

    away_055: float = np.inf
    toward_056: float = -np.inf
    away_058: float | None = None
    clearance_057: float = np.inf
    return_059: float | None = None
    offset_066: float = -np.inf
    other_065: float = -np.inf


def _barrier_clearance(log: RunLog, cycles, truth: _Truth) -> float | None:
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


def _big_vehicles(log: RunLog, cycles, paths, truth: _Truth, gap_min: float, ttc_s: float = 3.0,
                  hold_s: float = 1.0) -> _BigVehicles | None:
    road, w = log.road, log.road.lane_width
    geometry = road.layout.geometry
    specs = [sp for sp in log.scenario.traffic if sp.width >= BIG_VEHICLE_WIDTH_M
             and (geometry is not None or w / 2 < abs(sp.d) < 1.5 * w)]
    if not specs:
        return None
    traffic = Traffic(road._road if geometry is not None else road, tuple(specs))
    others = Traffic(road._road if geometry is not None else road, tuple(
        sp for sp in log.scenario.traffic if sp.width < BIG_VEHICLE_WIDTH_M and sp.direction == 1
        and (geometry is not None or w / 2 < abs(sp.d) < 1.5 * w)))
    half_car = 0.5 * log.vehicle_width
    n_window = round(DEVIATION_WINDOW_S / GRID_STEP_S) + 1
    out = _BigVehicles()
    s_hint = None
    was_abreast = None
    end_us = None
    other_until = {1: -np.inf, -1: -np.inf}
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
        other = {1: False, -1: False}
        v_ego = float(log.speed[truth.index(c.t0_us)])
        for v in others.at(c.t0_us * 1e-6):
            side = 1 if v.d > 0 else -1
            ahead = (v.s - 0.5 * v.length) - body[1]
            behind = body[0] - (v.s + 0.5 * v.length)
            if ahead <= 0 <= behind + v.length + (body[1] - body[0]):
                other[side] = other[side] or behind <= 0
            if ahead > 0 and v_ego - v.speed > 0 and ahead / (v_ego - v.speed) <= ttc_s:
                other[side] = True
            if behind > 0 and v.speed - v_ego > 0 and behind / (v.speed - v_ego) <= ttc_s:
                other[side] = True
        for side in (1, -1):   # Xe vừa vượt vẫn được tính trong t_offset_hold (SAD 6).
            if other[side]:
                other_until[side] = c.t0_us * 1e-6 + hold_s
            other[side] = c.t0_us * 1e-6 <= other_until[side]
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
                if one_side and other[-near]:
                    out.other_065 = max(out.other_065, abs(offset_away))
                elif one_side:
                    out.away_055 = min(out.away_055, offset_away)
                    out.offset_066 = max(out.offset_066, float(np.max(np.abs(p.d[:n_window]))))
                    if was_abreast is False:
                        out.away_058 = offset_away if out.away_058 is None else min(out.away_058, offset_away)
        was_abreast = abreast if _hwa(c) else None
    if end_us is not None and out.return_059 is None:
        out.return_059 = float("inf")
    return out


@dataclass
class _PathTruth:
    d: np.ndarray
    ay: np.ndarray
    ay_need: np.ndarray
    in_view: np.ndarray
    ay_need_max: float


def _path_truth(c: PlannerCycle, truth: _Truth, road, s_hint: float | None) -> tuple[_PathTruth, float]:
    _, x, y, _, kappa, v, _ = _points(c.trajectory)
    pose = truth.rear_at(c.t0_us)
    d, need = np.zeros(len(x)), np.zeros(len(x))
    hint = road.project(pose[0], pose[1], s_hint).s
    car_s = hint
    # Tầm nhìn tính từ pose lúc camera chụp đến view_range_end theo đường.
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
    """Dương nếu cờ đã bật tại t_event; âm nếu còn phải chờ cờ bật."""
    i = int(np.searchsorted(t_s, t_event_s, side="right")) - 1
    if i >= 0 and flags[i]:
        j = i
        while j > 0 and flags[j - 1]:
            j -= 1
        return float(t_event_s - t_s[j])
    later = np.nonzero(flags[max(i, 0):])[0]
    return -float(t_s[max(i, 0) + later[0]] - t_event_s) if len(later) else -float("inf")


def r79_vehicle(t_s: np.ndarray, a_y: np.ndarray, active: np.ndarray, aysmax: float = AYSMAX) -> dict:
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
    # Gán mỗi cửa sổ lọc cho chu kỳ ở cuối cửa sổ, nơi kiểm HWA có đang lái.
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
    idx = np.searchsorted(cycle_t_s, times_s, side="right") - 1
    return (idx >= 0) & active[np.clip(idx, 0, len(active) - 1)]


def _steering_rate_rms(log: RunLog, cycle_t_s: np.ndarray, hwa: np.ndarray) -> float | None:
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


EGO_LINES = (1, 2)


def lane_usable(c, cal: dict | None = None) -> bool:
    if c.inputs_ok is None or not c.inputs_ok.get("lane_model", True):
        return c.inputs_ok is None
    if c.lane_boundaries is None:
        return True
    cal = cal or {}
    ego, inferred = cal.get("conf_ego", 0.0), cal.get("conf_inferred", 0.0)
    return any(status == LineStatus.MEASURED and conf >= (ego if i in EGO_LINES else inferred)
               for i, (status, conf) in enumerate(c.lane_boundaries))


def boundary_fallback_criteria(log: RunLog, cycles, cal: dict[str, float]) -> list[Criterion]:
    active = {
        "PP-SWR-147": ("Chu kỳ mất path khi còn biên khác đủ tin", []),
        "PP-SWR-047": ("Chu kỳ LKA hoặc ELK được chọn khi chỉ còn biên ngoài", []),
    }
    bad = {rid: [] for rid in active}
    conf_ego = cal.get("conf_ego", 0.0)
    conf_inferred = cal.get("conf_inferred", 0.0)
    conf_edge = cal.get("conf_edge")
    # Mép đo trực tiếp chỉ đủ điều kiện nếu là biên của chính làn ego.
    direct_edge = tuple(edge is not None and abs(edge.offset_m) <= log.road.lane_width / 2 + 1e-6
                        for edge in log.road.layout.edges)
    for c in cycles:
        if c.inputs_ok is None or not c.inputs_ok.get("lane_model") or c.lane_boundaries is None:
            continue
        boundaries = c.lane_boundaries
        if any(boundaries[i][0] == LineStatus.MEASURED and boundaries[i][1] >= conf_ego for i in EGO_LINES):
            continue
        if not any(status == LineStatus.MEASURED and confidence >= conf_inferred
                   for i, (status, confidence) in enumerate(boundaries) if i not in EGO_LINES):
            continue
        if all(c.inputs_ok.get(name, True) for name in INPUTS_FOR_PATH):
            active["PP-SWR-147"][1].append(c)
            if not _some_path_valid(c):
                bad["PP-SWR-147"].append(c)
        status = c.path_status
        if status is None or not status.header.valid:
            continue
        function = status.active_function
        if function == ActiveFunction.ELK and any(direct_edge):
            rx = c.function_requests
            if not _usable_requests(c) or conf_edge is None:
                continue
            req = rx.message.requests[int(ActiveFunction.ELK) - 1]
            if req.elk_reason == ElkReason.ROAD_EDGE and req.side in (Side.LEFT, Side.RIGHT):
                side = 0 if req.side == Side.LEFT else 1
                edge_state, confidence = boundaries[4 + side]
                if direct_edge[side] and edge_state == LineStatus.MEASURED and confidence >= conf_edge:
                    # ICD không cho thấy planner gán một mép đơn dựa trên bề rộng đã nhớ như thế
                    # nào. Mép đối diện đo trực tiếp giúp xác định.
                    other_side = 1 - side
                    other_state, other_confidence = boundaries[4 + other_side]
                    if direct_edge[other_side] and other_state == LineStatus.MEASURED and other_confidence >= conf_edge:
                        active["PP-SWR-047"][1].append(c)
                    continue
        active["PP-SWR-047"][1].append(c)
        if function in INTERVENTION_FUNCTIONS:
            bad["PP-SWR-047"].append(c)
    return [Criterion(rid, metric, float(len(bad[rid])), "= 0", not bad[rid], applicable=bool(judged),
                      first_fail_s=bad[rid][0].t0_us * 1e-6 if bad[rid] else None)
            for rid, (metric, judged) in active.items()]


def over_refusal(cycles, expected_outcome: str | None, init_ok: bool = True, cal: dict | None = None,
                 *, lcc_enabled: bool = True) -> Criterion:
    metric = "Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030"
    if expected_outcome not in ("drive", "drive_limited") or not init_ok or not cycles \
            or any(c.inputs_ok is None for c in cycles):
        return Criterion("PP-SWR-030", metric, float("nan"), "= 0", True, applicable=False)
    started = {ActiveFunction.LKA: False, ActiveFunction.ELK: False}
    priority = FUNCTION_PRIORITY if lcc_enabled else INTERVENTION_FUNCTIONS[::-1]
    grace_us = round(RECOVERY_GRACE_S * 1e6)
    last_bad_us, previous, wrong, judged, first = None, None, 0, 0, None
    for c in cycles:
        now_s = c.t0_us * 1e-6
        if not (all(c.inputs_ok.get(k, True) for k in INPUTS_FOR_PATH) and lane_usable(c, cal)):
            last_bad_us = c.t0_us
            started = {f: False for f in started}
        message = c.function_requests.message if c.inputs_ok["function_requests"] else None
        requested = [f for f in priority
                     if message is not None and message.requests[int(f) - 1].state == RequestState.REQUEST]
        for f in started:
            if f not in requested or _phase(c, f) == InterventionPhase.COMPLETED:
                started[f] = False
        status = c.path_status
        actual = status.active_function if _valid(c) else ActiveFunction.NONE
        candidates = [f for f in requested if f == ActiveFunction.LCC or started[f]]
        expected = candidates[0] if candidates else ActiveFunction.NONE
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


LANE_INVALID_AGE_US = 250_000
LANE_KEEP_AGE_US = 170_000
T_COAST_MAX_US = 1_000_000


def _usable_requests(c) -> bool:
    rx = c.function_requests
    return (rx is not None and rx.message.header.valid
            and 0 <= c.t0_us - rx.rx_us <= FUNCTION_REQUESTS_TIMEOUT_US
            and -FUTURE_STAMP_TOLERANCE_US <= c.t0_us - rx.message.header.stamp_us
            <= FUNCTION_REQUESTS_MAX_AGE_US)


def _input_age_criteria(cycles, hwa_request_s) -> list:
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
    checks = []
    previous = None
    for c in cycles:
        if not _usable_requests(c):
            continue
        rx = c.function_requests
        if previous is not None and rx.rx_us != previous.rx_us:
            for function in (ActiveFunction.LCC, ActiveFunction.LKA, ActiveFunction.ELK):
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
            continue
        active = c.path_status.active_function
        if not entering:
            n += 1
            ok += active != function
        elif (function == ActiveFunction.LCC and not requests.driver_override and c.path_status.path_valid
              and not c.path_status.lane_too_narrow
              and all(requests.requests[int(f) - 1].state != RequestState.REQUEST
                      for f in (ActiveFunction.LKA, ActiveFunction.ELK))):
            n += 1
            ok += active == function
    share = ok / n if n else 1.0
    return [Criterion("PP-SWR-038", "Tỉ lệ thay đổi FunctionRequests thể hiện ở output trong một chu kỳ",
                      share, "= 1", share == 1.0, applicable=n > 0)]


def _yaw_delay_criterion(scenario, criteria) -> list:
    if not 0.0 < scenario.yaw_filter_delay_ms <= 50.0:
        return []
    parts = [c for c in criteria if c.id in ("PP-SWR-051", "PP-SWR-100", "PP-SWR-101", "PP-SWR-102")
             and c.applicable]
    ok = all(c.passed for c in parts)
    return [Criterion("PP-SWR-138", "PP-SWR-051 và 100 đến 102 đạt khi yaw rate trễ không báo",
                      float(ok), "= 1", ok, applicable=bool(parts))]


def _stale_requests(cycles) -> bool:
    """FunctionRequests quá tuổi là đầu vào không dùng được theo ICD. Tách trường hợp lỗi này khỏi
    điều kiện yêu cầu can thiệp.
    """
    for c in cycles:
        rx = c.function_requests
        if (rx is not None and rx.message.header.valid
                and c.t0_us - rx.message.header.stamp_us > FUNCTION_REQUESTS_MAX_AGE_US):
            return True
    return False


def _requests_timeout_share(cycles) -> tuple[float, bool]:
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
            last = c.t0_us
        if c.t0_us - last > FUNCTION_REQUESTS_TIMEOUT_US + _PLANNER_CYCLE_US:
            checked += 1
            s = c.path_status
            ok += s is not None and s.active_function == ActiveFunction.NONE and not s.path_valid
    return (ok / checked if checked else 1.0), checked > 0


LANE_MAX_AGE_US = 250_000
# Open loop điều khiển xe theo chuyển động định sẵn, nên bỏ các tiêu chí đo phản ứng của xe.
VEHICLE_CRITERIA = {"PP-SWR-007", "PP-SWR-051", "PP-SWR-060", "PP-SWR-084", "PP-SWR-085", "PP-SWR-086",
                    "PP-SWR-088", "PP-SWR-091", "PP-SWR-122", "PP-SWR-123", "PP-SWR-148"}


def _after_first(flags: list[bool]) -> list[bool]:
    """Chỉ tính sự kiện mất đầu vào sau ít nhất một lần đầu vào dùng được."""
    out, seen = [], False
    for bad in flags:
        seen |= not bad
        out.append(bad and seen)
    return out


def _reaction(cycles, condition, requirement, metric, need_none=False) -> Criterion:
    """Cho phép một chu kỳ phản ứng; từ chu kỳ thứ hai, path phải mất hiệu lực và active_function
    là NONE.
    """
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


def _following(c) -> bool:
    return c.lcc_status is not None and c.lcc_status.lcc_mode == LccMode.FOLLOW


def lane_loss_criteria(cycles, t_coast_s: float, cal: dict | None = None) -> list[Criterion]:
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
        anchor_us = cycles[start].t0_us  # Tính T_coast từ lúc mất đầu vào hoặc chu kỳ FOLLOW cuối (PP-SWR-173).
        while i < len(cycles) and usable_once[i]:
            if i > start and _following(cycles[i - 1]):
                anchor_us = cycles[i].t0_us
            dt = cycles[i].t0_us - anchor_us
            valid = _valid(cycles[i])
            wrong = ((coasting and not valid and dt < coast_us - tol_us)
                     or (valid and dt > coast_us + tol_us and not _following(cycles[i])))
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


def _some_path_valid(c: PlannerCycle) -> bool:
    lcc = c.lcc_trajectory is not None and c.lcc_status is not None and c.lcc_trajectory.header.valid \
        and c.lcc_status.path_valid
    return bool(_valid(c) or lcc or (c.intervention_status is not None and c.intervention_status.path_valid))


def _same_planner_pair(prev: PlannerCycle, cur: PlannerCycle) -> bool:
    return (prev.path_status is not None and cur.path_status is not None
            and prev.path_status.chosen == cur.path_status.chosen)


def _lcc_holds_at_car(c: PlannerCycle) -> bool:
    return (c.path_status is not None and c.path_status.chosen == PlannerId.LCC
            and any(_state(c, f) == RequestState.REQUEST for f in INTERVENTION_FUNCTIONS))


def _overriding(cycles) -> set[int]:
    out, now = set(), False
    for i, c in enumerate(cycles):
        if (c.inputs_ok or {}).get("function_requests") and c.function_requests is not None:
            now = bool(c.function_requests.message.driver_override)
        if now:
            out.add(i)
    return out


def _entry_errors(cycle, t_us, truth):
    if not _finite_outputs(cycle):
        return np.inf, np.inf
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


def _dlc_reversal(truth, start_us, stop_us, side, *, edge=False) -> float:
    road = truth.log.road
    lo, hi = truth.index(start_us), truth.index(stop_us)
    hint, series = None, []
    for x, y, _ in truth.front[lo:hi + 1]:
        p = road.project(x, y, hint)
        hint = p.s
        series.append(_dlc(truth.log, p, side, edge=edge))
    if not series:
        return 0.0
    k = int(np.argmin(series))
    best, worst = -np.inf, 0.0
    for value in series[k:]:
        best = max(best, value)
        worst = max(worst, best - value)
    return float(worst)


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
            or abs(pr.d) > cal["d_end"]
            or abs(truth.lateral_velocity(i, pf.heading, front=True)) > cal["v_lat_end"]
            or abs(_wrap(rear[2] - pr.heading)) > cal["heading_end"]):
        return False
    return _valid(prev) and abs(_path_at(prev, cur.t0_us, truth)[2]) <= cal["ay_add_end"]


def _target_geometry(truth, episodes):
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
            abreast = (target_active[i] and target.s + half_l >= p.s - widths[1]
                       and target.s - half_l <= p.s + widths[1])
            if abreast:
                span = half_w * abs(nx * ty - ny * tx) + half_l * abs(nx * tx + ny * ty)
                min_gap = min(min_gap, abs(nx * dx + ny * dy) - ego_span - span)
            if contact or hypot(dx, dy) > hypot(*widths) + hypot(half_l, half_w):
                continue
            # Kiểm va chạm bằng trục phân cách của hai hình chữ nhật.
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
    late_us = round(END_LATE_S * 1e6)
    completion_late = bool(reached and (not episode.completed
                                        or cycles[episode.stop].t0_us - cycles[reached[0]].t0_us > late_us))
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


PLAN_STEP_S = 0.1
FLOAT32_TOL = 1e-3
CURRENT_SPEED_TOL_MPS = 0.2


END_LATE_S = 0.5
SWITCH_WINDOW_S = 0.5
OVERRIDE_START_M = 0.05
HWA_LOW_SPEED_MPS = 60 / 3.6
LANE_CHANGE_WINDOW_S = 1.0


def _state(c, function):
    if not (c.inputs_ok or {}).get("function_requests") or c.function_requests is None:
        return None
    return c.function_requests.message.requests[int(function) - 1].state


def _inputs_ok(c, cal) -> bool:
    return all((c.inputs_ok or {}).get(k, True) for k in INPUTS_FOR_PATH) and lane_usable(c, cal)


def switch_criteria(log: RunLog, cycles, cal: dict | None = None) -> list[Criterion]:
    truth = _Truth(log)
    t = np.asarray(log.t_us)
    window_us = round(SWITCH_WINDOW_S * 1e6)
    bad = {k: 0 for k in ("034", "036", "037", "041", "042", "054")}
    seen = {k: 0 for k in bad}
    starts_039, starts_040 = [], []
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
    windows = []
    for prev, c in zip(cycles, cycles[1:]):
        for f in INTERVENTION_FUNCTIONS:
            if (_phase(prev, f) == InterventionPhase.ACTIVE and _state(prev, f) == RequestState.REQUEST
                    and _state(c, f) not in (None, RequestState.REQUEST)):
                windows.append((c.t0_us, "036"))
        if _state(prev, ActiveFunction.LCC) == RequestState.REQUEST and \
                _state(c, ActiveFunction.LCC) not in (None, RequestState.REQUEST):
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
            if kind == "036":
                ka = c.intervention_status
                actual = ActiveFunction.NONE if ka is None or ka.active_function == InterventionFunction.NONE \
                    else ActiveFunction[ka.active_function.name]
                eligible = [f for f in (ActiveFunction.ELK, ActiveFunction.LKA)
                            if f in requested and _phase(c, f) != InterventionPhase.COMPLETED]
                expected = eligible[0] if eligible else ActiveFunction.NONE
                seen["036"] += 1
                bad["036"] += actual != expected
                if not eligible:
                    seen["037"] += 1
                    bad["037"] += not (ka is not None and ka.path_valid
                                       and ka.active_function == InterventionFunction.NONE)
            elif not requested:
                seen["042"] += 1
                lcc = c.lcc_status
                bad["042"] += not (lcc is not None and lcc.path_valid and lcc.lcc_mode == LccMode.NONE)
    # PP-SWR-039 và 040 chấm path riêng của LCC, bất kể arbitrator chọn path nào.
    was_hold = False
    for c in cycles:
        usable = (c.inputs_ok or {}).get("function_requests") and c.function_requests is not None
        override = bool(usable and c.function_requests.message.driver_override)
        hold = override or any(_state(c, f) == RequestState.REQUEST for f in INTERVENTION_FUNCTIONS)
        lcc_ok = (c.lcc_trajectory is not None and c.lcc_status is not None and c.lcc_trajectory.header.valid
                  and c.lcc_status.path_valid)
        if lcc_ok:
            y0 = abs(c.lcc_trajectory.points[0].pose.y)
            if hold:
                starts_039.append(y0)
            elif was_hold and _state(c, ActiveFunction.LCC) == RequestState.REQUEST:
                starts_040.append(y0)
        if usable:
            was_hold = hold
    for c in cycles:
        if _state(c, ActiveFunction.LCC) != RequestState.REQUEST or not _inputs_ok(c, cal):
            continue
        speed = log.speed[int(np.clip(np.searchsorted(t, c.t0_us), 0, len(t) - 1))]
        if 0.0 <= speed <= HWA_LOW_SPEED_MPS:
            seen["054"] += 1
            bad["054"] += not _hwa(c)
    lane_changes = [stamp for stamp, _ in getattr(log, "lane_index_changes", [])]
    cont = [0.0, 0.0, 0.0]
    n_061 = 0
    override_cycles = _overriding(cycles)
    for i, (prev, c) in enumerate(zip(cycles, cycles[1:]), start=1):
        if not (_valid(prev) and _valid(c)) or c.path_status.active_function != prev.path_status.active_function:
            continue
        if i in override_cycles:
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
        Criterion("PP-SWR-039", "Lệch ngang điểm đầu path LCC so với xe khi driver_override hoặc LKA, ELK ở REQUEST [m]",
                  float(max(starts_039, default=float("nan"))), f"<= {OVERRIDE_START_M}",
                  max(starts_039, default=0.0) <= OVERRIDE_START_M, applicable=bool(starts_039)),
        Criterion("PP-SWR-040", "Lệch ngang điểm đầu path LCC khi hết driver_override hoặc LKA, ELK rời REQUEST [m]",
                  float(max(starts_040, default=float("nan"))), f"<= {OVERRIDE_START_M}",
                  max(starts_040, default=0.0) <= OVERRIDE_START_M, applicable=bool(starts_040)),
        Criterion("PP-SWR-061", "Lệch ngang giữa hai path liên tiếp khi lane model sang làn mới / ngưỡng của khoảng",
                  cont[0], "<= 1", cont[0] <= 1.0, applicable=n_061 > 0),
        Criterion("PP-SWR-061", "Lệch hướng giữa hai path liên tiếp khi lane model sang làn mới / ngưỡng của khoảng",
                  cont[1], "<= 1", cont[1] <= 1.0, applicable=n_061 > 0),
        Criterion("PP-SWR-061", "Lệch độ cong giữa hai path liên tiếp khi lane model sang làn mới / ngưỡng của khoảng",
                  cont[2], "<= 1", cont[2] <= 1.0, applicable=n_061 > 0),
    ]


def planner_criteria(cycles, cal: dict | None = None) -> list[Criterion]:
    id_bad = id_seen = mode_bad = mode_seen = valid_bad = valid_seen = 0
    for c in cycles:
        for traj, expected in ((c.lcc_trajectory, PlannerId.LCC), (c.ka_trajectory, PlannerId.LKA_ELK)):
            if traj is not None:
                id_seen += 1
                id_bad += traj.planner_id != expected
        if (c.lcc_status is not None and _state(c, ActiveFunction.LCC) == RequestState.REQUEST
                and c.lcc_status.path_valid and _inputs_ok(c, cal)):
            mode_seen += 1
            mode_bad += c.lcc_status.lcc_mode == LccMode.NONE
        if c.intervention_status is not None and c.ka_trajectory is not None:
            if c.intervention_status.active_function == InterventionFunction.NONE:
                valid_seen += 1
                valid_bad += bool(c.ka_trajectory.header.valid)
    return [
        Criterion("PP-SWR-019", "Chu kỳ có planner_id khác planner đã gửi", float(id_bad), "= 0", id_bad == 0,
                  applicable=id_seen > 0),
        Criterion("PP-SWR-067", "Chu kỳ LCC ở REQUEST, path_valid mà lcc_mode = NONE", float(mode_bad), "= 0",
                  mode_bad == 0, applicable=mode_seen > 0),
        Criterion("PP-SWR-180", "Chu kỳ LKA/ELK planner báo NONE mà Trajectory hợp lệ", float(valid_bad), "= 0",
                  valid_bad == 0, applicable=valid_seen > 0),
    ]


FOLLOW_SPEED_MAX_MPS = 60 / 3.6
FOLLOW_WHEEL_MAX_RAD = np.radians(20.0)
FOLLOW_DISTANCE_MAX_M = 30.0
FOLLOW_PATH_DEV_M = 0.8
FOLLOW_GAP_M = (2.0, 50.0)
_FOLLOW_KINDS = ("CAR", "TRUCK")


def _follow_coast(log, truth, cycles, following, cal) -> Criterion:
    coast_us = round(cal.get("T_coast", 1.0) * 1e6)
    start = first = None
    tested = False
    bad = 0
    distance = last_step = 0.0
    distance_case = log.scenario.name.startswith(("S22b", "S22-b-"))
    for i, c in enumerate(cycles):
        if following[i]:
            start = None
            last_step = log.speed[truth.index(c.t0_us)] * PLANNER_PERIOD_US * 1e-6
            distance += last_step
            continue
        if lane_usable(c, cal):
            start, distance = None, 0.0
            continue
        if i > 0 and following[i - 1]:
            if not distance_case or distance + last_step >= FOLLOW_DISTANCE_MAX_M:
                start = c.t0_us
            distance = 0.0
        if start is None:
            continue
        elapsed = c.t0_us - start
        tested |= elapsed > coast_us + PLANNER_PERIOD_US
        valid = c.lcc_status.path_valid
        wrong = ((not valid and elapsed < coast_us - PLANNER_PERIOD_US)
                 or (valid and elapsed > coast_us + PLANNER_PERIOD_US))
        if wrong:
            bad += 1
            if first is None:
                first = c.t0_us * 1e-6
    return Criterion("PP-SWR-173", "Chu kỳ path_valid sai thời hạn T_coast sau FOLLOW", float(bad),
                     "= 0", bad == 0, applicable=tested or bad > 0, first_fail_s=first)


def _follow_path_criteria(log, truth, cycles, following, cal) -> list[Criterion]:
    ay, jerk, continuity = 0.0, 0.0, 0.0
    dlc = np.inf
    missing = n_paths = n_pairs = 0
    previous = None
    overrides = _overriding(cycles)
    truth_times = truth.t
    for i, c in enumerate(cycles):
        if not following[i]:
            previous = None
            continue
        traj = c.lcc_trajectory
        if not (c.lcc_status.path_valid and traj is not None and traj.header.valid and _nonfinite(traj, "") is None):
            missing += 1
            previous = None
            continue
        cur = replace(c, trajectory=traj)
        path, _ = _path_truth(cur, truth, log.road, None)
        n_paths += 1
        ay = max(ay, float(np.max(np.abs(path.ay))))
        jerk = max(jerk, _jerk_max(path.ay))
        if i not in overrides and not any(_state(c, f) == RequestState.REQUEST for f in INTERVENTION_FUNCTIONS):
            if previous is not None:
                continuity = max(continuity, *_continuity(previous, cur, truth))
                n_pairs += 1
        previous = cur
        free_space = (log.road.lane_width - log.vehicle_width) * 0.5
        if i in overrides or np.max(np.abs(path.ay_need)) > AYSMAX or free_space < cal.get("free_space_min", 0.0):
            continue
        if c.path_status is None or c.path_status.active_function != ActiveFunction.LCC:
            continue
        start = int(np.searchsorted(truth_times, c.t0_us))
        end = int(np.searchsorted(truth_times, cycles[i + 1].t0_us)) if i + 1 < len(cycles) else len(truth_times)
        for front in truth.front[start:end]:
            projection = log.road.project(front[0], front[1])
            dlc = min(dlc, _dlc(log, projection, Side.LEFT), _dlc(log, projection, Side.RIGHT))
    rid = "PP-SWR-175"
    return [
        Criterion(rid, "Chu kỳ FOLLOW thiếu path LCC hợp lệ", float(missing), "= 0", missing == 0,
                  applicable=any(following)),
        Criterion(rid, "Gia tốc ngang lớn nhất của path FOLLOW [m/s²]", ay, f"<= {AYSMAX}",
                  ay <= AYSMAX, applicable=n_paths > 0),
        Criterion(rid, "Jerk ngang lớn nhất của path FOLLOW [m/s³]", jerk, f"<= {JERK_MAX_HWA}",
                  jerk <= JERK_MAX_HWA, applicable=n_paths > 0),
        Criterion(rid, "DLC nhỏ nhất khi xe chạy theo path FOLLOW [m]", float(dlc), ">= 0", dlc >= 0,
                  applicable=isfinite(dlc) and log.scenario.loop == "closed"),
        Criterion(rid, "Sai khác lớn nhất giữa hai path FOLLOW, chia cho giới hạn", continuity, "<= 1",
                  continuity <= 1.0, applicable=n_pairs > 0),
    ]


def follow_criteria(log: RunLog, cycles, cal: dict | None = None) -> list[Criterion]:
    """Chấm điều kiện vào và duy trì FOLLOW trên ground truth, LeadTarget và LongitudinalPlan mà
    planner nhận.
    """
    cal = cal or {}
    if not cycles or any(c.lcc_status is None for c in cycles):
        return []
    truth = _Truth(log)
    traffic = Traffic(log.road, tuple(log.scenario.traffic)) if log.scenario.traffic else None
    lat_max, vlat_max = cal.get("follow_lat_max", 1.0), cal.get("follow_vlat_max", 0.6)
    conf_ego = cal.get("conf_ego", 0.0)
    n = len(cycles)
    mode = [c.lcc_status.lcc_mode for c in cycles]
    following = [m == LccMode.FOLLOW for m in mode]
    entry, entry_loose, keep_ok = [False] * n, [False] * n, [True] * n
    # M1 bên trong planner không quan sát được đầy đủ; dùng offset LeadTarget với biên rõ để tránh
    # chấm nhầm ca sát ngưỡng.
    free = 0.5 * (log.road.lane_width - log.vehicle_width) - cal.get("dlc_offset_min", 0.3)
    m1_limit = min(FOLLOW_PATH_DEV_M, free)
    lines_back = [False] * n
    entry_id, driven = None, 0.0
    for i, c in enumerate(cycles):
        if c.lane_boundaries is None or c.inputs_ok is None:
            continue
        both = all(c.lane_boundaries[k][0] == LineStatus.MEASURED and c.lane_boundaries[k][1] >= conf_ego for k in EGO_LINES)
        lines_back[i] = both and c.inputs_ok.get("lane_model", True)
        lost = not lane_usable(c, cal)
        k = truth.index(c.t0_us)
        speed = log.speed[k]
        wheel = abs(log.wheel_angle[k] * log.steering_ratio)
        msg = c.lead_target.message if c.lead_target is not None else None
        usable = bool((c.inputs_ok or {}).get("lead_target")) and msg is not None
        plan = c.longitudinal_plan.message if c.longitudinal_plan is not None else None
        m_ok = speed < FOLLOW_SPEED_MAX_MPS and wheel < FOLLOW_WHEEL_MAX_RAD
        if following[i]:
            driven += speed * PLANNER_PERIOD_US * 1e-6
            if entry_id is not None and usable:
                m_ok = m_ok and msg.id == entry_id and msg.classification.name in _FOLLOW_KINDS
            keep_ok[i] = m_ok and driven < FOLLOW_DISTANCE_MAX_M and (usable or i == 0 or not following[i - 1])
            entry_id = entry_id if entry_id is not None else (msg.id if usable else None)
        else:
            driven, entry_id = 0.0, None
        if not (lost and _state(c, ActiveFunction.LCC) == RequestState.REQUEST and usable and m_ok
                and plan is not None and msg.id == plan.target_id and msg.classification.name in _FOLLOW_KINDS):
            continue
        lead = None
        if traffic is not None and plan.target_id:
            lead = next((v for v in traffic.at(c.t0_us * 1e-6) if v.id == plan.target_id), None)
        if lead is None or lead.kind not in _FOLLOW_KINDS:
            continue
        front, rear = truth.front[k], truth.rear[k]
        pf = log.road.project(front[0], front[1])
        pr = log.road.project(rear[0], rear[1], pf.s)
        after = traffic.at(c.t0_us * 1e-6 + 0.1)
        ahead = next((v for v in after if v.id == lead.id), lead)
        gap = lead.s - 0.5 * lead.length - (pf.s + BODY_OVERHANG_M)
        conditions = (FOLLOW_GAP_M[0] <= gap <= FOLLOW_GAP_M[1] and abs(lead.d - pr.d) < lat_max
                      and abs(ahead.d - lead.d) / 0.1 < vlat_max)
        entry[i] = bool(conditions and abs(lead.d) < 0.8 * m1_limit)
        entry_loose[i] = bool(conditions and abs(lead.d) < 1.25 * m1_limit)
    # PP-SWR-170 yêu cầu vào FOLLOW trong một chu kỳ. Không suy ngược điều kiện nội bộ M1 và M2 từ
    # chu kỳ đã rời FOLLOW.
    late = sum(1 for i in range(1, n - 1) if entry[i] and not entry[i - 1] and not any(following[i:i + 2]))
    held = sum(entry)
    wrong_entry = sum(1 for i in range(1, n) if following[i] and not following[i - 1] and not entry_loose[i]
                      and (cycles[i].inputs_ok or {}).get("lane_model", True) is not None
                      and cycles[i].lane_boundaries is not None)
    stay = sum(1 for i in range(2, n) if following[i] and following[i - 1] and not keep_ok[i] and not keep_ok[i - 1])
    back = sum(1 for i in range(2, n) if following[i] and lines_back[i] and lines_back[i - 1] and lines_back[i - 2])
    unusable = [not (c.inputs_ok or {}).get("lead_target", True) for c in cycles]
    leave_176 = sum(1 for i in range(n) if following[i] and unusable[i]
                    and (i == 0 or not following[i - 1] or unusable[i - 1]))
    judged_176 = any(bad and (following[i] or i > 0 and following[i - 1]) for i, bad in enumerate(unusable))
    wrong_mode = 0
    for i, c in enumerate(cycles):
        if c.lane_boundaries is None or c.inputs_ok is None or mode[i] == LccMode.NONE:
            continue
        ego = [c.lane_boundaries[k][0] == LineStatus.MEASURED and c.lane_boundaries[k][1] >= conf_ego for k in EGO_LINES]
        usable_lane = lane_usable(c, cal)
        wrong_mode += ((mode[i] == LccMode.LANE and not any(ego))
                       or (mode[i] == LccMode.INFERRED and (any(ego) or not usable_lane))
                       or (mode[i] in (LccMode.FOLLOW, LccMode.COAST) and usable_lane))
    judged_modes = any(m != LccMode.NONE for m in mode)
    any_follow = any(following)
    return [
        Criterion("PP-SWR-170", "Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW", float(late), "= 0", late == 0, applicable=held >= 3),
        Criterion("PP-SWR-171", "Lần vào FOLLOW khi điều kiện vào không thoả", float(wrong_entry), "= 0", wrong_entry == 0,
                  applicable=any_follow or any(not e for e in entry) and any(c.lane_boundaries is not None and not lane_usable(c, cal) for c in cycles)),
        Criterion("PP-SWR-172", "Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả", float(stay), "= 0", stay == 0, applicable=any_follow),
        _follow_coast(log, truth, cycles, following, cal),
        Criterion("PP-SWR-174", "Chu kỳ còn FOLLOW khi hai vạch làn mình đủ tin trở lại", float(back), "= 0", back == 0, applicable=any_follow),
        Criterion("PP-SWR-176", "Chu kỳ vào hoặc còn FOLLOW khi LeadTarget không hợp lệ", float(leave_176), "= 0",
                  leave_176 == 0, applicable=judged_176),
        Criterion("PP-SWR-177", "Chu kỳ lcc_mode không khớp trạng thái lane model", float(wrong_mode), "= 0", wrong_mode == 0, applicable=judged_modes),
        *(_follow_path_criteria(log, truth, cycles, following, cal) if any_follow else []),
    ]


def longitudinal_criteria(log: RunLog, cycles) -> list[Criterion]:
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
    """Lấy các đợt REQUEST do stand-in phát, theo mode đo hoặc mode lý tưởng đang dùng để cấp đầu
    vào.
    """
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


def _side_line_trusted(c, side, cal) -> bool:
    if c.inputs_ok is not None and not c.inputs_ok.get("lane_model", True):
        return False
    if c.lane_boundaries is None:
        return True
    status, confidence = c.lane_boundaries[EGO_LINES[0] if side == Side.LEFT else EGO_LINES[1]]
    return status == LineStatus.MEASURED and confidence >= cal.get("conf_ego", 0.0)


def _line_request(function, r) -> bool:
    return function == ActiveFunction.LKA or r.message.elk_reason != ElkReason.ROAD_EDGE


def _refused_unseen_line(cycles, function, r, cal) -> bool:
    return (_line_request(function, r) and r.message.side in (Side.LEFT, Side.RIGHT)
            and not any(_side_line_trusted(cycles[i], r.message.side, cal) for i in range(r.start, r.stop)))


def _unseen_line_criterion(cycles, episodes, requests, cal) -> Criterion:
    judged = any(_line_request(f, r) and r.message.side in (Side.LEFT, Side.RIGHT)
                 and not all(_side_line_trusted(cycles[i], r.message.side, cal) for i in range(r.start, r.stop))
                 for f in INTERVENTION_FUNCTIONS for r in requests[f])
    bad = [e for e in episodes if e.request is not None and _line_request(e.function, e.request)
           and e.request.message.side in (Side.LEFT, Side.RIGHT)
           and not _side_line_trusted(cycles[e.start], e.request.message.side, cal)]
    return Criterion("PP-SWR-092", "Lần LKA, ELK vạch bắt đầu khi vạch phía side không đủ tin",
                     float(len(bad)), "= 0", not bad, applicable=judged,
                     first_fail_s=cycles[bad[0].start].t0_us * 1e-6 if bad else None)


def _score_interventions(result, truth, paths, episodes, requests, cal, cycle_times):
    log, cycles = truth.log, truth.log.cycles
    expected = log.scenario.notes.get("expect_intervention")
    if expected == "none":
        # Nếu stand-in gửi yêu cầu dù điều kiện ADAS không cho phép, đó là lỗi phía thử. Hệ quả
        # không được tính thành lỗi planner.
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
        if not expected_requests and not _stale_requests(cycles):
            side = "" if desired is None else f" (phía {'trái' if desired == 'left' else 'phải'})"
            issue(ISSUE_NOT_JUDGED, f"{expected}: thiếu REQUEST đến planner{side}")
        elif (any(not any(e.request is r and e.function == function for e in episodes)
                  and not _refused_unseen_line(cycles, function, r, cal)
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
    start_kappa = []
    opposite_dlcs, completed_dlcs, completed_offsets, reversals = [], [], [], []
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
        if _finite_outputs(cycles[episode.start]):
            i_t = truth.index(start_us)
            car_kappa = truth.log.yaw_rate[i_t] / max(truth.log.speed[i_t], 1.0)
            start_kappa.append(abs(float(_points(cycles[episode.start].trajectory)[4][0]) - car_kappa))
        elapsed_s = (stop_us - episode.request.rx_us) * 1e-6
        handover_us = _handover_end_us(truth, stop_us, next_us)
        opposite_dlcs.append(_min_dlc(truth, start_us, handover_us, _opposite(req.side)))
        dtle = _min_dlc(truth, start_us, stop_us, req.side, edge=edge)
        reversals.append(_dlc_reversal(truth, start_us, stop_us, req.side, edge=edge))
        if lka:
            dtle_lka.append(dtle)
        if edge:
            dtle_edge.append(dtle)
        elif lka or req.elk_reason == ElkReason.SOLID_LINE:
            dtle_mark.append(dtle)
        if episode.completed:
            n_completed += 1
            times_to_complete[function].append((stop_us - start_us) * 1e-6)
            front = truth.front_at(stop_us)
            projected = log.road.project(front[0], front[1])
            completed_dlcs.append(_dlc(log, projected, req.side))
            completed_dlcs.append(_dlc(log, projected, _opposite(req.side)))
            completed_offsets.append(abs(log.road.project(*truth.rear_at(stop_us)[:2]).d))
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
    upper("PP-SWR-049", "Lệch độ cong điểm đầu so với xe khi LKA, ELK bắt đầu [1/m]", start_kappa, ENTRY_KAPPA)
    upper("PP-SWR-032", "Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện", [late_completion] if end_judged else [], 0)
    upper("PP-SWR-090", "Lần báo COMPLETED khi chưa đủ điều kiện", [early_completion] if n_completed else [], 0)
    lower("PP-SWR-084", "DLC nhỏ nhất ở hai phía khi LKA hoặc ELK COMPLETED [m]", completed_dlcs, 0)
    upper("PP-SWR-084", "Lệch tâm khi LKA hoặc ELK COMPLETED [m]", completed_offsets, 2 * cal["d_end"])
    lower("PP-SWR-085", "DLC phía đối diện qua bàn giao EPS [m]", opposite_dlcs, 0)
    upper("PP-SWR-094", "DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m]", reversals, DLC_REVERSAL_MAX_M)
    lower("PP-SWR-086", "DTLE vạch nhỏ nhất [m]", dtle_mark, MARK_DTLE_MIN_M)
    lower("PP-SWR-086", "DTLE mép đường nhỏ nhất [m]", dtle_edge, EDGE_DTLE_MIN_M)
    eps_delay = getattr(log.scenario, "eps_delay_s", None)
    if eps_delay is not None and log.actuator_delay_s + 1e-9 < eps_delay <= EPS_DELAY_MAX_S + 1e-9:
        lower("PP-SWR-091", "DTLE vạch khi EPS chậm tới 100 ms [m]", dtle_mark, MARK_DTLE_MIN_M)
        lower("PP-SWR-091", "DTLE mép khi EPS chậm tới 100 ms [m]", dtle_edge, EDGE_DTLE_MIN_M)
    upper("PP-SWR-089", "Số ELK REQUEST muộn đã khởi động", [accepted] if late_dlcs else [], 0)
    result.criteria.append(_unseen_line_criterion(cycles, episodes, requests, cal))
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
        active_paths = [p for p, use in zip(paths, active) if use and p is not None]
        ay_limit, added_limit, jerk_limit = INTERVENTION_LIMITS[function]
        later = [e for e in episodes if e.function == function][1:]
        if later:
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
    """Đổi gốc ngang sang tâm làn xe đang ở theo mốc camera đổi ID vạch (S17)."""

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


def _score_fault_exposure(result: Result, log: RunLog) -> None:
    names = [log.scenario.name, *log.scenario.notes.get("faults", [])]
    cycles = log.cycles
    if any(name.startswith("F24") for name in names):
        stamps = set(log.fault_frames.get("lane_model", []))
        exposure = next((c.t0_us for prev, c in zip(cycles, cycles[1:])
                         if (c.input_times or {}).get("lane_model", (None,))[0] in stamps
                         and prev.path_status is not None
                         and prev.path_status.active_function in INTERVENTION_FUNCTIONS), None)
        checks = [c for c in result.criteria if c.applicable and c.id in ("PP-SWR-085", "PP-SWR-086")]
        judged = exposure is not None and len({c.id for c in checks}) == 2 and log.scenario.loop == "closed"
        result.info["fault_exposure_s"] = None if exposure is None else exposure * 1e-6
        if not judged:
            add_issue(result, ISSUE_NOT_JUDGED, "F24: thiếu frame biên bị đổi trong lúc can thiệp hoặc thiếu đo DLC/DTLE")
        else:
            failed = sum(not c.passed for c in checks)
            result.criteria.append(Criterion("PP-SWR-093", "Tiêu chí DLC và DTLE trượt sau khi nhận lỗi F24",
                                              float(failed), "= 0", failed == 0))
    if any(name.startswith("F25") for name in names):
        start = log.fault_events.get("lcc_follow")
        stamps = set(log.fault_frames.get("lead_target", []))
        loss = any(f.channel == "lead_target" and f.kind in ("drop", "stop") for f in log.scenario.channel_faults)
        previous_stamp = exposure = None
        for c in cycles:
            if start is None or c.t0_us <= start or c.lead_target is None:
                continue
            stamp = c.lead_target.message.header.stamp_us
            if stamp in stamps or (loss and previous_stamp is not None
                                   and any(previous_stamp < s < stamp for s in stamps)):
                exposure = c.t0_us
                break
            if loss and stamps and (c.inputs_ok or {}).get("lead_target") is False and stamp < min(stamps):
                exposure = c.t0_us
                break
            previous_stamp = stamp
        result.info["fault_exposure_s"] = None if exposure is None else exposure * 1e-6
        if exposure is None:
            add_issue(result, ISSUE_NOT_JUDGED, "F25: chưa xác nhận lỗi LeadTarget tới planner sau khi vào FOLLOW")


def score_standalone(result: Result, scope: set[str]) -> None:
    failed = {c.id for c in result.criteria if c.id in scope and c.applicable and not c.passed}
    failed.update(i["requirement"] for i in result.issues
                  if i["kind"] == ISSUE_REQUIREMENT and i["requirement"] in scope)
    observed = {c.id for c in result.criteria if c.applicable}
    required = {"PP-SWR-039", "PP-SWR-040"} if result.info["planner_only"] == "lcc" else {"PP-SWR-030", "PP-SWR-180"}
    judged = required <= observed and not any(i["kind"] == ISSUE_NOT_JUDGED for i in result.issues)
    if not judged and not failed:
        add_issue(result, ISSUE_NOT_JUDGED, "PP-SWR-181: thiếu điều kiện để chấm planner chạy độc lập")
    result.criteria.append(Criterion("PP-SWR-181", "Yêu cầu trượt khi chỉ chạy một planner", float(len(failed)),
                                      "= 0", not failed, applicable=judged or bool(failed)))


def evaluate(log: RunLog, calibration: dict[str, float] | None = None) -> Result:
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

    finite = np.array([_finite_outputs(c) for c in cycles])

    paths: list[_PathTruth | None] = []
    s_hint = None
    for c, ok, good in zip(cycles, valid, finite):
        if ok and good:
            p, s_hint = _path_truth(c, truth, road, s_hint)
            paths.append(p)
        else:
            # Sau khoảng không chấm, xe có thể đã đi quá cửa sổ tìm của gợi ý cũ (PP-PR-080).
            s_hint = None
            paths.append(None)
    need_max = np.array([p.ay_need_max if p is not None else 0.0 for p in paths])

    lcc_enabled = log.planner_only != "lkaelk"
    intervention_enabled = log.planner_only != "lcc"
    missing_outputs = [c for c in cycles
                       if (lcc_enabled and (c.lcc_trajectory is None or c.lcc_status is None))
                       or (intervention_enabled and (c.ka_trajectory is None or c.intervention_status is None))]
    sent_every_cycle = not missing_outputs
    limits_every_cycle = all(c.lateral_limits is not None for c in cycles)
    flag_status = np.array([bool(c.path_status.lateral_limit_reached) if c.path_status else False
                            for c in cycles])
    flag_same = all(c.lateral_limits is None or c.lcc_status is None
                    or c.lateral_limits.lateral_limit_reached == c.lcc_status.lateral_limit_reached
                    for c in cycles)

    first: dict[str, float] = {}

    def mark(requirement: str, time_s: float) -> None:
        first.setdefault(requirement, float(time_s))

    if missing_outputs:
        mark("PP-SWR-010", missing_outputs[0].t0_us * 1e-6)
    for i, c in enumerate(cycles):
        if c.lateral_limits is None:
            mark("PP-SWR-150", t_s[i])
        if (c.lateral_limits is not None and c.lcc_status is not None
                and c.lateral_limits.lateral_limit_reached != c.lcc_status.lateral_limit_reached):
            mark("PP-SWR-009", t_s[i])

    ay_max = jerk_max = wheel_max = wheel_rate_max = deviation_max = 0.0
    jerk_sq_sum, jerk_count = 0.0, 0
    ay_floor_margin = np.inf
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
        if ay_max > PATH_AY_MAX_HWA:
            mark("PP-SWR-001", now_s)
        if jerk_max > JERK_MAX_HWA:
            mark("PP-SWR-003", now_s)
        deviation_max = max(deviation_max, float(np.max(np.abs(p.d[:n_window]))))
        near = np.arange(len(p.ay)) < n_window
        over = near & p.in_view & (np.abs(p.ay_need) > AYSMAX)
        if np.any(over):
            same_side = np.sign(p.ay[over]) == np.sign(p.ay_need[over])
            margin = np.where(same_side, np.abs(p.ay[over]), -np.inf) - (AYSMAX - cal["epsilon_ay"])
            ay_floor_margin = min(ay_floor_margin, float(np.min(margin)))
            if ay_floor_margin < 0.0:
                mark("PP-SWR-006", now_s)

    first_hwa = int(np.argmax(hwa)) if np.any(hwa) else len(cycles)
    hwa_request_s = log.scenario.hwa_request_s
    requested = t_s >= (hwa_request_s if hwa_request_s is not None else np.inf)
    sharp = np.zeros(len(cycles), dtype=bool)
    for i in range(first_hwa, len(cycles)):
        # Khi chu kỳ mất path, dùng độ cong quan sát ở chu kỳ trước.
        sharp[i] = (need_max[i] if paths[i] is not None else need_max[i - 1]) > AYSMAX
    judged_005 = sharp & requested
    kept_005 = bool(np.all(hwa[judged_005])) if np.any(judged_005) else True
    if not kept_005:
        mark("PP-SWR-005", t_s[int(np.argmax(judged_005 & ~hwa))])

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

    clear_times = []
    for i in range(1, len(cycles)):
        if valid[i] and valid[i - 1] and need_max[i - 1] >= AYSMAX > need_max[i]:
            for j in range(i, len(cycles)):
                if need_max[j] >= AYSMAX:
                    break
                if not flag_status[j]:
                    clear_times.append(t_s[j] - t_s[i])
                    break

    cont = [0.0, 0.0, 0.0]
    intervention_starts = {e.start for e in episodes}
    override_cycles = _overriding(cycles)
    for i in range(1, len(cycles)):
        if valid[i - 1] and valid[i] and finite[i - 1] and finite[i]:
            if i in intervention_starts:
                continue  # PP-SWR-031 được kiểm qua PP-SWR-080 và 049 ở chu kỳ đầu can thiệp.
            if i in override_cycles:
                continue
            if not _same_planner_pair(cycles[i - 1], cycles[i]):
                continue  # So tính liên tục trong cùng một planner. Việc arbitrator đổi nguồn path nằm ngoài phép đo (SRS 1.24).
            if _lcc_holds_at_car(cycles[i]):
                continue
            for j, value in enumerate(_continuity(cycles[i - 1], cycles[i], truth)):
                cont[j] = max(cont[j], value)
                if value > 1.0:
                    mark(("PP-SWR-100", "PP-SWR-101", "PP-SWR-102")[j], t_s[i])

    # PP-SWR-018 cho phép báo tầm nhìn ngắn hơn, chỉ giới hạn phần báo dài quá HORIZON_TOL_S.
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

    free_space = (log.road.lane_width - log.vehicle_width) / 2.0
    lane_wide_enough = free_space >= cal["free_space_min"]
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
            s_hint = None  # PP-PR-080: gợi ý cũ không dùng được sau khoảng không chấm.
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

    # Với F06, so sai lệch đoạn 2–3 s với path bám chính xác lane model sai, chỉ xét các frame có
    # lỗi (PP-SWR-125).
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

    big = _big_vehicles(log, cycles, paths, truth, cal["gap_truck_min"], cal.get("ttc_offset_start", 3.0), cal.get("t_offset_hold", 1.0))

    compute_ms = np.array([c.compute_ns for c in cycles]) * 1e-6
    # Gộp histogram của suite từ số mẫu trong từng bin, không lấy trung bình các histogram.
    compute_hist = np.histogram(np.clip(compute_ms, COMPUTE_BINS_MS[0], COMPUTE_BINS_MS[-1]),
                                               COMPUTE_BINS_MS)[0].tolist() if len(compute_ms) else []
    hwa_requested = [c for c in cycles if hwa_request_s is not None and c.t0_us >= hwa_request_s * 1e6]
    any_hwa = bool(np.any(hwa))
    timeout_share, timeout_judged = _requests_timeout_share(cycles)
    long_view = [c for c in cycles if c.lane_view_reported is not None and c.lane_view_reported > LONG_VIEW_M]
    long_view_valid = (sum(c.path_status is not None and c.path_status.path_valid for c in long_view) / len(long_view)
                       if long_view else 1.0)
    criteria = [
        Criterion("PP-SWR-010", "Trajectory và LccStatus, InterventionStatus mỗi chu kỳ", float(sent_every_cycle),
                  "= 1", sent_every_cycle),
        Criterion("PP-SWR-048", "Tỉ lệ chu kỳ quá timeout từ FunctionRequests dùng được gần nhất có NONE và path không hợp lệ",
                  timeout_share, "= 1", timeout_share == 1.0, applicable=timeout_judged),
        Criterion("PP-SWR-018", "observed_horizon_s trừ thời điểm ra khỏi tầm nhìn, lớn nhất [s]",
                  float(horizon_err), f"<= {HORIZON_TOL_S}", bool(horizon_err <= HORIZON_TOL_S),
                  applicable=bool(np.isfinite(horizon_err))),
        Criterion("PP-SWR-017", "Tỉ lệ chu kỳ có path hợp lệ khi lane model báo tầm nhìn > 126 m",
                  long_view_valid, "= 1", long_view_valid == 1.0, applicable=bool(long_view)),
        Criterion("PP-SWR-150", "LateralLimits mỗi chu kỳ", float(limits_every_cycle), "= 1",
                  limits_every_cycle, applicable=lcc_enabled),
        Criterion("PP-SWR-009", "Cờ giới hạn giống nhau ở LccStatus và LateralLimits",
                  float(flag_same), "= 1", flag_same),
        Criterion("PP-SWR-051", "DLC nhỏ nhất so với làn thật [m]", dlc_min, ">= 0",
                  dlc_min >= 0.0, applicable=bool(np.any(judged_051) if geometry is None else np.isfinite(dlc_min))),
        Criterion("PP-SWR-063", "Tỉ lệ chu kỳ có path hợp lệ báo lane_too_narrow khi khoảng trống thật < free_space_min",
                  narrow_share, "= 1", narrow_share == 1.0,
                  applicable=bool(judge_narrow and narrow_flags)),
        Criterion("PP-SWR-001", "a_y lớn nhất của path, HWA [m/s²]", ay_max, f"<= {PATH_AY_MAX_HWA:g}",
                  ay_max <= PATH_AY_MAX_HWA, applicable=any_hwa),
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
                  big.toward_056 if big else float("nan"), f"<= {OTHER_SIDE_OFFSET_M}", bool(big and big.toward_056 <= OTHER_SIDE_OFFSET_M),
                  applicable=bool(big and np.isfinite(big.toward_056))),
        Criterion("PP-SWR-058", "Lệch path về phía xa xe lớn lúc xe lớn tới ngang hàng [m]",
                  big.away_058 if big and big.away_058 is not None else float("nan"), "> 0",
                  bool(big and big.away_058 is not None and big.away_058 > 0.0),
                  applicable=bool(big and big.away_058 is not None)),
        Criterion("PP-SWR-065", "Lệch ngang lớn nhất của path khi một xe lớn quá gần và có xe ở làn bên kia [m]",
                  big.other_065 if big else float("nan"), f"<= {OTHER_SIDE_OFFSET_M}",
                  bool(big and big.other_065 <= OTHER_SIDE_OFFSET_M),
                  applicable=bool(big and np.isfinite(big.other_065))),
        Criterion("PP-SWR-066", "Lệch ngang lớn nhất của path khi dời vì đúng một xe lớn [m]",
                  big.offset_066 if big else float("nan"), f"<= {cal['offset_truck'] + OFFSET_TOLERANCE_M:.2f}",
                  bool(big and big.offset_066 <= cal["offset_truck"] + OFFSET_TOLERANCE_M),
                  applicable=bool(big and np.isfinite(big.offset_066))),
        Criterion("PP-SWR-100", "Lệch ngang giữa hai path liên tiếp / ngưỡng của khoảng", cont[0],
                  "<= 1", cont[0] <= 1.0),
        Criterion("PP-SWR-101", "Lệch hướng giữa hai path liên tiếp / ngưỡng của khoảng", cont[1],
                  "<= 1", cont[1] <= 1.0),
        Criterion("PP-SWR-102", "Lệch độ cong giữa hai path liên tiếp / ngưỡng của khoảng", cont[2],
                  "<= 1", cont[2] <= 1.0),
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
    if jerk_count:
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
        "compute_time_note": "Thời gian CPU của luồng gọi planner, gồm cả adapter SIL (ctypes)",
    }
    truth_t = np.asarray(log.t_us, dtype=float) * 1e-6
    info.update(r79_vehicle(truth_t, np.asarray(log.a_y, dtype=float),
                            _cycle_mask_at(truth_t, t_s, hwa) if len(cycles) else np.zeros(len(truth_t), bool)))
    for c in criteria:
        if c.applicable and not c.passed:
            c.first_fail_s = first.get(c.id)
    if intervention_enabled:
        criteria.append(over_refusal(cycles, log.scenario.notes.get("expected_outcome"),
                                     log.init_result == 0, cal, lcc_enabled=lcc_enabled))
    criteria.extend(fault_reaction_criteria(cycles, cal.get("T_coast", 1.0), cal))
    criteria.extend(boundary_fallback_criteria(log, cycles, cal))
    result = Result(log.scenario.name, log.seed, criteria, targets, info)
    if log.planner_only:
        result.info["planner_only"] = log.planner_only
    result.info["compute_hist"] = compute_hist
    result.criteria.extend(longitudinal_criteria(log, cycles))
    result.criteria.extend(switch_criteria(log, cycles, cal))
    result.criteria.extend(planner_criteria(cycles, cal))
    result.criteria.extend(follow_criteria(log, cycles, cal))
    adas = adas_requests(log)
    if adas is not None:
        result.info["adas_requests"] = adas
    fault = execution_fault([cycles[k] for k in np.flatnonzero(~finite)[:1]])
    if fault is not None:
        add_issue(result, ISSUE_EXECUTION, f"Lỗi thực thi: {fault[1]} không hữu hạn tại t = {fault[0]:.3f} s",
                  first_fail_s=fault[0])
    if intervention_enabled:
        _score_interventions(result, truth, paths, episodes, requests, cal, t_s)
    events = getattr(log, "fault_events", None) or {}
    if events:
        result.info["fault_events_s"] = {k: None if v is None else v * 1e-6 for k, v in events.items()}
        missing = sorted(k for k, v in events.items() if v is None)
        if missing:
            result.info["faults_not_injected"] = missing
    _score_fault_exposure(result, log)
    if (log.scenario.name.startswith(("S22b", "S22-b-"))
            and not any(c.id == "PP-SWR-173" and c.applicable for c in result.criteria)):
        add_issue(result, ISSUE_NOT_JUDGED, "S22b: chưa quan sát FOLLOW tới giới hạn 30 m rồi hết cửa sổ T_coast")
    from eval import labels
    if labels.difficulty(log.scenario) == "L1":
        failed = [c.id for c in result.criteria if c.applicable and not c.passed] + list(result.case_failures)
        result.criteria.append(Criterion("PP-SWR-062", "Requirement trượt ở biên ODD", float(len(failed)), "= 0",
                                         not failed))
    # Lỗi chưa được tiêm làm phép thử lỗi không đủ điều kiện; tiêu chí can thiệp độc lập vẫn được
    # chấm (PP-PR-069).
    if result.info.get("faults_not_injected"):
        add_issue(result, ISSUE_NOT_JUDGED,
                  "Lỗi chưa được bơm: sự kiện " + ", ".join(result.info["faults_not_injected"]) + " không xảy ra")
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

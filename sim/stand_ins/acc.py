"""Stand-in ACC and longitudinal actuator (Software Qualification Test Specification 4.7).

Test-side longitudinal block, fixed for every planner version (PP-ADR-001). It reads
LateralLimits (Interface Control Document 6.3) and sends LongitudinalPlan (5.7).

Implemented: CRUISE, FOLLOW and CURVE_LIMIT, target selection, the lateral_limit_reached
rule, limits, plan, loss of LateralLimits, actuator. FOLLOW reads the ObjectList, the
Trajectory and the lane model as received, like an ACC on the vehicle bus.

Numbers that 4.7 does not give (nhóm tự thống nhất, to be added to 4.7):
- speed-hold gain 0.4 1/s; curve-envelope gain 1.0 1/s plus the envelope's own slope
  as feedforward;
- LateralLimits timeout 75 ms, as PathStatus (Interface Control Document 6.2);
- the gap is counted from the front of the ego bounding box of the scenario file (centre at
  half the wheelbase, length 4.9 m, eval.openx), as the ObjectList gives no ego length; an
  object's position is moved forward by its relative speed over the age of the frame.
"""

from collections import deque
from dataclasses import dataclass
from math import hypot, sqrt

from interfaces import (
    LONGITUDINAL_PLAN_POINTS,
    TRAJECTORY_STEP_S,
    FrameId,
    Header,
    LaneModel,
    LateralLimits,
    LineStatus,
    LongitudinalMode,
    ObjectList,
    Trajectory,
    LongitudinalPlan,
    LongitudinalPoint,
)

PERIOD_US = 25_000  # 40 Hz (4.1)
AYSMAX = 2.5  # [m/s^2] HWA limit the planner's v_max refers to (PP-SWR-001)
AY_RESERVE = 0.3  # [m/s^2] left for HWA corrections (4.7)
CURVE_DECEL = 2.0  # [m/s^2] envelope before the curve (4.7)
LOOKAHEAD_S = 0.5  # d - 0.5 v in the envelope (4.7)
STABLE_VMAX = 0.05  # v_max change within 5 %: count d down (4.7)
A_MIN, A_MAX = -3.0, 1.5  # [m/s^2] (4.7)
JERK_MAX = 2.5  # [m/s^3] (4.7)
ACT_DELAY_S, ACT_TAU_S = 0.1, 0.3  # actuator (4.7)
K_SPEED = 0.4  # [1/s] nhóm tự thống nhất
K_CURVE = 1.0  # [1/s] nhóm tự thống nhất
LIMITS_TIMEOUT_US = 75_000  # nhóm tự thống nhất (as PathStatus)
# FOLLOW (4.7, "Chọn xe mục tiêu", "Bám xe trước")
STANDSTILL_GAP_M = 5.0
TIME_GAP_S = 1.8  # ISO 15622:2018 6.2.3.1 (1.5-2.2 s)
K_GAP, K_REL = 0.5, 1.0  # [1/s^2], [1/s]
GAP_ACCEL_LIMIT = 1.0  # [m/s^2] on the gap-error part
CORRIDOR_MARGIN_M = 0.2  # each side of the ego width
KEEP_MARGIN_M = 0.3  # more, each side, before a chosen target is dropped
KEEP_S = 1.0  # outside the wider corridor this long: dropped
LOOK_AHEAD_S = 1.0  # in the corridor now or after 1 s
MOVING_MPS = 1.0  # only objects seen moving at least this fast
EGO_LENGTH_M = 4.9  # bounding box of the scenario files (eval.openx)


@dataclass(frozen=True, slots=True)
class Lead:
    gap: float  # [m] bumper to bumper, now
    speed: float  # [m/s] over ground along the ego heading


class LeadSelector:
    """Target choice of 4.7 from the ObjectList, the Trajectory and the lane model received."""

    def __init__(self, vehicle_width: float, wheelbase: float) -> None:
        self.half = vehicle_width / 2
        self.front = wheelbase / 2 + EGO_LENGTH_M / 2
        self._moving: set[int] = set()
        self._target: int | None = None
        self._outside_since: int | None = None

    @staticmethod
    def _centre(x: float, path: list[tuple[float, float]], lane: LaneModel | None) -> float:
        if path and x <= path[-1][0]:
            for (x0, y0), (x1, y1) in zip(path, path[1:]):
                if x <= x1:
                    u = 0.0 if x1 <= x0 else (x - x0) / (x1 - x0)
                    return y0 + max(0.0, min(1.0, u)) * (y1 - y0)
            return path[0][1]
        if lane is not None and all(lane.lines[i].status != LineStatus.LOST for i in (1, 2)):
            left, right = lane.lines[1], lane.lines[2]
            return 0.5 * sum(l.c0 + l.c1 * x + l.c2 * x * x + l.c3 * x ** 3 for l in (left, right))
        return path[-1][1] if path else 0.0

    def _offset(self, obj, x: float, y: float, path, lane) -> float:
        """Distance from the corridor centre to the nearer side of the object [m]."""
        return abs(y - self._centre(x, path, lane)) - obj.width / 2

    def update(self, now_us: int, objects: ObjectList | None, trajectory: Trajectory | None,
               lane: LaneModel | None, v: float) -> Lead | None:
        if objects is None:
            self._target = None
            return None
        path = ([(p.pose.x, p.pose.y) for p in trajectory.points] if trajectory is not None else [])
        age = max(0.0, (now_us - objects.header.stamp_us) * 1e-6)
        best, chosen = None, None
        for obj in objects.objects[:objects.num_objects]:
            if obj.vx > 0 and hypot(obj.vx, obj.vy) >= MOVING_MPS:
                self._moving.add(obj.id)
            if obj.id not in self._moving or obj.vx <= 0:
                continue
            x = obj.x + (obj.vx - v) * age
            y = obj.y + obj.vy * age
            gap = x - obj.length / 2 - self.front
            if gap <= 0:
                continue
            inside = min(self._offset(obj, x, y, path, lane),
                         self._offset(obj, x + (obj.vx - v) * LOOK_AHEAD_S, y + obj.vy * LOOK_AHEAD_S, path, lane))
            lead = Lead(gap, obj.vx)
            if obj.id == self._target:
                chosen = (inside, lead)
            if inside < self.half + CORRIDOR_MARGIN_M and (best is None or gap < best[1].gap):
                best = (obj.id, lead)
        if chosen is not None and self._target is not None:
            if chosen[0] < self.half + CORRIDOR_MARGIN_M + KEEP_MARGIN_M:
                self._outside_since = None
            elif self._outside_since is None:
                self._outside_since = now_us
            if self._outside_since is None or now_us - self._outside_since <= KEEP_S * 1e6:
                if best is None or chosen[1].gap <= best[1].gap:
                    return chosen[1]
        elif self._target is not None and chosen is None:
            self._target = None
        if best is None:
            self._target = None
            return None
        if best[0] != self._target:
            self._target, self._outside_since = best[0], None
        return best[1]


@dataclass
class _Curve:
    v_max: float
    distance: float  # [m] to the curviest point, counted down while v_max is stable


class Acc:
    def __init__(self, set_speed_mps: float, read_limits: bool = True) -> None:
        """`read_limits` False: ACC ignores LateralLimits (S14 second run; R79 Annex 8 3.2.2)."""
        self.set_speed = set_speed_mps
        self.read_limits = read_limits
        self._limits: LateralLimits | None = None
        self._limits_rx = 0
        self._curve: _Curve | None = None
        self._last_cmd = 0.0
        self._counter = 0
        self.mode = LongitudinalMode.CRUISE
        self.command = 0.0
        self._lead: Lead | None = None

    def on_lateral_limits(self, msg: LateralLimits, rx_us: int) -> None:
        self._limits, self._limits_rx = msg, rx_us

    def _fresh_limits(self, now_us: int) -> LateralLimits | None:
        m = self._limits
        if m is None or not m.header.valid or now_us - self._limits_rx > LIMITS_TIMEOUT_US:
            return None
        return m

    def _update_curve(self, limits: LateralLimits | None, travelled: float) -> None:
        if limits is None or not self.read_limits:
            self._curve = None
            return
        c = self._curve
        if c is not None and abs(limits.v_max - c.v_max) <= STABLE_VMAX * c.v_max:
            c.distance = max(0.0, c.distance - travelled)
            c.v_max = min(c.v_max, limits.v_max)
        else:
            self._curve = _Curve(limits.v_max, limits.distance)

    @staticmethod
    def _law(v: float, set_speed: float, curve: _Curve | None, d: float, no_accel: bool,
             lead: Lead | None = None):
        """(acceleration, mode) before limits, for speed v and distance d to the curve."""
        a = K_SPEED * (set_speed - v)
        mode = LongitudinalMode.CRUISE
        if lead is not None:
            gap_error = lead.gap - (STANDSTILL_GAP_M + TIME_GAP_S * v)
            a_follow = (min(GAP_ACCEL_LIMIT, max(-GAP_ACCEL_LIMIT, K_GAP * gap_error))
                        + K_REL * (lead.speed - v))
            if a_follow < a:
                a, mode = a_follow, LongitudinalMode.FOLLOW
        if curve is not None:
            v_t = curve.v_max * sqrt(1.0 - AY_RESERVE / AYSMAX)
            room = max(0.0, d - LOOKAHEAD_S * v)
            v_allowed = sqrt(v_t * v_t + 2.0 * CURVE_DECEL * room)
            slope = -CURVE_DECEL * v / max(v_allowed, 0.1) if room > 0.0 else 0.0
            a_curve = slope + K_CURVE * (v_allowed - v)
            if a_curve < a:
                a, mode = a_curve, LongitudinalMode.CURVE_LIMIT
        if no_accel:
            a = min(a, 0.0)
        return a, mode

    def step(self, now_us: int, v: float, lead: Lead | None = None) -> LongitudinalPlan:
        dt = PERIOD_US * 1e-6
        self._lead = lead
        limits = self._fresh_limits(now_us)
        self._update_curve(limits, v * dt)
        # Lost LateralLimits: no acceleration (4.7). Flag on: no acceleration.
        no_accel = limits is None or (self.read_limits and limits.lateral_limit_reached)
        d = self._curve.distance if self._curve is not None else 0.0
        a, self.mode = self._law(v, self.set_speed, self._curve, d, no_accel, lead)
        a = min(A_MAX, max(A_MIN, a))
        a = min(self._last_cmd + JERK_MAX * dt, max(self._last_cmd - JERK_MAX * dt, a))
        self._last_cmd = self.command = a
        return self._plan(now_us, v, d, no_accel)

    def _plan(self, now_us: int, v: float, d: float, no_accel: bool) -> LongitudinalPlan:
        """The same law run 3 s ahead on the 0.1 s grid (4.7), without the actuator lag."""
        step = float(TRAJECTORY_STEP_S)
        points = []
        a_prev = self.command
        lead = self._lead
        for _ in range(LONGITUDINAL_PLAN_POINTS):
            points.append(LongitudinalPoint(max(v, 0.0), a_prev))
            a, _ = self._law(v, self.set_speed, self._curve, d, no_accel, lead)
            if lead is not None:  # the target keeps its speed over the plan
                lead = Lead(lead.gap + (lead.speed - v) * step, lead.speed)
            a = min(A_MAX, max(A_MIN, a))
            a = min(a_prev + JERK_MAX * step, max(a_prev - JERK_MAX * step, a))
            d = max(0.0, d - v * step)
            v = max(0.0, v + a * step)
            a_prev = a
        msg = LongitudinalPlan(Header(now_us, self._counter, True, FrameId.BASE_LINK),
                               self.mode, tuple(points), 0)
        self._counter = (self._counter + 1) % 256
        return msg


class LongitudinalActuator:
    """Acceleration command through a 0.1 s delay and a first-order lag tau = 0.3 s (4.7)."""

    def __init__(self, speed_mps: float) -> None:
        self.speed = speed_mps
        self.accel = 0.0
        self._queue: deque[tuple[int, float]] = deque()
        self._target = 0.0

    def command(self, now_us: int, accel: float) -> None:
        self._queue.append((now_us + round(ACT_DELAY_S * 1e6), accel))

    def step(self, now_us: int, dt: float) -> float:
        while self._queue and self._queue[0][0] <= now_us:
            self._target = self._queue.popleft()[1]
        self.accel += (self._target - self.accel) * dt / ACT_TAU_S
        self.speed = max(0.0, self.speed + self.accel * dt)
        return self.speed

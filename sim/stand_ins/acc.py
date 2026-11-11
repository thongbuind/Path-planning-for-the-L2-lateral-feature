"""Stand-in ACC and longitudinal actuator (Software Qualification Test Specification 4.7).

Test-side longitudinal block, fixed for every planner version (PP-ADR-001). It reads
LateralLimits (Interface Control Document 6.3) and sends LongitudinalPlan (5.7).

Implemented: CRUISE and CURVE_LIMIT, the lateral_limit_reached rule, limits, plan,
loss of LateralLimits, actuator. FOLLOW needs other vehicles in the simulator: later.

Numbers that 4.7 does not give (nhóm tự thống nhất, to be added to 4.7):
- speed-hold gain 0.4 1/s; curve-envelope gain 1.0 1/s plus the envelope's own slope
  as feedforward;
- LateralLimits timeout 75 ms, as PathStatus (Interface Control Document 6.2).
"""

from collections import deque
from dataclasses import dataclass
from math import sqrt

from interfaces import (
    LONGITUDINAL_PLAN_POINTS,
    TRAJECTORY_STEP_S,
    FrameId,
    Header,
    LateralLimits,
    LongitudinalMode,
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
    def _law(v: float, set_speed: float, curve: _Curve | None, d: float, no_accel: bool):
        """(acceleration, mode) before limits, for speed v and distance d to the curve."""
        a = K_SPEED * (set_speed - v)
        mode = LongitudinalMode.CRUISE
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

    def step(self, now_us: int, v: float) -> LongitudinalPlan:
        dt = PERIOD_US * 1e-6
        limits = self._fresh_limits(now_us)
        self._update_curve(limits, v * dt)
        # Lost LateralLimits: no acceleration (4.7). Flag on: no acceleration.
        no_accel = limits is None or (self.read_limits and limits.lateral_limit_reached)
        d = self._curve.distance if self._curve is not None else 0.0
        a, self.mode = self._law(v, self.set_speed, self._curve, d, no_accel)
        a = min(A_MAX, max(A_MIN, a))
        a = min(self._last_cmd + JERK_MAX * dt, max(self._last_cmd - JERK_MAX * dt, a))
        self._last_cmd = self.command = a
        return self._plan(now_us, v, d, no_accel)

    def _plan(self, now_us: int, v: float, d: float, no_accel: bool) -> LongitudinalPlan:
        """The same law run 3 s ahead on the 0.1 s grid (4.7), without the actuator lag."""
        step = float(TRAJECTORY_STEP_S)
        points = []
        a_prev = self.command
        for _ in range(LONGITUDINAL_PLAN_POINTS):
            points.append(LongitudinalPoint(max(v, 0.0), a_prev))
            a, _ = self._law(v, self.set_speed, self._curve, d, no_accel)
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

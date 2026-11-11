"""Ego-motion service (Interface Control Document 5.5; Software Qualification Test
Specification 4.5).

Answers with the true motion of base_link, lateral slip included (ICD 5.5): integrates
the chassis signals as received (speed, yaw rate) plus v_y of VehicleStateEstimate, so
its error follows any fault injected into those inputs. Between samples each input is
held. Before the first v_y arrives, v_y counts as 0.
"""

from bisect import bisect_right
from collections import deque
from math import cos, sin

from interfaces import EGO_MOTION_WINDOW_US, EgoMotionRequest, EgoMotionResponse

HISTORY_US = 2 * EGO_MOTION_WINDOW_US
_SMALL_YAW_RATE = 1e-9


class EgoMotion:
    def __init__(self) -> None:
        self._speed: deque[tuple[int, float]] = deque()
        self._yaw_rate: deque[tuple[int, float]] = deque()
        self._lateral: deque[tuple[int, float]] = deque()
        self.now_us = 0

    def on_speed(self, speed_mps: float, rx_us: int) -> None:
        self._push(self._speed, rx_us, speed_mps)

    def on_yaw_rate(self, yaw_rate: float, rx_us: int) -> None:
        self._push(self._yaw_rate, rx_us, yaw_rate)

    def on_lateral_velocity(self, v_y: float, rx_us: int) -> None:
        """v_y at base_link from VehicleStateEstimate (Interface Control Document 5.4)."""
        self._push(self._lateral, rx_us, v_y)

    def _push(self, history: deque, t_us: int, value: float) -> None:
        history.append((t_us, value))
        self.now_us = max(self.now_us, t_us)
        for h in (self._speed, self._yaw_rate, self._lateral):
            while h and h[0][0] < self.now_us - HISTORY_US:
                h.popleft()

    @staticmethod
    def _value_at(history: deque, t_us: int, default: float | None = None) -> float | None:
        times = [t for t, _ in history]
        i = bisect_right(times, t_us) - 1
        return history[i][1] if i >= 0 else default

    def query(self, request: EgoMotionRequest) -> EgoMotionResponse:
        t1, t2 = request.t1_us, request.t2_us
        invalid = EgoMotionResponse(False, 0.0, 0.0, 0.0)
        if t2 < t1 or not self._speed or not self._yaw_rate:
            return invalid
        if t1 < self._speed[0][0] or t1 < self._yaw_rate[0][0]:
            return invalid
        # Break points: every sample time inside (t1, t2).
        cuts = {t1, t2}
        for history in (self._speed, self._yaw_rate, self._lateral):
            cuts |= {t for t, _ in history if t1 < t < t2}
        cuts = sorted(cuts)
        x = y = yaw = 0.0
        for a, b in zip(cuts[:-1], cuts[1:]):
            v = self._value_at(self._speed, a)
            r = self._value_at(self._yaw_rate, a)
            vy = self._value_at(self._lateral, a, 0.0)
            dt = (b - a) * 1e-6
            end = yaw + r * dt
            if abs(r) < _SMALL_YAW_RATE:
                x += (v * cos(yaw) - vy * sin(yaw)) * dt
                y += (v * sin(yaw) + vy * cos(yaw)) * dt
            else:
                # Body velocity (v, vy) held, heading turning at r.
                x += (v * (sin(end) - sin(yaw)) + vy * (cos(end) - cos(yaw))) / r
                y += (v * (cos(yaw) - cos(end)) + vy * (sin(end) - sin(yaw))) / r
            yaw = end
        return EgoMotionResponse(True, x, y, yaw)

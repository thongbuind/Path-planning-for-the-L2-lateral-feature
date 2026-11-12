"""Prescribed driver inputs and disturbances for SIL (SQTS 4.4, 4.6).

The driver changes the EPS target to generate the approach arc and then returns
it to the nominal road-following angle. Bicycle dynamics determine the drift.
Wind and road banking apply a persistent signed force at the centre of gravity.
"""

from dataclasses import dataclass
from math import isfinite, sin

from interfaces import Side
from sim.messages import DriverSignals
from sim.vehicle.bicycle import G, steady_cornering
from sim.vehicle.profiles import VehicleProfile


@dataclass(frozen=True, slots=True)
class DriverSpec:
    steer_start_s: float = 0.0
    steer_release_s: float = 0.0
    drift_curvature: float = 0.0  # [1/m] road-relative, left positive
    torque_nm: float = 0.0  # during the same steering interval
    disturbance_start_s: float = 0.0
    wind_force_n: float = 0.0  # left positive at the CG
    bank_angle_rad: float = 0.0  # positive when the road slopes down to the left
    indicator: Side = Side.NONE
    indicator_start_s: float = 0.0
    indicator_end_s: float | None = None
    passive_hands_on: bool = False
    # More steering intervals of the same length (S16 repeated drift, S8c steer and return):
    # (start_s, scale): the first drift times scale; +1 the same drift, -1 the opposite.
    # With repeat_trigger (sim.faults.trigger), repeat k starts start_s after the k-th
    # occurrence of that event of the planner output (the harness sets the time).
    repeats: tuple[tuple[float, float], ...] = ()
    repeat_trigger: str | None = None
    # (start_s, end_s): the driver keeps torque_nm on the wheel, in the direction of the last
    # steering interval, between steering intervals too (S17 lane change, S9 c override).
    torque_windows: tuple[tuple[float, float], ...] = ()

    def __post_init__(self) -> None:
        from sim.faults import trigger
        trigger.check(self.repeat_trigger)
        length = self.steer_release_s - self.steer_start_s
        starts = [self.steer_start_s] + [t for t, _ in self.repeats]
        if self.repeats and (any(d == 0 or not isfinite(d) or not isfinite(t) for t, d in self.repeats)
                             or (self.repeat_trigger is None
                                 and any(b < a + length for a, b in zip(starts, starts[1:])))
                             or (self.repeat_trigger is not None and any(t < 0 for t, _ in self.repeats))):
            raise ValueError("driver repeats need a non-zero finite scale and must start after the previous one ends")
        times = (self.steer_start_s, self.steer_release_s, self.disturbance_start_s, self.indicator_start_s)
        levels = (self.drift_curvature, self.torque_nm, self.wind_force_n, self.bank_angle_rad)
        if not all(map(isfinite, (*times, *levels))) or min(times) < 0:
            raise ValueError("driver levels and times must be finite, times non-negative")
        if self.steer_release_s < self.steer_start_s or (
                (self.drift_curvature or self.torque_nm) and self.steer_release_s == self.steer_start_s):
            raise ValueError("driver steering interval must have positive duration")
        if any(not (isfinite(a) and isfinite(b)) or a < 0 or b <= a for a, b in self.torque_windows):
            raise ValueError("torque windows need 0 <= start < end")
        if self.indicator_end_s is not None and (
                not isfinite(self.indicator_end_s) or self.indicator_end_s <= self.indicator_start_s):
            raise ValueError("indicator must end after it starts")

    def command(self, now_us: int, vehicle: VehicleProfile, steering_ratio: float,
                speed_mps: float, curvature: float) -> tuple[float, float, DriverSignals]:
        """Wheel angle [rad], external lateral force [N], and signals at this instant."""
        t_s = now_us * 1e-6
        length = self.steer_release_s - self.steer_start_s
        direction = 0.0
        last = 1.0  # direction of the last steering interval started
        for start, sign in ((self.steer_start_s, 1.0), *self.repeats):
            if start <= t_s < start + length:
                direction = sign
            if start <= t_s:
                last = sign
        steering = direction != 0
        held = any(a <= t_s < b for a, b in self.torque_windows)
        if steering:
            curvature += direction * self.drift_curvature
        _, _, wheel_angle = steady_cornering(vehicle, speed_mps, curvature)
        force = 0.0
        if t_s >= self.disturbance_start_s:
            force = self.wind_force_n + vehicle.mass * G * sin(self.bank_angle_rad)
        indicator = Side.NONE
        if t_s >= self.indicator_start_s and (self.indicator_end_s is None or t_s < self.indicator_end_s):
            indicator = self.indicator
        torque = direction * self.torque_nm if steering else (
            (1.0 if last > 0 else -1.0) * self.torque_nm if held else 0.0)
        signals = DriverSignals(torque_nm=torque, indicator=indicator,
                                hands_on=steering or held or self.passive_hands_on)
        return wheel_angle * steering_ratio, force, signals

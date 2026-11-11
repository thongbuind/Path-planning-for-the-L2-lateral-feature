"""Stand-in EPS (Software Qualification Test Specification 4.6).

Tracks the requested steering wheel angle: pure delay `actuator_delay`, first-order
lag tau = 0.1 s, rate and angle limits from VehicleConfig. When the controller does
not control, it hands over to the fake driver's angle within 1 s.
"""

from collections import deque

from interfaces import VehicleConfig
from sim.messages import SteeringRequest

TAU_S = 0.1  # 4.6
HANDOVER_S = 1.0  # 4.6


class Eps:
    def __init__(self, vehicle: VehicleConfig, actuator_delay_s: float | None = None) -> None:
        """`actuator_delay_s` overrides VehicleConfig for the slow-EPS scenarios (S13)."""
        self.vehicle = vehicle
        self.delay_us = round(1e6 * (vehicle.actuator_delay if actuator_delay_s is None
                                     else actuator_delay_s))
        self._requests: deque[tuple[int, SteeringRequest]] = deque()
        self._command: SteeringRequest | None = None
        self._inactive_since_us: int | None = 0
        self._last_active_angle = 0.0
        self.angle = 0.0  # [rad] steering wheel angle
        self.rate = 0.0  # [rad/s]
        self.driver_angle = 0.0  # [rad] the fake driver's steering wheel angle

    def hold_driver_angle(self, angle: float) -> None:
        """Start with the fake driver steering `angle`, no handover pending."""
        self.angle = self.driver_angle = self._last_active_angle = angle

    @property
    def controlling(self) -> bool:
        return self._command is not None and self._command.active

    def on_request(self, request: SteeringRequest, rx_us: int) -> None:
        self._requests.append((rx_us + self.delay_us, request))

    def step(self, now_us: int, dt: float) -> float:
        """Advance by dt; returns the front wheel angle [rad]."""
        while self._requests and self._requests[0][0] <= now_us:
            _, cmd = self._requests.popleft()
            if cmd.active:
                self._inactive_since_us = None
            elif self._inactive_since_us is None:
                self._inactive_since_us = now_us
                self._last_active_angle = self.angle
            self._command = cmd

        if self.controlling:
            target = self._command.steering_wheel_angle_rad
        else:
            since = self._inactive_since_us if self._inactive_since_us is not None else now_us
            h = min(1.0, (now_us - since) / (HANDOVER_S * 1e6))
            target = (1 - h) * self._last_active_angle + h * self.driver_angle

        v = self.vehicle
        max_rate = v.max_steering_wheel_rate
        max_angle = v.max_wheel_angle * v.steering_ratio
        rate = min(max_rate, max(-max_rate, (target - self.angle) / TAU_S))
        self.angle = min(max_angle, max(-max_angle, self.angle + rate * dt))
        self.rate = rate
        return self.angle / v.steering_ratio

from collections import deque

from interfaces import VehicleConfig
from sim.messages import SteeringRequest

TAU_S = 0.1
# Ngưỡng torque_override lấy từ ADAS-FS 12 và nằm trong giới hạn Euro NCAP ghi tại đó.
OVERRIDE_TORQUE_NM = 3.0
HANDOVER_S = 1.0


class Eps:
    def __init__(self, vehicle: VehicleConfig, actuator_delay_s: float | None = None,
                 *, moving_driver_target: bool = False) -> None:
        self.vehicle = vehicle
        self.delay_us = round(1e6 * (vehicle.actuator_delay if actuator_delay_s is None
                                     else actuator_delay_s))
        self._requests: deque[tuple[int, SteeringRequest]] = deque()
        self._command: SteeringRequest | None = None
        self._inactive_since_us: int | None = None if moving_driver_target else 0
        self._last_active_angle = 0.0
        self._last_active_system_share = 0.0
        self.angle = 0.0
        self.rate = 0.0
        self.system_steering_share = 0.0
        self.driver_angle = 0.0
        self.driver_torque = 0.0

    def hold_driver_angle(self, angle: float) -> None:
        self.angle = self.driver_angle = self._last_active_angle = angle

    @property
    def controlling(self) -> bool:
        return self._command is not None and self._command.active

    def on_request(self, request: SteeringRequest, rx_us: int) -> None:
        self._requests.append((rx_us + self.delay_us, request))

    def step(self, now_us: int, dt: float) -> float:
        while self._requests and self._requests[0][0] <= now_us:
            _, cmd = self._requests.popleft()
            if cmd.active:
                self._inactive_since_us = None
            elif self.controlling:
                self._inactive_since_us = now_us
                self._last_active_angle = self.angle
                self._last_active_system_share = self.system_steering_share
            self._command = cmd

        if self.controlling and abs(self.driver_torque) >= OVERRIDE_TORQUE_NM:
            # Khi torque vượt ngưỡng, EPS theo tài xế; quyền theo lệnh hệ thống trở lại khi hết
            # override.
            target = self.driver_angle
            self.system_steering_share = 0.0
        elif self.controlling:
            target = self._command.steering_wheel_angle_rad
            self.system_steering_share = 1.0
        elif self._inactive_since_us is not None:
            h = min(1.0, (now_us - self._inactive_since_us) / (HANDOVER_S * 1e6))
            target = (1 - h) * self._last_active_angle + h * self.driver_angle
            self.system_steering_share = (1 - h) * self._last_active_system_share
        else:
            target = self.driver_angle
            self.system_steering_share = 0.0

        v = self.vehicle
        max_rate = v.max_steering_wheel_rate
        max_angle = v.max_wheel_angle * v.steering_ratio
        rate = min(max_rate, max(-max_rate, (target - self.angle) / TAU_S))
        self.angle = min(max_angle, max(-max_angle, self.angle + rate * dt))
        self.rate = rate
        return self.angle / v.steering_ratio

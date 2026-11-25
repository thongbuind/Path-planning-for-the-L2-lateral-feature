"""Các biến thể Lateral Controller của PP-TS-027 dùng trong SIL."""

from collections import deque
from math import exp, expm1, isfinite

from interfaces import EgoMotionQuery, VehicleConfig
from sim.messages import SteeringRequest
from sim.runtime.channel import PUBSUB_LATENCY_US
from sim.stand_ins.eps import TAU_S
from sim.stand_ins.lateral_controller import PREVIEW_S, US_PER_S, EgoState, LateralController


class StaticHwaCommandLimit(LateralController):
    def __init__(self, vehicle: VehicleConfig, understeer_gradient: float, *, sustained_ay_mps2: float) -> None:
        super().__init__(vehicle, understeer_gradient)
        if not isfinite(sustained_ay_mps2) or sustained_ay_mps2 <= 0.0:
            raise ValueError("sustained a_y must be finite and positive")
        self.sustained_ay_mps2 = sustained_ay_mps2

    def _steering_to_ay(self, speed_mps: float) -> float:
        speed_squared = speed_mps ** 2
        effective_wheelbase = self.vehicle.wheelbase + self.understeer_gradient * speed_squared
        return speed_squared / effective_wheelbase if effective_wheelbase > 0.0 else 0.0

    def _limit_wheel_angle(self, now_us: int, state: EgoState, wheel_angle: float) -> float:
        gain = self._steering_to_ay(state.speed_mps)
        if gain <= 0.0:
            return wheel_angle
        limit = self.sustained_ay_mps2 / gain
        return min(limit, max(-limit, wheel_angle))


class PredictedHwaCommandLimit(StaticHwaCommandLimit):
    def __init__(self, vehicle: VehicleConfig, understeer_gradient: float, *, sustained_ay_mps2: float) -> None:
        super().__init__(vehicle, understeer_gradient, sustained_ay_mps2=sustained_ay_mps2)
        self._delay_us = round(vehicle.actuator_delay * US_PER_S) + PUBSUB_LATENCY_US
        self._pending: deque[tuple[int, float]] = deque()
        self._applied_angle: float | None = None

    def step(self, now_us: int, state: EgoState, ego_motion: EgoMotionQuery) -> SteeringRequest:
        while self._pending and self._pending[0][0] <= now_us:
            _, self._applied_angle = self._pending.popleft()
        request = super().step(now_us, state, ego_motion)
        if request.active and self._controlling_hwa(state):
            self._pending.append((now_us + self._delay_us,
                                  request.steering_wheel_angle_rad / self.vehicle.steering_ratio))
        else:
            self._pending.clear()
            self._applied_angle = None
        return request

    def _acceleration_at_application(self, now_us: int, measured_ay: float, gain: float) -> float:
        target = measured_ay if self._applied_angle is None else gain * self._applied_angle
        position = now_us
        ay = measured_ay
        application = now_us + self._delay_us
        for at, angle in self._pending:
            decay = exp(-(at - position) / (US_PER_S * TAU_S))
            ay = target + decay * (ay - target)
            target = gain * angle
            position = at
        return target + exp(-(application - position) / (US_PER_S * TAU_S)) * (ay - target)

    def _limit_wheel_angle(self, now_us: int, state: EgoState, wheel_angle: float) -> float:
        gain = self._steering_to_ay(state.speed_mps)
        remaining_s = PREVIEW_S - self._delay_us / US_PER_S
        if gain <= 0.0 or remaining_s <= 0.0:
            return super()._limit_wheel_angle(now_us, state, wheel_angle)

        # Phần đáp ứng do lệnh mới tăng đơn điệu từ lúc EPS nhận lệnh tới cuối preview.
        # Khi a_y đã vượt ở đầu đoạn này, cùng biên cuối đoạn vẫn buộc lệnh kéo a_y về.
        measured_ay = state.speed_mps * state.yaw_rate_rps
        at_application = self._acceleration_at_application(now_us, measured_ay, gain)
        response = -expm1(-remaining_s / TAU_S)
        inherited = (1.0 - response) * at_application
        lower = (-self.sustained_ay_mps2 - inherited) / (response * gain)
        upper = (self.sustained_ay_mps2 - inherited) / (response * gain)
        return min(upper, max(lower, wheel_angle))

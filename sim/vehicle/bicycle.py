"""Bicycle model đặt tại trọng tâm và dùng RK4. Ở tốc độ thấp mô hình chuyển dần sang động học
(SQTS 4.4).
"""

from dataclasses import dataclass
from math import atan2, cos, sin, tan

from sim.vehicle.profiles import VehicleProfile

G = 9.81
MU_DRY = 1.0
KINEMATIC_BELOW_MPS = 3.0
DYNAMIC_ABOVE_MPS = 5.0


def steady_cornering(p: VehicleProfile, v: float, kappa: float) -> tuple[float, float, float]:
    """Trả v_y tại trọng tâm, yaw rate và góc bánh trước khi hai trục cân bằng lực ngang trên cua."""
    r = v * kappa
    if v <= 0.0 or kappa == 0.0:
        return 0.0, r, p.wheelbase * kappa
    alpha_f = p.mass * v * r * p.lr / (p.c_front * p.wheelbase)
    alpha_r = p.mass * v * r * p.lf / (p.c_rear * p.wheelbase)
    v_y = p.lr * r - v * alpha_r
    delta = alpha_f + (v_y + p.lf * r) / v
    return v_y, r, delta


@dataclass(slots=True)
class BicycleState:
    x: float
    y: float
    psi: float
    v_y: float  # [m/s] Vận tốc ngang tại trọng tâm, trong khung thân xe.
    r: float


class Bicycle:
    def __init__(self, profile: VehicleProfile, state: BicycleState, mu: float = MU_DRY) -> None:
        self.p = profile
        self.state = state
        self.mu = mu
        self.v_x = 0.0
        self.a_y = 0.0
        self.external_force_y = 0.0
        p = profile
        self._lf, self._lr, self._mass = p.lf, p.lr, p.mass
        self._c_front, self._c_rear, self._yaw_inertia = p.c_front, p.c_rear, p.yaw_inertia
        self._fz_f = p.mass * G * p.lr / p.wheelbase
        self._fz_r = p.mass * G * p.lf / p.wheelbase

    def _axle_forces(self, v_y: float, r: float, delta: float) -> tuple[float, float]:
        v = max(self.v_x, 0.1)
        alpha_f = delta - (v_y + self._lf * r) / v
        alpha_r = -(v_y - self._lr * r) / v
        lim_f, lim_r = self.mu * self._fz_f, self.mu * self._fz_r
        fy_f = min(lim_f, max(-lim_f, self._c_front * alpha_f))
        fy_r = min(lim_r, max(-lim_r, self._c_rear * alpha_r))
        return fy_f, fy_r

    def _derivative(self, s: tuple[float, ...], delta: float) -> tuple[float, ...]:
        _, _, psi, v_y, r = s
        v = self.v_x
        fy_f, fy_r = self._axle_forces(v_y, r, delta)
        dv_y = (fy_f * cos(delta) + fy_r + self.external_force_y) / self._mass - v * r
        dr = (self._lf * fy_f * cos(delta) - self._lr * fy_r) / self._yaw_inertia
        dx = v * cos(psi) - v_y * sin(psi)
        dy = v * sin(psi) + v_y * cos(psi)
        return dx, dy, r, dv_y, dr

    def step(self, dt: float, delta: float, v_x: float) -> None:
        self.v_x = v_x
        st = self.state
        s0 = (st.x, st.y, st.psi, st.v_y, st.r)

        def add(a, b, h):
            return tuple(ai + h * bi for ai, bi in zip(a, b))

        k1 = self._derivative(s0, delta)
        k2 = self._derivative(add(s0, k1, dt / 2), delta)
        k3 = self._derivative(add(s0, k2, dt / 2), delta)
        k4 = self._derivative(add(s0, k3, dt), delta)
        s1 = tuple(s0[i] + dt / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) for i in range(5))
        x, y, psi, v_y, r = s1

        w = min(1.0, max(0.0, (v_x - KINEMATIC_BELOW_MPS) / (DYNAMIC_ABOVE_MPS - KINEMATIC_BELOW_MPS)))
        if w < 1.0:
            r_kin = v_x * tan(delta) / self.p.wheelbase
            v_y_kin = self.p.lr * r_kin
            r = w * r + (1 - w) * r_kin
            v_y = w * v_y + (1 - w) * v_y_kin

        fy_f, fy_r = self._axle_forces(v_y, r, delta)
        self.a_y = (fy_f * cos(delta) + fy_r + self.external_force_y) / self.p.mass
        self.state = BicycleState(x, y, psi, v_y, r)

    def rear_axle(self) -> tuple[float, float, float]:
        st = self.state
        return st.x - self.p.lr * cos(st.psi), st.y - self.p.lr * sin(st.psi), st.psi

    def front_axle(self) -> tuple[float, float, float]:
        st = self.state
        return st.x + self.p.lf * cos(st.psi), st.y + self.p.lf * sin(st.psi), st.psi

    def rear_axle_lateral_velocity(self) -> float:
        return self.state.v_y - self.p.lr * self.state.r

    def slip_angle(self) -> float:
        return atan2(self.state.v_y, max(self.v_x, 0.1))

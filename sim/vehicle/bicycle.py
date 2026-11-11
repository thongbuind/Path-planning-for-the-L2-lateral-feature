"""Dynamic bicycle model (Software Qualification Test Specification 4.4).

States x, y, psi, v_y, r at the centre of gravity; RK4 with 1 ms steps. Linear tyres
F = C alpha, each axle limited to mu F_z. Below 5 m/s the model blends into a
kinematic bicycle, fully kinematic at 3 m/s. Longitudinal speed is an input
(scripted or from the stand-in ACC).
"""

from dataclasses import dataclass
from math import atan2, cos, sin, tan

from sim.vehicle.profiles import VehicleProfile

G = 9.81  # [m/s^2]
MU_DRY = 1.0  # 4.4
KINEMATIC_BELOW_MPS = 3.0  # 4.4: blend between 3 and 5 m/s
DYNAMIC_ABOVE_MPS = 5.0


def steady_cornering(p: VehicleProfile, v: float, kappa: float) -> tuple[float, float, float]:
    """(v_y at the CG, yaw rate, front wheel angle) of the linear model turning steadily on
    curvature kappa at speed v: r = v kappa, both axles in lateral force balance."""
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
    x: float  # [m] CG, world
    y: float
    psi: float  # [rad] heading, world
    v_y: float  # [m/s] lateral velocity at the CG, body frame
    r: float  # [rad/s] yaw rate


class Bicycle:
    def __init__(self, profile: VehicleProfile, state: BicycleState, mu: float = MU_DRY) -> None:
        self.p = profile
        self.state = state
        self.mu = mu
        self.v_x = 0.0
        self.a_y = 0.0  # [m/s^2] lateral acceleration at the CG, body frame
        self.external_force_y = 0.0  # [N] bank or crosswind, body frame

    def _axle_forces(self, v_y: float, r: float, delta: float) -> tuple[float, float]:
        p, v = self.p, max(self.v_x, 0.1)
        alpha_f = delta - (v_y + p.lf * r) / v
        alpha_r = -(v_y - p.lr * r) / v
        fz_f = p.mass * G * p.lr / p.wheelbase
        fz_r = p.mass * G * p.lf / p.wheelbase
        lim_f, lim_r = self.mu * fz_f, self.mu * fz_r
        fy_f = min(lim_f, max(-lim_f, p.c_front * alpha_f))
        fy_r = min(lim_r, max(-lim_r, p.c_rear * alpha_r))
        return fy_f, fy_r

    def _derivative(self, s: tuple[float, ...], delta: float) -> tuple[float, ...]:
        _, _, psi, v_y, r = s
        p, v = self.p, self.v_x
        fy_f, fy_r = self._axle_forces(v_y, r, delta)
        dv_y = (fy_f * cos(delta) + fy_r + self.external_force_y) / p.mass - v * r
        dr = (p.lf * fy_f * cos(delta) - p.lr * fy_r) / p.yaw_inertia
        dx = v * cos(psi) - v_y * sin(psi)
        dy = v * sin(psi) + v_y * cos(psi)
        return dx, dy, r, dv_y, dr

    def step(self, dt: float, delta: float, v_x: float) -> None:
        """Advance by dt with front wheel angle delta [rad] and speed v_x [m/s]."""
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

        # Low-speed blend towards the kinematic model (4.4).
        w = min(1.0, max(0.0, (v_x - KINEMATIC_BELOW_MPS) / (DYNAMIC_ABOVE_MPS - KINEMATIC_BELOW_MPS)))
        if w < 1.0:
            r_kin = v_x * tan(delta) / self.p.wheelbase
            v_y_kin = self.p.lr * r_kin
            r = w * r + (1 - w) * r_kin
            v_y = w * v_y + (1 - w) * v_y_kin

        fy_f, fy_r = self._axle_forces(v_y, r, delta)
        self.a_y = (fy_f * cos(delta) + fy_r + self.external_force_y) / self.p.mass
        self.state = BicycleState(x, y, psi, v_y, r)

    # Views at base_link (rear axle centre) and the front axle.
    def rear_axle(self) -> tuple[float, float, float]:
        st = self.state
        return st.x - self.p.lr * cos(st.psi), st.y - self.p.lr * sin(st.psi), st.psi

    def front_axle(self) -> tuple[float, float, float]:
        st = self.state
        return st.x + self.p.lf * cos(st.psi), st.y + self.p.lf * sin(st.psi), st.psi

    def rear_axle_lateral_velocity(self) -> float:
        """v_y at base_link (Interface Control Document 5.4)."""
        return self.state.v_y - self.p.lr * self.state.r

    def slip_angle(self) -> float:
        return atan2(self.state.v_y, max(self.v_x, 0.1))

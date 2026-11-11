"""Vehicle profiles VP-0 to VP-5 (Software Qualification Test Specification 4.4).

Published data per profile plus the derived parameters of the "Tham số" table of 4.4.
The planner only sees VehicleConfig; mass, tyre stiffness and inertia stay in the
simulator.
"""

from dataclasses import dataclass

from interfaces import VehicleConfig

# Same for every profile (4.4, nhóm tự thống nhất).
STEERING_RATIO = 15.0
MAX_STEERING_WHEEL_RATE = 6.0  # [rad/s]
ACTUATOR_DELAY_S = 0.05
# Tyre stiffness per 2000 kg (4.4): keeps K about 0.0029 rad/(m/s^2) for every profile.
C_FRONT_PER_2000KG = 100_000.0  # [N/rad]
C_REAR_PER_2000KG = 140_000.0
YAW_INERTIA_FACTOR = 0.83  # I_z = 0.83 m l_f l_r


@dataclass(frozen=True, slots=True)
class VehicleProfile:
    name: str
    wheelbase: float  # [m]
    width_with_mirrors: float  # [m]
    mass: float  # [kg]
    max_wheel_angle: float  # [rad]

    @property
    def lf(self) -> float:
        """CG to front axle; l_f = l_r = wheelbase / 2 (4.4)."""
        return 0.5 * self.wheelbase

    @property
    def lr(self) -> float:
        return 0.5 * self.wheelbase

    @property
    def c_front(self) -> float:
        return C_FRONT_PER_2000KG * self.mass / 2000.0

    @property
    def c_rear(self) -> float:
        return C_REAR_PER_2000KG * self.mass / 2000.0

    @property
    def yaw_inertia(self) -> float:
        return YAW_INERTIA_FACTOR * self.mass * self.lf * self.lr

    @property
    def understeer_gradient(self) -> float:
        """K [rad/(m/s^2)] of the linear bicycle model."""
        return self.mass / self.wheelbase * (self.lr / self.c_front - self.lf / self.c_rear)

    def vehicle_config(self) -> VehicleConfig:
        return VehicleConfig(
            wheelbase=self.wheelbase,
            rear_axle_to_cg=self.lr,
            vehicle_width=self.width_with_mirrors,
            steering_ratio=STEERING_RATIO,
            max_wheel_angle=self.max_wheel_angle,
            max_steering_wheel_rate=MAX_STEERING_WHEEL_RATE,
            actuator_delay=ACTUATOR_DELAY_S,
        )


PROFILES = {
    p.name: p
    for p in (
        VehicleProfile("VP-0", 2.90, 1.90, 2000.0, 0.61),
        VehicleProfile("VP-1", 2.075, 1.96, 857.0, 0.54),
        VehicleProfile("VP-2", 2.730, 2.11, 1600.0, 0.52),
        VehicleProfile("VP-3", 2.950, 2.21, 2540.0, 0.50),
        VehicleProfile("VP-4", 3.150, 2.254, 2932.0, 0.44),
        VehicleProfile("VP-5", 3.150, 2.50, 2932.0, 0.44),
    )
}

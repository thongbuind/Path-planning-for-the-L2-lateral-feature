from math import radians, sin

import pytest

from interfaces import Side
from sim.messages import SteeringRequest
from sim.stand_ins.driver import DriverSpec
from sim.stand_ins.eps import Eps
from sim.vehicle.bicycle import G, steady_cornering
from sim.vehicle.profiles import PROFILES

PROFILE = PROFILES["VP-0"]
VEHICLE = PROFILE.vehicle_config()


def test_driver_applies_arc_then_releases_and_indicates_on_its_own_schedule():
    spec = DriverSpec(steer_start_s=2.0, steer_release_s=2.5, drift_curvature=1 / 800,
                      torque_nm=2.0, indicator=Side.LEFT, indicator_start_s=1.0, indicator_end_s=3.0)
    nominal = 1 / 1200
    _, _, wheel_in_curve = steady_cornering(PROFILE, 20.0, nominal)
    angle, force, signals = spec.command(1_000_000, PROFILE, VEHICLE.steering_ratio, 20.0, nominal)
    assert angle == pytest.approx(wheel_in_curve * VEHICLE.steering_ratio)
    assert signals.indicator == Side.LEFT and not signals.hands_on and force == 0.0
    angle, _, signals = spec.command(2_250_000, PROFILE, VEHICLE.steering_ratio, 20.0, nominal)
    assert angle > wheel_in_curve * VEHICLE.steering_ratio
    assert signals.hands_on and signals.torque_nm == 2.0
    angle, _, signals = spec.command(2_500_000, PROFILE, VEHICLE.steering_ratio, 20.0, nominal)
    assert angle == pytest.approx(wheel_in_curve * VEHICLE.steering_ratio)
    assert not signals.hands_on and signals.torque_nm == 0.0
    _, _, signals = spec.command(3_000_000, PROFILE, VEHICLE.steering_ratio, 20.0, nominal)
    assert signals.indicator == Side.NONE


def test_wind_and_bank_force_is_persistent_and_signed():
    spec = DriverSpec(disturbance_start_s=1.0, wind_force_n=-100.0, bank_angle_rad=radians(-1.0))
    _, before, _ = spec.command(999_000, PROFILE, VEHICLE.steering_ratio, 20.0, 0.0)
    _, force, _ = spec.command(1_000_000, PROFILE, VEHICLE.steering_ratio, 20.0, 0.0)
    _, after, _ = spec.command(8_000_000, PROFILE, VEHICLE.steering_ratio, 20.0, 0.0)
    assert before == 0.0
    assert force == after == pytest.approx(-100.0 + PROFILE.mass * G * sin(radians(-1.0)))


def test_moving_driver_target_has_handover_only_after_controller_releases():
    eps = Eps(VEHICLE, actuator_delay_s=0.0, moving_driver_target=True)
    eps.driver_angle = 0.1
    eps.step(1_000, 0.001)
    assert eps.angle > 0.0
    eps.on_request(SteeringRequest(2_000, 0.2, True), 2_000)
    eps.step(2_000, 0.001)
    before = eps.angle
    eps.on_request(SteeringRequest(3_000, 0.2, False), 3_000)
    eps.step(3_000, 0.001)
    assert not eps.controlling and eps.angle == before
    eps.step(1_003_000, 0.001)
    assert eps.angle > before

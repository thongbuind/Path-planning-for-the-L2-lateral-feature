"""Vehicle profiles and bicycle model (Software Qualification Test Specification 4.4)."""

from math import isclose

import pytest

from sim.vehicle.bicycle import Bicycle, BicycleState, steady_cornering
from sim.vehicle.profiles import PROFILES


@pytest.mark.parametrize("name", sorted(PROFILES))
def test_understeer_gradient_same_for_every_profile(name):
    assert isclose(PROFILES[name].understeer_gradient, 0.0029, abs_tol=1e-4)


def test_vp0_vehicle_config_matches_table():
    cfg = PROFILES["VP-0"].vehicle_config()
    assert (cfg.wheelbase, cfg.rear_axle_to_cg, cfg.vehicle_width) == (2.9, 1.45, 1.9)
    assert (cfg.steering_ratio, cfg.max_steering_wheel_rate, cfg.actuator_delay) == (15.0, 6.0, 0.05)


def test_steady_state_yaw_rate():
    # Linear bicycle: r = v * delta / (L + K v^2).
    p = PROFILES["VP-0"]
    car = Bicycle(p, BicycleState(0.0, 0.0, 0.0, 0.0, 0.0))
    v, delta = 25.0, 0.002
    for _ in range(8000):
        car.step(1e-3, delta, v)
    expected = v * delta / (p.wheelbase + p.understeer_gradient * v * v)
    assert isclose(car.state.r, expected, rel_tol=1e-3)
    assert isclose(car.a_y, v * expected, rel_tol=2e-3)


def test_straight_line_without_steering():
    car = Bicycle(PROFILES["VP-0"], BicycleState(0.0, 0.0, 0.0, 0.0, 0.0))
    for _ in range(1000):
        car.step(1e-3, 0.0, 20.0)
    assert isclose(car.state.x, 20.0, rel_tol=1e-9)
    assert car.state.y == 0.0 and car.state.r == 0.0


def test_low_speed_is_kinematic():
    p = PROFILES["VP-0"]
    car = Bicycle(p, BicycleState(0.0, 0.0, 0.0, 0.0, 0.0))
    for _ in range(100):
        car.step(1e-3, 0.1, 2.0)
    assert isclose(car.state.r, 2.0 * 0.1003346720854505 / p.wheelbase, rel_tol=1e-6)  # tan(0.1)


def test_steady_cornering_state_stays_steady():
    p = PROFILES["VP-0"]
    v, kappa = 25.0, 1 / 500.0
    v_y, r, delta = steady_cornering(p, v, kappa)
    assert isclose(delta, (p.wheelbase + p.understeer_gradient * v * v) * kappa, rel_tol=1e-9)
    car = Bicycle(p, BicycleState(0.0, 0.0, 0.0, v_y, r))
    for _ in range(2000):
        car.step(1e-3, delta, v)
    # Steady state of the small-angle model (cos delta = 1): within 1e-3.
    assert isclose(car.state.r, r, rel_tol=1e-3) and isclose(car.state.v_y, v_y, rel_tol=1e-3)

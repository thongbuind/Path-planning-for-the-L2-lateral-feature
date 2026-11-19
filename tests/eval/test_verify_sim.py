"""Tools of the simulator verification (eval/verify_sim.py): the solver converges at order 4, and the
patches that change the step and the vehicle parameters are undone afterwards."""

import pytest

from eval import verify_sim
from sim import harness
from sim.vehicle import profiles


def test_solver_error_is_tiny_and_of_order_four():
    short = (("short step steer", 30.0, 1.0, lambda t: 0.02 if t >= 0.2 else 0.0),)
    row = verify_sim.solver_error(steps_us=(1000, 500), reference_us=125, inputs=short)[0]
    assert row["errors"]["1000"]["position_m"] < 1e-8
    # a_y and yaw rate are not at the round-off floor, so the order of RK4 shows
    assert row["observed_order"]["a_y_m_s2"] == pytest.approx(4.0, abs=0.5)
    assert row["observed_order"]["yaw_rate_rad_s"] == pytest.approx(4.0, abs=0.5)


def test_step_patch_is_undone():
    before = harness.STEP_US, harness.random_phase_us
    with verify_sim._step(250):
        assert harness.STEP_US == 250
        import numpy as np
        draws = [harness.random_phase_us(np.random.default_rng(3), 25_000, 250) for _ in range(2)]
        assert draws[0] == draws[1] and draws[0] % 1000 == 0   # phases on the 1 ms grid
    assert (harness.STEP_US, harness.random_phase_us) == before


def test_parameter_patch_is_undone():
    nominal = (profiles.C_FRONT_PER_2000KG, profiles.C_REAR_PER_2000KG, profiles.YAW_INERTIA_FACTOR)
    with verify_sim._perturbed("c_front", 1.2) as eps:
        assert eps is None and profiles.C_FRONT_PER_2000KG == pytest.approx(nominal[0] * 1.2)
    with verify_sim._perturbed("eps_delay", 0.8) as eps:
        assert eps == pytest.approx(profiles.ACTUATOR_DELAY_S * 0.8)
    with pytest.raises(ValueError):
        with verify_sim._perturbed("mass", 1.2):
            pass
    assert (profiles.C_FRONT_PER_2000KG, profiles.C_REAR_PER_2000KG, profiles.YAW_INERTIA_FACTOR) == nominal

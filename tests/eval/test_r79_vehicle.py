"""a_y and jerk on the vehicle as R79 Annex 8, 2.4 measures them (eval.metrics.r79_vehicle)."""

import numpy as np
import pytest

from eval.metrics import r79_vehicle

RATE = 1000.0  # ground truth of the simulator, 1 ms


def signal(duration_s, fn):
    t = np.arange(0.0, duration_s, 1.0 / RATE)
    return t, fn(t), np.ones_like(t, dtype=bool)


def test_constant_cornering_is_unchanged_and_within_limits():
    t, a, active = signal(20.0, lambda t: np.full_like(t, 2.0))
    out = r79_vehicle(t, a, active)
    assert out["ay_vehicle_r79_max"] == pytest.approx(2.0, abs=1e-6)  # started in steady state
    assert out["jerk_vehicle_r79_max"] == pytest.approx(0.0, abs=1e-6)
    assert out["ay_vehicle_r79_within_limits"]
    assert out["ay_vehicle_r79_limits"] == pytest.approx([2.8, 3.3, 2.0])


def test_long_exceedance_of_sustained_limit_fails():
    t, a, active = signal(20.0, lambda t: np.where((t > 5.0) & (t < 11.0), 3.1, 2.0))
    out = r79_vehicle(t, a, active)
    assert out["ay_vehicle_r79_over_sustained_s"] > 2.0
    assert not out["ay_vehicle_r79_within_limits"]


def test_short_pulse_is_smoothed_by_the_filter():
    # 0.3 s at 3.2 m/s^2 on top of 2.0: the 0.5 Hz filter keeps it well below 2.8.
    t, a, active = signal(20.0, lambda t: np.where((t > 5.0) & (t < 5.3), 3.2, 2.0))
    out = r79_vehicle(t, a, active)
    assert out["ay_vehicle_r79_max"] < 2.8
    assert out["ay_vehicle_r79_within_limits"]


def test_fast_oscillation_is_attenuated():
    t, a, _ = signal(20.0, lambda t: 1.0 * np.sin(2 * np.pi * 5.0 * t))
    out = r79_vehicle(t, a, t > 5.0)  # after the filter's start-up transient
    assert out["ay_vehicle_r79_max"] < 0.01  # 5 Hz is far above the 0.5 Hz cut-off


def test_only_hwa_samples_count():
    t, a, _ = signal(20.0, lambda t: np.where(t < 10.0, 3.5, 1.0))
    active = t > 15.0  # HWA drives only at the end, when a_y has long settled at 1.0
    out = r79_vehicle(t, a, active)
    assert out["ay_vehicle_r79_max"] == pytest.approx(1.0, abs=0.01)
    assert out["ay_vehicle_r79_over_sustained_s"] == 0.0


def test_no_hwa_reports_nothing_and_low_rate_is_rejected():
    t, a, active = signal(5.0, lambda t: np.ones_like(t))
    assert r79_vehicle(t, a, np.zeros_like(active))["ay_vehicle_r79_max"] is None
    with pytest.raises(ValueError):
        r79_vehicle(t[::20], a[::20], active[::20])  # 50 Hz < 100 Hz

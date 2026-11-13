"""Road ground truth (sim/world/road.py)."""

from math import isclose, pi

import pytest

from sim.world.road import Road, Segment


def test_straight_then_arc_geometry():
    radius = 1000.0
    road = Road([Segment("straight", 100.0), Segment("arc", 0.5 * pi * radius, 1 / radius)], 3.5)
    x, y, heading = road.pose_at(road.length)
    assert isclose(heading, 0.5 * pi, abs_tol=1e-3)
    assert isclose(x, 100.0 + radius, abs_tol=0.05)
    assert isclose(y, radius, abs_tol=0.05)


def test_clothoid_heading_is_half_of_arc_with_same_length():
    # Clothoid from 0 to 1/R over L turns by L / (2R).
    road = Road([Segment("clothoid", 100.0, 1 / 500.0)], 3.5)
    assert isclose(road.theta[-1], 100.0 / (2 * 500.0), rel_tol=1e-3)
    assert isclose(road.kappa[-1], 1 / 500.0, rel_tol=1e-9)


@pytest.mark.parametrize("d", [-1.75, 0.0, 0.4, 5.25])
def test_project_recovers_offset(d):
    road = Road([Segment("straight", 50.0), Segment("clothoid", 100.0, 1 / 500.0),
                 Segment("arc", 200.0, 1 / 500.0)], 3.5)
    for s in (20.0, 120.0, 250.0):
        x, y, _ = road.pose_at(s, d)
        proj = road.project(x, y, s_hint=s + 3.0)
        assert isclose(proj.s, s, abs_tol=1e-3)
        assert isclose(proj.d, d, abs_tol=1e-3)


def test_line_offsets_left_to_right():
    assert Road([Segment("straight", 10.0)], 3.5).line_offsets() == (5.25, 1.75, -1.75, -5.25)


def _project_reference(road, x, y, s_hint=None, window_m=20.0):
    """Projection as written with np.clip and np.argmin, before the scalar fast path."""
    import numpy as np
    from math import cos, sin
    from sim.world.road import SAMPLE_STEP_M, LaneProjection
    if s_hint is None:
        lo, hi = 0, len(road.s)
    else:
        lo = int(np.clip((s_hint - window_m) / SAMPLE_STEP_M, 0, len(road.s) - 1))
        hi = int(np.clip((s_hint + window_m) / SAMPLE_STEP_M, 1, len(road.s)))
    dx, dy = x - road.x[lo:hi], y - road.y[lo:hi]
    i = lo + int(np.argmin(dx * dx + dy * dy))
    th = road.theta[i]
    ex, ey = x - road.x[i], y - road.y[i]
    along = ex * cos(th) + ey * sin(th)
    d = -ex * sin(th) + ey * cos(th)
    return LaneProjection(float(road.s[i] + along), float(d), float(th + along * road.kappa[i]), float(road.kappa[i]))


def test_project_is_bit_identical_to_clip_reference():
    import numpy as np
    road = Road([Segment("straight", 50.0), Segment("clothoid", 100.0, 1 / 300.0),
                 Segment("arc", 200.0, 1 / 300.0), Segment("clothoid", 80.0, -1 / 300.0)], 3.5)
    rng = np.random.default_rng(7)
    hints = [None, -1e9, -25.0, -0.0, 0.0, 19.99, road.length, road.length + 30.0, 1e9, float("inf"), float("-inf")]
    for _ in range(400):
        s = float(rng.uniform(-30.0, road.length + 30.0))
        x, y, th = road.pose_at(min(max(s, 0.0), road.length))
        x, y = x + float(rng.normal(0, 3)), y + float(rng.normal(0, 3))
        for hint in hints + [s + float(rng.normal(0, 5)), np.float64(s)]:
            for window in (20.0, 5.0):
                assert road.project(x, y, hint, window) == _project_reference(road, x, y, hint, window)
    with pytest.raises(ValueError):
        road.project(0.0, 0.0, float("nan"))
    with pytest.raises(ValueError):
        _project_reference(road, 0.0, 0.0, float("nan"))

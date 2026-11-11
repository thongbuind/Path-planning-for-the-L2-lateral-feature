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

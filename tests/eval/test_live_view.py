from types import SimpleNamespace

import pytest

from eval import live, loader, metrics
from interfaces import Side
from sim.world.road import Road


def _view(half_car=1.0):
    view = live.LiveView()
    view.half_car = half_car
    return view


def _road(sid, variant):
    scenario = loader.load(sid, variant)
    return Road(list(scenario.segments), scenario.lane_width, scenario.road_layout)


def test_clearance_follows_a_lane_that_widens():
    road = metrics._LaneRelativeRoad(_road("S6b", "d"), [])
    fixed = 0.5 * road.lane_width - 1.0
    largest = 0.0
    for s in range(0, int(road.length), 5):
        x, y, _ = road.pose_at(float(s))
        left, right = _view().clearance(road, x, y, float(s))
        largest = max(largest, abs(left - fixed), abs(right - fixed))
    assert largest > 0.5


def test_clearance_of_a_constant_lane():
    road = _road("S1", "a")
    x, y, _ = road.pose_at(50.0, 0.2)
    left, right = _view().clearance(road, x, y, 50.0)
    assert left == pytest.approx(metrics._boundary_offset(road, Side.LEFT, 50.0) - 0.2 - 1.0, abs=1e-3)
    assert right == pytest.approx(0.2 - metrics._boundary_offset(road, Side.RIGHT, 50.0) - 1.0, abs=1e-3)


@pytest.mark.parametrize("share, controlling, torque, expected", [
    (1.0, True, 2.0, None),
    (1.0, True, 0.0, 1.0),
    (0.0, False, 2.0, 0.0),
])
def test_steering_share_is_never_invented(share, controlling, torque, expected):
    eps = SimpleNamespace(system_steering_share=share, controlling=controlling, driver_torque=torque, driver_angle=0.1)
    assert live.system_share(eps, 0.1) == expected


def test_lane_model_is_placed_at_the_global_capture_time():
    offset_us = 10_000
    h = SimpleNamespace(
        clocks={"camera": SimpleNamespace(to_global=lambda local_us: local_us - offset_us)},
        log=SimpleNamespace(t_us=[0, 10_000, 20_000, 30_000], rear=[(float(i), 0.0, 0.0) for i in range(4)]))
    line = SimpleNamespace(status=0, type=0, view_range_start=0.0, view_range_end=4.0, c0=0.0, c1=0.0, c2=0.0, c3=0.0)
    camera_stamp = 20_000 + offset_us  # Giờ toàn cục lúc chụp là 20 ms; đồng hồ camera đi trước 10 ms.
    msg = SimpleNamespace(header=SimpleNamespace(stamp_us=camera_stamp), lines=[line], road_edges=[])
    first_x = _view().lane_model_points(h, msg)["ls"][0]["pts"][0]
    assert first_x == 2.0

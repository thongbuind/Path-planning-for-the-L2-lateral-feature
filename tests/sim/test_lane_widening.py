"""OpenDRIVE lane widths, camera preview and the PP-SWR-060 oracle."""

import pytest

from eval import loader, openx
from eval.metrics import _widening_dlc, lane_relative
from interfaces import LineStatus, Side
from sim.harness import RunLog
from sim.sensors.lane_camera import CameraPose, LaneCamera
from sim.world.road import Road


def _road(variant):
    scenario = loader.load("S6b", variant)
    return scenario, Road(list(scenario.segments), scenario.lane_width, scenario.road_layout)


@pytest.mark.parametrize("variant, side", [("a", "right"), ("b", "right"), ("c", "left")])
def test_new_lane_starts_at_zero_width(variant, side):
    _, road = _road(variant)
    geometry = road.layout.geometry
    assert geometry.widening_sides(199) == (False, False)
    assert geometry.widening_sides(200) == (False, False)
    assert geometry.widening_sides(250) == (side == "left", side == "right")
    assert geometry.bounds(250) == (-1.75, 1.75)
    section = geometry.section_at(250)
    if variant == "a":
        assert section.bounds(-2, 250) == pytest.approx((-2.5, -1.75))
        assert geometry.lane_index(250, -2.0, 0) == 0  # hard shoulder
    elif variant == "b":
        after = geometry.section_at(380)
        assert after.bounds(-3, 380) == pytest.approx((-7.25, -3.75))
        assert geometry.lane_index(380, -2.0, 0) == 0  # separator


def test_camera_fits_right_boundary_and_reports_local_width():
    _, road = _road("e")
    camera = LaneCamera(road, view_end_m=50.0)
    msg = camera.capture(0, CameraPose(225.0, 0.0, 0.0, 225.0))
    right = msg.lines[2]
    assert right.status == LineStatus.MEASURED
    assert msg.lane_width == pytest.approx(3.5 + 1.5 * (3 * 0.25**2 - 2 * 0.25**3))
    assert right.c0 == pytest.approx(1.75 - msg.lane_width + 0.075, abs=1e-8)
    ahead = 30.0
    y = right.c0 + ahead * (right.c1 + ahead * (right.c2 + ahead * right.c3))
    assert y == pytest.approx(road.layout.geometry.bounds(225.0 + ahead)[0] + 0.075, abs=1e-8)


def test_camera_sees_taper_in_preview_and_reindexes_only_after_crossing():
    _, road = _road("c")
    camera = LaneCamera(road)
    approach = camera.capture(0, CameraPose(180.0, 0.0, 0.0, 180.0))
    assert approach.lines[0].status == LineStatus.MEASURED
    assert approach.lines[0].view_range_start > 20.0
    assert approach.lane_change == Side.NONE
    moved = camera.capture(50_000, CameraPose(250.0, 2.0, 0.0, 250.0))
    assert moved.lane_change == Side.LEFT
    assert moved.lane_width == pytest.approx(1.75)
    assert camera.capture(100_000, CameraPose(255.0, 2.0, 0.0, 255.0)).lane_change == Side.NONE


def test_portable_concrete_preserves_and_scales_width_profiles(tmp_path):
    source = openx.ROOT / "benchmark/scenarios/S6b.xosc"
    overrides = {**openx.anchors(source)["d"], "lane_width_m": 3.85, "direction": -1.0}
    concrete = tmp_path / "curve.xosc"
    openx.concrete(source, concrete, overrides)
    openx.validate(concrete.with_suffix(".xodr"))
    actual = openx.load_scenario(concrete)
    assert actual == openx.load_scenario(source, overrides)
    assert actual.road_layout.geometry.bounds(300) == pytest.approx((-3.575, 1.925))


def test_openx_rejects_negative_width_inside_polynomial():
    source = openx.ROOT / "benchmark/roads/S6ba.xodr"
    root = openx.parse(source)
    first = root.find(".//lane[@id='-2']/width")
    first.set("b", "-0.01")
    with pytest.raises(ValueError, match="negative"):
        openx._read_road(root)


def test_widening_dlc_cannot_be_reset_by_camera_lane_change():
    scenario, road = _road("c")
    log = RunLog(scenario, 1, road, 1.9, 2.9, 0.61, 6.0, 15.0, 0,
                 t_us=[2_000_000, 3_000_000], rear=[(190, 0, 0), (250, 2, 0)],
                 front=[(192.9, 0, 0), (252.9, 2, 0)], lane_index_changes=[(3_000_000, 1)])
    relative = lane_relative(log)
    criterion = _widening_dlc(log, relative.road)
    assert criterion.applicable and not criterion.passed
    assert criterion.value == pytest.approx(1.75 - 0.075 - 2 - 0.95)
    assert criterion.first_fail_s == 3.0


def test_widened_lane_center_and_clearance_use_current_station():
    scenario, road = _road("e")
    log = RunLog(scenario, 1, road, 1.9, 2.9, 0.61, 6.0, 15.0, 0,
                 t_us=[8_000_000], rear=[(300, -0.75, 0)], front=[(302.9, -0.75, 0)])
    relative = lane_relative(log)
    assert relative.road.project(300, -0.75).d == pytest.approx(0.0)
    criterion = _widening_dlc(log, relative.road)
    assert criterion.applicable and criterion.passed
    assert criterion.value == pytest.approx(2.5 - 0.075 - 0.95)

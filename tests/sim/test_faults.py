"""Lane-model fault mechanisms (sim/faults/lane.py) and the fault catalogue files."""

import numpy as np
import pytest

from eval import loader
from interfaces import LineStatus
from sim.faults.lane import LaneFault, LaneFaultInjector
from sim.sensors.lane_camera import CameraPose, LaneCamera
from sim.world.road import Road, Segment


def frame(t_us: int):
    road = Road([Segment("straight", 300.0)], 3.5)
    return LaneCamera(road).capture(t_us, CameraPose(50.0, 0.0, 0.0, 50.0))


def apply(fault: LaneFault, t_us: int, seed: int = 1):
    return LaneFaultInjector((fault,), np.random.default_rng(seed)).apply(frame(t_us))


def test_jump_only_while_active():
    fault = LaneFault("c0_jump", start_s=1.0, duration_s=0.5, value=0.6)
    assert apply(fault, 900_000).lines[1].c0 == pytest.approx(1.75, abs=1e-3)
    assert apply(fault, 1_200_000).lines[1].c0 == pytest.approx(2.35, abs=1e-3)
    assert apply(fault, 1_500_000).lines[1].c0 == pytest.approx(1.75, abs=1e-3)


def test_lose_and_fade_line():
    lost = apply(LaneFault("lose_line", lines=(1,), start_s=0.0), 0)
    assert lost.lines[1].status == LineStatus.LOST and lost.lines[2].status == LineStatus.MEASURED
    fade = LaneFault("fade_line", lines=(1,), start_s=1.0, value=2.0)
    assert apply(fade, 2_000_000).lines[1].confidence == pytest.approx(0.5)
    assert apply(fade, 3_000_000).lines[1].status == LineStatus.LOST


def test_noise_is_seeded_and_reports_its_sigma():
    fault = LaneFault("noise", sigma_c0=0.075, sigma_c1=0.005)
    a, b, c = apply(fault, 0, seed=3), apply(fault, 0, seed=3), apply(fault, 0, seed=4)
    assert a == b and a != c
    assert a.lines[1].variance[0] == pytest.approx(0.075 ** 2)


def test_curvature_error():
    out = apply(LaneFault("c2_error", value=0.0005), 0)
    assert all(line.c2 == pytest.approx(0.0005, abs=1e-9) for line in out.lines)


@pytest.mark.parametrize("fault_id, levels", [("F01", "abc"), ("F02", "abcde"), ("F04", "abc"),
                                              ("F06", "abcde")])
def test_catalogue_loads(fault_id, levels):
    for level in levels:
        scenario = loader.with_fault(loader.load("S1", "a"), fault_id, level)
        assert scenario.name == f"S1a_{fault_id}{level}" and len(scenario.lane_faults) == 1


def test_view_short_refits_on_the_shorter_window():
    road = Road([Segment("straight", 300.0)], 3.5)
    injector = LaneFaultInjector((LaneFault("view_short", start_s=1.0, duration_s=0.5, lines=(2,), value=20.0),),
                                 np.random.default_rng(1))
    assert injector.view_limits(900_000) == (None,) * 4
    limits = injector.view_limits(1_200_000)
    assert limits == (None, None, 20.0, None)
    lane = LaneCamera(road).capture(1_200_000, CameraPose(50.0, 0.0, 0.0, 50.0), limits)
    assert lane.lines[2].view_range_end <= 20.0 + 1e-9 and lane.lines[1].view_range_end > 70.0


def test_view_flicker_limits_every_other_frame():
    injector = LaneFaultInjector((LaneFault("view_flicker", value=30.0),), np.random.default_rng(1))
    assert injector.view_limits(0) == (None,) * 4
    assert injector.view_limits(50_000) == (30.0,) * 4


def test_view_extend_reports_a_longer_range_with_the_same_polynomial():
    base = frame(1_000_000)
    lane = apply(LaneFault("view_extend", start_s=1.0, value=126.0), 1_000_000)
    assert lane.lines[1].view_range_end == 126.0
    assert lane.lines[1].c2 == base.lines[1].c2

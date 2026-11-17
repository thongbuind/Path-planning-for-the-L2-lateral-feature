"""Behaviour checksum (eval.checksum; SIM-REQ-040): same run, same checksum; any bit, other one.

Shortened S1-like run as in test_slice_s1. Needs build/planner/libpp_planner; skipped otherwise.
"""

import math
from dataclasses import replace

import pytest

from adapters.sil.sil_planner import SilPlanner, library_path
from eval import checksum
from sim.harness import Harness
from sim.scenario import Scenario
from sim.world.road import Segment

pytestmark = pytest.mark.skipif(not library_path().exists(),
                                reason=f"planner library not built: {library_path()}")

SHORT = Scenario(
    name="S1-short",
    segments=(Segment("straight", 150.0), Segment("clothoid", 100.0, 1 / 500.0),
              Segment("arc", 300.0, 1 / 500.0)),
    lane_width=3.5,
    speed_mps=25.0,
    duration_s=10.0,
)


@pytest.fixture(scope="module")
def log():
    return Harness(SHORT, SilPlanner, seed=3).run()


def test_same_case_same_seed_same_checksum(log):
    again = Harness(SHORT, SilPlanner, seed=3).run()
    assert checksum.behavior_checksum(again) == checksum.behavior_checksum(log)


def test_compute_time_and_inputs_are_not_behaviour(log):
    before = checksum.behavior_checksum(log)
    cycles = list(log.cycles)
    cycles[3] = replace(cycles[3], compute_ns=cycles[3].compute_ns + 999)
    changed = replace(log, cycles=cycles, scenario=replace(log.scenario, name="renamed"))
    assert checksum.behavior_checksum(changed) == before


def test_one_bit_of_one_trajectory_point_changes_the_checksum(log):
    k = next(i for i, c in enumerate(log.cycles) if c.trajectory is not None)
    traj = log.cycles[k].trajectory
    point = traj.points[10]
    moved = replace(point, curvature=math.nextafter(point.curvature, 1.0))
    cycles = list(log.cycles)
    cycles[k] = replace(cycles[k], trajectory=replace(traj, points=traj.points[:10] + (moved,) + traj.points[11:]))
    assert checksum.behavior_checksum(replace(log, cycles=cycles)) != checksum.behavior_checksum(log)


def test_one_bit_of_ground_truth_changes_the_checksum(log):
    a_y = list(log.a_y)
    a_y[500] = math.nextafter(a_y[500], math.inf)
    assert checksum.behavior_checksum(replace(log, a_y=a_y)) != checksum.behavior_checksum(log)


def test_another_seed_gives_another_checksum(log):
    other = Harness(SHORT, SilPlanner, seed=4).run()
    assert checksum.behavior_checksum(other) != checksum.behavior_checksum(log)

"""Generated interface code is up to date and checks only structure."""

import subprocess
import sys
from pathlib import Path

import pytest

import interfaces as I

ROOT = Path(__file__).resolve().parents[2]


def test_generated_files_match_schema():
    result = subprocess.run([sys.executable, str(ROOT / "interfaces" / "gen.py"), "--check"],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_yaml_off_is_an_enum_value_not_a_boolean():
    assert I.RequestState.OFF == 0 and I.RequestState.REQUEST == 3
    assert I.LongitudinalMode.OFF == 0 and I.LongitudinalMode.CURVE_LIMIT == 3


def test_fixed_array_sizes_follow_the_icd():
    assert (I.TRAJECTORY_POINTS, I.LANE_LINES, I.ROAD_EDGES, I.MAX_OBJECTS, I.FUNCTIONS,
            I.LONGITUDINAL_PLAN_POINTS) == (31, 4, 2, 32, 3, 31)


def _point():
    return I.TrajectoryPoint(0.0, I.Pose2D(0.0, 0.0, 0.0), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)


def test_array_length_is_checked():
    header = I.Header(0, 0, True, I.FrameId.BASE_LINK)
    I.Trajectory(header, [_point()] * 31, 3.0)
    with pytest.raises(ValueError):
        I.Trajectory(header, [_point()] * 30, 3.0)


def test_list_is_stored_as_tuple():
    header = I.Header(0, 0, True, I.FrameId.BASE_LINK)
    assert isinstance(I.Trajectory(header, [_point()] * 31, 3.0).points, tuple)


@pytest.mark.parametrize("counter", [-1, 256, True, 1.0])
def test_unsigned_width_is_checked(counter):
    with pytest.raises(ValueError):
        I.Header(0, counter, True, I.FrameId.BASE_LINK)


def test_enum_value_is_checked_and_coerced():
    status = I.PathStatus(I.BasicHeader(0, 0, True), True, 2, 1, 2, False, False)
    assert status.active_function is I.ActiveFunction.LKA
    assert status.lka_phase is I.InterventionPhase.ACTIVE
    assert status.elk_phase is I.InterventionPhase.COMPLETED
    with pytest.raises(ValueError):
        I.PathStatus(I.BasicHeader(0, 0, True), False, 9, 0, 0, False, False)


def test_value_ranges_are_left_to_the_receiver():
    """A too wide vehicle is representable, so tests can check that the planner rejects it."""
    config = I.VehicleConfig(2.9, 1.45, 3.0, 15.0, 0.61, 6.0, 0.05)
    assert config.vehicle_width > I.MAX_VEHICLE_WIDTH_M


def test_planner_inputs_default_to_not_received():
    inputs = I.PlannerInputs(t0_us=25_000)
    assert inputs.lane_model is None and inputs.longitudinal_plan is None

"""Call contract of the two C planners through the SIL adapter (Interface Control Document section 4).

Needs build/planner/libpp_lcc and libpp_lkaelk; skipped otherwise.
"""

import pytest

import interfaces as I
from adapters.sil.sil_planner import LCC, LKAELK, SilPlanner, library_path, load_library

pytestmark = pytest.mark.skipif(not (library_path("pp_lcc").exists() and library_path("pp_lkaelk").exists()),
                                reason="planner libraries not built: build/planner/libpp_lcc, libpp_lkaelk")

VP0 = I.VehicleConfig(2.9, 1.45, 1.9, 15.0, 0.61, 6.0, 0.05)  # Software Qualification Test Specification 4.4

# family, inputs type, name of the status in the outputs
PLANNERS = [pytest.param(LCC, I.LccInputs, "lcc_status", id="lcc"),
            pytest.param(LKAELK, I.LkaElkInputs, "intervention_status", id="lkaelk")]


def no_motion(_request):
    return I.EgoMotionResponse(True, 0.0, 0.0, 0.0)


def make(family, config):
    return SilPlanner(config, load_library(library_path(family.library), family), family)


@pytest.mark.parametrize("family, inputs, status", PLANNERS)
def test_init_with_valid_vehicle_config(family, inputs, status):
    assert make(family, VP0).init_result is I.InitResult.OK


@pytest.mark.parametrize("config", [
    None,                                                     # missing (PP-SWR-146)
    I.VehicleConfig(2.9, 1.45, 2.51, 15.0, 0.61, 6.0, 0.05),  # wider than 2.5 m (PP-ASM-016)
    I.VehicleConfig(0.0, 0.0, 1.9, 15.0, 0.61, 6.0, 0.05),    # no wheelbase
    I.VehicleConfig(2.9, 3.0, 1.9, 15.0, 0.61, 6.0, 0.05),    # centre of gravity outside wheelbase
    I.VehicleConfig(2.9, 1.45, 1.9, float("nan"), 0.61, 6.0, 0.05),
])
@pytest.mark.parametrize("family, inputs, status", PLANNERS)
def test_bad_vehicle_config_is_rejected(family, inputs, status, config):
    planner = make(family, config)
    assert planner.init_result is I.InitResult.BAD_VEHICLE_CONFIG
    out = planner.step(inputs(t0_us=25_000), no_motion)
    assert out.trajectory is None                  # PP-SWR-146
    assert getattr(out, status) is not None        # PP-SWR-010
    assert not getattr(out, status).path_valid


@pytest.mark.parametrize("family, inputs, status", PLANNERS)
def test_status_every_cycle_with_counter_and_stamp(family, inputs, status):
    planner = make(family, VP0)
    counters = []
    for k in range(1, 260):
        out = planner.step(inputs(t0_us=k * I.PLANNER_PERIOD_US), no_motion)
        assert getattr(out, status).header.stamp_us == k * I.PLANNER_PERIOD_US
        counters.append(getattr(out, status).header.counter)
        assert out.trajectory.planner_id == (I.PlannerId.LCC if family is LCC else I.PlannerId.LKA_ELK)  # PP-SWR-019
    assert counters[:3] == [0, 1, 2]
    assert counters[256] == 0  # wraps at 256 (Interface Control Document section 4)


@pytest.mark.parametrize("family, inputs, status", PLANNERS)
def test_inputs_cross_into_c(family, inputs, status):
    line = I.LaneLine(0.0, 0.0, 0.0, 0.0, (0.0,) * 4, 0.0, 60.0, 0.9,
                      I.LineType.DASHED, True, I.LineStatus.MEASURED, 0.0)
    edge = I.RoadEdge(0.0, 0.0, 0.0, 0.0, (0.0,) * 4, 0.0, 60.0, 0.9,
                      I.RoadEdgeType.CURB, I.LineStatus.MEASURED, 0.0)
    lane = I.LaneModel(I.Header(10, 0, True, I.FrameId.BASE_LINK), (line,) * 4, (edge,) * 2,
                       3.5, I.LaneWidthSource.MEASURED, I.Side.NONE)
    out = make(family, VP0).step(inputs(t0_us=25_000, lane_model=I.Received(lane, rx_us=20_000)), no_motion)
    assert getattr(out, status) is not None


def test_lka_elk_trajectory_is_not_valid_without_a_request():
    """PP-SWR-180: LKA/ELK sends its Trajectory but it is valid only while it intervenes."""
    out = make(LKAELK, VP0).step(I.LkaElkInputs(t0_us=25_000), no_motion)
    assert out.trajectory is not None and not out.trajectory.header.valid
    assert out.intervention_status.active_function is I.InterventionFunction.NONE


def test_lcc_reports_no_mode_without_inputs():
    out = make(LCC, VP0).step(I.LccInputs(t0_us=25_000), no_motion)
    assert out.lcc_status.lcc_mode is I.LccMode.NONE and not out.lcc_status.path_valid   # PP-SWR-043
    assert out.lateral_limits is not None

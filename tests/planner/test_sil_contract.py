"""Call contract of the C planner through the SIL adapter (Interface Control Document section 4).

Needs build/planner/libpp_planner; skipped otherwise.
"""

import pytest

import interfaces as I
from adapters.sil.sil_planner import SilPlanner, library_path

pytestmark = pytest.mark.skipif(not library_path().exists(),
                                reason=f"planner library not built: {library_path()}")

VP0 = I.VehicleConfig(2.9, 1.45, 1.9, 15.0, 0.61, 6.0, 0.05)  # Software Qualification Test Specification 4.4


def no_motion(_request):
    return I.EgoMotionResponse(True, 0.0, 0.0, 0.0)


def test_init_with_valid_vehicle_config():
    assert SilPlanner(VP0).init_result is I.InitResult.OK


@pytest.mark.parametrize("config", [
    None,                                                     # missing (PP-SWR-146)
    I.VehicleConfig(2.9, 1.45, 2.51, 15.0, 0.61, 6.0, 0.05),  # wider than 2.5 m (PP-ASM-016)
    I.VehicleConfig(0.0, 0.0, 1.9, 15.0, 0.61, 6.0, 0.05),    # no wheelbase
    I.VehicleConfig(2.9, 3.0, 1.9, 15.0, 0.61, 6.0, 0.05),    # centre of gravity outside wheelbase
    I.VehicleConfig(2.9, 1.45, 1.9, float("nan"), 0.61, 6.0, 0.05),
])
def test_bad_vehicle_config_is_rejected(config):
    planner = SilPlanner(config)
    assert planner.init_result is I.InitResult.BAD_VEHICLE_CONFIG
    out = planner.step(I.PlannerInputs(t0_us=25_000), no_motion)
    assert out.trajectory is None                  # PP-SWR-146
    assert out.path_status is not None             # PP-SWR-010
    assert not out.path_status.path_valid


def test_path_status_every_cycle_with_counter_and_stamp():
    planner = SilPlanner(VP0)
    counters = []
    for k in range(1, 260):
        out = planner.step(I.PlannerInputs(t0_us=k * I.PLANNER_PERIOD_US), no_motion)
        assert out.path_status.header.stamp_us == k * I.PLANNER_PERIOD_US
        counters.append(out.path_status.header.counter)
    assert counters[:3] == [0, 1, 2]
    assert counters[256] == 0  # wraps at 256 (Interface Control Document section 4)


def test_inputs_cross_into_c():
    line = I.LaneLine(0.0, 0.0, 0.0, 0.0, (0.0,) * 4, 0.0, 60.0, 0.9,
                      I.LineType.DASHED, True, I.LineStatus.MEASURED, 0.0)
    edge = I.RoadEdge(0.0, 0.0, 0.0, 0.0, (0.0,) * 4, 0.0, 60.0, 0.9,
                      I.RoadEdgeType.CURB, I.LineStatus.MEASURED, 0.0)
    lane = I.LaneModel(I.Header(10, 0, True, I.FrameId.BASE_LINK), (line,) * 4, (edge,) * 2,
                       3.5, I.LaneWidthSource.MEASURED, I.Side.NONE)
    out = SilPlanner(VP0).step(
        I.PlannerInputs(t0_us=25_000, lane_model=I.Received(lane, rx_us=20_000)), no_motion)
    assert out.path_status is not None

import pytest

from interfaces import (
    ActiveFunction, BasicHeader, InitResult, InterventionPhase, PathStatus, PlannerOutputs,
    RequestState,
)
from sim.faults.lane import LaneFault
from sim.harness import Harness
from sim.scenario import Scenario
from sim.stand_ins.driver import DriverSpec
from sim.world.road import Segment


class _ReportsValidPath:
    init_result = InitResult.OK

    def __init__(self, _config):
        self.counter = 0

    def step(self, inputs, _ego_motion):
        header = BasicHeader(inputs.t0_us, self.counter, True)
        self.counter += 1
        status = PathStatus(header, True, ActiveFunction.NONE,
                            InterventionPhase.NONE, InterventionPhase.NONE, False, False)
        return PlannerOutputs(path_status=status)


@pytest.mark.parametrize("mode, expect_request", [("A", False), ("B", True)])
def test_harness_publishes_selected_mode_and_logs_actual_planner_input(mode, expect_request):
    scenario = Scenario(
        "stand-in unit fixture", (Segment("straight", 200),), 3.5, 20.0,
        duration_s=0.8, start_offset_m=0.45, start_heading_rad=0.02,
        hwa_request_s=None, adas_mode=mode, lka_enabled=True,
        lane_faults=(LaneFault("lose_line"),),
    )
    log = Harness(scenario, _ReportsValidPath, seed=1).run()
    assert not any(sample.measured_requests.requests[1].state == RequestState.REQUEST for sample in log.adas)
    assert any(sample.ideal_requests.requests[1].state == RequestState.REQUEST for sample in log.adas)
    requested = any(c.function_requests is not None
                    and c.function_requests.message.requests[1].state == RequestState.REQUEST for c in log.cycles)
    assert requested == expect_request
    assert len(log.rear_v_y) == len(log.yaw_rate) == len(log.t_us)


def test_driver_starts_parallel_to_offset_curve_before_departure():
    scenario = Scenario(
        "curve entry unit fixture", (Segment("arc", 200, 1 / 250),), 3.5, 25.0,
        duration_s=.5, start_offset_m=.25, hwa_request_s=None,
        driver=DriverSpec(steer_start_s=2.0, steer_release_s=3.0, drift_curvature=-1 / 1200),
    )
    log = Harness(scenario, _ReportsValidPath, seed=1).run()
    assert all(abs(log.road.project(x, y).d - scenario.start_offset_m) < .005
               for x, y, _ in log.rear)

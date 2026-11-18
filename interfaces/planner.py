"""Behaviour contract of the path planners, Python side.

Interface Control Document section 4, "Contract gọi hàm của planner". The C side is
interfaces/c/pp_planner.h. There are two planners (PP-ADR-016): the LCC planner and the
LKA/ELK planner. Any pair that meets this contract plugs into sim/harness.py; the SIL adapter
(adapters/sil) wraps the two C libraries behind it.

Handwritten: the data types it uses are generated from interfaces/schema.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from interfaces.inputs.ego_motion import EgoMotionRequest, EgoMotionResponse
from interfaces.inputs.vehicle_config import VehicleConfig
from interfaces.planner_io import InitResult, LccInputs, LccOutputs, LkaElkInputs, LkaElkOutputs

# Interface Control Document 5.5: called by the planner, answered in the same cycle.
EgoMotionQuery = Callable[[EgoMotionRequest], EgoMotionResponse]


class LccPlanner(Protocol):
    """The LCC planner: one instance, created once at start-up."""

    @property
    def init_result(self) -> InitResult:
        """Result of initialisation. Not OK means no Trajectory is ever sent (PP-SWR-146)."""
        ...

    def step(self, inputs: LccInputs, ego_motion: EgoMotionQuery) -> LccOutputs:
        """Run one cycle at inputs.t0_us; called every PLANNER_PERIOD_US."""
        ...


class LkaElkPlanner(Protocol):
    """The LKA/ELK planner: one instance, created once at start-up."""

    @property
    def init_result(self) -> InitResult:
        ...

    def step(self, inputs: LkaElkInputs, ego_motion: EgoMotionQuery) -> LkaElkOutputs:
        ...


@dataclass(frozen=True, slots=True)
class PlannerSet:
    """The two planners of one run. They share no state at run time (PP-ADR-016)."""

    lcc: LccPlanner | None
    lka_elk: LkaElkPlanner | None


# Creates both planners from VehicleConfig, or None when VehicleConfig is missing.
PlannerFactory = Callable[[VehicleConfig | None], PlannerSet]

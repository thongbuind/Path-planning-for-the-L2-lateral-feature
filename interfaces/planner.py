"""Behaviour contract of the path planner, Python side.

Interface Control Document section 4, "Contract gọi hàm của planner". The C side is
interfaces/c/pp_planner.h. Any planner that meets this contract plugs into sim/harness.py;
the SIL adapter (adapters/sil) wraps the C library behind it.

Handwritten: the data types it uses are generated from interfaces/schema.
"""

from collections.abc import Callable
from typing import Protocol

from interfaces.inputs.ego_motion import EgoMotionRequest, EgoMotionResponse
from interfaces.inputs.vehicle_config import VehicleConfig
from interfaces.planner_io import InitResult, PlannerInputs, PlannerOutputs

# Interface Control Document 5.5: called by the planner, answered in the same cycle.
EgoMotionQuery = Callable[[EgoMotionRequest], EgoMotionResponse]


class Planner(Protocol):
    """One planner instance, created once at start-up."""

    @property
    def init_result(self) -> InitResult:
        """Result of initialisation. Not OK means no Trajectory is ever sent (PP-SWR-146)."""
        ...

    def step(self, inputs: PlannerInputs, ego_motion: EgoMotionQuery) -> PlannerOutputs:
        """Run one cycle at inputs.t0_us; called every PLANNER_PERIOD_US."""
        ...


# Creates a planner from VehicleConfig, or None when VehicleConfig is missing.
PlannerFactory = Callable[[VehicleConfig | None], Planner]

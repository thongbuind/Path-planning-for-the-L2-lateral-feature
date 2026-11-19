"""Arbitrator stand-in (PP-ASM-022): picks the Trajectory of one of the two planners.

The arbitrator belongs to the system, not to the path planner (Software Requirements
Specification PP-ASM-022). The rule is fixed for every planner under test: the LKA/ELK
planner's Trajectory when its `active_function` is not NONE and `Trajectory.header.valid`
is true, otherwise the LCC planner's. Lateral Controller drives along the chosen Trajectory
only while the function that owns it is driving (LCC with `lcc_mode` not NONE, LKA, ELK).

`SystemStatus` is what an observer of the vehicle sees: the chosen path and the function that
drives it. It is not a planner output and has no interface of the planner behind it.
"""

from dataclasses import dataclass
from enum import IntEnum

from interfaces import (
    BasicHeader,
    InterventionFunction,
    InterventionPhase,
    LccMode,
    LccOutputs,
    LkaElkOutputs,
    PlannerId,
    Trajectory,
)


class ActiveFunction(IntEnum):
    """The function that drives the car; values match FunctionRequests.requests[] + 1."""

    NONE = 0
    LCC = 1
    LKA = 2
    ELK = 3


@dataclass(frozen=True, slots=True)
class SystemStatus:
    header: BasicHeader
    path_valid: bool  # The chosen path is usable
    active_function: ActiveFunction
    lka_phase: InterventionPhase
    elk_phase: InterventionPhase
    lateral_limit_reached: bool
    lane_too_narrow: bool
    lcc_mode: LccMode = LccMode.NONE
    chosen: PlannerId = PlannerId.LCC  # Planner whose Trajectory was chosen


PATH_STATUS_TIMEOUT_US = 75_000  # As LccStatus and InterventionStatus (Interface Control Document 6.2, 6.3)

_INTERVENTION = {InterventionFunction.LKA: ActiveFunction.LKA, InterventionFunction.ELK: ActiveFunction.ELK}


class Arbitrator:
    def __init__(self) -> None:
        self._counter = 0

    def choose(self, now_us: int, lcc: LccOutputs | None,
               lka_elk: LkaElkOutputs | None) -> tuple[Trajectory | None, SystemStatus]:
        lcc_traj = lcc.trajectory if lcc is not None else None
        lcc_status = lcc.lcc_status if lcc is not None else None
        ka_traj = lka_elk.trajectory if lka_elk is not None else None
        ka_status = lka_elk.intervention_status if lka_elk is not None else None
        phases = (ka_status.lka_phase, ka_status.elk_phase) if ka_status is not None else (
            InterventionPhase.NONE, InterventionPhase.NONE)
        ka_drives = (ka_status is not None and ka_status.active_function != InterventionFunction.NONE
                     and ka_traj is not None and ka_traj.header.valid)
        if ka_drives:
            trajectory, chosen = ka_traj, PlannerId.LKA_ELK
            function = _INTERVENTION[ka_status.active_function]
            path_valid = True
            limit = ka_status.lateral_limit_reached or (lcc_status is not None and lcc_status.lateral_limit_reached)
        else:
            trajectory, chosen = lcc_traj, PlannerId.LCC
            path_valid = lcc_traj is not None and lcc_traj.header.valid
            mode = lcc_status.lcc_mode if lcc_status is not None else LccMode.NONE
            function = ActiveFunction.LCC if path_valid and mode != LccMode.NONE else ActiveFunction.NONE
            limit = lcc_status is not None and lcc_status.lateral_limit_reached
        status = SystemStatus(
            BasicHeader(now_us, self._counter % 256, True), path_valid, function, phases[0], phases[1],
            bool(limit), bool(lcc_status is not None and lcc_status.lane_too_narrow),
            lcc_status.lcc_mode if lcc_status is not None else LccMode.NONE, chosen)
        self._counter += 1
        return trajectory, status

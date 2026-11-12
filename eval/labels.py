"""Labels of a concrete case (Software Qualification Test Specification 5.3).

Expected outcome: written in the scenario (`pp:expected_outcome`), derived by the test side
from the Software Requirements Specification and the ADAS Function Specification. A fault on
a host keeps the stricter of the two.

Difficulty: derived here from the concrete values, the highest level that applies.
  L5  outside the ODD or the operating range of the function (look-ahead below t_view_hwa)
  L4  more than one fault
  L3  one fault, or a simulator setting swept away from the scenario (Q1 to Q4)
  L2  the road needs more lateral acceleration than aysmax while HWA is requested
  L1  a value on an end of the ODD or of the function range: lane width, speed, vehicle width
  L0  otherwise
"""

from sim.scenario import Scenario
from sim.stand_ins.hwa_view_gate import HwaViewCalibration
from sim.vehicle.profiles import PROFILES

OUTCOMES = ("drive", "drive_limited", "refuse")
LEVELS = ("L0", "L1", "L2", "L3", "L4", "L5")

AYSMAX = 2.5  # [m/s^2] PP-SWR-001
LANE_WIDTH_M = (2.5, 5.5)  # Software Requirements Specification 5 (PP-ASM-015)
VEHICLE_WIDTH_MAX_M = 2.5  # Software Requirements Specification 5 (PP-ASM-016)
HWA_SPEED_MPS = (10 / 3.6, 130 / 3.6)  # ADAS Function Specification 7
LKA_ELK_SPEED_MPS = (70 / 3.6, 130 / 3.6)  # ADAS Function Specification 7: activation from 70 km/h


def stricter(a: str | None, b: str | None) -> str | None:
    known = [x for x in (a, b) if x]
    return max(known, key=OUTCOMES.index) if known else None


def _at(value: float, end: float) -> bool:
    return abs(value - end) <= 1e-6 * max(1.0, abs(end))


def difficulty(scenario: Scenario, swept: bool = False) -> str:
    hwa = scenario.hwa_request_s is not None
    intervention = scenario.lka_enabled or scenario.elk_enabled
    speed = scenario.speed_mps
    levels = ["L0"]
    view_gate = HwaViewCalibration()
    if hwa and scenario.hwa_view_gate and speed > 0 and scenario.camera_view_m / speed < view_gate.t_view_hwa:
        levels.append("L5")
    faults = fault_count(scenario)
    if faults > 1:
        levels.append("L4")
    elif faults == 1 or swept:
        levels.append("L3")
    if hwa and speed ** 2 * max((abs(s.curvature_end) for s in scenario.segments), default=0.0) > AYSMAX + 1e-9:
        levels.append("L2")
    ends = [*LANE_WIDTH_M]
    boundary = any(_at(scenario.lane_width, e) for e in ends)
    boundary |= _at(PROFILES[scenario.profile].width_with_mirrors, VEHICLE_WIDTH_MAX_M)
    if hwa:
        boundary |= any(_at(speed, e) for e in HWA_SPEED_MPS)
    if intervention:
        boundary |= any(_at(speed, e) for e in LKA_ELK_SPEED_MPS)
    if boundary:
        levels.append("L1")
    return max(levels, key=LEVELS.index)


FAULT_FIELDS = ("lane_faults", "channel_faults", "sensor_faults", "clock_faults", "ego_motion_faults")


def fault_count(scenario: Scenario) -> int:
    """Fault definitions of section 6 in the case: those the case names (pp:faults), else one
    when it holds any fault command or the CAN rounding of F18. A definition may hold several
    commands (F07: yaw rate and a_y), so commands are not counted."""
    named = scenario.notes.get("faults")
    if named:
        return len(named)
    return int(any(getattr(scenario, f) for f in FAULT_FIELDS) or (scenario.can_bus and not scenario.realism))


def of(scenario: Scenario, swept: bool = False) -> dict:
    return {"difficulty": difficulty(scenario, swept), "expected": scenario.notes.get("expected_outcome")}


def scope_extra(case_labels: dict) -> set[str]:
    """Software Qualification Test Specification 5.3: over-refusal is judged on PP-SWR-030 in
    every case labelled drive or drive_limited."""
    return {"PP-SWR-030"} if case_labels.get("expected") in ("drive", "drive_limited") else set()

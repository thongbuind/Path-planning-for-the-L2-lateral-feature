"""Scenario settings the simulator needs. The benchmark files are read by eval/ and
turned into this; sim/ never reads the benchmark itself (README import rules).
"""

from dataclasses import dataclass, field

from sim.faults.lane import LaneFault
from sim.world.road import Segment


@dataclass(frozen=True, slots=True)
class Scenario:
    name: str
    segments: tuple[Segment, ...]
    lane_width: float  # [m]
    speed_mps: float  # Held by the scenario until the stand-in ACC exists
    profile: str = "VP-0"
    duration_s: float = 30.0
    hwa_request_s: float = 1.0  # HWA goes to REQUEST at this time
    start_s: float = 10.0  # [m] where the car starts on the road
    start_offset_m: float = 0.0  # [m] lateral offset from the lane centre, left positive
    start_heading_rad: float = 0.0  # Relative to the lane
    lane_faults: tuple[LaneFault, ...] = ()  # Software Qualification Test Specification 6
    # Hold offset and heading until HWA starts driving (S2; test specification section 5)
    hold_until_hwa: bool = False
    # Longitudinal side (Software Qualification Test Specification 4.4, 4.7): 'off' holds
    # speed_mps; 'ignore_limits' runs the stand-in ACC without LateralLimits; 'on' reads them.
    # speed_mps is the ACC set speed when the ACC runs.
    acc: str = "off"
    notes: dict = field(default_factory=dict)

"""Scenario settings the simulator needs. The benchmark files are read by eval/ and
turned into this; sim/ never reads the benchmark itself (README import rules).
"""

from dataclasses import dataclass, field
from typing import Literal

from sim.faults.lane import LaneFault
from sim.stand_ins.driver import DriverSpec
from sim.stand_ins.scripted import RequestEvent
from sim.world.traffic import TrafficSpec
from sim.world.road import RoadLayout, Segment


@dataclass(frozen=True, slots=True)
class Scenario:
    name: str
    segments: tuple[Segment, ...]
    lane_width: float  # [m]
    speed_mps: float  # Held by the scenario until the stand-in ACC exists
    profile: str = "VP-0"
    duration_s: float = 30.0
    hwa_request_s: float | None = 1.0  # Time of HWA REQUEST, or None when disabled
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
    # Range the lane camera sees [m] (Software Qualification Test Specification 4.5: 0-80 m).
    # Shorter for S1b d, where a crest hides the curve; swept by the view range sweep (Q4).
    camera_view_m: float = 80.0
    camera_view_start_m: float = 0.0  # [m] in base_link; the hood hides the road closer than this
    # Scripted HWA leaves REQUEST when the preview stays too short (ADAS Function Specification 7; F22)
    hwa_view_gate: bool = False
    # Delays of Software Qualification Test Specification 6.1 (Q1 to Q3). Defaults: 4.5, PP-ASM-007.
    camera_latency_ms: float = 100.0  # Lane model and ObjectList, capture to send
    camera_jitter_ms: float = 0.0  # Uniform +/- on that delay
    yaw_filter_delay_ms: float = 0.0  # Yaw rate as of this long ago, stamped now (Q2)
    function_requests_latency_ms: float = 1.0  # FunctionRequests to the planner (Q3)
    traffic: tuple[TrafficSpec, ...] = ()  # Other vehicles (section 4.5, 5)
    notes: dict = field(default_factory=dict)
    road_layout: RoadLayout | None = None
    driver: DriverSpec | None = None
    adas_mode: Literal["scripted", "A", "B"] = "scripted"
    lka_enabled: bool = False
    elk_enabled: bool = False
    request_events: tuple[RequestEvent, ...] = ()

    def __post_init__(self) -> None:
        if self.adas_mode not in ("scripted", "A", "B"):
            raise ValueError("invalid ADAS mode")
        if self.request_events and self.adas_mode != "scripted":
            raise ValueError("request events require scripted ADAS mode")

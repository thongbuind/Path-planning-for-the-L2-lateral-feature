from dataclasses import dataclass, field
from typing import Literal

from sim.faults.channel import ChannelFault
from sim.faults.ego_motion import EgoMotionFault
from sim.faults.lane import LaneFault
from sim.faults.sensor import SensorFault
from sim.runtime.clock import ClockFault
from sim.stand_ins.driver import DriverSpec
from sim.stand_ins.scripted import RequestEvent
from sim.world.traffic import TrafficSpec
from sim.world.road import RoadLayout, Segment


@dataclass(frozen=True, slots=True)
class Scenario:
    name: str
    segments: tuple[Segment, ...]
    lane_width: float
    speed_mps: float
    profile: str = "VP-0"
    duration_s: float = 30.0
    hwa_request_s: float | None = 1.0
    start_s: float = 10.0
    start_offset_m: float = 0.0  # [m] Lệch khỏi tâm làn, dương về trái.
    start_heading_rad: float = 0.0
    lane_faults: tuple[LaneFault, ...] = ()
    # S2 giữ offset và hướng ban đầu cho tới lúc HWA bắt đầu lái.
    hold_until_hwa: bool = False
    # Khi có ACC, speed_mps là tốc độ đặt. ignore_limits vẫn chạy ACC nhưng không đọc
    # LateralLimits.
    acc: str = "off"
    camera_view_m: float = 80.0
    camera_view_start_m: float = 0.0
    hwa_view_gate: bool = False
    camera_latency_ms: float = 100.0  # Thời gian từ lúc chụp đến lúc phát LaneModel và ObjectList.
    camera_jitter_ms: float = 0.0
    yaw_filter_delay_ms: float = 0.0  # Q2 lấy yaw rate ở thời điểm cũ, nhưng dùng stamp hiện tại.
    function_requests_latency_ms: float = 1.0
    traffic: tuple[TrafficSpec, ...] = ()
    notes: dict = field(default_factory=dict)
    road_layout: RoadLayout | None = None
    driver: DriverSpec | None = None
    adas_mode: Literal["scripted", "A", "B"] = "scripted"
    lka_enabled: bool = False
    elk_enabled: bool = False
    request_events: tuple[RequestEvent, ...] = ()
    channel_faults: tuple[ChannelFault, ...] = ()
    sensor_faults: tuple[SensorFault, ...] = ()
    clock_faults: tuple[ClockFault, ...] = ()
    ego_motion_faults: tuple[EgoMotionFault, ...] = ()
    can_bus: bool = False
    realism: bool = False
    loop: Literal["closed", "open"] = "closed"
    road_mu: float = 1.0
    eps_delay_s: float | None = None  # Chỉ đổi độ trễ EPS thật của ca. VehicleConfig gửi planner giữ giá trị danh định.
    perception_noise_scale: float = 1.0
    object_list_on_empty_road: bool = False

    def __post_init__(self) -> None:
        if self.adas_mode not in ("scripted", "A", "B"):
            raise ValueError("invalid ADAS mode")
        if self.request_events and self.adas_mode != "scripted":
            raise ValueError("request events require scripted ADAS mode")
        if self.loop not in ("closed", "open"):
            raise ValueError("loop must be closed or open")

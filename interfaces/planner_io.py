"""Sinh từ interfaces/gen.py và interfaces/schema. ICD 4."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Generic, TypeVar

from interfaces._validate import check_uint
from interfaces.inputs.chassis_signals import ImuSignals, SpeedSignals, SteeringSignals
from interfaces.inputs.function_requests import FunctionRequests
from interfaces.inputs.lane_model import LaneModel
from interfaces.inputs.lead_target import LeadTarget
from interfaces.inputs.longitudinal_plan import LongitudinalPlan
from interfaces.inputs.object_list import ObjectList
from interfaces.inputs.vehicle_state import VehicleStateEstimate
from interfaces.outputs.intervention_status import InterventionStatus
from interfaces.outputs.lateral_limits import LateralLimits
from interfaces.outputs.lcc_status import LccStatus
from interfaces.outputs.trajectory import Trajectory


PLANNER_PERIOD_US = 25000


class InitResult(IntEnum):
    OK = 0
    BAD_ARGUMENT = 1
    BAD_VEHICLE_CONFIG = 2
    BAD_CALIBRATION = 3


T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Received(Generic[T]):
    """Message nhận mới nhất và thời điểm nhận theo đồng hồ bên nhận."""

    message: T
    rx_us: int

    def __post_init__(self) -> None:
        check_uint(self.rx_us, 64, "rx_us")


@dataclass(frozen=True, slots=True)
class LccInputs:
    """Input LCC: message nhận mới nhất kèm rx_us, hoặc vắng nếu chưa nhận."""

    t0_us: int  # [us]
    lane_model: Received[LaneModel] | None = None
    object_list: Received[ObjectList] | None = None
    lead_target: Received[LeadTarget] | None = None
    imu: Received[ImuSignals] | None = None
    steering: Received[SteeringSignals] | None = None
    speed: Received[SpeedSignals] | None = None
    vehicle_state: Received[VehicleStateEstimate] | None = None
    function_requests: Received[FunctionRequests] | None = None
    longitudinal_plan: Received[LongitudinalPlan] | None = None

    def __post_init__(self) -> None:
        check_uint(self.t0_us, 64, "t0_us")


@dataclass(frozen=True, slots=True)
class LccOutputs:
    """Đầu ra của một chu kỳ LCC, kèm cờ phát riêng cho từng message."""

    trajectory: Trajectory | None = None
    lcc_status: LccStatus | None = None
    lateral_limits: LateralLimits | None = None


@dataclass(frozen=True, slots=True)
class LkaElkInputs:
    """Input LKA/ELK: message nhận mới nhất kèm rx_us, hoặc vắng nếu chưa nhận."""

    t0_us: int  # [us]
    lane_model: Received[LaneModel] | None = None
    imu: Received[ImuSignals] | None = None
    steering: Received[SteeringSignals] | None = None
    speed: Received[SpeedSignals] | None = None
    vehicle_state: Received[VehicleStateEstimate] | None = None
    function_requests: Received[FunctionRequests] | None = None
    longitudinal_plan: Received[LongitudinalPlan] | None = None

    def __post_init__(self) -> None:
        check_uint(self.t0_us, 64, "t0_us")


@dataclass(frozen=True, slots=True)
class LkaElkOutputs:
    """Đầu ra của một chu kỳ LKA/ELK, kèm cờ phát riêng cho từng message."""

    trajectory: Trajectory | None = None
    intervention_status: InterventionStatus | None = None

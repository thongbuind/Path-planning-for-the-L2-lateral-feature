"""Hợp đồng gọi hai planner từ Python. Xem Interface Control Document mục 4 và pp_planner.h."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from interfaces.inputs.ego_motion import EgoMotionRequest, EgoMotionResponse
from interfaces.inputs.vehicle_config import VehicleConfig
from interfaces.planner_io import InitResult, LccInputs, LccOutputs, LkaElkInputs, LkaElkOutputs

# Planner gọi EgoMotionQuery và nhận kết quả trong cùng chu kỳ (ICD 5.5).
EgoMotionQuery = Callable[[EgoMotionRequest], EgoMotionResponse]


class LccPlanner(Protocol):
    @property
    def init_result(self) -> InitResult:
        """Khởi tạo khác OK thì planner không phát Trajectory (PP-SWR-146)."""
        ...

    def step(self, inputs: LccInputs, ego_motion: EgoMotionQuery) -> LccOutputs:
        ...


class LkaElkPlanner(Protocol):
    @property
    def init_result(self) -> InitResult:
        ...

    def step(self, inputs: LkaElkInputs, ego_motion: EgoMotionQuery) -> LkaElkOutputs:
        ...


@dataclass(frozen=True, slots=True)
class PlannerSet:
    """Hai planner của một run dùng state riêng (PP-ADR-016)."""

    lcc: LccPlanner | None
    lka_elk: LkaElkPlanner | None


# VehicleConfig có thể là None khi chưa nhận được cấu hình.
PlannerFactory = Callable[[VehicleConfig | None], PlannerSet]

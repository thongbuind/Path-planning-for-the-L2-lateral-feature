"""Điều kiện vào LCC khi tài xế bấm nút (ADAS Function Specification mục 7, PP-PR-003).

Khi yêu cầu LCC chuyển sang REQUEST, khối Chức năng ADAS chạy thử kiểm DLC hai phía, lệch tâm,
góc lệch so với làn và xi-nhan trên lane model đo được. Không thoả thì từ chối: giữ STANDBY tới
khi yêu cầu rời REQUEST (lần bấm sau). Tay trên vô lăng chưa có trong kịch bản nên chưa kiểm.
"""

from dataclasses import dataclass, replace
from math import atan, degrees

from interfaces import FunctionRequest, LaneModel, LineStatus, RequestState, Side, VehicleConfig

LEFT_EGO, RIGHT_EGO = 1, 2
_US_PER_S = 1_000_000


@dataclass(frozen=True, slots=True)
class HwaEntryCalibration:
    hwa_entry_dlc: float = 0.2
    hwa_entry_offset: float = 0.5
    hwa_entry_heading_deg: float = 2.0
    t_entry_wait: float = 0.5


def _y(line, x: float) -> float:
    return line.c0 + x * (line.c1 + x * (line.c2 + x * line.c3))


class HwaEntryGate:
    def __init__(self, vehicle: VehicleConfig, cal: HwaEntryCalibration = HwaEntryCalibration()) -> None:
        self.vehicle = vehicle
        self.cal = cal
        self.state: str | None = None  # None, "pending", "accepted", "refused"
        self._since_us = 0

    def entry_ok(self, lane: LaneModel) -> bool | None:
        """None khi chưa đủ hai vạch làn mình để quyết."""
        left, right = lane.lines[LEFT_EGO], lane.lines[RIGHT_EGO]
        if LineStatus.LOST in (left.status, right.status):
            return None
        x_front, half = self.vehicle.wheelbase, self.vehicle.vehicle_width / 2
        dlc_left = _y(left, x_front) - half
        dlc_right = -_y(right, x_front) - half
        offset = abs(left.c0 + right.c0) / 2  # Lệch tâm tại base_link, như d0 của planner (T6).
        heading = degrees(abs(atan((left.c1 + right.c1) / 2)))
        return (min(dlc_left, dlc_right) >= self.cal.hwa_entry_dlc
                and offset <= self.cal.hwa_entry_offset and heading <= self.cal.hwa_entry_heading_deg)

    def apply(self, request: FunctionRequest, now_us: int, lane: LaneModel | None,
              indicator: Side = Side.NONE) -> FunctionRequest:
        if request.state != RequestState.REQUEST:
            self.state = None
            return request
        if self.state == "accepted":
            return request
        standby = replace(request, state=RequestState.STANDBY)
        if self.state == "refused":
            return standby
        if self.state is None:
            self.state, self._since_us = "pending", now_us
        ok = self.entry_ok(lane) if lane is not None else None
        if ok is None:
            if now_us - self._since_us > round(self.cal.t_entry_wait * _US_PER_S):
                self.state = "refused"
            return standby
        self.state = "accepted" if ok and indicator == Side.NONE else "refused"
        return request if self.state == "accepted" else standby

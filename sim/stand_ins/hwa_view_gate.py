"""Tính thời gian nhìn trước từ tầm nhìn chung của L1/R1 chia cho tốc độ. LCC rời REQUEST nếu thời
gian quá ngắn đủ lâu (ADAS-FS 7).
"""

from dataclasses import dataclass, replace

from interfaces import FunctionRequest, LaneModel, LineStatus, RequestState

EGO_LINES = (1, 2)
_STANDSTILL_MPS = 0.1
_US_PER_S = 1_000_000


@dataclass(frozen=True, slots=True)
class HwaViewCalibration:
    t_view_hwa: float = 1.0
    t_view_hold: float = 0.5


class HwaViewGate:
    def __init__(self, cal: HwaViewCalibration = HwaViewCalibration()) -> None:
        self.cal = cal
        self._short_since_us: int | None = None

    @staticmethod
    def preview_s(lane: LaneModel | None, speed_mps: float) -> float:
        if speed_mps < _STANDSTILL_MPS:
            return float("inf")
        if lane is None:
            return 0.0
        ends = [lane.lines[i].view_range_end for i in EGO_LINES if lane.lines[i].status != LineStatus.LOST]
        return min(ends) / speed_mps if ends else 0.0

    def available(self, now_us: int, lane: LaneModel | None, speed_mps: float) -> bool:
        if self.preview_s(lane, speed_mps) >= self.cal.t_view_hwa:
            self._short_since_us = None
            return True
        if self._short_since_us is None:
            self._short_since_us = now_us
        return now_us - self._short_since_us <= round(self.cal.t_view_hold * _US_PER_S)

    def apply(self, request: FunctionRequest, now_us: int, lane: LaneModel | None,
              speed_mps: float, following: bool = False) -> FunctionRequest:
        if following:
            self._short_since_us = None
            return request
        ok = self.available(now_us, lane, speed_mps)
        if request.state == RequestState.REQUEST and not ok:
            return replace(request, state=RequestState.UNAVAILABLE)
        return request

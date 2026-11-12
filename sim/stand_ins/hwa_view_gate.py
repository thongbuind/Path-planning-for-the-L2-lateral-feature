"""HWA view-range availability (ADAS Function Specification 7, 13), test side.

Preview time = common view range end of the two ego-lane lines (L1, R1) / speed. Below
`t_view_hwa` for longer than `t_view_hold`, HWA leaves REQUEST for UNAVAILABLE, and it
returns by itself once the preview is long enough again (ADAS Function Specification 9.1).
Used with scripted requests, where the scenario otherwise holds HWA in REQUEST.
"""

from dataclasses import dataclass, replace

from interfaces import FunctionRequest, LaneModel, LineStatus, RequestState

EGO_LINES = (1, 2)  # L1, R1
_STANDSTILL_MPS = 0.1
_US_PER_S = 1_000_000


@dataclass(frozen=True, slots=True)
class HwaViewCalibration:
    """Start values of ADAS Function Specification 13."""

    t_view_hwa: float = 1.0  # [s]
    t_view_hold: float = 0.5  # [s]


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
              speed_mps: float) -> FunctionRequest:
        """HWA request after the view rule; call once per FunctionRequests cycle."""
        ok = self.available(now_us, lane, speed_mps)
        if request.state == RequestState.REQUEST and not ok:
            return replace(request, state=RequestState.UNAVAILABLE)
        return request

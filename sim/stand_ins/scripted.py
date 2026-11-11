"""Scripted stand-ins for the first closed loop (temporary).

Until the stand-in ADAS function block (Software Qualification Test Specification 4.1,
modes A and B) and the stand-in ACC (4.7) exist, these send fixed messages:

- FunctionRequests: HWA in REQUEST from a given time, LKA and ELK OFF.
- LongitudinalPlan: CRUISE at the scenario speed.

Deviation from 4.4 ("Kịch bản có HWA chạy với ACC bật"): speed is held by the scenario.
"""

from interfaces import (
    FUNCTIONS,
    LONGITUDINAL_PLAN_POINTS,
    BasicHeader,
    CancelReason,
    ElkReason,
    FrameId,
    FunctionRequest,
    FunctionRequests,
    Header,
    LongitudinalMode,
    LongitudinalPlan,
    LongitudinalPoint,
    RequestState,
    Side,
)

PERIOD_US = 25_000  # 40 Hz (4.1)


class ScriptedFunctionRequests:
    def __init__(self, hwa_request_us: int) -> None:
        self.hwa_request_us = hwa_request_us
        self._counter = 0

    def message(self, now_us: int) -> FunctionRequests:
        hwa = RequestState.REQUEST if now_us >= self.hwa_request_us else RequestState.STANDBY
        requests = [FunctionRequest(hwa, Side.NONE, float("inf"), ElkReason.NONE, CancelReason.NONE)]
        requests += [FunctionRequest(RequestState.OFF, Side.NONE, float("inf"),
                                     ElkReason.NONE, CancelReason.NONE)] * (FUNCTIONS - 1)
        msg = FunctionRequests(BasicHeader(now_us, self._counter, True), tuple(requests), False)
        self._counter = (self._counter + 1) % 256
        return msg


class ScriptedLongitudinal:
    def __init__(self, speed_mps: float) -> None:
        self.speed_mps = speed_mps
        self._counter = 0

    def message(self, now_us: int) -> LongitudinalPlan:
        points = (LongitudinalPoint(self.speed_mps, 0.0),) * LONGITUDINAL_PLAN_POINTS
        msg = LongitudinalPlan(Header(now_us, self._counter, True, FrameId.BASE_LINK),
                               LongitudinalMode.CRUISE, points, 0)
        self._counter = (self._counter + 1) % 256
        return msg

"""Scripted request inputs for planner tests, and constant-speed LongitudinalPlan.

The default is the original HWA request schedule with LKA and ELK off. A test can
supply complete request frames by simulation time to control the ICD input.
"""

from bisect import bisect_right
from dataclasses import dataclass

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


@dataclass(frozen=True, slots=True)
class RequestEvent:
    at_us: int
    requests: tuple[FunctionRequest, ...]  # HWA, LKA, ELK, per ICD 5.6
    driver_override: bool = False
    # sim.faults.trigger event: at_us counts from its first occurrence (S16 a, b, e)
    trigger: str | None = None

    def __post_init__(self) -> None:
        from sim.faults import trigger
        trigger.check(self.trigger)
        if self.at_us < 0 or len(self.requests) != FUNCTIONS:
            raise ValueError("request event needs a non-negative time and three requests")


class ScriptedFunctionRequests:
    def __init__(self, hwa_request_us: int | None, events: tuple[RequestEvent, ...] = ()) -> None:
        self.hwa_request_us = hwa_request_us
        timed = [e.at_us for e in events if e.trigger is None]
        if any(a >= b for a, b in zip(timed, timed[1:])):
            raise ValueError("request event times must be strictly increasing")
        self._pending = [e for e in events if e.trigger is not None]
        self._resolve([e for e in events if e.trigger is None])
        self._counter = 0

    def _resolve(self, events) -> None:
        self.events = tuple(sorted(events, key=lambda e: e.at_us))
        self._times = tuple(event.at_us for event in self.events)

    def on_event(self, event: str, t_us: int) -> None:
        """First occurrence of a planner-output event: its events get their time."""
        ready = [e for e in self._pending if e.trigger == event]
        if ready:
            self._pending = [e for e in self._pending if e.trigger != event]
            from dataclasses import replace
            self._resolve([*self.events, *(replace(e, at_us=t_us + e.at_us, trigger=None) for e in ready)])

    def hwa_request(self, now_us: int) -> FunctionRequest:
        hwa = RequestState.OFF
        if self.hwa_request_us is not None:
            hwa = RequestState.REQUEST if now_us >= self.hwa_request_us else RequestState.STANDBY
        return FunctionRequest(hwa, Side.NONE, float("inf"), ElkReason.NONE, CancelReason.NONE)

    def message(self, now_us: int) -> FunctionRequests:
        index = bisect_right(self._times, now_us) - 1
        if index >= 0:
            event = self.events[index]
            requests, override = event.requests, event.driver_override
        else:
            off = FunctionRequest(RequestState.OFF, Side.NONE, float("inf"), ElkReason.NONE, CancelReason.NONE)
            requests = (self.hwa_request(now_us),) + (off,) * (FUNCTIONS - 1)
            override = False
        msg = FunctionRequests(BasicHeader(now_us, self._counter, True), requests, override)
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

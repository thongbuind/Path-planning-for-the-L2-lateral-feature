"""LKA and ELK request stand-in, independent of the planner (PP-ADR-014).

The harness supplies measured inputs for mode A and ideal inputs for mode B.
This block uses the same decision logic in both modes (ADAS-FS 5–9, SQTS 4.1).
"""

from dataclasses import dataclass, field, replace
from math import hypot, inf, isfinite, radians

from interfaces import (
    COUNTER_MODULO, BasicHeader, CancelReason, EgoMotionQuery, EgoMotionResponse,
    ElkReason, FunctionRequest, FunctionRequests, InterventionPhase, LaneLine,
    LaneModel, Object, ObjectList, RequestState, RoadEdge, Side, VehicleConfig,
)
from sim.messages import DriverSignals
from sim.stand_ins.adas_observation import (
    EGO_LINE_INDEX, MIN_OUTWARD_SPEED, OUTER_LINE_INDEX, SIDES, Clearance, VehicleMotion,
    clearance, motion_since, object_conflict, sign_of_side, trusted,
)

_US_PER_S = 1_000_000
_SPEED_ENTRY = 70 / 3.6  # [m/s], ADAS-FS 7
_SPEED_EXIT = 65 / 3.6
_SPEED_MAX = 130 / 3.6
_PASSIVE_RATE = radians(15)  # ADAS-FS 8
_PASSIVE_HOLD_US = 500_000
_INTENT_RATE = radians(30)
_INTENT_HOLD_US = 200_000
_OVERRIDE_HOLD_US = 100_000
_LANE_CHANGE_WAIT_US = 1_000_000  # ADAS-FS 11
_JUMP_WAIT_US = 500_000
_LKA_SPEED_MIN = 0.1  # [m/s] outward speed, ADAS-FS 9
_LKA_SPEED_MAX = 1.0
_LATE_LINE_M = 0.3  # ADAS-FS 11, PP-SWR-089
_LANE_WIDTH_MIN, _LANE_WIDTH_MAX = 2.5, 5.5  # PP-ASM-015


@dataclass(frozen=True, slots=True)
class AdasCalibration:
    """Stand-in defaults from ADAS Function Specification 13."""

    tlc_lka: float = 1.0
    dlc_lka: float = 0.1
    tlc_elk_line: float = 0.6
    tlc_elk_object: float = 0.8
    k_sigma: float = 2.0
    sigma_tlc_max: float = 0.5
    n_confirm: int = 2
    conf_ego: float = 0.6
    conf_edge: float = 0.7
    view_min: float = 20.0
    exist_min: float = 0.7
    n_track: int = 3
    t_conflict: float = 3.0
    box_margin: float = 2.0
    abreast_margin: float = 1.0
    ttc_rear: float = 1.5
    decel_rear: float = 3.0
    torque_passive: float = 0.5
    torque_intent: float = 1.5
    torque_override: float = 3.0
    t_indicator: float = 2.0
    v_lat_swerve: float = 1.0
    t_reactivate_override: float = 3.0
    dlc_rearm: float = 0.3
    t_rearm: float = 2.0


@dataclass(frozen=True, slots=True)
class PathFeedback:
    """PathStatus values needed by the stand-in, with separate phase ownership."""

    path_valid: bool = False
    lka_phase: InterventionPhase = InterventionPhase.NONE
    elk_phase: InterventionPhase = InterventionPhase.NONE


@dataclass(frozen=True, slots=True)
class AdasInputs:
    lane: LaneModel | None
    objects: ObjectList | None
    motion: VehicleMotion | None
    driver: DriverSignals
    feedback: PathFeedback


@dataclass(frozen=True, slots=True)
class _CapturedBoundary:
    stamp_us: int
    boundary: LaneLine | RoadEdge


@dataclass(slots=True)
class _BoundaryHistory:
    accepted: _CapturedBoundary | None = None
    pending: _CapturedBoundary | None = None
    rejected_since_us: int | None = None


@dataclass(slots=True)
class _RequestState:
    request: FunctionRequest | None = None
    # Side -> (expiry, completed against a road edge).
    rearm: dict[Side, tuple[int, bool]] = field(default_factory=dict)

    def finish(self, now_us: int, rearm_s: float) -> Side:
        request = self.request
        if request is None:
            return Side.NONE
        self.rearm[request.side] = (now_us + round(rearm_s * _US_PER_S),
                                    request.elk_reason == ElkReason.ROAD_EDGE)
        self.request = None
        return request.side


def _request(state: RequestState, side: Side = Side.NONE, tlc: float = inf,
             elk_reason: ElkReason = ElkReason.NONE,
             cancel: CancelReason = CancelReason.NONE) -> FunctionRequest:
    return FunctionRequest(state, side, tlc, elk_reason, cancel)


class AdasFunction:
    def __init__(self, vehicle: VehicleConfig, *, lka_enabled: bool, elk_enabled: bool,
                 calibration: AdasCalibration = AdasCalibration()) -> None:
        self.vehicle = vehicle
        self.cal = calibration
        self.lka_enabled = lka_enabled
        self.elk_enabled = elk_enabled
        self.lka = _RequestState()
        self.elk = _RequestState()
        self._counter = 0
        self._speed_armed = False
        self._width: float | None = None
        self._lane_stamp: int | None = None
        self._lane_change_until = 0
        self._boundaries: dict[tuple[Side, bool], _BoundaryHistory] = {}
        self._object_stamp: int | None = None
        self._object_tracks: dict[int, int] = {}
        self._confirmations: dict[Side, tuple[int, int]] = {}
        self._passive_since: int | None = None
        self._torque_intent_since: dict[Side, int] = {}
        self._last_indicator: dict[Side, int] = {}
        self._override_start: tuple[Side, int] | None = None
        self._override_side = Side.NONE
        self._reactivate_at: dict[Side, int] = {}
        self.tlc_s = (inf, inf, inf, inf)  # L1, R1, left edge, right edge, for diagnostics

    def _stable_boundary(self, boundary: LaneLine | RoadEdge, side: Side, edge: bool,
                         stamp: int, now_us: int, frame: EgoMotionResponse, motion: VehicleMotion,
                         ego_motion: EgoMotionQuery) -> tuple[Clearance | None, bool]:
        confidence = self.cal.conf_edge if edge else self.cal.conf_ego
        if not trusted(boundary, confidence, self.cal.view_min):
            return None, False
        estimate = clearance(boundary, side, frame, self.vehicle, motion)
        if estimate is None or not any(boundary.variance):
            return estimate, False
        history = self._boundaries.setdefault((side, edge), _BoundaryHistory())
        current = _CapturedBoundary(stamp, boundary)

        def agrees(older: _CapturedBoundary) -> bool:
            delta = motion_since(older.stamp_us, now_us, ego_motion)
            previous = clearance(older.boundary, side, delta, self.vehicle, motion) if delta.valid else None
            return previous is not None and (
                abs(previous.dlc - estimate.dlc) <= self.cal.k_sigma * hypot(previous.sigma_dlc,
                                                                           estimate.sigma_dlc))

        accepted = history.accepted
        if (accepted is None or accepted.stamp_us == stamp or agrees(accepted)
                or (history.pending is not None and history.pending.stamp_us != stamp and agrees(history.pending))):
            history.accepted, history.pending, history.rejected_since_us = current, None, None
            return estimate, False
        if history.rejected_since_us is None:
            history.rejected_since_us = now_us
        history.pending = current
        return None, now_us - history.rejected_since_us < _JUMP_WAIT_US

    def _track_objects(self, objects: ObjectList | None) -> tuple[Object, ...]:
        if objects is None:
            self._object_stamp = None
            self._object_tracks.clear()
            return ()
        candidates = tuple(obj for obj in objects.objects[:objects.num_objects]
                           if obj.id and obj.existence_probability >= self.cal.exist_min
                           and obj.length > 0 and obj.width > 0
                           and all(map(isfinite, (obj.x, obj.y, obj.vx, obj.vy, obj.length, obj.width))))
        if objects.header.stamp_us != self._object_stamp:
            self._object_stamp = objects.header.stamp_us
            self._object_tracks = {obj.id: self._object_tracks.get(obj.id, 0) + 1 for obj in candidates}
        return tuple(obj for obj in candidates if self._object_tracks.get(obj.id, 0) >= self.cal.n_track)

    def _driver_intent(self, now_us: int, inputs: AdasInputs) -> tuple[bool, set[Side]]:
        signals, motion = inputs.driver, inputs.motion
        if signals.indicator != Side.NONE:
            self._last_indicator[signals.indicator] = now_us
        rate = motion.steering_rate_rps if motion is not None else 0.0
        passive = motion is not None and abs(signals.torque_nm) < self.cal.torque_passive and abs(rate) < _PASSIVE_RATE
        if not passive:
            self._passive_since = None
        elif self._passive_since is None:
            self._passive_since = now_us
        deliberate = set()
        for side in SIDES:
            sign = sign_of_side(side)
            if sign * signals.torque_nm >= self.cal.torque_intent:
                since = self._torque_intent_since.setdefault(side, now_us)
                if now_us - since >= _INTENT_HOLD_US:
                    deliberate.add(side)
            else:
                self._torque_intent_since.pop(side, None)
            if (sign * rate >= _INTENT_RATE or side in self._last_indicator
                    and now_us - self._last_indicator[side] < self.cal.t_indicator * _US_PER_S):
                deliberate.add(side)
        return self._passive_since is not None and now_us - self._passive_since >= _PASSIVE_HOLD_US, deliberate

    def _overridden(self, now_us: int, inputs: AdasInputs) -> bool:
        torque = inputs.driver.torque_nm
        if self._override_side != Side.NONE:
            if sign_of_side(self._override_side) * torque >= self.cal.torque_override:
                return True
            self._reactivate_at[self._override_side] = now_us + round(self.cal.t_reactivate_override * _US_PER_S)
            self._override_side = Side.NONE
        active = self.lka.request if inputs.feedback.lka_phase == InterventionPhase.ACTIVE else self.elk.request
        active = active or self.lka.request
        if active is None or sign_of_side(active.side) * torque < self.cal.torque_override:
            self._override_start = None
            return False
        if self._override_start is None or self._override_start[0] != active.side:
            self._override_start = (active.side, now_us)
        if now_us - self._override_start[1] < _OVERRIDE_HOLD_US:
            return False
        self._override_side = active.side
        self._override_start = None
        return True

    def _rearmed(self, state: _RequestState, side: Side, now_us: int,
                 marking: Clearance | None, edge: Clearance | None) -> bool:
        hold = state.rearm.get(side)
        if hold is None:
            return True
        expiry, was_edge = hold
        current = edge if was_edge else marking
        if now_us >= expiry:
            del state.rearm[side]
            return True
        if current is not None and current.dlc >= self.cal.dlc_rearm:
            del state.rearm[side]
        return False

    def _valid_estimate(self, c: Clearance) -> bool:
        return c.outward_speed < MIN_OUTWARD_SPEED or c.sigma_tlc <= self.cal.sigma_tlc_max

    def _close(self, c: Clearance, limit_s: float) -> bool:
        return c.outward_speed - self.cal.k_sigma * c.sigma_speed >= MIN_OUTWARD_SPEED and c.tlc <= limit_s

    def _keep_request(self, state: _RequestState, now_us: int, inputs: AdasInputs,
                      markings: dict[Side, Clearance], edges: dict[Side, Clearance],
                      alternate_boundary: bool, suspect: bool, deliberate: set[Side],
                      override: bool) -> FunctionRequest | None:
        req = state.request
        if req is None:
            return None
        object_elk = req.elk_reason in (ElkReason.ONCOMING, ElkReason.OVERTAKING)
        at_edge = req.elk_reason == ElkReason.ROAD_EDGE
        if override:
            cancel = CancelReason.DRIVER_OVERRIDE
        elif not inputs.driver.esc_enabled or inputs.driver.esc_active:
            cancel = CancelReason.ESC
        elif req.side in deliberate and not object_elk:
            cancel = CancelReason.INDICATOR if req.side in self._last_indicator and (
                now_us - self._last_indicator[req.side] < self.cal.t_indicator * _US_PER_S) else CancelReason.DRIVER_OVERRIDE
        elif inputs.motion is not None and inputs.motion.speed_mps > _SPEED_MAX:
            cancel = CancelReason.SPEED
        elif now_us < self._lane_change_until or (not suspect and not markings and alternate_boundary
                                                 and not (at_edge and req.side in edges)):
            cancel = CancelReason.LANE_QUALITY
        else:
            # Below 65 km/h, lost v_y or no remaining trusted boundary: keep
            # REQUEST for the intervention already underway (ADAS-FS 9).
            c = (edges if at_edge else markings).get(req.side)
            return req if c is None or suspect else replace(req, tlc=c.tlc)
        state.request = None
        return _request(RequestState.OFF, req.side, cancel=cancel)

    def _elk_objects(self, side: Side, c: Clearance, lane: LaneModel, lane_frame: EgoMotionResponse,
                     objects: tuple[Object, ...], object_frame: EgoMotionResponse, object_age_s: float,
                     speed: float, deliberate: bool) -> ElkReason:
        if not object_frame.valid or not self._close(c, self.cal.tlc_elk_object):
            return ElkReason.NONE
        line = lane.lines[EGO_LINE_INDEX[side]]
        outer = lane.lines[OUTER_LINE_INDEX[side]]
        if not trusted(outer, self.cal.conf_ego, self.cal.view_min):
            outer = None
        width = self._width if self._width is not None else lane.lane_width
        if not _LANE_WIDTH_MIN <= width <= _LANE_WIDTH_MAX and outer is None:
            return ElkReason.NONE
        for obj in objects:
            reason = object_conflict(
                obj, side, line, outer, width, object_frame, object_age_s, lane_frame,
                speed, self.vehicle.wheelbase, c.tlc, conflict_s=self.cal.t_conflict,
                box_margin=self.cal.box_margin, deliberate=deliberate, abreast_margin=self.cal.abreast_margin,
                ttc_rear=self.cal.ttc_rear, decel_rear=self.cal.decel_rear,
            )
            if reason != ElkReason.NONE:
                return reason
        return ElkReason.NONE

    def message(self, now_us: int, inputs: AdasInputs, ego_motion: EgoMotionQuery,
                hwa: FunctionRequest) -> FunctionRequests:
        lane, motion = inputs.lane, inputs.motion
        if lane is not None and lane.header.stamp_us != self._lane_stamp:
            self._lane_stamp = lane.header.stamp_us
            if lane.lane_change != Side.NONE:
                self._lane_change_until = now_us + _LANE_CHANGE_WAIT_US
                self._boundaries.clear()
                self._confirmations.clear()
                self._width = None

        markings: dict[Side, Clearance] = {}
        edges: dict[Side, Clearance] = {}
        suspect = False
        if lane is not None and motion is not None:
            frame = motion_since(lane.header.stamp_us, now_us, ego_motion)
            if frame.valid:
                for index, side in enumerate(SIDES):
                    for boundary, edge, estimates in ((lane.lines[EGO_LINE_INDEX[side]], False, markings),
                                                      (lane.road_edges[index], True, edges)):
                        estimate, pending = self._stable_boundary(boundary, side, edge, lane.header.stamp_us,
                                                                  now_us, frame, motion, ego_motion)
                        suspect |= pending
                        if estimate is not None:
                            estimates[side] = estimate
        self.tlc_s = tuple(group[side].tlc if side in group else inf
                           for group in (markings, edges) for side in SIDES)
        # Learn width only from a credible pair of boundaries of the ego lane.
        bounds = [markings.get(side) or edges.get(side) for side in SIDES]
        if all(bound is not None for bound in bounds):
            width = self.vehicle.vehicle_width + sum(bound.dlc for bound in bounds)
            if _LANE_WIDTH_MIN <= width <= _LANE_WIDTH_MAX:
                self._width = width

        passive, deliberate = self._driver_intent(now_us, inputs)
        speed = motion.speed_mps if motion is not None else 0.0
        self._speed_armed = (_SPEED_EXIT if self._speed_armed else _SPEED_ENTRY) <= speed <= _SPEED_MAX
        swerve = inputs.driver.indicator == Side.NONE and any(
            c.outward_speed > self.cal.v_lat_swerve for group in (markings, edges) for c in group.values())
        override = self._overridden(now_us, inputs) or swerve

        elk_side = self.elk.request.side if self.elk.request is not None else Side.NONE
        blocked_side = elk_side if inputs.feedback.elk_phase == InterventionPhase.ACTIVE else Side.NONE
        completed_elk = (self.elk.finish(now_us, self.cal.t_rearm)
                         if inputs.feedback.elk_phase == InterventionPhase.COMPLETED else Side.NONE)
        completed_lka = (self.lka.finish(now_us, self.cal.t_rearm)
                         if inputs.feedback.lka_phase == InterventionPhase.COMPLETED else Side.NONE)
        if completed_elk != Side.NONE:
            self.lka.rearm[completed_elk] = (now_us + round(self.cal.t_rearm * _US_PER_S), False)
            self._confirmations.pop(completed_elk, None)
        if self.lka.request is not None and self.lka.request.side in (blocked_side, completed_elk):
            self._confirmations.pop(self.lka.request.side, None)
            self.lka.request = None
        if completed_lka != Side.NONE:
            self._confirmations.pop(completed_lka, None)

        alt = bool(edges) or (lane is not None and any(trusted(lane.lines[i], self.cal.conf_ego, self.cal.view_min)
                                                     for i in OUTER_LINE_INDEX.values()))
        lka = (_request(RequestState.STANDBY) if completed_lka != Side.NONE else self._keep_request(
            self.lka, now_us, inputs, markings, edges, alt, suspect, deliberate, override))
        elk = (_request(RequestState.STANDBY) if completed_elk != Side.NONE else self._keep_request(
            self.elk, now_us, inputs, markings, edges, alt, suspect, deliberate, override))
        objects = self._track_objects(inputs.objects)
        can_start = (lane is not None and motion is not None and inputs.feedback.path_valid and self._speed_armed
                     and inputs.driver.esc_enabled and not inputs.driver.esc_active and not override
                     and now_us >= self._lane_change_until)
        if lka is None:
            lka = self._new_lka(now_us, lane, markings, passive, deliberate, can_start, blocked_side)
        if elk is None:
            elk = self._new_elk(now_us, inputs, markings, edges, objects, ego_motion, passive, deliberate, can_start)
        self.lka.request = lka if lka.state == RequestState.REQUEST else None
        self.elk.request = elk if elk.state == RequestState.REQUEST else None
        msg = FunctionRequests(BasicHeader(now_us, self._counter, True), (hwa, lka, elk), override)
        self._counter = (self._counter + 1) % COUNTER_MODULO
        return msg

    def _new_lka(self, now_us: int, lane: LaneModel | None, markings: dict[Side, Clearance],
                 passive: bool, deliberate: set[Side], can_start: bool, blocked_side: Side) -> FunctionRequest:
        if not self.lka_enabled:
            return _request(RequestState.OFF)
        available = {side: c for side, c in markings.items() if self._valid_estimate(c)}
        if not can_start or not available:
            self._confirmations.clear()
            return _request(RequestState.UNAVAILABLE)
        candidates = []
        for side in SIDES:
            c = available.get(side)
            ready = self._rearmed(self.lka, side, now_us, c, None)
            if (c is None or not ready or not passive or side == blocked_side or side in deliberate
                    or now_us < self._reactivate_at.get(side, 0)
                    or not _LKA_SPEED_MIN <= c.outward_speed <= _LKA_SPEED_MAX
                    or not (self._close(c, self.cal.tlc_lka) or c.dlc <= self.cal.dlc_lka)):
                self._confirmations.pop(side, None)
                continue
            stamp = lane.header.stamp_us
            last_stamp, count = self._confirmations.get(side, (-1, 0))
            if stamp != last_stamp:
                count += 1
                self._confirmations[side] = stamp, count
            if count >= self.cal.n_confirm:
                candidates.append(_request(RequestState.REQUEST, side, c.tlc))
        return min(candidates, key=lambda r: r.tlc, default=_request(RequestState.STANDBY))

    def _new_elk(self, now_us: int, inputs: AdasInputs, markings: dict[Side, Clearance],
                 edges: dict[Side, Clearance], objects: tuple[Object, ...], ego_motion: EgoMotionQuery,
                 passive: bool, deliberate: set[Side], can_start: bool) -> FunctionRequest:
        if not self.elk_enabled:
            return _request(RequestState.OFF)
        if not can_start:
            return _request(RequestState.UNAVAILABLE)
        lane, motion = inputs.lane, inputs.motion
        frame = motion_since(lane.header.stamp_us, now_us, ego_motion)
        object_stamp = inputs.objects.header.stamp_us if inputs.objects is not None else now_us
        object_frame = motion_since(object_stamp, now_us, ego_motion)
        available = False
        candidates = []
        for side in SIDES:
            c, edge = markings.get(side), edges.get(side)
            line_ok = c is not None and self._valid_estimate(c)
            edge_ok = (edge is not None and self._width is not None and self._valid_estimate(edge))
            available |= line_ok or edge_ok
            if not self._rearmed(self.elk, side, now_us, c, edge):
                continue
            intentional = side in deliberate
            allow_line = passive and not intentional and now_us >= self._reactivate_at.get(side, 0)
            if edge_ok and allow_line and self._close(edge, self.cal.tlc_elk_line):
                candidates.append(_request(RequestState.REQUEST, side, edge.tlc, ElkReason.ROAD_EDGE))
            if not line_ok or c.dlc < -_LATE_LINE_M:
                continue
            if passive or intentional:
                reason = self._elk_objects(side, c, lane, frame, objects, object_frame,
                                           (now_us - object_stamp) / _US_PER_S, motion.speed_mps, intentional)
                if reason != ElkReason.NONE:
                    candidates.append(_request(RequestState.REQUEST, side, c.tlc, reason))
                    continue
            line = lane.lines[EGO_LINE_INDEX[side]]
            if allow_line and not line.crossable and self._close(c, self.cal.tlc_elk_line):
                candidates.append(_request(RequestState.REQUEST, side, c.tlc, ElkReason.SOLID_LINE))
        standby = RequestState.STANDBY if available else RequestState.UNAVAILABLE
        return min(candidates, key=lambda r: r.tlc, default=_request(standby))

"""Prescribed departure geometry for the OpenSCENARIO adapter (SQTS 4.8, 5.1)."""

from dataclasses import replace
from math import asin, atan, cos, inf, isfinite, sin

from interfaces import CancelReason, ElkReason, FunctionRequest, RequestState, Side
from sim.scenario import Scenario
from sim.stand_ins.driver import DriverSpec
from sim.stand_ins.scripted import RequestEvent
from sim.vehicle.profiles import PROFILES


def configure(
    scenario: Scenario, *, side: str, v_lat_mps: float, radius_m: float, gap_m: float,
    boundary: str, target: str, steer_start_s: float, torque_nm: float, wind_n: float,
    bank_grade: float, indicated: bool, passive_hands_on: bool, late_request: bool,
    repeats: tuple = (), repeat_trigger: str | None = None, torque_windows: tuple = (),
) -> Scenario:
    """Set the approach arc and synchronize target with the nominal unassisted path."""
    if side not in ("left", "right") or boundary not in ("marking", "edge"):
        raise ValueError("unknown departure side or boundary")
    if target not in ("none", "oncoming", "overtaking"):
        raise ValueError("unknown departure target")
    numeric = (v_lat_mps, radius_m, gap_m, steer_start_s, torque_nm, wind_n, bank_grade)
    if (not all(map(isfinite, numeric)) or not 0 <= v_lat_mps < scenario.speed_mps
            or min(gap_m, steer_start_s, torque_nm, wind_n, bank_grade) < 0 or radius_m <= 0):
        raise ValueError("invalid departure geometry")
    if any(type(flag) is not bool for flag in (indicated, passive_hands_on, late_request)):
        raise ValueError("departure flags must be boolean")
    if target != "none" and (len(scenario.traffic) != 1 or v_lat_mps == 0 or boundary != "marking"):
        raise ValueError("traffic departure requires one target and a marking")
    if indicated and steer_start_s < 1.0:
        raise ValueError("the indicator needs one second before Tsteer")

    sign = 1 if side == "left" else -1
    request_side = Side.LEFT if sign > 0 else Side.RIGHT
    profile = PROFILES[scenario.profile]
    speed = scenario.speed_mps
    yaw = asin(v_lat_mps / speed)
    release_s = steer_start_s + radius_m * yaw / speed
    driver = DriverSpec(
        steer_start_s=steer_start_s, steer_release_s=release_s,
        drift_curvature=sign / radius_m if v_lat_mps else 0.0,
        torque_nm=sign * torque_nm if v_lat_mps else 0.0,
        disturbance_start_s=steer_start_s, wind_force_n=sign * wind_n,
        bank_angle_rad=sign * atan(bank_grade),
        indicator=request_side if indicated else Side.NONE,
        indicator_start_s=steer_start_s - 1.0 if indicated else 0.0,
        passive_hands_on=passive_hands_on,
        repeats=tuple((float(t), float(d)) for t, d in repeats), repeat_trigger=repeat_trigger or None,
        torque_windows=tuple((float(a), float(b)) for a, b in torque_windows),
    )
    if release_s >= scenario.duration_s or any(t + release_s - steer_start_s >= scenario.duration_s
                                                for t, _ in driver.repeats):
        raise ValueError("driver release must precede the end of the scenario")
    offset = scenario.start_offset_m
    layout = scenario.road_layout
    if v_lat_mps:
        index = 0 if sign > 0 else 1
        hazard = None if layout is None else (
            layout.edges[index] if boundary == "edge" else layout.markings[1 + index])
        if hazard is None:
            raise ValueError("departure requires the specified road boundary")
        arc_offset = radius_m * (1 - cos(yaw))
        offset = hazard.offset_m - sign * (arc_offset + gap_m + profile.width_with_mirrors / 2)
    traffic = scenario.traffic
    if target != "none":
        obj = traffic[0]
        oncoming = target == "oncoming"
        if (obj.direction == -1) != oncoming:
            raise ValueError("target heading disagrees with the encounter type")
        # LSS 7.2.4.3–4. Use the SQTS body overhang approximation for the
        # synchronization. Oncoming front edges meet at 10% VUT overlap.
        # The overtaking target's front edge reaches the VUT rear axle.
        tgt_d = hazard.offset_m + sign * 1.5
        front = profile.wheelbase + 1.0
        overlap = 0.1 * profile.width_with_mirrors if oncoming else 0.0
        after_arc = (gap_m + 1.5 - obj.width / 2 + overlap - front * sin(yaw)) / v_lat_mps
        meet = release_s + after_arc
        rear_s = scenario.start_s + speed * steer_start_s + radius_m * sin(yaw) + speed * cos(yaw) * after_arc
        aligned = rear_s + front * cos(yaw) if oncoming else rear_s
        target_s0 = aligned - obj.direction * (obj.length / 2 + obj.speed * meet)
        if not 0 <= target_s0 < sum(s.length for s in scenario.segments):
            raise ValueError("synchronized target starts outside the road")
        traffic = (replace(obj, s0=target_s0, d=tgt_d),)
    events = scenario.request_events
    if late_request:
        if scenario.adas_mode != "scripted" or boundary != "marking" or v_lat_mps == 0:
            raise ValueError("late request requires a scripted drift across a marking")
        # Put the nominal front tyre past the PP-SWR-089 threshold before
        # transmitting. Eval checks the actual tyre position at receipt.
        at_s = release_s + (gap_m + 0.45) / v_lat_mps
        if at_s >= scenario.duration_s:
            raise ValueError("late request must precede the end of the scenario")
        off = FunctionRequest(RequestState.OFF, Side.NONE, inf, ElkReason.NONE, CancelReason.NONE)
        elk = FunctionRequest(RequestState.REQUEST, request_side, 0.0,
                              ElkReason.OVERTAKING, CancelReason.NONE)
        events = (RequestEvent(round(at_s * 1e6), (off, off, elk)),)
    notes = {**scenario.notes, "departure_side": side, "departure_v_lat_mps": v_lat_mps}
    return replace(scenario, start_offset_m=offset, driver=driver, traffic=traffic,
                   request_events=events, notes=notes)

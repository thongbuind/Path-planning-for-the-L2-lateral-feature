"""Geometry and conflict prediction of the ADAS stand-in (ADAS-FS 5 and 6)."""

from dataclasses import dataclass
from math import cos, hypot, inf, isfinite, sin, sqrt

from interfaces import EgoMotionQuery, EgoMotionRequest, EgoMotionResponse, ElkReason
from interfaces import LaneLine, LineStatus, Object, RoadEdge, Side, VehicleConfig

MIN_OUTWARD_SPEED = 0.05  # [m/s] ADAS-FS 5
BODY_OVERHANG_M = 1.0  # SQTS 8.1: body extends 1 m beyond each axle
ABREAST_WINDOW_S = 1.0  # ADAS-FS 6, step 5
SIDES = (Side.LEFT, Side.RIGHT)
EGO_LINE_INDEX = {Side.LEFT: 1, Side.RIGHT: 2}
OUTER_LINE_INDEX = {Side.LEFT: 0, Side.RIGHT: 3}


@dataclass(frozen=True, slots=True)
class VehicleMotion:
    speed_mps: float
    lateral_velocity_mps: float  # at base_link
    lateral_velocity_variance: float
    yaw_rate_rps: float
    steering_rate_rps: float


@dataclass(frozen=True, slots=True)
class Clearance:
    dlc: float
    outward_speed: float
    tlc: float
    sigma_dlc: float
    sigma_speed: float
    sigma_tlc: float


def sign_of_side(side: Side) -> int:
    return 1 if side == Side.LEFT else -1


def motion_since(stamp_us: int, now_us: int, ego_motion: EgoMotionQuery) -> EgoMotionResponse:
    if stamp_us == now_us:
        return EgoMotionResponse(True, 0.0, 0.0, 0.0)
    if stamp_us > now_us:
        return EgoMotionResponse(False, 0.0, 0.0, 0.0)
    return ego_motion(EgoMotionRequest(stamp_us, now_us))


def trusted(boundary: LaneLine | RoadEdge, min_confidence: float, min_view: float) -> bool:
    return (boundary.status == LineStatus.MEASURED and boundary.confidence >= min_confidence
            and boundary.view_range_end - boundary.view_range_start >= min_view
            and all(map(isfinite, (boundary.c0, boundary.c1, boundary.c2, boundary.c3)))
            and all(isfinite(v) and v >= 0 for v in boundary.variance))


def _value_slope(boundary: LaneLine | RoadEdge, x: float) -> tuple[float, float]:
    y = boundary.c0 + x * (boundary.c1 + x * (boundary.c2 + x * boundary.c3))
    slope = boundary.c1 + x * (2 * boundary.c2 + x * 3 * boundary.c3)
    return y, slope


def clearance(boundary: LaneLine | RoadEdge, side: Side, frame: EgoMotionResponse,
              vehicle: VehicleConfig, motion: VehicleMotion) -> Clearance | None:
    """Evaluate the front axle and its velocity in the camera's capture frame."""
    c, s = cos(frame.dyaw), sin(frame.dyaw)
    x = frame.dx + vehicle.wheelbase * c
    y = frame.dy + vehicle.wheelbase * s
    if not boundary.view_range_start <= x <= boundary.view_range_end:
        return None
    line_y, slope = _value_slope(boundary, x)
    normal_length = hypot(1.0, slope)
    vy = motion.lateral_velocity_mps + motion.yaw_rate_rps * vehicle.wheelbase
    vx_camera = c * motion.speed_mps - s * vy
    vy_camera = s * motion.speed_mps + c * vy
    sign = sign_of_side(side)
    dlc = sign * (line_y - y) / normal_length - vehicle.vehicle_width / 2
    v_lat = sign * (vy_camera - slope * vx_camera) / normal_length
    var_c0, var_c1 = boundary.variance[:2]
    sigma_dlc = sqrt(var_c0 + x*x * var_c1)
    sigma_speed = sqrt(motion.speed_mps**2 * var_c1 + motion.lateral_velocity_variance)
    if v_lat < MIN_OUTWARD_SPEED:
        return Clearance(dlc, v_lat, inf, sigma_dlc, sigma_speed, inf)
    tlc = dlc / v_lat
    sigma_tlc = hypot(sigma_dlc / v_lat, tlc * sigma_speed / v_lat)
    return Clearance(dlc, v_lat, tlc, sigma_dlc, sigma_speed, sigma_tlc)


def _extrapolate_line(line: LaneLine, x: float) -> tuple[float, float]:
    # The lane model is forward-looking. Use its end tangent to assign objects
    # slightly outside the observed range, particularly a vehicle coming from behind.
    anchor = min(line.view_range_end, max(line.view_range_start, x))
    y, slope = _value_slope(line, anchor)
    return y + (x - anchor) * slope, slope


def _intersects_window(x: float, dv: float, t0: float, t1: float,
                       min_x: float, max_x: float) -> bool:
    a, b = x + t0 * dv, x + t1 * dv
    return min(a, b) <= max_x and max(a, b) >= min_x


def object_conflict(obj: Object, side: Side, line: LaneLine, outer: LaneLine | None,
                    lane_width: float, object_frame: EgoMotionResponse, age_s: float,
                    lane_frame: EgoMotionResponse, ego_speed: float, wheelbase: float,
                    tlc: float, *, conflict_s: float, box_margin: float,
                    deliberate: bool, abreast_margin: float, ttc_rear: float,
                    decel_rear: float) -> ElkReason:
    """Predict longitudinal overlap with an adjacent-lane object (ADAS-FS 6)."""
    c, s = cos(object_frame.dyaw), sin(object_frame.dyaw)
    dx = obj.x + obj.vx * age_s - object_frame.dx
    dy = obj.y + obj.vy * age_s - object_frame.dy
    x_now, y_now = c * dx + s * dy, -s * dx + c * dy
    vx_now, vy_now = c * obj.vx + s * obj.vy, -s * obj.vx + c * obj.vy
    c, s = cos(lane_frame.dyaw), sin(lane_frame.dyaw)
    x_lane = lane_frame.dx + c * x_now - s * y_now
    y_lane = lane_frame.dy + s * x_now + c * y_now
    line_y, slope = _extrapolate_line(line, x_lane)
    normal_length = hypot(1.0, slope)
    sign = sign_of_side(side)
    lateral = sign * (y_lane - line_y) / normal_length
    outer_y = (_extrapolate_line(outer, x_lane)[0] if outer is not None
               else line_y + sign * lane_width * normal_length)
    if not 0 <= lateral <= sign * (outer_y - line_y) / normal_length:
        return ElkReason.NONE

    vx_lane, vy_lane = c * vx_now - s * vy_now, s * vx_now + c * vy_now
    target_speed = (vx_lane + slope * vy_lane) / normal_length
    if target_speed == 0:
        return ElkReason.NONE
    dv = target_speed - ego_speed
    half_length = obj.length / 2
    rear_x, front_x = -BODY_OVERHANG_M - half_length, wheelbase + BODY_OVERHANG_M + half_length
    start = max(0.0, tlc)
    if not _intersects_window(x_now, dv, start, start + conflict_s,
                              rear_x - box_margin, front_x + box_margin):
        return ElkReason.NONE
    if target_speed < 0:
        # A deliberate crossing is only overridden for a qualifying adjacent conflict.
        if deliberate and not _intersects_window(x_now, dv, start, start + ABREAST_WINDOW_S,
                                                rear_x - abreast_margin, front_x + abreast_margin):
            return ElkReason.NONE
        return ElkReason.ONCOMING
    if deliberate:
        abreast = _intersects_window(x_now, dv, start, start + ABREAST_WINDOW_S,
                                     rear_x - abreast_margin, front_x + abreast_margin)
        rear_gap = rear_x - x_now
        cannot_brake = (rear_gap > 0 and dv > 0
                        and (rear_gap / dv <= ttc_rear or dv**2 / (2 * rear_gap) > decel_rear))
        if not (abreast or cannot_brake):
            return ElkReason.NONE
    return ElkReason.OVERTAKING

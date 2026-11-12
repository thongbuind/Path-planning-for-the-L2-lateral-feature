"""One RunLog as an MCAP file for Foxglove (Software Qualification Test Specification 4.1, 10).

Topics, log time = simulation time:
  /planner/trajectory, /planner/path_status, /planner/lateral_limits   outputs, as sent
  /planner/function_requests   FunctionRequests the planner received at each cycle
  /planner/cycle               compute time, lane-model view range given to the planner
  /truth/vehicle               ground truth every 10 ms: pose, speed, a_y, wheel angle, lane offset
                               and DLC of the front axle to both ego-lane boundaries
Metadata "run" holds what is needed to run the case again (the caller adds library, commit,
command); "scenario" holds the scenario values, faults included. Floats keep 6 significant
digits: the file is for viewing, a rerun goes through the manifest.
"""

import dataclasses
import enum
import math
from pathlib import Path

from sim.logging.mcap_writer import McapWriter

TRUTH_EVERY_US = 10_000


def _num(x: float) -> float | None:
    x = float(x)
    return float(f"{x:.6g}") if math.isfinite(x) else None


def _plain(value):
    """Dataclass tree to JSON values: enums by name, floats rounded, non-finite as null."""
    if isinstance(value, enum.Enum):
        return value.name
    if dataclasses.is_dataclass(value):
        return {f.name: _plain(getattr(value, f.name)) for f in dataclasses.fields(value)}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    if isinstance(value, bool) or value is None or isinstance(value, (int, str)):
        return value
    if isinstance(value, float):
        return _num(value)
    if hasattr(value, "item"):
        return _plain(value.item())
    return str(value)


def _trajectory(t) -> dict:
    return {"stamp_us": t.header.stamp_us, "counter": t.header.counter, "valid": t.header.valid,
            "observed_horizon_s": _num(t.observed_horizon_s),
            "points": [{"t": _num(p.time_from_start), "x": _num(p.pose.x), "y": _num(p.pose.y),
                        "yaw": _num(p.pose.yaw), "v": _num(p.longitudinal_velocity_mps),
                        "curvature": _num(p.curvature), "front_wheel_angle": _num(p.front_wheel_angle_rad)}
                       for p in t.points]}


def write(log, path: Path, run: dict[str, str] | None = None) -> Path:
    """Writes `log` (sim.harness.RunLog) to `path`; `run` adds rerun information."""
    scenario = log.scenario
    with McapWriter(path, profile="pp-sil") as out:
        out.metadata("run", {"scenario": scenario.name, "seed": str(log.seed), "profile": scenario.profile,
                             "init_result": str(log.init_result), **(run or {})})
        out.metadata("scenario", {f.name: repr(getattr(scenario, f.name)) for f in dataclasses.fields(scenario)})
        for c in log.cycles:
            ns = c.t0_us * 1000
            if c.trajectory is not None:
                out.message("/planner/trajectory", ns, _trajectory(c.trajectory))
            if c.path_status is not None:
                out.message("/planner/path_status", ns, _plain(c.path_status))
            if c.lateral_limits is not None:
                out.message("/planner/lateral_limits", ns, _plain(c.lateral_limits))
            if c.function_requests is not None:
                out.message("/planner/function_requests", ns,
                            {"rx_us": c.function_requests.rx_us, **_plain(c.function_requests.message)})
            out.message("/planner/cycle", ns, {
                "compute_ms": _num(c.compute_ns * 1e-6),
                "lane_capture_us": c.lane_view[0] if c.lane_view else None,
                "lane_view_end_m": _num(c.lane_view[1]) if c.lane_view else None,
                "lane_view_reported_m": _num(c.lane_view_reported) if c.lane_view_reported is not None else None})
        road, half_lane, half_car = log.road, 0.5 * log.road.lane_width, 0.5 * log.vehicle_width
        step = max(1, round(TRUTH_EVERY_US / max(1, (log.t_us[1] - log.t_us[0]) if len(log.t_us) > 1 else 1)))
        s_rear = s_front = None
        for k in range(0, len(log.t_us), step):
            rear, front = log.rear[k], log.front[k]
            pr = road.project(rear[0], rear[1], s_rear)
            pf = road.project(front[0], front[1], s_front)
            s_rear, s_front = pr.s, pf.s
            out.message("/truth/vehicle", log.t_us[k] * 1000, {
                "x": _num(rear[0]), "y": _num(rear[1]), "yaw": _num(rear[2]), "speed": _num(log.speed[k]),
                "a_y": _num(log.a_y[k]), "wheel_angle": _num(log.wheel_angle[k]),
                "eps_controlling": bool(log.eps_controlling[k]) if k < len(log.eps_controlling) else None,
                "lane_offset_m": _num(pr.d), "lane_width_m": _num(road.lane_width),
                "dlc_left_m": _num(half_lane - pf.d - half_car), "dlc_right_m": _num(half_lane + pf.d - half_car)})
    return Path(path)

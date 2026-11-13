"""PP-TS-013 joint acceleration and continuity experiment on the 1 m grid."""

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
from scipy.optimize import LinearConstraint, linprog, minimize

import prototype as P
from continuity_experiment import AY_MAX, AY_SUPPORT_MIN, LIMITS

VIEW_M = 80.0
CAMERA_PERIOD_S = 0.05
CAMERA_DELAY_S = 0.10
CAMERA_SAMPLE_NOISE_M = 0.03
CAMERA_SEED = 1
ACCEL_TOL = 1e-5
CASES = (
    ("S1f", "exact"),
    ("S14e", "exact"),
    ("S1be", "exact"),
    ("S14e-110", "exact"),
    ("S1f", "delayed-exact"),
    ("S1f", "cubic-clean"),
    ("S1f", "cubic"),
    ("S14e", "cubic-clean"),
    ("S14e", "cubic"),
)


class DelayedPreview:
    """A 20 Hz capture with an exact-geometry control or a cubic fit in the capture frame."""

    def __init__(self, road, source):
        self.road = road
        self.source = source
        self.frame = -1
        self.samples = int(VIEW_M / P.H) + 1

    def __call__(self, index):
        road = self.road
        now_s = road.sn[index]
        captured_t = now_s / road.v - CAMERA_DELAY_S
        if captured_t < 0.0:
            return np.zeros(self.samples)
        frame = int(np.floor(captured_t / CAMERA_PERIOD_S + 1e-9))
        if frame != self.frame:
            self.frame = frame
            self.start = frame * CAMERA_PERIOD_S * road.v
            self.end = self.start + VIEW_M
            if self.source != "delayed-exact":
                self.fit_cubic(frame)
        # Points beyond the last observed station are extrapolated by the prototype.
        count = min(self.samples, int(np.floor((self.end - now_s) / P.H)) + 1)
        if self.source == "delayed-exact":
            return road.kn[index:index + count]
        x, _ = self.coordinates(road.sn[index:index + count])
        slope = self.fit.deriv()(x)
        return self.fit.deriv(2)(x) / (1.0 + slope**2)**1.5

    def fit_cubic(self, frame):
        road = self.road
        at = self.start + np.arange(self.samples) * P.H
        self.origin_x = np.interp(self.start, road.s, road.x)
        self.origin_y = np.interp(self.start, road.s, road.y)
        theta = np.interp(self.start, road.s, road.th)
        self.cos, self.sin = np.cos(theta), np.sin(theta)
        x, y = self.coordinates(at)
        if self.source == "cubic":
            y += np.random.default_rng([CAMERA_SEED, frame]).normal(0, CAMERA_SAMPLE_NOISE_M, len(y))
        self.fit = np.polynomial.Polynomial.fit(x, y, deg=3)

    def coordinates(self, stations):
        dx = np.interp(stations, self.road.s, self.road.x) - self.origin_x
        dy = np.interp(stations, self.road.s, self.road.y) - self.origin_y
        return self.cos * dx + self.sin * dy, -self.sin * dx + self.cos * dy


def acceleration_bands(k, v):
    need = v**2 * k[1:-1]
    t = np.arange(1, len(k) - 1) * P.H / v
    required = (t <= 1.0) & (np.abs(need) > AY_MAX)
    lo = np.where(required & (need > 0.0), AY_SUPPORT_MIN, -AY_MAX)
    hi = np.where(required & (need < 0.0), -AY_SUPPORT_MIN, AY_MAX)
    return need, required, lo, hi


def bounded_path(k, observed, v, target, old, half_width, *, fixed_head=True):
    """Return the path, minimum relaxation and the correction outcome."""
    need, _, lo_ay, hi_ay = acceleration_bands(k[:observed], v)
    K = P.curvature_matrix(k[:observed])
    A = v**2 * K
    ay = need + A @ target[:observed]
    violation = float(max(0.0, np.max(lo_ay - ay), np.max(ay - hi_ay)))
    if violation <= ACCEL_TOL:
        return target, 0.0, "unchanged"

    lo = np.full(observed, -half_width)
    hi = -lo
    D = np.diff(np.eye(observed), axis=0) / P.H
    if old is None:
        C = np.empty((0, observed))
        c = np.empty(0)
    else:
        lo = np.maximum(lo, old[:observed] - LIMITS[0])
        hi = np.minimum(hi, old[:observed] + LIMITS[0])
        geometry = np.vstack((D / LIMITS[1], K / LIMITS[2]))
        C = np.vstack((geometry, -geometry))
        c = 1.0 + C @ old[:observed]
    # The replanned path starts with the already executed position, slope and curvature.
    if fixed_head:
        lo[:3] = target[:3]
        hi[:3] = target[:3]
    bounds = list(zip(lo, hi))
    bands = np.vstack((A, -A))
    b = np.r_[hi_ay - need, need - lo_ay]
    m = len(b)
    constraints = np.vstack((bands, C))
    slack_column = np.r_[-np.ones(m), np.zeros(len(c))]
    relaxation = linprog(np.r_[np.zeros(observed), 1.0],
                         A_ub=np.column_stack((constraints, slack_column)), b_ub=np.r_[b, c],
                         bounds=bounds + [(0, None)], method="highs")
    if not relaxation.success:
        raise RuntimeError(f"Acceleration feasibility LP failed: {relaxation.message}")
    minimum = max(0.0, float(relaxation.x[-1]))
    if minimum > ACCEL_TOL:
        return target, minimum, "infeasible"

    tail = len(target) - observed
    constraints = np.pad(constraints, ((0, 0), (0, tail)))
    upper = np.r_[b + minimum + 1e-7, c]
    difference = np.diff(np.eye(len(target)), axis=0) / P.H
    curvature = P.curvature_matrix(k)
    Q = np.eye(len(target)) + difference.T @ difference + 4.0 * curvature.T @ curvature

    def objective(d):
        delta = d - target
        grad = Q @ delta
        return 0.5 * delta @ grad, grad

    feasible = np.r_[relaxation.x[:-1], target[observed:]]
    excess = constraints @ target - upper
    needs_move = excess > 0.0
    improvement = constraints[needs_move] @ (target - feasible)
    initial = feasible
    if np.all(improvement > 0.0):
        fraction = min(1.0, float(np.max(excess[needs_move] / improvement, initial=0.0)))
        initial = target + fraction * (feasible - target)
    row_norm = np.linalg.norm(constraints, axis=1)
    full_bounds = bounds + [(-half_width, half_width)] * tail
    result = minimize(objective, initial, jac=True, method="SLSQP",
                      bounds=full_bounds,
                      constraints=[LinearConstraint(constraints / row_norm[:, None],
                                                    -np.inf, upper / row_norm)],
                      options={"ftol": 1e-10, "maxiter": 100})
    residual = np.max(constraints @ result.x - upper)
    box_lo, box_hi = np.asarray(full_bounds).T
    if (not np.all(np.isfinite(result.x)) or residual > ACCEL_TOL
            or np.any(result.x < box_lo - 1e-8) or np.any(result.x > box_hi + 1e-8)
            or result.fun > objective(initial)[0] + 1e-10):
        return target, minimum, "failed"
    return result.x, minimum, "solved" if result.success else "feasible-iterate"


def run(road, source, constrained):
    preview = None if source == "exact" else DelayedPreview(road, source)
    stats = {
        "windows": 0, "cap_violations": 0, "support_violations": 0, "support_windows": 0,
        "path_ay_peak_mps2": 0.0, "path_jerk_half_second_mps3": 0.0,
        "support_margin_mps2": None, "preview_max_near_ay_error_mps2": 0.0,
        "preview_missed_support_windows": 0,
    }
    correction = {
        "attempted": 0, "accepted": 0, "infeasible": 0, "qp_fallbacks": 0, "qp_feasible_iterates": 0,
        "max_required_relaxation_mps2": 0.0, "worst_relaxation_station_m": None,
    }
    continuity = {}

    def in_focus(i):
        return road.focus[0] <= road.sn[i] <= road.focus[1]

    def adjust(i, k, observed, target, old):
        d, slack, outcome = bounded_path(k, observed, road.v, target, old, P.CORRIDOR)
        if in_focus(i):
            correction["attempted"] += int(outcome != "unchanged")
            correction["accepted"] += int(outcome in ("solved", "feasible-iterate"))
            correction["infeasible"] += int(outcome == "infeasible")
            correction["qp_fallbacks"] += int(outcome == "failed")
            correction["qp_feasible_iterates"] += int(outcome == "feasible-iterate")
            if slack > correction["max_required_relaxation_mps2"]:
                correction["max_required_relaxation_mps2"] = slack
                correction["worst_relaxation_station_m"] = float(road.sn[i])
        return d

    def observe(i, offsets):
        if not in_focus(i):
            return
        stats["windows"] += 1
        k = road.kn[i:i + len(offsets)]
        need, required, _, _ = acceleration_bands(k, road.v)
        ay = need + road.v**2 * (P.curvature_matrix(k) @ offsets)
        peak = float(np.max(np.abs(ay)))
        stats["path_ay_peak_mps2"] = max(stats["path_ay_peak_mps2"], peak)
        stats["cap_violations"] += int(peak > AY_MAX + ACCEL_TOL)
        if preview is not None:
            seen = preview(i)
            near = min(len(need), int(road.v / P.H))
            predicted = road.v**2 * seen[1:near + 1]
            error = float(np.max(np.abs(predicted - need[:near])))
            stats["preview_max_near_ay_error_mps2"] = max(stats["preview_max_near_ay_error_mps2"], error)
            misses = required[:near] & (np.sign(need[:near]) * predicted <= AY_MAX)
            stats["preview_missed_support_windows"] += int(misses.any())
        step = int(np.ceil(0.5 * road.v / P.H))
        if len(ay) > step:
            jerk = np.max(np.abs(ay[step:] - ay[:-step])) / (step * P.H / road.v)
            stats["path_jerk_half_second_mps3"] = max(stats["path_jerk_half_second_mps3"], float(jerk))
        if required.any():
            margin = float(np.min(np.sign(need[required]) * ay[required]) - AY_SUPPORT_MIN)
            stats["support_windows"] += 1
            stats["support_violations"] += int(margin < -ACCEL_TOL)
            previous = stats["support_margin_mps2"]
            stats["support_margin_mps2"] = margin if previous is None else min(previous, margin)

    d = P.plan_receding(road, P.CORRIDOR, view=VIEW_M, continuity_limits=LIMITS,
                        cont_stats=continuity, preview=preview, observe_plan=observe,
                        adjust_plan=adjust if constrained else None)
    assert np.max(np.abs(d)) <= P.CORRIDOR + 1e-8
    return {"path": stats, "correction": correction if constrained else None,
            "continuity": continuity, "vehicle": P.cl_metrics(road, P.closed_loop(road, d))}


def main():
    roads = {road.name: road for road in P.research_roads()}
    roads["S14e-110"] = replace(roads["S14e"], name="S14e-110", v=110.0 / 3.6).build()
    records = []
    for name, source in CASES:
        road = roads[name]
        record = {"road": name, "speed_kmh": road.v * 3.6, "preview": source, "variants": {}}
        for variant, constrained in (("R-limited", False), ("R-ay", True)):
            result = run(road, source, constrained)
            record["variants"][variant] = result
            p, v = result["path"], result["vehicle"]
            c = result["correction"]
            relaxation = "" if c is None else (
                f"  relax {c['max_required_relaxation_mps2']:.3f} ({c['infeasible']}/{p['windows']})")
            print(f"{name:9s} {source:13s} {variant:9s} "
                  f"path peak {p['path_ay_peak_mps2']:.3f}  support {p['support_margin_mps2']}  "
                  f"vehicle peak {v['ay_peak']:.3f}  clear {v['clear_min']:.3f} m{relaxation}", flush=True)
        records.append(record)
    arc_speed = 25.0
    arc_k = np.full(int(3.0 * arc_speed / P.H), 1.0 / 200.0)
    _, arc_relaxation, _ = bounded_path(arc_k, len(arc_k), arc_speed, np.zeros_like(arc_k),
                                       None, P.CORRIDOR, fixed_head=False)
    output = {
        "study": "PP-TS-013",
        "method": "research sensitivity experiment, execution on the exact reference",
        "view_m": VIEW_M,
        "ay_max_mps2": AY_MAX,
        "ay_support_min_mps2": AY_SUPPORT_MIN,
        "continuity_targets": LIMITS,
        "camera": {"period_s": CAMERA_PERIOD_S, "delay_s": CAMERA_DELAY_S,
                   "sample_noise_m": CAMERA_SAMPLE_NOISE_M, "seed": CAMERA_SEED},
        "constant_arc_free_head": {"radius_m": 200.0, "speed_mps": arc_speed,
                                   "grid_points": len(arc_k), "corridor_half_width_m": P.CORRIDOR,
                                   "min_required_relaxation_mps2": arc_relaxation},
        "runs": records,
    }
    Path(__file__).with_name("acceleration_results.json").write_text(
        json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8",
    )


if __name__ == "__main__":
    main()

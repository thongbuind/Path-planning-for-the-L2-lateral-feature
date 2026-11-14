"""Paired PP-TS-013 experiment on preview, continuity and a blocked side.

Run with one BLAS thread. The experiment uses the research geometry and controller.
"""

import json
from pathlib import Path

import numpy as np

import prototype as P

SRS_LIMITS = np.array([0.05, 0.005, 0.0003])  # PP-SWR-100, 101, 102
LIMITS = tuple(0.9 * SRS_LIMITS)
AY_MAX = 2.5  # m/s², PP-SWR-001
AY_SUPPORT_MIN = AY_MAX - 0.2  # m/s², PP-SWR-006 with default epsilon_ay
CASES = (("Rf", 80.0), ("S1f", 80.0), ("S14e", 80.0), ("S1c", 80.0), ("S1f", 150.0))


def evaluate(road, view, corridor, limited):
    continuity = {}
    support_margin = None
    path_ay_peak = 0.0

    def observe(index, offsets):
        nonlocal support_margin, path_ay_peak
        if not road.focus[0] <= road.sn[index] <= road.focus[1]:
            return
        # Interior nodes in the observed horizon, with the same curvature approximation as T7.
        k = road.kn[index + 1:index + len(offsets) - 1]
        ay = road.v**2 * (k + np.diff(offsets, n=2) / P.H**2 + k**2 * offsets[1:-1])
        path_ay_peak = max(path_ay_peak, float(np.max(np.abs(ay), initial=0.0)))
        t = np.arange(1, len(offsets) - 1) * P.H / road.v
        needs_support = (t <= 1.0) & (road.v**2 * np.abs(k) > AY_MAX)
        if needs_support.any():
            margin = float(np.min(np.abs(ay[needs_support]))) - AY_SUPPORT_MIN
            support_margin = margin if support_margin is None else min(support_margin, margin)

    d = P.plan_receding(road, corridor, view=view, cont_stats=continuity,
                        continuity_limits=LIMITS if limited else None, observe_plan=observe)
    lower, upper = corridor
    d_min, d_max = float(d.min()), float(d.max())
    assert lower - 1e-12 <= d_min <= d_max <= upper + 1e-12
    if limited:
        names = ("max", "heading_max", "curvature_max")
        for key, limit in zip(names, LIMITS):
            assert continuity[key] <= limit + 1e-12, (road.name, key, continuity[key])
    return {
        "corridor_m": corridor,
        "d_min_m": d_min,
        "d_max_m": d_max,
        "continuity": continuity,
        "observed_plan": {"ay_peak_mps2": path_ay_peak, "support_margin_mps2": support_margin},
        "vehicle": P.cl_metrics(road, P.closed_loop(road, d)),
    }


def main():
    roads = {road.name: road for road in P.research_roads()}
    records = []
    symmetric = (-P.CORRIDOR, P.CORRIDOR)
    for name, view in CASES:
        road = roads[name]
        variants = {
            "R-cam": evaluate(road, view, symmetric, limited=False),
            "R-limited": evaluate(road, view, symmetric, limited=True),
        }
        if (name, view) == ("S1f", 80.0):
            for side, corridor in (("left", (-P.CORRIDOR, 0.0)), ("right", (0.0, P.CORRIDOR))):
                variants[f"R-limited-blocked-{side}"] = evaluate(road, view, corridor, limited=True)
        centre = P.cl_metrics(road, P.closed_loop(road, np.zeros_like(road.kn)))
        records.append({"road": name, "view_m": view, "centre": centre, "variants": variants})
        for label, result in variants.items():
            c, v = result["continuity"], result["vehicle"]
            print(f"{name:4s} {view:3.0f} m {label:24s} "
                  f"Δd {c['max'] * 1000:5.1f} mm  "
                  f"Δψ {c['heading_max'] * 1000:5.1f} mrad  "
                  f"Δκ {c['curvature_max'] * 1000:5.2f} 10⁻³/m  "
                  f"a_y {v['ay_peak']:.2f}  jerk RMS {v['jerk_rms']:.2f}  "
                  f"clear {v['clear_min']:.2f} m", flush=True)
    output = {
        "study": "PP-TS-013",
        "method": "research prototype with exact reference geometry",
        "profile": P.PROFILE.name,
        "replan_step_m": P.H,
        "srs_limits": SRS_LIMITS.tolist(),
        "limiter_targets": LIMITS,
        "observed_plan_thresholds_mps2": {"ay_max": AY_MAX, "ay_support_min": AY_SUPPORT_MIN},
        "runs": records,
    }
    Path(__file__).with_name("continuity_results.json").write_text(
        json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8",
    )


if __name__ == "__main__":
    main()

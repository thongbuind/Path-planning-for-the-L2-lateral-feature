import argparse
import json
from contextlib import contextmanager
from datetime import datetime
from math import log2, pi, sin
from pathlib import Path

import numpy as np

from eval import case, conclusion, metrics, planner_choice, provenance, runner
from sim import harness
from sim.vehicle import profiles
from sim.vehicle.bicycle import Bicycle, BicycleState

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "verification"
STEPS_US = (1000, 500, 250)
REFERENCE_STEP_US = 62.5
CASES = (("S1", "a", "HWA, curve and straight", "PP-SWR-051"),
         ("S1", "c", "HWA, curve at the lateral acceleration limit", "PP-SWR-051"),
         ("S5", "a", "ELK intervention", "PP-SWR-086"))
PARAMETERS = ("c_front", "c_rear", "yaw_inertia", "eps_delay")
FACTORS = (0.8, 1.2)


def _inputs():
    return (
        ("steady turn", 25.0, 8.0, lambda t: 0.012),
        ("step steer", 30.0, 6.0, lambda t: 0.02 if t >= 0.5 else 0.0),
        ("sine steer 0.4 Hz", 30.0, 10.0, lambda t: 0.02 * sin(2 * pi * 0.4 * t)),
    )


def integrate(step_us: float, speed: float, duration: float, steering) -> dict[int, tuple]:
    car = Bicycle(profiles.PROFILES["VP-0"], BicycleState(0.0, 0.0, 0.0, 0.0, 0.0))
    per_ms = round(1000.0 / step_us)
    out = {}
    for ms in range(round(duration * 1000)):
        delta = steering(ms * 1e-3)
        for _ in range(per_ms):
            car.step(step_us * 1e-6, delta, speed)
        s = car.state
        out[ms + 1] = (s.x, s.y, s.psi, s.v_y, s.r, car.a_y)
    return out


def solver_error(steps_us=STEPS_US, reference_us=REFERENCE_STEP_US, inputs=None) -> list[dict]:
    rows = []
    for name, speed, duration, steering in inputs or _inputs():
        ref = integrate(reference_us, speed, duration, steering)
        errors = {}
        for step in steps_us:
            run = integrate(step, speed, duration, steering)
            ms = sorted(ref)
            diff = np.array([[run[k][i] - ref[k][i] for i in range(6)] for k in ms])
            position = np.hypot(diff[:, 0], diff[:, 1])
            errors[step] = {"position_m": float(position.max()), "heading_rad": float(abs(diff[:, 2]).max()),
                            "yaw_rate_rad_s": float(abs(diff[:, 4]).max()), "a_y_m_s2": float(abs(diff[:, 5]).max())}
        order = {}
        for k in ("position_m", "heading_rad", "yaw_rate_rad_s", "a_y_m_s2"):
            coarse, fine = errors[steps_us[0]][k], errors[steps_us[1]][k]
            order[k] = log2(coarse / fine) if fine > 0 and coarse > 0 else None
        rows.append({"input": name, "speed_mps": speed, "duration_s": duration,
                     "errors": {str(s): e for s, e in errors.items()}, "observed_order": order})
    return rows


@contextmanager
def _step(step_us: int):
    """Khi đổi bước tích phân của harness, pha của các khối vẫn nằm trên lưới 1 ms."""
    saved = harness.STEP_US, harness.random_phase_us
    harness.STEP_US = step_us
    harness.random_phase_us = lambda rng, period_us, _step: int(rng.integers(0, period_us // 1000)) * 1000
    try:
        yield
    finally:
        harness.STEP_US, harness.random_phase_us = saved


@contextmanager
def _perturbed(parameter: str, factor: float):
    """Khi quét eps_delay, chỉ đổi độ trễ actuator thật. Planner vẫn nhận VehicleConfig danh định."""
    saved = (profiles.C_FRONT_PER_2000KG, profiles.C_REAR_PER_2000KG, profiles.YAW_INERTIA_FACTOR)
    try:
        if parameter == "c_front":
            profiles.C_FRONT_PER_2000KG = saved[0] * factor
        elif parameter == "c_rear":
            profiles.C_REAR_PER_2000KG = saved[1] * factor
        elif parameter == "yaw_inertia":
            profiles.YAW_INERTIA_FACTOR = saved[2] * factor
        elif parameter == "eps_delay":
            yield profiles.ACTUATOR_DELAY_S * factor
            return
        elif parameter != "nominal":
            raise ValueError(parameter)
        yield None
    finally:
        profiles.C_FRONT_PER_2000KG, profiles.C_REAR_PER_2000KG, profiles.YAW_INERTIA_FACTOR = saved


def _scenario(sid: str, variant: str, eps_delay=None):
    from dataclasses import replace
    scenario = case.resolve({"kind": "catalog", "sid": sid, "v": variant})
    return replace(scenario, eps_delay_s=eps_delay) if eps_delay is not None else scenario


def _summary(log, sid: str, variant: str, criterion: str) -> dict:
    result = metrics.evaluate(log)
    scope = runner.run_scope([sid, variant], [])
    record = {"case": result.scenario, "profile": log.scenario.profile, "seed": result.seed,
              "result": result.to_dict(), "scope": sorted(scope), "mcap": None, "rerun": ""}
    inside, _, _ = conclusion.run_failures(record)
    key = next((c for c in result.criteria if c.id == criterion and c.applicable), None)
    return {"vehicle_offset_max_m": result.info.get("vehicle_offset_max_m"),
            "key_criterion": criterion, "key_metric": None if key is None else key.metric,
            "key_value": None if key is None else float(key.value),
            "a_y_max_m_s2": float(np.max(np.abs(log.a_y))),
            "in_scope_failures": sorted({f["requirement"] for f in inside})}


def _grid(log) -> tuple[np.ndarray, np.ndarray]:
    t = np.asarray(log.t_us)
    mask = t % 1000 == 0
    return t[mask], np.asarray(log.rear)[mask][:, :2]


def _divergence(log, ref) -> float:
    (ta, pa), (tb, pb) = _grid(log), _grid(ref)
    n = min(len(ta), len(tb))
    return float(np.hypot(pa[:n, 0] - pb[:n, 0], pa[:n, 1] - pb[:n, 1]).max())


def closed_loop_error(planner, seed: int = 1) -> list[dict]:
    rows = []
    for sid, variant, purpose, criterion in CASES:
        logs = {}
        for step in STEPS_US:
            with _step(step):
                logs[step] = harness.Harness(_scenario(sid, variant), planner, seed).run()
        ref = logs[STEPS_US[-1]]
        rows.append({"case": f"{sid}{variant}", "purpose": purpose, "criterion": criterion,
                     "divergence_from_250us_m": {str(s): _divergence(logs[s], ref) for s in STEPS_US[:-1]},
                     "metrics": {str(s): _summary(logs[s], sid, variant, criterion) for s in STEPS_US}})
    return rows


def sensitivity(planner, seed: int = 1) -> list[dict]:
    rows = []
    for sid, variant, purpose, criterion in CASES:
        with _perturbed("nominal", 1.0):
            base_log = harness.Harness(_scenario(sid, variant), planner, seed).run()
        base = _summary(base_log, sid, variant, criterion)
        entry = {"case": f"{sid}{variant}", "purpose": purpose, "criterion": criterion, "nominal": base, "runs": []}
        for parameter in PARAMETERS:
            for factor in FACTORS:
                with _perturbed(parameter, factor) as eps:
                    log = harness.Harness(_scenario(sid, variant, eps), planner, seed).run()
                one = _summary(log, sid, variant, criterion)
                entry["runs"].append({
                    "parameter": parameter, "factor": factor, **one,
                    "divergence_m": _divergence(log, base_log),
                    "d_key_value": _delta(one["key_value"], base["key_value"]),
                    "verdict_changed": one["in_scope_failures"] != base["in_scope_failures"]})
        rows.append(entry)
    return rows


def _delta(a, b):
    return None if a is None or b is None else float(a - b)


def _f(value, digits=3) -> str:
    return "—" if value is None else f"{value:.{digits}g}"


def calculation_summary(solver, loop) -> list[str]:
    lines = ["# Calculation verification", "", "## Vehicle model, RK4 against 1/16 ms", "",
             "| Input | Step [ms] | Position [m] | Heading [rad] | Yaw rate [rad/s] | a_y [m/s²] |", "|---|---|---|---|---|---|"]
    for row in solver:
        for step, e in row["errors"].items():
            lines.append(f"| {row['input']} | {int(step) / 1000:g} | {_f(e['position_m'])} | {_f(e['heading_rad'])} | "
                         f"{_f(e['yaw_rate_rad_s'])} | {_f(e['a_y_m_s2'])} |")
        o = row["observed_order"]
        lines.append(f"| {row['input']} | observed order (1 → 0.5 ms) | {_f(o['position_m'], 2)} | {_f(o['heading_rad'], 2)} | "
                     f"{_f(o['yaw_rate_rad_s'], 2)} | {_f(o['a_y_m_s2'], 2)} |")
    lines += ["", "## Closed loop, steps 1, 0.5, 0.25 ms", "",
              "| Case | Step [ms] | Distance to the 0.25 ms run [m] | Key criterion value [m] | a_y max [m/s²] | In-scope failures |",
              "|---|---|---|---|---|---|"]
    for row in loop:
        for step, m in row["metrics"].items():
            far = row["divergence_from_250us_m"].get(step)
            lines.append(f"| {row['case']} ({row['criterion']}) | {int(step) / 1000:g} | {_f(far)} | "
                         f"{_f(m['key_value'], 5)} | {_f(m['a_y_max_m_s2'])} | {', '.join(m['in_scope_failures']) or '—'} |")
    return lines


def sensitivity_summary(rows) -> list[str]:
    lines = ["# Sensitivity", "", "Parameter scaled by 0.8 and 1.2; seed 1; the planner keeps the nominal VehicleConfig.", "",
             "| Case | Parameter | Factor | Distance to nominal [m] | Key criterion value [m] | Δ key value [m] | In-scope failures | Verdict changed |",
             "|---|---|---|---|---|---|---|---|"]
    for entry in rows:
        nominal = entry["nominal"]
        lines.append(f"| {entry['case']} ({entry['criterion']}) | nominal | 1 | — | {_f(nominal['key_value'], 5)} | — | "
                     f"{', '.join(nominal['in_scope_failures']) or '—'} | — |")
        for r in entry["runs"]:
            lines.append(f"| {entry['case']} | {r['parameter']} | {r['factor']:g} | {_f(r['divergence_m'])} | "
                         f"{_f(r['key_value'], 5)} | {_f(r['d_key_value'])} | {', '.join(r['in_scope_failures']) or '—'} | "
                         f"{'yes' if r['verdict_changed'] else 'no'} |")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Verification of the simulator itself (Simulation Handbook 13, 14; R171 Annex 5 3.6.3, "
            "3.6.4)."
        ),
    )
    parser.add_argument("kind", choices=("calculation", "sensitivity"))
    parser.add_argument("--seed", type=int, default=1)
    planner_choice.add_argument(parser)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    planner = planner_choice.resolve(args.planner)
    manifest = provenance.make("verification", args.kind, {"seed": args.seed})
    manifest["libraries"] = provenance.library_infos(planner, external=args.planner is not None)
    out = args.out / f"{datetime.now():%Y%m%d-%H%M}-{args.kind}-{manifest['git']['short'] or 'nogit'}"
    out.mkdir(parents=True, exist_ok=True)
    if args.kind == "calculation":
        solver = solver_error()
        loop = closed_loop_error(planner, args.seed)
        data, lines = {"solver": solver, "closed_loop": loop}, calculation_summary(solver, loop)
    else:
        rows = sensitivity(planner, args.seed)
        data, lines = {"cases": rows}, sensitivity_summary(rows)
    (out / "result.json").write_text(json.dumps({"manifest": manifest, **data}, indent=1, ensure_ascii=False,
                                                default=str) + "\n", encoding="utf-8")
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nWritten to {out}")


if __name__ == "__main__":
    main()

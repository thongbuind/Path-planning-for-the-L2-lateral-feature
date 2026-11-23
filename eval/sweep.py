"""Mỗi bộ calibration có thư viện riêng vì tham số được biên dịch vào planner (PP-ADR-013)."""

import argparse
import json
import math
import subprocess
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, replace
from pathlib import Path

import yaml

from eval import calibration as cal_io
from eval import loader, provenance

ROOT = Path(__file__).resolve().parents[1]
SUITE_DIR = ROOT / "benchmark" / "suites"
SWEEP_DIR = ROOT / "build" / "sweep"
BASE_CALIBRATION = ROOT / "planner" / "calibration" / "calibration.yaml"

RANK_TARGETS = ("PP-SWR-050", "PP-SWR-125", "PP-SWR-002", "PP-SWR-053")
JERK = "PP-SWR-003"


@dataclass(frozen=True)
class CalSet:
    name: str
    values: dict
    cmake: tuple = ()
    loops: tuple = ()  # Rỗng là mọi lượt; ("open",) cho nghiệm tham chiếu chỉ chạy vòng hở.


def load_suite(suite_id: str) -> dict:
    return yaml.safe_load((SUITE_DIR / f"{suite_id}.yaml").read_text(encoding="utf-8"))


def base_values(names) -> dict:
    params = yaml.safe_load(BASE_CALIBRATION.read_text(encoding="utf-8"))["parameters"]
    return {n: params[n]["value"] for n in names}


def one_at_a_time(suite: dict) -> list[CalSet]:
    base = base_values(suite["parameters"])
    sets = [CalSet("start", {})]
    for name, levels in suite["parameters"].items():
        for value in levels:
            if not math.isclose(float(value), float(base[name]), rel_tol=1e-9):
                sets.append(CalSet(f"{name}={value}", {name: value}))
    return sets


SIM_KEYS = ("camera_view_m", "camera_view_start_m", "camera_latency_ms", "camera_jitter_ms",
            "yaw_filter_delay_ms", "function_requests_latency_ms")
RUN_TEXT_KEYS = ("acc", "profile", "loop")
RUN_SIM_KEYS = SIM_KEYS + RUN_TEXT_KEYS


def check_sim(scenario) -> None:
    from eval import openx
    from sim.vehicle.profiles import PROFILES
    ok = (scenario.profile in PROFILES
          and 10.0 <= scenario.camera_view_m <= openx.CAMERA_VIEW_MAX_M
          and 0.0 <= scenario.camera_view_start_m < scenario.camera_view_m
          and 0.0 <= scenario.camera_latency_ms <= 1000.0
          and 0.0 <= scenario.camera_jitter_ms <= scenario.camera_latency_ms + 50.0
          and 0.0 <= scenario.yaw_filter_delay_ms <= 500.0
          and 0.0 <= scenario.function_requests_latency_ms <= 500.0
          and scenario.acc in ("off", "on", "ignore_limits")
          and scenario.loop in ("open", "closed")
          and 0.1 <= scenario.road_mu <= 1.2
          and (scenario.eps_delay_s is None or 0.0 <= scenario.eps_delay_s <= 0.5)
          and 1.0 <= scenario.perception_noise_scale <= 5.0)
    if not ok:
        raise ValueError("simulator values outside the supported ranges")


def split_run(run: list) -> tuple[list, dict]:
    spec, sim = list(run), {}
    if spec and isinstance(spec[-1], dict):
        sim = dict(spec.pop())
    unknown = set(sim) - set(RUN_SIM_KEYS)
    if unknown or len(spec) not in (2, 4):
        raise ValueError(f"invalid run {run!r}")
    return spec, sim


def load_run(run: list, *, object_list_on_empty_road: bool = False):
    spec, sim = split_run(run)
    scenario = loader.load(spec[0], spec[1])
    if len(spec) > 2:
        scenario = loader.with_fault(scenario, spec[2], spec[3])
    if object_list_on_empty_road:
        scenario = replace(scenario, object_list_on_empty_road=True)
    if sim:
        scenario = replace(scenario, **{k: (str(v) if k in RUN_TEXT_KEYS else float(v))
                                        for k, v in sim.items()},
                           name=scenario.name + " [" + ", ".join(f"{k}={v}" for k, v in sim.items()) + "]")
        check_sim(scenario)
    return scenario


def scope_of(suite: dict, run: list) -> set[str]:
    scope = suite["scope"]
    spec, _ = split_run(run)
    key = spec[2] if len(spec) > 2 else spec[0]
    return set(scope["always"]) | set(scope.get(key, []))


LAB_DIR = ROOT / "research" / "generators"


def _lab_calibration(cal_set: CalSet, values: dict, folder: Path) -> list[str]:
    """Giá trị cho tham số riêng của generator lab: bản chép generator.yaml, truyền qua PP_T7_LAB_CALIBRATION."""
    if not values:
        return []
    cmake = dict(cal_set.cmake)
    if cmake.get("PP_T7") != "lab" or not cmake.get("PP_T7_LAB"):
        raise KeyError(f"{cal_set.name}: unknown calibration parameters {sorted(values)}")
    spec = yaml.safe_load((LAB_DIR / cmake["PP_T7_LAB"] / "generator.yaml").read_text(encoding="utf-8"))
    own = spec.get("calibration") or {}
    unknown = sorted(set(values) - set(own))
    if unknown:
        raise KeyError(f"{cal_set.name}: not a parameter of {cmake['PP_T7_LAB']}: {unknown}")
    for name, value in values.items():
        own[name]["value"] = value
    lab_file = folder / "generator.yaml"
    lab_file.write_text(yaml.safe_dump(spec, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return [f"-DPP_T7_LAB_CALIBRATION={lab_file}"]


def _build(cal_set: CalSet, folder: Path) -> Path:
    params = yaml.safe_load(BASE_CALIBRATION.read_text(encoding="utf-8"))
    lab_values = {}
    for name, value in cal_set.values.items():
        if name in params["parameters"]:
            params["parameters"][name]["value"] = value
        else:
            lab_values[name] = value
    folder.mkdir(parents=True, exist_ok=True)
    cal_file = folder / "calibration.yaml"
    cal_file.write_text(yaml.safe_dump(params, sort_keys=False, allow_unicode=True), encoding="utf-8")
    build = folder / "build"
    subprocess.run(["cmake", "-S", str(ROOT / "planner"), "-B", str(build),
                    f"-DPP_CALIBRATION_FILE={cal_file}", "-DPP_BUILD_TESTS=OFF",
                    "-DPP_BUILD_LAYOUT_PROBE=OFF", "-DCMAKE_BUILD_TYPE=Release"]
                   + [f"-D{key}={value}" for key, value in cal_set.cmake]
                   + _lab_calibration(cal_set, lab_values, folder),
                   check=True, capture_output=True)
    subprocess.run(["cmake", "--build", str(build)], check=True, capture_output=True)
    return build


def _paired_evidence(log, result, scope: set[str]) -> dict:
    """Giữ đơn vị, điều kiện áp dụng và thời điểm để so các run ghép cặp."""
    from dataclasses import asdict

    import numpy as np

    def metric_row(metric) -> dict:
        row = asdict(metric)
        value = metric.value
        row["value"] = float(value) if value is not None and math.isfinite(value) else None
        if "applicable" in row:
            row["applicable"] = bool(row["applicable"])
            row["passed"] = bool(row["passed"])
        return row

    compute_ms = [cycle.compute_lcc_ns / 1.0e6 for cycle in log.cycles]
    timing = {}
    if compute_ms:
        p50, p95, p99 = np.percentile(compute_ms, (50, 95, 99))
        timing = {"p50": float(p50), "p95": float(p95), "p99": float(p99), "max": max(compute_ms)}
    return {
        "profile": log.scenario.profile,
        "acc": log.scenario.acc,
        "loop": log.scenario.loop,
        "scored": bool(result.scored),
        "issues": result.issues,
        "case_failures": result.case_failures,
        "criteria": [metric_row(c) for c in result.criteria if c.id in scope],
        "targets": [metric_row(t) for t in result.targets if t.id in scope],
        "timed_cycles": len(compute_ms),
        "compute_lcc_ms": timing,
        "hwa_share_after_request": result.info.get("hwa_share_after_request"),
        "lcc_driving_cycles": result.info.get("lcc_driving_cycles"),
        "lcc_requested_cycles": result.info.get("lcc_requested_cycles"),
        "path_near_limit_share": result.info.get("path_near_limit_share"),
        "vehicle": {k: result.info.get(k) for k in
                    ("ay_vehicle_r79_max", "jerk_vehicle_r79_max", "vehicle_offset_max_m",
                     "ay_vehicle_r79_over_sustained_s", "ay_vehicle_r79_within_limits")},
    }


def run_line(suite: dict, run: list, seed: int, planner, req_cal: dict, folder: Path, name: str) -> dict:
    """Một lượt của suite: tiêu chí trong phạm vi, giá trị target và, với paired_evidence, bằng chứng ghép
    cặp; ở vòng hở ghi output từng chu kỳ vào folder/name (eval.output_diff)."""
    from eval import metrics, proposed
    from sim.harness import Harness

    scenario = load_run(run, object_list_on_empty_road=suite.get("object_list_on_empty_road", False))
    scope = scope_of(suite, run)
    log = Harness(scenario, planner, seed).run()
    result = metrics.evaluate(log, req_cal)
    result.criteria.extend(proposed.criteria(result, suite.get("proposed", [])))
    result.targets.extend(proposed.targets(log, suite.get("proposed_targets", [])))
    failed = [c.id for c in result.criteria
              if c.id in scope and c.applicable and not c.passed]
    values = {t.id: t.value for t in result.targets if t.id in scope}
    values[JERK] = next(c.value for c in result.criteria if c.id == JERK)
    row = {"run": scenario.name, "seed": seed, "failed": failed, "values": values}
    if suite.get("paired_evidence"):
        row["spec"] = run
        row.update(_paired_evidence(log, result, scope))
        if scenario.loop == "open":
            from eval import output_diff
            output_diff.save(folder / name, output_diff.cycle_outputs(log))
            row["open_loop_file"] = name
    return row


def run_set(suite_id: str, cal_set: CalSet, which: str, root: Path | None = None) -> dict:
    suite = load_suite(suite_id)
    folder = (root or SWEEP_DIR / suite_id) / cal_set.name.replace("=", "_")
    lib = _build(cal_set, folder)
    from adapters.sil.sil_planner import PlannerLibraries

    planner = PlannerLibraries.at(lib)
    params = yaml.safe_load((folder / "calibration.yaml").read_text(encoding="utf-8"))["parameters"]
    req_cal = cal_io.from_parameters(params)
    part = suite[which]
    runs = []
    for index, run in enumerate(part["runs"]):
        scenario = load_run(run, object_list_on_empty_road=suite.get("object_list_on_empty_road", False))
        if cal_set.loops and scenario.loop not in cal_set.loops:
            continue
        for seed in part["seeds"]:
            runs.append(run_line(suite, run, seed, planner, req_cal, folder,
                                 f"open_loop/{which}/{index:03d}_s{seed}.npz"))
    summary = summarise(runs)
    out = {"set": cal_set.name, "values": cal_set.values, "cmake": dict(cal_set.cmake),
           "loops": list(cal_set.loops), "part": which, "library": str(lib), "summary": summary, "runs": runs}
    (folder / f"{which}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False),
                                          encoding="utf-8")
    return out


def summarise(runs: list[dict]) -> dict:
    worst = {}
    for r in runs:
        for k, v in r["values"].items():
            if v is not None and not (isinstance(v, float) and math.isnan(v)):
                worst[k] = max(worst.get(k, -math.inf), v)
    return {"failed": sum(len(r["failed"]) for r in runs),
            "failed_ids": sorted({f"{r['run']}:{i}" for r in runs for i in r["failed"]}),
            "worst": worst}


def rank_key(summary: dict) -> tuple:
    worst = summary["worst"]
    return (summary["failed"],) + tuple(round(worst.get(t, 0.0), 4) for t in RANK_TARGETS) \
        + (round(worst.get(JERK, 0.0), 3),)


def combined_sets(suite: dict, results: list[dict]) -> list[CalSet]:
    """Thử bộ giá trị tốt nhất, rồi trả từng tham số về giá trị đầu để đo riêng ảnh hưởng."""
    best = {}
    start_key = rank_key(next(r for r in results if r["set"] == "start")["summary"])
    for name in suite["parameters"]:
        own = [r for r in results if name in r["values"]]
        winner = min(own, key=lambda r: rank_key(r["summary"]), default=None)
        if winner is not None and rank_key(winner["summary"]) < start_key:
            best[name] = winner["values"][name]
    if not best:
        return []
    sets = [CalSet("combined", dict(best))]
    if len(best) > 1:
        for name in best:
            sets.append(CalSet(f"combined-without-{name}",
                               {k: v for k, v in best.items() if k != name}))
    return sets


def _table(results: list[dict]) -> list[str]:
    cols = ("PP-SWR-050", "PP-SWR-125", "PP-SWR-002", "PP-SWR-053", JERK)
    lines = ["| Bộ | Trượt | " + " | ".join(cols) + " |", "|---" * (len(cols) + 2) + "|"]
    for r in sorted(results, key=lambda r: rank_key(r["summary"])):
        w = r["summary"]["worst"]
        cells = [f"{w[c]:.4g}" if c in w and math.isfinite(w[c]) else "—" for c in cols]
        lines.append(f"| {r['set']} | {r['summary']['failed']} | " + " | ".join(cells) + " |")
    return lines


def main() -> None:
    from adapters.sil.sil_planner import PlannerLibraries

    parser = argparse.ArgumentParser(
        description="Calibration sweep (Software Qualification Test Specification 7).",
    )
    parser.add_argument("suite", help="Suite id in benchmark/suites, e.g. P1")
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--record", action="store_true",
                        help="Official run: clean working tree; copy to research/runs")
    args = parser.parse_args()
    suite = load_suite(args.suite)
    out_dir = SWEEP_DIR / args.suite
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = provenance.make("sweep", args.suite, {"jobs": args.jobs})
    if args.record:
        provenance.preflight(manifest)

    with ProcessPoolExecutor(max_workers=args.jobs) as pool:
        sets = one_at_a_time(suite)
        print(f"Phase 1: {len(sets)} sets", flush=True)
        phase1 = list(pool.map(run_set, [args.suite] * len(sets), sets, ["tuning"] * len(sets)))
        for r in phase1:
            print(f"  {r['set']:28s} failed {r['summary']['failed']}", flush=True)
        combo = combined_sets(suite, phase1)
        print(f"Phase 2: {len(combo)} sets", flush=True)
        phase2 = list(pool.map(run_set, [args.suite] * len(combo), combo, ["tuning"] * len(combo)))
        tuning = phase1 + phase2
        best = min(tuning, key=lambda r: rank_key(r["summary"]))
        print(f"Best on tuning: {best['set']}; scoring start and best on the test set", flush=True)
        finals = [CalSet("start", {})]
        if best["set"] != "start":
            finals.append(CalSet(best["set"], best["values"]))
        test = list(pool.map(run_set, [args.suite] * len(finals), finals, ["test"] * len(finals)))

    lines = [f"# Sweep {args.suite}", "", f"Best on tuning: **{best['set']}** {best['values']}", "",
             "## Tuning set (worst over runs and seeds)", ""] + _table(tuning)
    lines += ["", "## Test set", ""] + _table(test)
    for r in tuning + test:
        if r["summary"]["failed_ids"]:
            lines.append(f"- {r['part']} {r['set']}: " + ", ".join(r["summary"]["failed_ids"]))
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out_dir / "results.json").write_text(json.dumps(tuning + test, indent=1, ensure_ascii=False),
                                          encoding="utf-8")
    manifest["libraries"] = [
        info for lib in sorted({r["library"] for r in tuning + test})
        for info in provenance.library_infos(PlannerLibraries.at(Path(lib)))
    ]
    manifest["best"] = {"set": best["set"], "values": best["values"]}
    provenance.write(manifest, out_dir)
    print(f"Summary: {out_dir / 'summary.md'}", flush=True)
    if args.record:
        failed = sum(r["summary"]["failed"] for r in test)
        dest = provenance.record(manifest, {"summary.md": out_dir / "summary.md",
                                            "results.json": out_dir / "results.json"},
                                 f"Tốt nhất trên bộ chỉnh: {best['set']}; trượt trên bộ kiểm: {failed}")
        print(f"Recorded: {dest}", flush=True)


if __name__ == "__main__":
    main()

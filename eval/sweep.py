"""Calibration sweep (Software Qualification Test Specification 7).

    python3 -m eval.sweep P1 --jobs 2

Each calibration set is built into its own planner library (the calibration is a
constant data set built in, PP-ADR-013) and run on the tuning set of the suite. Phase 1
changes one parameter at a time; phase 2 combines the best values; the best set and the
start set are then scored on the test set. Ranking follows section 9: requirements first,
then safety targets, then comfort targets.

Writes build/sweep/<suite>/: one folder per set (calibration.yaml, build/, result.json),
summary.md, results.json and manifest.json. --record makes it an official run
(research/README.md).
"""

import argparse
import json
import math
import os
import subprocess
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import yaml

from eval import calibration as cal_io
from eval import loader, provenance

ROOT = Path(__file__).resolve().parents[1]
SUITE_DIR = ROOT / "benchmark" / "suites"
SWEEP_DIR = ROOT / "build" / "sweep"
BASE_CALIBRATION = ROOT / "planner" / "calibration" / "calibration.yaml"
LIB_NAME = "libpp_planner.dylib" if os.uname().sysname == "Darwin" else "libpp_planner.so"

# Ranking order of section 9 after the requirement count: safety, then comfort.
RANK_TARGETS = ("PP-SWR-050", "PP-SWR-125", "PP-SWR-002", "PP-SWR-053")
JERK = "PP-SWR-003"


@dataclass(frozen=True)
class CalSet:
    name: str
    values: dict       # parameter -> value, in the units of calibration.yaml
    cmake: tuple = ()  # (cache entry, value) pairs for build-time choices (trade studies)


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


def scope_of(suite: dict, run: list) -> set[str]:
    scope = suite["scope"]
    key = run[2] if len(run) > 2 else run[0]
    return set(scope["always"]) | set(scope.get(key, []))


def _build(cal_set: CalSet, folder: Path) -> Path:
    params = yaml.safe_load(BASE_CALIBRATION.read_text(encoding="utf-8"))
    for name, value in cal_set.values.items():
        params["parameters"][name]["value"] = value
    folder.mkdir(parents=True, exist_ok=True)
    cal_file = folder / "calibration.yaml"
    cal_file.write_text(yaml.safe_dump(params, sort_keys=False, allow_unicode=True), encoding="utf-8")
    build = folder / "build"
    subprocess.run(["cmake", "-S", str(ROOT / "planner"), "-B", str(build),
                    f"-DPP_CALIBRATION_FILE={cal_file}", "-DPP_BUILD_TESTS=OFF",
                    "-DPP_BUILD_LAYOUT_PROBE=OFF", "-DCMAKE_BUILD_TYPE=Release"]
                   + [f"-D{key}={value}" for key, value in cal_set.cmake],
                   check=True, capture_output=True)
    subprocess.run(["cmake", "--build", str(build)], check=True, capture_output=True)
    return build / LIB_NAME


def run_set(suite_id: str, cal_set: CalSet, which: str, root: Path | None = None) -> dict:
    """Builds the set and runs one part of the suite ('tuning' or 'test'); in a worker."""
    suite = load_suite(suite_id)
    folder = (root or SWEEP_DIR / suite_id) / cal_set.name.replace("=", "_")
    lib = _build(cal_set, folder)
    os.environ["PP_PLANNER_LIB"] = str(lib)
    # Imported after the library is chosen.
    from adapters.sil.sil_planner import SilPlanner
    from eval import metrics
    from sim.harness import Harness

    params = yaml.safe_load((folder / "calibration.yaml").read_text(encoding="utf-8"))["parameters"]
    req_cal = cal_io.from_parameters(params)
    part = suite[which]
    runs = []
    for run in part["runs"]:
        scenario = loader.load(run[0], run[1])
        if len(run) > 2:
            scenario = loader.with_fault(scenario, run[2], run[3])
        scope = scope_of(suite, run)
        for seed in part["seeds"]:
            result = metrics.evaluate(Harness(scenario, SilPlanner, seed).run(), req_cal)
            failed = [c.id for c in result.criteria
                      if c.id in scope and c.applicable and not c.passed]
            values = {t.id: t.value for t in result.targets if t.id in scope}
            values[JERK] = next(c.value for c in result.criteria if c.id == JERK)
            runs.append({"run": scenario.name, "seed": seed, "failed": failed, "values": values})
    summary = summarise(runs)
    out = {"set": cal_set.name, "values": cal_set.values, "cmake": dict(cal_set.cmake),
           "part": which, "library": str(lib), "summary": summary, "runs": runs}
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
    """Best value of each parameter together, and that set with each changed parameter put
    back to its start value (to see which change matters)."""
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
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
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
    manifest["libraries"] = [provenance.library_info(Path(lib))
                             for lib in sorted({r["library"] for r in tuning + test})]
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

"""Coverage matrix: many scenario runs with the delivered planner library.

    python3 -m eval.matrix M1 --jobs 2

Runs every (scenario, variant[, fault], longitudinal mode, profile, seed) of a suite in
benchmark/suites and writes build/matrix/<suite>/summary.md and runs.json. Each run is
judged with the scope of the named sweep suite (Kiểm chứng column of the SRS); all other
criteria are reported as information.
"""

import argparse
import json
import math
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path

import yaml

from eval import loader, sweep

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "build" / "matrix"
INFO = ("vehicle_offset_max_m", "ay_need_at_car_max", "speed_min_mps", "decel_max_mps2",
        "offset_at_hwa_start_m")


def expand(suite: dict) -> list[dict]:
    jobs = []
    for block in suite["blocks"]:
        for run in block["runs"]:
            for acc in block["acc"]:
                for profile in block.get("profiles", suite["profiles"]):
                    for seed in block.get("seeds", suite["seeds"]):
                        jobs.append({"run": list(run), "acc": acc, "profile": profile, "seed": seed})
    return jobs


def scope(suite: dict, run: list) -> set[str]:
    base = sweep.scope_of(sweep.load_suite(suite["scope_from"]), run)
    key = run[2] if len(run) > 2 else run[0]
    return base | set(suite.get("extra_scope", {}).get(key, []))


def run_one(suite_id: str, job: dict) -> dict:
    from adapters.sil.sil_planner import SilPlanner
    from eval import metrics
    from sim.harness import Harness

    suite = yaml.safe_load((sweep.SUITE_DIR / f"{suite_id}.yaml").read_text(encoding="utf-8"))
    run = job["run"]
    scenario = loader.load(run[0], run[1])
    if len(run) > 2:
        scenario = loader.with_fault(scenario, run[2], run[3])
    scenario = replace(scenario, acc=job["acc"], profile=job["profile"])
    result = metrics.evaluate(Harness(scenario, SilPlanner, job["seed"]).run())
    in_scope = scope(suite, run)
    failed = [c.id for c in result.criteria if c.applicable and not c.passed and c.id in in_scope]
    other = [c.id for c in result.criteria if c.applicable and not c.passed and c.id not in in_scope]
    return {**job, "name": scenario.name, "failed": failed, "failed_out_of_scope": other,
            "targets": {t.id: t.value for t in result.targets},
            "criteria": {c.id: c.value for c in result.criteria if c.applicable},
            "info": {k: result.info.get(k) for k in INFO}}


def _fmt(v, digits=3):
    if v is None or (isinstance(v, float) and not math.isfinite(v)):
        return "—"
    return f"{v:.{digits}g}" if isinstance(v, float) else str(v)


def summary(results: list[dict]) -> list[str]:
    lines = ["| Chạy | ACC | Profile | Seed | Trượt (trong phạm vi) | Trượt ngoài phạm vi | Lệch xe [m] | DLC min [m] | a_y cần tại xe [m/s²] | v min [m/s] | Báo trước [s] |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        lines.append(f"| {r['name']} | {r['acc']} | {r['profile']} | {r['seed']} | "
                     f"{', '.join(r['failed']) or '—'} | {', '.join(r['failed_out_of_scope']) or '—'} | "
                     f"{_fmt(r['info']['vehicle_offset_max_m'])} | {_fmt(r['criteria'].get('PP-SWR-051'))} | "
                     f"{_fmt(r['info']['ay_need_at_car_max'])} | {_fmt(r['info']['speed_min_mps'])} | "
                     f"{_fmt(r['targets'].get('PP-SWR-064'))} |")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("suite")
    parser.add_argument("--jobs", type=int, default=1)
    args = parser.parse_args()
    suite = yaml.safe_load((sweep.SUITE_DIR / f"{args.suite}.yaml").read_text(encoding="utf-8"))
    jobs = expand(suite)
    print(f"{len(jobs)} runs", flush=True)
    with ProcessPoolExecutor(max_workers=args.jobs) as pool:
        results = list(pool.map(run_one, [args.suite] * len(jobs), jobs, chunksize=4))
    out = OUT_DIR / args.suite
    out.mkdir(parents=True, exist_ok=True)
    (out / "runs.json").write_text(json.dumps(results, indent=1, ensure_ascii=False), encoding="utf-8")
    failed = [r for r in results if r["failed"]]
    head = [f"# Matrix {args.suite}", "", f"{len(results)} runs; {len(failed)} with an in-scope failure.", ""]
    (out / "summary.md").write_text("\n".join(head + summary(results)) + "\n", encoding="utf-8")
    print(f"{len(failed)} runs with in-scope failures; summary: {out / 'summary.md'}", flush=True)


if __name__ == "__main__":
    main()

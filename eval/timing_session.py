"""Phiên đo thời gian tính của PP-TS-031 (IMPLEMENTATION-PLAN.md GĐ 5.2).

1 job, các dòng vòng kín S1f và S1c của phần test, seed của phần test, lặp 3 lần; mỗi lượt chạy mọi cấu hình
theo thứ tự xoay vòng để nhiễu của máy (nhiệt, tiến trình khác) không dồn vào một cấu hình. Chỉ cấu hình mặc
định của mỗi thuật toán và mỗi mức số vòng (không có lưới, không có nghiệm tham chiếu). Bản build thường,
không telemetry. Kết quả: p99 của từng lượt; eval.campaign đọc `timing.json` và báo kèm p99 2 job của mọi cấu hình.
"""

import argparse
import json
from pathlib import Path

import numpy as np
import yaml

from eval import provenance, study, sweep

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "build" / "study"
LINES = (["S1", "f"], ["S1", "c"])
REPEATS = 3


def configs(plan: dict) -> list[sweep.CalSet]:
    return [s for s in study.variant_sets(plan) if plan["variants"][s.name].get("ranked", True)
            and "PP_T7_TELEMETRY" not in dict(s.cmake)]


def one(suite: dict, run: list, seed: int, lib: Path) -> dict:
    """Một lượt, chỉ đo thời gian (không chấm requirement)."""
    from adapters.sil.sil_planner import PlannerLibraries
    from sim.harness import Harness
    scenario = sweep.load_run(run, object_list_on_empty_road=suite.get("object_list_on_empty_road", False))
    log = Harness(scenario, PlannerLibraries.at(lib), seed).run()
    ms = np.array([c.compute_lcc_ns / 1e6 for c in log.cycles], dtype=float)
    return {"run": scenario.name, "seed": seed, "cycles": int(ms.size),
            "p99": float(np.percentile(ms, 99)) if ms.size else None, "max": float(ms.max()) if ms.size else None}


def main() -> None:
    parser = argparse.ArgumentParser(description="1-job timing session of a generator campaign (PP-TS-031)")
    parser.add_argument("study", nargs="?", default="PP-TS-031")
    parser.add_argument("--repeats", type=int, default=REPEATS)
    parser.add_argument("--record", action="store_true", help="Official run: locked plan, clean tree")
    args = parser.parse_args()
    plan_path = study.find_plan(args.study)
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    suite = sweep.load_suite(plan["suite"])
    runs = [r for r in suite["test"]["runs"] if r in [list(x) for x in LINES]]
    if len(runs) != len(LINES):
        raise SystemExit(f"{plan['suite']}: test part must contain {LINES}")
    sets = configs(plan)
    root = OUT_DIR / args.study / "timing"
    manifest = provenance.make("timing", args.study, {"plan": {"path": str(plan_path.relative_to(ROOT)),
                                                             "sha256": provenance.sha256(plan_path)},
                                                    "configs": [s.name for s in sets], "repeats": args.repeats,
                                                    "lines": [list(x) for x in LINES], "jobs": 1})
    if args.record and not plan.get("locked"):
        raise SystemExit(f"{plan_path}: set `locked` before an official run")
    libs = {}
    for s in sets:
        print(f"Build {s.name}", flush=True)
        libs[s.name] = sweep._build(s, root / s.name)
    from adapters.sil.sil_planner import PlannerLibraries
    manifest["libraries"] = [info for s in sets for info in provenance.library_infos(PlannerLibraries.at(libs[s.name]))]
    if args.record:
        provenance.preflight(manifest)
    rows = []
    turn = 0
    for rep in range(args.repeats):
        for run in runs:
            for seed in suite["test"]["seeds"]:
                order = sets[turn % len(sets):] + sets[:turn % len(sets)]  # Xoay vòng thứ tự build mỗi lượt.
                turn += 1
                for s in order:
                    r = one(suite, run, seed, libs[s.name])
                    rows.append({"config": s.name, "repeat": rep, **r})
                print(f"repeat {rep + 1}/{args.repeats} {run} seed {seed}: done", flush=True)
    summary = {}
    for s in sets:
        p99 = [r["p99"] for r in rows if r["config"] == s.name and r["p99"] is not None]
        summary[s.name] = {"p99_median_ms": float(np.median(p99)) if p99 else None,
                           "p99_max_ms": max(p99) if p99 else None, "n": len(p99)}
    root.mkdir(parents=True, exist_ok=True)
    (root / "timing.json").write_text(json.dumps({"rows": rows, "summary": summary}, indent=1), encoding="utf-8")
    provenance.write(manifest, root)
    print(f"{root / 'timing.json'}", flush=True)
    if args.record:
        dest = provenance.record(manifest, {"timing.json": root / "timing.json"}, "Phiên đo thời gian 1 job")
        print(f"Recorded: {dest}", flush=True)


if __name__ == "__main__":
    main()

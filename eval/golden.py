"""Golden set so checksum hành vi của cùng ca theo các điểm chạy runner, suite và live.

Với --suite, chạy các dòng của một phần suite (vòng hở và kín như khai báo) qua runner. Hành động diff
so với báo cáo của một build khác trên cùng máy: dùng để kiểm refactor planner giữ nguyên hành vi
từng bit (PP-TS-031 GĐ 1).
"""

import argparse
import json
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy
import yaml

from eval import isolation, planner_choice, provenance

ROOT = Path(__file__).resolve().parents[1]
SET = ROOT / "benchmark" / "suites" / "golden.yaml"
OUT = ROOT / "build" / "golden"
BASELINE = OUT / "baseline.json"
PATHS = ("runner", "suite", "live")
TIMEOUT_S = 600


def cases() -> list[dict]:
    data = yaml.safe_load(SET.read_text(encoding="utf-8"))
    return data["cases"]


def run_one(recipe: dict, seed: int, lib: str, path: str) -> dict:
    from eval import case, checksum
    from sim.harness import Harness
    planner = planner_choice.resolve(Path(lib))
    scenario = case.resolve(recipe)
    start = time.perf_counter()
    if path == "live":
        from eval import live
        log = live.simulate(scenario, planner, seed)
    else:
        log = Harness(scenario, planner, seed).run()
    seconds = time.perf_counter() - start
    return {"case_hash": case.case_hash(scenario), "checksum": checksum.behavior_checksum(log),
            "seconds": round(seconds, 3)}


def smoke_files(out: Path) -> dict[str, Path]:
    concrete = out / "concrete"
    if concrete.is_dir():  # Tái dùng ca cụ thể do golden set đã sinh để giữ đúng bộ đầu vào.
        shutil.rmtree(concrete)
    subprocess.run([sys.executable, "-m", "eval.generate", "smoke", "--out", str(concrete)], cwd=ROOT,
                   check=True, capture_output=True)
    manifest = json.loads((concrete / "manifest.json").read_text(encoding="utf-8"))
    return {c["id"]: concrete / c["file"] for c in manifest["cases"]}


def tasks(paths: tuple[str, ...], lib: Path, out: Path) -> list[tuple]:
    files = smoke_files(out) if "suite" in paths else {}
    result = []
    for entry in cases():
        for seed in entry.get("seeds", [1]):
            for path in paths:
                recipe = entry["recipe"]
                if path == "suite":
                    prefix = entry.get("smoke")
                    match = [f for cid, f in files.items() if prefix and cid.startswith(prefix + "-")]
                    if len(match) != 1:
                        continue
                    recipe = {"kind": "file", "path": str(match[0])}
                result.append((recipe, seed, str(lib), path, entry["id"]))
    return result


def run_line(run: list, seed: int, lib: str, on_empty_road: bool) -> dict:
    from eval import case, checksum, sweep
    from sim.harness import Harness
    planner = planner_choice.resolve(Path(lib))
    scenario = sweep.load_run(run, object_list_on_empty_road=on_empty_road)
    start = time.perf_counter()
    log = Harness(scenario, planner, seed).run()
    seconds = time.perf_counter() - start
    return {"case_hash": case.case_hash(scenario), "checksum": checksum.behavior_checksum(log),
            "seconds": round(seconds, 3)}


def suite_tasks(suite_id: str, part: str, lib: Path) -> list[tuple]:
    from eval import sweep
    suite = sweep.load_suite(suite_id)
    on_empty_road = bool(suite.get("object_list_on_empty_road", False))
    return [((run, seed, str(lib), on_empty_road), seed, json.dumps(run, ensure_ascii=False))
            for run in suite[part]["runs"] for seed in suite[part]["seeds"]]


def run_suite(suite_id: str, part: str, jobs: int, lib: Path) -> dict:
    todo = suite_tasks(suite_id, part, lib)
    results = []
    for (_, seed, cid), (status, value) in zip(todo, isolation.map_isolated(run_line, [t[0] for t in todo],
                                                                             jobs, TIMEOUT_S)):
        row = {"case": cid, "seed": seed, "path": "runner", "status": status}
        if status == "ok":
            row.update(value)
        else:
            row["error"] = str(value).splitlines()[0] if value else status
        results.append(row)
    return {"environment": environment(lib), "jobs": jobs, "paths": ["runner"],
            "suite": suite_id, "part": part, "results": results}


def run(paths: tuple[str, ...], jobs: int, lib: Path, out: Path = OUT) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    todo = tasks(paths, lib, out)
    results = []
    for task, (status, value) in zip(todo, isolation.map_isolated(run_one, [t[:4] for t in todo], jobs, TIMEOUT_S)):
        _, seed, _, path, cid = task
        row = {"case": cid, "seed": seed, "path": path, "status": status}
        if status == "ok":
            row.update(value)
        else:
            row["error"] = str(value).splitlines()[0] if value else status
        results.append(row)
    return {"environment": environment(lib), "jobs": jobs, "paths": list(paths), "results": results}


def environment(lib: Path) -> dict:
    from adapters.sil.sil_planner import PlannerLibraries
    infos = provenance.library_infos(PlannerLibraries.at(lib), external=True)
    return {"platform": f"{sys.platform}-{platform.machine()}", "python": platform.python_version(),
            "numpy": numpy.__version__, "library_sha256": "+".join(i["sha256"] for i in infos),
            "pp_version": " | ".join(str(i["pp_version"]) for i in infos)}


def key(row: dict) -> str:
    return f"{row['case']}/seed{row['seed']}"


def problems(report: dict, baseline: dict | None = None) -> list[str]:
    out = []
    reference = {key(r): r for r in report["results"] if r["path"] == "runner" and r["status"] == "ok"}
    for row in report["results"]:
        if row["status"] != "ok":
            out.append(f"{key(row)} {row['path']}: {row['status']} {row.get('error', '')}")
        elif row["path"] != "runner" and key(row) in reference and row["checksum"] != reference[key(row)]["checksum"]:
            same_case = row["case_hash"] == reference[key(row)]["case_hash"]
            out.append(f"{key(row)} {row['path']}: checksum differs from runner"
                       + ("" if same_case else " (case_hash differs too: the path builds another case)"))
    if baseline is not None:
        expected = {key(r): r["checksum"] for r in baseline["results"] if r["path"] == "runner" and r["status"] == "ok"}
        for k, row in reference.items():
            if k not in expected:
                out.append(f"{k}: not in the baseline")
            elif row["checksum"] != expected[k]:
                out.append(f"{k}: checksum differs from the baseline")
    return out


MACHINE_KEYS = ("platform", "python", "numpy")


def diff_problems(report: dict, against: dict) -> list[str]:
    """So hai build trên cùng máy và cùng bộ ca: case_hash và checksum phải trùng từng lượt."""
    out = []
    for k in MACHINE_KEYS:
        if report["environment"].get(k) != against["environment"].get(k):
            out.append(f"environment {k}: {report['environment'].get(k)} vs {against['environment'].get(k)}")
    if (report.get("suite"), report.get("part")) != (against.get("suite"), against.get("part")):
        out.append(f"different runs: {report.get('suite')} {report.get('part')} vs "
                   f"{against.get('suite')} {against.get('part')}")
    mine = {key(r): r for r in report["results"] if r["path"] == "runner"}
    theirs = {key(r): r for r in against["results"] if r["path"] == "runner"}
    for k in sorted(set(mine) | set(theirs)):
        a, b = mine.get(k), theirs.get(k)
        if a is None or b is None:
            out.append(f"{k}: only in {'the reference' if a is None else 'this run'}")
        elif a["status"] != "ok" or b["status"] != "ok":
            out.append(f"{k}: status {a['status']} vs {b['status']}")
        elif a["case_hash"] != b["case_hash"]:
            out.append(f"{k}: case_hash differs (not the same case)")
        elif a["checksum"] != b["checksum"]:
            out.append(f"{k}: checksum differs")
    return out


def table(report: dict) -> str:
    lines = ["| Case | Seed | Path | case_hash | checksum | s |", "|---|---|---|---|---|---|"]
    for r in report["results"]:
        lines.append(f"| {r['case']} | {r['seed']} | {r['path']} | {r.get('case_hash', '')[:12]} | "
                     f"{r.get('checksum', r['status'])[:16]} | {r.get('seconds', '')} |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Golden set of the simulation platform (benchmark/suites/golden.yaml): behaviour "
            "checksums"
        ),
    )
    parser.add_argument("action", choices=("run", "record", "check", "diff"))
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--paths", default="runner,suite", help=f"Comma list of {PATHS}")
    parser.add_argument("--suite", help="Run the lines of this suite (benchmark/suites/<ID>.yaml) instead "
                                        "of the golden set; only run and diff")
    parser.add_argument("--part", default="tuning", choices=("tuning", "test"), help="Part of --suite")
    parser.add_argument("--against", type=Path, help="diff: report JSON of the reference build")
    parser.add_argument("--name", help="File name stem of the report (default: time stamp and action)")
    planner_choice.add_argument(parser)
    args = parser.parse_args()
    if args.suite and args.action not in ("run", "diff"):
        parser.error("--suite only works with run and diff")
    if args.action == "diff" and not (args.against and args.against.is_file()):
        parser.error("diff needs --against <report.json>")
    paths = tuple(p for p in args.paths.split(",") if p)
    if not paths or set(paths) - set(PATHS) or "runner" not in paths:
        parser.error(f"--paths: comma list of {PATHS}, runner included")
    lib = (args.planner or planner_choice.default_location()).resolve()
    report = run_suite(args.suite, args.part, args.jobs, lib) if args.suite else run(paths, args.jobs, lib)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    OUT.mkdir(parents=True, exist_ok=True)
    name = args.name or f"{stamp}-{args.action}"
    (OUT / f"{name}.json").write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(table(report))
    print(f"Report: {OUT / name}.json")
    if args.action == "diff":
        against = json.loads(args.against.read_text(encoding="utf-8"))
        found = [r for r in problems(report) if "checksum differs from runner" not in r] + diff_problems(report, against)
        print("\n".join(found) if found else f"\nOK: every run matches {args.against.name} bit for bit")
        raise SystemExit(1 if found else 0)
    baseline = None
    if args.action == "check":
        if not BASELINE.is_file():
            raise SystemExit("no baseline: run python3 -m eval.golden record first")
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        if baseline["environment"] != report["environment"]:
            raise SystemExit(f"baseline recorded in another environment: {baseline['environment']}")
    found = problems(report, baseline)
    print("\n".join(found) if found else "\nOK: every path agrees" + (" with the baseline" if baseline else ""))
    if args.action == "record":
        if found:
            raise SystemExit("not recorded: fix the differences first")
        BASELINE.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
        print(f"Baseline: {BASELINE}")
    if found:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

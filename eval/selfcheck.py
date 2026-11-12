"""Evaluator self-check with bait planners (Software Qualification Test Specification 12).

    python3 -m eval.selfcheck [--only PM-05,PM-06] [--b0-only] [--jobs 2] [--record]

Builds eval/bait/pm_planner.c once per bait (PM-00 control and PM-01 to PM-10, `cc`), runs
conformance B0 on each, then the scenario runs of benchmark/suites/selfcheck.yaml on baits
that B0 does not block, each run in its own process (eval.runner --planner). A bait is
detected when one of its expected ids fails with the expected level and the control PM-00
does not fail that id. The benchmark may be used only when every bait is detected. Writes
build/selfcheck/summary.md, results.json, manifest.json. Exit status 1 otherwise. Re-run
after every change to sim/, eval/ or benchmark/.
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

from eval import conformance, loader, provenance, severity

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "eval" / "bait" / "pm_planner.c"
SUITE = ROOT / "benchmark" / "suites" / "selfcheck.yaml"
OUT_DIR = ROOT / "build" / "selfcheck"
SUFFIX = ".dylib" if sys.platform == "darwin" else ".so"
RUN_TIMEOUT_S = 900


def load_suite(path: Path = SUITE) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def build(bait: str, define: str | None, out: Path) -> Path:
    if shutil.which("cc") is None:
        raise SystemExit("no C compiler (cc) to build the bait planners")
    out.mkdir(parents=True, exist_ok=True)
    lib = out / f"lib{bait.lower().replace('-', '_')}{SUFFIX}"
    name = f'-DPM_NAME="{bait.lower().replace("-", "_")}"'
    subprocess.run(["cc", "-std=c11", "-O2", "-shared", "-fPIC", f"-I{ROOT / 'interfaces' / 'c'}",
                    name, *([f"-D{define}"] if define else []), str(SOURCE), "-o", str(lib), "-lm"],
                   check=True, capture_output=True)
    return lib


def missing_inputs(run: list) -> str | None:
    """Why a run cannot start (evaluator side), or None."""
    if not (loader.SCENARIO_DIR / f"{run[0]}.xosc").is_file():
        return f"kịch bản {run[0]} chưa có"
    if len(run) > 2 and not (loader.FAULT_DIR / f"{run[2]}.xosc").is_file():
        return f"lỗi {run[2]} chưa có"
    return None


def scenario_run(lib: Path, run: list, seed: int) -> dict:
    """One closed-loop run of eval.runner in a child process; failed requirement ids."""
    label = " ".join(run) + f" seed {seed}"
    with tempfile.TemporaryDirectory() as tmp:
        cmd = [sys.executable, "-m", "eval.runner", run[0], run[1], "--seed", str(seed),
               "--planner", str(lib), "--out", tmp]
        if len(run) > 2:
            cmd += ["--fault", run[2], run[3]]
        try:
            proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=RUN_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            return {"run": label, "failed": [severity.EXECUTION_FAULT], "error": "không trả về"}
        results = [p for p in Path(tmp).glob("*_seed*.json") if not p.name.endswith(".manifest.json")]
        if proc.returncode < 0:
            return {"run": label, "failed": [severity.EXECUTION_FAULT],
                    "error": f"planner làm tiến trình dừng (signal {-proc.returncode})"}
        if proc.returncode != 0 or not results:
            tail = proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else str(proc.returncode)
            return {"run": label, "failed": [], "error": f"lỗi bên chấm: {tail}", "evaluator_error": True}
        data = json.loads(results[0].read_text(encoding="utf-8"))
    failed = [c["id"] for c in data["criteria"] if c["applicable"] and not c["passed"]]
    issues = data.get("issues", [])
    failed += [i["requirement"] for i in issues if i["kind"] == "requirement" and i["requirement"]]
    failed += [severity.EXECUTION_FAULT for i in issues if i["kind"] == "execution"]
    judged = {c["id"] for c in data["criteria"] if c["applicable"]} | {
        i["requirement"] for i in issues if i["kind"] == "requirement" and i["requirement"]}
    return {"run": label, "failed": sorted(set(failed)), "case_failures": data["case_failures"],
            "judged_ids": sorted(judged)}


def judge(lib: Path, runs: list, seeds: list, jobs: int, b0_only: bool) -> dict:
    """B0, then the scenario runs unless B0 blocks."""
    b0 = conformance.run(lib)
    failed = {c["id"] for c in b0["checks"] if c["status"] == "fail"}
    out = {"b0": {k: b0[k] for k in ("levels", "blocked", "integrable")}, "b0_failed": sorted(failed),
           "runs": []}
    if b0["blocked"] or b0_only or not runs:
        out["runs_skipped"] = "B0 bị chặn" if b0["blocked"] else ("--b0-only" if b0_only else "")
        return out
    tasks, skipped = [], []
    for run in runs:
        why = missing_inputs(run)
        if why:
            skipped.append({"run": " ".join(run), "error": why, "evaluator_error": True})
        else:
            tasks += [(run, seed) for seed in seeds]
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        out["runs"] = skipped + list(pool.map(lambda t: scenario_run(lib, *t), tasks))
    return out


def failed_ids(judged: dict) -> set[str]:
    return set(judged["b0_failed"]) | {i for r in judged["runs"] for i in r.get("failed", [])}


def verdict(bait: dict, judged: dict, control: dict | None) -> tuple[str, str]:
    expect, level = bait["expect"], bait.get("level")
    got = failed_ids(judged) & set(expect)
    if not got:
        if bait.get("runs") and not judged["runs"] and judged.get("runs_skipped"):
            return "không phát hiện", f"ca kịch bản không chạy: {judged['runs_skipped']}"
        errors = [r["error"] for r in judged["runs"] if r.get("error")]
        if errors:
            return "không phát hiện", "; ".join(errors)
        judged_ids = {i for r in judged["runs"] for i in r.get("judged_ids", [])}
        unjudged = [i for i in expect if i.startswith("PP-SWR") and i not in judged_ids]
        if bait.get("runs") and unjudged:
            return "không phát hiện", "bên chấm không chấm " + ", ".join(unjudged) + " ở ca đã chạy"
        return "không phát hiện", "không trượt " + ", ".join(expect)
    levels = {severity.level(i) for i in got}
    if level not in levels:
        return "sai mức", f"{', '.join(sorted(got))} có mức {', '.join(str(lv) for lv in levels)}, cần {level}"
    distinct = sorted(set(distinct_failures(judged, control)) & set(expect))
    if not distinct:
        return "không phân biệt", f"PM-00 cũng trượt {', '.join(sorted(got))} ở cùng ca"
    return "đạt", ", ".join(distinct) + (f" ({level})" if level else "")


def distinct_failures(judged: dict, control: dict | None) -> list[str]:
    """Ids the bait fails where the control, on the same case (or in B0), does not."""
    if control is None:
        return sorted(failed_ids(judged))
    out = set(judged["b0_failed"]) - set(control["b0_failed"])
    control_runs = {r["run"]: set(r.get("failed", [])) for r in control["runs"]}
    for r in judged["runs"]:
        out |= set(r.get("failed", [])) - control_runs.get(r["run"], set())
    return sorted(out)


def summary(suite: dict, results: dict) -> list[str]:
    lines = ["| Mã | Lỗi cố ý | Phải được báo | Kết quả | Chi tiết |", "|---|---|---|---|---|"]
    for bait_id, bait in suite["baits"].items():
        if bait_id not in results:
            continue
        r = results[bait_id]
        want = ", ".join(bait["expect"]) + (f"; {bait['level']}" if bait.get("level") else "; không có cờ Tích hợp được")
        lines.append(f"| {bait_id} | {bait['fault']} | {want} | {r['verdict']} | {r['detail']} |")
    control = results.get(suite["control"])
    if control:
        lines += ["", f"{suite['control']} (đối chứng) trượt: " + (", ".join(sorted(failed_ids(control["judged"]))) or "không")]
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--only", help="Comma-separated bait ids; the control always runs when a bait needs scenarios")
    parser.add_argument("--b0-only", action="store_true", help="Conformance only, no scenario run (exploratory)")
    parser.add_argument("--jobs", type=int, default=1, help="Scenario runs at a time (8 GB: at most 2)")
    parser.add_argument("--out", type=Path, default=OUT_DIR)
    parser.add_argument("--record", action="store_true", help="Official run: clean working tree; copy to research/runs")
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be at least 1")
    if args.record and (args.only or args.b0_only):
        parser.error("--record runs every bait")
    suite = load_suite()
    chosen = [b.strip() for b in args.only.split(",")] if args.only else list(suite["baits"])
    unknown = [b for b in chosen if b not in suite["baits"]]
    if unknown:
        parser.error(f"unknown bait: {', '.join(unknown)}")
    manifest = provenance.make("selfcheck", "PM", {"baits": chosen, "b0_only": args.b0_only})
    manifest["inputs"][str(SOURCE.relative_to(ROOT))] = provenance.sha256(SOURCE)
    if args.record:
        provenance.preflight(manifest)
    lib_dir = args.out / "lib"
    needs_scenarios = not args.b0_only and any(suite["baits"][b].get("runs") for b in chosen)
    results = {}
    control = None
    if needs_scenarios:
        runs = [r for b in chosen for r in suite["baits"][b].get("runs", [])]
        unique = [list(r) for r in dict.fromkeys(tuple(r) for r in runs)]
        print(f"{suite['control']}: B0 và {len(unique)} ca", flush=True)
        control = judge(build(suite["control"], None, lib_dir), unique, suite["seeds"], args.jobs, False)
        results[suite["control"]] = {"verdict": "đối chứng", "detail": "", "judged": control}
    for bait_id in chosen:
        bait = suite["baits"][bait_id]
        print(f"{bait_id}: {bait['fault']}", flush=True)
        judged = judge(build(bait_id, bait["define"], lib_dir), bait.get("runs", []), suite["seeds"],
                       args.jobs, args.b0_only)
        v, detail = verdict(bait, judged, control if bait.get("runs") else None)
        results[bait_id] = {"verdict": v, "detail": detail, "judged": judged}
        print(f"  {v}: {detail}", flush=True)
    usable = all(results[b]["verdict"] == "đạt" for b in chosen)
    head = ["# Kiểm bên chấm", "",
            ("Mọi planner mồi bị báo đúng requirement và mức: benchmark dùng được."
             if usable and chosen == list(suite["baits"]) and not args.b0_only else
             "Benchmark chưa dùng được: " + (", ".join(b for b in chosen if results[b]["verdict"] != "đạt")
                                             or "chưa chạy đủ planner mồi") + "."), ""]
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "summary.md").write_text("\n".join(head + summary(suite, results)) + "\n", encoding="utf-8")
    (args.out / "results.json").write_text(json.dumps(results, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    provenance.write({**manifest, "summary": {b: results[b]["verdict"] for b in results}}, args.out)
    print("\n".join(head + summary(suite, results)))
    if args.record:
        dest = provenance.record(manifest, {"summary.md": args.out / "summary.md",
                                            "results.json": args.out / "results.json"}, head[2])
        print(f"Recorded: {dest}")
    if not usable:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

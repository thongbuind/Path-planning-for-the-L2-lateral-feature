"""Coverage matrix: many scenario runs with the delivered planner library.

    python3 -m eval.matrix M1 --jobs 2 [--planner LIB]

Runs every (scenario, variant[, fault], longitudinal mode, profile, seed) of a suite in
benchmark/suites and writes build/matrix/<suite>/summary.md, runs.json and manifest.json.
Each run is judged with the scope of the named sweep suite (Kiểm chứng column of the SRS);
all other criteria are reported as information. --record makes it an official run
(research/README.md).

A block may sweep simulator settings with `sim_sweep` (Software Qualification Test
Specification 6.1, Q4): one value at a time, the others at their scenario value, plus one
run at the scenario values. Only the fields in SIM_SWEEP_FIELDS can be swept.

B0 conformance runs first and enters the conclusion at the head of summary.md (Software
Qualification Test Specification 8.4, 10); being a development matrix, the runs go on even
when B0 blocks (eval.suite stops). Each run is its own process: a crash or hang is an
execution fault of that run. MCAP logs of runs with an in-scope failure in mcap/.
"""

import argparse
import json
import math
from dataclasses import fields, replace
from pathlib import Path

import yaml

from eval import aspects, conclusion, conformance, isolation, labels, loader, openx, planner_choice, provenance, report, sweep
from sim.scenario import Scenario

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "build" / "matrix"
INFO = ("vehicle_offset_max_m", "ay_need_at_car_max", "speed_min_mps", "decel_max_mps2",
        "offset_at_hwa_start_m", "ay_vehicle_r79_max", "ay_vehicle_r79_over_sustained_s",
        "jerk_vehicle_r79_max", "ay_vehicle_r79_within_limits")


SIM_SWEEP_FIELDS = sweep.SIM_KEYS
_DEFAULTS = {f.name: f.default for f in fields(Scenario)}


def sim_settings(block: dict) -> list[dict]:
    """[base] without a sweep; else the base first, then one change at a time on top of it.
    `sim` of the block sets values held for all its runs (Q1: jitter at every latency)."""
    base = {k: float(v) for k, v in block.get("sim", {}).items()}
    sweep_spec = block.get("sim_sweep", {})
    unknown = (set(sweep_spec) | set(base)) - set(SIM_SWEEP_FIELDS)
    if unknown:
        raise ValueError(f"cannot sweep {sorted(unknown)}")
    settings = [base]
    for name, values in sweep_spec.items():
        settings += [{**base, name: float(v)} for v in values
                     if float(v) != base.get(name, _DEFAULTS[name])]
    return settings


def apply_sim(scenario: Scenario, sim: dict) -> Scenario:
    scenario = replace(scenario, **sim)
    sweep.check_sim(scenario)
    return scenario


def expand(suite: dict) -> list[dict]:
    jobs = []
    for block in suite["blocks"]:
        for sim in sim_settings(block):
            for run in block["runs"]:
                for acc in block["acc"]:
                    for profile in block.get("profiles", suite["profiles"]):
                        for seed in block.get("seeds", suite["seeds"]):
                            job = {"run": list(run), "acc": acc, "profile": profile, "seed": seed}
                            if sim:
                                job["sim"] = sim
                            jobs.append(job)
    return jobs


def scope(suite: dict, run: list) -> set[str]:
    """Scope of the named sweep suite, plus every requirement whose Kiểm chứng column of the
    Software Requirements Specification names the scenario or fault (8.1)."""
    from eval.severity import srs_scope
    base = sweep.scope_of(sweep.load_suite(suite["scope_from"]), run)
    key = run[2] if len(run) > 2 else run[0]
    return base | set(suite.get("extra_scope", {}).get(key, [])) | srs_scope(key)


RUN_TIMEOUT_S = 1800


def run_one(suite_id: str, job: dict, planner, mcap_dir=None) -> dict:
    from eval import metrics
    from sim.harness import Harness
    from sim.logging import run_log

    suite = yaml.safe_load((sweep.SUITE_DIR / f"{suite_id}.yaml").read_text(encoding="utf-8"))
    run = job["run"]
    scenario = loader.load(run[0], run[1])
    if len(run) > 2:
        scenario = loader.with_fault(scenario, run[2], run[3])
    scenario = apply_sim(replace(scenario, acc=job["acc"], profile=job["profile"]), job.get("sim", {}))
    log = Harness(scenario, planner, job["seed"]).run()
    result = metrics.evaluate(log)
    from eval import differential
    result.criteria.extend(differential.criteria(scenario, log, planner, job["seed"]))
    in_scope = scope(suite, run) | labels.scope_extra(labels.of(scenario))
    failed = result.case_failures + [c.id for c in result.criteria if c.applicable and not c.passed and c.id in in_scope]
    other = [c.id for c in result.criteria if c.applicable and not c.passed and c.id not in in_scope]
    sim = ", ".join(f"{k}={v:g}" for k, v in job.get("sim", {}).items())
    name = scenario.name + (f" [{sim}]" if sim else "")
    rerun = (f"python3 -m eval.runner {run[0]} {run[1]} --seed {job['seed']}"
             + (f" --fault {run[2]} {run[3]}" if len(run) > 2 else "") + f" --acc {job['acc']}"
             + (f" --planner {planner.path}" if planner is not None else "")
             + (f"  # profile {job['profile']}; sim {sim}" if sim else f"  # profile {job['profile']}"))
    case_labels = labels.of(scenario, swept=bool(job.get("sim")))
    family = run[2] if len(run) > 2 else run[0]
    anchor = run[3] if len(run) > 2 else run[1]
    out = {**job, "name": name, "case": name, "failed": failed, "failed_out_of_scope": other,
           "labels": case_labels, "aspects": aspects.members(family, anchor, ["anchor"], case_labels),
           "targets": {t.id: t.value for t in result.targets},
           "criteria": {c.id: c.value for c in result.criteria if c.applicable},
           "info": {k: result.info.get(k) for k in INFO},
           "scope": sorted(in_scope), "result": result.to_dict(), "rerun": rerun, "mcap": None}
    if mcap_dir is not None and failed:
        safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in f"{name}_{job['acc']}_{job['profile']}")
        out["mcap"] = str(run_log.write(log, Path(mcap_dir) / f"{safe}_seed{job['seed']}.mcap", {"rerun": rerun}))
    return out


def _isolated_record(job: dict, status: str, value) -> dict:
    run = " ".join(job["run"])
    base = {**job, "name": run, "case": run, "failed": [], "failed_out_of_scope": [], "targets": {},
            "criteria": {}, "info": {k: None for k in INFO}}
    if status == "ok":
        return value
    if status == "crash":
        return {**base, "failed": ["execution"], "execution": f"Lỗi thực thi: tiến trình dừng ({value})"}
    if status == "timeout":
        return {**base, "failed": ["execution"], "execution": f"Lỗi thực thi: không trả về sau {RUN_TIMEOUT_S} s"}
    return {**base, "error": str(value).splitlines()[0]}


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
    planner_choice.add_argument(parser)
    parser.add_argument("--record", action="store_true",
                        help="Official run: clean working tree, library from HEAD; copy to research/runs")
    args = parser.parse_args()
    planner = planner_choice.from_args(args)
    manifest = provenance.make("matrix", args.suite, {"jobs": args.jobs, "start_method": isolation.START_METHOD})
    manifest["libraries"] = [provenance.library_info(planner.path, external=args.planner is not None)]
    if args.record:
        provenance.preflight(manifest)
    suite = yaml.safe_load((sweep.SUITE_DIR / f"{args.suite}.yaml").read_text(encoding="utf-8"))
    jobs = expand(suite)
    out = OUT_DIR / args.suite
    out.mkdir(parents=True, exist_ok=True)
    b0 = conformance.run(planner.path)
    (out / "conformance.json").write_text(json.dumps(b0, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"B0: {'bị chặn' if b0['blocked'] else 'đạt C1, C2'}; {len(jobs)} runs", flush=True)
    tasks = [(args.suite, job, planner, out / "mcap") for job in jobs]
    results = [_isolated_record(job, status, value) for job, (status, value)
               in zip(jobs, isolation.map_isolated(run_one, tasks, args.jobs, RUN_TIMEOUT_S))]
    (out / "runs.json").write_text(json.dumps(results, indent=1, ensure_ascii=False, default=report.jsonable),
                                   encoding="utf-8")
    failed = [r for r in results if r["failed"]]
    lib = manifest["libraries"][0]
    c = conclusion.conclude(results, b0)
    (out / "conclusion.json").write_text(json.dumps(c, indent=1, ensure_ascii=False, default=report.jsonable) + "\n",
                                         encoding="utf-8")
    from eval.suite import aspect_table
    head = conclusion.markdown(c, f"{lib['pp_version']} ({lib['sha256'][:12]})") + aspect_table(results, b0) + [
        "", f"## Matrix {args.suite}", "", f"{len(results)} runs; {len(failed)} with an in-scope failure.", ""]
    from eval import presentation
    extra = (presentation.sweep(results, out / "figures") + presentation.flexibility(results, {})
             + presentation.compute(results, out / "figures"))
    (out / "summary.md").write_text("\n".join(head + summary(results) + extra) + "\n", encoding="utf-8")
    provenance.write(manifest, out)
    print(f"{len(failed)} runs with in-scope failures; summary: {out / 'summary.md'}", flush=True)
    if args.record:
        other = sum(1 for r in results if r["failed_out_of_scope"])
        dest = provenance.record(manifest, {"summary.md": out / "summary.md",
                                            "results.json": out / "runs.json",
                                            "conclusion.json": out / "conclusion.json",
                                            "conformance.json": out / "conformance.json"},
                                 f"{c['verdict']}; {len(results)} lần chạy; {len(failed)} trượt trong phạm vi; "
                                 f"{other} có trượt ngoài phạm vi")
        print(f"Recorded: {dest}", flush=True)


if __name__ == "__main__":
    main()

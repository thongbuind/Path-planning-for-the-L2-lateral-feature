"""So sánh Lateral Controller với cùng thư viện planner và bộ chấm hiện hành."""

import argparse
import inspect
import json
from functools import partial
from pathlib import Path

import yaml

from eval import (case, checksum, differential, labels, matrix, metrics, planner_choice,
                  proposed, provenance, report, study, sweep)
from sim.harness import Harness
from sim.stand_ins.lateral_controller import LateralController


CONTROLLERS = {"stock": LateralController}


def assess(log, run, vehicle_ay: dict, extra_criteria=()) -> tuple[metrics.Result, set[str]]:
    scenario = log.scenario
    scope = matrix.scope(matrix.SCOPE, run) | labels.scope_extra(labels.of(scenario))
    result = metrics.evaluate(log)
    result.criteria.extend(extra_criteria)
    if run[0] == vehicle_ay["scenario"] and scenario.acc == vehicle_ay["acc"]:
        criterion = vehicle_ay["criterion"]
        result.criteria.extend(proposed.criteria(result, [criterion]))
        scope.add(criterion)
    return result, scope


def run_case(run: list, seed: int, planner, controller_factory, vehicle_ay: dict) -> dict:
    scenario = sweep.load_run(run)
    log = Harness(scenario, planner, seed, controller_factory=controller_factory).run()
    extra = differential.criteria(scenario, log, planner, seed, controller_factory=controller_factory)
    result, scope = assess(log, run, vehicle_ay, extra)
    return {
        "spec": run, "profile": scenario.profile, "acc": scenario.acc, "seed": seed,
        "case_hash": case.case_hash(scenario), "behavior_checksum": checksum.behavior_checksum(log),
        "scope": sorted(scope), "failed": result.case_failures + [
            criterion.id for criterion in result.criteria
            if criterion.id in scope and criterion.applicable and not criterion.passed
        ],
        "result": result.to_dict(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a draft controller study on a fixed planner build.")
    parser.add_argument("study")
    parser.add_argument("--list", action="store_true", help="Show the case list and controller availability")
    parser.add_argument("--planner", type=Path, help="Directory containing the two frozen planner libraries")
    parser.add_argument("--variant", action="append", help="Draft variant ID. May be repeated")
    parser.add_argument("--part", choices=("tuning", "test"))
    parser.add_argument("--case", type=int, help="One-based case number within the selected part")
    parser.add_argument("--seed", type=int, help="One seed from the selected part")
    parser.add_argument("--out", type=Path, help="New directory for draft results")
    args = parser.parse_args()

    plan_path = study.find_plan(args.study)
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    if plan.get("runner") != "eval.controller_study":
        parser.error(f"{args.study} is not a controller study")
    suite = sweep.load_suite(plan["suite"])
    if args.list:
        print(f"{args.study} · {suite['title']}")
        for name, variant in plan["variants"].items():
            status = "Sẵn sàng" if variant["controller"] in CONTROLLERS else "Chờ triển khai"
            print(f"{name} {status} · {variant['description']}")
        for part in plan["parts"]:
            print(f"{part} · seed {suite[part]['seeds']}")
            for index, run in enumerate(suite[part]["runs"], 1):
                print(f"  {index:2} {run}")
        return

    if args.planner is None or args.out is None:
        parser.error("a draft run needs --planner and --out")
    if (args.case is not None or args.seed is not None) and args.part is None:
        parser.error("--case and --seed require --part")
    selected = dict.fromkeys(args.variant or plan["variants"])
    unknown = selected.keys() - plan["variants"].keys()
    if unknown:
        parser.error(f"unknown variants: {', '.join(sorted(unknown))}")
    controllers = {name: CONTROLLERS.get(plan["variants"][name]["controller"]) for name in selected}
    unavailable = [name for name, factory in controllers.items() if factory is None]
    if unavailable:
        parser.error(f"controller not implemented: {', '.join(unavailable)}")
    parts = [args.part] if args.part else plan["parts"]
    if args.case is not None and not 1 <= args.case <= len(suite[args.part]["runs"]):
        parser.error("--case is outside the selected part")
    if args.seed is not None and args.seed not in suite[args.part]["seeds"]:
        parser.error("--seed is outside the selected part")

    planner = planner_choice.resolve(args.planner)
    libraries = provenance.library_infos(planner)
    baseline = plan["planner_baseline"]
    actual = {lib["build"].get("name"): lib["sha256"] for lib in libraries}
    if actual != baseline["libraries_sha256"]:
        parser.error("planner library hashes differ from the frozen baseline in the plan")
    if not provenance.sha256(provenance.CALIBRATION).startswith(baseline["calibration_sha256_prefix"]):
        parser.error("calibration file differs from the frozen baseline in the plan")
    if args.out.exists():
        parser.error("--out must be a new directory")

    manifest = provenance.make("study", args.study, {
        "draft": True, "parts": parts, "case": args.case, "seed": args.seed,
        "plan": {"path": str(plan_path.relative_to(provenance.ROOT)), "sha256": provenance.sha256(plan_path)},
        "suite": {"id": plan["suite"], "sha256": provenance.sha256(sweep.SUITE_DIR / f"{plan['suite']}.yaml")},
        "libraries": libraries,
        "controllers": {
            name: {"config": plan["variants"][name], "source": inspect.getfile(factory),
                   "sha256": provenance.sha256(Path(inspect.getfile(factory)))}
            for name, factory in controllers.items()
        },
    })
    args.out.mkdir(parents=True)
    results = []
    for name, controller in controllers.items():
        factory = partial(controller, **plan["variants"][name].get("parameters", {}))
        for part in parts:
            runs = suite[part]["runs"] if args.case is None else [suite[part]["runs"][args.case - 1]]
            seeds = suite[part]["seeds"] if args.seed is None else [args.seed]
            for run in runs:
                for seed in seeds:
                    row = run_case(run, seed, planner, factory, suite["vehicle_ay"])
                    results.append({"variant": name, "part": part, **row})
    (args.out / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2, default=report.jsonable)
                                          + "\n", encoding="utf-8")
    provenance.write(manifest, args.out)
    print(f"{len(results)} lượt nháp: {args.out / 'results.json'}")


if __name__ == "__main__":
    main()

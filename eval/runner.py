import argparse
from pathlib import Path

from eval import case, conclusion, labels, matrix, metrics, planner_choice, provenance, report
from interfaces.planner import PlannerFactory
from sim.harness import Harness, RunLog
from sim.scenario import Scenario

ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "build" / "runs"


def run(scenario: Scenario, seed: int, planner: PlannerFactory | None = None) -> RunLog:
    return Harness(scenario, planner or planner_choice.resolve(None), seed).run()


def parse_moment(text: str) -> tuple[str, float]:
    event, _, offset = text.partition("+")
    from sim.faults import trigger
    trigger.check(event)
    value = float(offset) if offset else 0.0
    if value < 0:
        raise ValueError("offset must be >= 0")
    return event, value


def run_scope(spec: list, faults: list) -> set[str]:
    keys = [spec] + [spec + list(f) for f in faults]
    return set().union(*(matrix.scope(matrix.SCOPE, k) for k in keys))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Runs one benchmark scenario against the delivered planner library (SIL).",
    )
    parser.add_argument("scenario", help="Scenario id, e.g. S1")
    parser.add_argument("variant", nargs="?", help="Variant letter; omit when scenario is a .xosc path")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--fault", nargs=2, metavar=("ID", "LEVEL"), action="append",
                        help="Fault from benchmark/faults, e.g. F02 c; repeat to combine (6.2)")
    parser.add_argument("--at", metavar="EVENT[+OFFSET]",
                        help="Start every fault OFFSET s after a planner-output event: "
                             "lka_active, elk_active, intervention_active, lcc_follow (sim.faults.trigger)")
    parser.add_argument("--acc", choices=("off", "ignore_limits", "on"),
                        help="Override the scenario's longitudinal side")
    parser.add_argument("--adas-mode", choices=("A", "B"),
                        help="Select the LKA/ELK stand-in inputs, A is timing comparison only")
    planner_choice.add_argument(parser)
    parser.add_argument("--planner-only", choices=planner_choice.FAMILIES,
                        help="Run just one planner family for standalone qualification")
    parser.add_argument("--out", type=Path, default=RUN_DIR)
    parser.add_argument("--record", action="store_true",
                        help="Official run: clean working tree, library from HEAD; copy to research/runs")
    args = parser.parse_args()

    planner = planner_choice.resolve(args.planner, args.planner_only)
    is_file = Path(args.scenario).suffix == ".xosc"
    if is_file and args.variant is not None:
        parser.error("omit variant when running a .xosc file")
    if not is_file and args.variant is None:
        parser.error("a scenario ID requires a variant")
    faults = args.fault or []
    if args.at and not faults:
        parser.error("--at needs --fault")
    trigger, offset_s = parse_moment(args.at) if args.at else (None, 0.0)
    target = ((Path(args.scenario).stem if is_file else args.scenario + args.variant)
              + "".join(f"-{''.join(f)}" for f in faults) + (f"@{args.at}" if args.at else ""))
    manifest = provenance.make("run", target, {"seed": args.seed, "planner_only": args.planner_only})
    manifest["libraries"] = provenance.library_infos(planner, external=args.planner is not None)
    if args.record:
        provenance.preflight(manifest)
    recipe = ({"kind": "file", "path": str(Path(args.scenario).resolve())} if is_file
              else {"kind": "catalog", "sid": args.scenario, "v": args.variant})
    if faults:
        recipe["faults"] = [list(f) for f in faults]
    if trigger:
        recipe["trigger"], recipe["offset_s"] = trigger, offset_s
    if args.acc:
        recipe["acc"] = args.acc
    if args.adas_mode:
        recipe["adas_mode"] = args.adas_mode
        manifest["adas_mode"] = args.adas_mode
    try:
        scenario = case.resolve(recipe)
    except ValueError as error:
        parser.error(str(error))
    doc = case.document(recipe, scenario)
    if is_file:
        manifest["concrete_inputs"] = doc["inputs"]
    from sim.logging import run_log
    log = run(scenario, args.seed, planner)
    result = metrics.evaluate(log)
    from eval import differential
    result.criteria.extend(differential.criteria(scenario, log, planner, args.seed))
    spec = None if is_file else [args.scenario, args.variant]
    scope = run_scope(spec, faults) | labels.scope_extra(labels.of(scenario)) if spec else None
    if args.planner_only and (spec == ["S9", "a"] or is_file and target.startswith("S9-a-")):
        scope = run_scope(["S9", "a"], faults) | labels.scope_extra(labels.of(scenario))
        metrics.score_standalone(result, scope)
    lib = manifest["libraries"][0]
    command = "python3 -m eval.runner " + " ".join(manifest["command"][1:])
    mcap = run_log.write(log, args.out / f"{result.scenario}_seed{result.seed}.mcap",
                         {"pp_version": str(lib["pp_version"]), "library_sha256": lib["sha256"],
                          "commit": str(manifest["git"]["commit"]), "rerun": command})
    record = {"case": result.scenario, "profile": scenario.profile, "seed": result.seed,
              "result": result.to_dict(), "scope": sorted(scope) if scope is not None else None,
              "mcap": str(mcap), "rerun": command}
    print("\n".join(conclusion.markdown(conclusion.conclude([record]), f"{lib['pp_version']}")) + "\n")
    print(report.text(result))
    path = report.write_json(result, args.out)
    provenance.write(manifest, args.out, path.stem + ".manifest.json")
    from eval import presentation
    figure = presentation.run_figure(log, result, args.out / f"{result.scenario}_seed{result.seed}.png")
    from eval import run_bundle
    from execution import bundle
    folder = bundle.Bundle.create(args.out)
    folder.write_json("request.json", {"run_id": folder.run_id, "recipe": recipe, "seed": args.seed,
                                       "command": command})
    bundle_manifest = run_bundle.write(folder.tmp, run_id=folder.run_id, parent=None, kind="run", doc=doc,
                                       planner=planner, seed=args.seed, log=log, result=result, command=command)
    final = folder.finalize({"state": "COMPLETED", "failure": None, "message": ""})
    print(f"\nJSON: {path}\nMCAP: {mcap}\nHình: {figure}\nBundle: {final}"
          f"\ncase_hash {doc['case_hash'][:12]}, behavior_checksum {bundle_manifest['bundle']['behavior_checksum'][:16]}")
    if args.record:
        failed = result.case_failures + [c.id for c in result.criteria if c.applicable and not c.passed]
        dest = provenance.record(manifest, {"results.json": path},
                                 "trượt: " + (", ".join(failed) or "không"))
        print(f"Recorded: {dest}")


if __name__ == "__main__":
    main()

"""Runs one benchmark scenario against the delivered planner library (SIL).

    python3 -m eval.runner S1 a --seed 1
    python3 -m eval.runner S1 a --fault F02 c

Needs build/planner/libpp_planner (see README). Writes build/runs/<scenario>_seed<n>.json
and manifest.json. --record makes it an official run (research/README.md).
"""

import argparse
from dataclasses import replace
from pathlib import Path

from adapters.sil.sil_planner import SilPlanner, library_path
from eval import loader, metrics, provenance, report
from sim.harness import Harness, RunLog
from sim.scenario import Scenario

ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "build" / "runs"


def run(scenario: Scenario, seed: int) -> RunLog:
    return Harness(scenario, SilPlanner, seed).run()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("scenario", help="Scenario id, e.g. S1")
    parser.add_argument("variant", nargs="?", help="Variant letter; omit when scenario is a .xosc path")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--fault", nargs=2, metavar=("ID", "LEVEL"),
                        help="Lane-model fault from benchmark/faults, e.g. F02 c")
    parser.add_argument("--acc", choices=("off", "ignore_limits", "on"),
                        help="Override the scenario's longitudinal side")
    parser.add_argument("--adas-mode", choices=("A", "B"),
                        help="Select the LKA/ELK stand-in inputs, A is timing comparison only")
    parser.add_argument("--out", type=Path, default=RUN_DIR)
    parser.add_argument("--record", action="store_true",
                        help="Official run: clean working tree, library from HEAD; copy to research/runs")
    args = parser.parse_args()

    if not library_path().exists():
        raise SystemExit(f"planner library not built: {library_path()}")
    is_file = Path(args.scenario).suffix == ".xosc"
    if is_file and args.variant is not None:
        parser.error("omit variant when running a .xosc file")
    if not is_file and args.variant is None:
        parser.error("a scenario ID requires a variant")
    target = (Path(args.scenario).stem if is_file else args.scenario + args.variant) + (f"-{''.join(args.fault)}" if args.fault else "")
    manifest = provenance.make("run", target, {"seed": args.seed})
    manifest["libraries"] = [provenance.library_info(library_path())]
    if args.record:
        provenance.preflight(manifest)
    scenario = loader.load_file(Path(args.scenario)) if is_file else loader.load(args.scenario, args.variant)
    if is_file:
        from eval import openx
        scenario_path = Path(args.scenario).resolve()
        scenario = replace(scenario, name=scenario_path.stem)
        resolved, _ = openx.resolve(openx.parse(scenario_path))
        road_path = scenario_path.parent / resolved.find("./RoadNetwork/LogicFile").attrib["filepath"]
        manifest["concrete_inputs"] = {str(p): provenance.sha256(p) for p in (scenario_path, road_path)}
    if args.fault:
        scenario = loader.with_fault(scenario, *args.fault)
    if args.acc:
        scenario = replace(scenario, acc=args.acc, name=f"{scenario.name}_acc-{args.acc}")
    if args.adas_mode:
        if scenario.adas_mode == "scripted":
            parser.error("--adas-mode applies to scenarios configured for the stand-in")
        scenario = replace(scenario, adas_mode=args.adas_mode, name=f"{scenario.name}_adas-{args.adas_mode}")
        manifest["adas_mode"] = args.adas_mode
    result = metrics.evaluate(run(scenario, args.seed))
    print(report.text(result))
    path = report.write_json(result, args.out)
    provenance.write(manifest, args.out, path.stem + ".manifest.json")
    print(f"\nJSON: {path}")
    if args.record:
        failed = result.case_failures + [c.id for c in result.criteria if c.applicable and not c.passed]
        dest = provenance.record(manifest, {"results.json": path},
                                 "trượt: " + (", ".join(failed) or "không"))
        print(f"Recorded: {dest}")


if __name__ == "__main__":
    main()

"""Runs one benchmark scenario against the delivered planner library (SIL).

    python3 -m eval.runner S1 a --seed 1
    python3 -m eval.runner S1 a --fault F02 c

Needs build/planner/libpp_planner (see README). Writes build/runs/<scenario>_seed<n>.json.
"""

import argparse
from dataclasses import replace
from pathlib import Path

from adapters.sil.sil_planner import SilPlanner, library_path
from eval import loader, metrics, report
from sim.harness import Harness, RunLog
from sim.scenario import Scenario

ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "build" / "runs"


def run(scenario: Scenario, seed: int) -> RunLog:
    return Harness(scenario, SilPlanner, seed).run()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("scenario", help="Scenario id, e.g. S1")
    parser.add_argument("variant", help="Variant letter, e.g. a")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--fault", nargs=2, metavar=("ID", "LEVEL"),
                        help="Lane-model fault from benchmark/faults, e.g. F02 c")
    parser.add_argument("--acc", choices=("off", "ignore_limits", "on"),
                        help="Override the scenario's longitudinal side")
    parser.add_argument("--out", type=Path, default=RUN_DIR)
    args = parser.parse_args()

    if not library_path().exists():
        raise SystemExit(f"planner library not built: {library_path()}")
    scenario = loader.load(args.scenario, args.variant)
    if args.fault:
        scenario = loader.with_fault(scenario, *args.fault)
    if args.acc:
        scenario = replace(scenario, acc=args.acc, name=f"{scenario.name}_acc-{args.acc}")
    result = metrics.evaluate(run(scenario, args.seed))
    print(report.text(result))
    print(f"\nJSON: {report.write_json(result, args.out)}")


if __name__ == "__main__":
    main()

import argparse
from dataclasses import replace
from pathlib import Path

from adapters.sil.sil_planner import IncompatibleLibrary, PlannerLibraries

FAMILIES = ("lcc", "lkaelk")


def add_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--planner", type=Path, metavar="LOCATION",
                        help="Planners under test: a directory with libpp_lcc and libpp_lkaelk, or one "
                             "library that exports pp_lcc_* and pp_lkaelk_* (built against "
                             "interfaces/c/pp_planner.h); default PP_PLANNER_LIB or build/planner")


def resolve(path: Path | None, only: str | None = None) -> PlannerLibraries:
    planner = PlannerLibraries.at(path) if path is not None else PlannerLibraries.default()
    if only is not None:
        if only not in FAMILIES:
            raise ValueError(f"unknown planner family {only!r}")
        planner = replace(planner, only=only)
    missing = [p for p in dict.fromkeys(p for p, _ in planner.paths()) if not p.is_file()]
    if missing:
        hint = "" if path is not None else " (build them, see README, or pass --planner)"
        raise SystemExit(f"planner library not found: {', '.join(str(p) for p in missing)}{hint}")
    try:
        planner.load()
    except IncompatibleLibrary as error:
        raise SystemExit(str(error)) from error
    return planner


def default_location() -> Path:
    return PlannerLibraries.default().lcc.parent if PlannerLibraries.default().lcc == PlannerLibraries.default().lka_elk \
        else PlannerLibraries.default().lcc.parent


def from_args(args: argparse.Namespace) -> PlannerLibraries:
    return resolve(args.planner)

"""Which planner library is under test (Software Qualification Test Specification 11).

The planner is any C library built against interfaces/c/pp_planner.h; eval/ is the only
place that chooses it. Order: --planner PATH, then PP_PLANNER_LIB, then the in-repo build
build/planner/libpp_planner.
"""

import argparse
from pathlib import Path

from adapters.sil.sil_planner import IncompatibleLibrary, PlannerLibrary, library_path


def add_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--planner", type=Path, metavar="LIB",
                        help="Planner library under test (.so/.dylib built against "
                             "interfaces/c/pp_planner.h); default PP_PLANNER_LIB or "
                             "build/planner/libpp_planner")


def resolve(path: Path | None) -> PlannerLibrary:
    """The planner under test; stops with a clear message if it cannot be called."""
    chosen = Path(path) if path is not None else library_path()
    if not chosen.is_file():
        hint = "" if path is not None else " (build it, see README, or pass --planner)"
        raise SystemExit(f"planner library not found: {chosen}{hint}")
    planner = PlannerLibrary(chosen)
    try:
        planner.load()
    except IncompatibleLibrary as error:
        raise SystemExit(str(error)) from error
    return planner


def from_args(args: argparse.Namespace) -> PlannerLibrary:
    return resolve(args.planner)

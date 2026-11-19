"""SIL adapter: the two C planner libraries behind the Python planner contract.

The simulator calls exactly the libraries that would be delivered (PP-ADR-013, PP-ADR-016):
the LCC planner (pp_lcc_*) and the LKA/ELK planner (pp_lkaelk_*). This is the only place that
knows the planners are C. A real vehicle needs its own adapter for its platform instead
(PP-ASM-019).

A planner under test is a directory with libpp_lcc and libpp_lkaelk, or one file that exports
both families (a stub or a bait planner of the evaluation).
"""

import ctypes
import functools
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from adapters.sil import pp_ctypes
from adapters.sil.convert import from_c, to_c
from interfaces import (
    EgoMotionQuery,
    InitResult,
    LccInputs,
    LccOutputs,
    LkaElkInputs,
    LkaElkOutputs,
    PlannerSet,
    VehicleConfig,
)

ROOT = Path(__file__).resolve().parents[2]
BUILD_DIR = ROOT / "build" / "planner"
STATE_ALIGNMENT = 8  # PP_STATE_ALIGNMENT in interfaces/c/pp_planner.h


@dataclass(frozen=True)
class Family:
    """One planner family of interfaces/c/pp_planner.h."""

    name: str      # "lcc", "lkaelk"
    prefix: str    # C symbol prefix
    library: str   # library name without lib and suffix
    inputs: str    # interface type names, see adapters/sil/pp_ctypes.py
    outputs: str


LCC = Family("lcc", "pp_lcc", "pp_lcc", "LccInputs", "LccOutputs")
LKAELK = Family("lkaelk", "pp_lkaelk", "pp_lkaelk", "LkaElkInputs", "LkaElkOutputs")
FAMILIES = (LCC, LKAELK)

_EGO_MOTION_FN = ctypes.CFUNCTYPE(
    None,
    ctypes.c_void_p,
    ctypes.POINTER(pp_ctypes.EgoMotionRequestC),
    ctypes.POINTER(pp_ctypes.EgoMotionResponseC),
)


def _suffix() -> str:
    return ".dylib" if sys.platform == "darwin" else ".so"


def library_path(name: str = "pp_lcc") -> Path:
    """A library of the in-repo build, by its name (pp_lcc, pp_lkaelk, pp_layout_probe)."""
    return BUILD_DIR / f"lib{name}{_suffix()}"


class IncompatibleLibrary(ValueError):
    """The file is not a planner library that can be called through pp_planner.h."""


def load_library(path: Path, family: Family = LCC) -> ctypes.CDLL:
    path = Path(path)
    if not path.is_file():
        raise IncompatibleLibrary(f"planner library not found: {path}")
    try:
        lib = ctypes.CDLL(str(path))
    except OSError as error:
        raise IncompatibleLibrary(f"cannot load {path}: {error}") from error
    p = family.prefix
    missing = [f"{p}_{name}" for name in ("state_size", "init", "step") if not hasattr(lib, f"{p}_{name}")]
    if missing:
        raise IncompatibleLibrary(f"{path}: missing {', '.join(missing)} (interfaces/c/pp_planner.h)")
    size = getattr(lib, f"{p}_state_size")
    size.restype = ctypes.c_size_t
    size.argtypes = []
    init = getattr(lib, f"{p}_init")
    init.restype = ctypes.c_uint8
    init.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(pp_ctypes.VehicleConfigC)]
    step = getattr(lib, f"{p}_step")
    step.restype = None
    step.argtypes = [ctypes.c_void_p, ctypes.POINTER(getattr(pp_ctypes, f"{family.inputs}C")),
                     _EGO_MOTION_FN, ctypes.c_void_p, ctypes.POINTER(getattr(pp_ctypes, f"{family.outputs}C"))]
    if hasattr(lib, f"{p}_version"):  # a library without it still runs, conformance C1 reports it
        version = getattr(lib, f"{p}_version")
        version.restype = ctypes.c_char_p
        version.argtypes = []
    return lib


def library_version(path: Path, family: Family = LCC) -> str | None:
    """Identification string of a built library (pp_<planner>_version()), None if it has none."""
    lib = load_library(Path(path), family)
    fn = getattr(lib, f"{family.prefix}_version", None)
    return fn().decode("ascii", errors="replace") if fn is not None else None


@functools.lru_cache(maxsize=None)
def _cached_library(path: str, family_name: str) -> ctypes.CDLL:
    family = next(f for f in FAMILIES if f.name == family_name)
    return load_library(Path(path), family)


@dataclass(frozen=True)
class PlannerLibraries:
    """Planner factory (interfaces.PlannerFactory) for the two C libraries built against
    interfaces/c/pp_planner.h. Picklable, so a worker process loads the libraries itself; each
    process loads a path once. Instances of one library share its process image, as two
    instances on one ECU would. `lcc` and `lka_elk` may be the same file."""

    lcc: Path
    lka_elk: Path
    only: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "lcc", Path(self.lcc).resolve())
        object.__setattr__(self, "lka_elk", Path(self.lka_elk).resolve())

    @classmethod
    def at(cls, location: Path) -> "PlannerLibraries":
        """A directory with libpp_lcc and libpp_lkaelk, or one file exporting both families."""
        location = Path(location)
        if location.is_dir():
            return cls(location / f"libpp_lcc{_suffix()}", location / f"libpp_lkaelk{_suffix()}")
        return cls(location, location)

    @classmethod
    def default(cls) -> "PlannerLibraries":
        """PP_PLANNER_LIB, else the in-repo build."""
        override = os.environ.get("PP_PLANNER_LIB")
        return cls.at(Path(override) if override else BUILD_DIR)

    @property
    def path(self) -> Path:
        """The LCC library: the one to show where a single path is wanted."""
        return self.paths()[0][0]

    @property
    def location(self) -> Path:
        return self.lcc if self.lcc == self.lka_elk else self.lcc.parent

    def paths(self) -> tuple[tuple[Path, Family], ...]:
        """Each library once with the family it is read for; a file with both families once per family."""
        libraries = ((self.lcc, LCC), (self.lka_elk, LKAELK))
        return tuple((path, family) for path, family in libraries
                     if self.only is None or self.only == family.name)

    def load(self) -> tuple[ctypes.CDLL, ...]:
        return tuple(_cached_library(str(path), family.name) for path, family in self.paths())

    def version(self) -> str | None:
        """Both identification strings, joined with ' | '; None when a library has none."""
        texts = [library_version(path, family) for path, family in self.paths()]
        return None if any(t is None for t in texts) else " | ".join(texts)

    def __call__(self, vehicle_config: VehicleConfig | None) -> PlannerSet:
        instances = {family.name: SilPlanner(vehicle_config, library, family)
                     for (_, family), library in zip(self.paths(), self.load())}
        return PlannerSet(instances.get(LCC.name), instances.get(LKAELK.name))


class SilPlanner:
    """One planner instance in a C library; meets interfaces.LccPlanner or LkaElkPlanner."""

    def __init__(self, vehicle_config: VehicleConfig | None, library: ctypes.CDLL, family: Family) -> None:
        self._lib = library
        self._family = family
        p = family.prefix
        self._step = getattr(library, f"{p}_step")
        size = int(getattr(library, f"{p}_state_size")())
        words = (size + STATE_ALIGNMENT - 1) // STATE_ALIGNMENT
        self._state = (ctypes.c_uint64 * words)()  # 8-byte aligned, owned here, no heap in C
        config = (ctypes.pointer(to_c(vehicle_config, "VehicleConfig"))
                  if vehicle_config is not None else None)
        self._init_result = InitResult(
            getattr(library, f"{p}_init")(self._state, ctypes.sizeof(self._state), config))
        self._inputs = getattr(pp_ctypes, f"{family.inputs}C")()
        self._outputs = getattr(pp_ctypes, f"{family.outputs}C")()

    @property
    def init_result(self) -> InitResult:
        return self._init_result

    def step(self, inputs: LccInputs | LkaElkInputs, ego_motion: EgoMotionQuery) -> LccOutputs | LkaElkOutputs:
        errors: list[BaseException] = []

        def answer(_context, request_ptr, response_ptr) -> None:
            try:
                request = from_c(request_ptr.contents, "EgoMotionRequest")
                to_c(ego_motion(request), "EgoMotionResponse", response_ptr.contents)
            except BaseException as error:  # never let an exception cross into C
                errors.append(error)
                response_ptr.contents.valid = False

        callback = _EGO_MOTION_FN(answer)  # kept alive for the duration of the call
        to_c(inputs, self._family.inputs, self._inputs)
        self._step(self._state, ctypes.byref(self._inputs), callback, None, ctypes.byref(self._outputs))
        if errors:
            raise errors[0]
        return from_c(self._outputs, self._family.outputs)

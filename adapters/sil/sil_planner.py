"""SIL adapter: the C planner library behind the Python Planner contract.

The simulator calls exactly the library that would be delivered (PP-ADR-013). This is
the only place that knows the planner is C. A real vehicle needs its own adapter for
its platform instead (PP-ASM-019).
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
    PlannerInputs,
    PlannerOutputs,
    VehicleConfig,
)

ROOT = Path(__file__).resolve().parents[2]
BUILD_DIR = ROOT / "build" / "planner"
STATE_ALIGNMENT = 8  # PP_STATE_ALIGNMENT in interfaces/c/pp_planner.h
# Calls of interfaces/c/pp_planner.h needed to run a planner at all. pp_version is also part
# of the contract; a library without it still runs, conformance C1 reports it.
REQUIRED_SYMBOLS = ("pp_state_size", "pp_init", "pp_step")
# In-house builds known to use an older PathStatus layout (before independent LKA and ELK
# phases). Other libraries are not judged by name; layout is checked by conformance C1.
_INCOMPATIBLE_VERSIONS = ("pp_planner 0.0.", "pp_planner 0.1.")

_EGO_MOTION_FN = ctypes.CFUNCTYPE(
    None,
    ctypes.c_void_p,
    ctypes.POINTER(pp_ctypes.EgoMotionRequestC),
    ctypes.POINTER(pp_ctypes.EgoMotionResponseC),
)


def library_path(name: str = "pp_planner") -> Path:
    """Built library; PP_PLANNER_LIB overrides the default build location."""
    override = os.environ.get("PP_PLANNER_LIB") if name == "pp_planner" else None
    if override:
        return Path(override)
    suffix = ".dylib" if sys.platform == "darwin" else ".so"
    return BUILD_DIR / f"lib{name}{suffix}"


class IncompatibleLibrary(ValueError):
    """The file is not a planner library that can be called through pp_planner.h."""


def load_library(path: Path | None = None) -> ctypes.CDLL:
    path = Path(path or library_path())
    if not path.is_file():
        raise IncompatibleLibrary(f"planner library not found: {path}")
    try:
        lib = ctypes.CDLL(str(path))
    except OSError as error:
        raise IncompatibleLibrary(f"cannot load {path}: {error}") from error
    missing = [name for name in REQUIRED_SYMBOLS if not hasattr(lib, name)]
    if missing:
        raise IncompatibleLibrary(f"{path}: missing {', '.join(missing)} (interfaces/c/pp_planner.h)")
    lib.pp_state_size.restype = ctypes.c_size_t
    lib.pp_state_size.argtypes = []
    lib.pp_init.restype = ctypes.c_uint8
    lib.pp_init.argtypes = [ctypes.c_void_p, ctypes.c_size_t,
                            ctypes.POINTER(pp_ctypes.VehicleConfigC)]
    lib.pp_step.restype = None
    lib.pp_step.argtypes = [ctypes.c_void_p, ctypes.POINTER(pp_ctypes.PlannerInputsC),
                            _EGO_MOTION_FN, ctypes.c_void_p,
                            ctypes.POINTER(pp_ctypes.PlannerOutputsC)]
    if hasattr(lib, "pp_version"):  # libraries built before pp_version() lack it
        lib.pp_version.restype = ctypes.c_char_p
        lib.pp_version.argtypes = []
    return lib


def library_version(path: Path | None = None) -> str | None:
    """Identification string of a built library (pp_version()), None if it has none."""
    lib = load_library(path)
    return lib.pp_version().decode("ascii", errors="replace") if hasattr(lib, "pp_version") else None


def check_version(lib: ctypes.CDLL) -> str | None:
    """pp_version() of a loaded library; refuses known incompatible in-house builds."""
    if not hasattr(lib, "pp_version"):
        return None
    version = lib.pp_version().decode("ascii", errors="replace")
    if version.startswith(_INCOMPATIBLE_VERSIONS):
        raise IncompatibleLibrary(f"Incompatible PathStatus ABI in {lib._name}: {version}")
    return version


@functools.lru_cache(maxsize=None)
def _cached_library(path: str) -> ctypes.CDLL:
    lib = load_library(Path(path))
    check_version(lib)
    return lib


@dataclass(frozen=True)
class PlannerLibrary:
    """Planner factory (interfaces.PlannerFactory) for any C library built against
    interfaces/c/pp_planner.h. Picklable, so a worker process loads the library itself;
    each process loads one path once. Instances of one library share its process image,
    as two instances on one ECU would."""

    path: Path

    def __post_init__(self) -> None:
        object.__setattr__(self, "path", Path(self.path).resolve())

    def load(self) -> ctypes.CDLL:
        return _cached_library(str(self.path))

    def version(self) -> str | None:
        return check_version(self.load())

    def __call__(self, vehicle_config: VehicleConfig | None) -> "SilPlanner":
        return SilPlanner(vehicle_config, library=self.load())


class SilPlanner:
    """One planner instance in the C library; meets interfaces.Planner."""

    def __init__(self, vehicle_config: VehicleConfig | None, library: ctypes.CDLL | None = None) -> None:
        self._lib = library or _cached_library(str(library_path()))
        check_version(self._lib)
        size = int(self._lib.pp_state_size())
        words = (size + STATE_ALIGNMENT - 1) // STATE_ALIGNMENT
        self._state = (ctypes.c_uint64 * words)()  # 8-byte aligned, owned here, no heap in C
        config = (ctypes.pointer(to_c(vehicle_config, "VehicleConfig"))
                  if vehicle_config is not None else None)
        self._init_result = InitResult(
            self._lib.pp_init(self._state, ctypes.sizeof(self._state), config))
        self._inputs = pp_ctypes.PlannerInputsC()
        self._outputs = pp_ctypes.PlannerOutputsC()

    @property
    def init_result(self) -> InitResult:
        return self._init_result

    def step(self, inputs: PlannerInputs, ego_motion: EgoMotionQuery) -> PlannerOutputs:
        errors: list[BaseException] = []

        def answer(_context, request_ptr, response_ptr) -> None:
            try:
                request = from_c(request_ptr.contents, "EgoMotionRequest")
                to_c(ego_motion(request), "EgoMotionResponse", response_ptr.contents)
            except BaseException as error:  # never let an exception cross into C
                errors.append(error)
                response_ptr.contents.valid = False

        callback = _EGO_MOTION_FN(answer)  # kept alive for the duration of the call
        to_c(inputs, "PlannerInputs", self._inputs)
        self._lib.pp_step(self._state, ctypes.byref(self._inputs), callback, None,
                          ctypes.byref(self._outputs))
        if errors:
            raise errors[0]
        return from_c(self._outputs, "PlannerOutputs")

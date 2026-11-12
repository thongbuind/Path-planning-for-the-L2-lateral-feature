"""Raw calls into a planner library for conformance B0 (Software Qualification Test
Specification 11): state memory with guard bytes, outputs pre-filled with a sentinel,
outputs read back field by field, and input sequences built without the simulator.

Only interfaces/c/pp_planner.h and the generated types are used; nothing of the planner's
inside is known here.
"""

import ctypes
import math
from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np

import interfaces as I
from adapters.sil import pp_ctypes
from adapters.sil.sil_planner import STATE_ALIGNMENT, load_library

GUARD_BYTES = 256  # each side of the state memory
GUARD_PATTERN = 0xC3
SENTINELS = (0xA5, 0x5A)  # outputs pre-fill, alternating per cycle
T_START_US = 1_000_000  # first cycle; stamps stay positive
FLT_MAX = float(np.finfo(np.float32).max)

EGO_MOTION_FN = ctypes.CFUNCTYPE(None, ctypes.c_void_p,
                                 ctypes.POINTER(pp_ctypes.EgoMotionRequestC),
                                 ctypes.POINTER(pp_ctypes.EgoMotionResponseC))


# ---- leaves of a ctypes struct ---------------------------------------------------------

@dataclass(frozen=True)
class Leaf:
    path: str
    offset: int
    ctype: type
    enum: type | None = None

    @property
    def size(self) -> int:
        return ctypes.sizeof(self.ctype)

    @property
    def is_float(self) -> bool:
        return self.ctype in (ctypes.c_float, ctypes.c_double)

    @property
    def is_bool(self) -> bool:
        return self.ctype is ctypes.c_bool

    def read(self, raw: bytes):
        return self.ctype.from_buffer_copy(raw, self.offset).value


def _enum_fields() -> dict[tuple[str, str], type]:
    out = {}
    for type_name, specs in pp_ctypes.FIELD_SPECS.items():
        for name, kind, ref in specs:
            if kind in ("enum", "array_enum"):
                out[(f"{type_name}C", name)] = getattr(I, ref)
    return out


_ENUMS = _enum_fields()


@lru_cache(maxsize=None)
def leaves(cls: type[ctypes.Structure]) -> tuple[Leaf, ...]:
    """Every scalar field of a struct with its byte offset; padding is not a field."""
    out: list[Leaf] = []

    def walk(struct: type[ctypes.Structure], base: int, prefix: str) -> None:
        for name, ctype in struct._fields_:
            offset = base + getattr(struct, name).offset
            path = f"{prefix}{name}"
            enum = _ENUMS.get((struct.__name__, name))
            if isinstance(ctype, type) and issubclass(ctype, ctypes.Structure):
                walk(ctype, offset, path + ".")
            elif isinstance(ctype, type) and issubclass(ctype, ctypes.Array):
                item = ctype._type_
                step = ctypes.sizeof(item)
                for i in range(ctype._length_):
                    if issubclass(item, ctypes.Structure):
                        walk(item, offset + i * step, f"{path}[{i}].")
                    else:
                        out.append(Leaf(f"{path}[{i}]", offset + i * step, item, enum))
            else:
                out.append(Leaf(path, offset, ctype, enum))

    walk(cls, 0, "")
    return tuple(out)


def sub_leaves(cls: type[ctypes.Structure], prefix: str) -> tuple[Leaf, ...]:
    return tuple(leaf for leaf in leaves(cls) if leaf.path.startswith(prefix))


def set_leaf(struct: ctypes.Structure, leaf: Leaf, value) -> None:
    leaf.ctype.from_buffer(struct, leaf.offset).value = value


# ---- one planner instance --------------------------------------------------------------

def vehicle_config_c(config: I.VehicleConfig | None):
    if config is None:
        return None
    from adapters.sil.convert import to_c
    return ctypes.pointer(to_c(config, "VehicleConfig"))


@dataclass
class StepResult:
    raw: bytes  # PlannerOutputsC
    sentinel: int
    requests: list[tuple[int, int]]


class Instance:
    """One planner instance in caller-owned memory: guard | state | guard. The state starts
    at an address aligned to PP_STATE_ALIGNMENT but not to twice that (C1)."""

    def __init__(self, lib: ctypes.CDLL, config: I.VehicleConfig | None) -> None:
        self.lib = lib
        self.state_size = int(lib.pp_state_size())
        total = GUARD_BYTES + self.state_size + GUARD_BYTES + 4 * STATE_ALIGNMENT
        self._memory = (ctypes.c_uint8 * total)()
        base = ctypes.addressof(self._memory)
        first = -(-(base + GUARD_BYTES) // (2 * STATE_ALIGNMENT)) * (2 * STATE_ALIGNMENT) + STATE_ALIGNMENT
        self._state_offset = first - base
        self._guards = ((self._state_offset - GUARD_BYTES, self._state_offset),
                        (self._state_offset + self.state_size,
                         self._state_offset + self.state_size + GUARD_BYTES))
        for lo, hi in self._guards:
            ctypes.memset(base + lo, GUARD_PATTERN, hi - lo)
        self.state = ctypes.c_void_p(first)
        self._config = vehicle_config_c(config)
        self.init_result = int(lib.pp_init(self.state, self.state_size, self._config))
        self._outputs = pp_ctypes.PlannerOutputsC()

    def guards_intact(self) -> bool:
        raw = bytes(self._memory)
        return all(all(b == GUARD_PATTERN for b in raw[lo:hi]) for lo, hi in self._guards)

    def step(self, inputs: pp_ctypes.PlannerInputsC, motion: "Motion", sentinel: int) -> StepResult:
        requests: list[tuple[int, int]] = []

        def answer(_context, request_ptr, response_ptr) -> None:
            req = request_ptr.contents
            requests.append((int(req.t1_us), int(req.t2_us)))
            motion.answer(int(req.t1_us), int(req.t2_us), response_ptr.contents)

        callback = EGO_MOTION_FN(answer)
        ctypes.memset(ctypes.byref(self._outputs), sentinel, ctypes.sizeof(self._outputs))
        self.lib.pp_step(self.state, ctypes.byref(inputs), callback, None, ctypes.byref(self._outputs))
        return StepResult(bytes(self._outputs), sentinel, requests)


def open_library(path) -> ctypes.CDLL:
    return load_library(path)


# ---- input sequences -------------------------------------------------------------------

@dataclass
class Motion:
    """EgoMotionQuery answers: straight driving at a constant speed (Interface Control
    Document 5.5), optionally reported invalid."""
    speed_mps: float = 20.0
    valid: bool = True

    def answer(self, t1_us: int, t2_us: int, response) -> None:
        response.valid = self.valid
        response.dx = self.speed_mps * (t2_us - t1_us) * 1e-6
        response.dy = 0.0
        response.dyaw = 0.0


@dataclass
class Sequence:
    """Input of every cycle; `frame(k)` returns PlannerInputsC for cycle k."""
    name: str
    cycles: int
    seed: int | None = None  # None: nominal straight road; else seeded variations
    absent: frozenset = frozenset()  # inputs never received
    invalid: frozenset = frozenset()  # inputs with header.valid = false
    extreme: tuple[str, str] | None = None  # (input, "low"|"high"): payload at the range ends
    motion: Motion = field(default_factory=Motion)

    def frame(self, k: int) -> pp_ctypes.PlannerInputsC:
        return build_inputs(self, k)


INPUTS = ("lane_model", "object_list", "imu", "steering", "speed", "vehicle_state",
          "function_requests", "longitudinal_plan")

# Range ends: the CAN encoding of Interface Control Document 5.3 for chassis signals (what
# the receiving layer can deliver after scaling to SI); else a range the Interface Control
# Document gives; else the range of the type.
_INT16 = (-32768, 32767)
_DEG = math.pi / 180.0
DBC_RANGE = {
    ("imu", "yaw_rate_rps"): tuple(r * 0.01 * _DEG for r in _INT16),          # int16 × 0,01 °/s
    ("imu", "accel_x_mps2"): tuple(r * 0.001 for r in _INT16),                # int16 × 0,001 m/s²
    ("imu", "accel_y_mps2"): tuple(r * 0.001 for r in _INT16),
    ("steering", "steering_wheel_angle_rad"): tuple(r * 0.1 * _DEG for r in _INT16),  # int16 × 0,1 °
    ("steering", "steering_wheel_rate_rps"): tuple(r * 0.1 * _DEG for r in _INT16),   # int16 × 0,1 °/s
    ("speed", "speed_mps"): (0.0, 65535 * 0.01 / 3.6),                         # uint16 × 0,01 km/h
}
_UNIT_RANGE = ("confidence", "existence_probability")


def _end(leaf: Leaf, which: str, message: str = ""):
    low = which == "low"
    name = leaf.path.rsplit(".", 1)[-1].split("[")[0]
    if (message, name) in DBC_RANGE:
        return DBC_RANGE[(message, name)][0 if low else 1]
    if leaf.enum is not None:
        values = [int(v) for v in leaf.enum]
        return min(values) if low else max(values)
    if leaf.is_bool:
        return not low
    if name in _UNIT_RANGE:
        return 0.0 if low else 1.0
    if name == "num_objects":
        return 0 if low else I.MAX_OBJECTS
    if leaf.is_float:
        return -FLT_MAX if low else FLT_MAX
    bits = 8 * leaf.size
    return 0 if low else (1 << bits) - 1


def _header(h, t_us: int, counter: int, valid: bool, frame: bool = True) -> None:
    h.stamp_us = t_us
    h.counter = counter % 256
    h.valid = valid
    if frame:
        h.frame_id = int(I.FrameId.BASE_LINK)


def build_inputs(seq: Sequence, k: int) -> pp_ctypes.PlannerInputsC:
    t0 = T_START_US + k * I.PLANNER_PERIOD_US
    rng = np.random.default_rng([seq.seed, k]) if seq.seed is not None else None
    # Seeded variations: the car weaves in the lane, the road bends, LKA requests come and go.
    offset = 0.3 * math.sin(k / 23.0) if rng is not None else 0.0
    curve = 1e-3 * math.sin(k / 61.0) if rng is not None else 0.0
    lka_request = rng is not None and (k // 80) % 3 == 1
    x = pp_ctypes.PlannerInputsC()
    x.t0_us = t0

    lm = x.lane_model.message
    _header(lm.header, t0 - 50_000, k, "lane_model" not in seq.invalid)
    for i, c0 in enumerate((5.25, 1.75, -1.75, -5.25)):
        line = lm.lines[i]
        line.c0 = c0 - offset + (float(rng.normal(0, 0.02)) if rng is not None else 0.0)
        line.c1, line.c2, line.c3 = 0.0, curve / 2, 0.0
        for j in range(4):
            line.variance[j] = 1e-4
        line.view_range_start, line.view_range_end = 0.0, 80.0
        line.confidence = 0.9
        line.type = int(I.LineType.DASHED)
        line.crossable = True
        line.status = int(I.LineStatus.MEASURED)
        line.predicted_duration = 0.0
    for i, c0 in enumerate((7.0, -7.0)):
        edge = lm.road_edges[i]
        edge.c0, edge.c1, edge.c2, edge.c3 = c0 - offset, 0.0, curve / 2, 0.0
        for j in range(4):
            edge.variance[j] = 1e-4
        edge.view_range_start, edge.view_range_end = 0.0, 80.0
        edge.confidence = 0.9
        edge.type = int(I.RoadEdgeType.CURB)
        edge.status = int(I.LineStatus.MEASURED)
        edge.predicted_duration = 0.0
    lm.lane_width = 3.5
    lm.lane_width_source = int(I.LaneWidthSource.MEASURED)
    lm.lane_change = int(I.Side.NONE)
    x.lane_model.rx_us = t0 - 5_000

    ol = x.object_list.message
    _header(ol.header, t0 - 50_000, k, "object_list" not in seq.invalid)
    ol.num_objects = 0
    x.object_list.rx_us = t0 - 5_000

    v = seq.motion.speed_mps
    for name, fill in (("imu", lambda m: (setattr(m, "yaw_rate_rps", v * curve), setattr(m, "accel_x_mps2", 0.0),
                                          setattr(m, "accel_y_mps2", v * v * curve))),
                       ("steering", lambda m: (setattr(m, "steering_wheel_angle_rad", 0.0),
                                               setattr(m, "steering_wheel_rate_rps", 0.0))),
                       ("speed", lambda m: (setattr(m, "speed_mps", v),
                                            setattr(m, "direction", int(I.Direction.FORWARD))))):
        slot = getattr(x, name)
        _header(slot.message.header, t0 - 2_000, k, name not in seq.invalid, frame=False)
        fill(slot.message)
        slot.rx_us = t0 - 2_000

    vs = x.vehicle_state.message
    _header(vs.header, t0 - 5_000, k, "vehicle_state" not in seq.invalid)
    vs.lateral_velocity, vs.lateral_velocity_variance, vs.slip_angle = 0.0, 1e-3, 0.0
    x.vehicle_state.rx_us = t0 - 3_000

    fr = x.function_requests.message
    _header(fr.header, t0 - 5_000, k, "function_requests" not in seq.invalid, frame=False)
    states = (I.RequestState.REQUEST,
              I.RequestState.REQUEST if lka_request else I.RequestState.STANDBY,
              I.RequestState.STANDBY)
    for i, state in enumerate(states):
        r = fr.requests[i]
        r.state = int(state)
        r.side = int(I.Side.LEFT if (i == 1 and lka_request) else I.Side.NONE)
        r.tlc = 0.8 if (i == 1 and lka_request) else 0.0
        r.elk_reason = int(I.ElkReason.NONE)
        r.cancel_reason = int(I.CancelReason.NONE)
    fr.driver_override = False
    x.function_requests.rx_us = t0 - 3_000

    lp = x.longitudinal_plan.message
    _header(lp.header, t0 - 5_000, k, "longitudinal_plan" not in seq.invalid)
    lp.mode = int(I.LongitudinalMode.CRUISE)
    for i in range(I.LONGITUDINAL_PLAN_POINTS):
        lp.points[i].v, lp.points[i].a = v, 0.0
    lp.target_id = 0
    x.longitudinal_plan.rx_us = t0 - 3_000

    for name in INPUTS:
        getattr(x, name).present = name not in seq.absent
    if seq.extreme is not None:
        name, which = seq.extreme
        message = getattr(x, name).message
        for leaf in leaves(type(message)):
            if not leaf.path.startswith("header."):  # header stays valid: the payload is judged
                set_leaf(message, leaf, _end(leaf, which, name))
    return x

"""Lỗi kênh tác động tại lúc phát lên các message trong khoảng [start_s, start_s + duration_s)."""

from dataclasses import dataclass, field, replace

import numpy as np

import interfaces as I
from sim.faults import trigger

KINDS = ("drop", "burst", "jitter", "late", "stop", "future_stamp", "counter_repeat",
         "counter_jump", "counter_stuck", "invalid", "crc", "drop_listed", "out_of_range",
         "lead_id", "lead_class", "lead_noise")
CHANNELS = ("lane_model", "object_list", "lead_target", "imu", "steering", "speed", "vehicle_state",
            "function_requests", "longitudinal_plan")
# Một số lỗi tương đương mất đúng frame bị ảnh hưởng (PP-SWR-130), hoặc tương đương không tiêm lỗi
# (PP-SWR-129).
LOSS_EQUIVALENT = ("counter_jump", "counter_stuck", "invalid")
NO_FAULT_EQUIVALENT = ("counter_repeat",)
MAX_DELTA_COUNTER = {"lane_model": I.LANE_MODEL_MAX_DELTA_COUNTER,
                     "object_list": I.OBJECT_LIST_MAX_DELTA_COUNTER,
                     "lead_target": I.LEAD_TARGET_MAX_DELTA_COUNTER,
                     "vehicle_state": I.VEHICLE_STATE_MAX_DELTA_COUNTER,
                     "function_requests": I.FUNCTION_REQUESTS_MAX_DELTA_COUNTER,
                     "longitudinal_plan": I.LONGITUDINAL_PLAN_MAX_DELTA_COUNTER}


@dataclass(frozen=True, slots=True)
class ChannelFault:
    kind: str
    channel: str
    start_s: float = 0.0
    duration_s: float | None = None
    value: float = 0.0
    every: int = 1
    count: int = 1
    indices: tuple[int, ...] = ()
    trigger: str | None = None  # Nếu có trigger, start_s tính từ sự kiện kích hoạt.
    field: str = ""

    def __post_init__(self) -> None:
        trigger.check(self.trigger)
        if self.kind not in KINDS or self.channel not in CHANNELS:
            raise ValueError(f"unknown channel fault {self.kind!r} on {self.channel!r}")
        if self.kind in ("lead_id", "lead_class", "lead_noise") and self.channel != "lead_target":
            raise ValueError("lead_id and lead_class need channel lead_target")
        if self.kind == "out_of_range" and (self.channel != "longitudinal_plan" or self.field not in ("v", "a")):
            raise ValueError("out_of_range needs channel longitudinal_plan and field v or a")
        if self.every < 1 or self.count < 0 or self.start_s < 0 or (self.duration_s is not None and self.duration_s <= 0):
            raise ValueError("channel fault needs every >= 1, count >= 0, start >= 0, duration > 0")

    def active(self, t_us: int) -> bool:
        start = round(self.start_s * 1e6)
        return t_us >= start and (self.duration_s is None or t_us < start + round(self.duration_s * 1e6))


@dataclass
class _State:
    index: int = 0
    in_window: int = 0
    held_counter: int | None = None
    counter_offset: int = 0
    hit: list[int] | None = None
    lead_stamps: list[int] = field(default_factory=list)


class ChannelFaultInjector:
    def __init__(self, faults: tuple[ChannelFault, ...], rng: np.random.Generator | None = None) -> None:
        self.faults = faults
        self._rng = rng
        self._states = [_State(hit=[]) for _ in faults]

    def deliveries(self, message, now_us: int, index: int) -> list[tuple[int, object]]:
        out = [(0, message)]
        for fault, st in zip(self.faults, self._states):
            last_counter = st.held_counter
            if not fault.active(now_us):
                if fault.kind == "counter_stuck":
                    st.held_counter = _counter(message)
                if fault.kind == "counter_jump" and st.counter_offset:
                    out = [(d, _with_counter(m, _counter(m) + st.counter_offset)) for d, m in out]
                continue
            k = st.in_window
            st.in_window += 1
            kind = fault.kind
            pick = k % fault.every == 0
            if kind == "stop" or (kind == "drop" and pick) or (kind == "drop_listed" and index in fault.indices):
                if fault.channel == "lead_target":
                    st.lead_stamps.append(message.header.stamp_us)
                return []
            if kind == "burst" and k % fault.every < fault.count:
                return []
            if kind == "jitter":
                extra = int(self._rng.integers(-round(fault.value * 1000), round(fault.value * 1000) + 1))
                out = [(d + extra, m) for d, m in out]
            elif kind == "late" and pick:
                out = [(d + round(fault.value * 1000), m) for d, m in out]
            elif kind == "future_stamp" and (fault.count == 0 or k < fault.count):
                out = [(d, _restamp(m, round(fault.value * 1000))) for d, m in out]
            elif kind == "counter_repeat" and pick:
                out = out + [(d + round(fault.value * 1000), m) for d, m in out]
            elif kind == "counter_jump":
                if pick:
                    st.counter_offset += fault.count
                    st.hit.append(index)
                if st.counter_offset:
                    out = [(d, _with_counter(m, _counter(m) + st.counter_offset)) for d, m in out]
            elif kind == "counter_stuck" and last_counter is not None:
                out = [(d, _with_counter(m, last_counter)) for d, m in out]
                st.hit.append(index)
            elif kind == "invalid" and pick:
                out = [(d, _with_valid(m, False)) for d, m in out]
                st.hit.append(index)
            elif kind == "crc" and pick:
                out = [(d, m.with_bad_crc()) for d, m in out]
                st.hit.append(index)
            elif kind == "out_of_range":
                out = [(d, _with_points(m, fault)) for d, m in out]
                st.hit.append(index)
            elif kind == "lead_id":
                out = [(d, replace(m, id=m.id + round(fault.value))) for d, m in out]
                st.lead_stamps.append(message.header.stamp_us)
            elif kind == "lead_noise":
                out = [(d, _lead_noise(m, fault.value, self._rng)) for d, m in out]
                st.lead_stamps.append(message.header.stamp_us)
            elif kind == "lead_class":
                out = [(d, replace(m, classification=I.LeadClass(round(fault.value)))) for d, m in out]
                st.lead_stamps.append(message.header.stamp_us)
        return out

    def lead_fault_stamps(self) -> list[int]:
        return sorted({stamp for state in self._states for stamp in state.lead_stamps})

    def fault_hits(self) -> list[list[int]]:
        return [list(st.hit) for st in self._states]


CAN_CHANNELS = ("imu", "steering", "speed")


def has_twin(fault: ChannelFault, can_bus: bool = False) -> bool:
    can = can_bus and fault.channel in CAN_CHANNELS
    if fault.kind == "invalid" and fault.channel in CAN_CHANNELS:
        # Qualifier FAULT là cảm biến tự báo hỏng, chấm theo PP-SWR-142, không so với ca mất khung
        # (SRS 1.27, PP-PR-036).
        return False
    return fault.kind in LOSS_EQUIVALENT + NO_FAULT_EQUIVALENT or (can and fault.kind == "crc")


def requirement(fault: ChannelFault, can_bus: bool = False) -> str:
    twin = equivalent(fault, [], can_bus)
    return "PP-SWR-129" if twin is None else "PP-SWR-130"


def equivalent(fault: ChannelFault, hit: list[int], can_bus: bool = False) -> ChannelFault | None:
    """Trên CAN, counter lặp và CRC sai bị bỏ, counter nhảy vẫn nhận. Pub/sub có giới hạn bước
    counter riêng.
    """
    can = can_bus and fault.channel in CAN_CHANNELS
    if fault.kind in NO_FAULT_EQUIVALENT or (can and fault.kind == "counter_jump"):
        return None
    if fault.kind == "counter_jump" and fault.count + 1 <= MAX_DELTA_COUNTER.get(fault.channel, 0):
        return None
    if fault.kind in LOSS_EQUIVALENT or (can and fault.kind == "crc"):
        return ChannelFault("drop_listed", fault.channel, indices=tuple(hit))
    raise ValueError(f"{fault.kind} has no reference twin")


def _is_frame(message) -> bool:
    return hasattr(message, "can_id")


def _counter(message) -> int:
    return message.counter if _is_frame(message) else message.header.counter


def _with_counter(message, counter: int):
    if _is_frame(message):
        return message.with_byte6(counter % 16, message.qualifier)
    return replace(message, header=replace(message.header, counter=counter % I.COUNTER_MODULO))


def _lead_noise(message, scale: float, rng):
    """Cộng nhiễu độc lập để sigma tổng của LeadTarget bằng scale lần giá trị danh định."""
    from math import hypot, sqrt
    from sim.sensors.lead_sensor import SIGMA_HEADING_RAD
    from sim.sensors.object_sensor import SIGMA_X_M, SIGMA_X_REL, SIGMA_Y_M, SIGMA_Y_REL
    extra = sqrt(max(scale * scale - 1.0, 0.0))
    draws = rng.standard_normal(3)
    r = hypot(message.x, message.y)
    return replace(message, x=message.x + extra * (SIGMA_X_M + SIGMA_X_REL * r) * float(draws[0]),
                   y=message.y + extra * (SIGMA_Y_M + SIGMA_Y_REL * r) * float(draws[1]),
                   heading=message.heading + extra * SIGMA_HEADING_RAD * float(draws[2]))


def _with_valid(message, valid: bool):
    if _is_frame(message):
        return message.with_byte6(message.counter, 0 if valid else 3)
    return replace(message, header=replace(message.header, valid=valid))


def _with_points(message, fault: ChannelFault):
    points = tuple(replace(p, **{fault.field: fault.value}) if not fault.indices or i in fault.indices else p
                   for i, p in enumerate(message.points))
    return replace(message, points=points)


def _restamp(message, add_us: int):
    if _is_frame(message):
        return message  # Frame CAN không mang stamp; receiver gắn thời điểm nhận (ICD 4).
    return replace(message, header=replace(message.header, stamp_us=message.header.stamp_us + add_us))

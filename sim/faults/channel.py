"""Faults on one message channel (Software Qualification Test Specification 4.2, 6: F10,
F11, F12, F15, F16, F19, F23).

Applied when a message is published, to messages published inside [start_s, start_s +
duration_s). Which message is hit depends only on its index on the channel, so a fault
never shifts a random stream, and its loss-equivalent (`equivalent()`) drops exactly the
messages the fault made unusable (PP-SWR-130).

| kind | Effect |
|---|---|
| drop | every `every`-th message is not delivered (isolated losses) |
| burst | `count` messages in a row not delivered, every `every` messages |
| jitter | extra delay uniform in +/- `value` ms; delivery may reorder |
| late | every `every`-th message delayed by `value` ms, so it arrives after a newer one |
| stop | nothing is delivered |
| future_stamp | header.stamp_us + `value` ms; `count` > 0: only the first `count` messages |
| counter_repeat | every `every`-th message delivered twice, the copy `value` ms later |
| counter_jump | every `every`-th message: counter + `count` (that message and the next keep the jump) |
| counter_stuck | counter held at the value before the window |
| invalid | header.valid = false; on a CAN frame qualifier FAULT (F16) |
| crc | CAN frame with a wrong CRC (F17) |
| drop_listed | the messages with index in `indices` are not delivered (loss-equivalent) |
| out_of_range | LongitudinalPlan only: `field` (v or a) of points `indices` (all when empty) set to `value` (F23) |

On a CAN channel the message is a sim.can.frames.CanFrame: the counter is the 4-bit frame
counter, changed by the sender (CRC still right). The CAN receive layer drops wrong CRC and
repeated counters, so the reference twin differs from a pub/sub channel (`equivalent`).
"""

from dataclasses import dataclass, replace

import numpy as np

from sim.faults import trigger

KINDS = ("drop", "burst", "jitter", "late", "stop", "future_stamp", "counter_repeat",
         "counter_jump", "counter_stuck", "invalid", "crc", "drop_listed", "out_of_range")
CHANNELS = ("lane_model", "object_list", "imu", "steering", "speed", "vehicle_state",
            "function_requests", "longitudinal_plan")
# Faults whose correct handling equals the loss of the messages they hit (PP-SWR-130), or
# equals no fault at all (PP-SWR-129).
LOSS_EQUIVALENT = ("counter_jump", "counter_stuck", "invalid")
NO_FAULT_EQUIVALENT = ("counter_repeat",)


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
    trigger: str | None = None  # sim.faults.trigger: start_s counts from this event
    field: str = ""  # out_of_range: payload field of LongitudinalPoint

    def __post_init__(self) -> None:
        trigger.check(self.trigger)
        if self.kind not in KINDS or self.channel not in CHANNELS:
            raise ValueError(f"unknown channel fault {self.kind!r} on {self.channel!r}")
        if self.kind == "out_of_range" and (self.channel != "longitudinal_plan" or self.field not in ("v", "a")):
            raise ValueError("out_of_range needs channel longitudinal_plan and field v or a")
        if self.every < 1 or self.count < 0 or self.start_s < 0 or (self.duration_s is not None and self.duration_s <= 0):
            raise ValueError("channel fault needs every >= 1, count >= 0, start >= 0, duration > 0")

    def active(self, t_us: int) -> bool:
        start = round(self.start_s * 1e6)
        return t_us >= start and (self.duration_s is None or t_us < start + round(self.duration_s * 1e6))


@dataclass
class _State:
    index: int = 0  # messages published on the channel so far
    in_window: int = 0  # messages published inside the window so far
    held_counter: int | None = None
    hit: list[int] | None = None  # indices made unusable (loss-equivalent bookkeeping)


class ChannelFaultInjector:
    """Turns one published message into the deliveries [(extra_delay_us, message)]."""

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
                continue
            k = st.in_window
            st.in_window += 1
            kind = fault.kind
            pick = k % fault.every == 0
            if kind == "stop" or (kind == "drop" and pick) or (kind == "drop_listed" and index in fault.indices):
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
            elif kind == "counter_jump" and pick:
                out = [(d, _with_counter(m, (_counter(m) + fault.count) % 256)) for d, m in out]
                st.hit.append(index)
            elif kind == "counter_stuck" and last_counter is not None:
                out = [(d, _with_counter(m, last_counter)) for d, m in out]
                st.hit.append(index)
            elif kind == "invalid":
                out = [(d, _with_valid(m, False)) for d, m in out]
                st.hit.append(index)
            elif kind == "crc":
                out = [(d, m.with_bad_crc()) for d, m in out]
                st.hit.append(index)
            elif kind == "out_of_range":
                out = [(d, _with_points(m, fault)) for d, m in out]
                st.hit.append(index)
        return out

    def fault_hits(self) -> list[list[int]]:
        """Per fault, in order: indices of the messages it made unusable."""
        return [list(st.hit) for st in self._states]


CAN_CHANNELS = ("imu", "steering", "speed")


def has_twin(fault: ChannelFault, can_bus: bool = False) -> bool:
    can = can_bus and fault.channel in CAN_CHANNELS
    return fault.kind in LOSS_EQUIVALENT + NO_FAULT_EQUIVALENT or (can and fault.kind == "crc")


def requirement(fault: ChannelFault, can_bus: bool = False) -> str:
    """PP-SWR-129 when the right handling equals no fault, else 130."""
    twin = equivalent(fault, [], can_bus)
    return "PP-SWR-129" if twin is None else "PP-SWR-130"


def equivalent(fault: ChannelFault, hit: list[int], can_bus: bool = False) -> ChannelFault | None:
    """Reference twin for PP-SWR-129, 130: None (no fault) or the loss of the messages hit.
    On a CAN channel the receive layer drops repeated counters and wrong CRC, and accepts a
    counter jump (counted as lost frames)."""
    can = can_bus and fault.channel in CAN_CHANNELS
    if fault.kind in NO_FAULT_EQUIVALENT or (can and fault.kind == "counter_jump"):
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
    return replace(message, header=replace(message.header, counter=counter))


def _with_valid(message, valid: bool):
    if _is_frame(message):
        return message.with_byte6(message.counter, 0 if valid else 3)  # qualifier VALID or FAULT
    return replace(message, header=replace(message.header, valid=valid))


def _with_points(message, fault: ChannelFault):
    points = tuple(replace(p, **{fault.field: fault.value}) if not fault.indices or i in fault.indices else p
                   for i, p in enumerate(message.points))
    return replace(message, points=points)


def _restamp(message, add_us: int):
    if _is_frame(message):
        return message  # CAN frames carry no stamp; the receiver stamps them (ICD 4)
    return replace(message, header=replace(message.header, stamp_us=message.header.stamp_us + add_us))

from dataclasses import dataclass
from math import pi

import numpy as np

from sim.faults import trigger

SIGNALS = ("yaw_rate", "accel_x", "accel_y", "speed", "steering_angle", "lateral_velocity")
KINDS = ("noise", "bias", "scale")
DEG = pi / 180.0

NOMINAL_SPEED_SIGMA = 0.02
NOMINAL_SPEED_SCALE = 0.005
NOMINAL_STEERING_SIGMA = 0.001
NOMINAL_STEERING_OFFSET = 0.01
NOMINAL_LATERAL_VELOCITY_SIGMA = 0.05


@dataclass(frozen=True, slots=True)
class SensorFault:
    kind: str
    signal: str
    value: float = 0.0
    start_s: float = 0.0
    duration_s: float | None = None
    trigger: str | None = None

    def __post_init__(self) -> None:
        trigger.check(self.trigger)
        if self.kind not in KINDS or self.signal not in SIGNALS:
            raise ValueError(f"unknown sensor fault {self.kind!r} on {self.signal!r}")
        if self.start_s < 0 or (self.duration_s is not None and self.duration_s <= 0) or (
                self.kind == "noise" and self.value < 0):
            raise ValueError("sensor fault needs start >= 0, duration > 0, sigma >= 0")

    def active(self, t_us: int) -> bool:
        start = round(self.start_s * 1e6)
        return t_us >= start and (self.duration_s is None or t_us < start + round(self.duration_s * 1e6))


def nominal(rng: np.random.Generator) -> tuple[SensorFault, ...]:
    return (SensorFault("noise", "speed", NOMINAL_SPEED_SIGMA),
            SensorFault("scale", "speed", float(rng.uniform(-NOMINAL_SPEED_SCALE, NOMINAL_SPEED_SCALE))),
            SensorFault("noise", "steering_angle", NOMINAL_STEERING_SIGMA),
            SensorFault("bias", "steering_angle", float(rng.uniform(-NOMINAL_STEERING_OFFSET, NOMINAL_STEERING_OFFSET))),
            SensorFault("noise", "lateral_velocity", NOMINAL_LATERAL_VELOCITY_SIGMA))


class SensorErrors:
    """Mỗi luồng tín hiệu có RNG riêng để thay lỗi của cảm biến này không làm lệch chuỗi của cảm
    biến khác.
    """

    def __init__(self, faults: tuple[SensorFault, ...], rngs: dict[str, np.random.Generator]) -> None:
        self.faults = faults
        self._rngs = rngs

    def apply(self, signal: str, value: float, t_us: int) -> float:
        for f in self.faults:
            if f.signal != signal:
                continue
            draw = float(self._rngs[signal].standard_normal()) if f.kind == "noise" else 0.0
            if not f.active(t_us):
                continue
            if f.kind == "noise":
                value += f.value * draw
            elif f.kind == "bias":
                value += f.value
            else:
                value *= 1.0 + f.value
        return value

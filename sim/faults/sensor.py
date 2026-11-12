"""Signal errors of the chassis sensors and VehicleStateEstimate (Software Qualification
Test Specification 4.5, 6: F07, F08; nominal sensor model).

| kind | Effect while active |
|---|---|
| noise | + N(0, value) at every sample |
| bias | + value |
| scale | x (1 + value) |

Noise is drawn at every sample, active or not, so the random stream does not depend on
the fault window.

NOMINAL holds the sensor errors of 4.5 that hold in every run ("Tốc độ", "Góc vô lăng",
"VehicleStateEstimate"). They are switched on with the nominal realism batch
(Scenario.realism); the scale error and the zero offset are drawn once per run.
"""

from dataclasses import dataclass
from math import pi

import numpy as np

from sim.faults import trigger

SIGNALS = ("yaw_rate", "accel_x", "accel_y", "speed", "steering_angle", "lateral_velocity")
KINDS = ("noise", "bias", "scale")
DEG = pi / 180.0

# Software Qualification Test Specification 4.5, column "Mức".
NOMINAL_SPEED_SIGMA = 0.02  # [m/s]
NOMINAL_SPEED_SCALE = 0.005  # +/- 0.5 %
NOMINAL_STEERING_SIGMA = 0.001  # [rad]
NOMINAL_STEERING_OFFSET = 0.01  # [rad], +/-
NOMINAL_LATERAL_VELOCITY_SIGMA = 0.05  # [m/s]


@dataclass(frozen=True, slots=True)
class SensorFault:
    kind: str
    signal: str
    value: float = 0.0
    start_s: float = 0.0
    duration_s: float | None = None
    trigger: str | None = None  # sim.faults.trigger: start_s counts from this event

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
    """The always-on errors of 4.5, with the per-run scale and offset drawn from rng."""
    return (SensorFault("noise", "speed", NOMINAL_SPEED_SIGMA),
            SensorFault("scale", "speed", float(rng.uniform(-NOMINAL_SPEED_SCALE, NOMINAL_SPEED_SCALE))),
            SensorFault("noise", "steering_angle", NOMINAL_STEERING_SIGMA),
            SensorFault("bias", "steering_angle", float(rng.uniform(-NOMINAL_STEERING_OFFSET, NOMINAL_STEERING_OFFSET))),
            SensorFault("noise", "lateral_velocity", NOMINAL_LATERAL_VELOCITY_SIGMA))


class SensorErrors:
    """Applies the faults of one run to sampled signals; one rng per sensor stream."""

    def __init__(self, faults: tuple[SensorFault, ...], rngs: dict[str, np.random.Generator]) -> None:
        self.faults = faults
        self._rngs = rngs  # signal -> generator

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

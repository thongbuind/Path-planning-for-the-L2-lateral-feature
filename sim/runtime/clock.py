"""ECU clocks (Software Qualification Test Specification 4.2, "Đồng hồ ECU"; 6: F14).

local(t) = t + offset(t). A gPTP-like synchronisation every SYNC_PERIOD_US sets the offset
to a residual error uniform in +/- SYNC_RESIDUAL_US; between two of them the offset grows
with the drift. Before the first one the offset is the start offset. Inside a window of lost
synchronisation (F14 c) no reset happens, so the drift accumulates.

local() is a pure function of the global time (the residual of synchronisation k is drawn
from a generator seeded with k), so any time can be converted in any order.

The simulator keeps one global time. Only what the planner sees is converted: the camera
ECU stamps lane model and ObjectList; the ADAS ECU gives t0, rx_us, the other stamps and
the EgoMotionQuery times. Stand-ins of the test bench keep the global time. Ideal clocks are
the default until the nominal realism batch switches them on.
"""

from dataclasses import dataclass

import numpy as np

SYNC_PERIOD_US = 125_000  # gPTP-like (4.2)
SYNC_RESIDUAL_US = 50.0  # +/- after a synchronisation (4.2)
DRIFT_PPM_MAX = 100.0  # +/- (4.2)
START_OFFSET_US_MAX = 10_000.0  # +/- before the first synchronisation (4.2; PP-ASM-012)
ECUS = ("camera", "adas")


@dataclass(frozen=True, slots=True)
class ClockFault:
    """F14: drift of one ECU in ppm (`drift`), or a window without synchronisation (`sync_loss`)."""
    kind: str
    ecu: str
    value: float = 0.0
    start_s: float = 0.0
    duration_s: float | None = None

    def __post_init__(self) -> None:
        if self.kind not in ("drift", "sync_loss") or self.ecu not in ECUS:
            raise ValueError(f"invalid clock fault {self.kind!r} on {self.ecu!r}")
        if self.start_s < 0 or (self.duration_s is not None and self.duration_s <= 0):
            raise ValueError("clock fault needs start >= 0 and duration > 0")


class EcuClock:
    def __init__(self, drift_ppm: float = 0.0, start_offset_us: float = 0.0, residual_us: float = 0.0,
                 seed: int = 0, sync_phase_us: int = 0,
                 sync_loss: tuple[tuple[int, int | None], ...] = ()) -> None:
        self.drift = drift_ppm * 1e-6
        self.start_offset_us = float(start_offset_us)
        self.residual_us = float(residual_us)
        self.seed = seed
        self.phase = int(sync_phase_us) % SYNC_PERIOD_US
        self.loss = sync_loss
        self.ideal = drift_ppm == 0 and start_offset_us == 0 and residual_us == 0

    def _synced(self, t_us: int) -> bool:
        return not any(a <= t_us and (b is None or t_us < b) for a, b in self.loss)

    def _residual(self, k: int) -> float:
        if self.residual_us == 0:
            return 0.0
        return self.residual_us * float(np.random.default_rng([self.seed, k]).uniform(-1.0, 1.0))

    def local(self, t_us: int) -> int:
        if self.ideal:
            return int(t_us)
        k = (int(t_us) - self.phase) // SYNC_PERIOD_US  # last synchronisation slot at or before t
        while k >= 0 and not self._synced(self.phase + k * SYNC_PERIOD_US):
            k -= 1
        if k < 0:
            offset = self.start_offset_us + self.drift * t_us
        else:
            s = self.phase + k * SYNC_PERIOD_US
            offset = self._residual(k) + self.drift * (t_us - s)
        return int(round(t_us + offset))

    def to_global(self, local_us: int) -> int:
        """Global time whose local time is local_us (offsets are small: two fixed-point steps)."""
        t = int(local_us)
        for _ in range(2):
            t = int(local_us) - (self.local(t) - t)
        return t


def clocks(seed: int, realism: bool, faults: tuple[ClockFault, ...]) -> dict[str, EcuClock]:
    """Clock of each ECU for one run: ideal, or with drift, start offset and residual drawn
    from the seed (realism), then F14 faults (drift value, windows without synchronisation)."""
    rng = np.random.default_rng([seed, 4242])
    out = {}
    for i, ecu in enumerate(ECUS):
        drift = float(rng.uniform(-DRIFT_PPM_MAX, DRIFT_PPM_MAX)) if realism else 0.0
        start = float(rng.uniform(-START_OFFSET_US_MAX, START_OFFSET_US_MAX)) if realism else 0.0
        phase = int(rng.integers(0, SYNC_PERIOD_US))
        residual = SYNC_RESIDUAL_US if realism else 0.0
        loss = []
        for f in faults:
            if f.ecu != ecu:
                continue
            if f.kind == "drift":
                drift = f.value
                residual = residual or SYNC_RESIDUAL_US
            else:
                end = None if f.duration_s is None else round((f.start_s + f.duration_s) * 1e6)
                loss.append((round(f.start_s * 1e6), end))
                residual = residual or SYNC_RESIDUAL_US
        out[ecu] = EcuClock(drift, start, residual, seed=seed * 10 + i, sync_phase_us=phase, sync_loss=tuple(loss))
    return out

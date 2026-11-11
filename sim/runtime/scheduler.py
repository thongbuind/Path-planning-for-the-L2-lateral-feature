"""Deterministic single-process scheduler (Software Qualification Test Specification 4.1, 4.2).

One step is 1 ms. Order within a step, as in 4.2:

1. integrate the vehicle model (physics),
2. sensors sample,
3. deliver messages that are due,
4. run the blocks whose turn it is, by fixed priority.

One common ideal clock for every ECU in this version; per-ECU drift and gPTP sync
come later.
"""

from collections.abc import Callable
from dataclasses import dataclass, field

STEP_US = 1_000

PHYSICS = 0
SENSOR = 1
BLOCK = 2


@dataclass(order=True)
class _Task:
    priority: int
    name: str = field(compare=False)
    period_us: int = field(compare=False)
    phase_us: int = field(compare=False)
    run: Callable[[int], None] = field(compare=False)

    def due(self, now_us: int) -> bool:
        return now_us >= self.phase_us and (now_us - self.phase_us) % self.period_us == 0


class Scheduler:
    def __init__(self, step_us: int = STEP_US) -> None:
        self.step_us = step_us
        self.now_us = 0
        self._physics: list[Callable[[int, float], None]] = []
        self._sensors: list[_Task] = []
        self._blocks: list[_Task] = []
        self._channels: list = []

    def add_physics(self, run: Callable[[int, float], None]) -> None:
        """Called every step with (now_us, dt_s), in the order added."""
        self._physics.append(run)

    def add_sensor(self, name: str, period_us: int, run: Callable[[int], None],
                   phase_us: int = 0) -> None:
        self._sensors.append(_Task(len(self._sensors), name, period_us, phase_us, run))

    def add_block(self, name: str, period_us: int, run: Callable[[int], None],
                  priority: int, phase_us: int = 0) -> None:
        if period_us % self.step_us or phase_us % self.step_us:
            raise ValueError(f"{name}: period and phase must be whole steps")
        self._blocks.append(_Task(priority, name, period_us, phase_us, run))
        self._blocks.sort()

    def add_channel(self, channel) -> None:
        self._channels.append(channel)

    def step(self) -> None:
        self.now_us += self.step_us
        now, dt = self.now_us, self.step_us * 1e-6
        for run in self._physics:
            run(now, dt)
        for task in self._sensors:
            if task.due(now):
                task.run(now)
        for channel in self._channels:
            channel.deliver(now)
        for task in self._blocks:
            if task.due(now):
                task.run(now)

    def run_until(self, end_us: int) -> None:
        while self.now_us < end_us:
            self.step()

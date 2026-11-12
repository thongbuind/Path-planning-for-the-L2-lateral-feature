"""Pub/sub channel with delivery delay (Software Qualification Test Specification 4.2).

The receiver keeps the newest delivered message and its delivery time rx_us
(Interface Control Document 4). A channel may add a uniform jitter of +/- jitter_us to its
delay (6.1, Q1); delivery stays in time order, so a late message can arrive after a newer one.
"""

from bisect import insort
from collections import deque
from collections.abc import Callable

import numpy as np
from typing import Generic, TypeVar

from interfaces import Received

T = TypeVar("T")

# In-memory pub/sub inside the ADAS ECU: 1 ms (PP-ASM-007).
PUBSUB_LATENCY_US = 1_000


class Channel(Generic[T]):
    def __init__(self, name: str, latency_us: int = PUBSUB_LATENCY_US,
                 on_deliver: Callable[[T, int], T] | None = None, *, jitter_us: int = 0,
                 rng: np.random.Generator | None = None) -> None:
        """`on_deliver(message, rx_us)` may rewrite the message at delivery, for
        example to stamp a CAN frame with its receive time (Interface Control Document 4)."""
        self.name = name
        if latency_us < 0 or jitter_us < 0 or (jitter_us > 0 and rng is None):
            raise ValueError("channel delay needs latency, jitter >= 0 and an rng for jitter")
        self.latency_us = latency_us
        self.jitter_us = jitter_us
        self._rng = rng
        self._seq = 0
        self._on_deliver = on_deliver
        self._queue: deque[tuple[int, T]] = deque()
        self.latest: Received[T] | None = None
        self.subscribers: list[Callable[[T, int], None]] = []

    def publish(self, message: T, now_us: int) -> None:
        delay = self.latency_us
        if self.jitter_us > 0:
            delay = max(0, delay + int(self._rng.integers(-self.jitter_us, self.jitter_us + 1)))
        self._seq += 1
        if self.jitter_us > 0:
            insort(self._queue, (now_us + delay, self._seq, message), key=lambda e: (e[0], e[1]))
        else:
            self._queue.append((now_us + delay, self._seq, message))

    def deliver(self, now_us: int) -> None:
        while self._queue and self._queue[0][0] <= now_us:
            _, _, message = self._queue.popleft()
            if self._on_deliver is not None:
                message = self._on_deliver(message, now_us)
            self.latest = Received(message, now_us)
            for subscriber in self.subscribers:
                subscriber(message, now_us)

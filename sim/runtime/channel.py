"""Kênh giữ message đã giao mới nhất và rx_us. Độ trễ giao có thể kèm jitter (SQTS 4.2)."""

from bisect import insort
from collections import deque
from collections.abc import Callable

import numpy as np
from typing import Generic, TypeVar

from interfaces import Received

T = TypeVar("T")

PUBSUB_LATENCY_US = 1_000


class Channel(Generic[T]):
    def __init__(self, name: str, latency_us: int = PUBSUB_LATENCY_US,
                 on_deliver: Callable[[T, int], T] | None = None, *, jitter_us: int = 0,
                 rng: np.random.Generator | None = None, faults=None) -> None:
        """on_deliver có thể sửa payload lúc giao, ví dụ gắn stamp lúc nhận frame CAN."""
        self.name = name
        if latency_us < 0 or jitter_us < 0 or (jitter_us > 0 and rng is None):
            raise ValueError("channel delay needs latency, jitter >= 0 and an rng for jitter")
        self.latency_us = latency_us
        self.jitter_us = jitter_us
        self._rng = rng
        self._seq = 0
        self.published = 0
        self._on_deliver = on_deliver
        self.faults = faults
        self._queue: deque[tuple[int, T]] = deque()
        self.latest: Received[T] | None = None
        self.subscribers: list[Callable[[T, int], None]] = []

    def publish(self, message: T, now_us: int) -> None:
        delay = self.latency_us
        if self.jitter_us > 0:
            delay = max(0, delay + int(self._rng.integers(-self.jitter_us, self.jitter_us + 1)))
        index = self.published
        self.published += 1
        if self.faults is None:
            deliveries = [(0, message)]
        else:
            deliveries = self.faults.deliveries(message, now_us, index)
        for extra_us, item in deliveries:
            entry = (now_us + max(0, delay + extra_us), self._seq, item)
            self._seq += 1
            if self.jitter_us > 0 or self.faults is not None:
                insort(self._queue, entry, key=lambda e: (e[0], e[1]))
            else:
                self._queue.append(entry)

    def deliver(self, now_us: int) -> None:
        while self._queue and self._queue[0][0] <= now_us:
            _, _, message = self._queue.popleft()
            if self._on_deliver is not None:
                message = self._on_deliver(message, now_us)
                if message is None:
                    continue
            self.latest = Received(message, now_us)
            for subscriber in self.subscribers:
                subscriber(message, now_us)

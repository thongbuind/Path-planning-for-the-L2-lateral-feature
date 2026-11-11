"""Pub/sub channel with delivery delay (Software Qualification Test Specification 4.2).

The receiver keeps the newest delivered message and its delivery time rx_us
(Interface Control Document 4). Jitter, drops and fault injection come later.
"""

from collections import deque
from collections.abc import Callable
from typing import Generic, TypeVar

from interfaces import Received

T = TypeVar("T")

# In-memory pub/sub inside the ADAS ECU: 1 ms (PP-ASM-007).
PUBSUB_LATENCY_US = 1_000


class Channel(Generic[T]):
    def __init__(self, name: str, latency_us: int = PUBSUB_LATENCY_US,
                 on_deliver: Callable[[T, int], T] | None = None) -> None:
        """`on_deliver(message, rx_us)` may rewrite the message at delivery, for
        example to stamp a CAN frame with its receive time (Interface Control Document 4)."""
        self.name = name
        self.latency_us = latency_us
        self._on_deliver = on_deliver
        self._queue: deque[tuple[int, T]] = deque()
        self.latest: Received[T] | None = None
        self.subscribers: list[Callable[[T, int], None]] = []

    def publish(self, message: T, now_us: int) -> None:
        self._queue.append((now_us + self.latency_us, message))

    def deliver(self, now_us: int) -> None:
        while self._queue and self._queue[0][0] <= now_us:
            _, message = self._queue.popleft()
            if self._on_deliver is not None:
                message = self._on_deliver(message, now_us)
            self.latest = Received(message, now_us)
            for subscriber in self.subscribers:
                subscriber(message, now_us)

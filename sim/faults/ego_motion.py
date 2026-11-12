"""Ego-motion not valid (Software Qualification Test Specification 6, F20; PP-SWR-143).

Acts on the planner's EgoMotionQuery only: every answer of a planner cycle that is hit has
valid = false. The Lateral Controller and the ADAS function stand-in keep their own queries.

| kind | Cycles hit |
|---|---|
| once | the first planner cycle at or after start_s |
| continuous | every cycle in [start_s, start_s + duration_s) |
| alternate | every other cycle in that window |
"""

from dataclasses import dataclass

KINDS = ("once", "continuous", "alternate")


@dataclass(frozen=True, slots=True)
class EgoMotionFault:
    kind: str
    start_s: float = 0.0
    duration_s: float | None = None

    def __post_init__(self) -> None:
        if self.kind not in KINDS or self.start_s < 0 or (self.duration_s is not None and self.duration_s <= 0):
            raise ValueError(f"invalid ego-motion fault {self.kind!r}")


class EgoMotionFaults:
    def __init__(self, faults: tuple[EgoMotionFault, ...]) -> None:
        self.faults = faults
        self._seen = [0] * len(faults)

    def invalid(self, t0_us: int) -> bool:
        """Whether the planner cycle at t0_us gets invalid answers; call once per cycle."""
        hit = False
        for i, f in enumerate(self.faults):
            start = round(f.start_s * 1e6)
            inside = t0_us >= start and (f.duration_s is None or t0_us < start + round(f.duration_s * 1e6))
            if f.kind == "once":
                inside = t0_us >= start
            if not inside:
                continue
            k = self._seen[i]
            self._seen[i] += 1
            hit |= (f.kind == "once" and k == 0) or f.kind == "continuous" or (f.kind == "alternate" and k % 2 == 0)
        return hit

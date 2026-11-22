"""F20 chỉ làm mất hiệu lực trả lời EgoMotionQuery của planner. Controller và stand-in ADAS vẫn
dùng dịch vụ gốc.
"""

from dataclasses import dataclass

from sim.faults import trigger

KINDS = ("once", "continuous", "alternate")


@dataclass(frozen=True, slots=True)
class EgoMotionFault:
    kind: str
    start_s: float = 0.0
    duration_s: float | None = None
    trigger: str | None = None

    def __post_init__(self) -> None:
        trigger.check(self.trigger)
        if self.kind not in KINDS or self.start_s < 0 or (self.duration_s is not None and self.duration_s <= 0):
            raise ValueError(f"invalid ego-motion fault {self.kind!r}")


class EgoMotionFaults:
    def __init__(self, faults: tuple[EgoMotionFault, ...]) -> None:
        self.faults = faults
        self._seen = [0] * len(faults)

    def invalid(self, t0_us: int) -> bool:
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

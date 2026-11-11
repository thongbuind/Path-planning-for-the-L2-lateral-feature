"""Other vehicles of a scenario (Software Qualification Test Specification 4.5, 5).

Each one drives along the road at a constant lateral offset from the ego-lane centre and
a constant speed. Good enough for overtaking a truck (S3, S3b, S15) and for the lane
cross-check of T2 (J2); manoeuvring traffic is a later step.
"""

from dataclasses import dataclass

from sim.world.road import Road


@dataclass(frozen=True, slots=True)
class TrafficSpec:
    """Initial state in road coordinates of the ego-lane centre."""

    id: int
    s0: float  # [m] arc length of the vehicle centre at t = 0
    d: float  # [m] lateral offset of the centre, left positive
    speed: float  # [m/s] along the road
    length: float = 4.8  # [m]
    width: float = 1.9  # [m] including mirrors


@dataclass(frozen=True, slots=True)
class TrafficState:
    id: int
    x: float  # World centre
    y: float
    heading: float  # Of the velocity vector, world
    speed: float
    s: float
    d: float
    length: float
    width: float


class Traffic:
    def __init__(self, road: Road, specs: tuple[TrafficSpec, ...]) -> None:
        self.road = road
        self.specs = specs

    def at(self, t_s: float) -> list[TrafficState]:
        out = []
        for spec in self.specs:
            s = spec.s0 + spec.speed * t_s
            x, y, heading = self.road.pose_at(s, spec.d)
            out.append(TrafficState(spec.id, x, y, heading, spec.speed, s, spec.d, spec.length, spec.width))
        return out

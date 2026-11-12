"""Other vehicles of a scenario (Software Qualification Test Specification 4.5, 5).

Longitudinal speed is constant, in either direction along the road. An optional
lateral manoeuvre joins two offsets with zero lateral speed at both ends.
"""

from dataclasses import dataclass
from math import atan2, hypot, isfinite, pi

from sim.world.road import Road


@dataclass(frozen=True, slots=True)
class LateralMotion:
    start_s: float  # [s] simulation time
    duration_s: float
    target_offset_m: float  # [m] left positive in road coordinates

    def __post_init__(self) -> None:
        if (not all(map(isfinite, (self.start_s, self.duration_s, self.target_offset_m)))
                or self.start_s < 0 or self.duration_s <= 0):
            raise ValueError("invalid traffic lateral motion")

    def at(self, t_s: float, initial_offset_m: float) -> tuple[float, float]:
        """Offset and lateral speed along a quintic with smooth endpoints."""
        u = (t_s - self.start_s) / self.duration_s
        if u <= 0:
            return initial_offset_m, 0.0
        if u >= 1:
            return self.target_offset_m, 0.0
        delta = self.target_offset_m - initial_offset_m
        blend = u**3 * (10 - 15 * u + 6 * u**2)
        rate = 30 * u**2 * (1 - u)**2 / self.duration_s
        return initial_offset_m + delta * blend, delta * rate


@dataclass(frozen=True, slots=True)
class TrafficSpec:
    """Initial state in road coordinates of the ego-lane centre."""

    id: int
    s0: float  # [m] arc length of the vehicle centre at t = 0
    d: float  # [m] lateral offset of the centre, left positive
    speed: float  # [m/s] along the road
    length: float = 4.8  # [m]
    width: float = 1.9  # [m] including mirrors
    direction: int = 1  # +1 along road s, -1 against it
    lateral_motion: LateralMotion | None = None

    def __post_init__(self) -> None:
        if (not all(map(isfinite, (self.s0, self.d, self.speed, self.length, self.width)))
                or self.speed < 0 or self.length <= 0 or self.width <= 0
                or self.direction not in (-1, 1)):
            raise ValueError("invalid traffic state or direction")


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
            longitudinal = spec.direction * spec.speed
            s = spec.s0 + longitudinal * t_s
            d, lateral = (spec.d, 0.0) if spec.lateral_motion is None else spec.lateral_motion.at(t_s, spec.d)
            x, y, heading = self.road.pose_at(s, d)
            if longitudinal or lateral:
                heading += atan2(lateral, longitudinal)
            elif spec.direction < 0:
                heading += pi
            speed = hypot(longitudinal, lateral)
            out.append(TrafficState(spec.id, x, y, heading, speed, s, d, spec.length, spec.width))
        return out

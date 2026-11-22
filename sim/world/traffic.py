from dataclasses import dataclass
from math import atan2, hypot, isfinite, pi

from sim.world.road import Road


@dataclass(frozen=True, slots=True)
class LateralMotion:
    start_s: float
    duration_s: float
    target_offset_m: float

    def __post_init__(self) -> None:
        if (not all(map(isfinite, (self.start_s, self.duration_s, self.target_offset_m)))
                or self.start_s < 0 or self.duration_s <= 0):
            raise ValueError("invalid traffic lateral motion")

    def at(self, t_s: float, initial_offset_m: float) -> tuple[float, float]:
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
    id: int
    s0: float
    d: float
    speed: float
    length: float = 4.8
    width: float = 1.9
    direction: int = 1  # +1 cùng chiều tăng s, -1 ngược chiều.
    lateral_motion: LateralMotion | None = None
    # Nội suy tuyến tính các mốc (t_s, speed_mps) và giữ mốc cuối. Danh sách rỗng dùng speed cố
    # định.
    speed_profile: tuple[tuple[float, float], ...] = ()
    kind: str = "CAR"

    def __post_init__(self) -> None:
        if (not all(map(isfinite, (self.s0, self.d, self.speed, self.length, self.width)))
                or self.speed < 0 or self.length <= 0 or self.width <= 0
                or self.direction not in (-1, 1)):
            raise ValueError("invalid traffic state or direction")
        times = [t for t, _ in self.speed_profile]
        if self.speed_profile and (
                times[0] != 0.0 or any(b <= a for a, b in zip(times, times[1:]))
                or not all(isfinite(t) and isfinite(v) and v >= 0 for t, v in self.speed_profile)
                or self.speed_profile[0][1] != self.speed):
            raise ValueError("speed profile needs t from 0 increasing, speed >= 0, first speed = speed")

    def travelled(self, t_s: float) -> tuple[float, float]:
        if not self.speed_profile:
            return self.speed * t_s, self.speed
        dist = 0.0
        points = self.speed_profile
        for (t0, v0), (t1, v1) in zip(points, points[1:]):
            if t_s <= t1:
                u = (t_s - t0) / (t1 - t0)
                v = v0 + (v1 - v0) * u
                return dist + 0.5 * (v0 + v) * (t_s - t0), v
            dist += 0.5 * (v0 + v1) * (t1 - t0)
        t_last, v_last = points[-1]
        return dist + v_last * (t_s - t_last), v_last


@dataclass(frozen=True, slots=True)
class TrafficState:
    id: int
    x: float
    y: float
    heading: float  # Góc của vector vận tốc trong tọa độ thế giới.
    speed: float
    s: float
    d: float
    length: float
    width: float
    kind: str = "CAR"


class Traffic:
    def __init__(self, road: Road, specs: tuple[TrafficSpec, ...]) -> None:
        self.road = road
        self.specs = specs

    def at(self, t_s: float) -> list[TrafficState]:
        out = []
        for spec in self.specs:
            travelled, speed_now = spec.travelled(t_s)
            longitudinal = spec.direction * speed_now
            s = spec.s0 + spec.direction * travelled
            d, lateral = (spec.d, 0.0) if spec.lateral_motion is None else spec.lateral_motion.at(t_s, spec.d)
            x, y, heading = self.road.pose_at(s, d)
            if longitudinal or lateral:
                heading += atan2(lateral, longitudinal)
            elif spec.direction < 0:
                heading += pi
            speed = hypot(longitudinal, lateral)
            out.append(TrafficState(spec.id, x, y, heading, speed, s, d, spec.length, spec.width, spec.kind))
        return out

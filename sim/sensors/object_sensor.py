"""ObjectList sensor: camera and radar fusion as seen by the planner (Interface Control
Document 5.2; Software Qualification Test Specification 4.5).

Vehicles of the scenario moved into base_link at the measurement time, with the noise of
section 4.5: x sigma 0.2 m + 1 % of range, y sigma 0.1 m + 0.5 %, vx 0.3 and vy 0.2 m/s,
size 0.1 m; 2 % of the object reports of a frame missed; ghosts at 0.05 per second that
live 0.2 s. Same period and latency as the lane camera (PP-ASM-002).

| Choice | Value | Source |
|---|---|---|
| Detection range | 150 m ahead, 80 m behind (corner radars) | nhóm tự thống nhất |
| existence_probability | 0.95 real, 0.6 ghost | nhóm tự thống nhất |
"""

from math import atan2, cos, hypot, sin

import numpy as np

from interfaces import MAX_OBJECTS, FrameId, Header, Object, ObjectList
from sim.world.traffic import TrafficState

PERIOD_US = 50_000
LATENCY_US = 100_000
RANGE_AHEAD_M = 150.0
RANGE_BEHIND_M = 80.0
SIGMA_X_M, SIGMA_X_REL = 0.2, 0.01
SIGMA_Y_M, SIGMA_Y_REL = 0.1, 0.005
SIGMA_VX, SIGMA_VY = 0.3, 0.2
SIGMA_SIZE_M = 0.1
MISS_RATE = 0.02
GHOST_RATE_PER_S = 0.05
GHOST_LIFE_S = 0.2
P_REAL, P_GHOST = 0.95, 0.6
GHOST_ID_BASE = 1_000_000
UNUSED = Object(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)  # Fills the fixed array


class ObjectSensor:
    def __init__(self, rng: np.random.Generator, noise_scale: float = 1.0, *, ideal: bool = False) -> None:
        self.rng = rng
        self.scale = noise_scale  # rain: 1.5 (section 4.5)
        self.ideal = ideal  # SQTS 4.1 mode B: retain visibility, omit measurement errors
        self.counter = 0
        self.ghosts: list[tuple[int, float, float, float]] = []  # id, x, y, end time
        self.next_ghost = GHOST_ID_BASE

    def capture(self, now_us: int, ego: tuple[float, float, float], ego_speed: float,
                vehicles: list[TrafficState]) -> ObjectList:
        ex, ey, eyaw = ego
        c, s = cos(eyaw), sin(eyaw)
        rng, k = self.rng, self.scale
        objects = []
        for v in vehicles:
            dx, dy = v.x - ex, v.y - ey
            x, y = c * dx + s * dy, -s * dx + c * dy
            vx_w, vy_w = v.speed * cos(v.heading), v.speed * sin(v.heading)
            vx, vy = c * vx_w + s * vy_w, -s * vx_w + c * vy_w
            in_range = -RANGE_BEHIND_M <= x <= RANGE_AHEAD_M
            if self.ideal:
                if in_range:
                    objects.append(Object(v.id, x, y, vx, vy, atan2(vy, vx), v.length, v.width, 1.0))
                continue
            draws = rng.standard_normal(6)
            missed = rng.random() < MISS_RATE
            if missed or not in_range:
                continue
            rng_m = hypot(x, y)
            objects.append(Object(
                id=v.id,
                x=x + k * (SIGMA_X_M + SIGMA_X_REL * rng_m) * float(draws[0]),
                y=y + k * (SIGMA_Y_M + SIGMA_Y_REL * rng_m) * float(draws[1]),
                vx=vx + k * SIGMA_VX * float(draws[2]),
                vy=vy + k * SIGMA_VY * float(draws[3]),
                heading=atan2(vy, vx),
                length=max(0.5, v.length + k * SIGMA_SIZE_M * float(draws[4])),
                width=max(0.5, v.width + k * SIGMA_SIZE_M * float(draws[5])),
                existence_probability=P_REAL))
        t_s = now_us * 1e-6
        if not self.ideal and rng.random() < GHOST_RATE_PER_S * PERIOD_US * 1e-6:
            self.ghosts.append((self.next_ghost, float(rng.uniform(5.0, 80.0)),
                                float(rng.uniform(-6.0, 6.0)), t_s + GHOST_LIFE_S))
            self.next_ghost += 1
        self.ghosts = [g for g in self.ghosts if g[3] > t_s]
        for gid, gx, gy, _ in self.ghosts:
            objects.append(Object(id=gid, x=gx, y=gy, vx=ego_speed, vy=0.0, heading=0.0,
                                  length=4.5, width=1.8, existence_probability=P_GHOST))
        objects = objects[:MAX_OBJECTS]
        used = len(objects)
        objects += [UNUSED] * (MAX_OBJECTS - used)
        self.counter = (self.counter + 1) % 256
        return ObjectList(Header(now_us, self.counter, True, FrameId.BASE_LINK), used, tuple(objects))

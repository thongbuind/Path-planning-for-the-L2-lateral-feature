"""LeadTarget mô phỏng đầu ra perception của đúng xe ACC đang bám (ICD 5.9)."""

from math import atan2, cos, hypot, sin

import numpy as np

from interfaces import FrameId, Header, LeadClass, LeadTarget
from sim.sensors.object_sensor import SIGMA_VX, SIGMA_VY, SIGMA_X_M, SIGMA_X_REL, SIGMA_Y_M, SIGMA_Y_REL
from sim.world.traffic import TrafficState

SIGMA_HEADING_RAD = 0.02
P_REAL = 0.95
_CLASSES = {"CAR": LeadClass.CAR, "TRUCK": LeadClass.TRUCK, "MOTORCYCLE": LeadClass.MOTORCYCLE,
            "OTHER": LeadClass.OTHER}


class LeadSensor:
    def __init__(self, rng: np.random.Generator, front_m: float, noise_scale: float = 1.0) -> None:
        self.rng = rng
        self.front = front_m
        self.scale = noise_scale
        self.counter = 0

    def capture(self, now_us: int, ego: tuple[float, float, float], ego_velocity: tuple[float, float],
                vehicles: list[TrafficState], target_id: int | None) -> LeadTarget:
        self.counter = (self.counter + 1) % 256
        draws = self.rng.standard_normal(5)       # Lấy mẫu kể cả lúc thiếu target để giữ chuỗi nhiễu tái lặp.
        target = next((v for v in vehicles if target_id is not None and v.id == target_id), None)
        header = Header(now_us, self.counter, target is not None, FrameId.BASE_LINK)
        if target is None:
            return LeadTarget(header, 0, LeadClass.UNKNOWN, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        ex, ey, eyaw = ego
        c, s = cos(eyaw), sin(eyaw)
        dx, dy = target.x - ex, target.y - ey
        x, y = c * dx + s * dy, -s * dx + c * dy
        vx_w, vy_w = target.speed * cos(target.heading), target.speed * sin(target.heading)
        vx, vy = c * vx_w + s * vy_w, -s * vx_w + c * vy_w
        k, rng_m = self.scale, hypot(x, y)
        x_m = x + k * (SIGMA_X_M + SIGMA_X_REL * rng_m) * float(draws[0])
        gap = x_m - target.length / 2 - self.front
        return LeadTarget(
            header, target.id, _CLASSES.get(target.kind, LeadClass.OTHER), x_m,
            y + k * (SIGMA_Y_M + SIGMA_Y_REL * rng_m) * float(draws[1]), gap,
            atan2(vy, vx) + k * SIGMA_HEADING_RAD * float(draws[2]),
            vx - ego_velocity[0] + k * SIGMA_VX * float(draws[3]),
            vy - ego_velocity[1] + k * SIGMA_VY * float(draws[4]), P_REAL)

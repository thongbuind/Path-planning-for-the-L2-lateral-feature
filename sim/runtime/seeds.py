"""Mỗi luồng có seed riêng. Giữ thứ tự tên cũ để thêm luồng không làm đổi chuỗi đã có."""

import numpy as np

STREAMS = ("phases", "lane_camera", "chassis", "state_estimator", "perception", "latency", "faults")


def spawn_streams(seed: int) -> dict[str, np.random.Generator]:
    children = np.random.SeedSequence(seed).spawn(len(STREAMS))
    return {name: np.random.default_rng(child) for name, child in zip(STREAMS, children)}


def random_phase_us(rng: np.random.Generator, period_us: int, step_us: int) -> int:
    return int(rng.integers(0, period_us // step_us)) * step_us

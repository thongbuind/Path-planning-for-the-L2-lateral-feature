"""Seeds (Software Qualification Test Specification 4.1, 4.2).

One main seed per run, split with numpy.random.SeedSequence.spawn into one stream per
named channel. The order of names is fixed, so a name keeps its stream when new
names are appended.
"""

import numpy as np

STREAMS = ("phases", "lane_camera", "chassis", "state_estimator", "perception", "latency", "faults")


def spawn_streams(seed: int) -> dict[str, np.random.Generator]:
    children = np.random.SeedSequence(seed).spawn(len(STREAMS))
    return {name: np.random.default_rng(child) for name, child in zip(STREAMS, children)}


def random_phase_us(rng: np.random.Generator, period_us: int, step_us: int) -> int:
    """Start phase of a block, a whole number of steps in [0, period) (4.2, "Độ lệch pha")."""
    return int(rng.integers(0, period_us // step_us)) * step_us

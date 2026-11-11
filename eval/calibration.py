"""Calibration values that requirements point to (Software Requirements Specification 7).

Read from the delivered calibration data set of the build under test, as a test bench
reads the A2L of an ECU build. Only parameters named in a requirement are read; no
planner code is imported.
"""

from math import pi
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CALIBRATION_FILE = ROOT / "planner" / "calibration" / "calibration.yaml"
REQUIREMENT_PARAMETERS = ("epsilon_ay", "free_space_min", "gap_truck_min")  # PP-SWR-006 (SRS 1.3); 051, 063 (SRS 1.4); 055, 056 (SRS 1.5)
_UNITS = {"deg": pi / 180.0, "ms": 1e-3}


def requirement_parameters(path: Path = CALIBRATION_FILE) -> dict[str, float]:
    return from_parameters(yaml.safe_load(path.read_text(encoding="utf-8"))["parameters"])


def from_parameters(params: dict) -> dict[str, float]:
    """The requirement-referenced values, SI units, from a parsed calibration data set."""
    return {name: float(params[name]["value"]) * _UNITS.get(params[name].get("unit", ""), 1.0)
            for name in REQUIREMENT_PARAMETERS}

"""Đọc các tham số calibration mà requirement tham chiếu, từ bộ dữ liệu của bản build đang chấm
(SRS 7).
"""

from math import pi
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CALIBRATION_FILE = ROOT / "planner" / "calibration" / "calibration.yaml"
REQUIREMENT_PARAMETERS = (
    "epsilon_ay", "free_space_min", "gap_truck_min",
    "T_end_hold", "v_lat_end", "d_end", "heading_end", "ay_add_end",
    "T_coast", "conf_ego", "conf_inferred",
    "conf_edge",
    "offset_truck", "ttc_offset_start", "t_offset_hold",
    "follow_lat_max", "follow_vlat_max", "d_end", "dlc_offset_min",
)
_UNITS = {"deg": pi / 180.0, "ms": 1e-3}


def requirement_parameters(path: Path = CALIBRATION_FILE) -> dict[str, float]:
    return from_parameters(yaml.safe_load(path.read_text(encoding="utf-8"))["parameters"])


def from_parameters(params: dict) -> dict[str, float]:
    return {name: float(params[name]["value"]) * _UNITS.get(params[name].get("unit", ""), 1.0)
            for name in REQUIREMENT_PARAMETERS if name in params or name != "conf_edge"}

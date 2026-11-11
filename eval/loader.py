"""Reads benchmark/scenarios/<id>.yaml into sim.scenario.Scenario."""

from math import radians
from pathlib import Path

import yaml

from dataclasses import replace

from sim.faults.lane import LaneFault
from sim.scenario import Scenario
from sim.world.road import Segment

ROOT = Path(__file__).resolve().parents[1]
SCENARIO_DIR = ROOT / "benchmark" / "scenarios"
FAULT_DIR = ROOT / "benchmark" / "faults"


def _segment(spec: dict) -> Segment:
    if "straight" in spec:
        return Segment("straight", float(spec["straight"]))
    if "clothoid" in spec:
        return Segment("clothoid", float(spec["clothoid"]), _curvature(spec))
    if "arc" in spec:
        return Segment("arc", float(spec["arc"]), _curvature(spec))
    raise ValueError(f"unknown road segment {spec!r}")


def _curvature(spec: dict) -> float:
    """radius_end / radius in metres; negative turns right; absent means straight."""
    radius = spec.get("radius_end", spec.get("radius"))
    return 0.0 if radius is None else 1.0 / float(radius)


def load(scenario_id: str, variant: str, directory: Path = SCENARIO_DIR) -> Scenario:
    data = yaml.safe_load((directory / f"{scenario_id}.yaml").read_text(encoding="utf-8"))
    if variant not in data["variants"]:
        raise KeyError(f"{scenario_id} has no variant {variant!r}")
    spec = {**data.get("defaults", {}), **data["variants"][variant]}
    return Scenario(
        name=f"{scenario_id}{variant}",
        segments=tuple(_segment(s) for s in spec["road"]),
        lane_width=float(spec["lane_width_m"]),
        speed_mps=float(spec["speed_kmh"]) / 3.6,
        profile=str(spec.get("profile", "VP-0")),
        duration_s=float(spec["duration_s"]),
        hwa_request_s=float(spec.get("hwa_request_s", 1.0)),
        start_s=float(spec.get("start_s_m", 10.0)),
        start_offset_m=float(spec.get("start_offset_m", 0.0)),
        start_heading_rad=radians(float(spec.get("start_heading_deg", 0.0))),
        hold_until_hwa=bool(spec.get("hold_until_hwa", False)),
        acc=str(spec.get("acc", "off")),
        notes={"description": spec.get("description", "")},
    )


def load_fault(fault_id: str, level: str, directory: Path = FAULT_DIR) -> LaneFault:
    data = yaml.safe_load((directory / f"{fault_id}.yaml").read_text(encoding="utf-8"))
    if level not in data["levels"]:
        raise KeyError(f"{fault_id} has no level {level!r}")
    spec = dict(data["levels"][level])
    if "lines" in spec:
        spec["lines"] = tuple(int(i) for i in spec["lines"])
    return LaneFault(**spec)


def with_fault(scenario: Scenario, fault_id: str, level: str) -> Scenario:
    """The scenario with one lane-model fault added (Software Qualification Test Specification 6.2)."""
    fault = load_fault(fault_id, level)
    return replace(scenario, name=f"{scenario.name}_{fault_id}{level}",
                   lane_faults=scenario.lane_faults + (fault,))

"""Read ASAM benchmark files into simulator values; sim never reads benchmark data."""
from dataclasses import replace
from pathlib import Path

from eval import openx
from sim.faults.lane import LaneFault
from sim.scenario import Scenario

ROOT = Path(__file__).resolve().parents[1]
SCENARIO_DIR = ROOT / 'benchmark' / 'scenarios'
FAULT_DIR = ROOT / 'benchmark' / 'faults'


def load(scenario_id: str, variant: str, directory: Path = SCENARIO_DIR) -> Scenario:
    path = directory / f'{scenario_id}.xosc'
    variants = openx.anchors(path)
    if variant not in variants:
        raise KeyError(f'{scenario_id} has no variant {variant!r}')
    return openx.load_scenario(path, variants[variant])


def load_file(path: Path) -> Scenario:
    return openx.load_scenario(path)


def _fault_root(fault_id: str, level: str, directory: Path):
    path = directory / f'{fault_id}.xosc'
    levels = openx.anchors(path)
    if level not in levels:
        raise KeyError(f'{fault_id} has no level {level!r}')
    root, _ = openx.resolve(openx.parse(path), levels[level])
    return root


def load_fault(fault_id: str, level: str, directory: Path = FAULT_DIR) -> LaneFault:
    root = _fault_root(fault_id, level, directory)
    commands = root.findall('./Storyboard/Init/Actions/UserDefinedAction/CustomCommandAction')
    if len(commands) != 1:
        raise ValueError('a fault definition must contain exactly one command')
    return openx.fault_from_command(commands[0])


def with_fault(scenario: Scenario, fault_id: str, level: str) -> Scenario:
    """Host scenario plus the fault; a fault file may also turn on the HWA view gate (F22)."""
    fault = load_fault(fault_id, level)
    properties = {p.get('name'): p.get('value') for p in
                  _fault_root(fault_id, level, FAULT_DIR).findall('./Entities/ScenarioObject/Vehicle/Properties/Property')}
    gate = scenario.hwa_view_gate or properties.get('pp:hwa_view_gate') == 'true'
    return replace(scenario, name=f'{scenario.name}_{fault_id}{level}',
                   lane_faults=scenario.lane_faults + (fault,), hwa_view_gate=gate)

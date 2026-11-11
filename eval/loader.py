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


def load_fault(fault_id: str, level: str, directory: Path = FAULT_DIR) -> LaneFault:
    path = directory / f'{fault_id}.xosc'
    levels = openx.anchors(path)
    if level not in levels:
        raise KeyError(f'{fault_id} has no level {level!r}')
    root, _ = openx.resolve(openx.parse(path), levels[level])
    commands = root.findall('./Storyboard/Init/Actions/UserDefinedAction/CustomCommandAction')
    if len(commands) != 1:
        raise ValueError('a fault definition must contain exactly one command')
    return openx.fault_from_command(commands[0])


def with_fault(scenario: Scenario, fault_id: str, level: str) -> Scenario:
    fault = load_fault(fault_id, level)
    return replace(scenario, name=f'{scenario.name}_{fault_id}{level}',
                   lane_faults=scenario.lane_faults + (fault,))

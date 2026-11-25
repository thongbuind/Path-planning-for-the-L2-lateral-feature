from dataclasses import replace
from pathlib import Path

from eval import labels, openx
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
    commands = fault_commands(fault_id, level, directory)
    if len(commands) != 1 or commands[0][0] != 'lane_faults':
        raise ValueError('a lane fault definition must contain exactly one lane fault command')
    return commands[0][1]


def fault_commands(fault_id: str, level: str, directory: Path = FAULT_DIR) -> list[tuple[str, object]]:
    root = _fault_root(fault_id, level, directory)
    commands = root.findall('./Storyboard/Init/Actions/UserDefinedAction/CustomCommandAction')
    # F13 và F18 khai báo lỗi bằng cấu hình, không cần lệnh tiêm.
    return [openx.fault_of_command(c) for c in commands if openx.enabled(c)]


def with_fault(scenario: Scenario, fault_id: str, level: str, trigger: str | None = None,
               offset_s: float = 0.0) -> Scenario:
    """Thêm lỗi vào ca host. Với trigger, mốc offset tính từ sự kiện kích hoạt."""
    root = _fault_root(fault_id, level, FAULT_DIR)
    properties = {p.get('name'): p.get('value') for p in
                  root.findall('./Entities/ScenarioObject/Vehicle/Properties/Property')}
    gate = scenario.hwa_view_gate or properties.get('pp:hwa_view_gate') == 'true'
    notes = dict(scenario.notes)
    outcome = labels.stricter(notes.get('expected_outcome'), properties.get('pp:expected_outcome') or None)
    if outcome:
        notes['expected_outcome'] = outcome
    added: dict[str, tuple] = {}
    for field_name, fault in fault_commands(fault_id, level):
        if trigger is not None and field_name != 'clock_faults':
            fault = replace(fault, trigger=trigger, start_s=offset_s)
        added[field_name] = added.get(field_name, getattr(scenario, field_name)) + (fault,)
    moment = '' if trigger is None else f'@{trigger}+{offset_s:g}'
    notes['faults'] = [*scenario.notes.get('faults', []), f'{fault_id}{level}{moment}']
    return replace(scenario, name=f'{scenario.name}_{fault_id}{level}{moment}', hwa_view_gate=gate, notes=notes,
                   can_bus=scenario.can_bus or properties.get('pp:can_bus') == 'true',
                   loop='open' if properties.get('pp:loop') == 'open' else scenario.loop, **added)

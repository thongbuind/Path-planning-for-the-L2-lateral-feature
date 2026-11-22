"""Cặp ca giữ nguyên seed. Bản đối chứng bỏ lỗi lặp counter hoặc thay các lỗi nhảy/đứng counter
bằng mất đúng frame bị ảnh hưởng (PP-SWR-129, 130).
"""

from dataclasses import replace

from eval.metrics import Criterion
from sim.faults import channel as channel_faults
from sim.harness import Harness, RunLog
from sim.scenario import Scenario


def needs_twin(scenario: Scenario) -> bool:
    return any(channel_faults.has_twin(f, scenario.can_bus or scenario.realism) for f in scenario.channel_faults)


def twin_of(scenario: Scenario, log: RunLog) -> tuple[Scenario, set[str]]:
    can = scenario.can_bus or scenario.realism
    kept, requirements = [], set()
    for fault, hits in zip(scenario.channel_faults, log.fault_hits):
        if not channel_faults.has_twin(fault, can):
            kept.append(fault)
            continue
        requirements.add(channel_faults.requirement(fault, can))
        twin = channel_faults.equivalent(fault, hits, can)
        if twin is not None:
            kept.append(twin)
    return replace(scenario, channel_faults=tuple(kept), name=scenario.name + "_twin"), requirements


def _outputs(c):
    return c.trajectory, c.path_status, c.lateral_limits


def criteria(scenario: Scenario, log: RunLog, planner, seed: int) -> list[Criterion]:
    if not needs_twin(scenario):
        return []
    twin_scenario, requirements = twin_of(scenario, log)
    twin = Harness(twin_scenario, planner, seed).run()
    differ = [a.t0_us for a, b in zip(log.cycles, twin.cycles) if _outputs(a) != _outputs(b)]
    differ += [c.t0_us for c in log.cycles[len(twin.cycles):]]
    first = differ[0] * 1e-6 if differ else None
    return [Criterion(r, "Chu kỳ output khác ca tham chiếu cùng seed", float(len(differ)), "= 0",
                      not differ, first_fail_s=first) for r in sorted(requirements)]

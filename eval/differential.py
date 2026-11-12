"""PP-SWR-129, 130 by comparison with a reference twin of the same seed (Software
Qualification Test Specification 6: F15, F16, F17).

The faulty run and its twin differ only in the faults that have a reference: none
(counter repeated, PP-SWR-129) or the loss of exactly the messages they hit (counter jump or
stuck, valid = false, qualifier FAULT, wrong CRC; PP-SWR-130). The planner outputs must be
the same at every cycle. Both runs are deterministic, so equal means equal values.
"""

from dataclasses import replace

from eval.metrics import Criterion
from sim.faults import channel as channel_faults
from sim.harness import Harness, RunLog
from sim.scenario import Scenario


def needs_twin(scenario: Scenario) -> bool:
    return any(channel_faults.has_twin(f, scenario.can_bus or scenario.realism) for f in scenario.channel_faults)


def twin_of(scenario: Scenario, log: RunLog) -> tuple[Scenario, set[str]]:
    """Reference scenario and the requirements it judges."""
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
    """One criterion per requirement judged: cycles whose outputs differ from the twin."""
    if not needs_twin(scenario):
        return []
    twin_scenario, requirements = twin_of(scenario, log)
    twin = Harness(twin_scenario, planner, seed).run()
    differ = [a.t0_us for a, b in zip(log.cycles, twin.cycles) if _outputs(a) != _outputs(b)]
    differ += [c.t0_us for c in log.cycles[len(twin.cycles):]]
    first = differ[0] * 1e-6 if differ else None
    return [Criterion(r, "Chu kỳ output khác ca tham chiếu cùng seed", float(len(differ)), "= 0",
                      not differ, first_fail_s=first) for r in sorted(requirements)]

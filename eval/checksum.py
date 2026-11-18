"""Behaviour checksum of one run (VERSION): equal checksums mean the same behaviour, bit for bit.

Hashes the whole RunLog except what is not behaviour:
  PlannerCycle.compute_ns, compute_lcc_ns, compute_ka_ns   wall clock of the planner calls (varies with the machine load)
  RunLog.scenario, .road    inputs; their identity is the case_hash (eval.case)
Every other field is in, so a field added to RunLog changes the checksum; bump VERSION when
the list changes on purpose. Floats are hashed as IEEE-754 binary64 (execution.canonical).
Used by the golden set, the CLI/web equivalence check and reruns (SIM-REQ-040 to 043).
"""

import dataclasses

from execution.canonical import Digest

VERSION = "behavior_checksum/2"   # 2: two planners, more PlannerCycle fields (PP-ADR-016)
EXCLUDE = {"PlannerCycle": {"compute_ns", "compute_lcc_ns", "compute_ka_ns"},
           "RunLog": {"scenario", "road", "fault_frames", "planner_only"}}
# Ground truth per step, hashed in blocks for speed.
TRUTH_INTS = ("t_us",)
TRUTH_FLOATS = ("rear", "front", "a_y", "speed", "wheel_angle", "rear_v_y", "yaw_rate")
TRUTH_BOOLS = ("eps_controlling",)


def behavior_checksum(log) -> str:
    d = Digest(EXCLUDE)
    d.update(VERSION)
    for name in TRUTH_INTS:
        d.update(name)
        d.ints(getattr(log, name))
    for name in TRUTH_FLOATS:
        d.update(name)
        d.floats(getattr(log, name))
    for name in TRUTH_BOOLS:
        d.update(name)
        d.raw(b"B", bytes(1 if x else 0 for x in getattr(log, name)))
    done = set(TRUTH_INTS + TRUTH_FLOATS + TRUTH_BOOLS) | EXCLUDE["RunLog"]
    for field in dataclasses.fields(log):
        if field.name not in done:
            d.update(field.name)
            d.update(getattr(log, field.name))
    return d.hexdigest()

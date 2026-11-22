"""Digest hành vi bỏ thời gian tính, dữ liệu đầu vào và thông tin môi trường. Đầu vào có case_hash
riêng.
"""

import dataclasses

from execution.canonical import Digest

VERSION = "behavior_checksum/2"   # Bản 2 ghi đầu ra của cả hai planner (PP-ADR-016).
EXCLUDE = {"PlannerCycle": {"compute_ns", "compute_lcc_ns", "compute_ka_ns"},
           "RunLog": {"scenario", "road", "fault_frames", "planner_only"}}
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

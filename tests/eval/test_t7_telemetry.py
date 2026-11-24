"""Tóm tắt telemetry T7 (eval/telemetry.py) và giới hạn slot của lab (research/generators/bench/slots.py)."""

import ctypes
import math
import sys
from pathlib import Path

from eval import telemetry

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research" / "generators" / "bench"))
import slots  # noqa: E402


def test_struct_matches_c_layout():
    # uint32 × 3, đệm 4 byte, double × 3 (pp_t7_input.h).
    assert ctypes.sizeof(telemetry.TelemetryC) == 40
    assert telemetry.TelemetryC.residual.offset == 16


def test_summary_counts_only_generator_cycles():
    records = [(0, 0, 0, math.nan, math.nan, 0.0),  # Chu kỳ generator không chạy.
               (10, 0, 0, 1e-4, 0.0, 0.0),
               (30, 2, 0, 1e-3, 0.5, 0.02),
               (20, 0, 0, math.nan, math.nan, 0.0)]
    s = telemetry.summary(records)
    assert s["cycles"] == 3
    assert s["work"]["max"] == 30.0
    assert math.isclose(s["fallback_share"], 1 / 3)
    assert s["fallback_codes"] == {"2": 1}
    assert s["residual"]["max"] == 1e-3
    assert math.isclose(s["t10_changed_share"], 1 / 3)
    assert telemetry.summary([(0, 0, 0, 0.0, 0.0, 0.0)]) is None


def test_slots_hold_and_release(tmp_path, monkeypatch):
    monkeypatch.setattr(slots, "DIR", tmp_path)
    monkeypatch.setenv("PP_LAB_SLOTS", "2")
    with slots.hold(2, "test"):
        assert len(list(tmp_path.iterdir())) == 2
    with slots.hold(1):
        pass

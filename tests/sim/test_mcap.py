"""MCAP run log (Software Qualification Test Specification 4.1): valid file layout, and a
short closed-loop run written with every topic."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from sim.logging import mcap_writer
from sim.logging.mcap_writer import MAGIC, McapWriter

ROOT = Path(__file__).resolve().parents[2]


def test_layout_and_round_trip(tmp_path):
    path = tmp_path / "x.mcap"
    with McapWriter(path) as w:
        w.metadata("run", {"seed": 3})
        w.message("/a", 1_000, {"v": 1.5, "ok": True, "p": [{"x": 1}]})
        w.message("/b", 2_000, {"s": "x"})
        w.message("/a", 3_000, {"v": 2.0, "ok": False, "p": []})
    raw = path.read_bytes()
    assert raw[:8] == MAGIC and raw[-8:] == MAGIC
    data = mcap_writer.read(path)
    assert [(t, ns) for t, ns, _ in data["messages"]] == [("/a", 1_000), ("/b", 2_000), ("/a", 3_000)]
    assert data["metadata"]["run"] == {"seed": "3"}
    assert data["ops"][0] == mcap_writer.OP_HEADER and data["ops"][-1] == mcap_writer.OP_FOOTER
    # Footer points at the summary section, which starts with a Schema record.
    assert raw[data["summary_start"]] == mcap_writer.OP_SCHEMA
    assert data["message_count"] == 3  # Statistics record of the summary


@pytest.mark.skipif(shutil.which("cc") is None, reason="no C compiler")
def test_closed_loop_run_is_logged(tmp_path):
    from eval import metrics
    from sim.harness import Harness
    from sim.logging import run_log
    from sim.scenario import Scenario
    from sim.world.road import Segment
    sys.path.insert(0, str(ROOT))
    from adapters.sil.sil_planner import PlannerLibrary
    lib = tmp_path / "libstub.so"
    subprocess.run(["cc", "-std=c11", "-shared", "-fPIC", f"-I{ROOT / 'interfaces' / 'c'}",
                    str(ROOT / "tests" / "eval" / "stub" / "stub_planner.c"), "-o", str(lib), "-lm"], check=True)
    scenario = Scenario(name="short", segments=(Segment("straight", 200.0),), lane_width=3.5,
                        speed_mps=20.0, duration_s=1.5)
    log = Harness(scenario, PlannerLibrary(lib), seed=1).run()
    path = run_log.write(log, tmp_path / "run.mcap", {"rerun": "x"})
    data = mcap_writer.read(path)
    topics = {t for t, _, _ in data["messages"]}
    assert {"/planner/trajectory", "/planner/path_status", "/planner/lateral_limits",
            "/planner/cycle", "/truth/vehicle"} <= topics
    assert data["metadata"]["run"]["scenario"] == "short" and data["metadata"]["run"]["rerun"] == "x"
    truth = [m for t, _, m in data["messages"] if t == "/truth/vehicle"]
    assert len(truth) == pytest.approx(150, abs=2) and abs(truth[0]["lane_offset_m"]) < 0.5
    assert metrics.execution_fault(log.cycles) is None

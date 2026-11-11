"""First closed SIL loop: the delivered planner library drives the simulated car.

Shortened S1-like run (straight, clothoid, arc R = 500 m, 90 km/h, 10 s) to keep the
test quick; the full S1 a runs with `python3 -m eval.runner S1 a`. Needs
build/planner/libpp_planner; skipped otherwise.
"""

import pytest

from adapters.sil.sil_planner import SilPlanner, library_path
from eval import loader, metrics
from sim.harness import Harness
from sim.scenario import Scenario
from sim.world.road import Segment

pytestmark = pytest.mark.skipif(not library_path().exists(),
                                reason=f"planner library not built: {library_path()}")

SHORT = Scenario(
    name="S1-short",
    segments=(Segment("straight", 150.0), Segment("clothoid", 100.0, 1 / 500.0),
              Segment("arc", 300.0, 1 / 500.0)),
    lane_width=3.5,
    speed_mps=25.0,
    duration_s=10.0,
)


def _fingerprint(log):
    cycles = [(c.t0_us, c.trajectory, c.path_status) for c in log.cycles]
    return cycles, log.rear


def test_same_seed_same_run():
    a = Harness(SHORT, SilPlanner, seed=3).run()
    b = Harness(SHORT, SilPlanner, seed=3).run()
    assert _fingerprint(a) == _fingerprint(b)


def test_closed_loop_keeps_lane():
    result = metrics.evaluate(Harness(SHORT, SilPlanner, seed=1).run())
    by_id = {c.id: c for c in result.criteria}
    assert result.info["init_result"] == 0
    assert result.info["first_hwa_s"] is not None
    assert result.info["first_hwa_s"] < SHORT.hwa_request_s + 0.2
    assert by_id["PP-SWR-010"].passed
    assert by_id["PP-SWR-051"].passed, by_id["PP-SWR-051"]


SHARP = Scenario(
    name="S1b-short",
    segments=(Segment("straight", 60.0), Segment("clothoid", 60.0, 1 / 200.0),
              Segment("arc", 200.0, 1 / 200.0)),
    lane_width=3.5,
    speed_mps=25.0,
    duration_s=7.0,
)


@pytest.fixture(scope="module")
def sharp_result():
    return metrics.evaluate(Harness(SHARP, SilPlanner, seed=1).run())


def test_sharp_curve_limits_path(sharp_result):
    """Curve needs 3.1 m/s^2 > aysmax after a short clothoid: path cut to aysmax, HWA kept.
    PP-SWR-006 is judged on 0-1 s (SRS 1.2)."""
    by_id = {c.id: c for c in sharp_result.criteria}
    assert sharp_result.info["ay_need_max"] > 3.0
    for rid in ("PP-SWR-001", "PP-SWR-005", "PP-SWR-006", "PP-SWR-009", "PP-SWR-150"):
        assert by_id[rid].applicable and by_id[rid].passed, by_id[rid]


def test_sharp_curve_flag_on_before_lane_crossing(sharp_result):
    """PP-SWR-007 (SRS 1.3, R79 5.6.2.2.3): the flag is on when a front tyre starts to touch
    the marking; target 064 reports how early it came on."""
    by_id = {c.id: c for c in sharp_result.criteria}
    assert by_id["PP-SWR-007"].applicable and by_id["PP-SWR-007"].passed, by_id["PP-SWR-007"]
    lead = {t.id: t.value for t in sharp_result.targets}.get("PP-SWR-064")
    assert lead is not None


def test_s1_scenario_file_loads():
    s = loader.load("S1", "a")
    assert s.name == "S1a" and s.speed_mps == pytest.approx(25.0)
    assert [seg.kind for seg in s.segments] == ["straight", "clothoid", "arc"]
    assert s.segments[-1].curvature_end == pytest.approx(1 / 1000)

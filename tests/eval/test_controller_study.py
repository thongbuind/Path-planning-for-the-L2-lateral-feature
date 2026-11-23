import sys
from types import SimpleNamespace

import pytest

from eval import controller_study, metrics, proposed, study, sweep


def test_case_set_preserves_partitions():
    source = sweep.load_suite("PP-TS-020")
    suite = sweep.load_suite("PP-TS-027")
    for part in ("tuning", "test"):
        assert suite[part] == source[part]


@pytest.mark.parametrize("run, scored_vehicle_ay", [
    (["S1b", "b", {"acc": "ignore_limits"}], True),
    (["S1b", "b", {"acc": "on"}], False),
    (["S1", "c", {"acc": "ignore_limits"}], False),
])
def test_scoring_keeps_current_path_limit(monkeypatch, run, scored_vehicle_ay):
    scenario = sweep.load_run(run)
    original = metrics.Criterion("PP-SWR-001", "path a_y", 2.5, "<= 2.5", True)
    result = metrics.Result(scenario.name, 3, [original], [], {
        "ay_vehicle_r79_within_limits": False,
        "ay_vehicle_r79_max": 4.09,
        "ay_vehicle_r79_limits": [2.8, 3.3, 2.0],
    })
    monkeypatch.setattr(metrics, "evaluate", lambda log: result)

    actual, scope = controller_study.assess(SimpleNamespace(scenario=scenario), run,
                                            sweep.load_suite("PP-TS-027")["vehicle_ay"])

    assert actual.criteria[0] is original
    assert "PP-SWR-001" in scope
    assert proposed.PATH_AY_PROPOSED not in scope
    assert (proposed.VEHICLE_AY_R79 in scope) is scored_vehicle_ay
    assert len(actual.criteria) == 1 + scored_vehicle_ay
    if scored_vehicle_ay:
        assert not actual.criteria[1].passed


def test_unimplemented_variant_is_rejected_before_loading_planner(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(sys, "argv", ["controller_study.py", "PP-TS-027", "--variant", "V1",
                                      "--planner", str(tmp_path), "--out", str(tmp_path / "results")])
    with pytest.raises(SystemExit, match="2"):
        controller_study.main()
    assert "controller not implemented: V1" in capsys.readouterr().err
    assert not (tmp_path / "results").exists()


def test_planner_only_study_entry_point_rejects_controller_study(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["study.py", "PP-TS-027"])
    with pytest.raises(SystemExit, match="2"):
        study.main()
    assert "eval.controller_study PP-TS-027" in capsys.readouterr().err

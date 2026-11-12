"""Calibration sweep logic (eval/sweep.py), without building or running."""

from eval import sweep


def test_one_at_a_time_skips_start_values():
    suite = sweep.load_suite("P1")
    sets = sweep.one_at_a_time(suite)
    assert sets[0].name == "start" and sets[0].values == {}
    names = [s.name for s in sets]
    assert "k_jump=3" not in names and "k_jump=2" in names     # 3 is the start value
    assert all(len(s.values) == 1 for s in sets[1:])
    assert len(sets) == 1 + sum(len(v) - 1 for v in suite["parameters"].values())


def test_scope_follows_scenario_or_fault():
    suite = sweep.load_suite("P1")
    plain = sweep.scope_of(suite, ["S1", "a"])
    fault = sweep.scope_of(suite, ["S1", "a", "F06", "a"])
    assert "PP-SWR-051" in plain and "PP-SWR-051" not in fault
    assert "PP-SWR-125" in fault and "PP-SWR-100" in fault


def test_rank_requirements_before_targets():
    worse_target = {"failed": 0, "worst": {"PP-SWR-050": 0.5}}
    one_failure = {"failed": 1, "worst": {"PP-SWR-050": 0.01}}
    assert sweep.rank_key(worse_target) < sweep.rank_key(one_failure)
    a = {"failed": 0, "worst": {"PP-SWR-050": 0.02, "PP-SWR-125": 0.9}}
    b = {"failed": 0, "worst": {"PP-SWR-050": 0.02, "PP-SWR-125": 0.5}}
    assert sweep.rank_key(b) < sweep.rank_key(a)


def test_combined_sets_take_improving_values_only():
    suite = {"parameters": {"k_jump": [2, 3], "T_flag": [0.2, 0.3]}}
    results = [
        {"set": "start", "values": {}, "summary": {"failed": 1, "worst": {}}},
        {"set": "k_jump=2", "values": {"k_jump": 2}, "summary": {"failed": 0, "worst": {}}},
        {"set": "T_flag=0.3", "values": {"T_flag": 0.3}, "summary": {"failed": 2, "worst": {}}},
    ]
    sets = sweep.combined_sets(suite, results)
    assert [s.values for s in sets] == [{"k_jump": 2}]


def test_matrix_sim_sweep_one_at_a_time():
    import pytest
    from eval import matrix
    from sim.scenario import Scenario
    block = {"sim_sweep": {"camera_view_m": [10, 80, 126], "camera_view_start_m": [0, 5]}}
    assert matrix.sim_settings(block) == [{}, {"camera_view_m": 10.0}, {"camera_view_m": 126.0},
                                          {"camera_view_start_m": 5.0}]
    with pytest.raises(ValueError):
        matrix.sim_settings({"sim_sweep": {"speed_mps": [10]}})
    base = Scenario("x", (), 3.5, 25.0)
    assert matrix.apply_sim(base, {"camera_view_m": 40.0}).camera_view_m == 40.0
    with pytest.raises(ValueError):
        matrix.apply_sim(base, {"camera_view_m": 150.0})


def test_suite_run_with_simulator_values():
    import pytest
    from eval import sweep
    assert sweep.split_run(["S1", "c", {"camera_view_m": 30}]) == (["S1", "c"], {"camera_view_m": 30})
    assert sweep.split_run(["S1", "c", "F22", "c"]) == (["S1", "c", "F22", "c"], {})
    scenario = sweep.load_run(["S14", "a", {"camera_view_m": 40, "acc": "on"}])
    assert scenario.camera_view_m == 40.0 and scenario.acc == "on" and "camera_view_m=40" in scenario.name
    with pytest.raises(ValueError):
        sweep.load_run(["S1", "c", {"speed_mps": 10}])
    suite = sweep.load_suite("PP-TS-014")
    for part in ("tuning", "test"):
        for run in suite[part]["runs"]:
            sweep.load_run(run)
            assert sweep.scope_of(suite, run)

"""Mở lưới calibration của plan thành cấu hình riêng (eval/study.py, GĐ 4.2 của PP-TS-031)."""

import pytest

from eval import study

PLAN = {
    "variants": {
        "quintic_duration": {"calibration": {}, "cmake": {"PP_T7": "quintic_duration"}},
        "qp_jerk_admm": {"calibration": {"qp_iters": 150}, "cmake": {"PP_T7": "qp_jerk_admm"}},
    },
    "tuning_grid": {
        "quintic_duration": {"T_hwa": [2.5, 3.0, 3.5], "T_recenter": [3.0, 3.5, 4.0]},
        "qp_jerk_admm": {"qp_w_dev+qp_w_comfort": [[0.15, 2.5], [0.30, 5.0]]},
    },
}


def test_grid_skips_the_default_cell_and_keeps_variant_values():
    sets, groups, warnings = study.grid_sets(PLAN)
    assert not warnings
    assert len(groups["quintic_duration"]) == 9 and groups["quintic_duration"][0] == "quintic_duration"
    names = {s.name for s in sets}
    assert "quintic_duration-T_hwa2.5-T_recenter3.0" in names
    assert "quintic_duration-T_hwa3.0-T_recenter3.5" not in names  # Ô mặc định là biến thể gốc.
    qp = next(s for s in sets if s.name.startswith("qp_jerk_admm-"))
    assert qp.values == {"qp_iters": 150, "qp_w_dev": 0.15, "qp_w_comfort": 2.5}
    assert qp.cmake == (("PP_T7", "qp_jerk_admm"),)


def test_grid_without_default_cell_is_refused():
    plan = {**PLAN, "tuning_grid": {"quintic_duration": {"T_hwa": [2.5, 3.5]}}}
    with pytest.raises(SystemExit):
        study.grid_sets(plan)


def test_undefined_grid_is_a_draft_warning_and_an_error_when_strict():
    plan = {**PLAN, "tuning_grid": {"qp_jerk_admm": {"x": None}}}
    assert study.grid_sets(plan)[2]
    with pytest.raises(SystemExit):
        study.grid_sets(plan, strict=True)


def test_campaign_plan_grids_expand():
    import yaml
    plan = yaml.safe_load(study.find_plan("PP-TS-031").read_text(encoding="utf-8"))
    sets, groups, _ = study.grid_sets(plan)
    assert len(groups["quintic_duration"]) == 9 and len(groups["qp_jerk_admm"]) == 9

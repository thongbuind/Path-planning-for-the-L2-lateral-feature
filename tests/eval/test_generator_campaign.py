"""Bên chấm của PP-TS-031: PP-SWR-068 đến 070, cửa loại 1a và 1b, luật thắng có dung sai (SQTS 9.1, 9.2),
lệch output vòng hở và dữ liệu dashboard của eval.campaign (cờ, nhãn từng ô, giả thuyết; không xếp hạng)."""

import json
from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pytest
import yaml

from eval import campaign, compare, output_diff, techniques
from eval.metrics import evaluate
from interfaces import (
    BasicHeader, FrameId, Header, InterventionPhase, LateralLimits, LccMode, LccStatus, PlannerId, Pose2D,
    Trajectory, TrajectoryPoint,
)
from sim.harness import PlannerCycle, RunLog
from sim.scenario import Scenario
from sim.stand_ins.arbitrator import ActiveFunction, SystemStatus
from sim.world.road import Road, Segment

SPEED = 20.0


def _log(kappa: float, duration_us: int = 3_000_000, lcc_lost_from_us: int | None = None) -> RunLog:
    segments = (Segment("straight", 5.0), Segment("arc", 400.0, kappa))
    scenario = Scenario("synthetic", segments, 3.5, SPEED, hwa_request_s=None)
    road = Road(list(segments), 3.5)
    log = RunLog(scenario, 1, road, 1.9, 2.9, .61, 6.0, 15.0, 0)
    for t in range(0, duration_us + 1, 1_000):
        s = 10.0 + SPEED * t * 1e-6
        log.t_us.append(t)
        log.rear.append(road.pose_at(s))
        log.front.append(road.pose_at(s + 2.9))
        log.rear_v_y.append(0.0)
        log.yaw_rate.append(SPEED * kappa)
        log.speed.append(SPEED)
        log.a_y.append(SPEED ** 2 * kappa)
        log.eps_controlling.append(True)
    for n, t in enumerate(range(0, duration_us + 1, 25_000)):
        hdr = BasicHeader(t, n % 256, True)
        status = SystemStatus(hdr, True, ActiveFunction.LCC, InterventionPhase.NONE, InterventionPhase.NONE,
                              False, False)
        points = tuple(TrajectoryPoint(i / 10, Pose2D(2.0 * i, 0.0, 0.0), SPEED, 0.0, 0.0,
                                       SPEED ** 2 * kappa, kappa, 0.0, 0.0) for i in range(31))
        trajectory = Trajectory(Header(t, n % 256, True, FrameId.BASE_LINK), points, 3.0, PlannerId.LCC)
        driving = lcc_lost_from_us is None or t < lcc_lost_from_us
        lcc = LccStatus(hdr, driving, LccMode.LANE if driving else LccMode.NONE, 0.0, False, False)
        log.cycles.append(PlannerCycle(t, trajectory, status, LateralLimits(hdr, 30.0, 0.0, False), 0,
                                       lcc_trajectory=trajectory, lcc_status=lcc))
    return log


def _target(result, rid):
    return next((t for t in result.targets if t.id == rid), None)


def test_vehicle_targets_and_dlc_without_the_aysmax_condition():
    # Xe ở tâm làn, a_y 3,2 m/s²: PP-SWR-070 là DLC của xe, 068 và 069 đo trên xe theo R79 Annex 8, 2.4.
    log = _log(kappa=0.008)
    result = evaluate(log)
    assert _target(result, "PP-SWR-070").value == pytest.approx((3.5 - 1.9) / 2, abs=0.02)
    assert _target(result, "PP-SWR-068").value == pytest.approx(3.2, abs=0.01)
    assert _target(result, "PP-SWR-069").value == pytest.approx(0.0, abs=0.01)
    assert result.info["lcc_driving_cycles"] == len(log.cycles)


def test_dlc_070_equals_051_when_both_are_judged():
    result = evaluate(_log(kappa=0.004))
    dlc_051 = next(c for c in result.criteria if c.id == "PP-SWR-051")
    assert dlc_051.applicable
    assert _target(result, "PP-SWR-070").value == pytest.approx(dlc_051.value, abs=1e-12)


def test_open_loop_has_no_vehicle_targets_and_lcc_cycles_follow_lcc_status():
    log = _log(kappa=0.004, lcc_lost_from_us=2_000_000)
    log.scenario = replace(log.scenario, loop="open")
    result = evaluate(log)
    assert all(_target(result, rid) is None for rid in ("PP-SWR-068", "PP-SWR-069", "PP-SWR-070"))
    assert result.info["lcc_driving_cycles"] == 80  # t = 0 … 1,975 s


def test_tolerance_and_few_units_make_a_tie():
    small = compare.verdict(np.full(8, 0.003), compare.tolerance(("PP-SWR-050", "m"), None, None))
    assert small["ci"][0] > 0 and small["result"] == 0
    assert compare.verdict(np.full(8, 0.006), 0.005)["result"] == 1
    assert compare.verdict(np.full(8, -0.006), 0.005)["result"] == -1
    few = compare.verdict(np.full(3, 1.0), 0.005)
    assert few["result"] == 0 and few["note"] == compare.FEW_UNITS


def test_relative_tolerances_and_groups():
    assert compare.tolerance(("PP-SWR-016", "Thời gian tính p99"), 2.0, 1.0) == pytest.approx(0.1)
    steering = ("PP-SWR-004", "Tốc độ quay vô lăng RMS khi HWA lái, vòng kín")
    assert compare.tolerance(steering, 0.4, 0.5) == pytest.approx(0.02)
    assert compare.tolerance(("PP-SWR-004", "Jerk ngang RMS của path 0–1 s khi HWA lái"), 0.4, 0.5) == 0.10
    assert "PP-SWR-070" in compare.GROUPS[compare.SAFETY] and "PP-SWR-070" in compare.LARGER_IS_BETTER
    assert "PP-SWR-050" in compare.GROUPS[compare.LANE_KEEPING]
    assert "PP-SWR-050" not in compare.GROUPS[compare.SAFETY]
    assert all(rid in compare.TOLERANCES for ids in compare.GROUPS.values() for rid in ids)


def _technique(name, values, failed=None, lcc=None, metric=("PP-SWR-070", "DLC"), profile="VP-0"):
    cases, records = {}, {}
    for i, v in enumerate(values):
        cid = f"S1-{i}"
        cases[cid] = {"id": cid, "family": "S1", "parameters": {"variant": str(i), "profile": profile}}
        records[(cid, 3)] = {
            "case": cid, "seed": 3, "profile": profile, "scope": None, "spec": ["S1", "f"],
            "failed": (failed or {}).get(i, []), "compute_lcc_ms": {"p99": 1.0},
            "result": {"criteria": [], "issues": [], "case_failures": [],
                       "info": {"lcc_driving_cycles": (lcc or {}).get(i, 100)},
                       "targets": [{"id": metric[0], "metric": metric[1], "value": v, "unit": "m"}]}}
    return {"name": name, "folder": name, "pp_version": name, "sha256": None, "b0": None,
            "generation_sha256": "g", "partial": False, "cases": cases, "records": records}


def test_gate_is_relative_to_the_baseline_and_checks_lcc_driving_time():
    base = _technique("base", [0.5] * 6, failed={0: ["PP-SWR-006"]})
    shared = _technique("shared", [0.5] * 6, failed={0: ["PP-SWR-006"]})
    new = _technique("new", [0.5] * 6, failed={1: ["PP-SWR-001"]})
    one = _technique("one", [0.5] * 6, lcc={2: 99})
    two = _technique("two", [0.5] * 6, lcc={2: 98})
    c = techniques.rank([base, shared, new, one, two], "base")
    assert c["rows"]["shared"]["gate"]["passed"] and c["rows"]["one"]["gate"]["passed"]
    assert c["rows"]["new"]["gate"]["requirements"] == {"PP-SWR-001": 1}
    assert c["rows"]["two"]["gate"]["lcc_cycles_lost_max"] == 2
    assert set(c["eliminated"]) == {"new", "two"}
    assert c["rows"]["base"]["gate"]["shared"] == {"PP-SWR-006": 1}


def test_larger_dlc_wins_only_beyond_the_tolerance():
    base = _technique("base", [0.50, 0.52, 0.51, 0.53, 0.50, 0.52])
    wide = _technique("wide", [0.53, 0.55, 0.54, 0.56, 0.53, 0.55])
    close = _technique("close", [0.505, 0.525, 0.515, 0.535, 0.505, 0.525])
    metric = ("PP-SWR-070", "DLC")
    assert compare.pairwise(wide, base, metric, False)["result"] == 1
    assert compare.pairwise(close, base, metric, False)["result"] == 0


def test_case_patterns():
    assert techniques.matches(["S1", "f"], ["S1", "f"])
    assert techniques.matches(["S1", "f", {"profile": "VP-3"}], ["S1", "f"])
    assert not techniques.matches(["S1", "f", "F12", "b"], ["S1", "f"])
    assert techniques.matches(["S1", "c", "F01", "c"], ["F01"])
    assert techniques.matches(["S1b", "c", {"acc": "on"}], ["S1b"])
    assert techniques.matches(["S1", "c", "F01", "c"], ["S1", "c", "F01", "c"])
    assert not techniques.matches(["S1", "c", "F01", "c"], ["F01", "a"])


def _cycle(t0, y, valid=True, request="r"):
    points = [SimpleNamespace(time_from_start=i / 10, pose=SimpleNamespace(y=y * i / 30)) for i in range(31)]
    traj = SimpleNamespace(points=points, header=SimpleNamespace(valid=valid))
    return SimpleNamespace(t0_us=t0, t0_local_us=t0, input_times=None, lane_boundaries=None, inputs_ok=None,
                           lane_view_reported=None, function_requests=request, longitudinal_plan=None,
                           lead_target=None, lcc_trajectory=traj,
                           lcc_status=SimpleNamespace(path_valid=valid))


def test_output_diff_pairs_cycles_with_the_same_inputs():
    a = output_diff.cycle_outputs(SimpleNamespace(cycles=[_cycle(0, 0.3), _cycle(25_000, 0.3), _cycle(50_000, 0.3),
                                                          _cycle(75_000, 0.3)]))
    b = output_diff.cycle_outputs(SimpleNamespace(cycles=[_cycle(0, 0.0), _cycle(25_000, 0.3),
                                                          _cycle(50_000, 0.3, request="other"),
                                                          _cycle(75_000, 0.3, valid=False)]))
    stats = output_diff.compare_runs(a, b)
    # Lệch 0–1 s của chu kỳ đầu: y(1 s) = 0,3 · 10 / 30 = 0,1 m.
    assert stats["cycles"] == 4 and stats["digest_mismatch"] == 1 and stats["valid_mismatch"] == 1
    assert stats["compared"] == 2 and stats["max_m"] == pytest.approx(0.1) and stats["differs"] == 1


def _row(run, seed, spec, p99, values, lcc=100, failed=(), open_file=None):
    return {"run": run, "seed": seed, "spec": spec, "profile": "VP-0", "loop": "open" if open_file else "closed",
            "failed": list(failed), "issues": [], "case_failures": [], "criteria": [],
            "targets": [{"id": k, "metric": k, "value": v, "unit": ""} for k, v in values.items()],
            "compute_lcc_ms": {"p99": p99, "max": 2 * p99}, "lcc_driving_cycles": lcc,
            "vehicle": {"ay_vehicle_r79_within_limits": True}, "open_loop_file": open_file}


def test_campaign_cells_flags_and_hypotheses_without_ranking(tmp_path):
    names = {"quintic_duration": (1.0, 0.0), "quintic_tangent_point": (1.2, 0.0),
             "qp_jerk_admm_it010": (0.5, 0.02), "qp_jerk_admm": (3.0, 0.001), "qp_jerk_admm_it1000_ref": (20.0, 0.0)}
    results = []
    for name, (p99, offset) in names.items():
        build = tmp_path / name / "build"
        build.mkdir(parents=True)
        runs = []
        for i in range(6):
            spec = ["S1", "f"] if i < 4 else ["S2", "d"]
            ay = 2.6 - (0.2 if name == "quintic_tangent_point" else 0.0) + 0.01 * i
            failed = ["PP-SWR-006"] if name == "qp_jerk_admm_it010" and i == 5 else []
            runs.append(_row(f"S1f-{i}", 3, spec, p99, {"PP-SWR-068": ay, "PP-SWR-069": 1.0, "PP-SWR-070": 0.5},
                             failed=failed))
        log = SimpleNamespace(cycles=[_cycle(25_000 * k, 0.3 + offset) for k in range(10)])
        output_diff.save(tmp_path / name / "open_loop/test/000_s3.npz", output_diff.cycle_outputs(log))
        open_row = _row("S1f-open", 3, ["S1", "f", {"loop": "open"}], p99, {}, open_file="open_loop/test/000_s3.npz")
        ranked = name != "qp_jerk_admm_it1000_ref"
        results.append({"set": name, "part": "test", "library": str(build),
                        "values": {"qp_iters": 10} if name.endswith("it010") else {},
                        "runs": (runs if ranked else []) + [open_row]})
    plan = {"id": "PP-TS-T", "suite": "PP-T7", "baseline": "quintic_duration", "flags": {"lcc_cycles_lost_max": 1},
            "case_groups": {"cua ngắn": [["S1", "f"]], "chức năng": [["S2"]]},
            "hypotheses": [
                {"id": "H1", "kind": "paired", "variants": ["quintic_tangent_point"], "against": "quintic_duration",
                 "cases": [["S1", "f"]], "primary": {"target": "PP-SWR-068", "improve_at_least": 0.10},
                 "guards": [{"target": "PP-SWR-069", "worsen_at_most": 0.10}]},
                {"id": "H2", "kind": "smallest", "variants": ["qp_jerk_admm_it010", "qp_jerk_admm"],
                 "reference": "qp_jerk_admm_it1000_ref", "at_most": 0.005},
                {"id": "H4b", "kind": "cheaper", "variants": ["qp_jerk_admm_it010"], "against": "qp_jerk_admm",
                 "reference": "qp_jerk_admm_it1000_ref", "p99_ratio_max": 0.9},
                {"id": "H5", "kind": "cells", "variants": ["quintic_tangent_point"], "against": "quintic_duration"}],
            "variants": {n: {"description": n} for n in names}}
    plan["variants"]["qp_jerk_admm_it1000_ref"].update({"loops": ["open"], "ranked": False})
    plan_path = tmp_path / "plan.yaml"
    plan_path.write_text(yaml.safe_dump(plan, allow_unicode=True), encoding="utf-8")
    (tmp_path / "results.json").write_text(json.dumps(results), encoding="utf-8")
    (tmp_path / "output_diff.json").write_text(json.dumps(output_diff.study_diffs(results, plan)), encoding="utf-8")

    data = campaign.build("PP-TS-T", plan_path, [tmp_path])
    assert data["draft"] is True
    assert not any(k in data for k in ("order", "eliminated", "copeland"))
    rows = data["parts"]["test"]["configs"]
    ay = next(c for k, c in rows["quintic_tangent_point"]["cells"].items() if k.startswith("PP-SWR-068"))
    assert ay["label"] == "better" and ay["n"] == 6 and ay["mean"] == pytest.approx(0.2)
    assert ay["groups"]["cua ngắn"]["n"] == 4
    # Trượt mới chỉ là cờ: cấu hình vẫn có ô so sánh.
    assert rows["qp_jerk_admm_it010"]["flags"]["new_failure_runs"] == 1 and rows["qp_jerk_admm_it010"]["cells"]
    assert rows["qp_jerk_admm_it1000_ref"]["cells"] == {}
    h = data["hypotheses"]["test"]
    assert h["H1"]["rows"][0]["holds"] is True and h["H1"]["summary"]["quintic_tangent_point"]["held"] == 1
    # Bản 10 vòng lệch 0,02 · 10 / 30 m so với nghiệm tham chiếu; bản 150 vòng lệch 0,00033 m.
    assert h["H2"]["rows"][-1]["config"] == "qp_jerk_admm"
    assert h["H4b"]["rows"][0]["holds"] is False
    assert h["H5"]["rows"][0]["holds"] is True
    qp = {r["config"]: r for r in data["parts"]["test"]["qp_iterations"]}
    assert qp["qp_jerk_admm_it010"]["iterations"] == 10 and "qp_jerk_admm_it1000_ref" not in qp


def test_dashboard_page_is_self_contained_and_marks_drafts():
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location(
        "dashboard_build", Path(__file__).resolve().parents[2] / "research/generators/dashboard/build.py")
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)
    data = {"study": "PP-TS-T", "baseline": "quintic_duration", "draft": True, "parts": {}, "grid_warnings": [],
            "note": "</script><b>"}
    html = build.page(data)
    assert "NHÁP" in html and 'class="page' in html
    assert "<script" not in html and "<button" not in html and "<select" not in html
    assert "http://" not in html.replace("http://www.w3.org", "") and "https://" not in html
    assert "NHÁP" not in build.page({**data, "draft": False})

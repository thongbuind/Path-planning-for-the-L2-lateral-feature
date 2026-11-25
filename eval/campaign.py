"""Dữ liệu dashboard so sánh generator T7 của PP-TS-031 (PP-TS-031 mục 3).

Chỉ mô tả: không xếp hạng, không điểm tổng, không loại. Mỗi ô là hiệu ghép cặp so với mốc kèm CI 95 %, n và
nhãn "tốt hơn", "xấu hơn" (CI không chứa 0 và |hiệu| ≥ dung sai SQTS 9.2), "trong dung sai" hoặc "ít dữ liệu".
Cờ cảnh báo (B0, trượt mới, LCC lái ít hơn) hiện cạnh chỉ số, không loại cấu hình nào.

Đọc một hay nhiều thư mục kết quả của eval.study (research/runs/<run-id>/ hoặc build/study/...), gộp lại, rồi
ghi research/generators/dashboard/techniques.json cho dashboard/build.py.
"""

import argparse
import datetime
import json
import math
import re
from pathlib import Path

import numpy as np
import yaml

from eval import compare, output_diff, report, techniques
from interfaces import PLANNER_PERIOD_US

ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = ROOT / "research" / "runs"
STUDY_DIR = ROOT / "build" / "study"
OUT = ROOT / "research" / "generators" / "dashboard" / "techniques.json"
LAB_DIR = ROOT / "research" / "generators"
CYCLE_MS = PLANNER_PERIOD_US / 1000.0
LABELS = {1: "better", -1: "worse", 0: "within"}
FEW = "few"
STEPS = (compare.SAFETY, compare.LANE_KEEPING, compare.COMPUTE)


# ---------------------------------------------------------------- nạp và gộp

def find_runs(study_id: str) -> list[Path]:
    """Các lần chạy --record của study; không có thì các thư mục nháp trong build/study/<id>."""
    official = sorted(p.parent for p in RUNS_DIR.glob(f"*-study-{study_id}-*/results.json"))
    official += sorted(p.parent for p in RUNS_DIR.glob(f"*-timing-{study_id}-*/timing.json"))
    if official:
        return official
    draft = STUDY_DIR / study_id
    return sorted({p.parent for name in ("results.json", "timing.json") for p in draft.rglob(name)}) \
        if draft.is_dir() else []


def _same_values(a: dict, b: dict) -> bool:
    rows_a = {(r["run"], r["seed"]): r["values"] for r in a["runs"]}
    rows_b = {(r["run"], r["seed"]): r["values"] for r in b["runs"]}
    if rows_a.keys() != rows_b.keys():
        return False
    for key, va in rows_a.items():
        vb = rows_b[key]
        for k in set(va) | set(vb):
            x, y = va.get(k), vb.get(k)
            if (x is None) != (y is None) or (x is not None and not (x == y or (math.isnan(x) and math.isnan(y)))):
                return False
    return True


def load(folders: list[Path], plan: dict) -> dict:
    """Gộp kết quả. Một cấu hình chạy ở nhiều lần (mốc có trong mỗi lần chạy theo nhóm) thì giữ lần đầu và
    ghi việc các lần lặp có trùng giá trị không (độ tin: tất định)."""
    entries, origin, repeats, diffs, manifests, timing = {}, {}, {}, [], [], {}
    for folder in folders:
        folder = Path(folder)
        manifest_path = folder / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
        manifests.append({"folder": str(folder), "run_id": manifest.get("run_id"),
                          "parts": manifest.get("parts"), "groups": manifest.get("groups"),
                          "dirty": manifest.get("git", {}).get("dirty", True), "commit": manifest.get("git", {}).get("short"),
                          "official": folder.resolve().is_relative_to(RUNS_DIR.resolve())})
        if (folder / "timing.json").is_file():
            summary = json.loads((folder / "timing.json").read_text(encoding="utf-8"))["summary"]
            timing.update({name: {**v, "run_id": manifest.get("run_id")} for name, v in summary.items()})
        if not (folder / "results.json").is_file():
            continue
        for entry in json.loads((folder / "results.json").read_text(encoding="utf-8")):
            key = (entry["set"], entry["part"])
            if key in entries:
                repeats.setdefault(key, []).append(_same_values(entries[key], entry))
                continue
            entries[key] = entry
            origin[key] = (folder, manifest)
        diff_path = folder / "output_diff.json"
        if diff_path.is_file():
            diffs.extend(json.loads(diff_path.read_text(encoding="utf-8"))["pairs"])
    seen, pairs = set(), []
    for p in diffs:
        k = (p["a"], p["b"], p["part"])
        if k not in seen:
            seen.add(k)
            pairs.append(p)
    techniques_by_part = {}
    for (name, part), entry in entries.items():
        folder, manifest = origin[(name, part)]
        t = _technique(entry, folder, manifest, plan, part)
        techniques_by_part.setdefault(part, {})[name] = t
    return {"techniques": techniques_by_part, "diffs": {"pairs": pairs}, "manifests": manifests, "timing": timing,
            "repeats": {f"{n}|{p}": v for (n, p), v in repeats.items()}}


def _technique(entry: dict, folder: Path, manifest: dict, plan: dict, part: str) -> dict:
    cases, records = {}, {}
    for row in entry["runs"]:
        case, record = techniques._record(row)
        record["t7_telemetry"] = row.get("t7_telemetry")
        cases[case["id"]] = case
        records[(row["run"], row["seed"])] = record
    lib = techniques._lcc_library(manifest, entry["library"])
    b0_path = folder / "conformance" / f"{entry['set']}.json"
    return {"folder": str(folder / entry["set"]), "name": entry["set"], "run_id": manifest.get("run_id"),
            "pp_version": lib.get("pp_version"), "sha256": lib.get("sha256"),
            "calibration_hash": (lib.get("build") or {}).get("calibration"),
            "state_size_bytes": lib.get("state_size_bytes"), "file_size_bytes": lib.get("file_size_bytes"),
            "b0": json.loads(b0_path.read_text(encoding="utf-8")) if b0_path.is_file() else None,
            "generation_sha256": f"{plan['suite']}:{part}", "partial": False,
            "cases": cases, "records": records, "calibration": entry.get("values") or {}, "library": entry["library"]}


# ---------------------------------------------------------------- ô so với mốc

def cell(a: dict, base: dict, metric: tuple[str, str], units: set | None = None, flexibility: bool = False,
         keep: bool = False) -> dict:
    """Hiệu theo hướng có lợi cho a (dương: tốt hơn mốc). keep: giữ hiệu từng lượt để vẽ phân bố."""
    diff, common, level_a, level_b = compare.paired_diff(a, base, metric, flexibility, units=units)
    v = compare.verdict(diff, compare.tolerance(metric, level_a, level_b))
    out = {"n": v["units"], "mean": v["mean"], "ci": v["ci"], "tolerance": v["tolerance"],
           "label": FEW if v["note"] else LABELS[v["result"]], "level": level_a, "level_base": level_b}
    if keep:
        out["diffs"] = [{"case": k[0], "seed": k[1], "d": round(float(x), 6)} for k, x in zip(common, diff)]
    if len(diff):
        k = int(np.argmin(diff))
        out["worst"] = {"case": common[k][0], "seed": common[k][1], "diff": float(diff[k])}
    return out


def flags(t: dict, base: dict, lost_max: int) -> dict:
    g = techniques.gate(t, base, lost_max)
    new_runs = []
    for key, r in t["records"].items():
        extra = techniques.failures(r) - techniques.failures(base["records"].get(key))
        if extra:
            new_runs.append({"case": key[0], "seed": key[1], "profile": r.get("profile"), "failed": sorted(extra)})
    return {"b0": g["b0"], "b0_blocked": bool(t.get("b0") and t["b0"].get("blocked")),
            "new_failure_runs": g["new_failure_runs"], "new_failures": new_runs,
            "requirements": g["requirements"], "shared_failures": g["shared"],
            "lcc_runs_lost": g["lcc_runs_lost"], "lcc_cycles_lost_max": g["lcc_cycles_lost_max"],
            "lcc_lost": g["lcc_lost"], "lcc_unmeasured_runs": g["lcc_unmeasured_runs"],
            "evaluator_errors": g["evaluator_errors"],
            "any": bool(g["new_failure_runs"] or g["lcc_runs_lost"] or (t.get("b0") and t["b0"].get("blocked")))}


def _metric_list(techs: list[dict]) -> list[dict]:
    groups = compare.group_metrics(techs)
    return [{"group": g, "id": m[0], "metric": m[1], "larger_is_better": m[0] in compare.LARGER_IS_BETTER}
            for g in STEPS for m in groups[g]]


def _flex_metrics(techs: list[dict]) -> list[tuple[str, str]]:
    return compare.group_metrics(techs)[compare.FLEXIBILITY]


# ---------------------------------------------------------------- chi phí, độ tin, chẩn đoán

def _median(values) -> float | None:
    values = [v for v in values if v is not None and math.isfinite(v)]
    return float(np.median(values)) if values else None


def _p99s(t: dict) -> dict:
    return {k: r["compute_lcc_ms"].get("p99") for k, r in t["records"].items() if r["compute_lcc_ms"].get("p99")}


def _telemetry(t: dict) -> dict | None:
    rows = [r["t7_telemetry"] for r in t["records"].values() if r.get("t7_telemetry")]
    if not rows:
        return None

    def worst(key, stat):
        values = [(r.get(key) or {}).get(stat) for r in rows]
        values = [v for v in values if v is not None and math.isfinite(v)]
        return max(values) if values else None

    return {"runs": len(rows), "work_max": worst("work", "max"), "work_p99": worst("work", "p99"),
            "infer_ops_max": max(r.get("infer_ops_max") or 0 for r in rows),
            "fallback_share_mean": float(np.mean([r["fallback_share"] for r in rows])),
            "residual_p99": worst("residual", "p99"), "slack_max": worst("slack", "max"),
            "t10_change_max_m": worst("t10_change_m", "max"),
            "t10_changed_share_mean": float(np.mean([r["t10_changed_share"] for r in rows
                                                     if r.get("t10_changed_share") is not None
                                                     and math.isfinite(r["t10_changed_share"])] or [math.nan]))}


def _weights_bytes(cmake: dict) -> int | None:
    lab = cmake.get("PP_T7_LAB")
    if not lab:
        return None
    files = list((LAB_DIR / lab).glob("model/*.h"))
    return sum(f.stat().st_size for f in files) if files else None


def cost(t: dict, cmake: dict) -> dict:
    p99s = list(_p99s(t).values())
    maxima = [r["compute_lcc_ms"].get("max") for r in t["records"].values() if r["compute_lcc_ms"].get("max")]
    p99 = _median(p99s)
    tm = _telemetry(t)
    return {"p99_median_ms": p99, "p99_cycle_share": None if p99 is None else p99 / CYCLE_MS,
            "p99_max_ms": max(p99s) if p99s else None, "max_ms": max(maxima) if maxima else None,
            "state_bytes": t["state_size_bytes"], "library_bytes": t["file_size_bytes"],
            "weights_bytes": _weights_bytes(cmake),
            "work_max": tm and tm["work_max"], "infer_ops_max": tm and tm["infer_ops_max"]}


def _info(t: dict, key: str) -> list:
    return [r["result"]["info"].get(key) for r in t["records"].values() if r["result"]["info"].get(key) is not None]


def diagnostics(t: dict) -> dict:
    near = _info(t, "path_near_limit_share")
    over = _info(t, "ay_vehicle_r79_over_sustained_s")
    jerk = [c["value"] for r in t["records"].values() for c in r["result"]["criteria"]
            if c["id"] == "PP-SWR-003" and c["value"] is not None]
    f06 = [v for r in t["records"].values() for (rid, _), v in compare._targets(r).items() if rid == "PP-SWR-125"]
    return {"path_jerk_max": max(jerk) if jerk else None,
            "near_limit_share_mean": float(np.mean(near)) if near else None,
            "near_limit_share_max": max(near) if near else None,
            "ay_over_sustained_max_s": max(over) if over else None,
            "r79_outside_runs": sum(1 for v in _info(t, "ay_vehicle_r79_within_limits") if v is False),
            "swr125_max": max(f06) if f06 else None, "telemetry": _telemetry(t)}


def by_profile(t: dict, metrics: list[dict]) -> dict:
    out = {}
    for m in metrics:
        if m["group"] == compare.COMPUTE:
            continue
        metric, worst = (m["id"], m["metric"]), {}
        pick = min if m["larger_is_better"] else max
        for r in t["records"].values():
            v = compare._targets(r).get(metric)
            if v is not None:
                worst[r["profile"]] = pick(worst.get(r["profile"], v), v)
        if worst:
            out[f"{m['id']}|{m['metric']}"] = worst
    return out


def credibility(t: dict, base: dict, diffs: dict, part: str, metrics: list[dict], baseline: str) -> dict:
    d = output_diff.lookup(diffs, t["name"], baseline, part) if t["name"] != baseline else None
    few = sum(1 for m in metrics if cell(t, base, (m["id"], m["metric"]))["label"] == FEW) if t["name"] != baseline else 0
    return {"compared_cycles": d and d["compared"], "digest_mismatch": d and d["digest_mismatch"],
            "valid_mismatch": d and d["valid_mismatch"], "differs_share": d and d["differs_share"],
            "few_data_metrics": few}


def gap(test_cells: dict, tuning_cells: dict) -> dict:
    """Chênh tuning–test (mục 2.6): nhãn đổi chiều, hoặc tốt hơn ở tuning mà trong dung sai ở test."""
    flipped, faded, measured = [], [], 0
    for key, c in test_cells.items():
        u = tuning_cells.get(key)
        if u is None or FEW in (c["label"], u["label"]):
            continue
        measured += 1
        if {c["label"], u["label"]} == {"better", "worse"}:
            flipped.append(key)
        elif u["label"] == "better" and c["label"] == "within":
            faded.append(key)
    return {"flipped": flipped, "faded": faded, "measured": measured}


# ---------------------------------------------------------------- giả thuyết

def _diff_max(diffs, a, ref, part):
    d = output_diff.lookup(diffs, a, ref, part)
    return None if not d or d["max_m"] is None else d


def hypothesis(h: dict, by_name: dict, flag: dict, diffs: dict, part: str, groups: dict) -> list[dict]:
    """Một dòng mỗi cấu hình (cả lưới của biến thể) hoặc mỗi cặp. holds: True, False, None (thiếu dữ liệu)."""
    kind, rows = h["kind"], []

    def configs(v):
        return [c for c in groups.get(v, [v]) if c in by_name] or [v]

    if kind == "paired":
        base = by_name.get(h["against"])
        for v in h["variants"]:
            for name in configs(v):
                p = by_name.get(name)
                if p is None or base is None:
                    rows.append({"variant": v, "config": name, "holds": None, "values": {}})
                    continue
                units = techniques._units(p, h.get("cases"))
                values, ok, have = {}, True, False
                for metric in techniques._metrics_of([p, base], h["primary"]["target"]):
                    c = cell(p, base, metric, units)
                    have = True
                    good = c["label"] != FEW and c["mean"] >= h["primary"]["improve_at_least"] and c["ci"][0] > 0
                    ok &= good
                    values[f"{metric[0]}|{metric[1]}"] = c
                for guard in h.get("guards", []):
                    for metric in techniques._metrics_of([p, base], guard["target"]):
                        c = cell(p, base, metric, units)
                        ok &= c["mean"] is not None and -c["mean"] <= guard["worsen_at_most"]
                        values[f"{metric[0]}|{metric[1]}"] = c
                new = flag.get(name, {}).get("new_failure_runs", 1)
                rows.append({"variant": v, "config": name, "holds": (ok and not new) if have else None,
                             "values": values, "new_failure_runs": new})
    elif kind == "smallest":
        first = None
        for v in h["variants"]:
            d = _diff_max(diffs, v, h["reference"], part)
            ok = bool(d and d["max_m"] <= h["at_most"] and d["valid_mismatch"] == 0) \
                and not flag.get(v, {}).get("new_failure_runs", 1)
            rows.append({"variant": v, "config": v, "holds": None if d is None else ok,
                         "values": {"diff_max_m": d and d["max_m"], "diff_mean_m": d and d["mean_m"],
                                    "valid_mismatch": d and d["valid_mismatch"]}})
            if ok and first is None:
                first = v
        rows.append({"variant": "smallest", "config": first, "holds": first is not None, "values": {}})
    elif kind == "beats":
        for a, b in h["pairs"]:
            da, db = _diff_max(diffs, a, h["reference"], part), _diff_max(diffs, b, h["reference"], part)
            rows.append({"variant": a, "config": a, "against": b,
                         "holds": None if not da or not db else da["max_m"] <= db["max_m"] - h["better_by"],
                         "values": {"diff_max_m": da and da["max_m"], "against_diff_max_m": db and db["max_m"]}})
    elif kind == "cheaper":
        ref_d = _diff_max(diffs, h["against"], h["reference"], part)
        against = by_name.get(h["against"])
        for v in h["variants"]:
            d, p = _diff_max(diffs, v, h["reference"], part), by_name.get(v)
            if not d or not ref_d or p is None or against is None:
                rows.append({"variant": v, "config": v, "holds": None, "values": {}})
                continue
            pa, pb = _p99s(p), _p99s(against)
            ratio = _median([pa[k] / pb[k] for k in set(pa) & set(pb) if pb[k] > 0])
            rows.append({"variant": v, "config": v,
                         "holds": d["max_m"] <= ref_d["max_m"] and ratio is not None and ratio <= h["p99_ratio_max"],
                         "values": {"diff_max_m": d["max_m"], "against_diff_max_m": ref_d["max_m"], "p99_ratio": ratio}})
    elif kind == "cells":
        against = by_name.get(h["against"])
        for v in h["variants"]:
            for name in configs(v):
                p = by_name.get(name)
                if p is None or against is None:
                    rows.append({"variant": v, "config": name, "holds": None, "values": {}})
                    continue
                labels = {}
                for m in _metric_list([p, against]):
                    if m["group"] in (compare.SAFETY, compare.LANE_KEEPING):
                        labels[f"{m['id']}|{m['metric']}"] = cell(p, against, (m["id"], m["metric"]))["label"]
                better = sum(1 for x in labels.values() if x == "better")
                worse = sum(1 for x in labels.values() if x == "worse")
                rows.append({"variant": v, "config": name, "holds": better > 0 and worse == 0,
                             "values": {"better": better, "worse": worse, "labels": labels}})
    else:  # report: chỉ báo cờ.
        for v in h["variants"]:
            for name in configs(v):
                f = flag.get(name)
                rows.append({"variant": v, "config": name, "holds": None,
                             "values": {} if f is None else {k: f[k] for k in ("new_failure_runs", "lcc_runs_lost", "b0")}})
    return rows


def hypothesis_summary(rows: list[dict]) -> dict:
    """"Đạt ở x/n cấu hình" theo từng biến thể (mục 2.5)."""
    out = {}
    for r in rows:
        if r["variant"] == "smallest":
            continue
        s = out.setdefault(r["variant"], {"held": 0, "measured": 0, "configs": 0})
        s["configs"] += 1
        if r["holds"] is not None:
            s["measured"] += 1
            s["held"] += bool(r["holds"])
    return out


# ---------------------------------------------------------------- số vòng QP

def _pareto(points: dict) -> set:
    return {n for n, (x, y) in points.items()
            if not any((x2 <= x and y2 <= y) and (x2 < x or y2 < y) for m, (x2, y2) in points.items() if m != n)}


def qp_iterations(by_name: dict, configs: dict, diffs: dict, part: str, reference: str | None) -> list[dict]:
    rows, points = [], {}
    for name, info in configs.items():
        iters = (by_name[name]["calibration"].get("qp_iters") if name in by_name else None) \
            or info["values"].get("qp_iters")
        if iters is None or name not in by_name or not info["compared"] or not info["default"]:
            continue
        d = _diff_max(diffs, name, reference, part) if reference else None
        p99 = _median(_p99s(by_name[name]).values())
        series = re.sub(r"_it\d+(_ref)?$", "", info["family"])  # Họ: QP thường, dịch thời gian, MLP warm start.
        rows.append({"config": name, "family": info["family"], "series": series, "iterations": int(iters),
                     "p99_median_ms": p99,
                     "diff_max_m": d and d["max_m"], "diff_mean_m": d and d["mean_m"]})
        if p99 is not None and d:
            points[name] = (p99, d["max_m"])
    front = _pareto(points)
    for r in rows:
        r["pareto"] = r["config"] in front
    return sorted(rows, key=lambda r: (r["series"], r["iterations"]))


# ---------------------------------------------------------------- tổng hợp

def config_table(plan: dict) -> tuple[dict, dict, list[str]]:
    from eval import study, sweep
    grid, groups, warnings = study.grid_sets(plan)
    configs = {}
    for cal_set in study.variant_sets(plan) + grid:
        family = cal_set.name if cal_set.name in plan["variants"] else cal_set.name.split("-", 1)[0]
        v = plan["variants"][family]
        values = dict(cal_set.values)
        if family.startswith("qp_jerk_admm") and "qp_iters" not in values:
            values["qp_iters"] = sweep.base_values(["qp_iters"])["qp_iters"]
        grid_keys = [n for key in (plan.get("tuning_grid") or {}).get(family) or {} for n in key.split("+")]
        if cal_set.name == family and grid_keys:  # Cấu hình mặc định: ghi giá trị mặc định của tham số lưới.
            try:
                defaults = study._defaults(cal_set)
                values.update({n: defaults[n] for n in grid_keys if n in defaults and n not in values})
            except FileNotFoundError:
                pass
        configs[cal_set.name] = {"family": family, "default": cal_set.name == family, "values": values,
                                 "grid_values": {n: values[n] for n in grid_keys if n in values}
                                 if cal_set.name != family else {},
                                 "description": v.get("description", ""), "compared": v.get("ranked", True),
                                 "cmake": dict(cal_set.cmake), "loops": list(cal_set.loops)}
    return configs, groups, warnings


def build(study_id: str, plan_path: Path, folders: list[Path]) -> dict:
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    loaded = load(folders, plan)
    configs, groups, warnings = config_table(plan)
    baseline = plan["baseline"]
    lost_max = (plan.get("flags") or plan.get("gates") or {}).get("lcc_cycles_lost_max", techniques.LCC_CYCLES_LOST_MAX)
    case_groups = plan.get("case_groups") or {}
    diffs = loaded["diffs"]
    reference = next((h["reference"] for h in plan.get("hypotheses", []) if h.get("reference")), None)
    parts_out, hypotheses = {}, {}
    for part, by_name in loaded["techniques"].items():
        base = by_name.get(baseline)
        if base is None:
            raise SystemExit(f"{part}: baseline {baseline} was not run")
        compared = [t for n, t in by_name.items() if configs.get(n, {}).get("compared", True)]
        metrics = _metric_list(compared)
        flex = _flex_metrics(compared)
        rows, flag = {}, {}
        for name, t in by_name.items():
            info = configs.get(name, {"compared": True})
            f = flags(t, base, lost_max)
            flag[name] = f
            cells = {}
            if name != baseline and info["compared"]:
                for m in metrics:
                    metric = (m["id"], m["metric"])
                    c = cell(t, base, metric, keep=True)
                    if c["n"] == 0:
                        continue
                    c["groups"] = {g: cell(t, base, metric, techniques._units(t, pats))
                                   for g, pats in case_groups.items()}
                    cells[f"{m['id']}|{m['metric']}"] = c
                for metric in flex:
                    c = cell(t, base, metric, flexibility=True)
                    if c["n"]:
                        cells[f"flex|{metric[0]}|{metric[1]}"] = c
            rows[name] = {"run_id": t["run_id"], "pp_version": t["pp_version"], "library_sha256": t["sha256"],
                          "calibration_hash": t["calibration_hash"], "runs": len(t["records"]),
                          "flags": f, "cells": cells,
                          "cost": {**cost(t, info.get("cmake", {})), "timing_1job": loaded["timing"].get(name)},
                          "credibility": credibility(t, base, diffs, part, metrics, baseline)
                          if info["compared"] else None,
                          "diagnostics": diagnostics(t), "by_profile": by_profile(t, metrics)}
        parts_out[part] = {"metrics": metrics, "flex_metrics": [list(m) for m in flex], "configs": rows,
                           "qp_iterations": qp_iterations(by_name, configs, diffs, part, reference)}
        hypotheses[part] = {}
        for h in plan.get("hypotheses", []):
            hr = hypothesis(h, by_name, flag, diffs, part, groups)
            hypotheses[part][h["id"]] = {"kind": h["kind"], "rows": hr, "summary": hypothesis_summary(hr)}
    if "test" in parts_out and "tuning" in parts_out:
        for name, row in parts_out["test"]["configs"].items():
            tuning_row = parts_out["tuning"]["configs"].get(name)
            if row["credibility"] is not None and tuning_row is not None:
                row["credibility"]["tuning_test_gap"] = gap(row["cells"], tuning_row["cells"])
    official = bool(loaded["manifests"]) and all(m["official"] and not m["dirty"] for m in loaded["manifests"])
    families = [{"variant": vid, "default": vid, "configs": groups.get(vid, [vid]),
                 "grid": (plan.get("tuning_grid") or {}).get(vid), "description": v.get("description", ""),
                 "compared": v.get("ranked", True)} for vid, v in plan["variants"].items()]
    return {"study": study_id, "plan": {"path": str(plan_path.relative_to(ROOT) if plan_path.is_relative_to(ROOT) else plan_path), "locked": plan.get("locked"),
                                        "sha256": _sha(plan_path)},
            "draft": not (official and plan.get("locked")), "baseline": baseline, "reference": reference,
            "case_groups": case_groups, "lost_max": lost_max, "families": families, "configs": configs,
            "grid_warnings": warnings, "runs": loaded["manifests"], "repeats": loaded["repeats"],
            "parts": parts_out, "hypotheses": hypotheses, "cycle_ms": CYCLE_MS}


def _sha(path: Path) -> str:
    from eval import provenance
    return provenance.sha256(path)


def _jsonable(value):
    """`locked` của plan.yaml là ngày (YAML đọc thành date)."""
    if isinstance(value, datetime.date):
        return value.isoformat()
    return report.jsonable(value)


def main() -> None:
    parser = argparse.ArgumentParser(description="Dashboard data of a generator campaign (PP-TS-031); no ranking")
    parser.add_argument("study", nargs="?", default="PP-TS-031")
    parser.add_argument("folders", nargs="*", type=Path,
                        help="eval.study result folders (default: its --record runs, else build/study drafts)")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    from eval import study
    plan_path = study.find_plan(args.study)
    folders = args.folders or find_runs(args.study)
    if not folders:
        raise SystemExit(f"{args.study}: no eval.study results found")
    data = build(args.study, plan_path, folders)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=1, ensure_ascii=False, default=_jsonable) + "\n",
                        encoding="utf-8")
    print(f"{args.out} ({'draft' if data['draft'] else 'official'}; {len(folders)} result folders)")


if __name__ == "__main__":
    main()

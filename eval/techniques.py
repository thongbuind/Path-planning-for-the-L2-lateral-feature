"""So sánh kỹ thuật trong một planner (Software Qualification Test Specification 9.1, 10).

Hai nguồn: thư mục kết quả của eval.suite (mỗi kỹ thuật một thư mục), hoặc kết quả của eval.study với
suite có paired_evidence (`--study`), khi đó sinh thêm bảng giả thuyết, chi phí, độ tin và chẩn đoán.
"""

import argparse
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
import yaml

from eval import compare, output_diff, report
from interfaces import PLANNER_PERIOD_US

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "build" / "techniques"
STUDY_DIR = ROOT / "build" / "study"
STEPS = (compare.SAFETY, compare.LANE_KEEPING, compare.FLEXIBILITY, compare.COMPUTE)
# SQTS 9.1 bước 1b: số chu kỳ LCC lái được ít hơn mốc ở một lần chạy.
LCC_CYCLES_LOST_MAX = 1
CYCLE_MS = PLANNER_PERIOD_US / 1000.0
EXECUTION = "execution"
MISSING = "thiếu dữ liệu"


# ---------------------------------------------------------------- bước 1: cửa loại

def failures(record: dict | None) -> set[str]:
    if record is None:
        return set()
    out = set(record.get("failed") or [])
    if EXECUTION in record:
        out.add(EXECUTION)
    for issue in (record.get("result") or {}).get("issues") or []:
        if issue.get("kind") == EXECUTION:
            out.add(EXECUTION)
    return out


def lcc_cycles(record: dict | None) -> int | None:
    if record is None or record.get("result") is None:
        return None
    value = (record["result"].get("info") or {}).get("lcc_driving_cycles")
    return None if value is None else int(value)


def gate(p: dict, base: dict, lost_max: int = LCC_CYCLES_LOST_MAX) -> dict:
    """1a: trượt mà mốc đạt ở cùng ca, profile, seed; 1b: LCC lái ít hơn mốc quá lost_max chu kỳ; B0."""
    new, shared, lost, unmeasured = {}, Counter(), [], 0
    for key, r in p["records"].items():
        b = base["records"].get(key)
        own, theirs = failures(r), failures(b)
        if own - theirs:
            new[key] = sorted(own - theirs)
        shared.update(own & theirs)
        mine, ref = lcc_cycles(r), lcc_cycles(b)
        if mine is None or ref is None:
            unmeasured += 1
        elif ref - mine > lost_max:
            lost.append({"case": key[0], "seed": key[1], "lost": ref - mine})
    profiles = sorted({p["records"][k].get("profile") for k in new if p["records"][k].get("profile")})
    b0 = p.get("b0")
    b0_text = "chưa chạy" if b0 is None else "trượt C1 hoặc C2" if b0.get("blocked") else "đạt C1, C2"
    return {"passed": not new and not lost and not (b0 and b0.get("blocked")),
            "new_failure_runs": len(new),
            "requirements": dict(Counter(f for v in new.values() for f in v).most_common()),
            "profiles": profiles, "shared": dict(shared.most_common()),
            "lcc_runs_lost": len(lost), "lcc_cycles_lost_max": max((x["lost"] for x in lost), default=0),
            "lcc_lost": lost[:20], "lcc_unmeasured_runs": unmeasured, "b0": b0_text,
            "evaluator_errors": sum("error" in r for r in p["records"].values())}


def rank(techniques: list[dict], baseline: str, lost_max: int = LCC_CYCLES_LOST_MAX) -> dict:
    compare.check_same_benchmark(techniques)
    by_name = {t["name"]: t for t in techniques}
    if baseline not in by_name:
        raise SystemExit(f"baseline {baseline} is not among the techniques")
    rows = {t["name"]: {"gate": gate(t, by_name[baseline], lost_max)} for t in techniques}
    kept = [t for t in techniques if rows[t["name"]]["gate"]["passed"]]
    score, duels = compare.copeland(kept) if len(kept) > 1 else ({t["name"]: {g: 0 for g in compare.GROUPS}
                                                                 for t in kept}, [])
    for name, s in score.items():
        rows[name]["copeland"] = s
    order = sorted((t["name"] for t in kept), key=lambda n: tuple(-score[n][g] for g in STEPS))
    eliminated = [t["name"] for t in techniques if t["name"] not in score]
    return {"baseline": baseline, "order": order, "eliminated": eliminated, "rows": rows, "duels": duels,
            "absolute": compare.absolute_values(techniques), "runs": len(techniques[0]["records"]),
            "techniques": [{"name": t["name"], "pp_version": t["pp_version"], "sha256": t["sha256"],
                            "folder": t["folder"]} for t in techniques]}


def gate_text(g: dict) -> str:
    if g["passed"]:
        return "đạt"
    parts = []
    if g["new_failure_runs"]:
        parts.append(f"{g['new_failure_runs']} lần chạy trượt mới")
    if g["lcc_runs_lost"]:
        parts.append(f"LCC lái ít hơn mốc ở {g['lcc_runs_lost']} lần chạy, tới {g['lcc_cycles_lost_max']} chu kỳ")
    if g["b0"] == "trượt C1 hoặc C2":
        parts.append("trượt B0")
    return "loại: " + "; ".join(parts)


def elimination_reason(name: str, g: dict) -> str:
    reqs = ", ".join(f"{k} ({v})" for k, v in list(g["requirements"].items())[:8])
    text = f"**{name} bị loại ở bước 1.**"
    if reqs:
        text += f" Trượt mới so với mốc: {reqs}. Profile có trượt mới: {', '.join(g['profiles']) or '—'}."
    if g["lcc_runs_lost"]:
        worst = max(g["lcc_lost"], key=lambda x: x["lost"])
        text += (f" LCC lái ít hơn mốc ở {g['lcc_runs_lost']} lần chạy; nhiều nhất {worst['lost']} chu kỳ "
                 f"({worst['case']}, seed {worst['seed']}).")
    return text


def markdown(c: dict) -> list[str]:
    names = [t["name"] for t in c["techniques"]]
    lines = ["# So sánh kỹ thuật", "",
             f"Mục 9.1 của Software Qualification Test Specification. Mốc: {c['baseline']}. {c['runs']} lần chạy "
             "mỗi kỹ thuật, cùng bộ ca, profile và seed. Thời gian tính đo trên máy chạy SIL, chỉ để so các kỹ thuật.",
             "", "| Kỹ thuật | Bước 1: cửa loại | " + " | ".join(f"Bước {i + 2}: {g}" for i, g in enumerate(STEPS))
             + " | Xếp hạng |", "|---|---|" + "---|" * len(STEPS) + "---|"]
    for name in names:
        row = c["rows"][name]
        cells = [str(row["copeland"][g]) if "copeland" in row else "—" for g in STEPS]
        place = str(c["order"].index(name) + 1) if name in c["order"] else "loại"
        lines.append(f"| {name} | {gate_text(row['gate'])} | " + " | ".join(cells) + f" | {place} |")
    for name in c["eliminated"]:
        lines += ["", elimination_reason(name, c["rows"][name]["gate"])]
    lines += ["", "## Bảng tổng", "", "Giá trị xấu nhất của mỗi performance target qua mọi seed (mục 10).", "",
              "| Performance target | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    targets = sorted({k for v in c["absolute"].values() for k in v})
    for key in targets:
        cells = [compare._f(c["absolute"][n].get(key, {}).get("worst")) for n in names]
        lines.append(f"| {key} | " + " | ".join(cells) + " |")
    if not c["eliminated"]:
        lines += ["", "Chưa có kỹ thuật nào bị loại; báo cáo cần ít nhất một kỹ thuật bị loại kèm số liệu (mục 9.1)."]
    return lines


# ---------------------------------------------------------------- kết quả của eval.study

def _plain(spec: list) -> list:
    return [x for x in spec if not isinstance(x, dict)]


def matches(spec: list, pattern: list) -> bool:
    """[S1, f]: ca S1 biến thể f không lỗi; [S12]: cả họ; [F01] hoặc [F01, c]: mọi lần chạy có lỗi đó;
    [S1, c, F01, c]: đúng tổ hợp. Khóa mô phỏng (profile, acc...) không xét.
    """
    spec = _plain(spec)
    family, rest = spec[0], spec[1:]
    fault, level = (rest[1], rest[2]) if len(rest) >= 3 else (None, None)
    head = str(pattern[0])
    if head.startswith("F"):
        return fault == head and (len(pattern) < 2 or level == pattern[1])
    if family != head:
        return False
    if len(pattern) == 1:
        return True
    if rest[0] != pattern[1]:
        return False
    if len(pattern) == 2:
        return fault is None
    return fault == pattern[2] and (len(pattern) < 4 or level == pattern[3])


def _record(row: dict) -> tuple[dict, dict]:
    spec = row.get("spec") or []
    plain, sim = _plain(spec), next((x for x in spec if isinstance(x, dict)), {})
    case = {"id": row["run"], "family": plain[0] if plain else row["run"],
            "parameters": {"variant": plain[1] if len(plain) > 1 else None,
                           "fault": plain[2:4] or None, **sim, "profile": row.get("profile")}}
    info = {k: row.get(k) for k in ("lcc_driving_cycles", "lcc_requested_cycles", "path_near_limit_share",
                                    "hwa_share_after_request")}
    info.update(row.get("vehicle") or {})
    record = {"case": row["run"], "seed": row["seed"], "profile": row.get("profile"), "scope": None,
              "failed": list(row.get("failed") or []), "spec": spec, "loop": row.get("loop"),
              "compute_lcc_ms": row.get("compute_lcc_ms") or {}, "open_loop_file": row.get("open_loop_file"),
              "result": {"criteria": row.get("criteria") or [], "targets": row.get("targets") or [],
                         "issues": row.get("issues") or [], "case_failures": row.get("case_failures") or [],
                         "info": info}}
    return case, record


def _lcc_library(manifest: dict, build: str) -> dict:
    build_dir = Path(build).resolve()
    for info in manifest.get("libraries", []):
        path = (ROOT / info["path"]).resolve()
        if path.parent == build_dir and info.get("family", "lcc") == "lcc" and "lkaelk" not in path.name:
            return info
    return {}


def load_study(folder: Path, plan: dict, part: str) -> list[dict]:
    folder = Path(folder)
    results = json.loads((folder / "results.json").read_text(encoding="utf-8"))
    manifest_path = folder / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
    out = []
    for entry in results:
        if entry["part"] != part:
            continue
        cases, records = {}, {}
        for row in entry["runs"]:
            case, record = _record(row)
            cases[case["id"]] = case
            records[(row["run"], row["seed"])] = record
        lib = _lcc_library(manifest, entry["library"])
        b0_path = folder / "conformance" / f"{entry['set']}.json"
        variant = plan["variants"].get(entry["set"], {})
        out.append({"folder": str(folder / entry["set"]), "name": entry["set"],
                    "pp_version": lib.get("pp_version"), "sha256": lib.get("sha256"),
                    "state_size_bytes": lib.get("state_size_bytes"), "file_size_bytes": lib.get("file_size_bytes"),
                    "b0": json.loads(b0_path.read_text(encoding="utf-8")) if b0_path.is_file() else None,
                    "generation_sha256": f"{plan['suite']}:{part}", "partial": False,
                    "cases": cases, "records": records, "calibration": entry.get("values") or {},
                    "ranked": variant.get("ranked", True), "description": variant.get("description", "")})
    return out


def _units(p: dict, patterns: list | None) -> set | None:
    if not patterns:
        return None
    return {k for k, r in p["records"].items() if any(matches(r["spec"], pat) for pat in patterns)}


def _metrics_of(techniques: list[dict], target: str) -> list[tuple[str, str]]:
    seen = set()
    for t in techniques:
        for r in t["records"].values():
            seen |= {m for m in compare._targets(r) if m[0] == target}
    return sorted(seen)


def metric_diff(a: dict, b: dict, metric: tuple[str, str], units: set | None = None) -> dict:
    """Hiệu theo hướng có lợi cho A, kèm khoảng tin cậy, dung sai, kết quả và đơn vị xấu nhất."""
    diff, common, level_a, level_b = compare.paired_diff(a, b, metric, units=units)
    out = compare.verdict(diff, compare.tolerance(metric, level_a, level_b))
    if len(diff):
        k = int(np.argmin(diff))
        out["worst"] = {"case": common[k][0], "seed": common[k][1], "diff": float(diff[k])}
    return out


def ranked_metrics(techniques: list[dict]) -> list[tuple[str, tuple[str, str]]]:
    groups = compare.group_metrics(techniques)
    return [(g, m) for g in (compare.SAFETY, compare.LANE_KEEPING, compare.COMPUTE) for m in groups[g]]


def _median(values) -> float | None:
    values = [v for v in values if v is not None and math.isfinite(v)]
    return float(np.median(values)) if values else None


def _p99s(p: dict) -> dict:
    return {k: r["compute_lcc_ms"].get("p99") for k, r in p["records"].items() if r["compute_lcc_ms"].get("p99")}


def p99_ratio(a: dict, b: dict) -> float | None:
    pa, pb = _p99s(a), _p99s(b)
    return _median([pa[k] / pb[k] for k in set(pa) & set(pb) if pb[k] > 0])


def _new_failures(name: str, gates: dict) -> bool:
    g = gates.get(name)
    return g is None or bool(g["new_failure_runs"])


def _diff_text(d: dict | None) -> str:
    if not d or d.get("max_m") is None:
        return "—"
    return f"lớn nhất {d['max_m']:.4f} m, TB {d['mean_m']:.4f} m"


def hypothesis(h: dict, by_name: dict, gates: dict, diffs: dict | None, part: str) -> list[dict]:
    """Một dòng mỗi biến thể hoặc mỗi cặp. holds: True, False hoặc None (thiếu dữ liệu)."""
    kind, rows = h["kind"], []
    if kind == "paired":
        base = by_name.get(h["against"])
        for v in h["variants"]:
            p = by_name.get(v)
            if p is None or base is None:
                rows.append({"variant": v, "holds": None, "text": MISSING})
                continue
            units = _units(p, h.get("cases"))
            texts, ok = [], True
            primary = _metrics_of([p, base], h["primary"]["target"])
            if not primary:
                rows.append({"variant": v, "holds": None, "text": f"{MISSING}: không có {h['primary']['target']}"})
                continue
            for metric in primary:
                d = metric_diff(p, base, metric, units)
                good = (d["note"] is None and d["mean"] >= h["primary"]["improve_at_least"] and d["ci"][0] > 0)
                ok &= good
                texts.append(f"{metric[0]}: giảm {compare._f(d['mean'])} {compare.ci_text(d)}, n = {d['units']}")
            for guard in h.get("guards", []):
                for metric in _metrics_of([p, base], guard["target"]):
                    d = metric_diff(p, base, metric, units)
                    good = d["mean"] is not None and -d["mean"] <= guard["worsen_at_most"]
                    ok &= good
                    texts.append(f"{metric[0]}: hiệu {compare._f(d['mean'])} (xấu đi tối đa {guard['worsen_at_most']:g})")
            new = _new_failures(v, gates)
            texts.append("có trượt mới" if new else "không trượt mới")
            rows.append({"variant": v, "holds": ok and not new, "text": "; ".join(texts)})
    elif kind == "smallest":
        chosen = None
        for v in h["variants"]:
            d = output_diff.lookup(diffs, v, h["reference"], part)
            within = bool(d and d["max_m"] is not None and d["max_m"] <= h["at_most"] and d["valid_mismatch"] == 0)
            ok = within and not _new_failures(v, gates)
            rows.append({"variant": v, "holds": None if d is None else ok,
                         "text": _diff_text(d) + (f"; {d['valid_mismatch']} chu kỳ chỉ một bên có path"
                                                  if d and d["valid_mismatch"] else "")})
            if ok and chosen is None:
                chosen = v
        rows.append({"variant": "Kết luận", "holds": chosen is not None,
                     "text": f"k nhỏ nhất đạt: {chosen}" if chosen else "không có số vòng nào đạt"})
    elif kind == "beats":
        for a, b in h["pairs"]:
            da, db = output_diff.lookup(diffs, a, h["reference"], part), output_diff.lookup(diffs, b, h["reference"], part)
            if not da or not db or da["max_m"] is None or db["max_m"] is None:
                rows.append({"variant": f"{a} so với {b}", "holds": None, "text": MISSING})
                continue
            rows.append({"variant": f"{a} so với {b}", "holds": da["max_m"] <= db["max_m"] - h["better_by"],
                         "text": f"{da['max_m']:.4f} m so với {db['max_m']:.4f} m"})
    elif kind == "cheaper":
        da_ref = output_diff.lookup(diffs, h["against"], h["reference"], part)
        against = by_name.get(h["against"])
        for v in h["variants"]:
            d, p = output_diff.lookup(diffs, v, h["reference"], part), by_name.get(v)
            if not d or not da_ref or p is None or against is None or d["max_m"] is None or da_ref["max_m"] is None:
                rows.append({"variant": v, "holds": None, "text": MISSING})
                continue
            ratio = p99_ratio(p, against)
            ok = d["max_m"] <= da_ref["max_m"] and ratio is not None and ratio <= h["p99_ratio_max"]
            rows.append({"variant": v, "holds": ok,
                         "text": f"lệch {d['max_m']:.4f} m so với {da_ref['max_m']:.4f} m; trung vị tỉ số p99 "
                                 f"{compare._f(ratio)}"})
    elif kind == "copeland":
        against = by_name.get(h["against"])
        for v in h["variants"]:
            p = by_name.get(v)
            if p is None or against is None:
                rows.append({"variant": v, "holds": None, "text": MISSING})
                continue
            metrics = compare.group_metrics([p, against])
            per_group = {g: sum(compare.pairwise(p, against, m, False)["result"] for m in metrics[g])
                         for g in (compare.SAFETY, compare.LANE_KEEPING)}
            ok = any(s > 0 for s in per_group.values()) and all(s >= 0 for s in per_group.values())
            ok &= gates.get(v, {}).get("passed", False)
            rows.append({"variant": v, "holds": ok,
                         "text": "; ".join(f"{g}: {s:+d}" for g, s in per_group.items())})
    else:
        for v in h["variants"]:
            g = gates.get(v)
            rows.append({"variant": v, "holds": None if g is None else g["passed"],
                         "text": MISSING if g is None else gate_text(g)})
    return rows


def _holds_text(v) -> str:
    return {True: "đạt", False: "không đạt", None: MISSING}[v]


def _pareto(points: dict[str, tuple[float, float]]) -> set[str]:
    return {n for n, (x, y) in points.items()
            if not any((x2 <= x and y2 <= y) and (x2 < x or y2 < y) for m, (x2, y2) in points.items() if m != n)}


def _iterations(t: dict, base_cal: dict) -> int | None:
    value = t["calibration"].get("qp_iters")
    if value is None and t["name"].startswith("qp_jerk_admm"):
        value = base_cal.get("qp_iters")
    return None if value is None else int(value)


def _target_mean(p: dict, target: str) -> float | None:
    values = [v for r in p["records"].values() for (rid, _), v in compare._targets(r).items() if rid == target]
    return float(np.mean(values)) if values else None


def _criterion_max(p: dict, rid: str) -> float | None:
    values = [c["value"] for r in p["records"].values() for c in r["result"]["criteria"]
              if c["id"] == rid and c["value"] is not None]
    return max(values) if values else None


def _info(p: dict, key: str) -> list:
    return [r["result"]["info"].get(key) for r in p["records"].values() if r["result"]["info"].get(key) is not None]


def _gap(p: dict, base: dict, tp: dict | None, tbase: dict | None, metrics) -> dict:
    """Chênh tuning và test: chỉ số đổi hướng thắng thua, hoặc thắng ở tuning mà hòa ở test."""
    if tp is None or tbase is None:
        return None
    flipped, lost, measured = [], [], 0
    for _, metric in metrics:
        test_d, tune_d = compare.pairwise(p, base, metric, False), compare.pairwise(tp, tbase, metric, False)
        if test_d["note"] or tune_d["note"]:
            continue
        measured += 1
        if test_d["result"] * tune_d["result"] < 0:
            flipped.append(metric[0])
        elif tune_d["result"] > 0 and test_d["result"] == 0:
            lost.append(metric[0])
    return {"flipped": flipped, "lost": lost, "measured": measured}


def _cell(d: dict) -> str:
    if d["units"] == 0:
        return "—"
    if d["note"]:
        return f"{compare._f(d['mean'])}, n = {d['units']}, {d['note']}"
    mark = {1: " ✓", -1: " ✗", 0: ""}[d["result"]]
    return f"{compare._f(d['mean'])} {compare.ci_text(d)}, n = {d['units']}{mark}"


def study_report(study_id: str, plan_path: Path, folder: Path, part: str = "test") -> tuple[list[str], dict]:
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    techniques = load_study(folder, plan, part)
    tuning = {t["name"]: t for t in load_study(folder, plan, "tuning")} if part != "tuning" else {}
    diffs_path = folder / "output_diff.json"
    diffs = json.loads(diffs_path.read_text(encoding="utf-8")) if diffs_path.is_file() else None
    manifest_path = folder / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
    from eval import sweep
    base_cal = sweep.base_values(["qp_iters"])
    baseline = plan["baseline"]
    by_name = {t["name"]: t for t in techniques}
    ranked = [t for t in techniques if t["ranked"]]
    lost_max = plan.get("gates", {}).get("lcc_cycles_lost_max", LCC_CYCLES_LOST_MAX)
    c = rank(ranked, baseline, lost_max)
    gates = {n: r["gate"] for n, r in c["rows"].items()}
    base = by_name[baseline]
    metrics = ranked_metrics(ranked)
    draft = bool(not plan.get("locked") or manifest.get("git", {}).get("dirty", True)
                 or "research/runs" not in str(Path(folder).resolve()))

    lines = [f"# Kết quả {study_id}", ""]
    if draft:
        lines += ["**Kết quả nháp.** Plan chưa khóa, cây làm việc chưa sạch hoặc lần chạy chưa ghi bằng `--record`; "
                  "không trích trong study hay tài liệu.", ""]
    lines += [f"- Plan: `{plan_path.relative_to(ROOT) if plan_path.is_relative_to(ROOT) else plan_path}`, "
              f"khóa {plan.get('locked') or 'chưa'}; suite {plan['suite']}, phần {part}; "
              f"run ID {manifest.get('run_id', '—')}.",
              f"- Mốc: `{baseline}`. Xếp hạng theo Software Qualification Test Specification 9.1; thắng, thua, "
              "hòa và dung sai theo 9.2. Mỗi lần chạy là một đơn vị ghép cặp (ca, profile, seed).",
              f"- {c['runs']} lần chạy mỗi generator. Thời gian tính đo trên máy chạy SIL, chỉ để so các generator.", ""]

    # Bảng 1
    lines += ["## 1. Kết luận và xếp hạng", "",
              "| Hạng | Generator | pp_version | B0 | Trượt mới so với mốc | LCC lái ít hơn mốc | "
              + " | ".join(STEPS) + " |", "|---|---|---|---|---|---|" + "---|" * len(STEPS)]
    for t in sorted(ranked, key=lambda t: (c["order"].index(t["name"]) if t["name"] in c["order"] else 999, t["name"])):
        g, row = gates[t["name"]], c["rows"][t["name"]]
        place = str(c["order"].index(t["name"]) + 1) if t["name"] in c["order"] else "loại"
        lost = f"{g['lcc_runs_lost']} lần, tới {g['lcc_cycles_lost_max']} chu kỳ" if g["lcc_runs_lost"] else "không"
        cells = [str(row["copeland"][s]) if "copeland" in row else "—" for s in STEPS]
        lines.append(f"| {place} | `{t['name']}` | {t['pp_version'] or '—'} | {g['b0']} | {g['new_failure_runs']} | "
                     f"{lost} | " + " | ".join(cells) + " |")
    for name in c["eliminated"]:
        lines += ["", elimination_reason(name, gates[name])]
    shared = gates[baseline]["shared"]
    lines += ["", "Trượt chung với mốc (vẫn tính vào kết luận khi giao): "
              + (", ".join(f"{k} ({v})" for k, v in shared.items()) or "không") + "."]
    unmeasured = sorted(n for n, g in gates.items() if g["lcc_unmeasured_runs"])
    if unmeasured:
        lines += ["", "Chưa đo được thời gian LCC lái ở một số lần chạy: " + ", ".join(unmeasured) + "."]

    # Bảng 2
    groups = plan.get("case_groups") or {}
    lines += ["", f"## 2. Hiệu ghép cặp so với `{baseline}`", "",
              "Hiệu dương: generator tốt hơn mốc. Ô ghi trung bình [khoảng tin cậy 95 %], n; ✓ thắng, ✗ thua theo "
              "luật của mục 9.2. Chỉ generator qua cửa loại.", "",
              "| Generator | Chỉ số | Dung sai | Tất cả | " + " | ".join(groups) + " | Lần chạy xấu nhất |",
              "|---|---|---|---|" + "---|" * len(groups) + "---|"]
    for name in c["order"]:
        if name == baseline:
            continue
        p = by_name[name]
        for _, metric in metrics:
            overall = metric_diff(p, base, metric)
            if overall["units"] == 0:
                continue
            cells = [_cell(metric_diff(p, base, metric, _units(p, pats))) for pats in groups.values()]
            worst = overall.get("worst")
            worst_text = f"{worst['case']}, seed {worst['seed']}: {compare._f(worst['diff'])}" if worst else "—"
            lines.append(f"| `{name}` | {metric[0]} {metric[1]} | {compare._f(overall['tolerance'])} | "
                         f"{_cell(overall)} | " + " | ".join(cells) + f" | {worst_text} |")

    # Bảng 3
    lines += ["", "## 3. Giả thuyết", "", "| Giả thuyết | Generator | Kết quả | Số liệu |", "|---|---|---|---|"]
    for h in plan.get("hypotheses", []):
        for row in hypothesis(h, by_name, gates, diffs, part):
            lines.append(f"| {h['id']} | {row['variant']} | {_holds_text(row['holds'])} | {row['text']} |")
    if diffs is None:
        lines += ["", "Chưa có `output_diff.json` (lần chạy không có lượt vòng hở hoặc thiếu nghiệm tham chiếu)."]

    # Bảng 4
    reference = next((h["reference"] for h in plan.get("hypotheses", []) if h.get("reference")), None)
    qp = [t for t in techniques if _iterations(t, base_cal) is not None]
    lines += ["", "## 4. Số vòng QP", "",
              f"Lệch output so với `{reference}` ở vòng hở, 0–1 s. Pareto: không generator nào vừa nhanh hơn vừa lệch ít hơn.", "",
              "| Generator | Số vòng | p99 [ms] | % chu kỳ 25 ms | Lệch so với nghiệm tham chiếu | a_y xe TB (068) | "
              "Jerk xe TB (069) | Trượt mới | Pareto |", "|---|---|---|---|---|---|---|---|---|"]
    points = {}
    for t in qp:
        d = output_diff.lookup(diffs, t["name"], reference, part) if reference else None
        p99 = _median(_p99s(t).values())
        if p99 is not None and d and d["max_m"] is not None:
            points[t["name"]] = (p99, d["max_m"])
    front = _pareto(points)
    for t in sorted(qp, key=lambda t: (_iterations(t, base_cal), t["name"])):
        d = output_diff.lookup(diffs, t["name"], reference, part) if reference else None
        p99 = _median(_p99s(t).values())
        new = gates[t["name"]]["new_failure_runs"] if t["name"] in gates else "—"
        lines.append(f"| `{t['name']}` | {_iterations(t, base_cal)} | {compare._f(p99)} | "
                     f"{compare._f(None if p99 is None else 100 * p99 / CYCLE_MS)} | {_diff_text(d)} | "
                     f"{compare._f(_target_mean(t, 'PP-SWR-068'))} | {compare._f(_target_mean(t, 'PP-SWR-069'))} | "
                     f"{new} | {'có' if t['name'] in front else ''} |")

    # Bảng 5
    lines += ["", "## 5. Chi phí vận hành", "",
              "Thời gian CPU của `pp_lcc_step` qua adapter SIL; trung vị qua lần chạy của p99 từng lần. Không xếp hạng "
              "trừ p99 (bước 5).", "",
              "| Generator | p99 trung vị [ms] | % chu kỳ 25 ms | p99 lớn nhất [ms] | Thời gian lớn nhất [ms] | "
              "State [byte] | Thư viện [byte] | Khối lượng việc mỗi chu kỳ |", "|---|---|---|---|---|---|---|---|"]
    for t in techniques:
        p99s = list(_p99s(t).values())
        maxima = [r["compute_lcc_ms"].get("max") for r in t["records"].values() if r["compute_lcc_ms"].get("max")]
        p99 = _median(p99s)
        lines.append(f"| `{t['name']}` | {compare._f(p99)} | {compare._f(None if p99 is None else 100 * p99 / CYCLE_MS)} | "
                     f"{compare._f(max(p99s) if p99s else None)} | {compare._f(max(maxima) if maxima else None)} | "
                     f"{t['state_size_bytes'] or '—'} | {t['file_size_bytes'] or '—'} | chưa có telemetry |")

    # Bảng 6
    lines += ["", "## 6. Độ tin", "",
              f"Vòng hở so với `{baseline}`: chỉ so chu kỳ có digest đầu vào trùng nhau. Path khác mốc khi lệch lớn nhất "
              f"0–1 s > {output_diff.DIFFERS_M:g} m. Chênh tuning và test: chỉ số đổi hướng thắng thua, hoặc thắng ở "
              "tuning mà hòa ở test.", "",
              "| Generator | Chu kỳ so được | Digest lệch | Chỉ một bên có path | Tỉ lệ chu kỳ path khác mốc | "
              "Chỉ số ít dữ liệu | Đổi hướng tuning và test | Thắng ở tuning, hòa ở test |",
              "|---|---|---|---|---|---|---|---|"]
    for t in ranked:
        d = output_diff.lookup(diffs, t["name"], baseline, part) if t["name"] != baseline else None
        few = sum(1 for _, m in metrics if compare.pairwise(t, base, m, False)["note"]) if t["name"] != baseline else 0
        gap = _gap(t, base, tuning.get(t["name"]), tuning.get(baseline), metrics) if t["name"] != baseline else None
        flipped = "—" if gap is None else ", ".join(gap["flipped"]) or "không"
        lost = "—" if gap is None else ", ".join(gap["lost"]) or "không"
        lines.append(f"| `{t['name']}` | {d['compared'] if d else '—'} | {d['digest_mismatch'] if d else '—'} | "
                     f"{d['valid_mismatch'] if d else '—'} | {compare._f(d['differs_share']) if d else '—'} | {few} | "
                     f"{flipped} | {lost} |")

    # Bảng 7
    lines += ["", "## 7. Chẩn đoán (không xếp hạng)", "",
              "| Generator | Jerk path lớn nhất (003) [m/s³] | Tỉ lệ chu kỳ path gần trần a_y hoặc jerk, TB / lớn nhất | "
              "a_y xe trên aysmax + 0,3 lâu nhất [s] | Lần chạy ngoài giới hạn R79 5.6.2.1.1 | PP-SWR-125 lớn nhất | Telemetry |",
              "|---|---|---|---|---|---|---|"]
    for t in techniques:
        near = _info(t, "path_near_limit_share")
        over = _info(t, "ay_vehicle_r79_over_sustained_s")
        outside = sum(1 for v in _info(t, "ay_vehicle_r79_within_limits") if v is False)
        f06 = [v for r in t["records"].values() for (rid, _), v in compare._targets(r).items() if rid == "PP-SWR-125"]
        lines.append(f"| `{t['name']}` | {compare._f(_criterion_max(t, 'PP-SWR-003'))} | "
                     f"{compare._f(float(np.mean(near)) if near else None)} / {compare._f(max(near) if near else None)} | "
                     f"{compare._f(max(over) if over else None)} | {outside} | {compare._f(max(f06) if f06 else None)} | "
                     "chưa có |")

    # Bảng 8
    profiles = sorted({r.get("profile") for t in ranked for r in t["records"].values() if r.get("profile")})
    lines += ["", "## 8. Flexibility", "",
              "Giá trị xấu nhất của mỗi chỉ số theo profile, qua mọi lần chạy có profile đó. Điểm thắng cặp của nhóm "
              "Flexibility ở bảng 1 so độ chênh giữa các profile.", "",
              "| Generator | Chỉ số | " + " | ".join(profiles) + " |", "|---|---|" + "---|" * len(profiles)]
    for t in ranked:
        for group, metric in metrics:
            if group == compare.COMPUTE:
                continue
            worst = {}
            for r in t["records"].values():
                v = compare._targets(r).get(metric)
                if v is None:
                    continue
                pick = min if metric[0] in compare.LARGER_IS_BETTER else max
                worst[r["profile"]] = pick(worst.get(r["profile"], v), v)
            if worst:
                lines.append(f"| `{t['name']}` | {metric[0]} {metric[1]} | "
                             + " | ".join(compare._f(worst.get(pr)) for pr in profiles) + " |")
    return lines, {**c, "hypotheses": {h["id"]: hypothesis(h, by_name, gates, diffs, part)
                                       for h in plan.get("hypotheses", [])}}


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Technique comparison within one planner (Software Qualification Test Specification "
            "9.1, 10)."
        ),
    )
    parser.add_argument("folders", nargs="*", type=Path, help="eval.suite output folders, one per technique")
    parser.add_argument("--name", action="append", help="Technique name per folder, in order")
    parser.add_argument("--baseline", help="Name of the delivered technique (step 1a, 1b)")
    parser.add_argument("--study", help="Trade study id; reads the eval.study output instead of folders")
    parser.add_argument("--results", type=Path, help="eval.study output folder (default build/study/<id>)")
    parser.add_argument("--part", default="test", choices=("tuning", "test"))
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.study:
        from eval import study
        plan_path = study.find_plan(args.study)
        plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
        folder = args.results or STUDY_DIR / args.study
        lines, data = study_report(args.study, plan_path, folder, args.part)
        out = args.out or (ROOT / plan["report"] if plan.get("report") else OUT_DIR / args.study / "RESULTS.md")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        json_dir = OUT_DIR / args.study
        json_dir.mkdir(parents=True, exist_ok=True)
        (json_dir / "techniques.json").write_text(json.dumps(data, indent=1, ensure_ascii=False, default=report.jsonable)
                                                  + "\n", encoding="utf-8")
        print(f"{out}")
        return
    if len(args.folders) < 2:
        parser.error("compare at least two techniques, or use --study")
    if not args.baseline:
        parser.error("--baseline names the delivered technique (Software Qualification Test Specification 9.1, 1a)")
    if args.name and len(args.name) != len(args.folders):
        parser.error("one --name per folder")
    names = args.name or [None] * len(args.folders)
    techniques = [compare.load(f, n) for f, n in zip(args.folders, names)]
    if len({t["name"] for t in techniques}) != len(techniques):
        parser.error("technique names must differ; use --name")
    c = rank(techniques, args.baseline)
    out = args.out or OUT_DIR / "-".join(t["name"] for t in techniques)
    out.mkdir(parents=True, exist_ok=True)
    (out / "techniques.json").write_text(json.dumps(c, indent=1, ensure_ascii=False, default=report.jsonable) + "\n",
                                         encoding="utf-8")
    (out / "report.md").write_text("\n".join(markdown(c)) + "\n", encoding="utf-8")
    print("\n".join(markdown(c)[:6 + len(techniques)]))
    print(f"\n{out / 'report.md'}")


if __name__ == "__main__":
    main()

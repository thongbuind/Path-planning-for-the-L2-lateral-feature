"""Comparison between planners (Software Qualification Test Specification 9.2, 10).

    python3 -m eval.suite build/concrete/regression/manifest.json --planner A.so --out build/suites/reg-A
    python3 -m eval.suite build/concrete/regression/manifest.json --planner B.so --out build/suites/reg-B
    python3 -m eval.compare build/suites/reg-A build/suites/reg-B [--name A --name B] [--out DIR]

Inputs are eval.suite output folders of the same generated suite: same cases, profiles and
seeds, every run executed. No planner is a reference; planners are only compared with each
other. A planner that failed C1 or C2 is not compared. Ranking, tier after tier:
  1  conclusion of 8.4 (no blocker, not approved, blocked); within Blocked fewer BLOCKER
     requirements failed ranks higher
  2  Euro NCAP LSS points (min over profiles), then mean pass rate of MAJOR and MINOR
     requirements
  3  Copeland score of pairwise wins per group of 9.1 steps 2 to 5, a group only when the
     earlier ones tie; a win needs the 95 % bootstrap interval (10 000 resamples over the
     runs, fixed seed) of the mean difference wholly on one side
Writes build/compare/<name>/report.md and compare.json.
"""

import argparse
import json
import math
import re
from itertools import combinations
from pathlib import Path

import numpy as np

from eval import conclusion, matrix, report, severity
from eval.suite import SCOPE

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "build" / "compare"
BOOTSTRAP_RESAMPLES = 10_000  # Software Qualification Test Specification 9.2
BOOTSTRAP_SEED = 20261112  # fixed (nhóm tự thống nhất)
CONFIDENCE = 0.95

# Euro NCAP Assessment Protocol SA v10.4.1, 4.3.2 and 4.3.3.6 (Software Qualification Test
# Specification 9.2): test line -> (family, description prefix after "Euro NCAP LSS ", points).
NCAP_LINES = {
    "LKA, vạch đứt": ("S4", "dashed-", 0.25),
    "LKA, vạch liền": ("S4", "solid-", 0.25),
    "ELK, chỉ mép đường": ("S6", "edge-right", 0.25),
    "ELK, vạch giữa đứt và không có vạch sát mép đường": ("S6", "edge-dashed-", 0.25),
    "ELK, vạch liền": ("S5", "solid-", 0.50),
    "ELK, xe ngược chiều": ("S7", "oncoming-", 0.50),
    "ELK, xe đang vượt": ("S8", ("overtaking-", "indicated-"), 0.50),
}
NCAP_MAX = sum(points for _, _, points in NCAP_LINES.values())
# Criteria of the protocol for a row (Software Qualification Test Specification 5.1).
NCAP_DTLE = "PP-SWR-086"

# Groups of 9.1 steps 2 to 5: performance targets by id; the flexibility group uses the
# targets of the safety and comfort groups, as the spread between profiles.
GROUPS = {
    "An toàn": ("PP-SWR-050", "PP-SWR-057", "PP-SWR-087"),
    "Cảm nhận người lái": ("PP-SWR-002", "PP-SWR-004", "PP-SWR-053", "PP-SWR-059", "PP-SWR-081", "PP-SWR-082"),
    "Flexibility": (),
    "Thời gian tính": ("PP-SWR-016",),
}
LARGER_IS_BETTER = {"PP-SWR-057", "PP-SWR-064", "PP-SWR-087"}  # 8.2 "Tốt hơn khi"


# ---- loading ---------------------------------------------------------------------------

def _scope(case: dict) -> list[str]:
    if "scope_keys" in case:
        return sorted(set().union(*(matrix.scope(SCOPE, k) for k in case["scope_keys"])))
    family, anchor = case["family"], case["anchor"] or "a"
    spec = ["S1", "a", family, anchor] if family.startswith("F") else [family, anchor]
    return sorted(matrix.scope(SCOPE, spec))


def load(folder: Path, name: str | None = None) -> dict:
    """One eval.suite output folder: planner, B0, generation, run records keyed by (case, seed)."""
    folder = Path(folder)
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    generation = json.loads((folder / "generation.json").read_text(encoding="utf-8"))
    cases = {c["id"]: c for c in generation["cases"]}
    b0_path = folder / "conformance.json"
    b0 = json.loads(b0_path.read_text(encoding="utf-8")) if b0_path.is_file() else None
    records = {}
    for line in (folder / "results.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        case = cases[r["case"]]
        r.setdefault("profile", case["parameters"].get("profile"))
        if "scope" not in r:  # written before eval.suite kept the scope
            r["scope"] = _scope(case)
        records[(r["case"], r["seed"])] = r
    lib = manifest["libraries"][0]
    return {"folder": str(folder), "name": name or lib.get("pp_version") or folder.name,
            "pp_version": lib.get("pp_version"), "sha256": lib.get("sha256"), "b0": b0,
            "generation_sha256": manifest.get("generation", {}).get("sha256"),
            "partial": manifest.get("summary", {}).get("partial", False),
            "cases": cases, "records": records}


def check_same_benchmark(planners: list[dict]) -> None:
    first = planners[0]
    for p in planners[1:]:
        if p["generation_sha256"] != first["generation_sha256"]:
            raise SystemExit(f"{p['folder']}: another generated suite than {first['folder']}")
        if set(p["records"]) != set(first["records"]):
            raise SystemExit(f"{p['folder']}: other runs (case, seed) than {first['folder']}")
    partial = [p["folder"] for p in planners if p["partial"]]
    if partial:
        raise SystemExit("partial suite runs cannot be compared: " + ", ".join(partial))


# ---- tier 1 and 2 ----------------------------------------------------------------------

def tier1(p: dict) -> dict:
    c = conclusion.conclude(list(p["records"].values()), p["b0"])
    blocker_reqs = sorted({f["requirement"] for f in c["failures"] if f["level"] == severity.BLOCKER})
    rank = {conclusion.NO_BLOCKER: 0, conclusion.NOT_APPROVED: 1, conclusion.BLOCKED: 2}[c["verdict"]]
    return {"verdict": c["verdict"], "rank": rank, "blocker_requirements": blocker_reqs,
            "counts": c["counts"], "integrable": c["integrable"]}


def _ncap_line(case: dict) -> str | None:
    params = case["parameters"]
    text = str(params.get("description", ""))
    if params.get("protocol") != "Euro NCAP LSS" or not text.startswith("Euro NCAP LSS "):
        return None
    rest = text.removeprefix("Euro NCAP LSS ")
    for line, (family, prefixes, _) in NCAP_LINES.items():
        prefixes = prefixes if isinstance(prefixes, tuple) else (prefixes,)
        if case["family"] == family and any(rest.startswith(x) for x in prefixes):
            return line
    return None


def _ncap_row_passed(record: dict) -> bool:
    if record.get("execution") or record.get("error") or record.get("result") is None:
        return False
    result = record["result"]
    criteria = {c["id"]: c for c in result["criteria"] if c["applicable"]}
    issues = result.get("issues")
    planner_issues = ([i for i in issues if i["kind"] != "not_judged"] if issues is not None
                      else [{"text": t} for t in result.get("case_failures", [])])
    if planner_issues:
        return False  # e.g. requested intervention not driven
    family_target = record.get("_family")
    if family_target in ("S7", "S8"):
        return result.get("info", {}).get("no_impact") is True  # SA 4.3.3.4: no impact
    dtle = criteria.get(NCAP_DTLE)
    return dtle is not None and dtle["passed"]


def ncap_points(p: dict) -> dict:
    """Per profile: a line scores when every grid row of it passes (every seed); min over profiles."""
    rows: dict[tuple[str, str], list[bool]] = {}
    for (case_id, _), record in p["records"].items():
        case = p["cases"][case_id]
        line = _ncap_line(case)
        if line is None:
            continue
        record = {**record, "_family": case["family"]}
        rows.setdefault((record["profile"], line), []).append(_ncap_row_passed(record))
    profiles = sorted({profile for profile, _ in rows})
    per_profile = {}
    for profile in profiles:
        lines = {line: (all(rows[(profile, line)]) if (profile, line) in rows else None) for line in NCAP_LINES}
        per_profile[profile] = {"lines": lines,
                                "points": sum(NCAP_LINES[l][2] for l, ok in lines.items() if ok)}
    missing = sorted({l for prof in per_profile.values() for l, ok in prof["lines"].items() if ok is None})
    return {"points": min((v["points"] for v in per_profile.values()), default=None),
            "max": NCAP_MAX, "per_profile": per_profile, "lines_without_rows": missing}


def pass_rate(p: dict) -> dict:
    """Per MAJOR or MINOR requirement: runs passed / runs judging it (in scope); mean, unweighted."""
    judged: dict[str, list[bool]] = {}
    for record in p["records"].values():
        if record.get("result") is None:
            continue
        scope = set(record["scope"]) if record.get("scope") is not None else None
        for c in record["result"]["criteria"]:
            if not c["applicable"] or (scope is not None and c["id"] not in scope):
                continue
            if severity.level(c["id"]) in (severity.MAJOR, severity.MINOR):
                judged.setdefault(c["id"], []).append(bool(c["passed"]))
    rates = {rid: sum(v) / len(v) for rid, v in sorted(judged.items())}
    return {"mean": float(np.mean(list(rates.values()))) if rates else None, "per_requirement": rates}


# ---- tier 3 ----------------------------------------------------------------------------

def _targets(record: dict) -> dict[tuple[str, str], float]:
    if record.get("result") is None:
        return {}
    return {(t["id"], t["metric"]): float(t["value"]) for t in record["result"]["targets"]
            if t["value"] is not None and math.isfinite(float(t["value"]))}


def _units(p: dict, metric: tuple[str, str], flexibility: bool) -> dict:
    """unit -> value; a unit is a run, or for flexibility (case without profile, seed) -> spread."""
    if not flexibility:
        return {k: v for k, r in p["records"].items() if (v := _targets(r).get(metric)) is not None}
    by_unit: dict[tuple, list[float]] = {}
    for (case_id, seed), record in p["records"].items():
        case = p["cases"][case_id]
        params = {k: v for k, v in case["parameters"].items() if k != "profile"}
        key = (case["family"], json.dumps(params, sort_keys=True, default=str), seed)
        value = _targets(record).get(metric)
        if value is not None:
            by_unit.setdefault(key, []).append(value)
    return {k: max(v) - min(v) for k, v in by_unit.items() if len(v) >= 2}


_INDEX_CACHE: dict[int, np.ndarray] = {}


def bootstrap_interval(diff: np.ndarray) -> tuple[float, float]:
    n = len(diff)
    if n not in _INDEX_CACHE:
        _INDEX_CACHE[n] = np.random.default_rng(BOOTSTRAP_SEED).integers(0, n, size=(BOOTSTRAP_RESAMPLES, n))
    means = diff[_INDEX_CACHE[n]].mean(axis=1)
    tail = (1.0 - CONFIDENCE) / 2 * 100
    lo, hi = np.percentile(means, [tail, 100 - tail])
    return float(lo), float(hi)


def pairwise(a: dict, b: dict, metric: tuple[str, str], flexibility: bool) -> dict:
    """Result for A against B: +1 A wins, -1 B wins, 0 tie; difference oriented "A better > 0"."""
    ua, ub = _units(a, metric, flexibility), _units(b, metric, flexibility)
    common = sorted(set(ua) & set(ub), key=str)
    larger = metric[0] in LARGER_IS_BETTER and not flexibility  # a spread is always better small
    diff = np.array([(ua[k] - ub[k]) if larger else (ub[k] - ua[k]) for k in common], dtype=float)
    if len(diff) < 2:
        return {"units": len(diff), "mean": float(diff.mean()) if len(diff) else None, "ci": None, "result": 0}
    lo, hi = bootstrap_interval(diff)
    return {"units": len(diff), "mean": float(diff.mean()), "ci": [lo, hi],
            "result": 1 if lo > 0 else -1 if hi < 0 else 0}


def group_metrics(planners: list[dict]) -> dict[str, list[tuple[str, str]]]:
    seen = set()
    for p in planners:
        for r in p["records"].values():
            seen |= set(_targets(r))
    out = {}
    for group, ids in GROUPS.items():
        source = GROUPS["An toàn"] + GROUPS["Cảm nhận người lái"] if group == "Flexibility" else ids
        out[group] = sorted(m for m in seen if m[0] in source)
    return out


def copeland(planners: list[dict]) -> tuple[dict, list[dict]]:
    """Score per planner and group (wins - losses), and every pairwise result."""
    metrics = group_metrics(planners)
    score = {p["name"]: {g: 0 for g in GROUPS} for p in planners}
    duels = []
    for a, b in combinations(planners, 2):
        for group, items in metrics.items():
            for metric in items:
                d = pairwise(a, b, metric, group == "Flexibility")
                score[a["name"]][group] += d["result"]
                score[b["name"]][group] -= d["result"]
                duels.append({"group": group, "metric": list(metric), "a": a["name"], "b": b["name"], **d})
    return score, duels


def absolute_values(planners: list[dict]) -> dict:
    """Mean and worst value of every performance target per planner, over all runs."""
    out = {}
    for p in planners:
        values: dict[tuple[str, str], list[float]] = {}
        for r in p["records"].values():
            for k, v in _targets(r).items():
                values.setdefault(k, []).append(v)
        out[p["name"]] = {f"{k[0]} {k[1]}": {
            "mean": float(np.mean(v)),
            "worst": float(max(v) if k[0] not in LARGER_IS_BETTER else min(v)), "runs": len(v)}
            for k, v in sorted(values.items())}
    return out


# ---- ranking and report ----------------------------------------------------------------

def compare(planners: list[dict]) -> dict:
    check_same_benchmark(planners)
    excluded = [p["name"] for p in planners if p["b0"] is not None and p["b0"]["blocked"]]
    compared = [p for p in planners if p["name"] not in excluded]
    rows = {}
    for p in compared:
        rows[p["name"]] = {"tier1": tier1(p), "ncap": ncap_points(p), "pass_rate": pass_rate(p),
                           "b0": "chưa chạy" if p["b0"] is None else "đạt C1, C2"}
    score, duels = copeland(compared) if len(compared) > 1 else ({p["name"]: {g: 0 for g in GROUPS}
                                                                  for p in compared}, [])
    for name in rows:
        rows[name]["copeland"] = score[name]

    def key(name):
        r = rows[name]
        t1 = r["tier1"]
        return ((t1["rank"], len(t1["blocker_requirements"]) if t1["rank"] == 2 else 0),
                (-(r["ncap"]["points"] or 0.0), -(r["pass_rate"]["mean"] or 0.0)),
                tuple(-r["copeland"][g] for g in GROUPS))

    order = sorted(rows, key=key)
    ranks, previous = {}, None
    for i, name in enumerate(order):
        ranks[name] = ranks[previous] if previous is not None and key(name) == key(previous) else i + 1
        previous = name
    return {"order": order, "ranks": ranks, "rows": rows, "excluded_b0": excluded, "duels": duels,
            "absolute": absolute_values(compared), "planners": [
                {"name": p["name"], "pp_version": p["pp_version"], "sha256": p["sha256"], "folder": p["folder"]}
                for p in planners], "runs": len(planners[0]["records"])}


def _f(v, digits=3):
    if v is None:
        return "—"
    return f"{v:.{digits}g}" if isinstance(v, float) else str(v)


def markdown(c: dict) -> list[str]:
    lines = ["# So sánh planner", "",
             f"- {len(c['planners'])} planner, cùng {c['runs']} lần chạy (ca cụ thể, profile, seed). "
             "Không planner nào làm mốc.",
             "- Xếp theo Software Qualification Test Specification 9.2: kết luận; điểm Euro NCAP rồi tỉ lệ đạt; "
             "điểm thắng cặp từng nhóm."]
    if c["excluded_b0"]:
        lines.append("- Không so (trượt C1 hoặc C2): " + ", ".join(c["excluded_b0"]))
    groups = list(GROUPS)
    lines += ["", "| Hạng | Planner | Kết luận | Requirement BLOCKER trượt | Euro NCAP LSS | Tỉ lệ đạt MAJOR, MINOR | "
              + " | ".join(f"Thắng cặp: {g}" for g in groups) + " |",
              "|---|---|---|---|---|---|" + "---|" * len(groups)]
    for name in c["order"]:
        r = c["rows"][name]
        t1, ncap = r["tier1"], r["ncap"]
        lines.append(f"| {c['ranks'][name]} | {name} | {t1['verdict']} | {len(t1['blocker_requirements'])} | "
                     f"{_f(ncap['points'])} / {ncap['max']:g} | {_f(r['pass_rate']['mean'])} | "
                     + " | ".join(str(r["copeland"][g]) for g in groups) + " |")
    lines += ["", "## Euro NCAP LSS theo profile", "",
              "| Planner | Profile | " + " | ".join(NCAP_LINES) + " | Điểm |",
              "|---|---|" + "---|" * len(NCAP_LINES) + "---|"]
    mark = {True: "đạt", False: "trượt", None: "không có hàng"}
    for name in c["order"]:
        for profile, v in c["rows"][name]["ncap"]["per_profile"].items():
            lines.append(f"| {name} | {profile} | " + " | ".join(mark[v["lines"][l]] for l in NCAP_LINES)
                         + f" | {v['points']:g} |")
    lines += ["", "## Requirement BLOCKER trượt", ""]
    for name in c["order"]:
        lines.append(f"- {name}: " + (", ".join(c["rows"][name]["tier1"]["blocker_requirements"]) or "không"))
    if c["duels"]:
        lines += ["", "## Thắng cặp", "",
                  "Hiệu dương: planner A tốt hơn. Khoảng tin cậy 95 %, bootstrap theo lần chạy.", "",
                  "| Nhóm | Chỉ số | A | B | Số đơn vị | Hiệu trung bình | Khoảng tin cậy | Kết quả |",
                  "|---|---|---|---|---|---|---|---|"]
        verdict = {1: "A thắng", -1: "B thắng", 0: "hòa"}
        for d in c["duels"]:
            ci = "—" if d["ci"] is None else f"[{d['ci'][0]:.3g}, {d['ci'][1]:.3g}]"
            lines.append(f"| {d['group']} | {d['metric'][0]} {d['metric'][1]} | {d['a']} | {d['b']} | {d['units']} | "
                         f"{_f(d['mean'])} | {ci} | {verdict[d['result']]} |")
    lines += ["", "## Giá trị tuyệt đối", "", "| Chỉ số | " + " | ".join(c["order"]) + " |",
              "|---|" + "---|" * len(c["order"])]
    metrics = sorted({m for v in c["absolute"].values() for m in v})
    for m in metrics:
        cells = []
        for name in c["order"]:
            v = c["absolute"][name].get(m)
            cells.append("—" if v is None else f"TB {_f(v['mean'])}, xấu nhất {_f(v['worst'])}")
        lines.append(f"| {m} | " + " | ".join(cells) + " |")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("folders", nargs="+", type=Path, help="eval.suite output folders, one per planner")
    parser.add_argument("--name", action="append", help="Display name per folder, in order")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if len(args.folders) < 2:
        parser.error("give at least two planners")
    if args.name and len(args.name) != len(args.folders):
        parser.error("one --name per folder")
    names = args.name or [None] * len(args.folders)
    planners = [load(f, n) for f, n in zip(args.folders, names)]
    if len({p["name"] for p in planners}) != len(planners):
        for i, p in enumerate(planners):
            p["name"] = f"{p['name']} [{Path(p['folder']).name}]"
    result = compare(planners)
    out = args.out or OUT_DIR / "-vs-".join(Path(f).name for f in args.folders)
    out.mkdir(parents=True, exist_ok=True)
    (out / "compare.json").write_text(json.dumps(result, indent=1, ensure_ascii=False, default=report.jsonable)
                                      + "\n", encoding="utf-8")
    text = "\n".join(markdown(result)) + "\n"
    (out / "report.md").write_text(text, encoding="utf-8")
    print("\n".join(text.splitlines()[:12 + len(result["order"])]))
    print(f"\nReport: {out / 'report.md'}")


if __name__ == "__main__":
    main()

"""Comparison of two suite runs, or of two campaigns (read-only): where did a change make things better or worse.

A side is a suite run (build/benchmark/<id>/suite) or a campaign (workbench.campaign). Each is reduced to
one small record per run: the requirements it failed, the ones it failed outside its scope, its case_hash
and behavior_checksum, and the value and limit of every failed criterion. Two sides are matched by case and
seed (suite) or by configuration (campaign), then each requirement of a matched run is new, fixed or still
failing. A run whose case_hash differs is a different case and is not compared. Before any result the two
sides' environments are listed: a different library or machine is the reason a result differs, and a
different Python, numpy or machine means the checksums are not comparable bit for bit.

Imports no SUT package; knows only the file layout (as workbench.evidence).
"""

import hashlib
import json
import re
from pathlib import Path

from workbench import evidence

LIMIT = re.compile(r"^\s*(<=|>=|<|>|=)\s*(-?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)\s*$")
MAX_ROWS = 400          # changed requirements listed in one answer; the counts always cover all of them
KINDS = ("suite", "campaign")


def margin(value, limit) -> float | None:
    """Distance to the limit, positive when the criterion has room, negative when it fails."""
    m = LIMIT.match(limit or "")
    if m is None or not isinstance(value, (int, float)) or isinstance(value, bool):
        return None
    op, bound = m.group(1), float(m.group(2))
    if op in ("<=", "<"):
        return bound - value
    if op in (">=", ">"):
        return value - bound
    return -abs(value - bound)


def family(case: str) -> str:
    """'S1b-a-VP-0-693b15015bfa' -> 'S1b-a'; 'F02-e-S1a-VP-5-29183b65ffaf' -> 'F02-e'; 'G01-S1c-...' -> 'G01'."""
    parts = case.split("-")
    return "-".join(parts[:2]) if len(parts) > 1 and re.fullmatch(r"[a-z]", parts[1]) else parts[0]


def _record(failed, oos, case_hash, checksum, criteria, label) -> dict:
    values = {}
    for c in criteria:
        if c.get("id") in failed or c.get("id") in oos:
            values.setdefault(c["id"], [c.get("value"), c.get("limit")])
    return {"failed": sorted(failed), "oos": sorted(oos), "case_hash": case_hash, "checksum": checksum,
            "values": values, "label": label}


# ---- suites ------------------------------------------------------------------------------

def _read_suite_runs(path: Path) -> dict:
    runs = {}
    with path.open("rb") as stream:
        for line in stream:
            r = json.loads(line)
            failed = set(r.get("failed") or [])
            if r.get("execution"):
                failed.add("EXECUTION")
            criteria = (r.get("result") or {}).get("criteria") or []
            runs[f"{r.get('case')}|{r.get('seed')}"] = _record(
                failed, set(r.get("failed_out_of_scope") or []), r.get("case_hash"), r.get("behavior_checksum"),
                criteria, f"{r.get('case')} seed {r.get('seed')}")
    return runs


def _environment(manifest: dict) -> dict:
    git = manifest.get("git") or {}
    libs = evidence._libraries(manifest)
    build = [(lib.get("build") or {}).get("calibration") for lib in manifest.get("libraries") or []]
    inputs = manifest.get("inputs") or {}
    return {"libraries": libs, "calibration": build, "commit": git.get("short"), "dirty": bool(git.get("dirty")),
            "environment": manifest.get("environment") or {}, "jobs": manifest.get("jobs"),
            "inputs": hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:12] if inputs else None}


def load_suite(suite_id: str) -> dict:
    if not evidence.SUITE_ID.match(suite_id) or not (evidence.BENCH / suite_id / "suite" / "conclusion.json").is_file():
        raise KeyError(suite_id)
    suite = evidence.BENCH / suite_id / "suite"
    manifest = evidence._read_json(suite / "manifest.json") if (suite / "manifest.json").is_file() else {}
    digest = evidence._cached(suite / "conclusion.json", evidence._digest)
    summary = evidence._read_json(suite / "summary.json") if (suite / "summary.json").is_file() else {}
    runs = evidence._cached(suite / "results.jsonl", _read_suite_runs)
    return {"kind": "suite", "id": suite_id, "target": manifest.get("target"), "finished": manifest.get("finished"),
            "verdict": digest.get("verdict"), "counts": digest.get("counts"), "runs_total": len(runs),
            "planned": summary.get("planned"), "scope": "requirement",
            **_environment(manifest), "runs": runs}


# ---- campaigns ---------------------------------------------------------------------------

def config_key(config: dict) -> str:
    """The identity of one campaign item: its configuration without the pacing."""
    return json.dumps({k: v for k, v in config.items() if k != "rate"}, sort_keys=True, ensure_ascii=False)


def _bundle_record(folder: Path, label: str) -> dict | None:
    if not (folder / "execution.json").is_file():
        return None
    execution = evidence._read_json(folder / "execution.json")
    if execution.get("state") != "COMPLETED" or not (folder / "evaluation.json").is_file():
        return {"failed": ["EXECUTION"], "oos": [], "case_hash": None, "checksum": None, "values": {},
                "label": label, "state": execution.get("state")}
    ev = evidence._read_json(folder / "evaluation.json")
    manifest = evidence._read_json(folder / "manifest.json") if (folder / "manifest.json").is_file() else {}
    bundle = manifest.get("bundle") or {}
    criteria = [c for c in ev.get("criteria") or [] if c.get("applicable")]
    failed = {c["id"] for c in criteria if not c.get("passed")}
    return _record(failed, set(), bundle.get("case_hash"), bundle.get("behavior_checksum"), criteria, label)


def load_campaign(doc: dict, runs_root: Path) -> dict:
    runs, manifest = {}, {}
    for item in doc.get("items") or []:
        rec = _bundle_record(runs_root / str(item.get("run_id")), item.get("label") or "")
        if rec is not None:
            runs[config_key(item["config"])] = rec
            manifest = manifest or (evidence._read_json(runs_root / item["run_id"] / "manifest.json")
                                    if (runs_root / item["run_id"] / "manifest.json").is_file() else {})
    failing = sum(1 for r in runs.values() if r["failed"])
    return {"kind": "campaign", "id": doc["id"], "target": doc.get("name"), "finished": None,
            "verdict": "Không đạt" if failing else "Đạt", "counts": {"failed_runs": failing},
            "runs_total": len(runs), "planned": len(doc.get("items") or []), "scope": "all",
            **_environment(manifest), "runs": runs}


# ---- comparison --------------------------------------------------------------------------

def _differences(a: dict, b: dict) -> list[dict]:
    out = []

    def add(key, label, x, y, level):
        if x != y:
            out.append({"key": key, "label": label, "base": x, "cand": y, "level": level})

    la = [lib.get("sha256") for lib in a["libraries"]]
    lb = [lib.get("sha256") for lib in b["libraries"]]
    add("libraries", "Thư viện planner (sha256)", [s[:12] for s in la if s], [s[:12] for s in lb if s], "info")
    add("pp_version", "Phiên bản planner", [lib.get("pp_version") for lib in a["libraries"]],
        [lib.get("pp_version") for lib in b["libraries"]], "info")
    add("calibration", "Bộ calibration", a["calibration"], b["calibration"], "info")
    add("commit", "Commit của simulator và bên chấm", a["commit"], b["commit"], "info")
    add("dirty", "Cây làm việc chưa commit", a["dirty"], b["dirty"], "warn")
    add("inputs", "Bộ đầu vào benchmark (băm các file kịch bản, lỗi, calibration)", a["inputs"], b["inputs"], "info")
    ea, eb = a["environment"], b["environment"]
    for key, label in (("platform", "Hệ điều hành"), ("machine", "Kiến trúc máy"), ("python", "Phiên bản Python"),
                       ("numpy", "Phiên bản numpy")):
        add(key, label + ": checksum hành vi không so được từng bit", ea.get(key), eb.get(key), "warn")
    add("target", "Loại lần chạy", a["target"], b["target"], "warn")
    if a["scope"] != b["scope"]:
        add("scope", "Cách chấm", a["scope"], b["scope"], "warn")
    return out


def compare(base: dict, cand: dict) -> dict:
    if base["kind"] != cand["kind"]:
        raise ValueError("chỉ so hai lần chạy suite với nhau, hoặc hai campaign với nhau")
    keys_a, keys_b = set(base["runs"]), set(cand["runs"])
    matched = sorted(keys_a & keys_b)
    counts = {"matched": 0, "only_base": len(keys_a - keys_b), "only_cand": len(keys_b - keys_a), "case_changed": 0,
              "behavior_same": 0, "behavior_changed": 0, "new": 0, "fixed": 0, "still": 0}
    by_req: dict = {}
    by_fam: dict = {}
    rows = []
    changed_cases = []
    for key in matched:
        a, b = base["runs"][key], cand["runs"][key]
        if a.get("case_hash") != b.get("case_hash"):
            counts["case_changed"] += 1
            changed_cases.append(a["label"])
            continue
        counts["matched"] += 1
        counts["behavior_same" if a["checksum"] == b["checksum"] else "behavior_changed"] += 1
        fam = family(a["label"].split(" seed ")[0]) if base["kind"] == "suite" else a["label"]
        for req in sorted(set(a["failed"]) | set(b["failed"])):
            kind = "still" if req in a["failed"] and req in b["failed"] else "new" if req in b["failed"] else "fixed"
            counts[kind] += 1
            row = by_req.setdefault(req, {"id": req, "new": 0, "fixed": 0, "still": 0})
            row[kind] += 1
            frow = by_fam.setdefault(fam, {"id": fam, "new": 0, "fixed": 0, "still": 0})
            frow[kind] += 1
            va, vb = a["values"].get(req), b["values"].get(req)
            limit = (vb or va or [None, None])[1]
            ma = margin(va[0], limit) if va else None
            mb = margin(vb[0], limit) if vb else None
            rows.append({"kind": kind, "requirement": req, "run": a["label"], "key": key, "limit": limit,
                         "base_value": va[0] if va else None, "cand_value": vb[0] if vb else None,
                         "base_margin": ma, "cand_margin": mb,
                         "delta_margin": (mb - ma) if ma is not None and mb is not None else None})
    order = {"new": 0, "still": 1, "fixed": 2}
    rows.sort(key=lambda r: (order[r["kind"]], r["delta_margin"] if r["delta_margin"] is not None else 0.0,
                             r["requirement"], r["run"]))
    warnings = []
    if counts["only_base"] or counts["only_cand"]:
        warnings.append(f"{counts['only_base']} lượt chỉ có ở baseline và {counts['only_cand']} lượt chỉ có ở candidate: "
                        "tập ca không trùng nhau, các lượt này không được so.")
    if counts["case_changed"]:
        warnings.append(f"{counts['case_changed']} lượt cùng tên nhưng khác case_hash: ca đã đổi nên không được so.")
    if not counts["matched"]:
        warnings.append("Không có lượt nào ghép được giữa hai bên.")
    if counts["matched"] and counts["behavior_changed"] == 0 and counts["new"] + counts["fixed"]:
        warnings.append("Hành vi mọi lượt ghép được giống nhau từng bit nhưng kết quả chấm khác: bên chấm hoặc tiêu chí đã đổi.")
    return {"base": _meta(base), "cand": _meta(cand), "differences": _differences(base, cand), "warnings": warnings,
            "counts": counts, "by_requirement": sorted(by_req.values(), key=lambda r: (-(r["new"] + r["fixed"]), r["id"])),
            "by_family": sorted(by_fam.values(), key=lambda r: (-(r["new"] + r["fixed"]), r["id"]))[:60],
            "changes": rows[:MAX_ROWS], "truncated": max(0, len(rows) - MAX_ROWS),
            "case_changed_examples": changed_cases[:5]}


def _meta(side: dict) -> dict:
    return {k: side[k] for k in ("kind", "id", "target", "finished", "verdict", "counts", "runs_total", "planned",
                                 "commit", "dirty", "libraries")}


def parse_ref(text: str) -> tuple[str, str]:
    """'suite:<id>' or 'campaign:<id>'."""
    kind, _, ident = (text or "").partition(":")
    if kind not in KINDS or not ident:
        raise ValueError("tham chiếu phải có dạng suite:<id> hoặc campaign:<id>")
    return kind, ident

"""Read-only views for the workbench UI: suite conclusions, golden baseline, per-run verdicts.

Reads files other tools wrote (build/benchmark/*/suite, build/golden/baseline.json, run bundles).
Imports no SUT package; knows only the file layout. Nothing here writes or runs anything.
"""

import json
import re
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "build" / "benchmark"
GOLDEN = ROOT / "build" / "golden" / "baseline.json"
GOLDEN_SET = ROOT / "benchmark" / "suites" / "golden.yaml"
SUITE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,80}$")

_lock = threading.Lock()
_cache: dict = {}


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _cached(path: Path, build):
    """build(path) cached by (path, mtime, size): the files are large and change rarely."""
    st = path.stat()
    key = (str(path), st.st_mtime_ns, st.st_size)
    with _lock:
        if key not in _cache:
            _cache[key] = build(path)
        return _cache[key]


# ---- suites ------------------------------------------------------------------------------

def _suite_dirs() -> list[Path]:
    if not BENCH.is_dir():
        return []
    return [p for p in BENCH.iterdir() if p.is_dir() and SUITE_ID.match(p.name)
            and (p / "suite" / "conclusion.json").is_file()]


def _libraries(manifest: dict) -> list[dict]:
    return [{"pp_version": lib.get("pp_version"), "sha256": lib.get("sha256")} for lib in manifest.get("libraries") or []]


def _planner(manifest: dict) -> dict:
    libs = _libraries(manifest)
    git = manifest.get("git") or {}
    return {"pp_version": " | ".join(str(lib["pp_version"]) for lib in libs) or None, "libraries": libs,
            "commit": git.get("short"), "dirty": bool(git.get("dirty")),
            "environment": manifest.get("environment")}


def suites() -> list[dict]:
    out = []
    for folder in _suite_dirs():
        suite = folder / "suite"
        try:
            summary = _read_json(suite / "summary.json") if (suite / "summary.json").is_file() else {}
            manifest = _read_json(suite / "manifest.json") if (suite / "manifest.json").is_file() else {}
        except ValueError:
            continue
        out.append({"id": folder.name, "target": manifest.get("target"), "finished": manifest.get("finished"),
                    "planned": summary.get("planned"), "executed": summary.get("executed"),
                    "partial": summary.get("partial"), "verdict": summary.get("verdict"),
                    "planner": _planner(manifest), "has_report": (folder / "report.html").is_file()})
    return sorted(out, key=lambda s: (s["finished"] or "", s["id"]), reverse=True)


def _digest(path: Path) -> dict:
    c = _read_json(path)
    failures = c.get("failures") or []
    by_req: dict = {}
    first: dict = {}
    for f in failures:
        if f.get("level") != "BLOCKER":
            continue
        rid = f["requirement"]
        row = by_req.setdefault(rid, {"id": rid, "sg": ", ".join(f.get("safety_goals") or []), "n": 0})
        row["n"] += 1
        if rid not in first:
            first[rid] = {k: f.get(k) for k in ("requirement", "case", "profile", "seed", "first_fail_s",
                                                "value", "limit", "text")}
            first[rid]["sg"] = row["sg"]
    return {"verdict": c.get("verdict"), "integrable": c.get("integrable"), "b0_blocked": c.get("b0_blocked"),
            "runs": c.get("runs"), "counts": c.get("counts"),
            "n_failures": len(failures), "n_out_of_scope": len(c.get("out_of_scope") or []),
            "not_judged": len(c.get("not_judged") or []),
            "by_requirement": sorted(by_req.values(), key=lambda r: (-r["n"], r["id"])),
            "first_fails": sorted(first.values(), key=lambda r: r["requirement"])}


def suite(suite_id: str) -> dict:
    if not SUITE_ID.match(suite_id) or not (BENCH / suite_id / "suite" / "conclusion.json").is_file():
        raise KeyError(suite_id)
    folder = BENCH / suite_id
    out = _cached(folder / "suite" / "conclusion.json", _digest)
    row = next((s for s in suites() if s["id"] == suite_id), {})
    return {"id": suite_id, **row, **out}


def suite_report(suite_id: str) -> bytes:
    if not SUITE_ID.match(suite_id) or not (BENCH / suite_id / "report.html").is_file():
        raise KeyError(suite_id)
    return (BENCH / suite_id / "report.html").read_bytes()


# ---- golden ------------------------------------------------------------------------------

def _purposes() -> dict:
    """{case id: purpose} from golden.yaml, read line by line (the file has a fixed, flat shape)."""
    out, cur = {}, None
    if not GOLDEN_SET.is_file():
        return out
    for line in GOLDEN_SET.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*-\s*id:\s*(G-\d+)\s*$", line)
        if m:
            cur = m.group(1)
            continue
        m = re.match(r"\s+purpose:\s*(.+?)\s*$", line)
        if m and cur:
            out[cur] = m.group(1)
    return out


def golden() -> dict:
    if not GOLDEN.is_file():
        return {"recorded": False}
    data = _read_json(GOLDEN)
    purposes = _purposes()
    cases: dict = {}
    for r in data.get("results", []):
        key = (r["case"], r["seed"])
        row = cases.setdefault(key, {"id": r["case"], "purpose": purposes.get(r["case"], ""), "seed": r["seed"],
                                     "checksum": None, "paths": {}})
        ok = r.get("status") == "ok" and r.get("checksum")
        row["paths"][r["path"]] = "ok" if ok else (r.get("status") or "?")
        if ok:
            if row["checksum"] is None:
                row["checksum"] = r["checksum"]
            elif row["checksum"] != r["checksum"]:
                row["paths"][r["path"]] = "lệch"
    rows = sorted(cases.values(), key=lambda c: (c["id"], c["seed"]))
    return {"recorded": True, "environment": data.get("environment"), "paths": data.get("paths"),
            "jobs": data.get("jobs"), "recorded_at": GOLDEN.stat().st_mtime, "cases": rows,
            "n_results": len(data.get("results", []))}


# ---- runs --------------------------------------------------------------------------------

def run_summary(folder: Path) -> dict:
    """What the run list needs beyond execution.json: source, evaluation verdict, duration."""
    def build(_):
        out = {"source": None, "target": None, "verdict": None, "applicable": None, "passed": None, "first_fail": None}
        try:
            manifest = _read_json(folder / "manifest.json") if (folder / "manifest.json").is_file() else {}
            out["target"] = manifest.get("target")
            out["source"] = "Web" if (manifest.get("kind") == "live" or (not manifest and (folder / "request.json").is_file())) else "CLI"
            if (folder / "evaluation.json").is_file():
                ev = _read_json(folder / "evaluation.json")
                crit = [c for c in ev.get("criteria", []) if c.get("applicable")]
                bad = [c for c in crit if not c.get("passed")]
                out["verdict"] = ("pass" if ev.get("passed") else
                                  "not_judged" if ev.get("passed", False) is None else "fail")
                out["applicable"] = len(crit)
                out["passed"] = len(crit) - len(bad)
                out["first_fail"] = bad[0]["id"] if bad else None
        except (ValueError, KeyError):
            pass
        return out
    marker = folder / "execution.json"
    return _cached(marker, build)


# ---- rerun -------------------------------------------------------------------------------

def _identity(manifest: dict) -> dict:
    """What a rerun must reproduce, from the manifest of a run."""
    bundle = manifest.get("bundle") or {}
    return {"case_hash": bundle.get("case_hash"), "behavior_checksum": bundle.get("behavior_checksum"),
            "checksum_version": bundle.get("checksum_version"), "libraries": _libraries(manifest),
            "commit": (manifest.get("git") or {}).get("commit")}


def rerun_request(folder: Path) -> dict:
    """Request of a run that repeats a finished run; KeyError when the run left no identity."""
    manifest = _read_json(folder / "manifest.json") if (folder / "manifest.json").is_file() else {}
    bundle = manifest.get("bundle") or {}
    if not bundle.get("recipe") or not bundle.get("behavior_checksum"):
        raise KeyError(folder.name)
    request = {"recipe": bundle["recipe"], "seed": manifest.get("seed", 1), "rate": 0,
               "planner_only": manifest.get("planner_only"),
               "expect": {**_identity(manifest), "source": {"run": folder.name}}}
    original = _read_json(folder / "request.json") if (folder / "request.json").is_file() else {}
    if original.get("config"):
        request["config"] = {**original["config"], "rate": 0}
    return request


def _suite_record(suite_dir: Path, case: str, seed: int) -> dict:
    needle = json.dumps(case).encode()
    with (suite_dir / "results.jsonl").open("rb") as stream:
        for line in stream:
            if needle in line:
                record = json.loads(line)
                if record.get("case") == case and record.get("seed") == seed:
                    return record
    raise KeyError(case)


def suite_rerun_request(suite_id: str, case: str, seed: int) -> dict:
    """Request of a run that repeats one run of a suite from its frozen case file."""
    if not SUITE_ID.match(suite_id):
        raise KeyError(suite_id)
    folder = BENCH / suite_id
    record = _suite_record(folder / "suite", case, seed)
    cases = _read_json(folder / "concrete" / "manifest.json")["cases"]
    entry = next(c for c in cases if c["id"] == case)
    path = folder / "concrete" / entry["file"]
    if not path.is_file():
        raise KeyError(case)
    manifest = _read_json(folder / "suite" / "manifest.json")
    return {"recipe": {"kind": "file", "path": str(path.relative_to(ROOT))}, "seed": seed, "rate": 0,
            "planner_only": entry.get("planner_only"),
            "expect": {"case_hash": record.get("case_hash"), "behavior_checksum": record.get("behavior_checksum"),
                       "checksum_version": None, "libraries": _libraries(manifest),
                       "commit": (manifest.get("git") or {}).get("commit"),
                       "source": {"suite": suite_id, "case": case}}}


def rerun_check(folder: Path) -> dict | None:
    """Result of a rerun against what it had to reproduce; None for any other run."""
    request = _read_json(folder / "request.json") if (folder / "request.json").is_file() else {}
    expected = request.get("expect")
    if not expected:
        return None
    if not (folder / "manifest.json").is_file():
        return {"expected": expected, "actual": None, "match": None, "reasons": ["Lần chạy lại không hoàn tất."]}
    actual = _identity(_read_json(folder / "manifest.json"))
    match = bool(expected.get("behavior_checksum")) and expected["behavior_checksum"] == actual["behavior_checksum"]
    reasons = []
    if not match:
        if expected.get("checksum_version") and expected["checksum_version"] != actual["checksum_version"]:
            reasons.append(f"Phiên bản checksum khác: {expected['checksum_version']} và {actual['checksum_version']}.")
        if expected.get("case_hash") != actual["case_hash"]:
            reasons.append("Ca đã đổi (case_hash khác).")
        if [lib.get("sha256") for lib in expected.get("libraries") or []] != [lib["sha256"] for lib in actual["libraries"]]:
            reasons.append("Thư viện planner khác bản đã ghi (sha256 khác).")
        if expected.get("commit") != actual["commit"]:
            reasons.append("Commit của simulator hoặc bên chấm khác bản đã ghi.")
        if not reasons:
            reasons.append("Cùng ca, thư viện và commit nhưng hành vi khác: cần mở problem report.")
    return {"expected": expected, "actual": actual, "match": match, "reasons": reasons}


def bundle_files(folder: Path, verify) -> dict:
    """Files of a finished bundle with sizes, and the SHA256SUMS check (verify: execution.bundle.verify)."""
    files = [{"name": p.relative_to(folder).as_posix(), "size": p.stat().st_size}
             for p in sorted(folder.rglob("*")) if p.is_file()]
    return {"files": files, "problems": verify(folder)}

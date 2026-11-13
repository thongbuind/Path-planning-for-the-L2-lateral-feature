"""Conclusion of a benchmark report (Software Qualification Test Specification 8.4, 10).

Every failure gets the level of its requirement (eval.severity). A requirement counts only
in the cases its Kiểm chứng column names (section 8.1, the run's scope); failures outside
are listed as information. B0 (section 11) comes first: C1 or C2 failed blocks the planner,
C3 decides the Integrable flag.

A run record, as eval.suite and eval.matrix keep them:
  {"case", "profile", "seed", "result": metrics.Result.to_dict() or None,
   "scope": [ids] or None (None: every criterion), "execution": text or None,
   "error": text or None (evaluator side), "mcap": path or None, "rerun": command}
"""

from eval import severity

# Names of Software Qualification Test Specification 8.4 (renamed in 1.30).
BLOCKED = "Không đạt"
NOT_APPROVED = "Không đạt quy định"
NO_BLOCKER = "Đạt trong phạm vi đã thử"
LEVELS = (severity.BLOCKER, severity.MAJOR, severity.MINOR)


def _row(level, requirement, run, *, first_fail_s=None, value=None, limit="", text=""):
    return {"level": level, "requirement": requirement,
            "safety_goals": severity.safety_goals(requirement), "case": run.get("case"),
            "profile": run.get("profile"), "seed": run.get("seed"), "first_fail_s": first_fail_s,
            "value": value, "limit": limit, "text": text, "mcap": run.get("mcap"), "rerun": run.get("rerun")}


def _level(requirement: str) -> str | None:
    try:
        return severity.level(requirement)
    except KeyError:
        return severity.BLOCKER  # unknown to the specification: never hidden


level_of = _level  # public name for other report sections


def run_failures(run: dict) -> tuple[list[dict], list[dict], list[str]]:
    """(failures in scope, failures out of scope, reasons the case was not judged)."""
    if run.get("execution"):
        return [_row(severity.BLOCKER, severity.EXECUTION_FAULT, run, text=run["execution"])], [], []
    if run.get("error"):
        return [], [], [f"Lỗi bên chấm: {run['error']}"]
    result = run["result"]
    scope = None if run.get("scope") is None else set(run["scope"])
    inside, outside, not_judged = [], [], []
    for c in result["criteria"]:
        if not c["applicable"] or c["passed"]:
            continue
        level = _level(c["id"])
        if level is None:
            continue
        row = _row(level, c["id"], run, first_fail_s=c.get("first_fail_s"), value=c["value"],
                   limit=c["limit"], text=c["metric"])
        (inside if scope is None or c["id"] in scope else outside).append(row)
    issues = result.get("issues")
    if issues is None:  # result written before issues were classified
        issues = [{"kind": "requirement", "requirement": None, "text": t, "first_fail_s": None}
                  for t in result.get("case_failures", [])]
    for issue in issues:
        if issue["kind"] == "not_judged":
            not_judged.append(issue["text"])
        elif issue["kind"] == "execution":
            inside.append(_row(severity.BLOCKER, severity.EXECUTION_FAULT, run,
                               first_fail_s=issue.get("first_fail_s"), text=issue["text"]))
        else:
            requirement = issue.get("requirement") or "?"
            inside.append(_row(_level(requirement) if requirement != "?" else severity.BLOCKER,
                               requirement, run, first_fail_s=issue.get("first_fail_s"), text=issue["text"]))
    return inside, outside, not_judged


def b0_failures(b0: dict) -> list[dict]:
    run = {"case": "B0", "profile": None, "seed": None}
    return [_row(severity.BLOCKER, c["id"], run, text=f"{c.get('title', '')}: {c['detail']}".strip(": "))
            for c in b0["checks"] if c["status"] == "fail" and c["level"] in ("C1", "C2")]


def conclude(runs: list[dict], b0: dict | None = None) -> dict:
    failures = b0_failures(b0) if b0 else []
    outside, not_judged = [], []
    for run in runs:
        i, o, n = run_failures(run)
        failures += i
        outside += o
        not_judged += [{"case": run.get("case"), "seed": run.get("seed"), "text": t} for t in n]
    levels = {f["level"] for f in failures}
    verdict = (BLOCKED if severity.BLOCKER in levels else NOT_APPROVED if severity.MAJOR in levels
               else NO_BLOCKER)
    order = {lv: i for i, lv in enumerate(LEVELS)}
    failures.sort(key=lambda f: (order[f["level"]], f["requirement"], str(f["case"]), f["seed"] or 0))
    return {"verdict": verdict,
            "integrable": None if b0 is None else bool(b0["integrable"]),
            "b0_blocked": bool(b0 and b0["blocked"]),
            "runs": len(runs),
            "counts": {lv: sum(f["level"] == lv for f in failures) for lv in LEVELS},
            "failures": failures, "out_of_scope": outside, "not_judged": not_judged}


def _fmt(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def markdown(c: dict, planner: str = "") -> list[str]:
    """Head of a report: conclusion, Integrable flag, every failure by level."""
    integrable = {None: "chưa chạy B0", True: "có", False: "không"}[c["integrable"]]
    lines = [f"# Kết luận: {c['verdict']}", ""]
    if planner:
        lines.append(f"- Planner: {planner}")
    lines += [f"- Tích hợp được: {integrable}",
              f"- Đã chạy: {c['runs']} lần chạy; trượt BLOCKER {c['counts']['BLOCKER']}, "
              f"MAJOR {c['counts']['MAJOR']}, MINOR {c['counts']['MINOR']}"
              + (f"; {len(c['not_judged'])} ca không được chấm" if c["not_judged"] else ""),
              "- Kết luận chỉ đúng trong phạm vi đã thử, không phải bằng chứng an toàn "
              "(Software Qualification Test Specification 3)."]
    if c["b0_blocked"]:
        lines.append("- B0 trượt C1 hoặc C2: không chạy bộ khác.")
    head = ("| Requirement | Safety goal | Ca | Profile | Seed | Trượt đầu tiên [s] | Giá trị | Ngưỡng | "
            "Chi tiết | MCAP |")
    for level in LEVELS:
        rows = [f for f in c["failures"] if f["level"] == level]
        if not rows:
            continue
        lines += ["", f"## Trượt {level}", "", head, "|---|---|---|---|---|---|---|---|---|---|"]
        for f in rows:
            lines.append(f"| {f['requirement']} | {', '.join(f['safety_goals']) or '—'} | {_fmt(f['case'])} | "
                         f"{_fmt(f['profile'])} | {_fmt(f['seed'])} | {_fmt(f['first_fail_s'])} | "
                         f"{_fmt(f['value'])} | {f['limit'] or '—'} | {f['text'].replace('|', '/')} | "
                         f"{f['mcap'] or '—'} |")
    if c["not_judged"]:
        lines += ["", "## Ca không được chấm", "", "| Ca | Seed | Lý do |", "|---|---|---|"]
        lines += [f"| {n['case']} | {_fmt(n['seed'])} | {n['text'].splitlines()[0].replace('|', '/')} |"
                  for n in c["not_judged"]]
    if c["out_of_scope"]:
        lines += ["", "## Trượt ngoài phạm vi chấm của ca (thông tin, không tính vào kết luận)", "",
                  "| Mức | Requirement | Ca | Seed | Giá trị | Ngưỡng |", "|---|---|---|---|---|---|"]
        lines += [f"| {f['level']} | {f['requirement']} | {_fmt(f['case'])} | {_fmt(f['seed'])} | "
                  f"{_fmt(f['value'])} | {f['limit'] or '—'} |" for f in c["out_of_scope"]]
    return lines

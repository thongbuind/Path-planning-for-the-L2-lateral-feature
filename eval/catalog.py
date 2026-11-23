"""Catalog ca kiểm của path planner để bàn giao: Given, When, Then cho từng anchor.

Sinh từ benchmark (Software Qualification Test Specification mục 5, 6) và cột Kiểm chứng của
Software Requirements Specification, không cần thư viện planner. Then là các requirement trong
phạm vi chấm của ca, như bên chấm dùng (SQTS 8.1).

    python -m eval.catalog --suite regression --out build/catalog
"""

import argparse
import csv
import json
import re
from pathlib import Path

from eval import case, openx, severity
from eval.runner import run_scope

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "benchmark"
SUITES = BENCHMARK / "suites"
_ROW = re.compile(r"^\|\s*(PP-SWR-\d{3})\s*\|")
_CLOSED: set[str] = set()
WHEN = "Planner nhận input qua Interface Control Document mỗi chu kỳ 25 ms; bên chấm đo trên chuyển động thật của xe"


def requirements(path: Path = severity.SRS) -> dict[str, str]:
    """ID → câu requirement, đọc từ các bảng có cột Yêu cầu."""
    out, header = {}, None
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and cells[0] == "ID":
            header = cells
            continue
        if _ROW.match(line.strip()) and header and "Yêu cầu" in header:
            out[cells[0]] = cells[header.index("Yêu cầu")]
    return out


def closed_loop_only(path: Path = severity.SRS) -> set[str]:
    """Requirement có ghi "vòng kín" ở cột Kiểm chứng: cần xe chạy theo path, không chấm được vòng hở."""
    out, header = set(), None
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and cells[0] == "ID":
            header = cells
            continue
        if _ROW.match(line.strip()) and header and "Kiểm chứng" in header and "vòng kín" in cells[header.index("Kiểm chứng")]:
            out.add(cells[0])
    return out


def _level(rid: str) -> str | None:
    try:
        return severity.level(rid)
    except KeyError:
        return None


def _entry(code: str, variant: str, recipe: dict, host: list[str] | None, anchor: dict, scope: set[str]) -> dict:
    scenario = case.resolve(recipe)
    folder = "faults" if code.startswith("F") else "scenarios"
    return {
        "id": f"{code}-{variant}" + (f"-{host[0]}{host[1]}" if host else ""),
        "code": code, "variant": variant, "host": "".join(host) if host else None,
        "given": anchor.get("description") or scenario.notes.get("description", ""),
        "loop": scenario.loop,
        "profile": anchor.get("profile") or "mọi profile của suite",
        "expected_outcome": scenario.notes.get("expected_outcome"),
        "when": WHEN,
        "then": sorted(r for r in scope if r.startswith("PP-SWR-")),
        "then_open_loop": sorted(r for r in scope if r.startswith("PP-SWR-") and r not in _CLOSED),
        "files": [str((BENCHMARK / folder / f"{code}{suffix}").relative_to(ROOT))
                  for suffix in (".xosc", ".anchors.xosc")],
    }


def build(suite_id: str) -> list[dict]:
    _CLOSED.clear()
    _CLOSED.update(closed_loop_only())
    suite = json.loads((SUITES / f"{suite_id}.json").read_text(encoding="utf-8"))
    entries = []
    for sid in suite["scenarios"]:
        anchors = openx.parameter_sets(BENCHMARK / "scenarios" / f"{sid}.xosc", ".anchors.xosc")
        for v, anchor in anchors.items():
            entries.append(_entry(sid, v, {"kind": "catalog", "sid": sid, "v": v}, None, anchor,
                                  run_scope([sid, v], [])))
    overrides = suite.get("fault_host_overrides", {})
    for fid in suite["faults"]:
        anchors = openx.parameter_sets(BENCHMARK / "faults" / f"{fid}.xosc", ".anchors.xosc")
        for host in overrides.get(fid) or suite["fault_hosts"]:
            for v, anchor in anchors.items():
                recipe = {"kind": "catalog", "sid": host[0], "v": host[1], "faults": [[fid, v]]}
                entries.append(_entry(fid, v, recipe, list(host), anchor, run_scope(list(host), [[fid, v]])))
    return entries


def _markdown(entries: list[dict], texts: dict[str, str], suite_id: str) -> str:
    lines = [f"# Catalog ca kiểm của path planner (suite {suite_id})", "",
             "Sinh bằng `python -m eval.catalog`. Given lấy từ anchor của benchmark; When chung cho mọi ca; "
             "Then là requirement trong phạm vi chấm, câu đầy đủ ở bảng cuối.", "",
             f"When: {WHEN}.", "",
             "Then vòng hở: phần của Then chấm được khi xe đi theo quỹ đạo định sẵn, không theo path "
             "(requirement không ghi vòng kín ở cột Kiểm chứng của Software Requirements Specification).", "",
             "| ID | Given | Vòng | Profile | Kết quả mong đợi | Then | Then vòng hở | File |",
             "|---|---|---|---|---|---|---|---|"]
    for e in entries:
        then = ", ".join(r.removeprefix("PP-SWR-") for r in e["then"])
        opened = ", ".join(r.removeprefix("PP-SWR-") for r in e["then_open_loop"]) or "—"
        lines.append(f"| {e['id']} | {e['given']} | {e['loop']} | {e['profile']} | {e['expected_outcome'] or '—'} | "
                     f"{then} | {opened} | `{e['files'][0]}` |")
    used = sorted({r for e in entries for r in e["then"]})
    lines += ["", "## Requirement", "", "| ID | Yêu cầu | Mức khi trượt | Chỉ vòng kín |", "|---|---|---|---|"]
    lines += [f"| {r} | {texts.get(r, '')} | {_level(r) or '—'} | {'có' if r in _CLOSED else 'không'} |" for r in used]
    return "\n".join(lines) + "\n"


def write(entries: list[dict], out: Path, suite_id: str) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    texts = requirements()
    data = {"suite": suite_id, "when": WHEN, "cases": entries,
            "requirements": {r: {"text": texts.get(r, ""), "level": _level(r), "closed_loop_only": r in _CLOSED}
                             for r in sorted({r for e in entries for r in e["then"]})}}
    paths = [out / "planner-test-catalog.json", out / "planner-test-catalog.csv", out / "planner-test-catalog.md"]
    paths[0].write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with paths[1].open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "code", "variant", "host", "given", "loop", "profile", "expected_outcome", "then",
                    "then_open_loop", "file"])
        for e in entries:
            w.writerow([e["id"], e["code"], e["variant"], e["host"] or "", e["given"], e["loop"], e["profile"],
                        e["expected_outcome"] or "", ";".join(e["then"]), ";".join(e["then_open_loop"]), e["files"][0]])
    paths[2].write_text(_markdown(entries, texts, suite_id), encoding="utf-8")
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Writes the planner test catalog (Given/When/Then) of a suite.")
    parser.add_argument("--suite", default="regression")
    parser.add_argument("--out", type=Path, default=ROOT / "build" / "catalog")
    args = parser.parse_args()
    entries = build(args.suite)
    for path in write(entries, args.out, args.suite):
        print(path)
    print(f"{len(entries)} ca")


if __name__ == "__main__":
    main()

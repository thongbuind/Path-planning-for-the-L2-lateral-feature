"""Ba chỉ số của quy trình kiểm chứng trên một lần chạy suite: requirement coverage, pass rate và
danh sách requirement chưa được chấm. Code coverage đo riêng ở Unit Test Specification mục 7.

Requirement là dòng PP-SWR có cột Type trong Software Requirements Specification, không tính
performance target. Một requirement được chấm khi ít nhất một lượt có nó trong phạm vi và
criterion của nó áp dụng được.

    python -m eval.verification_metrics build/p0/regression/official-suite/results.jsonl
"""

import argparse
import json
import re
from collections import Counter
from pathlib import Path

from eval import severity

_ROW = re.compile(r"^\|\s*(PP-SWR-\d{3})\s*\|")


def verification_methods(path: Path = severity.SRS) -> dict[str, str]:
    """ID → nội dung cột Kiểm chứng của các requirement (bỏ performance target, bỏ obsolete)."""
    types = severity.requirement_types(path)
    out, header = {}, None
    text = path.read_text(encoding="utf-8")
    text = text[:text.find("\n## 9. Performance targets")] if "\n## 9. Performance targets" in text else text
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and cells[0] == "ID":
            header = cells
            continue
        if (_ROW.match(line.strip()) and header and "Kiểm chứng" in header and types.get(cells[0])
                and "obsolete" not in line):
            out[cells[0]] = cells[header.index("Kiểm chứng")]
    return out


def compute(records: list[dict], methods: dict[str, str], texts: dict[str, str] | None = None) -> dict:
    tested = sorted(r for r, m in methods.items() if m.startswith("Test"))
    judged, failed, scoped = Counter(), Counter(), Counter()
    own: set[str] = set()
    runs_failed = 0
    for rec in records:
        scope = set(rec.get("scope") or [])
        scoped.update(scope)
        criteria = rec.get("result", {}).get("criteria", [])
        own.update(c["id"] for c in criteria)
        in_scope = [c for c in criteria if c["id"] in scope and c["applicable"]]
        for c in in_scope:
            judged[c["id"]] += 1
            if not c["passed"]:
                failed[c["id"]] += 1
        runs_failed += bool(rec.get("failed"))
    covered = [r for r in tested if judged[r]]
    # Requirement ghép (ví dụ "khi lỗi X, PP-SWR-051 và 100 phải thoả") không có criterion riêng;
    # bên chấm kiểm qua requirement mà nó trỏ tới, trên đúng ca có trong phạm vi.
    texts = texts or {}
    refers = lambda r: bool(re.search(r"PP-SWR-\d{3}", texts.get(r, "")))
    composite = [r for r in tested if r not in own and scoped[r] and refers(r)]
    missing = [r for r in tested if r not in own and scoped[r] and not refers(r)]
    passing = [r for r in covered if not failed[r]]
    return {
        "runs": len(records),
        "runs_passed": len(records) - runs_failed,
        "requirements_test": len(tested),
        "requirements_judged": len(covered),
        "requirements_composite": len(composite),
        "requirements_passed": len(passing),
        "not_judged": [r for r in tested if not judged[r] and r not in composite and r not in missing],
        "no_criterion": missing,
        "composite": composite,
        "failing": {r: (failed[r], judged[r]) for r in covered if failed[r]},
        "other_methods": Counter(re.split(r"[:,; ]", m.strip())[0] for r, m in methods.items()
                                 if not m.startswith("Test")),
    }


def markdown(m: dict, source: str) -> str:
    pct = lambda a, b: f"{100.0 * a / b:.1f} %" if b else "—"
    lines = [f"# Chỉ số kiểm chứng ({source})", "",
             "| Chỉ số | Giá trị |", "|---|---|",
             f"| Requirement có Kiểm chứng Test | {m['requirements_test']} |",
             f"| Có criterion riêng và đã được chấm | {m['requirements_judged']} |",
             f"| Requirement ghép, kiểm qua requirement mà nó trỏ tới trên ca trong phạm vi | {m['requirements_composite']} |",
             f"| Requirement coverage | {m['requirements_judged'] + m['requirements_composite']} / {m['requirements_test']} "
             f"({pct(m['requirements_judged'] + m['requirements_composite'], m['requirements_test'])}) |",
             f"| Requirement đạt ở mọi lượt đã chấm | {m['requirements_passed']} / {m['requirements_judged']} |",
             f"| Pass rate theo lượt | {m['runs_passed']} / {m['runs']} ({pct(m['runs_passed'], m['runs'])}) |",
             f"| Requirement kiểm chứng cách khác | "
             f"{', '.join(f'{k} {v}' for k, v in sorted(m['other_methods'].items())) or '—'} |", "",
             "## Requirement chưa được chấm", ""]
    lines += [", ".join(m["not_judged"]) or "Không có.", "", "## Requirement ghép", "",
              ", ".join(m["composite"]) or "Không có.", "",
              "## Có trong phạm vi nhưng bên chấm chưa có criterion", "",
              ", ".join(m["no_criterion"]) or "Không có.", "", "## Requirement có lượt trượt", "",
              "| ID | Lượt trượt / lượt chấm |", "|---|---|"]
    lines += [f"| {r} | {f} / {j} |" for r, (f, j) in sorted(m["failing"].items())]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Requirement coverage and pass rate of one suite run.")
    parser.add_argument("results", type=Path, help="results.jsonl of a suite run")
    parser.add_argument("--out", type=Path, help="write the markdown here instead of printing it")
    args = parser.parse_args()
    records = [json.loads(line) for line in args.results.read_text(encoding="utf-8").splitlines() if line.strip()]
    from eval.catalog import requirements
    text = markdown(compute(records, verification_methods(), requirements()), str(args.results))
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()

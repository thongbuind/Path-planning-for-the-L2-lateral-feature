"""Text and JSON report of one run (Software Qualification Test Specification section 10)."""

import json
from pathlib import Path

from eval.metrics import Result


def text(result: Result) -> str:
    verdict = ("ĐẠT" if result.passed else "TRƯỢT") if result.scored else "ĐỐI CHIẾU THỜI ĐIỂM"
    lines = [f"Kịch bản {result.scenario}, seed {result.seed}: "
             f"{verdict}", "",
             *(f"TRƯỢT: {reason}" for reason in result.case_failures),
             f"{'Requirement':<12} {'Chỉ số':<52} {'Giá trị':>12}  {'Ngưỡng':<12} Kết quả"]
    for c in result.criteria:
        if not c.applicable:
            lines.append(f"{c.id:<12} {c.metric:<52} {'—':>12}  {c.limit:<12} không áp dụng")
            continue
        lines.append(f"{c.id:<12} {c.metric:<52} {c.value:>12.5g}  {c.limit:<12} "
                     f"{'đạt' if c.passed else 'TRƯỢT'}")
    lines += ["", f"{'Target':<12} {'Chỉ số':<52} {'Giá trị':>12}"]
    for t in result.targets:
        lines.append(f"{t.id:<12} {t.metric:<52} {t.value:>12.5g} {t.unit}")
    lines += [""] + [f"{key}: {value}" for key, value in result.info.items()]
    return "\n".join(lines)


def write_json(result: Result, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{result.scenario}_seed{result.seed}.json"
    path.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return path

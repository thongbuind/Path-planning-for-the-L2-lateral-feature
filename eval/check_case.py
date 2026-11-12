"""Quick check of one new or changed scenario, fault or combination before it enters a suite.

    python3 -m eval.check_case S11                # scenario: every anchor
    python3 -m eval.check_case F05 --host S4 a --at lka_active+0.2
    python3 -m eval.check_case G01
    python3 -m eval.check_case S11 --run          # also one SIL run per anchor, seed 1

Checks, in order (benchmark/AUTHORING.md):
  1  files: <id>.xosc, <id>.anchors.xosc, <id>.ranges.xosc pass the ASAM XSD; roads they use exist
  2  every anchor loads into the simulator subset (eval.openx) and is concrete in an ODD
  3  every anchor has an expected outcome (5.3), a difficulty label and scenario_id = the code
  4  traceability: the code is named in the Kiểm chứng column of the Software Requirements
     Specification, or exempt in Software Qualification Test Specification 6.3
  5  with --run: one closed-loop run per anchor, seed 1, with the delivered planner; prints the
     conclusion and failures only (it never changes the case to make it pass)
Exit status 1 on any check failing. Light: no suite, at most one run per anchor.
"""

import argparse
from pathlib import Path
import sys

import yaml

from eval import labels, loader, openx, severity

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "benchmark"
EXEMPT = {"S10", "F09"}  # Software Qualification Test Specification 6.3


def _files(code: str) -> list[Path]:
    folder = "faults" if code.startswith("F") else "scenarios"
    base = BENCHMARK / folder / code
    return [base.with_suffix(".xosc"), Path(f"{base}.anchors.xosc"), Path(f"{base}.ranges.xosc")]


def check_files(code: str, problems: list[str]) -> None:
    for path in _files(code):
        if not path.is_file():
            problems.append(f"thiếu file {path.relative_to(ROOT)}")
            continue
        try:
            openx.validate(path)
        except Exception as exc:  # xmlschema error text is long: first line only
            problems.append(f"{path.name} không qua XSD: {str(exc).splitlines()[0]}")


def check_anchors(code: str, host, trigger, offset, problems: list[str]) -> list:
    """[(name, scenario)] for every anchor; problems appended."""
    out = []
    if code.startswith("G"):
        from eval.generate import load_combination
        combo = load_combination(code)
        for sid, variant in combo["hosts"]:
            scenario = loader.load(sid, variant)
            for fid, level in combo["faults"]:
                scenario = loader.with_fault(scenario, fid, level)
            from dataclasses import replace
            scenario = replace(scenario, **{k: float(v) for k, v in combo.get("sim", {}).items()})
            out.append((f"{code} trên {sid}{variant}", scenario))
        return out
    folder = BENCHMARK / ("faults" if code.startswith("F") else "scenarios")
    try:
        anchors = openx.anchors(folder / f"{code}.xosc")
    except Exception as exc:
        problems.append(f"không đọc được anchors: {exc}")
        return out
    for variant in anchors:
        try:
            if code.startswith("F"):
                base = loader.load(*host) if host else loader.load("S1", "a")
                scenario = loader.with_fault(base, code, variant, trigger, offset)
                name = f"{code} {variant} trên {''.join(host) if host else 'S1a'}"
            else:
                scenario = loader.load(code, variant)
                name = f"{code} {variant}"
        except Exception as exc:
            problems.append(f"{code} {variant} không nạp được: {exc}")
            continue
        if not code.startswith("F") and not scenario.name.startswith(code):
            problems.append(f"{name}: scenario_id là {scenario.name[:-len(variant)] or '—'}, phải là {code}")
        case_labels = labels.of(scenario)
        if not case_labels["expected"]:
            problems.append(f"{name}: thiếu pp:expected_outcome (mục 5.3)")
        out.append((name, scenario))
    return out


def check_trace(code: str, problems: list[str]) -> None:
    if code.startswith("G") or code in EXEMPT:
        return
    named = {rid for rid, (codes, _, _) in severity.verification().items() if code in codes}
    if not named:
        problems.append(f"{code} chưa có trong cột Kiểm chứng của Software Requirements Specification "
                        "(nêu trong chat, không tự gắn truy vết)")


def run_one(name, scenario) -> list[str]:
    from eval import metrics, planner_choice
    from sim.harness import Harness
    log = Harness(scenario, planner_choice.resolve(None), 1).run()
    result = metrics.evaluate(log)
    failed = result.case_failures + [c.id for c in result.criteria if c.applicable and not c.passed]
    missing = result.info.get("faults_not_injected")
    note = f"; lỗi không được bơm: {missing}" if missing else ""
    return [f"  {name}: {'đạt' if not failed else 'trượt ' + ', '.join(dict.fromkeys(failed))}{note}"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("code", help="S.., F.. or G..")
    parser.add_argument("--host", nargs=2, metavar=("SCENARIO", "VARIANT"), help="Host of a fault (default S1 a)")
    parser.add_argument("--at", metavar="EVENT[+OFFSET]", help="Fault moment, as eval.runner --at")
    parser.add_argument("--run", action="store_true", help="One SIL run per anchor, seed 1")
    args = parser.parse_args()
    trigger, offset = (None, 0.0)
    if args.at:
        from eval.runner import parse_moment
        trigger, offset = parse_moment(args.at)
    problems: list[str] = []
    if not args.code.startswith("G"):
        check_files(args.code, problems)
    else:
        path = BENCHMARK / "combinations" / f"{args.code}.yaml"
        if not path.is_file():
            problems.append(f"thiếu {path.relative_to(ROOT)}")
        else:
            yaml.safe_load(path.read_text(encoding="utf-8"))
    cases = check_anchors(args.code, args.host, trigger, offset, problems)
    check_trace(args.code, problems)
    print(f"{args.code}: {len(cases)} ca nạp được")
    for name, scenario in cases:
        print(f"  {name}: {labels.of(scenario)}")
    if args.run:
        print("Chạy SIL, seed 1:")
        for name, scenario in cases:
            print("\n".join(run_one(name, scenario)))
    if problems:
        print("Vấn đề:\n" + "\n".join(f"  - {p}" for p in problems))
        sys.exit(1)
    print("Không có vấn đề.")


if __name__ == "__main__":
    main()

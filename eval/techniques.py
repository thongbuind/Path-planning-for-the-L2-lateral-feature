"""Technique comparison within one planner (Software Qualification Test Specification 9.1, 10).

    python3 -m eval.suite build/concrete/regression/manifest.json --planner build/planner/libpp_planner.dylib --out build/suites/reg-quintic
    python3 -m eval.suite build/concrete/regression/manifest.json --planner build/planner-qp/libpp_planner.dylib --out build/suites/reg-qp
    python3 -m eval.techniques build/suites/reg-quintic build/suites/reg-qp --name quintic --name qp [--out DIR]

One eval.suite output folder per technique, each built with the best calibration of that
technique (section 7), on the same generated suite. Steps of 9.1, in order:
  1  every requirement of 8.1 met on every profile; a technique that fails is eliminated,
     however smooth it is, with the failures as the reason
  2  safety targets, 3 driver-perception targets, 4 flexibility (spread between profiles),
     5 compute time: Copeland score of the 9.2 pairwise test per group, a later group only
     when the earlier ones tie
Writes build/techniques/<name>/report.md and techniques.json: the comparison table (worst
value of every performance target over all seeds, section 10 "Bảng tổng") and the reason
for each elimination.
"""

import argparse
from collections import Counter
import json
from pathlib import Path

from eval import compare, report

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "build" / "techniques"
STEPS = ("An toàn", "Cảm nhận người lái", "Flexibility", "Thời gian tính")  # 9.1 steps 2 to 5


def step1(p: dict) -> dict:
    """Requirements of 8.1 on every profile: in-scope failures and execution faults eliminate."""
    failing = [r for r in p["records"].values() if r.get("failed") or "execution" in r]
    errors = sum("error" in r for r in p["records"].values())
    reqs = Counter(f for r in failing for f in (r.get("failed") or ["execution"]))
    profiles = sorted({r.get("profile") for r in failing if r.get("profile")})
    return {"passed": not failing, "runs_failed": len(failing), "requirements": dict(reqs.most_common()),
            "profiles": profiles, "evaluator_errors": errors}


def rank(techniques: list[dict]) -> dict:
    compare.check_same_benchmark(techniques)
    rows = {t["name"]: {"step1": step1(t)} for t in techniques}
    kept = [t for t in techniques if rows[t["name"]]["step1"]["passed"]]
    score, duels = compare.copeland(kept) if len(kept) > 1 else ({t["name"]: {g: 0 for g in compare.GROUPS}
                                                                 for t in kept}, [])
    for name, s in score.items():
        rows[name]["copeland"] = s
    order = sorted((t["name"] for t in kept), key=lambda n: tuple(-score[n][g] for g in STEPS))
    eliminated = [t["name"] for t in techniques if t["name"] not in score]
    return {"order": order, "eliminated": eliminated, "rows": rows, "duels": duels,
            "absolute": compare.absolute_values(techniques), "runs": len(techniques[0]["records"]),
            "techniques": [{"name": t["name"], "pp_version": t["pp_version"], "sha256": t["sha256"],
                            "folder": t["folder"]} for t in techniques]}


def markdown(c: dict) -> list[str]:
    names = [t["name"] for t in c["techniques"]]
    lines = ["# So sánh kỹ thuật", "",
             f"Mục 9.1 của Software Qualification Test Specification. {c['runs']} lần chạy mỗi kỹ thuật, cùng bộ ca, "
             "profile và seed. Thời gian tính đo trên máy chạy SIL, chỉ để so các kỹ thuật.", "",
             "| Kỹ thuật | Bước 1: requirement | " + " | ".join(f"Bước {i + 2}: {g}" for i, g in enumerate(STEPS))
             + " | Xếp hạng |", "|---|---|" + "---|" * len(STEPS) + "---|"]
    for name in names:
        row = c["rows"][name]
        s1 = row["step1"]
        verdict = "đạt" if s1["passed"] else f"loại: {s1['runs_failed']} lần chạy trượt"
        cells = [str(row["copeland"][g]) if "copeland" in row else "—" for g in STEPS]
        place = str(c["order"].index(name) + 1) if name in c["order"] else "loại"
        lines.append(f"| {name} | {verdict} | " + " | ".join(cells) + f" | {place} |")
    for name in c["eliminated"]:
        s1 = c["rows"][name]["step1"]
        reqs = ", ".join(f"{k} ({v})" for k, v in list(s1["requirements"].items())[:8])
        lines += ["", f"**{name} bị loại ở bước 1.** Trượt: {reqs}. Profile có trượt: "
                  f"{', '.join(s1['profiles']) or '—'}."]
    lines += ["", "## Bảng tổng", "", "Giá trị xấu nhất của mỗi performance target qua mọi seed (mục 10).", "",
              "| Performance target | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    targets = sorted({k for v in c["absolute"].values() for k in v})
    for key in targets:
        cells = [compare._f(c["absolute"][n].get(key, {}).get("worst")) for n in names]
        lines.append(f"| {key} | " + " | ".join(cells) + " |")
    if not c["eliminated"]:
        lines += ["", "Chưa có kỹ thuật nào bị loại; báo cáo cần ít nhất một kỹ thuật bị loại kèm số liệu (mục 9.1)."]
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("folders", nargs="+", type=Path)
    parser.add_argument("--name", action="append", help="Technique name per folder, in order")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if len(args.folders) < 2:
        parser.error("compare at least two techniques")
    if args.name and len(args.name) != len(args.folders):
        parser.error("one --name per folder")
    names = args.name or [None] * len(args.folders)
    techniques = [compare.load(f, n) for f, n in zip(args.folders, names)]
    if len({t["name"] for t in techniques}) != len(techniques):
        parser.error("technique names must differ; use --name")
    c = rank(techniques)
    out = args.out or OUT_DIR / "-".join(t["name"] for t in techniques)
    out.mkdir(parents=True, exist_ok=True)
    (out / "techniques.json").write_text(json.dumps(c, indent=1, ensure_ascii=False, default=report.jsonable) + "\n",
                                         encoding="utf-8")
    (out / "report.md").write_text("\n".join(markdown(c)) + "\n", encoding="utf-8")
    print("\n".join(markdown(c)[:6 + len(techniques)]))
    print(f"\n{out / 'report.md'}")


if __name__ == "__main__":
    main()

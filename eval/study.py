import argparse
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import yaml

from eval import provenance, sweep

ROOT = Path(__file__).resolve().parents[1]
STUDIES = ROOT / "research" / "studies"
OUT_DIR = ROOT / "build" / "study"


def find_plan(study_id: str) -> Path:
    plans = sorted(STUDIES.glob(f"{study_id}-*/plan.yaml"))
    if len(plans) != 1:
        raise SystemExit(f"{study_id}: expected one research/studies/{study_id}-*/plan.yaml, "
                         f"found {len(plans)}")
    return plans[0]


def variant_sets(plan: dict) -> list[sweep.CalSet]:
    return [sweep.CalSet(vid, dict(v.get("calibration") or {}),
                         tuple(sorted((v.get("cmake") or {}).items())))
            for vid, v in plan["variants"].items()]


def run_variant(suite_id: str, cal_set: sweep.CalSet, parts: list[str], root: Path) -> list[dict]:
    """Một worker chạy mọi phần của cùng biến thể để thư mục build chỉ có một tiến trình dùng."""
    return [sweep.run_set(suite_id, cal_set, part, root) for part in parts]


def table(results: list[dict], plan: dict) -> list[str]:
    lines = sweep._table(results)
    described = {vid: v.get("description", "") for vid, v in plan["variants"].items()}
    return lines + [""] + [f"- {r['set']}: {described.get(r['set'], '')}" for r in
                           sorted(results, key=lambda r: sweep.rank_key(r["summary"]))]


def main() -> None:
    from adapters.sil.sil_planner import PlannerLibraries

    parser = argparse.ArgumentParser(
        description="Runs the variants of a trade study (research/README.md, step 5).",
    )
    parser.add_argument("study", help="Trade study id, e.g. PP-TS-003")
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--variant", action="append", metavar="ID",
                        help="Run only this variant in a draft run; may be repeated")
    parser.add_argument("--part", choices=("tuning", "test"),
                        help="Run only this part in a draft run")
    parser.add_argument("--record", action="store_true",
                        help="Official run: locked plan, clean working tree; copy to research/runs")
    args = parser.parse_args()

    plan_path = find_plan(args.study)
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    if plan.get("runner") == "eval.controller_study":
        parser.error(f"run {args.study} with python3 -m eval.controller_study {args.study}")
    parts = plan.get("parts", ["tuning", "test"])
    sets = variant_sets(plan)
    if args.record and (args.variant or args.part):
        parser.error("--variant and --part are only available for draft runs")
    if args.variant:
        unknown = set(args.variant) - set(plan["variants"])
        if unknown:
            parser.error(f"unknown variants: {', '.join(sorted(unknown))}")
        sets = [cal_set for cal_set in sets if cal_set.name in args.variant]
    if args.part:
        if args.part not in parts:
            parser.error(f"{args.part} is not part of {args.study}")
        parts = [args.part]
    suite = sweep.load_suite(plan["suite"])
    manifest = provenance.make("study", args.study, {
        "jobs": args.jobs,
        "parts": parts,
        "variants": [s.name for s in sets],
        "plan": {
            "path": str(plan_path.relative_to(ROOT)),
            "sha256": provenance.sha256(plan_path),
            "content": plan,
        },
    })
    if args.record:
        if not plan.get("locked"):
            raise SystemExit(f"{plan_path}: set `locked` (step 2) before an official run")
        provenance.preflight(manifest)

    root = OUT_DIR / args.study
    if args.variant or args.part:
        draft_name = "-".join([*parts, *(cal_set.name for cal_set in sets)])
        root = root / "draft" / draft_name
    print(f"{args.study}: {len(sets)} variants × {parts} of suite {plan['suite']}", flush=True)
    with ProcessPoolExecutor(max_workers=args.jobs) as pool:
        per_variant = list(pool.map(run_variant, [plan["suite"]] * len(sets), sets,
                                    [parts] * len(sets), [root] * len(sets)))
    results = [r for runs in per_variant for r in runs]

    lines = [f"# Study {args.study}", "", f"Plan: `{manifest['plan']['path']}`, "
             f"locked {plan.get('locked') or 'no'}; suite {plan['suite']}.", ""]
    if suite.get("paired_evidence"):
        lines += ["Bảng dưới dùng để dò nhanh. Đối chiếu B0, lỗi, điều kiện áp dụng và số đo "
                  "ghép cặp trong `results.json` trước khi xếp hạng theo đề cương.", ""]
    if plan.get("equal_within"):
        lines += ["Coi như ngang nhau khi chênh nhỏ hơn: "
                  + ", ".join(f"{k} {v}" for k, v in plan["equal_within"].items()), ""]
    for part in parts:
        lines += [f"## {part}", ""] + table([r for r in results if r["part"] == part], plan) + [""]
    for r in results:
        if r["summary"]["failed_ids"]:
            lines.append(f"- {r['part']} {r['set']}: " + ", ".join(r["summary"]["failed_ids"]))
    root.mkdir(parents=True, exist_ok=True)
    (root / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (root / "results.json").write_text(json.dumps(results, indent=1, ensure_ascii=False),
                                       encoding="utf-8")
    manifest["libraries"] = [
        info for lib in sorted({r["library"] for r in results})
        for info in provenance.library_infos(PlannerLibraries.at(Path(lib)))
    ]
    provenance.write(manifest, root)
    print(f"Summary: {root / 'summary.md'}", flush=True)
    if args.record:
        conclusion = "Đã lưu kết quả ghép cặp"
        if not suite.get("paired_evidence"):
            best = min((r for r in results if r["part"] == parts[-1]),
                       key=lambda r: sweep.rank_key(r["summary"]))
            conclusion = f"Đứng đầu ở {parts[-1]}: {best['set']}"
        dest = provenance.record(manifest, {"summary.md": root / "summary.md",
                                            "results.json": root / "results.json"}, conclusion)
        print(f"Recorded: {dest}", flush=True)


if __name__ == "__main__":
    main()

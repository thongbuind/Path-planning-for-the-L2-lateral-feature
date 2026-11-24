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
                         tuple(sorted((v.get("cmake") or {}).items())), tuple(v.get("loops") or ()))
            for vid, v in plan["variants"].items()]


def _defaults(cal_set: sweep.CalSet) -> dict:
    """Giá trị mặc định của mọi tham số mà biến thể thấy: calibration chung, rồi generator.yaml của bản lab,
    rồi calibration riêng của biến thể trong plan."""
    params = yaml.safe_load(sweep.BASE_CALIBRATION.read_text(encoding="utf-8"))["parameters"]
    values = {name: p["value"] for name, p in params.items()}
    cmake = dict(cal_set.cmake)
    if cmake.get("PP_T7") == "lab" and cmake.get("PP_T7_LAB"):
        lab = sweep.LAB_DIR / cmake["PP_T7_LAB"] / "generator.yaml"
        if not lab.is_file():
            raise FileNotFoundError(f"{lab} does not exist yet")
        own = yaml.safe_load(lab.read_text(encoding="utf-8")).get("calibration") or {}
        values.update({name: p["value"] for name, p in own.items()})
    values.update(cal_set.values)
    return values


def _same(a, b) -> bool:
    return abs(float(a) - float(b)) <= 1e-9 * max(1.0, abs(float(b)))


def grid_name(vid: str, values: dict) -> str:
    """Tên cấu hình của lưới (IMPLEMENTATION-PLAN.md mục 1): <tên>-<tham số><giá trị>-..."""
    return vid + "".join(f"-{name}{float(value)}" for name, value in values.items())


def grid_sets(plan: dict, strict: bool = False) -> tuple[list[sweep.CalSet], dict, list[str]]:
    """Mở `tuning_grid` thành các cấu hình riêng, chạy như biến thể trên mọi phần của plan.

    Ô trùng giá trị mặc định chính là biến thể gốc nên không chạy lại. Mỗi lưới phải chứa đúng một ô như
    thế (cấu hình mặc định là tâm lưới). Khóa "a+b" là hai tham số đi cùng nhau. Trả về (cấu hình, nhóm:
    biến thể → tên các cấu hình của lưới gồm cả biến thể gốc, cảnh báo). strict: lỗi thay vì cảnh báo.
    """
    import itertools

    sets, groups, warnings = [], {}, []
    base_sets = {s.name: s for s in variant_sets(plan)}
    for vid, grid in (plan.get("tuning_grid") or {}).items():
        problem = None
        if vid not in base_sets:
            problem = f"tuning_grid {vid}: not a variant"
        elif not grid or any(levels is None for levels in grid.values()):
            problem = f"tuning_grid {vid}: levels not defined yet"
        if problem is None:
            try:
                defaults = _defaults(base_sets[vid])
            except FileNotFoundError as error:
                problem = f"tuning_grid {vid}: {error}"
        if problem is not None:
            if strict:
                raise SystemExit(problem)
            warnings.append(problem)
            continue
        axes = []
        for key, levels in grid.items():
            names = key.split("+")
            axes.append([dict(zip(names, level if len(names) > 1 else [level])) for level in levels])
        unknown = sorted({n for axis in axes for n in axis[0]} - set(defaults))
        if unknown:
            if strict:
                raise SystemExit(f"tuning_grid {vid}: unknown parameters {unknown}")
            warnings.append(f"tuning_grid {vid}: unknown parameters {unknown}")
            continue
        names, centre = [vid], 0
        for cells in itertools.product(*axes):
            values = {k: v for cell in cells for k, v in cell.items()}
            if all(_same(v, defaults[k]) for k, v in values.items()):
                centre += 1
                continue
            base = base_sets[vid]
            name = grid_name(vid, values)
            sets.append(sweep.CalSet(name, {**base.values, **values}, base.cmake, base.loops))
            names.append(name)
        if centre != 1:
            raise SystemExit(f"tuning_grid {vid}: the default calibration must be exactly one cell "
                             f"(found {centre})")
        groups[vid] = names
    return sets, groups, warnings


def run_variant(suite_id: str, cal_set: sweep.CalSet, parts: list[str], root: Path) -> list[dict]:
    """Một worker chạy mọi phần của cùng biến thể để thư mục build chỉ có một tiến trình dùng."""
    return [sweep.run_set(suite_id, cal_set, part, root) for part in parts]


def table(results: list[dict], plan: dict) -> list[str]:
    lines = sweep._table(results)
    described = {vid: v.get("description", "") for vid, v in plan["variants"].items()}
    for r in results:  # Cấu hình của lưới mô tả theo biến thể gốc.
        base = r["set"].split("-", 1)[0]
        if r["set"] not in described and base in described:
            described[r["set"]] = f"{described[base]}; lưới {r['set'][len(base) + 1:]}"
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
                        help="Run only this variant or grid configuration in a draft run; may be repeated")
    parser.add_argument("--group", action="append", metavar="ID",
                        help="Run only this variant and its calibration grid (also in an official run); "
                             "may be repeated")
    parser.add_argument("--part", choices=("tuning", "test"),
                        help="Run only this part (an official run records which part)")
    parser.add_argument("--record", action="store_true",
                        help="Official run: locked plan, clean working tree; copy to research/runs")
    args = parser.parse_args()

    plan_path = find_plan(args.study)
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    if plan.get("runner") == "eval.controller_study":
        parser.error(f"run {args.study} with python3 -m eval.controller_study {args.study}")
    parts = plan.get("parts", ["tuning", "test"])
    suite = sweep.load_suite(plan["suite"])
    grid, groups, grid_warnings = grid_sets(plan, strict=args.record)
    for warning in grid_warnings:
        print(f"Draft: {warning}; grid skipped", flush=True)
    sets = variant_sets(plan) + grid
    if args.record and args.variant:
        parser.error("--variant is only available for draft runs; use --group")
    if args.group:
        unknown = set(args.group) - set(plan["variants"])
        if unknown:
            parser.error(f"unknown variants: {', '.join(sorted(unknown))}")
        wanted = {name for vid in args.group for name in groups.get(vid, [vid])}
        if suite.get("paired_evidence"):  # Mỗi lần chạy theo nhóm tự chứa mốc, để hiệu ghép cặp tính trong lần đó.
            from eval import output_diff
            wanted |= set(output_diff.anchors(plan))
        sets = [cal_set for cal_set in sets if cal_set.name in wanted]
    if args.variant:
        unknown = set(args.variant) - {cal_set.name for cal_set in sets}
        if unknown:
            parser.error(f"unknown variants: {', '.join(sorted(unknown))}")
        sets = [cal_set for cal_set in sets if cal_set.name in args.variant]
    if args.part:
        if args.part not in parts:
            parser.error(f"{args.part} is not part of {args.study}")
        parts = [args.part]
    manifest = provenance.make("study", args.study, {
        "jobs": args.jobs,
        "parts": parts,
        "variants": [s.name for s in sets],
        "groups": args.group or [],
        "grid": {vid: names for vid, names in groups.items() if any(n in {s.name for s in sets} for n in names)},
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
    if args.variant or args.group or args.part:
        label = "-".join([*parts, *(args.group or []), *(cal_set.name for cal_set in sets if args.variant)])
        if len(label) > 80:
            import hashlib
            label = label[:60] + "-" + hashlib.sha256(label.encode()).hexdigest()[:8]
        root = root / ("record" if args.record else "draft") / label
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
    files = {"summary.md": root / "summary.md", "results.json": root / "results.json"}
    if suite.get("paired_evidence"):
        from eval import output_diff
        diffs = output_diff.study_diffs(results, plan)
        if diffs["pairs"]:
            (root / "output_diff.json").write_text(json.dumps(diffs, indent=1, ensure_ascii=False),
                                                   encoding="utf-8")
            files["output_diff.json"] = root / "output_diff.json"
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
        dest = provenance.record(manifest, files, conclusion)
        print(f"Recorded: {dest}", flush=True)


if __name__ == "__main__":
    main()

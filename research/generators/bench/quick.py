"""Quick bench (tầng L1) cho generator T7: build nháp, chạy một phần nhỏ của tuning PP-T7.

Chỉ dùng để dò. Kết quả nằm trong build/lab/, không trích trong study (research/generators/README.md).
Từ chối seed và dòng không thuộc phần tuning của PP-T7, để dữ liệu test không ảnh hưởng tới lúc dò.
"""

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from eval import calibration as cal_io  # noqa: E402
from eval import isolation, output_diff, sweep  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import slots  # noqa: E402

SUITE = "PP-T7"
OUT = ROOT / "build" / "lab"
REGISTRY = ROOT / "research" / "generators" / "registry.yaml"
TIMEOUT_S = 600
# 3 dòng vòng hở × seed 1, 2; S1d, S1g, S1b a, S24a, S24b (cua ngắn) vòng kín seed 1.
QUICK = (
    (["S1", "d", {"loop": "open"}], (1, 2)),
    (["S1", "g", "F01", "a", {"loop": "open"}], (1, 2)),
    (["S1b", "a", {"acc": "ignore_limits", "loop": "open"}], (1, 2)),
    (["S1", "d"], (1,)),
    (["S1", "g"], (1,)),
    (["S1b", "a", {"acc": "ignore_limits"}], (1,)),
    (["S24", "a"], (1,)),
    (["S24", "b"], (1,)),
)
# 016 lấy p99 thời gian LCC từ bằng chứng ghép cặp: values chỉ giữ một trong bốn target cùng ID.
COLUMNS = ("PP-SWR-070", "PP-SWR-068", "PP-SWR-069", "PP-SWR-050", "PP-SWR-004")


def runs_for(choice: str, suite: dict) -> list[tuple[list, int]]:
    tuning = suite["tuning"]
    chosen = [(run, seed) for run, seeds in QUICK for seed in seeds] if choice == "quick" else \
        [(run, seed) for run in tuning["runs"] for seed in tuning["seeds"]]
    for run, seed in chosen:
        if run not in tuning["runs"] or seed not in tuning["seeds"]:
            raise SystemExit(f"{run} seed {seed} is not in the tuning part of {SUITE}: refused")
    return chosen


def cmake_of(generator: str) -> dict:
    entries = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))["generators"]
    entry = entries.get(generator)
    if entry is None or "cmake" not in entry:
        raise SystemExit(f"{generator}: no CMake key in {REGISTRY.name}")
    return dict(entry["cmake"])


def parse_sets(items: list[str]) -> dict:
    values = {}
    for item in items:
        name, sep, value = item.partition("=")
        if not sep:
            raise SystemExit(f"--set {item}: expected name=value")
        values[name] = float(value)
    return values


def label_of(generator: str, values: dict, telemetry: bool) -> str:
    label = generator + ("-tm" if telemetry else "")
    if values:
        label += "-" + hashlib.sha256(json.dumps(values, sort_keys=True).encode()).hexdigest()[:8]
    return label


def one(run: list, seed: int, lib: str, folder: str, name: str) -> dict:
    from adapters.sil.sil_planner import PlannerLibraries
    suite = sweep.load_suite(SUITE)
    params = yaml.safe_load((Path(folder) / "calibration.yaml").read_text(encoding="utf-8"))["parameters"]
    return sweep.run_line(suite, run, seed, PlannerLibraries.at(Path(lib)), cal_io.from_parameters(params),
                          Path(folder), name)


def fmt(value) -> str:
    return "—" if value is None or not math.isfinite(value) else f"{value:.3f}"


def table(rows: list[dict], against: dict | None) -> list[str]:
    head = ["Run", "Seed", "Trượt"] + [c.removeprefix("PP-SWR-") for c in COLUMNS] + ["016 p99 LCC [ms]"]
    if against:
        head += ["Lệch output max [m]"]
    telemetry = any(r.get("t7_telemetry") for r in rows)
    if telemetry:  # p99 thời gian của bản telemetry không dùng được (đọc telemetry trong vùng đo).
        head += ["work p99", "work max", "tỉ lệ fallback", "T10 sửa max [m]"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for r in rows:
        cells = [r["run"], str(r["seed"]), ", ".join(x.removeprefix("PP-SWR-") for x in r["failed"]) or "—"]
        other = against.get((r["run"], r["seed"])) if against else None
        for c in COLUMNS:
            value = r["values"].get(c)
            text = fmt(value)
            if other is not None and value is not None and other["values"].get(c) is not None:
                text += f" ({value - other['values'][c]:+.3f})"
            cells.append(text)
        p99 = (r.get("compute_lcc_ms") or {}).get("p99")
        cells.append(fmt(p99))
        if against:
            cells.append(fmt(r.get("output_diff_max_m")))
        if telemetry:
            tm = r.get("t7_telemetry") or {}
            work = tm.get("work") or {}
            t10 = tm.get("t10_change_m") or {}
            cells += [fmt(work.get("p99")), fmt(work.get("max")), fmt(tm.get("fallback_share")), fmt(t10.get("max"))]
        lines.append("| " + " | ".join(cells) + " |")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Quick draft bench of a T7 generator on the PP-T7 tuning part")
    parser.add_argument("generator", help="Name in research/generators/registry.yaml")
    parser.add_argument("--set", action="append", default=[], metavar="NAME=VALUE",
                        help="Calibration value (shared or the generator's own); repeatable")
    parser.add_argument("--telemetry", action="store_true", help="Build with PP_T7_TELEMETRY")
    parser.add_argument("--runs", choices=("quick", "tuning"), default="quick")
    parser.add_argument("--against", help="Label of an earlier quick result to show differences against")
    parser.add_argument("--jobs", type=int, default=1)
    args = parser.parse_args()

    suite = sweep.load_suite(SUITE)
    chosen = runs_for(args.runs, suite)
    values = parse_sets(args.set)
    cmake = cmake_of(args.generator)
    if args.telemetry:
        cmake["PP_T7_TELEMETRY"] = "ON"
    label = label_of(args.generator, values, args.telemetry)
    folder = OUT / label
    print(f"Build {label}", flush=True)
    lib = sweep._build(sweep.CalSet(label, values, tuple(sorted(cmake.items()))), folder)
    tasks = [(run, seed, str(lib), str(folder), f"open_loop/{i:03d}_s{seed}.npz")
             for i, (run, seed) in enumerate(chosen)]
    rows = []
    with slots.hold(args.jobs, f"quick {label}"):
        results = list(isolation.map_isolated(one, tasks, args.jobs, TIMEOUT_S))
    for (run, seed, *_), (status, value) in zip(tasks, results):
        if status != "ok":
            raise SystemExit(f"{run} seed {seed}: {status} {str(value).splitlines()[0] if value else ''}")
        rows.append(value)

    against = None
    if args.against:
        other = json.loads((OUT / args.against / "quick.json").read_text(encoding="utf-8"))
        against = {(r["run"], r["seed"]): r for r in other["rows"]}
        for r in rows:
            o = against.get((r["run"], r["seed"]))
            if o and r.get("open_loop_file") and o.get("open_loop_file"):
                stats = output_diff.compare_runs(output_diff.load(folder / r["open_loop_file"]),
                                                 output_diff.load(OUT / args.against / o["open_loop_file"]))
                r["output_diff_max_m"] = stats["max_m"]
                r["output_digest_mismatch"] = stats["digest_mismatch"]
    report = {"label": label, "generator": args.generator, "values": values, "cmake": cmake, "library": str(lib),
              "runs": args.runs, "against": args.against, "rows": rows}
    (folder / "quick.json").write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [f"# Quick bench {label} (nháp)", ""] + table(rows, against)
    (folder / "quick.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\n{folder / 'quick.md'}")


if __name__ == "__main__":
    main()

"""Run a whole benchmark for one planner, keep the log, write the HTML dashboard.

    python3 -m eval.run_full                        # full suite, 4 workers, MCAP for failed runs
    python3 -m eval.run_full --planner build/other/libpp_planner.dylib --jobs 4
    python3 -m eval.run_full --suite smoke --max-runs 6   # quick check of the pipeline

Steps, all into build/benchmark/<time>-<suite>-<planner commit>/:
  1  eval.generate <suite>      -> concrete/   (cases and manifest)
  2  eval.suite --continue-after-b0 -> suite/  (B0, then every run; nothing stops on a failure)
  3  eval.report_html           -> report.html (slides: overview, B0, B1..B8)
run.log keeps the output of every step with the time. A failing aspect suite, B0 failing or a
crash of the suite step never stops the next steps: the dashboard shows what was run.
Heavy: full is 3.916 runs, about 1.5-2 hours on 4 workers (MCAP and figures of failed runs extra).
"""

import argparse
from datetime import datetime
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


class Log:
    def __init__(self, path: Path):
        self.stream = path.open("a", encoding="utf-8")

    def __call__(self, line: str) -> None:
        stamped = f"{datetime.now():%H:%M:%S} {line.rstrip()}"
        print(stamped, flush=True)
        self.stream.write(stamped + "\n")
        self.stream.flush()


def step(log: Log, title: str, command: list[str]) -> int:
    log(f"== {title}: {' '.join(command)}")
    started = time.monotonic()
    process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, encoding="utf-8", errors="replace", bufsize=1)
    for line in process.stdout:
        log(line)
    code = process.wait()
    log(f"== {title}: mã thoát {code}, {(time.monotonic() - started) / 60:.1f} phút")
    return code


def planner_commit(planner: Path | None) -> str:
    try:
        from eval import planner_choice, provenance
        lib = planner_choice.resolve(planner)
        build = provenance.library_info(lib.path, external=planner is not None).get("build", {})
        return str(build.get("commit") or "planner")[:7]
    except Exception:
        return "planner"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--suite", choices=("smoke", "regression", "full"), default="full")
    parser.add_argument("--planner", type=Path, help="Planner library under test (default: as eval.suite)")
    parser.add_argument("--jobs", type=int, default=4, help="Worker processes; each holds one SIL log (8 GB: 4)")
    parser.add_argument("--mcap", choices=("failed", "all", "none"), default="failed",
                        help="MCAP logs: failed runs (default), every run (about 15 GB for full), none")
    parser.add_argument("--max-runs", type=int, help="Exploratory prefix only, to check the pipeline")
    parser.add_argument("--record", action="store_true", help="Official run (clean tree, research/register)")
    parser.add_argument("--out", type=Path, help="Run folder (default build/benchmark/<time>-<suite>-<commit>)")
    args = parser.parse_args()
    if args.record and args.max_runs:
        parser.error("--record needs every run")

    out = args.out or ROOT / "build" / "benchmark" / f"{datetime.now():%Y%m%d-%H%M}-{args.suite}-{planner_commit(args.planner)}"
    out.mkdir(parents=True, exist_ok=False)
    log = Log(out / "run.log")
    log(f"Benchmark {args.suite} -> {out}")
    py = sys.executable

    concrete = out / "concrete"
    if step(log, "1/3 sinh ca", [py, "-m", "eval.generate", args.suite, "--out", str(concrete)]) != 0:
        log("Không sinh được ca; dừng.")
        raise SystemExit(2)

    suite = out / "suite"
    command = [py, "-m", "eval.suite", str(concrete / "manifest.json"), "--out", str(suite),
               "--jobs", str(args.jobs), "--mcap", args.mcap, "--continue-after-b0"]
    if args.planner:
        command += ["--planner", str(args.planner)]
    if args.max_runs:
        command += ["--max-runs", str(args.max_runs)]
    if args.record:
        command.append("--record")
    code = step(log, "2/3 chạy bộ", command)
    if code not in (0, 1):  # 1 = some run failed, which is a result, not a crash
        log("Bước chạy bộ dừng bất thường; vẫn lập dashboard từ các lần chạy đã có.")

    log("== 3/3 lập dashboard")
    try:
        from eval import report_html
        report = report_html.write(suite, out / "report.html", generation=concrete / "manifest.json")
        log(f"Dashboard: {report}")
    except Exception as exc:  # the log and results stay; the dashboard can be rebuilt later
        log(f"Không lập được dashboard: {exc!r}. Lập lại: python3 -m eval.report_html {suite}")
        raise SystemExit(3)
    summary = suite / "summary.json"
    if summary.is_file():
        log(f"Tóm tắt: {summary.read_text(encoding='utf-8').strip()}")


if __name__ == "__main__":
    main()

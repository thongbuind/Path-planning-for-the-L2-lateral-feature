import json
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
REPORTS = ("report.html", "report-details.html", "report-en.html", "report-en-details.html")


def latest_benchmark(project=PROJECT):
    candidates = []
    for root in (project / "research" / "runs", project / "build" / "benchmark"):
        if not root.is_dir():
            continue
        for run in root.iterdir():
            match = re.match(r"^(\d{8})(?:-(\d{4}))?-", run.name)
            if not match or not run.is_dir() or not all((run / f).is_file() for f in REPORTS[:2]):
                continue
            data = run / "suite" if (run / "suite").is_dir() else run
            results, summary = data / "results.jsonl", data / "summary.json"
            if not summary.is_file() or not results.is_file() or not results.stat().st_size:
                continue
            try:
                if json.loads(summary.read_text(encoding="utf-8")).get("partial"):
                    continue
            except (OSError, ValueError):
                continue
            # Lấy ngày từ run ID, dùng mtime của kết quả để phân định các run cùng ngày.
            candidates.append(((match.group(1), results.stat().st_mtime_ns), run, data))
    if not candidates:
        return None
    _, run, data = max(candidates, key=lambda item: item[0])
    return {"run": str(run.resolve()), "data": str(data.resolve())}


if __name__ == "__main__":
    selected = latest_benchmark()
    if not selected:
        raise SystemExit("Không có benchmark đã hoàn tất với báo cáo")
    print(json.dumps(selected))

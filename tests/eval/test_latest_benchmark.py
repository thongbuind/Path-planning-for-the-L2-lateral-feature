import importlib.util
from pathlib import Path


spec = importlib.util.spec_from_file_location("latest_benchmark", Path(__file__).parents[2] / "web" / "latest_benchmark.py")
latest = importlib.util.module_from_spec(spec)
spec.loader.exec_module(latest)


def test_selects_latest_complete_run_and_ignores_empty_or_incomplete(tmp_path):
    def make(root, name, *, complete=True, results="{}\n"):
        run = tmp_path / root / name
        data = run / "suite" if root == "build/benchmark" else run
        data.mkdir(parents=True)
        for report in latest.REPORTS[:None if complete else 1]:
            (run / report).write_text("report")
        (data / "summary.json").write_text("{}")
        (data / "results.jsonl").write_text(results)
        return run

    make("research/runs", "20261115-1126-suite-full-abc")
    expected = make("build/benchmark", "20261116-1000-full-abc")
    make("build/benchmark", "20261117-1000-full-abc", results="")
    make("build/benchmark", "20261118-1000-full-abc", complete=False)
    selected = latest.latest_benchmark(tmp_path)
    assert selected == {"run": str(expected), "data": str(expected / "suite")}

    newest = make("build/benchmark", "20261119-1000-full-abc")
    (newest / "report-en.html").unlink()
    (newest / "report-en-details.html").unlink()
    assert latest.latest_benchmark(tmp_path)["run"] == str(newest)

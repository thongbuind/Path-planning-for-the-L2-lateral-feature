import json

import pytest

from eval import provenance, run_artifacts
from workbench import compare, evidence


def test_archived_suite_restores_reports_and_workbench_files(tmp_path, monkeypatch):
    store = tmp_path / "artifacts"
    run_artifacts.prepare_store(store)
    original = tmp_path / "original"
    original.mkdir()
    concrete = original / "concrete"
    concrete.mkdir()
    case, road = concrete / "c1.xosc", concrete / "c1.xodr"
    case.write_text("scenario")
    road.write_text("road")
    generation = {"suite": "smoke", "definition": {}, "runs": [{"case": "c1", "seed": 1}],
                  "cases": [{"id": "c1", "family": "S1", "file": case.name, "parameters": {},
                             "sha256": provenance.sha256(case), "road_sha256": provenance.sha256(road)}]}
    manifest_path = concrete / "manifest.json"
    manifest_path.write_text(json.dumps(generation))
    suite = original / "suite"
    suite.mkdir()
    (suite / "generation.json").write_text(json.dumps(generation))
    (suite / "conformance.json").write_text('{"checks": [], "blocked": false, "integrable": true}')
    result = {"case": "c1", "seed": 1, "labels": {}, "aspects": [], "result": {"criteria": []}}
    (suite / "results.jsonl").write_text(json.dumps(result) + "\n")
    (suite / "conclusion.json").write_text('{}')
    (suite / "summary.json").write_text('{"executed": 1, "partial": false}')
    (suite / "report.md").write_text('# Suite')
    manifest = {"run_id": "20261121-1200-suite-smoke-abcdef0", "target": "smoke", "kind": "suite",
                "git": {"commit": "abcdef0123", "short": "abcdef0", "dirty": False}, "libraries": [],
                "generation": {"sha256": provenance.sha256(manifest_path)}}
    artifact = run_artifacts.pack(store, manifest, suite, manifest_path)

    records = tmp_path / "records"
    monkeypatch.setattr(provenance, "RUNS_DIR", records)
    monkeypatch.setattr(provenance, "INDEX", records / "INDEX.md")
    record = provenance.record({**manifest, "artifact": artifact},
                               {name: suite / name for name in run_artifacts.RECORD_FILES if name != "manifest.json"},
                               "complete")
    assert {p.name for p in record.iterdir()} == set(run_artifacts.RECORD_FILES)
    assert manifest["run_id"] in provenance.INDEX.read_text()

    benchmark = tmp_path / "benchmark"
    restored = run_artifacts.restore(record, store, benchmark)
    assert (restored / "concrete" / case.name).read_bytes() == case.read_bytes()
    assert (restored / "suite" / "results.jsonl").read_bytes() == (suite / "results.jsonl").read_bytes()
    assert 'href="suite/results.jsonl"' in (restored / "report.html").read_text()
    assert (restored / "report-en-details.html").is_file()
    monkeypatch.setattr(evidence, "BENCH", benchmark)
    assert compare.load_suite(restored.name)["runs_total"] == 1

    with pytest.raises(FileExistsError):
        run_artifacts.restore(record, store, benchmark)
    with (store / artifact["file"]).open("ab") as stream:
        stream.write(b"corrupt")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        run_artifacts.restore(record, store, tmp_path / "tampered")
    assert not (tmp_path / "tampered").exists()

"""Benchmark dashboard from an eval.suite folder (Software Qualification Test Specification 10)."""

import json
import re
import sys

import pytest

from eval import conclusion, report_html, run_full


def _case(cid, family, profile="VP-0"):
    return {"id": cid, "family": family, "host": None, "anchor": "a", "methods": ["anchor"],
            "source": f"benchmark/scenarios/{family}.xosc", "file": f"cases/{cid}.xosc",
            "parameters": {"profile": profile, "duration_s": 36.0, "description": "x"}}


def _record(cid, aspects, failed=(), offset=0.1):
    criteria = [{"id": rid, "metric": "m", "value": 1.0, "limit": "<= 0", "passed": False,
                 "applicable": True, "first_fail_s": 1.0} for rid in failed]
    hist = [0] * 60
    hist[30] = 100
    return {"case": cid, "seed": 1, "profile": "VP-0", "labels": {"expected": "drive"}, "aspects": aspects,
            "scope": None, "failed": list(failed), "mcap": None, "rerun": "cmd",
            "result": {"criteria": criteria, "issues": [], "case_failures": [],
                       "targets": [{"id": "PP-SWR-053", "metric": "a_y thêm vào", "value": 0.2}],
                       "info": {"vehicle_offset_max_m": offset, "compute_hist": hist, "other": [1] * 1000}}}


def _suite(folder, records, cases, b0=True, generation=True, manifest=True):
    folder.mkdir()
    gen = {"suite": "full", "definition": {"scenarios": ["S1", "S4"], "faults": [], "profiles": ["VP-0"]},
           "cases": cases, "runs": [{"case": c["id"], "seed": 1} for c in cases]}
    if generation:
        (folder / "generation.json").write_text(json.dumps(gen), encoding="utf-8")
    if manifest:
        (folder / "manifest.json").write_text(json.dumps({"libraries": [{"pp_version": "pp 0.1", "sha256": "ab" * 32}]}))
    if b0:
        checks = [{"id": "C1.symbols", "status": "pass", "title": "Có đủ symbol"},
                  {"id": "C2.robust", "status": "fail", "title": "Không dừng", "detail": "inf"}]
        (folder / "conformance.json").write_text(json.dumps({"checks": checks, "blocked": True, "integrable": False}))
    (folder / "results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
    return gen


def test_ten_core_slides_and_metadata_with_b0_after_overview(tmp_path):
    cases = [_case("c1", "S1"), _case("c2", "S4")]
    _suite(tmp_path / "s", [_record("c1", ["B1", "B8"]), _record("c2", ["B1", "B8"], failed=["PP-SWR-051"])], cases)
    html = report_html.write(tmp_path / "s").read_text(encoding="utf-8")
    titles = re.findall(r'<div class="title">([^<]+)</div>', html)
    assert len(titles) == 11 and titles[1] == "B0 · Conformance"
    assert [t.split(" · ")[0] for t in titles[2:10]] == [f"B{i}" for i in range(1, 9)]
    assert "11 / 11" in html and "Input biên không làm dừng" in html  # B0 failing check by its name
    legends = re.findall(r'<div class="card fit".*?</div></div></div>', html, re.S)
    assert legends and all("…" not in x for x in legends)  # legend text is never cut


def test_aspect_verdict_from_failure_levels(tmp_path):
    blocker = report_html.aspect_stats([_record("c1", ["B1"], failed=["PP-SWR-051"]), _record("c2", ["B1"])])
    assert blocker["verdict"] == conclusion.BLOCKED and blocker["passed"] == 1 and blocker["runs"] == 2
    assert report_html.aspect_stats([_record("c1", ["B1"])])["verdict"] == conclusion.NO_BLOCKER


def test_stopped_suite_still_reports(tmp_path):
    cases = [_case("c1", "S1"), _case("c2", "S4"), _case("c3", "S4")]
    gen = _suite(tmp_path / "s", [_record("c1", ["B1"])], cases, generation=False, manifest=False)
    with (tmp_path / "s" / "results.jsonl").open("a") as stream:
        stream.write('{"case": "c2", "seed"')  # cut while writing
    with pytest.raises(FileNotFoundError):
        report_html.write(tmp_path / "s")
    (tmp_path / "gen.json").write_text(json.dumps(gen))
    html = report_html.write(tmp_path / "s", generation=tmp_path / "gen.json").read_text(encoding="utf-8")
    assert "Chưa chạy hết: 1 / 3 lần chạy" in html


def test_records_are_slimmed(tmp_path):
    cases = [_case("c1", "S1")]
    _suite(tmp_path / "s", [_record("c1", ["B1"], failed=["PP-SWR-051"])], cases)
    r = report_html.load(tmp_path / "s")["records"][0]
    assert "other" not in r["result"]["info"] and r["result"]["criteria"] == []
    assert [f["requirement"] for f in r["_fail"]] == ["PP-SWR-051"]


def test_run_full_step_logs_output_and_exit_code(tmp_path):
    log = run_full.Log(tmp_path / "run.log")
    code = run_full.step(log, "thử", [sys.executable, "-c", "print('xin chào'); raise SystemExit(1)"])
    text = (tmp_path / "run.log").read_text(encoding="utf-8")
    assert code == 1 and "xin chào" in text and "mã thoát 1" in text


def test_near_limit_never_rounds_below_limit_up_to_100():
    assert report_html.limit_percent(.999) == "99,90 %"
    assert report_html.limit_percent(.999999999) == "< 100 %"
    assert report_html.limit_percent(1) == "100,00 %"
    assert report_html.precise(0.000000001) != "0"


def test_units_and_observed_behavior_survive_slimming():
    r = _record("c1", ["B5", "B6"])
    r["result"]["targets"][0]["unit"] = "s"
    r["result"]["criteria"].append({"id":"PP-SWR-089", "metric":"ELK démarrage", "value":0,
                                     "limit":"= 0", "applicable":True, "passed":True})
    result = report_html._slim(r)
    assert result["result"]["targets"][0]["unit"] == "s"
    assert result["_behavior"][0]["id"] == "PP-SWR-089"
    assert result["_behavior"][0]["passed"] is True


def test_profile_comparison_uses_parameters_and_seed():
    a = {"_case":_case("a", "S1", "VP-0"), "seed":1}
    b = {"_case":_case("b", "S1", "VP-1"), "seed":1}
    assert report_html.profile_signature(a) == report_html.profile_signature(b)
    b["_case"]["parameters"]["speed_mps"] = 10
    assert report_html.profile_signature(a) != report_html.profile_signature(b)


def test_b0_evidence_is_written(tmp_path):
    cases = [_case("c1", "S1")]
    _suite(tmp_path / "s", [_record("c1", ["B3", "B6"], failed=["PP-SWR-051"])], cases)
    out = report_html.write(tmp_path / "s")
    main = out.read_text()
    details = (out.parent / "report-details.html").read_text()
    assert 'id="C2.robust"' in details and 'inf' in details
    assert 'Chưa ghi nhận cho lượt chạy này' in main


def test_english_report_localizes_legacy_run_data(tmp_path):
    folder = tmp_path / "s"
    case = _case("c1", "S1")
    record = _record("c1", ["B1", "B6"], failed=["PP-SWR-051"])
    record["result"]["targets"] = [{"id": "PP-SWR-004", "value": 0.5, "unit": "rad/s",
                                     "metric": "Tốc độ quay vô lăng RMS khi HWA lái, vòng kín"}]
    _suite(folder, [record], [case])
    b0 = folder / "conformance.json"
    checks = json.loads(b0.read_text())
    checks["checks"][1]["detail"] = "longitudinal_plan đầu cao của dải: chu kỳ 0: acceleration = inf"
    b0.write_text(json.dumps(checks), encoding="utf-8")

    out = report_html.write(folder, lang="en")
    main = out.read_text(encoding="utf-8")
    details = out.with_name("report-en-details.html").read_text(encoding="utf-8")

    assert out.name == "report-en.html"
    assert '<html lang="en">' in main and '<html lang="en">' in details
    assert '✕ Fail' in main and 'report-en-details.html#C2.robust' in main
    assert 'longitudinal_plan upper range endpoint: cycle 0: acceleration = inf' in details
    assert 'RMS steering wheel rate [rad/s]' in main and '0.5 rad/s' in main
    assert 'id="PP-SWR-156"' in details and 'id="run-c1-1"' in details


def test_one_colour_set():
    """Every colour comes from the token block at the top; no hex literal elsewhere."""
    import re
    from pathlib import Path
    src = Path(report_html.__file__).read_text(encoding="utf-8")
    after_tokens = src.split("CSS_VARS = (", 1)[1]
    assert re.findall(r"#[0-9a-fA-F]{6}\b", after_tokens) == []


def test_nice_ticks_are_round():
    assert report_html.nice_ticks(0, 3.87) == [0, 1, 2, 3, 4]
    assert report_html.nice_ticks(-0.38, 0.36) == [-0.4, -0.2, 0, 0.2, 0.4]

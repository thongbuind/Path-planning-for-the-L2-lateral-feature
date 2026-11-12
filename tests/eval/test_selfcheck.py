"""Severity from the Software Requirements Specification (Software Qualification Test
Specification 8.4) and the evaluator self-check with bait planners (section 12)."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from eval import selfcheck, severity

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("check, level", [
    ("PP-SWR-001", "BLOCKER"),   # Regulatory, SG-01
    ("PP-SWR-100", "BLOCKER"),   # Safety, SG-04
    ("PP-SWR-014", "BLOCKER"),   # Interface
    ("PP-SWR-050", None),        # Performance target
    ("C2.counter", "BLOCKER"),
    ("C3.memory", None),         # removes the Integrable flag only
    (severity.EXECUTION_FAULT, "BLOCKER"),
])
def test_level_follows_the_type_column(check, level):
    assert severity.level(check) == level


def test_every_type_in_the_specification_has_a_level_rule():
    kinds = {w.strip() for t in severity.requirement_types().values() for w in t.split(",")}
    assert kinds <= {"Safety", "Regulatory", "Functional", "Interface", "Performance"} | {
        k for k in kinds if k.startswith("SG-")}
    assert any(severity.level(i) == "MINOR" for i in severity.requirement_types())


def test_unknown_requirement_is_an_error():
    with pytest.raises(KeyError):
        severity.level("PP-SWR-999")


def _judged(b0=(), runs=()):
    return {"b0_failed": list(b0), "runs": list(runs)}


BAIT = {"expect": ["PP-SWR-100"], "level": "BLOCKER", "runs": [["S1", "a"]]}


def test_detected_only_when_the_control_does_not_fail_the_same_id_on_the_same_case():
    bait = _judged(runs=[{"run": "S1 a seed 1", "failed": ["PP-SWR-100"], "judged_ids": ["PP-SWR-100"]}])
    clean = _judged(runs=[{"run": "S1 a seed 1", "failed": ["PP-SWR-051"]},
                          {"run": "S1b a seed 1", "failed": ["PP-SWR-100"]}])  # other case: does not count
    assert selfcheck.verdict(BAIT, bait, clean)[0] == "đạt"
    assert selfcheck.verdict(BAIT, bait, bait)[0] == "không phân biệt"


def test_missing_criterion_and_wrong_level_are_reported():
    no_criterion = _judged(runs=[{"failed": [], "judged_ids": ["PP-SWR-001"]}])
    assert "không chấm PP-SWR-100" in selfcheck.verdict(BAIT, no_criterion, _judged())[1]
    wrong = {**BAIT, "level": "MINOR"}
    hit = _judged(runs=[{"failed": ["PP-SWR-100"], "judged_ids": ["PP-SWR-100"]}])
    assert selfcheck.verdict(wrong, hit, _judged())[0] == "sai mức"


def test_suite_matches_the_table_of_section_12():
    suite = selfcheck.load_suite()
    assert list(suite["baits"]) == [f"PM-{i:02d}" for i in range(1, 10)]
    for bait in suite["baits"].values():
        for check in bait["expect"]:
            assert severity.level(check) == bait["level"]


@pytest.mark.skipif(shutil.which("cc") is None, reason="no C compiler")
@pytest.mark.parametrize("define", [None] + [f"PM_{i:02d}" for i in range(1, 10)])
def test_bait_sources_build_without_warnings(tmp_path, define):
    subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Wpedantic", "-Werror", "-shared", "-fPIC",
                    f"-I{ROOT / 'interfaces' / 'c'}", *([f"-D{define}"] if define else []),
                    str(selfcheck.SOURCE), "-o", str(tmp_path / f"lib{define}.so"), "-lm"],
                   check=True, capture_output=True)


@pytest.mark.skipif(shutil.which("cc") is None, reason="no C compiler")
def test_conformance_baits_are_detected(tmp_path):
    proc = subprocess.run([sys.executable, "-m", "eval.selfcheck", "--only", "PM-05,PM-08", "--b0-only",
                           "--out", str(tmp_path)], cwd=ROOT, capture_output=True, text=True)
    summary = (tmp_path / "summary.md").read_text(encoding="utf-8")
    assert "| PM-05 |" in summary and "| PM-08 |" in summary
    assert summary.count("| đạt |") == 2, summary
    assert proc.returncode == 0


def test_numpy_scalars_in_a_result_are_written_as_json():
    import json

    import numpy as np

    from eval import report
    assert json.loads(json.dumps({"passed": np.bool_(True), "v": np.float32(0.5)}, default=report.jsonable)) \
        == {"passed": True, "v": 0.5}

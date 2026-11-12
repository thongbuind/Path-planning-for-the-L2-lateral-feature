"""Comparison between planners (Software Qualification Test Specification 9.2) on synthetic
eval.suite output folders."""

import json

import numpy as np
import pytest

from eval import compare, severity

FUNCTIONAL = next(i for i, t in severity.requirement_types().items() if t == "Functional")


def _case(cid, family, profile, description="", protocol=""):
    return {"id": cid, "family": family, "anchor": "a", "methods": ["anchor"],
            "parameters": {"profile": profile, "description": description, "protocol": protocol,
                           "variant": cid.rsplit("-VP-", 1)[0]}}


def _record(cid, seed, profile, targets=(), failed=(), passed=(), info=None):
    criteria = [{"id": i, "metric": "m", "value": 1.0, "limit": "x", "passed": False, "applicable": True}
                for i in failed] + [{"id": i, "metric": "m", "value": 0.0, "limit": "x", "passed": True,
                                     "applicable": True} for i in passed]
    return {"case": cid, "seed": seed, "profile": profile, "scope": None,
            "result": {"criteria": criteria, "issues": [], "case_failures": [], "info": info or {},
                       "targets": [{"id": i, "metric": m, "value": v, "unit": ""} for i, m, v in targets]}}


def _folder(tmp_path, name, cases, records, b0=None, generation="g1"):
    folder = tmp_path / name
    folder.mkdir()
    (folder / "manifest.json").write_text(json.dumps({
        "libraries": [{"pp_version": name, "sha256": "0" * 64}], "generation": {"sha256": generation},
        "summary": {"partial": False}}))
    (folder / "generation.json").write_text(json.dumps({"cases": cases}))
    (folder / "results.jsonl").write_text("\n".join(json.dumps(r) for r in records))
    if b0 is not None:
        (folder / "conformance.json").write_text(json.dumps(b0))
    return compare.load(folder)


CASES = [_case(f"S1-{i}-{p}", "S1", p) for i in range(8) for p in ("VP-0", "VP-1")]


def _runs(lateral, failed=()):
    """S1 runs with PP-SWR-050 = lateral(i, profile)."""
    return [_record(c["id"], 1, c["parameters"]["profile"],
                    targets=[("PP-SWR-050", "Lệch ngang", lateral(i, c["parameters"]["profile"]))],
                    failed=failed if i == 0 else ())
            for i, c in enumerate(CASES)]


def test_conclusion_ranks_first_then_pairwise_wins(tmp_path):
    good = _folder(tmp_path, "good", CASES, _runs(lambda i, p: 0.10 + 0.001 * i))
    worse = _folder(tmp_path, "worse", CASES, _runs(lambda i, p: 0.20 + 0.001 * i))
    blocked = _folder(tmp_path, "blocked", CASES, _runs(lambda i, p: 0.01, failed=["PP-SWR-100"]))
    c = compare.compare([worse, blocked, good])
    assert c["order"] == ["good", "worse", "blocked"]  # blocked last although its path is best
    # Copeland over every planner that passed C1 and C2, blocked ones included (9.2).
    score = {n: c["rows"][n]["copeland"]["An toàn"] for n in c["order"]}
    assert score == {"good": 0, "worse": -2, "blocked": 2}
    assert c["rows"]["blocked"]["tier1"]["verdict"] == "Bị chặn"


def test_fewer_blocker_requirements_rank_higher_within_blocked(tmp_path):
    one = _folder(tmp_path, "one", CASES, _runs(lambda i, p: 0.1, failed=["PP-SWR-100"]))
    two = _folder(tmp_path, "two", CASES, _runs(lambda i, p: 0.1, failed=["PP-SWR-100", "PP-SWR-001"]))
    assert compare.compare([two, one])["order"] == ["one", "two"]


def test_noisy_difference_is_a_tie_and_direction_follows_better_when():
    rng = np.random.default_rng(1)
    lo, hi = compare.bootstrap_interval(rng.normal(0, 1, 30))
    assert lo < 0 < hi
    lo, hi = compare.bootstrap_interval(np.full(30, 0.2) + rng.normal(0, 0.01, 30))
    assert lo > 0
    assert "PP-SWR-087" in compare.LARGER_IS_BETTER  # DTLE: larger is better (8.2)


def test_flexibility_uses_the_spread_between_profiles(tmp_path):
    even = _folder(tmp_path, "even", CASES, _runs(lambda i, p: 0.1 + 0.01 * i))
    uneven = _folder(tmp_path, "uneven", CASES, _runs(lambda i, p: 0.1 + 0.01 * i + (0.05 if p == "VP-1" else 0)))
    d = compare.pairwise(even, uneven, ("PP-SWR-050", "Lệch ngang"), flexibility=True)
    assert d["units"] == 8 and d["result"] == 1


def test_ncap_line_needs_every_row_and_takes_the_worst_profile(tmp_path):
    cases, records = [], []
    for profile in ("VP-0", "VP-1"):
        for k in range(5):
            cid = f"S4-d{k}-{profile}"
            cases.append(_case(cid, "S4", profile, f"Euro NCAP LSS dashed-left-{k + 2}", "Euro NCAP LSS"))
            ok = not (profile == "VP-1" and k == 3)
            records.append(_record(cid, 1, profile, passed=["PP-SWR-086"] if ok else (),
                                   failed=() if ok else ["PP-SWR-086"]))
        cid = f"S7-o-{profile}"
        cases.append(_case(cid, "S7", profile, "Euro NCAP LSS oncoming-left-2", "Euro NCAP LSS"))
        records.append(_record(cid, 1, profile, info={"no_impact": True}))
    p = _folder(tmp_path, "p", cases, records)
    n = compare.ncap_points(p)
    assert n["per_profile"]["VP-0"]["points"] == 0.75 and n["per_profile"]["VP-1"]["points"] == 0.5
    assert n["points"] == 0.5  # one calibration for every vehicle: the worst profile counts
    assert n["per_profile"]["VP-0"]["lines"]["LKA, vạch liền"] is None


def test_pass_rate_of_major_and_minor_requirements(tmp_path):
    records = [_record(c["id"], 1, c["parameters"]["profile"], failed=[FUNCTIONAL] if i < 4 else (),
                       passed=[FUNCTIONAL] if i >= 4 else ()) for i, c in enumerate(CASES)]
    p = _folder(tmp_path, "p", CASES, records)
    assert compare.pass_rate(p)["mean"] == pytest.approx(12 / 16)


def test_other_benchmark_or_b0_blocked_planner(tmp_path):
    a = _folder(tmp_path, "a", CASES, _runs(lambda i, p: 0.1))
    b = _folder(tmp_path, "b", CASES, _runs(lambda i, p: 0.1), generation="g2")
    with pytest.raises(SystemExit, match="another generated suite"):
        compare.compare([a, b])
    blocked = _folder(tmp_path, "c", CASES, _runs(lambda i, p: 0.1),
                      b0={"checks": [], "blocked": True, "integrable": False})
    c = compare.compare([a, blocked])
    assert c["excluded_b0"] == ["c"] and c["order"] == ["a"]
    assert "Không so (trượt C1 hoặc C2): c" in "\n".join(compare.markdown(c))

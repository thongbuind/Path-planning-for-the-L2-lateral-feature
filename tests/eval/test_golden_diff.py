from eval import golden


def report(rows, numpy="2.0", suite="PP-T7"):
    return {"environment": {"platform": "darwin-arm64", "python": "3.12", "numpy": numpy, "library_sha256": "x"},
            "suite": suite, "part": "tuning",
            "results": [{"case": c, "seed": s, "path": "runner", "status": "ok", "case_hash": h, "checksum": k}
                        for c, s, h, k in rows]}


BASE = [("[\"S1\", \"a\"]", 1, "h1", "c1"), ("[\"S1\", \"a\"]", 2, "h2", "c2")]


def test_same_behaviour_with_another_library_is_clean():
    other = report(BASE)
    other["environment"]["library_sha256"] = "y"
    assert golden.diff_problems(other, report(BASE)) == []


def test_checksum_case_and_coverage_differences_are_reported():
    changed = report([BASE[0][:3] + ("cX",), ("[\"S1\", \"b\"]", 1, "h3", "c3")])
    found = golden.diff_problems(changed, report(BASE))
    assert any("seed1: checksum differs" in f for f in found)
    assert any("only in the reference" in f for f in found)
    assert any("only in this run" in f for f in found)
    assert any("case_hash differs" in f for f in golden.diff_problems(report([BASE[0][:2] + ("hZ", "c1"), BASE[1]]),
                                                                       report(BASE)))


def test_another_machine_or_suite_is_refused():
    assert any("numpy" in f for f in golden.diff_problems(report(BASE, numpy="1.26"), report(BASE)))
    assert any("different runs" in f for f in golden.diff_problems(report(BASE, suite="PP-T4"), report(BASE)))

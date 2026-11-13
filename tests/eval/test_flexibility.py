"""Flexibility table (Software Qualification Test Specification 8.3): B7 runs only, rate of
requirements passed per profile."""

from eval import presentation


def _run(profile, failed=(), aspects=("B7",), judged=("PP-SWR-001", "PP-SWR-051")):
    criteria = [{"id": r, "metric": r, "value": 1.0, "limit": "", "applicable": True,
                 "passed": r not in failed, "first_fail_s": None} for r in judged]
    return {"case": f"S1-a-{profile}", "seed": 1, "profile": profile, "aspects": list(aspects),
            "scope": list(judged), "failed": list(failed),
            "result": {"criteria": criteria, "targets": [], "issues": [], "case_failures": []}}


def test_rate_counts_requirements_not_runs_and_only_b7():
    records = [_run("VP-0"), _run("VP-0", failed=["PP-SWR-051"]), _run("VP-1"),
               _run("VP-1", failed=["PP-SWR-001"], aspects=("B4",))]  # not in B7: ignored
    text = "\n".join(presentation.flexibility(records, {}))
    assert "| VP-0 | 2 | 50.0% | PP-SWR-051 |" in text
    assert "| VP-1 | 1 | 100.0% | — |" in text
    assert "trên mọi profile: không (VP-0)" in text

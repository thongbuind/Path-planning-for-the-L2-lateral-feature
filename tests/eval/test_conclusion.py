"""Conclusion and severity of a report (Software Qualification Test Specification 8.4, 10)."""

import math
from dataclasses import dataclass

from eval import conclusion, metrics


def _run(criteria=(), issues=(), scope=None, **extra):
    result = {"criteria": [{"id": i, "metric": "m", "value": v, "limit": "<= 1", "passed": False,
                            "applicable": True, "first_fail_s": t} for i, v, t in criteria],
              "issues": list(issues), "case_failures": [x["text"] for x in issues]}
    return {"case": "S1a", "profile": "VP-0", "seed": 1, "result": result, "scope": scope,
            "mcap": "x.mcap", "rerun": "cmd", **extra}


def test_levels_give_the_three_conclusions():
    assert conclusion.conclude([_run()])["verdict"] == conclusion.NO_BLOCKER
    c = conclusion.conclude([_run([("PP-SWR-100", 0.1, 3.2)])])
    assert c["verdict"] == conclusion.BLOCKED
    row = c["failures"][0]
    assert (row["requirement"], row["safety_goals"], row["first_fail_s"], row["mcap"]) == \
        ("PP-SWR-100", ["SG-04"], 3.2, "x.mcap")


def test_minor_only_is_no_blocker():
    from eval import severity
    functional = next(i for i, t in severity.requirement_types().items() if t == "Functional")
    c = conclusion.conclude([_run([(functional, 1.0, None)])])
    assert c["verdict"] == conclusion.NO_BLOCKER and c["counts"]["MINOR"] == 1


def test_only_failures_in_scope_count():
    c = conclusion.conclude([_run([("PP-SWR-100", 0.1, 1.0)], scope=["PP-SWR-001"])])
    assert c["verdict"] == conclusion.NO_BLOCKER
    assert [f["requirement"] for f in c["out_of_scope"]] == ["PP-SWR-100"]


def test_case_issues_execution_and_not_judged():
    issues = [{"kind": "requirement", "requirement": "PP-SWR-030", "text": "LKA: thiếu path", "first_fail_s": None},
              {"kind": "not_judged", "requirement": None, "text": "LKA: thiếu REQUEST", "first_fail_s": None}]
    c = conclusion.conclude([_run(issues=issues), {"case": "S2a", "seed": 1, "execution": "Lỗi thực thi: signal 11"},
                             {"case": "S3a", "seed": 1, "error": "KeyError"}])
    assert c["verdict"] == conclusion.BLOCKED
    assert {f["requirement"] for f in c["failures"]} == {"PP-SWR-030", "execution"}
    assert len(c["not_judged"]) == 2  # precondition, evaluator error
    text = "\n".join(conclusion.markdown(c, "lib"))
    assert text.startswith("# Kết luận: Không đạt\n") and "## Trượt BLOCKER" in text and "## Ca không được chấm" in text


def test_b0_blocks_and_sets_the_integrable_flag():
    b0 = {"checks": [{"id": "C2.counter", "status": "fail", "level": "C2", "title": "t", "detail": "d"}],
          "blocked": True, "integrable": False}
    c = conclusion.conclude([], b0)
    assert c["verdict"] == conclusion.BLOCKED and c["integrable"] is False and c["b0_blocked"]
    ok = conclusion.conclude([], {"checks": [], "blocked": False, "integrable": True})
    assert ok["integrable"] is True and ok["verdict"] == conclusion.NO_BLOCKER


def test_nan_in_an_output_is_an_execution_fault():
    @dataclass
    class Point:
        x: float

    @dataclass
    class Cycle:
        t0_us: int
        trajectory: object
        path_status: object = None
        lateral_limits: object = None

    assert metrics.execution_fault([Cycle(25_000, (Point(1.0),))]) is None
    t, field = metrics.execution_fault([Cycle(25_000, (Point(1.0),)), Cycle(50_000, (Point(math.nan),))])
    assert (round(t, 6), field) == (0.05, "trajectory[0].x")


def test_nonfinite_matches_reference_walk():
    """eval.metrics._nonfinite with cached field names gives the path of the old walk."""
    from dataclasses import dataclass, field
    import numpy as np
    from eval import metrics

    def reference(value, path):
        if isinstance(value, float):
            return None if np.isfinite(value) else path
        if hasattr(value, "__dataclass_fields__"):
            for name in value.__dataclass_fields__:
                found = reference(getattr(value, name), f"{path}.{name}")
                if found:
                    return found
        elif isinstance(value, (list, tuple)):
            for i, item in enumerate(value):
                found = reference(item, f"{path}[{i}]")
                if found:
                    return found
        return None

    @dataclass
    class Empty:
        pass

    @dataclass
    class Point:
        x: float
        tags: tuple = ()

    @dataclass
    class Msg:
        points: list = field(default_factory=list)
        e: Empty = field(default_factory=Empty)
        n: int = 3
        a: object = None

    bad = [float("nan"), float("inf"), -float("inf"), np.float64("nan"), np.float64(np.inf)]
    good = [0.0, -0.0, 1e308, np.float64(2.5), np.float32(np.nan), 7, "nan"]
    for value in bad + good:
        for msg in (value, Msg([Point(1.0), Point(value)]), Msg(a=(Point(0.0, (1.0, value)),)), [Empty(), value]):
            assert metrics._nonfinite(msg, "m") == reference(msg, "m")

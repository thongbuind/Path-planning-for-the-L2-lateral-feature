"""Scope of a run (Software Qualification Test Specification 8.1; PP-TS-015 V1)."""

import yaml

from eval import matrix, sweep


def test_base_is_owned_by_scope_file_and_equals_p1_start():
    p1 = sweep.load_suite("P1")["scope"]
    obsolete = {"PP-SWR-083"}  # PP-TS-016
    assert ({k: sorted(v) for k, v in matrix.SCOPE["base"].items()}
            == {k: sorted(set(v) - obsolete) for k, v in p1.items()})
    for name in ("Q1", "Q2", "Q3", "Q4", "M1"):
        suite = yaml.safe_load((sweep.SUITE_DIR / f"{name}.yaml").read_text(encoding="utf-8"))
        assert suite["scope_from"] == "scope"


def test_fault_on_host_gets_host_and_fault_scope():
    plain = matrix.scope(matrix.SCOPE, ["S1", "a"])
    fault = matrix.scope(matrix.SCOPE, ["S1", "a", "F06", "a"])
    assert "PP-SWR-051" in plain and plain <= fault
    assert "PP-SWR-125" in fault


def test_scenario_variant_named_as_another_anchor_gets_its_scope():
    rain = matrix.scope(matrix.SCOPE, ["S12", "a"])
    assert matrix.scope(matrix.SCOPE, ["S1", "c"]) <= rain
    assert "PP-SWR-032" in matrix.scope(matrix.SCOPE, ["S12", "b"])
    assert "PP-SWR-005" in matrix.scope(matrix.SCOPE, ["S14", "a"])
    assert "PP-SWR-005" not in matrix.scope(matrix.SCOPE, ["S14", "e"])  # not an anchor of S1b
    assert "PP-SWR-051" not in matrix.scope(matrix.SCOPE, ["S12", None])  # sampled case


def test_case_scope_uses_the_real_host():
    on_c = {"id": "x", "family": "F01", "host": "S1c", "anchor": "a"}
    legacy = {"id": "y", "family": "F01", "host": None, "anchor": "a"}
    assert matrix.case_scope(on_c) == matrix.scope(matrix.SCOPE, ["S1", "c", "F01", "a"])
    assert matrix.case_scope(legacy) == matrix.scope(matrix.SCOPE, ["S1", "a", "F01", "a"])
    assert matrix.split_host("S1ba") == ["S1b", "a"]
    injected = {"id": "z", "family": "G01", "host": "S1c", "anchor": None,
                "scope_keys": [["S1", "c"], ["S1", "c", "F01", "c"]]}
    assert "PP-SWR-051" in matrix.case_scope(injected)

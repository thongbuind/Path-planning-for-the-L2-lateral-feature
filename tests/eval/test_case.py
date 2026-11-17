"""Resolved case (eval.case): recipes, identity, inputs (SIM-REQ-025, 029)."""

import ast
from dataclasses import replace
from pathlib import Path

import pytest

from eval import case, loader

ROOT = Path(__file__).resolve().parents[2]


def test_catalog_recipe_matches_loader_and_with_fault():
    recipe = {"kind": "catalog", "sid": "S4", "v": "a", "faults": [["F04", "a"]],
              "trigger": "lka_active", "offset_s": 0.2}
    built = case.resolve(recipe)
    direct = loader.with_fault(loader.load("S4", "a"), "F04", "a", "lka_active", 0.2)
    assert case.case_hash(built) == case.case_hash(direct)


def test_case_hash_ignores_name_and_notes_only():
    base = case.resolve({"kind": "catalog", "sid": "S1", "v": "a"})
    assert case.case_hash(replace(base, name="other", notes={"x": 1})) == case.case_hash(base)
    assert case.case_hash(replace(base, speed_mps=base.speed_mps + 1e-9)) != case.case_hash(base)


def test_modifiers_change_the_identity():
    base = {"kind": "catalog", "sid": "S1", "v": "c"}
    hashes = {case.case_hash(case.resolve({**base, **mod})) for mod in (
        {}, {"vehicle": "VP-4"}, {"sim": {"road_mu": 0.5}}, {"faults": [["F14", "a"]]}, {"acc": "on"})}
    assert len(hashes) == 5


@pytest.mark.parametrize("recipe", [
    {"kind": "catalog", "sid": "S1"},
    {"kind": "catalog", "sid": "S1", "v": "a", "faults": [["F4", "a"]]},
    {"kind": "catalog", "sid": "S1", "v": "a", "sim": {"road_mu": 2.0}},
    {"kind": "catalog", "sid": "S1", "v": "a", "sim": {"speed_mps": 10.0}},
    {"kind": "catalog", "sid": "S1", "v": "a", "trigger": "lka_active"},
    {"kind": "catalog", "sid": "S1", "v": "a", "colour": "red"},
    {"kind": "other"},
])
def test_invalid_recipes_are_refused(recipe):
    with pytest.raises((ValueError, KeyError)):
        case.resolve(recipe)


def test_document_hashes_every_input_file():
    doc = case.document({"kind": "catalog", "sid": "S4", "v": "a", "faults": [["F04", "a"]]})
    assert doc["schema"] == case.SCHEMA and doc["c14n"] == "c14n/1"
    names = set(doc["inputs"])
    assert {"benchmark/scenarios/S4.xosc", "benchmark/scenarios/S4.anchors.xosc",
            "benchmark/faults/F04.xosc", "benchmark/faults/F04.anchors.xosc"} <= names
    assert any(n.endswith(".xodr") for n in names)
    assert doc["case_hash"] == case.case_hash(case.resolve(doc["recipe"]))


def test_simulator_reads_no_excluded_field():
    """EXCLUDE is safe only while sim/ never reads Scenario.notes, nor .name outside logging."""
    bad = []
    for path in (ROOT / "sim").rglob("*.py"):
        if path.parts[-2] == "logging":
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Attribute) and node.attr in case.EXCLUDE["Scenario"]:
                owner = ast.unparse(node.value)
                if "scenario" in owner or owner in ("sc", "self.scenario"):
                    bad.append(f"{path.relative_to(ROOT)}:{node.lineno} {owner}.{node.attr}")
    assert not bad, bad

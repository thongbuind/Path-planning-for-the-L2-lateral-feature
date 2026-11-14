"""B2 holds a case for every test of Software Qualification Test Specification 5.1 run in SIL (PP-PR-042)."""

from eval import aspects
from eval import report_html

L0 = {"difficulty": "L0", "expected": "drive"}


def test_r79_esf_anchors_are_regulatory():
    for family, anchor in [("S7", "a"), ("S7", "e"), ("S8", "a"), ("S8", "c"), ("S8", "d")]:
        assert "B2" in aspects.members(family, anchor, ["anchor"], L0)
    assert "B2" not in aspects.members("S8", "late", ["anchor"], L0)


def test_r79_esf_row_maps_to_anchor_cases():
    tests = report_html.regulatory_tests()
    row = next(i for i, t in enumerate(tests) if t["source"] == "R79 Annex 8, 3.3.1, 3.3.2")
    assert row in report_html.test_of({"family": "S7", "anchor": "a", "parameters": {}}, tests)
    assert row in report_html.test_of({"family": "S8", "anchor": "c", "parameters": {}}, tests)
    assert row not in report_html.test_of({"family": "S8", "anchor": "late", "parameters": {}}, tests)
    # Euro NCAP grid cases stay with their own protocol rows.
    assert row not in report_html.test_of({"family": "S7", "anchor": None, "parameters": {"protocol": "Euro NCAP LSS"}}, tests)


def test_every_sil_test_of_5_1_has_b2_cases():
    """Each 5.1 row names scenarios whose anchors (or protocol grid) are in B2."""
    definitions = aspects.definitions()["B2"]
    families = set(definitions.get("families", []))
    anchored = definitions.get("anchors", {})
    for t in report_html.regulatory_tests():
        if t["docs"] == ["Euro NCAP LSS"]:
            continue  # protocol grids, B2 by method
        covered = any(f in families or (f in anchored and (a is None or a & set(anchored[f])))
                      for f, a in t["refs"])
        assert covered, t["source"]

"""Technique comparison of Software Qualification Test Specification 9.1 on synthetic suite folders."""

import json

from eval import compare, techniques


def _folder(tmp_path, name, lateral, failed_first=False):
    cases = [{"id": f"S1-{i}-{p}", "family": "S1", "anchor": "a", "methods": ["anchor"],
              "parameters": {"profile": p, "variant": f"S1-{i}"}} for i in range(8) for p in ("VP-0", "VP-1")]
    records = []
    for i, c in enumerate(cases):
        p = c["parameters"]["profile"]
        records.append({"case": c["id"], "seed": 1, "profile": p, "scope": None,
                        "failed": ["PP-SWR-100"] if failed_first and i == 0 else [],
                        "result": {"criteria": [], "issues": [], "case_failures": [], "info": {},
                                   "targets": [{"id": "PP-SWR-050", "metric": "Lệch ngang",
                                                "value": lateral(i), "unit": "m"}]}})
    folder = tmp_path / name
    folder.mkdir()
    (folder / "manifest.json").write_text(json.dumps({
        "libraries": [{"pp_version": name, "sha256": "0" * 64}], "generation": {"sha256": "g"},
        "summary": {"partial": False}}))
    (folder / "generation.json").write_text(json.dumps({"cases": cases}))
    (folder / "results.jsonl").write_text("\n".join(json.dumps(r) for r in records))
    return compare.load(folder, name)


def test_failing_technique_is_eliminated_however_smooth(tmp_path):
    smooth = _folder(tmp_path, "smooth", lambda i: 0.01, failed_first=True)
    good = _folder(tmp_path, "good", lambda i: 0.10 + 0.001 * i)
    worse = _folder(tmp_path, "worse", lambda i: 0.20 + 0.001 * i)
    c = techniques.rank([smooth, worse, good])
    assert c["eliminated"] == ["smooth"] and c["order"] == ["good", "worse"]
    assert c["rows"]["smooth"]["step1"]["requirements"] == {"PP-SWR-100": 1}
    text = "\n".join(techniques.markdown(c))
    assert "smooth bị loại ở bước 1" in text and "| good | đạt |" in text
    assert "PP-SWR-050 Lệch ngang" in text  # summary table, worst value per technique

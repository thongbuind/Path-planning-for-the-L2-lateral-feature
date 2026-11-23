"""Catalog bàn giao: mỗi ca có Given, Then lấy từ phạm vi chấm, Then vòng hở là tập con."""

import json

from eval import catalog


def test_smoke_catalog_is_complete(tmp_path):
    entries = catalog.build("smoke")
    assert entries
    ids = [e["id"] for e in entries]
    assert len(ids) == len(set(ids))
    for e in entries:
        assert e["given"] and e["then"]
        assert set(e["then_open_loop"]) <= set(e["then"])
        assert all(r.startswith("PP-SWR-") for r in e["then"])
    paths = catalog.write(entries, tmp_path, "smoke")
    data = json.loads(paths[0].read_text(encoding="utf-8"))
    assert {r for e in data["cases"] for r in e["then"]} == set(data["requirements"])
    assert all(v["text"] for v in data["requirements"].values())


def test_closed_loop_flag_comes_from_the_verification_column():
    closed = catalog.closed_loop_only()
    assert "PP-SWR-051" in closed  # "Test, vòng kín: S1"
    assert "PP-SWR-001" not in closed  # "Test: S1, S1b, S12 (a)"

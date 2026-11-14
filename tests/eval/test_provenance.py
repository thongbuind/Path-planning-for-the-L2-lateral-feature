"""Run provenance and official-run rules (eval/provenance.py, research/README.md)."""

import pytest

from adapters.sil.sil_planner import library_path
from eval import provenance, study


def manifest(dirty=False, commit="b9e5d4dc27a8", build=None):
    lib = {"path": "lib", "build": provenance.parse_version(build) if build is not None else {}}
    return {"git": {"commit": commit + "ffff", "short": commit[:7], "dirty": dirty},
            "libraries": [lib]}


def test_parse_version():
    v = provenance.parse_version("pp_planner 0.1.0 commit b9e5d4dc27a8-dirty calibration 3f2a91c0aa11")
    assert v["version"] == "0.1.0" and v["commit"] == "b9e5d4dc27a8" and v["dirty"]
    assert v["calibration"] == "3f2a91c0aa11"
    assert provenance.parse_version(None) == {}


def test_official_run_needs_clean_tree_and_library_from_head():
    good = "pp_planner 0.1.0 commit b9e5d4dc27a8 calibration 3f2a91c0aa11"
    assert provenance.official_problems(manifest(build=good)) == []
    assert any("uncommitted" in p for p in provenance.official_problems(manifest(dirty=True, build=good)))
    assert any("no pp_version" in p for p in provenance.official_problems(manifest(build=None)))
    stale = "pp_planner 0.1.0 commit 000000000000 calibration 3f2a91c0aa11"
    assert any("rebuild" in p for p in provenance.official_problems(manifest(build=stale)))
    dirty_lib = "pp_planner 0.1.0 commit b9e5d4dc27a8-dirty calibration 3f2a91c0aa11"
    assert any("uncommitted planner" in p for p in provenance.official_problems(manifest(build=dirty_lib)))


def test_changes_under_research_do_not_make_a_run_unofficial(monkeypatch):
    status = " M research/runs/INDEX.md\n?? research/runs/x/manifest.json\n"
    monkeypatch.setattr(provenance, "_git",
                        lambda *a: status if a[0] == "status" else "b9e5d4dc27a8" if a[0] == "rev-parse" else None)
    assert not provenance.git_state()["dirty"]
    status = " M research/register.md\n M eval/sweep.py\n"
    assert provenance.git_state()["changed"] == [" M eval/sweep.py"]


def test_manifest_hashes_benchmark_inputs():
    m = provenance.make("run", "S1a")
    assert m["run_id"].startswith(tuple("0123456789")) and "-run-S1a-" in m["run_id"]
    assert "benchmark/suites/M1.yaml" in m["inputs"]
    assert "planner/calibration/calibration.yaml" in m["inputs"]


def test_study_variants_become_build_sets():
    plan = {"variants": {"V0": {"calibration": {}}, "V1": {"calibration": {"k_jump": 2},
                                                           "cmake": {"PP_T7": "qp"}}}}
    sets = study.variant_sets(plan)
    assert [s.name for s in sets] == ["V0", "V1"]
    assert sets[1].values == {"k_jump": 2} and sets[1].cmake == (("PP_T7", "qp"),)


@pytest.mark.skipif(not library_path().exists(), reason="planner library not built")
def test_built_library_names_itself():
    info = provenance.library_info(library_path())
    assert info["build"].get("name") == "pp_planner"
    assert info["build"]["commit"] and info["build"]["calibration"]

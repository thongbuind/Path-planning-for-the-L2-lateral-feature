"""Simulator identity and model validation state in every report (SIM-REQ-120, 121)."""

from eval import conclusion, credibility, provenance


def test_models_are_unique_and_say_their_validation():
    ids = [m.id for m in credibility.MODELS]
    assert len(ids) == len(set(ids))
    assert all(m.validation for m in credibility.MODELS)
    assert not any(m.validated for m in credibility.MODELS)  # no real vehicle data exists yet


def test_simulator_text_names_version_and_validation_state():
    text = credibility.simulator_text(credibility.simulator_info({"commit": "abcdef0123456789", "dirty": False}))
    assert "commit abcdef0" in text and "dirty" not in text
    assert "behavior_checksum/" in text and "chưa model nào" in text
    dirty = credibility.simulator_text(credibility.simulator_info({"commit": "abcdef0123456789", "dirty": True}))
    assert "abcdef0-dirty" in dirty
    assert "không có git" in credibility.simulator_text(credibility.simulator_info({}))


def test_text_counts_a_validated_model():
    info = credibility.simulator_info({"commit": "abcdef0"})
    info["models"][0]["validated"] = True
    assert f"1/{len(info['models'])} model đã validation" in credibility.simulator_text(info)


def test_manifest_records_the_simulator():
    info = provenance.make("run", "S1a")["simulator"]
    assert {m["id"] for m in info["models"]} == {m.id for m in credibility.MODELS}
    assert info["checksum_version"] and info["bundle_schema"] == "run_bundle/1"


def test_every_conclusion_names_the_simulator():
    c = conclusion.conclude([])
    assert any(line.startswith("- Simulator: ") for line in conclusion.markdown(c, "lib"))
    given = conclusion.markdown(c, "lib", simulator="commit x")
    assert "- Simulator: commit x" in given


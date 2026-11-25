"""Khung lab của PP-TS-031: tạo generator, registry, quick bench và giá trị calibration riêng của lab."""

import importlib.util
from pathlib import Path

import pytest
import yaml

from eval import sweep

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "research" / "generators"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_registry_names_follow_the_naming_rule():
    entries = yaml.safe_load((LAB / "registry.yaml").read_text(encoding="utf-8"))["generators"]
    for name, entry in entries.items():
        assert entry["kind"] in ("builtin", "config", "lab", "tool")
        if entry["kind"] in ("lab", "tool"):
            assert entry["cmake"] == {"PP_T7": "lab", "PP_T7_LAB": name}
            assert entry["base"] in entries
    plan = yaml.safe_load((ROOT / "research/studies/PP-TS-031-t7-generator-campaign/plan.yaml").read_text())
    for variant in plan["variants"].values():
        lab = (variant.get("cmake") or {}).get("PP_T7_LAB")
        if lab:
            assert lab in entries


def test_new_generator_renders_the_template(tmp_path):
    gen = load(LAB / "new_generator.py", "new_generator")
    target = gen.create("quintic_tangent_point", "qtp", "quintic_duration", tmp_path)
    files = sorted(str(p.relative_to(target)) for p in target.rglob("*") if p.is_file())
    assert "src/quintic_tangent_point.c" in files and "tests/test_quintic_tangent_point.c" in files
    text = "".join(p.read_text(encoding="utf-8") for p in target.rglob("*") if p.is_file())
    assert "__NAME__" not in text and "__PREFIX__" not in text and "__UPPER__" not in text
    assert yaml.safe_load((target / "generator.yaml").read_text())["calibration_prefix"] == "qtp"
    with pytest.raises(SystemExit):
        gen.create("quintic_tangent_point", "qtp", "quintic_duration", tmp_path)
    registry = tmp_path / "registry.yaml"
    registry.write_text((LAB / "registry.yaml").read_text(encoding="utf-8"), encoding="utf-8")
    gen.mark_developing("quintic_tangent_point", registry)
    assert yaml.safe_load(registry.read_text())["generators"]["quintic_tangent_point"]["status"] == "developing"
    assert registry.read_text().startswith("# Danh sách generator")


def test_quick_bench_refuses_test_seeds_and_lines():
    quick = load(LAB / "bench" / "quick.py", "quick_bench")
    suite = sweep.load_suite("PP-T7")
    chosen = quick.runs_for("quick", suite)
    assert len(chosen) == 11 and {seed for _, seed in chosen} <= {1, 2}
    assert len(quick.runs_for("tuning", suite)) == 28
    quick.QUICK = ((["S1", "f"], (3,)),)
    with pytest.raises(SystemExit):
        quick.runs_for("quick", suite)
    assert quick.label_of("x", {}, False) == "x" and quick.label_of("x", {"a": 1.0}, True).startswith("x-tm-")


def test_sweep_writes_lab_calibration_values(tmp_path, monkeypatch):
    lab = tmp_path / "quintic_tangent_point"
    lab.mkdir()
    (lab / "generator.yaml").write_text(yaml.safe_dump(
        {"name": "quintic_tangent_point", "calibration_prefix": "qtp",
         "calibration": {"qtp_amp_m": {"value": 0.2, "unit": "m", "min": 0.0, "max": 0.5}}}))
    monkeypatch.setattr(sweep, "LAB_DIR", tmp_path)
    cal_set = sweep.CalSet("a", {"qtp_amp_m": 0.3},
                           (("PP_T7", "lab"), ("PP_T7_LAB", "quintic_tangent_point")))
    args = sweep._lab_calibration(cal_set, {"qtp_amp_m": 0.3}, tmp_path)
    assert args == [f"-DPP_T7_LAB_CALIBRATION={tmp_path / 'generator.yaml'}"]
    assert yaml.safe_load((tmp_path / "generator.yaml").read_text())["calibration"]["qtp_amp_m"]["value"] == 0.3
    assert sweep._lab_calibration(cal_set, {}, tmp_path) == []
    with pytest.raises(KeyError):
        sweep._lab_calibration(cal_set, {"qtp_other": 1.0}, tmp_path)
    with pytest.raises(KeyError):
        sweep._lab_calibration(sweep.CalSet("b", {"x": 1.0}), {"x": 1.0}, tmp_path)

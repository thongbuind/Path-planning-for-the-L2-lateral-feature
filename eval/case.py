"""Resolved case: the exact Scenario the harness gets, the recipe that builds it, its identity.

A recipe is plain JSON, so the CLI, the live web and a rerun build the case the same way:

    {"kind": "catalog", "sid": "S4", "v": "a"}            scenario and variant of benchmark/scenarios
    {"kind": "file", "path": "build/.../S1-a-....xosc"}   a concrete OpenSCENARIO file (suite, --xosc)

plus optional modifiers, applied in this order whatever the kind:
    "faults": [["F04", "a"], ...]   fault definitions of benchmark/faults (6.2: several allowed)
    "trigger", "offset_s"           start the timed faults after a planner-output event
    "vehicle": "VP-4"                vehicle profile
    "sim": {"road_mu": 0.5, ...}    environment values of SIM_KEYS
    "acc": "on"                      longitudinal side
    "adas_mode": "A"                 inputs of the LKA/ELK stand-in
    "name": "..."                    display name (not part of the identity)

Identity: case_hash = sha256 of the Scenario in c14n/1 (execution.canonical) without the
fields the simulator does not read (EXCLUDE). Same case_hash means the harness gets the same
values bit for bit. Schema of resolved-case.json: SCHEMA.
"""

import re
from dataclasses import replace
from pathlib import Path

from eval import loader, openx, provenance
from execution import canonical
from sim.scenario import Scenario

SCHEMA = "resolved_case/1"
ROOT = Path(__file__).resolve().parents[1]
# Fields sim/ never reads (tests/eval/test_case.py checks it): display name and evaluation notes.
EXCLUDE = {"Scenario": {"name", "notes"}}
SIM_KEYS = {"road_mu": (0.1, 1.0), "camera_latency_ms": (0.0, 500.0), "perception_noise_scale": (0.0, 10.0)}
ACC = ("off", "on", "ignore_limits")
ADAS_MODES = ("A", "B")
KINDS = ("catalog", "file")
MODIFIERS = {"faults", "trigger", "offset_s", "vehicle", "sim", "acc", "adas_mode", "name"}


def _check(recipe: dict) -> None:
    kind = recipe.get("kind")
    if kind not in KINDS:
        raise ValueError(f"recipe kind must be one of {KINDS}")
    base = {"kind", "sid", "v"} if kind == "catalog" else {"kind", "path"}
    unknown = set(recipe) - base - MODIFIERS
    if unknown:
        raise ValueError(f"unknown recipe fields: {sorted(unknown)}")
    if kind == "catalog":
        if not (re.fullmatch(r"S\d+[a-z]?", str(recipe.get("sid", "")))
                and re.fullmatch(r"[a-z][a-z0-9-]*", str(recipe.get("v", "")))):
            raise ValueError("invalid scenario or variant")
    for fault in recipe.get("faults") or []:
        if not (len(fault) == 2 and re.fullmatch(r"F\d{2}", str(fault[0]))
                and re.fullmatch(r"[a-z]", str(fault[1]))):
            raise ValueError("invalid fault")
    for key, value in (recipe.get("sim") or {}).items():
        if key not in SIM_KEYS:
            raise ValueError(f"unknown sim key {key!r}")
        lo, hi = SIM_KEYS[key]
        if not lo <= float(value) <= hi:
            raise ValueError(f"{key} out of range")
    if recipe.get("acc") not in (None, *ACC):
        raise ValueError("invalid acc")
    if recipe.get("adas_mode") not in (None, *ADAS_MODES):
        raise ValueError("invalid adas_mode")
    if recipe.get("trigger") is not None:
        from sim.faults import trigger
        trigger.check(recipe["trigger"])
        if not recipe.get("faults"):
            raise ValueError("trigger needs a fault")
    if float(recipe.get("offset_s") or 0.0) < 0:
        raise ValueError("offset_s must be >= 0")


def _path(recipe: dict) -> Path:
    path = Path(recipe["path"])
    return path if path.is_absolute() else ROOT / path


def resolve(recipe: dict) -> Scenario:
    """The Scenario of a recipe; ValueError or KeyError when the recipe is invalid."""
    _check(recipe)
    if recipe["kind"] == "catalog":
        sid, v = recipe["sid"], recipe["v"]
        scenario = replace(loader.load(sid, v), name=f"{sid}{v}")
    else:
        path = _path(recipe)
        scenario = replace(loader.load_file(path), name=path.stem)
    trigger = recipe.get("trigger")
    offset = float(recipe.get("offset_s") or 0.0)
    for fault_id, level in recipe.get("faults") or []:
        scenario = loader.with_fault(scenario, fault_id, level, trigger, offset)
    if recipe.get("vehicle"):
        from sim.vehicle.profiles import PROFILES
        if recipe["vehicle"] not in PROFILES:
            raise ValueError("unknown vehicle profile")
        scenario = replace(scenario, profile=recipe["vehicle"])
    if recipe.get("sim"):
        scenario = replace(scenario, **{k: float(v) for k, v in recipe["sim"].items()})
    if recipe.get("acc"):
        scenario = replace(scenario, acc=recipe["acc"], name=f"{scenario.name}_acc-{recipe['acc']}")
    if recipe.get("adas_mode"):
        if scenario.adas_mode == "scripted":
            raise ValueError("adas_mode applies to scenarios configured for the stand-in")
        scenario = replace(scenario, adas_mode=recipe["adas_mode"], name=f"{scenario.name}_adas-{recipe['adas_mode']}")
    if recipe.get("name"):
        scenario = replace(scenario, name=str(recipe["name"]))
    return scenario


def plain(scenario: Scenario) -> dict:
    return canonical.to_plain(scenario, EXCLUDE)


def case_hash(scenario: Scenario) -> str:
    return canonical.sha256_hex(canonical.dumps(plain(scenario)))


def _road_of(path: Path, overrides=None) -> Path | None:
    try:
        root, _ = openx.resolve(openx.parse(path), overrides)
        return (path.parent / root.find("./RoadNetwork/LogicFile").attrib["filepath"]).resolve()
    except Exception:  # noqa: BLE001  a file without a road file: nothing more to hash
        return None


def _rel(path: Path) -> str:
    path = path.resolve()
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def inputs(recipe: dict) -> dict[str, str]:
    """sha256 of every benchmark file the recipe reads."""
    files: list[Path] = []
    if recipe["kind"] == "catalog":
        scenario = loader.SCENARIO_DIR / f"{recipe['sid']}.xosc"
        files += [scenario, scenario.with_suffix(".anchors.xosc")]
        files.append(_road_of(scenario, openx.anchors(scenario).get(recipe["v"])))
    else:
        path = _path(recipe)
        files += [path, _road_of(path)]
    for fault_id, _ in recipe.get("faults") or []:
        fault = loader.FAULT_DIR / f"{fault_id}.xosc"
        files += [fault, fault.with_suffix(".anchors.xosc")]
    return {_rel(f): provenance.sha256(f) for f in files if f is not None and f.is_file()}


def document(recipe: dict, scenario: Scenario | None = None) -> dict:
    """Content of resolved-case.json."""
    scenario = scenario or resolve(recipe)
    case = plain(scenario)
    return {"schema": SCHEMA, "c14n": canonical.C14N, "recipe": recipe, "case": case,
            "case_hash": canonical.sha256_hex(canonical.dumps(case)), "inputs": inputs(recipe),
            "annotations": {"name": scenario.name, "notes": canonical.to_plain(scenario.notes)}}

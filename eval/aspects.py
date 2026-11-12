"""Aspect suites B1 to B8 of benchmark/suites/aspects.yaml (Software Qualification Test
Specification 5.3): which aspects a labelled concrete case belongs to."""

from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ASPECTS = ROOT / "benchmark" / "suites" / "aspects.yaml"
_KEYS = {"title", "note", "difficulty", "expected", "families", "methods", "anchors", "all"}


@lru_cache(maxsize=None)
def definitions(path: Path = ASPECTS) -> dict:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    for aspect, rule in data.items():
        if set(rule) - _KEYS:
            raise ValueError(f"{aspect}: unknown keys {sorted(set(rule) - _KEYS)}")
    return data


def members(family: str, anchor: str | None, methods: list[str], labels: dict) -> list[str]:
    out = []
    for aspect, rule in definitions().items():
        if (rule.get("all")
                or labels.get("difficulty") in rule.get("difficulty", [])
                or labels.get("expected") in rule.get("expected", [])
                or family in rule.get("families", [])
                or any(m in rule.get("methods", []) for m in methods)
                or (anchor is not None and anchor in rule.get("anchors", {}).get(family, []))):
            out.append(aspect)
    return out

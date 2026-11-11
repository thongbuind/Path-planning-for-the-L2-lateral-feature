"""Import rules of README.md and the integration-ready rules of PP-ADR-013, checked statically."""

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

# Python package -> top-level packages it must not import.
FORBIDDEN = {
    "interfaces": {"planner", "adapters", "sim", "benchmark", "eval"},
    "adapters": {"planner", "sim", "benchmark", "eval"},
    "sim": {"planner", "adapters", "benchmark", "eval"},
    "eval": {"planner"},
}


def _python_files(package: str):
    return sorted((ROOT / package).rglob("*.py")) if (ROOT / package).exists() else []


def _imports(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            yield node.module.split(".")[0]


@pytest.mark.parametrize("package", sorted(FORBIDDEN))
def test_python_import_rules(package):
    bad = [f"{p.relative_to(ROOT)} imports {name}"
           for p in _python_files(package)
           for name in _imports(p) if name in FORBIDDEN[package]]
    assert not bad, "\n".join(bad)


PLANNER_C = sorted((ROOT / "planner" / "src").rglob("*.[ch]"))
ALLOWED_SYSTEM_HEADERS = {"stdbool.h", "stdint.h", "stddef.h", "string.h", "math.h", "float.h"}
# No heap, no I/O, no OS clock or environment (PP-ADR-013).
FORBIDDEN_CALLS = re.compile(
    r"\b(malloc|calloc|realloc|free|fopen|fread|fwrite|printf|fprintf|puts|"
    r"time|clock|clock_gettime|gettimeofday|getenv|exit|abort)\s*\(")


@pytest.mark.parametrize("path", PLANNER_C, ids=lambda p: p.name)
def test_planner_c_is_integration_ready(path):
    text = path.read_text(encoding="utf-8")
    code = re.sub(r"/\*.*?\*/|//[^\n]*", "", text, flags=re.S)
    for header in re.findall(r'#include\s*<([^>]+)>', code):
        assert header in ALLOWED_SYSTEM_HEADERS, f"{path.name}: <{header}>"
    # Own headers: interface and generated ones start with pp_; unit headers live in planner/src
    # (module names of Software Detailed Design section 3).
    src = ROOT / "planner" / "src"
    for header in re.findall(r'#include\s*"([^"]+)"', code):
        own_unit = (src / header).is_file() or (path.parent / header).is_file()
        assert header.startswith("pp_") or own_unit, f"{path.name}: \"{header}\""
    assert not FORBIDDEN_CALLS.search(code), f"{path.name}: {FORBIDDEN_CALLS.search(code).group(0)}"

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

FORBIDDEN = {
    "interfaces": {"planner", "adapters", "sim", "benchmark", "eval"},
    "adapters": {"planner", "sim", "benchmark", "eval"},
    "sim": {"planner", "adapters", "benchmark", "eval", "execution", "workbench"},
    "eval": {"planner", "workbench"},
    # Worker của mỗi SUT được cấu hình qua lệnh gọi; execution và workbench không import planner
    # (SIM-REQ-140, 141).
    "execution": {"interfaces", "planner", "adapters", "sim", "benchmark", "eval", "workbench"},
    "workbench": {"interfaces", "planner", "adapters", "sim", "benchmark", "eval"},
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


CODE_PACKAGES = {"interfaces", "planner", "adapters", "sim", "eval", "benchmark", "execution", "workbench"}


def test_web_reads_no_source_code():
    files = [p for p in (ROOT / "web").rglob("*.py") if "dist" not in p.parts and "__pycache__" not in p.parts]
    bad = [f"{p.relative_to(ROOT)} imports {name}" for p in files for name in _imports(p) if name in CODE_PACKAGES]
    assert not bad, "\n".join(bad)


@pytest.mark.parametrize("package", sorted(FORBIDDEN))
def test_python_import_rules(package):
    bad = [f"{p.relative_to(ROOT)} imports {name}"
           for p in _python_files(package)
           for name in _imports(p) if name in FORBIDDEN[package]]
    assert not bad, "\n".join(bad)


PLANNER_C = sorted((ROOT / "planner" / "src").rglob("*.[ch]"))
ALLOWED_SYSTEM_HEADERS = {"stdbool.h", "stdint.h", "stddef.h", "string.h", "math.h", "float.h"}
# PP-ADR-013: không heap, I/O, đồng hồ hệ điều hành hoặc biến môi trường.
FORBIDDEN_CALLS = re.compile(
    r"\b(malloc|calloc|realloc|free|fopen|fread|fwrite|printf|fprintf|puts|"
    r"time|clock|clock_gettime|gettimeofday|getenv|exit|abort)\s*\(")


@pytest.mark.parametrize("path", PLANNER_C, ids=lambda p: p.name)
def test_planner_c_is_integration_ready(path):
    text = path.read_text(encoding="utf-8")
    code = re.sub(r"/\*.*?\*/|//[^\n]*", "", text, flags=re.S)
    for header in re.findall(r'#include\s*<([^>]+)>', code):
        assert header in ALLOWED_SYSTEM_HEADERS, f"{path.name}: <{header}>"
    src = ROOT / "planner" / "src"
    for header in re.findall(r'#include\s*"([^"]+)"', code):
        own_unit = (src / header).is_file() or (path.parent / header).is_file()
        assert header.startswith("pp_") or own_unit, f"{path.name}: \"{header}\""
    assert not FORBIDDEN_CALLS.search(code), f"{path.name}: {FORBIDDEN_CALLS.search(code).group(0)}"

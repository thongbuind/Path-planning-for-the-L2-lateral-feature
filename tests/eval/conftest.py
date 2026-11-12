"""Builds tests/eval/stub/stub_planner.c, a test double of a planner library, on demand."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
STUB = Path(__file__).with_name("stub") / "stub_planner.c"
SUFFIX = ".dylib" if sys.platform == "darwin" else ".so"


@pytest.fixture(scope="session")
def build_stub(tmp_path_factory):
    """build_stub("STUB_NAN", ...) -> path of the library; one build per set of defines."""
    if shutil.which("cc") is None:
        pytest.skip("no C compiler")
    folder = tmp_path_factory.mktemp("stubs")
    built: dict[tuple[str, ...], Path] = {}

    def build(*defines: str) -> Path:
        key = tuple(sorted(defines))
        if key not in built:
            name = "_".join(d.lower() for d in key) or "conformant"
            out = folder / f"libstub_{name}{SUFFIX}"
            subprocess.run(["cc", "-std=c11", "-shared", "-fPIC", "-O0",
                            f"-I{ROOT / 'interfaces' / 'c'}", *(f"-D{d}" for d in key),
                            str(STUB), "-o", str(out), "-lm"], check=True, capture_output=True)
            built[key] = out
        return built[key]

    return build

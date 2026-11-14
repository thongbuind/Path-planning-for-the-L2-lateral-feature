"""The ctypes mirror has the same size and field offsets as the C structs.

Needs the layout probe built with the planner (planner/CMakeLists.txt); skipped otherwise.
"""

import ctypes

import pytest

from adapters.sil import pp_ctypes
from adapters.sil.sil_planner import library_path

PROBE = library_path("pp_layout_probe")
pytestmark = pytest.mark.skipif(not PROBE.exists(), reason=f"layout probe not built: {PROBE}")

STRUCTS = sorted(name[:-1] for name, value in vars(pp_ctypes).items()
                 if name.endswith("C") and isinstance(value, type)
                 and issubclass(value, ctypes.Structure))


@pytest.fixture(scope="module")
def probe():
    lib = ctypes.CDLL(str(PROBE))
    lib.pp_probe_sizeof.restype = ctypes.c_size_t
    lib.pp_probe_sizeof.argtypes = [ctypes.c_char_p]
    lib.pp_probe_offsetof.restype = ctypes.c_size_t
    lib.pp_probe_offsetof.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    return lib


@pytest.mark.parametrize("name", STRUCTS)
def test_size_and_offsets_match(probe, name):
    ctype = getattr(pp_ctypes, f"{name}C")
    assert probe.pp_probe_sizeof(name.encode()) == ctypes.sizeof(ctype)
    for field, _ in ctype._fields_:
        offset = probe.pp_probe_offsetof(name.encode(), field.encode())
        assert offset == getattr(ctype, field).offset, f"{name}.{field}"

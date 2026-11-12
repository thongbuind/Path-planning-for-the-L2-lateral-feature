"""Severity of a failure (Software Qualification Test Specification 8.4).

Derived from the Type column of the Software Requirements Specification, never assigned per
case: Safety, a safety goal (SG-nn) or Interface -> BLOCKER; Regulatory without a safety goal
-> MAJOR; Functional without a safety goal -> MINOR; Performance -> none (measured, ranked).
Failing C1 or C2 (section 11) and an execution fault of the planner are BLOCKER as well.
"""

import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRS = ROOT / "docs" / "vi" / "path-planner-software-requirements-specification.md"

BLOCKER, MAJOR, MINOR = "BLOCKER", "MAJOR", "MINOR"
ORDER = {BLOCKER: 0, MAJOR: 1, MINOR: 2, None: 3}
EXECUTION_FAULT = "execution"  # planner stopped, did not return, or NaN/inf in its output

_ROW = re.compile(r"^\|\s*(PP-SWR-\d{3})\s*\|(.*)\|\s*$")


@lru_cache(maxsize=None)
def requirement_types(path: Path = SRS) -> dict[str, str]:
    """PP-SWR id -> Type cell, from every requirement table (ID, Yêu cầu, Kiểm chứng, Type, Nguồn)."""
    types = {}
    header = None
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and cells[0] == "ID":
            header = cells
            continue
        match = _ROW.match(line.strip())
        if match and header and "Type" in header:
            types[match.group(1)] = cells[header.index("Type")]
    return types


_CODE = re.compile(r"\b([SFQ]\d+[a-z]?)\b")


@lru_cache(maxsize=None)
def verification(path: Path = SRS) -> dict[str, tuple[frozenset[str], bool, bool]]:
    """PP-SWR id -> (codes in its Kiểm chứng cell, "mọi kịch bản", "mọi lỗi")."""
    out = {}
    header = None
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and cells[0] == "ID":
            header = cells
            continue
        match = _ROW.match(line.strip())
        if match and header and "Kiểm chứng" in header:
            cell = cells[header.index("Kiểm chứng")]
            out[match.group(1)] = (frozenset(_CODE.findall(cell)), "mọi kịch bản" in cell, "mọi lỗi" in cell)
    return out


def srs_scope(family: str) -> set[str]:
    """Requirements whose Kiểm chứng column names this scenario or fault code (Software
    Qualification Test Specification 8.1), or every scenario, or every fault for a fault."""
    return {rid for rid, (codes, every, every_fault) in verification().items()
            if family in codes or every or (every_fault and family.startswith("F"))}


def safety_goals(check_id: str) -> list[str]:
    """SG-nn named in the Type cell of a requirement; empty for other ids."""
    kind = requirement_types().get(check_id, "")
    return [w.strip() for w in kind.split(",") if w.strip().startswith("SG-")]


def level(check_id: str) -> str | None:
    """Severity of failing one check: a PP-SWR id, a conformance id (C1.x, C2.x, C3.x) or
    EXECUTION_FAULT. None: no severity (performance target, or C3 which only removes the
    Integrable flag)."""
    if check_id == EXECUTION_FAULT or check_id.startswith(("C1.", "C2.")):
        return BLOCKER
    if check_id.startswith("C3."):
        return None
    kind = requirement_types().get(check_id)
    if kind is None:
        raise KeyError(f"{check_id} is not in the Software Requirements Specification")
    words = {w.strip() for w in kind.split(",")}
    if "Safety" in words or "Interface" in words or any(w.startswith("SG-") for w in words):
        return BLOCKER
    if "Regulatory" in words:
        return MAJOR
    if "Functional" in words:
        return MINOR
    return None

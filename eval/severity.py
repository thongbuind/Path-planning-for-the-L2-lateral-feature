"""Mức độ lỗi lấy từ cột Type trong SRS theo SQTS 8.4."""

import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRS = ROOT / "docs" / "vi" / "path-planner-software-requirements-specification.md"

BLOCKER, MAJOR, MINOR = "BLOCKER", "MAJOR", "MINOR"
ORDER = {BLOCKER: 0, MAJOR: 1, MINOR: 2, None: 3}
EXECUTION_FAULT = "execution"

_ROW = re.compile(r"^\|\s*(PP-SWR-\d{3})\s*\|(.*)\|\s*$")


@lru_cache(maxsize=None)
def requirement_types(path: Path = SRS) -> dict[str, str]:
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
    return {rid for rid, (codes, every, every_fault) in verification().items()
            if family in codes or every or (every_fault and family.startswith("F"))}


def safety_goals(check_id: str) -> list[str]:
    kind = requirement_types().get(check_id, "")
    return [w.strip() for w in kind.split(",") if w.strip().startswith("SG-")]


def level(check_id: str) -> str | None:
    """C3 chỉ ảnh hưởng cờ Tích hợp được; performance target không có mức lỗi."""
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

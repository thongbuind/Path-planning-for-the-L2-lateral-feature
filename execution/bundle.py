"""Run bundle v1: one folder per execution, written to a temporary name, renamed when final.

    <root>/.tmp-<run_id>/   while the run writes (never read as a result)
    <root>/<run_id>/        final; never modified afterwards (SIM-REQ-021, 024)

Files: manifest.json, resolved-case.json, execution.json, evaluation.json (required for a
complete run), trace.mcap, frames.ndjson.gz, worker.log, request.json (optional), SHA256SUMS
(last). execution.json says the state, the failure class and whether the bundle is complete;
an incomplete bundle lists the required files it misses (SIM-REQ-022).
"""

import gzip
import hashlib
import json
import os
import secrets
import shutil
import time
from pathlib import Path

SCHEMA = "run_bundle/1"
REQUIRED = ("manifest.json", "resolved-case.json", "execution.json", "evaluation.json")
SUMS = "SHA256SUMS"
TMP_PREFIX = ".tmp-"


def new_run_id() -> str:
    """Unique and sortable: time of creation plus 24 random bits; never reused."""
    return time.strftime("%Y%m%d-%H%M%S") + "-" + secrets.token_hex(3)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _default(value):
    """Numpy scalars as their Python value (duck typed); anything else as text."""
    if hasattr(value, "item"):
        return value.item()
    return str(value)


def write_json(path: Path, obj) -> Path:
    tmp = path.with_name(path.name + ".part")
    tmp.write_text(json.dumps(obj, indent=1, ensure_ascii=False, default=_default) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return path


class Bundle:
    def __init__(self, root: Path, run_id: str) -> None:
        self.root = Path(root)
        self.run_id = run_id
        self.tmp = self.root / f"{TMP_PREFIX}{run_id}"
        self.final = self.root / run_id

    @classmethod
    def create(cls, root: Path, run_id: str | None = None) -> "Bundle":
        bundle = cls(root, run_id or new_run_id())
        if bundle.final.exists() or bundle.tmp.exists():
            raise FileExistsError(f"run {bundle.run_id} already exists")
        bundle.tmp.mkdir(parents=True)
        return bundle

    def path(self, name: str) -> Path:
        return self.tmp / name

    def write_json(self, name: str, obj) -> Path:
        return write_json(self.path(name), obj)

    def compress(self, name: str) -> None:
        """name -> name.gz, in place (event log at the end of a run)."""
        source = self.path(name)
        if source.is_file():
            with source.open("rb") as raw, gzip.open(self.path(name + ".gz"), "wb") as packed:
                shutil.copyfileobj(raw, packed)
            source.unlink()

    def finalize(self, execution: dict) -> Path:
        """Writes execution.json and SHA256SUMS, then renames the folder. Returns the final path."""
        for part in self.tmp.glob("*.part"):
            part.unlink()
        present = {p.name for p in self.tmp.iterdir()}
        missing = [n for n in REQUIRED if n != "execution.json" and n not in present]
        complete = execution.get("state") == "COMPLETED" and not missing
        execution = {"schema": SCHEMA, "run_id": self.run_id, **execution, "complete": complete,
                     "missing": missing}
        self.write_json("execution.json", execution)
        files = sorted(p for p in self.tmp.rglob("*") if p.is_file() and p.name != SUMS)
        lines = [f"{_sha256(p)}  {p.relative_to(self.tmp).as_posix()}" for p in files]
        (self.tmp / SUMS).write_text("\n".join(lines) + "\n", encoding="utf-8")
        os.replace(self.tmp, self.final)
        return self.final


def read(folder: Path) -> dict:
    """The JSON files of a final bundle that exist: {"manifest": ..., "execution": ..., ...}."""
    folder = Path(folder)
    out = {}
    for name in ("manifest", "resolved-case", "execution", "evaluation", "request"):
        path = folder / f"{name}.json"
        if path.is_file():
            out[name] = json.loads(path.read_text(encoding="utf-8"))
    return out


def verify(folder: Path) -> list[str]:
    """Files whose sha256 differs from SHA256SUMS, or that appeared or went missing."""
    folder = Path(folder)
    sums = folder / SUMS
    if not sums.is_file():
        return [f"{SUMS} missing"]
    expected = {}
    for line in sums.read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        expected[name] = digest
    actual = {p.relative_to(folder).as_posix(): _sha256(p) for p in folder.rglob("*") if p.is_file() and p.name != SUMS}
    problems = [f"changed: {n}" for n in expected if n in actual and actual[n] != expected[n]]
    problems += [f"missing: {n}" for n in expected if n not in actual]
    problems += [f"added: {n}" for n in actual if n not in expected]
    return problems


def listing(root: Path) -> list[Path]:
    """Final bundles under root, newest first."""
    root = Path(root)
    if not root.is_dir():
        return []
    return sorted((p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")
                   and (p / "execution.json").is_file()), key=lambda p: p.name, reverse=True)

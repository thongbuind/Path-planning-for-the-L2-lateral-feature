"""Provenance of a benchmark run (research/README.md): what produced a result.

Every run writes a manifest.json next to its results in build/. An official run
(--record) also needs a clean working tree and planner libraries built from the current
commit (read back with pp_version()); its manifest and results are then copied to
research/runs/<run-id>/ and listed in research/runs/INDEX.md.
"""

import hashlib
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import numpy

ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = ROOT / "research" / "runs"
INDEX = RUNS_DIR / "INDEX.md"
CALIBRATION = ROOT / "planner" / "calibration" / "calibration.yaml"
BENCHMARK = ROOT / "benchmark"


def _git(*args: str) -> str | None:
    try:
        out = subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.stdout.rstrip()


def git_state() -> dict:
    """Commit and uncommitted changes. research/ holds records and is written by official
    runs, so changes there do not make a run unofficial (a study plan is hashed instead)."""
    commit = _git("rev-parse", "HEAD")
    lines = [line for line in (_git("status", "--porcelain") or "").splitlines() if line]
    changed = [line for line in lines if not line[3:].strip('"').startswith("research/")]
    return {"commit": commit, "short": commit[:7] if commit else None,
            "branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty": bool(changed), "changed": changed[:50]}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 16), b""):
            digest.update(block)
    return digest.hexdigest()


def _rel(path: Path) -> str:
    path = Path(path).resolve()
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def parse_version(text: str | None) -> dict:
    """'pp_planner 0.1.0 commit <sha>[-dirty] calibration <id>' -> fields."""
    if not text:
        return {}
    words = text.split()
    fields = {"name": words[0], "version": words[1] if len(words) > 1 else None}
    for key, value in zip(words[2::2], words[3::2]):
        fields[key] = value
    commit = fields.get("commit", "")
    fields["dirty"] = commit.endswith("-dirty")
    fields["commit"] = commit.removesuffix("-dirty") or None
    return fields


def library_info(path: Path) -> dict:
    from adapters.sil.sil_planner import library_version  # loads the library
    text = library_version(Path(path))
    return {"path": _rel(path), "sha256": sha256(path), "pp_version": text,
            "build": parse_version(text)}


def input_files() -> dict:
    """sha256 of the benchmark definitions and the start calibration."""
    files = sorted(p for p in BENCHMARK.rglob("*")
                   if p.is_file() and p.suffix in {".yaml", ".json", ".xosc", ".xodr", ".xsd"}) + [CALIBRATION]
    return {_rel(p): sha256(p) for p in files}


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def make(kind: str, target: str, extra: dict | None = None) -> dict:
    """Manifest at the start of a run; libraries and results are added by the caller."""
    git = git_state()
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    run_id = f"{stamp}-{kind}-{target}-{git['short'] or 'nogit'}" + ("-dirty" if git["dirty"] else "")
    return {"run_id": run_id, "kind": kind, "target": target, "started": now(),
            "command": [Path(sys.argv[0]).name] + sys.argv[1:], "git": git, "libraries": [],
            "inputs": input_files(),
            "environment": {"python": platform.python_version(), "numpy": numpy.__version__,
                            "platform": platform.platform(), "machine": platform.machine()},
            **(extra or {})}


def official_problems(manifest: dict) -> list[str]:
    """Why a run cannot be official; empty when it can."""
    git = manifest["git"]
    problems = []
    if not git["commit"]:
        problems.append("not in a git repository")
    if git["dirty"]:
        problems.append("working tree has uncommitted changes: commit first, or run without --record")
    for lib in manifest["libraries"]:
        build = lib["build"]
        if not build:
            problems.append(f"{lib['path']}: no pp_version(); rebuild the planner library")
        elif build["dirty"]:
            problems.append(f"{lib['path']}: built from uncommitted planner sources; rebuild after commit")
        elif git["commit"] and not git["commit"].startswith(build["commit"] or "-"):
            problems.append(f"{lib['path']}: built from {build['commit']}, HEAD is {git['short']}; rebuild")
    return problems


def preflight(manifest: dict) -> None:
    """Stops an official run before it starts, so no time is spent on a run that cannot count."""
    problems = official_problems(manifest)
    if problems:
        raise SystemExit("Not an official run:\n  - " + "\n  - ".join(problems))


def write(manifest: dict, out_dir: Path, name: str = "manifest.json") -> Path:
    manifest = {**manifest, "finished": manifest.get("finished") or now()}
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / name
    path.write_text(json.dumps(manifest, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    return path


def record(manifest: dict, files: dict[str, Path], result: str) -> Path:
    """Copies an official run to research/runs/<run-id>/ and adds its line to INDEX.md."""
    preflight(manifest)
    dest = RUNS_DIR / manifest["run_id"]
    dest.mkdir(parents=True, exist_ok=False)
    for name, src in files.items():
        shutil.copyfile(src, dest / name)
    write(manifest, dest)
    libs = ", ".join(lib["build"].get("calibration", "?") for lib in manifest["libraries"]) or "—"
    row = (f"| {manifest['run_id']} | {manifest['kind']} | {manifest['target']} | "
           f"{manifest['git']['short']} | calibration {libs} | {result} | |\n")
    with open(INDEX, "a", encoding="utf-8") as f:
        f.write(row)
    return dest

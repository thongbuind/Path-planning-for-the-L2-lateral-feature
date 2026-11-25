import hashlib
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy

from eval import credibility

ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = ROOT / "research" / "runs"
INDEX = RUNS_DIR / "INDEX.md"
CALIBRATION = ROOT / "planner" / "calibration" / "calibration.yaml"
BENCHMARK = ROOT / "benchmark"
SRS = ROOT / "docs" / "vi" / "path-planner-software-requirements-specification.md"


def _git(*args: str) -> str | None:
    try:
        out = subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.stdout.rstrip()


def git_state() -> dict:
    """Bản ghi trong research/ không làm run mất tính chính thức; kế hoạch study được hash riêng."""
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


def library_info(path: Path, external: bool = False, family=None) -> dict:
    from adapters.sil.sil_planner import LCC, load_library
    family = family or LCC
    lib = load_library(Path(path), family)
    version = getattr(lib, f"{family.prefix}_version", None)
    text = version().decode("ascii", errors="replace") if version is not None else None
    # Kích thước state và tệp thư viện: ngữ cảnh chi phí phần cứng, SQTS 9.1 bước 5 (không xếp hạng).
    return {"path": _rel(path), "sha256": sha256(path), "pp_version": text,
            "build": parse_version(text), "external": external,
            "family": family.name, "state_size_bytes": int(getattr(lib, f"{family.prefix}_state_size")()),
            "file_size_bytes": Path(path).stat().st_size}


def library_infos(planner, external: bool = False) -> list[dict]:
    return [library_info(path, external, family) for path, family in planner.paths()]


def _known_commit(commit: str | None) -> bool:
    return bool(commit) and _git("cat-file", "-e", f"{commit}^{{commit}}") is not None


def input_files() -> dict:
    files = sorted(p for p in BENCHMARK.rglob("*")
                   if p.is_file() and p.suffix in {".yaml", ".json", ".xosc", ".xodr", ".xsd"}) + [CALIBRATION, SRS]
    return {_rel(p): sha256(p) for p in files}


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def make(kind: str, target: str, extra: dict | None = None) -> dict:
    git = git_state()
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    run_id = f"{stamp}-{kind}-{target}-{git['short'] or 'nogit'}" + ("-dirty" if git["dirty"] else "")
    return {"run_id": run_id, "kind": kind, "target": target, "started": now(),
            "command": [Path(sys.argv[0]).name] + sys.argv[1:], "git": git, "libraries": [],
            "simulator": credibility.simulator_info(git),
            "inputs": input_files(),
            "environment": {"python": platform.python_version(), "numpy": numpy.__version__,
                            "platform": platform.platform(), "machine": platform.machine()},
            **(extra or {})}


def official_problems(manifest: dict) -> list[str]:
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
        elif lib.get("external") and not _known_commit(build["commit"]):
            continue  # Build ngoài repo được nhận diện bằng SHA-256 và pp_version khi không có commit tương ứng ở local.
        elif build["dirty"]:
            problems.append(f"{lib['path']}: built from uncommitted planner sources; rebuild after commit")
        elif git["commit"] and not git["commit"].startswith(build["commit"] or "-"):
            problems.append(f"{lib['path']}: built from {build['commit']}, HEAD is {git['short']}; rebuild")
    return problems


def preflight(manifest: dict) -> None:
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
    """Lưu hồ sơ của lần chạy chính thức và thêm một mục vào INDEX.md."""
    preflight(manifest)
    dest = RUNS_DIR / manifest["run_id"]
    if dest.exists():
        raise FileExistsError(dest)
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".record-", dir=RUNS_DIR) as staging:
        tmp = Path(staging)
        for name, src in files.items():
            shutil.copyfile(src, tmp / name)
        write(manifest, tmp)
        tmp.rename(dest)
    libs = ", ".join(lib["build"].get("calibration", "?") for lib in manifest["libraries"]) or "—"
    row = (f"| {manifest['run_id']} | {manifest['kind']} | {manifest['target']} | "
           f"{manifest['git']['short']} | calibration {libs} | {result} | |\n")
    with open(INDEX, "a", encoding="utf-8") as f:
        f.write(row)
    return dest

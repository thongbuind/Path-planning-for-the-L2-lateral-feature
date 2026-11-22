import argparse
import json
import re
import shutil
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, BadZipFile, ZipFile

from eval import provenance

SUITE_DATA = ("results.jsonl", "generation.json", "conformance.json")
RECORD_FILES = ("manifest.json", "summary.json", "report.md", "conclusion.json")
RUN_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,80}")
CONCRETE_MANIFEST = "concrete/manifest.json"


def _archive_name(run_id: str, digest: str) -> str:
    if not RUN_ID.fullmatch(run_id) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("Invalid run ID or artifact SHA-256")
    return f"{run_id}-{digest}.zip"


def _case_files(manifest: dict) -> dict[PurePosixPath, str]:
    paths = {}
    for case in manifest["cases"]:
        name = case["file"]
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or "\\" in name or path.suffix != ".xosc":
            raise ValueError(f"Invalid concrete scenario path: {name}")
        for file, key in ((path, "sha256"), (path.with_suffix(".xodr"), "road_sha256")):
            digest = case[key]
            if paths.setdefault(file, digest) != digest:
                raise ValueError(f"Conflicting hashes for {file}")
    return paths


def prepare_store(store: Path) -> None:
    path = store.resolve()
    if path.is_relative_to(provenance.ROOT) and not path.is_relative_to(provenance.ROOT / "build"):
        raise ValueError("Use a shared directory outside the repository or build/ for a local trial")
    store.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=store):
        pass


def pack(store: Path, manifest: dict, suite_dir: Path, concrete: Path) -> dict:
    """Ghi ZIP theo SHA-256 trước khi lưu tên và hash trong hồ sơ nghiên cứu."""
    run_id = manifest["run_id"]
    generation = manifest["generation"]["sha256"]
    if provenance.sha256(concrete) != generation:
        raise ValueError("Concrete manifest SHA-256 differs from the official run")
    cases = _case_files(json.loads(concrete.read_bytes()))
    with TemporaryDirectory(dir=store) as staging:
        tmp = Path(staging) / "suite.zip"
        with ZipFile(tmp, "w", compression=ZIP_DEFLATED, compresslevel=3) as archive:
            for name in SUITE_DATA:
                archive.write(suite_dir / name, f"suite/{name}")
            archive.write(concrete, CONCRETE_MANIFEST)
            for file, expected in sorted(cases.items()):
                source = concrete.parent / file
                if provenance.sha256(source) != expected:
                    raise ValueError(f"Concrete input changed: {source}")
                archive.write(source, f"concrete/{file.as_posix()}")
        digest = provenance.sha256(tmp)
        filename = _archive_name(run_id, digest)
        tmp.replace(store / filename)
    return {"file": filename, "sha256": digest}


def restore(record: Path, store: Path, benchmark: Path) -> Path:
    """Kiểm SHA-256 rồi khôi phục theo bố cục thư mục Workbench đọc được."""
    from eval import report_html

    manifest = json.loads((record / "manifest.json").read_bytes())
    run_id = manifest["run_id"]
    artifact = manifest["artifact"]
    filename = _archive_name(run_id, artifact["sha256"])
    if artifact["file"] != filename:
        raise ValueError("Artifact filename differs from its run ID and SHA-256")
    archive_path = store / filename
    if provenance.sha256(archive_path) != artifact["sha256"]:
        raise ValueError(f"Artifact SHA-256 mismatch: {archive_path}")
    dest = benchmark / run_id
    if dest.exists():
        raise FileExistsError(dest)
    benchmark.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".restore-", dir=benchmark) as staging:
        tmp = Path(staging)
        with ZipFile(archive_path) as archive:
            generation = json.loads(archive.read(CONCRETE_MANIFEST))
            members = [CONCRETE_MANIFEST, *(f"suite/{name}" for name in SUITE_DATA),
                       *(f"concrete/{file.as_posix()}" for file in _case_files(generation))]
            if sorted(archive.namelist()) != sorted(members):
                raise ValueError("Unexpected files in suite artifact")
            archive.extractall(tmp, members)
        if provenance.sha256(tmp / CONCRETE_MANIFEST) != manifest["generation"]["sha256"]:
            raise ValueError("Restored concrete manifest SHA-256 differs from the official run")
        suite = tmp / "suite"
        for name in RECORD_FILES:
            shutil.copyfile(record / name, suite / name)
        for lang, name in (("vi", "report.html"), ("en", "report-en.html")):
            report_html.write(suite, tmp / name, lang=lang)
        tmp.rename(dest)
    return dest


def main() -> None:
    parser = argparse.ArgumentParser(description="Restore an official suite for dashboard and Workbench")
    parser.add_argument("record", type=Path, help="research/runs/<run-id>")
    parser.add_argument("--artifact-dir", type=Path, required=True, help="Directory containing the recorded ZIP")
    parser.add_argument("--benchmark-dir", type=Path, default=provenance.ROOT / "build" / "benchmark")
    args = parser.parse_args()
    try:
        print(restore(args.record, args.artifact_dir, args.benchmark_dir))
    except (OSError, ValueError, KeyError, BadZipFile) as exc:
        parser.exit(1, f"Cannot restore suite: {exc}\n")


if __name__ == "__main__":
    main()

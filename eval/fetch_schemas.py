"""Tải XSD từ ASAM và kiểm SHA-256. Repo không phân phối lại các XSD theo điều khoản giấy phép
ASAM.
"""

import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import time
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "benchmark" / "schema"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check() -> list[str]:
    problems = []
    for source in json.loads((SCHEMA / "sources.json").read_text(encoding="utf-8")):
        for name, digest in source["files"].items():
            path = SCHEMA / source["directory"] / name
            if not path.is_file():
                problems.append(f"thiếu {path.relative_to(ROOT)}")
            elif _sha(path.read_bytes()) != digest:
                problems.append(f"sai SHA-256: {path.relative_to(ROOT)}")
    return problems


def _download(url: str, attempts: int = 3) -> bytes:
    last = None
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "path-planning-schema-fetch/1"})
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.read()
        except OSError as error:
            last = error
            time.sleep(2 * (attempt + 1))
    raise SystemExit(f"{url}: {type(last).__name__}: {last}")


def fetch() -> None:
    for source in json.loads((SCHEMA / "sources.json").read_text(encoding="utf-8")):
        folder = SCHEMA / source["directory"]
        if all((folder / n).is_file() for n in source["files"]):
            continue
        data = _download(source["url"])
        if _sha(data) != source["archive_sha256"]:
            raise SystemExit(f"{source['url']}: archive SHA-256 differs from sources.json")
        folder.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            for name, digest in source["files"].items():
                # Archive OpenDRIVE có thể chứa nhiều bản trùng tên. Chọn bản khớp SHA-256 đã ghi.
                copies = [archive.read(m) for m in archive.namelist() if Path(m).name == name]
                content = next((c for c in copies if _sha(c) == digest), None)
                if content is None:
                    raise SystemExit(f"{name}: no copy in the archive has the SHA-256 of sources.json "
                                     f"({len(copies)} copies found)")
                (folder / name).write_bytes(content)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Download the ASAM XSD files the benchmark validates against, from ASAM, and check "
            "them."
        ),
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        fetch()
    problems = check()
    print("\n".join(problems) or "XSD đủ và đúng SHA-256.")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()

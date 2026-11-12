"""Download the ASAM XSD files the benchmark validates against, from ASAM, and check them.

    python3 -m eval.fetch_schemas            # missing files only
    python3 -m eval.fetch_schemas --check    # hashes of the files present, no download

The XSD files are ASAM standards (ASAM license terms 1(1)(a), www.asam.net/license.html):
redistributing them is not clearly allowed for this project, so a public copy of the
repository should not contain them. Each machine fetches the official archives listed in
benchmark/schema/sources.json and every file is checked against its SHA-256 there.
"""

import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
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


def fetch() -> None:
    for source in json.loads((SCHEMA / "sources.json").read_text(encoding="utf-8")):
        folder = SCHEMA / source["directory"]
        if all((folder / n).is_file() for n in source["files"]):
            continue
        with urllib.request.urlopen(source["url"], timeout=60) as response:  # official ASAM URL
            data = response.read()
        if _sha(data) != source["archive_sha256"]:
            raise SystemExit(f"{source['url']}: archive SHA-256 differs from sources.json")
        folder.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            members = {Path(m).name: m for m in archive.namelist()}
            for name, digest in source["files"].items():
                content = archive.read(members[name])
                if _sha(content) != digest:
                    raise SystemExit(f"{name}: SHA-256 differs from sources.json")
                (folder / name).write_bytes(content)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        fetch()
    problems = check()
    print("\n".join(problems) or "XSD đủ và đúng SHA-256.")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()

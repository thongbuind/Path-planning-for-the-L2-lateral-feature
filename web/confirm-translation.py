"""Ghi nhận cặp Markdown VI/EN đã được đối chiếu."""

import argparse
import hashlib
import json
import re
from pathlib import Path
from tempfile import TemporaryDirectory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("doc_id", help="ID tài liệu sau khi đã kiểm tra bản dịch")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", args.doc_id):
        parser.error("ID tài liệu không hợp lệ")

    docs = Path(__file__).resolve().parents[1] / "docs"
    name = args.doc_id + ".md"
    vi = docs / "vi" / name
    en = docs / "en" / name
    if not vi.is_file() or not en.is_file():
        parser.error("Cần có cả bản tiếng Việt và bản tiếng Anh")

    record = {
        "vi": hashlib.sha256(vi.read_bytes()).hexdigest(),
        "en": hashlib.sha256(en.read_bytes()).hexdigest(),
    }
    manifest = en.with_name("versions.json")
    records = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else {}
    records[args.doc_id] = record
    with TemporaryDirectory(dir=manifest.parent) as temp_dir:
        tmp = Path(temp_dir) / manifest.name
        tmp.write_text(json.dumps(records, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp.replace(manifest)
    print(f"{args.doc_id} · VI {record['vi'][:8]} · EN {record['en'][:8]}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Truy vết giữa yêu cầu của planner và kịch bản, lỗi bơm vào của benchmark.

Nguồn duy nhất của truy vết là cột Kiểm chứng trong docs/vi/yeu-cau-path-planner.md.
Cột Yêu cầu trong ba bảng của docs/vi/benchmark-evaluation.md (danh mục kịch bản,
danh mục lỗi, quét độ trễ) được sinh từ cột đó. Mã không truy về yêu cầu nào của
planner thì ghi ở bảng "Mã | Lý do" (benchmark mục 4.3) để không bị báo mồ côi.

Chạy từ thư mục G1:
    python3 tools/trace.py            kiểm tra, in ma trận và các mục mồ côi
    python3 tools/trace.py --write    ghi lại cột Yêu cầu của benchmark
    python3 tools/trace.py --quiet    chỉ in lỗi và cảnh báo

Mã thoát 1 khi có lỗi, hoặc khi cột Yêu cầu của benchmark chưa khớp mà không có --write.
Chỉ dùng thư viện chuẩn.
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs" / "vi"
REQ_DOC = DOCS / "yeu-cau-path-planner.md"
BENCH_DOC = DOCS / "benchmark-evaluation.md"

METHODS = ("Test", "Analysis", "Inspection", "Demonstration")
KEYWORDS = {"mọi kịch bản": "all_scenarios", "mọi lỗi": "all_faults", "chưa có kịch bản": "none"}
CODE_ITEM = re.compile(r"([SFQ]\d+[a-z]?)(?: \((.+)\))?")
REQ_ROW_ID = re.compile(r"PP-SWR-(\d{3})")
REF = re.compile(r"PP-SWR-(\d{3})((?:(?:, | và | đến )\d{3}(?!\d))*)")

BENCH_TABLES = {
    # tên bảng: (ô đầu của dòng tiêu đề, cột chứa mã)
    "kịch bản": ("#", 0),
    "lỗi": ("Mã", 0),
    "quét độ trễ": ("Mã", 0),
}


def split_cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def tables(lines):
    """Trả về các bảng markdown: (chỉ số dòng tiêu đề, tiêu đề, [(chỉ số dòng, ô)])."""
    out, i = [], 0
    while i < len(lines):
        if lines[i].startswith("|") and i + 1 < len(lines) and lines[i + 1].startswith("|---"):
            header = split_cells(lines[i])
            rows, j = [], i + 2
            while j < len(lines) and lines[j].startswith("|"):
                rows.append((j, split_cells(lines[j])))
                j += 1
            out.append((i, header, rows))
            i = j
        else:
            i += 1
    return out


def split_top(text):
    """Tách theo dấu phẩy ở ngoài ngoặc."""
    parts, depth, cur = [], 0, ""
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts if p.strip()]


def parse_verification(cell):
    """Đọc một ô Kiểm chứng. Trả về (phương pháp, [(mã, chi tiết, vòng)], từ khoá, lỗi)."""
    methods, refs, flags, errors = set(), [], set(), []
    for seg in (s.strip() for s in cell.split(";")):
        head, sep, body = seg.partition(":")
        method = head.split(",")[0].strip()
        if method not in METHODS:
            errors.append(f"phương pháp không rõ: {head!r}")
            continue
        methods.add(method)
        if method != "Test":
            continue
        if not sep or not body.strip():
            errors.append("Test thiếu danh sách mã")
            continue
        loop = "vòng kín" if "vòng kín" in head else "vòng hở"
        for item in split_top(body):
            if item in KEYWORDS:
                flags.add(KEYWORDS[item])
                continue
            if " đến " in item:
                errors.append(f"không ghi khoảng, hãy liệt kê từng mã: {item!r}")
                continue
            m = CODE_ITEM.fullmatch(item)
            if not m:
                errors.append(f"không đọc được: {item!r}")
                continue
            refs.append((m.group(1), m.group(2) or "", loop))
    return methods, refs, flags, errors


def expand_refs(text):
    """Mọi ID PP-SWR được nhắc trong một văn bản, mở rộng 'a đến b'."""
    found = set()
    for m in REF.finditer(text):
        nums = [m.group(1)] + re.findall(r"\d{3}", m.group(2))
        seps = re.findall(r", | và | đến ", m.group(2))
        ids = [int(nums[0])]
        for sep, n in zip(seps, nums[1:]):
            n = int(n)
            ids += list(range(ids[-1] + 1, n + 1)) if sep == " đến " else [n]
        found.update(f"{i:03d}" for i in ids)
    return found


def load_requirements(errors):
    lines = REQ_DOC.read_text(encoding="utf-8").split("\n")
    reqs = {}
    for _, header, rows in tables(lines):
        if header[:3] != ["ID", "Yêu cầu", "Kiểm chứng"]:
            continue
        status_col = header.index("Trạng thái") if "Trạng thái" in header else None
        for _, cells in rows:
            m = REQ_ROW_ID.fullmatch(cells[0])
            if not m:
                errors.append(f"dòng yêu cầu không có ID hợp lệ: {cells[0]!r}")
                continue
            rid = m.group(1)
            if rid in reqs:
                errors.append(f"PP-SWR-{rid} bị trùng")
            status = cells[status_col] if status_col is not None else ""
            reqs[rid] = {"verify": cells[2], "status": status}
    return reqs


def load_bench_codes(lines):
    """Mã của ba bảng benchmark: {tên bảng: (chỉ số dòng tiêu đề, tiêu đề, dòng)}."""
    found = {}
    for idx, header, rows in tables(lines):
        if header[0] == "#" and "Kịch bản" in header and "kịch bản" not in found:
            found["kịch bản"] = (idx, header, rows)
        elif header[:2] == ["Mã", "Nhóm"]:
            found["lỗi"] = (idx, header, rows)
        elif header[:2] == ["Mã", "Quét"]:
            found["quét độ trễ"] = (idx, header, rows)
        elif header == ["Mã", "Lý do"]:
            found["miễn"] = (idx, header, rows)
    return found


def fmt_ids(entries):
    """[(id, chi tiết)] → 'PP-SWR-001, 003 (a, b), 050'."""
    merged = defaultdict(list)
    for rid, detail in entries:
        if detail and detail not in merged[rid]:
            merged[rid].append(detail)
        merged.setdefault(rid, [])
    parts = []
    for k, rid in enumerate(sorted(merged)):
        label = f"PP-SWR-{rid}" if k == 0 else rid
        parts.append(f"{label} ({'; '.join(merged[rid])})" if merged[rid] else label)
    return ", ".join(parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write", action="store_true", help="ghi lại cột Yêu cầu của benchmark")
    ap.add_argument("--quiet", action="store_true", help="chỉ in lỗi và cảnh báo")
    args = ap.parse_args()

    errors, warnings = [], []
    reqs = load_requirements(errors)
    bench_lines = BENCH_DOC.read_text(encoding="utf-8").split("\n")
    bench = load_bench_codes(bench_lines)
    exempt_table = bench.pop("miễn", None)
    exempt = {cells[0]: cells[1] for _, cells in exempt_table[2]} if exempt_table else {}
    for name in BENCH_TABLES:
        if name not in bench:
            errors.append(f"không thấy bảng {name} trong benchmark")
    codes = {name: [cells[0] for _, cells in bench[name][2]] for name in bench}
    all_codes = {c for lst in codes.values() for c in lst}
    for c in exempt:
        if c not in all_codes:
            errors.append(f"bảng miễn (benchmark mục 4.3) có mã không tồn tại: {c}")

    # Đọc cột Kiểm chứng.
    by_code = defaultdict(list)       # mã → [(id, chi tiết)]
    no_scenario, test_without_ref = [], []
    for rid, r in sorted(reqs.items()):
        if r["status"] == "obsolete":
            continue
        if not r["verify"]:
            errors.append(f"PP-SWR-{rid}: cột Kiểm chứng trống")
            continue
        methods, refs, flags, errs = parse_verification(r["verify"])
        errors += [f"PP-SWR-{rid}: {e}" for e in errs]
        for code, detail, loop in refs:
            if code not in all_codes:
                errors.append(f"PP-SWR-{rid}: mã {code} không có trong benchmark")
            by_code[code].append((rid, ", ".join(x for x in (detail, loop if loop == "vòng kín" else "") if x)))
        if "none" in flags:
            no_scenario.append(rid)
        elif "Test" in methods and not refs and not flags & {"all_scenarios", "all_faults"}:
            test_without_ref.append(rid)

    # ID được nhắc ở các tài liệu khác phải có thật.
    for doc in sorted(DOCS.glob("*.md")):
        missing = sorted(expand_refs(doc.read_text(encoding="utf-8")) - set(reqs))
        if missing:
            errors.append(f"{doc.name} nhắc ID không có: " + ", ".join(f"PP-SWR-{m}" for m in missing))
        obsolete = sorted(i for i in expand_refs(doc.read_text(encoding="utf-8"))
                          if reqs.get(i, {}).get("status") == "obsolete")
        if obsolete and doc != REQ_DOC:
            warnings.append(f"{doc.name} nhắc ID đã obsolete: " + ", ".join(obsolete))

    if test_without_ref:
        warnings.append("Test nhưng không có mã nào: " + ", ".join(f"PP-SWR-{r}" for r in test_without_ref))
    if no_scenario:
        warnings.append("Chưa có kịch bản: " + ", ".join(f"PP-SWR-{r}" for r in no_scenario))
    for name, lst in codes.items():
        orphans = [c for c in lst if c not in by_code and c not in exempt]
        if orphans:
            warnings.append(f"{name.capitalize()} không yêu cầu nào trỏ tới: " + ", ".join(orphans))
    traced_exempt = sorted(c for c in exempt if c in by_code)
    if traced_exempt:
        warnings.append("Mã nằm trong bảng miễn nhưng có yêu cầu trỏ tới: " + ", ".join(traced_exempt))

    # Sinh cột Yêu cầu của benchmark.
    stale = []
    new_lines = list(bench_lines)
    for name, (idx, header, rows) in bench.items():
        if "Yêu cầu" not in header:
            errors.append(f"bảng {name} của benchmark thiếu cột Yêu cầu")
            continue
        col = header.index("Yêu cầu")
        for line_no, cells in rows:
            want = fmt_ids(by_code.get(cells[0], []))
            if cells[col] != want:
                stale.append(cells[0])
                cells = cells[:col] + [want] + cells[col + 1:]
                new_lines[line_no] = "| " + " | ".join(c if c else " " for c in cells) + " |"

    if not args.quiet:
        print(f"Yêu cầu: {len(reqs)}. Mã ở benchmark: "
              + ", ".join(f"{len(v)} {k}" for k, v in codes.items()) + ".\n")
        print("Ma trận (mã → yêu cầu):")
        for name, lst in codes.items():
            for c in lst:
                cell = fmt_ids(by_code.get(c, [])) or ("miễn: " + exempt[c] if c in exempt else "—")
                print(f"  {c:5} {cell}")
        print()

    if stale:
        if args.write:
            BENCH_DOC.write_text("\n".join(new_lines), encoding="utf-8")
            print(f"Đã ghi lại cột Yêu cầu của benchmark: {len(stale)} dòng ({', '.join(stale)}).")
        else:
            errors.append(f"cột Yêu cầu của benchmark chưa khớp ở {len(stale)} dòng ({', '.join(stale)}); "
                          "chạy lại với --write")

    for w in warnings:
        print("Cảnh báo:", w)
    for e in errors:
        print("Lỗi:", e)
    if not errors:
        print("Không có lỗi.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

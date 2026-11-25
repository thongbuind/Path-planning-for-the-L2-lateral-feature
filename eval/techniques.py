"""So sánh kỹ thuật trong một planner (Software Qualification Test Specification 9.1, 10).

Đọc thư mục kết quả của eval.suite, mỗi kỹ thuật một thư mục, và xếp hạng theo 9.1: dùng khi quyết định đưa
một kỹ thuật vào planner. Chiến dịch generator của lab (PP-TS-031) không xếp hạng: dữ liệu dashboard do
eval.campaign sinh; các hàm đọc kết quả eval.study ở đây dùng chung cho nó.
"""

import argparse
import json
from collections import Counter
from pathlib import Path


from eval import compare, report

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "build" / "techniques"
STEPS = (compare.SAFETY, compare.LANE_KEEPING, compare.FLEXIBILITY, compare.COMPUTE)
# SQTS 9.1 bước 1b: số chu kỳ LCC lái được ít hơn mốc ở một lần chạy.
LCC_CYCLES_LOST_MAX = 1
EXECUTION = "execution"


# ---------------------------------------------------------------- bước 1: cửa loại

def failures(record: dict | None) -> set[str]:
    if record is None:
        return set()
    out = set(record.get("failed") or [])
    if EXECUTION in record:
        out.add(EXECUTION)
    for issue in (record.get("result") or {}).get("issues") or []:
        if issue.get("kind") == EXECUTION:
            out.add(EXECUTION)
    return out


def lcc_cycles(record: dict | None) -> int | None:
    if record is None or record.get("result") is None:
        return None
    value = (record["result"].get("info") or {}).get("lcc_driving_cycles")
    return None if value is None else int(value)


def gate(p: dict, base: dict, lost_max: int = LCC_CYCLES_LOST_MAX) -> dict:
    """1a: trượt mà mốc đạt ở cùng ca, profile, seed; 1b: LCC lái ít hơn mốc quá lost_max chu kỳ; B0."""
    new, shared, lost, unmeasured = {}, Counter(), [], 0
    for key, r in p["records"].items():
        b = base["records"].get(key)
        own, theirs = failures(r), failures(b)
        if own - theirs:
            new[key] = sorted(own - theirs)
        shared.update(own & theirs)
        mine, ref = lcc_cycles(r), lcc_cycles(b)
        if mine is None or ref is None:
            unmeasured += 1
        elif ref - mine > lost_max:
            lost.append({"case": key[0], "seed": key[1], "lost": ref - mine})
    profiles = sorted({p["records"][k].get("profile") for k in new if p["records"][k].get("profile")})
    b0 = p.get("b0")
    b0_text = "chưa chạy" if b0 is None else "trượt C1 hoặc C2" if b0.get("blocked") else "đạt C1, C2"
    return {"passed": not new and not lost and not (b0 and b0.get("blocked")),
            "new_failure_runs": len(new),
            "requirements": dict(Counter(f for v in new.values() for f in v).most_common()),
            "profiles": profiles, "shared": dict(shared.most_common()),
            "lcc_runs_lost": len(lost), "lcc_cycles_lost_max": max((x["lost"] for x in lost), default=0),
            "lcc_lost": lost[:20], "lcc_unmeasured_runs": unmeasured, "b0": b0_text,
            "evaluator_errors": sum("error" in r for r in p["records"].values())}


def rank(techniques: list[dict], baseline: str, lost_max: int = LCC_CYCLES_LOST_MAX) -> dict:
    compare.check_same_benchmark(techniques)
    by_name = {t["name"]: t for t in techniques}
    if baseline not in by_name:
        raise SystemExit(f"baseline {baseline} is not among the techniques")
    rows = {t["name"]: {"gate": gate(t, by_name[baseline], lost_max)} for t in techniques}
    kept = [t for t in techniques if rows[t["name"]]["gate"]["passed"]]
    score, duels = compare.copeland(kept) if len(kept) > 1 else ({t["name"]: {g: 0 for g in compare.GROUPS}
                                                                 for t in kept}, [])
    for name, s in score.items():
        rows[name]["copeland"] = s
    order = sorted((t["name"] for t in kept), key=lambda n: tuple(-score[n][g] for g in STEPS))
    eliminated = [t["name"] for t in techniques if t["name"] not in score]
    return {"baseline": baseline, "order": order, "eliminated": eliminated, "rows": rows, "duels": duels,
            "absolute": compare.absolute_values(techniques), "runs": len(techniques[0]["records"]),
            "techniques": [{"name": t["name"], "pp_version": t["pp_version"], "sha256": t["sha256"],
                            "folder": t["folder"]} for t in techniques]}


def gate_text(g: dict) -> str:
    if g["passed"]:
        return "đạt"
    parts = []
    if g["new_failure_runs"]:
        parts.append(f"{g['new_failure_runs']} lần chạy trượt mới")
    if g["lcc_runs_lost"]:
        parts.append(f"LCC lái ít hơn mốc ở {g['lcc_runs_lost']} lần chạy, tới {g['lcc_cycles_lost_max']} chu kỳ")
    if g["b0"] == "trượt C1 hoặc C2":
        parts.append("trượt B0")
    return "loại: " + "; ".join(parts)


def elimination_reason(name: str, g: dict) -> str:
    reqs = ", ".join(f"{k} ({v})" for k, v in list(g["requirements"].items())[:8])
    text = f"**{name} bị loại ở bước 1.**"
    if reqs:
        text += f" Trượt mới so với mốc: {reqs}. Profile có trượt mới: {', '.join(g['profiles']) or '—'}."
    if g["lcc_runs_lost"]:
        worst = max(g["lcc_lost"], key=lambda x: x["lost"])
        text += (f" LCC lái ít hơn mốc ở {g['lcc_runs_lost']} lần chạy; nhiều nhất {worst['lost']} chu kỳ "
                 f"({worst['case']}, seed {worst['seed']}).")
    return text


def markdown(c: dict) -> list[str]:
    names = [t["name"] for t in c["techniques"]]
    lines = ["# So sánh kỹ thuật", "",
             f"Mục 9.1 của Software Qualification Test Specification. Mốc: {c['baseline']}. {c['runs']} lần chạy "
             "mỗi kỹ thuật, cùng bộ ca, profile và seed. Thời gian tính đo trên máy chạy SIL, chỉ để so các kỹ thuật.",
             "", "| Kỹ thuật | Bước 1: cửa loại | " + " | ".join(f"Bước {i + 2}: {g}" for i, g in enumerate(STEPS))
             + " | Xếp hạng |", "|---|---|" + "---|" * len(STEPS) + "---|"]
    for name in names:
        row = c["rows"][name]
        cells = [str(row["copeland"][g]) if "copeland" in row else "—" for g in STEPS]
        place = str(c["order"].index(name) + 1) if name in c["order"] else "loại"
        lines.append(f"| {name} | {gate_text(row['gate'])} | " + " | ".join(cells) + f" | {place} |")
    for name in c["eliminated"]:
        lines += ["", elimination_reason(name, c["rows"][name]["gate"])]
    lines += ["", "## Bảng tổng", "", "Giá trị xấu nhất của mỗi performance target qua mọi seed (mục 10).", "",
              "| Performance target | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    targets = sorted({k for v in c["absolute"].values() for k in v})
    for key in targets:
        cells = [compare._f(c["absolute"][n].get(key, {}).get("worst")) for n in names]
        lines.append(f"| {key} | " + " | ".join(cells) + " |")
    if not c["eliminated"]:
        lines += ["", "Chưa có kỹ thuật nào bị loại; báo cáo cần ít nhất một kỹ thuật bị loại kèm số liệu (mục 9.1)."]
    return lines


# ---------------------------------------------------------------- kết quả của eval.study

def _plain(spec: list) -> list:
    return [x for x in spec if not isinstance(x, dict)]


def matches(spec: list, pattern: list) -> bool:
    """[S1, f]: ca S1 biến thể f không lỗi; [S12]: cả họ; [F01] hoặc [F01, c]: mọi lần chạy có lỗi đó;
    [S1, c, F01, c]: đúng tổ hợp. Khóa mô phỏng (profile, acc...) không xét.
    """
    spec = _plain(spec)
    family, rest = spec[0], spec[1:]
    fault, level = (rest[1], rest[2]) if len(rest) >= 3 else (None, None)
    head = str(pattern[0])
    if head.startswith("F"):
        return fault == head and (len(pattern) < 2 or level == pattern[1])
    if family != head:
        return False
    if len(pattern) == 1:
        return True
    if rest[0] != pattern[1]:
        return False
    if len(pattern) == 2:
        return fault is None
    return fault == pattern[2] and (len(pattern) < 4 or level == pattern[3])


def _record(row: dict) -> tuple[dict, dict]:
    spec = row.get("spec") or []
    plain, sim = _plain(spec), next((x for x in spec if isinstance(x, dict)), {})
    case = {"id": row["run"], "family": plain[0] if plain else row["run"],
            "parameters": {"variant": plain[1] if len(plain) > 1 else None,
                           "fault": plain[2:4] or None, **sim, "profile": row.get("profile")}}
    info = {k: row.get(k) for k in ("lcc_driving_cycles", "lcc_requested_cycles", "path_near_limit_share",
                                    "hwa_share_after_request")}
    info.update(row.get("vehicle") or {})
    record = {"case": row["run"], "seed": row["seed"], "profile": row.get("profile"), "scope": None,
              "failed": list(row.get("failed") or []), "spec": spec, "loop": row.get("loop"),
              "compute_lcc_ms": row.get("compute_lcc_ms") or {}, "open_loop_file": row.get("open_loop_file"),
              "result": {"criteria": row.get("criteria") or [], "targets": row.get("targets") or [],
                         "issues": row.get("issues") or [], "case_failures": row.get("case_failures") or [],
                         "info": info}}
    return case, record


def _lcc_library(manifest: dict, build: str) -> dict:
    build_dir = Path(build).resolve()
    for info in manifest.get("libraries", []):
        path = (ROOT / info["path"]).resolve()
        if path.parent == build_dir and info.get("family", "lcc") == "lcc" and "lkaelk" not in path.name:
            return info
    return {}


def load_study(folder: Path, plan: dict, part: str) -> list[dict]:
    folder = Path(folder)
    results = json.loads((folder / "results.json").read_text(encoding="utf-8"))
    manifest_path = folder / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
    out = []
    for entry in results:
        if entry["part"] != part:
            continue
        cases, records = {}, {}
        for row in entry["runs"]:
            case, record = _record(row)
            cases[case["id"]] = case
            records[(row["run"], row["seed"])] = record
        lib = _lcc_library(manifest, entry["library"])
        b0_path = folder / "conformance" / f"{entry['set']}.json"
        variant = plan["variants"].get(entry["set"], {})
        out.append({"folder": str(folder / entry["set"]), "name": entry["set"],
                    "pp_version": lib.get("pp_version"), "sha256": lib.get("sha256"),
                    "state_size_bytes": lib.get("state_size_bytes"), "file_size_bytes": lib.get("file_size_bytes"),
                    "b0": json.loads(b0_path.read_text(encoding="utf-8")) if b0_path.is_file() else None,
                    "generation_sha256": f"{plan['suite']}:{part}", "partial": False,
                    "cases": cases, "records": records, "calibration": entry.get("values") or {},
                    "ranked": variant.get("ranked", True), "description": variant.get("description", "")})
    return out


def _units(p: dict, patterns: list | None) -> set | None:
    if not patterns:
        return None
    return {k for k, r in p["records"].items() if any(matches(r["spec"], pat) for pat in patterns)}


def _metrics_of(techniques: list[dict], target: str) -> list[tuple[str, str]]:
    seen = set()
    for t in techniques:
        for r in t["records"].values():
            seen |= {m for m in compare._targets(r) if m[0] == target}
    return sorted(seen)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Technique comparison within one planner (Software Qualification Test Specification "
            "9.1, 10)."
        ),
    )
    parser.add_argument("folders", nargs="*", type=Path, help="eval.suite output folders, one per technique")
    parser.add_argument("--name", action="append", help="Technique name per folder, in order")
    parser.add_argument("--baseline", help="Name of the delivered technique (step 1a, 1b)")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if len(args.folders) < 2:
        parser.error("compare at least two techniques (lab campaign: python3 -m eval.campaign)")
    if not args.baseline:
        parser.error("--baseline names the delivered technique (Software Qualification Test Specification 9.1, 1a)")
    if args.name and len(args.name) != len(args.folders):
        parser.error("one --name per folder")
    names = args.name or [None] * len(args.folders)
    techniques = [compare.load(f, n) for f, n in zip(args.folders, names)]
    if len({t["name"] for t in techniques}) != len(techniques):
        parser.error("technique names must differ; use --name")
    c = rank(techniques, args.baseline)
    out = args.out or OUT_DIR / "-".join(t["name"] for t in techniques)
    out.mkdir(parents=True, exist_ok=True)
    (out / "techniques.json").write_text(json.dumps(c, indent=1, ensure_ascii=False, default=report.jsonable) + "\n",
                                         encoding="utf-8")
    (out / "report.md").write_text("\n".join(markdown(c)) + "\n", encoding="utf-8")
    print("\n".join(markdown(c)[:6 + len(techniques)]))
    print(f"\n{out / 'report.md'}")


if __name__ == "__main__":
    main()

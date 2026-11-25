"""Tóm tắt các lần quick bench của luồng C từ build/lab/<nhãn>/quick.json (nháp L1, không trích trong study).

- lệch output vòng hở so với một nhãn tham chiếu (eval.output_diff, đoạn 0–1 s): max, p99, mean trên mọi chu kỳ
  ghép được của các dòng vòng hở;
- trung vị p99 thời gian LCC (016) trên các dòng, và tỉ số ghép cặp theo dòng so với một nhãn khác;
- dòng trượt, telemetry (fallback, infer_ops) nếu có.
"""

import argparse
import json

import numpy as np

import common  # noqa: F401  (sys.path)
from common import LAB, ROOT

BENCH = ROOT / "build" / "lab"


def load(label: str) -> dict:
    return json.loads((BENCH / label / "quick.json").read_text(encoding="utf-8"))


def diff(label: str, ref: str) -> dict:
    from eval import output_diff
    a, b = load(label), load(ref)
    other = {(r["run"], r["seed"]): r for r in b["rows"]}
    per = []
    values = []
    for r in a["rows"]:
        o = other.get((r["run"], r["seed"]))
        if not (o and r.get("open_loop_file") and o.get("open_loop_file")):
            continue
        ra = output_diff.load(BENCH / label / r["open_loop_file"])
        rb = output_diff.load(BENCH / ref / o["open_loop_file"])
        stats = output_diff.compare_runs(ra, rb)
        per.append(stats)
        common_t, ia, ib = np.intersect1d(ra["t0_us"], rb["t0_us"], return_indices=True)
        both = ra["valid"][ia] & rb["valid"][ib] & (ra["digest"][ia] == rb["digest"][ib])
        values.append(np.max(np.abs(ra["y"][ia][both] - rb["y"][ib][both]), axis=1))
    v = np.concatenate(values) if values else np.zeros(0)
    return {"max_m": float(v.max()) if v.size else None, "p99_m": float(np.percentile(v, 99)) if v.size else None,
            "mean_m": float(v.mean()) if v.size else None, "cycles": int(v.size),
            "digest_mismatch": int(sum(s["digest_mismatch"] for s in per)),
            "valid_mismatch": int(sum(s["valid_mismatch"] for s in per)),
            "run_max_m": [s["max_m"] for s in per]}


def timing(label: str, against: str | None = None, keep: set | None = None) -> dict:
    """keep: chỉ các (run, seed) này (QUICK của quick.py đổi theo PP-T7; so trên phần chung của mọi nhãn)."""
    a = load(label)
    p99 = [(r["run"], r["seed"], (r.get("compute_lcc_ms") or {}).get("p99")) for r in a["rows"]
           if keep is None or (r["run"], r["seed"]) in keep]
    out = {"p99_median_ms": float(np.median([x[2] for x in p99 if x[2] is not None]))}
    if against:
        b = {(r["run"], r["seed"]): (r.get("compute_lcc_ms") or {}).get("p99") for r in load(against)["rows"]}
        ratios = [x[2] / b[(x[0], x[1])] for x in p99 if x[2] and b.get((x[0], x[1]))]
        out["p99_ratio_median"] = float(np.median(ratios))
        out["p99_ratios"] = [round(r, 3) for r in ratios]
    return out


def failures(label: str) -> list:
    return [(r["run"], r["seed"], r["failed"]) for r in load(label)["rows"] if r["failed"]]


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarise stream-C quick bench results")
    parser.add_argument("labels", nargs="*")
    parser.add_argument("--ref", help="Reference label for output differences")
    parser.add_argument("--timing-against", help="Label for paired p99 ratios")
    parser.add_argument("--common", action="store_true", help="Timing only on runs present in every label")
    args = parser.parse_args()
    keep = None
    if args.common:
        sets = [{(r["run"], r["seed"]) for r in load(x)["rows"]} for x in args.labels + [args.timing_against] if x]
        keep = set.intersection(*sets)
    for label in args.labels:
        row = {"label": label, "failed": failures(label)}
        if args.ref:
            row["diff"] = diff(label, args.ref)
        row["timing"] = timing(label, args.timing_against, keep)
        tm = [r.get("t7_telemetry") for r in load(label)["rows"] if r.get("t7_telemetry")]
        if tm:
            row["telemetry"] = [{"fallback_share": t["fallback_share"], "codes": t["fallback_codes"],
                                 "infer_ops_max": t["infer_ops_max"], "work_max": (t["work"] or {}).get("max")}
                                for t in tm]
        print(json.dumps(row))


if __name__ == "__main__":
    main()

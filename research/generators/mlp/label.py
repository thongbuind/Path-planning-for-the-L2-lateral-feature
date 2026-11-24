"""Gom bản ghi của teacher thành bộ dữ liệu, chỉ nhận nhãn khi nghiệm 1000 vòng đạt ngưỡng chất lượng.

Ngưỡng chốt trên phần validation (THRESHOLDS, lý do ở data_card.md); --report in phân bố trên validation để chốt.
Mẫu bị loại (không hữu hạn, không hội tụ, bất khả thi) ghi riêng ở rejected.npz, không vào huấn luyện.
Bộ dữ liệu giữ cả bài toán QP từng cửa sổ (float64) để giải lại offline (nhãn lưới trọng số của
qp_jerk_admm_mlp_weights).
"""

import argparse
import json

import numpy as np

import common
from common import F, N, OUT, TR, TR_FEATURES, TR_LABEL, TR_DRIVE, TR_PROBLEM

RAW = OUT / "raw"
RAW_DAGGER = OUT / "raw_dagger"
MAX_WINDOWS = 10_000  # Trần của PP-TS-031 cho cả bộ (train + validation + ngoài miền).
# Chốt 2026-11-24 trên validation (data_card.md mục Nhãn), qp.c sau commit 28c4995: lũy thừa 10 nhỏ nhất trên giá
# trị lớn nhất của validation (primal 3,3e-5, dual 1,4e-4, vi phạm 2,1e-7). Residual tương đối; vi phạm theo đơn
# vị hàng (m/s², m/s³).
THRESHOLDS = {"primal": 1e-4, "dual": 1e-3, "violation": 1e-6}


def load_raw(manifest: dict, raw=RAW, source: str = "qp") -> dict:
    rows, meta = [], []
    for spec in manifest["scenarios"]:
        path = raw / f"{spec['id']}.npz"
        if not path.exists():
            continue
        rec = np.load(path)["records"]
        rows.append(rec)
        for r in rec:
            meta.append((spec["id"], int(r[TR["COUNT"]]), spec["split"], spec["family"], spec["noise"],
                         spec["profile"], spec["speed_mps"], spec["loop"], source))
    rec = np.concatenate(rows) if rows else np.zeros((0, common.TR_DOUBLES))
    cols = list(zip(*meta)) if meta else [[]] * len(KEYS)
    return {"records": rec, **{k: np.asarray(v) for k, v in zip(KEYS, cols)}}


KEYS = ("scenario", "call", "split", "family", "noise", "profile", "speed", "loop", "source")


def merge(a: dict, b: dict) -> dict:
    return {k: np.concatenate([a[k], b[k]]) for k in a}


def cap(data: dict, limit: int = MAX_WINDOWS, seed: int = 100) -> tuple[dict, int]:
    """Giữ ≤ limit cửa sổ: bỏ ngẫu nhiên (seed cố định) cửa sổ train/validation do QP lái; giữ mọi cửa sổ DAgger
    và ngoài miền. Bỏ trước khi lọc nhãn để trần áp lên mọi cửa sổ đã thu."""
    extra = len(data["split"]) - limit
    if extra <= 0:
        return data, 0
    pool = np.flatnonzero((data["source"] == "qp") & (data["split"] != "ood"))
    drop = np.random.default_rng(seed).choice(pool, size=extra, replace=False)
    keep = np.ones(len(data["split"]), bool)
    keep[drop] = False
    return {k: v[keep] for k, v in data.items()}, int(extra)


def quality(rec: np.ndarray) -> dict:
    return {"label_ok": rec[:, TR["LABEL_OK"]] == 1.0, "primal": rec[:, TR["PRIMAL"]],
            "dual": rec[:, TR["DUAL"]], "violation": rec[:, TR["VIOLATION"]]}


def accept(rec: np.ndarray, th: dict = THRESHOLDS) -> np.ndarray:
    q = quality(rec)
    finite = np.all(np.isfinite(rec[:, TR_LABEL:TR_LABEL + N]), axis=1) & np.all(
        np.isfinite(rec[:, TR_FEATURES:TR_FEATURES + F]), axis=1)
    with np.errstate(invalid="ignore"):
        return (q["label_ok"] & finite & (q["primal"] <= th["primal"]) & (q["dual"] <= th["dual"])
                & (q["violation"] <= th["violation"]))


def report(data: dict) -> None:
    rec = data["records"]
    for split in ("train", "validation", "ood"):
        m = data["split"] == split
        q = quality(rec[m])
        print(f"{split}: {m.sum()} windows, label_ok {q['label_ok'].mean():.4f}")
        for k in ("primal", "dual", "violation"):
            v = q[k][np.isfinite(q[k])]
            pct = np.percentile(v, [50, 90, 99, 99.5, 99.9, 100]) if v.size else []
            print(f"  {k}: p50/90/99/99.5/99.9/max = " + " ".join(f"{x:.2e}" for x in pct))
            for t in (1e-6, 1e-4, 1e-3, 1e-2, 1e-1):
                print(f"     > {t:g}: {np.mean(v > t):.4f}", end="")
            print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble the labelled MLP dataset")
    parser.add_argument("--manifest", default=str(OUT / "manifest.json"))
    parser.add_argument("--dagger", help="Manifest of the DAgger round (raw_dagger/) to merge")
    parser.add_argument("--report", action="store_true", help="Print label-quality distributions only")
    args = parser.parse_args()
    import slots
    manifest = json.loads(open(args.manifest, encoding="utf-8").read())
    with slots.hold(1, "mlp label"):
        data = load_raw(manifest)
        dropped = 0
        if args.dagger:
            data = merge(data, load_raw(json.loads(open(args.dagger, encoding="utf-8").read()), RAW_DAGGER, "dagger"))
            data, dropped = cap(data)
        if args.report:
            report(data)
            return
        rec = data["records"]
        ok = accept(rec)
        feats = rec[:, TR_FEATURES:TR_FEATURES + F]
        ref = common.features(common.unpack_problem(rec[:, TR_PROBLEM:]))
        feature_gap = float(np.nanmax(np.abs(feats - ref))) if len(rec) else 0.0
        keys = {k: data[k] for k in KEYS}
        for mask, name in ((ok, "dataset.npz"), (~ok, "rejected.npz")):
            np.savez_compressed(OUT / name, x=feats[mask].astype(np.float32), y=rec[mask, TR_LABEL:TR_LABEL + N].astype(np.float32),
                                drive=rec[mask, TR_DRIVE:TR_DRIVE + N].astype(np.float32),
                                start=rec[mask][:, TR_PROBLEM:TR_PROBLEM + 3], problem=rec[mask, TR_PROBLEM:],
                                quality=rec[mask][:, [TR["PRIMAL"], TR["DUAL"], TR["VIOLATION"], TR["VIOL_AY"], TR["VIOL_JERK"], TR["SLACK"]]],
                                flags=rec[mask][:, [TR["FROM_OLD"], TR["RECENTERING"], TR["FOLLOW"], TR["FROM_CAR"], TR["REF_WARM"], TR["DRIVE_WARM"]]],
                                **{k: v[mask] for k, v in keys.items()})
        summary = {"thresholds": THRESHOLDS, "feature_gap_c_vs_python": feature_gap, "max_windows": MAX_WINDOWS,
                   "dropped_for_cap": dropped, "dagger_windows": int((data["source"] == "dagger").sum()),
                   "splits": {}}
        for split in ("train", "validation", "ood"):
            m = data["split"] == split
            summary["splits"][split] = {"windows": int(m.sum()), "accepted": int((m & ok).sum()),
                                        "rejected": int((m & ~ok).sum()),
                                        "scenarios": int(len(set(data["scenario"][m])))}
            lst = sorted(f"{s}:{c}" for s, c in zip(data["scenario"][m & ok], data["call"][m & ok]))
            (OUT / f"list_{split}.txt").write_text("\n".join(lst) + "\n", encoding="utf-8")
        reasons = {}
        q = quality(rec)
        with np.errstate(invalid="ignore"):
            for name, bad in (("label_not_finite", ~q["label_ok"]), ("primal", q["primal"] > THRESHOLDS["primal"]),
                              ("dual", q["dual"] > THRESHOLDS["dual"]),
                              ("violation", q["violation"] > THRESHOLDS["violation"])):
                reasons[name] = {s: int((bad & (data["split"] == s)).sum()) for s in ("train", "validation", "ood")}
        summary["reject_reasons"] = reasons
        (OUT / "label_summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
        print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()

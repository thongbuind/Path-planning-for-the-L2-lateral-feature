"""Nhãn "trọng số tốt nhất" cho qp_jerk_admm_mlp_weights (PP-TS-031 mục 2, cách i).

Mỗi cửa sổ của dataset.npz (luồng C, vòng 1): giải lại QP ở mọi ô của resolve.GRID, chấm bằng resolve.score, nhãn là
resolve.pick. Ô có nghiệm không đạt ngưỡng chất lượng bị bỏ (S = +inf); ô mặc định không đạt thì cửa sổ không có nhãn.

    python3 grid_labels.py --sample 40      # mẫu nhỏ: đo thời gian, bộ nhớ, hội tụ; không ghi nhãn
    python3 grid_labels.py                  # cả bộ (chạy nặng: hỏi trước), ghi build/lab/mlp_weights/labels.npz
"""

import argparse
import json
import resource
import sys
import time

import numpy as np

import resolve
from resolve import GRID, OUT, common

DATASET = common.OUT / "round1" / "dataset.npz"


def load(path=DATASET) -> dict:
    with np.load(path) as d:
        return {k: d[k] for k in d.files}


def window(solver, problem, warm, dt_before, iters=resolve.LABEL_ITERS):
    """Mọi ô của lưới cho một cửa sổ: (ok[G], terms[G, 3], scores[G], label hoặc -1)."""
    g = len(GRID)
    ok = np.zeros(g, bool)
    t = np.full((g, 3), np.nan)
    for i, w in enumerate(GRID):
        jerk, stats = solver.solve(problem, warm, dt_before, w, iters)
        if jerk is not None and resolve.accepted(stats):
            ok[i] = True
            t[i] = resolve.terms(problem, jerk)
    s = np.where(ok, resolve.score(t), np.inf)
    return ok, t, s, (resolve.pick(s) if ok[resolve.DEFAULT_INDEX] else -1)


def rss_mb() -> float:
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return peak / (1024 * 1024) if sys.platform == "darwin" else peak / 1024


def sample(data: dict, count: int, seed: int = 100) -> dict:
    """Đo trên `count` cửa sổ train ngẫu nhiên: CPU mỗi cửa sổ, RSS, hội tụ ở ô mặc định so với nhãn của teacher và
    so với gấp đôi số vòng."""
    solver = resolve.Solver()
    rng = np.random.default_rng(seed)
    idx = rng.choice(np.flatnonzero(data["split"] == "train"), size=count, replace=False)
    dtb = resolve.ref_dtarget(data["scenario"][idx], data["call"][idx])
    warm = data["flags"][idx, 4] > 0.5
    cpu0 = time.process_time()
    accepted, no_label = [], 0
    for k, i in enumerate(idx):
        ok, _, _, lab = window(solver, data["problem"][i], warm[k], dtb[k])
        accepted.append(ok.mean())
        no_label += int(lab < 0)
    cpu = time.process_time() - cpu0
    # Hội tụ ở ô mặc định: lệch d (0–3 s) so với nhãn teacher (1000 vòng, warm) và so với 2000 vòng lạnh.
    gaps_teacher, gaps_double, solve_cpu = [], [], []
    for k, i in enumerate(idx):
        p = data["problem"][i]
        c = time.process_time()
        j1, _ = solver.solve(p, warm[k], dtb[k], resolve.DEFAULT)
        solve_cpu.append(time.process_time() - c)
        j2, _ = solver.solve(p, warm[k], dtb[k], resolve.DEFAULT, 2 * resolve.LABEL_ITERS)
        start = data["start"][i]
        d1, d2 = common.integrate(start, j1), common.integrate(start, j2)
        dt = common.integrate(start, data["y"][i].astype(float))
        gaps_teacher.append(np.abs(d1 - dt).max())
        gaps_double.append(np.abs(d1 - d2).max())
    per_window = cpu / count
    n_all = len(data["split"])
    return {"windows": int(count), "grid": int(len(GRID)), "iters": resolve.LABEL_ITERS,
            "cpu_s": round(cpu, 2), "cpu_s_per_window": round(per_window, 4),
            "cpu_ms_per_solve": round(1e3 * float(np.median(solve_cpu)), 3),
            "estimate_full_cpu_min": round(per_window * n_all / 60.0, 1), "dataset_windows": int(n_all),
            "peak_rss_mb": round(rss_mb(), 1), "grid_cells_accepted_mean": round(float(np.mean(accepted)), 4),
            "windows_without_label": int(no_label),
            "default_vs_teacher_d_gap_m": {"p50": float(np.median(gaps_teacher)), "max": float(np.max(gaps_teacher))},
            "default_1000_vs_2000_d_gap_m": {"p50": float(np.median(gaps_double)), "max": float(np.max(gaps_double))}}


def full(data: dict) -> dict:
    solver = resolve.Solver()
    n, g = len(data["split"]), len(GRID)
    dtb = resolve.ref_dtarget(data["scenario"], data["call"])
    warm = data["flags"][:, 4] > 0.5
    ok = np.zeros((n, g), bool)
    t = np.full((n, g, 3), np.nan)
    s = np.full((n, g), np.inf)
    label = np.full(n, -1)
    cpu0 = time.process_time()
    for i in range(n):
        ok[i], t[i], s[i], label[i] = window(solver, data["problem"][i], warm[i], dtb[i])
        if (i + 1) % 500 == 0:
            print(f"{i + 1}/{n} windows, {time.process_time() - cpu0:.0f} s CPU", flush=True)
    np.savez_compressed(OUT / "labels.npz", grid=GRID, ok=ok, terms=t, scores=s, label=label,
                        weights=np.where(label[:, None] >= 0, GRID[np.maximum(label, 0)], np.nan),
                        scenario=data["scenario"], call=data["call"], split=data["split"],
                        dataset_sha256=common.sha256_file(DATASET))
    summary = {"windows": int(n), "labelled": int((label >= 0).sum()), "cpu_s": round(time.process_time() - cpu0, 1),
               "peak_rss_mb": round(rss_mb(), 1), "default_share": {}, "label_counts": {}}
    for split in ("train", "validation", "ood"):
        m = (data["split"] == split) & (label >= 0)
        summary["default_share"][split] = float(np.mean(label[m] == resolve.DEFAULT_INDEX)) if m.any() else None
        summary["label_counts"][split] = {int(k): int(v) for k, v in zip(*np.unique(label[m], return_counts=True))}
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Grid labels of qp_jerk_admm_mlp_weights")
    parser.add_argument("--sample", type=int, help="Timing sample of this many train windows (writes no labels)")
    args = parser.parse_args()
    sys.path.insert(0, str(common.LAB / "bench"))
    import slots
    OUT.mkdir(parents=True, exist_ok=True)
    data = load()
    with slots.hold(1, "mlp_weights label"):
        result = sample(data, args.sample) if args.sample else full(data)
    name = "label_sample.json" if args.sample else "label_summary.json"
    (OUT / name).write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()

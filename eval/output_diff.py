"""Lệch output của LCC planner giữa hai build ở vòng hở, ghép cặp theo từng chu kỳ (PP-TS-031).

Ở vòng hở xe đi theo path định trước, nên đầu vào của planner không phụ thuộc build. Một chu kỳ chỉ được
so khi digest đầu vào của hai build trùng nhau. Chỉ đọc output qua interface (Trajectory, LccStatus).
"""

import hashlib
import math
from pathlib import Path

import numpy as np

from interfaces import TRAJECTORY_STEP_S

# Đoạn 0–1 s như PP-SWR-050.
WINDOW_S = 1.0
GRID_S = np.round(np.arange(0.0, WINDOW_S + 1e-9, float(TRAJECTORY_STEP_S)), 6)
# Path "khác" khi lệch lớn nhất trên 0–1 s vượt dung sai của lệch ngang PP-SWR-050 (SQTS 9.2).
DIFFERS_M = 0.005


def input_digest(cycle) -> int:
    """Digest những gì harness ghi lại về đầu vào của chu kỳ: stamp, thời điểm nhận, valid của từng
    kênh, trạng thái biên làn, FunctionRequests, LongitudinalPlan, LeadTarget và cờ usable. Nội dung
    lane model không có trong log; ở vòng hở nó chỉ phụ thuộc vị trí xe và seed.
    """
    parts = (cycle.t0_us, cycle.t0_local_us, cycle.input_times, cycle.lane_boundaries, cycle.inputs_ok,
             cycle.lane_view_reported, cycle.function_requests, cycle.longitudinal_plan, cycle.lead_target)
    text = repr(parts).encode("utf-8")
    return int.from_bytes(hashlib.blake2b(text, digest_size=8).digest(), "little")


def _lateral_on_grid(traj) -> np.ndarray | None:
    t = np.array([p.time_from_start for p in traj.points], dtype=float)
    y = np.array([p.pose.y for p in traj.points], dtype=float)
    if len(t) < 2 or t[0] > 1e-6 or t[-1] < WINDOW_S - 1e-6 or not np.all(np.isfinite(y)):
        return None
    return np.interp(GRID_S, t, y)


def cycle_outputs(log) -> dict[str, np.ndarray]:
    n = len(log.cycles)
    out = {"t0_us": np.zeros(n, dtype=np.int64), "digest": np.zeros(n, dtype=np.uint64),
           "valid": np.zeros(n, dtype=bool), "y": np.full((n, len(GRID_S)), np.nan)}
    for i, c in enumerate(log.cycles):
        out["t0_us"][i] = c.t0_us
        out["digest"][i] = input_digest(c)
        traj, status = c.lcc_trajectory, c.lcc_status
        if traj is None or status is None or not (traj.header.valid and status.path_valid):
            continue
        y = _lateral_on_grid(traj)
        if y is not None:
            out["valid"][i] = True
            out["y"][i] = y
    return out


def save(path: Path, outputs: dict[str, np.ndarray]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **outputs)


def load(path: Path) -> dict[str, np.ndarray]:
    with np.load(path) as data:
        return {k: data[k] for k in data.files}


def compare_runs(a: dict[str, np.ndarray], b: dict[str, np.ndarray]) -> dict:
    """Thống kê lệch của A so với B trên các chu kỳ cùng t0 và cùng digest đầu vào."""
    common, ia, ib = np.intersect1d(a["t0_us"], b["t0_us"], return_indices=True)
    same = a["digest"][ia] == b["digest"][ib]
    va, vb = a["valid"][ia] & same, b["valid"][ib] & same
    both = va & vb
    diff = np.max(np.abs(a["y"][ia][both] - b["y"][ib][both]), axis=1) if np.any(both) else np.zeros(0)
    return {"cycles": int(len(common)), "digest_mismatch": int(np.count_nonzero(~same)),
            "valid_mismatch": int(np.count_nonzero(va != vb)), "compared": int(len(diff)),
            "max_m": float(diff.max()) if len(diff) else None,
            "p99_m": float(np.percentile(diff, 99)) if len(diff) else None,
            "mean_m": float(diff.mean()) if len(diff) else None,
            "differs": int(np.count_nonzero(diff > DIFFERS_M))}


def aggregate(per_run: list[dict]) -> dict:
    compared = sum(r["compared"] for r in per_run)
    maxima = [r["max_m"] for r in per_run if r["max_m"] is not None]
    mean = (sum(r["mean_m"] * r["compared"] for r in per_run if r["compared"]) / compared) if compared else None
    return {"runs": len(per_run), "cycles": sum(r["cycles"] for r in per_run),
            "digest_mismatch": sum(r["digest_mismatch"] for r in per_run),
            "valid_mismatch": sum(r["valid_mismatch"] for r in per_run), "compared": compared,
            "max_m": max(maxima) if maxima else None,
            "p99_run_max_m": max((r["p99_m"] for r in per_run if r["p99_m"] is not None), default=None),
            "mean_m": mean,
            "differs_share": sum(r["differs"] for r in per_run) / compared if compared else None}


def _key(row: dict) -> tuple:
    return (row["run"], row["seed"])


def compare_entries(a: dict, b: dict) -> dict:
    """a, b: hai mục cùng part trong results.json của eval.study."""
    root_a, root_b = Path(a["library"]).parent, Path(b["library"]).parent
    rows_b = {_key(r): r for r in b["runs"] if r.get("open_loop_file")}
    per_run = []
    for row in a["runs"]:
        other = rows_b.get(_key(row))
        if not row.get("open_loop_file") or other is None:
            continue
        stats = compare_runs(load(root_a / row["open_loop_file"]), load(root_b / other["open_loop_file"]))
        per_run.append({"run": row["run"], "seed": row["seed"], **stats})
    return {"a": a["set"], "b": b["set"], "part": a["part"], **aggregate(per_run), "per_run": per_run}


def anchors(plan: dict) -> list[str]:
    """Mốc so output: kỹ thuật đang giao và mọi nghiệm tham chiếu ghi trong giả thuyết."""
    names = [plan["baseline"]] if plan.get("baseline") else []
    for h in plan.get("hypotheses", []):
        if h.get("reference") and h["reference"] not in names:
            names.append(h["reference"])
    return names


def study_diffs(results: list[dict], plan: dict) -> dict:
    entries = {(r["set"], r["part"]): r for r in results}
    pairs = []
    for (name, part), entry in sorted(entries.items()):
        for anchor in anchors(plan):
            other = entries.get((anchor, part))
            if anchor == name or other is None:
                continue
            pairs.append(compare_entries(entry, other))
    return {"window_s": WINDOW_S, "differs_m": DIFFERS_M, "anchors": anchors(plan), "pairs": pairs}


def lookup(diffs: dict | None, a: str, b: str, part: str = "test") -> dict | None:
    if not diffs:
        return None
    return next((p for p in diffs["pairs"] if p["a"] == a and p["b"] == b and p["part"] == part), None)


def finite(value) -> bool:
    return value is not None and math.isfinite(value)

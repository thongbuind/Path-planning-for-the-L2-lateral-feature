"""Result presentation of Software Qualification Test Specification 8.3 and 10.

Suite level (records of eval.suite or eval.matrix):
- flexibility(records): profile x indicator table, worst profile marked (8.3, B7)
- compute(records, out): histogram of planner compute time with p95, p99 (PP-SWR-016, B8)
- dtle_by_v_lat(records, cases, out): smallest DTLE by lateral speed for S4 to S8
- sweep(records, out): indicators by swept simulator value, one line per run (6.1, Q1 to Q4)

Run level:
- run_figure(log, result, path): d(t) of path and car with the lane boundaries, a_y, jerk,
  function driving, function changes and fault windows; continuity between consecutive paths
  with the threshold.

Each function returns markdown lines; figures are PNG files next to the report. Values are
read from the results only (black box, CLAUDE.md "Planner và đánh giá phát triển độc lập").
"""

from collections import defaultdict
import json
import math
from pathlib import Path

import numpy as np

from eval.metrics import COMPUTE_BINS_MS

# Indicators of the flexibility table: safety and comfort targets of 9.1 steps 2 and 3, and
# the requirement pass rate (8.3 point 1).
LARGER_IS_BETTER = {"PP-SWR-057", "PP-SWR-064", "PP-SWR-087"}  # 8.2 "Tốt hơn khi"
FLEX_TARGETS = ("PP-SWR-050", "PP-SWR-057", "PP-SWR-087", "PP-SWR-002", "PP-SWR-004", "PP-SWR-053",
                "PP-SWR-059", "PP-SWR-081", "PP-SWR-082")


def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def _fmt(v, digits=3):
    if v is None or (isinstance(v, float) and not math.isfinite(v)):
        return "—"
    return f"{v:.{digits}g}"


def _label(key: str) -> str:
    """'id|metric' as a table cell (a raw '|' would split the column)."""
    return key.replace("|", " ")


def _targets(record) -> dict[str, float]:
    """'id|metric' -> value of one run record."""
    result = record.get("result") or {}
    return {f"{t['id']}|{t['metric']}": t["value"] for t in result.get("targets", [])
            if t.get("value") is not None and math.isfinite(t["value"])}


def _unit_key(record, cases) -> str:
    """A concrete case without its profile, and the seed: the unit of 8.3."""
    case = cases.get(record.get("case"))
    if case is None:  # eval.matrix record
        return json.dumps([record.get("run"), record.get("acc"), record.get("sim"), record.get("seed")],
                          sort_keys=True, default=str)
    params = {k: v for k, v in case.get("parameters", {}).items() if k != "profile"}
    return json.dumps([case.get("family"), case.get("anchor"), case.get("host"), params,
                       case.get("inject"), record.get("seed")], sort_keys=True, default=str)


# ---- 8.3 Flexibility -----------------------------------------------------------------------

def flexibility(records, cases) -> list[str]:
    runs = [r for r in records if "result" in r and r.get("profile")]
    profiles = sorted({r["profile"] for r in runs})
    if len(profiles) < 2:
        return ["", "## Flexibility", "", "Chỉ một profile: không có bảng flexibility (mục 8.3)."]
    per_profile = defaultdict(lambda: {"runs": 0, "passed": 0, "values": defaultdict(list)})
    units = defaultdict(lambda: defaultdict(dict))  # unit -> indicator -> profile -> value
    # Worst value per profile only over units run on every profile: samples, fault and event
    # cases on fewer profiles would compare different case sets (5.2).
    unit_profiles = defaultdict(set)
    for r in runs:
        unit_profiles[_unit_key(r, cases)].add(r["profile"])
    complete = {u for u, seen in unit_profiles.items() if len(seen) == len(profiles)}
    for r in runs:
        row = per_profile[r["profile"]]
        row["runs"] += 1
        row["passed"] += not r.get("failed")
        unit = _unit_key(r, cases)
        for key, value in _targets(r).items():
            if key.split("|")[0] in FLEX_TARGETS:
                if unit in complete:
                    row["values"][key].append(value)
                units[unit][key][r["profile"]] = value
    indicators = sorted({k for row in per_profile.values() for k in row["values"]})

    def worst(key, values):
        return min(values) if key.split("|")[0] in LARGER_IS_BETTER else max(values)

    lines = ["", "## Flexibility", "",
             "Cùng bản build và bộ calibration trên mọi profile (mục 8.3). Ô là giá trị xấu nhất của profile "
             "trên các ca chạy đủ mọi profile; **đậm** là profile tệ nhất của chỉ số. Tỉ lệ đạt tính trên mọi lần chạy.", "",
             "| Profile | Lần chạy | Tỉ lệ đạt requirement | " + " | ".join(_label(k) for k in indicators) + " |",
             "|---|---|---|" + "---|" * len(indicators)]
    worst_profile = {}
    for key in indicators:
        vals = {p: worst(key, per_profile[p]["values"][key]) for p in profiles if per_profile[p]["values"][key]}
        if vals:
            worst_profile[key] = (min if key.split("|")[0] in LARGER_IS_BETTER else max)(vals, key=vals.get)
    for p in profiles:
        row = per_profile[p]
        rate = row["passed"] / row["runs"] if row["runs"] else float("nan")
        cells = []
        for key in indicators:
            v = worst(key, row["values"][key]) if row["values"][key] else None
            text = _fmt(v)
            cells.append(f"**{text}**" if worst_profile.get(key) == p else text)
        lines.append(f"| {p} | {row['runs']} | {rate:.1%} | " + " | ".join(cells) + " |")
    lines += ["", "| Chỉ số | Độ chênh lớn nhất giữa profile | Độ chênh nhỏ nhất | Profile tệ nhất |", "|---|---|---|---|"]
    for key in indicators:
        spreads = [max(v.values()) - min(v.values()) for u in units.values() if len(v := u.get(key, {})) >= 2]
        lines.append(f"| {_label(key)} | {_fmt(max(spreads) if spreads else None)} | "
                     f"{_fmt(min(spreads) if spreads else None)} | {worst_profile.get(key, '—')} |")
    failing = [p for p in profiles if per_profile[p]["passed"] < per_profile[p]["runs"]]
    lines += ["", "Requirement đạt 100 % trên mọi profile: " + ("có" if not failing else "không (" + ", ".join(failing) + ")")]
    return lines


# ---- PP-SWR-016 compute time -----------------------------------------------------------------

def _percentile(counts, edges, q):
    total = counts.sum()
    if total == 0:
        return None
    k = np.searchsorted(np.cumsum(counts), q * total)
    return float(edges[min(k + 1, len(edges) - 1)])


def compute(records, out: Path | None) -> list[str]:
    counts = np.zeros(len(COMPUTE_BINS_MS) - 1)
    worst = []
    for r in records:
        hist = ((r.get("result") or {}).get("info") or {}).get("compute_hist")
        if hist:
            counts += np.asarray(hist)
        v = _targets(r).get("PP-SWR-016|Thời gian tính lớn nhất")
        if v is not None:
            worst.append(v)
    lines = ["", "## Thời gian tính", ""]
    if counts.sum() == 0:
        return lines + ["Không có số liệu thời gian tính."]
    p95, p99 = _percentile(counts, COMPUTE_BINS_MS, 0.95), _percentile(counts, COMPUTE_BINS_MS, 0.99)
    lines += [f"{int(counts.sum())} chu kỳ. p95 ≤ {_fmt(p95)} ms, p99 ≤ {_fmt(p99)} ms (cận trên của bin), "
              f"lớn nhất {_fmt(max(worst) if worst else None)} ms. Đo trên máy chạy SIL, gồm adapter; "
              "không khẳng định thời gian trên ECU (mục 9.1)."]
    if out is not None:
        plt = _plt()
        fig, ax = plt.subplots(figsize=(7, 3.2))
        ax.stairs(counts, COMPUTE_BINS_MS)
        ax.set_xscale("log")
        for q, v in (("p95", p95), ("p99", p99)):
            ax.axvline(v, linestyle="--", color="gray")
            ax.text(v, ax.get_ylim()[1] * 0.9, q, rotation=90, va="top")
        ax.set_xlabel("Thời gian tính mỗi chu kỳ [ms]")
        ax.set_ylabel("Số chu kỳ")
        fig.tight_layout()
        out.mkdir(parents=True, exist_ok=True)
        fig.savefig(out / "compute.png", dpi=110)
        plt.close(fig)
        lines += ["", "![Thời gian tính](figures/compute.png)"]
    return lines


# ---- DTLE by v_lat (Euro NCAP style) ---------------------------------------------------------

def dtle_by_v_lat(records, cases, out: Path | None) -> list[str]:
    points = defaultdict(list)  # family -> [(v_lat, dtle)]
    for r in records:
        case = cases.get(r.get("case"), {})
        v_lat = case.get("parameters", {}).get("departure_v_lat_mps")
        family = case.get("family", "")
        if v_lat is None or family[:2] not in ("S4", "S5", "S6", "S7", "S8") or "inject" in case:
            continue
        dtles = [i["dtle_m"] for i in ((r.get("result") or {}).get("info") or {}).get("interventions") or []
                 if i.get("dtle_m") is not None]
        if dtles:
            points[family].append((float(v_lat), min(dtles)))
    lines = ["", "## DTLE theo v_lat", ""]
    if not points:
        return lines + ["Không có ca trôi làn có can thiệp."]
    lines += ["| Kịch bản | v_lat [m/s] | DTLE nhỏ nhất [m] |", "|---|---|---|"]
    for family in sorted(points):
        by_v = defaultdict(list)
        for v, d in points[family]:
            by_v[round(v, 3)].append(d)
        for v in sorted(by_v):
            lines.append(f"| {family} | {v:g} | {_fmt(min(by_v[v]))} |")
    if out is not None:
        plt = _plt()
        fig, ax = plt.subplots(figsize=(6, 3.2))
        for family in sorted(points):
            v, d = zip(*sorted(points[family]))
            ax.plot(v, d, "o", label=family)
        ax.axhline(0.0, color="gray", linestyle="--")
        ax.set_xlabel("v_lat [m/s]")
        ax.set_ylabel("DTLE nhỏ nhất [m]")
        ax.legend()
        fig.tight_layout()
        out.mkdir(parents=True, exist_ok=True)
        fig.savefig(out / "dtle_v_lat.png", dpi=110)
        plt.close(fig)
        lines += ["", "![DTLE theo v_lat](figures/dtle_v_lat.png)"]
    return lines


# ---- 6.1 sweeps ---------------------------------------------------------------------------

SWEEP_INDICATORS = (("criteria", "PP-SWR-051"), ("criteria", "PP-SWR-100"), ("info", "vehicle_offset_max_m"))


def sweep(records, out: Path | None) -> list[str]:
    """Indicators by swept simulator value; one line per run without the swept value."""
    swept = sorted({k for r in records for k in (r.get("sim") or {})})
    lines = []
    for key in swept:
        if len({(r.get("sim") or {}).get(key) for r in records}) < 2:
            continue
        series = defaultdict(list)
        for r in records:
            if key not in (r.get("sim") or {}) or "error" in r:
                continue
            base = " ".join(r["run"]) + f" {r.get('acc', '')} {r.get('profile', '')}"
            series[base].append((r["sim"][key], r))
        lines += ["", f"## Quét {key}"]
        levels = sorted({v for s in series.values() for v, _ in s})
        for group, name in SWEEP_INDICATORS:
            lines += ["", f"{name} theo {key}", "", "| Chạy | " + " | ".join(f"{v:g}" for v in levels) + " |",
                      "|---|" + "---|" * len(levels)]
            for base, items in sorted(series.items()):
                at = {v: (r.get(group) or {}).get(name) for v, r in items}
                lines.append(f"| {base} | " + " | ".join(_fmt(at.get(v)) for v in levels) + " |")
        if out is not None:
            plt = _plt()
            fig, axes = plt.subplots(len(SWEEP_INDICATORS), 1, figsize=(7, 2.4 * len(SWEEP_INDICATORS)), sharex=True)
            for ax, (group, name) in zip(axes, SWEEP_INDICATORS):
                for base, items in sorted(series.items()):
                    xs, ys = zip(*sorted((v, (r.get(group) or {}).get(name)) for v, r in items))
                    ax.plot(xs, [np.nan if y is None else y for y in ys], marker="o", label=base)
                ax.set_ylabel(name)
            axes[-1].set_xlabel(key)
            axes[0].legend(fontsize=7)
            fig.tight_layout()
            out.mkdir(parents=True, exist_ok=True)
            fig.savefig(out / f"sweep_{key}.png", dpi=110)
            plt.close(fig)
            lines += ["", f"![Quét {key}](figures/sweep_{key}.png)"]
    return lines


# ---- run figure -----------------------------------------------------------------------------

def run_figure(log, result, path: Path) -> Path:
    """Time plots of one run (section 10, "Theo thời gian", "Liên tục")."""
    from eval import metrics
    plt = _plt()
    truth = metrics._Truth(log)
    t = np.asarray(log.t_us) * 1e-6
    hint = None
    d_car = []
    for x, y, _ in log.rear:
        p = log.road.project(x, y, hint)
        hint = p.s
        d_car.append(p.d)
    t_c, d_path, func, cont = [], [], [], []
    prev = None
    hint = None
    for c in log.cycles:
        status = c.path_status
        func.append(int(status.active_function) if status is not None and status.path_valid else 0)
        t_c.append(c.t0_us * 1e-6)
        valid = status is not None and status.path_valid and c.trajectory is not None
        if valid:
            pose = truth.rear_at(c.t0_us)
            p0 = c.trajectory.points[0].pose
            wx, wy, _ = metrics._to_world(pose, p0.x, p0.y, p0.yaw)
            proj = log.road.project(wx, wy, hint)
            hint = proj.s
            d_path.append(proj.d)
            # Only two paths of the same function (a change is exempt, PP-SWR-038).
            same = prev is not None and prev.path_status.active_function == status.active_function
            cont.append(metrics._continuity(prev, c, truth)[0] if same else np.nan)
            prev = c
        else:
            d_path.append(np.nan)
            cont.append(np.nan)
            prev = None
    a_y = np.asarray(log.a_y)
    jerk = np.gradient(a_y, t) if len(t) > 1 else np.zeros_like(a_y)
    w = log.road.lane_width
    fig, axes = plt.subplots(5, 1, figsize=(9, 11), sharex=True)
    ax = axes[0]
    ax.plot(t, d_car, label="xe (trục sau)")
    ax.plot(t_c, d_path, label="path, điểm 0", linewidth=0.8)
    half = w / 2 - log.vehicle_width / 2
    for y in (w / 2, -w / 2):
        ax.axhline(y, color="black", linewidth=0.8)
    for y in (half, -half):
        ax.axhline(y, color="gray", linestyle=":", linewidth=0.8)
    ax.set_ylabel("d [m]")
    ax.legend(fontsize=7)
    axes[1].plot(t, a_y)
    axes[1].set_ylabel("a_y xe [m/s²]")
    axes[2].plot(t, jerk, linewidth=0.6)
    axes[2].set_ylabel("jerk xe [m/s³]")
    axes[3].step(t_c, func, where="post")
    axes[3].set_yticks([0, 1, 2, 3], ["NONE", "HWA", "LKA", "ELK"])
    axes[3].set_ylabel("Chức năng")
    axes[4].plot(t_c, cont)
    axes[4].axhline(metrics.CONTINUITY_LATERAL_M, color="red", linestyle="--", label="ngưỡng PP-SWR-100")
    axes[4].legend(fontsize=7)
    axes[4].set_ylabel("Lệch hai path [m]")
    axes[4].set_xlabel("t [s]")
    # Function changes and fault windows on every panel.
    changes = [t_c[i] for i in range(1, len(func)) if func[i] != func[i - 1]]
    windows = []
    for group in ("lane_faults", "channel_faults", "sensor_faults", "ego_motion_faults"):
        for f in getattr(log.scenario, group, ()):
            if f.start_s < 1e8:
                end = f.start_s + f.duration_s if f.duration_s is not None else t[-1]
                windows.append((f.start_s, end))
    for ax in axes:
        for x in changes:
            ax.axvline(x, color="purple", linewidth=0.5, alpha=0.6)
        for a, b in windows:
            ax.axvspan(a, b, color="orange", alpha=0.15)
    fig.suptitle(f"{result.scenario}, seed {result.seed} (cam: lỗi; tím: đổi chức năng)")
    fig.tight_layout()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=100)
    plt.close(fig)
    return path


def suite_sections(records, cases, out: Path) -> list[str]:
    figures = out / "figures"
    return flexibility(records, cases) + compute(records, figures) + dtle_by_v_lat(records, cases, figures)

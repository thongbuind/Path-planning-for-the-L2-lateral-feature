#!/usr/bin/env python3
"""PP-TS-013: one sample curve, top view of the two driven lines + key metrics.

Runs B0 (lane centre = reference line) and R-cam (comfort line, camera view only) closed loop
with prototype.py, then draws a PNG. Draft research figure. Default = Rf; options give other curves:
    python3 sample_figure.py --radius 80 --deg 90 --kmh 50 --clothoid 30 --out sample-R80-90deg.png

Run:  python3 research/studies/PP-TS-013-comfort-line/sample_figure.py
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.gridspec import GridSpec  # noqa: E402
from matplotlib.patches import Polygon  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import prototype as P  # noqa: E402

SURF, INK, INK2, INK3, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1"
C_B0, C_NEW = "#eb6834", "#2a78d6"
ASPHALT, ASPHALT2, MARK = "#cfcdc6", "#e2e0da", "#ffffff"
GOOD, BAD = "#1c5cab", "#c23a3a"
import argparse  # noqa: E402

_ap = argparse.ArgumentParser()
_ap.add_argument("--radius", type=float, default=250.0)
_ap.add_argument("--deg", type=float, default=20.0)
_ap.add_argument("--kmh", type=float, default=90.0)
_ap.add_argument("--clothoid", type=float, default=60.0)
_ap.add_argument("--exag", type=float, default=12.0)
_ap.add_argument("--out", default="sample-rf.png")
_ap.add_argument("--view", type=float, default=80.0, help="camera view range [m]")
_ap.add_argument("--lead", type=float, default=150.0, help="straight before the curve [m]")
_ap.add_argument("--title", default="Một mẫu điển hình")
_ap.add_argument("--xodr", default=None, help="take the curve from an OpenDRIVE road (first straight = lead)")
_ap.add_argument("--label", default=None, help="road description when --xodr is used")
ARGS = _ap.parse_args()
K_EXAG = ARGS.exag  # lateral exaggeration of the overview
_ARC = (np.radians(ARGS.deg) - ARGS.clothoid / ARGS.radius) * ARGS.radius
CURVE_END = ARGS.lead + 2 * ARGS.clothoid + _ARC
S_FROM, S_TO = max(5.0, ARGS.lead - 150.0), CURVE_END + 150.0
LABEL = f"cua trái R {ARGS.radius:.0f} m, đổi hướng {ARGS.deg:.0f}°, {ARGS.kmh:.0f} km/h"
XSEGS = None
if ARGS.xodr:
    _x = P.road_from_xodr(Path(ARGS.xodr), "x", "", 0.0, (0.0, 0.0))
    _curve = _x.segs[1:-1] if _x.segs[-1][1] == 0 == _x.segs[-1][2] else _x.segs[1:]
    XSEGS = [(ARGS.lead, 0.0, 0.0)] + list(_curve) + [(250.0, 0.0, 0.0)]
    CURVE_END = ARGS.lead + sum(sg[0] for sg in _curve)
    S_FROM, S_TO = max(5.0, ARGS.lead - 150.0), CURVE_END + 150.0
    LABEL = ARGS.label or Path(ARGS.xodr).stem
SBEND = XSEGS is not None and min(sg[1] for sg in XSEGS) < 0 < max(sg[1] for sg in XSEGS)
NAME = {"B0": "Bám ref line (tâm làn), như hiện tại", "R-cam": "Đề xuất: line êm trong hành lang ±0,3 m"}
COMMA = FuncFormatter(lambda x, _: f"{x:g}".replace(".", ",").replace("-", "−"))

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "axes.titlecolor": INK, "axes.titlesize": 11,
    "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.facecolor": SURF,
    "figure.facecolor": SURF, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
})


def vn(x, nd=2):
    if abs(x) < 0.5 * 10 ** (-nd):
        x = 0.0
    return f"{x:.{nd}f}".replace(".", ",").replace("-", "−")


# ----------------------------------------------------------------------------- run
def run():
    R, Lc = ARGS.radius, ARGS.clothoid
    if XSEGS is not None:
        segs = XSEGS
    else:
        assert _ARC > -1e-6, "deflection too small for the clothoids"
        segs = [(ARGS.lead, 0, 0), (Lc, 0, 1 / R)]
        if _ARC > 0.5:
            segs.append((_ARC, 1 / R, 1 / R))
        segs += [(Lc, 1 / R, 0), (250.0, 0, 0)]
    road = P.Road("sample", LABEL, ARGS.kmh / 3.6, segs, (ARGS.lead - 50.0, S_TO)).build()
    cont = {}
    paths = {"B0": np.zeros_like(road.kn), "R-cam": P.plan_receding(road, P.CORRIDOR, view=ARGS.view, cont_stats=cont)}
    out = {}
    for v, d in paths.items():
        log = P.closed_loop(road, d)
        out[v] = {"d": d, "log": log, "m": P.cl_metrics(road, log)}
        m = (log["s"] >= road.focus[0]) & (log["s"] <= road.focus[1])
        out[v]["m"]["d_veh_max"] = float(np.max(np.abs(log["dveh"][m])))
    out["B0"]["m"]["cont"] = 0.0
    out["R-cam"]["m"]["cont"] = cont["max"]
    return road, out


# ----------------------------------------------------------------------------- geometry helpers
def frame(road):
    """Rotate so that the entry runs straight up."""
    rot = np.pi / 2
    c, s = np.cos(rot), np.sin(rot)
    x = c * road.x - s * road.y
    y = s * road.x + c * road.y
    th = road.th + rot
    return x, y, th


def pt(road, X, Y, TH, s, d, k=K_EXAG):
    xs = np.interp(s, road.s, X)
    ys = np.interp(s, road.s, Y)
    ts = np.interp(s, road.s, TH)
    return xs - k * d * np.sin(ts), ys + k * d * np.cos(ts)


def key_points(road, log):
    s, d = log["s"], log["dveh"]
    m = (s >= ARGS.lead - 40) & (s <= CURVE_END + 120)
    s, d = s[m], d[m]
    if SBEND:  # apex of each curve and the change of direction between them
        i1 = int(np.argmax(d))
        i2 = int(np.argmin(d))
        lo, hi = sorted((i1, i2))
        ic = lo + int(np.argmin(np.abs(d[lo:hi + 1])))
        return {"Apex 1": s[i1], "Đổi chiều": s[ic], "Apex 2": s[i2]}
    i_apex = int(np.argmax(d))
    i_in = int(np.argmin(d[:i_apex]))
    i_out = i_apex + int(np.argmin(d[i_apex:]))
    return {"Turn-in": s[i_in], "Apex": s[i_apex], "Exit": s[i_out]}


# ----------------------------------------------------------------------------- left half
def overview(ax, road, out, keys):
    X, Y, TH = frame(road)
    ss = np.arange(S_FROM, S_TO, 0.5)
    # road surface: ego lane and part of the neighbour lanes
    for lo, hi, col in ((-1.75 - 1.4, -1.75, ASPHALT2), (1.75, 1.75 + 1.4, ASPHALT2), (-1.75, 1.75, ASPHALT)):
        xa, ya = pt(road, X, Y, TH, ss, lo)
        xb, yb = pt(road, X, Y, TH, ss[::-1], hi)
        ax.add_patch(Polygon(np.column_stack([np.r_[xa, xb], np.r_[ya, yb]]), color=col, lw=0, zorder=1))
    for dl in (-1.75, 1.75):
        xa, ya = pt(road, X, Y, TH, ss, dl)
        ax.plot(xa, ya, color=MARK, lw=2.2, ls=(0, (6, 5)), zorder=2)
    # corridor of the new path (light)
    xa, ya = pt(road, X, Y, TH, ss, -P.CORRIDOR)
    xb, yb = pt(road, X, Y, TH, ss[::-1], P.CORRIDOR)
    ax.add_patch(Polygon(np.column_stack([np.r_[xa, xb], np.r_[ya, yb]]), color="#bcd5f3", alpha=0.55, lw=0, zorder=2))
    xa, ya = pt(road, X, Y, TH, ss, 0.0)
    ax.plot(xa, ya, color=INK3, lw=0.8, ls=(0, (1, 3)), zorder=3)
    for v, col, lw in (("B0", C_B0, 3.0), ("R-cam", C_NEW, 3.0)):
        lg = out[v]["log"]
        m = (lg["s"] >= S_FROM) & (lg["s"] <= S_TO)
        x, y = pt(road, X, Y, TH, lg["s"][m], lg["dveh"][m])
        ax.plot(x, y, color=col, lw=lw, zorder=4, solid_capstyle="round")
    # key points as lines across the road (like the racing-line sketch)
    for name, s0 in keys.items():
        xa, ya = pt(road, X, Y, TH, np.array([s0, s0]), np.array([-1.75 - 1.4, 1.75 + 1.4]))
        ax.plot(xa, ya, color=INK, lw=1.6, zorder=5)
        xt, yt = pt(road, X, Y, TH, s0, 1.75 + 2.0)
        ax.text(xt, yt, f"{name}\ns = {s0:.0f} m", fontsize=9.5, color=INK, fontweight="bold",
                va="center", ha="right", zorder=6)
    x0, y0 = pt(road, X, Y, TH, S_FROM + 5, 1.75 + 2.6)
    ax.annotate("", xy=(x0, y0 + 30), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", color=INK2, lw=1.5),
                annotation_clip=False, zorder=7)
    ax.text(x0 - 4, y0 + 15, "hướng xe", fontsize=8.5, color=INK2, va="center", ha="right")
    ax.set_aspect("equal")
    ax.axis("off")
    segs = np.cumsum([sg[0] for sg in road.segs])
    ax.set_title(f"Toàn cảnh: {LABEL}\n"
                 f"tâm làn cong từ s = {ARGS.lead:.0f} đến {CURVE_END:.0f} m"
                 + ("\n" if XSEGS is not None else
                    (f" (cung tròn {ARGS.lead + ARGS.clothoid:.0f}–{ARGS.lead + ARGS.clothoid + _ARC:.0f} m)\n"
                     if _ARC > 0.5 else ", chỉ có hai clothoid\n"))
                 + f"camera nhìn {ARGS.view:.0f} m; "
                 f"chiều ngang phóng đại ×{K_EXAG:.0f}: làn 3,5 m vẽ thành {3.5 * K_EXAG:.0f} m", fontsize=10.5)


def zoom(ax, road, out, name, s0, half=9.0, compact=False):
    ax.add_patch(plt.Rectangle((-half, -1.75 - 0.9), 2 * half, 0.9, color=ASPHALT2, lw=0))
    ax.add_patch(plt.Rectangle((-half, 1.75), 2 * half, 0.9, color=ASPHALT2, lw=0))
    ax.add_patch(plt.Rectangle((-half, -1.75), 2 * half, 3.5, color=ASPHALT, lw=0))
    for yl in (-1.75, 1.75):
        ax.plot([-half, half], [yl, yl], color=MARK, lw=2.5, ls=(0, (3, 3)))
    ax.plot([-half, half], [0, 0], color=INK3, lw=0.8, ls=(0, (1, 3)))
    ax.axhspan(-P.CORRIDOR, P.CORRIDOR, color="#bcd5f3", alpha=0.45, lw=0)
    texts = []
    for v, col in (("B0", C_B0), ("R-cam", C_NEW)):
        lg = out[v]["log"]
        m = (lg["s"] >= s0 - half) & (lg["s"] <= s0 + half)
        ax.plot(lg["s"][m] - s0, lg["dveh"][m], color=col, lw=2.0)
        i = int(np.argmin(np.abs(lg["s"] - s0)))
        d, psi = lg["dveh"][i], lg["psirel"][i]
        along = np.array([-P.REAR_CORNER, P.PROFILE.wheelbase + P.FRONT_CORNER])
        lat = np.array([-0.95, 0.95])
        cs = [(along[0], lat[0]), (along[1], lat[0]), (along[1], lat[1]), (along[0], lat[1])]
        poly = [(a * np.cos(psi) - l * np.sin(psi) + lg["s"][i] - s0 - 1.4,
                 d + a * np.sin(psi) + l * np.cos(psi)) for a, l in cs]
        ax.add_patch(Polygon(poly, closed=True, fc=col, alpha=0.18, ec=col, lw=1.8))
        gap_l = 1.75 - (d + 0.95)
        gap_r = (d - 0.95) + 1.75
        texts.append((v, d, gap_l, gap_r))
    ax.set_xlim(-half, half)
    ax.set_ylim(-1.75 - 0.9, 1.75 + 0.9)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([-1.75, 0, 1.75])
    ax.yaxis.set_major_formatter(COMMA)
    ax.tick_params(labelsize=8)
    ax.grid(False)
    side = lambda d: ("trái" if d > 0.02 else ("phải" if d < -0.02 else "giữa")) if SBEND else (  # noqa: E731
        "trái (trong cua)" if d > 0.02 else ("phải (ngoài cua)" if d < -0.02 else "giữa"))
    b, n = texts
    if compact:
        ax.set_title(f"{name} · s = {s0:.0f} m · đúng tỉ lệ →", fontsize=10.5)
        ax.text(0.0, -0.08, f"Ref: lệch {vn(b[1])} m · hở T {vn(b[2])} / P {vn(b[3])} m",
                transform=ax.transAxes, fontsize=8.6, color=C_B0, va="top", fontweight="bold")
        ax.text(0.0, -0.22, f"Đề xuất: lệch {vn(n[1])} m · hở T {vn(n[2])} / P {vn(n[3])} m",
                transform=ax.transAxes, fontsize=8.6, color=C_NEW, va="top", fontweight="bold")
        return
    ax.set_title(f"{name} · s = {s0:.0f} m · đúng tỉ lệ, xe đi sang phải", fontsize=10.5)
    ax.text(0.0, -0.09, f"Bám ref line: lệch {vn(b[1])} m · hở tới vạch trái {vn(b[2])} / phải {vn(b[3])} m",
            transform=ax.transAxes, fontsize=8.8, color=C_B0, va="top", fontweight="bold")
    ax.text(0.0, -0.24, f"Đề xuất: lệch {vn(n[1])} m về {side(n[1])} · hở trái {vn(n[2])} / phải {vn(n[3])} m",
            transform=ax.transAxes, fontsize=8.8, color=C_NEW, va="top", fontweight="bold")


# ----------------------------------------------------------------------------- right half
ROWS = [
    ("a_y đỉnh", "m/s²", "ay_peak", 2),
    ("jerk ngang đỉnh", "m/s³", "jerk_peak", 2),
    ("jerk ngang rms", "m/s³", "jerk_rms", 2),
    ("góc vô-lăng đỉnh", "°", "sw_peak", 1),
    ("tốc độ vô-lăng đỉnh", "°/s", "swr_peak", 1),
    ("tổng hành trình vô-lăng", "°", "sw_travel", 1),
    ("số lần đảo lái (khe 0,5°)", "lần", "reversals", 0),
    ("lệch tâm làn lớn nhất của xe", "m", "d_veh_max", 2),
    ("khoảng hở thân xe–vạch nhỏ nhất", "m", "clear_min", 2),
    ("path đổi giữa 2 chu kỳ, đoạn 0–3 s", "m", "cont", 3),
]
LOWER_BETTER = {"clear_min": False}


def table(ax, out):
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(len(ROWS) + 0.2, -1.2)
    cols = (0.0, 0.47, 0.64, 0.81)
    for x, h in zip(cols, ("Chỉ số (đo trên xe, vòng kín)", "Bám ref line", "Đề xuất", "Thay đổi")):
        ax.text(x, -0.6, h, fontsize=10, fontweight="bold", color=INK, va="center")
    ax.plot([0, 1], [-0.15, -0.15], color=INK3, lw=0.8)
    for i, (lab, unit, k, nd) in enumerate(ROWS):
        b, n = out["B0"]["m"][k], out["R-cam"]["m"][k]
        y = i + 0.4
        if i % 2 == 0:
            ax.add_patch(plt.Rectangle((0, i - 0.08), 1, 0.96, color="#f3f2ee", lw=0))
        ax.text(cols[0], y, f"{lab} ({unit})", fontsize=9.6, color=INK, va="center")
        fmt = (lambda x: f"{int(round(x))}") if nd == 0 else (lambda x: vn(x, nd))
        ax.text(cols[1], y, fmt(b), fontsize=10, color=C_B0, va="center", fontweight="bold")
        ax.text(cols[2], y, fmt(n), fontsize=10, color=C_NEW, va="center", fontweight="bold")
        if k == "cont":
            txt, col = ("> 0,05 m PP-SWR-100", BAD) if n > 0.05 else ("đạt", GOOD)
        elif k in ("clear_min", "d_veh_max"):
            txt, col = f"{'+' if n - b >= 0 else '−'}{vn(abs(n - b))} m (cái giá)", INK2
        elif k == "reversals":
            txt, col = f"{int(n - b):+d} lần".replace("-", "−"), (GOOD if n < b else (BAD if n > b else INK2))
        elif b > 1e-9:
            pc = 100 * (n - b) / b
            better = pc < 0
            txt, col = f"{'−' if pc < 0 else '+'}{abs(pc):.0f} %", (GOOD if better else BAD)
        else:
            txt, col = "—", INK2
        ax.text(cols[3], y, txt, fontsize=10, color=col, va="center", fontweight="bold")


def charts(axes, road, out, keys):
    specs = [
        ("dveh", "Lệch khỏi tâm làn của xe, đúng tỉ lệ (m)", None),
        ("ay", "a_y của xe (m/s²)", None),
        ("jerk", "Jerk ngang của xe (m/s³)", None),
        ("sw", "Góc vô-lăng (°)", None),
    ]
    for ax, (k, title, _) in zip(axes, specs):
        for v, col in (("B0", C_B0), ("R-cam", C_NEW)):
            lg = out[v]["log"]
            m = (lg["s"] >= S_FROM) & (lg["s"] <= S_TO)
            if k == "jerk":
                y = np.gradient(lg["ay"], P.CTRL_DT)
                y = np.convolve(y, np.ones(10) / 10, mode="same")
            else:
                y = lg[k]
            ax.plot(lg["s"][m], y[m], color=col, lw=2.0)
        for name, s0 in keys.items():
            ax.axvline(s0, color=INK2, lw=0.9, ls=(0, (2, 2)))
        ax.set_title(title, fontsize=10.5)
        ax.set_xlim(S_FROM, S_TO)
        ax.yaxis.set_major_formatter(COMMA)
        ax.axhline(0, color=INK3, lw=0.6)
    a = axes[0]
    a.axhspan(-P.CORRIDOR, P.CORRIDOR, color="#bcd5f3", alpha=0.45, lw=0)
    a.set_ylim(-0.45, 0.45)
    a.text(S_FROM + 3, -P.CORRIDOR + 0.02, "hành lang ±0,3 m", fontsize=8, color=C_NEW)
    a.text(S_FROM + 3, -0.43, "+ trái / − phải" if SBEND else "+ trái (trong cua) / − phải (ngoài cua)",
           fontsize=8, color=INK2)
    for j, (name, s0) in enumerate(keys.items()):
        a.text(s0 + 2, 0.43 - (0.07 * j if SBEND else 0.0), name, fontsize=8, color=INK, ha="left", va="top",
               fontweight="bold", bbox=dict(fc=SURF, ec="none", pad=0.5))
    axes[1].axhline(2.5, color=INK2, lw=0.8, ls=(0, (2, 2)))
    axes[1].text(S_FROM + 3, 2.53, "aysmax HWA 2,5", fontsize=8, color=INK2, va="bottom")
    for ax in axes[2:]:
        ax.set_xlabel("quãng đường dọc làn s (m)")


def main():
    road, out = run()
    keys = key_points(road, out["R-cam"]["log"])
    fig = plt.figure(figsize=(22, 12.5), dpi=105)
    fig.text(0.015, 0.968, f"{ARGS.title}: line chạy bám ref line so với line êm đề xuất (ý tưởng racing line)",
             fontsize=18, fontweight="bold", color=INK)
    fig.text(0.015, 0.945,
             (f"Hình học {Path(ARGS.xodr).stem} của benchmark" if ARGS.xodr else "Đường nghiên cứu, không thuộc benchmark")
             + f" · đoạn thẳng trước cua {ARGS.lead:.0f} m · VP-0 rộng 1,90 m kể gương · làn 3,5 m · camera {ARGS.view:.0f} m · "
             "line = vị trí thật của tâm cầu sau, vòng kín (bicycle động lực học + stand-in SQTS 4.6) · "
             "nháp nguyên mẫu Python, không phải planner C",
             fontsize=9.8, color=INK2)
    handles = [plt.Line2D([], [], color=C_B0, lw=3), plt.Line2D([], [], color=C_NEW, lw=3),
               plt.Rectangle((0, 0), 1, 1, color="#bcd5f3")]
    fig.legend(handles, [NAME["B0"], NAME["R-cam"], "hành lang cho phép của path đề xuất"],
               loc="upper left", bbox_to_anchor=(0.015, 0.935), ncol=3, fontsize=10.5, handlelength=2.6)

    gs = GridSpec(1, 2, figure=fig, left=0.015, right=0.985, top=0.845, bottom=0.085 if ARGS.deg < 45 else 0.125,
                  wspace=0.07,
                  width_ratios=[1.0, 1.0])
    if ARGS.deg < 45:  # long thin overview: zooms in a column beside it
        left = gs[0].subgridspec(3, 2, width_ratios=[0.95, 1.05], hspace=0.6, wspace=0.04)
        ax_ov = fig.add_subplot(left[:, 0])
        overview(ax_ov, road, out, keys)
        for r, (name, s0) in enumerate(keys.items()):
            zoom(fig.add_subplot(left[r, 1]), road, out, name, s0)
    else:  # wide corner: big overview on top, zooms in a row below
        left = gs[0].subgridspec(2, 3, height_ratios=[3.2, 1], hspace=0.28, wspace=0.12)
        ax_ov = fig.add_subplot(left[0, :])
        overview(ax_ov, road, out, keys)
        for c, (name, s0) in enumerate(keys.items()):
            zoom(fig.add_subplot(left[1, c]), road, out, name, s0, half=5.0, compact=True)

    right = gs[1].subgridspec(3, 2, height_ratios=[1.2, 1, 1], hspace=0.45, wspace=0.2)
    tax = fig.add_subplot(right[0, :])
    table(tax, out)
    axes = [fig.add_subplot(right[1, 0]), fig.add_subplot(right[1, 1]),
            fig.add_subplot(right[2, 0]), fig.add_subplot(right[2, 1])]
    charts(axes, road, out, keys)

    mb, mn = out["B0"]["m"], out["R-cam"]["m"]
    ay_pc = 100 * (mn["ay_peak"] - mb["ay_peak"]) / mb["ay_peak"]
    swr_pc = 100 * (mn["swr_peak"] - mb["swr_peak"]) / mb["swr_peak"]
    shape = ("lấn vào phía trong của cua trái, cắt chéo qua tâm ở chỗ đổi chiều, rồi lấn vào phía trong của cua phải: "
             "gần như một đường thẳng chéo qua hai cua" if SBEND else
             "vào cua từ phía ngoài (phải), lấn vào phía trong quanh đỉnh cua, ra cua về phía ngoài rồi về tâm")
    note = (f"Đọc hình: line đề xuất {shape}. a_y đỉnh {vn(ay_pc, 0)} %, tốc độ vô-lăng đỉnh {vn(swr_pc, 0)} %; đổi lại thân xe gần vạch hơn "
            f"{vn(mb['clear_min'] - mn['clear_min'])} m. ")
    if ARGS.deg >= 45:
        note += "Cung tròn dài nên a_y trên cung gần như không đổi; lợi chủ yếu ở hai đoạn chuyển tiếp. "
    if mn["reversals"] > mb["reversals"]:
        note += "Số lần đảo lái tăng do path lắc nhẹ một nhịp sau lối ra trước khi về tâm. "
    note += (f"Path đổi giữa hai chu kỳ (0–3 s) tối đa {vn(mn['cont'], 3)} m: "
             + ("vượt 0,05 m của PP-SWR-100." if mn["cont"] > 0.05 else "đạt PP-SWR-100 ở mẫu này."))
    fig.text(0.015, 0.012, textwrap.fill(note, 135), fontsize=9.2, color=INK2)
    path = HERE / ARGS.out
    fig.savefig(path, dpi=105)
    for v in out:
        print(v, {k: round(float(x), 3) for k, x in out[v]["m"].items()})
    print("keys", {k: round(float(s), 1) for k, s in keys.items()})
    print("wrote", path)


if __name__ == "__main__":
    main()

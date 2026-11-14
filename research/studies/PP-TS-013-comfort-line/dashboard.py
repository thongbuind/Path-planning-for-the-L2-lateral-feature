#!/usr/bin/env python3
"""PP-TS-013 dashboard: comfort line in a corridor vs lane centre. Reads results.json.

Run:  python3 research/studies/PP-TS-013-comfort-line/dashboard.py
Writes dashboard.png next to this file.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.gridspec import GridSpec  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402
from matplotlib.transforms import blended_transform_factory  # noqa: E402
import textwrap  # noqa: E402

HERE = Path(__file__).resolve().parent
R = json.loads((HERE / "results.json").read_text())
META = R["meta"]

# Reference palette (dataviz skill), light mode; validated all-pairs for 3 slots.
SURF = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
INK3 = "#8a8984"
GRID = "#e6e5e1"
C_RC = "#2a78d6"  # slot 1: R-cam (candidate)
C_B0 = "#eb6834"  # slot 2: B0 (lane centre)
C_RG = "#1baf7a"  # slot 3: R-glob (upper bound) - low contrast: dashed + direct label
CORR = "#dce9f8"
DIV = LinearSegmentedColormap.from_list("div", ["#2a78d6", "#f0efec", "#e34948"])

NAMES = {"B0": "B0 · bám tâm làn (bình thường)", "R-cam": "R-cam · cắt cua, chỉ thấy 80 m camera",
         "R-glob": "R-glob · cắt cua, biết trước cả đường (tham chiếu, cần bản đồ)"}
STYLE = {"B0": dict(color=C_B0, lw=2.0), "R-cam": dict(color=C_RC, lw=2.2),
         "R-glob": dict(color=C_RG, lw=1.6, ls=(0, (5, 3)))}
ORDER = ["Rf", "S1f", "S14e", "S1d", "S1c", "S1be"]
SHORT = {"Rf": "Rf cua hữu hạn R250, 20°", "S1f": "S1f S-bend R171, 90", "S14e": "S14e S-bend R171, 130",
         "S1d": "S1d chữ S R500, 90", "S1c": "S1c vào cung dài R250", "S1be": "S1be vào R200, clothoid 60 m"}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "axes.titlecolor": INK, "axes.titlesize": 11.5,
    "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.facecolor": SURF,
    "figure.facecolor": SURF, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
})


def vn(x, nd=2):
    """Vietnamese decimal comma."""
    return f"{x:.{nd}f}".replace(".", ",")


def vnpct(x):
    return f"{x:+.0f} %".replace("-", "−")


COMMA = FuncFormatter(lambda x, _: f"{x:g}".replace(".", ",").replace("-", "−"))


def arr(x):
    return np.asarray(x, dtype=float)


def pct(b, r):
    return 100.0 * (r - b) / b if b > 1e-9 else 0.0


def focus_mask(road, s):
    f0, f1 = road["focus"]
    return (s >= f0) & (s <= f1)


def lane_panel(ax, axk, name, title):
    road = R["roads"][name]
    sn = arr(road["sn"])
    m = focus_mask(road, sn)
    kr = arr(road["kr"])
    # curvature strip (reference only)
    axk.fill_between(sn[m], kr[m] * 1000, 0, color="#c9c8c2", lw=0)
    axk.axhline(0, color=INK3, lw=0.6)
    axk.set_ylabel("κ tâm làn\n(1/km)", fontsize=8.5)
    axk.tick_params(labelbottom=False, labelsize=8, length=0)
    axk.spines["bottom"].set_visible(False)
    axk.set_title(title)
    axk.grid(False)
    lim = META["corridor"]
    body = (META["lane_width"] - 1.90) / 2  # path offset at which the body (mirrors) touches the line
    ax.axhspan(-lim, lim, color=CORR, lw=0, zorder=0)
    for y in (body, -body):
        ax.axhline(y, color=INK2, lw=1.0, ls=(0, (2, 2)))
    ax.text(sn[m][0] + 3, body - 0.08, "thân xe (kể gương) chạm vạch làn", fontsize=8, color=INK2, va="top")
    ax.text(sn[m][0] + 3, lim + 0.03, f"hành lang path ±{vn(lim, 1)} m", fontsize=8, color=C_RC, va="bottom")
    for v in ("B0", "R-glob", "R-cam"):
        d = arr(road["variants"][v]["d"])
        ax.plot(sn[m], d[m], **STYLE[v], zorder=3)
    ax.set_ylim(-1.0, 1.0)
    ax.set_xlim(sn[m][0], sn[m][-1])
    ax.set_ylabel("lệch tâm làn d (m)\n+ trái / − phải")
    ax.set_xlabel("quãng đường dọc làn s (m)   ·   vạch làn ở ±1,75 m, ngoài khung")
    return road


def signal_panels(axes, name):
    road = R["roads"][name]
    keys = [("ay", "a_y của xe (m/s²)"), ("jerk", "jerk ngang của xe (m/s³)"), ("sw", "góc vô-lăng (°)")]
    for ax, (k, lab) in zip(axes, keys):
        for v in ("B0", "R-cam"):
            lg = road["variants"][v]["log"]
            s, t = arr(lg["s"]), arr(lg["t"])
            if k == "jerk":
                y = np.gradient(arr(lg["ay"]), t)
                y = np.convolve(y, np.ones(3) / 3, mode="same")
            else:
                y = arr(lg[k])
            m = focus_mask(road, s)
            ax.plot(s[m], y[m], **STYLE[v])
        ax.set_title(f"{name} · {lab}", fontsize=10.5)
        ax.axhline(0, color=INK3, lw=0.6)
        ax.set_xlabel("s (m)")
    axes[0].axhline(2.5, color=INK2, lw=0.8, ls=(0, (2, 2)))
    axes[0].text(axes[0].get_xlim()[0] + 5, 2.42, "aysmax HWA 2,5 m/s²", fontsize=8, color=INK2, va="top")


METRICS = [
    ("ay_peak", "a_y đỉnh"), ("jerk_peak", "jerk đỉnh"), ("jerk_rms", "jerk rms"),
    ("swr_peak", "tốc độ\nvô-lăng đỉnh"), ("sw_travel", "hành trình\nvô-lăng"),
]


def heat_table(ax):
    rows = ORDER
    vals = np.zeros((len(rows), len(METRICS)))
    for i, n in enumerate(rows):
        b = R["roads"][n]["variants"]["B0"]["cl"]
        r = R["roads"][n]["variants"]["R-cam"]["cl"]
        for j, (k, _) in enumerate(METRICS):
            vals[i, j] = pct(b[k], r[k])
    ncol = len(METRICS) + 2
    ax.set_xlim(-2.1, ncol)
    ax.set_ylim(len(rows), -1.1)
    ax.axis("off")
    for j, (_, lab) in enumerate(METRICS):
        ax.text(j + 0.5, -0.55, lab, ha="center", va="center", fontsize=8.8, color=INK2)
    ax.text(len(METRICS) + 0.5, -0.55, "số lần\nđảo lái", ha="center", va="center", fontsize=8.8, color=INK2)
    ax.text(len(METRICS) + 1.5, -0.55, "khoảng hở\nthân–vạch min", ha="center", va="center", fontsize=8.8, color=INK2)
    for i, n in enumerate(rows):
        ax.text(-0.08, i + 0.5, SHORT[n], ha="right", va="center", fontsize=9, color=INK)
        for j in range(len(METRICS)):
            v = vals[i, j]
            c = DIV(0.5 + np.clip(v, -50, 50) / 100.0)
            ax.add_patch(plt.Rectangle((j + 0.03, i + 0.04), 0.94, 0.92, color=c, lw=0))
            ax.text(j + 0.5, i + 0.5, vnpct(v), ha="center", va="center", fontsize=9.5,
                    color="white" if abs(v) > 30 else INK, fontweight="bold")
        b = R["roads"][n]["variants"]["B0"]["cl"]
        r = R["roads"][n]["variants"]["R-cam"]["cl"]
        for j, txt in ((len(METRICS), f"{b['reversals']} → {r['reversals']}"),
                       (len(METRICS) + 1, f"{vn(b['clear_min'])} → {vn(r['clear_min'])} m")):
            ax.add_patch(plt.Rectangle((j + 0.03, i + 0.04), 0.94, 0.92, color="#f0efec", lw=0))
            ax.text(j + 0.5, i + 0.5, txt, ha="center", va="center", fontsize=9, color=INK)
    ax.set_title("R-cam so với B0, đo trên chuyển động thật của xe (vòng kín) · xanh = tốt hơn, đỏ = tệ hơn",
                 loc="left", pad=6, x=0.0)


def sweep_panel(ax):
    xs = [0.0, 0.1, 0.2, 0.3, 0.45, 0.6]
    ends = []
    for n in ORDER:
        sw = R["sweep"][n]
        b = sw["0.0"]["ay_peak"]
        y = [pct(b, sw[str(c)]["ay_peak"]) for c in xs]
        ax.plot(xs, y, color=INK2, lw=1.4, marker="o", ms=4.5, mfc=SURF, mec=INK2, mew=1.2)
        ends.append((y[-1], n))
    ends.sort()
    groups = []  # merge lines that end within 2 % of each other into one label
    for y, n in ends:
        if groups and abs(y - groups[-1][0][-1]) < 2.0:
            groups[-1][0].append(y)
            groups[-1][1].append(n)
        else:
            groups.append(([y], [n]))
    for ys, ns in groups:
        ax.text(0.615, float(np.mean(ys)), ", ".join(ns), fontsize=8.5, color=INK, va="center")
    tr = blended_transform_factory(ax.transData, ax.transAxes)
    ax.axvline(0.3, color=C_RC, lw=1.2)
    ax.text(0.305, 0.62, "dùng ở study\n(offset_max)", fontsize=8, color=C_RC, va="top", transform=tr)
    lim_body = (META["lane_width"] - 1.90) / 2 - META["margin"]
    ax.axvline(lim_body, color=INK2, lw=1.0, ls=(0, (2, 2)))
    ax.text(lim_body + 0.005, 0.62, "thân xe cách\nvạch 0,3 m", fontsize=8, color=INK2, va="top", transform=tr)
    ax.set_xlim(-0.01, 0.78)
    ax.xaxis.set_major_formatter(COMMA)
    ax.yaxis.set_major_formatter(COMMA)
    ax.set_xlabel("nửa bề rộng hành lang (m)")
    ax.set_ylabel("thay đổi a_y đỉnh của path (%)")
    ax.set_title("Cắt cua bao nhiêu thì đủ? (R-cam, mức path)")


def kpi(fig, x, w, big, small, note):
    ax = fig.add_axes([x, 0.885, w, 0.065])
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, color="#f3f2ee", lw=0))
    ax.text(0.05, 0.62, big, fontsize=19, fontweight="bold", color=INK, va="center", transform=ax.transAxes)
    ax.text(0.05, 0.22, small, fontsize=9, color=INK2, va="center", transform=ax.transAxes)
    ax.text(0.95, 0.62, note, fontsize=9, color=INK2, va="center", ha="right", transform=ax.transAxes)


def main():
    fig = plt.figure(figsize=(21, 16), dpi=110)
    fig.text(0.02, 0.976, "Quỹ đạo êm trong hành lang an toàn (ý tưởng racing line) so với bám tâm làn",
             fontsize=19, fontweight="bold", color=INK)
    fig.text(0.02, 0.959,
             f"PP-TS-013 · nháp nghiên cứu, nguyên mẫu Python (không phải planner C) · VP-0 (rộng 1,90 m kể gương), "
             f"làn {vn(META['lane_width'], 1)} m, camera {META['view_m']:.0f} m · path cắt cua trong ±{vn(META['corridor'], 1)} m, "
             "a_y path không vượt a_y tâm làn cần trong ±80 m · vòng kín: bicycle động lực học + luật điều khiển stand-in (SQTS 4.6)",
             fontsize=10, color=INK2)

    rr = R["roads"]

    def cl(n, v, k):
        return rr[n]["variants"][v]["cl"][k]

    jr = [pct(cl(n, "B0", "jerk_rms"), cl(n, "R-cam", "jerk_rms")) for n in ORDER]
    tr = [pct(cl(n, "B0", "sw_travel"), cl(n, "R-cam", "sw_travel")) for n in ORDER]
    dclear = [cl(n, "R-cam", "clear_min") - cl(n, "B0", "clear_min") for n in ORDER]
    worse = [x for x in dclear if x < 0]
    kpi(fig, 0.02, 0.23, f"{vn(cl('S1f', 'B0', 'ay_peak'))} → {vn(cl('S1f', 'R-cam', 'ay_peak'))}",
        "a_y đỉnh của xe (m/s²), S-bend R171 90 km/h", vnpct(pct(cl('S1f', 'B0', 'ay_peak'), cl('S1f', 'R-cam', 'ay_peak'))))
    kpi(fig, 0.265, 0.23, f"{vn(cl('Rf', 'B0', 'ay_peak'))} → {vn(cl('Rf', 'R-cam', 'ay_peak'))}",
        "a_y đỉnh của xe (m/s²), cua hữu hạn Rf", vnpct(pct(cl('Rf', 'B0', 'ay_peak'), cl('Rf', 'R-cam', 'ay_peak'))))
    kpi(fig, 0.51, 0.23, f"{vnpct(np.median(jr))} / {vnpct(np.median(tr))}",
        "trung vị 6 đường: jerk rms / tổng hành trình vô-lăng", "vòng kín")
    kpi(fig, 0.755, 0.225, f"−{vn(-min(worse))} … −{vn(-max(worse))} m",
        f"cái giá: khoảng hở thân xe–vạch giảm ở {len(worse)}/6 đường", f"min còn {vn(min(cl(n, 'R-cam', 'clear_min') for n in ORDER))} m")

    handles = [plt.Line2D([], [], **STYLE[v]) for v in ("B0", "R-cam", "R-glob")]
    fig.legend(handles, [NAMES[v] for v in ("B0", "R-cam", "R-glob")], loc="upper left",
               bbox_to_anchor=(0.02, 0.875), ncol=3, fontsize=10.5, handlelength=3)

    outer = GridSpec(3, 1, figure=fig, left=0.055, right=0.985, top=0.83, bottom=0.07,
                     height_ratios=[2.7, 1.7, 2.5], hspace=0.32)
    top = outer[0].subgridspec(2, 2, height_ratios=[0.22, 1], hspace=0.06, wspace=0.12)
    axk1 = fig.add_subplot(top[0, 0])
    ax1 = fig.add_subplot(top[1, 0], sharex=axk1)
    axk2 = fig.add_subplot(top[0, 1])
    ax2 = fig.add_subplot(top[1, 1], sharex=axk2)
    lane_panel(ax1, axk1, "Rf", "Rf · cua hữu hạn: ngoài → trong → ngoài, đúng kiểu racing line")
    lane_panel(ax2, axk2, "S1f", "S1f · S-bend R171 (90 km/h): một đường gần thẳng chéo qua hai cua")

    mid = outer[1].subgridspec(1, 3, wspace=0.18)
    sig = [fig.add_subplot(mid[0, k]) for k in range(3)]
    signal_panels(sig, "S1f")

    bot = outer[2].subgridspec(1, 3, width_ratios=[1.55, 0.95, 0.5], wspace=0.16)
    axh = fig.add_subplot(bot[0, 0])
    heat_table(axh)
    axs = fig.add_subplot(bot[0, 1])
    sweep_panel(axs)
    axt = fig.add_subplot(bot[0, 2])
    axt.axis("off")
    rows = [
        ("Lợi nhiều", "cua ngắn, chữ S: path thấy lối ra trong 80 m và nắn thẳng."),
        ("Gần như 0 về a_y", "cua có cung dài; jerk, vô-lăng vẫn giảm nhẹ."),
        ("Không cần bản đồ", "biết trước cả đường (R-glob) không hơn camera 80 m."),
        ("Cái giá", "path lệch tâm tới 0,3 m; thân xe gần vạch hơn 0,1–0,2 m."),
        ("Chưa đạt", "đoạn 2–3 s của path đổi tới 0,13 m giữa hai chu kỳ (PP-SWR-100: 0,05 m); PP-SWR-006 cần viết lại."),
        ("Chưa xét", "xe làn bên, xe ngược chiều, nhiễu lane model."),
    ]
    y = 1.0
    axt.text(0, y, "Đọc nhanh", fontsize=11.5, fontweight="bold", color=INK, va="top", transform=axt.transAxes)
    y -= 0.08
    for h, t in rows:
        axt.text(0, y, h, fontsize=9.5, fontweight="bold", color=INK, va="top", transform=axt.transAxes)
        body = textwrap.fill(t, 33)
        axt.text(0, y - 0.05, body, fontsize=8.8, color=INK2, va="top", transform=axt.transAxes,
                 linespacing=1.35)
        y -= 0.07 + 0.042 * (body.count("\n") + 1)

    for ax in (ax1, ax2, axk1, axk2, *sig):
        ax.yaxis.set_major_formatter(COMMA)
    fig.text(0.02, 0.018,
             "Nháp, không trích dẫn chính thức (research/README.md). Hành lang ±0,3 m lấy lại offset_max hiện có; trọng số chi phí, "
             "ngoại suy 80 m và cửa sổ ±80 m của ngưỡng a_y là lựa chọn nghiên cứu, cần chốt. Khoảng hở: thân xe kể gương tới tâm vạch. "
             "R-glob tối ưu tổng chi phí, không tối ưu a_y đỉnh.",
             fontsize=8.8, color=INK3)
    fig.savefig(HERE / "dashboard.png", dpi=110)
    print("wrote", HERE / "dashboard.png")


if __name__ == "__main__":
    main()

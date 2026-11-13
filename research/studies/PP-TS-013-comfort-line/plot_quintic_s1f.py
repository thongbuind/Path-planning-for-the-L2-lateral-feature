"""Replay the clean S1f SIL pair and plot the driven lines and vehicle response."""

from dataclasses import replace
import json
from math import atan, atan2, cos, sin
import os
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
from scipy.signal import butter, sosfilt, sosfilt_zi

import quintic_experiment as experiment
from interfaces import ActiveFunction, Pose2D


COLORS = ("#eb6834", "#2a78d6")
LABELS = ("Quintic gốc", "Quintic + điểm trung gian")
STYLES = ("-", "--")
SURFACE, ROAD, SHOULDER, CORRIDOR = "#fcfcfb", "#cfcdc6", "#e2e0da", "#bcd5f3"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e6e5e1"
REFERENCE, REFERENCE_STYLE = "#454541", (0, (1.2, 3.1))
EXAGGERATION = 24.0
FOLLOW_COLOR, FOLLOW_STYLE = "#137d62", "-."


class RefLinePlanner:
    """For the ideal reference run, give the controller the true lane centre."""

    def __init__(self, harness):
        self.base = harness.planner
        self.harness = harness
        self.station = None

    @property
    def init_result(self):
        return self.base.init_result

    def step(self, inputs, ego_motion):
        out = self.base.step(inputs, ego_motion)
        traj = out.trajectory
        status = out.path_status
        if (traj is None or not traj.header.valid or status is None or not status.path_valid
                or status.active_function != ActiveFunction.HWA):
            return out
        road = self.harness.road
        x0, y0, yaw0 = self.harness.vehicle.rear_axle()
        self.station = road.project(x0, y0, self.station).s
        s = self.station
        c, sn = cos(yaw0), sin(yaw0)
        points = []
        for i, p in enumerate(traj.points):
            if i:
                prev = traj.points[i - 1]
                dt = p.time_from_start - prev.time_from_start
                s += 0.5 * (prev.longitudinal_velocity_mps + p.longitudinal_velocity_mps) * dt
            x, y, yaw = road.pose_at(s)
            k = float(np.interp(s, road.s, road.kappa))
            dx, dy, d_yaw = x - x0, y - y0, yaw - yaw0
            pose = Pose2D(c * dx + sn * dy, -sn * dx + c * dy, atan2(sin(d_yaw), cos(d_yaw)))
            points.append(replace(p, pose=pose, lateral_velocity_mps=0.0, curvature=k,
                                  heading_rate_rps=p.longitudinal_velocity_mps * k,
                                  front_wheel_angle_rad=atan(self.harness.vehicle_config.wheelbase * k)))
        return replace(out, trajectory=replace(traj, points=tuple(points)))


def trace(log):
    metrics = experiment.metrics
    t = np.asarray(log.t_us, dtype=float) * 1e-6
    active = metrics._cycle_mask_at(
        t, np.array([c.t0_us for c in log.cycles]) * 1e-6,
        np.array([metrics._hwa(c) for c in log.cycles]),
    )
    dt = float(np.median(np.diff(t)))
    sos = butter(metrics.R79_FILTER_ORDER, metrics.R79_FILTER_HZ, btype="low",
                 fs=1 / dt, output="sos")
    ay, _ = sosfilt(sos, log.a_y, zi=sosfilt_zi(sos) * log.a_y[0])
    window = round(metrics.JERK_WINDOW_S / dt)
    jerk = (ay[window:] - ay[:-window]) / (window * dt)
    jerk = np.r_[np.zeros(window), jerk]

    idx = np.flatnonzero(active)
    peak_indices = [idx[np.argmax(np.abs(signal[idx]))] for signal in (ay, jerk)]
    # Keep the actual peak samples while reducing the plotted data to about 100 Hz.
    take = np.unique(np.r_[idx[::10], peak_indices, idx[-1]])
    rear = np.asarray(log.rear)
    station, offset = [], []
    hint = None
    for x, y, _ in rear[take]:
        p = log.road.project(x, y, hint)
        hint = p.s
        station.append(p.s)
        offset.append(p.d)
    peak = tuple((station[np.searchsorted(take, k)], signal[k])
                 for k, signal in zip(peak_indices, (ay, jerk)))
    steering = np.degrees(log.steering_ratio * np.asarray(log.wheel_angle)[take])
    return {"s": np.asarray(station), "d": np.asarray(offset), "rear": rear[take],
            "ay": ay[take], "jerk": jerk[take], "steering": steering, "peak": peak}


def curve_sections(road):
    direction = np.sign(np.where(np.abs(road.kappa) > 1e-9, road.kappa, 0))
    changes = np.r_[0, np.flatnonzero(direction[1:] != direction[:-1]) + 1, len(direction) - 1]
    return [(road.s[a], road.s[b], "Cua trái" if direction[a] > 0 else "Cua phải")
            for a, b in zip(changes[:-1], changes[1:]) if direction[a] != 0]


def vn(value, precision=3):
    return f"{value:.{precision}f}".replace(".", ",").replace("-", "−")


def key_stations(road):
    left = road.s[np.isclose(road.kappa, road.kappa.max(), atol=1e-10)]
    right = road.s[np.isclose(road.kappa, road.kappa.min(), atol=1e-10)]
    swap = road.s[np.flatnonzero((road.kappa < 0) & (road.s > left[-1]))[0]]
    return [("Đỉnh cua 1", float(left.mean())), ("Đổi chiều", float(swap)),
            ("Đỉnh cua 2", float(right.mean()))]


def overview_points(road, s, d):
    theta = np.interp(s, road.s, road.theta)
    dx = EXAGGERATION * d
    return -np.interp(s, road.s, road.y) - dx * np.cos(theta), np.interp(s, road.s, road.x) - dx * np.sin(theta)


def draw_overview(ax, road, traces, keys, s_lo, s_hi):
    half = road.lane_width / 2
    s = np.linspace(s_lo, s_hi, 700)
    edge = half + 1.35
    for lo, hi, color in ((-edge, edge, SHOULDER), (-half, half, ROAD), (-0.3, 0.3, CORRIDOR)):
        x1, y1 = overview_points(road, s, lo)
        x2, y2 = overview_points(road, s[::-1], hi)
        ax.fill(np.r_[x1, x2], np.r_[y1, y2], color=color, lw=0)
    for d in (-half, half):
        ax.plot(*overview_points(road, s, d), color="white", lw=1.8, ls=(0, (6, 5)))
    for data, color, style in zip(traces, COLORS, STYLES):
        keep = (data["s"] >= s_lo) & (data["s"] <= s_hi)
        ax.plot(*overview_points(road, data["s"][keep], data["d"][keep]),
                color=color, lw=2.4, ls=style, zorder=4)
    ax.plot(*overview_points(road, s, 0.0), color=REFERENCE, lw=1.25, ls=REFERENCE_STYLE,
            dash_capstyle="round", zorder=4.5)
    for title, station in keys:
        x, y = overview_points(road, np.full(2, station), np.array([-edge, edge]))
        ax.plot(x, y, color=INK, lw=1.15, zorder=5)
        tx, ty = overview_points(road, station, edge + 0.32)
        ax.text(tx, ty, f"{title}\ns = {vn(station, 1)} m", ha="right", va="center",
                fontsize=9.4, weight="bold")
    x, y = overview_points(road, s_lo + 12, edge + 0.65)
    ax.annotate("hướng xe", xy=(x, y + 19), xytext=(x, y), ha="right", va="top",
                fontsize=8.5, color=MUTED, arrowprops={"arrowstyle": "-|>", "color": MUTED, "lw": 1.1})
    left_edge, _ = overview_points(road, s, edge)
    right_edge, _ = overview_points(road, s, -edge)
    ax.set_xlim(left_edge.min() - 32, right_edge.max() + 5)
    ax.margins(y=0.04)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"Toàn cảnh cua chữ S\nChiều ngang phóng đại ×{EXAGGERATION:g}", loc="left")


def draw_zoom(ax, road, traces, key, wheelbase, vehicle_width):
    from matplotlib.patches import Polygon

    title, s0 = key
    half = road.lane_width / 2
    ax.set_facecolor(SHOULDER)
    ax.axhspan(-half, half, color=ROAD)
    for boundary in (-half, half):
        ax.axhline(boundary, color="white", lw=2, ls=(0, (6, 4)), zorder=1)
    ax.axhline(0.0, color=REFERENCE, lw=1.1, ls=REFERENCE_STYLE, dash_capstyle="round", zorder=6)
    theta = np.interp(s0, road.s, road.theta)
    body_x = np.array([-1.0, wheelbase + 1.0, wheelbase + 1.0, -1.0])
    body_y = 0.5 * vehicle_width * np.array([-1.0, -1.0, 1.0, 1.0])
    for index, (data, color, style) in enumerate(zip(traces, COLORS, STYLES)):
        d = np.interp(s0, data["s"], data["d"])
        delta = np.interp(s0, data["s"], np.unwrap(data["rear"][:, 2])) - theta
        c, sn = np.cos(delta), np.sin(delta)
        xb, yb = c * body_x - sn * body_y, d + sn * body_x + c * body_y
        ax.add_patch(Polygon(np.column_stack((xb, yb)), color=color, lw=0, alpha=0.10, zorder=2))
        ax.add_patch(Polygon(np.column_stack((xb, yb)), fill=False, edgecolor=color,
                             linestyle=style, linewidth=1.2, zorder=4))
        keep = np.abs(data["s"] - s0) <= 10
        ax.plot(data["s"][keep] - s0, data["d"][keep], color=color, lw=1.9, ls=style, zorder=5)
        ax.text(0, -0.13 - index * 0.15, f"{LABELS[index]}  ·  d = {vn(100 * d, 1)} cm",
                color=color, transform=ax.transAxes, va="top", fontsize=9.2, weight="bold")
    ax.set_title(f"{title} · s = {vn(s0, 1)} m\nĐúng tỉ lệ · xe đi sang phải", loc="left")
    ax.set_xlim(-8.5, 8.5)
    ax.set_ylim(-2.45, 2.45)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([-half, 0, half], [vn(-half, 2), "0", vn(half, 2)])
    ax.tick_params(length=0, labelsize=8)
    for spine in ax.spines.values():
        spine.set_visible(False)


def draw_table(ax, row, traces):
    first, second = [row[name] for name in ("quintic", "waypoint")]
    values = [
        ("Đỉnh gia tốc ngang xe (m/s²)", first["vehicle_peak_ay_mps2"], second["vehicle_peak_ay_mps2"], 3, False),
        ("Đỉnh jerk ngang xe (m/s³)", first["vehicle_peak_jerk_mps3"], second["vehicle_peak_jerk_mps3"], 3, False),
        ("Đỉnh góc vô-lăng (°)", *(float(np.max(np.abs(t["steering"]))) for t in traces), 1, False),
        ("Khoảng hở DLC nhỏ nhất (m)", first["criteria"]["PP-SWR-051"]["value"],
         second["criteria"]["PP-SWR-051"]["value"], 3, True),
        ("Lệch tâm lớn nhất của xe (m)", first["vehicle_max_offset_m"], second["vehicle_max_offset_m"], 3, False),
        ("Lệch ngang giữa hai path (mm)", 1000 * first["criteria"]["PP-SWR-100"]["value"],
         1000 * second["criteria"]["PP-SWR-100"]["value"], 1, False),
    ]
    headers = ["Chỉ số SIL", "Quintic gốc", "Có điểm giữa", "Thay đổi"]
    data = []
    for label, a, b, precision, _ in values:
        change = (b / a - 1.0) * 100
        data.append([label, vn(a, precision), vn(b, precision),
                     ("+" if change > 0 else "") + vn(change, 1) + "%"])
    table = ax.table(cellText=data, colLabels=headers, cellLoc="left", colLoc="left",
                     colWidths=(0.47, 0.17, 0.19, 0.17), bbox=(0, 0.08, 1, 0.86))
    table.auto_set_font_size(False)
    table.set_fontsize(10.1)
    for (i, j), cell in table.get_celld().items():
        cell.PAD = 0.018
        cell.set_linewidth(0)
        cell.set_facecolor("#efeee9" if i and i % 2 else SURFACE)
        if i == 0:
            cell.set_text_props(weight="bold")
        elif j in (1, 2):
            cell.set_text_props(color=COLORS[j - 1], weight="bold")
        elif j == 3:
            _, a, b, _, higher_better = values[i - 1]
            color = "#1c5cab" if ((b > a) == higher_better) else "#ab3333"
            cell.set_text_props(color=color, weight="bold")
    ax.axis("off")


def draw_charts(axes, traces, keys, s_lo, s_hi):
    from matplotlib.ticker import FuncFormatter

    chart_spec = (("d", "Lệch ngang của tâm trục sau (m)"), ("ay", "Gia tốc ngang của xe (m/s²)"),
                  ("jerk", "Jerk ngang của xe (m/s³)"), ("steering", "Góc vô-lăng (°)"))
    for i, (ax, (signal, title)) in enumerate(zip(axes, chart_spec)):
        if signal == "d":
            ax.axhspan(-0.30, 0.30, color=CORRIDOR, alpha=0.55)
        if signal == "d":
            ax.axhline(0.0, color=REFERENCE, lw=1.0, ls=REFERENCE_STYLE, dash_capstyle="round", zorder=3)
        else:
            ax.axhline(0.0, lw=0.8, color="#a6a39a")
        for _, s in keys:
            ax.axvline(s, ls=":", lw=0.95, color="#868481")
        for data, color, style in zip(traces, (*COLORS, FOLLOW_COLOR), (*STYLES, FOLLOW_STYLE)):
            ax.plot(data["s"], data[signal], color=color, lw=1.8, ls=style)
            if signal in ("ay", "jerk"):
                px, py = data["peak"][int(signal == "jerk")]
                ax.scatter(px, py, color=color, s=24, edgecolor=SURFACE, linewidth=0.65, zorder=4)
        ax.set_xlim(s_lo, s_hi)
        if signal == "d":
            ax.set_ylim(-0.34, 0.34)
            ax.text(s_lo + 5, -0.322, "+ trái / − phải", fontsize=8, color=MUTED)
        ax.set_title(title, loc="left")
        ax.grid(color=GRID, lw=0.75)
        ax.set_axisbelow(True)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:g}".replace(".", ",").replace("-", "−")))
        if i >= 2:
            ax.set_xlabel("Quãng đường dọc tâm làn s (m)")


def plot(log, traces, row):
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10, "text.color": INK, "axes.labelcolor": MUTED,
        "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": GRID,
        "axes.facecolor": SURFACE, "xtick.color": MUTED, "ytick.color": MUTED,
        "axes.titleweight": "bold", "axes.titlesize": 11, "axes.titlepad": 8,
    })
    road = log.road
    keys = key_stations(road)
    curves = curve_sections(road)
    s_lo = 20 * np.floor((curves[0][0] - 45) / 20)
    last_peak = max(s for data in traces for s, _ in data["peak"])
    s_hi = 20 * np.ceil(max(curves[-1][1] + 55, last_peak + 10) / 20)
    fig = plt.figure(figsize=(21.8, 12.0), facecolor=SURFACE)
    fig.text(0.018, 0.962, "Cua chữ S (S1f) · Quintic gốc và quintic có điểm trung gian",
             fontsize=22, weight="bold")
    fig.text(0.018, 0.932, "SIL vòng kín · VP-0 · làn 3,5 m · 90 km/h · seed 1 · camera 80 m, trễ 100 ms",
             fontsize=11, color=MUTED)
    handles = [Line2D([0], [0], color=color, ls=style, lw=2.6, label=label)
               for color, style, label in zip(COLORS, STYLES, LABELS)]
    handles.append(Line2D([0], [0], color=REFERENCE, ls=REFERENCE_STYLE, lw=1.5,
                          dash_capstyle="round", label="Ref line · tâm làn thật"))
    handles.append(Line2D([0], [0], color=FOLLOW_COLOR, ls=FOLLOW_STYLE, lw=2.1,
                          label="Xe bám ref line · 4 đồ thị"))
    handles.append(Patch(facecolor=CORRIDOR, label="Dải ±0,30 m quanh tâm"))
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.014, 0.911),
               frameon=False, ncol=5, handlelength=2.8, columnspacing=2.2)

    layout = fig.add_gridspec(1, 2, left=0.018, right=0.979, top=0.846, bottom=0.12,
                              wspace=0.068, width_ratios=(1, 1.10))
    road_grid = layout[0, 0].subgridspec(3, 2, width_ratios=(0.90, 1.14), wspace=0.07, hspace=0.38)
    draw_overview(fig.add_subplot(road_grid[:, 0]), road, traces, keys, s_lo, s_hi)
    for i, key in enumerate(keys):
        draw_zoom(fig.add_subplot(road_grid[i, 1]), road, traces, key, log.wheelbase, log.vehicle_width)

    metric_grid = layout[0, 1].subgridspec(3, 2, height_ratios=(1.17, 1, 1), wspace=0.24, hspace=0.46)
    draw_table(fig.add_subplot(metric_grid[0, :]), row, traces[:2])
    axes = [fig.add_subplot(metric_grid[i, j]) for i in (1, 2) for j in (0, 1)]
    draw_charts(axes, traces, keys, s_lo, s_hi)
    fig.text(0.018, 0.064, "Xe bám ref line: bộ điều khiển nhận trực tiếp tâm làn thật, dùng cùng mô hình xe và tốc độ.",
             fontsize=9.3, color=MUTED)
    fig.text(0.018, 0.042, "Đường màu là chuyển động của tâm trục sau. Hình thân xe tại các điểm zoom "
             "dùng bề rộng kể gương và chiều dài xấp xỉ theo SQTS.", fontsize=9.3, color=MUTED)
    fig.text(0.018, 0.020, "Gia tốc ngang lọc 0,5 Hz · Jerk trung bình trượt 0,5 s · Chấm tròn đánh dấu đỉnh trị tuyệt đối.",
             fontsize=9.3, color=MUTED)
    fig.savefig(experiment.HERE / "s1f-quintic-comparison.png", dpi=132)
    plt.close(fig)


def main():
    original = json.loads((experiment.HERE / "quintic_results.json").read_text(encoding="utf-8"))
    row = next(r for r in original["runs"] if r["case"] == "S1f" and r["seed"] == 1
               and r["publish_object_list_on_empty_road"])
    scenario = replace(experiment.loader.load("S1", "f"), acc=row["acc"],
                       camera_latency_ms=original["camera_latency_ms"], camera_view_m=original["camera_view_m"])
    with TemporaryDirectory(prefix=".s1f-plot-", dir=experiment.HERE) as work:
        work = Path(work)
        os.environ["MPLCONFIGDIR"] = str(work / "matplotlib")
        libraries = experiment.build_pair(work)
        traces = []
        for key, library in zip(("quintic", "waypoint"), libraries):
            log = experiment.ObjectListHarness(scenario, library, row["seed"]).run()
            result = experiment.metrics.evaluate(log)
            data = trace(log)
            dlc = next(c.value for c in result.criteria if c.id == "PP-SWR-051")
            for expected, (_, value) in zip(("vehicle_peak_ay_mps2", "vehicle_peak_jerk_mps3"), data["peak"]):
                np.testing.assert_allclose(abs(value), row[key][expected], rtol=0, atol=1e-6)
            np.testing.assert_allclose(dlc, row[key]["criteria"]["PP-SWR-051"]["value"], rtol=0, atol=1e-6)
            traces.append(data)
        oracle = experiment.ObjectListHarness(scenario, libraries[0], row["seed"])
        oracle.planner = RefLinePlanner(oracle)
        ref_log = oracle.run()
        ref_trace = trace(ref_log)
        assert np.all(np.isfinite(ref_trace["ay"])) and np.all(np.isfinite(ref_trace["steering"]))
        traces.append(ref_trace)
        print("Ref line peak a_y / jerk:",
              *(round(abs(value), 3) for _, value in ref_trace["peak"]), flush=True)
        plot(log, traces, row)


if __name__ == "__main__":
    main()

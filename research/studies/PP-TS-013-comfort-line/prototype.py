#!/usr/bin/env python3
"""Prototype PP-TS-013 so path trong hành lang an toàn; kết quả thuộc nghiên cứu hình học, không
phải lượt benchmark của planner C.
"""

from __future__ import annotations

import json
import sys
import time
import xml.etree.ElementTree as ET
from collections.abc import Callable
from dataclasses import dataclass
from math import atan2, cos, sin
from pathlib import Path

import numpy as np
from scipy.interpolate import CubicSpline

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))

from sim.vehicle.bicycle import Bicycle, BicycleState, steady_cornering  # noqa: E402
from sim.vehicle.profiles import (  # noqa: E402
    ACTUATOR_DELAY_S,
    MAX_STEERING_WHEEL_RATE,
    PROFILES,
    STEERING_RATIO,
)

PROFILE = PROFILES["VP-0"]
LANE_W = 3.5
VIEW_M = 80.0
H = 1.0
OFFSET_MAX = 0.3
FREE_SIDE = (LANE_W - PROFILE.width_with_mirrors) / 2
MARGIN = 0.3
CORRIDOR = min(OFFSET_MAX, FREE_SIDE - MARGIN)

A0, J0, D0 = 1.0, 1.0, 1.0
W_J = 4.0
W_D = 1.0
W_PK = 1e3
W_TERM = 1e4
CAP_SPAN = 80.0
EXTRAP_M = 80.0  # Sau tầm nhìn, ngoại suy độ cong cuối và đưa path về tâm làn ở cuối cửa sổ mở rộng.

CTRL_DT = 0.01
SIM_DT = 0.002
REVERSAL_GAP_DEG = 0.5


@dataclass
class Road:
    name: str
    label: str
    v: float
    segs: list
    focus: tuple

    def build(self, pad: float = VIEW_M + 120.0):
        k_end = self.segs[-1][2]
        segs = list(self.segs) + [(pad, k_end, k_end)]
        ds = 0.05
        L = sum(s[0] for s in segs)
        s = np.arange(0.0, L + ds / 2, ds)
        k = np.zeros_like(s)
        s0 = 0.0
        for length, k0, k1 in segs:
            m = (s >= s0) & (s <= s0 + length)
            k[m] = k0 + (k1 - k0) * (s[m] - s0) / length
            s0 += length
        th = np.concatenate([[0.0], np.cumsum(0.5 * (k[1:] + k[:-1]) * ds)])
        x = np.concatenate([[0.0], np.cumsum(0.5 * (np.cos(th[1:]) + np.cos(th[:-1])) * ds)])
        y = np.concatenate([[0.0], np.cumsum(0.5 * (np.sin(th[1:]) + np.sin(th[:-1])) * ds)])
        self.s, self.k, self.th, self.x, self.y = s, k, th, x, y
        self.length = L - pad  # Các chỉ số chỉ tính đến mốc cuối phần đường thử.
        self.sn = np.arange(0.0, L - 1e-9, H)
        self.kn = np.interp(self.sn, s, k)
        return self


def road_from_xodr(path: Path, name, label, v, focus, trim=None) -> Road:
    root = ET.parse(path).getroot()
    segs = []
    for g in root.iter("geometry"):
        L = float(g.get("length"))
        child = list(g)[0]
        if child.tag == "line":
            segs.append((L, 0.0, 0.0))
        elif child.tag == "arc":
            c = float(child.get("curvature"))
            segs.append((L, c, c))
        elif child.tag == "spiral":
            segs.append((L, float(child.get("curvStart")), float(child.get("curvEnd"))))
    if trim is not None:
        segs[0] = (segs[0][0] - trim, 0.0, 0.0)
    return Road(name, label, v, segs, focus)


def research_roads() -> list[Road]:
    rd = ROOT / "benchmark" / "roads"
    roads = []
    R, Lc, defl = 250.0, 60.0, np.radians(20.0)
    arc = (defl - Lc / R) * R
    roads.append(Road("Rf", "Rf (nghiên cứu): cua hữu hạn R 250 m, đổi hướng 20°, 90 km/h", 25.0,
                      [(150.0, 0, 0), (Lc, 0, 1 / R), (arc, 1 / R, 1 / R), (Lc, 1 / R, 0), (250.0, 0, 0)],
                      (100.0, 150 + 2 * Lc + arc + 150)))
    roads.append(road_from_xodr(rd / "S1d.xodr", "S1d", "S1d: cua chữ S R 500 m, 90 km/h", 25.0, (100.0, 800.0), trim=50))
    roads.append(road_from_xodr(rd / "S1f.xodr", "S1f", "S1f: R171 S-bend 787/374 m, 90 km/h", 25.0, (50.0, 450.0), trim=50))
    roads.append(road_from_xodr(rd / "S14e.xodr", "S14e", "S14e: R171 S-bend, 130 km/h", 36.111, (50.0, 450.0), trim=50))
    roads.append(road_from_xodr(rd / "S1c.xodr", "S1c", "S1c: vào cung R 250 m (dài), 90 km/h", 25.0, (100.0, 600.0), trim=100))
    roads.append(road_from_xodr(rd / "S1be.xodr", "S1be", "S1be: vào R 200 m, clothoid 60 m, 90 km/h", 25.0, (50.0, 360.0), trim=50))
    for r in roads:
        segs = r.segs
        if segs[-1][1] == segs[-1][2] and segs[-1][1] != 0 and segs[-1][0] > 250:
            segs[-1] = (250.0, segs[-1][1], segs[-1][2])
        r.focus = (r.focus[0], min(r.focus[1], sum(s[0] for s in segs)))
        r.build()
    return roads


def ls_rows(kr: np.ndarray, v: float):
    n = len(kr)
    m = n - 2
    K = np.zeros((m, n))
    for i in range(m):
        K[i, i] += 1 / H**2
        K[i, i + 1] += -2 / H**2 + kr[i + 1] ** 2
        K[i, i + 2] += 1 / H**2
    k0 = kr[1:-1]
    Dk = (np.eye(m, k=1) - np.eye(m))[:-1] / H
    A_ay = v**2 * K / A0
    b_ay = -v**2 * k0 / A0
    A_j = np.sqrt(W_J) * v**3 * (Dk @ K) / J0
    b_j = -np.sqrt(W_J) * v**3 * (Dk @ k0) / J0
    A_d = np.sqrt(W_D) * np.eye(n) / D0
    b_d = np.zeros(n)
    return np.vstack([A_ay, A_j, A_d]), np.concatenate([b_ay, b_j, b_d])


def curvature_matrix(kr):
    n = len(kr)
    K = np.zeros((n - 2, n))
    for i in range(n - 2):
        K[i, i] += 1 / H**2
        K[i, i + 1] += -2 / H**2 + kr[i + 1] ** 2
        K[i, i + 2] += 1 / H**2
    return K


def box_qp(Hm, g, lo, hi, x0=None, max_iter=500):
    """QP hộp có Hessian xác định dương; dùng active set trên biến gốc và điểm khởi đầu từ chu kỳ
    trước.
    """
    n = len(g)
    x = np.clip(np.zeros(n) if x0 is None else x0, lo, hi)
    tol = 1e-12
    W = (x <= lo + tol) | (x >= hi - tol)
    for _ in range(max_iter):
        F = ~W
        xn = x.copy()
        if F.any():
            rhs = -(g[F] + Hm[np.ix_(F, W)] @ x[W])
            xn[F] = np.linalg.solve(Hm[np.ix_(F, F)], rhs)
        p = xn - x
        out_lo = F & (xn < lo - tol)
        out_hi = F & (xn > hi + tol)
        if out_lo.any() or out_hi.any():
            alpha = 1.0
            with np.errstate(divide="ignore", invalid="ignore"):
                a_lo = np.where(out_lo, (lo - x) / p, np.inf)
                a_hi = np.where(out_hi, (hi - x) / p, np.inf)
            alpha = min(1.0, float(np.min(np.minimum(a_lo, a_hi))))
            x = np.clip(x + alpha * p, lo, hi)
            W = W | (x <= lo + tol) | (x >= hi - tol)
            continue
        x = xn
        grad = Hm @ x + g
        at_lo = W & (x <= lo + tol)
        at_hi = W & (x >= hi - tol)
        viol = np.where(at_lo, -grad, 0.0) + np.where(at_hi, grad, 0.0)
        k = int(np.argmax(viol))
        if viol[k] <= 1e-10:
            return x
        W[k] = False
    return x


def solve_window(kr, v, fixed_head, corridor, tail_parallel=True, fixed_tail=None, klim=None,
                 tail_centre=False, x0=None):
    """Fit offset theo hành lang đối xứng hoặc cặp biên (phải, trái). Phạt vượt ngưỡng độ cong nếu
    có.
    """
    n = len(kr)
    A, b = ls_rows(kr, v)
    rows_A, rows_b = [A], [b]
    if tail_parallel:
        t = np.zeros((2, n))
        t[0, -1], t[0, -2] = 1 / H, -1 / H
        t[1, -1], t[1, -2], t[1, -3] = 1 / H**2, -2 / H**2, 1 / H**2
        rows_A.append(np.sqrt(W_TERM) * t * v**2)
        rows_b.append(np.zeros(2))
    if tail_centre:
        t = np.zeros((1, n))
        t[0, -1] = 1.0
        rows_A.append(np.sqrt(W_TERM) * t / D0)
        rows_b.append(np.zeros(1))
    A = np.vstack(rows_A)
    b = np.concatenate(rows_b)
    fix = np.full(n, np.nan)
    fix[: len(fixed_head)] = fixed_head
    if fixed_tail is not None:
        fix[n - len(fixed_tail):] = fixed_tail
    free = np.isnan(fix)
    dfix = np.where(free, 0.0, fix)
    if isinstance(corridor, tuple):
        lower, upper = corridor
    else:
        half = max(0.0, corridor)
        lower, upper = -half, half
    if not lower <= 0.0 <= upper:
        raise ValueError("corridor must contain the lane centre")
    if lower == upper == 0.0:
        return dfix
    lo = np.full(free.sum(), lower)
    hi = np.full(free.sum(), upper)
    Af = A[:, free]
    r0 = b - A[:, ~free] @ dfix[~free]
    H0 = Af.T @ Af
    g0 = -Af.T @ r0
    K = curvature_matrix(kr)
    Kf = K[:, free]
    k0 = kr[1:-1] + K[:, ~free] @ dfix[~free]
    c = W_PK * v**4 / A0**2
    x = None if x0 is None else x0[free]
    act = np.zeros(n - 2)
    for _ in range(15):
        Hm, g = H0, g0
        if klim is not None and act.any():
            idx = np.nonzero(act)[0]
            Ki = Kf[idx]
            Hm = H0 + c * Ki.T @ Ki
            g = g0 + c * Ki.T @ (k0[idx] - act[idx] * klim[1:-1][idx])
        x = box_qp(Hm, g, lo, hi, x)
        if klim is None:
            break
        kp = Kf @ x + k0
        new = np.where(kp > klim[1:-1], 1.0, np.where(kp < -klim[1:-1], -1.0, 0.0))
        if np.array_equal(new, act):
            break
        act = new
    d = dfix.copy()
    d[free] = x
    return d


def peak_limit(kr_known: np.ndarray, i: int, j: int) -> np.ndarray:
    span = int(round(CAP_SPAN / H))
    a = np.abs(kr_known)
    out = np.empty(j - i)
    for k in range(i, j):
        out[k - i] = a[max(0, k - span):min(len(a), k + span + 1)].max()
    return out


def plan_global(road: Road, corridor: float, cap: bool = True) -> np.ndarray:
    """Đối chứng biết toàn bộ đường, chia khối 150 m với tầm nhìn trước 250 m."""
    kr = road.kn
    n = len(kr)
    d = np.zeros(n)
    block, look = 150, 250
    i = 0
    while i < n - 3:
        j = min(n, i + block + look)
        end_tail = np.zeros(3) if j == n else None
        klim = peak_limit(kr, i, j) if cap else None
        w = solve_window(kr[i:j], road.v, d[i:i + 3], corridor, tail_parallel=(j != n),
                         fixed_tail=end_tail, klim=klim)
        d[i + 3:min(n, i + block + 3)] = w[3:min(j - i, block + 3)]
        i += block
    return d


def continuity_change(new: np.ndarray, old: np.ndarray, curvature: np.ndarray) -> np.ndarray:
    delta = new - old
    heading = np.diff(delta) / H
    bend = np.diff(delta, n=2) / H**2 + curvature[1:-1]**2 * delta[1:-1]
    return np.array([np.max(np.abs(a), initial=0.0) for a in (delta, heading, bend)])


def plan_receding(road: Road, corridor: float | tuple[float, float], view: float = VIEW_M,
                  cap: bool = True, extrap: float = EXTRAP_M, cont_stats: dict | None = None,
                  continuity_limits: tuple[float, float, float] | None = None,
                  observe_plan: Callable[[int, np.ndarray], None] | None = None,
                  preview: Callable[[int], np.ndarray] | None = None,
                  adjust_plan: Callable[[int, np.ndarray, int, np.ndarray, np.ndarray | None],
                                        np.ndarray] | None = None) -> np.ndarray:
    """Chỉ quan sát [s, s + view]. Ngoài vùng đó giữ độ cong cuối và yêu cầu quay về tâm làn."""
    kr = road.kn
    n = len(kr)
    nv = int(round(view / H)) + 1
    ne = int(round(extrap / H))
    horizon = int(3.0 * road.v / H)
    limits = None if continuity_limits is None else np.asarray(continuity_limits, dtype=float)
    if limits is not None and (limits.shape != (3,) or not np.all(np.isfinite(limits) & (limits > 0))):
        raise ValueError("continuity_limits requires three positive, finite thresholds")
    d = np.zeros(n)
    first = int(np.argmax(np.abs(kr) > 1e-9)) if preview is None else 0
    history = np.zeros(n) if preview is not None else kr
    prev = None
    for i in range(max(0, first - nv - 3), n - nv):
        seen = kr[i:i + nv] if preview is None else preview(i)
        nh = min(len(seen), horizon)
        if preview is not None:
            history[i] = seen[0]
        kw = np.concatenate([seen, np.full(nv + ne - len(seen), seen[-1])])
        if cap:
            known = np.concatenate([history[max(0, i - nv):i], kw])
            off = min(i, nv)
            klim = peak_limit(known, off, off + len(kw))
        else:
            klim = None
        x0 = None if prev is None else np.concatenate([prev[1:], prev[-1:]])
        w = solve_window(kw, road.v, d[i:i + 3], corridor, tail_parallel=True,
                         tail_centre=(ne > 0), klim=klim, x0=x0)
        scale = 1.0
        if x0 is not None and limits is not None:
            change = continuity_change(w[:nh], x0[:nh], seen[:nh])
            scale = max(1.0, float(np.max(change / limits)))
            if scale > 1.0:
                w = x0 + (w - x0) / scale
        if adjust_plan is not None:
            w = adjust_plan(i, kw, nh, w, x0)
        if x0 is not None and cont_stats is not None and road.focus[0] <= road.sn[i] <= road.focus[1]:
            change = continuity_change(w[:nh], x0[:nh], kr[i:i + nh])
            for key, value in zip(("max", "heading_max", "curvature_max"), change):
                cont_stats[key] = max(cont_stats.get(key, 0.0), float(value))
            cont_stats["cycles"] = cont_stats.get("cycles", 0) + 1
            cont_stats["limited_cycles"] = cont_stats.get("limited_cycles", 0) + int(scale > 1.0)
        d[i + 3] = w[3]
        if observe_plan is not None:
            observe_plan(i, w[:nh])
        prev = w
    return d


def path_signals(road: Road, d: np.ndarray):
    kr = road.kn
    dpp = np.zeros_like(d)
    dpp[1:-1] = (d[2:] - 2 * d[1:-1] + d[:-2]) / H**2
    kp = kr + dpp + kr**2 * d
    v = road.v
    ay = v**2 * kp
    jy = np.gradient(ay, H) * v
    return kp, ay, jy


from sim.stand_ins.lateral_controller import HEADING_GAIN, LATERAL_GAIN_RAD_PER_M, PREVIEW_S  # noqa: E402

FRONT_CORNER = 0.9
REAR_CORNER = 1.0


def closed_loop(road: Road, d: np.ndarray):
    p = PROFILE
    v = road.v
    ds = road.s[1] - road.s[0]
    cs = CubicSpline(road.sn, d)
    dd = cs(road.s)
    nx, ny = -np.sin(road.th), np.cos(road.th)
    px, py = road.x + dd * nx, road.y + dd * ny
    pth = np.unwrap(np.arctan2(np.gradient(py), np.gradient(px)))
    kp_nodes, _, _ = path_signals(road, d)
    kp_dense = np.interp(road.s, road.sn, kp_nodes)
    K = p.understeer_gradient

    st = BicycleState(px[0] + p.lr * cos(pth[0]), py[0] + p.lr * sin(pth[0]), pth[0], 0.0, 0.0)
    car = Bicycle(p, st)
    car.v_x = v
    n_delay = int(round(ACTUATOR_DELAY_S / CTRL_DT))
    queue = [0.0] * n_delay
    sw_prev = 0.0
    idx = 0
    t_end = road.length / v
    sub = int(round(CTRL_DT / SIM_DT))
    log = {k: [] for k in ("t", "s", "ay", "sw", "ey", "dveh", "psirel")}
    t = 0.0
    nmax = len(px) - 1
    while t < t_end:
        psi = st.psi
        xr, yr = st.x - p.lr * cos(psi), st.y - p.lr * sin(psi)
        lo, hi = max(0, idx - 200), min(len(px), idx + 800)
        j = lo + int(np.argmin((px[lo:hi] - xr) ** 2 + (py[lo:hi] - yr) ** 2))
        idx = j
        ey_now = -(xr - px[j]) * sin(pth[j]) + (yr - py[j]) * cos(pth[j])
        vyb = st.v_y - p.lr * st.r
        r = st.r
        T = PREVIEW_S
        yaw = r * T
        if abs(r) < 1e-6:
            bx, by = v * T, vyb * T
        else:
            bx = (v * sin(yaw) + vyb * (cos(yaw) - 1.0)) / r
            by = (v * (1.0 - cos(yaw)) + vyb * sin(yaw)) / r
        qx = xr + bx * cos(psi) - by * sin(psi)
        qy = yr + bx * sin(psi) + by * cos(psi)
        qpsi = psi + yaw
        jt = min(nmax, j + int(round(v * T / ds)))
        dx, dy = px[jt] - qx, py[jt] - qy
        e_y = -sin(qpsi) * dx + cos(qpsi) * dy
        e_yaw = (pth[jt] - qpsi + np.pi) % (2 * np.pi) - np.pi
        slip = atan2(vyb, v)
        jf = min(nmax, j + int(round(v * ACTUATOR_DELAY_S / ds)))
        kff = kp_dense[jf]
        delta = p.wheelbase * kff + K * v * v * kff + LATERAL_GAIN_RAD_PER_M * e_y + HEADING_GAIN * (e_yaw - slip)
        delta = float(np.clip(delta, -p.max_wheel_angle, p.max_wheel_angle))
        sw = delta * STEERING_RATIO
        step = MAX_STEERING_WHEEL_RATE * CTRL_DT
        sw = float(np.clip(sw, sw_prev - step, sw_prev + step))
        sw_prev = sw
        queue.append(sw / STEERING_RATIO)
        delta_applied = queue.pop(0)
        for _ in range(sub):
            car.step(SIM_DT, delta_applied, v)
        st = car.state
        t += CTRL_DT
        xr, yr = st.x - p.lr * cos(st.psi), st.y - p.lr * sin(st.psi)
        dveh = -(xr - road.x[j]) * sin(road.th[j]) + (yr - road.y[j]) * cos(road.th[j])
        log["t"].append(t)
        log["s"].append(road.s[j])
        log["ay"].append(car.a_y)
        log["sw"].append(np.degrees(delta_applied * STEERING_RATIO))
        log["ey"].append(ey_now)
        log["dveh"].append(dveh)
        log["psirel"].append(st.psi - road.th[j])
    return {k: np.asarray(val) for k, val in log.items()}


def reversals(sw_deg: np.ndarray, gap: float) -> int:
    count, ext, direction = 0, sw_deg[0], 0
    for a in sw_deg[1:]:
        if direction >= 0:
            if a > ext:
                ext = a
            elif ext - a >= gap:
                if direction > 0:
                    count += 1
                direction, ext = -1, a
        if direction < 0:
            if a < ext:
                ext = a
            elif a - ext >= gap:
                count += 1
                direction, ext = 1, a
    return count


def cl_metrics(road: Road, log):
    m = (log["s"] >= road.focus[0]) & (log["s"] <= road.focus[1])
    ay = log["ay"][m]
    jy = np.gradient(log["ay"], CTRL_DT)
    k = 10
    jy = np.convolve(jy, np.ones(k) / k, mode="same")[m]
    sw = log["sw"][m]
    swr = np.gradient(log["sw"], CTRL_DT)[m]
    half_body = PROFILE.width_with_mirrors / 2
    dv, sp = log["dveh"][m], np.sin(log["psirel"][m])
    front = dv + (PROFILE.wheelbase + FRONT_CORNER) * sp
    rear = dv - REAR_CORNER * sp
    clear = LANE_W / 2 - half_body - np.maximum(np.abs(front), np.abs(rear))
    return {
        "ay_peak": float(np.max(np.abs(ay))),
        "ay_rms": float(np.sqrt(np.mean(ay**2))),
        "jerk_peak": float(np.max(np.abs(jy))),
        "jerk_rms": float(np.sqrt(np.mean(jy**2))),
        "swr_peak": float(np.max(np.abs(swr))),
        "swr_rms": float(np.sqrt(np.mean(swr**2))),
        "sw_travel": float(np.sum(np.abs(np.diff(sw)))),
        "sw_peak": float(np.max(np.abs(sw))),
        "reversals": reversals(sw, REVERSAL_GAP_DEG),
        "clear_min": float(np.min(clear)),
        "track_err_max": float(np.max(np.abs(log["ey"][m]))),
    }


def path_metrics(road: Road, d):
    _, ay, jy = path_signals(road, d)
    m = (road.sn >= road.focus[0]) & (road.sn <= road.focus[1])
    return {
        "ay_peak": float(np.max(np.abs(ay[m]))),
        "jerk_peak": float(np.max(np.abs(jy[m]))),
        "jerk_rms": float(np.sqrt(np.mean(jy[m] ** 2))),
        "d_maxabs": float(np.max(np.abs(d[m]))),
    }


def main():
    t0 = time.time()
    roads = research_roads()
    out = {
        "meta": {
            "study": "PP-TS-013", "kind": "draft prototype (Python, not the C planner)",
            "profile": PROFILE.name, "lane_width": LANE_W, "view_m": VIEW_M, "corridor": CORRIDOR,
            "weights": {"A0": A0, "J0": J0, "D0": D0, "W_J": W_J, "W_D": W_D, "W_PK": W_PK,
                        "W_TERM": W_TERM, "CAP_SPAN": CAP_SPAN, "EXTRAP_M": EXTRAP_M},
            "free_side": FREE_SIDE, "margin": MARGIN, "reversal_gap_deg": REVERSAL_GAP_DEG,
        },
        "roads": {},
        "sweep": {},
    }
    for road in roads:
        print(f"[{road.name}] planning ...", flush=True)
        paths = {
            "B0": np.zeros_like(road.kn),
            "R-cam": plan_receding(road, CORRIDOR),
            "R-glob": plan_global(road, CORRIDOR),
        }
        rec = {"label": road.label, "v": road.v, "focus": road.focus,
               "sn": road.sn.tolist(), "kr": road.kn.tolist(), "variants": {}}
        for name, d in paths.items():
            print(f"  {name}: closed loop ...", flush=True)
            log = closed_loop(road, d)
            _, ay_p, jy_p = path_signals(road, d)
            dec = slice(None, None, 5)
            rec["variants"][name] = {
                "d": d.tolist(), "ay_path": ay_p.tolist(), "jy_path": jy_p.tolist(),
                "path": path_metrics(road, d), "cl": cl_metrics(road, log),
                "log": {k: log[k][dec].tolist() for k in ("t", "s", "ay", "sw", "ey", "dveh")},
            }
        out["roads"][road.name] = rec
        sw = {}
        for c in (0.0, 0.1, 0.2, 0.3, 0.45, 0.6):  # 0,45 m và 0,6 m vượt offset_max, chỉ dùng để đo độ nhạy.
            d = plan_receding(road, c) if c > 0 else np.zeros_like(road.kn)
            sw[str(c)] = path_metrics(road, d)
        out["sweep"][road.name] = sw
        b, r = rec["variants"]["B0"]["cl"], rec["variants"]["R-cam"]["cl"]
        print(f"  ay {b['ay_peak']:.2f}->{r['ay_peak']:.2f}  jerk {b['jerk_peak']:.2f}->{r['jerk_peak']:.2f}"
              f"  swr {b['swr_peak']:.1f}->{r['swr_peak']:.1f}  clear {b['clear_min']:.2f}->{r['clear_min']:.2f}")
    out["meta"]["runtime_s"] = round(time.time() - t0, 1)
    (HERE / "results.json").write_text(json.dumps(out))
    print(f"done in {out['meta']['runtime_s']} s")


if __name__ == "__main__":
    main()

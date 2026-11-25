"""Prototype hình học PP-TS-005 trên đường S14e, dùng dữ liệu không nhiễu để so cách dựng lại đường
từ frame cũ.
"""

import numpy as np

segs = [(0, 150, 0, 0), (150, 30, 0, 0.0012706480304955528), (180, 57.1, 0.0012706480304955528, 0.0012706480304955528),
        (237.1, 14, 0.0012706480304955528, 0), (251.1, 26, 0, -0.00267379679144385),
        (277.1, 5.1, -0.00267379679144385, -0.00267379679144385),
        (282.2, 39, -0.00267379679144385, 0), (321.2, 600, 0, 0)]
ds = 0.05
S = np.arange(0, 900, ds)
K = np.zeros_like(S)
for s0, L, k0, k1 in segs:
    m = (S >= s0) & (S < s0 + L)
    K[m] = k0 + (k1 - k0) * (S[m] - s0) / L
TH = np.concatenate([[0], np.cumsum(0.5 * (K[1:] + K[:-1]) * ds)])
X = np.concatenate([[0], np.cumsum(np.cos(0.5 * (TH[1:] + TH[:-1])) * ds)])
Y = np.concatenate([[0], np.cumsum(np.sin(0.5 * (TH[1:] + TH[:-1])) * ds)])

def pose(s):
    i = int(round(s / ds)); return X[i], Y[i], TH[i]

def to_base(px, py, ps):
    x0, y0, t0 = ps; c, s = np.cos(t0), np.sin(t0)
    dx, dy = px - x0, py - y0
    return c * dx + s * dy, -s * dx + c * dy

def frame(s, view=80.0):
    m = (S >= s - 10) & (S <= s + view + 20)
    bx, by = to_base(X[m], Y[m], pose(s))
    k = (bx >= 0) & (bx <= view)
    c3, c2, c1, c0 = np.polyfit(bx[k], by[k], 3)
    return np.array([c0, c1, c2, c3])

def cubic_kappa(c, x):
    d1 = c[1] + 2 * c[2] * x + 3 * c[3] * x * x; d2 = 2 * c[2] + 6 * c[3] * x
    return d2 / (1 + d1 * d1) ** 1.5

def truth_base(s, xs):
    m = (S >= s - 5) & (S <= s + 130)
    bx, by = to_base(X[m], Y[m], pose(s))
    return np.interp(xs, bx, by), np.interp(xs, bx, K[m])

V = 28.0
DT = 0.05
STEP = V * DT
xs_eval = np.arange(0, 30.01, 1.0)
s_list = np.arange(120, 380, STEP)

def window_weight(x, view=80.0):
    # Sai số fit cubic lớn ở hai đầu cửa sổ; dùng trọng số cao hơn ở giữa.
    u = (x - 0.5 * view) / (0.5 * view)
    return 1.0 / (1e-4 + (0.02 + 0.5 * u ** 6) ** 2)

import sys
BIAS=float(sys.argv[1]) if len(sys.argv)>1 else 0.0
res = {k: [] for k in ("V0", "T5", "V1", "V2", "V3", "V4")}
# V4 dùng y0, psi0 và độ cong theo ô 2 m với xấp xỉ góc nhỏ x ≈ s.
CELL = 2.0
cells = np.arange(-10.0, 90.0, CELL)
def basis(xq):
    sub = np.linspace(0, 1, 9)[:-1] + 1/16
    B = np.zeros((len(xq), 2 + len(cells)))
    B[:, 0] = 1.0; B[:, 1] = xq
    for i, a in enumerate(cells):
        u = a + sub * CELL
        for j, x in enumerate(xq):
            if x >= 0:
                m = (u >= 0) & (u <= x); B[j, 2 + i] = np.sum((x - u[m])) * CELL / 8
            else:
                m = (u <= 0) & (u >= x); B[j, 2 + i] = np.sum((u[m] - x)) * CELL / 8
    return B
SIG_DK = 2.0e-4      # Prior cho mức đổi độ cong theo mỗi ô 2 m, lấy thang từ clothoid S14e.
D = np.zeros((len(cells) - 1, 2 + len(cells)))
for i in range(len(cells) - 1):
    D[i, 2 + i] = -1 / SIG_DK; D[i, 3 + i] = 1 / SIG_DK
B_eval = basis(xs_eval)
k_cell0 = int(np.argmin(np.abs(cells + CELL / 2)))
kmem = {}
kmem_raw = {}
pts = []
for n, s in enumerate(s_list):
    c = frame(s)
    yt, kt = truth_base(s, xs_eval)
    y0 = np.polyval(c[::-1], xs_eval); k0 = cubic_kappa(c, xs_eval)
    res["V0"].append((s, np.max(np.abs(y0 - yt)), k0[0] - kt[0]))
    grid = np.arange(0, 80.01, 2.0)
    for x in grid:
        key = round((s + x) / 2.0)
        z = cubic_kappa(c, x)
        for mem, w in ((kmem_raw, 1.0), (kmem, window_weight(x))):
            a, ww = mem.get(key, (0.0, 0.0))
            ww *= 0.97
            mem[key] = ((a * ww + z * w) / (ww + w), ww + w)
    xk = grid; zk = np.array([kmem_raw[round((s + x) / 2.0)][0] for x in xk])
    b, a = np.polyfit(xk, zk, 1)
    c5 = np.array([c[0], c[1], a / 2, b / 6])
    res["T5"].append((s, np.max(np.abs(np.polyval(c5[::-1], xs_eval) - yt)),
                      cubic_kappa(c5, 0) - kt[0]))
    zk1 = np.array([kmem[round((s + x) / 2.0)][0] for x in xk])
    th = np.arctan(c[1]) + np.concatenate([[0], np.cumsum(0.5 * (zk1[1:] + zk1[:-1]) * 2.0)])
    yy = c[0] + np.concatenate([[0], np.cumsum(np.sin(0.5 * (th[1:] + th[:-1])) * 2.0)])
    y1 = np.interp(xs_eval, xk, yy)
    res["V1"].append((s, np.max(np.abs(y1 - yt)), zk1[0] - kt[0]))
    # V2 lưu điểm giữa cửa sổ trong tọa độ thế giới, tương đương bù ego-motion chính xác.
    xp, yp, tp = pose(s); cc, ss = np.cos(tp), np.sin(tp)
    for x in np.arange(0, 80.01, 2.0):
        y = np.polyval(c[::-1], x)
        pts.append((xp + cc * x - ss * y, yp + ss * x + cc * y, window_weight(x), n * DT))
    pts = [p for p in pts if n * DT - p[3] <= 3.0]
    P = np.array(pts)
    bx, by = to_base(P[:, 0], P[:, 1], (xp, yp, tp))
    age = n * DT - P[:, 3]
    if BIAS:
        # Mô phỏng bias yaw bằng cách xoay điểm lịch sử quanh xe một góc bias × tuổi điểm.
        a = BIAS * age; ca, sa = np.cos(a), np.sin(a)
        bx, by = ca * bx - sa * by, sa * bx + ca * by
    w = P[:, 2] * np.exp(-(n * DT - P[:, 3]) / 1.5)
    keep = bx > -20
    bx, by, w = bx[keep], by[keep], w[keep]
    yv = []; kv0 = None
    for x in xs_eval:
        g = w * np.exp(-0.5 * ((bx - x) / 15.0) ** 2)
        A = np.vstack([np.ones_like(bx), bx - x, (bx - x) ** 2]).T
        sol = np.linalg.lstsq(A * np.sqrt(g)[:, None], by * np.sqrt(g), rcond=None)[0]
        yv.append(sol[0])
        if kv0 is None:
            kv0 = 2 * sol[2] / (1 + sol[1] ** 2) ** 1.5
    res["V2"].append((s, np.max(np.abs(np.array(yv) - yt)), kv0 - kt[0]))
    g = w * np.exp(-0.5 * (bx / 15.0) ** 2)
    A = np.vstack([np.ones_like(bx), bx, bx ** 2]).T
    sol = np.linalg.lstsq(A * np.sqrt(g)[:, None], by * np.sqrt(g), rcond=None)[0]
    th = np.arctan(sol[1]) + np.concatenate([[0], np.cumsum(0.5 * (zk1[1:] + zk1[:-1]) * 2.0)])
    yy = sol[0] + np.concatenate([[0], np.cumsum(np.sin(0.5 * (th[1:] + th[:-1])) * 2.0)])
    # V4 fit bình phương tối thiểu đồng thời trên điểm đã lưu, có prior về độ trơn.
    sig_pt = 1.0 / np.sqrt(np.maximum(w, 1e-12))
    Bp = basis(bx) / sig_pt[:, None]
    sol4 = np.linalg.lstsq(np.vstack([Bp, D]), np.concatenate([by / sig_pt, np.zeros(len(D))]), rcond=None)[0]
    y4 = B_eval @ sol4
    res["V4"].append((s, np.max(np.abs(y4 - yt)), sol4[2 + k_cell0] - kt[0]))
    res["V3"].append((s, np.max(np.abs(np.interp(xs_eval, xk, yy) - yt)), zk1[0] - kt[0]))

print(f"S14e centre line, v = {V} m/s, frames {len(s_list)}, car s {s_list[0]:.0f}..{s_list[-1]:.0f} m")
print(f"{'variant':6} {'max |dy| 0-30 m':>16} {'max |dk| at car':>16} {'= a_y err':>10}   worst s")
for k, r in res.items():
    r = np.array(r); r = r[r[:, 0] >= 160]
    i = np.argmax(np.abs(r[:, 2]))
    print(f"{k:6} {r[:,1].max():16.3f} {np.abs(r[:,2]).max():16.5f} {V*V*np.abs(r[:,2]).max():10.2f}   {r[i,0]:.0f}")
print("\nselected positions: s, dk at car [1/m] for V0 / T5 / V1 / V2")
for s_sel in (200, 240, 250, 260, 280):
    i = int(np.argmin(np.abs(s_list - s_sel)))
    print(f"{s_list[i]:6.1f}", " ".join(f"{res[k][i][2]:+.5f}" for k in res), "  true k",
          f"{truth_base(s_list[i], np.array([0.0]))[1][0]:+.5f}")

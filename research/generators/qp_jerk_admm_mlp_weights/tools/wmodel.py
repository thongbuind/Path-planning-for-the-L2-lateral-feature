"""MLP 2 lớp ẩn × 32 (ReLU) chọn trọng số QP, bất biến theo gương: u(x) = c + h ⊙ (b3 + W3 (g(x̃) + g(M x̃)) / 2).

Bài toán soi gương d → −d có cùng trọng số tốt nhất, nên đầu ra phải chẵn (C1 dùng bản lẻ vì jerk đổi dấu). Ba đầu
ra trong không gian u = (ln qp_w_dev, ln qp_w_jerk, qp_a_comfort), chuẩn hóa theo tâm c và nửa dải h của lưới
(resolve.py). Chuẩn hóa đặc trưng và bộ kiểm ngoài miền dùng nguyên của luồng C (mlp/model.py). Bản C:
../src/mlpw_infer.c (cùng phép tính, gom lớp 1 theo phần chẵn và lẻ).
"""

import numpy as np

import resolve  # noqa: F401  (thêm research/generators/mlp vào sys.path)
import model as c1  # research/generators/mlp/model.py
from common import EVEN, F, H, ODD, PAIRS, mirror

O = 3
normaliser = c1.normaliser
in_domain = c1.in_domain
even_odd_weights = c1.even_odd_weights


def space() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Tâm, nửa dải của u và dải kẹp vật lý [lo, hi] (cùng dải với lưới)."""
    lo = np.array([np.log(min(resolve.W_DEV)), np.log(min(resolve.W_JERK)), min(resolve.A_COMFORT)])
    hi = np.array([np.log(max(resolve.W_DEV)), np.log(max(resolve.W_JERK)), max(resolve.A_COMFORT)])
    return 0.5 * (lo + hi), 0.5 * (hi - lo), lo, hi


def to_u(w: np.ndarray) -> np.ndarray:
    return np.stack([np.log(w[..., 0]), np.log(w[..., 1]), w[..., 2]], axis=-1)


def to_w(u: np.ndarray) -> np.ndarray:
    return np.stack([np.exp(u[..., 0]), np.exp(u[..., 1]), u[..., 2]], axis=-1)


def init(rng: np.random.Generator) -> dict:
    he = lambda fan_in, shape: rng.normal(0.0, np.sqrt(2.0 / fan_in), shape)  # noqa: E731
    return {"w1": he(F, (H, F)), "b1": np.zeros(H), "w2": he(H, (H, H)), "b2": np.zeros(H),
            "w3": rng.normal(0.0, np.sqrt(1.0 / H), (O, H)), "b3": np.zeros(O)}


def _branch(p, xn):
    z1 = xn @ p["w1"].T + p["b1"]
    h1 = np.maximum(z1, 0.0)
    z2 = h1 @ p["w2"].T + p["b2"]
    return np.maximum(z2, 0.0), (xn, z1, h1, z2)


def _forward_n(p, norm, x):
    hp, cp = _branch(p, (x - norm["mean"]) * norm["inv_std"])
    hm, cm = _branch(p, (mirror(x) - norm["mean"]) * norm["inv_std"])
    s = 0.5 * (hp + hm)
    return s @ p["w3"].T + p["b3"], (cp, cm, s)


def forward_u(p: dict, norm: dict, x: np.ndarray) -> np.ndarray:
    """u chưa kẹp (float64, tham chiếu cho bản C)."""
    c, h, _, _ = space()
    return c + h * _forward_n(p, norm, x)[0]


def weights(p: dict, norm: dict, x: np.ndarray) -> np.ndarray:
    """Trọng số vật lý đã kẹp vào dải."""
    _, _, lo, hi = space()
    return to_w(np.clip(forward_u(p, norm, x), lo, hi))


def loss_and_grad(p: dict, norm: dict, x: np.ndarray, yn: np.ndarray, l2: float):
    """MSE trên đầu ra chuẩn hóa yn = (u − c) / h, cộng l2 × tổng bình phương các ma trận trọng số."""
    out, (cp, cm, s) = _forward_n(p, norm, x)
    err = out - yn
    n = x.shape[0]
    loss = float(np.mean(np.sum(err * err, axis=1)))
    g_out = 2.0 * err / n
    grads = {"w3": g_out.T @ s, "b3": g_out.sum(axis=0)}
    g_s = g_out @ p["w3"]
    for key in ("w1", "b1", "w2", "b2"):
        grads[key] = 0.0
    for xn, z1, h1, z2 in (cp, cm):
        g_z2 = 0.5 * g_s * (z2 > 0.0)
        grads["w2"] = grads["w2"] + g_z2.T @ h1
        grads["b2"] = grads["b2"] + g_z2.sum(axis=0)
        g_z1 = (g_z2 @ p["w2"]) * (z1 > 0.0)
        grads["w1"] = grads["w1"] + g_z1.T @ xn
        grads["b1"] = grads["b1"] + g_z1.sum(axis=0)
    for key in ("w1", "w2", "w3"):
        loss += l2 * float(np.sum(p[key] ** 2))
        grads[key] = grads[key] + 2.0 * l2 * p[key]
    return loss, grads


def forward_c(a: dict, x: np.ndarray) -> np.ndarray:
    """Mô phỏng mlpw_infer.c bằng float32 từ các mảng đã xuất; trả u chưa kẹp."""
    f32 = np.float32
    xn = ((x - a["mean"].astype(f32).astype(float)).astype(f32) * a["inv_std"].astype(f32))
    xe = np.concatenate([xn[..., EVEN], np.stack([f32(0.5) * (xn[..., b] - xn[..., a_]) for a_, b in PAIRS], -1)], -1)
    xo = np.concatenate([xn[..., ODD], np.stack([f32(0.5) * (xn[..., a_] + xn[..., b]) for a_, b in PAIRS], -1)], -1)
    se = xe @ a["w_even"].astype(f32).T + a["b1"].astype(f32)
    so = xo @ a["w_odd"].astype(f32).T
    hp, hm = np.maximum(se + so, 0), np.maximum(se - so, 0)
    w2, b2 = a["w2"].astype(f32), a["b2"].astype(f32)
    s = f32(0.5) * (np.maximum(hp @ w2.T + b2, 0) + np.maximum(hm @ w2.T + b2, 0))
    out = s @ a["w3"].astype(f32).T + a["b3"].astype(f32)
    return (a["centre"].astype(f32) + a["half"].astype(f32) * out).astype(float)

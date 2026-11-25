"""MLP 2 lớp ẩn × 32 (ReLU) đối xứng gương, bằng numpy: j(x) = σ_y ⊙ (g(x̃) − g(M x̃)) / 2.

Bài toán QP đổi thành bài toán soi gương khi d → −d, κ → −κ, nên nghiệm jerk đổi dấu. Mô hình giữ đúng tính chất
này theo cấu trúc: không cần nhân đôi dữ liệu, không có lệch hệ thống trên đường thẳng ở tâm làn. Bản C:
research/generators/mlp/c/mlp_infer.c (cùng phép tính, gom lớp 1 theo phần chẵn và lẻ).
"""

import numpy as np

from common import EVEN, F, H, N, ODD, PAIRS, mirror

OOD_SIGMA = 5.0


def normaliser(x_train: np.ndarray) -> dict:
    """Chuẩn hóa đóng băng theo train, đối xứng gương: trung bình nhóm lẻ bằng 0, cặp hành lang cùng σ."""
    both = np.concatenate([x_train, mirror(x_train)])
    mean = both.mean(axis=0)
    std = both.std(axis=0)
    mean[ODD] = 0.0
    for a, b in PAIRS:
        m = 0.5 * (mean[b] - mean[a])
        mean[a], mean[b] = -m, m
        s = 0.5 * (std[a] + std[b])
        std[a] = std[b] = s
    floor = 1e-6 * np.maximum(1.0, np.abs(mean))
    constant = std <= floor
    sigma = np.maximum(std, floor)
    inv_std = np.where(constant, 0.0, 1.0 / sigma)
    return {"mean": mean, "sigma": sigma, "inv_std": inv_std, "constant": constant}


def in_domain(norm: dict, x: np.ndarray) -> np.ndarray:
    """Đúng bộ kiểm của mlp_jerk(): hữu hạn và mọi đặc trưng trong 5 σ của train."""
    dev = np.abs(x - norm["mean"])
    return np.all(np.isfinite(x), axis=-1) & np.all(dev <= OOD_SIGMA * norm["sigma"], axis=-1)


def init(rng: np.random.Generator) -> dict:
    he = lambda fan_in, shape: rng.normal(0.0, np.sqrt(2.0 / fan_in), shape)  # noqa: E731
    return {"w1": he(F, (H, F)), "b1": np.zeros(H), "w2": he(H, (H, H)), "b2": np.zeros(H),
            "w3": rng.normal(0.0, np.sqrt(1.0 / H), (N, H))}


def _branch(p: dict, xn: np.ndarray):
    z1 = xn @ p["w1"].T + p["b1"]
    h1 = np.maximum(z1, 0.0)
    z2 = h1 @ p["w2"].T + p["b2"]
    h2 = np.maximum(z2, 0.0)
    return h2, (xn, z1, h1, z2)


def forward(p: dict, norm: dict, x: np.ndarray, out_scale: np.ndarray) -> np.ndarray:
    """Jerk [m/s³] cho đặc trưng thô x (float64, tham chiếu cho bản C)."""
    return out_scale * _forward_n(p, norm, x)[0]


def _forward_n(p, norm, x):
    xp = (x - norm["mean"]) * norm["inv_std"]
    xm = (mirror(x) - norm["mean"]) * norm["inv_std"]
    hp, cp = _branch(p, xp)
    hm, cm = _branch(p, xm)
    diff = 0.5 * (hp - hm)
    return diff @ p["w3"].T, (cp, cm, diff)


def loss_and_grad(p: dict, norm: dict, x: np.ndarray, yn: np.ndarray, weights: np.ndarray, l2: float):
    """MSE có trọng số trên nhãn chuẩn hóa yn = y / σ_y. weights: [N] trọng số từng bước."""
    out, (cp, cm, diff) = _forward_n(p, norm, x)
    err = out - yn
    n = x.shape[0]
    loss = float(np.mean(np.sum(weights * err * err, axis=1)))
    g_out = 2.0 * weights * err / n
    grads = {"w3": g_out.T @ diff}
    g_diff = g_out @ p["w3"]
    for key in ("w1", "b1", "w2", "b2"):
        grads[key] = 0.0
    for sign, (xn, z1, h1, z2) in ((0.5, cp), (-0.5, cm)):
        g_z2 = sign * g_diff * (z2 > 0.0)
        grads["w2"] = grads["w2"] + g_z2.T @ h1
        grads["b2"] = grads["b2"] + g_z2.sum(axis=0)
        g_z1 = (g_z2 @ p["w2"]) * (z1 > 0.0)
        grads["w1"] = grads["w1"] + g_z1.T @ xn
        grads["b1"] = grads["b1"] + g_z1.sum(axis=0)
    for key in ("w1", "w2", "w3"):
        loss += l2 * float(np.sum(p[key] ** 2))
        grads[key] = grads[key] + 2.0 * l2 * p[key]
    return loss, grads


def even_odd_weights(p: dict) -> tuple[np.ndarray, np.ndarray]:
    """Lớp 1 viết lại theo phần chẵn và lẻ như mlp_infer.c: cặp (a, b) có e = (x̃b − x̃a)/2, o = (x̃a + x̃b)/2."""
    w1 = p["w1"]
    we = [w1[:, i] for i in EVEN] + [w1[:, b] - w1[:, a] for a, b in PAIRS]
    wo = [w1[:, i] for i in ODD] + [w1[:, a] + w1[:, b] for a, b in PAIRS]
    return np.stack(we, axis=1), np.stack(wo, axis=1)


def forward_c(model: dict, x: np.ndarray) -> np.ndarray:
    """Mô phỏng mlp_infer.c bằng float32 từ các mảng đã xuất (để kiểm bản xuất, không dùng khi huấn luyện)."""
    f32 = np.float32
    xn = ((x - model["mean"].astype(f32).astype(float)).astype(f32) * model["inv_std"].astype(f32))
    xe = np.concatenate([xn[..., EVEN], np.stack([f32(0.5) * (xn[..., b] - xn[..., a]) for a, b in PAIRS], -1)], -1)
    xo = np.concatenate([xn[..., ODD], np.stack([f32(0.5) * (xn[..., a] + xn[..., b]) for a, b in PAIRS], -1)], -1)
    se = xe @ model["w_even"].astype(f32).T + model["b1"].astype(f32)
    so = xo @ model["w_odd"].astype(f32).T
    hp, hm = np.maximum(se + so, 0), np.maximum(se - so, 0)
    w2, b2 = model["w2"].astype(f32), model["b2"].astype(f32)
    diff = f32(0.5) * (np.maximum(hp @ w2.T + b2, 0) - np.maximum(hm @ w2.T + b2, 0))
    return (diff @ model["w3"].astype(f32).T) * model["out_scale"].astype(f32)

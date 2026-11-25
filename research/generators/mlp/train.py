"""Huấn luyện MLP luồng C bằng numpy (Adam, ≤ 20 epoch), chuẩn hóa đóng băng theo train, chọn epoch theo
validation. Báo loss train/validation/ngoài miền và sai số theo đơn vị vật lý (jerk, lệch d trên 0–1 s).
"""

import argparse
import json

import numpy as np

import common
import model as mlp
from common import N, OUT

CONFIG = {"hidden": [common.H, common.H], "activation": "relu", "mirror_symmetric": True, "epochs": 20,
          "batch": 32, "lr": 1e-2, "lr_final": 1e-4, "adam": [0.9, 0.999, 1e-8], "l2": 1e-5, "seed": 100,
          "loss": "MSE trên jerk chuẩn hóa theo σ của nhãn", "step_weights": "early",
          "train_in_domain_only": True, "select": "epoch có loss validation (phần trong miền) nhỏ nhất"}
# Cấu hình trên chọn trong 8 cấu hình (notes.md) theo loss validation trong miền, trọng số đều 30 bước.


def step_weights(kind: str) -> np.ndarray:
    k = np.arange(N)
    if kind == "uniform":
        return np.ones(N)
    if kind == "early":  # Các bước đầu quyết định lệch d trên 0–1 s; tổng trọng số vẫn là N.
        w = 1.0 + 4.0 * np.exp(-k / 5.0)
        return w * N / w.sum()
    raise ValueError(kind)


def load(path=OUT / "dataset.npz") -> dict:
    with np.load(path) as d:
        return {k: d[k] for k in d.files}


def out_scale_of(y: np.ndarray) -> np.ndarray:
    """σ nhãn đối xứng gương (trung bình 0): căn của trung bình y²; sàn 1e-3 m/s³."""
    return np.maximum(np.sqrt(np.mean(y.astype(float) ** 2, axis=0)), 1e-3)


def metrics(params, norm, scale, x, y, start, drive=None) -> dict:
    if len(x) == 0:
        return {"n": 0}
    pred = mlp.forward(params, norm, x, scale)
    inside = mlp.in_domain(norm, x)
    dn = (pred - y) / scale
    d_err = np.abs(common.integrate(start, pred) - common.integrate(start, y))
    win = d_err[:, :10].max(axis=1)  # t = 0,1 … 1,0 s
    out = {"n": int(len(x)), "loss": float(np.mean(np.sum(dn * dn, axis=1))),
           "loss_in_domain": float(np.mean(np.sum(dn[inside] ** 2, axis=1))) if inside.any() else None,
           "in_domain_share": float(inside.mean()),
           "jerk_rmse": float(np.sqrt(np.mean((pred - y) ** 2))),
           "d_err_0_1s_p50": float(np.percentile(win, 50)), "d_err_0_1s_p99": float(np.percentile(win, 99)),
           "d_err_0_1s_max": float(win.max()), "d_err_3s_p50": float(np.percentile(d_err[:, -1], 50)),
           "label_jerk_rms": float(np.sqrt(np.mean(y ** 2)))}
    if drive is not None:
        dd = np.abs(common.integrate(start, drive) - common.integrate(start, y))[:, :10].max(axis=1)
        out["drive150_d_err_0_1s_p50"] = float(np.percentile(dd, 50))
        out["drive150_d_err_0_1s_p99"] = float(np.percentile(dd, 99))
    zero = np.abs(common.integrate(start, np.zeros_like(y)) - common.integrate(start, y))[:, :10].max(axis=1)
    out["zero_jerk_d_err_0_1s_p50"] = float(np.percentile(zero, 50))
    # Chỉ các cửa sổ trong miền: đây là nơi MLP thật sự được dùng (ngoài miền thì generator dự phòng).
    if inside.any():
        out["in_domain"] = {"jerk_rmse": float(np.sqrt(np.mean((pred[inside] - y[inside]) ** 2))),
                            "d_err_0_1s_p50": float(np.percentile(win[inside], 50)),
                            "d_err_0_1s_p99": float(np.percentile(win[inside], 99)),
                            "d_err_0_1s_max": float(win[inside].max()),
                            "zero_jerk_d_err_0_1s_p50": float(np.percentile(zero[inside], 50)),
                            "zero_jerk_d_err_0_1s_p99": float(np.percentile(zero[inside], 99))}
    return out


def train(data: dict, config: dict = CONFIG, log=print) -> dict:
    split = data["split"]
    tr, va, od = (split == "train"), (split == "validation"), (split == "ood")
    x = data["x"].astype(float)
    y = data["y"].astype(float)
    start = data["start"].astype(float)
    norm = mlp.normaliser(x[tr])
    scale = out_scale_of(y[tr])
    yn = y / scale
    rng = np.random.default_rng(config["seed"])
    params = mlp.init(rng)
    m = {k: np.zeros_like(v) for k, v in params.items()}
    v = {k: np.zeros_like(v) for k, v in params.items()}
    b1, b2, eps = config["adam"]
    weights = step_weights(config["step_weights"])
    # MLP chỉ được dùng trong miền (bộ kiểm 5 σ): tùy chọn chỉ học trên các cửa sổ đó.
    fit = (tr & mlp.in_domain(norm, x)) if config["train_in_domain_only"] else tr
    sel = va & mlp.in_domain(norm, x)
    idx = np.flatnonzero(fit)
    steps_per_epoch = int(np.ceil(len(idx) / config["batch"]))
    total = steps_per_epoch * config["epochs"]
    step = 0
    best, history = None, []
    for epoch in range(config["epochs"]):
        order = rng.permutation(idx)
        for s in range(steps_per_epoch):
            batch = order[s * config["batch"]:(s + 1) * config["batch"]]
            lr = config["lr_final"] + 0.5 * (config["lr"] - config["lr_final"]) * (1 + np.cos(np.pi * step / total))
            _, grads = mlp.loss_and_grad(params, norm, x[batch], yn[batch], weights, config["l2"])
            step += 1
            for k in params:
                m[k] = b1 * m[k] + (1 - b1) * grads[k]
                v[k] = b2 * v[k] + (1 - b2) * grads[k] ** 2
                mh = m[k] / (1 - b1 ** step)
                vh = v[k] / (1 - b2 ** step)
                params[k] = params[k] - lr * mh / (np.sqrt(vh) + eps)
        lt = float(mlp.loss_and_grad(params, norm, x[fit], yn[fit], weights, 0.0)[0])
        lv = float(mlp.loss_and_grad(params, norm, x[sel], yn[sel], weights, 0.0)[0])
        history.append({"epoch": epoch + 1, "train": lt, "validation": lv})
        log(f"epoch {epoch + 1:2d}: train {lt:.4f} validation {lv:.4f}")
        if best is None or lv < best[0]:
            best = (lv, epoch + 1, {k: p.copy() for k, p in params.items()})
    params = best[2]
    result = {"config": config, "history": history, "best_epoch": best[1], "params": params, "norm": norm,
              "out_scale": scale}
    result["metrics"] = {name: metrics(params, norm, scale, x[mk], y[mk], start[mk], data["drive"][mk].astype(float))
                         for name, mk in (("train", tr), ("validation", va), ("ood", od))}
    # Ngoài miền tách theo loại: tốc độ 110–130 km/h hay VP-3/5.
    fast = od & (data["speed"] > 105 / 3.6)
    result["metrics"]["ood_speed"] = metrics(params, norm, scale, x[fast], y[fast], start[fast])
    result["metrics"]["ood_profile"] = metrics(params, norm, scale, x[od & ~fast], y[od & ~fast], start[od & ~fast])
    return result


def save(result: dict, path) -> None:
    flat = {f"p_{k}": v for k, v in result["params"].items()}
    flat.update({f"n_{k}": v for k, v in result["norm"].items()})
    flat["out_scale"] = result["out_scale"]
    np.savez(path, **flat, meta=json.dumps({k: result[k] for k in ("config", "history", "best_epoch", "metrics")}))


def load_model(path) -> dict:
    with np.load(path) as d:
        return {"params": {k[2:]: d[k] for k in d.files if k.startswith("p_")},
                "norm": {k[2:]: d[k] for k in d.files if k.startswith("n_")},
                "out_scale": d["out_scale"], "meta": json.loads(str(d["meta"]))}


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the stream-C MLP (numpy)")
    parser.add_argument("--out", default=str(OUT / "model.npz"))
    parser.add_argument("--set", action="append", default=[], help="key=value (JSON) ghi đè CONFIG")
    args = parser.parse_args()
    config = dict(CONFIG)
    for item in args.set:
        key, value = item.split("=", 1)
        config[key] = json.loads(value)
    import slots
    with slots.hold(1, "mlp train"):
        result = train(load(), config)
    save(result, args.out)
    metrics_file = OUT / (str(args.out).rsplit("/", 1)[-1].replace(".npz", "") + "_metrics.json")
    if args.out == str(OUT / "model.npz"):
        metrics_file = OUT / "train_metrics.json"
    metrics_file.write_text(json.dumps({k: result[k] for k in ("config", "history", "best_epoch",
                                                                                "metrics")}, indent=1), encoding="utf-8")
    print(json.dumps(result["metrics"], indent=1))


if __name__ == "__main__":
    main()

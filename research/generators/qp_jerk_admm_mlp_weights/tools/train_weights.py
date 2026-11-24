"""Huấn luyện MLP chọn trọng số (numpy, Adam), một model cho mỗi mức điều chuẩn l2 của lưới PP-TS-031
(`mlpw_regularisation`). Cấu hình còn lại như luồng C (mlp/train.py CONFIG). Chọn epoch theo loss validation trong miền.

Ngoài loss, chấm lại trên validation và ngoài miền bằng chính hàm mục tiêu của nhãn: giải QP với trọng số MLP dự
đoán (đã kẹp) và so S với trọng số mặc định và với nhãn của lưới (giới hạn trên của cách i).

    python3 train_weights.py            # ba mức, ghi build/lab/mlp_weights/model_r<mức>.npz, train_metrics.json
"""

import argparse
import json
import sys

import numpy as np

import grid_labels
import resolve
import wmodel
from resolve import OUT, common

LEVELS = (1.0e-4, 1.0e-3, 1.0e-2)  # plan.yaml mlpw_regularisation; tâm 1e-3 là mặc định
CONFIG = {"hidden": [common.H, common.H], "activation": "relu", "mirror_even": True, "epochs": 20, "batch": 32,
          "lr": 1e-2, "lr_final": 1e-4, "adam": [0.9, 0.999, 1e-8], "seed": 100,
          "loss": "MSE trên u chuẩn hóa theo tâm và nửa dải của lưới", "train_in_domain_only": True,
          "select": "epoch có loss validation (phần trong miền) nhỏ nhất"}


def tag(level: float) -> str:
    return f"{level:.0e}".replace("e-0", "e-")


def dataset() -> dict:
    data = grid_labels.load()
    with np.load(OUT / "labels.npz") as lab:
        assert str(lab["dataset_sha256"]) == common.sha256_file(grid_labels.DATASET)
        assert np.array_equal(lab["call"], data["call"]) and np.array_equal(lab["scenario"], data["scenario"])
        data["label"] = lab["label"]
        data["label_w"] = lab["weights"]
        data["scores"] = lab["scores"]
    return data


def train(data: dict, l2: float, config: dict = CONFIG, log=print) -> dict:
    split, has = data["split"], data["label"] >= 0
    x = data["x"].astype(float)
    norm = wmodel.normaliser(x[split == "train"])
    c, h, _, _ = wmodel.space()
    yn = np.where(has[:, None], (wmodel.to_u(np.nan_to_num(data["label_w"], nan=1.0)) - c) / h, 0.0)
    fit = (split == "train") & has & wmodel.in_domain(norm, x)
    sel = (split == "validation") & has & wmodel.in_domain(norm, x)
    rng = np.random.default_rng(config["seed"])
    params = wmodel.init(rng)
    m = {k: np.zeros_like(v) for k, v in params.items()}
    v = {k: np.zeros_like(v) for k, v in params.items()}
    b1, b2, eps = config["adam"]
    idx = np.flatnonzero(fit)
    per_epoch = int(np.ceil(len(idx) / config["batch"]))
    total, step, best, history = per_epoch * config["epochs"], 0, None, []
    for epoch in range(config["epochs"]):
        order = rng.permutation(idx)
        for s in range(per_epoch):
            batch = order[s * config["batch"]:(s + 1) * config["batch"]]
            lr = config["lr_final"] + 0.5 * (config["lr"] - config["lr_final"]) * (1 + np.cos(np.pi * step / total))
            _, grads = wmodel.loss_and_grad(params, norm, x[batch], yn[batch], l2)
            step += 1
            for k in params:
                m[k] = b1 * m[k] + (1 - b1) * grads[k]
                v[k] = b2 * v[k] + (1 - b2) * grads[k] ** 2
                params[k] = params[k] - lr * (m[k] / (1 - b1 ** step)) / (np.sqrt(v[k] / (1 - b2 ** step)) + eps)
        lt = wmodel.loss_and_grad(params, norm, x[fit], yn[fit], 0.0)[0]
        lv = wmodel.loss_and_grad(params, norm, x[sel], yn[sel], 0.0)[0]
        history.append({"epoch": epoch + 1, "train": lt, "validation": lv})
        log(f"l2 {l2:g} epoch {epoch + 1:2d}: train {lt:.4f} validation {lv:.4f}")
        if best is None or lv < best[0]:
            best = (lv, epoch + 1, {k: p.copy() for k, p in params.items()})
    # Loss của mô hình hằng (trung bình nhãn train): mốc để thấy MLP học được gì từ đặc trưng.
    const = yn[fit].mean(axis=0)
    const_loss = float(np.mean(np.sum((yn[sel] - const) ** 2, axis=1)))
    return {"l2": l2, "config": {**config, "l2": l2}, "history": history, "best_epoch": best[1], "params": best[2],
            "norm": norm, "constant_validation_loss": const_loss}


def objective_check(solver, data: dict, result: dict, mask: np.ndarray) -> dict:
    """S trung bình với trọng số MLP (kẹp), mặc định và nhãn trên các cửa sổ có nhãn và trong miền của mask."""
    x = data["x"].astype(float)
    inside = wmodel.in_domain(result["norm"], x)
    rows = np.flatnonzero(mask & (data["label"] >= 0) & inside)
    w = wmodel.weights(result["params"], result["norm"], x[rows])
    dtb = resolve.ref_dtarget(data["scenario"][rows], data["call"][rows])
    s_mlp, failed = [], 0
    for k, i in enumerate(rows):
        jerk, stats = solver.solve(data["problem"][i], data["flags"][i, 4] > 0.5, dtb[k], w[k])
        if jerk is None or not resolve.accepted(stats):
            failed += 1
            s_mlp.append(np.nan)
            continue
        s_mlp.append(float(resolve.score(resolve.terms(data["problem"][i], jerk))))
    s_mlp = np.array(s_mlp)
    s_def = data["scores"][rows, resolve.DEFAULT_INDEX]
    s_lab = data["scores"][rows, data["label"][rows]]
    ok = np.isfinite(s_mlp)
    gain = s_def[ok] - s_mlp[ok]
    return {"windows": int(len(rows)), "in_domain_share": float(inside[mask].mean()), "solve_failed": int(failed),
            "S_gain_vs_default_mean": float(gain.mean()), "S_gain_label_vs_default_mean": float((s_def - s_lab).mean()),
            "share_better_by_1": float(np.mean(gain >= 1.0)), "share_worse_by_1": float(np.mean(gain <= -1.0)),
            "worst_gain": float(gain.min()),
            "weights_p05_p50_p95": np.percentile(w, [5, 50, 95], axis=0).round(4).tolist()}


def save(result: dict, path) -> None:
    flat = {f"p_{k}": v for k, v in result["params"].items()}
    flat.update({f"n_{k}": v for k, v in result["norm"].items()})
    meta = {k: result[k] for k in ("l2", "config", "history", "best_epoch", "constant_validation_loss", "metrics")}
    np.savez(path, **flat, meta=json.dumps(meta))


def load_model(path) -> dict:
    with np.load(path) as d:
        return {"params": {k[2:]: d[k] for k in d.files if k.startswith("p_")},
                "norm": {k[2:]: d[k] for k in d.files if k.startswith("n_")}, "meta": json.loads(str(d["meta"]))}


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the weight-choosing MLP at the three l2 levels")
    parser.parse_args()
    sys.path.insert(0, str(common.LAB / "bench"))
    import slots
    data = dataset()
    solver = resolve.Solver()
    summary = {}
    with slots.hold(1, "mlp_weights train"):
        for level in LEVELS:
            result = train(data, level)
            result["metrics"] = {name: objective_check(solver, data, result, data["split"] == name)
                                 for name in ("validation", "ood")}
            save(result, OUT / f"model_r{tag(level)}.npz")
            summary[tag(level)] = {k: result[k] for k in ("best_epoch", "constant_validation_loss", "metrics")}
            summary[tag(level)]["validation_loss"] = result["history"][result["best_epoch"] - 1]["validation"]
            print(json.dumps(summary[tag(level)], indent=1), flush=True)
    (OUT / "train_metrics.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()

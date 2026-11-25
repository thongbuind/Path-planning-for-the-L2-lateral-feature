"""Xuất ba model (ba mức mlpw_regularisation) ra C: ../model/weights.h (mảng const float, không sửa tay) và dữ liệu kiểm
L0 ../tests/mlpw_fixture.h. Kiểm bản float32 kiểu C so với numpy float64 trên validation trước khi ghi.

    python3 export_weights.py
"""

import math

import numpy as np

import grid_labels
import train_weights
import wmodel
from resolve import GEN, OUT, common

# Dùng nguyên bộ định dạng hằng của luồng C.
import export as c1_export  # research/generators/mlp/export.py

_floats, _doubles = c1_export._floats, c1_export._doubles


def arrays(m: dict) -> dict:
    we, wo = wmodel.even_odd_weights(m["params"])
    c, h, _, _ = wmodel.space()
    n, p = m["norm"], m["params"]
    return {"mean": n["mean"], "sigma": n["sigma"], "inv_std": n["inv_std"], "w_even": we, "w_odd": wo, "b1": p["b1"],
            "w2": p["w2"], "b2": p["b2"], "w3": p["w3"], "b3": p["b3"], "centre": c, "half": h}


def weights_header(models: list, hashes: list, data_hash: str, label_hash: str) -> str:
    parts = ["/* Sinh bởi research/generators/qp_jerk_admm_mlp_weights/tools/export_weights.py, không sửa tay. Dataset "
             f"sha256 {data_hash[:16]}, nhãn labels.npz sha256 {label_hash[:16]} (notes.md, mục Data card). */\n",
             "#ifndef LAB_MLPW_WEIGHTS_H\n#define LAB_MLPW_WEIGHTS_H\n\n#include \"mlpw_infer.h\"\n\n",
             f"#define MLPW_MODEL_COUNT ({len(models)}U)\n\n"]
    names = []
    for (level, m), digest in zip(models, hashes):
        t = train_weights.tag(level).replace("-", "m")
        parts.append(f"/* l2 = {level:g}: model_r{train_weights.tag(level)}.npz sha256 {digest[:16]}, epoch "
                     f"{m['meta']['best_epoch']}. */\n")
        for key, values in arrays(m).items():
            parts.append(_floats(f"mlpw_{t}_{key}", values))
        keys = ", ".join(f"mlpw_{t}_{k}" for k in arrays(m))
        parts.append(f"static const mlpw_model_t MLPW_MODEL_{t.upper()} = {{\n    {keys},\n}};\n\n")
        names.append(f"&MLPW_MODEL_{t.upper()}")
    levels = ", ".join(f"{math.log10(level):.1f}" for level, _ in models)
    parts.append(f"/* log10 của mlpw_regularisation ứng với từng model. */\nstatic const double mlpw_levels[MLPW_MODEL_COUNT] "
                 f"= {{{levels}}};\nstatic const mlpw_model_t *const mlpw_models[MLPW_MODEL_COUNT] = {{{', '.join(names)}}};\n"
                 "\n#endif\n")
    return "".join(parts)


def fixture_header(models: list, data: dict) -> str:
    """Ba bài toán validation trong miền của model giữa (cua, không có path cũ, bất kỳ); vector đặc trưng gồm ba vector
    đó và bản soi gương của vector đầu; u của numpy (float64, chưa kẹp) cho từng model; một vector ngoài miền."""
    centre = models[len(models) // 2][1]
    va = np.flatnonzero(data["split"] == "validation")
    va = va[wmodel.in_domain(centre["norm"], data["x"][va].astype(float))]
    curve = va[np.argmax(np.abs(data["x"][va, 13]))]
    no_old = va[np.flatnonzero(data["x"][va, 6] == 0.0)[0]] if np.any(data["x"][va, 6] == 0.0) else va[1]
    pick = [int(curve), int(no_old), int(va[len(va) // 2])]
    problems = data["problem"][pick]
    feats = common.features(common.unpack_problem(problems))
    x = np.concatenate([feats, common.mirror(feats[:1])])
    u = np.stack([wmodel.forward_u(m["params"], m["norm"], x) for _, m in models])
    ood = feats[2].copy()
    ood[9] = centre["norm"]["mean"][9] + 6.0 * centre["norm"]["sigma"][9]
    return "".join([
        "/* Sinh bởi tools/export_weights.py, không sửa tay: dữ liệu kiểm L0 của đặc trưng và suy luận. */\n",
        "#ifndef LAB_MLPW_FIXTURE_H\n#define LAB_MLPW_FIXTURE_H\n\n",
        f"#define FIX_PROBLEMS ({len(pick)}U)\n#define FIX_VECTORS ({len(x)}U)\n#define FIX_MODELS ({len(models)}U)\n",
        f"#define FIX_PROBLEM_SIZE ({common.PROBLEM_SIZE}U)\n\n",
        "/* Bài toán theo bố cục TR_PROBLEM của teacher; đặc trưng của common.features (float64). */\n",
        _doubles("fix_problem", problems), _doubles("fix_features", feats),
        "/* Vector đặc trưng (ba vector trên, rồi bản soi gương của vector đầu); u[model][vector][3] của wmodel.forward_u. */\n",
        _doubles("fix_x", x), _doubles("fix_u", u),
        "/* Vector ngoài miền: vector thứ ba với v tại k = 0 lệch 6 σ (model giữa). */\n", _doubles("fix_ood", ood),
        "\n#endif\n"])


def main() -> None:
    data = grid_labels.load()
    models, hashes = [], []
    for level in train_weights.LEVELS:
        path = OUT / f"model_r{train_weights.tag(level)}.npz"
        models.append((level, train_weights.load_model(path)))
        hashes.append(common.sha256_file(path))
    x = data["x"][data["split"] == "validation"].astype(float)
    for level, m in models:
        gap = np.abs(wmodel.forward_c(arrays(m), x) - wmodel.forward_u(m["params"], m["norm"], x)).max()
        print(f"export check l2 {level:g}: max |float32 C-style − float64| = {gap:.2e} (u)")
        assert gap < 1e-4
    (GEN / "model").mkdir(exist_ok=True)
    (GEN / "model" / "weights.h").write_text(
        weights_header(models, hashes, common.sha256_file(grid_labels.DATASET), common.sha256_file(OUT / "labels.npz")),
        encoding="utf-8")
    (GEN / "tests" / "mlpw_fixture.h").write_text(fixture_header(models, data), encoding="utf-8")
    print(f"wrote {GEN / 'model' / 'weights.h'} and {GEN / 'tests' / 'mlpw_fixture.h'}")


if __name__ == "__main__":
    main()

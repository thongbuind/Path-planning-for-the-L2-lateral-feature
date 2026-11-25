"""Xuất model đã huấn luyện ra C: <generator>/model/weights.h (mảng const float) và dữ liệu kiểm L0
<generator>/tests/mlp_fixture.h (bài toán và đặc trưng tham chiếu của Python, vector đặc trưng và jerk của numpy).
"""

import argparse
from pathlib import Path

import numpy as np

import common
import model as mlp
import train
from common import F, N, OUT

GENERATORS = ("qp_jerk_admm_mlp_warmstart", "mlp_jerk_direct")


def _c_float(v: float) -> str:
    """Hằng float C: 9 chữ số khôi phục đúng float32; luôn có dấu chấm hoặc mũ (``0F`` không hợp lệ)."""
    s = f"{v:.9g}"
    return (s if ("." in s or "e" in s) else s + ".0") + "F"


def _floats(name: str, values, per_line: int = 6) -> str:
    flat = np.asarray(values, dtype=np.float32).ravel()
    body = ",\n".join("    " + ", ".join(_c_float(float(v)) for v in flat[i:i + per_line])
                      for i in range(0, len(flat), per_line))
    return f"static const float {name}[{len(flat)}] = {{\n{body}\n}};\n"


def _doubles(name: str, values, per_line: int = 4) -> str:
    flat = np.asarray(values, dtype=np.float64).ravel()
    body = ",\n".join("    " + ", ".join(f"{float(v):.17g}" for v in flat[i:i + per_line])
                      for i in range(0, len(flat), per_line))
    return f"static const double {name}[{len(flat)}] = {{\n{body}\n}};\n"


def arrays(m: dict) -> dict:
    we, wo = mlp.even_odd_weights(m["params"])
    norm = m["norm"]
    return {"mean": norm["mean"], "sigma": norm["sigma"], "inv_std": norm["inv_std"], "w_even": we, "w_odd": wo,
            "b1": m["params"]["b1"], "w2": m["params"]["w2"], "b2": m["params"]["b2"], "w3": m["params"]["w3"],
            "out_scale": m["out_scale"]}


def weights_header(m: dict, model_hash: str, data_hash: str, model_name: str = "model.npz") -> str:
    a = arrays(m)
    parts = [f"/* Sinh bởi research/generators/mlp/export.py, không sửa tay. Model build/lab/mlp/{model_name} sha256 "
             f"{model_hash[:16]}, dataset sha256 {data_hash[:16]} (data_card.md). */\n",
             "#ifndef LAB_MLP_WEIGHTS_H\n#define LAB_MLP_WEIGHTS_H\n\n#include \"mlp_infer.h\"\n\n"]
    for key, values in a.items():
        parts.append(_floats(f"mlp_{key}", values))
    parts.append("\nstatic const mlp_model_t MLP_MODEL = {\n    mlp_mean, mlp_sigma, mlp_inv_std, mlp_w_even, mlp_w_odd, "
                 "mlp_b1, mlp_w2, mlp_b2, mlp_w3, mlp_out_scale,\n};\n\n#endif\n")
    return "".join(parts)


def fixture_header(m: dict, data: dict) -> str:
    """Ba bài toán validation (một ca cua, một ca không có path cũ, một ca bất kỳ) và các vector đặc trưng:
    ba vector đó, bản soi gương của vector đầu, và một vector ngoài miền."""
    va = np.flatnonzero(data["split"] == "validation")
    inside = mlp.in_domain(m["norm"], data["x"][va].astype(float))
    va = va[inside]
    curve = va[np.argmax(np.abs(data["x"][va, 13]))]
    no_old = va[np.flatnonzero(data["x"][va, 6] == 0.0)[0]] if np.any(data["x"][va, 6] == 0.0) else va[1]
    pick = [int(curve), int(no_old), int(va[len(va) // 2])]
    problems = data["problem"][pick]
    feats = common.features(common.unpack_problem(problems))
    x = np.concatenate([feats, common.mirror(feats[:1])])
    jerk = mlp.forward(m["params"], m["norm"], x, m["out_scale"])
    ood = feats[2].copy()
    ood[9] = m["norm"]["mean"][9] + 6.0 * m["norm"]["sigma"][9]  # v tại k = 0 lệch 6 σ.
    parts = ["/* Sinh bởi research/generators/mlp/export.py, không sửa tay: dữ liệu kiểm L0 của đặc trưng và suy luận. */\n",
             "#ifndef LAB_MLP_FIXTURE_H\n#define LAB_MLP_FIXTURE_H\n\n",
             f"#define FIX_PROBLEMS ({len(pick)}U)\n#define FIX_VECTORS ({len(x)}U)\n",
             f"#define FIX_PROBLEM_SIZE ({common.PROBLEM_SIZE}U)\n\n",
             "/* Bài toán theo bố cục TR_PROBLEM của teacher; đặc trưng tính bằng common.features (float64). */\n",
             _doubles("fix_problem", problems), _doubles("fix_features", feats),
             "/* Vector đặc trưng (ba vector trên, rồi bản soi gương của vector đầu) và jerk của model.forward (float64). */\n",
             _doubles("fix_x", x), _doubles("fix_jerk", jerk),
             "/* Vector ngoài miền: vector thứ ba với v tại k = 0 lệch 6 σ. */\n", _doubles("fix_ood", ood),
             "\n#endif\n"]
    return "".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the trained MLP to C headers")
    parser.add_argument("--model", default=str(OUT / "model.npz"))
    parser.add_argument("--dataset", default=str(OUT / "dataset.npz"), help="Dataset the model was trained on")
    parser.add_argument("--generators", nargs="*", default=list(GENERATORS))
    args = parser.parse_args()
    m = train.load_model(args.model)
    data = train.load(args.dataset)
    model_hash = common.sha256_file(args.model)
    data_hash = common.sha256_file(args.dataset)
    # Bản xuất float32 phải khớp numpy float64 trên validation.
    va = (data["split"] == "validation")
    x = data["x"][va].astype(float)
    ref = mlp.forward(m["params"], m["norm"], x, m["out_scale"])
    got = mlp.forward_c(arrays(m), x)
    print(f"export check: max |float32 C-style − float64| = {np.abs(got - ref).max():.2e} m/s³")
    for gen in args.generators:
        folder = common.LAB / gen
        (folder / "model").mkdir(exist_ok=True)
        (folder / "model" / "weights.h").write_text(weights_header(m, model_hash, data_hash, str(Path(args.model).resolve().relative_to(OUT))), encoding="utf-8")
        (folder / "tests" / "mlp_fixture.h").write_text(fixture_header(m, data), encoding="utf-8")
        print(f"wrote {folder / 'model' / 'weights.h'}")
    assert F == 28 and N == 30


if __name__ == "__main__":
    main()

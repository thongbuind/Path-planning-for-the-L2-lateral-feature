"""Phần dùng chung của pipeline MLP luồng C (PP-TS-031): đường dẫn, bố cục bản ghi của teacher, đặc trưng
tham chiếu bằng numpy và phép soi gương. Bố cục phải khớp research/generators/qp_jerk_admm_teacher/src/
qp_jerk_admm_teacher.h; đặc trưng phải khớp research/generators/mlp/c/mlp_features.c.
"""

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LAB = ROOT / "research" / "generators"
OUT = ROOT / "build" / "lab" / "mlp"
for p in (str(ROOT), str(LAB / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

TEACHER = "qp_jerk_admm_teacher"
N = 30  # PP_QP_N
DT = 0.1
F = 28  # MLP_FEATURES
H = 32  # MLP_HIDDEN
LAYOUT = 31001.0

# Chỉ số bản ghi (qp_jerk_admm_teacher.h).
TR = dict(LAYOUT=0, SIZE=1, COUNT=2, LABEL_OK=3, DRIVE_OK=4, PRIMAL=5, DUAL=6, VIOLATION=7, VIOL_AY=8,
          VIOL_JERK=9, SLACK=10, FROM_OLD=11, RECENTERING=12, FOLLOW=13, FROM_CAR=14, SHIFT_S=15, REF_WARM=16,
          DRIVE_WARM=17, REF_DTARGET=18, DRIVE_ITERS=19)
TR_FEATURES = 20
TR_LABEL = TR_FEATURES + F
TR_DRIVE = TR_LABEL + N
TR_PROBLEM = TR_DRIVE + N
PROBLEM_SIZE = 5 + 7 * N + 2
TR_DOUBLES = TR_PROBLEM + PROBLEM_SIZE

FEATURE_NAMES = (["d0", "d0_dot", "d0_ddot", "d_target", "d_min0", "d_max0", "old_share", "old_first",
                  "old_last"] + [f"v_{k}" for k in (0, 9, 19, 29)] + [f"v2k_{k}" for k in (0, 9, 19, 29)]
                 + [f"v3dk_{k}" for k in (0, 9, 19, 29)]
                 + ["d_min9", "d_max9", "d_min19", "d_max19", "d_min29", "d_max29", "ay_limit"])
EVEN = [6, 9, 10, 11, 12, 27]
ODD = [0, 1, 2, 3, 7, 8, 13, 14, 15, 16, 17, 18, 19, 20]
PAIRS = [(4, 5), (21, 22), (23, 24), (25, 26)]
assert len(FEATURE_NAMES) == F and len(EVEN) + len(ODD) + 2 * len(PAIRS) == F


def mirror(x: np.ndarray) -> np.ndarray:
    """Đặc trưng của bài toán soi gương d → −d: nhóm lẻ đổi dấu, cặp (d_min, d_max) → (−d_max, −d_min)."""
    m = np.array(x, copy=True)
    m[..., ODD] = -x[..., ODD]
    for a, b in PAIRS:
        m[..., a] = -x[..., b]
        m[..., b] = -x[..., a]
    return m


def unpack_problem(p: np.ndarray) -> dict:
    """Bài toán QP từ khối TR_PROBLEM của bản ghi (một hàng hoặc nhiều hàng)."""
    blocks = {}
    for i, name in enumerate(("v", "kappa", "dkappa", "d_max", "d_min", "d_old", "has_old")):
        blocks[name] = p[..., 5 + i * N:5 + (i + 1) * N]
    return dict(d=p[..., 0], d_dot=p[..., 1], d_ddot=p[..., 2], heading=p[..., 3], d_target=p[..., 4],
                ay_limit=p[..., 5 + 7 * N], jerk_limit=p[..., 6 + 7 * N], **blocks)


def features(pb: dict) -> np.ndarray:
    """Bản tham chiếu của mlp_features() (cùng thứ tự phép tính, float64)."""
    d_min, d_max, has = pb["d_min"], pb["d_max"], pb["has_old"] > 0.5
    rows = d_min.shape[:-1]
    out = np.zeros(rows + (F,))
    out[..., 0], out[..., 1], out[..., 2], out[..., 3] = pb["d"], pb["d_dot"], pb["d_ddot"], pb["d_target"]
    out[..., 4], out[..., 5] = d_min[..., 0], d_max[..., 0]
    count = has.sum(axis=-1)
    first = np.where(has.any(axis=-1), np.take_along_axis(pb["d_old"], has.argmax(axis=-1)[..., None], -1)[..., 0], 0.0)
    last_idx = N - 1 - has[..., ::-1].argmax(axis=-1)
    last = np.where(has.any(axis=-1), np.take_along_axis(pb["d_old"], last_idx[..., None], -1)[..., 0], 0.0)
    out[..., 6], out[..., 7], out[..., 8] = count / N, first, last
    for i, k in enumerate((0, 9, 19, 29)):
        v = pb["v"][..., k]
        out[..., 9 + i] = v
        out[..., 13 + i] = v * v * pb["kappa"][..., k]
        out[..., 17 + i] = v * v * v * pb["dkappa"][..., k]
    for i, k in enumerate((9, 19, 29)):
        out[..., 21 + 2 * i] = d_min[..., k]
        out[..., 22 + 2 * i] = d_max[..., k]
    out[..., 27] = pb["ay_limit"]
    return out


def integrate(start: np.ndarray, jerk: np.ndarray) -> np.ndarray:
    """d(t_1..t_30) từ trạng thái đầu (d, d', d'') và jerk hằng từng đoạn, như cuối pp_generate_qp_seeded."""
    d, v, a = (start[..., i].astype(float) for i in range(3))
    out = np.zeros(jerk.shape)
    for k in range(N):
        j = jerk[..., k]
        d = d + v * DT + 0.5 * a * DT * DT + j * DT ** 3 / 6.0
        v = v + a * DT + 0.5 * j * DT * DT
        a = a + j * DT
        out[..., k] = d
    return out


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sha256_json(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()

"""Giải lại offline bài toán QP của từng cửa sổ (dataset.npz của luồng C) với trọng số cho trước, và hàm mục tiêu
thay thế dùng để tạo nhãn "trọng số tốt nhất" của qp_jerk_admm_mlp_weights.

Bộ giải là đúng qp.c của planner (biên dịch cùng resolve.c thành thư viện nhỏ, nạp qua ctypes), calibration mặc định
trừ ba trọng số. Lưới, hàm mục tiêu và mọi hằng số dưới đây chốt ở notes.md TRƯỚC khi tạo nhãn; không đổi sau khi đã
thấy nhãn.
"""

import ctypes
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
GEN = HERE.parent
sys.path.append(str(GEN.parent / "mlp"))

import common  # noqa: E402  (research/generators/mlp/common.py)
from common import N, ROOT, TR  # noqa: E402

OUT = ROOT / "build" / "lab" / "mlp_weights"
TOOL = OUT / "tool"
SOURCES = [HERE / "resolve.c", ROOT / "planner" / "src" / "generators" / "qp.c"]

# ---- Lưới trọng số (notes.md mục "Lưới và hàm mục tiêu"). Thứ tự trục: qp_w_dev, qp_w_jerk, qp_a_comfort. ----
DEFAULT = (0.30, 1.0, 2.0)  # calibration.yaml
W_DEV = tuple(round(0.30 * 2.0 ** (e / 2.0), 6) for e in (-2, -1, 0, 1, 2))  # 0,15 … 0,60, bước ×√2
W_JERK = tuple(round(1.0 * 2.0 ** (e / 2.0), 6) for e in (-2, -1, 0, 1, 2))  # 0,5 … 2,0, bước ×√2
A_COMFORT = (1.0, 1.5, 2.0, 2.5)  # m/s²; trần 2,5 của calibration.yaml
GRID = np.array([(a, b, c) for a in W_DEV for b in W_JERK for c in A_COMFORT])
DEFAULT_INDEX = int(np.flatnonzero(np.all(np.isclose(GRID, DEFAULT), axis=1))[0])

# ---- Hàm mục tiêu thay thế: mỗi thành phần chia cho dung sai thực tế của dashboard (eval.compare.TOLERANCES). ----
TOL_JERK = 0.10  # m/s³, PP-SWR-004
TOL_DEV = 0.005  # m, PP-SWR-050
TOL_DLC = 0.01  # m, PP-SWR-070
EARLY_STEPS = 10  # 0–1 s: cửa sổ đo của PP-SWR-004 (RMS path) và PP-SWR-050
CORRIDOR_MARGIN = 0.3  # m, qp_corridor_margin mặc định: d_max = nửa khoảng trống − biên này (pp_t7_qp_problem)
DEAD_BAND = 1.0  # đơn vị dung sai: không hơn mặc định ít nhất một dung sai thì nhãn là mặc định

# ---- Chất lượng nghiệm: cùng ngưỡng nhận nhãn của luồng C (mlp/label.py THRESHOLDS). ----
LABEL_ITERS = 1000  # như qp_jerk_admm_it1000_ref; kiểm hội tụ ở notes.md
THRESHOLDS = {"primal": 1e-4, "dual": 1e-3, "violation": 1e-6}


def build(force: bool = False) -> Path:
    """Sinh calibration mặc định và biên dịch libresolve (không cảnh báo)."""
    lib = TOOL / ("libresolve.dylib" if sys.platform == "darwin" else "libresolve.so")
    newest = max(p.stat().st_mtime for p in SOURCES + [ROOT / "planner" / "calibration" / "calibration.yaml"])
    if lib.exists() and lib.stat().st_mtime > newest and not force:
        return lib
    TOOL.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(ROOT / "planner" / "calibration" / "gen_calibration.py"), "--input",
                    str(ROOT / "planner" / "calibration" / "calibration.yaml"), "--out-dir", str(TOOL)], check=True)
    flags = ["-O2", "-std=c11", "-Wall", "-Wextra", "-Wpedantic", "-Wconversion", "-Wsign-conversion", "-Wshadow",
             "-Wmissing-prototypes", "-Werror", "-shared", "-fPIC"]
    inc = ["-I", str(ROOT / "interfaces" / "c"), "-I", str(ROOT / "planner" / "src"), "-I", str(TOOL)]
    subprocess.run(["cc", *flags, *inc, *map(str, SOURCES), str(TOOL / "pp_calibration.c"), "-o", str(lib)], check=True)
    return lib


class Solver:
    def __init__(self):
        self.lib = ctypes.CDLL(str(build()))
        dp = ctypes.POINTER(ctypes.c_double)
        self.lib.mlpw_resolve.argtypes = [dp, ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_double,
                                          ctypes.c_double, ctypes.c_int, dp, dp]
        self.lib.mlpw_resolve.restype = ctypes.c_int
        assert self.lib.mlpw_problem_size() == common.PROBLEM_SIZE and self.lib.mlpw_horizon() == N
        self._jerk = np.zeros(N)
        self._stats = np.zeros(5)

    def solve(self, problem: np.ndarray, warm: bool, d_target_before: float, w, iters: int = LABEL_ITERS):
        """Trả (jerk[N], stats[5] = primal, dual, vi phạm a_y, vi phạm jerk, slack) hoặc (None, stats)."""
        p = np.ascontiguousarray(problem, dtype=np.float64)
        dp = ctypes.POINTER(ctypes.c_double)
        ok = self.lib.mlpw_resolve(p.ctypes.data_as(dp), int(bool(warm)), float(d_target_before), float(w[0]),
                                   float(w[1]), float(w[2]), int(iters), self._jerk.ctypes.data_as(dp),
                                   self._stats.ctypes.data_as(dp))
        return (self._jerk.copy() if ok else None), self._stats.copy()


def accepted(stats: np.ndarray) -> bool:
    with np.errstate(invalid="ignore"):
        return bool(np.all(np.isfinite(stats[:4])) and stats[0] <= THRESHOLDS["primal"]
                    and stats[1] <= THRESHOLDS["dual"] and max(stats[2], stats[3]) <= THRESHOLDS["violation"])


def terms(problem: np.ndarray, jerk: np.ndarray) -> np.ndarray:
    """Ba thành phần của hàm mục tiêu trên path vòng hở của nghiệm: jerk RMS 0–1 s [m/s³], lệch đích RMS 0–1 s [m],
    DLC nhỏ nhất 0–3 s [m]. problem, jerk có thể là nhiều hàng."""
    pb = common.unpack_problem(problem)
    path_jerk = jerk + pb["v"] ** 3 * pb["dkappa"]  # jerk ngang của path, như hàng jerk cứng của qp.c
    j_rms = np.sqrt(np.mean(path_jerk[..., :EARLY_STEPS] ** 2, axis=-1))
    d = common.integrate(np.stack([pb["d"], pb["d_dot"], pb["d_ddot"]], axis=-1), jerk)  # d(t_1 … t_30)
    e_rms = np.sqrt(np.mean((d[..., :EARLY_STEPS] - pb["d_target"][..., None]) ** 2, axis=-1))
    left = pb["d_max"] + CORRIDOR_MARGIN - d
    right = d - (pb["d_min"] - CORRIDOR_MARGIN)
    dlc = np.min(np.minimum(left, right), axis=-1)
    return np.stack([j_rms, e_rms, dlc], axis=-1)


def score(t: np.ndarray) -> np.ndarray:
    """S = J/0,10 + E/0,005 − DLC/0,01 (đơn vị dung sai; nhỏ hơn là tốt hơn)."""
    return t[..., 0] / TOL_JERK + t[..., 1] / TOL_DEV - t[..., 2] / TOL_DLC


def pick(scores: np.ndarray) -> int:
    """Chỉ số nhãn trong GRID: ô có S nhỏ nhất, trừ khi không hơn ô mặc định ít nhất DEAD_BAND (khi đó là mặc
    định). Ô có nghiệm không đạt ngưỡng mang S = +inf. Gọi khi ô mặc định hữu hạn."""
    best = int(np.argmin(scores))
    return best if scores[DEFAULT_INDEX] - scores[best] >= DEAD_BAND else DEFAULT_INDEX


def ref_dtarget(scenarios: np.ndarray, calls: np.ndarray, raw=common.OUT / "raw") -> np.ndarray:
    """TR_REF_DTARGET của từng cửa sổ (dataset.npz không giữ trường này) lấy từ bản ghi thô theo (kịch bản, lần gọi)."""
    out = np.full(len(scenarios), np.nan)
    cache = {}
    for i, (s, c) in enumerate(zip(scenarios, calls)):
        if s not in cache:
            rec = np.load(raw / f"{s}.npz")["records"]
            cache[s] = {int(r[TR["COUNT"]]): r[TR["REF_DTARGET"]] for r in rec}
        out[i] = cache[s][int(c)]
    return out

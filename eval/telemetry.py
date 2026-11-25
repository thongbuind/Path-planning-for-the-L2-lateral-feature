"""Telemetry nghiên cứu của generator T7 (PP-TS-031), chỉ có ở bản build lab với PP_T7_TELEMETRY.

Đây là chẩn đoán và khối lượng việc (PP-TS-031 mục 3.3), không phải chỉ số so với mốc.
Bản build không có telemetry thì không bọc gì, nên lượt chạy và vùng đo thời gian giữ nguyên.
Bản có telemetry đọc state sau mỗi bước, trong vùng đo thời gian: không dùng để đo thời gian.
"""

import ctypes
import math

import numpy as np

SYMBOL = "pp_lcc_t7_telemetry"
WORKSPACE_SYMBOL = "pp_lcc_t7_workspace"


class TelemetryC(ctypes.Structure):
    """Bản sao pp_t7_telemetry_t (planner/src/generators/pp_t7_input.h)."""

    _fields_ = [("work", ctypes.c_uint32), ("fallback", ctypes.c_uint32), ("infer_ops", ctypes.c_uint32),
                ("residual", ctypes.c_double), ("slack", ctypes.c_double), ("t10_change_m", ctypes.c_double)]


def has_telemetry(library: ctypes.CDLL) -> bool:
    return hasattr(library, SYMBOL)


def _bind(library: ctypes.CDLL):
    fn = getattr(library, SYMBOL)
    fn.restype = ctypes.c_bool
    fn.argtypes = [ctypes.c_void_p, ctypes.POINTER(TelemetryC)]
    ws = getattr(library, WORKSPACE_SYMBOL, None)
    if ws is not None:
        ws.restype = ctypes.c_void_p
        ws.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t)]
    return fn, ws


class _Probe:
    """Bọc SilPlanner của LCC: sau mỗi bước đọc telemetry, và nếu có `capture`, gọi capture(ws_bytes)."""

    def __init__(self, inner, library: ctypes.CDLL, records: list, capture=None) -> None:
        self._inner = inner
        self._fn, self._ws = _bind(library)
        self._records = records
        self._capture = capture
        self._tm = TelemetryC()

    def __getattr__(self, name):
        return getattr(self._inner, name)

    def step(self, inputs, ego_motion):
        out = self._inner.step(inputs, ego_motion)
        state = self._inner._state
        if self._fn(state, ctypes.byref(self._tm)):
            t = self._tm
            self._records.append((t.work, t.fallback, t.infer_ops, t.residual, t.slack, t.t10_change_m))
        if self._capture is not None and self._ws is not None:
            size = ctypes.c_size_t(0)
            address = self._ws(state, ctypes.byref(size))
            if address:
                self._capture(ctypes.string_at(address, size.value))
        return out


class Recording:
    """Factory planner cho Harness, giữ telemetry của mọi chu kỳ LCC. `records` rỗng nếu thư viện không
    có telemetry. `capture` (tùy chọn) nhận bytes của ws mỗi chu kỳ, cho bộ ghi dữ liệu của MLP."""

    def __init__(self, libraries, capture=None) -> None:
        self._libraries = libraries
        self._capture = capture
        self.records: list[tuple] = []

    def __getattr__(self, name):
        return getattr(self._libraries, name)

    def __call__(self, vehicle_config):
        planners = self._libraries(vehicle_config)
        lcc_library = self._libraries.load()[0]
        if planners.lcc is not None and has_telemetry(lcc_library):
            from interfaces import PlannerSet
            planners = PlannerSet(_Probe(planners.lcc, lcc_library, self.records, self._capture),
                                  planners.lka_elk)
        return planners


def wrap(libraries):
    """Trả `libraries` nguyên vẹn nếu bản build không có telemetry, để lượt chạy thường không đổi."""
    library = libraries.load()[0]
    return Recording(libraries) if has_telemetry(library) else libraries


def _finite(values) -> np.ndarray:
    a = np.asarray(values, dtype=float)
    return a[np.isfinite(a)]


def _stats(values) -> dict | None:
    a = _finite(values)
    if a.size == 0:
        return None
    p50, p99 = np.percentile(a, (50, 99))
    return {"p50": float(p50), "p99": float(p99), "max": float(a.max()), "mean": float(a.mean())}


def summary(records: list[tuple]) -> dict | None:
    """Tóm tắt một lượt: chỉ tính chu kỳ generator đã chạy (work > 0 hoặc có lý do dùng nghiệm thay thế)."""
    rows = [r for r in records if r[0] > 0 or r[1] != 0]
    if not rows:
        return None
    work, fallback, ops, residual, slack, t10 = (list(c) for c in zip(*rows))
    codes = {}
    for code in fallback:
        if code:
            codes[str(code)] = codes.get(str(code), 0) + 1
    t10a = np.asarray(t10, dtype=float)
    return {
        "cycles": len(rows),
        "work": _stats(work),
        "fallback_share": sum(1 for c in fallback if c) / len(rows),
        "fallback_codes": codes,
        "infer_ops_max": int(max(ops)),
        "residual": _stats(residual),
        "slack": _stats(slack),
        "t10_change_m": _stats(t10a),
        "t10_changed_share": float(np.mean(t10a > 1e-3)) if t10a.size else math.nan,
    }

"""Cô lập từng run trong tiến trình con để crash và timeout của SUT không làm mất kết quả của cả
suite.
"""

import multiprocessing
import os
import traceback
from concurrent.futures import ThreadPoolExecutor

START_METHODS = ("forkserver", "spawn")
START_METHOD = os.environ.get("PP_START_METHOD", "forkserver")
if START_METHOD not in START_METHODS:
    raise ValueError(f"PP_START_METHOD must be one of {START_METHODS}")
# Forkserver chỉ nạp trước phụ thuộc của worker. Không nạp planner C hoặc mô-đun CLI mà child sẽ
# khởi động lại.
PRELOAD = ["numpy", "scipy.signal", "yaml", "sim.harness", "eval.metrics", "eval.differential",
           "eval.loader", "eval.labels", "eval.aspects", "eval.conformance", "eval.case", "eval.checksum"]

_CTX = multiprocessing.get_context(START_METHOD)
if START_METHOD == "forkserver":
    _CTX.set_forkserver_preload(PRELOAD)


def _child(conn, fn, args) -> None:
    try:
        conn.send(("ok", fn(*args)))
    except BaseException as error:
        conn.send(("error", f"{type(error).__name__}: {error}\n{traceback.format_exc(limit=3)}"))
    finally:
        conn.close()


def run_isolated(fn, args: tuple, timeout_s: float) -> tuple[str, object]:
    parent, child = _CTX.Pipe(duplex=False)
    proc = _CTX.Process(target=_child, args=(child, fn, args), daemon=True)
    proc.start()
    child.close()
    try:
        if not parent.poll(timeout_s):
            proc.kill()
            proc.join()
            return "timeout", None
        try:
            status, value = parent.recv()
        except EOFError:
            proc.join()
            code = proc.exitcode
            return "crash", f"signal {-code}" if code is not None and code < 0 else f"exit {code}"
        proc.join()
        return status, value
    finally:
        parent.close()


def map_isolated(fn, tasks: list[tuple], jobs: int, timeout_s: float):
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        yield from pool.map(lambda args: run_isolated(fn, args, timeout_s), tasks)

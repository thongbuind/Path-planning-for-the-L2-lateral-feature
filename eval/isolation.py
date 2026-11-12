"""One run per child process, so a planner that crashes or hangs is an execution fault of
that run (Software Qualification Test Specification 8.4), not the end of the suite.

    status, value = run_isolated(fn, args, timeout_s)
    status: "ok" (value = fn(*args)), "error" (value = exception text, evaluator side),
            "crash" (value = exit code or signal), "timeout" (value = None)

`fn` must be importable at module level (spawn start method, also used on Linux so that
behaviour does not depend on the platform).
"""

import multiprocessing
import traceback
from concurrent.futures import ThreadPoolExecutor

_CTX = multiprocessing.get_context("spawn")


def _child(conn, fn, args) -> None:
    try:
        conn.send(("ok", fn(*args)))
    except BaseException as error:  # reported to the parent, never lost
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
        except EOFError:  # the child died before sending
            proc.join()
            code = proc.exitcode
            return "crash", f"signal {-code}" if code is not None and code < 0 else f"exit {code}"
        proc.join()
        return status, value
    finally:
        parent.close()


def map_isolated(fn, tasks: list[tuple], jobs: int, timeout_s: float):
    """run_isolated over tasks, at most `jobs` children at a time, results in task order."""
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        yield from pool.map(lambda args: run_isolated(fn, args, timeout_s), tasks)

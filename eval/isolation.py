"""One run per child process, so a planner that crashes or hangs is an execution fault of
that run (Software Qualification Test Specification 8.4), not the end of the suite.

    status, value = run_isolated(fn, args, timeout_s)
    status: "ok" (value = fn(*args)), "error" (value = exception text, evaluator side),
            "crash" (value = exit code or signal), "timeout" (value = None)

`fn` must be importable at module level. Children start from a fork server that has already
imported the simulator and the evaluation (PRELOAD), so a run does not pay those imports
again (Software Qualification Test Specification 4.1). Each run is still a fresh process.
The fork server only imports: no planner library is loaded and no numerical work runs before
the fork. `PP_START_METHOD=spawn` falls back to a clean interpreter per run.
"""

import multiprocessing
import os
import traceback
from concurrent.futures import ThreadPoolExecutor

START_METHODS = ("forkserver", "spawn")
START_METHOD = os.environ.get("PP_START_METHOD", "forkserver")
if START_METHOD not in START_METHODS:
    raise ValueError(f"PP_START_METHOD must be one of {START_METHODS}")
# Modules imported once by the fork server; the planner library is never among them. The
# drivers that use this module (eval.suite, eval.matrix) are left out, also indirectly: each
# child re-runs its main module as __mp_main__, as with spawn, and the main module must not
# already be imported (runpy warning, two copies of the module).
PRELOAD = ["numpy", "scipy.signal", "yaml", "sim.harness", "eval.metrics", "eval.differential",
           "eval.loader", "eval.labels", "eval.aspects", "eval.conformance"]

_CTX = multiprocessing.get_context(START_METHOD)
if START_METHOD == "forkserver":
    _CTX.set_forkserver_preload(PRELOAD)


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

"""Supervision of worker processes: one run per process, owned by the supervisor, not by the
observers that watch it (SIM-REQ-002 to 012).

A worker is `command + [run_folder]`. It reads <run_folder>/request.json, writes its files
into the folder, prints one JSON object per line on stdout and reads control lines on stdin.
The supervisor numbers the lines (`seq`), keeps them in <run_folder>/frames.ndjson (gzip at the
end), routes stderr and non-JSON stdout to worker.log, and finalizes the bundle with the state:

    QUEUED -> RUNNING <-> PAUSED -> COMPLETED | FAILED | CANCELLED | TIMED_OUT

A FAILED run has one class (`classify`): SUT_EXECUTION (native crash inside the SUT adapter, or
reported by the worker), SIM_ERROR, EVAL_ERROR, INFRA. Lines a worker may print: {"type":
"phase", "phase": ...}, {"type": "error", "class": ..., "message": ...} and {"type": "budget",
"timeout_s": ...} (its own time limit, wall clock without pauses; not passed to observers); any
other line is an event for the observers. The supervisor adds {"type": "state", ...} events.
"""

import json
import os
import shutil
import signal
import subprocess
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path

from execution import bundle as B

STATES = ("QUEUED", "RUNNING", "PAUSED", "COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT")
TERMINAL = frozenset({"COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT"})
CLASSES = ("SUT_EXECUTION", "SIM_ERROR", "EVAL_ERROR", "INFRA")
NATIVE_SIGNALS = frozenset(int(s) for s in (signal.SIGSEGV, signal.SIGBUS, signal.SIGILL, signal.SIGFPE,
                                             signal.SIGABRT))
EVENTS = "frames.ndjson"
LOG = "worker.log"
OWNER = "supervisor.json"
DEFAULT_TIMEOUT_S = 1800.0


@dataclass
class Settings:
    root: Path
    command: list[str]
    cwd: Path | None = None
    env: dict | None = None
    max_running: int = 2  # N_max
    cancel_grace_s: float = 2.0  # T_cancel
    keep: int | None = 50  # N_keep; None: never delete
    max_bytes: int | None = 2_000_000_000  # S_max
    sut_marker: str = "adapters/sil"  # in the stack of a native crash: the crash is the SUT's


def classify(returncode: int | None, *, cancelled: bool, timed_out: bool, reported: str | None,
             log_tail: str, sut_marker: str) -> tuple[str, str | None]:
    """(state, failure class) of a finished worker."""
    if timed_out:
        return "TIMED_OUT", None
    if cancelled:
        return "CANCELLED", None
    if returncode == 0:
        return "COMPLETED", None
    if returncode is not None and returncode < 0 and -returncode in NATIVE_SIGNALS:
        return "FAILED", "SUT_EXECUTION" if sut_marker and sut_marker in log_tail else "SIM_ERROR"
    if returncode is not None and returncode < 0:
        return "FAILED", "INFRA"  # killed from outside
    if reported in CLASSES:
        return "FAILED", reported
    return "FAILED", "INFRA"


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


@dataclass
class Run:
    run_id: str
    request: dict
    timeout_s: float
    label: str = ""
    parent: str | None = None
    state: str = "QUEUED"
    failure: str | None = None
    message: str = ""
    phase: str = ""
    reported: str | None = None
    created: float = field(default_factory=time.time)
    started: float | None = None
    ended: float | None = None
    paused_since: float | None = None
    paused_total: float = 0.0
    cancel_requested: bool = False
    timed_out: bool = False
    proc: subprocess.Popen | None = None
    bundle: B.Bundle | None = None
    events: list[bytes] | None = field(default_factory=list)
    folder: Path | None = None

    def summary(self) -> dict:
        return {"run_id": self.run_id, "state": self.state, "failure": self.failure, "message": self.message,
                "phase": self.phase, "label": self.label, "parent_run_id": self.parent,
                "created": self.created, "started": self.started, "ended": self.ended,
                "events": len(self.events) if self.events is not None else None}


class Supervisor:
    def __init__(self, settings: Settings) -> None:
        self.s = settings
        self.s.root.mkdir(parents=True, exist_ok=True)
        self._runs: dict[str, Run] = {}
        self._queue: deque[str] = deque()
        self._idem: dict[str, str] = {}
        self._lock = threading.RLock()
        self._changed = threading.Condition(self._lock)
        self._closing = False
        self.recover()
        self._monitor = threading.Thread(target=self._watch, daemon=True)
        self._monitor.start()

    # ---- recovery and retention ---------------------------------------------------------

    def recover(self) -> list[str]:
        """Finalize the folders left by a supervisor that stopped during a run (INFRA)."""
        done = []
        for tmp in sorted(self.s.root.glob(B.TMP_PREFIX + "*")):
            owner = tmp / OWNER
            if not owner.is_file():
                continue  # written by another tool (eval.runner): not ours
            pid = json.loads(owner.read_text(encoding="utf-8")).get("pid")
            if isinstance(pid, int) and pid != os.getpid() and _alive(pid):
                continue
            stale = B.Bundle(self.s.root, tmp.name[len(B.TMP_PREFIX):])
            stale.compress(EVENTS)
            stale.finalize({"state": "FAILED", "failure": "INFRA",
                            "message": "supervisor stopped during the run", "recovered": time.time()})
            done.append(stale.run_id)
        return done

    def _prune(self) -> None:
        if self.s.keep is None and self.s.max_bytes is None:
            return
        pinned = set(self.pinned())
        total = 0
        for i, folder in enumerate(B.listing(self.s.root)):
            size = sum(p.stat().st_size for p in folder.rglob("*") if p.is_file())
            total += size
            if folder.name in pinned:
                continue
            if (self.s.keep is not None and i >= self.s.keep) or (self.s.max_bytes is not None and total > self.s.max_bytes):
                shutil.rmtree(folder, ignore_errors=True)
                total -= size

    def pinned(self) -> list[str]:
        path = self.s.root / ".pinned.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else []

    def pin(self, run_id: str, on: bool = True) -> None:
        with self._lock:
            ids = [r for r in self.pinned() if r != run_id] + ([run_id] if on else [])
            B.write_json(self.s.root / ".pinned.json", ids)

    # ---- control ------------------------------------------------------------------------

    def submit(self, request: dict, *, timeout_s: float | None = None, idempotency_key: str | None = None,
               label: str = "", parent: str | None = None) -> str:
        with self._lock:
            if self._closing:
                raise RuntimeError("supervisor is shutting down")
            if idempotency_key and idempotency_key in self._idem:
                return self._idem[idempotency_key]
            run_id = B.new_run_id()
            while run_id in self._runs or (self.s.root / run_id).exists():
                run_id = B.new_run_id()
            run = Run(run_id, request, timeout_s or DEFAULT_TIMEOUT_S, label, parent)
            self._runs[run_id] = run
            if idempotency_key:
                self._idem[idempotency_key] = run_id
            self._emit(run, {"type": "state", "state": "QUEUED"})
            self._queue.append(run_id)
            self._start_queued()
            return run_id

    def _running(self) -> int:
        return sum(1 for r in self._runs.values() if r.state in ("RUNNING", "PAUSED"))

    def _start_queued(self) -> None:
        while self._queue and self._running() < self.s.max_running:
            run = self._runs[self._queue.popleft()]
            if run.state == "QUEUED":
                self._start(run)

    def _start(self, run: Run) -> None:
        run.bundle = B.Bundle.create(self.s.root, run.run_id)
        run.bundle.write_json("request.json", {"run_id": run.run_id, "parent_run_id": run.parent, **run.request})
        run.bundle.write_json(OWNER, {"pid": os.getpid()})
        run.bundle.path(EVENTS).write_bytes(b"".join(run.events or []))  # events from before the folder existed
        log = run.bundle.path(LOG).open("ab")
        try:
            run.proc = subprocess.Popen([*self.s.command, str(run.bundle.tmp)], cwd=self.s.cwd, env=self.s.env,
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log)
        except OSError as error:
            log.close()
            run.message = f"worker did not start: {error}"
            self._finish(run, returncode=None, reported="INFRA")
            return
        log.close()
        run.started = time.time()
        self._set_state(run, "RUNNING")
        threading.Thread(target=self._pump, args=(run,), daemon=True).start()

    def control(self, run_id: str, message: dict) -> str:
        with self._lock:
            run = self._get(run_id)
            if run.state not in ("RUNNING", "PAUSED") or run.proc is None:
                raise LookupError(f"run {run_id} is {run.state}")
            try:
                run.proc.stdin.write((json.dumps(message) + "\n").encode())
                run.proc.stdin.flush()
            except (OSError, ValueError) as error:
                raise LookupError(f"run {run_id} no longer reads commands") from error
            cmd = message.get("cmd")
            if cmd == "pause" and run.state == "RUNNING":
                run.paused_since = time.time()
                self._set_state(run, "PAUSED")
            elif cmd == "resume" and run.state == "PAUSED":
                run.paused_total += time.time() - (run.paused_since or time.time())
                run.paused_since = None
                self._set_state(run, "RUNNING")
            return run.state

    def cancel(self, run_id: str) -> str:
        with self._lock:
            run = self._get(run_id)
            if run.state in TERMINAL:
                return run.state
            run.cancel_requested = True
            if run.state == "QUEUED":
                self._queue.remove(run_id)
                run.message = "cancelled before start"
                self._finish(run, returncode=None, reported=None)
                return run.state
            proc = run.proc
        self._stop(proc)
        return "CANCELLING"

    def _stop(self, proc: subprocess.Popen | None) -> None:
        """SIGTERM, then SIGKILL after the grace period (T_cancel)."""
        if proc is None or proc.poll() is not None:
            return
        proc.terminate()

        def escalate():
            try:
                proc.wait(self.s.cancel_grace_s)
            except subprocess.TimeoutExpired:
                proc.kill()

        threading.Thread(target=escalate, daemon=True).start()

    def shutdown(self, wait_s: float = 5.0) -> None:
        with self._lock:
            self._closing = True
            for run_id in list(self._queue):
                self.cancel(run_id)
            active = [r for r in self._runs.values() if r.state in ("RUNNING", "PAUSED")]
        for run in active:
            self.cancel(run.run_id)
        deadline = time.time() + wait_s
        with self._lock:
            while any(r.state not in TERMINAL for r in active) and time.time() < deadline:
                self._changed.wait(0.2)

    # ---- worker output ------------------------------------------------------------------

    def _emit(self, run: Run, obj: dict) -> None:
        """Numbers an event, keeps it for observers and in the event log of the run folder."""
        with self._lock:
            if run.events is None:
                return
            obj = {**obj, "seq": len(run.events) + 1}
            line = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode() + b"\n"
            run.events.append(line)
            if run.bundle is not None and run.bundle.tmp.is_dir():
                with run.bundle.path(EVENTS).open("ab") as stream:
                    stream.write(line)
            self._changed.notify_all()

    def _set_state(self, run: Run, state: str) -> None:
        run.state = state
        self._emit(run, {"type": "state", "state": state, "failure": run.failure, "message": run.message})

    def _pump(self, run: Run) -> None:
        assert run.proc is not None and run.proc.stdout is not None
        for raw in run.proc.stdout:
            try:
                obj = json.loads(raw)
                if not isinstance(obj, dict):
                    raise ValueError
            except ValueError:
                with run.bundle.path(LOG).open("ab") as log:
                    log.write(b"[stdout] " + raw)
                continue
            kind = obj.get("type")
            if kind == "budget":  # the worker knows how long its run may take (T_timeout)
                try:
                    run.timeout_s = float(obj["timeout_s"])
                except (KeyError, TypeError, ValueError):
                    pass
                continue
            if kind == "phase":
                run.phase = str(obj.get("phase", ""))
            elif kind == "error":
                run.reported = obj.get("class")
                run.message = str(obj.get("message", ""))
            self._emit(run, obj)
        returncode = run.proc.wait()
        with self._lock:
            self._finish(run, returncode, run.reported)

    def _finish(self, run: Run, returncode: int | None, reported: str | None) -> None:
        """Terminal state, final event, bundle finalized; next queued run starts."""
        tail = ""
        if run.bundle is not None and run.bundle.path(LOG).is_file():
            tail = run.bundle.path(LOG).read_bytes()[-20000:].decode("utf-8", "replace")
        if run.proc is None and not run.cancel_requested and reported == "INFRA":
            state, failure = "FAILED", "INFRA"
        else:
            state, failure = classify(returncode, cancelled=run.cancel_requested, timed_out=run.timed_out,
                                      reported=reported, log_tail=tail, sut_marker=self.s.sut_marker)
        run.failure = failure
        run.ended = time.time()
        if run.bundle is None:  # cancelled while queued: still one bundle per run (SIM-REQ-020)
            run.bundle = B.Bundle.create(self.s.root, run.run_id)
            run.bundle.write_json("request.json", {"run_id": run.run_id, "parent_run_id": run.parent, **run.request})
            run.bundle.path(EVENTS).write_bytes(b"".join(run.events or []))
        if state == "TIMED_OUT" and not run.message:
            run.message = f"no end after {run.timeout_s:g} s (paused time excluded)"
        self._set_state(run, state)
        if run.bundle is not None:
            run.bundle.compress(EVENTS)
            if run.bundle.path(OWNER).is_file():
                run.bundle.path(OWNER).unlink()
            run.folder = run.bundle.finalize({
                "state": state, "failure": failure, "message": run.message, "phase": run.phase,
                "returncode": returncode, "signal": -returncode if returncode is not None and returncode < 0 else None,
                "created": run.created, "started": run.started, "ended": run.ended, "paused_s": round(run.paused_total, 3),
                "timeout_s": run.timeout_s, "cancelled": run.cancel_requested, "label": run.label,
                "parent_run_id": run.parent})
        run.events = None  # served from the bundle from now on
        self._changed.notify_all()
        self._start_queued()
        try:
            self._prune()
        except OSError:
            pass

    def _watch(self) -> None:
        """Timeouts, wall clock without paused time (SIM-REQ-007)."""
        while True:
            time.sleep(0.25)
            with self._lock:
                now = time.time()
                late = []
                for run in self._runs.values():
                    if run.state != "RUNNING" or run.started is None or run.timed_out:
                        continue
                    if now - run.started - run.paused_total > run.timeout_s:
                        run.timed_out = True
                        late.append(run.proc)
            for proc in late:
                self._stop(proc)

    # ---- queries ------------------------------------------------------------------------

    def _get(self, run_id: str) -> Run:
        run = self._runs.get(run_id)
        if run is None:
            raise KeyError(run_id)
        return run

    def status(self, run_id: str) -> dict:
        with self._lock:
            run = self._runs.get(run_id)
            if run is not None and run.state not in TERMINAL:
                return run.summary()
        folder = self.s.root / run_id
        if not (folder / "execution.json").is_file():
            raise KeyError(run_id)
        return {"run_id": run_id, **B.read(folder)}

    def runs(self, limit: int = 100) -> list[dict]:
        with self._lock:
            active = [r.summary() for r in self._runs.values() if r.state not in TERMINAL]
        finished = []
        for folder in B.listing(self.s.root)[:limit]:
            execution = json.loads((folder / "execution.json").read_text(encoding="utf-8"))
            finished.append({"run_id": folder.name, "state": execution.get("state"), "failure": execution.get("failure"),
                             "message": execution.get("message", ""), "label": execution.get("label", ""),
                             "parent_run_id": execution.get("parent_run_id"), "complete": execution.get("complete"),
                             "created": execution.get("created"), "ended": execution.get("ended")})
        return sorted(active, key=lambda r: r["created"], reverse=True) + finished

    def request_of(self, run_id: str) -> dict:
        with self._lock:
            run = self._runs.get(run_id)
            if run is not None:
                return dict(run.request)
        data = B.read(self.s.root / run_id).get("request")
        if data is None:
            raise KeyError(run_id)
        return {k: v for k, v in data.items() if k not in ("run_id", "parent_run_id")}

    def events(self, run_id: str, after: int = 0, idle_s: float = 15.0):
        """Event lines with seq > after, live until the run ends. Yields b"" every idle_s
        without news, so the caller can notice a closed connection."""
        nxt = after + 1
        while True:
            with self._lock:
                run = self._runs.get(run_id)
                if run is None or run.events is None:
                    break
                chunk = run.events[nxt - 1:]
                if not chunk:
                    if run.state in TERMINAL:
                        return
                    self._changed.wait(idle_s)
                    chunk = run.events[nxt - 1:] if run.events is not None else []
            if chunk:
                nxt += len(chunk)
                yield from chunk
            elif run is not None and run.events is not None:
                yield b""
        path = self.s.root / run_id / (EVENTS + ".gz")
        if not path.is_file():
            if not (self.s.root / run_id).is_dir() and run_id not in self._runs:
                raise KeyError(run_id)
            return
        import gzip
        with gzip.open(path, "rb") as stream:
            for line in stream:
                try:
                    seq = json.loads(line).get("seq", 0)
                except ValueError:
                    continue
                if seq >= nxt:
                    yield line

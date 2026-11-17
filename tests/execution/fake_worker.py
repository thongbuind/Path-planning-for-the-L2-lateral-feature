"""Test double of a worker for execution.supervisor: behaviour chosen by request.json "mode".

    ok          10 events, the required files, exit 0
    slow        one event every 50 ms for "n" events; pause/resume on stdin
    stderr      prints to stderr and a non-JSON stdout line, then exits 1 without a class
    eval_error  reports EVAL_ERROR, exit 3
    crash_sut   stack text naming the SUT adapter on stderr, then SIGSEGV
    crash_sim   stack text without it, then SIGSEGV
    stubborn    ignores SIGTERM and never ends
"""

import json
import os
import signal
import sys
import threading
import time
from pathlib import Path

folder = Path(sys.argv[1])
request = json.loads((folder / "request.json").read_text())
request = {**request, **request.get("config", {})}  # the workbench wraps it in "config"
mode = request["mode"]
paused = threading.Event()


def send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def controls():
    for line in sys.stdin:
        cmd = json.loads(line).get("cmd")
        if cmd == "pause":
            paused.set()
        elif cmd == "resume":
            paused.clear()


def files():
    for name in ("manifest.json", "resolved-case.json", "evaluation.json"):
        (folder / name).write_text(json.dumps({"name": name, "run_id": request["run_id"]}))


threading.Thread(target=controls, daemon=True).start()
send({"type": "phase", "phase": "simulate"})
if mode == "ok":
    for k in range(10):
        send({"type": "f", "k": k})
    files()
elif mode == "slow":
    for k in range(int(request.get("n", 40))):
        while paused.is_set():
            time.sleep(0.01)
        send({"type": "f", "k": k})
        time.sleep(0.05)
    files()
elif mode == "stderr":
    sys.stderr.write("Traceback (most recent call last):\n  something broke\n")
    sys.stderr.flush()
    print("plain text, not JSON", flush=True)
    sys.exit(1)
elif mode == "eval_error":
    send({"type": "error", "class": "EVAL_ERROR", "message": "metric failed"})
    sys.exit(3)
elif mode in ("crash_sut", "crash_sim"):
    where = "adapters/sil/sil_planner.py" if mode == "crash_sut" else "sim/vehicle/bicycle.py"
    sys.stderr.write(f'Fatal Python error: Segmentation fault\n  File "{where}", line 1 in step\n')
    sys.stderr.flush()
    os.kill(os.getpid(), signal.SIGSEGV)
elif mode == "stubborn":
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    send({"type": "f", "k": 0})
    while True:
        time.sleep(0.1)

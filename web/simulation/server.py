#!/usr/bin/env python3
"""Server cục bộ cho web Path Planner SIL: tệp tĩnh và API chạy planner thật theo thời gian thực.

    python3 web/simulation/server.py            rồi mở http://127.0.0.1:8793

Mỗi lần bấm Chạy, server sinh một tiến trình tools/rt_run.py chạy simulator và libpp_planner của repo,
đọc từng chu kỳ 25 ms mà tiến trình đó đẩy ra và chuyển tiếp lên trình duyệt. Một lượt chạy tại một
thời điểm: bấm Chạy lần nữa, đóng tab hay bấm Dừng thì lượt cũ bị dừng. Chỉ ĐỌC repo, không ghi file,
chỉ nghe ở 127.0.0.1.

API
    GET  /api/catalog   kịch bản, lỗi và mức lỗi, tổ hợp, xe của benchmark
    POST /api/run       body JSON cấu hình; trả về luồng NDJSON của lượt chạy
    POST /api/control   {"cmd":"pause"} {"cmd":"resume"} {"cmd":"rate","value":2}
    POST /api/stop      dừng lượt đang chạy
"""

import http.server
import json
import os
import select
import socket
import socketserver
import subprocess
import sys
import threading
from pathlib import Path

WEB = Path(__file__).resolve().parent
REPO = WEB.parents[1]
RT = WEB / "tools" / "rt_run.py"
PORT = int(os.environ.get("PP_PORT", "8793"))

ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONPATH=str(REPO / "build" / "python-deps"))
LOCK = threading.Lock()
RUN = {"proc": None}
CATALOG = {"json": None}


def spawn(*args, nice=0):
    return subprocess.Popen([sys.executable, "-u", str(RT), *args], cwd=str(REPO), env=ENV,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            preexec_fn=(lambda: os.nice(nice)) if nice else None)


def kill_current():
    with LOCK:
        proc, RUN["proc"] = RUN["proc"], None
    if proc is not None and proc.poll() is None:
        proc.kill()
        proc.wait()


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(WEB), **kw)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):
        pass

    def _origin_ok(self):
        o = self.headers.get("Origin")
        port = self.server.server_port
        return o is None or o in (f"http://127.0.0.1:{port}", f"http://localhost:{port}")

    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}") if n < 65536 else {}

    def do_GET(self):
        if self.path == "/api/catalog":
            if CATALOG["json"] is None:
                proc = spawn("catalog", nice=10)
                out = proc.stdout.read()
                proc.wait()
                try:
                    obj = json.loads(out.decode("utf-8"))
                except ValueError:
                    return self._json(500, {"error": "không đọc được danh mục"})
                if obj.get("type") == "error":
                    return self._json(500, {"error": obj["message"]})
                CATALOG["json"] = obj
            return self._json(200, CATALOG["json"])
        super().do_GET()

    def do_POST(self):
        if not self._origin_ok():
            return self._json(403, {"error": "origin không được phép"})
        try:
            cfg = self._body()
        except ValueError:
            return self._json(400, {"error": "JSON không hợp lệ"})
        if self.path == "/api/run":
            return self._run(cfg)
        if self.path == "/api/control":
            with LOCK:
                proc = RUN["proc"]
                if proc is None or proc.poll() is not None:
                    return self._json(409, {"error": "không có lượt chạy"})
                try:
                    proc.stdin.write((json.dumps(cfg) + "\n").encode())
                    proc.stdin.flush()
                except OSError:
                    return self._json(409, {"error": "lượt chạy đã kết thúc"})
            return self._json(200, {"ok": True})
        if self.path == "/api/stop":
            kill_current()
            return self._json(200, {"ok": True})
        self._json(404, {"error": "không có API này"})

    def _run(self, cfg):
        kill_current()
        proc = spawn("run", json.dumps(cfg))
        with LOCK:
            RUN["proc"] = proc
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()
        # Lượt chạy đang tạm dừng không ghi gì ra nên ghi lỗi không báo được client đã đóng: canh socket.
        threading.Thread(target=self._watch, args=(proc,), daemon=True).start()
        try:
            for line in proc.stdout:
                self.wfile.write(line)
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            if proc.poll() is None:
                proc.kill()
            proc.wait()
            with LOCK:
                if RUN["proc"] is proc:
                    RUN["proc"] = None


    def _watch(self, proc):
        conn = self.connection
        while proc.poll() is None:
            try:
                ready, _, _ = select.select([conn], [], [], 1.0)
                if ready and conn.recv(1, socket.MSG_PEEK) == b"":
                    proc.kill()
                    return
            except (OSError, ValueError):
                proc.kill()
                return


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


if __name__ == "__main__":
    try:
        srv = Server(("127.0.0.1", PORT), Handler)
    except OSError as e:
        raise SystemExit(f"Không mở được cổng {PORT}: {e}. Có thể server cũ còn chạy: pkill -f pp-replay/server.py, "
                         f"hoặc đổi cổng bằng PP_PORT=8794")
    print(f"Path Planner SIL: http://127.0.0.1:{PORT}  (Ctrl+C để dừng)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        kill_current()

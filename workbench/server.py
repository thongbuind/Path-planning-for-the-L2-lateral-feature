"""Server phục vụ UI và API run. Đóng tab không dừng run; khi nối lại, stream tiếp tục từ seq đã
nhận (PP-PR-064).
"""

import argparse
import http.server
import json
import math
import os
import re
import signal
import socketserver
import subprocess
import sys
import threading
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from execution import bundle as bundles
from execution.supervisor import Settings, Supervisor
from workbench import campaign, compare, evidence

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "web" / "simulation"
RUNS = ROOT / "build" / "runs"
PORT = int(os.environ.get("PP_PORT", "8793"))
WORKER = [sys.executable, "-u", "-m", "eval.live", "run"]
CATALOG = [sys.executable, "-m", "eval.live", "catalog"]
STATIC_FILES = {"index.html", "app.css", "js/i18n.js", "js/catalog-en.js", "js/core.js", "js/scene.js",
                "js/charts.js", "js/ui.js", "wb.css", "js/wb.js", "js/wb-runs.js", "js/wb-evidence.js",
                "js/wb-compare.js"}
BUNDLE_FILES = {"manifest.json", "resolved-case.json", "execution.json", "evaluation.json", "request.json",
                "trace.mcap", "frames.ndjson.gz", "worker.log", "SHA256SUMS"}
RUN_PATH = re.compile(r"^/api/runs/([0-9]{8}-[0-9]{6}-[0-9a-f]{6})(/events|/control|/cancel|/bundle|/pin|/rerun|/files/[A-Za-z0-9._-]+)?$")
SUITE_PATH = re.compile(r"^/api/suites/([A-Za-z0-9][A-Za-z0-9._-]{0,80})(/report|/reopen)?$")
CAMPAIGN_PATH = re.compile(r"^/api/campaigns/([0-9]{8}-[0-9]{6}-[0-9a-f]{6})(/cancel|/repeat|/delete)?$")
MAX_BODY = 65536


class App:
    def __init__(self, runs: Path, max_running: int, worker: list[str] | None = None,
                 catalog: list[str] | None = None) -> None:
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        self.supervisor = Supervisor(Settings(root=runs, command=worker or WORKER, cwd=ROOT, env=env,
                                              max_running=max_running))
        self.catalog_command = catalog or CATALOG
        self.campaigns = Path(runs).parent / "campaigns"
        self.env = env
        self._catalog: bytes | None = None
        self._lock = threading.Lock()

    def catalog(self) -> tuple[int, bytes]:
        with self._lock:
            if self._catalog is None:
                proc = subprocess.run(self.catalog_command, cwd=ROOT, env=self.env, capture_output=True)
                try:
                    obj = json.loads(proc.stdout.decode("utf-8"))
                except ValueError:
                    return 500, _dumps({"error": "không đọc được danh mục"})
                if obj.get("type") == "error":
                    return 500, _dumps({"error": obj.get("message", "lỗi danh mục")})
                self._catalog = _dumps(obj)
            return 200, self._catalog


def _finite(obj):
    """Gửi null cho trình duyệt vì JSON không có Infinity hoặc NaN. Bundle giữ dữ liệu gốc."""
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
    if isinstance(obj, dict):
        return {k: _finite(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_finite(v) for v in obj]
    return obj


def _dumps(obj) -> bytes:
    return json.dumps(_finite(obj), ensure_ascii=False, allow_nan=False).encode("utf-8")


class Handler(http.server.SimpleHTTPRequestHandler):
    app: App

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(STATIC), **kw)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):
        pass

    def _origin_ok(self) -> bool:
        origin = self.headers.get("Origin")
        port = self.server.server_port
        return origin is None or origin in (f"http://127.0.0.1:{port}", f"http://localhost:{port}")

    def _json(self, code: int, obj) -> None:
        body = obj if isinstance(obj, bytes) else _dumps(obj)
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        if n > MAX_BODY:
            raise ValueError("body too large")
        data = json.loads(self.rfile.read(n) or b"{}")
        if not isinstance(data, dict):
            raise ValueError("body must be a JSON object")
        return data


    def do_GET(self):
        url = urlsplit(self.path)
        if url.path == "/api/catalog":
            return self._json(*self.app.catalog())
        if url.path == "/api/runs":
            st = self.app.supervisor.s
            return self._json(200, {"runs": self._runs(), "limits": {"max_running": st.max_running, "keep": st.keep,
                                                                    "max_bytes": st.max_bytes}})
        if url.path == "/api/suites":
            return self._json(200, {"suites": evidence.suites()})
        if url.path == "/api/golden":
            return self._json(200, evidence.golden())
        if url.path == "/api/campaigns":
            return self._json(200, {"campaigns": campaign.listing(self.app.campaigns, self.app.supervisor),
                                    "max_runs": campaign.MAX_RUNS})
        mc = CAMPAIGN_PATH.match(url.path)
        if mc:
            if mc.group(2):
                return self._json(405, {"error": "dùng POST"})
            try:
                return self._json(200, campaign.status(self.app.campaigns, self.app.supervisor, mc.group(1)))
            except KeyError:
                return self._json(404, {"error": "không có campaign này"})
        if url.path == "/api/compare":
            return self._compare(parse_qs(url.query))
        ms = SUITE_PATH.match(url.path)
        if ms:
            try:
                if ms.group(2) == "/reopen":
                    return self._json(405, {"error": "dùng POST"})
                if ms.group(2):
                    body = evidence.suite_report(ms.group(1))
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    return self.wfile.write(body)
                return self._json(200, evidence.suite(ms.group(1)))
            except KeyError:
                return self._json(404, {"error": "không có suite này"})
        m = RUN_PATH.match(url.path)
        if m:
            run_id, tail = m.group(1), m.group(2) or ""
            try:
                if not tail:
                    status = self.app.supervisor.status(run_id)
                    folder = self.app.supervisor.s.root / run_id
                    rerun = evidence.rerun_check(folder) if (folder / "execution.json").is_file() else None
                    return self._json(200, {**status, "rerun": rerun,
                                            "pinned": run_id in self.app.supervisor.pinned()})
                if tail == "/bundle":
                    folder = self.app.supervisor.s.root / run_id
                    if not (folder / "execution.json").is_file():
                        raise KeyError(run_id)
                    return self._json(200, evidence.bundle_files(folder, bundles.verify))
                if tail == "/events":
                    after = int(parse_qs(url.query).get("from", ["0"])[0])
                    return self._events(run_id, after)
                if tail.startswith("/files/"):
                    return self._file(run_id, tail[len("/files/"):])
            except KeyError:
                return self._json(404, {"error": "không có run này"})
            return self._json(405, {"error": "dùng POST"})
        if url.path.startswith("/api/"):
            return self._json(404, {"error": "không có API này"})
        name = url.path.lstrip("/") or "index.html"
        if name not in STATIC_FILES:
            return self.send_error(404)
        return super().do_GET()

    def _side(self, ref: str) -> dict:
        kind, ident = compare.parse_ref(ref)
        if kind == "suite":
            return compare.load_suite(ident)
        return compare.load_campaign(campaign.read(self.app.campaigns, ident), self.app.supervisor.s.root)

    def _compare(self, query: dict) -> None:
        try:
            base = self._side((query.get("base") or [""])[0])
            cand = self._side((query.get("cand") or [""])[0])
            return self._json(200, compare.compare(base, cand))
        except KeyError:
            return self._json(404, {"error": "không có lần chạy hoặc campaign này"})
        except ValueError as error:
            return self._json(400, {"error": str(error)})

    def _runs(self) -> list[dict]:
        sup = self.app.supervisor
        pinned = set(sup.pinned())
        out = []
        for r in sup.runs():
            folder = sup.s.root / r["run_id"]
            row = {**r, "pinned": r["run_id"] in pinned}
            if (folder / "execution.json").is_file():
                row.update(evidence.run_summary(folder))
            out.append(row)
        return out

    def _events(self, run_id: str, after: int) -> None:
        stream = self.app.supervisor.events(run_id, after)
        first = next(stream, None)  # Kiểm tra run tồn tại trước khi gửi HTTP header của stream.
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()
        try:
            for line in ([first] if first is not None else []):
                self.wfile.write(line or b"\n")
            for line in stream:
                self.wfile.write(line or b"\n")  # Gửi keep-alive để phát hiện tab đóng khi worker chưa có sự kiện mới.
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            stream.close()

    def _file(self, run_id: str, name: str) -> None:
        folder = self.app.supervisor.s.root / run_id
        path = folder / name
        if name not in BUNDLE_FILES or not (folder / "execution.json").is_file() or not path.is_file():
            return self._json(404, {"error": "không có file này"})
        data = path.read_bytes()
        kind = "application/json" if name.endswith(".json") else "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Content-Disposition", f'attachment; filename="{run_id}-{name}"')
        self.end_headers()
        self.wfile.write(data)


    def do_POST(self):
        if not self._origin_ok():
            return self._json(403, {"error": "origin không được phép"})
        try:
            body = self._body()
        except ValueError as error:
            return self._json(400, {"error": f"JSON không hợp lệ: {error}"})
        url = urlsplit(self.path)
        sup = self.app.supervisor
        if url.path == "/api/runs":
            config = body.get("config", body)
            label = _label(config)
            try:
                run_id = sup.submit({"config": config}, idempotency_key=self.headers.get("Idempotency-Key"),
                                    label=label, parent=body.get("parent_run_id"))
            except RuntimeError as error:
                return self._json(503, {"error": str(error)})
            return self._json(201, {"run_id": run_id})
        if url.path == "/api/campaigns":
            try:
                doc = campaign.create(self.app.campaigns, sup, body, label_of=_label)
            except campaign.CampaignError as error:
                return self._json(400, {"error": str(error)})
            except RuntimeError as error:
                return self._json(503, {"error": str(error)})
            return self._json(201, {"id": doc["id"], "runs": len(doc["items"])})
        mc = CAMPAIGN_PATH.match(url.path)
        if mc and mc.group(2):
            try:
                if mc.group(2) == "/cancel":
                    return self._json(200, campaign.cancel(self.app.campaigns, sup, mc.group(1)))
                if mc.group(2) == "/repeat":
                    doc = campaign.repeat(self.app.campaigns, sup, mc.group(1), label_of=_label)
                    return self._json(201, {"id": doc["id"], "runs": len(doc["items"])})
                campaign.delete(self.app.campaigns, sup, mc.group(1))
                return self._json(200, {"deleted": mc.group(1)})
            except KeyError:
                return self._json(404, {"error": "không có campaign này"})
            except campaign.CampaignError as error:
                return self._json(409, {"error": str(error)})
            except RuntimeError as error:
                return self._json(503, {"error": str(error)})
        ms = SUITE_PATH.match(url.path)
        if ms and ms.group(2) == "/reopen":
            try:
                request = evidence.suite_rerun_request(ms.group(1), str(body.get("case")), int(body.get("seed", 1)))
            except (KeyError, StopIteration, OSError, ValueError):
                return self._json(404, {"error": "không tìm thấy ca này hoặc thư mục ca của suite đã bị xóa"})
            return self._start_rerun(request, f"Mở lại {body.get('case')} seed {body.get('seed', 1)}", None)
        m = RUN_PATH.match(url.path)
        if m and m.group(2) == "/rerun":
            folder = sup.s.root / m.group(1)
            if not (folder / "execution.json").is_file():
                return self._json(404, {"error": "không có run này (chỉ mở lại run đã xong)"})
            try:
                request = evidence.rerun_request(folder)
            except KeyError:
                return self._json(409, {"error": "run này không có đủ recipe và checksum để chạy lại"})
            label = (bundles.read(folder).get("execution") or {}).get("label") or m.group(1)
            return self._start_rerun(request, f"Mở lại {label}", m.group(1))
        if m and m.group(2) == "/pin":
            if not (sup.s.root / m.group(1) / "execution.json").is_file():
                return self._json(404, {"error": "không có run này (chỉ ghim run đã xong)"})
            sup.pin(m.group(1), bool(body.get("on", True)))
            return self._json(200, {"pinned": m.group(1) in sup.pinned()})
        if m and m.group(2) in ("/control", "/cancel"):
            try:
                if m.group(2) == "/cancel":
                    return self._json(200, {"state": sup.cancel(m.group(1))})
                return self._json(200, {"state": sup.control(m.group(1), body)})
            except KeyError:
                return self._json(404, {"error": "không có run này"})
            except LookupError as error:
                return self._json(409, {"error": str(error)})
        return self._json(404, {"error": "không có API này"})

    def _start_rerun(self, request: dict, label: str, parent: str | None) -> None:
        try:
            run_id = self.app.supervisor.submit(request, idempotency_key=self.headers.get("Idempotency-Key"),
                                                label=label, parent=parent)
        except RuntimeError as error:
            return self._json(503, {"error": str(error)})
        return self._json(201, {"run_id": run_id})


def _label(config: dict) -> str:
    sc = config.get("scenario") or {}
    faults = " ".join("".join(f) for f in config.get("faults") or [])
    return " ".join(x for x in (f"{sc.get('sid', '')} {sc.get('v', '')}".strip(), faults,
                               config.get("vehicle") or "", f"seed {config.get('seed', 1)}") if x)


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Workbench server: static UI of web/simulation and the run API (replaces "
            "web/simulation/server.py)."
        ),
    )
    parser.add_argument("--port", type=int, default=PORT)
    parser.add_argument("--runs", type=Path, default=RUNS)
    parser.add_argument("--max-running", type=int, default=2, help="N_max: runs at the same time (8 GB: 2)")
    args = parser.parse_args()
    Handler.app = App(args.runs, args.max_running)
    try:
        srv = Server(("127.0.0.1", args.port), Handler)
    except OSError as error:
        raise SystemExit(f"Không mở được cổng {args.port}: {error}. Đổi cổng bằng --port hoặc PP_PORT")
    def stop(*_):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, stop)
    print(f"Path Planner workbench: http://127.0.0.1:{args.port}/  (Ctrl+C để dừng; run đang chạy sẽ bị hủy)",
          flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        Handler.app.supervisor.shutdown()
        srv.server_close()


if __name__ == "__main__":
    main()

"""Server nhỏ cho spec-web: phục vụ file tĩnh và đồng bộ tài liệu với file Markdown.

Chạy:  python3 serve.py            (mặc định http://127.0.0.1:8770/)
       python3 serve.py --port 8771

Tài liệu gốc nằm trong docs/vi/<id>.md. Bản dịch trong docs/en/ chỉ đọc:

GET /api/docs/<id>  trả nội dung md, kèm ETag theo thời điểm sửa file. Gửi If-None-Match
                    trùng ETag thì nhận 304 (web hỏi định kỳ để biết md vừa đổi).
PUT /api/docs/<id>  thân là md mới. Gửi If-Match là ETag lúc web tải; nếu file đã bị sửa ở
                    ngoài sau đó thì trả 409 và không ghi đè.

GET/POST/PUT /api/reviews/<id> đọc, tạo và sửa nhận xét trong spec-web/data/review-comments/<id>.json.
Chỉ nghe trên 127.0.0.1 và dùng thư viện chuẩn.
"""
import argparse
import json
import os
import re
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from review_store import ReviewError, read_reviews, save_review

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(ROOT)
DOCS = Path(PROJECT) / "docs"
DOC_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
EN_DOCUMENT = re.compile(r"/en/(versions\.json|[a-z0-9][a-z0-9-]{0,63}\.md)")
MAX_BODY = 2 * 1024 * 1024
MAX_REVIEW_BODY = 64 * 1024
STATIC_ROOT = Path(ROOT).resolve()
STATIC_PATHS = {
    "index.html", "report.html", "style.css", "reviews.css",
    "app.js", "cards.js", "docmd.js", "diagrams.js", "reviews.js",
    "home", "home/index.html", "technical-documents", "technical-documents/index.html",
}


def doc_path(path):
    m = re.fullmatch(r"/api/docs/([^/?#]+)", path)
    if not m or not DOC_ID.match(m.group(1)):
        return None
    p = str(DOCS / "vi" / (m.group(1) + ".md"))
    return p if os.path.isfile(p) else None


def etag(p):
    return '"%d"' % os.stat(p).st_mtime_ns


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        translation = EN_DOCUMENT.fullmatch(path.partition("?")[0])
        if translation:
            return str(DOCS / "en" / translation.group(1))
        return super().translate_path(path)

    def send_head(self):
        # Chỉ phục vụ trang, tài nguyên và bản xuất. Nhận xét đi qua API.
        target = Path(self.translate_path(self.path)).resolve()
        if EN_DOCUMENT.fullmatch(self.path.partition("?")[0]):
            if target.parent != (DOCS / "en").resolve():
                return self.send_error(404)
            return super().send_head()
        if not target.is_relative_to(STATIC_ROOT):
            return self.send_error(404)
        parts = target.relative_to(STATIC_ROOT).parts
        if parts and parts[0] not in {"en", "dist"} and "/".join(parts) not in STATIC_PATHS:
            return self.send_error(404)
        return super().send_head()

    def end_headers(self):
        # Không cache, để sửa file xong tải lại là thấy ngay.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        if len(args) >= 2 and "/api/docs/" in str(args[0]) and str(args[1]) == "304":
            return  # bỏ log của các lần hỏi định kỳ không có gì mới
        super().log_message(fmt, *args)

    def do_GET(self):
        if self.path.startswith("/api/reviews/"):
            return self.handle_reviews("GET")
        if not self.path.startswith("/api/"):
            return super().do_GET()
        if self.path == "/api/ping":
            # Cho trang mở thẳng từ file:// (origin "null") biết serve.py đang chạy để chuyển sang.
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "null")
            self.send_header("Content-Length", "0")
            return self.end_headers()
        p = doc_path(self.path)
        if not p:
            return self.send_error(404)
        tag = etag(p)
        if self.headers.get("If-None-Match") == tag:
            self.send_response(304)
            self.send_header("ETag", tag)
            return self.end_headers()
        with open(p, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "text/markdown; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("ETag", tag)
        self.end_headers()
        self.wfile.write(data)

    def do_PUT(self):
        if self.path.startswith("/api/reviews/"):
            return self.handle_reviews("PUT")
        p = doc_path(self.path)
        if not p:
            return self.send_error(404)
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > MAX_BODY:
            return self.send_error(413)
        data = self.rfile.read(length)
        data.decode("utf-8")  # từ chối nếu không phải UTF-8
        expected = self.headers.get("If-Match")
        if expected and expected != etag(p):
            self.send_response(409)
            self.send_header("ETag", etag(p))
            return self.end_headers()
        tmp = p + ".tmp"
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, p)  # ghi nguyên tử: không bao giờ để lại file dở
        self.send_response(204)
        self.send_header("ETag", etag(p))
        self.end_headers()

    def do_POST(self):
        if self.path.startswith("/api/reviews/"):
            return self.handle_reviews("POST")
        self.send_error(404)

    def handle_reviews(self, method):
        doc_id = self.path[len("/api/reviews/"):]
        if not DOC_ID.fullmatch(doc_id) or not doc_path("/api/docs/" + doc_id):
            return self.send_error(404)
        try:
            if method == "GET":
                result = read_reviews(PROJECT, doc_id)
            else:
                if self.headers.get_content_type() != "application/json":
                    raise ReviewError(415, "invalid_review")
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                except ValueError:
                    raise ReviewError(400, "invalid_review")
                if not 0 < length <= MAX_REVIEW_BODY:
                    raise ReviewError(413, "invalid_review")
                try:
                    payload = json.loads(self.rfile.read(length).decode("utf-8"))
                except (ValueError, UnicodeError):
                    raise ReviewError(400, "invalid_review")
                result = save_review(PROJECT, doc_id, payload, create=method == "POST")
            status = 200
        except ReviewError as error:
            status, result = error.status, error.data
        except (OSError, ValueError, KeyError) as error:
            self.log_error("File nhận xét: %s", error)
            status, result = 500, {"error": "review_store_unavailable"}
        data = json.dumps(result, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8770)
    args = ap.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), partial(Handler, directory=ROOT))
    print(f"spec-web: http://127.0.0.1:{args.port}/")
    server.serve_forever()


if __name__ == "__main__":
    main()

"""Lưu nhận xét theo báo cáo trong spec-web/data/review-comments/."""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory


REVIEW_DIR = Path("spec-web/data/review-comments")


class ReviewError(Exception):
    def __init__(self, status, code, review=None):
        super().__init__(code)
        self.status = status
        self.data = {"error": code}
        if review is not None:
            self.data["review"] = review


def read_reviews(project, doc_id):
    path = Path(project) / REVIEW_DIR / (doc_id + ".json")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"report": doc_id, "nextNumber": 1, "reviews": []}
    if (
        not isinstance(data, dict)
        or data.get("report") != doc_id
        or type(data.get("nextNumber")) is not int
        or not isinstance(data.get("reviews"), list)
    ):
        raise ValueError("File nhận xét không đúng định dạng")
    return data


def lock_file(file):
    # Hai tiến trình serve.py cùng workspace cũng phải cấp số và ghi tuần tự.
    if os.name == "nt":
        import msvcrt

        file.seek(0)
        msvcrt.locking(file.fileno(), msvcrt.LK_LOCK, 1)
    else:
        import fcntl

        fcntl.flock(file, fcntl.LOCK_EX)


def validate_anchor(anchor):
    if not isinstance(anchor, dict):
        raise ReviewError(400, "invalid_anchor")
    limits = {"quote": 4096, "excerpt": 4096, "prefix": 64, "suffix": 64}
    for key, limit in limits.items():
        if not isinstance(anchor.get(key), str) or len(anchor[key]) > limit:
            raise ReviewError(400, "invalid_anchor")
    revision = anchor.get("revision")
    start = anchor.get("start")
    multiple = anchor.get("multiple", True)
    if (
        anchor.get("language") not in ("vi", "en")
        or type(start) is not int
        or start < 0
        or type(multiple) is not bool
        or not anchor["quote"].strip()
        or not anchor["excerpt"].strip()
        or (revision is not None and
            (not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{64}", revision)))
    ):
        raise ReviewError(400, "invalid_anchor")
    return {
        **{key: anchor[key] for key in (*limits, "language", "start")},
        "revision": revision,
        "multiple": multiple,
    }


SEVERITIES = {"major", "minor", "question"}  # Lớn, Nhỏ, Câu hỏi


def save_review(project, doc_id, payload, create):
    if not isinstance(payload, dict):
        raise ReviewError(400, "invalid_review")
    review_id = payload.get("id")
    body = payload.get("body")
    # Khi sửa, có thể chỉ đổi trạng thái đã xong mà không gửi lại nội dung.
    has_body = create or "body" in payload
    resolved = payload.get("resolved")
    resolution = payload.get("resolution")
    severity = payload.get("severity")
    if (
        not isinstance(review_id, str) or not re.fullmatch(r"[0-9a-f]{32}", review_id)
        or (has_body and (not isinstance(body, str) or len(body) > 6000 or not body.strip()))
        or (resolved is not None and type(resolved) is not bool)
        or (resolution is not None and (not isinstance(resolution, str) or len(resolution) > 2000))
        or (severity is not None and severity not in SEVERITIES)
        or (not create and not has_body and resolved is None and severity is None)
    ):
        raise ReviewError(400, "invalid_review")
    body = body.strip() if has_body else None
    anchor = validate_anchor(payload.get("anchor")) if create else None
    if not create and has_body and type(payload.get("version")) is not int:
        raise ReviewError(400, "invalid_review")

    folder = Path(project) / REVIEW_DIR
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / (doc_id + ".json")
    with (folder / ("." + doc_id + ".lock")).open("a+b") as lock:
        lock_file(lock)
        data = read_reviews(project, doc_id)
        reviews = data["reviews"]
        review = next((item for item in reviews if item["id"] == review_id), None)
        timestamp = datetime.now(timezone.utc).isoformat()
        if create:
            if review:
                if review["body"] == body and review["anchor"] == anchor:
                    return data  # Yêu cầu tạo gửi lại sau lỗi kết nối.
                raise ReviewError(409, "review_changed", review)
            review = {
                "id": review_id,
                "number": data["nextNumber"],
                "version": 1,
                "anchor": anchor,
                "body": body,
                "severity": severity or "minor",
                "createdAt": timestamp,
                "updatedAt": timestamp,
            }
            reviews.append(review)
            data["nextNumber"] += 1
        else:
            if not review:
                raise ReviewError(404, "review_missing")
            changed = False
            if has_body and review["body"] != body:
                if payload["version"] != review["version"]:
                    raise ReviewError(409, "review_changed", review)
                review["body"] = body
                changed = True
            if resolved is not None and bool(review.get("resolved")) != resolved:
                # Đổi trạng thái không cần khớp phiên bản: bấm hai lần cho cùng kết quả.
                review["resolved"] = resolved
                if resolved:
                    review["resolvedAt"] = timestamp
                else:
                    review.pop("resolvedAt", None)
                changed = True
            if severity is not None and review.get("severity") != severity:
                review["severity"] = severity
                changed = True
            if resolution is not None and review.get("resolution") != resolution.strip():
                review["resolution"] = resolution.strip()
                changed = True
            if not changed:
                return data  # Lưu lại cùng nội dung không tăng phiên bản.
            review.update(version=review["version"] + 1, updatedAt=timestamp)

        with TemporaryDirectory(dir=folder) as temp_dir:
            temp_path = Path(temp_dir) / path.name
            temp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            temp_path.replace(path)
    return data


def resolve_reviews(project, doc_id, numbers, resolved=True, resolution=None):
    """Đánh dấu xong hoặc mở lại các nhận xét theo số thứ tự, qua cùng khoá và cách ghi."""
    data = read_reviews(project, doc_id)
    by_number = {item["number"]: item for item in data["reviews"]}
    missing = [n for n in numbers if n not in by_number]
    if missing:
        raise ReviewError(404, "review_missing")
    for n in numbers:
        payload = {"id": by_number[n]["id"], "resolved": resolved}
        if resolution is not None:
            payload["resolution"] = resolution
        data = save_review(project, doc_id, payload, create=False)
    return data


if __name__ == "__main__":
    # Dùng từ dòng lệnh, ví dụ:
    #   python3 spec-web/review_store.py resolve adas-functions 1 5 6 --note "Đã sửa trong bản mới"
    #   python3 spec-web/review_store.py reopen adas-functions 3
    import argparse

    parser = argparse.ArgumentParser(description="Đánh dấu nhận xét đã xong hoặc mở lại")
    parser.add_argument("action", choices=["resolve", "reopen"])
    parser.add_argument("doc")
    parser.add_argument("numbers", nargs="+", type=int)
    parser.add_argument("--note", help="Ghi chú đã xử lý thế nào")
    args = parser.parse_args()
    project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    result = resolve_reviews(project, args.doc, args.numbers, args.action == "resolve", args.note)
    open_count = sum(1 for item in result["reviews"] if not item.get("resolved"))
    print(f"{args.doc}: {len(result['reviews'])} nhận xét, còn mở {open_count}")

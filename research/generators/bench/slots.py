"""Giới hạn số tiến trình bench chạy cùng lúc trên máy 8 GB (mặc định 2, PP_LAB_SLOTS đổi được).

Mỗi slot là một file khóa trong build/lab/.slots; khóa tự nhả khi tiến trình kết thúc, kể cả khi lỗi.
Dùng chung cho quick bench và mọi lần chạy nặng của lab (sinh dữ liệu MLP): `with slots.hold(n): ...`.
"""

import contextlib
import fcntl
import os
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DIR = ROOT / "build" / "lab" / ".slots"


def total() -> int:
    return max(1, int(os.environ.get("PP_LAB_SLOTS", "2")))


@contextlib.contextmanager
def hold(count: int = 1, label: str = ""):
    """Chờ tới khi giữ được `count` slot (count ≤ tổng slot), rồi nhả khi ra khỏi khối."""
    count = min(max(1, count), total())
    DIR.mkdir(parents=True, exist_ok=True)
    held, waited = [], False
    try:
        while len(held) < count:
            for i in range(total()):
                if len(held) == count:
                    break
                path = DIR / f"slot{i}"
                if any(h[1] == path for h in held):
                    continue
                f = open(path, "a+")
                try:
                    fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except OSError:
                    f.close()
                    continue
                f.seek(0)
                f.truncate()
                f.write(f"{os.getpid()} {label}\n")
                f.flush()
                held.append((f, path))
            if len(held) < count:
                for f, _ in held:  # Nhả hết rồi thử lại, để hai tiến trình cùng cần nhiều slot không khóa nhau.
                    fcntl.flock(f, fcntl.LOCK_UN)
                    f.close()
                held = []
                if not waited:
                    print(f"Waiting for a bench slot ({count} of {total()})", flush=True)
                    waited = True
                time.sleep(2.0)
        yield
    finally:
        for f, _ in held:
            fcntl.flock(f, fcntl.LOCK_UN)
            f.close()

# PP-PR-064 Web live: run gắn với tab, một run toàn cục, không để lại bằng chứng

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở; đang sửa |
| Mở ngày | 2026-11-17 |
| Requirement bị ảnh hưởng | Không có requirement của planner; lỗi của công cụ kiểm thử |
| Tái hiện | `web/simulation/server.py` tại sim-up-g0 (91e70fc): bấm Chạy hai lần, hoặc đóng tab giữa run |

## 1. Hiện tượng

- Server giữ một biến `RUN` toàn cục; bấm Chạy lần nữa thì lượt cũ bị giết (`server.py:36`, `_run` gọi `kill_current()`).
- Đóng tab là giết run: `_watch` gọi `proc.kill()` khi socket đóng.
- Run live không ghi file nào; không có case_id, không tái lập hay bàn giao được.
- Worker chạy với `stderr=DEVNULL`, và `rt_run.py` chuyển stdout của thư viện sang stderr: mọi traceback bị mất.

## 2. Nguyên nhân

Vòng đời của run gắn với kết nối HTTP của trình duyệt. Server không có định danh run, không có thư mục kết quả.

Hành vi mô phỏng của web không khác CLI: lần chạy nháp 2026-11-17 với 13 lượt của golden set (`benchmark/suites/golden.yaml`) cho cùng behaviour checksum qua `rt_run.py` cũ và `eval.runner`. Khác biệt chỉ ở vòng đời và bằng chứng.

## 3. Cách sửa

- Lõi thực thi chung `execution/`: định danh run, bundle ghi tạm rồi đổi tên, supervisor theo `run_id`.
- `eval/live.py` thay `rt_run.py`; dựng ca bằng `eval.case` như CLI; dùng observer hook của harness.
- `workbench/server.py` thay `web/simulation/server.py`; `web/serve.py` chuyển tiếp qua HTTP.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

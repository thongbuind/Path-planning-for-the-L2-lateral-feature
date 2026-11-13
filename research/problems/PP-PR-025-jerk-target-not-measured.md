# PP-PR-025 Bên chấm không tính performance target jerk ngang PP-SWR-004

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-13 |
| Requirement bị ảnh hưởng | PP-SWR-004; Software Qualification Test Specification 8.2 (dòng "Jerk ngang của HWA: đỉnh và RMS"), 9.1 bước 3 |
| Tái hiện | Đọc mã: `eval/metrics.py` không tạo `Target("PP-SWR-004", …)`; mọi `results.jsonl` (ví dụ `build/suites/speed3-fork-j4`) không có target PP-SWR-004 |

## 1. Hiện tượng

- Software Qualification Test Specification 8.2 liệt kê jerk ngang của HWA (đỉnh và RMS) là performance target của PP-SWR-004.
- `eval.metrics.evaluate` chỉ chấm giới hạn jerk của path (PP-SWR-003) và ghi `jerk_vehicle_r79_max` làm thông tin. Không lần chạy nào có target PP-SWR-004.
- Hệ quả: trang B6 Comfort của dashboard và bước 3 của so sánh kỹ thuật (9.1) thiếu chỉ số jerk.

## 2. Nguyên nhân

Bên chấm chưa cài chỉ số này. Không phải lỗi của planner.

## 3. Cách sửa

Chưa quyết định. Hướng cần xét: thêm `Target("PP-SWR-004", "Jerk ngang của path khi HWA lái, đỉnh")` và một target RMS trong `eval/metrics.py`, đo trên path như PP-SWR-003, rồi thêm PP-SWR-004 vào `COMFORT_TARGETS` của `eval/report_html.py`.

## 4. Xác nhận

Chưa có.

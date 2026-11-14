# PP-PR-025 Bên chấm không tính performance target jerk ngang PP-SWR-004

| Mục | Nội dung |
|---|---|
| Trạng thái | Đóng; xác nhận ở 20261113-1803-suite-regression-3c31309 |
| Mở ngày | 2026-11-13 |
| Requirement bị ảnh hưởng | PP-SWR-004; Software Qualification Test Specification 8.2 (dòng "Jerk ngang của HWA: đỉnh và RMS"), 9.1 bước 3 |
| Tái hiện | Đọc mã: `eval/metrics.py` không tạo `Target("PP-SWR-004", …)`; mọi `results.jsonl` (ví dụ `build/suites/speed3-fork-j4`) không có target PP-SWR-004 |

## 1. Hiện tượng

- Software Qualification Test Specification 8.2 liệt kê jerk ngang của HWA (đỉnh và RMS) là performance target của PP-SWR-004.
- `eval.metrics.evaluate` chỉ chấm giới hạn jerk của path (PP-SWR-003) và ghi `jerk_vehicle_r79_max` làm thông tin. Không lần chạy nào có target PP-SWR-004.
- Hệ quả: trang B6 Comfort của dashboard và bước 3 của so sánh kỹ thuật (9.1) thiếu chỉ số jerk.
- Kiểm lại 2026-11-13: dòng "Tốc độ quay vô lăng RMS" (chỉ số phụ cho PP-SWR-004, vòng kín) của 8.2 cũng chưa được tính. `eval/presentation.py` (`FLEX_TARGETS`) và `eval/compare.py` (nhóm "Cảm nhận người lái") đã liệt kê PP-SWR-004 nên luôn trống. Các dòng khác của 8.2 đã có.

## 2. Nguyên nhân

Bên chấm chưa cài chỉ số này. Không phải lỗi của planner.

## 3. Cách sửa

Chọn 2026-11-13. Ba target PP-SWR-004, chỉ khi HWA lái:

| Target | Cách đo |
|---|---|
| Jerk ngang lớn nhất của path (trung bình 0,5 s) | Như PP-SWR-003, lớn nhất qua mọi path HWA |
| Jerk ngang RMS của path 0–1 s | RMS của jerk trên lưới 0,1 s, đoạn 0–1 s của mọi path HWA |
| Tốc độ quay vô lăng RMS, vòng kín | Góc bánh thật của xe trong simulator nhân tỉ số lái, đạo hàm theo bước mô phỏng |

| Chỗ sửa | Nội dung |
|---|---|
| `eval/metrics.py` | Ba target; `_steering_rate_rms` |
| `eval/report_html.py` | PP-SWR-004 vào `COMFORT_TARGETS` (trang B6) |
| `tests/eval/test_slice_s1.py`, `test_intervention_metrics.py` | Có đủ ba target trên cua S1b ngắn, đỉnh bằng giá trị PP-SWR-003; không có target khi HWA không lái |

## 4. Xác nhận

Chưa có lần chạy chính thức. Lần chạy nháp 2026-11-13, VP-0, seed 1:

| Ca | Đỉnh [m/s³] | RMS 0–1 s [m/s³] | Vô lăng RMS [rad/s] |
|---|---|---|---|
| S1 a | 0,179 | 0,057 | 0,007 |
| S1 c | 0,700 | 0,262 | 0,030 |
| S2 a | 0,171 | 0,028 | 0,008 |

Xác nhận chính thức [20261113-1803-suite-regression-3c31309](../runs/20261113-1803-suite-regression-3c31309/report.md): Performance target PP-SWR-004 có ở mục targets của mọi ca HWA.

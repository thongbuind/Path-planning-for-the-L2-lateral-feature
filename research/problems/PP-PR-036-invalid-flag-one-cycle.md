# PP-PR-036 F16 a, c: message valid = false lệch 1–2 chu kỳ so với mất message

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-13 |
| Requirement bị ảnh hưởng | PP-SWR-130 |
| Tái hiện | [20261113-1803-suite-regression-3c31309](../runs/20261113-1803-suite-regression-3c31309/report.md): F16 a (lane model), F16 c (FunctionRequests) trên S1a, S1c |

## 1. Hiện tượng

| Ca | Chu kỳ khác ca tham chiếu | Trượt đầu tiên |
|---|---|---|
| F16 a, lane model `valid = false` 0,5 s | 2 | 4,233 s |
| F16 c, FunctionRequests `valid = false` 0,5 s | 1 | 4,033 s |
| F16 b, IMU qualifier FAULT | Đạt | — |

## 2. Nguyên nhân

Chưa phân tích. Giả thuyết: planner cập nhật thời điểm nhận hoặc bộ đếm timeout bằng message `valid = false`, nên mốc hết timeout hoặc mốc hồi phục lệch một chu kỳ so với khi message không tới.

## 3. Cách sửa

- So hai log (ca lỗi và ca tham chiếu) quanh chu kỳ khác đầu tiên.
- Nếu đúng giả thuyết: T1 bỏ message `valid = false` trước mọi cập nhật thời gian, như chưa nhận (định nghĩa "Hợp lệ" của Interface Control Document).
- Nếu lệch do cách bên chấm dựng ca tham chiếu: sửa `sim/faults/channel.py`.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

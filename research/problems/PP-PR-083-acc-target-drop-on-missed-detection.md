# PP-PR-083 ACC chạy thử bỏ mục tiêu khi cảm biến sót một khung, LeadTarget `valid = false`

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã sửa, chờ hồi quy |
| Mở ngày | 2026-11-23 |
| Requirement bị ảnh hưởng | PP-SWR-172, 176 |
| Tái hiện | 20261123-1254-suite-regression-54307f1: PP-SWR-172 trượt 48 lượt (S22, F25), PP-SWR-176 trượt 16 lượt (F25); `S22-a-VP-0-3020d44fb647`, seed 1 |

## 1. Hiện tượng

- Lượt trượt mới sau khi PP-PR-036 bỏ bộ lọc `valid = false` ở harness. Lần hồi quy trước không có.
- Trong S22 a, LeadTarget `valid = false` 1 đến 2 khung, khoảng 1,5 s một lần, dù xe trước vẫn ở đó. Planner coi như mất message (Interface Control Document 5.9, PP-SWR-130) và giữ FOLLOW; bên chấm thấy FOLLOW trong chu kỳ LeadTarget không dùng được.

## 2. Nguyên nhân

Phía đánh giá. Mô hình cảm biến vật thể thỉnh thoảng sót xe trước một khung (ObjectList hợp lệ, danh sách rỗng). `LeadSelector` của ACC chạy thử (`sim/stand_ins/acc.py`) bỏ mục tiêu ngay khung đó, nên perception chạy thử gửi LeadTarget `valid = false`. Bộ track của ACC thật giữ mục tiêu qua vài khung sót. Trước PP-PR-036, harness bỏ khung `valid = false` nên hiện tượng bị che.

Đã loại trừ bằng lượt nháp: không do PP-TS-020 V1a (`ay_margin_hwa` = 0 vẫn trượt), không do cổng vào LCC, không do bản sửa phép chiếu của PP-PR-080.

## 3. Cách sửa

Đã sửa 2026-11-23: `LeadSelector` giữ mục tiêu tới `KEEP_S` khi mục tiêu bị sót và không có ứng viên khác, hoặc khi tạm thời không có ObjectList. `tests/sim` 147 test đạt.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| Lượt nháp 2026-11-23 | S22 a, b, c VP-0, VP-1 và F25 a, e đạt PP-SWR-172, 176. Còn PP-SWR-171 ở S22 e (PP-PR-079) và PP-SWR-170 ở F25 c, d (PP-PR-074), có từ trước |

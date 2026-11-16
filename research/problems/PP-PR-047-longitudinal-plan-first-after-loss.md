# PP-PR-047 S14 d: message đầu tiên sau khi mất LongitudinalPlan bị bỏ theo kiểm counter

| Mục | Nội dung |
|---|---|
| Trạng thái | Đóng (xác nhận 20261114-2252-suite-regression-98a122b) |
| Mở ngày | 2026-11-14 |
| Requirement bị ảnh hưởng | PP-SWR-153; PP-SWR-129, 130 |
| Tái hiện | [20261114-1952-suite-regression-0776bad](../runs/20261114-1952-suite-regression-0776bad/report.md): S14 d, mọi profile, seed 1 |

## 1. Hiện tượng

- PP-SWR-153 trượt 1 chu kỳ ở cả 6 lượt S14 d (mất LongitudinalPlan 2 s khi vào cung). Ở [20261114-1021-suite-regression-d7ed84c](../runs/20261114-1021-suite-regression-d7ed84c/report.md) đạt.

## 2. Nguyên nhân

- Kiểm counter E2E mới (PP-PR-035): sau 2 s mất, bước counter của message đầu tiên lớn hơn MaxDeltaCounter (WRONGSEQUENCE), nên planner bỏ message đó và dùng phương án dự phòng thêm một chu kỳ. Bên chấm coi message đó hợp lệ.
- Khi message đang giữ đã quá timeout, input đã coi như mất; bỏ thêm message đầu chỉ làm chậm hồi phục. AUTOSAR E2E Profile 1, 2 cũng nới MaxDeltaCounter mỗi lần gọi không có dữ liệu mới.

## 3. Cách sửa

- T1: khi message đang giữ đã quá timeout, nhận message mới đầu tiên có bước ≥ 1 (đồng bộ lại). Bước 0 (lặp, đứng yên) vẫn bỏ.
- Interface Control Document 1.12 mục 4 ghi quy tắc này.
- Kiểm cục bộ: S14 d đạt 153; F15 b, c vẫn đạt 130 (0 chu kỳ khác). Unit test `test_resync_after_timeout`.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| [20261114-2252-suite-regression-98a122b](../runs/20261114-2252-suite-regression-98a122b/report.md) | S14 d hết trượt PP-SWR-153 (6 lượt); F15 b, c đạt PP-SWR-130 |

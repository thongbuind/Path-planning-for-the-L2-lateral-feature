# PP-PR-050 S14 c: độ cong đầu xa của path đổi trong một chu kỳ

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-14 |
| Requirement bị ảnh hưởng | PP-SWR-100 |
| Tái hiện | [20261114-1952-suite-regression-0776bad](../runs/20261114-1952-suite-regression-0776bad/report.md): S14 c, mọi profile, seed 1; có từ [20261114-1021-suite-regression-d7ed84c](../runs/20261114-1021-suite-regression-d7ed84c/report.md) |

## 1. Hiện tượng

- PP-SWR-100 0,141 m tại 12,36 s ở cả 6 lượt; giá trị như ở d7ed84c.
- Log VP-0: một chu kỳ duy nhất, độ cong điểm cuối 0,00494 → 0,00449 1/m, lệch lớn nhất ở t = 2,9 s; chu kỳ sau lại ≤ 0,05 m.

## 2. Nguyên nhân

Chưa phân tích. Giả thuyết: lần T10 kiểm lại sau T4 cắt phần xa khi tốc độ của LongitudinalPlan đổi (S14 c có ACC đọc LateralLimits và xe khác lấn làn).

## 3. Cách sửa

Phân tích log: tốc độ trong Trajectory và lần cắt của T10 tại chu kỳ đó.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

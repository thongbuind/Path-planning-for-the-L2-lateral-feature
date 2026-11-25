# PP-PR-085 S1b b, c, f với ACC bỏ qua LateralLimits: PP-SWR-100 trượt

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-25 |
| Requirement bị ảnh hưởng | PP-SWR-100 |
| Tái hiện | [20261125-0007-study-PP-TS-031-074a928](../runs/20261125-0007-study-PP-TS-031-074a928/summary.md), phần test của PP-T7: `quintic_duration` trượt ở S1b b, S1b c (vòng kín và vòng hở), S1b f, mỗi ca một seed; `qp_jerk_admm` trượt ở S1b b |

## 1. Hiện tượng

- Các ca là cua gắt hơn aysmax, ACC không giảm tốc theo LateralLimits (`acc: ignore_limits`).
- Path đổi giữa hai chu kỳ quá ngưỡng của PP-SWR-100 (đoạn 0–1 s).
- Có ở bản đang giao (`quintic_duration`), nên không do generator lab.

## 2. Nguyên nhân

Chưa phân tích.

## 3. Cách sửa

Chưa làm.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

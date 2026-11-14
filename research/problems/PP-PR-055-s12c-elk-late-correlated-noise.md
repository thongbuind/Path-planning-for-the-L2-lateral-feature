# PP-PR-055 S12 c: ELK bắt đầu trễ 0,8 s vì T2 loại frame nhất quán

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã sửa, chờ hồi quy chính thức |
| Mở ngày | 2026-11-14 |
| Requirement bị ảnh hưởng | PP-SWR-088, 085, 100 |
| Tái hiện | [20261114-2153-suite-regression-71fb7c1](../runs/20261114-2153-suite-regression-71fb7c1/report.md): S12 c seed 1, 6 profile; PP-SWR-088 0,18–0,20 m (0776bad: 0,90 m) |

## 1. Hiện tượng

- REQUEST ELK (xe ngược chiều) lúc 4,384 s; ELK chỉ bắt đầu lúc 5,227 s, DTLE −0,32 m, khoảng cách ngang tới xe kia 0,19 m.
- Seed 2 đến 5 không bị. Kết quả seed 1 đổi theo cách trình biên dịch gộp FMA (thư viện chỉ khác chuỗi `pp_version()`): ca nằm sát ngưỡng.

## 2. Nguyên nhân

- Log T2 (bản build `-ffp-contract=off` có in): L1 bị loại suốt 1 s tới khi R1 nhận. Nhiều frame chỉ lệch 2,0–2,8σ so với bộ nhớ, nhưng vẫn bị loại theo quy tắc của PP-PR-048 bản 1: ứng viên được cập nhật bằng frame mới nhất, mà nhiễu mưa tương quan theo thời gian nên frame luôn gần frame trước hơn bộ nhớ.
- Vạch phía can thiệp bị loại thì planner không bắt đầu ELK (PP-SWR-092).

## 3. Cách sửa

- T2: bỏ quy tắc PP-PR-048 bản 1; thay bằng giữ bộ nhớ trước tranh chấp làm vị trí cũ cho R2 (Software Detailed Design 1.18).
- Unit test `test_slow_drift_within_the_check_is_taken` (trượt với quy tắc bản 1).
- Nháp seed 1: S12 c 0,90 m (cả bản build `-ffp-contract=off`), seed 2, 3 đạt; G01 trên S1c đạt, trên S4c chỉ còn PP-SWR-032; F06 a, b, c, e, F01 c, F02 b, F03 a, S7 c, S12 a, d, S1b a, F04 a lúc LKA đạt.
- Đề xuất riêng (chưa làm): build thư viện với `-ffp-contract=off` để kết quả SIL không đổi theo cách gộp FMA.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

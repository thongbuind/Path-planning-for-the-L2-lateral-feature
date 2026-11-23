# PP-PR-081 S19 f: không báo `lane_too_narrow` khi làn hẹp dần trong lúc LCC lái

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-23 |
| Requirement bị ảnh hưởng | PP-SWR-063; PP-SWR-062 |
| Tái hiện | Lượt nháp 2026-11-23, S19 f (biến thể mới, SQTS 1.51), VP-5, seed 1, thư viện của cây làm việc có PP-TS-020 V1a |

## 1. Hiện tượng

- VP-5 (2,5 m tính cả gương) vào LCC ở làn 3,5 m; từ s = 150 m làn hẹp dần còn 2,5 m trong 100 m, mép phải dời vào.
- PP-SWR-063: chỉ 0,9 % số chu kỳ có path hợp lệ báo `lane_too_narrow` khi khoảng trống thật nhỏ hơn `free_space_min`. Ngưỡng là 100 %.
- PP-SWR-051 đạt (DLC nhỏ nhất 0,009 m), PP-SWR-050 lớn nhất 0,35 m.
- S19 b (làn 2,5 m từ đầu) báo đúng: PP-SWR-063 đạt.

## 2. Nguyên nhân

Chưa phân tích. Giả thuyết: T2 giữ bề rộng làn cũ khi biên phải dời vào chậm (`ref_rate`, `T_confirm`), nên khoảng trống planner tính còn lớn hơn thật.

## 3. Cách sửa

Chưa làm.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

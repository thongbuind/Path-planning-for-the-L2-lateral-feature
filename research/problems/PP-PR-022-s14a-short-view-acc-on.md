# PP-PR-022 S14a với tầm nhìn ngắn: ACC đọc LateralLimits lại rời làn xa hơn

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-12 |
| Requirement bị ảnh hưởng | PP-SWR-051, 151, 152 |
| Tái hiện | Lần chạy nháp `build/matrix/Q4` (Q4, VP-0, seed 1), cây làm việc chưa commit |

Đây là ghi nhận để điều tra, chưa phải kết luận benchmark.

## 1. Hiện tượng

| Tầm nhìn [m] | ACC bỏ qua: DLC nhỏ nhất [m] | ACC đọc LateralLimits: DLC nhỏ nhất [m] | v nhỏ nhất khi đọc [m/s] |
|---|---|---|---|
| 80 | 0,80 | 0,75 | 20,0 |
| 20 | 0,29 | −6,51 | 20,4 |
| 10 | −0,71 | −12,4 | 20,5 |

- Khi ACC giảm tốc theo LateralLimits, xe rời làn xa hơn khi ACC bỏ qua, dù tốc độ thấp hơn.
- Mức 10 m và 20 m dưới `t_view_hwa`; trong xe thật HWA đã trả lái.

## 2. Nguyên nhân

Chưa điều tra. Cần xem `v_max`, `distance` của LateralLimits theo thời gian, và tương tác giữa giảm tốc với path khi tầm nhìn ngắn. Có thể cùng gốc với PP-PR-021.

## 3. Cách sửa

Chưa có.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

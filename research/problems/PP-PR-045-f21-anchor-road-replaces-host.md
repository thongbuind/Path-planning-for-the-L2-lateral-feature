# PP-PR-045 F21 c, d: đường của anchor thay hình học của ca chủ

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-14 |
| Requirement bị ảnh hưởng | Không có requirement nào trượt; độ phủ của F21 trên ca chủ (PP-SWR-147, 148, 051) |
| Tái hiện | [20261114-1021-suite-regression-d7ed84c](../runs/20261114-1021-suite-regression-d7ed84c/report.md): F21-c-S1c, F21-d-S1c |

## 1. Hiện tượng

| Ca | Độ cong cung, 1014d20 | Độ cong cung, d7ed84c |
|---|---|---|
| F21-c-S1c | 0,004 1/m (R = 250 m của S1c) | 0,001 1/m (R = 1000 m) |
| F21-d-S1c | 0,004 1/m | 0,002 1/m (R = 500 m) |

- Ca mang tên S1c nhưng không còn là cua S1c (a_y cần chạm aysmax).
- F21-c-S1c trượt 051 ở 1014d20 (−0,81 đến −1,13 m) và đạt ở d7ed84c. Kết quả đạt này không phải bằng chứng planner giữ làn trên cua S1c.

## 2. Nguyên nhân

- `eval/generate.py` (commit 010011f): khi `road_file` của anchor khác đường danh định, đường của anchor thay đường của ca chủ.
- F21 c, d dùng `F21c.xodr`, `S1b.xodr` để có mép đường phải đúng mô tả F21(c) và cua R = 500 m của F21(d). Ca cũ trên S1c không có mép đường nào, nên cũng không đúng mô tả F21(c).

## 3. Cách sửa

Bên chấm, không đổi planner:

- Giữ hình học (planView) của ca chủ; anchor chỉ thêm lớp biên cần cho lỗi (mép đường phải của F21(c)).
- F21(d) trên ca chủ: giữ độ cong của ca chủ; R = 500 m chỉ áp khi chạy F21(d) đơn lẻ.
- Chạy lại F21 trên S1c sau khi sửa. Ghi kết quả cũ và mới vào đây; không chỉnh tiếp sau khi thấy kết quả.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

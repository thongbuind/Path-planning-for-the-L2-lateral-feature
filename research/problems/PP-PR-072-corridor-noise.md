# PP-PR-072 Hành lang can thiệp đi theo nhiễu lane model

| Mục | Nội dung |
|---|---|
| Trạng thái | Đóng (e395662) |
| Mở ngày | 2026-11-18 |
| Requirement bị ảnh hưởng | PP-SWR-094, 085 |
| Tái hiện | [20261118-1546-suite-regression-edb02b8](../runs/20261118-1546-suite-regression-edb02b8/report.md) |

## 1. Hiện tượng

S4c, S12 b, G01 trên S4c: path nhảy theo nhiễu của lane model, xe lắc và DLC giảm lại.

## 2. Nguyên nhân

Mỗi frame phù hợp được nhận nguyên, biên dịch vào được nhận ngay, lúc T2 coast hành lang lấy bộ nhớ của T2.

## 3. Cách sửa

Lọc hành lang theo `corridor_tau`, biên dịch vào phải giữ `corridor_toward`, lúc T2 coast hành lang đi tiếp bằng ego-motion.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| 20261118-2030-suite-regression-e3158a5 | PP-SWR-094 ở nhóm nhiễu còn 0 |

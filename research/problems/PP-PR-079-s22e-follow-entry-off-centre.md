# PP-PR-079 S22 e: vào FOLLOW khi xe trước lệch tâm quá giới hạn

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-19 |
| Requirement bị ảnh hưởng | PP-SWR-171 |
| Tái hiện | [20261118-2030-suite-regression-e3158a5](../runs/20261118-2030-suite-regression-e3158a5/report.md), S22 e, sáu profile, seed 1 |

## 1. Hiện tượng

PP-SWR-171 (Safety, SG-01): 6 đến 11 lần vào FOLLOW khi điều kiện vào không thỏa, ở cả sáu profile của S22 e. Cột Kiểm chứng của PP-SWR-171 là S23, nên S22 e không tính vào kết luận. Lỗi này đã có ở baseline `edb02b8`.

## 2. Nguyên nhân

Chưa phân tích. Ghi nhận ban đầu: ca có xe trước lệch tâm 0,8 đến 0,9 m. Bên chấm coi điều kiện vào thỏa khi xe trước lệch dưới 1,25 lần giới hạn M1 (giới hạn M1 là nhỏ hơn của 0,8 m và khoảng trống mỗi bên trừ `dlc_offset_min`). Giả thuyết: planner kiểm V3 theo vị trí xe trước so với xe mình, còn bên chấm kiểm thêm theo giới hạn M1, và hai cách này khác nhau ở làn hẹp (PP-ASM-025, 026 chưa được mentor xác nhận).

## 3. Cách sửa

Chưa làm. Cần phân biệt lỗi planner với lỗi hiểu requirement ở bên chấm. Nếu là cách hiểu điều kiện vào, câu hỏi 4 và 5 trong cau-hoi-mentor-hai-planner.md quyết định hướng sửa.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| 20261118-2030-suite-regression-e3158a5 | Còn trượt ngoài phạm vi, BLOCKER, 6 lượt |

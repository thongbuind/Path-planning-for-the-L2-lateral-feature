# PP-PR-077 PP-SWR-094 trượt ở các ca ELK vì xe làn bên, ngoài phạm vi chấm

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-19 |
| Requirement bị ảnh hưởng | PP-SWR-094 |
| Tái hiện | [20261118-2030-suite-regression-e3158a5](../runs/20261118-2030-suite-regression-e3158a5/report.md), mục "Trượt ngoài phạm vi chấm của ca", PP-SWR-094 |

## 1. Hiện tượng

PP-SWR-094 trượt ở 146 lượt ngoài phạm vi, giá trị 0,100 đến 0,276 m, ngưỡng 0,1 m (DLC thật giảm lại sau điểm nhỏ nhất của lần can thiệp).

| Nhóm | Số lượt | Giá trị lớn nhất [m] |
|---|---|---|
| S8 (ELK, xe vượt làn bên) | 79 | 0,205 |
| S7 (xe ngược chiều) | 37 | 0,214 |
| S21 | 11 | 0,153 |
| S12 c, d | 11 | 0,172 |
| S8b | 8 | 0,276 |

- Cột Kiểm chứng của PP-SWR-094 chỉ ghi S4, S5, S6, S20, F24, nên các lượt này không tính vào kết luận. Trong phạm vi, PP-SWR-094 đạt ở mọi lượt (khoảng 700 lượt F, S4, S5, S6, S13, S20, G01).
- Số lượt ngoài phạm vi tăng từ 97 (baseline `edb02b8`) lên 146 sau khi LKA, ELK chuyển sang hai pha (PP-TS-026 V4, `e395662`). PP-TS-026 chỉ chấm S4, S5, S6, S20, F24 nên không thấy phần tăng này.
- S8b c nặng nhất: 0,198 đến 0,276 m ở cả sáu profile.

## 2. Nguyên nhân

Chưa phân tích. Chưa xem log của ca nào. Giả thuyết:

1. Pha về tâm của ELK vì xe làn bên dùng `T_return_object` = 2 s và kéo xe quá tâm, rồi path kéo lại.
2. Độ lệch `offset_truck` thay đổi khi xe lớn đi ngang hàng, làm đích thay đổi giữa lần can thiệp.

Nghi vấn về phạm vi: câu requirement áp cho mọi lần LKA, ELK, còn cột Kiểm chứng chỉ có năm mã. Một trong hai phải đổi, và quyết định này thuộc người phụ trách.

## 3. Cách sửa

Chưa làm. Cần quyết một trong hai hướng:

- Mở rộng cột Kiểm chứng của PP-SWR-094 sang S7, S8, S8b, S12, S21 và sửa planner (cần plan mới, kể cả PP-TS-026).
- Giữ phạm vi hiện tại và ghi giới hạn vào Assumptions and dependencies của Software Requirements Specification.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| 20261118-2030-suite-regression-e3158a5 | 146 lượt trượt ngoài phạm vi |

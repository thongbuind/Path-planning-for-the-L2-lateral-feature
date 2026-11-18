# PP-PR-074 Vào lại FOLLOW chậm sau lỗi LeadTarget

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-18 |
| Requirement bị ảnh hưởng | PP-SWR-170 |
| Tái hiện | [20261118-1546-suite-regression-edb02b8](../runs/20261118-1546-suite-regression-edb02b8/report.md) |

## 1. Hiện tượng

F25: PP-SWR-170 trượt 8 lần.

## 2. Nguyên nhân

Sau lỗi, điều kiện M1, M2 và độ dài vết chưa đạt ngay ở chu kỳ bên chấm coi là đủ điều kiện.

## 3. Cách sửa

Đã giữ vết qua frame lỗi (e3158a5), giảm từ 14 xuống 8. Phần còn lại cần xem bên chấm có nên tính M1, M2 không.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| 20261118-2030-suite-regression-e3158a5 | Còn trượt, mức MINOR |

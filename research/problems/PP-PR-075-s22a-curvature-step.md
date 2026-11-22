# PP-PR-075 S22 a: độ cong đổi quá ngưỡng giữa hai path

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-18 |
| Requirement bị ảnh hưởng | PP-SWR-102 |
| Tái hiện | [20261118-1546-suite-regression-edb02b8](../runs/20261118-1546-suite-regression-edb02b8/report.md) |

## 1. Hiện tượng

S22 a VP-0: PP-SWR-102 tỉ số 1,37.

- Trên [hồi quy bb08d77](../runs/20261119-0948-suite-regression-bb08d77/report.md), VP-0 seed 1 chuyển FOLLOW → COAST tại 3,234 s, rồi COAST → FOLLOW tại 3,259 s. `path_valid` giữ `true` qua cả hai lần chuyển.
- Khi vào lại FOLLOW, điểm 2,9 s của path mới lệch độ cong 0,001649 1/m so với path cũ nội suy thêm 25 ms. Ngưỡng của đoạn này là 0,0012 1/m. Lane model không báo tầm nhìn ở hai chu kỳ này.

## 2. Nguyên nhân

Chưa xác định khâu tạo bước nhảy. Cần so độ cong tại điểm 2,9 s trước T4, sau T4 và sau lần T10 kiểm cuối.

## 3. Cách sửa

Chưa làm.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| 20261118-2030-suite-regression-e3158a5 | Còn trượt, BLOCKER |
| [20261119-0948-suite-regression-bb08d77](../runs/20261119-0948-suite-regression-bb08d77/report.md) | Còn trượt, tỉ số 1,374 tại 3,259 s |

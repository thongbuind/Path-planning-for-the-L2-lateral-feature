# PP-PR-075 S22 a: độ cong đổi quá ngưỡng giữa hai path

| Mục | Nội dung |
|---|---|
| Trạng thái | Đóng, xác nhận ở 20261122-0758-suite-regression-591e3de |
| Mở ngày | 2026-11-18 |
| Requirement bị ảnh hưởng | PP-SWR-102 |
| Tái hiện | [20261118-1546-suite-regression-edb02b8](../runs/20261118-1546-suite-regression-edb02b8/report.md) |

## 1. Hiện tượng

S22 a VP-0: PP-SWR-102 tỉ số 1,37.

- Trên [hồi quy bb08d77](../runs/20261119-0948-suite-regression-bb08d77/report.md), VP-0 seed 1 chuyển FOLLOW → COAST tại 3,234 s, rồi COAST → FOLLOW tại 3,259 s. `path_valid` giữ `true` qua cả hai lần chuyển.
- Khi vào lại FOLLOW, điểm 2,9 s của path mới lệch độ cong 0,001649 1/m so với path cũ nội suy thêm 25 ms. Ngưỡng của đoạn này là 0,0012 1/m. Lane model không báo tầm nhìn ở hai chu kỳ này.

## 2. Nguyên nhân

T4 dùng tầm nhìn của reference line FOLLOW, kết thúc ở xe trước. Điểm 2,9 s nằm ngoài tầm nhìn này. Bên chấm vẫn so điểm đó trong đoạn thời gian chung vì lane model đã mất.

## 3. Cách sửa

Từ `ecfe00e`, T4 lấy tầm nhìn từ lane model cả khi dựng path FOLLOW. Khi lane model mất, T4 kiểm hết đoạn thời gian chung của hai path.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| 20261118-2030-suite-regression-e3158a5 | Còn trượt, BLOCKER |
| [20261119-0948-suite-regression-bb08d77](../runs/20261119-0948-suite-regression-bb08d77/report.md) | Còn trượt, tỉ số 1,374 tại 3,259 s |
| [20261122-0758-suite-regression-591e3de](../runs/20261122-0758-suite-regression-591e3de/report.md) | S22 a VP-0 seed 1 đạt PP-SWR-102, tỉ số lớn nhất 0,900. PP-SWR-100, 101 và 174 đạt |

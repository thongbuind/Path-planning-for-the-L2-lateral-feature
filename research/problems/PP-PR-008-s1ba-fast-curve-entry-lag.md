# PP-PR-008 S1ba ở 130 km/h: path T7 A trễ so với a_y cần lúc vào cua

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở, đã tìm nguyên nhân; sửa qua PP-TS-003 |
| Mở ngày | 2026-11-11 |
| Requirement bị ảnh hưởng | PP-SWR-006 |
| Tái hiện | 20261111-1443-suite-regression-ef8bf4b, `S1b-a-VP-*` (speed 36,1 m/s, ACC off), seed 1, 2 |

## 1. Hiện tượng

- Cả 6 profile: a_y của path trong 0–1 s thấp hơn aysmax − epsilon_ay tới 0,53 m/s² ở điểm có a_y cần > aysmax.
- Ở 90 km/h (S1ba anchor) đạt.

## 2. Nguyên nhân

- Clothoid vào cua ở 130 km/h: a_y cần tăng khoảng 2,4 m/s³, dưới giới hạn jerk của path.
- T7 A tạo quintic tới trạng thái cuối theo thời lượng, nên a_y của path tăng chậm hơn a_y cần: lúc điểm 1 s phía trước cần 2,84 m/s², path chỉ có 1,97 m/s².

## 3. Cách sửa

T7 C bám a_y cần vì ràng buộc a_y nằm trong cùng bài toán. Lần chạy nháp cùng ca: PP-SWR-006 đạt (+0,04 m/s²), nhưng PP-SWR-100 trượt theo PP-PR-006. Quyết định ở PP-TS-003.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

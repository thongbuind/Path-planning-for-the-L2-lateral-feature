# PP-PR-003 Đưa về giữa khi xe đang hướng ra ngoài: lốp đè vạch (S2c, S2d)

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-11 |
| Requirement bị ảnh hưởng | PP-SWR-051, 052 |
| Tái hiện | 20261111-1024-matrix-M1-b9e5d4d: S2c (24/24 lần chạy), S2d (4/24), cả ACC `off` và `on` |

## 1. Hiện tượng

- S2c: HWA bật khi xe lệch 0,5 m, góc 2° hướng ra ngoài, 90 km/h. Xe tiếp tục ra tới khoảng 1,0 m rồi mới quay về. DLC nhỏ nhất −0,19 m (VP-0) đến −0,50 m (VP-5).
- S2d: lệch 0,4 m phía ngoài cua trái R = 500 m. DLC nhỏ nhất −0,02 m ở VP-5.
- M1 không tính các lần này là trượt, vì cột Kiểm chứng của SRS không gán PP-SWR-051 cho S2.

## 2. Nguyên nhân

Chưa phân tích. Giả thuyết:

- Vận tốc ngang lúc bật là 25·sin 2° ≈ 0,87 m/s. Với a_y thêm vào ≤ 0,5 m/s², cần khoảng 1,7 s và 0,76 m để dừng trôi ra.
- Điều kiện vào HWA (ADAS Function Specification mục 7: DLC, lệch tâm, góc lệch) lẽ ra chặn trạng thái đầu này. Nếu đúng, kịch bản S2c nằm ngoài điều kiện vào, và cần xét lại kịch bản hoặc requirement chứ không phải planner.

## 3. Cách sửa

Chưa chọn. Trước hết kiểm trạng thái đầu của S2c, S2d theo ngưỡng `hwa_entry_*`.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

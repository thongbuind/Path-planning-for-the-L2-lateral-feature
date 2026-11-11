# PP-PR-007 S14a ở 130 km/h: xe ra khỏi đường sau đoạn vượt aysmax, PP-SWR-051 chấm khi đã ra ngoài

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở, đã tìm nguyên nhân; cần quyết định về requirement |
| Mở ngày | 2026-11-11 |
| Requirement bị ảnh hưởng | PP-SWR-051 |
| Tái hiện | 20261111-1443-suite-regression-ef8bf4b, `S14-a-VP-*` (speed 36,1 m/s, ACC on), seed 1, 2 |

## 1. Hiện tượng

- Cả 6 profile: DLC nhỏ nhất −19 m (xe ra hẳn khỏi đường); PP-SWR-100 0,073 m.
- Ca sinh từ biên của dải tốc độ: 130 km/h vào cua R = 200 m, a_y cần 6,5 m/s².

## 2. Nguyên nhân

- Để vào cua với a_y ≤ aysmax cần v ≤ 22,4 m/s. Giảm từ 36,1 m/s ở 2 đến 3 m/s² cần khoảng 200 m; camera chỉ thấy khoảng 80 m.
- Khối dọc giảm tốc từ 3,5 s. Planner bật cờ giới hạn từ 4,0 s và giữ a_y ở aysmax (đúng PP-SWR-005, 006, 007). Xe trôi ra ngoài 3 m trước khi tốc độ đủ thấp.
- PP-SWR-051 chỉ chấm ở chu kỳ có a_y cần ≤ aysmax. Các chu kỳ đó tới khi xe đã ở ngoài làn, hệ quả của đoạn vượt giới hạn trước đó.

## 3. Cách sửa

Không phải lỗi path; là điều kiện áp dụng của requirement. Cần quyết định:

| Hướng | Nội dung |
|---|---|
| A | SRS: PP-SWR-051 không chấm từ lúc vượt aysmax tới khi xe đã về hẳn trong làn |
| B | Giữ SRS; ghi ca này là giới hạn đã biết của camera (ODD, R171 5.3.7.1.1.1) |

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

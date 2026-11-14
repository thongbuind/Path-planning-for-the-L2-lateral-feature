# PP-PR-034 Path HWA vẫn hợp lệ khi IMU hoặc góc lái mất, không hợp lệ

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã sửa điều kiện xuất path, chờ hồi quy chính thức |
| Mở ngày | 2026-11-13 |
| Requirement bị ảnh hưởng | PP-SWR-142 |
| Tái hiện | [20261113-1803-suite-regression-3c31309](../runs/20261113-1803-suite-regression-3c31309/report.md): F12 c, e; F17 a; F16 b |

## 1. Hiện tượng

| Ca | Input | Chu kỳ còn path hợp lệ (ngưỡng: chỉ chu kỳ đầu) |
|---|---|---|
| F12 c | IMU ngừng gửi | 38 (cả đoạn mất) |
| F12 e | Góc lái ngừng gửi | 39 |
| F17 a | IMU CRC sai | 18 |
| F16 b | IMU qualifier FAULT | 142 trượt ngoài phạm vi |
| F12 d, F17 b | Tốc độ | 142 đạt |

## 2. Nguyên nhân

- `planner/src/pp_planner.c`: HWA chỉ bắt buộc tốc độ (`forward`, ghi chú "Speed is required (PP-SWR-142)").
- IMU mất thì `yaw_rate = 0.0` và path HWA vẫn được tạo. Góc lái không được kiểm cho HWA.
- `chassis_valid` (IMU và góc lái) chỉ dùng cho `can_start`, `can_continue` của LKA, ELK.

Nguồn liên quan:

| Văn bản | Mục | Nội dung |
|---|---|---|
| R171 | 5.4.1, 5.4.2 | Phát hiện hư hỏng; chấm dứt hỗ trợ an toàn, giảm dần nếu an toàn; báo tài xế |
| R79 | 5.6.2.2.4 | Hư hỏng của hệ thống phải báo bằng tín hiệu nhìn thấy |
| Software Qualification Test Specification | 4.6 | Path không hợp lệ: controller giữ lệnh cuối, EPS trả lái trong 1 s |

- Phần giảm dần của R171 5.4.2 do controller và EPS làm, nên planner đặt `path_valid = false` ngay vẫn phù hợp.
- Mốc "một chu kỳ" của PP-SWR-142 là nhóm tự thống nhất; văn bản không cho số.

## 3. Cách sửa

- IMU, tốc độ và góc lái hợp lệ là điều kiện chung cho mọi path. Khi thiếu input, vẫn xuất đủ thông điệp theo chu kỳ và đặt `path_valid = false`, `active_function = NONE`.
- Nếu thiết kế muốn HWA chạy tiếp khi mất IMU (ví dụ dùng ego-motion thay yaw rate), thì đó là đổi PP-SWR-142: cần quyết định trước khi sửa code.

Quan sát kèm, chưa rõ có cùng nguyên nhân: F17 b trên S1c (CRC tốc độ sai) trượt 051, DLC −0,87 đến −1,29 m ở 3 lần chạy. Cần log để biết xe rời làn trong lúc path không hợp lệ hay sau khi path hồi phục.

## 4. Xác nhận

PP-SWR-142 đạt ở 42/42 lượt có điều kiện chấm trong tập F12, F16 và F17 của hồi quy cục bộ. Test qua `pp_step` kiểm mất IMU, góc lái không hợp lệ và phục hồi với mẫu mới.

| Run ID | Kết quả |
|---|---|

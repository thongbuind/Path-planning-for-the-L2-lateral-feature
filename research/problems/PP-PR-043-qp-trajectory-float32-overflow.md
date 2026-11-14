# PP-PR-043 Bản QP xuất tọa độ vô cực ở B0

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã sửa, chờ hồi quy chính thức |
| Mở ngày | 2026-11-14 |
| Liên quan | B0 C2.robust, C2.finite, PP-SWR-043, PP-TS-003 |

## 1. Hiện tượng

B0 C2 cấp `VehicleStateEstimate` hợp lệ với `lateral_velocity` ở hai đầu dải float32. Bản QP tạo `pose.y` vô cực ở các điểm 11–12 của chu kỳ đầu tiên.

## 2. Nguyên nhân và cách sửa

Giá trị double còn hữu hạn trong T7 có thể vượt miền float32 khi T11 đổi tọa độ sang kiểu dữ liệu của interface. T11 kiểm miền biểu diễn trước khi ép kiểu. Khi lỗi xảy ra, planner gửi trajectory không hợp lệ và `active_function = NONE`. Bản QP xóa trạng thái khởi tạo lại của bộ giải sau đường lỗi.

## 3. Xác nhận

Test T11 kiểm một tọa độ hữu hạn vượt `FLT_MAX`. B0 cục bộ của bản QP đạt C2 sau khi sửa và cho phép chạy tiếp 10 lượt SIL đối chiếu. PP-TS-003 tiếp tục theo dõi lựa chọn generator.

# PP-PR-066 HUD web: tỉ lệ đóng góp lái gán 0,5 khi có lực tài xế

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-17 |
| Requirement bị ảnh hưởng | Không; chỉ hiển thị |
| Tái hiện | Đọc code `web/simulation/tools/rt_run.py` tại sim-up-g0 |

## 1. Hiện tượng

Khi EPS đang theo lệnh hệ thống và tài xế có lực tay lái dưới mức override, HUD hiện tỉ lệ đóng góp lái của hệ thống là 0,5.

## 2. Nguyên nhân

EPS chạy thử không có mô-men motor để so với mô-men tài xế. `rt_run.py` gán cứng `system_share = 0.5` cho trường hợp này. Người xem dễ hiểu thành đóng góp vật lý 50 %.

## 3. Cách sửa

Chỉ hiển thị đại lượng có định nghĩa vật lý trong mô hình (`Eps.system_steering_share` theo trạng thái điều khiển và bàn giao). Không có đại lượng thì không hiện tỉ lệ.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

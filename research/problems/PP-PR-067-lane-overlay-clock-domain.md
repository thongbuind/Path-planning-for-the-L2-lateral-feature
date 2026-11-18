# PP-PR-067 Overlay lane model trên web tra tư thế xe bằng stamp của đồng hồ camera

| Mục | Nội dung |
|---|---|
| Trạng thái | Đóng (eb73eee) |
| Mở ngày | 2026-11-17 |
| Requirement bị ảnh hưởng | Không; chỉ hiển thị |
| Tái hiện | Lần chạy nháp 2026-11-17, seed 1: S1 c, S1 c + F14 a, b, c |

## 1. Hiện tượng

Overlay lane model đặt theo tư thế xe tại thời điểm trên trục thời gian toàn cục bằng stamp của đồng hồ camera.

| Ca | Lệch thời gian lớn nhất [ms] | Lệch vị trí overlay lớn nhất [m] |
|---|---|---|
| S1 c, đồng hồ lý tưởng | 0,0 | 0,000 |
| S1 c + F14 a, b, c | 0,1 | 0,025 |

## 2. Nguyên nhân

`rt_run.py` tìm `log.t_us` (thời gian toàn cục) bằng `header.stamp_us` của lane model, là thời điểm chụp trên đồng hồ camera ECU (`_camera_stamp`). Hai miền đồng hồ lệch nhau dưới F14 và trước lần đồng bộ đầu tiên của chế độ realism (tới ±10 ms theo SQTS 4.2).

## 3. Cách sửa

Đổi stamp sang thời gian toàn cục bằng `clocks["camera"].to_global` trước khi tra tư thế.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| eb73eee; `tests/eval/test_live_view.py` | Stamp camera đổi về thời gian toàn cục trước khi tra tư thế xe |

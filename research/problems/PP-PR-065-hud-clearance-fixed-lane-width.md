# PP-PR-065 HUD web: khoảng hở tính với nửa bề rộng làn cố định

| Mục | Nội dung |
|---|---|
| Trạng thái | Đóng (eb73eee) |
| Mở ngày | 2026-11-17 |
| Requirement bị ảnh hưởng | Không; chỉ hiển thị, không vào chấm |
| Tái hiện | Lần chạy nháp 2026-11-17, seed 1: S1 a, S6b a, S6b d |

## 1. Hiện tượng

Khoảng hở hai bên trên HUD (`dl`, `dr`) khác DLC của evaluator ở làn có hình học riêng:

| Ca | Lệch lớn nhất HUD so với evaluator, trái / phải [m] |
|---|---|
| S1 a (làn không đổi) | 0,000 / 0,000 |
| S6b a | 0,075 / 0,075 |
| S6b d (làn ego mở rộng về bên phải trong cua) | 0,075 / 1,425 |

## 2. Nguyên nhân

`rt_run.py` tính `half_lane = 0.5 * road.lane_width` một lần và trừ `d` của trục trước. Evaluator (`metrics._dlc`) lấy biên làn theo hình học tại `s`, theo làn xe đang ở (`lane_relative`), tính cả vạch sơn.

## 3. Cách sửa

HUD lấy khoảng hở bằng cùng hàm hình học với evaluator, không tự tính.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| eb73eee; `tests/eval/test_live_view.py` | Khoảng hở theo biên làn thật tại bánh trước, kể cả làn đổi bề rộng |

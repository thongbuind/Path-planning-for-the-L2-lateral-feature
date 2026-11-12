# PP-PR-019 ELK mép đường mất path ở tick hủy

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã sửa, chờ xác nhận chính thức |
| Mở ngày | 2026-11-12 |
| Requirement bị ảnh hưởng | PP-SWR-037 |
| Tái hiện | ELK ROAD_EDGE đang ACTIVE với hai mép đo được, không có vạch. Khối ADAS gửi OFF hợp lệ |

## 1. Hiện tượng

Khi ADAS rút yêu cầu, geometry đủ cho path bàn giao vẫn có nhưng planner có thể báo path không hợp lệ.

## 2. Nguyên nhân

Việc dựng reference line của mép đường dựa vào state mới của ELK. Tick nhận OFF bỏ qua hành lang trước khi T9 chuyển sang NONE.

## 3. Cách sửa

Xét hành lang mép đường cho tick bàn giao nếu pha trước là ELK ACTIVE do ROAD_EDGE. Kiểm lại biên đo trực tiếp theo PP-SWR-047.

## 4. Xác nhận

Unit test API `test_elk_road_edge_keeps_path_on_cancellation_tick` kiểm NONE với PathStatus và Trajectory hợp lệ sau khi nhận OFF.

# PP-PR-068 SQTS 4.1 mô tả chế độ thời gian thực chưa có trong code

| Mục | Nội dung |
|---|---|
| Trạng thái | Đóng 2026-11-19: hướng A |
| Mở ngày | 2026-11-17 |
| Requirement bị ảnh hưởng | Không có requirement của planner; Software Qualification Test Specification 4.1 |
| Tái hiện | Tìm `udp_multicast`, `python-can` trong `sim/`, `eval/`, `tools/`, `web/simulation/` tại sim-up-g0 |

## 1. Hiện tượng

Software Qualification Test Specification 4.1, dòng "Chế độ thời gian thực": mỗi ECU một tiến trình, socket thật, bus CAN ảo `udp_multicast` của `python-can`, để kiểm tích hợp. Code không có chế độ này; `requirements.txt` không có `python-can`. Bus CAN ảo hiện có (`sim/can/`) chạy trong tiến trình của chế độ tất định.

## 2. Nguyên nhân

Chế độ được thiết kế trong tài liệu nhưng chưa được cài.

## 3. Cách sửa

Ba hướng, người phụ trách quyết:

| Hướng | Việc |
|---|---|
| A | Sửa SQTS 4.1: ghi chế độ này chưa triển khai |
| B | Bỏ dòng này khỏi SQTS 4.1 |
| C | Cài đặt chế độ (ước lượng 10 ngày công trở lên) |

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| Không có lần chạy | Software Qualification Test Specification 1.50, mục 4.1: dòng "Chế độ thời gian thực" ghi chưa triển khai. Hướng C để backlog |

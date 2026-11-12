# PP-PR-013 ELK hoàn tất trước khi yêu cầu rút LKA tới planner

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã cài PP-TS-010 V1, chờ SIL hai chức năng cùng yêu cầu |
| Mở ngày | 2026-11-11 |
| Requirement bị ảnh hưởng | PP-SWR-033, ADAS Function Specification mục 9 |
| Tái hiện | Phân tích chuỗi message khi cả hai chức năng còn REQUEST cùng phía tại tick ELK COMPLETED |

## 1. Hiện tượng

Planner có thể chọn LKA ở tick ELK hoàn tất theo PP-SWR-033. Khối ADAS rút LKA cùng phía sau khi đọc PathStatus, nên LKA có thể đã được công bố ACTIVE trong khoảng chuyển message.

## 2. Nguyên nhân

`lka_phase` và `elk_phase` phân biệt chức năng hoàn tất. Quy tắc rút yêu cầu tại COMPLETED vẫn cần vòng truyền PathStatus rồi FunctionRequests trước khi thay đổi input mà planner xét.

## 3. Cách sửa

Chọn thời điểm rút yêu cầu theo PP-TS-010. Giữ PP-SWR-033.

## 4. Xác nhận

Kiểm chuỗi hai chức năng cùng phía và khác phía với độ trễ message. Quan sát cả trạng thái yêu cầu lẫn pha điều khiển tại tick hoàn tất.

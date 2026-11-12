# PP-PR-011 S6 chỉ có mép đường xung đột với điều kiện ELK

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã cài PP-TS-007 V1, chờ xác nhận chính thức |
| Mở ngày | 2026-11-11 |
| Requirement bị ảnh hưởng | PP-SWR-047, 086 |
| Tái hiện | Đối chiếu S6 (a, b) trong Software Qualification Test Specification mục 5 với Software Requirements Specification 8.2. Phát hiện qua phân tích |

## 1. Hiện tượng

S6 (a, b) yêu cầu ELK khi chỉ có mép đường. PP-SWR-047 chặn chọn ELK nếu tâm làn chỉ suy được từ mép đường. Trong điều kiện này không có lần ELK để đo DTLE theo PP-SWR-086.

## 2. Nguyên nhân

Điều kiện cấm gom mép đường đo trực tiếp của làn đang chạy với các biên ngoài làn dùng để suy tâm làn khi perception suy giảm. Bảng bài thử S6 bao gồm mép đường đo trực tiếp không kèm vạch.

F21(c) ghi chỉ còn mép đường phải trong 5 s. Để kiểm cả hai nhánh sau thay đổi, ca này cần xác định mép đó là biên ngoài hành lang làn đang chạy. Nếu cùng một mép vừa là biên trực tiếp đủ điều kiện vừa được dùng làm biên xa của F21(c), hai ca sẽ yêu cầu phản ứng khác nhau từ cùng input.

## 3. Cách sửa

Chốt điều kiện ELK ở mép đường theo PP-TS-007 và cập nhật đồng bộ requirement, điều kiện khả dụng và các ca kiểm chứng liên quan.

## 4. Xác nhận

Kiểm S6 có và không có vạch theo phạm vi đã duyệt. Kiểm ELK vẫn bị chặn với tâm làn suy từ biên xa trong trường hợp F21.

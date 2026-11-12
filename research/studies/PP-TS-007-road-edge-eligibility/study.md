# PP-TS-007 Điều kiện ELK ở mép đường không có vạch

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã quyết |
| Mở ngày | 2026-11-11 |
| Khóa ngày | — |
| Quyết định ngày | 2026-11-11 |
| Liên quan | PP-PR-011; PP-SWR-047, 085, 086; ADAS Function Specification mục 6, 7; S6, F21 |

## 1. Câu hỏi

Khi nào biên đường đo trực tiếp cung cấp đủ thông tin để ELK mép đường hoạt động mà vẫn xác định được vùng trở về?

## 2. Phương án

| ID | Phương án | Hệ quả |
|---|---|---|
| V0 | Giữ PP-SWR-047 hiện tại | Chỉ chấm ELK mép đường khi có vạch làn mình đủ tin để dựng tâm làn. S6 chỉ có mép đường nằm ngoài phạm vi kiểm chứng hiện hành |
| V1 | Cho phép ELK với mép đường đo trực tiếp và hành lang đủ tin | Cần chốt điều kiện quan sát biên đối diện hoặc bề rộng làn và phạm vi sửa requirement. Vẫn chặn dùng biên xa suy ra trong trường hợp F21 |

## 3. Cách đánh giá

- Phân tích điều kiện khả dụng theo nguồn hình học, gồm mất cả hai vạch, mép đường đo trực tiếp và mép suy ra khi cảm biến suy giảm.
- Dùng S6 để kiểm DTLE và DLC phía đối diện. Dùng F21 hoặc input tương đương để kiểm việc chặn ELK với biên xa suy ra.
- Chốt tiêu chí theo requirement và test trước khi chạy so sánh.

## 7. Quyết định

Người dùng chọn V1. Mép phía nguy hiểm phải MEASURED, confidence ≥ `conf_edge`. Cần thêm biên đối diện đủ tin hoặc bề rộng làn đã nhớ. F21 vẫn chặn ELK với biên xa suy ra. Làm rõ trong Interface Control Document nếu planner dùng `elk_reason` để chọn biên.

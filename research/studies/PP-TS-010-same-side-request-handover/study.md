# PP-TS-010 Thời điểm rút LKA cùng phía với ELK

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã quyết |
| Mở ngày | 2026-11-11 |
| Khóa ngày | — |
| Quyết định ngày | 2026-11-12 |
| Liên quan | PP-PR-013, PP-SWR-030, 033, ADAS Function Specification mục 9 |

## 1. Câu hỏi

Khối ADAS nên rút LKA cùng phía lúc nào để tránh một lần LKA phát sinh khi ELK kết thúc?

## 2. Phương án

| ID | Phương án | Hệ quả |
|---|---|---|
| V0 | Rút LKA khi nhận ELK COMPLETED | Quy tắc hiện hành. Trong thời gian vòng truyền message, planner còn thấy LKA REQUEST |
| V1 | Rút LKA cùng phía khi nhận ELK ACTIVE. Duy trì chặn cùng phía trong lúc ELK hoạt động và áp điều kiện tái kích hoạt khi hoàn tất | Cho phép hai yêu cầu ban đầu cùng tồn tại. Planner có thể quan sát việc rút trước tick ELK hoàn tất. Cần quy định hành vi khi ELK bị hủy |

## 3. Cách đánh giá

- Kiểm ưu tiên ELK khi hai chức năng cùng yêu cầu.
- Kiểm số lần LKA bắt đầu khi ELK hoàn tất, khả năng chuyển sang LKA khác phía và hành vi khi ELK bị hủy giữa chừng.

## 7. Quyết định

Người dùng duyệt V1. Giữ LKA cùng phía ở STANDBY khi ELK ACTIVE. Khi ELK COMPLETED, áp điều kiện tái kích hoạt cho phía vừa can thiệp. LKA khác phía vẫn được xét theo PP-SWR-033.

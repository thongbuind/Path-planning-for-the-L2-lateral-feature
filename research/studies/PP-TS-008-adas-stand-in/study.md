# PP-TS-008 Nguồn FunctionRequests cho SIL LKA, ELK

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã quyết |
| Mở ngày | 2026-11-11 |
| Khóa ngày | — |
| Quyết định ngày | 2026-11-11 |
| Liên quan | PP-ADR-014; ADAS Function Specification mục 5 đến 9; Software Qualification Test Specification mục 4.1, 7, 8.2 |

## 1. Câu hỏi

SIL sẽ tạo FunctionRequests bằng cách nào để tái hiện được kích hoạt và phân biệt lỗi kích hoạt với lỗi planner?

## 2. Phương án

| ID | Phương án | Hệ quả |
|---|---|---|
| V0 | HWA theo lịch, LKA và ELK OFF | Baseline |
| V1 | Kịch bản phát LKA, ELK REQUEST theo lịch | Kiểm planner với chuỗi input cố định. Cần một nguồn yêu cầu khác để kiểm S10, P2, P3 |
| V2 | Stand-in tính DLC, TLC, ý định và nguy cơ từ các tín hiệu được cấp | Dùng được cho S10, P2, P3. Chế độ tín hiệu đo và chế độ tín hiệu lý tưởng cho phép so sánh thời điểm kích hoạt. Có thể cấp chuỗi yêu cầu cố định cho bài thử arbitration vòng hở |

## 3. Cách đánh giá

- Kiểm chuỗi trạng thái theo ADAS Function Specification mục 9.1, gồm hủy yêu cầu và tái kích hoạt.
- Đo kích hoạt thừa và chênh thời điểm giữa hai chế độ theo Software Qualification Test Specification mục 8.2 khi có bộ chạy tương ứng.
- Đánh giá planner qua FunctionRequests thực nhận, Trajectory, PathStatus và ground truth của bên đánh giá.

## 7. Quyết định

Người dùng chọn V2. Chấm planner ở chế độ B. Dùng A so thời điểm kích hoạt. Giữ chuỗi yêu cầu định sẵn cho kiểm thử có input cần kiểm soát. Khối ADAS nhận phản hồi từ PathStatus theo PP-ADR-014.

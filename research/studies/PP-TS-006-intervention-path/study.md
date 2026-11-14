# PP-TS-006 Kỹ thuật tạo path can thiệp LKA, ELK

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-11 |
| Khóa ngày | — |
| Quyết định ngày | — |
| Liên quan | PP-SWR-031, 032, 080 đến 090, 100 đến 102, 110 đến 117; Software Detailed Design mục 10, 12 |

## 1. Câu hỏi

Dùng kỹ thuật nào để tạo path can thiệp từ trạng thái xe lúc kích hoạt và đưa xe vào vùng an toàn với ngân sách a_y, jerk của từng chức năng?

## 2. Phương án

| ID | Phương án | Cách cài | Ghi chú |
|---|---|---|---|
| V0 | Baseline HWA | T7 chưa có path LKA, ELK | Mốc chức năng |
| V1 | Quintic theo thời lượng | Dùng T7 A cho path can thiệp ở cả hai bản build HWA | Kiểm ngân sách và biên trước khi chọn thời lượng, sau đó kiểm path xuất |
| V2 | QP với ràng buộc can thiệp | Dùng bộ giải T7 C với đích ngang, biên theo phía nguy hiểm và giới hạn của LKA, ELK | Cần xử lý xe đã ngoài corridor lúc kích hoạt và giới hạn trên path xuất |

## 3. Cách đánh giá

| Mục | Nội dung |
|---|---|
| Tiêu chí loại | Các requirement LKA, ELK trong phạm vi ca đã duyệt và hồi quy HWA |
| Xếp hạng | Theo Software Qualification Test Specification mục 9, dùng các target 081, 082, 087 và thời gian tính |
| Điều kiện so sánh | Cùng bản HWA, mô hình driver, stand-in, benchmark, seed, profile và ngân sách chỉnh |
| Bộ chỉnh, bộ kiểm | Định trước trong `plan.yaml` sau khi duyệt phạm vi. Giữ PP-TS-003 độc lập |

## 7. Quyết định

Ngày 2026-11-11, người dùng duyệt tích hợp V1 cho cả hai bản build. `PP_T7` chọn kỹ thuật HWA. V2 giữ trong study để so sánh sau.

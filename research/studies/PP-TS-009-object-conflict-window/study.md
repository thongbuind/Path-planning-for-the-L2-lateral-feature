# PP-TS-009 Cửa sổ dự báo xung đột ELK khi trôi chậm

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã quyết |
| Mở ngày | 2026-11-11 |
| Khóa ngày | — |
| Quyết định ngày | 2026-11-12 |
| Liên quan | PP-PR-012, PP-SWR-088, 089, ADAS Function Specification mục 6, 13 |

## 1. Câu hỏi

Cửa sổ dự báo phải tính thế nào để phát hiện xung đột ở dải v_lat của S7, S8 trong khi vẫn chặn kích hoạt thừa?

## 2. Phương án

| ID | Phương án | Ghi chú |
|---|---|---|
| V0 | Cửa sổ cố định với `t_conflict` 2 s | Baseline đặc tả |
| V1 | `t_conflict` 3 s cho ELK vật thể | Trong dải đã có. Theo phân tích S7(a), phát hiện sớm hơn trước khi xe đi quá 0,3 m qua vạch |
| V2 | Dự báo thời điểm hai bao xe tiến đến khoảng hở nguy hiểm | Dùng khoảng cách ngang và vận tốc dự báo của vật thể. Cần quy định cách giới hạn thời gian ngoại suy |

## 3. Cách đánh giá

- Kiểm tra hình học đồng bộ xe ở S7 và S8 theo protocol trước khi chạy.
- Kiểm khả năng phát hiện xung đột ở v_lat thấp và kích hoạt thừa ở ca gần vạch hoặc xe làn bên không xung đột. Khóa giá trị và phạm vi trước khi thu kết quả.

## 7. Quyết định

Người dùng duyệt V1. Dùng `t_conflict` = 3 s trong stand-in ELK vật thể trước lần chạy S7 và S8.

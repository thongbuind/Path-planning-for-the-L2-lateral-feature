# PP-PR-020 Tick COMPLETED còn lệch khi đối chiếu điều kiện thật

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-12 |
| Requirement bị ảnh hưởng | PP-SWR-032, 090 |
| Tái hiện | S4b(b, c, e), S6(b), VP-0, seed 1. Dùng phép đo bổ sung PP-SWR-032, 090 ngoài cột Kiểm chứng của các neo này |

## 1. Hiện tượng

S4b(b) đạt điều kiện giữ trên ground truth trước tick COMPLETED. S4b(c, e) và S6(b) báo COMPLETED trước khi điều kiện thật giữ đủ. Hai bản build có cùng hành vi.

## 2. Nguyên nhân

T9 xét điều kiện từ geometry ước lượng và tín hiệu chassis. Eval xét cùng giới hạn trên geometry thật và chuyển động thật. Sai lệch vẫn còn ở các ca này sau khi đưa v_y về t0 theo PP-PR-018. Chưa xác định tín hiệu chi phối ở từng tick chuyển ngưỡng.

## 3. Cách xác nhận

Đối chiếu mỗi thành phần của điều kiện kết thúc quanh đầu cửa sổ giữ. Dùng input ICD và ground truth để kiểm sai số của heading, v_lat tại cầu trước và a_y thêm vào. Giữ ngưỡng và các kịch bản đã chốt. Xem PP-TS-012 khi chọn cách xử lý.

# PP-PR-038 ELK có REQUEST nhưng planner không có path can thiệp (F04, S16)

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-13 |
| Requirement bị ảnh hưởng | Kết quả mong đợi của ca; liên quan PP-SWR-030, 047 |
| Tái hiện | [20261113-1803-suite-regression-3c31309](../runs/20261113-1803-suite-regression-3c31309/report.md): F04 a, c trên S5a lúc ELK đang lái (4), S16 (2) |

## 1. Hiện tượng

Bên chấm báo "ELK: có REQUEST nhưng thiếu path can thiệp hợp lệ". F04 a (vạch trái mất ngay) và c (độ tin vạch trái giảm về 0 trong 2 s) ở VP-2 đến VP-5.

## 2. Nguyên nhân

Chưa phân tích. Giả thuyết:
- `can_start` của ELK cần vạch phía đó đáng tin (`pp_intervention_line_trusted`). Mất vạch phía can thiệp thì planner không bắt đầu được.
- Nếu đúng, planner từ chối là hợp với văn bản. Câu hỏi là khối Chức năng ADAS chạy thử có nên gửi REQUEST khi vạch phía đó mất không, và ca có nên mong đợi can thiệp không.

Nguồn liên quan:

| Văn bản | Mục | Nội dung |
|---|---|---|
| EU 2021/646 | Recital (bản text dòng 59) | ELKS không bắt buộc hoạt động khi không có vạch |
| R79 | Annex 8, 3.3.4 | Chỉ thử khi không có vạch nếu hệ thống khai báo làm được |
| ADAS Function Specification | Bảng khả dụng | Biên kém tin thì UNAVAILABLE ở phía đó |
| PP-SWR-046 | — | Chỉ nói tiếp tục khi VehicleStateEstimate mất; chưa nói khi vạch mất giữa lúc ELK đang lái |

S16 (can thiệp lặp, 2 lần chạy) có thể là nguyên nhân khác: cần xem riêng.

## 3. Cách sửa

- Xem log: lúc REQUEST, vạch phía ELK còn không; ELK đã ACTIVE trước khi vạch mất hay chưa.
- Nếu REQUEST tới khi vạch đã mất: sửa khối Chức năng ADAS chạy thử theo bảng khả dụng của ADAS Function Specification (bên chấm).
- Nếu vạch mất giữa lúc ELK đang lái: cần thêm requirement cho trường hợp này (tiếp tục path can thiệp đã tạo, như PP-SWR-046, hay dừng). Quyết định trước khi sửa.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

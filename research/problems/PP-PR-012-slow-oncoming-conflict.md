# PP-PR-012 Cửa sổ xung đột ELK khi trôi chậm

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã cài PP-TS-009 V1; xác nhận một phần: chưa có ca xe ngược chiều không xung đột |
| Mở ngày | 2026-11-11 |
| Requirement bị ảnh hưởng | PP-SWR-088, 089 |
| Tái hiện | Phân tích hình học S7(a), Euro NCAP LSS 7.2.4.3. Giả sử VP-0 và xe mục tiêu đều rộng 1,90 m. Chưa chạy SIL |

## 1. Hiện tượng

S7(a) có thể thiếu REQUEST khi áp cửa sổ `t_conflict` 2 s và giới hạn yêu cầu muộn 0,3 m.

## 2. Nguyên nhân

Tâm xe mục tiêu cách mép trong vạch 1,50 m. Với bề rộng 1,90 m, mép gần của xe mục tiêu cách vạch 0,55 m. Tại thời điểm chồng lấn 10 % bề rộng VP-0, mép xe mình đã qua vạch khoảng 0,74 m. Ở v_lat 0,2 m/s, thời điểm đó cách lúc qua vạch khoảng 3,7 s. `box_margin` 2 m dời thời điểm vào hộp khoảng 0,05 s khi hai xe tiến lại với tốc độ tương đối 40 m/s. Sau khi qua vạch, phải trôi thêm khoảng 0,33 m thì thời điểm vào hộp mới nằm trong 2 s tới. Lúc đó đã quá giới hạn 0,3 m của 089.

## 3. Cách sửa

Chốt hình học xe mục tiêu và quy tắc dự báo theo PP-TS-009 trước khi chạy benchmark. Giữ đồng bộ xe mục tiêu theo Euro NCAP LSS.

## 4. Xác nhận

Kiểm bằng tín hiệu lý tưởng với bài xe ngược chiều trôi chậm. Chấm REQUEST, can thiệp, 088 và hành vi với xe không tạo xung đột.

Xác nhận chính thức [20261113-1803-suite-regression-3c31309](../runs/20261113-1803-suite-regression-3c31309/report.md): S7(a): PP-SWR-088, 089 đạt; PP-SWR-089 đo ở 6 lần chạy.

Đánh giá lại 2026-11-13: chưa đủ điều kiện đóng. Mọi ca S7 trong lần chạy trên đều có xung đột và có can thiệp (PP-SWR-088 đạt, 0,43–1,10 m). Mục 4 còn đòi hành vi với xe không tạo xung đột: chưa có ca nào như vậy trong bộ hồi quy.

# Triển khai Path Planner (đang chờ)

**Trạng thái: chờ.** Tài liệu này sẽ mô tả **cách triển khai** path planner của G1: thuật toán cụ thể cho từng phần, và kỹ thuật lập path được chọn. Việc viết sẽ bắt đầu khi kế hoạch tính năng ở tài liệu Thiết kế tính năng Path Planner đã xong. Hiện tài liệu chỉ giữ các ghi chú và nhận xét về thuật toán, để chúng không bị mất. **Chưa làm gì ở đây.**

**Liên hệ với các tài liệu khác.**

| Tài liệu | Quan hệ với tài liệu này |
|---|---|
| Thiết kế tính năng Path Planner | Cho **kế hoạch tính năng**: làm gì, giới hạn nào, chịu lỗi thế nào. Tài liệu này trả lời **làm bằng cách nào** cho từng mục ở đó |
| Benchmark và Evaluation | Cho kết quả so sánh các kỹ thuật ứng viên, dùng để chọn kỹ thuật chính (T7) |
| Chức năng ADAS | Hàm tính DLC, v_lat, TLC dùng chung với khối ADAS (T6) |

## 1. Ghi chú chờ triển khai

| # | Chủ đề | Mục trong Thiết kế tính năng Path Planner | Cần làm |
|---|---|---|---|
| T1 | Bù trễ | Mục 3 | Thuật toán dời lane model theo stamp lúc chụp bằng ego-motion; xử lý khi stamp bất thường; kiểm chứng bằng quét trễ 0–200 ms và mất đồng bộ đồng hồ; đo độ trễ bộ lọc yaw rate bằng tương quan chéo giữa bản thô và bản đã lọc, rồi ghi thành tham số cấu hình. Cần cẩn thận vì ảnh hưởng trực tiếp tới độ chính xác và an toàn |
| T2 | Đường tham chiếu | Mục 4 | Thuật toán chi tiết cho từng trường hợp: hai vạch; một vạch cộng bề rộng nhớ được; bề rộng thay đổi ở lối ra và nhập làn; vạch kép; chuyển từ vạch L1 sang L2 khi chuyển làn; kiểm tính nhất quán của đường biên ở hai thang thời gian (ngưỡng từng frame, ngưỡng song song và bề rộng), cách xác nhận một thay đổi thật của làn |
| T3 | Lớp dự phòng nhiễu | Mục 4.1 | Đặt số cho giới hạn tốc độ thay đổi tham chiếu và trọng số jerk; cân giữa rung và phản ứng chậm |
| T4 | c0 jump | Mục 4 | Một thuật toán nối path thật êm: dạng đường nối, tốc độ dời tâm, cách giữ ngưỡng liên tục |
| T5 | Kết hợp c2 | Mục 4 | Cách đặt trọng số giữa c2 của camera, r/v và lịch sử path |
| T6 | Trạng thái đầu của path | Mục 4.2 | Ngưỡng chuyển giữa "bắt đầu từ path cũ" và "tính lại từ số đo"; hàm dùng chung với khối ADAS |
| T7 | Kỹ thuật chính | Toàn bộ | Khảo sát và chọn một kỹ thuật, kèm ít nhất một phương án bị loại và lý do (đề bài). Kết quả lấy từ Benchmark và Evaluation |

## 2. Kỹ thuật ứng viên

Đề bài yêu cầu khảo sát và chọn một kỹ thuật, kèm ít nhất một phương án bị loại và lý do. Chưa chọn. Benchmark và Evaluation sẽ so sánh các phương án trên cùng kịch bản.

| Kỹ thuật | Ý chính | Dự đoán điểm mạnh | Dự đoán điểm yếu |
|---|---|---|---|
| Quintic hoặc clothoid theo thời lượng | Từ trạng thái hiện tại tới trạng thái đích trong T giây; chọn T theo chức năng và TLC | Nhẹ, dễ chứng minh giới hạn bằng công thức, dễ chạy trên ECU | Không tự giữ biên làn; phải kiểm tra rồi chọn lại T |
| Lấy mẫu trong Frenet (Werling và cộng sự 2010) | Sinh nhiều path quintic với đích và T khác nhau, chọn path có chi phí thấp nhất (jerk, thời lượng, độ lệch) mà vẫn trong giới hạn | Chọn được path tốt nhất trong tập; xử lý được biên; cùng cách làm áp dụng được cho quỹ đạo dọc nếu sau này cần | Tốn tính hơn; kết quả phụ thuộc lưới lấy mẫu, có thể nhảy giữa hai path ở hai chu kỳ |
| Tối ưu (QP hoặc MPC) trên độ lệch ngang | Tối ưu d(s) với ràng buộc biên làn; ELK siết biên và nới giới hạn a_y | Giữ biên và giới hạn một cách tường minh; một công thức cho cả ba chức năng | Nặng nhất; cần bộ giải chạy được thời gian thực; khó chứng minh luôn có nghiệm |

## Nguồn

- Đề bài G1 (`G1_Path_Planning.pdf`), mục Techniques to investigate
- Werling, Ziegler, Kammel, Thrun (2010), Optimal trajectory generation for dynamic street scenarios in a Frenet frame, ICRA

# PP-PR-030 F21 a, b, d: HWA thôi lái khi mất hai vạch làn mình, còn vạch làn bên

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở, đã tìm nguyên nhân: bước 4 của T2 chưa cài |
| Mở ngày | 2026-11-13 |
| Requirement bị ảnh hưởng | PP-SWR-147; lộ qua PP-SWR-030 |
| Tái hiện | [20261113-1803-suite-regression-3c31309](../runs/20261113-1803-suite-regression-3c31309/report.md): F21 a, b, d trên S1a, mọi profile được chạy, seed 1 |

## 1. Hiện tượng

| Ca | Trượt | Tỉ lệ thời gian HWA lái sau REQUEST |
|---|---|---|
| F21 a (còn L2, R2, độ tin ≥ `conf_inferred`) | 030: 916 chu kỳ từ 5,1 s | 15 % |
| F21 b (chỉ còn L2) | 030: 916 chu kỳ từ 5,1 s | 15 % |
| F21 d (như a, cua R = 500 m) | 030: 356–916 chu kỳ | 45 % |
| F21 c (chỉ còn mép đường phải) | Không trượt 030 | 81 % |
| F21 e (độ tin dưới `conf_inferred`) | Không trượt; dừng là đúng | 15 % |

- 24 lần chạy trượt. PP-SWR-043 đạt: path không hợp lệ và chức năng là NONE.
- 051 đạt ở a, b vì đường thẳng: xe đi thẳng khi EPS trả lái. Không phải bằng chứng path còn tốt.
- Bên chấm không có tiêu chí PP-SWR-147 (PP-PR-031). Lỗi chỉ lộ nhờ 030.

## 2. Nguyên nhân

Chưa cài. Ghi chú đầu `planner/src/reference_line.h`: "Not yet: ... step 4 (centre inferred from adjacent lines and road edges)". Cờ `inferred` (PP-SWR-047) được khai báo nhưng không chỗ nào đặt.

- Mất hai vạch làn mình: T2 coast theo `T_coast`, rồi reference line không hợp lệ, nên path không hợp lệ (đúng chuỗi của PP-SWR-124).
- F21 c vẫn lái vì có đường riêng cho mép đường (`pp_road_edge_references`), không qua bước 4 của T2.

Nguồn liên quan:

| Văn bản | Mục | Nội dung |
|---|---|---|
| Mentor | PP-SWR-147 | Mất hai vạch làn mình mà còn biên khác đủ tin thì giữ path |
| R171 | Annex 3, 4.1.3.2 (a) | Chiến lược bảo đảm controllability: không chấm dứt hỗ trợ ngay, tiếp tục trên quỹ đạo phù hợp khi vạch tạm thời không thấy |
| R171 | 5.3.5.1.1 | Tránh dao động nhanh giữa stand-by và active |
| R171 | Annex 4, 4.2.5.1.1 (c) | Thử với nhiều loại biên làn: vạch, mép đường, chỉ một vạch |

## 3. Cách sửa

- Cài bước 4 của T2 theo Software Detailed Design mục 5: tâm làn suy từ L2, R2 (dời một bề rộng làn đã nhớ) khi độ tin ≥ `conf_inferred`; đặt `inferred = true` để PP-SWR-047 chặn LKA, ELK.
- Giữ F21 e dừng như hiện tại (độ tin dưới `conf_inferred`).
- Đồng thời xem lại `coast_ok` (PP-PR-037): hai chỗ cùng dựa vào biên ngoài làn.
- Bên chấm thêm tiêu chí 147 theo PP-PR-031 trước khi xác nhận.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

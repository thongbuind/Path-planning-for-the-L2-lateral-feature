# PP-TS-003 Kỹ thuật tạo path HWA (T7)

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở; đã cài V1, V2; plan chờ khóa; PP-PR-006 mở |
| Mở ngày | 2026-11-11 |
| Khóa ngày | — |
| Quyết định ngày | — |
| Liên quan | PP-SWR-001 đến 007, 050 đến 053, 100 đến 102, 151; SQTS mục 9 |

## 1. Câu hỏi

- Quyết định cần đưa ra: kỹ thuật tạo path HWA, và cắt cua nhẹ trong làn khi cần và đủ điều kiện an toàn.
- Yêu cầu của người dùng: cắt cua là một phần của cùng một thuật toán vẽ path, không phải một chế độ bật bằng `if`.

## 2. Phương án

| ID | Phương án | Cách cài | Ghi chú |
|---|---|---|---|
| V0 | Quintic theo thời lượng (T7 A), T4 trộn, T10 cắt | `PP_T7=quintic` | Mốc |
| V1 | QP hợp nhất (T7 C): biến là jerk trên 30 bước; chi phí jerk, lệch tâm, cuối horizon, a_y vượt `qp_a_comfort`, ra ngoài corridor; ràng buộc a_y ≤ `qp_ay_margin`·aysmax, liên tục với path cũ | `PP_T7=qp` | Cắt cua chỉ xuất hiện khi ràng buộc chạm |
| V2 | Như V1, `qp_a_comfort` = 0: phạt thẳng a_y² | `PP_T7=qp`, calibration | Cùng công thức: σ ≥ trị tuyệt đối của a_y |

Cơ chế chung của V1 và V2 sau các vòng sửa bản C (trước khi khóa plan):

| Phần | Cách làm |
|---|---|
| Liên tục với path cũ | Chi phí mềm `qp_w_cont` so với path cũ đã dời theo phần offset T8 vừa đổi; sau đó T4 vẫn trộn như V0 |
| a_y | a_y = d̈/q² + v²κ/q, q = 1 − κd lấy tại path cũ, đúng như T11 xuất path |
| a_y cần > aysmax − epsilon_ay/2 | a_y giữ trong dải [aysmax − epsilon_ay/2, aysmax] (PP-SWR-006); không phạt comfort ở các điểm này |
| Jerk | Ràng buộc cứng ±0,9·jerk lớn nhất HWA, tính cả phần v³·dκ/ds của reference line |
| Bộ giải | ADMM 150 vòng, ρ thích nghi; ρ riêng từng khối hàng (a_y ×10, jerk ×0,1) để hội tụ ở dải hẹp |

Câu hỏi con: bộ giải ADMM tự viết hay OSQP. Chọn ADMM tự viết (không phải tải, giữ không heap, tất định); người dùng giao làm ngày 2026-11-11 mà chưa chọn, nên dùng phương án đã đề xuất.

## 3. Cách đánh giá

Chưa khóa.

| Mục | Nội dung |
|---|---|
| Tiêu chí loại | Requirement trong phạm vi của P1 và S14 |
| Xếp hạng | SQTS mục 9; thêm a_y lớn nhất của xe trong cua ngắn |
| Bộ chạy | Như M1, thêm cua ngắn và cua chữ S |
| Ngân sách chỉnh | Mỗi phương án một sweep cùng số bộ calibration |

## 4. Lần chạy

| Run ID | Phương án | Ghi chú |
|---|---|---|
| 20261111-1024-matrix-M1-b9e5d4d | V0 | Đăng ký lại; mốc |

## 5. Kết quả

**Nguyên mẫu (Python, trước khi viết C).**

- Biến là d tại 31 điểm: điều kiện số xấu (jerk là sai phân bậc ba, hệ số 1/Δt³), ADMM không hội tụ ở cua chạm aysmax, cân bằng Ruiz không giúp được.
- Đổi sang dạng nén (biến là jerk): so với nghiệm chính xác (`scipy` trust-constr), ADMM với ρ thích nghi, 150 vòng, sai ≤ 3 mm ở cả 6 ca thử (đưa về giữa, cua 2,5 / 3,1 / 4,2 m/s², vào cua, bám path cũ).
- Trọng số chọn trên bài đưa về giữa từ 0,5 m: không vọt qua tâm, vào 0,1 m sau 2,3 s, a_y thêm 0,27 m/s², jerk 0,84 m/s³.

**Bản C** (`planner/src/generators/qp.c`, `PP_T7=qp`): cùng kết quả với nguyên mẫu trên ca cua 3,1 m/s² (d cuối −3,037 so với −3,038 m). Trạng thái planner 37 KB. 11/11 unit test C đạt.

**Lần chạy nháp bản C (chỉ để dò lỗi, không dùng để quyết định).** Mỗi lỗi tìm được đã sửa ở cơ chế chung (bảng mục 2):

| Lỗi | Nguyên nhân | Sửa |
|---|---|---|
| a_y vượt aysmax tới 0,04 m/s² ở cua vượt giới hạn | ADMM chưa hội tụ ở dải a_y hẹp sau 150 vòng | ρ riêng từng khối hàng |
| Xe trôi khỏi path ở cua vượt aysmax, path nhảy khi reset | a_y bỏ hệ số q: path chỉ đạt 2,488 m/s² khi xe đã ra ngoài 1 m | a_y theo công thức T11 |
| a_y path thấp hơn aysmax khi a_y cần vượt aysmax | Chi phí comfort kéo a_y xuống | Bỏ comfort ở các điểm đó |
| S3: dời tâm chậm hơn V0 khoảng 1,5 s | Chi phí liên tục giữ path ở chỗ cũ khi offset mục tiêu đổi | Dời path cũ theo phần offset vừa đổi |
| Còn lại: S1b b, e trượt PP-SWR-100 | Xe bám trễ lúc vào cua, stitching reset | PP-PR-006, chưa sửa |

## 6. Đề xuất

## 7. Quyết định

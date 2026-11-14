# PP-TS-005 Sai số khớp đa thức của lane model (T2, T5)

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở; plan nháp chờ duyệt |
| Mở ngày | 2026-11-11 |
| Khóa ngày | — |
| Quyết định ngày | — |
| Liên quan | PP-PR-004; PP-SWR-051, 100, 125; SOTIF TC-11; Chalmers 2014 (`docs/reference/standards/`) |

## 1. Câu hỏi

- Quyết định cần đưa ra: planner xử lý thế nào khi đa thức bậc 3 của lane model sai có hệ thống (không phải nhiễu) ở hai đầu cửa sổ khớp, như trên cua chữ S của R171.
- Vì sao cần: PP-PR-004, độ cong tại xe sai cả dấu.

## 2. Phương án

| ID | Phương án | Cách cài | Ghi chú |
|---|---|---|---|
| V0 | Bản hiện tại: T5 tin camera như nhau trên cả tầm nhìn | — | Mốc |
| V1 | T5: phương sai đo của camera tăng ở hai đầu cửa sổ khớp (gần xe và cuối tầm nhìn); điểm gần xe chủ yếu lấy từ lần quan sát trước, khi điểm đó còn ở giữa cửa sổ, dời theo ego-motion | Build-time | Ít thay đổi; vẫn chỉ nhớ độ cong |
| V2 | Bộ nhớ điểm vạch: giữ các điểm vạch đã quan sát (lấy mẫu từ đa thức ở giữa cửa sổ), dời theo ego-motion, khớp lại reference line từ bộ nhớ và lần đo mới | Build-time | Giống ý của Chalmers; tốn bộ nhớ cố định hơn |

## 3. Cách đánh giá

Bản nháp ngày 2026-11-14, chưa khóa: [plan.yaml](plan.yaml), suite `benchmark/suites/PP-TS-005.yaml`.

| Mục | Nội dung |
|---|---|
| Tiêu chí loại | PP-SWR-051, 100 đến 102 và requirement trong phạm vi của suite |
| Xếp hạng | Software Qualification Test Specification mục 9 |
| Bộ chỉnh | Cua chữ S R = 500 m (S1 d), S1 b, S1b a, F01, F06, F02 trên S1; seed 1, 2 |
| Bộ kiểm | Cua chữ S của R171 (S1 f, S14 e hai chế độ ACC), S1 g, S1 c, S1 e, S1b b, c, S14 a, tầm nhìn 40 m, F01, F06, F02; seed 3, 4 |
| Ngân sách chỉnh | Như nhau cho mọi phương án; ghi khi V1, V2 đã cài, trước khi khóa |
| Liên quan khác | V1, V2 sửa T2, T5; cài sau khi PP-PR-030 (bước 4 của T2) đã vào nhánh chính để không sửa chồng |

## 4. Lần chạy

| Run ID | Phương án | Ghi chú |
|---|---|---|

## 5. Kết quả

## 6. Đề xuất

## 7. Quyết định

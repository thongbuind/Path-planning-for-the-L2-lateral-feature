# PP-TS-005 Sai số khớp đa thức của lane model (T2, T5)

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
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

Chưa khóa. Bộ chạy dự kiến: S1 (f), S14 (e), S1b, F01, F06 trên S1a và S1c; tiêu chí loại PP-SWR-051, 100 đến 102.

## 4. Lần chạy

| Run ID | Phương án | Ghi chú |
|---|---|---|

## 5. Kết quả

## 6. Đề xuất

## 7. Quyết định

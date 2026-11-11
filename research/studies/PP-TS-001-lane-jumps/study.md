# PP-TS-001 Xử lý lane model nhảy (T2)

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-11 |
| Khóa ngày | — |
| Quyết định ngày | — |
| Liên quan | PP-SWR-121, 122; PP-ADR-006, 007; SOTIF TC-01; F02, F03 |

## 1. Câu hỏi

- Quyết định cần đưa ra: cách T2 nhận hay loại một bước nhảy của biên làn.
- Vì sao cần: J0 (R1 + R2) giữ lệch xe 0,009 m ở F02 a–d. F02e (bước nhảy giữ nguyên) chưa cứu được, vì không có tham chiếu độc lập để biết vạch mới là sai.

## 2. Phương án

| ID | Phương án | Cách cài | Cần thêm |
|---|---|---|---|
| V0 = J0 | Kiểm từng frame (`k_jump`), cộng R1 (chỉ nhận sau `T_confirm` ổn định) và R2 (giữ vị trí cũ, quay về thì nhận ngay) | Bản hiện tại | — |
| J1 | J0 cộng thang chậm (song song, bề rộng) của Software Detailed Design. Bắt được một vạch nhận nhầm (F03) và làn mở rộng | Build-time | F03 trong simulator |
| J2 | J1 cộng kiểm chéo bằng xe ở làn bên: cả lane model nhảy mà xe làn bên không nhảy theo thì không bao giờ nhận. Cách duy nhất cứu được F02e | Build-time | Đợt ObjectList |
| J3 | Thận trọng: cả hai vạch nhảy thì `path_valid = false` ngay, HWA trả lái | Build-time | — |

## 3. Cách đánh giá

Chưa khóa: cần F03 trong simulator trước.

| Mục | Nội dung |
|---|---|
| Tiêu chí loại | PP-SWR-100 đến 102, 121, 122, 051 |
| Xếp hạng | Lệch xe (PP-SWR-050); độ liên tục; tỉ lệ thời gian HWA còn lái; số lần loại nhầm khi nhiễu ban đêm |
| Bộ chạy | F01c, F02 a–e, F03 a–e; sau này thêm S6b |

## 4. Lần chạy

| Run ID | Phương án | Ghi chú |
|---|---|---|
| 20261111-1024-matrix-M1-b9e5d4d | J0 | Đăng ký lại. F02e: lốp đè vạch ở 2/4 lần chạy (VP-0, VP-5) |

## 5. Kết quả

Chưa có so sánh. J0 là mốc.

## 6. Đề xuất

## 7. Quyết định

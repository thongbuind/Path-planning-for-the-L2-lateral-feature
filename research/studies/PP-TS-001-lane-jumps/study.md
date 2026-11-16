# PP-TS-001 Xử lý lane model nhảy (T2)

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã quyết: J0 kiểm hình dạng; J1 còn mở |
| Mở ngày | 2026-11-11 |
| Khóa ngày | 2026-11-14 |
| Quyết định ngày | 2026-11-14 |
| Liên quan | PP-SWR-121, 122; PP-ADR-006, 007; SOTIF TC-01; F02, F03 |

## 1. Câu hỏi

- Quyết định cần đưa ra: cách T2 nhận hay loại một bước nhảy của biên làn.
- Vì sao cần: J0 (R1 + R2) giữ lệch xe 0,009 m ở F02 a–d. F02e (bước nhảy giữ nguyên) chưa cứu được, vì không có tham chiếu độc lập để biết vạch mới là sai.

## 2. Phương án

| ID | Phương án | Cách cài | Cần thêm |
|---|---|---|---|
| V0 = J0 | Kiểm từng frame (`k_jump`), cộng R1 (chỉ nhận sau `T_confirm` ổn định) và R2 (giữ vị trí cũ, quay về thì nhận ngay) | Bản hiện tại | — |
| J0 kiểm hình dạng | Kiểm thêm ở 50% và 75% đoạn tầm nhìn chung của hai frame sau bù ego-motion. Ngưỡng dùng `k_jump` và phương sai của các hệ số đa thức báo qua interface | `PP_T2_SHAPE_CHECK=ON` | Kiểm F06 và các ca sạch, nhiễu, mất vạch để phát hiện loại nhầm |
| J1 | J0 cộng thang chậm (song song, bề rộng) của Software Detailed Design. Bắt được một vạch nhận nhầm (F03) và làn mở rộng | Build-time | F03 trong simulator |
| J2 | J1 cộng kiểm chéo bằng xe ở làn bên: cả lane model nhảy mà xe làn bên không nhảy theo thì không bao giờ nhận. Cách duy nhất cứu được F02e | Build-time | Đợt ObjectList |
| J3 | Thận trọng: cả hai vạch nhảy thì `path_valid = false` ngay, HWA trả lái | Build-time | — |

## 3. Cách đánh giá

F03 đã có trong simulator. [Kế hoạch](plan.yaml) và [bộ chạy](../../../benchmark/suites/PP-TS-001.yaml) định trước so sánh J0 với bản kiểm hình dạng trên cùng quintic và calibration. Bộ kiểm dùng seed 3, 4. J1, J2, J3 sẽ cần phương án thực thi và kế hoạch riêng trước khi so sánh.

| Mục | Nội dung |
|---|---|
| Tiêu chí loại | PP-SWR-100 đến 102, 121, 122, 051 |
| Xếp hạng | Lệch xe (PP-SWR-050); độ liên tục; tỉ lệ thời gian HWA còn lái; số lần loại nhầm khi nhiễu ban đêm |
| Bộ chạy | F01, F02, F03, F06, F21, S1 và S6b |
| Ngân sách chỉnh | Không có: J0 kiểm hình dạng không thêm calibration parameter |
| Mức chênh coi như ngang nhau | PP-SWR-050: 0,005 m; PP-SWR-051: 0,01 m |

Trước khi khóa (2026-11-14), bộ kiểm thêm F06 a, d trên ca chủ S1a, vì [20261114-1021-suite-regression-d7ed84c](../../runs/20261114-1021-suite-regression-d7ed84c/report.md) còn trượt PP-SWR-051 ở F06 trên S1a.

## 4. Lần chạy

| Run ID | Phương án | Ghi chú |
|---|---|---|
| 20261111-1024-matrix-M1-b9e5d4d | J0 | Đăng ký lại. F02e: lốp đè vạch ở 2/4 lần chạy (VP-0, VP-5) |
| [20261114-1857-study-PP-TS-001-13913da](../../runs/20261114-1857-study-PP-TS-001-13913da/summary.md) | J0, J0 kiểm hình dạng | Theo plan khóa 2026-11-14; 42 lượt mỗi phương án |

## 5. Kết quả

Lần chạy [20261114-1857-study-PP-TS-001-13913da](../../runs/20261114-1857-study-PP-TS-001-13913da/summary.md). Số lượt trượt: bộ chỉnh 12 (J0) và 8 (J0 kiểm hình dạng); bộ kiểm 23 và 14.

| Ca | J0 | J0 kiểm hình dạng |
|---|---|---|
| F06 a trên S1a, S1c | Trượt 051; lệch xe 1,02–1,09 m | Đạt; 0,17–0,35 m |
| F06 b trên S1c | Trượt 051, 100 (101 ở seed 3); 1,83 m | Đạt; 0,85 m |
| F06 e trên S1c | Trượt 051, 100; 1,75 m | Trượt 100; đạt 051; 0,78 m |
| F06 d trên S1a, S1c (sai kéo dài 2 s) | Trượt 051 (cả 100 trên S1c); 1,45–1,75 m | Như J0; 1,78–1,82 m |
| F03 c trên S1c | Trượt 051, 100 | Như J0 |
| F01 b, c trên S1c | Trượt 100 | Như J0 |
| S1 a, f; S6b d; F01; F02 a, b, d, e; F03 a; F21 a, b | Đạt | Như J0; PP-SWR-050 lệch nhau < 0,005 m |

- 27/42 lượt mỗi bộ cho kết quả như nhau. Không thấy loại nhầm ở ca sạch, nhiễu ban đêm F01 hay mất vạch F21.
- F06 d và F03 c còn trượt như dự đoán ở mục 6: sau `T_confirm`, hình học sai được nhận. F06 d với kiểm hình dạng lệch xe lớn hơn J0 0,07–0,33 m.
- F01 b, c trên S1c trượt 100 ở cả hai phương án; cơ chế ở PP-PR-005, không thuộc T2.

## 6. Đề xuất

- Chọn J0 kiểm hình dạng: hết trượt 051 ở F06 a, b, e, không có trượt mới, không cần thêm calibration parameter.
- F06 d, F03 c và F02 e cần tham chiếu độc lập (J1, J2). Mở kế hoạch riêng cho J1 sau quyết định này.
- F06 d xấu hơn J0 0,07–0,33 m: ghi nhận, xét lại khi làm J1.

## 7. Quyết định

- 2026-11-14, người dùng chọn J0 kiểm hình dạng theo [20261114-1857-study-PP-TS-001-13913da](../../runs/20261114-1857-study-PP-TS-001-13913da/summary.md).
- Bản giao luôn kiểm hình dạng; bỏ công tắc build `PP_T2_SHAPE_CHECK` (Software Detailed Design 1.13, T2).
- F06 d, F03 c, F02 e: cần tham chiếu độc lập, để cho J1 với kế hoạch riêng.

## 8. Ghi chú cho kế hoạch J1 (2026-11-14)

| Ca | Thang chậm (song song, bề rộng) bắt được | Nguồn tham chiếu cần |
|---|---|---|
| F03 c, một vạch nhận nhầm | Có: vạch nhầm lệch song song và đổi bề rộng | — |
| F06 d, c2 sai trên mọi vạch 2 s | Không: các vạch vẫn song song, bề rộng không đổi | Độc lập với camera, ví dụ độ cong từ yaw rate khi xe đang bám làn (T5) |
| F02 e, cả lane model dời | Không | Xe ở làn bên (J2) |

PP-PR-048 cho thấy F06 d trượt cả ở J0 (PP-SWR-032) và J0 kiểm hình dạng (PP-SWR-086), độc lập với lỗi đã sửa. Kế hoạch J1 chỉ nên nhắm F03; F06 d cần phương án riêng.

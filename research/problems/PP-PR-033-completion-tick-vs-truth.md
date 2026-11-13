# PP-PR-033 PP-SWR-032 và 090 đòi tick COMPLETED trùng với trạng thái thật

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở; cần quyết định về requirement |
| Mở ngày | 2026-11-13 |
| Requirement bị ảnh hưởng | PP-SWR-032, 090 |
| Tái hiện | [20261113-1803-suite-regression-3c31309](../runs/20261113-1803-suite-regression-3c31309/report.md) |

## 1. Hiện tượng

| Requirement | Hướng lệch | Ca | Lần chạy |
|---|---|---|---|
| PP-SWR-032 | COMPLETED muộn hơn tick điều kiện thật giữ đủ | F01 (21), G01 (12), S12 (12), F06 (3), S13 (2) | 50 trong phạm vi |
| PP-SWR-090 | COMPLETED sớm hơn | F02 (3), S5 c (1) | 4 trong phạm vi |
| PP-SWR-090 | COMPLETED sớm hơn | S4b, S6, S7, S8, S8b | 35 ngoài phạm vi (PP-PR-020) |

## 2. Nguyên nhân

- 032 (không được muộn) và 090 (không được sớm) gộp lại đòi tick COMPLETED trùng tick đầu tiên mà điều kiện thật đã giữ đủ `T_end_hold`.
- Planner chỉ thấy ước lượng. Ngưỡng (`heading_end` 0,5°, `v_lat_end` 0,1 m/s, `ay_add_end` 0,2 m/s²) cùng cỡ với sai số ước lượng (PP-PR-020).
- Nhiễu camera làm ước lượng vượt ngưỡng lâu hơn nên báo muộn (F01, G01, S12). Sai số hệ thống trên cua và mép đường làm báo sớm (PP-PR-020).
- Không planner nào trùng tick ở mọi ca có nhiễu: requirement không đạt được, không phải lỗi riêng của planner.

Nguồn liên quan:

| Văn bản | Nội dung |
|---|---|
| R79, R171, EU 2021/646, Euro NCAP LSS và SA | Không quy định thời điểm kết thúc can thiệp. Bài thử chấm DTLE và không va chạm, không chấm thời điểm kết thúc |
| Software Requirements Specification | Điều kiện kết thúc và các ngưỡng là nhóm tự thống nhất |
| Thứ tự ưu tiên của dự án | An toàn trước: báo sớm thì trả lái khi xe còn trôi; báo muộn chỉ giữ can thiệp lâu hơn |

## 3. Cách sửa

Đổi requirement, nên mở trade study. Phương án đề xuất:

| ID | Phương án |
|---|---|
| V0 | Giữ như hiện tại |
| V1 | 090 giữ chặt trên trạng thái thật. 032 cho phép muộn tới `T_end_late` sau tick thật (nhóm tự thống nhất; giới hạn trên chọn sao cho tổng thời lượng can thiệp không đổi đáng kể). Planner thêm biên cho sai số ước lượng (ngưỡng trừ một bội phương sai lane model báo) để không báo sớm |
| Loại | Chấm cả hai trên ước lượng planner gửi: trái quy tắc đo trên chuyển động thật |

Đề xuất V1. PP-PR-020 xử lý cùng study.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

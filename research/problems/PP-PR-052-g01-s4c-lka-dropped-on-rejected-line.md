# PP-PR-052 G01 trên S4c: LKA bị hủy khi vạch còn lại bị loại một frame

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã sửa, chờ hồi quy chính thức |
| Mở ngày | 2026-11-14 |
| Requirement bị ảnh hưởng | PP-SWR-030, 047 |
| Tái hiện | [20261114-1952-suite-regression-0776bad](../runs/20261114-1952-suite-regression-0776bad/report.md): G01 trên S4c, 6 profile, trượt đầu tiên 7,152 s |

## 1. Hiện tượng

- LKA (LEFT) bắt đầu 3,827 s. F04 a mất L1 từ 4 s; LKA tiếp tục trên R1 cộng bề rộng đã nhớ.
- 7,152 s: pha LKA về NONE (không COMPLETED), REQUEST vẫn còn, mọi input dùng được. Không bắt đầu lại (PP-SWR-045).

## 2. Nguyên nhân

- Log T2 (bản build nháp có in): frame R1 lệch 3,11σ so với bộ nhớ (nhiễu F01 c ×2,5), bị loại 4 chu kỳ.
- Không còn vạch làn mình nào được nhận, T2 bước 4 suy tâm từ L2, đặt cờ suy ra; PP-SWR-047 cấm LKA nên LKA bị hủy.
- Vô lý: vạch chỉ bị nghi ở một frame lại bị xử lý nặng hơn mất hẳn (không có biên ngoài thì T2 bám reference line cũ và LKA tiếp tục).

## 3. Cách sửa

- T2: vạch làn mình chỉ bị loại ở kiểm nhất quán thì bám reference line cũ (bước 5) trước, hết `T_coast` mới suy tâm từ biên ngoài.
- Unit test `test_rejected_ego_line_coasts_before_inference`. Software Detailed Design 1.17.
- Nháp seed 1: G01 trên S4c hết trượt PP-SWR-030, còn PP-SWR-032 (nhiễu điều kiện kết thúc, PP-TS-018). G01 trên S1c, F21 a, b, d trên S1a, F04 a, b, F04 a lúc LKA, F02 b, F01 c, S12 a, F06 c: đạt. F21 c trên S1c trượt như trước khi sửa (PP-PR-054).

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

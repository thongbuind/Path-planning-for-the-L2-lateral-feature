# PP-PR-078 lcc_mode = COAST trong khi vạch làn còn đo được

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-19 |
| Requirement bị ảnh hưởng | PP-SWR-177 (Interface), liên quan PP-SWR-121, 124 |
| Tái hiện | [20261118-2030-suite-regression-e3158a5](../runs/20261118-2030-suite-regression-e3158a5/report.md), `S1b-b-VP-0-5a25651bbb89`, seed 1 (chạy lại cục bộ 2026-11-19, cùng 78 chu kỳ) |

## 1. Hiện tượng

PP-SWR-177 trượt ở 200 lượt ngoài phạm vi (cột Kiểm chứng chỉ ghi S22, S23), từ 2 đến 78 chu kỳ mỗi lượt, ở mọi ca có HWA: S1b, S14, S17, F02, F06, F03, G01, F15. Số lượt không đổi qua ba lần hồi quy 18/11.

Tái hiện trên S1b b, VP-0, seed 1 (ca danh định, không lỗi):

| Khối | Thời điểm [s] | Chu kỳ | Lane model | `lcc_mode` |
|---|---|---|---|---|
| 1 | 10,26 đến 11,21 | 39 | L2, L1, R1 MEASURED độ tin cậy 1,0; R2 LOST | COAST |
| 2 | 11,46 đến 12,41 | 39 | L2, L1 MEASURED; R1, R2 LOST | COAST |

- Cả hai khối bắt đầu đúng chu kỳ camera báo mất một vạch và dài 39 chu kỳ, bằng `T_coast` = 1,0 s.
- Ở khối 1 cả hai vạch làn mình vẫn đo được. `inputs_ok.lane_model` đúng suốt hai khối và `path_valid = true`.
- Tiêu chí của bên chấm coi COAST chỉ đúng khi không còn biên làn đủ tin nào.

## 2. Nguyên nhân

Phân tích mới ở mức đọc code và một lần chạy lại, chưa xác nhận trên ca khác.

- [pp_lcc.c:376](../../planner/src/pp_lcc.c) đặt COAST khi `ref.coasting`; cờ này do `coast()` ở [reference_line.c:238](../../planner/src/reference_line.c) đặt (bước 5: đi tiếp reference line cũ bằng ego-motion, tối đa `T_coast`).
- Bước 5 chạy khi các bước trước không nhận được reference line mới. Suy ra từ thời lượng 39 chu kỳ: khi một vạch biến mất khỏi lane model, planner không dùng frame mới trong khoảng 1 s và đi bằng bộ nhớ. `T_confirm` và `T_coast` đều bằng 1,0 s nên chưa phân biệt được tham số nào quyết định.
- SRS định nghĩa COAST là "bám path cũ vì mất mọi biên" (Interface, `lcc_mode`), còn planner dùng nhãn này cho cả lúc giữ bộ nhớ khi còn biên đo được. Bên chấm đọc đúng định nghĩa của SRS.

Hai cách hiểu cần phân biệt:

1. Lỗi gán nhãn của planner: nên báo LANE hoặc INFERRED khi còn biên đo được.
2. SRS thiếu một chế độ cho trạng thái giữ bộ nhớ sau khi lane model đổi cấu trúc.

Hệ quả khác nếu đúng: planner bỏ qua lane model hợp lệ gần 1 s mỗi lần một vạch mất. Chưa đo ảnh hưởng tới DLC hay path của việc này.

## 3. Cách sửa

Chưa làm; nằm ở phía planner và đổi nghĩa một trường interface nên cần PP-ADR hoặc sửa SRS. Việc này thuộc đợt nâng cấp planner, ngoài đợt hoàn thiện nền tảng.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| 20261118-2030-suite-regression-e3158a5 | 200 lượt trượt ngoài phạm vi |

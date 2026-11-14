# PP-PR-048 F06 c (sai c3) và F06 d lúc LKA, ELK trượt sau khi bật kiểm hình dạng

| Mục | Nội dung |
|---|---|
| Trạng thái | Đóng phần F06 c; F06 d chuyển sang J1 (xác nhận 20261114-2252-suite-regression-98a122b) |
| Mở ngày | 2026-11-14 |
| Requirement bị ảnh hưởng | PP-SWR-051; PP-SWR-086; PP-TS-001 |
| Tái hiện | [20261114-1952-suite-regression-0776bad](../runs/20261114-1952-suite-regression-0776bad/report.md): F06 c trên S1a, S1c; F06 d trên S4a, S5a lúc LKA, ELK |

## 1. Hiện tượng

- F06 c (c3 + 4·10⁻⁶ 1/m² trên mọi vạch, 1 s): DLC −0,97 đến −1,27 m ở 6 lượt. Đạt ở d7ed84c (trước khi bật kiểm hình dạng).
- Log F06 c trên S1a, VP-1: lỗi kéo dài 4,0–5,0 s, nhưng độ cong cuối path tiếp tục tăng tới 0,0018 1/m sau khi lỗi hết; xe trôi 0,8 m lúc 7,4 s rồi rời làn.
- F06 d lúc LKA, ELK: PP-SWR-086 trượt, DTLE không đo được (NaN), 4 lượt.
- Lần chạy nháp cùng commit 13913da (thư viện J0 và J0 kiểm hình dạng của PP-TS-001), F06 c trên S1a seed 1: J0 đạt (DLC 0,38 m), J0 kiểm hình dạng trượt (−0,97 m). F06 d lúc LKA: J0 trượt 032, J0 kiểm hình dạng trượt 086.

## 2. Nguyên nhân

- Giả thuyết ban đầu sai một phần: R2 đã so cả hình dạng (dùng chung phép kiểm từng frame).
- Log bộ nhớ biên (bản build nháp có in, F06 c trên S1a seed 1, 40 Hz): khi frame bị loại, bộ nhớ chỉ được dời theo ego-motion, đoạn tầm nhìn chung ngắn đi khoảng 0,6 m mỗi chu kỳ. Độ lệch hình dạng giảm từ 5,0σ xuống 3,1σ trong 0,7 s.
- Ở 0,7 s (ứng viên mới 0,70 s < `T_confirm`), hình dạng sai qua ngưỡng 3σ so với bộ nhớ cũ và được nhận như frame bình thường. Không phải thay đổi, nên không có vị trí cũ cho R2.
- Khi lỗi hết, hình dạng đúng lệch 5,5σ so với bộ nhớ (lúc này là hình dạng sai) và bị loại thêm 1 s. Planner bám reference line có độ cong sai, xe rời làn.
- F06 d (c2 sai 2 s > `T_confirm`): R1 nhận hình dạng sai đúng thiết kế. Không do lỗi trên; thuộc hướng J1 của PP-TS-001, cùng nhóm F03 c, F02 e.

## 3. Cách sửa

- Bản đầu (commit 83dc910): frame khớp ứng viên hơn bộ nhớ thì tính cho ứng viên. Bỏ ở commit sau vì gây PP-PR-055 (loại frame nhất quán khi nhiễu tương quan theo thời gian).
- Bản hiện tại (Software Detailed Design 1.18): frame nhất quán với bộ nhớ trong lúc có ứng viên vẫn được nhận, nhưng bộ nhớ trước đó được giữ làm vị trí cũ trong `T_confirm`. Hình dạng sai có thể lọt vào ở cuối lỗi; khi lỗi hết, R2 nhận lại hình dạng đúng ngay.
- Unit test `test_shape_change_cannot_slip_in_while_the_memory_ages`, `test_noisy_frame_does_not_hold_back_the_next_one`, `test_slow_drift_within_the_check_is_taken`.
- Nháp seed 1 với bản hiện tại: F06 c trên S1a, S1c, F06 a, b, e đạt.
- F06 d (c2 sai 2 s > `T_confirm`): R1 nhận đúng thiết kế, thuộc J1 (PP-TS-001 mục 8).

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| [20261114-2153-suite-regression-71fb7c1](../runs/20261114-2153-suite-regression-71fb7c1/report.md) | Bản 1: F06 c hết trượt (6 lượt); gây trượt mới S12 c (PP-PR-055) |
| [20261114-2252-suite-regression-98a122b](../runs/20261114-2252-suite-regression-98a122b/report.md) | Bản 2: F06 c trên S1a, S1c đạt (6 lượt); F06 d vẫn trượt (J1) |

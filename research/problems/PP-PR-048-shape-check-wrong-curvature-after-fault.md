# PP-PR-048 F06 c (sai c3) và F06 d lúc LKA, ELK trượt sau khi bật kiểm hình dạng

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã sửa F06 c, chờ hồi quy chính thức; F06 d chuyển sang J1 |
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

- T2 (`check_line`): khi đang có ứng viên, frame nhất quán với ứng viên và khớp ứng viên hơn bộ nhớ (độ lệch chuẩn hóa lớn nhất của c0 và hai điểm hình dạng nhỏ hơn) thì tính tiếp cho ứng viên. Thay đổi chỉ được nhận qua R1, và R2 có vị trí cũ để quay về.
- Frame nhất quán với bộ nhớ và gần bộ nhớ hơn vẫn được nhận ngay (một frame nhiễu không giữ chân frame sau).
- Unit test: `test_shape_change_cannot_slip_in_while_the_memory_ages`, `test_noisy_frame_does_not_hold_back_the_next_one`.
- Software Detailed Design 1.16, mục T2.
- Lần chạy nháp seed 1: F06 c trên S1a, S1c đạt; F06 a trên S1a đạt. Không đổi: S1a, S1b a, S3 a, S12 a, F01 a, F02 b, F06 b, e (đạt); F06 d trên S1a, S1c, S4a lúc LKA, S5a lúc ELK và F03 c trên S1a trượt với cùng giá trị như regression 0776bad.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

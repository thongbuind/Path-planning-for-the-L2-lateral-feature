# PP-PR-049 F08: bias yaw rate làm xe rời làn trên cua

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở; nguyên nhân gốc đã xác nhận, sửa qua PP-TS-028 |
| Mở ngày | 2026-11-14 |
| Requirement bị ảnh hưởng | PP-SWR-136; PP-SWR-051, 100 |
| Tái hiện | [20261114-1952-suite-regression-0776bad](../runs/20261114-1952-suite-regression-0776bad/report.md): F08 b, c trên S1c; F08 c trên S1a |

## 1. Hiện tượng

- F08 b (0,3 °/s) trên S1c: PP-SWR-051 −0,97 đến −1,28 m và PP-SWR-100 0,057 m, 3 lượt.
- F08 c (1 °/s, cảm biến thô) trên S1a, S1c: PP-SWR-100 0,073–0,079 m.
- F08 a (0,1 °/s) trên S1c vẫn trượt PP-SWR-051 ở 0776bad (−0,91 đến −1,21 m, 6 lượt); ghi trước đây là hết trượt là sai.
- PP-SWR-136 đòi đạt tới 0,3 °/s (F08 a, b); F08 c nằm ngoài câu của 136 nhưng trong phạm vi chấm của 100.

## 2. Nguyên nhân

- S1c cần a_y đúng bằng aysmax = 2,5 m/s². PP-SWR-001 chặn path tại aysmax nên không còn biên để kéo xe về khi đã lệch ra ngoài cua. S1c không lỗi cũng trôi ra −0,3 m sau 22 s; bias 0,1 °/s cộng khoảng 0,044 m/s² nhu cầu, xe lệch thêm khoảng 1,7 m trong 9 s.
- Không do T5: bản build nháp bỏ yaw rate khỏi T5 cho kết quả gần như không đổi (F08 a −0,89 m).
- Bản build nháp nới giới hạn a_y HWA thêm 0,3 m/s² (UN R79 5.6.2.1.1 cho phép vượt aysmax tới 0,3 m/s², hoặc 40 % trong tối đa 2 s): S1c, F08 a, F08 b trên S1c đạt PP-SWR-051 (DLC 0,60–0,74 m), PP-SWR-001 trượt theo câu hiện tại. F17 b, F21 c trên S1c không đổi (PP-PR-054).
- F08 c trên S1a (đường thẳng) chưa phân tích.

- 2026-11-23, sau PP-TS-020 V1a: F08 a trên S1c VP-0 đạt (DLC 0,73 m); F08 b, c trên S1c VP-5 còn trượt (−0,20 m, −1,27 m). Lượt nháp tách nguồn của bias (planner, Lateral Controller chạy thử và ego-motion cùng nhận IMU có bias):

| F08 trên S1c, VP-5, seed 1 | b: PP-SWR-051 [m] | c: PP-SWR-051 [m] |
|---|---|---|
| Bias ở mọi khối | −0,195 | −1,269 |
| Controller nhận yaw rate thật | −0,145 | −1,285 |
| Planner nhận EgoMotionQuery từ yaw rate thật, các khối khác giữ bias | 0,427 | 0,289 |
| Chỉ truy vấn bù trễ của T1 dùng yaw rate thật | — | −1,282 |
| Chỉ các truy vấn mang bộ nhớ sang chu kỳ sau dùng yaw rate thật | — | 0,194 |

- Nguyên nhân gốc thuộc planner: bộ nhớ giữa các chu kỳ (reference line của T3, cùng path cũ của T4, độ cong của T5) được dời bằng EgoMotionQuery. Bias yaw làm bộ nhớ quay lệch so với đường thật; sai số tại khoảng cách s tăng với tốc độ s·b, trong khi T3 chỉ cho r(s) dời về phía camera tối đa `ref_rate` = 0,1 m/s. Từ s > 0,1 / b (57 m ở 0,1 °/s, 19 m ở 0,3 °/s, 5,7 m ở 1 °/s) reference line trôi khỏi làn.
- Cách sửa có nhiều phương án: PP-TS-028.

## 3. Cách sửa

- Không sửa được trong phạm vi PP-SWR-001 hiện tại. Đề xuất trade study: biên a_y vượt aysmax theo R79 5.6.2.1.1 (liên tục ≤ 0,3 m/s², ngắn hạn ≤ 40 % trong 2 s), chỉ dùng để giữ xe trong làn; ảnh hưởng PP-SWR-001, 005, 006, cờ giới hạn.
- 2026-11-16: người dùng đồng ý mở [PP-TS-020](../studies/PP-TS-020-path-ay-ceiling/study.md).

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| 20261118-2030-suite-regression-e3158a5 | F08 trên S1c còn trượt PP-SWR-051 12 lần, PP-SWR-100 1 lần |
| 20261118-2127-study-PP-TS-020-ac82bb3 | V1a gỡ F08 a, còn F08 b 3 trên 4 lượt; V1b, V1c gỡ cả hai nhưng thêm trượt R79 ở S1b a, c. F08 c chưa có trong suite |

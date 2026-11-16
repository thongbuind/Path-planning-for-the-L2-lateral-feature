# PP-PR-049 F08: bias yaw rate làm xe rời làn trên cua

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã khoanh vùng; sửa qua PP-TS-020 |
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

## 3. Cách sửa

- Không sửa được trong phạm vi PP-SWR-001 hiện tại. Đề xuất trade study: biên a_y vượt aysmax theo R79 5.6.2.1.1 (liên tục ≤ 0,3 m/s², ngắn hạn ≤ 40 % trong 2 s), chỉ dùng để giữ xe trong làn; ảnh hưởng PP-SWR-001, 005, 006, cờ giới hạn.
- 2026-11-16: người dùng đồng ý mở [PP-TS-020](../studies/PP-TS-020-path-ay-ceiling/study.md).

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

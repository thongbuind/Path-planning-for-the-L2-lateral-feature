# PP-PR-049 F08: bias yaw rate làm xe rời làn trên cua

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-14 |
| Requirement bị ảnh hưởng | PP-SWR-136; PP-SWR-051, 100 |
| Tái hiện | [20261114-1952-suite-regression-0776bad](../runs/20261114-1952-suite-regression-0776bad/report.md): F08 b, c trên S1c; F08 c trên S1a |

## 1. Hiện tượng

- F08 b (0,3 °/s) trên S1c: PP-SWR-051 −0,97 đến −1,28 m và PP-SWR-100 0,057 m, 3 lượt.
- F08 c (1 °/s, cảm biến thô) trên S1a, S1c: PP-SWR-100 0,073–0,079 m.
- F08 a (0,1 °/s) hết trượt so với d7ed84c.
- PP-SWR-136 đòi đạt tới 0,3 °/s (F08 a, b); F08 c nằm ngoài câu của 136 nhưng trong phạm vi chấm của 100.

## 2. Nguyên nhân

Chưa phân tích. Yaw rate dùng ở ego-motion (bù trễ T1, T4) và ở đo độ cong r/v của T5 tại s = 0.

## 3. Cách sửa

Phân tích log F08 b trên S1c: tách ảnh hưởng của ego-motion và của T5.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

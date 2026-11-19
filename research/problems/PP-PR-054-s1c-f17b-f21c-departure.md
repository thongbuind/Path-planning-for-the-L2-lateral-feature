# PP-PR-054 F17 b và F21 c trên S1c: xe rời làn ở cua chạm aysmax

| Mục | Nội dung |
|---|---|
| Trạng thái | Không còn tái hiện ở e3158a5: F17 b, F21 c trên S1c đạt |
| Mở ngày | 2026-11-14 |
| Requirement bị ảnh hưởng | PP-SWR-051; PP-SWR-130, 142, 148 |
| Tái hiện | [20261114-1952-suite-regression-0776bad](../runs/20261114-1952-suite-regression-0776bad/report.md): F17 b trên S1c, 3 lượt, DLC −0,87 đến −1,29 m. F21 c trên S1c (lượt nháp, ngoài bộ regression): DLC −0,82 m |

## 1. Hiện tượng

- F17 b (CRC sai) trên S1c: PP-SWR-051 trượt.
- F21 c (chỉ còn mép đường phải, 5 s) trên S1c: trượt cả ở commit 83dc910, trước PP-PR-052.

## 2. Nguyên nhân

Chưa phân tích. Bản build nháp nới giới hạn a_y HWA thêm 0,3 m/s² (PP-PR-049) không đổi kết quả của hai ca này, nên không cùng gốc với F08.

## 3. Cách sửa

Phân tích log: thời điểm lệch so với lúc có lỗi, nhánh T2 (suy tâm, coast) và giới hạn T10.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| 20261118-2030-suite-regression-e3158a5 | F17 b, F21 c trên S1c, VP-0, 1, 5, seed 1: đạt |
| [20261118-2127-study-PP-TS-020-ac82bb3](../runs/20261118-2127-study-PP-TS-020-ac82bb3/summary.md) | S1c + F17 b, VP-0 và VP-5, seed 3, 4: đạt ở mọi phương án |

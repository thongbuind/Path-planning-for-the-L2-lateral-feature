# PP-PR-009 F03 c: cả bốn vạch nhảy 3,5 m trong 2 s, xe đi theo sang làn bên

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở; sửa qua PP-TS-001 |
| Mở ngày | 2026-11-11 |
| Requirement bị ảnh hưởng | PP-SWR-051, 100 |
| Tái hiện | Lần chạy nháp smoke: F03 c trên S1a và S1c, seed 1, cả `PP_T7=quintic` và `qp` |

## 1. Hiện tượng

- DLC nhỏ nhất −1,1 đến −4,0 m: xe ra khỏi làn thật về phía làn bên.
- F03 a, b (một vạch, 0,05 và 0,5 s) và d (một vạch 0,5 m trong 2 s) đạt.

## 2. Nguyên nhân

- Cả bốn vạch dời 3,5 m cùng lúc, bề rộng làn không đổi; ego-motion không có chuyển động ngang.
- T2 R1 nhận thay đổi khi vị trí mới ổn định suốt `T_confirm` (1,0 s). Lỗi giữ 2 s, nên T2 nhận làn sai và xe đi theo.
- Không có kiểm tra nào so độ dời của cả làn với chuyển động ngang của xe.

## 3. Cách sửa

Thuộc câu hỏi của PP-TS-001 (J0–J3). J1 (song song, bề rộng) không bắt được ca này: cả làn dời, vẫn song song, bề rộng không đổi. Cần thêm một phép kiểm theo ego-motion: tốc độ dời ngang biểu kiến của cả làn (3,5 m trong 2 s, 1,75 m/s) so với chuyển động ngang của xe (gần 0). Lệch cho phép lấy theo sai số của ego-motion: bias yaw rate 0,3 °/s (PP-SWR-136) gây khoảng 0,26 m sau 2 s ở 25 m/s, nhỏ hơn nhiều so với 3,5 m. Hướng chung: cả làn dời một bước mà ego-motion không dời thì không nhận dù ổn định; coast theo T_coast rồi suy giảm. Cần giữ đúng các ca làn thật đổi (lối ra, nhập làn), nơi chỉ một biên dời.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

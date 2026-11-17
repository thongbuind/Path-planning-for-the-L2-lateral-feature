# PP-PR-057 F06 d: xe rời làn sau khi lỗi đã hết, rồi HWA lái tiếp ở làn bên

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở. Cơ chế 1: phương án B đã sửa trong cây làm việc 2026-11-17, chờ hồi quy; F06 d còn trượt. Cơ chế 2, 3 chờ quyết định |
| Mở ngày | 2026-11-17 |
| Requirement bị ảnh hưởng | PP-SWR-051; PP-SWR-125; PP-SWR-061; SG-01 |
| Tái hiện | [20261115-1126-suite-full-7495822](../runs/20261115-1126-suite-full-7495822/report.md): F06 d và các biến thể F06 a dài 2 s trên S1a, S1c, 25 lượt, DLC −0,97 đến −1,30 m. Lượt nháp 2026-11-16: `python3 -m eval.runner S1 a --fault F06 d --seed 1`, thư viện từ cây làm việc 2f86a0b (đã có reset mềm của PP-TS-021), VP-0 |

## 1. Hiện tượng

Lần chạy full, lỗi trên cả bốn vạch, ca chủ S1a và S1c:

| Lỗi | Dài 0,05–1 s | Dài 2 s | Vĩnh viễn |
|---|---|---|---|
| F06 (c2 ± 0,0005 1/m) | Đạt, DLC 0,3–0,6 m | Trượt 051, −1,0 đến −1,3 m | — |
| F03 (dời 3,5 m) | Đạt | Trượt 051, −1,0 đến −1,3 m | — |
| F02 (c0 nhảy 1 m) | Đạt | — | Trượt 051, −0,2 đến −0,5 m |

- Ranh giới đạt, trượt trùng `T_confirm` = 1 s.
- F06 d: PP-SWR-125 là 0,976, path bám gần như nguyên lane model sai.

Lượt nháp, lỗi 4,0–6,0 s, đường thẳng, 25 m/s. Lệch và v_lat đo trên chuyển động thật; path đọc từ Trajectory:

| Lúc [s] | Path | Xe |
|---|---|---|
| 4,0–5,08 | Không đổi | Giữa làn |
| 5,08 | Bắt đầu cong theo lane model sai | Giữa làn |
| 6,0 | Lỗi hết | Lệch 0,01 m, v_lat 0,10 m/s |
| 6,3–7,08 | Đứng yên trên hình sai | Lệch tới 0,30 m, v_lat 0,73 m/s |
| 7,08 | Bắt đầu quay về; đầu xa dời 0,05 m mỗi chu kỳ | DLC trái 0,35 m |
| 7,49 | Đang quay về | Lốp đè vạch |
| 8,38 | Đang quay về | Sang làn bên |
| 8,98 | Về tới nơi | Lệch 2,6 m |
| 9,48 | Chuyển sang tâm làn bên | Dừng ở 3,6 m; HWA lái tiếp, không cờ |

Xe lệch lớn nhất 1,78 m trước khi lane model đổi làn, khớp 1,80 m của lần chạy full.

## 2. Nguyên nhân

Ba cơ chế nối tiếp. Cơ chế 1 và 2 đọc từ Trajectory và code; log không ghi lane model đầu vào.

| # | Cơ chế | Khoảng | Hậu quả |
|---|---|---|---|
| 1 | T2 nhận hình học sai sau `T_confirm` (R1), đúng thiết kế (PP-PR-048). Khi lỗi hết, hình học đúng lại bị coi là bước nhảy mới và bị loại thêm `T_confirm`; planner bám reference line sai trong `T_coast` | 6,0–7,08 s | Lệch 0,01 → 0,30 m; v_lat 0,10 → 0,73 m/s |
| 2 | T4 bước 4 trộn một λ theo ngưỡng 0–1 s cho cả path: đầu xa chỉ dời `cont_margin` · 0,05 m mỗi chu kỳ, cần 1,9 s để dời 3,3 m | 7,08–8,98 s | Xe đè vạch sau 0,4 s. Lúc 7,08 s cần giảm tốc ngang khoảng 0,8 m/s² trong 0,35 m còn lại |
| 3 | Khi xe sang làn bên ngoài ý muốn, lane model đổi làn và HWA đưa xe về giữa làn mới | Từ 9,48 s | Không cờ, không trả lái |

- Cơ chế 1, xác nhận 2026-11-17 bằng log bộ nhớ biên của vạch L1 (bản build nháp ngoài cây làm việc, chỉ thêm lệnh in vào `check_line`; cùng ca, cùng seed, xe lệch 1,78 m như bản không in). Lệch tính theo bội của ngưỡng `k_jump`·σ, trên 1 là không nhất quán:

| Lúc [s] | Frame so với bộ nhớ đang dùng | Vị trí cũ (`previous`) | Kết quả |
|---|---|---|---|
| 4,108 | 3,5 | Không có | Frame sai đầu tiên bị loại; thành ứng viên |
| 5,108 | 0,15 (ứng viên đủ 1,0 s) | Bắt đầu giữ, tuổi 0,025 s | Hình học sai được nhận (R1) |
| 6,083 | 0,0 | Tuổi 1,000 s: hết hạn | — |
| 6,108 | 3,7 | Không còn | Frame đúng đầu tiên bị loại, chậm một chu kỳ so với lúc vị trí cũ hết hạn |
| 7,108 | 0,0 (ứng viên đủ 1,0 s) | Giữ hình sai | Hình học đúng được nhận |

- Vị trí cũ hết hạn đúng một chu kỳ (25 ms) trước frame đúng đầu tiên: nó được giữ `T_confirm` kể từ lần nhận, frame đúng tới sau 2 · `T_confirm` cộng trễ lane model.
- R2 lúc đó cũng đã yếu: tầm nhìn của vị trí cũ co về sau xe (kết thúc ở −10 m lúc 6,08 s), không còn đoạn chung với frame mới, nên phép kiểm hình dạng bị bỏ và chỉ còn so c0 ngoại suy (PP-PR-058).
- Cơ chế 2 có hai mặt: trộn chậm cũng làm path bám hình sai chậm hơn trong 5,08–6,0 s. Trộn theo đoạn bị loại ở PP-TS-021, nhưng suite của PP-TS-021 không có F06 d hay F03 c.
- Thang chậm của T2 (song song, bề rộng) trong Software Detailed Design mục 5 chưa có trong code: không có `parallel_max`, `width_dev_max`. Không bắt được F06 d (các vạch vẫn song song), nhưng liên quan F03.
- Khi L1, R1 cùng đủ tin, tâm làn lấy trung bình hai vạch kể cả khi bề rộng đo ngoài 2,5–5,5 m (T2 bước 2). F03 a một vạch, 2 s: DLC giảm từ 0,79 xuống 0,19 m; VP-5 trượt (−0,12 m).

## 3. Cách sửa

Đề xuất, chờ quyết định. Có nhiều cách nên cần trade study; cơ chế 1 có thể gộp vào hướng J1 của PP-TS-001.

| # | Phương án | Nhắm cơ chế | Ghi chú |
|---|---|---|---|
| A | Bề rộng đo ngoài 2,5–5,5 m: bỏ vạch vừa đổi, neo vào vạch còn lại cộng w_mem | F03 một vạch | Đã sửa trong cây làm việc 2026-11-17 (Software Detailed Design 1.23): dùng vạch cho tâm gần tâm cũ hơn. Unit test `test_width_outside_the_odd_keeps_the_stable_line`. 35 lượt nháp không đổi; chưa có ca benchmark chạy đơn được cho F03 một vạch dài 2 s, chờ lần chạy đủ bộ |
| B | Giữ vị trí cũ tới khi biên ổn định lại, không hết hạn theo `T_confirm` | 1 | Đã xác nhận nguyên nhân. Cần sửa PP-PR-058 cùng lúc, nếu không R2 chỉ so c0. Giới hạn: vị trí cũ chỉ dời bằng ego-motion, bias 0,3 °/s cho lệch 0,25 m sau 2 s (Software Architectural Design A.4), vượt ngưỡng `k_jump`·σ khoảng 0,13 m; không cứu được lỗi dài |
| C | Bước nhảy đồng thời trên mọi biên mà không kiểm chứng được: hết `T_coast` thì `path_valid = false` | 1 | J3 của PP-TS-001; mất khả dụng khi làn dời thật |
| D | Nhận theo bằng chứng trong bộ ước lượng đường V3 của PP-TS-005, thay nhận theo thời gian | 1 | V3 đang ghi xoá bộ nhớ khi T2 nhận thay đổi; giữ câu đó thì F06 d vẫn trượt |
| E | Xét lại trộn theo đoạn của T4 với F06 d, F03 c trong bộ chạy | 2 | Chỉ có lợi sau khi sửa cơ chế 1 |
| F | Quyết định HWA có được lái tiếp sau khi rời làn ngoài ý muốn không | 3 | Chưa có requirement; đưa vào HARA (SG-01) |

Phía đánh giá: F06 hiện chỉ có 1 s và 2 s; F03 có 0,05, 0,5 và 2 s. Thêm 1,5 s và 3 s để thấy đường cong theo thời lượng lỗi, không chỉ hai phía của `T_confirm`. Bộ chỉnh của P1 quét `T_confirm` nhưng chỉ có lỗi dài 1 s.

## 4. Phương án B đã áp (2026-11-17)

- T2: vị trí cũ được giữ chừng nào tầm nhìn của nó, dời bằng ego-motion, còn tới vị trí xe (`check_line`), thay cho `T_confirm`. Không thêm calibration parameter. Software Detailed Design 1.22.
- Sửa cùng PP-PR-058, nên R2 vẫn so được hình dạng trên đoạn chung.
- Unit test mới: `test_return_after_a_long_fault_is_taken_at_once`, `test_old_position_ends_when_its_range_is_behind_the_car`. Unit test C 15/15 đạt.

Lượt nháp, seed 1, VP-0, thư viện build ngoài cây làm việc. Trước là `build/planner` (2026-11-16); sau là bản có PP-PR-058 và phương án B. Ô ghi DLC nhỏ nhất / lệch xe lớn nhất [m]:

| Ca | Trước | Sau |
|---|---|---|
| S1 a + F06 d | −0,99 / 1,78 | −0,29 / 1,10 |
| S1 a + F03 c | −0,96 / 1,76 | −0,24 / 1,05 |
| S1 c + F06 d | −0,98 / 1,77 | −0,81 / 1,64 |
| S1 c + F06 e | 0,32 / 0,51 | 0,30 / 0,53 |
| S1 a, c, f; S4 a; S5 a; S6b d; S7 c; S12 a, b, c; S17 a; F01 a, c; F02 a, e; F03 a; F04 a; F05 a; F06 a | — | Như trước: cùng requirement trượt (S12 b, c trượt 032 ở cả hai), lệch xe chênh dưới 0,01 m |

- S1 a + F06 d sau khi sửa: hình học đúng được nhận lúc 6,108 s, ngay frame đúng đầu tiên. Xe vẫn rời làn vì cơ chế 2.
- Log T4 (bản build nháp có in `pp_stitch_blend`): từ 6,3 đến 7,8 s λ = 0,03–0,09, luôn do lệch ngang ở đầu xa quyết định (1,0–1,7 m). Cùng lúc path ứng viên chỉ lệch path cũ 0,03–0,11 m tại điểm 1 s. Độ cong tại xe về 0 lúc 7,5 s; lốp đè vạch lúc 7,86 s.
- Phương án mới cho cơ chế 2, chưa có trong PP-TS-019, 021: giữ một λ cho cả path, nhưng mỗi điểm so với ngưỡng của đoạn mình (0,05 / 0,1 / 0,2 m). Path gửi vẫn là tổ hợp lồi của hai path nên giữ tính khả thi; ở ca này λ lớn hơn khoảng 3–4 lần. Cần trade study với F06 d, F03 c trong bộ chạy.

## 5. Xác nhận

| Run ID | Kết quả |
|---|---|
| [20261117-0908-suite-regression-c56f0bf](../runs/20261117-0908-suite-regression-c56f0bf/report.md) | Phương án A, B: F06 d, F03 c trên S1a còn trượt 051 nhưng DLC từ −1,30…−0,96 m lên −0,60…−0,23 m; trên S1c F03 c −0,54…−0,17 m, F06 d −1,15…−0,73 m. F06 d lúc LKA, ELK hết trượt 086 (4 lượt); F06 b, e trên S1c hết trượt. Cơ chế 2 còn mở (PP-TS-022) |
| [20261117-1315-study-PP-TS-022-d2e7d27](../runs/20261117-1315-study-PP-TS-022-d2e7d27/summary.md) | Cơ chế 2 (PP-TS-022): V1 (trộn theo ngưỡng từng đoạn) sửa F06 d trên S1 a, S1 c (4 lượt, lệch 1,08 / 1,69 → 0,75 / 0,77 m); F03 c vẫn trượt; cái giá ở ca nhiễu (lệch tâm +0,03 đến +0,08 m). Quyết định chờ |

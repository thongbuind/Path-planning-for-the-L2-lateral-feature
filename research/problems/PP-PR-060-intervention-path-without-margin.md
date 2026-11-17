# PP-PR-060 Path LKA, ELK dừng sát vạch dù mới dùng khoảng một phần ba giới hạn

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở. Phương án A đã thử và gỡ 2026-11-17: lợi 2–3 cm, có trượt mới |
| Mở ngày | 2026-11-17 |
| Requirement bị ảnh hưởng | PP-SWR-086, 091; target PP-SWR-087; PP-SWR-110 đến 115; PP-TS-006; PP-PR-039 |
| Tái hiện | [20261115-1126-suite-full-7495822](../runs/20261115-1126-suite-full-7495822/report.md): DTLE của S5, S6 0,03–0,05 m ở mọi v_lat; S13 b ELK VP-3 −0,45 m; S5 a VP-4 −0,67 m. Lượt nháp 2026-11-17, seed 1, VP-0 (bảng dưới) |

## 1. Hiện tượng

Lượt nháp, thư viện build ngoài cây làm việc (có PP-PR-058 và phương án B của PP-PR-057):

| Ca | DTLE nhỏ nhất [m] | a_y path / giới hạn [m/s²] | Jerk path / giới hạn [m/s³] |
|---|---|---|---|
| S4 a (LKA, 0,2 m/s) | 0,112 | 0,44 / 3,0 | 0,63 / 5 |
| S4 c (LKA, 0,6 m/s) | −0,007 | 0,85 / 3,0 | 1,24 / 5 |
| S13 b (S4 c, EPS chậm 100 ms) | −0,023 | 0,85 / 3,0 | 1,24 / 5 |
| S5 a (ELK, 0,2 m/s) | 0,043 | 0,91 / 4,0 | 1,96 / 10 |
| S5 c (ELK, 0,6 m/s) | 0,047 | 1,27 / 4,0 | 2,36 / 10 |
| S6 a (ELK mép đường) | 0,034 | 0,91 / 4,0 | 1,96 / 10 |
| S7 a (ELK, xe làn bên) | — | 1,45 / 4,0 | 3,63 / 10 |

- DTLE của ELK gần như không đổi theo v_lat (0,03–0,05 m): path được chọn để lốp vừa chạm vạch.
- Path dùng 15–36 % giới hạn a_y và 13–36 % giới hạn jerk của chức năng. a_y thêm vào bằng a_y (đường thẳng): LKA dùng tới 56 % của 1,5 m/s², ELK tới 48 % của 3,0 m/s².

## 2. Nguyên nhân

`pp_intervention_begin`, `candidate_score` (`intervention.c`):

- Điểm của ứng viên là phần lốp trước lấn quá mức cho phép. LKA được lấn 0,3 m (`PP_MARK_DTLE_ALLOW_M`, đúng ngưỡng của PP-SWR-086); ELK 0 m.
- Ứng viên có thời lượng khởi đầu (`T_lka`, `T_elk`) được nhận ngay khi điểm ≤ 0. Chỉ khi nó lấn quá mức mới thử thời lượng khác, và dừng ở ứng viên đầu tiên có điểm ≤ 0.
- Không có số hạng nào thưởng khoảng hở lớn hơn, nên path không chừa gì cho sai số bám, trễ EPS hay sai số lane model.
- Hệ số quintic giữ nguyên suốt lần can thiệp; xe bám trễ thì path không lập lại.

## 3. Cách sửa

Có nhiều cách; phần so kỹ thuật thuộc PP-TS-006. Phương án, chờ quyết định:

| # | Phương án | Ghi chú |
|---|---|---|
| A | Trong các ứng viên T10 không cắt, chọn ứng viên có khoảng hở tới vạch lớn nhất; hoặc đặt khoảng hở tối thiểu là calibration parameter | Sửa nhỏ trong hàm chọn. Thời lượng can thiệp ngắn hơn, a_y và jerk cao hơn; cần đo target PP-SWR-081, 082 và cảm nhận người lái |
| B | Lập lại quintic từ trạng thái đo khi xe lệch profile quá ngưỡng | PP-TS-006; đổi cách giữ hệ số ở Software Detailed Design mục 10 |

## 4. Thử phương án A (2026-11-17, nháp, đã gỡ khỏi code)

Cài thử: calibration `intervention_margin` = 0,1 m trừ vào mức lấn cho phép; khi thời lượng khởi đầu không giữ được khoảng hở thì thử thời lượng ngắn dần, lấy ứng viên đầu tiên đạt. Seed 1, VP-0, trước → sau:

| Ca | DTLE [m] | a_y path [m/s²] | Jerk path [m/s³] | DLC phía đối diện [m] | Requirement trượt |
|---|---|---|---|---|---|
| S5 a | 0,043 → 0,069 | 0,91 → 1,44 | 1,96 → 4,01 | 0,87 → 0,47 | — |
| S5 c | 0,047 → 0,049 | 1,27 → 1,39 | 2,36 → 4,00 | 0,86 → 0,46 | — |
| S6 a | 0,034 → 0,059 | 0,91 → 1,44 | 1,96 → 4,01 | 1,03 → 0,65 | — |
| S6 b | 0,040 → 0,044 | 1,27 → 1,39 | 2,36 → 3,99 | 1,01 → 0,64 | 090 → 090 |
| S8 a | — | 0,85 → 1,31 | 1,82 → 3,81 | 0,88 → 0,88 | — → 090 |
| S4 a, c; S13 a, b; S7 a, c; S9 a; S4b d; S5 d; S16 d; S12 c | Không đổi | | | | Không đổi |

- Jerk gấp đôi chỉ thêm 0,2–2,6 cm DTLE; DLC phía đối diện giảm khoảng 0,4 m; S8 a trượt mới PP-SWR-090.
- LKA không đổi: mức lấn cho phép 0,3 m không phải ràng buộc đang chạm.
- Kết luận: nhận định ở mục 2 chỉ đúng một phần. DTLE của ELK chủ yếu do trạng thái của xe lúc bắt đầu can thiệp quyết định (vị trí lốp và v_lat khi nhận REQUEST), không do path dùng ít giới hạn. Đòn bẩy nằm ở thời điểm REQUEST (ADAS Function Specification, TLC) và ở phương án B; không sửa hàm chọn ứng viên.
- Code và calibration đã trả về như trước; 35 lượt nháp sau khi gỡ cho đúng giá trị cũ ở mọi tiêu chí.
- S16 d (ELK lần thứ ba) trượt PP-SWR-086 với DTLE −0,48 m ở cả hai bản; chưa phân tích.

## 5. Xác nhận

| Run ID | Kết quả |
|---|---|

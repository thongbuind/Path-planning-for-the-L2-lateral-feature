# quintic_ay_sampling

Sổ tay phát triển, không phải kết quả. Kết quả chính thức chỉ nằm ở PP-TS-031 và `research/runs/`.

## Ý tưởng

PP-TS-024 V2: path quintic_duration cộng một hiệu chỉnh ngang hình smoothstep bậc 7 (`common/driver_shape`), chọn trong tập ứng viên theo đỉnh a_y và jerk dự báo. Không áp dụng được thì giữ nguyên path quintic_duration.

## Thay đổi so với generator gốc

| Bước | Nội dung |
|---|---|
| 1 | `pp_t7_quintic_search` như quintic_duration; giữ lại path Frenet, points, samples (không tính lại path gốc) |
| 2 | Điều kiện mục 2.4 của PP-TS-024, đọc từ input: FOLLOW, start_from_car, đưa về giữa, offset, làn coasting/inferred/line_rejected, không có ObjectList |
| 3 | Từ path gốc: tầm nhìn `end` (điểm in_view liên tiếp từ 0) ≥ `qas_view_min_s`; hành lang = nửa (làn − xe) − `qas_corridor_margin_m` > 0; a_y cần trong [`qas_ay_need_min_mps2`, aysmax − `qas_ay_need_margin_mps2`) |
| 4 | Cắt tỉa chính xác: hiệu chỉnh bằng 0 cùng ba đạo hàm tại t = 0 và t ≥ end, nên a_y ở đó không đổi. Nếu max a_y ở các điểm đó đã ≥ đỉnh gốc − `qas_ay_gain_min_mps2` thì không ứng viên nào đạt: bỏ qua (cung dài, vào cua dài, ra cua) |
| 5 | Vật thể: vật thể có tâm lệch khỏi ref quá nửa bề rộng của nó và mép gần trong 1,5 bề rộng làn chặn hiệu chỉnh về phía nó; xe trong làn không chặn; chặn cả hai phía thì không áp dụng |
| 6 | Tập ứng viên: 2 đỉnh (`qas_peak_early`, `qas_peak_late` × end) × 2 dấu × thang biên độ bước `qas_amplitude_step_m` tới min(`qas_amplitude_m`, trần hành lang) |
| 7 | Chấm: ứng viên đạt khi a_y ≤ aysmax, jerk ≤ jerk gốc + `qas_jerk_tol_mps3`, và jerk ≤ `jerk_target_hwa` (hoặc ≤ jerk gốc nếu gốc đã vượt). Chọn a_y nhỏ nhất, hòa thì jerk nhỏ hơn. Chỉ áp dụng khi giảm ≥ `qas_ay_gain_min_mps2` |
| 8 | Ứng viên được chọn chạy lại T11 (`pp_output_points`) và `pp_feasibility_check` thật; trượt thì giữ gốc (mã 12) |

Tối ưu CPU:

- Mẫu đường tham chiếu (kappa, dkappa) lấy một lần mỗi chu kỳ (`lab_qas_frame`); mỗi vị trí đỉnh tính một hình dạng đơn vị; ứng viên = base + offset × shape, cả hai dấu và mọi biên độ dùng chung.
- Dự báo a_y bằng công thức độ cong của T11 viết lại không có atan/cos/tan (cos(atan t) = 1/√(1+t²)); khớp `pp_feasibility_check` tới 1e-9 (L0).
- Mỗi hướng tăng biên độ dần và dừng ở mức đầu tiên không đạt hoặc không còn giảm a_y (đỉnh a_y, jerk theo biên độ gần lồi). L0 vét cạn cho cùng kết quả trên cua ngắn mẫu.
- Bước 4 bỏ hẳn việc chấm trên cung dài. Chỉ ứng viên thắng đi qua T11 đầy đủ (một lần đi ref nữa).

## Quyết định tự chốt (để duyệt)

| # | Quyết định | Lý do |
|---|---|---|
| D1 | Tập ứng viên theo V2 (2 đỉnh × 2 dấu), không theo V3 (3 đỉnh × 4 biên độ × 2 dấu) | Đúng PP-TS-024 mục 2 ý 3 và lưới của plan.yaml (cặp đỉnh × biên độ); V3 không gắn được với lưới |
| D2 | Luật chọn theo PP-TS-024 (min a_y với ràng buộc jerk trong dung sai, giảm ≥ 0,05 m/s²), không dùng điểm a_y + 0,10 × jerk của pilot | Mỗi ngưỡng có nguồn ở study; trọng số 0,10 của pilot không có nguồn và cộng hai đơn vị khác nhau |
| D3 | Thêm thang biên độ (bước 0,025 m) từ V3 | Thử với một biên độ: trên cua ngắn mẫu, biên độ 0,05–0,20 m tăng jerk 0,4–1,6 m/s³ nên không ứng viên nào đạt; biên độ nhỏ hơn mới qua dung sai jerk. PP-TS-024 mục 3 cũng nói biên độ thực có thể thấp hơn. Bước cố định theo mét để ba mức lưới có tập ứng viên lồng nhau |
| D4 | Dung sai jerk tương đối 0,10 m/s³ so với path gốc (dung sai 069 của H1) cộng trần `jerk_target_hwa` như pilot | "jerk trong dung sai" của PP-TS-024 mục 2 ý 3 |
| D5 | Thu nhỏ cả biên độ theo hành lang (giải tích), không kẹp từng mẫu | PP-TS-024 mục 2 ý 1 |
| D6 | Thay luật "có vật thể là dùng V0" của pilot bằng hành lang từng phía theo vật thể | PP-TS-024 mục 2.4 ("hành lang từng phía ... khoảng hở với vật thể"). Trên tuning, luật pilot tắt hiệu chỉnh ở 97 % chu kỳ S14c và 60 % S3a dù vật thể không ở làn kề cùng phía |
| D7 | Đỉnh tính theo phần của end (thời lượng in_view, tối đa 3 s), như pilot | Đơn vị của lưới trong PP-TS-024 mục 3 |
| D8 | Các ngưỡng của pilot (0,025 m; 0,4; 0,1 m/s²; 2,0 s; 0,30 m) thành tham số `qas_` cố định | Không có nguồn ngoài pilot |
| D9 | work = số lần thử thời lượng + số ứng viên đã chấm | test_t7_contract (telemetry) đòi work > 0 cả khi fallback |

## Lần dò bằng quick bench

Đã dùng 13/20 lượt ở đợt đầu, thêm 4/10 lượt ở đợt S24 a và 4/6 lượt ở đợt S24 b (`--runs tuning` tính 2). Hai lần hỏng trước khi chạy (lỗi CMake, sai cú pháp shell) không tính.

| Ngày | Nhãn | Thay đổi | Nhận xét |
|---|---|---|---|
| 2026-11-24 | `quintic_ay_sampling-tm` (quick, `--against quintic_duration`) | Bản đầu: luật pilot cho vật thể, thang biên độ | Fallback 100 %: mã 11 (không giảm đủ) phần lớn, 9 (không cua), 10 ở S1b a. Lệch output 0. work max 9 |
| 2026-11-24 | `quintic_ay_sampling-tm` (tuning) | Thêm cắt tỉa bước 4 | Fallback 100 % trên 12 dòng; mã 6 (vật thể) 97 % ở S14c, 61 % ở S3a, 81 % ở S22a |
| 2026-11-24 | `quintic_ay_sampling-tm` (tuning) | Hành lang từng phía theo vật thể (D6) | Mã 6 về 0. Vẫn fallback 100 %: các cua của tuning là cung dài nên đỉnh a_y nằm ngoài vùng hiệu chỉnh (mã 11, phần lớn bị cắt ở bước 4, work 1) |
| 2026-11-24 | `quintic_duration-ad15c8ac` (tuning, `T_hwa=3.0` = mặc định) | Mốc tuning ở nhãn riêng, không ghi đè `quintic_duration` | 0 lượt trượt |
| 2026-11-24 | `quintic_ay_sampling` (tuning, không telemetry, `--against quintic_duration-ad15c8ac`) | Mặc định, đo thời gian | Mọi chỉ số +0,000, 0 trượt, lệch output vòng hở 0. Trung vị p99 0,98 ms so với 1,03 ms; tỉ số ghép cặp trung vị 1,03 (nhiễu máy) |
| 2026-11-24 | `quintic_ay_sampling-tm-4e7d4317` (quick, (0,35; 0,55) × 0,30) | Góc lưới | Fallback 100 %, giống mặc định |
| 2026-11-24 | `quintic_ay_sampling-tm-bccf722d` (quick, (0,45; 0,65) × 0,30) | Góc lưới | Fallback 100 %, giống mặc định |
| 2026-11-24 | `quintic_ay_sampling` (tuning, không telemetry, `--against quintic_duration-ad15c8ac`) | Đo lại sau khi sửa CMake, build sạch không đi vòng | Mọi chỉ số +0,000 trên 24 lượt, 0 trượt, lệch output 0. Trung vị p99 0,59 ms (max 1,42) so với 0,61 ms (max 1,96); tỉ số ghép cặp trung vị 1,04 |
| 2026-11-24 | `quintic_duration-ad15c8ac` (quick, có S24 a) | Mốc quick mới (10 lượt); ghi đè bản tuning cùng nhãn | S24 a: 070 0,606; 068 2,175; 069 1,647 |
| 2026-11-24 | `quintic_ay_sampling-tm` (quick) | Mặc định, có S24 a | S24 a fallback 100 %: mã 9 592, 11 119, 10 83 chu kỳ; work max 14 (có chấm ứng viên). Mọi chỉ số +0,000 |
| 2026-11-24 | `quintic_ay_sampling-tm-3d975608` | Chẩn đoán: `qas_ay_gain_min_mps2` 0,005 | S24 a áp dụng 2 chu kỳ (fallback 99,7 %): 068 −0,000, 069 −0,028, 070 +0,017, 050 −0,017 |
| 2026-11-24 | `quintic_ay_sampling-tm-8d24fb21` | Chẩn đoán: thêm `qas_jerk_tol_mps3` 2,0 | S24 a áp dụng 15 chu kỳ (98,1 %): 068 −0,027, 069 −0,190, 070 −0,015, 050 +0,016; S1g_F01a vòng hở lệch output 0,05 m. Không đổi mặc định |
| 2026-11-24 | `quintic_duration-ad15c8ac` (quick, có S24 b) | Mốc quick 11 lượt | S24 b: 070 0,205; 068 1,791; 069 1,465; 050 0,673 |
| 2026-11-24 | `quintic_ay_sampling-tm` (quick) | Mặc định, có S24 b | S24 b fallback 100 %: mã 9 618, 11 144, 10 19, 8 13; work max 13. Mọi dòng +0,000 |
| 2026-11-24 | `quintic_ay_sampling-tm-46481f94` | Chẩn đoán: `qas_jerk_tol_mps3` 2,0 | S24 b áp dụng 1 chu kỳ (99,9 %), mọi chỉ số ±0,000. Trần `jerk_target_hwa` 2,5 vẫn chặn |
| 2026-11-24 | `quintic_ay_sampling-tm-ea09238a` | Cặp đỉnh (0,35; 0,55) | S24 b fallback 100 %, giống mặc định |

Dò trên cua tổng hợp (chỉ trong L0, không phải benchmark): cua ngắn 1–1,75 s, a_y 1–2 m/s², 20–30 m/s, có ứng viên giảm đỉnh a_y 0,1–0,45 m/s² mà jerk tăng ≤ 0,1 m/s³ ở phần lớn vị trí cua trong tầm nhìn; cua ≥ 3 s gần như không có.

### S24 a (cua ngắn của tuning, 110 km/h)

- Dò tổng hợp cùng hình học (clothoid 50 m, R 450 m, cung 30 m, clothoid 50 m, 30,6 m/s), quét vị trí cua trong tầm nhìn: giảm đỉnh a_y dự báo lớn nhất ≤ 0,018 m/s² với cả ba cặp đỉnh, biên độ tới 0,30 m, kể cả khi bỏ ràng buộc jerk; trong dung sai jerk ≤ 0,012. Ngưỡng 0,05 không bao giờ đạt. Thử hình dạng một bướu sin⁴ (độ cong giảm cả ở đỉnh) cũng chỉ ≤ 0,012.
- Nguyên nhân chung: hiệu chỉnh nằm trong tầm nhìn (end ≤ 3 s) và phải bằng 0 ở t = 0 và t = end. Nó chỉ hạ được một bướu a_y ngắn hơn khoảng 1–1,5 s, nằm trong tầm nhìn và có a_y thấp hai bên. Bướu a_y của S24 a dài 4,25 s (130 m ở 30,6 m/s), dài hơn cả tầm nhìn, nên đỉnh a_y trong tầm nhìn luôn nằm trên đoạn cung, ở t = 0 hoặc gần end. "Ngắn" phải tính theo thời gian, không theo mét. Đây là giới hạn hình học của phương án, không chỉnh được bằng calibration.
- Mã 10 ở 83 chu kỳ: a_y cần ước lượng vượt 2,4 m/s² dù a_y danh định 2,07 (ước lượng độ cong vòng kín lệch lên khoảng 15 %). Dù không chặn, lợi dự báo vẫn ≤ 0,02.
- Đề xuất plan.yaml: giữ nguyên mặc định và các mức lưới. Trên tuning (kể cả S24 a), mọi mức lưới cho cùng kết quả vì không ứng viên nào đạt.

### S24 b (72 km/h, cả cua 2,5 s)

- Dò tổng hợp cùng hình học (clothoid 20 m, R 180 m, cung 10 m, clothoid 20 m, 20 m/s), quét vị trí cua: bỏ ràng buộc jerk thì có ứng viên giảm đỉnh a_y 0,1–0,33 m/s², nhưng jerk path tăng 2–5,8 m/s³ (từ 2,22 lên 4–8). Trong dung sai jerk (+0,10, trần 2,5) lợi ≤ 0,02 ở hầu hết vị trí; ≥ 0,05 chỉ ở 1–2 vị trí rời rạc (mặc định 0,074 khi xe đã vào cua 17 m; cặp (0,35; 0,55) 0,097 khi cua còn cách 25 m). Vòng kín không chu kỳ nào đạt.
- Nguyên nhân chung: ràng buộc jerk. Smoothstep bậc 7 với nửa 1,2 s thêm jerk khoảng 7 lần phần a_y nó bớt, và jerk thêm rơi đúng chỗ clothoid đã cho jerk lớn nhất (v³·dκ/ds = 2,22 m/s³). Dung sai +0,10 m/s³ (guard 069 của H1) và trần `jerk_target_hwa` không để lại chỗ. Với S24 a thì giới hạn là độ dài theo thời gian (mục trên); với S24 b là jerk.
- Đề xuất plan.yaml: giữ mặc định (0,40; 0,60; 0,20) và các mức lưới. Cặp đỉnh chỉ đổi vị trí rời rạc nào đạt, không có mức nào tốt hơn ổn định; biên độ không có tác dụng vì ứng viên đạt (nếu có) ở biên độ nhỏ.

## Vấn đề còn mở

- Phần tuning không có cua có bướu a_y ngắn theo thời gian (S24 a dài 4,25 s), nên trên tuning generator trùng quintic_duration ở mọi chu kỳ; không dò được mặc định hay lưới. Hiệu quả chỉ có thể thấy ở phần test (S1f, S14e, S1b f).
- Hiệu chỉnh gắn với t = 0 và trượt theo tầm nhìn mỗi chu kỳ (như pilot): xe chỉ thấy nó qua preview của controller và blend T4, không phải một đường cắt cua cố định trên đường. Chưa đo được vòng kín.
- Chọn ứng viên có thể đổi giữa các chu kỳ (đỉnh sớm/muộn, bật/tắt); T4 blend giữ PP-SWR-100 đến 102 nhưng có thể làm hiệu chỉnh yếu đi. Chưa thêm hysteresis (cần ws giữ lựa chọn trước) vì không có dữ liệu tuning để dò.
- Lỗi CMake khi `PP_T7_LAB_DIR` rỗng (`planner/CMakeLists.txt` dòng 40) đã được session contract sửa ngày 2026-11-24; các lần đo cuối build sạch bằng lệnh thường.

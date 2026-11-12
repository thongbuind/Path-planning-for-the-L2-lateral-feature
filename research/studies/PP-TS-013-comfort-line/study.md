# PP-TS-013 Path êm trong hành lang an toàn (ý tưởng racing line)

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở; nghiên cứu nguyên mẫu Python, chưa áp dụng vào planner |
| Mở ngày | 2026-11-12 (mở với số PP-TS-012; đổi sang PP-TS-013 cùng ngày vì trùng số với study đưa v_y về t0, study đó đã có problem report trỏ tới) |
| Khóa ngày | — |
| Quyết định ngày | — |
| Liên quan | PP-TS-003 (T7 C QP); PP-SWR-001, 003, 004, 006, 051, 053, 056, 059, 100 |

## 1. Câu hỏi

- Quyết định cần đưa ra: path HWA có nên chủ động dùng một hành lang hẹp quanh tâm làn để giảm a_y, jerk và thao tác đánh lái, không chỉ khi chạm giới hạn a_y như PP-TS-003 V1.
- Vì sao cần: yêu cầu người dùng 2026-11-12, lấy ý tưởng racing line (ngoài → trong → ngoài). Mục tiêu là path êm nhất, không phải nhanh nhất.

## 2. Phương án

| ID | Phương án | Cách cài (nguyên mẫu) | Ghi chú |
|---|---|---|---|
| B0 | Bám tâm làn (d = 0) | — | Mốc, như path hiện tại khi không lệch tâm |
| R-cam | Tối ưu d(s) trong hành lang, chỉ thấy tầm nhìn camera 80 m, lập lại mỗi 1 m | `prototype.py`, `plan_receding` | Ứng viên |
| R-glob | Như R-cam nhưng biết trước cả đường | `plan_global` | Tham chiếu; cần bản đồ, hệ thống L2 không có |

Bài toán của R-cam, R-glob:

| Phần | Cách làm |
|---|---|
| Biến | d(s) lệch khỏi tâm làn, mỗi 1 m |
| Độ cong path | κ_p ≈ κ_r + d'' + κ_r²·d |
| Chi phí | (a_y/1)² + 4·(jerk/1)² + 1·(d/1 m)² mỗi điểm, a_y = v²κ_p, jerk = v³·dκ_p/ds |
| Ngưỡng đỉnh a_y | Phạt mềm (trọng số 1000) phần a_y path vượt a_y lớn nhất mà tâm làn cần trong ±80 m quanh điểm đó |
| Hành lang | trị tuyệt đối của d ≤ min(`offset_max`, khoảng trống mỗi bên − `dlc_offset_min`) = 0,3 m với VP-0, làn 3,5 m |
| Liên tục | d, d', d'' ở 3 điểm đầu giữ theo path đã đi |
| Ngoài tầm nhìn | Giả định độ cong cuối cùng thấy được kéo dài 80 m; cuối đoạn đó path song song và về tâm (phạt mềm) |
| Bộ giải | QP chặn hộp, active set, khởi động ấm từ chu kỳ trước; sai khác với scipy `lsq_linear` < 1e-8 m |

Lựa chọn nghiên cứu, chưa chốt:

| Lựa chọn | Giá trị | Lý do |
|---|---|---|
| Trọng số W_J, W_D | 4; 1 | W_D = 0,02 làm path không về tâm sau cua (receding horizon cứ hoãn); 1 về tâm trong khoảng 1 s mà gần như không mất lợi ích |
| Ngưỡng đỉnh a_y | ±80 m quanh điểm | Không có ngưỡng: cua có cung dài thì a_y đỉnh tăng 2–5 % (cắt vào rồi phải cong gắt hơn cung để quay ra). Chỉ lấy trong cửa sổ nhìn thấy: path kẹt ở mép hành lang sau cua |
| Ngoại suy 80 m, về tâm | — | Không ngoại suy: path ôm phía trong suốt cung dài |
| Hành lang 0,3 m | `offset_max` hiện có | Cùng mức đã chấp nhận cho dời tâm khi có xe lớn (PP-SWR-055); không có nguồn quy định |

## 3. Cách đánh giá

Chưa khóa. Lần này là nguyên mẫu để xem hướng có đáng làm không.

| Mục | Nội dung |
|---|---|
| Đường | Rf (đường nghiên cứu, không thuộc benchmark: R 250 m, đổi hướng 20°, clothoid 60 m, 90 km/h); S1c, S1d, S1f, S1be, S14e lấy hình học từ `benchmark/roads` |
| Xe, làn | VP-0, làn 3,5 m, camera 80 m |
| Vòng kín | Mô hình bicycle động lực học của `sim/vehicle`; luật điều khiển và hệ số của stand-in (`sim/stand_ins/lateral_controller.py`, SQTS 4.6); trễ 50 ms; giới hạn tốc độ vô-lăng 6 rad/s |
| Chỉ số | Trên chuyển động thật của xe: a_y đỉnh, jerk đỉnh và rms, tốc độ vô-lăng đỉnh, tổng hành trình vô-lăng, số lần đảo lái (khe 0,5°), khoảng hở thân xe kể gương tới tâm vạch |
| Chưa có | Lane model có nhiễu, trễ camera, planner C, ACC, xe khác |

## 4. Lần chạy

| Run ID | Phương án | Ghi chú |
|---|---|---|
| — | B0, R-cam, R-glob | Nháp: `python3 prototype.py` rồi `python3 dashboard.py`; 232 s, một tiến trình. Không phải lần chạy chính thức: không dùng planner C, không có `--record` |
| — | B0, R-cam trên Rf | Nháp: `python3 sample_figure.py` → `sample-rf.png` (hình nhìn từ trên xuống, turn-in, apex, exit, chỉ số); 4 s |
| — | B0, R-cam trên cua 90°, R 80 m, 50 km/h | Nháp: `python3 sample_figure.py --radius 80 --deg 90 --kmh 50 --clothoid 30 --exag 8 --out sample-R80-90deg.png`. a_y đỉnh −3 %, tốc độ vô-lăng đỉnh −38 %, jerk rms −21 %, đảo lái 4 → 6 (path lắc một nhịp sau lối ra), path đổi giữa hai chu kỳ 0,029 m |
| — | R-cam, quét loại cua | Nháp: `python3 best_case_sweep.py 80` và `150` → `best_case_sweep_view80.json`, `_view150.json`. Cua đơn và chữ S, 6–90° mỗi cua, 90 km/h, a_y tâm làn 2,0 m/s², mức path |
| — | B0, R-cam trên khúc uốn 6° (hai clothoid 33 m, R 312 m, 90 km/h), camera 150 m | Nháp: `python3 sample_figure.py --radius 312.5 --deg 6 --kmh 90 --clothoid 32.7249 --exag 12 --view 150 --lead 300 --out sample-best-6deg.png`. a_y đỉnh −56 %, tốc độ vô-lăng đỉnh −85 %, jerk rms −69 %, path đổi giữa hai chu kỳ 0,001 m |

Kết quả quét loại cua (mức path, a_y đỉnh của R-cam so với B0):

| Cua đơn | 6° | 10° | 15° | 20° | ≥ 30° |
|---|---|---|---|---|---|
| Camera 80 m | −55 % (path đổi 161 mm) | −36 % (122 mm) | −17 % (114 mm) | −2 % | ≈ 0 |
| Camera 150 m | −56 % (0,7 mm) | −37 % (2,1 mm) | −16 % (1,8 mm) | −4 % (145 mm) | ≈ 0 |

Cua chữ S của R171 Annex 4, 4.2.4.1 (hình học S1f, 90 km/h, đoạn thẳng trước cua 300 m), mức path:

| Tầm nhìn | a_y đỉnh | jerk rms | Path đổi giữa 2 chu kỳ |
|---|---|---|---|
| 80 m | −45 % | −48 % | 129 mm |
| 126 m (buffer hiện tại của planner) | −49 % | −52 % | 126 mm |
| 150 m | −49 % | −52 % | 32 mm |

Vòng kín ở 150 m (`python3 sample_figure.py --xodr ../../../benchmark/roads/S1f.xodr --kmh 90 --deg 10 --exag 12 --view 150 --lead 300 --out sample-r171-sbend.png`): a_y đỉnh 1,84 → 0,89 m/s² (−51 %), tốc độ vô-lăng đỉnh −63 %, tổng hành trình vô-lăng −46 %, khoảng hở thân xe–vạch 0,67 → 0,48 m.

- Hiệu quả nhất: khúc uốn đổi hướng nhỏ, cả khúc cua nằm trong tầm nhìn. Cua chữ S cùng góc kém hơn cua đơn một chút.
- Tầm nhìn 150 m là giả định thử trong research, không phải giả định cảm biến của SQTS (80 m). Với nó, PP-SWR-100 đạt ở mọi cua tới 15°. Vấn đề PP-SWR-100 ở mục 5 chủ yếu do khúc cua dài hơn tầm nhìn.

## 5. Kết quả

**Nguyên mẫu, nháp, không dùng để quyết định.** Hình: `dashboard.png`. Số liệu: `results.json`.

R-cam so với B0, vòng kín:

| Đường | a_y đỉnh | jerk rms | Tốc độ vô-lăng đỉnh | Khoảng hở min (m) |
|---|---|---|---|---|
| Rf | −16 % | −23 % | −20 % | 0,68 → 0,46 |
| S1f | −49 % | −51 % | −60 % | 0,67 → 0,51 |
| S14e | −50 % | −49 % | −56 % | 0,44 → 0,50 |
| S1d | −2 % | −6 % | −10 % | 0,76 → 0,65 |
| S1c | −2 % | −11 % | −28 % | 0,72 → 0,61 |
| S1be | −4 % | −18 % | −39 % | 0,66 → 0,47 |

- Lợi nhiều ở cua ngắn và chữ S: path thấy lối ra trong 80 m.
- Cua có cung dài: a_y đỉnh gần như không đổi; jerk và vô-lăng vẫn giảm.
- R-glob không tốt hơn R-cam đáng kể. Không cần bản đồ cho phần lợi này.
- Quét hành lang: Rf và S1f gần bão hòa ở 0,3 m; mở rộng tới 0,6 m chỉ thêm 1–2 điểm %.
- Jerk đỉnh S1d tăng 13 % (0,37 → 0,42 m/s³), vẫn thấp.

Vấn đề tìm được:

| Vấn đề | Chi tiết | Hướng xử lý |
|---|---|---|
| PP-SWR-100 | Trên Rf, S1f, S14e, đoạn 2–3 s của path đổi tới 0,11–0,13 m giữa hai lần lập liên tiếp, khi lối ra cua vừa vào tầm nhìn. Đoạn 0–1 s đổi ≤ 0,015 m | Thêm chi phí liên tục so với path cũ như `qp_w_cont` của PP-TS-003 V1, rồi đo lại lợi ích |
| PP-SWR-006 | Câu hiện tại so a_y path với a_y tâm làn cần. Khi a_y cần > aysmax, path cắt cua có a_y thấp hơn aysmax − `epsilon_ay` dù vẫn ở trong làn (S14e) | Cần viết lại theo ý gốc của R79 5.6.2.2.3, ví dụ theo a_y mà path cần để ở trong làn |
| PP-SWR-053, 059 | Đo thời gian tới lúc lệch ngang ≤ 0,1 m; S2d chạy trên cua R 500 m. Path cắt cua có thể làm kết quả xấu đi | Đo khi tích hợp |
| PP-SWR-056 | Không được lệch về phía xe lớn. Hành lang phải hẹp về 0 ở phía đó | Hành lang theo từng phía, là input liên tục, như PP-TS-003 đã đề xuất |
| Phía trong cua | Đường hai chiều: phía trong cua trái là làn ngược chiều | Hành lang theo từng phía; cần quyết định có cắt về phía đó không |

## 6. Đề xuất

Chưa đề xuất áp dụng. Bước tiếp theo nếu người dùng muốn đi tiếp:

1. Thêm chi phí liên tục với path cũ, đo lại PP-SWR-100 và lợi ích.
2. Hành lang theo từng phía làm input; nối với T8 (PP-SWR-055, 056).
3. Gộp vào PP-TS-003 thành phương án V3 của T7 C (cùng QP: thêm hành lang và ngưỡng đỉnh a_y), chạy trên bộ chính thức.
4. Đề xuất viết lại PP-SWR-006.

## 7. Quyết định

- Người quyết, ngày:
- Chọn:
- Lý do:
- Đưa vào:
- Hồi quy:

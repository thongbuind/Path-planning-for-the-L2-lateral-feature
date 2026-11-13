# PP-TS-013 Path êm trong hành lang an toàn (ý tưởng racing line)

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở. Đã so sánh nháp qua SIL với quintic C làm mốc |
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
- Tầm nhìn 150 m là mức thử nghiên cứu. SQTS dùng 80 m danh định. Ở 150 m, cua đơn 15° đổi 1,8 mm, còn cua chữ S 15° đổi 92,7 mm. Phép đo này dùng đường tham chiếu thật của nguyên mẫu.

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
| PP-SWR-006 | Câu hiện tại so a_y path với a_y tâm làn cần. Khi a_y cần > aysmax, path cắt cua có a_y thấp hơn aysmax − `epsilon_ay` dù vẫn ở trong làn (S14e) | Thử đồng thời sàn và trần theo SRS ở mục 5.2 |
| PP-SWR-053, 059 | Đo thời gian tới lúc lệch ngang ≤ 0,1 m; S2d chạy trên cua R 500 m. Path cắt cua có thể làm kết quả xấu đi | Đo khi tích hợp |
| PP-SWR-056 | Không được lệch về phía xe lớn. Hành lang phải hẹp về 0 ở phía đó | Hành lang theo từng phía, là input liên tục, như PP-TS-003 đã đề xuất |
| Phía trong cua | Đường hai chiều: phía trong cua trái là làn ngược chiều | Hành lang theo từng phía; cần quyết định có cắt về phía đó không |

### 5.1. Giới hạn độ đổi của path trong tầm nhìn

R-limited giải cùng QP với R-cam. Sau khi dời path cũ theo 1 m đã đi, lấy phần chung trong 3 s và trong tầm nhìn hiện tại. Từ chênh lệch (d), (d') và độ cong xấp xỉ, tính một hệ số trộn cho cả đường. Mục tiêu từng cặp path là 45 mm, 4,5 mrad và 0,00027 1/m, tương ứng 90% ngưỡng PP-SWR-100 đến 102. Trộn trực tiếp (d(s)) rồi suy ra hình học. Hai đường nằm trong cùng hành lang tĩnh nên đường trộn cũng nằm trong hành lang đó.

Chạy `continuity_experiment.py` bằng một luồng BLAS. Kết quả ở `continuity_results.json` gồm số liệu chuyển động xe, giới hạn hành lang và số đo theo từng cặp path. Độ cong đường tham chiếu vẫn là độ cong thật. Hai ca chặn phía của S1f dùng hành lang cố định suốt ca. Phép đo trên từng path xấp xỉ gia tốc ngang tại các nút trong tầm nhìn, kèm biên nhỏ nhất so với sàn PP-SWR-006 trên 0–1 s.

| Ca, tầm nhìn | Lệch ngang giữa hai path, mm | Đỉnh a_y xe, m/s² | Chu kỳ phải trộn |
|---|---|---|---|
| Rf, 80 m | 123,0 → 45,0 | 2,19 → 2,22 | 3/348 |
| S1f, 80 m | 128,8 → 45,0 | 0,936 → 0,938 | 8/401 |
| S14e, 80 m | 108,8 → 45,0 | 2,00 → 2,00 | 6/401 |
| S1c, 80 m | 2,5 → 2,5 | 2,51 → 2,51 | 0/351 |
| S1f, 150 m | 31,9 → 32,2 | 0,893 → 0,893 | 1/401 |

Ở S1f, R-limited giữ mức giảm 49% đỉnh a_y của xe so với bám tâm làn. Khi chặn cố định phía trái hoặc phải, path ở trong hành lang đã cấp và mức giảm lần lượt là 32% và 36%. Hai thử nghiệm đó đo đáp ứng với biên tĩnh.

Ở S14e 80 m, a_y đỉnh của xe vẫn giảm khoảng 50%. Trên các path được lập theo từng chu kỳ, a_y đỉnh xấp xỉ 2,729 m/s², cao hơn giới hạn 2,5 m/s² của PP-SWR-001. Ở những điểm trong 0–1 s cần hỗ trợ sát giới hạn, giá trị thấp nhất xấp xỉ 1,374 m/s², hụt 0,926 m/s² so với sàn 2,3 m/s² của PP-SWR-006. Giữ hai ràng buộc này là việc cần thử trước khi dùng kết quả S14e để xếp hạng độ êm.

### 5.2. Sàn và trần gia tốc ngang với độ cong ước lượng

R-ay bắt đầu bằng path R-limited. Ở các nút trong tầm nhìn, chặn trị tuyệt đối a_y ở 2,5 m/s². Trên 0–1 s, khi độ cong đầu vào báo a_y cần vượt 2,5 m/s², áp thêm sàn 2,3 m/s² theo hướng cua. Một bài toán tuyến tính đo mức nới chung nhỏ nhất cho hai ngưỡng trong hành lang ±0,3 m, giữ ba điểm đầu và ba giới hạn liên tục của mục 5.1. Nếu mức nới nằm trong dung sai số 0,00001 m/s², bài toán bậc hai chiếu toàn bộ đường, kể cả đoạn nối với đuôi ngoại suy, về tập nghiệm khả thi gần path R-limited. Khi bộ giải dừng sớm, chỉ nhận nghiệm đã kiểm các ràng buộc và có chi phí không cao hơn điểm khởi tạo. Cửa sổ bất khả thi được ghi lại và dùng path R-limited để tiếp tục phép đo. Các cửa sổ đó vẫn được tính khi báo vi phạm.

Chạy trong thư mục hồ sơ bằng `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -B acceleration_experiment.py`. `acceleration_results.json` giữ cả số đo path theo hình học thật và số liệu chuyển động xe. Cửa sổ dùng lưới 1 m. Phép đo xét các nút trong phần quan sát của horizon 3 s.

| Ca dùng độ cong thật | Cửa sổ R-ay cần nới | Mức nới lớn nhất, m/s² | Đỉnh a_y trên path, m/s² |
|---|---|---|---|
| S1f, 90 km/h | 0/401 | 0 | 1,158 |
| S14e, 130 km/h | 61/401 | 0,924 | 2,776 |
| S1be, 90 km/h | 279/311 | 0,630 | 3,131 |
| Hình học S14e, 110 km/h | 0/401 | 0 | 1,986 |

Trên đoạn cung R 200 m ở 90 km/h, thử thả tự do ba điểm đầu và bỏ giới hạn liên tục vẫn cần nới ít nhất 0,080 m/s² trên cửa sổ 75 điểm. Ở S14e, phép thử hạ tốc độ hằng từ 130 xuống 110 km/h cho a_y đỉnh của xe 1,412 m/s² khi dùng độ cong thật. Hai kết quả này định lượng vai trò của tốc độ và độ dài cua trong hành lang đang xét.

Đối chứng camera lấy mẫu đường tâm ở 20 Hz, trễ 100 ms, tầm nhìn dọc đường 80 m tại lúc chụp. Thử giữ độ cong thật trong phần tầm nhìn còn lại, khớp một đa thức bậc ba cho cả đoạn, rồi thêm nhiễu Gaussian σ = 0,03 m vào từng mẫu ngang trước khi khớp, seed 1. Chỉ tín hiệu độ cong nhìn trước đi qua mô hình này. Vị trí ngang, mô phỏng xe và phép đo vẫn dùng đường thật. Đây là phép thử độ nhạy của đầu vào độ cong.

| Đầu vào S1f ở 90 km/h | Đỉnh a_y của xe, m/s² |
|---|---|
| Bám tâm làn | 1,839 |
| Độ cong thật trong 80 m | 0,938 |
| Độ cong thật với tầm nhìn rút ngắn do trễ | 0,961 |
| Một cubic có trễ, không nhiễu | 1,881 |
| Một cubic có trễ và nhiễu | 1,880 |

Với S1f, đổi sang một cubic làm mất mức giảm đỉnh a_y trong phép thử này. Ảnh hưởng từ việc rút ngắn tầm nhìn do trễ và từ mức nhiễu đã thử nhỏ hơn nhiều. Ở S14e, cả hai bản cubic đánh giá hụt nhu cầu hỗ trợ tại ít nhất một nút của cả 59 cửa sổ có a_y cần thực vượt giới hạn trong 0–1 s. Với bản cubic có nhiễu, R-ay vẫn vượt trần a_y theo đường thật trong 95/401 cửa sổ.

### 5.3. So sánh quintic C và quintic có điểm trung gian

Mốc là generator quintic C hiện tại với T4, T8 và T10. Phương án thử cộng vào path mốc một độ lệch ngang có hai đoạn quintic. Độ lệch và hai đạo hàm bằng 0 ở đầu và cuối horizon. Hai đoạn có cùng vị trí và đạo hàm ngang bậc 1, 2 tại điểm nối. Quét thời điểm giữa 1,0, 1,5 và 2,0 s, với lệch ±0,05, ±0,10, ±0,20 và ±0,30 m. Chỉ xét ca HWA có hai biên đủ tin, ObjectList hợp lệ và trống, đủ tầm nhìn cho cả horizon, đang giữ làn và a_y cần còn cách giới hạn ít nhất nửa epsilon_ay.

Mỗi ứng viên qua T4 và T10 trước khi so điểm. Ứng viên cần ở trong hành lang tính từ bề rộng xe và làn, đạt ngưỡng gia tốc ngang, jerk và độ đổi path theo dữ liệu planner có. Điểm thử là đỉnh trị tuyệt đối a_y cộng 0,2 s nhân jerk RMS. Chọn ứng viên khi điểm giảm ít nhất 0,005 m/s². Bên chấm SIL kiểm riêng chuyển động thật và tính liên tục từ output. Sàn PP-SWR-006 vẫn được chấm trên các cửa sổ áp dụng.

`quintic_experiment.py` build tuần tự hai thư viện từ cùng bản chụp mã nguồn trong thư mục tạm dưới hồ sơ này. Bản thử thêm `quintic_comfort.inc` vào bản sao C. Tám lượt chạy cặp dùng VP-0, camera 80 m, trễ 100 ms, cùng kịch bản và seed trong mỗi cặp. Các ca S1 và S14 dùng harness nghiên cứu cho cảm biến ObjectList chuẩn phát cả khi đường trống. Một ca S1f + F01(a) dùng lịch phát mặc định để kiểm hành vi khi vắng ObjectList. S3a dùng kênh ObjectList của ca gốc. Số liệu và hash thư viện ở `quintic_results.json`.

| Ca S1f có ObjectList | Đỉnh a_y xe, m/s² | Đỉnh jerk xe, m/s³ | Chu kỳ chọn điểm trung gian |
|---|---|---|---|
| Sạch, seed 1 | 1,439 → 1,412 | 1,407 → 1,616 | 136 |
| F01(a), seed 1 | 1,416 → 1,418 | 1,398 → 1,641 | 118 |
| F01(a), seed 2 | 1,447 → 1,443 | 1,390 → 1,649 | 151 |
| F01(c), seed 1 | 1,367 → 1,375 | 1,377 → 1,462 | 102 |

Cả hai bản đạt các tiêu chí đã chấm trên bốn lượt S1f trong bảng. Khoảng hở nhỏ nhất của bản điểm trung gian giảm khoảng 1,3–2,7 cm. Bản có điểm trung gian giảm đỉnh a_y của xe 1,9% ở ca sạch, còn jerk đỉnh tăng 6–19% trên bốn lượt. Hai bản cho cùng số đo khi vắng ObjectList ở S1f + F01(a). Bản thử chọn 0 lần ở S3a và S14e. Hai bản cùng trượt PP-SWR-006, 100 và 101 ở S14e trong cấu hình này.

Quintic C là mốc phù hợp để tiếp tục so sánh SIL. Với lưới điểm trung gian và hàm điểm đã thử, mức giảm đỉnh a_y thiếu ổn định dưới nhiễu và jerk đỉnh tăng trên xe.

## 6. Đề xuất

Tiếp tục kiểm chứng trong nguyên mẫu nghiên cứu:

1. So một cubic với ước lượng độ cong cục bộ theo đoạn, dùng cùng mẫu camera, trễ và nhiễu. Đo sai số trong 0–1 s và mức giảm đỉnh a_y trên S1f.
2. Thử tốc độ thay đổi theo preview trên S14e và S1be. Giữ sàn, trần a_y và hành lang khi đánh giá mức giảm tốc cần thiết.
3. Thử hành lang đổi theo thời gian khi xe ở làn bên tiến tới. Đo thời gian rời phía bị chặn và khoảng hở trong lúc chuyển tiếp theo PP-SWR-055 và 056.
4. Giữ quintic C làm mốc. Nếu thử lại quintic có điểm trung gian, kiểm jerk đỉnh và độ đổi điểm trung gian giữa chu kỳ cùng với chi phí trong horizon.
5. Để xét chọn generator chính thức, so ứng viên với quintic và QP V2 trên cùng dữ liệu và bộ kiểm SIL.

## 7. Quyết định

- Người quyết, ngày:
- Chọn:
- Lý do:
- Đưa vào:
- Hồi quy:

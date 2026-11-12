# Software Qualification Test Specification

| Mục | Nội dung |
|---|---|
| Mã tài liệu | `PP-SQTS` |
| Phiên bản | 1.19 |
| Trạng thái | BL1 |
| Tác giả | thongbui |
| Người review | thongbui |
| Cập nhật | 2026-11-12 |

## 1. Purpose and scope {#test-scope}

- **Mục đích.** Quy định cách kiểm chứng path planner: môi trường giả lập, test case, fault injection, tiêu chí đạt, mức nghiêm trọng, chỉ số, cách chọn calibration, so sánh kỹ thuật và so sánh giữa các planner.
- **Nội dung thêm.** Conformance của planner với contract gọi hàm; kiểm chính bên chấm bằng planner mồi.
- **Phạm vi.** Kiểm thử hộp đen dựa trên Software Requirements Specification: requirement chấm đạt hoặc trượt; performance target đo và xếp hạng; flexibility trên nhiều xe.
- **Ngoài phạm vi.** Unit test của planner; kiểm thử trên xe thật. Không có log xe thật: mọi test chạy trên simulator.

## 2. References {#test-references}

| Tài liệu | Dùng cho |
|---|---|
| [Software Requirements Specification](report.html?doc=path-planner-software-requirements-specification&lang=vi) | Requirement, performance target, ODD; cột Kiểm chứng là nguồn truy vết |
| [Interface Control Document](report.html?doc=path-planner-interface-control-document&lang=vi) | Interface duy nhất mà bên test được quan sát |
| [ADAS Function Specification](report.html?doc=adas-function-specification&lang=vi) | Ngưỡng của khối Chức năng ADAS chạy thử |
| Đề bài G1 | Bộ tối thiểu 3 kịch bản × 5 trạng thái lỗi; các chỉ số so sánh kỹ thuật |
| Euro NCAP LSS Test Protocol v4.3 | Tốc độ thử 72 km/h, trôi bằng cung R = 1200 m, v_lat 0,2–0,6 m/s |
| Bosch SMI230 (bản giới thiệu sản phẩm 2018) | Mức nhiễu và bias IMU |
| ISO 15622:2018 | ACC chạy thử |
| UN R79 Annex 8; UN R171 Annex 4; EU 2021/646 Annex I Part 2; Euro NCAP Assessment Protocol SA v10.4.1 | Bài thử của văn bản (mục 5.1). Bản đã tải: `docs/reference/standards/` |
| Euro NCAP Assessment Protocol SA v10.4.1, mục 4.3.2, 4.3.3.6 | Điểm LSS (mục 9.2) |
| ISO 21448:2022 | Giới hạn của kết luận: còn tình huống nguy hiểm chưa biết (mục 3, 8.4) |
| ISO 26262-8:2018, mục 11 | Độ tin cậy của công cụ phần mềm: kiểm bên chấm (mục 12) |
| Menzel, Bagschik, Maurer, Scenarios for Development, Test and Validation of Automated Vehicles, IEEE IV 2018 (PEGASUS) | Ba tầng kịch bản: chức năng, logic, cụ thể (mục 5.2) |
| ASAM OpenSCENARIO XML 1.x, ASAM OpenDRIVE 1.x | Định dạng kịch bản logic và đường (mục 5.2) |
| Thông số công bố của VinFast VF 3, VF 6, VF 8, VF 9 | Vehicle profiles (mục 4.4) |

## 3. Test principles {#test-principles}

- **Độc lập.** Bên test chỉ quan sát planner qua Interface Control Document (input, output, thời gian tính). Không đọc biến nội bộ, không dựa vào cơ chế hay ngưỡng bên trong planner. Planner không đọc tên kịch bản, ground truth, seed hay cấu hình của test.
- **Định trước.** Kịch bản, seed, tiêu chí và thứ tự xếp hạng chốt trước khi chạy. Đổi thì ghi lý do và chạy lại cho mọi kỹ thuật.
- **Chỉnh và chấm tách riêng.** Chọn calibration trên bộ chỉnh; điểm chính thức trên bộ kiểm (seed khác, một số kịch bản không dùng lúc chỉnh). Mỗi kỹ thuật cùng ngân sách công sức chỉnh.
- **Không đối phó bài thi.** Ca mới chỉ thêm ở phía test. Ca trượt thì sửa cơ chế chung của planner rồi chạy lại cả bộ.
- **Báo cáo đủ và tái lập được.** Báo cáo mọi kịch bản và seed, kể cả ca xấu nhất; mỗi kết quả kèm phiên bản code, file kịch bản, seed.
- **Ưu tiên.** An toàn, rồi quy định, rồi cảm nhận người lái, sau cùng là thời gian tính. Đo trên chuyển động thật của xe so với làn thật.
- **Giới hạn của kết luận.** Benchmark chứng minh được planner bị chặn. Không thấy lỗi chặn chỉ có nghĩa trong phạm vi đã thử, không phải bằng chứng an toàn (ISO 21448).
- **Học qua kết quả.** Planner và bên test học từ nhau qua kết quả, problem report, log và requirement. Không qua phần bên trong của phía kia.

## 4. Test environment {#simulation-design}

### 4.1 Cách chạy {#benchmark-run}

| Mục | Quy định |
|---|---|
| Chế độ chấm điểm | Tất định, một tiến trình, bước 1 ms. Cùng seed thì cùng kết quả. Chỉ số chính thức lấy từ chế độ này |
| Chế độ thời gian thực | Mỗi ECU một tiến trình, socket thật, bus CAN ảo `udp_multicast` của `python-can`. Chỉ để kiểm tích hợp |
| Vòng hở | Xe đi theo quỹ đạo định sẵn, không theo path; đo chất lượng path |
| Vòng kín | Path qua Lateral Controller và EPS chạy thử vào mô hình xe. Khối chạy thử cố định cho mọi kỹ thuật |
| Độ mượt | Luôn tính trên output của planner, kể cả ở vòng kín |
| Khối Chức năng ADAS chạy thử | Chế độ B dùng tín hiệu lý tưởng từ ground truth để chấm planner. Chế độ A dùng message nhận được để so thời điểm kích hoạt. Ca kiểm arbitration và yêu cầu muộn có thể dùng chuỗi FunctionRequests định sẵn. Mục 4.8 |
| Mốc không nhiễu | Mỗi kịch bản có bản không nhiễu để tách lỗi thuật toán khỏi ảnh hưởng của nhiễu |
| IMU | Kịch bản chính dùng IMU sạch (mentor); nhiễu và bias IMU là fault injection |
| Tần số | Planner và khối Chức năng ADAS 40 Hz; tín hiệu xe theo signal list (mentor) |
| Seed | Một seed chính mỗi lần chạy, tách luồng cho từng kênh; 10 seed cho mỗi ô có nhiễu |
| Log | Một file MCAP mỗi lần chạy, đủ để chạy lại; xem bằng Foxglove |
| Máy 8 GB RAM | Chạy từng lô nhỏ |

### 4.2 Bộ lập lịch và đồng hồ {#sim-scheduler}

| Mục | Quy định |
|---|---|
| Kiến trúc | Thành phần chỉ nói chuyện qua interface; hai chế độ dùng chung code, chỉ khác lớp truyền và lớp lập lịch. Python cộng numpy; planner là thư viện C chạy qua adapter SIL (PP-ADR-013) |
| Bước | 1 ms. Thứ tự mỗi bước: tích phân mô hình xe, cảm biến lấy mẫu, giao message đến hạn, chạy khối đến lượt theo ưu tiên cố định |
| Độ lệch pha | Mỗi khối bắt đầu ở một pha ngẫu nhiên theo seed |
| Kênh truyền | Trễ = danh định + jitter đều; có xác suất mất; bên nhận giữ message mới nhất; kiểm counter, CRC, qualifier lúc nhận |
| Fault injection theo kênh | Mất chuỗi, thêm trễ, gửi trùng, đảo thứ tự, ngừng gửi, CRC sai, counter đứng yên |
| Thời gian tính của planner | Mô phỏng là 5 ms; thời gian thật đo riêng |
| Seed | `numpy.random.SeedSequence.spawn` |
| Đồng hồ ECU | Mỗi ECU trôi tới ±100 ppm; lệch ban đầu tới ±10 ms; đồng bộ kiểu gPTP mỗi 125 ms, sai số sau đồng bộ tới ±50 µs |

### 4.3 Bus CAN ảo {#sim-can}

Tín hiệu khung gầm đi qua bus CAN ảo theo DBC ở Interface Control Document: làm tròn theo factor, chu kỳ cố định, counter, CRC, timeout. Dùng `cantools` và bus ảo của `python-can`. Fault injection: mất khung, CRC sai, counter lặp hoặc nhảy, ngừng gửi.

### 4.4 Mô hình xe và vehicle profiles {#sim-vehicle}

| Mục | Quy định |
|---|---|
| Mô hình | Bicycle động lực học, lốp tuyến tính F = C·α; trạng thái x, y, ψ, v_y, r; RK4 bước 1 ms |
| Giới hạn bám | Lực ngang mỗi trục ≤ μ·F_z; μ = 1,0 khô, 0,5 ướt |
| Tốc độ thấp | Chuyển dần sang kinematic trong 3–5 m/s |
| Tốc độ dọc | Từ ACC chạy thử (mục 4.7). Kịch bản có HWA chạy với ACC bật; kịch bản chỉ có LKA, ELK và S11 giữ tốc độ theo kịch bản |
| Nguồn trôi làn | Tài xế giả đặt góc lái để tạo cung trôi rồi thả lực điều khiển. Gió ngang và đường nghiêng gây lực ngang duy trì ở trọng tâm. Mục 4.8 |
| Trạng thái đầu | Xe bắt đầu trong cua thì ở trạng thái ôm cua ổn định theo độ cong tại đó; tài xế giả giữ góc lái tương ứng |

**Vehicle profiles.** Planner nhận profile qua VehicleConfig. VP-0 là profile mặc định của mọi kịch bản; VP-1 đến VP-5 dùng cho S19 và bộ flexibility (mục 8.3).

| Profile | Xe | Chiều dài cơ sở (m) | Bề rộng thân / kể cả gương (m) | Khối lượng (kg) | Bán kính quay vòng (m) | Góc bánh tối đa (rad) |
|---|---|---|---|---|---|---|
| VP-0 | Xe điện cỡ trung, giá trị điển hình | 2,90 | — / 1,90 | 2000 | — | 0,61 |
| VP-1 | VinFast VF 3 | 2,075 | 1,679 / 1,96 | 857 | 4,05 | 0,54 |
| VP-2 | VinFast VF 6 | 2,730 | 1,834 / 2,11 | 1600 | 5,5 | 0,52 |
| VP-3 | VinFast VF 8 (2022) | 2,950 | 1,934 / 2,21 | 2540 | 6,2 | 0,50 |
| VP-4 | VinFast VF 9 | 3,150 | 2,004 / 2,254 | 2932 | 7,33 | 0,44 |
| VP-5 | Tổng hợp: như VP-4, rộng tối đa | 3,150 | — / 2,50 | 2932 | 7,33 | 0,44 |

| Tham số | Cách lấy | Nguồn |
|---|---|---|
| Chiều dài cơ sở, bề rộng thân, khối lượng, bán kính quay vòng | Thông số công bố | VF 3, VF 6, VF 8, VF 9: bonbanh.com và brochure VinFast; VF 9 bề rộng 2,254 m: Vietnam News, 2,004 m: bonbanh (Appendix A) |
| Bề rộng kể cả gương | VF 9: hiểu 2,254 m là có gương, 2,004 m là không. VF 3, VF 6, VF 8: thân + 0,28 m, theo chênh lệch có và không có gương mà Volkswagen công bố cho Golf 8 (1,789 / 2,073 m) | nhóm tự thống nhất |
| Góc bánh tối đa | asin(chiều dài cơ sở / bán kính quay vòng) | nhóm tự thống nhất |
| Phân bố khối lượng | l_f = l_r = chiều dài cơ sở / 2 | nhóm tự thống nhất |
| Độ cứng lốp | C_f = 100 000·m/2000, C_r = 140 000·m/2000 N/rad: giữ hệ số thiếu lái K ≈ 0,0029 rad/(m/s²) cho mọi profile | nhóm tự thống nhất |
| Mô-men quán tính | I_z = 0,83·m·l_f·l_r (xe con thường 0,8–1,1) | nhóm tự thống nhất |
| Tỉ số lái, tốc độ vô lăng tối đa, trễ chấp hành | 15; 6 rad/s; 50 ms cho mọi profile | nhóm tự thống nhất |

Bỏ qua chuyển tải khi vào cua, hệ treo, mặt đường gồ ghề: nhỏ ở mức a_y của HWA và LKA.

### 4.5 Mô hình cảm biến {#sim-sensors}

Mức lỗi do bên test đặt từ datasheet hoặc tài liệu, không lấy từ giả định của planner. Không có nguồn thì quét nhiều mức.

| Kênh | Cách sinh | Mức |
|---|---|---|
| Lane model | Hình học làn trong tầm nhìn, đưa về `base_link`, khớp đa thức bậc 3 cho từng vạch của ba làn và từng mép đường; fault injection theo mục 6. Tầm nhìn danh định 0–80 m, riêng từng vạch; mỗi vạch khớp trên đúng đoạn nó thấy. Điểm đầu, điểm cuối đặt theo kịch bản (điểm cuối 10–126 m, quét ở Q4); lỗi tầm nhìn ở F22. Trễ chụp tới gửi 100 ms | Không lỗi: báo σ_c0 = 0,03 m, σ_c1 = 0,002 (mức F01 a); lỗi theo mục 6 |
| ObjectList | Vật thể của kịch bản đưa về `base_link`, cùng chu kỳ và trễ với lane model; tầm phát hiện 150 m phía trước, 80 m phía sau; `existence_probability` 0,95 với vật thật, 0,6 với vật thể ảo (nhóm tự thống nhất) | x: σ = 0,2 m + 1 % khoảng cách; y: σ = 0,1 m + 0,5 %; vx, vy: σ = 0,3 và 0,2 m/s; kích thước σ = 0,1 m; bỏ sót 2 % frame; vật thể ảo 0,05 lần/s, tồn tại 0,2 s; mưa: σ × 1,5 |
| Yaw rate | Sạch ở kịch bản chính | Fault injection: σ = 0,07 hoặc 0,14 °/s (0,02 °/s/√Hz × √12 hoặc √50 Hz); bias 0,1 / 0,3 / 1 °/s |
| a_x, a_y | Sạch ở kịch bản chính; trên đường nghiêng vẫn chứa g·sin(góc nghiêng) | Fault injection: σ = 0,004 hoặc 0,008 m/s²; bias tới 0,2 m/s² |
| Tốc độ | Từ mô hình xe, trước khi mã hoá CAN | σ = 0,02 m/s; sai tỉ lệ ±0,5 % |
| Góc vô lăng | Như trên | σ = 0,001 rad; lệch điểm 0 ±0,01 rad |
| VehicleStateEstimate | v_y thật cộng nhiễu | σ = 0,05 m/s |
| Ego-motion | Tích phân tốc độ và yaw rate từ chính tín hiệu CAN, cộng v_y của VehicleStateEstimate để có cả trượt ngang (Interface Control Document 5.5), nên sai số tự sinh khi bơm lỗi IMU hoặc v_y | — |

Traffic đi theo chiều tăng hoặc giảm `s`. Xe ngược chiều có `vx` âm khi hai xe cùng phương. Dịch ngang nếu có dùng quintic theo thời gian, với v_lat và gia tốc ngang của phần dịch bằng 0 tại hai đầu. Xe mục tiêu S7 và S8 giữ offset ngang theo Euro NCAP LSS 7.2.4.3 và 7.2.4.4. ObjectList giữ 32 ô, `num_objects` đếm số ô có dữ liệu.

Đường có vạch đứt, liền, kép và mép đường cố định. LaneModel biểu diễn mép gần xe của vạch và mặt gần xe của rào chắn. Vạch kép giữ `crossable` theo nét phía xe. Biên vắng mặt báo LOST.

Nguồn: nhiễu và bias IMU theo Bosch SMI230 (cảm biến thô, nên là chặn trên của tín hiệu đã lọc). Nhiễu tốc độ, góc lái, perception, v_y: nhóm tự thống nhất. Trễ camera 100 ms: danh định, dưới mức xấu nhất 120 ms của PP-ASM-001; mức khác quét ở Q1. Tầm nhìn 0–80 m: nhóm tự thống nhất, chờ số đo của camera thật (PP-ASM-020); điểm đầu 0 m là giả định lạc quan, vì nắp capo che phần đường gần xe.

### 4.6 Lateral Controller và EPS chạy thử {#sim-controller}

Công cụ vòng kín, cố định cho mọi phiên bản planner.

| Phần | Quy định |
|---|---|
| Controller | 100 Hz. Đọc điểm path theo `stamp_us + time_from_start`, đưa về `base_link` hiện tại. δ = L·κ + K·v²·κ + k_y·e_y + k_ψ·e_ψ; k_y, k_ψ chỉnh một lần rồi giữ cố định |
| Thời điểm đọc path | κ tại thời điểm hiện tại cộng `actuator_delay` (PP-ADR-010); e_y, e_ψ tại điểm nhìn trước 0,5 s |
| Sai số hướng | e_ψ so `pose.yaw` của path với hướng chuyển động của xe tại `base_link`: hướng thân cộng atan(v_y / v), vì `pose.yaw` là hướng tiếp tuyến (Interface Control Document 6.1) |
| Hệ số thiếu lái K | Lấy từ mô hình xe của simulator (mục 4.4), không qua VehicleConfig |
| Path không hợp lệ hoặc quá 75 ms | Giữ lệnh cuối và báo ngừng điều khiển; EPS trả quyền lái trong 1 s |
| EPS | Bám góc vô lăng yêu cầu: trễ thuần theo `actuator_delay`, khâu bậc một τ = 0,1 s, giới hạn tốc độ và góc theo VehicleConfig; không điều khiển thì chuyển dần trong 1 s sang góc của tài xế giả. Lúc bắt đầu, tài xế giả đang giữ góc lái, không có chuyển giao |

EPS giả lập nhận góc để đơn giản; EPS trên xe L2 thật thường nhận mô-men. Giá trị là điển hình, không phải số đo của một EPS cụ thể.

### 4.7 ACC chạy thử {#sim-acc}

Khối dọc trong simulator, thuộc bên test và cố định cho mọi phiên bản planner (PP-ADR-001). Interface với planner ở [Interface Control Document](report.html?doc=path-planner-interface-control-document&lang=vi#longitudinal-plan).

| Phần | Cách làm | Nguồn |
|---|---|---|
| Chế độ | OFF, CRUISE, FOLLOW, CURVE_LIMIT. Chuyển tự động theo lệnh nhỏ nhất | ISO 15622:2018 6.1 |
| Lệnh gia tốc | Nhỏ nhất trong ba: theo tốc độ đặt, theo xe trước, theo đường bao tốc độ của cua; sau đó giới hạn gia tốc và jerk | ISO 15622:2018 6.1 |
| Chọn xe mục tiêu | Hành lang rộng bằng bề rộng xe cộng 0,2 m mỗi bên, đi theo Trajectory trong 3 s, nối tiếp bằng tâm lane model. Chọn xe có thân trong hành lang lúc này hoặc sau 1 s; chỉ vật thể cùng chiều đã từng chạy từ 1 m/s. Bỏ xe đã chọn khi ra ngoài hành lang nới thêm 0,3 m mỗi bên quá 1 s | nhóm tự thống nhất |
| Vật thể đứng yên | Không phản ứng với vật chưa từng chạy | ISO 15622:2018 6.2.2 |
| Bám xe trước | c_des = 5 m + τ·v, τ = 1,8 s. a = 0,5·(c − c_des) + 1,0·(v_trước − v), phần do sai số khoảng cách giới hạn ±1,0 m/s² | τ: ISO 15622:2018 6.2.3.1 (1,5–2,2 s); còn lại: nhóm tự thống nhất |
| Tốc độ trong cua | v_t = v_max·√(1 − 0,3 / 2,5), để lại 0,3 m/s² a_y cho HWA sửa lệch. v_cho_phép = √(v_t² + 2·2,0·max(0, d − 0,5·v)), d là khoảng cách tới chỗ cong nhất; v_max đổi không quá 5 % thì d đếm lùi theo quãng xe đã đi | nhóm tự thống nhất |
| Luật bám | Theo tốc độ đặt: a = 0,4·(v_đặt − v). Theo đường bao: a = dv_cho_phép/dt + 1,0·(v_cho_phép − v) | nhóm tự thống nhất |
| `lateral_limit_reached` | Không tăng tốc khi cờ bật | nhóm tự thống nhất |
| Giới hạn | Gia tốc −3,0 tới +1,5 m/s²; jerk ≤ 2,5 m/s³; không có AEB | nhóm tự thống nhất |
| LongitudinalPlan | Chạy luật trên tới 3 s, lấy v(t), a(t) trên lưới 0,1 s | nhóm tự thống nhất |
| Mất LateralLimits (quá 75 ms, như PathStatus); ACC tắt | Không tăng tốc; ACC tắt thì gửi OFF, tốc độ hiện tại, gia tốc 0 | nhóm tự thống nhất |
| Chấp hành | Lệnh gia tốc qua trễ 0,1 s và khâu bậc một τ = 0,3 s | nhóm tự thống nhất |

### 4.8 Tài xế và Chức năng ADAS chạy thử {#sim-adas-function}

| Phần | Quy định | Nguồn |
|---|---|---|
| Điều kiện tầm nhìn của HWA | Khi kịch bản bật (F22), HWA theo kịch bản rời REQUEST sang UNAVAILABLE nếu thời gian nhìn trước của L1, R1 dưới `t_view_hwa` liên tục quá `t_view_hold`; tự trở lại khi đủ. Tốc độ đọc từ tín hiệu tốc độ | ADAS Function Specification mục 7, 13 (giá trị khởi đầu) |
| Stand-in LKA, ELK | Tính DLC, TLC, ý định và nguy cơ từ tín hiệu được cấp. Phát FunctionRequests ở 40 Hz. Nhận kết quả can thiệp qua PathStatus | ADAS Function Specification mục 5–9, 12, PP-ADR-014, PP-TS-008 |
| Chế độ A | Đọc message cảm biến sau trễ và fault injection. Bù chuyển động từ lúc đo bằng EgoMotionQuery. Dùng để so thời điểm kích hoạt | Mục 4.1, 4.5 |
| Chế độ B | Dùng cùng nhịp lấy mẫu làn và vật thể 20 Hz. Hình học và động học lấy từ simulator, không bơm sai số cho tín hiệu của stand-in. Bù chuyển động theo pose thật. Chấm planner từ FunctionRequests thực nhận, các output ICD và ground truth | Mục 4.1, 4.5 |
| Log | Lưu TLC của A và B trên cùng trạng thái xe. Lưu FunctionRequests thực nhận và thời điểm nhận tại mỗi tick planner | Mục 8.2, Interface Control Document mục 4 |
| Góc lái khi tạo drift | Đặt độ cong cung trôi cộng độ cong đường. Khi thả, trả mục tiêu góc lái về mức bám độ cong đường và để bicycle tích phân chuyển động | Euro NCAP LSS 7.2.2, EU 2021/646 Annex I Part 2, 5.3.3.1.2 |
| Khởi tạo trong cua | Độ cong danh định tính trên đường offset. Hướng chuyển động của cầu sau ban đầu theo tiếp tuyến đường offset, có bù góc trượt của bicycle | Mô hình tại mục 4.4, PP-PR-015 |
| Bắt đầu đánh lái | Bài Euro NCAP có đoạn thẳng 2 s từ T0 tới Tsteer | Euro NCAP LSS 4.2.1 |
| Thả lực điều khiển | Tại Tsteer + R·asin(v_lat/v)/v. Với các neo có cung tạo trôi, thời điểm từ 2,576 đến 3,800 s. Báo v_lat thật tại lúc bắt đầu can thiệp để kiểm dung sai ±0,05 m/s của bài chuẩn | Euro NCAP LSS 7.2.2.1–7.2.2.4, 7.2.3, 7.4.3, EU 2021/646 Annex I Part 2, 5.3.3.1.2–5.3.3.1.3 |
| Xi-nhan S8(c, d) | Bật tại 1,0 s, tức 1,0 s trước Tsteer. Giữ đến cuối ca | Euro NCAP LSS 7.2.4.4.5 cho lúc bật. Lúc tắt do nhóm tự thống nhất |
| Tay và mô-men | Lấy mẫu 50 Hz. Trong cung tạo trôi, dùng 1,0 N·m theo hướng đánh lái. Sau cung, mô-men bằng 0. Tay giữ thụ động cho Euro NCAP, thả tay cho lưới EU | ADAS Function Specification mục 8, 12. Euro NCAP LSS 7.2.2.4. EU 2021/646 Annex I Part 2, 5.3.3.1.2 |
| Gió ngang S4(d) | 300 N hằng tại trọng tâm hướng sang phải từ 2,0 s đến hết ca 20 s, tương ứng 0,15 m/s² ban đầu ở VP-0 | nhóm tự thống nhất, mô hình tại mục 4.4 |
| Nghiêng ngang S4(e) | Dốc ngang 2 % xuống trái từ 2,0 s đến hết ca 20 s, tương ứng khoảng 1,15° | nhóm tự thống nhất, mô hình tại mục 4.4 |
| Rào chắn S6(d) | Rộng 0,2 m, cao 0,8 m, dọc đường. Mặt gần xe trùng biên phải của làn | nhóm tự thống nhất |
| Xe mục tiêu S7, S8 | Rộng 1,9 m, dài 4,8 m. Tâm xe cách mép trong vạch 1,5 m. Đồng bộ theo quỹ đạo danh định chưa can thiệp, 10 % chồng lấn đầu xe ở S7, đầu xe mục tiêu ngang cầu sau xe thử ở S8 | Kích thước do nhóm tự thống nhất. Euro NCAP LSS 7.2.4.3–7.2.4.4 cho đồng bộ |
| S8 late | Giữ xe trôi và phát ELK REQUEST từ thời điểm quỹ đạo danh định đưa lốp qua vạch 0,45 m. Xác nhận DLC thật ở thời điểm nhận theo mục 8.1 | 0,3 m theo PP-SWR-089. Dự phòng sai số mô hình 0,15 m do nhóm tự thống nhất |
| v_lat ở neo bổ sung | S4b(b–e) dùng 0,3 m/s như S4b(a). S5(e), S6(c, d), S7(d, e) dùng 0,4 m/s | nhóm tự thống nhất trong dải Euro NCAP LSS 7.2.4–7.2.5 |
| Chiều dài và thời gian ca | Bắt đầu ở s = 100 m trên đường dài 1.200 m. Các neo tạo trôi bằng cung chạy 17 s, riêng S8 late chạy 10 s | nhóm tự thống nhất |
| Trôi lặp S4(d, e) | Lực ngang tiếp tục sau COMPLETED. Can thiệp mới hợp lệ khi thỏa điều kiện tái kích hoạt. Chấm từng lần can thiệp | ADAS Function Specification mục 9, PP-SWR-035 |

## 5. Test cases {#benchmark-scenarios}

**Bộ tối thiểu của đề bài.** HWA bám cua (S1), LKA trôi làn (S4), ELK xe ngược chiều (S7), mỗi kịch bản với 5 trạng thái: không lỗi, nhiễu (F01), c0 jump (F02), mất một vạch (F04), c2 sai (F06).

- Tốc độ thử theo Euro NCAP LSS: 72 km/h, trôi bằng cung R = 1200 m rồi giữ v_lat; thêm 90 km/h.
- Biến thể trong bảng là bộ cụ thể neo: mọi điểm thử của văn bản ở mục 5.1, cộng ít nhất một biến thể ở ranh giới của requirement. Các bộ cụ thể khác sinh tự động từ dải tham số (mục 5.2). Kịch bản có hai phía chạy cả hai phía.
- Mặc định: làn 3,5 m, profile VP-0. Clothoid vào cua dài 100 m, trừ khi biến thể ghi khác.
- Cột Yêu cầu sinh bằng `python3 tools/trace.py --write` từ cột Kiểm chứng của Software Requirements Specification; không sửa tay. Mã cố định: không đánh số lại, không dùng lại.

| # | Kịch bản | Biến thể | Yêu cầu |
|---|---|---|---|
| S1 | HWA bám cua | 90 km/h, vào cua bằng clothoid. a) R = 1000 m (a_y cua 0,6 m/s²); b) R = 500 m (1,25); c) R = 250 m (2,5, chạm aysmax); d) cua chữ S, R = 500 m; e) 130 km/h, R = 1000 m (1,3); f) cua chữ S của R171 Annex 4, 4.2.4.1 (R = 787 m rồi 374 m); g) R = 300 m (2,08 m/s², 83 % aysmax) | PP-SWR-001, 003, 004, 008 (a, b, d, e), 050 (a, b, d, e), 051 (vòng kín) |
| S1b | HWA cua gắt hơn aysmax | a) 90 km/h, R = 200 m (3,1 m/s²); b) 90 km/h, R = 150 m (4,2); c) 110 km/h, R = 300 m (3,1); d) R = 200 m ngay sau đỉnh dốc, camera thấy 40 m suốt ca (đường phẳng, chỉ mô phỏng tầm nhìn); e) như a, clothoid 60 m; f) 90 km/h, R = 230 m (2,72 m/s², trong dải aysmax + 0,1 tới + 0,4) | PP-SWR-001, 005, 006, 007 (vòng kín), 064 |
| S2 | HWA bật khi xe lệch tâm | 90 km/h; độ lệch và góc tính tại lúc HWA bắt đầu lái. a) lệch 0,2 m, góc 0°; b) 0,4 m, 1° hướng vào tâm; c) 0,5 m, 2° hướng ra ngoài; d) 0,4 m phía ngoài cua R = 500 m; e) 0,5 m ở 130 km/h | PP-SWR-002, 052, 053 |
| S3 | HWA dời tâm khi vượt xe tải ở làn bên | Xe tải rộng 2,5 m. a) chậm hơn 5 m/s; b) chậm hơn 2 m/s; c) chậm hơn 10 m/s; d) xe tải cách vạch 0,1 m; e) xe tải lấn vạch 0,3 m | PP-SWR-002, 055, 056, 057, 058, 059 |
| S3b | Xe lớn vượt mình từ phía sau, làn hẹp | Xe tải nhanh hơn 5 m/s, chỉ radar góc thấy trước khi ngang hàng. a) bên kia trống, làn 3,5 m; b) bên kia có xe con; c) bên kia có xe tải; d) như a, làn 3,0 m; e) như c, làn 2,75 m | PP-SWR-056, 057 |
| S4 | LKA trôi làn đường thẳng | a) 72 km/h, vạch đứt, v_lat 0,2 m/s; b) 72 km/h, vạch liền, 0,4; c) 90 km/h, 0,6; d) trôi do gió ngang; e) trôi do đường nghiêng | PP-SWR-032, 080, 081, 083, 084 (vòng kín), 085 (vòng kín), 086 (vòng kín), 087 (vòng kín), 090, 110, 112, 114 |
| S4b | LKA trôi làn trong cua | 90 km/h. a) R = 1000 m, ra ngoài 0,3 m/s; b) R = 500 m, ra ngoài; c) R = 500 m, vào trong; d) R = 250 m, ra ngoài, chỉ còn 0,5 m/s² trong giới hạn LKA; e) ra ngoài ngay đoạn clothoid | PP-SWR-083, 085 (vòng kín), 110, 112, 114 |
| S5 | ELK vạch liền, LKA tắt | a) 72 km/h, v_lat 0,2; b) 0,4; c) 0,6; d) 90 km/h, 0,4; e) vạch kép; f) 72 km/h, 0,5 | PP-SWR-032, 080, 082, 083, 085 (vòng kín), 086 (vòng kín), 090, 111, 113, 115 |
| S6 | ELK mép đường | Phía hành khách. a) chỉ mép đường, v_lat 0,2; b) chỉ mép đường, 0,6; c) vạch giữa đứt, không có vạch sát mép; d) mép đường là rào chắn; e) 90 km/h, 0,4 | PP-SWR-080, 082, 083, 085 (vòng kín), 086 (vòng kín), 111, 113, 115 |
| S6b | Làn mở rộng | HWA bật. a) làn khẩn cấp rộng dần 1,5 m trên 100 m, phía phải; b) tách nhánh lối ra; c) thêm làn bên trái; d) mở rộng trong cua R = 500 m; e) mở rộng lúc đang dời tâm vì xe tải bên kia | PP-SWR-050, 060 (vòng kín) |
| S7 | ELK xe ngược chiều | Xe kia cách mép trong vạch giữa 1,5 m, 10 % chồng lấn nếu không can thiệp. a) cả hai 72 km/h, v_lat 0,2; b) 0,4; c) 0,6; d) xe kia 90 km/h; e) trong cua R = 500 m | PP-SWR-082, 083, 085 (vòng kín), 088 (vòng kín), 111, 113, 115 |
| S8 | ELK xe đang vượt | a) xe kia 80 km/h, mình 72 km/h, trôi 0,2 m/s; b) cùng 72 km/h, trôi 0,4; c) xi-nhan 1,0 ± 0,5 s trước lúc đánh lái, 0,5 m/s; d) như c, 0,7 m/s; e) xe kia 100 km/h, trôi 0,4. Ca bổ sung late bơm ELK REQUEST sau khi lốp trước đã qua vạch | PP-SWR-082, 083, 085 (vòng kín), 088 (vòng kín), 089, 111, 113, 115 |
| S8b | Chuyển làn có xi-nhan, xe sau ở nhiều khoảng cách | a) cách 20 m, nhanh hơn 2,2 m/s; b) 10 m, 2,2 m/s; c) 20 m, 8 m/s; d) 12 m, 10 m/s (TTC 1,2 s); e) 30 m, 14 m/s (cần 3,3 m/s²). a–c: không can thiệp; d, e: can thiệp theo ADAS Function Specification mục 6, bước 5 | PP-SWR-082 (d, e), 083 (d, e), 085 (d, e, vòng kín), 111 (d, e), 113 (d, e), 115 (d, e) |
| S8c | Bẻ lái gấp tránh vật, làn bên có xe | Không xi-nhan. a) v_lat 1,2 m/s; b) 1,5 m/s; c) bẻ rồi trả ngay; d) bẻ khi LKA đang can thiệp | PP-SWR-031 (d), 036 (d), 037 (d) |
| S9 | Chuyển giữa chức năng | a) LKA lên ELK; b) ELK xong về HWA; c) HWA bị ghi đè rồi buông; d) yêu cầu bị hủy vì xi-nhan; e) tài xế tắt HWA giữa cua R = 500 m | PP-SWR-030 (a), 031, 033 (b), 036 (d), 037 (d), 038, 039 (c), 040 (c), 042 (e) |
| S10 | Đi gần vạch mà không trôi | a) DLC 0,2 m, v_lat gần 0; b) DLC 0,4 m; c) cắt cua R = 500 m; d) đi lệch một bên khi có xe tải; e) như a, ban đêm, chế độ A |   |
| S11 | Tắc đường trên cao tốc | HWA bật. a) 0–30 km/h; b) 0–60 km/h; c) dừng 10 s rồi chạy; d) xe khác cắt vào ở 20 km/h | PP-SWR-050, 054 |
| S12 | Trời mưa | μ = 0,5, nhiễu camera ban đêm, nhiễu perception × 1,5. a) S1c; b) S4c; c) S7c; d) S4b-d | PP-SWR-001 (a) |
| S13 | EPS chậm | S4c và S5c với trễ EPS a) 75 ms; b) 100 ms; c) 150 ms | PP-SWR-091 (a, b, vòng kín) |
| S14 | Ngang và dọc trao đổi ràng buộc | Chạy hai lần: ACC đọc và bỏ qua LateralLimits. a) S1b-a; b) xe khác lấn 0,5 m; c) cả hai; d) mất LongitudinalPlan giữa cua; e) cua chữ S của S1f ở 130 km/h (khúc R = 374 m cần 3,5 m/s²) | PP-SWR-009, 150, 151, 152, 153, 154 (d), 155 (d) |
| S15 | Dời tâm khi hai bên có vật | a) xe tải hai bên; b) xe tải và rào chắn; c) xe tải và xe con; d) xe tải hai bên, làn 3,0 m; e) rào chắn hai bên | PP-SWR-056, 057 |
| S16 | Can thiệp lặp | a) LKA COMPLETED, REQUEST giữ thêm 1 s; b) như a, REQUEST rời 0,2 s rồi quay lại; c) trôi ba lần, 0,4 m/s, cách 2 s; d) như c, ELK vạch liền; e) lần hai bắt đầu 0,2 s sau COMPLETED | PP-SWR-034 (a, b), 035 (c, d, e), 041 (a, b) |
| S17 | Tài xế chuyển làn khi HWA bật | Lane model đổi làn khi xe qua vạch. a) đường thẳng 90 km/h, 4 s; b) 2,5 s; c) cua R = 500 m; d) hai lần liên tiếp; e) cờ chuyển làn trễ một frame | PP-SWR-039, 040, 061 |
| S19 | Bề rộng làn và bề rộng xe | HWA, 90 km/h, đường thẳng rồi cua R = 500 m. a) làn 2,5 m, VP-1; b) làn 2,5 m, VP-5; c) làn 5,5 m, VP-2; d) làn 3,0 m, VP-4, xe tải 2,5 m ở làn bên chậm hơn 5 m/s; e) như d, xe tải hai bên | PP-SWR-050, 062, 063 (b) |

### 5.1 Bài thử theo văn bản {#benchmark-regulatory}

Mỗi bài thử của văn bản ứng với kịch bản nào. Bài thử của khối khác (Lateral Controller, EPS, khối Chức năng ADAS) ghi "Không".

| Văn bản, mục | Bài thử | Điểm thử của văn bản | Tiêu chí đạt | Kịch bản | Ghi chú |
|---|---|---|---|---|---|
| R79 Annex 8, 3.2.1; R171 Annex 4, 4.2.5.1.1.1.1 | Giữ làn trong cua | Không tay, tốc độ không đổi; cua cần 80–90 % aysmax | Lốp trước không vượt mép ngoài vạch; jerk ≤ 5 m/s³ | S1 (g) | aysmax như nhau trên 10–130 km/h nên thử một dải |
| R79 Annex 8, 3.2.2; R171 Annex 4, 4.2.5.1.1.1.2 | a_y lớn nhất | Cua cần > aysmax + 0,3 m/s²; tắt giảm tốc trong cua | a_y trong giới hạn của R79 5.6.2.1.1; jerk ≤ 5 m/s³ | S1b (a, b, c), ACC bỏ qua LateralLimits | |
| R79 Annex 8, 3.2.5 | Cảnh báo vượt vạch | Cua cần aysmax + 0,1 tới + 0,4 m/s² | Cảnh báo muộn nhất khi lốp trước vượt vạch; vẫn hỗ trợ | S1b (f) | Cảnh báo dựa trên `lateral_limit_reached` |
| R79 Annex 8, 3.1, 3.2.3, 3.2.4 | Cảnh báo của CSF; lực ghi đè; tay rời vô lăng | — | — | Không | Khối Chức năng ADAS, Lateral Controller, EPS |
| R79 Annex 8, 3.3.1, 3.3.2 | ESF với xe làn bên | Xe làn bên áp sát; chuyển làn chủ ý | Không rời làn gốc; cảnh báo không muộn hơn lúc can thiệp | S7, S8 | Cảnh báo thuộc khối Chức năng ADAS |
| R79 Annex 8, 3.3.3 đến 3.3.5 | ESF với vật trên đường; không có vạch; phản ứng sai | — | — | Không | Ngoài chức năng ELK và ngoài ODD của dự án |
| R171 Annex 4, 4.2.4.1, 4.2.5.1.1.2 | Vị trí trong làn, thử mở rộng | Cua chữ S chuẩn; nhiều độ cong và tốc độ, ít nhất một ca vượt a_y khai báo; vạch, mép đường, một vạch | Không rời làn, chuyển động ổn định | S1 (f), S14 (e), F04, F21 | R171 đạt khi ≥ 90 % bài thử đúng (Annex 3 Appendix 4); dự án đòi mọi bài |
| R171 5.3.7.1.1.1, 5.3.7.1.3 | Chỉnh tốc độ theo độ cong | — | Có chiến lược, mô tả được | S14 | Software Architectural Design mục 6.2 |
| EU 2021/646 Annex I Part 2, 5.3.3; 3.6.2 | ELK lane keep | Vạch liền, trái và phải; 72 ± 1 km/h; cung R ≥ 1200 m rồi thả tay; v_lat 0,2 và 0,5 ± 0,05 m/s | DTLM không vượt −0,3 m | S5 (a, f) | Dải của 3.6.2: v_lat 0,2–0,5 m/s tới 100 km/h, 0,2–0,3 m/s trên 100 km/h |
| EU 2021/646 Annex I Part 2, 5.3.2 | Ghi đè ELK | Tài xế ghi đè giữa lúc can thiệp | Không mất hỗ trợ lái đột ngột sau ghi đè | S9 (c) | Lực ≤ 50 N thuộc EPS |
| EU 2021/646 Annex I Part 2, 4.3; Euro NCAP LSS 7.2.6 | LDW | — | — | Không | Cảnh báo, thuộc khối Chức năng ADAS |
| Euro NCAP LSS 7.2.3, 7.2.5; SA 4.3.2 | LKA vạch đứt, vạch liền | 72 km/h; cung R = 1200 m; v_lat 0,2–0,6 m/s bước 0,1; hai phía | DTLE ≥ −0,3 m | S4 | |
| Euro NCAP LSS 7.2.4.1, 7.2.4.2; SA 4.3.3 | ELK mép đường, vạch liền | Mép đường phía hành khách: chỉ mép đường, hoặc vạch giữa đứt và không có vạch sát mép. Vạch liền: hai phía. v_lat 0,2–0,6 m/s bước 0,1 | DTLE ≥ −0,1 m (mép đường), ≥ −0,3 m (vạch) | S5, S6 | |
| Euro NCAP LSS 7.2.4.3; SA 4.3.3.4 | ELK xe ngược chiều | Xe kia cách mép trong vạch giữa 1,5 m, chồng 10 % nếu không can thiệp; phía tài xế; v_lat 0,2–0,6 m/s | Không va chạm | S7 | |
| Euro NCAP LSS 7.2.4.4; SA 4.3.3.4 | ELK xe đang vượt | Cùng 72 km/h, và 80 so với 72 km/h; không chủ ý v_lat 0,2–0,6 m/s; chủ ý có xi-nhan 1,0 ± 0,5 s, v_lat 0,5–0,7 m/s, cung R = 800 m | Không va chạm | S8 | |
| R79 Annex 8, 2.4 | Cách đo a_y và jerk | Tại trọng tâm, lấy mẫu ≥ 100 Hz, lọc Butterworth bậc 4 cắt 0,5 Hz, jerk trung bình trượt 0,5 s của đạo hàm | — | HWA, LKA, ELK vòng kín | Chấm trên Trajectory. Giá trị xe thật là thông tin (mục 8.2) |

Lưới chuẩn ghi từng hàng trong `*.protocol.xosc`, chạy ở regression và full. Euro NCAP lấy cả hai phía cho vạch, phía hành khách cho mép đường và phía tài xế cho xe mục tiêu. Lưới Euro NCAP chọn bề rộng giữa biên trong 3,7 m theo mục 6.1.3.1 để áp dụng cùng hình học cho các profile. Lưới EU dùng hai phía và v_lat 0,2, 0,5 m/s. Các neo và lấy mẫu độ phủ dùng các phân phối riêng.

### 5.2 Kịch bản chức năng, logic, cụ thể {#benchmark-scenario-levels}

Theo ba tầng của PEGASUS, cũng là khung của ISO 34502.

| Tầng | Là gì | Ở đâu |
|---|---|---|
| Chức năng | Mô tả bằng lời: đường, xe mình, xe khác, lỗi, tiêu chí đạt | Bảng ở mục 5 |
| Logic | Dải giá trị của từng tham số | `benchmark/scenarios/`: kịch bản ASAM OpenSCENARIO XML (`.xosc`) có `ParameterDeclarations`; file dải tham số (`ParameterValueDistribution`, khai bằng `DistributionRange` hoặc `DistributionSet`); đường ASAM OpenDRIVE (`.xodr`) |
| Cụ thể | Một giá trị cho mọi tham số | Sinh từ tầng logic. Biến thể a, b, c… ở mục 5 là bộ cụ thể neo, mã cố định |

| Nhóm | Tham số chung | Dải |
|---|---|---|
| Đường | Bề rộng làn; loại biên mỗi bên | 2,5–5,5 m (Software Requirements Specification mục 5); vạch đứt, liền, kép, mép đường |
| Xe mình | Tốc độ; vehicle profile | Dải của chức năng (ADAS Function Specification mục 7); VP-0 đến VP-5 |
| Cảm biến, thời gian | Nhiễu lane model; trễ camera | F01; Q1 |
| Khối dọc | Chế độ ACC | Đọc hoặc bỏ qua LateralLimits |

Tham số riêng (bán kính, v_lat, xe khác…) và dải của chúng khai trong file của từng kịch bản, lấy từ cột điểm thử của mục 5.1 khi văn bản cho dải.

**Chọn bộ cụ thể.**

1. Neo: mọi biến thể ở mục 5.
2. Biên: từng tham số ở giá trị nhỏ nhất và lớn nhất của dải, các tham số khác ở giá trị danh định.
3. Ghép đôi: mọi cặp giá trị nhỏ nhất, danh định, lớn nhất của hai tham số bất kỳ (pairwise).
4. Ngẫu nhiên: Latin hypercube trong dải, seed cố định.

| Bộ chạy | Gồm | Dùng khi |
|---|---|---|
| Smoke | Neo; VP-0; một seed | Mỗi lần sửa code |
| Hồi quy | Neo và biên; mọi profile; hai seed | Mỗi thay đổi lớn của planner, trước khi chốt một trade study |
| Đầy đủ | Bốn cách chọn; mọi profile; mười seed cho ô có nhiễu (mục 4.1) | Trước mỗi baseline |

Ba bộ chạy này là độ sâu. Mục 5.3 là khía cạnh. Mỗi khía cạnh chạy được ở cả ba độ sâu.

### 5.3 Bộ chạy theo khía cạnh {#benchmark-aspects}

Mỗi bộ cụ thể mang hai nhãn: độ khó và kết quả mong đợi. Bên test gán nhãn, suy từ Software Requirements Specification và ADAS Function Specification. Bộ theo khía cạnh lọc theo nhãn, không theo danh sách viết tay.

**Độ khó.** Ca thuộc nhiều mức thì lấy mức cao nhất.

| Mức | Điều kiện của ca | Ví dụ |
|---|---|---|
| L0 | Trong ODD, xa biên của dải; không lỗi; a_y cần không vượt aysmax | S1 (a), S4 (a) |
| L1 | Ít nhất một tham số ở biên dải của ODD hoặc của chức năng: bề rộng làn, tốc độ, bề rộng xe, thời gian nhìn trước | S19 (a) |
| L2 | Trong ODD nhưng cần vượt giới hạn quyền lái của chức năng | S1b, S14 |
| L3 | Một lỗi ở mục 6 | F01 đến F22, Q1 đến Q4 |
| L4 | Ghép lỗi theo mục 6.2 | Ca đêm mưa |
| L5 | Ngoài ODD hoặc ngoài dải hoạt động của chức năng | Q4 ở mức thời gian nhìn trước dưới `t_view_hwa` |

**Kết quả mong đợi.** Ghi trong kịch bản bằng mã ở cột 2.

| Kết quả | Mã | Quan sát được ở output |
|---|---|---|
| Lái | `drive` | Path hợp lệ của chức năng được chọn theo PP-SWR-030 ở mọi chu kỳ, trừ khoảng mà requirement cho phép khác |
| Lái có giới hạn | `drive_limited` | Như Lái; thêm cờ theo requirement: `lateral_limit_reached` (PP-SWR-007), `lane_too_narrow` (PP-SWR-063) |
| Từ chối | `refuse` | Không bắt đầu chức năng (PP-SWR-047, 089, 146), hoặc `path_valid = false` và `active_function = NONE` trong thời hạn của requirement (PP-SWR-124, 142 đến 145) |

Chấm cả hai chiều:

- **Từ chối thiếu.** Ca Từ chối mà planner vẫn lái: trượt requirement của ca.
- **Từ chối thừa.** Ca Lái hoặc Lái có giới hạn mà `active_function` khác chức năng được chọn theo PP-SWR-030, trong khi không có điều kiện nào của PP-SWR-124, 142 đến 145: trượt PP-SWR-030.

**Khía cạnh.**

| Bộ | Câu hỏi | Gồm |
|---|---|---|
| B0 Conformance | Planner có đúng contract gọi hàm không | Mục 11; không dùng kịch bản. Chạy trước mọi bộ khác |
| B1 Nominal | Lái đúng trong điều kiện bình thường không | L0 |
| B2 Regulatory | Có qua bài thử của văn bản không | Lưới chuẩn ở mục 5.1 |
| B3 Performance limit | Ở biên ODD và khi vượt giới hạn quyền lái có làm đúng không | L1, L2 |
| B4 Robustness | Khi có lỗi cảm biến, thời gian, toàn vẹn có làm đúng không | L3, L4 |
| B5 Degradation and refusal | Có từ chối, suy giảm đúng lúc, và không từ chối thừa không | Ca Lái có giới hạn, ca Từ chối, L5; S10 |
| B6 Comfort | Path có êm không | Performance target về cảm nhận người lái (mục 8.2) trên ca của B1 |
| B7 Flexibility | Cùng bản build và calibration có chạy được trên mọi xe không | Mục 8.3 |
| B8 Compute | Thời gian tính | PP-SWR-016 trên mọi ca |

## 6. Fault injection {#benchmark-faults}

Mỗi lỗi bơm ở ba thời điểm: HWA đang chạy ổn định, ngay lúc LKA hoặc ELK kích hoạt, giữa lúc can thiệp. Lỗi theo thời điểm chụp của frame; lane model không gửi cờ (PP-ASM-009). Cột Yêu cầu sinh tự động như ở mục 5.

| Mã | Nhóm | Lỗi | Mức hoặc dạng | Yêu cầu |
|---|---|---|---|---|
| F01 | Lane model | Nhiễu c0, c1 | a) ban ngày σ_c0 = 0,03 m, σ_c1 = 0,002; b) × 1,5; c) ban đêm hoặc mưa × 2,5 | PP-SWR-120 |
| F02 | Lane model | c0 jump, không có cờ | Cả lane model nhảy trong một frame. a) 0,3 m; b) 0,6 m; c) 1,0 m, a–c giữ 1 s rồi về; d) 0,6 m, quay lại sau một frame; e) 0,6 m, giữ | PP-SWR-121 |
| F03 | Lane model | Nhận nhầm vạch làn bên | a) vạch trái nhảy sang L2 trong một frame; b) như a, kéo dài 0,5 s; c) cả hai vạch nhảy sang làn bên, không có cờ chuyển làn; d) vạch cũ hoặc vết nứt lệch 0,5 m, kéo dài 2 s; e) như a, giữa lúc ELK | PP-SWR-050, 122 (vòng kín) |
| F04 | Lane model | Mất một vạch | a) trái, mất ngay; b) phải, mất ngay; c) trái, độ tin giảm về 0 trong 2 s; d) phải, độ tin giảm về 0 trong 2 s; e) mất lúc bề rộng làn đang đổi | PP-SWR-050, 123 (a–d, vòng kín) |
| F05 | Lane model | Mất mọi biên: hai vạch làn mình, vạch làn bên, mép đường | a) dựng lại 0,5 s rồi mất; b) dựng lại 1 s rồi mất; c) mất 0,5 s rồi có lại; d) mất giữa cua R = 500 m | PP-SWR-043, 124 |
| F06 | Lane model | Độ cong sai | Mọi vạch. a) c2 +0,0005 1/m trên đường thẳng; b) −0,0005 1/m trong cua; c) c3 +4·10⁻⁶ 1/m², cùng sai số độ cong với a tại 40 m; d) như a, kéo dài 2 s; e) như a, ở đoạn vào cua. a, b, c, e kéo dài 1 s | PP-SWR-125 |
| F07 | IMU | Nhiễu | a) yaw rate σ = 0,07 °/s, a_y σ = 0,004 m/s²; b) 0,14 °/s và 0,008 m/s² | PP-SWR-135 (a, b, vòng kín) |
| F08 | IMU | Bias yaw rate | a) 0,1 °/s; b) 0,3 °/s; c) 1 °/s (cảm biến thô chưa bù) | PP-SWR-136 (a, b, vòng kín) |
| F09 | Thời gian | Trễ | Quét ở mục 6.1 |   |
| F10 | Thời gian | Jitter, mất message | a) mất lẻ; b) mất chuỗi 2; c) mất chuỗi 5; d) jitter ±20 ms | PP-SWR-126 |
| F11 | Thời gian | Muộn, sai thứ tự | Message đến sau message mới hơn | PP-SWR-127 |
| F12 | Thời gian | Ngừng gửi | Từng input ngừng gửi quá timeout, rồi gửi lại (hồi phục) | PP-SWR-043 (Lane Model), 044 (Lane Model, hồi phục), 045 (Lane Model, hồi phục), 046 (v_y, trong S5), 124 (Lane Model), 140 (Perception, trong S3), 141 (Perception, trong S5), 142 (IMU, tốc độ, góc lái), 144 (v_y), 145 (FunctionRequests) |
| F13 | Thời gian | Camera chậm hơn planner | 20 Hz so với 40 Hz, luôn có | PP-SWR-128 |
| F14 | Thời gian | Mất đồng bộ đồng hồ | a) trôi ±20 ppm; b) ±100 ppm; c) mất gPTP 10 s | PP-SWR-137 (a, b, c, vòng kín) |
| F15 | Toàn vẹn | Counter lặp, nhảy, đứng yên | Trên từng kênh | PP-SWR-129 (lặp), 130 (nhảy, đứng yên) |
| F16 | Toàn vẹn | Cờ không hợp lệ | `valid = false`, qualifier FAULT | PP-SWR-130 |
| F17 | Toàn vẹn | CRC sai | Khung CAN | PP-SWR-130, 142 |
| F18 | Toàn vẹn | Làm tròn CAN | Theo factor của DBC, luôn có | PP-SWR-139 (vòng kín) |
| F19 | Thời gian | Stamp ở tương lai | a) lane model +5 ms; b) +15 ms; c) +50 ms; d) một frame +50 ms; e) ObjectList +15 ms | PP-SWR-132 |
| F20 | Ego-motion | Không hợp lệ | a) một lần; b) liên tục; c) xen kẽ mỗi chu kỳ; d) như b, giữa lúc LKA | PP-SWR-043, 143 |
| F21 | Lane model | Mất hai vạch làn mình, còn biên khác | a) còn L2, R2, độ tin ≥ `conf_inferred`; b) chỉ còn L2; c) chỉ còn mép đường phải ngoài hành lang làn đang chạy, kéo dài 5 s; d) như a, cua R = 500 m; e) như a, độ tin giữa `conf_ego` và `conf_inferred` | PP-SWR-047, 050, 124 (e), 147 (a–d), 148 (a–d, vòng kín) |
| F22 | Lane model | Tầm nhìn ngắn hoặc thay đổi, không có cờ | Bật điều kiện tầm nhìn của HWA (mục 4.8); đường chủ chạy 25 m/s. a) mọi vạch còn 30 m trong 0,5 s, ngắn hơn `t_view_hold` nên HWA vẫn lái; b) chỉ R1 còn 30 m, tới cuối ca; c) mọi vạch còn 30 m trong 2 s, ở đoạn vào cua; d) 30 m và tầm nhìn danh định xen kẽ từng frame, 2 s; e) báo 150 m với cùng đa thức, phần ngoài đoạn đã thấy là ngoại suy, 1 s, ở đoạn vào cua; f) mọi vạch còn 15 m trong 3 s (0,6 s nhìn trước): HWA rời REQUEST sau `t_view_hold`, rồi trở lại | PP-SWR-017 (e), 042 (f), 050, 149 (a, b, c, d, e, f, vòng kín) |

### 6.1 Quét độ trễ và tầm nhìn

Độ trễ thật (mentor) và tầm nhìn thật (PP-ASM-020) chưa biết, nên quét nhiều mức. Chỉ đổi simulator; planner giữ nguyên cấu hình.

| Mã | Quét | Mức | Yêu cầu |
|---|---|---|---|
| Q1 | Trễ camera (lane model, vật thể) | 0 / 50 / 100 / 150 / 200 / 300 ms, mỗi mức jitter ±20 ms | PP-SWR-012, 013, 131 (300 ms), 133 (200 ms) |
| Q2 | Trễ yaw rate đã lọc, planner không được báo | 0 / 25 / 50 / 100 ms | PP-SWR-138 (0–50 ms, vòng kín) |
| Q3 | Trễ FunctionRequests | 20 / 40 / 60 ms | PP-SWR-038 |
| Q4 | Tầm nhìn camera | Điểm cuối 10 / 20 / 40 / 80 / 126 m; điểm đầu 0 / 5 / 10 m. Trên S1 (a, c, f) và S14 (a, e). Mức có thời gian nhìn trước dưới `t_view_hwa` vẫn chạy để thấy khả năng của thuật toán. Chạy: `python3 -m eval.matrix Q4` | PP-SWR-017, 050, 151 |

### 6.2 Ghép lỗi

1. Mỗi kịch bản và biến thể với từng lỗi một, ở ba thời điểm, vòng hở và vòng kín. Lỗi nhiều mức chạy đủ mức trên biến thể khó nhất, mức giữa trên các biến thể còn lại.
2. Ca gộp "đêm mưa": nhiễu × 2,5, μ = 0,5, mất một vạch, trễ camera 150 ms.

### 6.3 Mã không truy về requirement của planner {#benchmark-trace-exempt}

| Mã | Lý do |
|---|---|
| S10 | Kiểm khối Chức năng ADAS: không kích hoạt thừa khi xe đi gần vạch mà không trôi. Dùng để chọn `tlc_lka` (mục 7) |
| F09 | Dòng gom của quét độ trễ; truy vết ở Q1, Q2, Q3 |

## 7. Calibration sweeps {#test-calibration}

| Mã | Tham số | Cách quét | Chọn theo |
|---|---|---|---|
| P1 | Calibration parameter của planner (Software Architectural Design mục 11) | Từng tham số trong dải quét, các tham số khác ở giá trị khởi đầu; sau đó quét gộp quanh bộ tốt nhất | Đạt mọi requirement trên mọi profile; rồi performance target theo thứ tự ưu tiên ở mục 9 |
| P2 | `tlc_lka` của khối Chức năng ADAS | 0,6 / 1,0 / 1,5 s trên S4 đến S8 và S10 | DTLE nhỏ nhất (S4–S8) đặt cạnh số lần kích hoạt thừa (S10, mục tiêu 0) |
| P3 | Calibration parameter khác của khối Chức năng ADAS | Như P1 | Như P2 |

Chọn trên bộ chỉnh, chấm trên bộ kiểm. Một bộ calibration cho mọi profile.

## 8. Tiêu chí đạt và chỉ số {#test-criteria}

### 8.1 Requirement: đạt hoặc trượt {#benchmark-pass-fail}

Một requirement đạt khi đạt ở mọi kịch bản, biến thể, seed và profile mà cột Kiểm chứng của Software Requirements Specification chỉ ra.

| Chỉ số | Cách đo | Ngưỡng | Requirement |
|---|---|---|---|
| DTLE nhỏ nhất | Từ mép ngoài lốp trước tới mép trong vạch hoặc mép đường, nhỏ nhất trong lần can thiệp | ≥ −0,3 m (LKA, ELK vạch liền), ≥ −0,1 m (ELK mép đường) | PP-SWR-086, 091 |
| Khoảng cách tới xe ở làn bên | Khoảng cách ngang nhỏ nhất giữa hai xe trong lần ELK do xe ở làn bên | ≥ 0,3 m | PP-SWR-088 |
| DLC so với làn thật | Nhỏ nhất ở mỗi phía. Với PP-SWR-051 chỉ khi khoảng trống thật mỗi bên ≥ `free_space_min` | ≥ 0 | PP-SWR-051, 060, 122, 123, 148 |
| DLC phía trôi khi LKA hoàn tất | DLC thật phía yêu cầu tại tick LKA báo COMPLETED | ≥ 0 | PP-SWR-084 |
| DLC phía đối diện | DLC nhỏ nhất ở phía đối diện từ lúc bắt đầu can thiệp tới hết 1 s bàn giao EPS sau COMPLETED hoặc hủy. Dừng cửa sổ tại lần can thiệp độc lập kế tiếp | ≥ 0 | PP-SWR-085 |
| `lane_too_narrow` khi làn hẹp | Khoảng trống thật mỗi bên < `free_space_min`: tỉ lệ chu kỳ có path hợp lệ báo `lane_too_narrow` | = 1 | PP-SWR-063 |
| a_y, a_y thêm vào, jerk | Trên Trajectory, theo chức năng đang lái. a_y cần lấy từ độ cong làn thật tại điểm path. Jerk trung bình 0,5 s | Theo PP-SWR-001, 003, 110 đến 115 | PP-SWR-001, 003, 110 đến 115 |
| Góc bánh, tốc độ vô lăng | Trên path | Theo VehicleConfig của profile | PP-SWR-116, 117 |
| Liên tục | Lệch ngang, hướng, độ cong giữa hai path liên tiếp, mọi chu kỳ, ở phần path mới trong tầm nhìn lane model báo, đổi về t0 theo chuyển động thật; không có lane model thì cả path | ≤ 0,05 m; ≤ 0,005 rad; ≤ 0,0003 1/m | PP-SWR-100 đến 102 |
| Phần quan sát | `observed_horizon_s` so với thời điểm path ra khỏi tầm nhìn lane model báo, mọi chu kỳ có path hợp lệ và có lane model | ≤ 0,1 s | PP-SWR-018 |
| Thời lượng can thiệp | REQUEST tới COMPLETED hoặc hủy | ≤ 10 s | PP-SWR-083 |
| Điểm đầu path can thiệp | Tại tick bắt đầu, so vị trí và v_lat tại cầu sau với trạng thái thật trong hệ làn | ≤ 0,1 m và ≤ 0,1 m/s | PP-SWR-080 |
| Hoàn tất | Theo dõi DLC, v_lat tại cầu trước, góc thân xe so với hướng làn và a_y thêm vào của path đang áp dụng tại mỗi tick | Báo COMPLETED cho đúng chức năng tại tick đủ `T_end_hold` | PP-SWR-032, 090 |
| ELK REQUEST muộn | DLC của lốp trước theo vạch phía yêu cầu tại thời điểm planner nhận REQUEST. Ca bổ sung S8 late bơm yêu cầu theo quỹ đạo danh định và xác nhận điều kiện bằng xe thật trong SIL | Không khởi động ELK nếu DLC < −0,3 m | PP-SWR-089 |
| Phản ứng với lỗi | Thời điểm `path_valid`, `active_function` đổi | Theo requirement, sai lệch ≤ một chu kỳ | PP-SWR-124, 142 đến 145, 147 |
| Output và arbitration | Giá trị PathStatus theo sự kiện | Theo requirement | PP-SWR-010 đến 015, 030 đến 047 |
| Cờ giới hạn lúc đè vạch | Giá trị `lateral_limit_reached` lúc lốp trước bắt đầu đè vạch, khi HWA lái và a_y cần lớn nhất > aysmax | true | PP-SWR-007 |
| Dời tâm khi có xe lớn | Trung bình lệch của path so với tâm làn thật trên đoạn 0–1 s, dương là ra xa xe lớn có khoảng hở nhỏ nhất. Chấm ở chu kỳ HWA lái, xe lớn ngang hàng với khoảng hở < `gap_truck_min`: 055 khi làn bên kia không có xe lớn ngang hàng, nhỏ nhất; 058 ở chu kỳ đầu tiên xe lớn tới ngang hàng, nhỏ nhất; 056 lớn nhất của phần lệch về phía xe lớn. Thân xe theo chiều dọc: cầu sau − 1 m tới cầu trước + 1 m | 055, 058: > 0; 056: ≤ 0 | PP-SWR-055, 056, 058 |

SIL xấp xỉ mép ngoài lốp trước bằng nửa `vehicle_width` ở cầu trước. Bề rộng kể cả gương làm DLC và DTLE bi quan khoảng 0,1–0,15 m. Khi phân tích ca S6 trượt trong khoảng này, kiểm lại xấp xỉ hình học. Ngưỡng chấm giữ theo requirement.

Ca được định trước cần can thiệp phải có REQUEST đến planner và path can thiệp của chức năng tương ứng. Thiếu một trong hai thì ca trượt và báo rõ bước thiếu.

Với PP-SWR-083, chấm từng lần có kết thúc quan sát được hoặc đã tới hạn 10 s. Nếu log dừng trước hạn trong lần đang ACTIVE, ghi thời lượng đã quan sát. Ca cần can thiệp phải có ít nhất một lần đủ cửa sổ chấm thời lượng.

Khi LKA hoặc ELK bắt đầu và trạng thái thật lệch khỏi path cũ quá 0,1 m hoặc 0,1 m/s, áp PP-SWR-080 tại tick đó theo PP-SWR-031. Những cặp path tiếp theo vẫn chấm liên tục.

### 8.2 Performance target: đo và xếp hạng {#benchmark-metrics}

Không có ngưỡng đạt. Báo cáo giá trị xấu nhất qua mọi seed và mức suy giảm so với mốc không nhiễu.

| Chỉ số | Cách đo | Tốt hơn khi | Target |
|---|---|---|---|
| Lệch ngang | Path so với tâm làn thật, đoạn 0–1 s | Nhỏ hơn | PP-SWR-050 |
| a_y thêm vào của HWA | Lớn nhất khi đưa về giữa hoặc dời tâm | Nhỏ hơn | PP-SWR-002 |
| Jerk ngang của HWA | Đỉnh và RMS | Nhỏ hơn | PP-SWR-004 |
| Lệch ngang tăng theo trễ | Q1 so với trễ 0 | Nhỏ hơn | PP-SWR-013 |
| Thời gian tính | Đồng hồ thật của máy: trung bình, p95, p99, lớn nhất | Nhỏ hơn | PP-SWR-016 |
| Thời gian báo trước | Từ lúc cờ giới hạn bật tới lúc a_y cần tại vị trí xe vượt aysmax; nhỏ nhất | Dài hơn | PP-SWR-064 |
| Thời gian tắt cờ | Từ lúc a_y cần lớn nhất < aysmax tới lúc cờ tắt; lớn nhất | Ngắn hơn | PP-SWR-008 |
| Thời gian đưa về giữa | Từ lúc HWA bắt đầu tới lệch ngang ≤ 0,1 m | Ngắn hơn | PP-SWR-053 |
| Khoảng hở khi dời tâm | Khoảng cách ngang nhỏ nhất từ thân xe thật (tại cầu sau và cầu trước) tới mép xe lớn, khi ngang hàng | Lớn hơn | PP-SWR-057 |
| Thời gian trả về sau xe lớn | Từ lúc hết ngang hàng tới lúc lệch ngang của xe thật ≤ 0,1 m | Ngắn hơn | PP-SWR-059 |
| Thời lượng LKA, ELK | Bắt đầu path can thiệp tới COMPLETED | Ngắn hơn | PP-SWR-081, 082 |
| DTLE của LKA | Như 8.1 | Lớn hơn | PP-SWR-087 |
| Độ cong sai | Lệch ngang đoạn 2–3 s chia cho lệch của path bám đúng lane model sai | Nhỏ hơn | PP-SWR-125 |
| Tốc độ quay vô lăng RMS | Vòng kín | Nhỏ hơn | Chỉ số phụ cho PP-SWR-004 |

Chỉ số của khối Chức năng ADAS (chọn calibration ở P2, P3): số lần kích hoạt thừa trong S10; lệch thời điểm kích hoạt giữa chế độ A và B.

Với S7, S8, báo thêm có va chạm với xe mục tiêu trong ca hay không theo Euro NCAP SA 4.3.3.4. Với LKA, ELK, báo a_y và jerk của xe thật theo phương pháp R79 Annex 8, 2.4. Hai kết quả này là thông tin bổ sung.

Thông tin thêm, đo trên xe theo R79 Annex 8, 2.4, trong khi HWA đang lái: a_y tại trọng tâm (ground truth 1 kHz, lọc Butterworth bậc 4 cắt 0,5 Hz, lọc nhân quả từ trạng thái ổn định), jerk là trung bình trượt 0,5 s của đạo hàm; thời gian dài nhất a_y vượt aysmax + 0,3 m/s²; có nằm trong giới hạn của R79 5.6.2.1.1 không (vượt aysmax + 0,3 tối đa 2 s, không vượt min(1,4·aysmax; 3,3) m/s²). Chưa chấm đạt hoặc trượt vì chưa có requirement trỏ tới.

### 8.3 Flexibility {#benchmark-flexibility}

- **Bộ chạy.** Bộ tối thiểu của đề bài, cộng S2, S3, S5, S6, S19, trên VP-0 đến VP-5; cùng một bản build và một bộ calibration.
- **Điểm.** (1) Tỉ lệ requirement đạt trên từng profile; phải là 100 % trên mọi profile. (2) Độ chênh của mỗi performance target giữa các profile: giá trị lớn nhất, nhỏ nhất, và profile tệ nhất.
- **Trình bày.** Bảng profile × chỉ số, đánh dấu profile tệ nhất của mỗi chỉ số.

### 8.4 Mức nghiêm trọng và kết luận {#benchmark-severity}

Mức của một lần trượt suy từ cột Type của Software Requirements Specification, không gán tay theo ca.

| Mức | Gồm | Lý do |
|---|---|---|
| BLOCKER | Requirement có Type Safety, hoặc có safety goal; requirement Type Interface; trượt C1 hoặc C2 (mục 11); lỗi thực thi của planner | Vi phạm safety goal; output không dùng được ở bên nhận |
| MAJOR | Requirement Type Regulatory không có safety goal | Không qua phê duyệt kiểu loại |
| MINOR | Requirement Type Functional không có safety goal | Sai chức năng, không vi phạm safety goal |
| — | Performance target | Chỉ đo và xếp hạng (mục 8.2) |

- Một lần trượt ở bất kỳ ca, profile, seed nào là đủ, như mục 8.1.
- Lỗi thực thi của planner: tiến trình dừng trong lúc gọi `pp_init` hoặc `pp_step`; lời gọi không trả về; output có NaN hoặc vô cực. Lỗi ở simulator hoặc bên chấm báo riêng, ca đó không được chấm.

| Kết luận | Khi |
|---|---|
| Bị chặn | Có ít nhất một trượt BLOCKER |
| Không qua phê duyệt | Không có BLOCKER; có trượt MAJOR |
| Không thấy lỗi chặn trong phạm vi đã thử | Không có BLOCKER và MAJOR |

- Cờ riêng: Tích hợp được khi đạt C3 (mục 11).
- Báo cáo không ghi planner là an toàn (mục 3).

## 9. Xếp hạng và so sánh {#test-ranking}

### 9.1 So sánh kỹ thuật trong một planner {#technique-comparison}

| Bước | Tiêu chí |
|---|---|
| 1 | Đạt mọi requirement ở mục 8.1 trên mọi profile. Trượt thì loại, dù mượt hơn |
| 2 | Performance target về an toàn: lệch ngang, khoảng hở, DTLE của LKA |
| 3 | Performance target về cảm nhận người lái: a_y thêm vào, jerk, thời gian đưa về giữa và trả về, thời lượng can thiệp |
| 4 | Flexibility: độ chênh giữa các profile |
| 5 | Thời gian tính |

- Ứng viên: quintic hoặc clothoid theo thời lượng; lấy mẫu trong Frenet (Werling 2010); QP hoặc MPC (Software Detailed Design). Mỗi kỹ thuật chạy với bộ calibration tốt nhất của chính nó (mục 7).
- Kết quả cho báo cáo: một bảng so sánh, và ít nhất một kỹ thuật bị loại kèm lý do bằng số liệu (đề bài).
- Thời gian tính trên Python chỉ dùng để so sánh các kỹ thuật, không khẳng định chạy được trên ECU.

### 9.2 So sánh giữa các planner {#planner-comparison}

- Đối tượng: mọi planner nộp dưới dạng thư viện C và đạt C1, C2 (mục 11).
- Không planner nào làm mốc; chỉ so các planner với nhau.
- Mọi planner chạy cùng bản benchmark, cùng ca cụ thể, profile và seed.

| Tầng | Chấm | Cách xếp |
|---|---|---|
| 1 | Kết luận ở mục 8.4 | Không thấy lỗi chặn, rồi Không qua phê duyệt, rồi Bị chặn. Trong cùng kết luận Bị chặn, ít requirement BLOCKER trượt hơn thì xếp trên |
| 2 | Điểm Euro NCAP LSS; tỉ lệ đạt của requirement MAJOR, MINOR | Điểm Euro NCAP cao hơn; bằng nhau thì tỉ lệ đạt trung bình cao hơn |
| 3 | Performance target theo bốn nhóm của mục 9.1, bước 2 đến 5 | Điểm thắng cặp từng nhóm; nhóm sau chỉ xét khi nhóm trước bằng điểm |

**Điểm Euro NCAP LSS** (Euro NCAP SA v10.4.1, mục 4.3.2, 4.3.3.6).

| Bài thử | Kịch bản | Điểm |
|---|---|---|
| LKA, vạch đứt | S4 | 0,25 |
| LKA, vạch liền | S4 | 0,25 |
| ELK, chỉ mép đường | S6 | 0,25 |
| ELK, vạch giữa đứt và không có vạch sát mép đường | S6 | 0,25 |
| ELK, vạch liền | S5 | 0,50 |
| ELK, xe ngược chiều | S7 | 0,50 |
| ELK, xe đang vượt | S8 | 0,50 |

- Một dòng được điểm khi mọi hàng của lưới chuẩn (mục 5.1) thuộc dòng đó đạt tiêu chí của văn bản, như Euro NCAP chấm theo tổ hợp.
- Tính riêng cho từng profile. Điểm của planner là điểm thấp nhất qua các profile (một bộ calibration cho mọi xe).
- Điều kiện được tính điểm (ESC, ELK mặc định bật) và điểm HMI thuộc khối khác, không chấm.

**Tỉ lệ đạt.** Với mỗi requirement: số lần chạy đạt chia số lần chạy có chấm requirement đó. Trung bình qua các requirement, không trọng số.

**Điểm thắng cặp.**

- Đơn vị ghép cặp: một lần chạy (ca cụ thể, profile, seed). Riêng flexibility: một ca cụ thể và seed, giá trị là độ chênh giữa các profile.
- Với mỗi performance target và mỗi cặp planner: lấy hiệu trên từng đơn vị, theo hướng "Tốt hơn khi" ở mục 8.2.
- Planner A thắng B khi khoảng tin cậy 95 % của trung bình hiệu nằm hẳn về phía A tốt hơn. Khoảng tin cậy tính bằng bootstrap theo đơn vị, 10 000 lần lấy mẫu lại, seed cố định (nhóm tự thống nhất). Không thì hòa.
- Điểm của một planner trong một nhóm: số lần thắng trừ số lần thua, qua mọi chỉ số của nhóm và mọi planner khác (phương pháp Copeland). Không dùng trọng số giữa các chỉ số.

## 10. Trình bày kết quả {#test-reporting}

| Loại | Nội dung |
|---|---|
| Kết luận | Đầu báo cáo: kết luận ở mục 8.4 và cờ Tích hợp được. Bị chặn thì liệt kê mọi trượt BLOCKER: ID requirement, safety goal, mã ca, profile, seed, thời điểm trượt đầu tiên, file MCAP |
| So sánh planner | Mục 9.2: kết luận, điểm Euro NCAP, tỉ lệ đạt, điểm thắng cặp từng nhóm; kèm giá trị tuyệt đối của mọi chỉ số |
| Bảng tổng | Mỗi kỹ thuật một hàng: requirement đạt hay trượt, giá trị xấu nhất của mỗi performance target qua mọi seed |
| Theo thời gian | d(t) của path và xe cùng hai biên làn; a_y; jerk; chức năng đang lái; thời điểm đổi chức năng và bơm lỗi |
| Liên tục | Lệch giữa hai path liên tiếp theo chu kỳ, kèm đường ngưỡng |
| Theo v_lat | DTLE nhỏ nhất theo v_lat cho S4–S8, như Euro NCAP |
| Quét trễ | Chỉ số theo mức trễ, mỗi kỹ thuật một đường |
| Flexibility | Bảng profile × chỉ số |
| Thời gian tính | Histogram kèm p95, p99 |

## 11. Planner conformance {#planner-conformance}

- Planner được chấm là thư viện C11 theo `interfaces/c/pp_planner.h` (Interface Control Document mục 4; PP-ADR-013). Bên test nhận file thư viện đã build và chuỗi `pp_version`.
- Bộ B0 chỉ kiểm điều quan sát được qua contract gọi hàm. Không kiểm thuật toán, trạng thái bên trong, cấu trúc code hay MISRA.

| Mức | Kiểm | Nguồn | Trượt thì |
|---|---|---|---|
| C1 API | Có đủ `pp_state_size`, `pp_init`, `pp_step`, `pp_version`. Build từ `pp_types.h` của cùng phiên bản schema; kích thước và layout struct khớp header sinh ra. Chạy được với vùng nhớ trạng thái căn theo `PP_STATE_ALIGNMENT` | Interface Control Document mục 4 | Bị chặn; không chạy bộ khác |
| C2 Contract | `pp_init` không trả OK khi VehicleConfig thiếu hoặc ngoài giới hạn; khi đó không chu kỳ nào gửi Trajectory. Mỗi chu kỳ `pp_step` điền mọi output. Counter, stamp, enum, kích thước mảng, 31 điểm trên 0–3 s đúng Interface Control Document. Không có NaN hoặc vô cực. Input chưa nhận, `valid = false` hoặc giá trị ở hai đầu dải không làm planner dừng. `pp_version` trả cùng một chuỗi, có phiên bản, commit và mã bộ calibration | Interface Control Document mục 4, 6; PP-SWR-010, 011, 014, 146 | Bị chặn; không chạy bộ khác |
| C3 Integration | Cùng chuỗi input cho cùng output từng bit. Hai instance chạy xen kẽ cho cùng output như khi chạy riêng. Không ghi ra ngoài vùng nhớ trạng thái (kiểm bằng byte canh ở hai đầu). Bảng symbol không có cấp phát động, đọc file, đọc đồng hồ hệ thống | Interface Control Document mục 4; PP-ADR-013 | Vẫn chạy bộ khác; không có cờ Tích hợp được |

## 12. Kiểm bên chấm {#evaluator-check}

- Benchmark là công cụ kiểm chứng, nên phải chứng minh được nó phát hiện lỗi (ISO 26262-8:2018, mục 11).
- Bên test giữ một bộ planner mồi. Mỗi planner mồi là thư viện C theo `pp_planner.h`, viết riêng ở phía test, cố ý sai một điểm.
- Benchmark chỉ được dùng khi mọi planner mồi bị báo đúng requirement và đúng mức ở bảng dưới. Trượt thêm ở chỗ khác không ảnh hưởng.
- Chạy lại bộ planner mồi mỗi khi sửa `sim/`, `eval/` hoặc `benchmark/`.

| Mã | Lỗi cố ý | Phải được báo |
|---|---|---|
| PM-01 | Cộng bước nhảy ngang 0,1 m vào path mỗi 40 chu kỳ | PP-SWR-100; BLOCKER |
| PM-02 | Không giới hạn a_y theo aysmax | PP-SWR-001; BLOCKER |
| PM-03 | Giữ `path_valid = true` khi ego-motion không hợp lệ | PP-SWR-143; BLOCKER |
| PM-04 | Luôn `path_valid = false` khi HWA ở REQUEST | PP-SWR-030 (từ chối thừa); BLOCKER |
| PM-05 | Counter của PathStatus không tăng | C2 (PP-SWR-014); BLOCKER |
| PM-06 | Gửi Trajectory dù `pp_init` báo VehicleConfig sai | C2 (PP-SWR-146); BLOCKER |
| PM-07 | Giữ trạng thái trong biến toàn cục | C3 |
| PM-08 | Ghi quá cuối vùng nhớ trạng thái | C3 |
| PM-09 | Đọc đồng hồ hệ thống | C3 |

## Appendix A. Nguồn số liệu {#test-appendix}

- [autotijd.be, Volkswagen Golf 1.5L eTSI 115 hp](https://autotijd.be/en/dimensions/volkswagen/golf/15l-etsi-115-hp): bề rộng 1789 mm không gương, 2073 mm có gương; chỉ dùng cho chênh lệch bề rộng gương.
- [ISO 15622:2018, bản xem trước](https://cdn.standards.iteh.ai/samples/71515/46b6e07bde1f4c6f91cd143563bdc70f/ISO-15622-2018.pdf); [Euro NCAP LSS Test Protocol v4.3](https://cdn.euroncap.com/cars/assets/euro_ncap_lss_test_protocol_v43_f2ddd5f6d6.pdf); Bosch SMI230, bản giới thiệu sản phẩm 2018.

## Revision history {#revision-history}

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 0.4 | 2026-11-09 | Mô hình xe, dòng Tốc độ dọc: mọi kịch bản có HWA chạy với ACC chạy thử bật |
| 0.5 | 2026-11-10 | Thêm S19, F21; F05 là mất mọi biên; ACC chạy thử chuyển từ Software Architectural Design sang |
| 1.0 | 2026-11-10 | Refactor thành Software Qualification Test Specification, baseline BL1. Thêm vehicle profiles VP-0 đến VP-5 có nguồn và chấm flexibility; tách tiêu chí đạt (requirement) khỏi chỉ số xếp hạng (performance target); thêm calibration sweeps P1 đến P3; bỏ phần chạy lại log thật (không có log); bỏ nhãn trạng thái và việc mở |
| 1.1 | 2026-11-10 | Lateral Controller chạy thử: tách thời điểm đọc κ và sai số, ghi nguồn của K, controller báo ngừng điều khiển còn EPS trả quyền lái |
| 1.2 | 2026-11-10 | Mục 4.2: planner chạy trong simulator qua adapter SIL (PP-ADR-013) |
| 1.3 | 2026-11-10 | Mục 4.6: e_ψ của Lateral Controller chạy thử so với hướng chuyển động của xe, theo nghĩa `pose.yaw` ở Interface Control Document 6.1 |
| 1.4 | 2026-11-11 | Mục 4.5: ego-motion cộng v_y của VehicleStateEstimate, theo Interface Control Document 5.5 |
| 1.5 | 2026-11-11 | Chốt các lựa chọn của lần chạy đầu: trạng thái đầu trong cua, EPS lúc bắt đầu, tầm nhìn và trễ của camera, clothoid 100 m; thêm S1b e (clothoid 60 m); S2 tính tại lúc HWA bắt đầu lái, tốc độ, hướng góc của b; hình dạng của F02, F04, F06 |
| 1.6 | 2026-11-11 | Mục 8: PP-SWR-007 chấm lúc lốp đè vạch; thêm chỉ số thời gian báo trước (PP-SWR-064) và thời gian tắt cờ (PP-SWR-008), theo SRS 1.3 |
| 1.7 | 2026-11-11 | Mục 4.7: luật bám tốc độ đặt và đường bao trong cua; timeout của LateralLimits |
| 1.8 | 2026-11-11 | Mục 5.1: bài thử của R79 Annex 8, R171 Annex 4, EU 2021/646, Euro NCAP và kịch bản tương ứng; thêm biến thể neo S1 f, g, S1b f, S5 f, S14 e. Mục 5.2: ba tầng kịch bản, định dạng ASAM OpenSCENARIO và OpenDRIVE, cách chọn bộ cụ thể, bộ chạy smoke, hồi quy, đầy đủ |
| 1.9 | 2026-11-11 | Mục 8.2: a_y và jerk đo trên xe theo R79 Annex 8, 2.4, báo dạng thông tin |
| 1.10 | 2026-11-11 | Mục 8.1: PP-SWR-051 chỉ chấm khi khoảng trống thật đủ; dòng riêng cho PP-SWR-063, theo SRS 1.4 |
| 1.11 | 2026-11-11 | S1b d: tầm nhìn 40 m suốt ca, đường phẳng |
| 1.12 | 2026-11-11 | Mục 4.5: tầm phát hiện và `existence_probability` của ObjectList. Mục 8.1: cách chấm PP-SWR-055, 056, 058 theo SRS 1.5. Mục 8.2: cách đo target 057, 059 |
| 1.13 | 2026-11-11 | Mục 4: tài xế, traffic, biên đường và stand-in LKA, ELK hai chế độ. Mục 8: cửa sổ DLC, hình học DTLE, ca thiếu can thiệp và chỉ số vòng kín LKA, ELK |
| 1.14 | 2026-11-12 | F21(c) dùng mép ngoài hành lang làn đang chạy, theo PP-SWR-047 và PP-TS-007 |
| 1.15 | 2026-11-12 | Cụ thể hóa input tài xế, xe mục tiêu, neo S4–S8 và lưới chuẩn. Bổ sung cửa sổ đo, điều kiện hoàn tất và ca ELK REQUEST muộn |
| 1.16 | 2026-11-12 | Mục 4.5: tầm nhìn riêng từng vạch, điểm đầu và điểm cuối theo kịch bản. Mục 6: thêm F22 (lỗi tầm nhìn), Q4 (quét tầm nhìn) |
| 1.17 | 2026-11-12 | Mục 4.8: điều kiện tầm nhìn của HWA ở phía simulator. Mục 6: F22 bật điều kiện này, b dùng 30 m, thêm f (HWA trả lái rồi trở lại); Q4 chạy bằng `eval.matrix` |
| 1.18 | 2026-11-12 | Mục 5.3: bộ chạy theo khía cạnh B0–B8, nhãn độ khó L0–L5 và kết quả mong đợi, chấm hai chiều. Mục 8.4: mức nghiêm trọng, kết luận. Mục 9: tách so sánh kỹ thuật (9.1) và so sánh giữa các planner (9.2). Mục 10: kết luận đầu báo cáo. Mục 11: planner conformance. Mục 12: kiểm bên chấm bằng planner mồi |
| 1.19 | 2026-11-12 | Mục 8.1: liên tục chỉ chấm trong tầm nhìn lane model báo (SRS 1.9); thêm chỉ số `observed_horizon_s` (PP-SWR-018) |

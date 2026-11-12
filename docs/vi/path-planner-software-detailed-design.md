# Software Detailed Design

| Mục | Nội dung |
|---|---|
| Mã tài liệu | `PP-SDD` |
| Phiên bản | 1.7 |
| Trạng thái | BL1 |
| Tác giả | thongbui |
| Người review | thongbui |
| Cập nhật | 2026-11-12 |

## 1. Purpose and scope {#dd-scope}

- **Mục đích.** Mô tả thuật toán của từng thành phần path planner, đủ để viết code.
- **Phạm vi.** Mười một unit T1 đến T11, cấu trúc code, calibration parameter cấp thuật toán.
- **Ngoài phạm vi.** Kiến trúc và quyết định (Software Architectural Design, Architecture Decision Records); code của simulator và khối chạy thử (Software Qualification Test Specification).

## 2. References {#dd-references}

| Tài liệu | Dùng cho |
|---|---|
| [Software Architectural Design](report.html?doc=path-planner-software-architectural-design&lang=vi) | Thành phần, chu kỳ, calibration parameter cấp thiết kế |
| [Software Requirements Specification](report.html?doc=path-planner-software-requirements-specification&lang=vi) | Requirement, định nghĩa, giới hạn của calibration parameter |
| [Interface Control Document](report.html?doc=path-planner-interface-control-document&lang=vi) | Message và trường |
| [Software Qualification Test Specification](report.html?doc=path-planner-software-qualification-test-specification&lang=vi) | Chọn kỹ thuật lập path và calibration |
| Werling, Ziegler, Kammel, Thrun (2010), ICRA | Quintic và lấy mẫu trong Frenet; đổi Frenet sang Cartesian |

## 3. Units và cấu trúc code {#dd-units}

Ký hiệu: s là toạ độ dọc theo reference line, d là lệch ngang (dương sang trái), t ∈ [0, 3] s là thời gian trên path, v(t) lấy từ LongitudinalPlan.

| Unit | Thành phần trong Software Architectural Design | Module (`planner/src/`) |
|---|---|---|
| T1 Latency compensation | Input check, Latency compensation | `input_check.c`, `latency.c` |
| T2 Reference line | Reference line | `reference_line.c` |
| T3 Reference shaping | Reference line (lớp chống nhiễu) | `reference_line.c` |
| T4 Stitching và continuity | Stitching và continuity | `stitching.c` |
| T5 Curvature fusion | Reference line | `curvature.c` |
| T6 Lateral state | Path generation (trạng thái đầu) | `lateral_state.c`, riêng của planner (PP-ADR-014) |
| T7 Path generation | Path generation | `generators/quintic.c`, `generators/qp.c`, `intervention.c` |
| T8 Offset | Path generation (HWA) | `offset.c` |
| T9 Arbitration | Arbitration | `arbitration.c` |
| T10 Feasibility | Feasibility | `feasibility.c` |
| T11 Output | Output | `output.c` |

- C11, theo một phần MISRA C:2012 (PP-ADR-013). Không cấp phát động, không đọc file, không biến toàn cục; trạng thái nằm trong vùng nhớ do bên gọi cấp.
- Kiểu message lấy từ header C sinh ra trong `interfaces/c/`, theo Interface Control Document. Contract gọi hàm ở `interfaces/c/pp_planner.h`.
- Mọi calibration parameter nằm trong `planner/calibration/calibration.yaml`. Lúc build, file này sinh thành struct hằng trong C. Lúc `pp_init`, planner kiểm từng giá trị nằm trong giới hạn của Software Requirements Specification mục 7; sai thì không gửi Trajectory, như khi thiếu VehicleConfig.
- Planner chỉ dùng `interfaces/c/`; không gọi gì của simulator hay code test.
- Hàm số học dùng chung (khớp đa thức bậc 3, hệ 4×4) ở `pp_math.c`. Trong planner tính bằng double; chỉ struct của interface là float32.

## 4. T1 Latency compensation {#dd-t1}

| Bước | Việc |
|---|---|
| 1 | Input check: bỏ message có CRC sai hoặc counter lặp; ghi nhận mất khi counter nhảy; `valid = false` coi như chưa nhận. Quá timeout hoặc tuổi > 250 ms hoặc stamp ở tương lai > 10 ms: input không hợp lệ. Tuổi > 170 ms: ghi log (PP-SWR-131 đến 134) |
| 2 | Lấy LaneModel mới nhất, stamp t_c. Truy vấn ego-motion (t_c, t0). Không hợp lệ: `path_valid = false` (PP-SWR-143) |
| 3 | Với mỗi vạch và mép đường: lấy mẫu y(x) mỗi 1 m trong tầm nhìn; đổi mẫu sang `base_link` tại t0 bằng p_mới = R(−Δψ)·(p_cũ − [Δx, Δy]); khớp lại đa thức bậc 3 bằng bình phương tối thiểu; dời tầm nhìn đi Δx |
| 4 | Giữa hai frame camera, lặp bước 2–3 với frame mới nhất; không giữ đa thức đã dời từ chu kỳ trước (PP-SWR-128) |
| 5 | Stamp của IMU lùi đi `imu_filter_delay` lúc nhận. Giá trị đo một lần trên xe: độ trễ làm tương quan chéo giữa yaw rate thô và đã lọc lớn nhất, quét 0–200 ms |

## 5. T2 Reference line {#dd-t2}

**Bộ nhớ** giữ qua các chu kỳ: bề rộng làn w_mem; với mỗi biên k ∈ {L2, L1, R1, R2, mép trái, mép phải}, khoảng cách o_k từ biên tới tâm làn mình và độ bất định σ_o,k.

| Bước | Việc |
|---|---|
| 1 | Kiểm tính nhất quán từng biên (bảng dưới). Biên đủ tin = đạt điều kiện ở Software Requirements Specification mục 4 và nhất quán |
| 2 | L1 và R1 cùng đủ tin: tâm làn = (y_L1 + y_R1) / 2. Cập nhật w_mem và mọi o_k bằng lọc thông thấp hằng số thời gian `tau_mem`, chỉ khi bề rộng đo trong 2,5–5,5 m; đặt lại σ_o,k = `sigma_mem0` |
| 3 | Chỉ một trong L1, R1 đủ tin: tâm làn = biên đó ∓ w_mem/2. Không cập nhật bộ nhớ |
| 4 | Không vạch làn mình nào đủ tin, còn biên khác đủ tin: mỗi biên cho một tâm ứng viên y_k − o_k; kết hợp hệ số theo trọng số 1 / (σ_c0,k² + σ_o,k²). Đặt cờ tâm làn suy ra (PP-SWR-047). σ_o,k² tăng `q_mem` mỗi giây |
| 5 | Không còn biên nào đủ tin, kể cả khi lane model không hợp lệ: bám reference line cũ đã dời bằng ego-motion tối đa `T_coast`, path nối tiếp path cũ qua T4; rồi `path_valid = false` |
| 6 | Biên làn của reference line = tâm làn ± w/2, dùng cho khoảng hở (T8) và corridor (T7). Khoảng trống mỗi bên = (w − `vehicle_width`) / 2; nhỏ hơn `free_space_min` thì `lane_too_narrow = true` |

**Kiểm tính nhất quán**

| Thang | Kiểm | Không nhất quán khi |
|---|---|---|
| Từng frame | Biên mới so với bộ nhớ của biên đó, bộ nhớ dời bằng ego-motion mỗi chu kỳ, tại x = 0 | Lệch c0 > `k_jump`·√(σ_mới² + σ_cũ²) |
| Chậm: song song | Hiệu c1 của hai biên làn mình, lọc thông thấp `tau_mem` | Lệch > `parallel_max`; biên bị loại là biên đổi hướng so với lịch sử của chính nó |
| Chậm: bề rộng | Bề rộng đo so với w_mem | Lệch > `width_dev_max` giữ quá `T_confirm` |

- Biên không nhất quán thì không dùng, bộ nhớ giữ giá trị cũ. Vị trí mới thành ứng viên; ứng viên nhất quán với chính nó suốt `T_confirm` thì nhận là thay đổi thật. Sau khi nhận, vị trí cũ được giữ thêm `T_confirm`: biên quay về vị trí cũ thì nhận ngay.

**Chấp nhận thay đổi thật của làn**

| Thay đổi | Điều kiện | Xử lý |
|---|---|---|
| Đổi làn | Cả hai biên nhảy cùng chiều khoảng w_mem; hoặc `lane_change` của lane model; xác nhận trong một frame | Gán lại L1, R1 theo làn mới; dời reference line một bề rộng làn; T4 giữ path liên tục (PP-SWR-061) |
| Làn hẹp lại | Một biên dịch vào trong, liên tục và song song với lịch sử của chính nó, giữ `T_confirm` | Nhận bề rộng mới; tâm dịch theo, qua giới hạn của T3 |
| Làn rộng ra | Một biên dịch ra ngoài | Không nhận: neo tâm vào biên ổn định cộng w_mem (PP-SWR-060). Chỉ đặt lại w_mem khi cả hai biên cùng đo lại được một bề rộng mới, không còn biên nào đang dịch |

## 6. T3 Reference shaping {#dd-t3}

- Giữ một reference line đã làm mượt r(s), đưa từ chu kỳ trước sang `base_link` mới bằng ego-motion.
- Tại mỗi điểm s mỗi 1 m: r(s) ← r(s) + clamp(r_thô(s) − r(s), ±`ref_rate`·Δt).
- Khi T2 nhận đổi làn, dời r(s) đúng một bước nhảy trước khi giới hạn, để không kéo path theo bước nhảy.
- Path bám r(s); phần nhiễu còn lại được trọng số jerk của T7 lọc (PP-SWR-120).

## 7. T4 Stitching và continuity {#dd-t4}

| Bước | Việc |
|---|---|
| 1 | Đưa path chu kỳ trước về `base_link` tại t0 bằng ego-motion. Path cũ hơn timeout của Trajectory (75 ms) coi như không hợp lệ |
| 2 | Trạng thái đầu (d, ḋ, d̈) = trạng thái của path cũ tại t0, tính theo reference line mới. Nếu trạng thái đo (T6) lệch quá `stitch_reset` thì dùng trạng thái đo. Khi LKA, ELK bắt đầu luôn dùng trạng thái đo (PP-SWR-080) |
| 3 | T7 sinh path ứng viên từ trạng thái đầu |
| 4 | Chiếu về ngưỡng liên tục: tính lệch lớn nhất giữa path ứng viên và path cũ trên đoạn thời gian chung, cho lệch ngang Δd, hướng Δψ, độ cong Δκ. λ = min(1, `cont_margin`·0,05/Δd, `cont_margin`·0,005/Δψ, `cont_margin`·0,0003/Δκ). Path gửi = path cũ + λ·(path ứng viên − path cũ) |
| 5 | Bỏ bước 4 khi PP-SWR-031 cho phép (LKA, ELK bắt đầu lúc xe đã lệch) và khi path cũ không hợp lệ |

- Bước 2 lấy điểm của path cũ tại t0 bằng nội suy Hermite theo hướng tiếp tuyến. Nội suy dây cung lệch vào trong cua κ·L²·f(1−f)/2 và kéo điểm đầu vào trong mỗi chu kỳ.
- Bước 4 trộn trên 31 điểm Cartesian, cùng cách đo của PP-SWR-100 đến 102.
- Tổ hợp lồi của hai path đều nằm trong giới hạn a_y, jerk (ràng buộc tuyến tính theo d̈ và d⃛) thì vẫn nằm trong giới hạn.
- c0 jump: T2 loại biên nhảy nên reference line không nhảy. Nếu là thay đổi thật, bước 4 đưa path tới vị trí mới qua nhiều chu kỳ (PP-SWR-121).

## 8. T5 Curvature fusion {#dd-t5}

- Biến cần ước lượng: độ cong của tâm làn κ(s) tại các điểm s mỗi 2 m trong tầm nhìn.
- Mỗi điểm là một bộ lọc Kalman một chiều. Prior: κ(s) của chu kỳ trước, dời theo quãng xe đã đi, phương sai cộng `q_kappa`·Δs.
- Đo từ camera: κ_cam = 2·c2 + 6·c3·x, phương sai 4·σ_c2² + 36·x²·σ_c3², không nhỏ hơn `sigma_kappa_min`² (lane model có thể báo phương sai c2, c3 bằng 0). Chỉ cập nhật khi có frame mới.
- Đo tại s = 0 từ xe: κ_r = r / v, phương sai (`sigma_r` / v)²; chỉ dùng khi v > 5 m/s.
- Đo nào lệch prior quá `k_jump`·σ thì giảm trọng số đi 10 lần thay vì bỏ hẳn, để vẫn theo được cua thật (PP-SWR-125).
- Output: κ(s) trong đoạn đã quan sát khớp thành κ = a + b·x, trọng số 1/phương sai; thay c2 = a/2, c3 = b/6 của reference line. Lấy s ≈ x.

## 9. T6 Lateral state {#dd-t6}

Planner tự tính, không dùng chung với khối Chức năng ADAS (PP-ADR-014). Input: lane model tại t0, v_y, r, v, VehicleConfig.

| Đại lượng | Công thức |
|---|---|
| d0 | −c0 của tâm làn (xe ở tâm làn thì d0 = 0) |
| Góc lệch so với làn | −atan(c1 của tâm làn) |
| v_lat so với tâm làn | v_y + r·x_f − v·y_c'(x_f), như ADAS Function Specification mục 5 |
| DLC, TLC hai phía, độ bất định | Như ADAS Function Specification mục 5 |

## 10. T7 Path generation {#dd-t7}

**Interface chung** cho mọi kỹ thuật: `generate(trạng thái đầu, reference line, d mục tiêu, corridor, giới hạn, v(t)) → d(t)` trên lưới 0,1 s, 0–3 s. Corridor là [biên phải + `vehicle_width`/2, biên trái − `vehicle_width`/2]; ELK siết biên phía nguy hiểm để bánh xe không qua vạch phía đó.

| Chức năng | d mục tiêu | Thời lượng |
|---|---|---|
| HWA giữ làn | Offset của T8 (0 khi không có xe lớn) | `T_hwa` |
| HWA đưa về giữa | 0 | `T_recenter`. Bắt đầu khi HWA ở REQUEST mà chu kỳ trước chưa lái; kết thúc khi lệch ngang ≤ `recenter_done` hoặc HWA rời REQUEST |
| LKA | Điểm có DLC phía đã trôi = `dlc_target_lka`, giới hạn từ tâm làn tới phía đó | Khởi đầu bằng `T_lka` |
| ELK | Trong hành lang theo biên nguy hiểm, cách biên ít nhất `dlc_target_lka` nếu còn chỗ | Khởi đầu bằng `T_elk` |

LKA và ELK dùng kỹ thuật A trong cả hai bản build. Khi T9 chọn lần can thiệp mới, T7 dựng quintic từ trạng thái đo được (PP-SWR-080). T7 thử thời lượng trên lưới `intervention_T_step` nếu path ban đầu chưa đạt. Giới hạn thời lượng là phần còn lại của 10 s kể từ lúc nhận REQUEST (PP-SWR-083).

- Xét giới hạn a_y, a_y thêm vào và jerk theo PP-SWR-110 đến 115. Ưu tiên ứng viên thoả giới hạn và giảm phần lốp trước lấn qua hành lang. TLC thu hẹp khoảng cách dự kiến còn lại đến biên khi xe đang trôi ra. T10 kiểm path sau khi trộn với path cũ.
- Giữ hệ số quintic và mốc bắt đầu trong suốt lần can thiệp. Mỗi chu kỳ lấy mẫu theo thời gian đã qua, dùng reference line hiện tại. Sau thời lượng quintic, mẫu ngang giữ đích và vận tốc ngang bằng 0 cho tới khi T9 kết thúc hoặc hủy.
- Với ELK mép đường, dựng reference line từ mép nguy hiểm và biên đối diện đủ tin. Khi biên đối diện mất, dùng lại bề rộng đã nhớ nếu mép còn MEASURED và vị trí khớp mép đã gắn với làn sau bù ego-motion. Vạch ngoài làn đo được ở cùng phía loại mép đó khỏi hành lang làn đang chạy (PP-SWR-047).

**Ba kỹ thuật ứng viên** (đề bài: chọn một, ít nhất một phương án bị loại kèm lý do; chọn theo Software Qualification Test Specification mục 9):

| Kỹ thuật | Thuật toán | Calibration |
|---|---|---|
| A. Quintic theo thời lượng | d(t) bậc 5 từ trạng thái đầu tới (d mục tiêu, 0, 0) trong T. Chưa đạt `ay_add_max_hwa`, `jerk_target_hwa` thì tăng T theo bước 0,25 s tới `T_max`; giới hạn cứng do T10 cắt | `T_max` |
| B. Lấy mẫu Frenet | Sinh quintic với d cuối trong d mục tiêu ± `d_sample_span` bước `d_sample_step`, T trong `T_set`. Bỏ path vượt giới hạn hoặc ra khỏi corridor. Chọn path có J = `w_jerk`·∫d⃛² + `w_time`·T + `w_dev`·(d cuối − d mục tiêu)² + `w_cons`·∫(d − d_cũ)² nhỏ nhất | `d_sample_span`, `d_sample_step`, `T_set`, `w_jerk`, `w_time`, `w_dev`, `w_cons` |
| C. QP hợp nhất | Biến là jerk ngang j_k trên 30 bước (dạng nén); d, ḋ, d̈ có được bằng tích phân chính xác từ trạng thái đầu của T4. Cực tiểu `qp_w_jerk`·Σj² + `qp_w_dev`·Σ ramp·(d − o)² + `qp_w_cont`·Σ(d − d_cũ)² + cuối horizon `qp_w_term_d`·(d − o)² + `qp_w_term_v`·ḋ² + `qp_w_comfort`·Σσ² + `qp_w_corridor`·Σe²; o là offset của T8, d_cũ là path cũ chiếu lên reference line mới rồi dời theo phần o vừa đổi so với chu kỳ trước. Ràng buộc tuyến tính: a_y = d̈/q² + v²κ_ref/q, q = 1 − κ_ref·d lấy tại path cũ (như T11); trị tuyệt đối của a_y ≤ `qp_ay_margin`·aysmax; điểm có a_y cần > aysmax − epsilon_ay/2 thì a_y giữ trong [aysmax − epsilon_ay/2, aysmax] (PP-SWR-006) và không vào σ; điểm khác a_y vượt `qp_a_comfort` thì vào σ; d ra ngoài corridor (bề rộng làn − bề rộng xe − `qp_corridor_margin`) thì vào e; jerk của path (j + v³·dκ_ref/ds) trong ±0,9·jerk lớn nhất HWA. Cắt cua chỉ xuất hiện khi các ràng buộc này chạm; không có chế độ riêng. Giải bằng ADMM, ρ thích nghi, ρ riêng từng khối hàng (a_y ×10, jerk ×0,1), `qp_iters` vòng cố định, warm start từ chu kỳ trước; ma trận KKT khối chéo nên chỉ phân rã một khối 30×30. Sau đó T4 trộn như kỹ thuật A; T10 vẫn kiểm path cuối | Mục 15 |

Với HWA, `PP_T7` chọn `quintic` hoặc `qp` lúc build và được ghi trong `pp_version()` (PP-TS-003). Với LKA và ELK, bản `qp` cũng dùng quintic. PP-TS-006 theo dõi so sánh kỹ thuật cho can thiệp.

## 11. T8 Offset {#dd-t8}

| Bước | Việc |
|---|---|
| 1 | Gán vật thể vào làn theo biên của reference line. Xe lớn: bề rộng ≥ 2,3 m (Software Requirements Specification mục 4) |
| 2 | Bắt đầu khi TTC tới lúc ngang hàng với xe lớn ≤ `ttc_offset_start`; kết thúc `t_offset_hold` sau khi đuôi xe lớn đã qua đầu xe mình |
| 3 | Khoảng hở tới xe lớn mỗi bên: từ thân xe (± `vehicle_width`/2 quanh tâm làn) tới mép gần nhất của xe lớn phía đó trong cửa sổ ngang hàng; nhiều xe thì lấy nhỏ nhất; giữ giá trị cuối trong `t_offset_hold` |
| 4 | s = (w − `vehicle_width`) / 2. o_lim = max(0, min(`offset_max`, s − `dlc_offset_min`)). Phần thiếu h = max(0, `gap_truck_min` − khoảng hở) |
| 5 | o theo bảng ở Software Architectural Design mục 6 (một bên: h ra xa; hai bên: cân bằng), o dương là sang trái, cắt trong [−o_lim, o_lim]; đổi o tối đa `ref_rate` mỗi giây |
| 6 | ObjectList không hợp lệ: o về 0 với cùng tốc độ (PP-SWR-140) |

## 12. T9 Arbitration {#dd-t9}

Mỗi chức năng LKA và ELK giữ riêng pha, mốc nhận REQUEST, side, lý do ELK, mốc bắt đầu giữ điều kiện kết thúc và cờ chặn REQUEST. PathStatus công bố `lka_phase` và `elk_phase` theo PP-ADR-015.

| Bước | Việc |
|---|---|
| 1 | Kiểm timeout FunctionRequests theo thời gian nhận. Khi quá 75 ms, vô hiệu path ở cả PathStatus và Trajectory (PP-SWR-145) |
| 2 | Khi state rời REQUEST, xóa pha và cờ chặn của chức năng đó. Khi vừa nhận ELK REQUEST, chặn yêu cầu nếu lốp trước đã qua vạch phía yêu cầu quá 0,3 m (PP-SWR-089) |
| 3 | Lần can thiệp đang ACTIVE: tính điều kiện kết thúc từ DLC hai phía, v_lat, góc lệch và trị tuyệt đối a_y thêm vào của path đang áp dụng tại t0. Đưa v_y về t0 bằng ngoại suy tuyến tính từ hai VehicleStateEstimate hợp lệ gần nhất. Đặt COMPLETED khi giữ liên tục `T_end_hold`. Giữ pha tới khi state rời REQUEST (PP-SWR-032, 041, 090) |
| 4 | Chọn ELK > LKA > HWA trong các REQUEST đủ điều kiện. LKA, ELK cần biên đủ tin theo PP-SWR-047. Lần mới cần v_y hợp lệ. Lần đang chạy tiếp tục lấy mẫu quintic nếu chỉ mất v_y (PP-SWR-046). Hủy khi không còn đủ điều kiện hoặc đã tới giới hạn thời gian của PP-SWR-083 |
| 5 | Khi hoàn tất hoặc hủy, chọn chức năng kế tiếp ngay trong cùng chu kỳ. Nếu không còn ứng viên, báo NONE và giữ path bàn giao hợp lệ khi input cho phép. ELK mép đường vẫn xét hành lang theo biên trực tiếp ở tick nhận OFF. Trộn T4 theo PP-SWR-031, 036, 037 |
| 6 | Khi path không hợp lệ, báo NONE. Chặn các REQUEST can thiệp đang giữ cho tới khi rời REQUEST rồi yêu cầu lại (PP-SWR-043, 045) |

Kết quả khớp bảng arbitration state ở Software Architectural Design mục 5.1; unit test kiểm từng ô của bảng đó.

## 13. T10 Feasibility và giới hạn {#dd-t10}

| Bước | Việc |
|---|---|
| 1 | Trên 31 điểm: a_y = v²·κ; a_y thêm vào = a_y − v²·κ_ref; jerk = đạo hàm a_y, trung bình 0,5 s; `front_wheel_angle` = atan(`wheelbase`·κ); tốc độ quay vô lăng = `steering_ratio` × tốc độ đổi góc bánh |
| 2 | Vượt giới hạn của chức năng đang lái hoặc của VehicleConfig: cắt κ về giới hạn rồi tích phân lại d(t); vẫn giữ a_y ≥ aysmax − `epsilon_ay` khi a_y cần vượt aysmax (PP-SWR-006) |
| 3 | `lateral_limit_reached`: bật khi a_y cần lớn nhất trong tầm nhìn > aysmax + `delta_ay`, tắt khi < aysmax − `delta_ay`; điều kiện phải đúng ở các chu kỳ liên tiếp trong `T_flag` / 2 |
| 4 | LateralLimits: κ_max là trị tuyệt đối lớn nhất của κ(s) trong tầm nhìn; `v_max` = √(giới hạn a_y của chức năng / κ_max); `distance` = s tại κ_max |

- Bước 2 cắt cả độ cong của điểm 0, giữ vị trí. Jerk cắt theo từng bước 0,1 s, chặt hơn trung bình 0,5 s của requirement. Mỗi giới hạn chừa 10⁻⁶ tương đối để giá trị float32 gửi đi không vượt.
- Bước 3 và 4 dùng độ cong lớn hơn giữa reference line của camera và của T5: cờ và `v_max` báo trước cho khối dọc, nên lấy phía an toàn. Path vẫn bám độ cong của T5.

## 14. T11 Output {#dd-t11}

- Lấy mẫu t_k = 0,1·k, k = 0…30; s(t) tích phân v(t).
- Đổi (s, d) sang (x, y, yaw, κ) trong `base_link` theo công thức Frenet sang Cartesian của Werling (2010).
- `heading_rate` = v·κ; `lateral_velocity` = ḋ; `front_wheel_angle` theo T10; `rear_wheel_angle` = 0.
- `header.stamp_us` = t0; `counter` tăng 1.
- Gửi Trajectory, PathStatus, LateralLimits; ghi thời gian tính và log overrun nếu quá `t_budget`.

## 15. Calibration parameters cấp thuật toán {#dd-calibration}

Bổ sung cho Software Architectural Design mục 11; cùng cách quét (Software Qualification Test Specification, P1).

| Tham số | Đơn vị | Khởi đầu | Dải quét | Unit |
|---|---|---|---|---|
| `imu_filter_delay` | ms | 0 | Đo trên xe | T1 |
| `tau_mem` | s | 2,0 | 0,5–5,0 | T2 |
| `sigma_mem0` | m | 0,05 | 0,03–0,1 | T2 |
| `q_mem` | m²/s | 0,001 | 0,0002–0,005 | T2 |
| `parallel_max` | rad | 0,008 | 0,005–0,015 | T2 |
| `width_dev_max` | m | 0,3 | 0,2–0,5 | T2 |
| `cont_margin` | — | 0,9 | 0,7–1,0 | T4 |
| `q_kappa` | 1/m³ | 1·10⁻⁹ | 1·10⁻¹⁰–1·10⁻⁸ | T5 |
| `sigma_r` | rad/s | 0,002 | 0,001–0,005 | T5 |
| `sigma_kappa_min` | 1/m | 1·10⁻⁴ | 5·10⁻⁵–5·10⁻⁴ | T5 |
| `T_hwa` | s | 3,0 | 2,0–4,0 | T7 |
| `T_max` | s | 5,0 | 4,0–8,0 | T7 |
| `intervention_T_step` | s | 0,25 | 0,1–0,5 | T7 A |
| `recenter_done` | m | 0,1 | 0,05–0,2 | T7 |
| `d_sample_span`, `d_sample_step` | m | 0,3; 0,05 | 0,2–0,5; 0,025–0,1 | T7 B |
| `T_set` | s | 1,5 đến 4,0, bước 0,5 | — | T7 B |
| `w_jerk`, `w_time`, `w_dev`, `w_cons` | — | 1; 0,1; 1; 1 | 0,1–10 mỗi trọng số | T7 B |
| `qp_w_jerk`, `qp_w_dev`, `qp_T_ramp` | —; —; s | 1; 0,3; 1,0 | 0,3–3; 0,1–3; 0,5–2 | T7 C |
| `qp_w_term_d`, `qp_w_term_v` | — | 10; 10 | 0–50 | T7 C |
| `qp_w_comfort`, `qp_w_corridor` | — | 5; 500 | 1–50; 100–5000 | T7 C |
| `qp_w_cont` | — | 200 | 0–2000 | T7 C |
| `qp_a_comfort` | m/s² | 2,0 | 0–2,5 (0 là phạt thẳng a_y²) | T7 C |
| `qp_ay_margin` | — | 1,0 | 0,95–1,0 | T7 C |
| `qp_corridor_margin` | m | 0,3 | 0,1–0,5 | T7 C |
| `qp_iters`, `qp_rho0` | — | 150; 1,0 | 75–300; 0,1–10 | T7 C |

## Revision history {#revision-history}

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 0.3 | 2026-11-10 | Ghi chú T1 đến T8, bảng kỹ thuật ứng viên |
| 1.0 | 2026-11-10 | Viết thành Software Detailed Design, baseline BL1: thuật toán của 11 unit, cấu trúc code, calibration parameter cấp thuật toán |
| 1.1 | 2026-11-10 | Cấu trúc code chuyển sang C11 (PP-ADR-013): module `planner/src/*.c`, kiểu message từ `interfaces/c/`, calibration sinh thành struct lúc build |
| 1.2 | 2026-11-10 | T6 là hàm riêng của planner (PP-ADR-014) |
| 1.3 | 2026-11-11 | Ghi chú từ lần cài đặt đầu: `pp_math.c` và số học double; T2 bộ nhớ biên, nhận thay đổi qua `T_confirm`, bám reference line cũ cả khi lane model không hợp lệ; T4 nội suy Hermite, trộn trên điểm Cartesian; T5 sàn phương sai camera, chỉ cập nhật khi có frame mới, khớp lại c2, c3; T7 thời điểm bắt đầu và kết thúc đưa về giữa, `ay_add_max_hwa` và `jerk_target_hwa` là mục tiêu; T10 cắt cả điểm 0, chừa biên float32, cờ và LateralLimits lấy độ cong lớn hơn; thêm `sigma_kappa_min`, `recenter_done` |
| 1.4 | 2026-11-11 | T2: thay đổi chỉ được nhận khi vị trí mới ổn định suốt `T_confirm`; sau khi nhận, biên quay về vị trí cũ trong `T_confirm` thì nhận ngay |
| 1.5 | 2026-11-11 | T7 C viết lại thành QP hợp nhất dạng nén, giải bằng ADMM (PP-TS-003); calibration của T7 C; kỹ thuật chọn lúc build |
| 1.6 | 2026-11-11 | T7 C: liên tục với path cũ thành chi phí `qp_w_cont`, T4 vẫn trộn; a_y theo công thức của T11; dải a_y của PP-SWR-006; ràng buộc jerk; ρ theo khối hàng; `qp_ay_margin` 1,0. T8: offset theo khoảng hở tới xe lớn và `gap_truck_min`; T7 C dời path cũ theo phần offset vừa đổi |
| 1.7 | 2026-11-12 | T7 quintic cho LKA, ELK trong cả hai bản build. T9 giữ pha riêng, áp PP-SWR-145 tại output và chọn lại trong cùng chu kỳ khi hoàn tất hoặc hủy |

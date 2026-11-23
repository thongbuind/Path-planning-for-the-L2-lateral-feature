# Software Detailed Design

| Mục | Nội dung |
|---|---|
| Mã tài liệu | `PP-SDD` |
| Phiên bản | 1.30 |
| Trạng thái | BL1 |
| Tác giả | thongbui |
| Người review | thongbui |
| Cập nhật | 2026-11-23 |

## 1. Purpose and scope {#dd-scope}

- **Mục đích.** Mô tả thuật toán của từng thành phần của hai path planner (LCC planner, LKA/ELK planner), đủ để viết code.
- **Phạm vi.** Mười hai unit T1 đến T12, cấu trúc code, calibration parameter cấp thuật toán.
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
| T8 Offset | Path generation (LCC) | `offset.c` |
| T9 Intervention selection | Intervention selection | `selection.c` |
| T10 Feasibility | Feasibility | `feasibility.c` |
| T11 Output | Output | `output.c` |
| T12 Bám xe trước | Lead trail | `follow.c` |

- Hai planner dùng chung mã lõi và biên dịch riêng, không chia sẻ trạng thái lúc chạy (PP-ADR-016). LCC planner dùng T1 đến T8 và T10 đến T12; LKA/ELK planner dùng T1 đến T7 (chỉ kỹ thuật A), T9 đến T11. T8 và T12 chỉ có ở LCC planner; T9 chỉ có ở LKA/ELK planner.

- C11, theo một phần MISRA C:2012 (PP-ADR-013). Không cấp phát động, không đọc file, không biến toàn cục; trạng thái nằm trong vùng nhớ do bên gọi cấp.
- Kiểu message lấy từ header C sinh ra trong `interfaces/c/`, theo Interface Control Document. Contract gọi hàm ở `interfaces/c/pp_planner.h`.
- Mọi calibration parameter nằm trong `planner/calibration/calibration.yaml`. Lúc build, file này sinh thành struct hằng trong C. Lúc `pp_init`, planner kiểm từng giá trị nằm trong giới hạn của Software Requirements Specification mục 7; sai thì không gửi Trajectory, như khi thiếu VehicleConfig.
- Planner chỉ dùng `interfaces/c/`; không gọi gì của simulator hay code test.
- Hàm số học dùng chung (khớp đa thức bậc 3, hệ 4×4) ở `pp_math.c`. Trong planner tính bằng double; chỉ struct của interface là float32.

### 3.1 Interface của từng unit {#dd-unit-interface}

Mọi unit chạy trong một lần gọi `pp_*_step`, mỗi chu kỳ 25 ms, theo thứ tự ở Software Architectural Design mục 3.2. Trạng thái là phần giữ giữa hai chu kỳ, nằm trong vùng nhớ do bên gọi cấp.

| Unit | Nhiệm vụ | Input | Output | Trạng thái giữa chu kỳ | Calibration parameter | Chạy khi |
|---|---|---|---|---|---|---|
| T1 | Kiểm valid, counter, CRC, timeout, tuổi; dời lane model về t0 | Mọi input, EgoMotionQuery | Input dùng được, lane model tại t0 | Counter và message dùng được gần nhất của mỗi input | `imu_filter_delay` | Mỗi chu kỳ; dời lane model khi có frame mới |
| T2 | Chọn biên đủ tin, dựng tâm và bề rộng, suy tâm từ biên khác, COAST | Lane model tại t0, ego-motion | Reference line, bề rộng, `lane_too_narrow`, cờ biên bị loại | Track từng vạch (đã nhận, chờ xác nhận, vị trí cũ), bề rộng nhớ, reference line cũ cho COAST | `conf_ego`, `conf_edge`, `conf_inferred`, `k_jump`, `T_confirm`, `T_coast`, `free_space_min`, `tau_mem`, `sigma_mem0`, `q_mem`, `parallel_max`, `width_dev_max` | Mỗi chu kỳ |
| T3 | Làm mượt reference line, giới hạn tốc độ dời | Reference line thô, ego-motion | Reference line đã làm mượt | r(s) của chu kỳ trước | `ref_rate` | Mỗi chu kỳ |
| T4 | Nối path mới với path cũ, giữ continuity | Path ứng viên, path cũ, ego-motion | Path đã nối, trạng thái đầu của path | Path đã gửi ở chu kỳ trước | `stitch_reset`, `stitch_soft_min`, `cont_margin` | Mỗi chu kỳ |
| T5 | Ước lượng độ cong κ(s) của tâm làn | Reference line, yaw rate, tốc độ | c2, c3 của tâm làn | κ và phương sai trên lưới 2 m, stamp của frame cuối | `q_kappa`, `sigma_r`, `sigma_kappa_min`, `k_jump` | Dự báo mỗi chu kỳ; cập nhật camera khi có frame mới |
| T6 | Trạng thái ngang của xe so với làn | Reference line tại t0, v_y, r, v, VehicleConfig | d, ḋ, d̈, góc lệch, DLC | Không | — | Mỗi chu kỳ |
| T7 | Path LCC (quintic hoặc QP) hoặc path can thiệp hai pha | Reference line, trạng thái đầu, LongitudinalPlan, độ dời tâm | Path ứng viên 31 điểm | Vùng làm việc của QP (khởi tạo nóng) | `T_hwa`, `T_max`, `T_recenter`, `ay_add_max_hwa`, `jerk_target_hwa`, `T_lka`, `T_elk`, `T_return`, `T_return_object`, nhóm `w_*`, nhóm `qp_*` | Mỗi chu kỳ |
| T8 | Dời tâm LCC vì xe lớn | ObjectList, reference line | Độ dời tâm | Độ dời hiện tại, lúc bắt đầu giữ | `offset_max`, `offset_truck`, `gap_truck_min`, `dlc_offset_min`, `ttc_offset_start`, `t_offset_hold` | Mỗi chu kỳ, chỉ LCC planner |
| T9 | Chọn LKA hoặc ELK, pha, hành lang, báo COMPLETED | FunctionRequests, cờ hợp lệ, VehicleStateEstimate | `active_function`, pha, hành lang | Pha của từng chức năng, hành lang can thiệp, bộ đếm `T_end_hold` | `d_end`, `v_lat_end`, `heading_end`, `ay_add_end`, `T_end_hold`, `T_end_margin`, `corridor_tol`, `corridor_tau`, `corridor_toward` | Mỗi chu kỳ, chỉ LKA/ELK planner |
| T10 | Kiểm và cắt a_y, jerk, góc và tốc độ lái; cờ giới hạn; LateralLimits | Path, VehicleConfig, reference line của camera | Path cuối, `lateral_limit_reached`, LateralLimits | Cờ giới hạn có trễ và bộ đếm xác nhận | `epsilon_ay`, `ay_margin_hwa`, `delta_ay`, `T_flag` | Mỗi chu kỳ; bước 2 chạy hai lần ở LCC planner |
| T11 | Đổi sang `base_link`, lấy mẫu 31 điểm, điền header | Path cuối, trạng thái của planner | Trajectory, LccStatus hoặc InterventionStatus, LateralLimits | Counter của từng output | — | Mỗi chu kỳ |
| T12 | Lưu vết xe trước, dựng reference line ảo | LeadTarget, LongitudinalPlan, ego-motion | Reference line ảo, `lcc_mode = FOLLOW` | Vết xe trước, tâm làn gốc | `trail_n`, `trail_spacing`, `trail_fit_max`, `exist_min`, `follow_lat_max`, `follow_vlat_max` | Mỗi chu kỳ, chỉ LCC planner |

Hai loại tham số:

| Loại | Gồm | Ở đâu |
|---|---|---|
| Cố định | Giới hạn từ requirement (aysmax, jerk của từng chức năng, 31 điểm, chu kỳ 25 ms, giới hạn của FOLLOW) và hằng số của thuật toán (lưới 2 m của T5, bước 0,1 s của path) | Hằng số trong `planner/src/*.h`, trỏ về requirement |
| Calibration parameter | Mọi con số người thiết kế chọn | `planner/calibration/calibration.yaml`, sinh struct hằng lúc build; chỉnh lúc chạy xét ở PP-TS-029 |

## 4. T1 Latency compensation {#dd-t1}

| Bước | Việc |
|---|---|
| 1 | Input check: khung CAN do lớp nhận kiểm (bỏ CRC sai, counter lặp; ghi nhận mất khi counter nhảy). Message pub/sub: kiểm counter theo Interface Control Document mục 4; message được nhận thay message đang giữ, message bị bỏ hoặc có `valid = false` thì giữ message cũ như mất message. Quá timeout hoặc tuổi > 250 ms hoặc stamp ở tương lai > 10 ms: input không hợp lệ. Tuổi > 170 ms: ghi log (PP-SWR-131 đến 134). LongitudinalPlan có một điểm `v` hoặc `a` ngoài dải của Interface Control Document 5.7, kể cả NaN và vô cực: bỏ cả message, T11 dùng tốc độ hiện tại và gia tốc 0 (PP-SWR-154, 156) |
| 2 | Lấy LaneModel mới nhất, stamp t_c. Truy vấn ego-motion (t_c, t0). Không hợp lệ: `path_valid = false` (PP-SWR-143) |
| 3 | Với mỗi vạch và mép đường: lấy mẫu y(x) mỗi 1 m trong tầm nhìn; đổi mẫu sang `base_link` tại t0 bằng p_mới = R(−Δψ)·(p_cũ − [Δx, Δy]); khớp lại đa thức bậc 3 bằng bình phương tối thiểu; dời tầm nhìn đi Δx |
| 4 | Giữa hai frame camera, lặp bước 2–3 với frame mới nhất; không giữ đa thức đã dời từ chu kỳ trước (PP-SWR-128) |
| 5 | Stamp của IMU lùi đi `imu_filter_delay` lúc nhận. Giá trị đo một lần trên xe: độ trễ làm tương quan chéo giữa yaw rate thô và đã lọc lớn nhất, quét 0–200 ms |

## 5. T2 Reference line {#dd-t2}

**Bộ nhớ** giữ qua các chu kỳ: bề rộng làn w_mem; với mỗi biên k ∈ {L2, L1, R1, R2, mép trái, mép phải}, khoảng cách o_k từ biên tới tâm làn mình và độ bất định σ_o,k.

| Bước | Việc |
|---|---|
| 1 | Kiểm tính nhất quán từng biên (bảng dưới). Biên đủ tin = đạt điều kiện ở Software Requirements Specification mục 4 và nhất quán |
| 2 | L1 và R1 cùng đủ tin: tâm làn = (y_L1 + y_R1) / 2. Cập nhật w_mem và mọi o_k bằng lọc thông thấp hằng số thời gian `tau_mem`, chỉ khi bề rộng đo trong 2,5–5,5 m; đặt lại σ_o,k = `sigma_mem0`. Bề rộng đo ngoài 2,5–5,5 m khi đã có w_mem và reference line của chu kỳ trước: chỉ dùng vạch cho tâm gần tâm cũ hơn, theo bước 3 (PP-SWR-060, 122). LCC planner giữ reference line này làm tâm làn gốc cho T12 |
| 3 | Chỉ một trong L1, R1 đủ tin: tâm làn = biên đó ∓ w_mem/2. Không cập nhật bộ nhớ |
| 4 | Không vạch làn mình nào đủ tin, còn biên khác đủ tin: mỗi biên cho một tâm ứng viên y_k − o_k; kết hợp hệ số theo trọng số 1 / (σ_c0,k² + σ_o,k²). Đặt cờ tâm làn suy ra (PP-SWR-047). σ_o,k² tăng `q_mem` mỗi giây. Nếu vạch làn mình chỉ bị loại ở kiểm nhất quán (không mất, vẫn đủ tin theo SRS 4), làm bước 5 trước; hết `T_coast` mới suy tâm |
| 5 | Không còn biên nào đủ tin, kể cả khi lane model không hợp lệ: LCC planner dùng reference line ảo của T12 nếu đủ điều kiện bám xe. Không bám xe được, và với LKA/ELK planner: bám reference line cũ đã dời bằng ego-motion tối đa `T_coast`, path nối tiếp path cũ qua T4; rồi `path_valid = false`. Khi rời FOLLOW, `T_coast` tính từ lúc rời; nếu bộ nhớ reference line đã hết hạn trước đó thì coast trên đường vừa bám (PP-SWR-173) |
| 6 | Biên làn của reference line = tâm làn ± w/2, dùng cho khoảng hở (T8) và corridor (T7). Khoảng trống mỗi bên = (w − `vehicle_width`) / 2; nhỏ hơn `free_space_min` thì `lane_too_narrow = true` |

**Kiểm tính nhất quán**

| Thang | Kiểm | Không nhất quán khi |
|---|---|---|
| Từng frame | Biên mới so với bộ nhớ của biên đó, bộ nhớ dời bằng ego-motion mỗi chu kỳ, tại x = 0 | Lệch c0 > `k_jump`·√(σ_mới² + σ_cũ²) |
| Từng frame: hình dạng | Như trên, tại 50 % và 75 % đoạn tầm nhìn chung của hai frame | Lệch y(x) > `k_jump`·σ(x), σ(x)² = Σₖ (σ²ₖ,mới + σ²ₖ,cũ)·x²ᵏ trên các hệ số c0–c3 (PP-TS-001) |
| Chậm: song song | Hiệu c1 của hai biên làn mình, lọc thông thấp `tau_mem` | Lệch > `parallel_max`; biên bị loại là biên đổi hướng so với lịch sử của chính nó |
| Chậm: bề rộng | Bề rộng đo so với w_mem | Lệch > `width_dev_max` giữ quá `T_confirm` |

- Biên không nhất quán thì không dùng, bộ nhớ giữ giá trị cũ. Vị trí mới thành ứng viên; ứng viên nhất quán với chính nó suốt `T_confirm` thì nhận là thay đổi thật. Khi đang có ứng viên mà frame lại nhất quán với bộ nhớ, frame được nhận và bộ nhớ trước đó được giữ làm vị trí cũ như sau một thay đổi: bộ nhớ chỉ được dời theo ego-motion nên đoạn tầm nhìn chung ngắn dần và phép kiểm hình dạng yếu dần. Sau khi nhận, vị trí cũ được giữ chừng nào tầm nhìn của nó, dời bằng ego-motion, còn tới vị trí xe: biên quay về vị trí cũ thì nhận ngay.

**Chấp nhận thay đổi thật của làn**

| Thay đổi | Điều kiện | Xử lý |
|---|---|---|
| Đổi làn | Cả hai biên nhảy cùng chiều khoảng w_mem; hoặc `lane_change` của lane model; xác nhận trong một frame | Gán lại L1, R1 theo làn mới; dời reference line một bề rộng làn; T4 giữ path liên tục (PP-SWR-061) |
| Làn hẹp lại | Một biên dịch vào trong, liên tục và song song với lịch sử của chính nó, giữ `T_confirm` | Nhận bề rộng mới; tâm dịch theo, qua giới hạn của T3 |
| Làn rộng ra | Một biên dịch ra ngoài | Không nhận: neo tâm vào biên ổn định cộng w_mem (PP-SWR-060). Chỉ đặt lại w_mem khi cả hai biên cùng đo lại được một bề rộng mới, không còn biên nào đang dịch |

### 5.1 T12 Bám xe trước {#dd-t12}

Chỉ LCC planner. Điều kiện vào và duy trì ở Software Requirements Specification mục 8.13 (V1 đến V6, M1 đến M6); tóm tắt ở Software Architectural Design mục 6.3.

| Bước | Việc |
|---|---|
| 1 | Bộ đệm vết: mảng cỡ cố định `trail_n` điểm, xếp từ cũ tới mới. Mỗi chu kỳ có LeadTarget hợp lệ, `existence_probability` ≥ `exist_min`, loại CAR hoặc TRUCK thì thêm tâm xe trước (x, y) khi cách điểm cuối ≥ `trail_spacing`; đầy thì bỏ điểm cũ nhất. Mỗi chu kỳ dời mọi điểm bằng ego-motion; bỏ điểm đã ở sau xe mình. Frame mất, không hợp lệ, sai loại xe, hoặc báo `id` khác mục tiêu ACC đang có vết thì bỏ qua, không xóa bộ đệm: một frame lỗi không làm mất vết. Xe được ghi đổi thật (`id` mới là mục tiêu ACC, hoặc chưa có mục tiêu ACC) thì xóa bộ đệm. Ghi cả lúc còn vạch, để lúc mất vạch đã có sẵn vết |
| 2 | Tâm làn gốc: reference line của T2 ở lần cuối L1, R1 đủ tin, dời bằng ego-motion mỗi chu kỳ; ngoài đoạn đã quan sát thì ngoại suy theo độ cong cuối. Chiếu xe mình và xe trước lên tâm làn gốc: d_ego, d_lead |
| 3 | Đại lượng điều kiện: V3 = \|d_lead − d_ego\|. V4 = thành phần theo pháp tuyến tâm làn gốc của vận tốc xe trước, lấy từ `vx_rel`, `vy_rel` cộng vận tốc xe mình. M1 = lệch lớn nhất của path tới tâm làn gốc trên 3 s, so với min(0,8 m, s − `dlc_offset_min`), s = (w_mem − `vehicle_width`) / 2. M3, M4 từ `ESC_Speed`, `SAS_Steering`. M5 = quãng đường tích phân từ ego-motion kể từ lúc vào |
| 4 | Reference line ảo: parabol y(x) khớp bình phương tối thiểu qua các điểm của bộ đệm và vị trí xe trước hiện tại, thêm điểm neo ở xe mình (đầu đường) và các điểm neo dọc `heading` của xe trước, phía sau nó, với trọng số bằng nửa số điểm của vết cộng 5: nhiễu của vết không thành hướng tại xe trước, nơi đường tiếp tục theo cung tròn. Không dùng bậc 3 vì hệ số c3 chỉ khuếch đại nhiễu thành độ cong tại xe trước. Sai số khớp RMS > `trail_fit_max` thì không có path bám (M2 sai); không dùng sai số lớn nhất vì một điểm nhiễu của vết tốt đã làm hỏng (nhiễu vị trí xe trước ở 30 m cỡ 0,25 m). Bề rộng làn = w_mem |
| 5 | Path: quintic về d = 0 trên reference line ảo trong `T_hwa` (kỹ thuật A), qua T4, T10 với giới hạn của LCC. `view_end` = x của xe trước, nên `observed_horizon_s` là thời điểm path tới xe trước. T5 không chạy; độ cong lấy từ phép khớp |
| 6 | Một điều kiện M sai: rời mode, về LANE nếu L1, R1 đủ tin trở lại, không thì COAST (T2 bước 5). T4 nối path |
| 7 | Báo `lcc_mode` và `follow_distance` trong LccStatus theo chế độ đã dựng path của chu kỳ đó (PP-SWR-177) |

## 6. T3 Reference shaping {#dd-t3}

- Giữ một reference line đã làm mượt r(s), đưa từ chu kỳ trước sang `base_link` mới bằng ego-motion.
- Tại mỗi điểm s mỗi 1 m: r(s) ← r(s) + clamp(r_thô(s) − r(s), ±`ref_rate`·Δt).
- Khi T2 nhận đổi làn, dời r(s) đúng một bước nhảy trước khi giới hạn, để không kéo path theo bước nhảy.
- Path bám r(s); phần nhiễu còn lại được trọng số jerk của T7 lọc (PP-SWR-120).

## 7. T4 Stitching và continuity {#dd-t4}

| Bước | Việc |
|---|---|
| 1 | Đưa path chu kỳ trước về `base_link` tại t0 bằng ego-motion. Path cũ hơn timeout của Trajectory (75 ms) coi như không hợp lệ |
| 2 | Trạng thái đầu (d, ḋ, d̈, góc lệch) = S_cũ + w·(S_đo − S_cũ): S_cũ là trạng thái của path cũ tại t0, tính theo reference line mới; S_đo là trạng thái đo (T6); w = clamp((trị tuyệt đối của d_cũ − d_đo − `stitch_soft_min`) / (`stitch_reset` − `stitch_soft_min`), 0, 1). Khi `stitch_reset` ≤ `stitch_soft_min`, w = 0 tới `stitch_reset` và 1 khi vượt (PP-TS-021). Khi LKA, ELK bắt đầu luôn dùng trạng thái đo (PP-SWR-080). Với LCC planner, trong khi `driver_override`, hoặc LKA hoặc ELK ở REQUEST, và ở chu kỳ đầu sau khi hết, dùng trạng thái đo (PP-SWR-039, 040); khi không có FunctionRequests dùng được thì giữ giá trị của message dùng được gần nhất |
| 3 | T7 sinh path ứng viên từ trạng thái đầu. Với LCC, T10 bước 2 cắt path ứng viên trước bước 4 |
| 4 | Chiếu về ngưỡng liên tục: tính lệch lớn nhất giữa path ứng viên và path cũ trên đoạn thời gian chung, chỉ ở các điểm có x ≤ `view_end` của reference line (cả path khi bám reference line cũ), cho lệch ngang Δd, hướng Δψ, độ cong Δκ. Lệch của mỗi điểm chia cho hệ số của đoạn chứa điểm đó trước khi lấy giá trị lớn nhất: 1 cho 0–1 s, 2 cho 1–2 s, 4 sau 2 s (điểm đúng 1 s, 2 s thuộc đoạn trước; PP-TS-022 V1). λ = min(1, `cont_margin`·0,05/Δd, `cont_margin`·0,005/Δψ, `cont_margin`·0,0003/Δκ, ngưỡng chặt nhất của PP-SWR-100 đến 102 (đoạn 0–1 s)). Path gửi = path cũ + λ·(path ứng viên − path cũ) |
| 5 | Bỏ bước 4 ở chu kỳ đầu của mỗi lần LKA, ELK bắt đầu (PP-SWR-031, 049), khi path cũ không hợp lệ, và với LCC planner trong khi `driver_override = true` hoặc LKA hoặc ELK ở REQUEST (PP-TS-017) |

- Bước 2 lấy điểm của path cũ tại t0 bằng nội suy Hermite theo hướng tiếp tuyến. Nội suy dây cung lệch vào trong cua κ·L²·f(1−f)/2 và kéo điểm đầu vào trong mỗi chu kỳ.
- Bước 4 trộn trên 31 điểm Cartesian, cùng cách đo và cùng ba đoạn của PP-SWR-100 đến 102. Vẫn một λ cho cả path nên path gửi là tổ hợp lồi của hai path.
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
| LCC giữ làn | Offset của T8 (0 khi không có xe lớn) | `T_hwa` |
| LCC đưa về giữa | 0 | `T_recenter`. Bắt đầu khi LCC ở REQUEST mà chu kỳ trước chưa lái, khi hết ghi đè, hoặc khi LKA và ELK cùng rời REQUEST; kết thúc khi lệch ngang ≤ `recenter_done` hoặc LCC rời REQUEST |
| LCC khi tài xế ghi đè, hoặc khi LKA hoặc ELK ở REQUEST | Lệch ngang hiện tại của xe: path song song với làn, không kéo xe về (PP-TS-017) | `T_recenter`. Hết điều kiện thì chuyển sang LCC đưa về giữa |
| LCC bám xe trước | 0 trên reference line ảo của T12 | `T_hwa` |
| LKA | Tâm làn của hành lang can thiệp, d = 0 | Pha chặn đà khởi đầu bằng `T_lka`, pha về tâm `T_return` |
| ELK | Như LKA; biên phía nguy hiểm siết như ở interface chung | Pha chặn đà khởi đầu bằng `T_elk`, pha về tâm `T_return` |

LKA và ELK dùng kỹ thuật A trong cả hai bản build. Khi T9 chọn lần can thiệp mới, T7 dựng quintic từ trạng thái đo được (PP-SWR-080). T7 thử thời lượng trên lưới `intervention_T_step`, tới `intervention_T_max`, nếu path ban đầu chưa đạt.

- Xét giới hạn a_y, a_y thêm vào và jerk theo PP-SWR-110 đến 115. Ứng viên thoả giới hạn là ứng viên T10 bước 2 không cắt; ứng viên bị cắt chỉ dùng khi không còn ứng viên nào khác. Trong số đó, ưu tiên ứng viên giảm phần lốp trước lấn qua hành lang. TLC thu hẹp khoảng cách dự kiến còn lại đến biên khi xe đang trôi ra. T10 kiểm path sau khi trộn với path cũ.
- Xe đang trôi ra phía `side`: pha chặn đà là quintic từ trạng thái đo (d0, v0, a0) tới đỉnh d0 + 0,4·v0·T + 0,05·a0·T², kết thúc với vận tốc, gia tốc và jerk bằng 0; pha về tâm là quintic từ đỉnh về d = 0 trong `T_return`. Xe đã tự đi về phía tâm: chỉ một quintic về tâm trong `T_return` (PP-TS-026, PP-SWR-094). ELK vì xe ngược chiều hoặc đang vượt dùng `T_return_object` thay cho `T_return`, để rời phía có xe sớm hơn (PP-SWR-088). Ứng viên thời lượng áp cho pha chặn đà.
- Giữ hệ số quintic và mốc bắt đầu trong suốt lần can thiệp. Mỗi chu kỳ lấy mẫu theo thời gian đã qua, trên hành lang can thiệp của T9 (bước 7), không trên reference line của chu kỳ đó: biên nhảy không được kéo path theo. Sau thời lượng quintic, mẫu ngang giữ đích và vận tốc ngang bằng 0 cho tới khi T9 kết thúc hoặc hủy.
- Với ELK mép đường, dựng reference line từ mép nguy hiểm và biên đối diện đủ tin. Khi biên đối diện mất, dùng lại bề rộng đã nhớ nếu mép còn MEASURED và vị trí khớp mép đã gắn với làn sau bù ego-motion. Vạch ngoài làn đo được ở cùng phía loại mép đó khỏi hành lang làn đang chạy (PP-SWR-047).

**Ba kỹ thuật ứng viên** (đề bài: chọn một, ít nhất một phương án bị loại kèm lý do; chọn theo Software Qualification Test Specification mục 9):

| Kỹ thuật | Thuật toán | Calibration |
|---|---|---|
| A. Quintic theo thời lượng | d(t) bậc 5 từ trạng thái đầu tới (d mục tiêu, 0, 0) trong T. Chưa đạt `ay_add_max_hwa`, `jerk_target_hwa` thì tăng T theo bước 0,25 s tới `T_max`; giới hạn cứng do T10 cắt | `T_max` |
| B. Lấy mẫu Frenet | Sinh quintic với d cuối trong d mục tiêu ± `d_sample_span` bước `d_sample_step`, T trong `T_set`. Bỏ path vượt giới hạn hoặc ra khỏi corridor. Chọn path có J = `w_jerk`·∫d⃛² + `w_time`·T + `w_dev`·(d cuối − d mục tiêu)² + `w_cons`·∫(d − d_cũ)² nhỏ nhất | `d_sample_span`, `d_sample_step`, `T_set`, `w_jerk`, `w_time`, `w_dev`, `w_cons` |
| C. QP hợp nhất | Biến là jerk ngang j_k trên 30 bước (dạng nén); d, ḋ, d̈ có được bằng tích phân chính xác từ trạng thái đầu của T4. Cực tiểu `qp_w_jerk`·Σj² + `qp_w_dev`·Σ ramp·(d − o)² + `qp_w_cont`·Σ(d − d_cũ)² + cuối horizon `qp_w_term_d`·(d − o)² + `qp_w_term_v`·ḋ² + `qp_w_comfort`·Σσ² + `qp_w_corridor`·Σe²; o là offset của T8, d_cũ là path cũ chiếu lên reference line mới rồi dời theo phần o vừa đổi so với chu kỳ trước. Ràng buộc tuyến tính: a_y = d̈/q² + v²κ_ref/q, q = 1 − κ_ref·d lấy tại path cũ (như T11); trị tuyệt đối của a_y ≤ `qp_ay_margin`·aysmax; điểm có a_y cần > aysmax − epsilon_ay/2 thì a_y giữ trong [aysmax − epsilon_ay/2, aysmax] (PP-SWR-006) và không vào σ; điểm khác a_y vượt `qp_a_comfort` thì vào σ; d ra ngoài corridor (bề rộng làn − bề rộng xe − `qp_corridor_margin`) thì vào e; jerk của path (j + v³·dκ_ref/ds) trong ±0,9·jerk lớn nhất LCC. Cắt cua chỉ xuất hiện khi các ràng buộc này chạm; không có chế độ riêng. Giải bằng ADMM, ρ thích nghi, ρ riêng từng khối hàng (a_y ×10, jerk ×0,1), `qp_iters` vòng cố định, warm start từ chu kỳ trước; ma trận KKT khối chéo nên chỉ phân rã một khối 30×30. Sau đó T4 trộn như kỹ thuật A; T10 vẫn kiểm path cuối | Mục 15 |

Với LCC, `PP_T7` chọn `quintic` hoặc `qp` lúc build và được ghi trong `pp_version()` (PP-TS-003). Với LKA và ELK, bản `qp` cũng dùng quintic. PP-TS-006 theo dõi so sánh kỹ thuật cho can thiệp.

## 11. T8 Offset {#dd-t8}

| Bước | Việc |
|---|---|
| 1 | Gán vật thể vào làn theo biên của reference line. Xe lớn: bề rộng ≥ 2,3 m (Software Requirements Specification mục 4) |
| 2 | Bắt đầu khi TTC tới lúc ngang hàng với xe lớn ≤ `ttc_offset_start`; kết thúc `t_offset_hold` sau khi đuôi xe lớn đã qua đầu xe mình |
| 3 | Khoảng hở tới xe lớn mỗi bên: từ thân xe (± `vehicle_width`/2 quanh tâm làn) tới mép gần nhất của xe lớn phía đó trong cửa sổ ngang hàng; nhiều xe thì lấy nhỏ nhất; giữ giá trị cuối trong `t_offset_hold` |
| 4 | s = (w − `vehicle_width`) / 2. o_lim = max(0, min(`offset_max`, s − `dlc_offset_min`)). Phần thiếu h = max(0, `gap_truck_min` − khoảng hở); h > 0 là xe lớn quá gần. Xe ở làn bên kia: vật thể không phải xe lớn, ngang hàng hoặc có TTC tới lúc ngang hàng ≤ `ttc_offset_start` |
| 5 | o theo bảng ở Software Architectural Design mục 6: một xe lớn có h > 0 và làn bên kia không có xe thì dời ± min(`offset_truck`, o_lim) ra xa; một xe lớn và bên kia có xe không phải xe lớn thì 0; hai xe lớn thì cân bằng (g_T − g_P) / 2. o dương là sang trái, cắt trong [−o_lim, o_lim]; đổi o tối đa `ref_rate` mỗi giây |
| 6 | ObjectList không hợp lệ: o về 0 với cùng tốc độ (PP-SWR-140) |

## 12. T9 Intervention selection {#dd-t9}

Chỉ LKA/ELK planner. Việc chọn giữa hai planner thuộc arbitrator của công ty, không có ở đây (PP-ASM-022). Mỗi chức năng LKA và ELK giữ riêng pha, mốc nhận REQUEST, side, lý do ELK, mốc bắt đầu giữ điều kiện kết thúc và cờ chặn REQUEST. InterventionStatus công bố `lka_phase` và `elk_phase` theo PP-ADR-015.

| Bước | Việc |
|---|---|
| 1 | Kiểm timeout FunctionRequests theo thời gian nhận. Khi quá 75 ms, vô hiệu path ở cả InterventionStatus và Trajectory (PP-SWR-145) |
| 2 | Khi state rời REQUEST, xóa pha và cờ chặn của chức năng đó. Khi vừa nhận ELK REQUEST, chặn yêu cầu nếu lốp trước đã qua vạch phía yêu cầu quá 0,3 m (PP-SWR-089) |
| 3 | Lần can thiệp đang ACTIVE: tính điều kiện kết thúc từ DLC hai phía, lệch tâm, v_lat, góc lệch và trị tuyệt đối a_y thêm vào của path đang áp dụng tại t0, theo hành lang can thiệp (bước 7); ngưỡng `d_end`, `v_lat_end`, `heading_end`, `ay_add_end`. Đưa v_y về t0 bằng ngoại suy tuyến tính từ hai VehicleStateEstimate hợp lệ gần nhất. Đặt COMPLETED khi giữ liên tục `T_end_hold` + `T_end_margin`: điều kiện tính trên ước lượng nên giữ thêm để không báo trước trạng thái thật. Giữ pha tới khi state rời REQUEST (PP-SWR-032, 041, 090) |
| 4 | Chọn ELK > LKA trong các REQUEST đủ điều kiện. LKA, ELK cần biên đủ tin theo PP-SWR-047. Lần mới của LKA, ELK vạch cần vạch làn mình phía `side` đủ tin, không bị T2 loại, trên reference line không coast và không suy ra (PP-SWR-092). Lần mới cần v_y hợp lệ. Lần đang chạy tiếp tục lấy mẫu quintic nếu chỉ mất v_y (PP-SWR-046). Hủy khi không còn đủ điều kiện. Không có mốc cắt thời lượng |
| 5 | Khi hoàn tất hoặc hủy, chọn chức năng kế tiếp ngay trong cùng chu kỳ. Nếu không còn ứng viên, báo NONE và `Trajectory.header.valid = false` (PP-SWR-180). ELK mép đường vẫn xét hành lang theo biên trực tiếp ở tick nhận OFF. Trộn T4 theo PP-SWR-031, 036, 037 |
| 6 | Khi path không hợp lệ, báo NONE. Chặn các REQUEST can thiệp đang giữ cho tới khi rời REQUEST rồi yêu cầu lại (PP-SWR-043, 045) |
| 7 | Hành lang can thiệp: lúc lần can thiệp bắt đầu, chốt reference line (tâm, bề rộng, hai biên) làm hành lang; mỗi chu kỳ dời hành lang bằng ego-motion. Biên phía nguy hiểm mới lệch hành lang không quá `corridor_tol`: hành lang tiến về reference line chu kỳ đó với hằng số thời gian `corridor_tau`. Dịch vào phía xe quá `corridor_tol` và giữ liên tục `corridor_toward`: tiến nhanh gấp bốn. Dịch ra xa thì giữ hành lang cũ tới khi biên vẫn ở ngoài suốt `T_confirm`; khi đó, nếu biên đối diện cũng đổi thì hành lang tiến về reference line với `corridor_tau`, nếu không thì dịch tới biên mới với tốc độ `ref_rate`. Chu kỳ có biên đang chờ xác nhận không tính vào điều kiện kết thúc: bộ đếm `T_end_hold` đặt lại (PP-SWR-093, 094; PP-ADR-019). Lane model báo đổi làn thì hủy can thiệp |

Kết quả khớp bảng intervention state ở Software Architectural Design mục 5.1; unit test kiểm từng ô của bảng đó.

## 13. T10 Feasibility và giới hạn {#dd-t10}

| Bước | Việc |
|---|---|
| 1 | Trên 31 điểm: a_y = v²·κ; a_y thêm vào = a_y − v²·κ_ref; jerk = đạo hàm a_y, trung bình 0,5 s; `front_wheel_angle` = atan(`wheelbase`·κ); tốc độ quay vô lăng = `steering_ratio` × tốc độ đổi góc bánh |
| 2 | Vượt giới hạn của chức năng đang lái hoặc của VehicleConfig: cắt κ về giới hạn rồi tích phân lại d(t); vẫn giữ a_y ≥ aysmax − `epsilon_ay` khi a_y cần vượt aysmax (PP-SWR-006) |
| 3 | `lateral_limit_reached`: bật khi a_y cần lớn nhất trong tầm nhìn > aysmax + `delta_ay`, tắt khi < aysmax − `delta_ay`; điều kiện phải đúng ở các chu kỳ liên tiếp trong `T_flag` / 2 |
| 4 | LateralLimits: κ_max là trị tuyệt đối lớn nhất của κ(s) trong tầm nhìn; `v_max` = √(giới hạn a_y của chức năng / κ_max); `distance` = s tại κ_max |

- Với LCC, bước 2 chạy hai lần: trên path ứng viên trước T4 bước 4, và trên path gửi sau đó. Tổ hợp lồi của hai path khả thi vẫn khả thi, nên lần sau chỉ gặp phần do tốc độ đổi; T10 không phá liên tục sau khi trộn (PP-TS-003).
- Bước 2 cắt cả độ cong của điểm 0, giữ vị trí. Jerk cắt theo từng bước 0,1 s, chặt hơn trung bình 0,5 s của requirement. Mỗi giới hạn chừa 10⁻⁶ tương đối để giá trị float32 gửi đi không vượt.
- Bước 3 và 4 chỉ chạy ở LCC planner (LccStatus, LateralLimits). LKA/ELK planner chỉ chạy bước 1 và 2, và ghi `lateral_limit_reached` của InterventionStatus khi bước 2 cắt path.
- Với LCC, giới hạn a_y ở bước 2 là aysmax + `ay_margin_hwa` (PP-SWR-001, PP-TS-020). Cờ ở bước 3 và `v_max` ở bước 4 vẫn tính theo aysmax.
- Bước 3 và 4 dùng độ cong lớn hơn giữa reference line của camera và của T5: cờ và `v_max` báo trước cho khối dọc, nên lấy phía an toàn. Path vẫn bám độ cong của T5.

## 14. T11 Output {#dd-t11}

- Lấy mẫu t_k = 0,1·k, k = 0…30; s(t) tích phân v(t).
- Đổi (s, d) sang (x, y, yaw, κ) trong `base_link` theo công thức Frenet sang Cartesian của Werling (2010).
- `heading_rate` = v·κ; `lateral_velocity` = ḋ; `front_wheel_angle` theo T10; `rear_wheel_angle` = 0.
- `observed_horizon_s`: thời điểm path có x vượt `view_end` của reference line, nội suy tuyến tính giữa hai điểm; cả path nằm trong thì 3 s (PP-SWR-018).
- `header.stamp_us` = t0; `counter` tăng 1.
- Đặt `planner_id`. LCC planner gửi Trajectory, LccStatus, LateralLimits; LKA/ELK planner gửi Trajectory, InterventionStatus. Ghi thời gian tính và log overrun nếu quá `t_budget`.

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
| `stitch_soft_min` | m | 0,02 | 0–0,05 | T4 |
| `q_kappa` | 1/m³ | 1·10⁻⁹ | 1·10⁻¹⁰–1·10⁻⁸ | T5 |
| `sigma_r` | rad/s | 0,002 | 0,001–0,005 | T5 |
| `sigma_kappa_min` | 1/m | 1·10⁻⁴ | 5·10⁻⁵–5·10⁻⁴ | T5 |
| `T_hwa` | s | 3,0 | 2,0–4,0 | T7 |
| `T_max` | s | 5,0 | 4,0–8,0 | T7 |
| `intervention_T_step` | s | 0,25 | 0,1–0,5 | T7 A |
| `intervention_T_max` | s | 10,0 | 5,0–10,0 | T7 A |
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
| `trail_n` | điểm | 128 | 100–256 | T12 |
| `trail_spacing` | m | 0,5 | 0,25–1,0 | T12 |
| `trail_fit_max` | m | 0,4 | 0,3–0,6 | T12; RMS của phép khớp |
| `exist_min` | — | 0,5 | 0,3–0,8 | T12; dưới ngưỡng này LeadTarget coi như không có xe trước |
| `corridor_tol` | m | 0,15 | 0,1–0,3 | T9 bước 7; lệch biên nguy hiểm tới ngưỡng này vẫn là cùng một biên |
| `corridor_tau` | s | 0,5 | 0,25–1,0 | T9 bước 7; lọc nhiễu lane model trong lúc can thiệp |
| `corridor_toward` | s | 0,15 | 0,1–0,3 | T9 bước 7; ba frame camera trước khi coi biên thật sự dịch vào |

Giới hạn của T12: `trail_n`·`trail_spacing` ≥ 50 m, bằng khoảng cách lớn nhất tới xe trước (V2), để vết phủ từ xe mình tới xe trước.

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
| 1.8 | 2026-11-12 | T4 bước 4 chỉ xét phần path trong tầm nhìn (SRS 1.9, PP-TS-014). T11 thêm `observed_horizon_s` |
| 1.9 | 2026-11-13 | T1 bước 1 bỏ LongitudinalPlan ngoài dải (PP-SWR-156) |
| 1.10 | 2026-11-13 | T7: lưới thời lượng quintic của LKA, ELK tới `intervention_T_max` (mục 15), thay cho phần còn lại của 10 s; T9 bước 4 bỏ hủy khi quá 10 s (PP-SWR-083 obsolete, PP-TS-016) |
| 1.11 | 2026-11-13 | Theo PP-TS-017 V2: T4 bước 2 dùng trạng thái đo trong lúc ghi đè và chu kỳ đầu sau đó; bước 5 bỏ trộn trong lúc ghi đè; T7 nhắm độ lệch hiện tại của xe trong lúc ghi đè, rồi về tâm theo `T_recenter` (PP-SWR-039, 040; PP-PR-032) |
| 1.12 | 2026-11-14 | T7: ứng viên LKA, ELK thoả giới hạn khi T10 bước 2 không cắt. Lý do: T10 cắt jerk theo từng bước 0,1 s, chặt hơn trung bình 0,5 s; path bị cắt không kết thúc song song với làn và phần xa nhảy giữa các chu kỳ (PP-PR-041). T9 bước 4 trỏ điều kiện bắt đầu LKA, ELK vạch về PP-SWR-092 (PP-PR-038) |
| 1.13 | 2026-11-14 | T2 kiểm từng frame thêm hình dạng: so hai frame tại 50 % và 75 % đoạn tầm nhìn chung, ngưỡng `k_jump` theo phương sai các hệ số. Lý do: PP-TS-001 chọn J0 kiểm hình dạng (20261114-1857-study-PP-TS-001-13913da); kiểm riêng c0 không thấy độ cong sai (F06). Ảnh hưởng: PP-SWR-121, 122, 125; T2 |
| 1.14 | 2026-11-14 | T1 bước 1: kiểm counter của message pub/sub theo AUTOSAR E2E Profile 5 và giữ message dùng được gần nhất; `valid = false` như mất message. Lý do: PP-PR-035. Ảnh hưởng: PP-SWR-129, 130 |
| 1.15 | 2026-11-14 | HWA: T10 bước 2 cắt path ứng viên trước T4 bước 4, rồi kiểm lại path gửi. Lý do: PP-TS-003 chọn V0b (20261114-1934-study-PP-TS-003-272a711); T10 sau T4 phá liên tục ở cua tại aysmax (PP-PR-005, 006). Ảnh hưởng: PP-SWR-100 đến 102, 001; T4, T10 |
| 1.16 | 2026-11-14 | T2: khi đang có ứng viên, frame khớp ứng viên hơn bộ nhớ thì tính cho ứng viên. Lý do: PP-PR-048; hình dạng sai ngắn hơn `T_confirm` lọt qua bộ nhớ cũ và không để lại vị trí cũ cho R2 (F06 c). Ảnh hưởng: PP-SWR-121, 122, 125; T2 |
| 1.17 | 2026-11-14 | T2 bước 4: vạch làn mình bị loại ở kiểm nhất quán thì bám reference line cũ trước khi suy tâm từ biên ngoài. Lý do: PP-PR-052; một frame nhiễu làm tâm thành suy ra và LKA bị hủy (G01 trên S4c). Ảnh hưởng: PP-SWR-047, 030; T2 |
| 1.18 | 2026-11-14 | T2: thay quy tắc của 1.16. Frame nhất quán với bộ nhớ trong lúc có ứng viên được nhận, bộ nhớ trước đó giữ làm vị trí cũ cho R2. Lý do: PP-PR-055; quy tắc 1.16 loại cả frame nhất quán khi nhiễu tương quan theo thời gian, ELK bắt đầu trễ 0,8 s (S12 c). Ảnh hưởng: PP-SWR-121, 122, 125, 088; T2 |
| 1.19 | 2026-11-16 | T4 bước 4: ngưỡng của λ theo SRS 1.21 (0,2 m, 0,02 rad, 0,0012 1/m); `cont_margin` 0,9 → 0,225, dải 0,2–1,0, giữ giới hạn trộn cũ 0,045 m, 0,0045 rad, 0,00027 1/m. Lý do: mentor nới PP-SWR-100 đến 102; chưa có lần chạy cho giới hạn trộn lớn hơn |
| 1.20 | 2026-11-16 | T4 bước 4: một λ cho cả path theo ngưỡng đoạn 0–1 s của SRS 1.22; `cont_margin` trở lại 0,9, dải 0,7–1,0. Thay 1.19. Lý do: PP-SWR-100 đến 102 chia ba đoạn; trộn theo từng đoạn là phương án V4 của PP-TS-019 |
| 1.21 | 2026-11-16 | T4 bước 2: reset mềm, trạng thái đầu trộn path cũ và trạng thái đo theo độ lệch; thêm `stitch_soft_min` (mục 15). T4 bước 4 giữ một λ. Lý do: PP-TS-021 V7 (20261116-1748-study-PP-TS-021-8726b80); reset nhị phân để xe đứng sát dưới `stitch_reset` (PP-PR-056) hoặc làm path đổi qua lại mỗi chu kỳ khi ngưỡng nhỏ. Ảnh hưởng: PP-SWR-100, 051, target 050; PP-ADR-004 |
| 1.22 | 2026-11-17 | T2: vị trí cũ được giữ tới khi tầm nhìn của nó, dời bằng ego-motion, không còn tới vị trí xe, thay cho `T_confirm`. Lý do: PP-PR-057; với lỗi dài 2 · `T_confirm` vị trí cũ hết hạn một chu kỳ trước khi hình học đúng quay về (F06 d). Ảnh hưởng: PP-SWR-121, 122, 125; T2 |
| 1.23 | 2026-11-17 | T2 bước 2: bề rộng đo ngoài 2,5–5,5 m thì chỉ dùng vạch cho tâm gần tâm cũ hơn. Lý do: PP-PR-057; một vạch nhận nhầm được nhận sau `T_confirm` kéo tâm làn về giữa hai vạch cách nhau 7 m (F03 a dài 2 s). Ảnh hưởng: PP-SWR-060, 122; T2 |
| 1.24 | 2026-11-17 | T4 bước 5: bỏ trộn ở chu kỳ đầu của mọi lần LKA, ELK bắt đầu; trạng thái đầu là trạng thái đo, độ cong từ yaw rate (T6). Lý do: PP-PR-062, SRS 1.23. Ảnh hưởng: T4, T7, T9 |
| 1.25 | 2026-11-17 | T4 bước 4: lệch của mỗi điểm chia cho hệ số của đoạn thời gian chứa nó (1, 2, 4) trước khi tính λ; vẫn một λ cho cả path. Lý do: PP-TS-022 V1 (20261117-1315-study-PP-TS-022-d2e7d27); path quay về từ xa chậm ở F06 d vì phần xa bị giữ theo ngưỡng 0–1 s. Ảnh hưởng: PP-SWR-100 đến 102, 051; T4 |
| 1.26 | 2026-11-18 | Hai planner (PP-ADR-016). Mục 3: unit nào ở planner nào; thêm T12 (mục 5.1, bám xe trước, PP-ADR-018). T9 đổi tên Intervention selection, bỏ nhánh HWA, thêm bước 7 hành lang can thiệp (PP-ADR-019). T4: LCC planner bắt đầu từ trạng thái đo cả khi LKA, ELK ở REQUEST. T7: LKA, ELK về tâm làn, lấy mẫu trên hành lang can thiệp. T8: dời `offset_truck`, xe ở làn bên kia chặn dời. T10, T11 theo từng planner. Mục 15: thêm `trail_n`, `trail_spacing`, `trail_fit_max`. Lý do: mentor đổi sản phẩm ngày 18/11 (SRS 1.24). Ảnh hưởng: PP-SWR-039, 040, 055, 065, 066, 093, 094, 170 đến 178, 180, 181 |
| 1.27 | 2026-11-18 | Khớp với mã đã tách hai planner. Mục 3: module T9 là `selection.c`. T12: bộ đệm vết ghi không cần `target_id` khớp; reference line ảo là parabol có điểm neo theo `heading` xe trước, M2 theo RMS (`trail_fit_max` 0,4 m); thêm `exist_min`, `corridor_tol`. Lý do: bám xe trước chạy đầu cuối trong simulator cho thấy sai số lớn nhất và hệ số bậc 3 làm FOLLOW ngắt liên tục với nhiễu vị trí xe trước 0,25 m. Ảnh hưởng: calibration.yaml, PP-SWR-172 (xe trước đổi thì rời FOLLOW vẫn đúng theo M6) |
| 1.28 | 2026-11-18 | T7: path LKA, ELK hai pha (PP-ADR-021). T9 bước 3 giữ thêm `T_end_margin`; bước 7 lọc nhiễu bằng `corridor_tau`, `corridor_toward`. T12: bộ nhớ reference line đã hết hạn thì lấy đường đang bám để coast sau khi rời FOLLOW. Bước 1: frame lỗi của LeadTarget không xóa bộ đệm vết. Lý do: PP-TS-026, PP-PR-070, 071, 072 |
| 1.29 | 2026-11-23 | T10: giới hạn a_y của path LCC là aysmax + `ay_margin_hwa`; cờ và `v_max` giữ theo aysmax. Lý do: PP-TS-020 V1a, SRS 1.26 |
| 1.30 | 2026-11-23 | Mục 3.1: interface của từng unit (nhiệm vụ, input, output, trạng thái, calibration parameter, lúc chạy) và hai loại tham số. Lý do: quy trình phát triển của công ty, bước 2.2 |

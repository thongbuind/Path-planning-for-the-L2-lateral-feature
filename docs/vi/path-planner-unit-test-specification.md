# Unit Test Specification

| Mục | Nội dung |
|---|---|
| Mã tài liệu | `PP-UTS` |
| Phiên bản | 1.2 |
| Trạng thái | BL1 |
| Tác giả | thongbui |
| Người review | thongbui |
| Cập nhật | 2026-11-23 |

## 1. Purpose and scope {#uts-scope}

- **Mục đích:** Quy định các ca kiểm unit (SWU) và kiểm tích hợp unit (SWU integration) của hai path planner, mỗi ca truy về thiết kế mà nó kiểm.
- **Phạm vi:** Unit test C trong `tests/planner/c/`, chạy bằng `ctest` trên thư viện build từ `planner/`. Các unit T1 đến T12 của Software Detailed Design và hàm số học chung.
- **Ngoài phạm vi:** Kiểm chứng cả SWC qua interface (Software Qualification Test Specification). Kiểm hợp đồng SIL bằng Python (`tests/planner/test_sil_contract.py`). Simulator và bên chấm.

## 2. References {#uts-references}

| Tài liệu | Dùng cho |
|---|---|
| [Software Detailed Design](report.html?doc=path-planner-software-detailed-design&lang=vi) | Thuật toán và interface của từng unit (mục 3.1) |
| [Software Requirements Specification](report.html?doc=path-planner-software-requirements-specification&lang=vi) | Requirement mà một ca kiểm trực tiếp |
| [Software Qualification Test Specification](report.html?doc=path-planner-software-qualification-test-specification&lang=vi) | Kiểm chứng SWC hộp đen |
| `tests/planner/c/pp_test.h` | Macro kiểm `PP_CHECK`, `PP_CHECK_NEAR` |

## 3. Test principles {#uts-principles}

- **Được biết bên trong.** Unit test gọi hàm nội bộ và đọc trạng thái nội bộ. Kết quả không tính vào benchmark (Software Qualification Test Specification mục 3).
- **Dạng ca.** Given input, trạng thái và calibration; When gọi hàm của unit; Then output hoặc trạng thái mong đợi, với dung sai ghi trong `PP_CHECK_NEAR`.
- **Loại ca.** N danh định; B biên; I input sai; S chuyển trạng thái; F lỗi và hồi phục; Num độ chính xác số học, giới hạn float32 và tính tất định.
- **Calibration.** Dùng bộ calibration giao (`calibration.yaml`) trừ khi ca ghi khác. Đổi một calibration parameter thì ca nào phụ thuộc giá trị phải được xem lại.
- **Đạt.** Mọi phép kiểm trong file đạt (`PP_TEST_RESULT` trả 0). CI chạy toàn bộ mỗi lần push.
- **Viết trước hoặc song song code.** Unit mới hoặc thay đổi thiết kế của unit thì thêm ca vào tài liệu này cùng lúc với code.

## 4. Test environment {#uts-environment}

| Mục | Nội dung |
|---|---|
| Build | `cmake -S planner -B build/planner`, `PP_BUILD_TESTS=ON` (mặc định). Ca của T7 contract và `test_lcc_step` chạy cho từng giá trị `PP_T7` |
| Chạy | `ctest --test-dir build/planner --output-on-failure` |
| Trình biên dịch | C11, cờ cảnh báo của `planner/CMakeLists.txt` (`-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow`) |
| Trạng thái của planner | Vùng nhớ do test cấp, như bên gọi thật |

## 5. Ca kiểm unit {#uts-cases}

### 5.1 T1 Latency compensation và kiểm input {#uts-t1}

| ID | Test | Loại | Given → When → Then | Truy vết |
|---|---|---|---|---|
| UT-T1-01 | `test_input_check: first_message_is_accepted_when_valid` | N | Message đầu, valid → kiểm nhận → được dùng | T1; PP-SWR-129 |
| UT-T1-02 | `test_input_check: same_delivery_is_not_new` | B | Cùng một lần giao → kiểm lại → không coi là message mới | T1 |
| UT-T1-03 | `test_input_check: steps_within_the_limit_are_accepted` | B | Counter tăng không quá MaxDeltaCounter → nhận | T1; PP-SWR-129 |
| UT-T1-04 | `test_input_check: counter_wraps` | B | Counter quay vòng 255 → 0 → nhận như tăng 1 | T1; PP-SWR-129 |
| UT-T1-05 | `test_input_check: repeated_or_stuck_counter_is_lost` | I | Counter lặp hoặc đứng yên → coi như mất message | T1; PP-SWR-130 |
| UT-T1-06 | `test_input_check: wrong_sequence_is_lost_then_resynchronised` | F | Counter nhảy quá giới hạn → mất, rồi đồng bộ lại ở message sau | T1; PP-SWR-130 |
| UT-T1-07 | `test_input_check: invalid_message_keeps_the_sequence` | I | Message `valid = false` → bỏ như mất, vẫn theo dõi counter | T1; PP-SWR-130 |
| UT-T1-08 | `test_input_check: resync_after_timeout` | F | Mất quá timeout → message đầu sau đó được nhận lại | T1 |
| UT-T1-09 | `test_latency: no_motion_keeps_line` | N | Ego-motion bằng 0 → dời lane model → vạch không đổi | T1 |
| UT-T1-10 | `test_latency: translation` | N | Xe tiến một đoạn → vạch dời đúng đoạn đó | T1 |
| UT-T1-11 | `test_latency: rotation` | N | Xe quay một góc → vạch quay ngược góc đó | T1 |
| UT-T1-12 | `test_latency: short_view_range_is_dropped` | B | Tầm nhìn còn lại sau khi dời quá ngắn → bỏ vạch | T1 |
| UT-T1-13 | `test_latency: repeated_move_keeps_the_view_range` | Num | Dời nhiều lần liên tiếp → tầm nhìn không co thêm do làm tròn | T1 |
| UT-T1-14 | `test_latency: move_under_three_metres_fails` | B | Đoạn vạch còn dưới 3 m → dời báo không thành | T1 |

### 5.2 T2 Reference line và T3 Reference shaping {#uts-t2}

| ID | Test | Loại | Given → When → Then | Truy vết |
|---|---|---|---|---|
| UT-T2-01 | `centre_between_lines` | N | L1, R1 đủ tin → tâm làn ở giữa, bề rộng bằng khoảng cách hai vạch | T2 |
| UT-T2-02 | `one_line_uses_remembered_width` | S | Chỉ còn một vạch → tâm lấy từ vạch đó và bề rộng nhớ | T2 |
| UT-T2-03 | `no_trusted_line` | I | Không vạch nào đủ tin → không có reference line từ vạch làn mình | T2 |
| UT-T2-04 | `width_memory_filters_and_rejects` | F | Bề rộng đo nhiễu hoặc ngoài dải → bộ nhớ lọc, bỏ giá trị ngoài dải | T2 |
| UT-T2-05 | `lane_too_narrow` | B | Khoảng trống mỗi bên dưới `free_space_min` → `lane_too_narrow = true` | T2; PP-SWR-063 |
| UT-T2-06 | `walk_straight_and_arc_continuation` | N | Đi dọc reference line quá cuối tầm nhìn → nối cung tròn liên tục | T2 |
| UT-T2-07 | `walk_curve` | Num | Đi dọc đường cong → vị trí và hướng khớp đa thức | T2 |
| UT-T2-08 | `sampled_walk_matches_cubic` | Num | Mảng mẫu và đa thức cùng hình học → đi dọc cho cùng kết quả | T2; PP-TS-005 |
| UT-T2-09 | `sampled_project_matches_cubic` | Num | Chiếu điểm lên mảng mẫu và lên đa thức → cùng kết quả | T2; PP-TS-005 |
| UT-T2-10 | `sampled_line_without_range_ahead` | B | Mảng mẫu không có phần phía trước xe → xử lý không lỗi | T2 |
| UT-T2-11 | `wrong_slots_need_two_matching_markings` | I | Vạch nằm sai ô L1, R1 → chỉ sửa khi hai vạch cùng khớp | T2 |
| UT-T2-12 | `crossed_marking_changes_slot` | S | Xe qua vạch → vạch đổi ô đúng phía | T2 |
| UT-T2-13 | `inferred_centre_uses_remembered_offsets` | S | Mất L1, R1, còn biên khác → tâm suy ra từ khoảng cách đã nhớ | T2; PP-SWR-147 |
| UT-T2-14 | `rejected_ego_line_coasts_before_inference` | F | Vạch làn mình bị loại vì không nhất quán → COAST trước khi suy tâm | T2; PP-SWR-124 |
| UT-T2-15 | `inference_needs_a_known_boundary` | I | Không có biên nào đã nhớ khoảng cách → không suy tâm | T2; PP-SWR-148 |
| UT-T2-16 | `jump_of_one_line_is_rejected` | F | Một vạch nhảy c0 quá `k_jump`·σ → bị loại | T2; PP-SWR-121 |
| UT-T2-17 | `shape_jump_is_rejected_without_a_c0_jump` | F | Hình dạng đổi quá ngưỡng, c0 không đổi → bị loại | T2; PP-SWR-125 |
| UT-T2-18 | `jump_of_both_lines_coasts_then_is_accepted` | S | Cả hai vạch nhảy → COAST, nhận sau `T_confirm` | T2; PP-SWR-122 |
| UT-T2-19 | `flickering_jump_is_never_accepted` | F | Vạch nhảy qua lại → không bao giờ được nhận | T2 |
| UT-T2-20 | `return_after_a_change_is_taken_at_once` | S | Vạch về vị trí cũ sau khi đổi → nhận ngay | T2 |
| UT-T2-21 | `shape_change_cannot_slip_in_while_the_memory_ages` | F | Hình dạng đổi dần trong lúc bộ nhớ cũ đi → không lọt qua kiểm | T2 |
| UT-T2-22 | `noisy_frame_does_not_hold_back_the_next_one` | F | Một frame nhiễu → frame tốt sau đó vẫn được nhận | T2 |
| UT-T2-23 | `slow_drift_within_the_check_is_taken` | B | Vạch trôi chậm trong ngưỡng kiểm → được nhận | T2 |
| UT-T2-24 | `coast_ends_after_t_coast` | B | COAST kéo dài → hết `T_coast` thì không còn reference line | T2; PP-SWR-124 |
| UT-T2-25 | `return_after_a_long_fault_is_taken_at_once` | F | Vạch trở lại sau lỗi dài → nhận ngay | T2 |
| UT-T2-26 | `old_position_ends_when_its_range_is_behind_the_car` | B | Vị trí cũ của vạch đã ra sau xe → bỏ bộ nhớ đó | T2 |
| UT-T2-27 | `width_outside_the_odd_keeps_the_stable_line` | I | Bề rộng đo ngoài 2,5–5,5 m → giữ vạch ổn định hơn | T2; ODD |

Tất cả trong `test_reference_line`. T3 (giới hạn `ref_rate`) chưa có ca riêng; xem mục 7.

### 5.3 T4 Stitching và continuity {#uts-t4}

| ID | Test | Loại | Given → When → Then | Truy vết |
|---|---|---|---|---|
| UT-T4-01 | `move_old` | N | Path cũ và ego-motion → dời sang `base_link` mới → điểm đúng vị trí | T4 |
| UT-T4-02 | `sample_on_curve_stays_on_the_arc` | Num | Path cũ trên cung tròn → lấy mẫu sau khi dời → vẫn nằm trên cung | T4 |
| UT-T4-03 | `old_path_not_usable` | I | Path cũ không dùng được → không trộn, λ = 1 | T4 |
| UT-T4-04 | `start_from_old_path_or_reset` | B | Xe lệch path cũ dưới và trên `stitch_reset` → điểm đầu lấy từ path cũ hoặc từ xe | T4; PP-SWR-100 |
| UT-T4-05 | `start_curvature_gives_lateral_acceleration` | N | Độ cong điểm đầu → d̈ đầu bằng v²·κ | T4 |
| UT-T4-06 | `blend_limits_the_jump` | B | Path mới lệch path cũ → trộn giữ bước nhảy trong ngưỡng | T4; PP-SWR-100 |
| UT-T4-07 | `blend_limit_of_a_far_change` | B | Đổi ở phần xa → giữ ngưỡng của đoạn sau 2 s | T4; PP-SWR-100 |
| UT-T4-08 | `blend_ignores_change_beyond_view` | B | Đổi ở phần ngoài tầm nhìn → không tính vào giới hạn trộn | T4; PP-SWR-100 |
| UT-T4-09 | `soft_weight` | Num | Lệch giữa `stitch_soft_min` và `stitch_reset` → trọng số trộn mềm đúng công thức | T4 |
| UT-T4-10 | `soft_start_blends_every_component` | N | Điểm đầu mềm → trộn đủ d, ḋ, d̈ | T4 |

### 5.4 T5 Curvature fusion {#uts-t5}

| ID | Test | Loại | Given → When → Then | Truy vết |
|---|---|---|---|---|
| UT-T5-01 | `first_measurement_initialises` | S | Chưa có prior → phép đo đầu khởi tạo κ và phương sai | T5 |
| UT-T5-02 | `outlier_gets_a_tenth_of_the_weight` | F | Phép đo lệch quá `k_jump`·σ → trọng số giảm 10 lần | T5; PP-SWR-125 |
| UT-T5-03 | `predict_shifts_by_distance` | N | Xe đi Δs → lưới κ dời đúng Δs, phương sai tăng | T5 |
| UT-T5-04 | `fit_recovers_line` | Num | κ tuyến tính theo s → khớp lại đúng a, b | T5 |
| UT-T5-05 | `yaw_rate_only_above_5_mps` | B | Tốc độ dưới 5 m/s → không dùng yaw rate | T5 |

### 5.5 T6 Lateral state và T11 Output {#uts-t6}

| ID | Test | Loại | Given → When → Then | Truy vết |
|---|---|---|---|---|
| UT-T6-01 | `test_output: lateral_state_offset_and_heading` | N | Xe lệch và lệch góc so với tâm làn → d0 và góc lệch đúng dấu, đúng độ lớn | T6 |
| UT-T11-01 | `test_output: speed_profile_constant_and_shifted` | N | LongitudinalPlan hằng và dời thời gian → v(t) của 31 điểm đúng | T11 |
| UT-T11-02 | `test_output: points_on_straight_centre` | N | Path trên tâm đường thẳng → 31 điểm trên trục x, bước 0,1 s | T11 |
| UT-T11-03 | `test_output: points_follow_curve_with_offset` | N | Path dời tâm trên cua → điểm theo cua, lệch đúng độ dời | T11 |
| UT-T11-04 | `test_output: output_rejects_position_outside_float32` | Num | Vị trí vượt dải float32 → không gửi path hợp lệ | T11 |
| UT-T11-05 | `test_version: version_names_build` | N | Đọc chuỗi phiên bản → có commit và mã bộ calibration | T11; R79 Annex 6, 3.3.5 |

### 5.6 T7 Path generation {#uts-t7}

| ID | Test | Loại | Given → When → Then | Truy vết |
|---|---|---|---|---|
| UT-T7-01 | `test_quintic: boundary_conditions` | Num | Điều kiện đầu và cuối → quintic thoả d, ḋ, d̈ ở hai đầu | T7 |
| UT-T7-02 | `test_quintic: holds_after_duration` | B | Thời gian vượt T → giữ giá trị cuối | T7 |
| UT-T7-03 | `test_quintic: rejects_zero_duration` | I | T = 0 → từ chối | T7 |
| UT-T7-04 | `test_quintic: grid` | N | Lấy mẫu trên lưới 0,1 s → đúng 31 điểm | T7 |
| UT-T7-05 | `test_qp: recentre_without_overshoot` | N | Xe lệch tâm → QP đưa về không vượt qua tâm | T7 C; target PP-SWR-053 |
| UT-T7-06 | `test_qp: curve_at_limit_keeps_the_hard_limit` | B | Cua cần đúng giới hạn → a_y của path không vượt giới hạn cứng | T7 C; PP-SWR-001 |
| UT-T7-07 | `test_qp: curve_beyond_limit_assists_at_the_limit` | B | Cua cần vượt giới hạn → path ở mức giới hạn, không thấp hơn nhiều | T7 C; PP-SWR-006 |
| UT-T7-08 | `test_qp: continuity_with_old_path` | N | Có path cũ → path QP liên tục với path cũ | T7 C; PP-SWR-100 |
| UT-T7-09 | `test_qp: deterministic` | Num | Cùng input hai lần → cùng output từng bit | T7 C |
| UT-T7-10 | `test_intervention: measured_edge_needs_association_with_ego_lane` | I | Mép đường đo được nhưng không gắn với làn mình → không dùng cho ELK | T7 |
| UT-T7-11 | `test_intervention: profile_advances_from_original_start_time` | N | Path can thiệp qua nhiều chu kỳ → tính từ thời điểm bắt đầu gốc | T7 |
| UT-T7-12 | `test_intervention: chosen_candidate_is_not_cut_by_t10` | N | Path can thiệp chọn trong giới hạn → T10 không phải cắt | T7, T10; PP-SWR-110 đến 115 |
| UT-T7-13 | `test_intervention: outward_start_is_arrested_then_returns_slowly` | S | Xe đang trôi ra → pha chặn đà rồi về tâm trong `T_return` | T7; PP-TS-026 V4; PP-SWR-094 |
| UT-T7-14 | `test_t7_contract: path_starts_at_start_and_moves_to_target` | N | Đường thẳng, xe lệch 0,3 m → điểm 0 tại xe, điểm cuối gần mục tiêu hơn, x tăng dần, giá trị hữu hạn | T7 contract |
| UT-T7-15 | `test_t7_contract: on_target_stays_on_target` | B | Xe đã ở offset mục tiêu → path giữ offset trong 1 mm | T7 contract |
| UT-T7-16 | `test_t7_contract: reset_makes_output_depend_on_input_only` | S | Sau `pp_t7_reset`, kể cả trên vùng nhớ rác → cùng input cho path giống từng bit | T7 contract |
| UT-T7-17 | `test_t7_contract: non_finite_start_fails_and_recovers` | F | Trạng thái đầu NaN → không có path; chu kỳ sau cho path như sau reset | T7 contract |

### 5.7 T8 Offset {#uts-t8}

| ID | Test | Loại | Given → When → Then | Truy vết |
|---|---|---|---|---|
| UT-T8-01 | `truck_centred_in_right_lane_moves_left` | N | Xe lớn giữa làn phải → dời tâm sang trái | T8; PP-SWR-055 |
| UT-T8-02 | `truck_on_the_left_moves_right_by_offset_truck_even_when_very_close` | B | Xe lớn bên trái rất gần → dời sang phải đúng `offset_truck` | T8; PP-SWR-055 |
| UT-T8-03 | `narrow_lane_limits_the_offset` | B | Làn hẹp → độ dời bị chặn theo khoảng trống trừ `dlc_offset_min` | T8 |
| UT-T8-04 | `vehicle_on_the_other_side_blocks_the_offset` | S | Có xe tới ở làn bên kia → không dời | T8; PP-SWR-065 |
| UT-T8-05 | `far_truck_no_offset` | B | Xe lớn còn xa → không dời | T8 |
| UT-T8-06 | `trucks_both_sides_balance` | N | Xe lớn hai bên → giữ cách cân bằng | T8 |
| UT-T8-07 | `rate_limit_and_return_without_object_list` | F | Mất ObjectList → độ dời về 0 có giới hạn tốc độ | T8; PP-SWR-140 |
| UT-T8-08 | `ghost_sized_object_ignored` | I | Vật thể có kích thước không hợp lý → bỏ qua | T8 |

### 5.8 T9 Intervention selection {#uts-t9}

| ID | Test | Loại | Given → When → Then | Truy vết |
|---|---|---|---|---|
| UT-T9-01 | `test_selection: completion_waits_and_belongs_to_its_function` | S | Điều kiện kết thúc giữ đủ → COMPLETED đúng chức năng, sau `T_end_hold` | T9; PP-SWR-032, 090 |
| UT-T9-02 | `test_selection: late_request_needs_a_new_one_and_long_ones_go_on` | S | Yêu cầu tới sau COMPLETED → cần yêu cầu mới; yêu cầu dài tiếp tục | T9; PP-SWR-034, 035 |
| UT-T9-03 | `test_selection: invalid_path_blocks_current_request` | F | Path không hợp lệ → chặn yêu cầu đang có | T9; PP-SWR-030 |
| UT-T9-04 | `test_intervention: aligns_vehicle_state_with_completion_tick` | Num | VehicleStateEstimate cũ hơn t0 → ngoại suy về đúng tick | T9; PP-TS-012 |
| UT-T9-05 | `test_intervention: end_condition_needs_the_car_near_the_centre` | B | Xe còn xa tâm hơn `d_end` → chưa kết thúc | T9; PP-SWR-084 |
| UT-T9-06 | `test_intervention: corridor_holds_a_jump_away_and_takes_one_toward_the_car` | F | Biên nhảy ra xa → giữ hành lang; nhảy vào phía xe → nhận | T9; PP-SWR-093 |

### 5.9 T10 Feasibility và giới hạn {#uts-t10}

| ID | Test | Loại | Given → When → Then | Truy vết |
|---|---|---|---|---|
| UT-T10-01 | `check` | N | Path đã biết → a_y, a_y thêm vào, jerk, góc bánh tính đúng | T10 |
| UT-T10-02 | `curve_support` | B | Cua cần vượt aysmax → path vẫn ≥ aysmax − `epsilon_ay` | T10; PP-SWR-006 |
| UT-T10-03 | `cut_to_aysmax_and_integrate_again` | B | Path vượt giới hạn → cắt κ rồi tích phân lại d(t) | T10; PP-SWR-001 |
| UT-T10-04 | `hwa_path_ceiling_follows_margin` | B | `ay_margin_hwa` và cờ giới hạn → trần LCC bằng aysmax + margin, hoặc aysmax khi cờ bật | T10; PP-SWR-001; PP-TS-020 |
| UT-T10-05 | `point0_curvature_is_cut_too` | B | Điểm 0 vượt giới hạn → cũng bị cắt, giữ vị trí | T10 |
| UT-T10-06 | `jerk_is_limited` | B | Jerk vượt giới hạn → bị cắt | T10; PP-SWR-003 |
| UT-T10-07 | `jerk_stays_below_limit_after_float32` | Num | Sau khi đổi sang float32 → jerk vẫn dưới giới hạn | T10; PP-SWR-003 |
| UT-T10-08 | `steering_wheel_rate_is_limited` | B | Tốc độ quay vô lăng vượt VehicleConfig → bị cắt | T10; PP-SWR-117 |
| UT-T10-09 | `path_within_limits_is_untouched` | N | Path trong giới hạn → không đổi | T10 |
| UT-T10-10 | `flag_hysteresis_and_confirmation` | S | a_y cần quanh ngưỡng → cờ bật, tắt theo `delta_ay` và `T_flag` | T10; PP-SWR-007; target 008, 064 |
| UT-T10-11 | `curve_limit` | N | Cua trong tầm nhìn → `v_max` và `distance` của LateralLimits đúng | T10; PP-SWR-151 |
| UT-T10-12 | `ay_need_max_within_view` | B | Phần path ngoài tầm nhìn → không tính vào a_y cần | T10 |

Tất cả trong `test_feasibility`.

### 5.10 T12 Bám xe trước {#uts-t12}

| ID | Test | Loại | Given → When → Then | Truy vết |
|---|---|---|---|---|
| UT-T12-01 | `all_conditions_met_follows_the_lead` | N | Mất vạch, xe trước đủ điều kiện → FOLLOW | T12; PP-SWR-170 |
| UT-T12-02 | `each_entry_condition_blocks` | B | Thiếu từng điều kiện vào → không FOLLOW | T12; PP-SWR-171 |
| UT-T12-03 | `no_follow_without_original_centre_or_trail` | I | Không có tâm làn gốc hoặc vết xe trước → không FOLLOW | T12 |
| UT-T12-04 | `keep_conditions_while_following` | S | Đang FOLLOW, điều kiện duy trì sai → rời FOLLOW | T12; PP-SWR-172 |
| UT-T12-05 | `trail_survives_bad_frames_and_follows_the_acc_target` | F | Vài frame LeadTarget xấu → vết vẫn giữ, theo đúng mục tiêu ACC | T12 |
| UT-T12-06 | `path_within_the_limit_of_the_original_centre` | B | Vết xe trước lệch xa → path giữ trong giới hạn so với tâm làn gốc | T12; PP-ASM-026 |

### 5.11 Hàm số học chung {#uts-math}

| ID | Test | Loại | Given → When → Then | Truy vết |
|---|---|---|---|---|
| UT-M-01 | `fit_recovers_exact_cubic` | Num | Mẫu của một đa thức bậc 3 → khớp lại đúng hệ số | `pp_math.c` |
| UT-M-02 | `fit_needs_four_samples` | I | Dưới bốn mẫu → báo không khớp được | `pp_math.c` |
| UT-M-03 | `solve4_singular` | I | Hệ 4×4 suy biến → báo lỗi, không chia cho 0 | `pp_math.c` |
| UT-M-04 | `derivatives` | Num | Đạo hàm bậc 1, 2 của đa thức → đúng giá trị | `pp_math.c` |

## 6. Ca kiểm tích hợp unit {#uts-integration}

Gọi `pp_lcc_step` hoặc `pp_lkaelk_step` với input dựng tay, kiểm output qua interface.

| ID | Test | Loại | Given → When → Then | Truy vết |
|---|---|---|---|---|
| IT-L-01 | `test_lcc_step: lcc_path_from_car_to_centre` | N | LCC REQUEST, xe lệch tâm → path từ xe về tâm | T1–T11; PP-SWR-052 |
| IT-L-02 | `test_lcc_step: no_lane_model_means_no_path` | I | Chưa có lane model → `path_valid = false` | PP-SWR-043 |
| IT-L-03 | `test_lcc_step: stale_lane_model` | F | Lane model quá tuổi → không có path | PP-SWR-124 |
| IT-L-04 | `test_lcc_step: lcc_not_requested` | S | LCC không ở REQUEST → `lcc_mode = NONE` | T9 |
| IT-L-05 | `test_lcc_step: chassis_fault_invalidates_lcc_and_fresh_inputs_restore_it` | F | Chassis không hợp lệ → hủy path; input tốt trở lại → có path | PP-SWR-142 |
| IT-L-06 | `test_lcc_step: function_requests_timeout_and_recovery` | F | FunctionRequests quá timeout → coi như tắt; có lại → chạy lại | PP-SWR-145 |
| IT-L-07 | `test_lcc_step: longitudinal_plan_range` | I | LongitudinalPlan ngoài dải → không dùng | PP-SWR-156 |
| IT-L-08 | `test_lcc_step: driver_override_path_starts_at_car` | S | Tài xế ghi đè → path bắt đầu từ xe | PP-SWR-039 |
| IT-L-09 | `test_lcc_step: lka_request_makes_the_lcc_path_start_at_the_car` | S | LKA được yêu cầu → path LCC bắt đầu từ xe | PP-SWR-040 |
| IT-L-10 | `test_lcc_step: lcc_mode_follows_the_state_of_the_lane` | S | Trạng thái vạch đổi → `lcc_mode` LANE, INFERRED, COAST đúng | PP-SWR-177 |
| IT-L-11 | `test_lcc_step: follow_the_lead_when_both_lines_are_lost` | S | Mất hai vạch, có xe trước → FOLLOW | PP-SWR-170 |
| IT-L-12 | `test_lcc_step: no_follow_when_a_condition_fails` | B | Một điều kiện bám xe sai → không FOLLOW | PP-SWR-171 |
| IT-K-01 | `test_lkaelk_step: no_lane_model_means_no_path` | I | Chưa có lane model → không có path can thiệp | PP-SWR-043 |
| IT-K-02 | `test_lkaelk_step: stale_lane_model` | F | Lane model quá tuổi → không có path | PP-SWR-124 |
| IT-K-03 | `test_lkaelk_step: no_request_sends_an_invalid_trajectory` | S | Không có yêu cầu → Trajectory `valid = false` | PP-SWR-043 |
| IT-K-04 | `test_lkaelk_step: chassis_fault_blocks_a_request_until_it_is_made_again` | F | Chassis lỗi giữa lần can thiệp → chặn tới khi có yêu cầu mới | PP-SWR-142 |
| IT-K-05 | `test_lkaelk_step: function_requests_timeout_invalidates_the_path` | F | FunctionRequests quá timeout → hủy path | PP-SWR-145 |
| IT-K-06 | `test_lkaelk_step: interventions_can_switch_and_cancel_in_one_cycle` | S | Đổi LKA sang ELK hoặc hủy → đổi trong một chu kỳ | PP-SWR-030, 036 |
| IT-K-07 | `test_lkaelk_step: active_lka_can_coast_on_last_ego_reference` | F | Mất vạch lúc LKA ACTIVE → COAST trên reference line cuối | PP-SWR-124 |
| IT-K-08 | `test_lkaelk_step: elk_road_edge_keeps_path_on_cancellation_tick` | B | ELK mép đường bị hủy → chu kỳ hủy vẫn có path | PP-SWR-036 |

## 7. Độ phủ và việc còn thiếu {#uts-coverage}

| Unit | Số ca | Loại đã có | Thiếu |
|---|---|---|---|
| T1 | 14 | N, B, I, F, Num | — |
| T2 | 27 | Đủ sáu loại | — |
| T3 | 0 | — | Ca riêng cho giới hạn `ref_rate`, cả khi bộ nhớ quay vì bias yaw (PP-TS-028) |
| T4 | 10 | N, B, I, Num | Ca F khi ego-motion không hợp lệ |
| T5 | 5 | N, B, S, F, Num | — |
| T6 | 1 | N | Ca B khi xe gần vạch; v_lat khi xe trôi |
| T7 | 17 | Đủ sáu loại | — |
| T8 | 8 | N, B, I, S, F | — |
| T9 | 6 | B, S, F, Num | Ca N cho một lần LKA trọn vẹn |
| T10 | 12 | N, B, S, Num | Ca I cho VehicleConfig biên |
| T11 | 5 | N, Num | Ca counter quay vòng của output |
| T12 | 6 | N, B, I, S, F | — |

- Code coverage, 2026-11-23, commit 54307f1, chỉ từ unit test và tích hợp unit (source-based coverage của clang, `llvm-cov`). Không đặt ngưỡng phần trăm; nhánh chưa chạy là danh sách việc cho ca mới.

| File | Line | Branch |
|---|---|---|
| `curvature.c` | 83/83 (100 %) | 30/38 (79,0 %) |
| `feasibility.c` | 160/163 (98,2 %) | 59/66 (89,4 %) |
| `follow.c` | 210/217 (96,8 %) | 132/162 (81,5 %) |
| `generators/qp.c` | 292/294 (99,3 %) | 122/140 (87,1 %) |
| `generators/quintic.c` | 45/45 (100 %) | 9/10 (90,0 %) |
| `input_check.c` | 23/25 (92,0 %) | 32/34 (94,1 %) |
| `intervention.c` | 282/295 (95,6 %) | 139/182 (76,4 %) |
| `latency.c` | 85/86 (98,8 %) | 32/38 (84,2 %) |
| `lateral_state.c` | 10/10 (100 %) | 1/2 (50,0 %) |
| `offset.c` | 98/108 (90,7 %) | 57/78 (73,1 %) |
| `output.c` | 81/81 (100 %) | 19/20 (95,0 %) |
| `pp_core.c` | 318/329 (96,7 %) | 162/226 (71,7 %) |
| `pp_lcc.c` | 238/278 (85,6 %) | 122/178 (68,5 %) |
| `pp_lkaelk.c` | 178/188 (94,7 %) | 123/142 (86,6 %) |
| `pp_math.c` | 107/109 (98,2 %) | 44/46 (95,7 %) |
| `reference_line.c` | 573/584 (98,1 %) | 237/270 (87,8 %) |
| `selection.c` | 85/87 (97,7 %) | 63/70 (90,0 %) |
| `stitching.c` | 175/177 (98,9 %) | 50/56 (89,3 %) |
| Tổng | 3582/3698 (96,9 %) | 1834/2502 (73,3 %) |

- Đo lại: build `planner/` với `CMAKE_C_FLAGS="-fprofile-instr-generate -fcoverage-mapping"`, chạy `ctest` với `LLVM_PROFILE_FILE`, gộp bằng `llvm-profdata merge`, báo cáo bằng `llvm-cov report`.
- Static analysis, 2026-11-23, `clang --analyze` (Apple clang) trên 18 file của `planner/src/`, commit 54307f1: 2 cảnh báo `core.NullDereference`.

| Vị trí | Đường analyzer báo | Đánh giá | Xử lý |
|---|---|---|---|
| `pp_core.c:277` (T5) | `in->lane_model` NULL nhưng `lane_ok` được giả định true | Không xảy ra lúc chạy: `lane_ok` chỉ true khi `lane_model` khác NULL; analyzer mất dấu khi con trỏ tới trường của frame được truyền cho T2 | Thêm kiểm tra phòng vệ |
| `pp_lkaelk.c:86` (T7) | `in->function_requests` NULL khi bắt đầu can thiệp | Không xảy ra lúc chạy: can thiệp chỉ bắt đầu khi có FunctionRequests dùng được | Thêm kiểm tra phòng vệ |

- Kiểm MISRA C:2012, 2026-11-23, cppcheck 2.22 addon `misra.py` (không có bản text của luật), 18 file `planner/src/`, commit 54307f1: 334 lần báo trên 13 luật.

| Luật | Loại | Số lần | Đánh giá |
|---|---|---|---|
| 7.3 | Required | 202 | Báo nhầm: các dòng bị báo là khai báo `const pp_calibration_t *cal`, không có hằng số hậu tố `l` |
| 10.8 | Required | 57 | Thật: ép kiểu biểu thức ghép sang kiểu khác, nhiều nhất ở `generators/qp.c`; sửa bằng ép từng toán hạng |
| 15.5 | Advisory | 40 | Hàm có nhiều `return`; giữ, ghi deviation |
| 12.1 | Advisory | 17 | Thiếu ngoặc làm rõ thứ tự toán tử; sửa |
| 9.3 | Required | 3 | Mảng khởi tạo một phần (`curvature.c`, `intervention.c`, `reference_line.c`); sửa |
| 8.9 | Advisory | 3 | Biến file chỉ dùng trong một hàm; sửa |
| 11.5 | Advisory | 3 | Ép `void *` sang con trỏ đối tượng ở vùng nhớ do bên gọi cấp; deviation theo PP-ADR-013 |
| 1.4 | Required | 2 | `_Static_assert`, `_Alignof` của C11; deviation theo PP-ADR-013 (chọn C11) |
| 11.3 | Required | 2 | Ép con trỏ vùng nhớ trạng thái sang kiểu state; deviation, kiểm căn lề bằng `_Static_assert` và lúc init |
| 15.7 | Required | 2 | Thiếu `else` cuối chuỗi `else if` (`feasibility.c`, `reference_line.c`); sửa |
| 10.7 | Required | 1 | `pp_core.c:71`, phép `%` trên biểu thức ghép; sửa |
| 11.6 | Required | 1 | `pp_core.c:35`, ép con trỏ sang `uintptr_t` để kiểm căn lề; deviation |
| 14.1 | Required | 1 | Báo nhầm: biến đếm của vòng lặp là `uint32_t`, `double` chỉ tính trong thân |

- Cách chạy: `cppcheck --dump` từng file, rồi `python3 misra.py *.dump`. Trên máy này `--addon=misra` không in kết quả.
- Requirement được ghi ở cột Truy vết chỉ để định hướng. Kết luận đạt về requirement là của Software Qualification Test Specification.

## Revision history {#revision-history}

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 2026-11-23 | Bản đầu: nguyên tắc, môi trường, 111 ca unit và 20 ca tích hợp unit truy về Software Detailed Design, bảng độ phủ theo unit |
| 1.1 | 2026-11-23 | Mục 7: kết quả static analysis bằng clang analyzer và code coverage theo file, kiểm MISRA C:2012 bằng cppcheck |
| 1.2 | 2026-11-23 | Mục 4, 5.6: bốn ca của T7 contract (UT-T7-14 đến 17), chạy cho từng generator. Lý do: PP-TS-031 GĐ 1 |

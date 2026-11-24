# Study PP-TS-031

Plan: `research/studies/PP-TS-031-t7-generator-campaign/plan.yaml`, locked 2026-11-24; suite PP-T7.

Bảng dưới dùng để dò nhanh. Đối chiếu B0, lỗi, điều kiện áp dụng và số đo ghép cặp trong `results.json` trước khi xếp hạng theo đề cương.

## test

| Bộ | Trượt | PP-SWR-050 | PP-SWR-125 | PP-SWR-002 | PP-SWR-053 | PP-SWR-003 |
|---|---|---|---|---|---|---|
| qp_jerk_admm_it1000_ref | 2 | 0.9163 | — | — | — | 4.801 |
| qp_jerk_admm_mlp_weights | 6 | 2.008 | 0.07079 | 0.5576 | 2.166 | 4.801 |
| qp_jerk_admm-qp_w_dev0.15-qp_w_comfort5.0 | 6 | 2.012 | 0.06708 | 0.5516 | 2.186 | 4.801 |
| qp_jerk_admm-qp_w_dev0.15-qp_w_comfort10.0 | 6 | 2.07 | 0.06794 | 0.5516 | 2.186 | 4.801 |
| qp_jerk_admm-qp_w_dev0.15-qp_w_comfort2.5 | 6 | 2.084 | 0.06567 | 0.5516 | 2.186 | 4.801 |
| qp_jerk_admm_it075 | 7 | 2.007 | 0.06664 | 0.5659 | 2.156 | 4.797 |
| qp_jerk_admm | 7 | 2.008 | 0.06659 | 0.573 | 2.136 | 4.801 |
| qp_jerk_admm_mlp_weights-mlpw_regularisation0.01 | 7 | 2.008 | 0.068 | 0.5542 | 2.166 | 4.801 |
| qp_jerk_admm_mlp_weights-mlpw_regularisation0.0001 | 7 | 2.008 | 0.06872 | 0.4968 | 2.306 | 4.801 |
| qp_jerk_admm_it100 | 7 | 2.008 | 0.06662 | 0.5685 | 2.146 | 4.801 |
| qp_jerk_admm_shift_warmstart_it050 | 7 | 2.008 | 0.06672 | 0.5611 | 2.166 | 4.804 |
| qp_jerk_admm_mlp_warmstart_it050 | 7 | 2.008 | 0.06716 | 0.5629 | 2.166 | 4.803 |
| qp_jerk_admm_shift_warmstart_it075 | 7 | 2.009 | 0.06666 | 0.5659 | 2.156 | 4.801 |
| qp_jerk_admm_mlp_warmstart_it075 | 7 | 2.009 | 0.06666 | 0.566 | 2.156 | 4.8 |
| qp_jerk_admm_mlp_warmstart_it025 | 7 | 2.021 | 0.06698 | 0.5466 | 2.196 | 4.797 |
| qp_jerk_admm_shift_warmstart_it025 | 7 | 2.021 | 0.06706 | 0.5429 | 2.216 | 4.819 |
| qp_jerk_admm-qp_w_dev0.6-qp_w_comfort10.0 | 7 | 2.06 | 0.06651 | 0.6206 | 2.036 | 4.801 |
| qp_jerk_admm_it010 | 7 | 2.062 | 0.06477 | 0.4984 | 2.346 | 5 |
| qp_jerk_admm-qp_w_dev0.3-qp_w_comfort10.0 | 7 | 2.067 | 0.06741 | 0.573 | 2.136 | 4.801 |
| qp_jerk_admm-qp_w_dev0.6-qp_w_comfort2.5 | 7 | 2.073 | 0.06438 | 0.6206 | 2.036 | 4.801 |
| qp_jerk_admm-qp_w_dev0.3-qp_w_comfort2.5 | 7 | 2.08 | 0.0652 | 0.573 | 2.136 | 4.801 |
| qp_jerk_admm_it025 | 7 | 2.092 | 0.06672 | 0.5417 | 2.216 | 4.854 |
| qp_jerk_admm-qp_w_dev0.6-qp_w_comfort5.0 | 7 | 2.099 | 0.0657 | 0.6206 | 2.036 | 4.801 |
| qp_jerk_admm_it050 | 7 | 2.101 | 0.06663 | 0.5607 | 2.166 | 4.797 |
| qp_jerk_admm_shift_warmstart_it010 | 7 | 2.105 | 0.06924 | 0.4926 | 2.366 | 5 |
| qp_jerk_admm_mlp_warmstart_it010 | 7 | 4.946 | 0.06274 | 0.544 | 2.206 | 5 |
| quintic_duration-T_hwa2.5-T_recenter4.0 | 10 | 4.031 | 0.05316 | 0.4166 | 3.706 | 3.375 |
| quintic_duration-T_hwa2.5-T_recenter3.5 | 10 | 4.031 | 0.05316 | 0.441 | 3.096 | 3.375 |
| quintic_duration-T_hwa2.5-T_recenter3.0 | 10 | 4.031 | 0.05316 | 0.5004 | 2.586 | 3.375 |
| quintic_duration-T_hwa3.0-T_recenter4.0 | 10 | 4.153 | 0.05389 | 0.4166 | 3.706 | 3.364 |
| quintic_duration | 10 | 4.153 | 0.05389 | 0.441 | 3.096 | 3.364 |
| quintic_tangent_point | 10 | 4.153 | 0.05389 | 0.441 | 3.096 | 3.364 |
| quintic_ay_sampling | 10 | 4.153 | 0.05389 | 0.441 | 3.096 | 3.364 |
| quintic_tangent_point-qtp_center_s1.5-qtp_dlc_margin_m0.0 | 10 | 4.153 | 0.05389 | 0.441 | 3.096 | 3.364 |
| quintic_tangent_point-qtp_center_s1.5-qtp_dlc_margin_m0.01 | 10 | 4.153 | 0.05389 | 0.441 | 3.096 | 3.364 |
| quintic_tangent_point-qtp_center_s1.5-qtp_dlc_margin_m0.02 | 10 | 4.153 | 0.05389 | 0.441 | 3.096 | 3.364 |
| quintic_tangent_point-qtp_center_s1.75-qtp_dlc_margin_m0.0 | 10 | 4.153 | 0.05389 | 0.441 | 3.096 | 3.364 |
| quintic_tangent_point-qtp_center_s2.0-qtp_dlc_margin_m0.0 | 10 | 4.153 | 0.05389 | 0.441 | 3.096 | 3.364 |
| quintic_tangent_point-qtp_center_s2.0-qtp_dlc_margin_m0.01 | 10 | 4.153 | 0.05389 | 0.441 | 3.096 | 3.364 |
| quintic_ay_sampling-qas_peak_early0.35-qas_peak_late0.55-qas_amplitude_m0.1 | 10 | 4.153 | 0.05389 | 0.441 | 3.096 | 3.364 |
| quintic_ay_sampling-qas_peak_early0.35-qas_peak_late0.55-qas_amplitude_m0.2 | 10 | 4.153 | 0.05389 | 0.441 | 3.096 | 3.364 |
| quintic_ay_sampling-qas_peak_early0.35-qas_peak_late0.55-qas_amplitude_m0.3 | 10 | 4.153 | 0.05389 | 0.441 | 3.096 | 3.364 |
| quintic_ay_sampling-qas_peak_early0.4-qas_peak_late0.6-qas_amplitude_m0.1 | 10 | 4.153 | 0.05389 | 0.441 | 3.096 | 3.364 |
| quintic_ay_sampling-qas_peak_early0.4-qas_peak_late0.6-qas_amplitude_m0.3 | 10 | 4.153 | 0.05389 | 0.441 | 3.096 | 3.364 |
| quintic_ay_sampling-qas_peak_early0.45-qas_peak_late0.65-qas_amplitude_m0.1 | 10 | 4.153 | 0.05389 | 0.441 | 3.096 | 3.364 |
| quintic_ay_sampling-qas_peak_early0.45-qas_peak_late0.65-qas_amplitude_m0.2 | 10 | 4.153 | 0.05389 | 0.441 | 3.096 | 3.364 |
| quintic_ay_sampling-qas_peak_early0.45-qas_peak_late0.65-qas_amplitude_m0.3 | 10 | 4.153 | 0.05389 | 0.441 | 3.096 | 3.364 |
| quintic_duration-T_hwa3.0-T_recenter3.0 | 10 | 4.153 | 0.05389 | 0.5004 | 2.586 | 3.364 |
| quintic_tangent_point-qtp_center_s1.75-qtp_dlc_margin_m0.02 | 10 | 4.154 | 0.05396 | 0.441 | 3.096 | 3.364 |
| quintic_tangent_point-qtp_center_s2.0-qtp_dlc_margin_m0.02 | 10 | 4.154 | 0.05396 | 0.441 | 3.096 | 3.364 |
| quintic_duration-T_hwa3.5-T_recenter4.0 | 10 | 4.185 | 0.05575 | 0.3735 | 3.726 | 3.353 |
| quintic_duration-T_hwa3.5-T_recenter3.5 | 10 | 4.185 | 0.05575 | 0.4426 | 3.096 | 3.353 |
| quintic_duration-T_hwa3.5-T_recenter3.0 | 10 | 4.185 | 0.05575 | 0.502 | 2.586 | 3.353 |
| mlp_jerk_direct | 32 | 2.153 | 1.545 | 1.314 | 1.606 | 4.257 |

- qp_jerk_admm_it1000_ref: QP jerk, ADMM 1000 vòng, nghiệm tham chiếu; chỉ vòng hở, không xếp hạng
- qp_jerk_admm_mlp_weights: QP jerk, MLP chọn trọng số, 150 vòng
- qp_jerk_admm-qp_w_dev0.15-qp_w_comfort5.0: QP jerk, ADMM 150 vòng; lưới qp_w_dev0.15-qp_w_comfort5.0
- qp_jerk_admm-qp_w_dev0.15-qp_w_comfort10.0: QP jerk, ADMM 150 vòng; lưới qp_w_dev0.15-qp_w_comfort10.0
- qp_jerk_admm-qp_w_dev0.15-qp_w_comfort2.5: QP jerk, ADMM 150 vòng; lưới qp_w_dev0.15-qp_w_comfort2.5
- qp_jerk_admm_it075: QP jerk, ADMM 75 vòng
- qp_jerk_admm: QP jerk, ADMM 150 vòng
- qp_jerk_admm_mlp_weights-mlpw_regularisation0.01: QP jerk, MLP chọn trọng số, 150 vòng; lưới mlpw_regularisation0.01
- qp_jerk_admm_mlp_weights-mlpw_regularisation0.0001: QP jerk, MLP chọn trọng số, 150 vòng; lưới mlpw_regularisation0.0001
- qp_jerk_admm_it100: QP jerk, ADMM 100 vòng
- qp_jerk_admm_shift_warmstart_it050: QP jerk, warm start dịch thời gian, 50 vòng
- qp_jerk_admm_mlp_warmstart_it050: QP jerk, MLP warm start, 50 vòng
- qp_jerk_admm_shift_warmstart_it075: QP jerk, warm start dịch thời gian, 75 vòng
- qp_jerk_admm_mlp_warmstart_it075: QP jerk, MLP warm start, 75 vòng
- qp_jerk_admm_mlp_warmstart_it025: QP jerk, MLP warm start, 25 vòng
- qp_jerk_admm_shift_warmstart_it025: QP jerk, warm start dịch thời gian, 25 vòng
- qp_jerk_admm-qp_w_dev0.6-qp_w_comfort10.0: QP jerk, ADMM 150 vòng; lưới qp_w_dev0.6-qp_w_comfort10.0
- qp_jerk_admm_it010: QP jerk, ADMM 10 vòng
- qp_jerk_admm-qp_w_dev0.3-qp_w_comfort10.0: QP jerk, ADMM 150 vòng; lưới qp_w_dev0.3-qp_w_comfort10.0
- qp_jerk_admm-qp_w_dev0.6-qp_w_comfort2.5: QP jerk, ADMM 150 vòng; lưới qp_w_dev0.6-qp_w_comfort2.5
- qp_jerk_admm-qp_w_dev0.3-qp_w_comfort2.5: QP jerk, ADMM 150 vòng; lưới qp_w_dev0.3-qp_w_comfort2.5
- qp_jerk_admm_it025: QP jerk, ADMM 25 vòng
- qp_jerk_admm-qp_w_dev0.6-qp_w_comfort5.0: QP jerk, ADMM 150 vòng; lưới qp_w_dev0.6-qp_w_comfort5.0
- qp_jerk_admm_it050: QP jerk, ADMM 50 vòng
- qp_jerk_admm_shift_warmstart_it010: QP jerk, warm start dịch thời gian, 10 vòng
- qp_jerk_admm_mlp_warmstart_it010: QP jerk, MLP warm start, 10 vòng
- quintic_duration-T_hwa2.5-T_recenter4.0: Quintic theo thời lượng, bản đang giao (mốc); lưới T_hwa2.5-T_recenter4.0
- quintic_duration-T_hwa2.5-T_recenter3.5: Quintic theo thời lượng, bản đang giao (mốc); lưới T_hwa2.5-T_recenter3.5
- quintic_duration-T_hwa2.5-T_recenter3.0: Quintic theo thời lượng, bản đang giao (mốc); lưới T_hwa2.5-T_recenter3.0
- quintic_duration-T_hwa3.0-T_recenter4.0: Quintic theo thời lượng, bản đang giao (mốc); lưới T_hwa3.0-T_recenter4.0
- quintic_duration: Quintic theo thời lượng, bản đang giao (mốc)
- quintic_tangent_point: Quintic cộng hiệu chỉnh ngang theo tangent point
- quintic_ay_sampling: Quintic cộng hiệu chỉnh ngang chọn theo a_y và jerk dự báo
- quintic_tangent_point-qtp_center_s1.5-qtp_dlc_margin_m0.0: Quintic cộng hiệu chỉnh ngang theo tangent point; lưới qtp_center_s1.5-qtp_dlc_margin_m0.0
- quintic_tangent_point-qtp_center_s1.5-qtp_dlc_margin_m0.01: Quintic cộng hiệu chỉnh ngang theo tangent point; lưới qtp_center_s1.5-qtp_dlc_margin_m0.01
- quintic_tangent_point-qtp_center_s1.5-qtp_dlc_margin_m0.02: Quintic cộng hiệu chỉnh ngang theo tangent point; lưới qtp_center_s1.5-qtp_dlc_margin_m0.02
- quintic_tangent_point-qtp_center_s1.75-qtp_dlc_margin_m0.0: Quintic cộng hiệu chỉnh ngang theo tangent point; lưới qtp_center_s1.75-qtp_dlc_margin_m0.0
- quintic_tangent_point-qtp_center_s2.0-qtp_dlc_margin_m0.0: Quintic cộng hiệu chỉnh ngang theo tangent point; lưới qtp_center_s2.0-qtp_dlc_margin_m0.0
- quintic_tangent_point-qtp_center_s2.0-qtp_dlc_margin_m0.01: Quintic cộng hiệu chỉnh ngang theo tangent point; lưới qtp_center_s2.0-qtp_dlc_margin_m0.01
- quintic_ay_sampling-qas_peak_early0.35-qas_peak_late0.55-qas_amplitude_m0.1: Quintic cộng hiệu chỉnh ngang chọn theo a_y và jerk dự báo; lưới qas_peak_early0.35-qas_peak_late0.55-qas_amplitude_m0.1
- quintic_ay_sampling-qas_peak_early0.35-qas_peak_late0.55-qas_amplitude_m0.2: Quintic cộng hiệu chỉnh ngang chọn theo a_y và jerk dự báo; lưới qas_peak_early0.35-qas_peak_late0.55-qas_amplitude_m0.2
- quintic_ay_sampling-qas_peak_early0.35-qas_peak_late0.55-qas_amplitude_m0.3: Quintic cộng hiệu chỉnh ngang chọn theo a_y và jerk dự báo; lưới qas_peak_early0.35-qas_peak_late0.55-qas_amplitude_m0.3
- quintic_ay_sampling-qas_peak_early0.4-qas_peak_late0.6-qas_amplitude_m0.1: Quintic cộng hiệu chỉnh ngang chọn theo a_y và jerk dự báo; lưới qas_peak_early0.4-qas_peak_late0.6-qas_amplitude_m0.1
- quintic_ay_sampling-qas_peak_early0.4-qas_peak_late0.6-qas_amplitude_m0.3: Quintic cộng hiệu chỉnh ngang chọn theo a_y và jerk dự báo; lưới qas_peak_early0.4-qas_peak_late0.6-qas_amplitude_m0.3
- quintic_ay_sampling-qas_peak_early0.45-qas_peak_late0.65-qas_amplitude_m0.1: Quintic cộng hiệu chỉnh ngang chọn theo a_y và jerk dự báo; lưới qas_peak_early0.45-qas_peak_late0.65-qas_amplitude_m0.1
- quintic_ay_sampling-qas_peak_early0.45-qas_peak_late0.65-qas_amplitude_m0.2: Quintic cộng hiệu chỉnh ngang chọn theo a_y và jerk dự báo; lưới qas_peak_early0.45-qas_peak_late0.65-qas_amplitude_m0.2
- quintic_ay_sampling-qas_peak_early0.45-qas_peak_late0.65-qas_amplitude_m0.3: Quintic cộng hiệu chỉnh ngang chọn theo a_y và jerk dự báo; lưới qas_peak_early0.45-qas_peak_late0.65-qas_amplitude_m0.3
- quintic_duration-T_hwa3.0-T_recenter3.0: Quintic theo thời lượng, bản đang giao (mốc); lưới T_hwa3.0-T_recenter3.0
- quintic_tangent_point-qtp_center_s1.75-qtp_dlc_margin_m0.02: Quintic cộng hiệu chỉnh ngang theo tangent point; lưới qtp_center_s1.75-qtp_dlc_margin_m0.02
- quintic_tangent_point-qtp_center_s2.0-qtp_dlc_margin_m0.02: Quintic cộng hiệu chỉnh ngang theo tangent point; lưới qtp_center_s2.0-qtp_dlc_margin_m0.02
- quintic_duration-T_hwa3.5-T_recenter4.0: Quintic theo thời lượng, bản đang giao (mốc); lưới T_hwa3.5-T_recenter4.0
- quintic_duration-T_hwa3.5-T_recenter3.5: Quintic theo thời lượng, bản đang giao (mốc); lưới T_hwa3.5-T_recenter3.5
- quintic_duration-T_hwa3.5-T_recenter3.0: Quintic theo thời lượng, bản đang giao (mốc); lưới T_hwa3.5-T_recenter3.0
- mlp_jerk_direct: MLP xuất chuỗi jerk, không có QP (đối chứng)

- test quintic_duration: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test qp_jerk_admm: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100
- test qp_jerk_admm_it010: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100
- test qp_jerk_admm_it025: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100
- test qp_jerk_admm_it050: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100
- test qp_jerk_admm_it075: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100
- test qp_jerk_admm_it100: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100
- test qp_jerk_admm_it1000_ref: S14e [acc=ignore_limits, loop=open]:PP-SWR-006
- test qp_jerk_admm_shift_warmstart_it010: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100
- test qp_jerk_admm_shift_warmstart_it025: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100
- test qp_jerk_admm_shift_warmstart_it050: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100
- test qp_jerk_admm_shift_warmstart_it075: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100
- test quintic_tangent_point: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test quintic_ay_sampling: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test qp_jerk_admm_mlp_warmstart_it010: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100
- test qp_jerk_admm_mlp_warmstart_it025: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100
- test qp_jerk_admm_mlp_warmstart_it050: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100
- test qp_jerk_admm_mlp_warmstart_it075: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100
- test qp_jerk_admm_mlp_weights: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100
- test mlp_jerk_direct: S12a:PP-SWR-051, S14e [acc=on]:PP-SWR-051, S1a_F01c:PP-SWR-051, S1c [profile=VP-3]:PP-SWR-051, S1c [profile=VP-5]:PP-SWR-051, S1c_F01c [profile=VP-5]:PP-SWR-051, S1c_F01c:PP-SWR-051, S1c_F06e:PP-SWR-051, S1f [camera_view_m=40, profile=VP-5]:PP-SWR-051, S1f [profile=VP-3]:PP-SWR-051, S22c:PP-SWR-173, S2d:PP-SWR-052, S3a:PP-SWR-055, S3a:PP-SWR-056, S3a:PP-SWR-058, S3b:PP-SWR-055, S3b:PP-SWR-056, S3b:PP-SWR-058
- test quintic_duration-T_hwa2.5-T_recenter3.0: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test quintic_duration-T_hwa2.5-T_recenter3.5: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test quintic_duration-T_hwa2.5-T_recenter4.0: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test quintic_duration-T_hwa3.0-T_recenter3.0: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test quintic_duration-T_hwa3.0-T_recenter4.0: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test quintic_duration-T_hwa3.5-T_recenter3.0: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test quintic_duration-T_hwa3.5-T_recenter3.5: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test quintic_duration-T_hwa3.5-T_recenter4.0: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test qp_jerk_admm-qp_w_dev0.15-qp_w_comfort2.5: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100
- test qp_jerk_admm-qp_w_dev0.15-qp_w_comfort5.0: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100
- test qp_jerk_admm-qp_w_dev0.15-qp_w_comfort10.0: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100
- test qp_jerk_admm-qp_w_dev0.3-qp_w_comfort2.5: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100
- test qp_jerk_admm-qp_w_dev0.3-qp_w_comfort10.0: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100
- test qp_jerk_admm-qp_w_dev0.6-qp_w_comfort2.5: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100
- test qp_jerk_admm-qp_w_dev0.6-qp_w_comfort5.0: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100
- test qp_jerk_admm-qp_w_dev0.6-qp_w_comfort10.0: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100
- test quintic_tangent_point-qtp_center_s1.5-qtp_dlc_margin_m0.0: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test quintic_tangent_point-qtp_center_s1.5-qtp_dlc_margin_m0.01: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test quintic_tangent_point-qtp_center_s1.5-qtp_dlc_margin_m0.02: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test quintic_tangent_point-qtp_center_s1.75-qtp_dlc_margin_m0.0: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test quintic_tangent_point-qtp_center_s1.75-qtp_dlc_margin_m0.02: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test quintic_tangent_point-qtp_center_s2.0-qtp_dlc_margin_m0.0: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test quintic_tangent_point-qtp_center_s2.0-qtp_dlc_margin_m0.01: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test quintic_tangent_point-qtp_center_s2.0-qtp_dlc_margin_m0.02: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test quintic_ay_sampling-qas_peak_early0.35-qas_peak_late0.55-qas_amplitude_m0.1: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test quintic_ay_sampling-qas_peak_early0.35-qas_peak_late0.55-qas_amplitude_m0.2: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test quintic_ay_sampling-qas_peak_early0.35-qas_peak_late0.55-qas_amplitude_m0.3: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test quintic_ay_sampling-qas_peak_early0.4-qas_peak_late0.6-qas_amplitude_m0.1: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test quintic_ay_sampling-qas_peak_early0.4-qas_peak_late0.6-qas_amplitude_m0.3: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test quintic_ay_sampling-qas_peak_early0.45-qas_peak_late0.65-qas_amplitude_m0.1: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test quintic_ay_sampling-qas_peak_early0.45-qas_peak_late0.65-qas_amplitude_m0.2: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test quintic_ay_sampling-qas_peak_early0.45-qas_peak_late0.65-qas_amplitude_m0.3: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100, S1bc [acc=ignore_limits, loop=open]:PP-SWR-100, S1bc [acc=ignore_limits]:PP-SWR-100, S1bf [acc=ignore_limits]:PP-SWR-100
- test qp_jerk_admm_mlp_weights-mlpw_regularisation0.0001: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100
- test qp_jerk_admm_mlp_weights-mlpw_regularisation0.01: S14e [acc=ignore_limits, loop=open]:PP-SWR-006, S14e [acc=ignore_limits]:PP-SWR-006, S14e [acc=on]:PP-SWR-006, S1bb [acc=ignore_limits]:PP-SWR-100

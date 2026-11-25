# Study PP-TS-031

Plan: `research/studies/PP-TS-031-t7-generator-campaign/plan.yaml`, locked 2026-11-24; suite PP-T7.

Bảng dưới dùng để dò nhanh. Đối chiếu B0, lỗi, điều kiện áp dụng và số đo ghép cặp trong `results.json` trước khi xếp hạng theo đề cương.

## tuning

| Bộ | Trượt | PP-SWR-050 | PP-SWR-125 | PP-SWR-002 | PP-SWR-053 | PP-SWR-003 |
|---|---|---|---|---|---|---|
| qp_jerk_admm_it1000_ref | 0 | 0.591 | — | — | — | 0.918 |
| quintic_duration-T_hwa3.5-T_recenter3.0 | 0 | 1.836 | — | 0.3193 | 0.821 | 1.546 |
| quintic_duration-T_hwa3.5-T_recenter3.5 | 0 | 1.836 | — | 0.3316 | 0.838 | 1.546 |
| quintic_duration-T_hwa3.5-T_recenter4.0 | 0 | 1.836 | — | 0.3418 | 0.848 | 1.546 |
| quintic_duration-T_hwa3.0-T_recenter3.0 | 0 | 1.843 | — | 0.3182 | 0.821 | 1.658 |
| quintic_duration | 0 | 1.843 | — | 0.3295 | 0.831 | 1.658 |
| quintic_ay_sampling | 0 | 1.843 | — | 0.3295 | 0.831 | 1.658 |
| quintic_tangent_point-qtp_center_s1.5-qtp_dlc_margin_m0.0 | 0 | 1.843 | — | 0.3295 | 0.831 | 1.658 |
| quintic_tangent_point-qtp_center_s1.5-qtp_dlc_margin_m0.01 | 0 | 1.843 | — | 0.3295 | 0.831 | 1.658 |
| quintic_tangent_point-qtp_center_s1.5-qtp_dlc_margin_m0.02 | 0 | 1.843 | — | 0.3295 | 0.831 | 1.658 |
| quintic_tangent_point-qtp_center_s1.75-qtp_dlc_margin_m0.0 | 0 | 1.843 | — | 0.3295 | 0.831 | 1.658 |
| quintic_tangent_point-qtp_center_s2.0-qtp_dlc_margin_m0.0 | 0 | 1.843 | — | 0.3295 | 0.831 | 1.658 |
| quintic_ay_sampling-qas_peak_early0.35-qas_peak_late0.55-qas_amplitude_m0.1 | 0 | 1.843 | — | 0.3295 | 0.831 | 1.658 |
| quintic_ay_sampling-qas_peak_early0.35-qas_peak_late0.55-qas_amplitude_m0.2 | 0 | 1.843 | — | 0.3295 | 0.831 | 1.658 |
| quintic_ay_sampling-qas_peak_early0.35-qas_peak_late0.55-qas_amplitude_m0.3 | 0 | 1.843 | — | 0.3295 | 0.831 | 1.658 |
| quintic_ay_sampling-qas_peak_early0.4-qas_peak_late0.6-qas_amplitude_m0.1 | 0 | 1.843 | — | 0.3295 | 0.831 | 1.658 |
| quintic_ay_sampling-qas_peak_early0.4-qas_peak_late0.6-qas_amplitude_m0.3 | 0 | 1.843 | — | 0.3295 | 0.831 | 1.658 |
| quintic_ay_sampling-qas_peak_early0.45-qas_peak_late0.65-qas_amplitude_m0.1 | 0 | 1.843 | — | 0.3295 | 0.831 | 1.658 |
| quintic_ay_sampling-qas_peak_early0.45-qas_peak_late0.65-qas_amplitude_m0.2 | 0 | 1.843 | — | 0.3295 | 0.831 | 1.658 |
| quintic_ay_sampling-qas_peak_early0.45-qas_peak_late0.65-qas_amplitude_m0.3 | 0 | 1.843 | — | 0.3295 | 0.831 | 1.658 |
| quintic_duration-T_hwa3.0-T_recenter4.0 | 0 | 1.843 | — | 0.3379 | 0.841 | 1.658 |
| quintic_tangent_point | 0 | 1.843 | — | 0.3295 | 0.831 | 1.658 |
| quintic_tangent_point-qtp_center_s2.0-qtp_dlc_margin_m0.01 | 0 | 1.843 | — | 0.3295 | 0.831 | 1.658 |
| quintic_tangent_point-qtp_center_s1.75-qtp_dlc_margin_m0.02 | 0 | 1.843 | — | 0.3295 | 0.831 | 1.658 |
| quintic_tangent_point-qtp_center_s2.0-qtp_dlc_margin_m0.02 | 0 | 1.843 | — | 0.3295 | 0.831 | 1.658 |
| quintic_duration-T_hwa2.5-T_recenter3.0 | 0 | 1.844 | — | 0.316 | 0.818 | 1.831 |
| quintic_duration-T_hwa2.5-T_recenter3.5 | 0 | 1.844 | — | 0.3227 | 0.828 | 1.831 |
| quintic_duration-T_hwa2.5-T_recenter4.0 | 0 | 1.844 | — | 0.3285 | 0.831 | 1.831 |
| qp_jerk_admm_mlp_warmstart_it010 | 0 | 1.942 | — | 0.6466 | 2.831 | 3.252 |
| qp_jerk_admm_shift_warmstart_it010 | 0 | 2.043 | — | 0.6514 | 2.731 | 3.366 |
| qp_jerk_admm_shift_warmstart_it025 | 0 | 2.066 | — | 0.6529 | 2.721 | 2.837 |
| qp_jerk_admm_mlp_warmstart_it025 | 0 | 2.066 | — | 0.6529 | 2.721 | 2.839 |
| qp_jerk_admm-qp_w_dev0.15-qp_w_comfort5.0 | 0 | 2.067 | — | 0.6812 | 2.811 | 3.504 |
| qp_jerk_admm_it075 | 0 | 2.069 | — | 0.6529 | 2.721 | 3.034 |
| qp_jerk_admm-qp_w_dev0.15-qp_w_comfort10.0 | 0 | 2.069 | — | 0.6812 | 2.811 | 3.32 |
| qp_jerk_admm_shift_warmstart_it075 | 0 | 2.069 | — | 0.6529 | 2.721 | 3.292 |
| qp_jerk_admm_mlp_warmstart_it075 | 0 | 2.069 | — | 0.6529 | 2.721 | 3.292 |
| qp_jerk_admm_it050 | 0 | 2.069 | — | 0.6529 | 2.721 | 2.459 |
| qp_jerk_admm_shift_warmstart_it050 | 0 | 2.07 | — | 0.6529 | 2.721 | 2.993 |
| qp_jerk_admm_mlp_warmstart_it050 | 0 | 2.07 | — | 0.6529 | 2.721 | 2.993 |
| qp_jerk_admm-qp_w_dev0.3-qp_w_comfort10.0 | 0 | 2.07 | — | 0.6529 | 2.721 | 3.335 |
| qp_jerk_admm-qp_w_dev0.6-qp_w_comfort5.0 | 0 | 2.07 | — | 0.6093 | 2.581 | 3.656 |
| qp_jerk_admm-qp_w_dev0.6-qp_w_comfort10.0 | 0 | 2.072 | — | 0.6093 | 2.581 | 3.466 |
| qp_jerk_admm_it010 | 0 | 2.155 | — | 0.6538 | 2.751 | 2.92 |
| qp_jerk_admm-qp_w_dev0.15-qp_w_comfort2.5 | 0 | 2.165 | — | 0.6812 | 2.811 | 3.615 |
| qp_jerk_admm_it025 | 0 | 2.166 | — | 0.6529 | 2.721 | 2.646 |
| qp_jerk_admm-qp_w_dev0.3-qp_w_comfort2.5 | 0 | 2.166 | — | 0.6529 | 2.721 | 3.645 |
| qp_jerk_admm-qp_w_dev0.6-qp_w_comfort2.5 | 0 | 2.168 | — | 0.6093 | 2.581 | 3.781 |
| qp_jerk_admm_mlp_weights-mlpw_regularisation0.01 | 0 | 2.168 | — | 0.65 | 2.721 | 3.513 |
| qp_jerk_admm | 0 | 2.168 | — | 0.6529 | 2.721 | 3.535 |
| qp_jerk_admm_mlp_weights-mlpw_regularisation0.0001 | 0 | 2.168 | — | 0.6505 | 2.731 | 3.532 |
| qp_jerk_admm_mlp_weights | 0 | 2.168 | — | 0.6507 | 2.741 | 3.535 |
| qp_jerk_admm_it100 | 0 | 2.168 | — | 0.6529 | 2.721 | 3.349 |
| mlp_jerk_direct | 12 | 1.234 | — | 0.4266 | 0.831 | 2.978 |

- qp_jerk_admm_it1000_ref: QP jerk, ADMM 1000 vòng, nghiệm tham chiếu; chỉ vòng hở, không xếp hạng
- quintic_duration-T_hwa3.5-T_recenter3.0: Quintic theo thời lượng, bản đang giao (mốc); lưới T_hwa3.5-T_recenter3.0
- quintic_duration-T_hwa3.5-T_recenter3.5: Quintic theo thời lượng, bản đang giao (mốc); lưới T_hwa3.5-T_recenter3.5
- quintic_duration-T_hwa3.5-T_recenter4.0: Quintic theo thời lượng, bản đang giao (mốc); lưới T_hwa3.5-T_recenter4.0
- quintic_duration-T_hwa3.0-T_recenter3.0: Quintic theo thời lượng, bản đang giao (mốc); lưới T_hwa3.0-T_recenter3.0
- quintic_duration: Quintic theo thời lượng, bản đang giao (mốc)
- quintic_ay_sampling: Quintic cộng hiệu chỉnh ngang chọn theo a_y và jerk dự báo
- quintic_tangent_point-qtp_center_s1.5-qtp_dlc_margin_m0.0: Quintic cộng hiệu chỉnh ngang theo tangent point; lưới qtp_center_s1.5-qtp_dlc_margin_m0.0
- quintic_tangent_point-qtp_center_s1.5-qtp_dlc_margin_m0.01: Quintic cộng hiệu chỉnh ngang theo tangent point; lưới qtp_center_s1.5-qtp_dlc_margin_m0.01
- quintic_tangent_point-qtp_center_s1.5-qtp_dlc_margin_m0.02: Quintic cộng hiệu chỉnh ngang theo tangent point; lưới qtp_center_s1.5-qtp_dlc_margin_m0.02
- quintic_tangent_point-qtp_center_s1.75-qtp_dlc_margin_m0.0: Quintic cộng hiệu chỉnh ngang theo tangent point; lưới qtp_center_s1.75-qtp_dlc_margin_m0.0
- quintic_tangent_point-qtp_center_s2.0-qtp_dlc_margin_m0.0: Quintic cộng hiệu chỉnh ngang theo tangent point; lưới qtp_center_s2.0-qtp_dlc_margin_m0.0
- quintic_ay_sampling-qas_peak_early0.35-qas_peak_late0.55-qas_amplitude_m0.1: Quintic cộng hiệu chỉnh ngang chọn theo a_y và jerk dự báo; lưới qas_peak_early0.35-qas_peak_late0.55-qas_amplitude_m0.1
- quintic_ay_sampling-qas_peak_early0.35-qas_peak_late0.55-qas_amplitude_m0.2: Quintic cộng hiệu chỉnh ngang chọn theo a_y và jerk dự báo; lưới qas_peak_early0.35-qas_peak_late0.55-qas_amplitude_m0.2
- quintic_ay_sampling-qas_peak_early0.35-qas_peak_late0.55-qas_amplitude_m0.3: Quintic cộng hiệu chỉnh ngang chọn theo a_y và jerk dự báo; lưới qas_peak_early0.35-qas_peak_late0.55-qas_amplitude_m0.3
- quintic_ay_sampling-qas_peak_early0.4-qas_peak_late0.6-qas_amplitude_m0.1: Quintic cộng hiệu chỉnh ngang chọn theo a_y và jerk dự báo; lưới qas_peak_early0.4-qas_peak_late0.6-qas_amplitude_m0.1
- quintic_ay_sampling-qas_peak_early0.4-qas_peak_late0.6-qas_amplitude_m0.3: Quintic cộng hiệu chỉnh ngang chọn theo a_y và jerk dự báo; lưới qas_peak_early0.4-qas_peak_late0.6-qas_amplitude_m0.3
- quintic_ay_sampling-qas_peak_early0.45-qas_peak_late0.65-qas_amplitude_m0.1: Quintic cộng hiệu chỉnh ngang chọn theo a_y và jerk dự báo; lưới qas_peak_early0.45-qas_peak_late0.65-qas_amplitude_m0.1
- quintic_ay_sampling-qas_peak_early0.45-qas_peak_late0.65-qas_amplitude_m0.2: Quintic cộng hiệu chỉnh ngang chọn theo a_y và jerk dự báo; lưới qas_peak_early0.45-qas_peak_late0.65-qas_amplitude_m0.2
- quintic_ay_sampling-qas_peak_early0.45-qas_peak_late0.65-qas_amplitude_m0.3: Quintic cộng hiệu chỉnh ngang chọn theo a_y và jerk dự báo; lưới qas_peak_early0.45-qas_peak_late0.65-qas_amplitude_m0.3
- quintic_duration-T_hwa3.0-T_recenter4.0: Quintic theo thời lượng, bản đang giao (mốc); lưới T_hwa3.0-T_recenter4.0
- quintic_tangent_point: Quintic cộng hiệu chỉnh ngang theo tangent point
- quintic_tangent_point-qtp_center_s2.0-qtp_dlc_margin_m0.01: Quintic cộng hiệu chỉnh ngang theo tangent point; lưới qtp_center_s2.0-qtp_dlc_margin_m0.01
- quintic_tangent_point-qtp_center_s1.75-qtp_dlc_margin_m0.02: Quintic cộng hiệu chỉnh ngang theo tangent point; lưới qtp_center_s1.75-qtp_dlc_margin_m0.02
- quintic_tangent_point-qtp_center_s2.0-qtp_dlc_margin_m0.02: Quintic cộng hiệu chỉnh ngang theo tangent point; lưới qtp_center_s2.0-qtp_dlc_margin_m0.02
- quintic_duration-T_hwa2.5-T_recenter3.0: Quintic theo thời lượng, bản đang giao (mốc); lưới T_hwa2.5-T_recenter3.0
- quintic_duration-T_hwa2.5-T_recenter3.5: Quintic theo thời lượng, bản đang giao (mốc); lưới T_hwa2.5-T_recenter3.5
- quintic_duration-T_hwa2.5-T_recenter4.0: Quintic theo thời lượng, bản đang giao (mốc); lưới T_hwa2.5-T_recenter4.0
- qp_jerk_admm_mlp_warmstart_it010: QP jerk, MLP warm start, 10 vòng
- qp_jerk_admm_shift_warmstart_it010: QP jerk, warm start dịch thời gian, 10 vòng
- qp_jerk_admm_shift_warmstart_it025: QP jerk, warm start dịch thời gian, 25 vòng
- qp_jerk_admm_mlp_warmstart_it025: QP jerk, MLP warm start, 25 vòng
- qp_jerk_admm-qp_w_dev0.15-qp_w_comfort5.0: QP jerk, ADMM 150 vòng; lưới qp_w_dev0.15-qp_w_comfort5.0
- qp_jerk_admm_it075: QP jerk, ADMM 75 vòng
- qp_jerk_admm-qp_w_dev0.15-qp_w_comfort10.0: QP jerk, ADMM 150 vòng; lưới qp_w_dev0.15-qp_w_comfort10.0
- qp_jerk_admm_shift_warmstart_it075: QP jerk, warm start dịch thời gian, 75 vòng
- qp_jerk_admm_mlp_warmstart_it075: QP jerk, MLP warm start, 75 vòng
- qp_jerk_admm_it050: QP jerk, ADMM 50 vòng
- qp_jerk_admm_shift_warmstart_it050: QP jerk, warm start dịch thời gian, 50 vòng
- qp_jerk_admm_mlp_warmstart_it050: QP jerk, MLP warm start, 50 vòng
- qp_jerk_admm-qp_w_dev0.3-qp_w_comfort10.0: QP jerk, ADMM 150 vòng; lưới qp_w_dev0.3-qp_w_comfort10.0
- qp_jerk_admm-qp_w_dev0.6-qp_w_comfort5.0: QP jerk, ADMM 150 vòng; lưới qp_w_dev0.6-qp_w_comfort5.0
- qp_jerk_admm-qp_w_dev0.6-qp_w_comfort10.0: QP jerk, ADMM 150 vòng; lưới qp_w_dev0.6-qp_w_comfort10.0
- qp_jerk_admm_it010: QP jerk, ADMM 10 vòng
- qp_jerk_admm-qp_w_dev0.15-qp_w_comfort2.5: QP jerk, ADMM 150 vòng; lưới qp_w_dev0.15-qp_w_comfort2.5
- qp_jerk_admm_it025: QP jerk, ADMM 25 vòng
- qp_jerk_admm-qp_w_dev0.3-qp_w_comfort2.5: QP jerk, ADMM 150 vòng; lưới qp_w_dev0.3-qp_w_comfort2.5
- qp_jerk_admm-qp_w_dev0.6-qp_w_comfort2.5: QP jerk, ADMM 150 vòng; lưới qp_w_dev0.6-qp_w_comfort2.5
- qp_jerk_admm_mlp_weights-mlpw_regularisation0.01: QP jerk, MLP chọn trọng số, 150 vòng; lưới mlpw_regularisation0.01
- qp_jerk_admm: QP jerk, ADMM 150 vòng
- qp_jerk_admm_mlp_weights-mlpw_regularisation0.0001: QP jerk, MLP chọn trọng số, 150 vòng; lưới mlpw_regularisation0.0001
- qp_jerk_admm_mlp_weights: QP jerk, MLP chọn trọng số, 150 vòng
- qp_jerk_admm_it100: QP jerk, ADMM 100 vòng
- mlp_jerk_direct: MLP xuất chuỗi jerk, không có QP (đối chứng)

- tuning mlp_jerk_direct: S1a:PP-SWR-051, S1g:PP-SWR-051, S1g_F01a:PP-SWR-051, S3a:PP-SWR-055, S3a:PP-SWR-056, S3a:PP-SWR-058

# Kết luận: Không đạt

- Planner: pp_planner 0.2.0 commit d2e7d2794621 calibration 418f18b44dc0 t7 quintic (a51120a43115)
- Tích hợp được: có
- Đã chạy: 2085 lần chạy; trượt BLOCKER 51, MAJOR 0, MINOR 46
- Kết luận chỉ đúng trong phạm vi đã thử, không phải bằng chứng an toàn (Software Qualification Test Specification 3).

## Trượt BLOCKER

| Requirement | Safety goal | Ca | Profile | Seed | Trượt đầu tiên [s] | Giá trị | Ngưỡng | Chi tiết | MCAP |
|---|---|---|---|---|---|---|---|---|---|
| PP-SWR-005 | SG-02 | S1b-a-VP-0-693b15015bfa | VP-0 | 1 | 7.858 | 1 | = 0 | Chu kỳ cua gắt mà mất path hoặc HWA | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S1b-a-VP-0-693b15015bfa_seed1.mcap |
| PP-SWR-006 | SG-02 | S1b-a-VP-0-693b15015bfa | VP-0 | 1 | 3.958 | -0.1153 | >= 0 | a_y path trừ (aysmax − epsilon_ay), 0–1 s, khi a_y cần > aysmax [m/s²] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S1b-a-VP-0-693b15015bfa_seed1.mcap |
| PP-SWR-007 | SG-01 | S1b-a-VP-0-693b15015bfa | VP-0 | 1 | 8.621 | 1 | = 0 | Lần lốp đè vạch khi cua gắt mà cờ chưa bật | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S1b-a-VP-0-693b15015bfa_seed1.mcap |
| PP-SWR-030 | SG-01 | S14-a-VP-0-3290c39907ee | VP-0 | 1 | 7.858 | 29 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S14-a-VP-0-3290c39907ee_seed1.mcap |
| PP-SWR-030 | SG-01 | S16-d-VP-0-e29852ad5a1c | VP-0 | 1 | — | — | — | ELK: có REQUEST nhưng thiếu path can thiệp hợp lệ | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S16-d-VP-0-e29852ad5a1c_seed1.mcap |
| PP-SWR-030 | SG-01 | S16-d-VP-3-c4c71c213cb3 | VP-3 | 1 | — | — | — | ELK: có REQUEST nhưng thiếu path can thiệp hợp lệ | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S16-d-VP-3-c4c71c213cb3_seed1.mcap |
| PP-SWR-030 | SG-01 | S1b-a-VP-0-693b15015bfa | VP-0 | 1 | 7.858 | 29 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S1b-a-VP-0-693b15015bfa_seed1.mcap |
| PP-SWR-051 | SG-01 | F02-e-S1a-VP-5-29183b65ffaf | VP-5 | 1 | — | -0.1104 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F02-e-S1a-VP-5-29183b65ffaf_seed1.mcap |
| PP-SWR-051 | SG-01 | F02-e-S1c-VP-5-50d3444b79d5 | VP-5 | 1 | — | -0.1131 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F02-e-S1c-VP-5-50d3444b79d5_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1a-VP-0-1c03af025ee4 | VP-0 | 1 | — | -0.2409 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F03-c-S1a-VP-0-1c03af025ee4_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1a-VP-1-a5219f0b3fc2 | VP-1 | 1 | — | -0.2344 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F03-c-S1a-VP-1-a5219f0b3fc2_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1a-VP-5-4a0b9685f06c | VP-5 | 1 | — | -0.5521 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F03-c-S1a-VP-5-4a0b9685f06c_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1c-VP-0-0e2929c3df25 | VP-0 | 1 | — | -0.1758 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F03-c-S1c-VP-0-0e2929c3df25_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1c-VP-1-4278b1e68610 | VP-1 | 1 | — | -0.1691 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F03-c-S1c-VP-1-4278b1e68610_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1c-VP-5-ce2933b62cf1 | VP-5 | 1 | — | -0.5426 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F03-c-S1c-VP-5-ce2933b62cf1_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1a-VP-0-5158987ade9c | VP-0 | 1 | — | -0.2939 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F06-a-S1a-VP-0-5158987ade9c_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1c-VP-0-aed66d9b07f6 | VP-0 | 1 | — | -0.807 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F06-a-S1c-VP-0-aed66d9b07f6_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1a-VP-0-24550cfc95c5 | VP-0 | 1 | — | -0.2939 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F06-d-S1a-VP-0-24550cfc95c5_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1a-VP-1-3a4b29f3fe5b | VP-1 | 1 | — | -0.3006 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F06-d-S1a-VP-1-3a4b29f3fe5b_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1a-VP-5-9e2995fea291 | VP-5 | 1 | — | -0.6023 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F06-d-S1a-VP-5-9e2995fea291_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1c-VP-0-608ec3b8fc9f | VP-0 | 1 | — | -0.807 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F06-d-S1c-VP-0-608ec3b8fc9f_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1c-VP-1-40397bd3efa4 | VP-1 | 1 | — | -0.729 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F06-d-S1c-VP-1-40397bd3efa4_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1c-VP-5-bdab3c9103b7 | VP-5 | 1 | — | -1.15 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F06-d-S1c-VP-5-bdab3c9103b7_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-0-4efddd649b2a | VP-0 | 1 | — | -0.7418 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F08-a-S1c-VP-0-4efddd649b2a_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-0-9d836e616214 | VP-0 | 1 | — | -0.7418 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F08-a-S1c-VP-0-9d836e616214_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-1-9f6496a368b0 | VP-1 | 1 | — | -0.8226 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F08-a-S1c-VP-1-9f6496a368b0_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-1-c098420638d4 | VP-1 | 1 | — | -0.8226 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F08-a-S1c-VP-1-c098420638d4_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-5-5d6c59c69cbe | VP-5 | 1 | — | -1.028 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F08-a-S1c-VP-5-5d6c59c69cbe_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-5-dce61f599c6e | VP-5 | 1 | — | -1.028 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F08-a-S1c-VP-5-dce61f599c6e_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-b-S1c-VP-0-4ae7633cf949 | VP-0 | 1 | — | -0.9729 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F08-b-S1c-VP-0-4ae7633cf949_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-b-S1c-VP-1-297eab73e001 | VP-1 | 1 | — | -0.9906 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F08-b-S1c-VP-1-297eab73e001_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-b-S1c-VP-5-9d66d718191a | VP-5 | 1 | — | -1.281 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F08-b-S1c-VP-5-9d66d718191a_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1c-VP-0-bca0f1afb997 | VP-0 | 1 | — | -0.9593 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F08-c-S1c-VP-0-bca0f1afb997_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1c-VP-1-3d8334644eea | VP-1 | 1 | — | -1.02 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F08-c-S1c-VP-1-3d8334644eea_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1c-VP-5-06d7bb8fda8b | VP-5 | 1 | — | -1.357 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F08-c-S1c-VP-5-06d7bb8fda8b_seed1.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-5-38898514a806 | VP-5 | 1 | — | -0.0044 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/G01-S1c-VP-5-38898514a806_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-a-VP-0-cabfa230312d | VP-0 | 1 | — | -23.16 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S14-a-VP-0-cabfa230312d_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-0-ff8e4ce04140 | VP-0 | 1 | — | -0.0208 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S14-e-VP-0-ff8e4ce04140_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-1-c599c50726eb | VP-1 | 1 | — | -0.1124 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S14-e-VP-1-c599c50726eb_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-2-d2cc20ee8bbf | VP-2 | 1 | — | -0.1375 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S14-e-VP-2-d2cc20ee8bbf_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-3-24dcd5adb2de | VP-3 | 1 | — | -0.1734 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S14-e-VP-3-24dcd5adb2de_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-4-a571d2de589d | VP-4 | 1 | — | -0.1832 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S14-e-VP-4-a571d2de589d_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-5-3f2b28b63f2e | VP-5 | 1 | — | -0.3062 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S14-e-VP-5-3f2b28b63f2e_seed1.mcap |
| PP-SWR-085 | SG-01 | F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0 | VP-3 | 1 | — | -0.1043 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0_seed1.mcap |
| PP-SWR-085 | SG-01 | S13-b-elk-VP-3-036d4797fb02 | VP-3 | 1 | — | -0.09176 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S13-b-elk-VP-3-036d4797fb02_seed1.mcap |
| PP-SWR-085 | SG-01 | S6-b-VP-5-025575367d8c | VP-5 | 1 | — | -0.1609 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S6-b-VP-5-025575367d8c_seed1.mcap |
| PP-SWR-086 | SG-03 | S13-b-elk-VP-3-036d4797fb02 | VP-3 | 1 | — | -0.4499 | >= -0.3 | DTLE vạch nhỏ nhất [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S13-b-elk-VP-3-036d4797fb02_seed1.mcap |
| PP-SWR-086 | SG-03 | S6-b-VP-4-49ce96f36822 | VP-4 | 1 | — | -0.2425 | >= -0.1 | DTLE mép đường nhỏ nhất [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S6-b-VP-4-49ce96f36822_seed1.mcap |
| PP-SWR-086 | SG-03 | S6-b-VP-5-025575367d8c | VP-5 | 1 | — | -0.3602 | >= -0.1 | DTLE mép đường nhỏ nhất [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S6-b-VP-5-025575367d8c_seed1.mcap |
| PP-SWR-091 | SG-03 | S13-b-elk-VP-3-036d4797fb02 | VP-3 | 1 | — | -0.4499 | >= -0.3 | DTLE vạch khi EPS chậm tới 100 ms [m] | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S13-b-elk-VP-3-036d4797fb02_seed1.mcap |
| PP-SWR-102 | SG-04 | S6-b-VP-4-49ce96f36822 | VP-4 | 1 | 11.18 | 2.329 | <= 1 | Lệch độ cong giữa hai path liên tiếp / ngưỡng của khoảng | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S6-b-VP-4-49ce96f36822_seed1.mcap |

## Trượt MINOR

| Requirement | Safety goal | Ca | Profile | Seed | Trượt đầu tiên [s] | Giá trị | Ngưỡng | Chi tiết | MCAP |
|---|---|---|---|---|---|---|---|---|---|
| PP-SWR-032 | — | F01-a-S4a_at_lka_activep0-VP-0-c97d4f8c3b33 | VP-0 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F01-a-S4a_at_lka_activep0-VP-0-c97d4f8c3b33_seed1.mcap |
| PP-SWR-032 | — | F01-a-S4a_at_lka_activep0-VP-0-c97d4f8c3b33 | VP-0 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F01-a-S4a_at_lka_activep0-VP-0-c97d4f8c3b33_seed2.mcap |
| PP-SWR-032 | — | F01-a-S5a_at_elk_activep0.2-VP-1-44c9a8a8a61d | VP-1 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F01-a-S5a_at_elk_activep0.2-VP-1-44c9a8a8a61d_seed1.mcap |
| PP-SWR-032 | — | F01-a-S5a_at_elk_activep0.2-VP-1-44c9a8a8a61d | VP-1 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F01-a-S5a_at_elk_activep0.2-VP-1-44c9a8a8a61d_seed2.mcap |
| PP-SWR-032 | — | F01-b-S4a_at_lka_activep0-VP-2-26b730c60966 | VP-2 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F01-b-S4a_at_lka_activep0-VP-2-26b730c60966_seed1.mcap |
| PP-SWR-032 | — | F01-b-S4a_at_lka_activep0-VP-2-26b730c60966 | VP-2 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F01-b-S4a_at_lka_activep0-VP-2-26b730c60966_seed2.mcap |
| PP-SWR-032 | — | F01-b-S4a_at_lka_activep0.2-VP-3-7e4bb0e3caed | VP-3 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F01-b-S4a_at_lka_activep0.2-VP-3-7e4bb0e3caed_seed1.mcap |
| PP-SWR-032 | — | F01-b-S4a_at_lka_activep0.2-VP-3-7e4bb0e3caed | VP-3 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F01-b-S4a_at_lka_activep0.2-VP-3-7e4bb0e3caed_seed2.mcap |
| PP-SWR-032 | — | F01-b-S5a_at_elk_activep0-VP-2-795bfb495e44 | VP-2 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F01-b-S5a_at_elk_activep0-VP-2-795bfb495e44_seed1.mcap |
| PP-SWR-032 | — | F01-b-S5a_at_elk_activep0.2-VP-3-43bbc0fa0b87 | VP-3 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F01-b-S5a_at_elk_activep0.2-VP-3-43bbc0fa0b87_seed1.mcap |
| PP-SWR-032 | — | F01-b-S5a_at_elk_activep0.2-VP-3-43bbc0fa0b87 | VP-3 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F01-b-S5a_at_elk_activep0.2-VP-3-43bbc0fa0b87_seed2.mcap |
| PP-SWR-032 | — | F01-c-S4a_at_lka_activep0-VP-4-914355537c7d | VP-4 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F01-c-S4a_at_lka_activep0-VP-4-914355537c7d_seed1.mcap |
| PP-SWR-032 | — | F01-c-S4a_at_lka_activep0-VP-4-914355537c7d | VP-4 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F01-c-S4a_at_lka_activep0-VP-4-914355537c7d_seed2.mcap |
| PP-SWR-032 | — | F01-c-S4a_at_lka_activep0.2-VP-5-2e109dc103db | VP-5 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F01-c-S4a_at_lka_activep0.2-VP-5-2e109dc103db_seed1.mcap |
| PP-SWR-032 | — | F01-c-S4a_at_lka_activep0.2-VP-5-2e109dc103db | VP-5 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F01-c-S4a_at_lka_activep0.2-VP-5-2e109dc103db_seed2.mcap |
| PP-SWR-032 | — | F01-c-S5a_at_elk_activep0-VP-4-d7e0b59fbf4d | VP-4 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F01-c-S5a_at_elk_activep0-VP-4-d7e0b59fbf4d_seed1.mcap |
| PP-SWR-032 | — | F01-c-S5a_at_elk_activep0-VP-4-d7e0b59fbf4d | VP-4 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F01-c-S5a_at_elk_activep0-VP-4-d7e0b59fbf4d_seed2.mcap |
| PP-SWR-032 | — | F01-c-S5a_at_elk_activep0.2-VP-5-fbea90d7d4d0 | VP-5 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F01-c-S5a_at_elk_activep0.2-VP-5-fbea90d7d4d0_seed1.mcap |
| PP-SWR-032 | — | F01-c-S5a_at_elk_activep0.2-VP-5-fbea90d7d4d0 | VP-5 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F01-c-S5a_at_elk_activep0.2-VP-5-fbea90d7d4d0_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-0-944a5944b2f0 | VP-0 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/G01-S4c-VP-0-944a5944b2f0_seed1.mcap |
| PP-SWR-032 | — | G01-S4c-VP-0-944a5944b2f0 | VP-0 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/G01-S4c-VP-0-944a5944b2f0_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-1-d9c02f4d85c9 | VP-1 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/G01-S4c-VP-1-d9c02f4d85c9_seed1.mcap |
| PP-SWR-032 | — | G01-S4c-VP-1-d9c02f4d85c9 | VP-1 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/G01-S4c-VP-1-d9c02f4d85c9_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-2-19b08e51426b | VP-2 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/G01-S4c-VP-2-19b08e51426b_seed1.mcap |
| PP-SWR-032 | — | G01-S4c-VP-2-19b08e51426b | VP-2 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/G01-S4c-VP-2-19b08e51426b_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-3-9991783c316d | VP-3 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/G01-S4c-VP-3-9991783c316d_seed1.mcap |
| PP-SWR-032 | — | G01-S4c-VP-3-9991783c316d | VP-3 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/G01-S4c-VP-3-9991783c316d_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-4-072664ac9b98 | VP-4 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/G01-S4c-VP-4-072664ac9b98_seed1.mcap |
| PP-SWR-032 | — | G01-S4c-VP-4-072664ac9b98 | VP-4 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/G01-S4c-VP-4-072664ac9b98_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-5-26df2868e70c | VP-5 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/G01-S4c-VP-5-26df2868e70c_seed1.mcap |
| PP-SWR-032 | — | G01-S4c-VP-5-26df2868e70c | VP-5 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/G01-S4c-VP-5-26df2868e70c_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-0-69e53aeef11a | VP-0 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S12-b-VP-0-69e53aeef11a_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-0-69e53aeef11a | VP-0 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S12-b-VP-0-69e53aeef11a_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-1-4b3e70a50a26 | VP-1 | 1 | — | 2 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S12-b-VP-1-4b3e70a50a26_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-1-4b3e70a50a26 | VP-1 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S12-b-VP-1-4b3e70a50a26_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-2-0962daddf5bd | VP-2 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S12-b-VP-2-0962daddf5bd_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-2-0962daddf5bd | VP-2 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S12-b-VP-2-0962daddf5bd_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-3-984dbaa7f733 | VP-3 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S12-b-VP-3-984dbaa7f733_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-3-984dbaa7f733 | VP-3 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S12-b-VP-3-984dbaa7f733_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-4-a4945d3bcd67 | VP-4 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S12-b-VP-4-a4945d3bcd67_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-4-a4945d3bcd67 | VP-4 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S12-b-VP-4-a4945d3bcd67_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-5-2b777db332c0 | VP-5 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S12-b-VP-5-2b777db332c0_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-5-2b777db332c0 | VP-5 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S12-b-VP-5-2b777db332c0_seed2.mcap |
| PP-SWR-032 | — | S13-a-VP-5-4d54367ca2b0 | VP-5 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S13-a-VP-5-4d54367ca2b0_seed1.mcap |
| PP-SWR-090 | — | F02-e-S5a_at_elk_activep0.2-VP-3-bb766866f0d0 | VP-3 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/F02-e-S5a_at_elk_activep0.2-VP-3-bb766866f0d0_seed1.mcap |
| PP-SWR-090 | — | S5-c-VP-5-fc8939d6aa80 | VP-5 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /private/tmp/claude-501/-Users-thongbui-nd-Documents-T-i-li-u---Nidai-Thong-Bui-vinuni-ADAS/747cb73f-3f96-4f8e-82a4-cee18ab58c9d/scratchpad/wt-d2e7d27/build/benchmark/20261117-1217-regression-d2e7d27/suite/mcap/S5-c-VP-5-fc8939d6aa80_seed1.mcap |

## Trượt ngoài phạm vi chấm của ca (thông tin, không tính vào kết luận)

| Mức | Requirement | Ca | Seed | Giá trị | Ngưỡng |
|---|---|---|---|---|---|
| BLOCKER | PP-SWR-051 | S2-c-VP-0-b84bf321b14a | 1 | -0.2357 | >= 0 |
| BLOCKER | PP-SWR-051 | S2-c-VP-1-1db4613cf0cb | 1 | -0.2158 | >= 0 |
| BLOCKER | PP-SWR-051 | S2-c-VP-2-213efa4e998e | 1 | -0.3308 | >= 0 |
| BLOCKER | PP-SWR-051 | S2-c-VP-3-4e8dc883d0cd | 1 | -0.3936 | >= 0 |
| BLOCKER | PP-SWR-051 | S2-c-VP-4-255842c24eca | 1 | -0.427 | >= 0 |
| BLOCKER | PP-SWR-051 | S2-c-VP-5-9ad0657941fb | 1 | -0.55 | >= 0 |
| MINOR | PP-SWR-062 | S2-c-VP-5-9ad0657941fb | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-051 | S2-d-VP-5-a311ab7697a8 | 1 | -0.0234 | >= 0 |
| MINOR | PP-SWR-062 | S2-d-VP-5-a311ab7697a8 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-0-ff8e4ce04140 | 1 | -1.411 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-0-dc72ffbcfa45 | 1 | -1.234 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-1-c599c50726eb | 1 | -1.452 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-1-9e894e6e0e47 | 1 | -1.251 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-2-d2cc20ee8bbf | 1 | -1.417 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-2-8ea25fd5bd76 | 1 | -1.236 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-3-24dcd5adb2de | 1 | -1.409 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-3-5cf328ad0176 | 1 | -1.233 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-4-a571d2de589d | 1 | -1.376 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-4-f51e1424afde | 1 | -1.226 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-5-3f2b28b63f2e | 1 | -1.376 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-5-845fd11edffe | 1 | -1.226 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-0-cabfa230312d | 1 | -0.2637 | >= 0 |
| BLOCKER | PP-SWR-005 | S14-a-VP-0-3290c39907ee | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-0-3290c39907ee | 1 | -0.1153 | >= 0 |
| BLOCKER | PP-SWR-007 | S14-a-VP-0-3290c39907ee | 1 | 1 | = 0 |
| MINOR | PP-SWR-090 | S4b-b-VP-1-311647f45960 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S4b-c-VP-0-5f3bb8bbbdcc | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S4b-c-VP-1-6341e6253ac1 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S4b-c-VP-2-f89a9a0c7f96 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S4b-c-VP-3-23a7856ac085 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S4b-c-VP-4-f876104a11e9 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S4b-c-VP-5-e35d853524b2 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S4b-c-VP-5-e35d853524b2 | 1 | 1 | = 0 |
| MINOR | PP-SWR-090 | S4b-e-VP-0-3c6fbd348bdd | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S4b-e-VP-2-8664d4326faa | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S4b-e-VP-3-bc1154b2eab4 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S4b-e-VP-4-ee510703be24 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S5-c-VP-5-fc8939d6aa80 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-039 | S6-b-VP-4-49ce96f36822 | 1 | 2.723 | <= 0.05 |
| BLOCKER | PP-SWR-039 | S6-b-VP-5-025575367d8c | 1 | 1.725 | <= 0.05 |
| MINOR | PP-SWR-062 | S6-b-VP-5-025575367d8c | 1 | 3 | = 0 |
| MINOR | PP-SWR-090 | S7-c-VP-4-8cb3daf05752 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S7-c-VP-5-4bd69c0394ed | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S7-c-VP-5-4bd69c0394ed | 1 | 1 | = 0 |
| MINOR | PP-SWR-090 | S7-ncap-oncoming-left-6-VP-4-2a08dfdd25a8 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S7-ncap-oncoming-left-6-VP-5-cab30fbcc9c6 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S7-ncap-oncoming-left-6-VP-5-cab30fbcc9c6 | 1 | 1 | = 0 |
| MINOR | PP-SWR-090 | S8-c-VP-5-bbbfcc78ba46 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S8-c-VP-5-bbbfcc78ba46 | 1 | 1 | = 0 |
| MINOR | PP-SWR-090 | S8-ncap-overtaking-left-72-6-VP-4-f47122da8706 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S8-ncap-overtaking-left-72-6-VP-5-7ef6dcd6c783 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S8-ncap-overtaking-left-72-6-VP-5-7ef6dcd6c783 | 1 | 1 | = 0 |
| MINOR | PP-SWR-090 | S8-ncap-overtaking-left-80-6-VP-4-0cbde2b617d6 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S8-ncap-overtaking-left-80-6-VP-5-86f156f800c1 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S8-ncap-overtaking-left-80-6-VP-5-86f156f800c1 | 1 | 1 | = 0 |
| MINOR | PP-SWR-090 | S8-ncap-indicated-left-72-6-VP-0-aed1782d180f | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S8-ncap-indicated-left-80-6-VP-0-f4639fd2f64c | 1 | 1 | <= 0 |
| MINOR | PP-SWR-055 | S3b-d-VP-5-befbcf67d7a8 | 1 | 0 | > 0 |
| MINOR | PP-SWR-058 | S3b-d-VP-5-befbcf67d7a8 | 1 | 0 | > 0 |
| MINOR | PP-SWR-062 | S3b-d-VP-5-befbcf67d7a8 | 1 | 2 | = 0 |
| MINOR | PP-SWR-090 | S8b-c-VP-5-95f29b93c5d0 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S8b-c-VP-5-95f29b93c5d0 | 1 | 1 | = 0 |
| MINOR | PP-SWR-090 | S8b-d-VP-3-35bbcb740d95 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S8b-d-VP-5-5c0fcb91d951 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S8b-d-VP-5-5c0fcb91d951 | 1 | 1 | = 0 |
| MINOR | PP-SWR-090 | S8b-e-VP-3-68c659f51086 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S8b-e-VP-5-a5e9d93895f4 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S8b-e-VP-5-a5e9d93895f4 | 1 | 1 | = 0 |
| MINOR | PP-SWR-032 | S12-c-VP-0-425b042b9630 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-0-425b042b9630 | 2 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-1-c5f495806475 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-1-c5f495806475 | 2 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-2-dcd8acfe5043 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-2-dcd8acfe5043 | 2 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-3-4b7830a9f53c | 1 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-3-4b7830a9f53c | 2 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-4-406ed8c312c5 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-4-406ed8c312c5 | 2 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-5-7039c477036e | 1 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-5-7039c477036e | 2 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S13-a-VP-5-4d54367ca2b0 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-086 | S16-c-VP-0-fde743d6df3f | 1 | -0.3825 | >= -0.3 |
| BLOCKER | PP-SWR-086 | S16-c-VP-2-70ee4251d683 | 1 | -0.3599 | >= -0.3 |
| BLOCKER | PP-SWR-086 | S16-c-VP-3-7333de786139 | 1 | -0.389 | >= -0.3 |
| BLOCKER | PP-SWR-086 | S16-c-VP-4-17c9ae7cbeeb | 1 | -0.4137 | >= -0.3 |
| BLOCKER | PP-SWR-085 | S16-c-VP-5-8588c1885ba1 | 1 | -0.1121 | >= 0 |
| BLOCKER | PP-SWR-086 | S16-c-VP-5-8588c1885ba1 | 1 | -0.4586 | >= -0.3 |
| MINOR | PP-SWR-062 | S16-c-VP-5-8588c1885ba1 | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-086 | S16-d-VP-1-875c67fe6ec3 | 1 | -0.3409 | >= -0.3 |
| BLOCKER | PP-SWR-086 | S16-d-VP-2-d8db2d5453a8 | 1 | -0.4352 | >= -0.3 |
| BLOCKER | PP-SWR-086 | S16-c-VP-0-da72edc4ec56 | 1 | -0.3825 | >= -0.3 |
| BLOCKER | PP-SWR-086 | S16-c-VP-0-8573bbceb147 | 1 | -0.3822 | >= -0.3 |
| BLOCKER | PP-SWR-086 | S16-c-VP-0-6f5b10397642 | 1 | -0.3824 | >= -0.3 |
| BLOCKER | PP-SWR-051 | S17-b-VP-0-3de8f33b03db | 1 | -0.2587 | >= 0 |
| BLOCKER | PP-SWR-051 | S17-b-VP-1-e7d4b9f04c9b | 1 | -0.07919 | >= 0 |
| BLOCKER | PP-SWR-051 | S17-b-VP-2-31d7c4a6ad1f | 1 | -0.1414 | >= 0 |
| BLOCKER | PP-SWR-051 | S17-b-VP-3-d35d81d4965b | 1 | -0.2063 | >= 0 |
| BLOCKER | PP-SWR-051 | S17-b-VP-4-fce608d216a6 | 1 | -0.2749 | >= 0 |
| BLOCKER | PP-SWR-051 | S17-b-VP-5-7c84dc0ea45e | 1 | -0.3724 | >= 0 |
| MINOR | PP-SWR-062 | S17-b-VP-5-7c84dc0ea45e | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-051 | S17-c-VP-0-ec530a565153 | 1 | -5.581 | >= 0 |
| BLOCKER | PP-SWR-051 | S17-c-VP-1-2fb27134ba07 | 1 | -5.702 | >= 0 |
| BLOCKER | PP-SWR-051 | S17-c-VP-2-d36a269b1605 | 1 | -5.935 | >= 0 |
| BLOCKER | PP-SWR-051 | S17-c-VP-3-23bdadaaa5df | 1 | -6.04 | >= 0 |
| BLOCKER | PP-SWR-051 | S17-c-VP-4-7235bceb0cae | 1 | -6.074 | >= 0 |
| BLOCKER | PP-SWR-051 | S17-c-VP-5-2fa05512e157 | 1 | -6.284 | >= 0 |
| MINOR | PP-SWR-062 | S17-c-VP-5-2fa05512e157 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-051 | S17-d-VP-3-32384fa9491c | 1 | -0.0125 | >= 0 |
| BLOCKER | PP-SWR-051 | S17-d-VP-4-0847e3e773ff | 1 | -0.07952 | >= 0 |
| BLOCKER | PP-SWR-051 | S17-d-VP-5-adc239af2eb2 | 1 | -0.3932 | >= 0 |
| MINOR | PP-SWR-062 | S17-d-VP-5-adc239af2eb2 | 1 | 1 | = 0 |

## Bộ theo khía cạnh

| Bộ | Khía cạnh | Lần chạy | Kết luận | BLOCKER | MAJOR | MINOR |
|---|---|---|---|---|---|---|
| B0 | Conformance | — | Đạt C1, C2; Tích hợp được | — | — | — |
| B1 | Nominal | 922 | Không đạt | 7 | 0 | 0 |
| B2 | Regulatory | 594 | Không đạt | 6 | 0 | 0 |
| B3 | Performance limit | 295 | Không đạt | 14 | 0 | 2 |
| B4 | Robustness | 868 | Không đạt | 30 | 0 | 44 |
| B5 | Degradation and refusal | 312 | Không đạt | 12 | 0 | 0 |
| B6 | Comfort | 922 | Không đạt | 7 | 0 | 0 |
| B7 | Flexibility | 803 | Không đạt | 15 | 0 | 21 |
| B8 | Compute | 2085 | Không đạt | 51 | 0 | 46 |

## Số lần chạy

```json
{
 "planned": 2085,
 "executed": 2085,
 "failed": 90,
 "failed_out_of_scope": 90,
 "errors": 0,
 "execution_faults": 0,
 "partial": false
}
```

## Flexibility

Cùng bản build và bộ calibration trên mọi profile (mục 8.3). Ô là giá trị xấu nhất của profile trên các ca chạy đủ mọi profile; **đậm** là profile tệ nhất của chỉ số. Bộ chạy là B7. Tỉ lệ đạt requirement: số requirement không trượt ở lần chạy nào của profile, chia số requirement được chấm trên profile đó.

| Profile | Lần chạy | Tỉ lệ đạt requirement | Requirement trượt | PP-SWR-002 a_y thêm vào lớn nhất khi đưa về giữa | PP-SWR-004 Jerk ngang RMS của path 0–1 s khi HWA lái | PP-SWR-004 Jerk ngang lớn nhất của path khi HWA lái (trung bình 0,5 s) | PP-SWR-004 Tốc độ quay vô lăng RMS khi HWA lái, vòng kín | PP-SWR-050 Lệch ngang của path so với tâm làn thật, 0–1 s, lớn nhất | PP-SWR-053 Thời gian đưa xe về giữa (lệch ≤ 0,1 m) | PP-SWR-057 Khoảng cách ngang nhỏ nhất từ thân xe tới xe lớn khi ngang hàng | PP-SWR-059 Thời gian từ lúc hết ngang hàng tới lúc lệch ≤ 0,1 m | PP-SWR-081 Thời lượng path LKA tới COMPLETED | PP-SWR-082 Thời lượng path ELK tới COMPLETED | PP-SWR-087 DTLE LKA nhỏ nhất |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VP-0 | 210 | 93.3% | PP-SWR-032, PP-SWR-051 | 1.4 | 0.293 | 1.54 | 0.191 | 1.04 | 3.63 | 0.634 | 4.97 | 4.45 | 3.77 | -0.00941 |
| VP-1 | 145 | 93.5% | PP-SWR-032, PP-SWR-051 | **1.62** | **0.339** | **1.55** | 0.191 | 0.984 | 3.34 | 0.611 | **5.02** | 4.17 | 3.5 | 0.00715 |
| VP-2 | 103 | 96.9% | PP-SWR-032 | 1.44 | 0.302 | 1.54 | 0.191 | 1.03 | 3.57 | 0.531 | 5.02 | 4.38 | 3.72 | 0.00277 |
| VP-3 | 102 | 90.3% | PP-SWR-032, PP-SWR-085, PP-SWR-090 | 1.39 | 0.291 | 1.54 | 0.191 | 1.04 | 3.64 | 0.479 | 5 | 4.45 | 3.8 | -0.00949 |
| VP-4 | 102 | 90.3% | PP-SWR-032, PP-SWR-086, PP-SWR-102 | 1.35 | 0.285 | 1.54 | **0.192** | **1.05** | **3.69** | 0.452 | 5 | **4.52** | **3.85** | -0.00993 |
| VP-5 | 141 | 84.8% | PP-SWR-032, PP-SWR-051, PP-SWR-085, PP-SWR-086, PP-SWR-090 | 1.35 | 0.285 | 1.54 | 0.192 | 1.05 | 3.69 | **0.326** | 4 | 4.52 | 3.85 | **-0.0221** |

| Chỉ số | Độ chênh lớn nhất giữa profile | Độ chênh nhỏ nhất | Profile tệ nhất |
|---|---|---|---|
| PP-SWR-002 a_y thêm vào lớn nhất khi đưa về giữa | 0.274 | 0 | VP-1 |
| PP-SWR-004 Jerk ngang RMS của path 0–1 s khi HWA lái | 0.0578 | 7.37e-06 | VP-1 |
| PP-SWR-004 Jerk ngang lớn nhất của path khi HWA lái (trung bình 0,5 s) | 0.438 | 0 | VP-1 |
| PP-SWR-004 Tốc độ quay vô lăng RMS khi HWA lái, vòng kín | 0.0121 | 0.000493 | VP-4 |
| PP-SWR-050 Lệch ngang của path so với tâm làn thật, 0–1 s, lớn nhất | 0.158 | 0 | VP-4 |
| PP-SWR-053 Thời gian đưa xe về giữa (lệch ≤ 0,1 m) | 0.35 | 0 | VP-4 |
| PP-SWR-057 Khoảng cách ngang nhỏ nhất từ thân xe tới xe lớn khi ngang hàng | 0.308 | 0.242 | VP-5 |
| PP-SWR-059 Thời gian từ lúc hết ngang hàng tới lúc lệch ≤ 0,1 m | 4.85 | 1.02 | VP-1 |
| PP-SWR-081 Thời lượng path LKA tới COMPLETED | 0.525 | 0 | VP-4 |
| PP-SWR-082 Thời lượng path ELK tới COMPLETED | 1.37 | 0 | VP-4 |
| PP-SWR-087 DTLE LKA nhỏ nhất | 0.117 | 0.00805 | VP-5 |

Requirement đạt 100 % trên mọi profile: không (VP-0, VP-1, VP-2, VP-3, VP-4, VP-5)

## Thời gian tính

1701970 chu kỳ. p95 ≤ 0.794 ms, p99 ≤ 1 ms (cận trên của bin), lớn nhất 140 ms. Đo trên máy chạy SIL, gồm adapter; không khẳng định thời gian trên ECU (mục 9.1).

![Thời gian tính](figures/compute.png)

## DTLE theo v_lat

| Kịch bản | v_lat [m/s] | DTLE nhỏ nhất [m] |
|---|---|---|
| S4 | 0 | 0.0679 |
| S4 | 0.2 | 0.0983 |
| S4 | 0.3 | 0.127 |
| S4 | 0.4 | 0.147 |
| S4 | 0.5 | 0.0633 |
| S4 | 0.6 | -0.0221 |
| S4b | 0.2 | 0.0969 |
| S4b | 0.3 | 0.112 |
| S4b | 0.6 | 0.171 |
| S5 | 0.2 | 0.0326 |
| S5 | 0.3 | 0.0341 |
| S5 | 0.4 | 0.0314 |
| S5 | 0.5 | 0.0396 |
| S5 | 0.6 | 0.0408 |
| S6 | 0.2 | 0.0326 |
| S6 | 0.3 | 0.0341 |
| S6 | 0.4 | 0.0341 |
| S6 | 0.5 | 0.0396 |
| S6 | 0.6 | -0.36 |
| S7 | 0.2 | -0.163 |
| S7 | 0.3 | 0.134 |
| S7 | 0.4 | 0.156 |
| S7 | 0.5 | 0.186 |
| S7 | 0.6 | 0.0984 |
| S8 | 0.2 | 0.0465 |
| S8 | 0.3 | 0.0497 |
| S8 | 0.4 | 0.0546 |
| S8 | 0.5 | 0.0571 |
| S8 | 0.6 | 0.0624 |
| S8 | 0.7 | 0.0616 |
| S8b | 0.5 | -0.319 |
| S8c | 0.4 | 0.279 |

![DTLE theo v_lat](figures/dtle_v_lat.png)

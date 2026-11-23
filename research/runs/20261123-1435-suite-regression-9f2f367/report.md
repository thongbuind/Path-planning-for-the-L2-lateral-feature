# Kết luận: Không đạt

- Planner: pp_lcc 0.3.0 commit 9f2f367c04a6 calibration 2432aea753bc t7 quintic (91694d77e862) / pp_lkaelk 0.3.0 commit 9f2f367c04a6 calibration 2432aea753bc (1c54a8ccd771)
- Simulator: commit 9f2f367 (simulator và bên chấm), behavior_checksum/2, run_bundle/1; chưa model nào trong 9 model được validation với dữ liệu thật (Simulation Handbook mục 9, 15)
- Tích hợp được: có
- Đã chạy: 2310 lần chạy; trượt BLOCKER 20, MAJOR 0, MINOR 43; 10 ca không được chấm
- Kết luận chỉ đúng trong phạm vi đã thử, không phải bằng chứng an toàn (Software Qualification Test Specification 3).

## Trượt BLOCKER

| Requirement | Safety goal | Ca | Profile | Seed | Trượt đầu tiên [s] | Giá trị | Ngưỡng | Chi tiết | MCAP |
|---|---|---|---|---|---|---|---|---|---|
| PP-SWR-051 | SG-01 | F02-e-S1a-VP-5-29183b65ffaf | VP-5 | 1 | — | -0.1106 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F02-e-S1a-VP-5-29183b65ffaf_seed1.mcap |
| PP-SWR-051 | SG-01 | F02-e-S1c-VP-5-50d3444b79d5 | VP-5 | 1 | — | -0.1491 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F02-e-S1c-VP-5-50d3444b79d5_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1a-VP-5-9e2995fea291 | VP-5 | 1 | — | -0.2729 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F06-d-S1a-VP-5-9e2995fea291_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1c-VP-5-bdab3c9103b7 | VP-5 | 1 | — | -0.2797 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F06-d-S1c-VP-5-bdab3c9103b7_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-b-S1c-VP-1-297eab73e001 | VP-1 | 1 | — | -0.3463 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F08-b-S1c-VP-1-297eab73e001_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-b-S1c-VP-5-9d66d718191a | VP-5 | 1 | — | -0.1948 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F08-b-S1c-VP-5-9d66d718191a_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1c-VP-0-bca0f1afb997 | VP-0 | 1 | — | -0.9853 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F08-c-S1c-VP-0-bca0f1afb997_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1c-VP-1-3d8334644eea | VP-1 | 1 | — | -1.017 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F08-c-S1c-VP-1-3d8334644eea_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1c-VP-5-06d7bb8fda8b | VP-5 | 1 | — | -1.269 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F08-c-S1c-VP-5-06d7bb8fda8b_seed1.mcap |
| PP-SWR-063 | SG-01 | S19-f-VP-5-9c4f0f44d054 | VP-5 | 1 | — | 0.008746 | = 1 | Tỉ lệ chu kỳ có path hợp lệ báo lane_too_narrow khi khoảng trống thật < free_space_min | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/S19-f-VP-5-9c4f0f44d054_seed1.mcap |
| PP-SWR-088 | SG-03 | S7-a-VP-0-ea43d4a89263 | VP-0 | 1 | — | 0.2871 | >= 0.3 | Khoảng cách ngang nhỏ nhất tới xe mục tiêu [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/S7-a-VP-0-ea43d4a89263_seed1.mcap |
| PP-SWR-094 | SG-01 | S12-d-VP-0-aa6a4007e24f | VP-0 | 1 | — | 0.1288 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/S12-d-VP-0-aa6a4007e24f_seed1.mcap |
| PP-SWR-094 | SG-01 | S12-d-VP-1-32e05ce9da2f | VP-1 | 1 | — | 0.1169 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/S12-d-VP-1-32e05ce9da2f_seed1.mcap |
| PP-SWR-094 | SG-01 | S12-d-VP-2-f8db4bffd193 | VP-2 | 1 | — | 0.1262 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/S12-d-VP-2-f8db4bffd193_seed1.mcap |
| PP-SWR-094 | SG-01 | S12-d-VP-3-0739ffa64fa8 | VP-3 | 1 | — | 0.1295 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/S12-d-VP-3-0739ffa64fa8_seed1.mcap |
| PP-SWR-094 | SG-01 | S12-d-VP-4-6c8c429307ff | VP-4 | 1 | — | 0.1324 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/S12-d-VP-4-6c8c429307ff_seed1.mcap |
| PP-SWR-094 | SG-01 | S12-d-VP-5-6c4d792cde2a | VP-5 | 1 | — | 0.1329 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/S12-d-VP-5-6c4d792cde2a_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-c-S1c-VP-0-bca0f1afb997 | VP-0 | 1 | 15.16 | 1.142 | <= 1 | Lệch ngang giữa hai path liên tiếp / ngưỡng của khoảng | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F08-c-S1c-VP-0-bca0f1afb997_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-c-S1c-VP-1-3d8334644eea | VP-1 | 1 | 7.383 | 1.14 | <= 1 | Lệch ngang giữa hai path liên tiếp / ngưỡng của khoảng | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F08-c-S1c-VP-1-3d8334644eea_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-c-S1c-VP-5-06d7bb8fda8b | VP-5 | 1 | 15.21 | 1.142 | <= 1 | Lệch ngang giữa hai path liên tiếp / ngưỡng của khoảng | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F08-c-S1c-VP-5-06d7bb8fda8b_seed1.mcap |

## Trượt MINOR

| Requirement | Safety goal | Ca | Profile | Seed | Trượt đầu tiên [s] | Giá trị | Ngưỡng | Chi tiết | MCAP |
|---|---|---|---|---|---|---|---|---|---|
| PP-SWR-032 | — | F01-c-S4a_at_lka_activep0-VP-4-914355537c7d | VP-4 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F01-c-S4a_at_lka_activep0-VP-4-914355537c7d_seed1.mcap |
| PP-SWR-032 | — | F01-c-S4a_at_lka_activep0-VP-4-914355537c7d | VP-4 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F01-c-S4a_at_lka_activep0-VP-4-914355537c7d_seed2.mcap |
| PP-SWR-032 | — | F01-c-S4a_at_lka_activep0.2-VP-5-2e109dc103db | VP-5 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F01-c-S4a_at_lka_activep0.2-VP-5-2e109dc103db_seed2.mcap |
| PP-SWR-032 | — | F01-c-S5a_at_elk_activep0-VP-4-d7e0b59fbf4d | VP-4 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F01-c-S5a_at_elk_activep0-VP-4-d7e0b59fbf4d_seed1.mcap |
| PP-SWR-032 | — | F01-c-S5a_at_elk_activep0-VP-4-d7e0b59fbf4d | VP-4 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F01-c-S5a_at_elk_activep0-VP-4-d7e0b59fbf4d_seed2.mcap |
| PP-SWR-032 | — | F01-c-S5a_at_elk_activep0.2-VP-5-fbea90d7d4d0 | VP-5 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F01-c-S5a_at_elk_activep0.2-VP-5-fbea90d7d4d0_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-0-944a5944b2f0 | VP-0 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/G01-S4c-VP-0-944a5944b2f0_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-1-d9c02f4d85c9 | VP-1 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/G01-S4c-VP-1-d9c02f4d85c9_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-2-19b08e51426b | VP-2 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/G01-S4c-VP-2-19b08e51426b_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-3-9991783c316d | VP-3 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/G01-S4c-VP-3-9991783c316d_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-4-072664ac9b98 | VP-4 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/G01-S4c-VP-4-072664ac9b98_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-5-26df2868e70c | VP-5 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/G01-S4c-VP-5-26df2868e70c_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-0-69e53aeef11a | VP-0 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/S12-b-VP-0-69e53aeef11a_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-1-4b3e70a50a26 | VP-1 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/S12-b-VP-1-4b3e70a50a26_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-2-0962daddf5bd | VP-2 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/S12-b-VP-2-0962daddf5bd_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-3-984dbaa7f733 | VP-3 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/S12-b-VP-3-984dbaa7f733_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-4-a4945d3bcd67 | VP-4 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/S12-b-VP-4-a4945d3bcd67_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-5-2b777db332c0 | VP-5 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/S12-b-VP-5-2b777db332c0_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-5-2b777db332c0 | VP-5 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/S12-b-VP-5-2b777db332c0_seed2.mcap |
| PP-SWR-032 | — | S20-a-VP-2-1a3aca6c43ec | VP-2 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/S20-a-VP-2-1a3aca6c43ec_seed1.mcap |
| PP-SWR-062 | — | S19-f-VP-5-9c4f0f44d054 | VP-5 | 1 | — | 1 | = 0 | Requirement trượt ở biên ODD | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/S19-f-VP-5-9c4f0f44d054_seed1.mcap |
| PP-SWR-084 | — | F02-e-S4a_at_lka_activep0-VP-2-c5082f1b14ba | VP-2 | 1 | — | 0.6282 | <= 0.2 | Lệch tâm khi LKA hoặc ELK COMPLETED [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F02-e-S4a_at_lka_activep0-VP-2-c5082f1b14ba_seed1.mcap |
| PP-SWR-084 | — | F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0 | VP-3 | 1 | — | -0.03123 | >= 0 | DLC nhỏ nhất ở hai phía khi LKA hoặc ELK COMPLETED [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0_seed1.mcap |
| PP-SWR-084 | — | F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0 | VP-3 | 1 | — | 0.617 | <= 0.2 | Lệch tâm khi LKA hoặc ELK COMPLETED [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0_seed1.mcap |
| PP-SWR-084 | — | F02-e-S5a_at_elk_activep0-VP-2-29b21e6b793a | VP-2 | 1 | — | 0.6125 | <= 0.2 | Lệch tâm khi LKA hoặc ELK COMPLETED [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F02-e-S5a_at_elk_activep0-VP-2-29b21e6b793a_seed1.mcap |
| PP-SWR-084 | — | F02-e-S5a_at_elk_activep0.2-VP-3-bb766866f0d0 | VP-3 | 1 | — | -0.02195 | >= 0 | DLC nhỏ nhất ở hai phía khi LKA hoặc ELK COMPLETED [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F02-e-S5a_at_elk_activep0.2-VP-3-bb766866f0d0_seed1.mcap |
| PP-SWR-084 | — | F02-e-S5a_at_elk_activep0.2-VP-3-bb766866f0d0 | VP-3 | 1 | — | 0.6082 | <= 0.2 | Lệch tâm khi LKA hoặc ELK COMPLETED [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F02-e-S5a_at_elk_activep0.2-VP-3-bb766866f0d0_seed1.mcap |
| PP-SWR-090 | — | F01-c-S5a_at_elk_activep0-VP-4-d7e0b59fbf4d | VP-4 | 2 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F01-c-S5a_at_elk_activep0-VP-4-d7e0b59fbf4d_seed2.mcap |
| PP-SWR-090 | — | F02-e-S4a_at_lka_activep0-VP-2-c5082f1b14ba | VP-2 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F02-e-S4a_at_lka_activep0-VP-2-c5082f1b14ba_seed1.mcap |
| PP-SWR-090 | — | F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0 | VP-3 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0_seed1.mcap |
| PP-SWR-090 | — | F02-e-S5a_at_elk_activep0-VP-2-29b21e6b793a | VP-2 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F02-e-S5a_at_elk_activep0-VP-2-29b21e6b793a_seed1.mcap |
| PP-SWR-090 | — | F02-e-S5a_at_elk_activep0.2-VP-3-bb766866f0d0 | VP-3 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F02-e-S5a_at_elk_activep0.2-VP-3-bb766866f0d0_seed1.mcap |
| PP-SWR-090 | — | G01-S4c-VP-0-944a5944b2f0 | VP-0 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/G01-S4c-VP-0-944a5944b2f0_seed1.mcap |
| PP-SWR-090 | — | G01-S4c-VP-3-9991783c316d | VP-3 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/G01-S4c-VP-3-9991783c316d_seed1.mcap |
| PP-SWR-090 | — | G01-S4c-VP-4-072664ac9b98 | VP-4 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/G01-S4c-VP-4-072664ac9b98_seed1.mcap |
| PP-SWR-090 | — | S12-b-VP-2-0962daddf5bd | VP-2 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/S12-b-VP-2-0962daddf5bd_seed1.mcap |
| PP-SWR-170 | — | F25-c-S22a-VP-0-191326001926 | VP-0 | 1 | — | 1 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F25-c-S22a-VP-0-191326001926_seed1.mcap |
| PP-SWR-170 | — | F25-c-S22a-VP-1-42edbe799a5c | VP-1 | 1 | — | 1 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F25-c-S22a-VP-1-42edbe799a5c_seed1.mcap |
| PP-SWR-170 | — | F25-c-S22a-VP-5-dc4b57212bae | VP-5 | 1 | — | 1 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F25-c-S22a-VP-5-dc4b57212bae_seed1.mcap |
| PP-SWR-170 | — | F25-d-S22a-VP-0-deb4c617404b | VP-0 | 1 | — | 1 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F25-d-S22a-VP-0-deb4c617404b_seed1.mcap |
| PP-SWR-170 | — | F25-d-S22a-VP-1-294c7b39bdf1 | VP-1 | 1 | — | 1 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F25-d-S22a-VP-1-294c7b39bdf1_seed1.mcap |
| PP-SWR-170 | — | F25-d-S22a-VP-5-425685eb4bcc | VP-5 | 1 | — | 1 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F25-d-S22a-VP-5-425685eb4bcc_seed1.mcap |
| PP-SWR-170 | — | F25-e-S22a-VP-5-fb5ac378351a | VP-5 | 1 | — | 1 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1434-regression-9f2f367/suite/mcap/F25-e-S22a-VP-5-fb5ac378351a_seed1.mcap |

## Ca không được chấm

| Ca | Seed | Lý do |
|---|---|---|
| S22-b-VP-0-8164b3daec3e | 1 | S22b: chưa quan sát FOLLOW tới giới hạn 30 m rồi hết cửa sổ T_coast |
| S22-b-VP-1-582804600d03 | 1 | S22b: chưa quan sát FOLLOW tới giới hạn 30 m rồi hết cửa sổ T_coast |
| S22-b-VP-2-8d3c37c7f1c4 | 1 | S22b: chưa quan sát FOLLOW tới giới hạn 30 m rồi hết cửa sổ T_coast |
| S22-b-VP-3-f36ffd799338 | 1 | S22b: chưa quan sát FOLLOW tới giới hạn 30 m rồi hết cửa sổ T_coast |
| S22-b-VP-4-7f58abaa6cee | 1 | S22b: chưa quan sát FOLLOW tới giới hạn 30 m rồi hết cửa sổ T_coast |
| S22-b-VP-5-a7e1dee3be4c | 1 | S22b: chưa quan sát FOLLOW tới giới hạn 30 m rồi hết cửa sổ T_coast |
| S9-a-VP-2-5bb051a1b54a-lcc-only | 1 | PP-SWR-181: thiếu điều kiện để chấm planner chạy độc lập |
| S9-a-VP-3-b54b502a1c35-lcc-only | 1 | PP-SWR-181: thiếu điều kiện để chấm planner chạy độc lập |
| S9-a-VP-4-5a91eb7dfd98-lcc-only | 1 | PP-SWR-181: thiếu điều kiện để chấm planner chạy độc lập |
| S9-a-VP-5-6fda0ebe7bd8-lcc-only | 1 | PP-SWR-181: thiếu điều kiện để chấm planner chạy độc lập |

## Trượt ngoài phạm vi chấm của ca (thông tin, không tính vào kết luận)

| Mức | Requirement | Ca | Seed | Giá trị | Ngưỡng |
|---|---|---|---|---|---|
| BLOCKER | PP-SWR-006 | S14-e-VP-0-ff8e4ce04140 | 1 | -1.433 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-0-dc72ffbcfa45 | 1 | -1.238 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-1-c599c50726eb | 1 | -1.478 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-1-9e894e6e0e47 | 1 | -1.26 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-2-d2cc20ee8bbf | 1 | -1.444 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-2-8ea25fd5bd76 | 1 | -1.246 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-3-24dcd5adb2de | 1 | -1.432 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-3-5cf328ad0176 | 1 | -1.238 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-4-a571d2de589d | 1 | -1.427 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-4-f51e1424afde | 1 | -1.235 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-5-3f2b28b63f2e | 1 | -1.427 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-5-845fd11edffe | 1 | -1.235 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-0-cabfa230312d | 1 | -0.1895 | >= 0 |
| MINOR | PP-SWR-032 | S4b-c-VP-0-5f3bb8bbbdcc | 1 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S4b-c-VP-1-6341e6253ac1 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S6-c-VP-5-c9c129cfa590 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S6-c-VP-5-c9c129cfa590 | 1 | 1 | = 0 |
| MINOR | PP-SWR-090 | S6-ncap-edge-dashed-right-6-VP-5-49871ee9baf9 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S6-ncap-edge-dashed-right-6-VP-5-49871ee9baf9 | 1 | 1 | = 0 |
| MINOR | PP-SWR-055 | S3b-d-VP-5-befbcf67d7a8 | 1 | 0 | > 0 |
| MINOR | PP-SWR-058 | S3b-d-VP-5-befbcf67d7a8 | 1 | 0 | > 0 |
| MINOR | PP-SWR-062 | S3b-d-VP-5-befbcf67d7a8 | 1 | 2 | = 0 |
| MINOR | PP-SWR-032 | S12-c-VP-0-425b042b9630 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-1-c5f495806475 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-2-dcd8acfe5043 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-3-4b7830a9f53c | 1 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-4-406ed8c312c5 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-5-7039c477036e | 1 | 1 | <= 0 |
| BLOCKER | PP-SWR-086 | S16-c-VP-5-8588c1885ba1 | 1 | -0.4879 | >= -0.3 |
| MINOR | PP-SWR-062 | S16-c-VP-5-8588c1885ba1 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-171 | S22-e-VP-0-6a0b15bf41ce | 1 | 7 | = 0 |
| BLOCKER | PP-SWR-171 | S22-e-VP-1-cb77b9982ed7 | 1 | 7 | = 0 |
| BLOCKER | PP-SWR-171 | S22-e-VP-2-7e815a10acd8 | 1 | 6 | = 0 |
| BLOCKER | PP-SWR-171 | S22-e-VP-3-315220d56377 | 1 | 6 | = 0 |
| BLOCKER | PP-SWR-171 | S22-e-VP-4-e573fdd87cfc | 1 | 7 | = 0 |
| BLOCKER | PP-SWR-171 | S22-e-VP-5-876e2407c39d | 1 | 9 | = 0 |
| BLOCKER | PP-SWR-177 | F02-a-S1a-VP-0-03f9aa55c220 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-a-S1a-VP-1-c2b686f96a0f | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-a-S1a-VP-5-495c5d9579bb | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-b-S1a-VP-0-588ef0de14fa | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-b-S1a-VP-1-b9637d7adb6d | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-b-S1a-VP-5-0ede763cd7e6 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-c-S1a-VP-0-c2a0635dfaa8 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-c-S1a-VP-1-071fab324605 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-c-S1a-VP-5-8356182dd429 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-d-S1a-VP-0-6b765cd3d54d | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-177 | F02-d-S1a-VP-1-5d5632b2a7b8 | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-177 | F02-d-S1a-VP-5-bc5aa75a38bc | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-177 | F02-e-S1a-VP-0-6b44a28b9988 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-e-S1a-VP-1-06c41012e265 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-e-S1a-VP-5-29183b65ffaf | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-a-S1a-VP-0-09281c9387be | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-177 | F02-a-S1a-VP-0-2ea080fdbaf6 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-a-S1a-VP-0-3885a49d104c | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-a-S1a-VP-0-59ceca94550d | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-a-S1c-VP-0-968b6b33d208 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-a-S1c-VP-1-272e6eeb7876 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-a-S1c-VP-5-24abae5ae155 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-b-S1c-VP-0-e41f41a94a55 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-b-S1c-VP-1-4372bc04d974 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-b-S1c-VP-5-2a0abd42e6a5 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-c-S1c-VP-0-1d5b329983a3 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-c-S1c-VP-1-5ff648de8b5e | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-c-S1c-VP-5-59d54780ce4c | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-d-S1c-VP-0-e2d95f2acdac | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-177 | F02-d-S1c-VP-1-6fc53dfb81c0 | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-177 | F02-d-S1c-VP-5-7be0a49e21e1 | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-177 | F02-e-S1c-VP-0-4e53e9fcde7b | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-e-S1c-VP-1-6cfe9ba031f0 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-e-S1c-VP-5-50d3444b79d5 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-a-S1c-VP-0-320eecf936e3 | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-177 | F02-a-S1c-VP-0-dbb3f96c56ca | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-a-S1c-VP-0-cfc05257709a | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F02-a-S1c-VP-0-69dee6e0acbb | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-a-S1a-VP-0-80f1becb446a | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-a-S1a-VP-1-cbe75d17374b | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-a-S1a-VP-5-e8fc0fb072e3 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-b-S1a-VP-0-46da72dcd782 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-b-S1a-VP-1-ce7e7e39c2ab | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-b-S1a-VP-5-cc03ac29fdde | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-c-S1a-VP-0-30e82c76c3b1 | 1 | 30 | = 0 |
| BLOCKER | PP-SWR-177 | F06-c-S1a-VP-1-6b570b993a18 | 1 | 30 | = 0 |
| BLOCKER | PP-SWR-177 | F06-c-S1a-VP-5-8b671013e181 | 1 | 30 | = 0 |
| BLOCKER | PP-SWR-177 | F06-d-S1a-VP-0-24550cfc95c5 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-d-S1a-VP-1-3a4b29f3fe5b | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-d-S1a-VP-5-9e2995fea291 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-e-S1a-VP-0-32d8e11b13a4 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-e-S1a-VP-1-5196def8dd8f | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-e-S1a-VP-5-a76b71e5c69c | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-a-S1a-VP-0-3397774191aa | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-a-S1a-VP-0-1f040b41d9e1 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-a-S1a-VP-0-5158987ade9c | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-a-S1a-VP-0-9ae034e25470 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-a-S1c-VP-0-868c0af677ac | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-a-S1c-VP-1-b4b47edd75f6 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-a-S1c-VP-5-03661768786f | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-b-S1c-VP-0-d617705779af | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-b-S1c-VP-1-6a696f8d0446 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-b-S1c-VP-5-545957874102 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-c-S1c-VP-0-10a0d5eaaabe | 1 | 30 | = 0 |
| BLOCKER | PP-SWR-177 | F06-c-S1c-VP-1-2173028b2f9c | 1 | 30 | = 0 |
| BLOCKER | PP-SWR-177 | F06-c-S1c-VP-5-a0b8ff4879e1 | 1 | 30 | = 0 |
| BLOCKER | PP-SWR-177 | F06-d-S1c-VP-0-608ec3b8fc9f | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-d-S1c-VP-1-40397bd3efa4 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-d-S1c-VP-5-bdab3c9103b7 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-e-S1c-VP-0-21907f19a036 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-e-S1c-VP-1-1f3d70de82c2 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-e-S1c-VP-5-87266b531a26 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-a-S1c-VP-0-cd7c41428ff3 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-a-S1c-VP-0-4e752ad53686 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-a-S1c-VP-0-aed66d9b07f6 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F06-a-S1c-VP-0-5178b8cf8034 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-061 | F08-c-S1c-VP-0-bca0f1afb997 | 1 | 1.142 | <= 1 |
| BLOCKER | PP-SWR-061 | F08-c-S1c-VP-1-3d8334644eea | 1 | 1.14 | <= 1 |
| BLOCKER | PP-SWR-061 | F08-c-S1c-VP-5-06d7bb8fda8b | 1 | 1.142 | <= 1 |
| BLOCKER | PP-SWR-177 | F15-c-S1a-VP-0-1759e7623f79 | 1 | 16 | = 0 |
| BLOCKER | PP-SWR-177 | F15-c-S1a-VP-1-ee83c26fa37b | 1 | 16 | = 0 |
| BLOCKER | PP-SWR-177 | F15-c-S1a-VP-5-36b99b375e24 | 1 | 16 | = 0 |
| BLOCKER | PP-SWR-177 | F15-c-S1c-VP-0-10538de9a5b7 | 1 | 16 | = 0 |
| BLOCKER | PP-SWR-177 | F15-c-S1c-VP-1-768b8651648e | 1 | 16 | = 0 |
| BLOCKER | PP-SWR-177 | F15-c-S1c-VP-5-8bd5e66f138e | 1 | 16 | = 0 |
| BLOCKER | PP-SWR-177 | G01-S1c-VP-0-1467a0e9844f | 1 | 14 | = 0 |
| BLOCKER | PP-SWR-177 | G01-S1c-VP-0-1467a0e9844f | 2 | 8 | = 0 |
| BLOCKER | PP-SWR-177 | G01-S1c-VP-1-15c9123704b8 | 1 | 14 | = 0 |
| BLOCKER | PP-SWR-177 | G01-S1c-VP-1-15c9123704b8 | 2 | 8 | = 0 |
| BLOCKER | PP-SWR-177 | G01-S1c-VP-2-b56ea41bbee2 | 1 | 14 | = 0 |
| BLOCKER | PP-SWR-177 | G01-S1c-VP-2-b56ea41bbee2 | 2 | 8 | = 0 |
| BLOCKER | PP-SWR-177 | G01-S1c-VP-3-0970d8d23b03 | 1 | 14 | = 0 |
| BLOCKER | PP-SWR-177 | G01-S1c-VP-3-0970d8d23b03 | 2 | 8 | = 0 |
| BLOCKER | PP-SWR-177 | G01-S1c-VP-4-e79aef633429 | 1 | 14 | = 0 |
| BLOCKER | PP-SWR-177 | G01-S1c-VP-4-e79aef633429 | 2 | 8 | = 0 |
| BLOCKER | PP-SWR-177 | G01-S1c-VP-5-38898514a806 | 1 | 14 | = 0 |
| BLOCKER | PP-SWR-177 | G01-S1c-VP-5-38898514a806 | 2 | 8 | = 0 |

## Bộ theo khía cạnh

| Bộ | Khía cạnh | Lần chạy | Kết luận | BLOCKER | MAJOR | MINOR |
|---|---|---|---|---|---|---|
| B0 | Conformance | — | Đạt C1, C2; Tích hợp được | — | — | — |
| B1 | Nominal | 1004 | Không đạt | 1 | 0 | 1 |
| B2 | Regulatory | 594 | Đạt trong phạm vi đã thử | 0 | 0 | 0 |
| B3 | Performance limit | 311 | Không đạt | 1 | 0 | 1 |
| B4 | Robustness | 995 | Không đạt | 18 | 0 | 41 |
| B5 | Degradation and refusal | 400 | Không đạt | 1 | 0 | 8 |
| B6 | Comfort | 1004 | Không đạt | 1 | 0 | 1 |
| B7 | Flexibility | 804 | Không đạt | 6 | 0 | 18 |
| B8 | Compute | 2310 | Không đạt | 20 | 0 | 43 |

## Số lần chạy

```json
{
 "planned": 2310,
 "executed": 2310,
 "failed": 52,
 "failed_out_of_scope": 128,
 "errors": 0,
 "execution_faults": 0,
 "not_judged": 10,
 "partial": false
}
```

## Flexibility

Cùng bản build và bộ calibration trên mọi profile (mục 8.3). Ô là giá trị xấu nhất của profile trên các ca chạy đủ mọi profile; **đậm** là profile tệ nhất của chỉ số. Bộ chạy là B7. Tỉ lệ đạt requirement: số requirement không trượt ở lần chạy nào của profile, chia số requirement được chấm trên profile đó.

| Profile | Lần chạy | Tỉ lệ đạt requirement | Requirement trượt | PP-SWR-002 a_y thêm vào lớn nhất khi đưa về giữa | PP-SWR-004 Jerk ngang RMS của path 0–1 s khi HWA lái | PP-SWR-004 Jerk ngang lớn nhất của path khi HWA lái (trung bình 0,5 s) | PP-SWR-004 Tốc độ quay vô lăng RMS khi HWA lái, vòng kín | PP-SWR-050 Lệch ngang của path so với tâm làn thật, 0–1 s, lớn nhất | PP-SWR-053 Thời gian đưa xe về giữa (lệch ≤ 0,1 m) | PP-SWR-057 Khoảng cách ngang nhỏ nhất từ thân xe tới xe lớn khi ngang hàng | PP-SWR-059 Thời gian từ lúc hết ngang hàng tới lúc lệch ≤ 0,1 m | PP-SWR-081 Thời lượng path LKA tới COMPLETED | PP-SWR-082 Thời lượng path ELK tới COMPLETED | PP-SWR-087 DTLE LKA nhỏ nhất |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VP-0 | 210 | 97.0% | PP-SWR-088 | **0.441** | 0.287 | 1.58 | 0.0773 | 0.521 | 3.09 | 0.588 | 1.65 | **5.52** | **5.05** | **0.0189** |
| VP-1 | 145 | 100.0% | — | 0.441 | 0.282 | **1.58** | **0.0797** | 0.514 | **3.2** | 0.558 | 1.5 | 5.5 | 5.02 | 0.036 |
| VP-2 | 103 | 94.3% | PP-SWR-084, PP-SWR-090 | 0.441 | 0.287 | 1.58 | 0.0777 | 0.519 | 3.11 | 0.483 | 1.7 | 5.42 | 4.95 | 0.0347 |
| VP-3 | 102 | 94.1% | PP-SWR-084, PP-SWR-090 | 0.441 | 0.288 | 1.57 | 0.0772 | 0.521 | 3.09 | 0.433 | 1.67 | 5.35 | 4.9 | 0.019 |
| VP-4 | 102 | 94.1% | PP-SWR-032, PP-SWR-090 | 0.441 | **0.288** | 1.57 | 0.0768 | **0.523** | 3.07 | 0.41 | **1.72** | 5.3 | 4.88 | 0.0194 |
| VP-5 | 142 | 88.9% | PP-SWR-032, PP-SWR-051, PP-SWR-062, PP-SWR-063 | 0.0919 | 0.288 | 1.57 | 0.0492 | 0.404 | 1.95 | **0.287** | 1.72 | 4.65 | 4.2 | 0.0194 |

| Chỉ số | Độ chênh lớn nhất giữa profile | Độ chênh nhỏ nhất | Profile tệ nhất |
|---|---|---|---|
| PP-SWR-002 a_y thêm vào lớn nhất khi đưa về giữa | 0.441 | 0 | VP-0 |
| PP-SWR-004 Jerk ngang RMS của path 0–1 s khi HWA lái | 0.0138 | 3.15e-06 | VP-4 |
| PP-SWR-004 Jerk ngang lớn nhất của path khi HWA lái (trung bình 0,5 s) | 0.0456 | 0 | VP-1 |
| PP-SWR-004 Tốc độ quay vô lăng RMS khi HWA lái, vòng kín | 0.0137 | 0.000796 | VP-1 |
| PP-SWR-050 Lệch ngang của path so với tâm làn thật, 0–1 s, lớn nhất | 0.523 | 0 | VP-4 |
| PP-SWR-053 Thời gian đưa xe về giữa (lệch ≤ 0,1 m) | 0.13 | 0 | VP-1 |
| PP-SWR-057 Khoảng cách ngang nhỏ nhất từ thân xe tới xe lớn khi ngang hàng | 0.301 | 0.293 | VP-5 |
| PP-SWR-059 Thời gian từ lúc hết ngang hàng tới lúc lệch ≤ 0,1 m | 1.72 | 0 | VP-4 |
| PP-SWR-081 Thời lượng path LKA tới COMPLETED | 1.3 | 0.875 | VP-0 |
| PP-SWR-082 Thời lượng path ELK tới COMPLETED | 1.38 | 0.05 | VP-0 |
| PP-SWR-087 DTLE LKA nhỏ nhất | 0.18 | 0.00353 | VP-0 |

Requirement đạt 100 % trên mọi profile: không (VP-0, VP-2, VP-3, VP-4, VP-5)

## Thời gian tính

1825970 chu kỳ. p95 ≤ 1.26 ms, p99 ≤ 2 ms (cận trên của bin), lớn nhất 695 ms. Đo trên máy chạy SIL, gồm adapter; không khẳng định thời gian trên ECU (mục 9.1).

![Thời gian tính](figures/compute.png)

## DTLE theo v_lat

| Kịch bản | v_lat [m/s] | DTLE nhỏ nhất [m] |
|---|---|---|
| S4 | 0 | 0.0486 |
| S4 | 0.2 | 0.0452 |
| S4 | 0.3 | 0.0534 |
| S4 | 0.4 | 0.0449 |
| S4 | 0.5 | 0.0478 |
| S4 | 0.6 | 0.0189 |
| S4b | 0.2 | 0.0795 |
| S4b | 0.3 | 0.0444 |
| S4b | 0.6 | 0.238 |
| S5 | 0.2 | 0.0242 |
| S5 | 0.3 | 0.0258 |
| S5 | 0.4 | 0.0153 |
| S5 | 0.5 | 0.0188 |
| S5 | 0.6 | 0.0217 |
| S6 | 0.2 | 0.022 |
| S6 | 0.3 | 0.0258 |
| S6 | 0.4 | 0.0157 |
| S6 | 0.5 | 0.0261 |
| S6 | 0.6 | 0.0194 |
| S7 | 0.2 | -0.273 |
| S7 | 0.3 | 0.12 |
| S7 | 0.4 | 0.159 |
| S7 | 0.5 | 0.2 |
| S7 | 0.6 | 0.133 |
| S8 | 0.2 | 0.0796 |
| S8 | 0.3 | 0.12 |
| S8 | 0.4 | 0.159 |
| S8 | 0.5 | 0.199 |
| S8 | 0.6 | 0.133 |
| S8 | 0.7 | 0.196 |
| S8b | 0.5 | -0.352 |
| S8c | 0.4 | 0.241 |

![DTLE theo v_lat](figures/dtle_v_lat.png)

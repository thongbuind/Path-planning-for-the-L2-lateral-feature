# Kết luận: Không đạt

- Planner: pp_lcc 0.3.0 commit edb02b8b9784 calibration 6b03f0759737 t7 quintic (b09be0856dbb) / pp_lkaelk 0.3.0 commit edb02b8b9784 calibration 6b03f0759737 (61df32ec8a95)
- Tích hợp được: có
- Đã chạy: 2309 lần chạy; trượt BLOCKER 201, MAJOR 0, MINOR 51; 6 ca không được chấm
- Kết luận chỉ đúng trong phạm vi đã thử, không phải bằng chứng an toàn (Software Qualification Test Specification 3).

## Trượt BLOCKER

| Requirement | Safety goal | Ca | Profile | Seed | Trượt đầu tiên [s] | Giá trị | Ngưỡng | Chi tiết | MCAP |
|---|---|---|---|---|---|---|---|---|---|
| PP-SWR-005 | SG-02 | S1b-a-VP-0-693b15015bfa | VP-0 | 1 | 7.858 | 1 | = 0 | Chu kỳ cua gắt mà mất path hoặc HWA | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S1b-a-VP-0-693b15015bfa_seed1.mcap |
| PP-SWR-006 | SG-02 | S1b-a-VP-0-693b15015bfa | VP-0 | 1 | 3.958 | -0.1154 | >= 0 | a_y path trừ (aysmax − epsilon_ay), 0–1 s, khi a_y cần > aysmax [m/s²] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S1b-a-VP-0-693b15015bfa_seed1.mcap |
| PP-SWR-007 | SG-01 | S1b-a-VP-0-693b15015bfa | VP-0 | 1 | 8.641 | 1 | = 0 | Lần lốp đè vạch khi cua gắt mà cờ chưa bật | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S1b-a-VP-0-693b15015bfa_seed1.mcap |
| PP-SWR-030 | SG-01 | S14-a-VP-0-3290c39907ee | VP-0 | 1 | 7.858 | 29 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S14-a-VP-0-3290c39907ee_seed1.mcap |
| PP-SWR-030 | SG-01 | S1b-a-VP-0-693b15015bfa | VP-0 | 1 | 7.858 | 29 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S1b-a-VP-0-693b15015bfa_seed1.mcap |
| PP-SWR-051 | SG-01 | F02-e-S1a-VP-5-29183b65ffaf | VP-5 | 1 | — | -0.1106 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F02-e-S1a-VP-5-29183b65ffaf_seed1.mcap |
| PP-SWR-051 | SG-01 | F02-e-S1c-VP-5-50d3444b79d5 | VP-5 | 1 | — | -0.1113 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F02-e-S1c-VP-5-50d3444b79d5_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1a-VP-0-1c03af025ee4 | VP-0 | 1 | — | -0.2756 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F03-c-S1a-VP-0-1c03af025ee4_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1a-VP-1-a5219f0b3fc2 | VP-1 | 1 | — | -0.272 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F03-c-S1a-VP-1-a5219f0b3fc2_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1a-VP-5-4a0b9685f06c | VP-5 | 1 | — | -0.5839 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F03-c-S1a-VP-5-4a0b9685f06c_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1c-VP-0-0e2929c3df25 | VP-0 | 1 | — | -0.3244 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F03-c-S1c-VP-0-0e2929c3df25_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1c-VP-1-4278b1e68610 | VP-1 | 1 | — | -0.3244 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F03-c-S1c-VP-1-4278b1e68610_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1c-VP-5-ce2933b62cf1 | VP-5 | 1 | — | -0.6323 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F03-c-S1c-VP-5-ce2933b62cf1_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-b-S1c-VP-5-545957874102 | VP-5 | 1 | — | -0.01292 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F06-b-S1c-VP-5-545957874102_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1a-VP-5-9e2995fea291 | VP-5 | 1 | — | -0.2729 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F06-d-S1a-VP-5-9e2995fea291_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1c-VP-5-bdab3c9103b7 | VP-5 | 1 | — | -0.2797 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F06-d-S1c-VP-5-bdab3c9103b7_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-e-S1c-VP-5-87266b531a26 | VP-5 | 1 | — | -0.09161 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F06-e-S1c-VP-5-87266b531a26_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-0-4efddd649b2a | VP-0 | 1 | — | -0.7409 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F08-a-S1c-VP-0-4efddd649b2a_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-0-9d836e616214 | VP-0 | 1 | — | -0.7409 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F08-a-S1c-VP-0-9d836e616214_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-1-9f6496a368b0 | VP-1 | 1 | — | -0.8217 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F08-a-S1c-VP-1-9f6496a368b0_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-1-c098420638d4 | VP-1 | 1 | — | -0.8217 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F08-a-S1c-VP-1-c098420638d4_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-5-5d6c59c69cbe | VP-5 | 1 | — | -1.027 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F08-a-S1c-VP-5-5d6c59c69cbe_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-5-dce61f599c6e | VP-5 | 1 | — | -1.027 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F08-a-S1c-VP-5-dce61f599c6e_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-b-S1c-VP-0-4ae7633cf949 | VP-0 | 1 | — | -0.9732 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F08-b-S1c-VP-0-4ae7633cf949_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-b-S1c-VP-1-297eab73e001 | VP-1 | 1 | — | -0.9909 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F08-b-S1c-VP-1-297eab73e001_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-b-S1c-VP-5-9d66d718191a | VP-5 | 1 | — | -1.281 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F08-b-S1c-VP-5-9d66d718191a_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1c-VP-0-bca0f1afb997 | VP-0 | 1 | — | -0.9929 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F08-c-S1c-VP-0-bca0f1afb997_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1c-VP-1-3d8334644eea | VP-1 | 1 | — | -1.024 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F08-c-S1c-VP-1-3d8334644eea_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1c-VP-5-06d7bb8fda8b | VP-5 | 1 | — | -1.358 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F08-c-S1c-VP-5-06d7bb8fda8b_seed1.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-5-38898514a806 | VP-5 | 1 | — | -0.03031 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/G01-S1c-VP-5-38898514a806_seed1.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-5-38898514a806 | VP-5 | 2 | — | -0.002867 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/G01-S1c-VP-5-38898514a806_seed2.mcap |
| PP-SWR-051 | SG-01 | S14-a-VP-0-cabfa230312d | VP-0 | 1 | — | -23.06 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S14-a-VP-0-cabfa230312d_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-0-ff8e4ce04140 | VP-0 | 1 | — | -0.02073 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S14-e-VP-0-ff8e4ce04140_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-1-c599c50726eb | VP-1 | 1 | — | -0.1111 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S14-e-VP-1-c599c50726eb_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-2-d2cc20ee8bbf | VP-2 | 1 | — | -0.1375 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S14-e-VP-2-d2cc20ee8bbf_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-3-24dcd5adb2de | VP-3 | 1 | — | -0.1731 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S14-e-VP-3-24dcd5adb2de_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-4-a571d2de589d | VP-4 | 1 | — | -0.1802 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S14-e-VP-4-a571d2de589d_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-5-3f2b28b63f2e | VP-5 | 1 | — | -0.3032 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S14-e-VP-5-3f2b28b63f2e_seed1.mcap |
| PP-SWR-085 | SG-01 | F02-e-S4a_at_lka_activep0-VP-2-c5082f1b14ba | VP-2 | 1 | — | -0.1353 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F02-e-S4a_at_lka_activep0-VP-2-c5082f1b14ba_seed1.mcap |
| PP-SWR-085 | SG-01 | F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0 | VP-3 | 1 | — | -0.185 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0_seed1.mcap |
| PP-SWR-085 | SG-01 | F06-d-S5a_at_elk_activep0-VP-0-f32caea02125 | VP-0 | 1 | — | -0.005515 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F06-d-S5a_at_elk_activep0-VP-0-f32caea02125_seed1.mcap |
| PP-SWR-085 | SG-01 | G01-S4c-VP-0-944a5944b2f0 | VP-0 | 2 | — | -0.5862 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/G01-S4c-VP-0-944a5944b2f0_seed2.mcap |
| PP-SWR-085 | SG-01 | G01-S4c-VP-1-d9c02f4d85c9 | VP-1 | 2 | — | -0.5512 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/G01-S4c-VP-1-d9c02f4d85c9_seed2.mcap |
| PP-SWR-085 | SG-01 | G01-S4c-VP-2-19b08e51426b | VP-2 | 2 | — | -0.6807 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/G01-S4c-VP-2-19b08e51426b_seed2.mcap |
| PP-SWR-085 | SG-01 | G01-S4c-VP-3-9991783c316d | VP-3 | 2 | — | -0.7415 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/G01-S4c-VP-3-9991783c316d_seed2.mcap |
| PP-SWR-085 | SG-01 | G01-S4c-VP-4-072664ac9b98 | VP-4 | 2 | — | -0.7766 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/G01-S4c-VP-4-072664ac9b98_seed2.mcap |
| PP-SWR-085 | SG-01 | G01-S4c-VP-5-26df2868e70c | VP-5 | 2 | — | -0.895 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/G01-S4c-VP-5-26df2868e70c_seed2.mcap |
| PP-SWR-085 | SG-01 | S13-b-elk-VP-3-036d4797fb02 | VP-3 | 1 | — | -0.003434 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S13-b-elk-VP-3-036d4797fb02_seed1.mcap |
| PP-SWR-085 | SG-01 | S13-b-elk-VP-4-fcc4ba55c158 | VP-4 | 1 | — | -0.01553 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S13-b-elk-VP-4-fcc4ba55c158_seed1.mcap |
| PP-SWR-085 | SG-01 | S13-c-elk-VP-3-6a4d13fdd9f5 | VP-3 | 1 | — | -0.02134 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S13-c-elk-VP-3-6a4d13fdd9f5_seed1.mcap |
| PP-SWR-085 | SG-01 | S5-c-VP-4-5861012ff8ee | VP-4 | 1 | — | -0.1274 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S5-c-VP-4-5861012ff8ee_seed1.mcap |
| PP-SWR-085 | SG-01 | S5-eu-left-2-VP-4-5d769c7a5088 | VP-4 | 1 | — | -0.01242 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S5-eu-left-2-VP-4-5d769c7a5088_seed1.mcap |
| PP-SWR-085 | SG-01 | S5-eu-right-2-VP-4-a4a9ddbdd537 | VP-4 | 1 | — | -0.01242 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S5-eu-right-2-VP-4-a4a9ddbdd537_seed1.mcap |
| PP-SWR-085 | SG-01 | S5-ncap-solid-left-2-VP-4-8bdaed8c6e66 | VP-4 | 1 | — | -0.01242 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S5-ncap-solid-left-2-VP-4-8bdaed8c6e66_seed1.mcap |
| PP-SWR-085 | SG-01 | S5-ncap-solid-left-3-VP-5-4acb5b0a3172 | VP-5 | 1 | — | -0.1072 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S5-ncap-solid-left-3-VP-5-4acb5b0a3172_seed1.mcap |
| PP-SWR-085 | SG-01 | S5-ncap-solid-right-2-VP-4-5df4bc9318e1 | VP-4 | 1 | — | -0.01242 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S5-ncap-solid-right-2-VP-4-5df4bc9318e1_seed1.mcap |
| PP-SWR-085 | SG-01 | S5-ncap-solid-right-3-VP-5-5a13dff6278d | VP-5 | 1 | — | -0.1072 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S5-ncap-solid-right-3-VP-5-5a13dff6278d_seed1.mcap |
| PP-SWR-085 | SG-01 | S6-b-VP-4-49ce96f36822 | VP-4 | 1 | — | -0.08269 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S6-b-VP-4-49ce96f36822_seed1.mcap |
| PP-SWR-085 | SG-01 | S6-b-VP-5-025575367d8c | VP-5 | 1 | — | -0.1614 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S6-b-VP-5-025575367d8c_seed1.mcap |
| PP-SWR-085 | SG-01 | S6-ncap-edge-right-2-VP-4-bbdf6c75e9d4 | VP-4 | 1 | — | -0.01242 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S6-ncap-edge-right-2-VP-4-bbdf6c75e9d4_seed1.mcap |
| PP-SWR-085 | SG-01 | S6-ncap-edge-right-3-VP-5-f947a2b37a7b | VP-5 | 1 | — | -0.1072 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S6-ncap-edge-right-3-VP-5-f947a2b37a7b_seed1.mcap |
| PP-SWR-086 | SG-03 | S5-c-VP-4-5861012ff8ee | VP-4 | 1 | — | -0.3246 | >= -0.3 | DTLE vạch nhỏ nhất [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S5-c-VP-4-5861012ff8ee_seed1.mcap |
| PP-SWR-086 | SG-03 | S5-ncap-solid-left-3-VP-5-4acb5b0a3172 | VP-5 | 1 | — | -0.3519 | >= -0.3 | DTLE vạch nhỏ nhất [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S5-ncap-solid-left-3-VP-5-4acb5b0a3172_seed1.mcap |
| PP-SWR-086 | SG-03 | S5-ncap-solid-right-3-VP-5-5a13dff6278d | VP-5 | 1 | — | -0.3519 | >= -0.3 | DTLE vạch nhỏ nhất [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S5-ncap-solid-right-3-VP-5-5a13dff6278d_seed1.mcap |
| PP-SWR-086 | SG-03 | S6-b-VP-4-49ce96f36822 | VP-4 | 1 | — | -0.3138 | >= -0.1 | DTLE mép đường nhỏ nhất [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S6-b-VP-4-49ce96f36822_seed1.mcap |
| PP-SWR-086 | SG-03 | S6-b-VP-5-025575367d8c | VP-5 | 1 | — | -0.3602 | >= -0.1 | DTLE mép đường nhỏ nhất [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S6-b-VP-5-025575367d8c_seed1.mcap |
| PP-SWR-086 | SG-03 | S6-ncap-edge-right-2-VP-4-bbdf6c75e9d4 | VP-4 | 1 | — | -0.2804 | >= -0.1 | DTLE mép đường nhỏ nhất [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S6-ncap-edge-right-2-VP-4-bbdf6c75e9d4_seed1.mcap |
| PP-SWR-086 | SG-03 | S6-ncap-edge-right-3-VP-5-f947a2b37a7b | VP-5 | 1 | — | -0.3519 | >= -0.1 | DTLE mép đường nhỏ nhất [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S6-ncap-edge-right-3-VP-5-f947a2b37a7b_seed1.mcap |
| PP-SWR-094 | SG-01 | F01-a-S4a_at_lka_activep0-VP-0-c97d4f8c3b33 | VP-0 | 1 | — | 0.1005 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F01-a-S4a_at_lka_activep0-VP-0-c97d4f8c3b33_seed1.mcap |
| PP-SWR-094 | SG-01 | F01-a-S4a_at_lka_activep0-VP-0-c97d4f8c3b33 | VP-0 | 2 | — | 0.1168 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F01-a-S4a_at_lka_activep0-VP-0-c97d4f8c3b33_seed2.mcap |
| PP-SWR-094 | SG-01 | F01-b-S4a_at_lka_activep0-VP-2-26b730c60966 | VP-2 | 2 | — | 0.1108 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F01-b-S4a_at_lka_activep0-VP-2-26b730c60966_seed2.mcap |
| PP-SWR-094 | SG-01 | F01-b-S4a_at_lka_activep0.2-VP-3-7e4bb0e3caed | VP-3 | 2 | — | 0.1098 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F01-b-S4a_at_lka_activep0.2-VP-3-7e4bb0e3caed_seed2.mcap |
| PP-SWR-094 | SG-01 | F01-c-S4a_at_lka_activep0.2-VP-5-2e109dc103db | VP-5 | 2 | — | 0.1051 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F01-c-S4a_at_lka_activep0.2-VP-5-2e109dc103db_seed2.mcap |
| PP-SWR-094 | SG-01 | F02-e-S4a_at_lka_activep0-VP-2-c5082f1b14ba | VP-2 | 1 | — | 0.2126 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F02-e-S4a_at_lka_activep0-VP-2-c5082f1b14ba_seed1.mcap |
| PP-SWR-094 | SG-01 | F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0 | VP-3 | 1 | — | 0.2144 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0_seed1.mcap |
| PP-SWR-094 | SG-01 | F06-d-S5a_at_elk_activep0.2-VP-1-f5395e617721 | VP-1 | 1 | — | 0.2949 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F06-d-S5a_at_elk_activep0.2-VP-1-f5395e617721_seed1.mcap |
| PP-SWR-094 | SG-01 | F24-a-S20a_at_elk_activep0-VP-0-2604af6c1440 | VP-0 | 1 | — | 0.2082 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F24-a-S20a_at_elk_activep0-VP-0-2604af6c1440_seed1.mcap |
| PP-SWR-094 | SG-01 | F24-a-S20a_at_elk_activep0.2-VP-1-18b3f0e32790 | VP-1 | 1 | — | 0.1446 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F24-a-S20a_at_elk_activep0.2-VP-1-18b3f0e32790_seed1.mcap |
| PP-SWR-094 | SG-01 | F24-b-S20a_at_elk_activep0-VP-2-8e727d26bcaa | VP-2 | 1 | — | 0.1675 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F24-b-S20a_at_elk_activep0-VP-2-8e727d26bcaa_seed1.mcap |
| PP-SWR-094 | SG-01 | F24-b-S20a_at_elk_activep0.2-VP-3-eba1fa34bf25 | VP-3 | 1 | — | 0.1624 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F24-b-S20a_at_elk_activep0.2-VP-3-eba1fa34bf25_seed1.mcap |
| PP-SWR-094 | SG-01 | F24-c-S20a_at_elk_activep0-VP-4-c62637d20840 | VP-4 | 1 | — | 0.1641 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F24-c-S20a_at_elk_activep0-VP-4-c62637d20840_seed1.mcap |
| PP-SWR-094 | SG-01 | F24-d-S20a_at_elk_activep0-VP-0-9f6d45fe995a | VP-0 | 1 | — | 0.2067 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F24-d-S20a_at_elk_activep0-VP-0-9f6d45fe995a_seed1.mcap |
| PP-SWR-094 | SG-01 | F24-d-S20a_at_elk_activep0.2-VP-1-26dec7ab400f | VP-1 | 1 | — | 0.1436 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F24-d-S20a_at_elk_activep0.2-VP-1-26dec7ab400f_seed1.mcap |
| PP-SWR-094 | SG-01 | F24-e-S20a_at_elk_activep0.2-VP-3-10c014488d32 | VP-3 | 1 | — | 0.15 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F24-e-S20a_at_elk_activep0.2-VP-3-10c014488d32_seed1.mcap |
| PP-SWR-094 | SG-01 | G01-S4c-VP-5-26df2868e70c | VP-5 | 1 | — | 0.1599 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/G01-S4c-VP-5-26df2868e70c_seed1.mcap |
| PP-SWR-094 | SG-01 | S12-b-VP-0-69e53aeef11a | VP-0 | 1 | — | 0.1733 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S12-b-VP-0-69e53aeef11a_seed1.mcap |
| PP-SWR-094 | SG-01 | S12-b-VP-0-69e53aeef11a | VP-0 | 2 | — | 0.1756 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S12-b-VP-0-69e53aeef11a_seed2.mcap |
| PP-SWR-094 | SG-01 | S12-b-VP-1-4b3e70a50a26 | VP-1 | 1 | — | 0.1319 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S12-b-VP-1-4b3e70a50a26_seed1.mcap |
| PP-SWR-094 | SG-01 | S12-b-VP-2-0962daddf5bd | VP-2 | 1 | — | 0.1586 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S12-b-VP-2-0962daddf5bd_seed1.mcap |
| PP-SWR-094 | SG-01 | S12-b-VP-3-984dbaa7f733 | VP-3 | 1 | — | 0.1489 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S12-b-VP-3-984dbaa7f733_seed1.mcap |
| PP-SWR-094 | SG-01 | S12-b-VP-4-a4945d3bcd67 | VP-4 | 1 | — | 0.1511 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S12-b-VP-4-a4945d3bcd67_seed1.mcap |
| PP-SWR-094 | SG-01 | S12-b-VP-5-2b777db332c0 | VP-5 | 1 | — | 0.1284 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S12-b-VP-5-2b777db332c0_seed1.mcap |
| PP-SWR-094 | SG-01 | S12-b-VP-5-2b777db332c0 | VP-5 | 2 | — | 0.1622 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S12-b-VP-5-2b777db332c0_seed2.mcap |
| PP-SWR-094 | SG-01 | S13-a-VP-0-c60458419e3e | VP-0 | 1 | — | 0.2441 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S13-a-VP-0-c60458419e3e_seed1.mcap |
| PP-SWR-094 | SG-01 | S13-a-VP-1-f59eff79bc0a | VP-1 | 1 | — | 0.1628 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S13-a-VP-1-f59eff79bc0a_seed1.mcap |
| PP-SWR-094 | SG-01 | S13-a-VP-2-ac07ce02b0df | VP-2 | 1 | — | 0.2038 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S13-a-VP-2-ac07ce02b0df_seed1.mcap |
| PP-SWR-094 | SG-01 | S13-a-VP-3-4a83d1b0c579 | VP-3 | 1 | — | 0.2169 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S13-a-VP-3-4a83d1b0c579_seed1.mcap |
| PP-SWR-094 | SG-01 | S13-a-VP-4-3bf8321b14c5 | VP-4 | 1 | — | 0.2267 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S13-a-VP-4-3bf8321b14c5_seed1.mcap |
| PP-SWR-094 | SG-01 | S13-a-VP-5-4d54367ca2b0 | VP-5 | 1 | — | 0.1985 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S13-a-VP-5-4d54367ca2b0_seed1.mcap |
| PP-SWR-094 | SG-01 | S13-b-VP-0-6ade629e2201 | VP-0 | 1 | — | 0.2757 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S13-b-VP-0-6ade629e2201_seed1.mcap |
| PP-SWR-094 | SG-01 | S13-b-VP-1-398dbf551f74 | VP-1 | 1 | — | 0.1864 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S13-b-VP-1-398dbf551f74_seed1.mcap |
| PP-SWR-094 | SG-01 | S13-b-VP-2-4fffc637c1cf | VP-2 | 1 | — | 0.2319 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S13-b-VP-2-4fffc637c1cf_seed1.mcap |
| PP-SWR-094 | SG-01 | S13-b-VP-3-211bc754a1dd | VP-3 | 1 | — | 0.246 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S13-b-VP-3-211bc754a1dd_seed1.mcap |
| PP-SWR-094 | SG-01 | S13-b-VP-4-bfdc840c5867 | VP-4 | 1 | — | 0.2569 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S13-b-VP-4-bfdc840c5867_seed1.mcap |
| PP-SWR-094 | SG-01 | S13-b-VP-5-72d0771a6181 | VP-5 | 1 | — | 0.2272 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S13-b-VP-5-72d0771a6181_seed1.mcap |
| PP-SWR-094 | SG-01 | S13-c-VP-0-492397b1cdb4 | VP-0 | 1 | — | 0.3508 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S13-c-VP-0-492397b1cdb4_seed1.mcap |
| PP-SWR-094 | SG-01 | S13-c-VP-1-4bff591ea4f1 | VP-1 | 1 | — | 0.2369 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S13-c-VP-1-4bff591ea4f1_seed1.mcap |
| PP-SWR-094 | SG-01 | S13-c-VP-2-b3cfb16c6452 | VP-2 | 1 | — | 0.2951 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S13-c-VP-2-b3cfb16c6452_seed1.mcap |
| PP-SWR-094 | SG-01 | S13-c-VP-3-e8bb12b3275a | VP-3 | 1 | — | 0.3131 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S13-c-VP-3-e8bb12b3275a_seed1.mcap |
| PP-SWR-094 | SG-01 | S13-c-VP-4-3d5c29091f8d | VP-4 | 1 | — | 0.3271 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S13-c-VP-4-3d5c29091f8d_seed1.mcap |
| PP-SWR-094 | SG-01 | S13-c-VP-5-724d6d5db36f | VP-5 | 1 | — | 0.2904 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S13-c-VP-5-724d6d5db36f_seed1.mcap |
| PP-SWR-094 | SG-01 | S13-c-elk-VP-5-9fe8e17e251a | VP-5 | 1 | — | 0.1022 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S13-c-elk-VP-5-9fe8e17e251a_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-a-VP-0-8ba389cfe7e5 | VP-0 | 1 | — | 0.1912 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-a-VP-0-8ba389cfe7e5_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-a-VP-0-d80f119be8d9 | VP-0 | 1 | — | 0.2066 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-a-VP-0-d80f119be8d9_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-a-VP-0-e8f42c436c08 | VP-0 | 1 | — | 0.1899 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-a-VP-0-e8f42c436c08_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-a-VP-1-4a3c44070492 | VP-1 | 1 | — | 0.1411 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-a-VP-1-4a3c44070492_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-a-VP-1-4aa42b2b63cc | VP-1 | 1 | — | 0.1435 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-a-VP-1-4aa42b2b63cc_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-a-VP-2-1a3aca6c43ec | VP-2 | 1 | — | 0.1573 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-a-VP-2-1a3aca6c43ec_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-a-VP-2-57554acd1219 | VP-2 | 1 | — | 0.1659 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-a-VP-2-57554acd1219_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-a-VP-3-0c1b3863e3f9 | VP-3 | 1 | — | 0.1609 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-a-VP-3-0c1b3863e3f9_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-a-VP-3-5110804c16f4 | VP-3 | 1 | — | 0.1532 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-a-VP-3-5110804c16f4_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-a-VP-4-34088aa3a905 | VP-4 | 1 | — | 0.1623 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-a-VP-4-34088aa3a905_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-a-VP-4-81e920fb5e5c | VP-4 | 1 | — | 0.1548 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-a-VP-4-81e920fb5e5c_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-a-VP-5-c5bc50661089 | VP-5 | 1 | — | 0.1226 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-a-VP-5-c5bc50661089_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-b-VP-0-af29ec291be2 | VP-0 | 1 | — | 0.2043 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-b-VP-0-af29ec291be2_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-b-VP-1-54a995b0031e | VP-1 | 1 | — | 0.1542 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-b-VP-1-54a995b0031e_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-b-VP-2-e6e7a64f9f51 | VP-2 | 1 | — | 0.171 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-b-VP-2-e6e7a64f9f51_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-b-VP-3-2a6f3e117870 | VP-3 | 1 | — | 0.169 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-b-VP-3-2a6f3e117870_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-b-VP-4-9a746c95da73 | VP-4 | 1 | — | 0.1716 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-b-VP-4-9a746c95da73_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-b-VP-5-2790db1df683 | VP-5 | 1 | — | 0.1409 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-b-VP-5-2790db1df683_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-c-VP-0-f0942ab04d9a | VP-0 | 1 | — | 0.209 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-c-VP-0-f0942ab04d9a_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-c-VP-1-f9c74ac113d9 | VP-1 | 1 | — | 0.1558 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-c-VP-1-f9c74ac113d9_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-c-VP-2-be2160ce507b | VP-2 | 1 | — | 0.1757 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-c-VP-2-be2160ce507b_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-c-VP-3-ae739ee498dd | VP-3 | 1 | — | 0.1754 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-c-VP-3-ae739ee498dd_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-c-VP-4-1b3167df8aba | VP-4 | 1 | — | 0.1782 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-c-VP-4-1b3167df8aba_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-c-VP-5-4c60083ac9aa | VP-5 | 1 | — | 0.1471 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-c-VP-5-4c60083ac9aa_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-d-VP-1-57454ada83d5 | VP-1 | 1 | — | 0.1633 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-d-VP-1-57454ada83d5_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-d-VP-2-ba30eb1b5fbc | VP-2 | 1 | — | 0.1887 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-d-VP-2-ba30eb1b5fbc_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-d-VP-3-1bf1820573f9 | VP-3 | 1 | — | 0.1855 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-d-VP-3-1bf1820573f9_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-d-VP-4-7c804019a23d | VP-4 | 1 | — | 0.1896 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-d-VP-4-7c804019a23d_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-d-VP-5-0068791828e3 | VP-5 | 1 | — | 0.1062 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-d-VP-5-0068791828e3_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-e-VP-1-d7374cb77d39 | VP-1 | 1 | — | 0.1683 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-e-VP-1-d7374cb77d39_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-e-VP-2-3f0728de949e | VP-2 | 1 | — | 0.1884 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-e-VP-2-3f0728de949e_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-e-VP-3-1446b147b84f | VP-3 | 1 | — | 0.1872 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-e-VP-3-1446b147b84f_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-e-VP-4-49c117c143d9 | VP-4 | 1 | — | 0.1907 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-e-VP-4-49c117c143d9_seed1.mcap |
| PP-SWR-094 | SG-01 | S20-e-VP-5-04f6e1b49552 | VP-5 | 1 | — | 0.1595 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-e-VP-5-04f6e1b49552_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-a-VP-0-52a3aff02879 | VP-0 | 1 | — | 0.1151 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-a-VP-0-52a3aff02879_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-a-VP-0-b44bc723e37b | VP-0 | 1 | — | 0.1636 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-a-VP-0-b44bc723e37b_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-c-VP-0-3cf435f6b5c5 | VP-0 | 1 | — | 0.2146 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-c-VP-0-3cf435f6b5c5_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-c-VP-1-5bd5b746056e | VP-1 | 1 | — | 0.1371 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-c-VP-1-5bd5b746056e_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-c-VP-2-73dc0581a812 | VP-2 | 1 | — | 0.1769 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-c-VP-2-73dc0581a812_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-c-VP-3-c267c4fdf99e | VP-3 | 1 | — | 0.188 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-c-VP-3-c267c4fdf99e_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-c-VP-4-d696878ce99b | VP-4 | 1 | — | 0.1969 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-c-VP-4-d696878ce99b_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-c-VP-5-5f07bfc08f00 | VP-5 | 1 | — | 0.1686 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-c-VP-5-5f07bfc08f00_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-dashed-left-4-VP-0-f72bc620891d | VP-0 | 1 | — | 0.1083 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-dashed-left-4-VP-0-f72bc620891d_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-dashed-left-5-VP-0-7fbc0173b940 | VP-0 | 1 | — | 0.1152 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-dashed-left-5-VP-0-7fbc0173b940_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-dashed-left-6-VP-0-32bc0ee876a7 | VP-0 | 1 | — | 0.2051 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-dashed-left-6-VP-0-32bc0ee876a7_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-dashed-left-6-VP-2-6d391c13b0e2 | VP-2 | 1 | — | 0.169 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-dashed-left-6-VP-2-6d391c13b0e2_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-dashed-left-6-VP-3-8757d8a9cfe1 | VP-3 | 1 | — | 0.1746 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-dashed-left-6-VP-3-8757d8a9cfe1_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-dashed-left-6-VP-4-07c2217edd71 | VP-4 | 1 | — | 0.1824 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-dashed-left-6-VP-4-07c2217edd71_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-dashed-left-6-VP-5-c678e1434b96 | VP-5 | 1 | — | 0.1247 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-dashed-left-6-VP-5-c678e1434b96_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-dashed-right-4-VP-0-61ba924dc72d | VP-0 | 1 | — | 0.1083 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-dashed-right-4-VP-0-61ba924dc72d_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-dashed-right-5-VP-0-c04da4e9c03e | VP-0 | 1 | — | 0.1152 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-dashed-right-5-VP-0-c04da4e9c03e_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-dashed-right-6-VP-0-861ac188be6f | VP-0 | 1 | — | 0.2051 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-dashed-right-6-VP-0-861ac188be6f_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-dashed-right-6-VP-2-b6d634bcc2af | VP-2 | 1 | — | 0.169 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-dashed-right-6-VP-2-b6d634bcc2af_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-dashed-right-6-VP-3-252dd2632149 | VP-3 | 1 | — | 0.1746 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-dashed-right-6-VP-3-252dd2632149_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-dashed-right-6-VP-4-7c7f3788f028 | VP-4 | 1 | — | 0.1824 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-dashed-right-6-VP-4-7c7f3788f028_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-dashed-right-6-VP-5-f228489a2b17 | VP-5 | 1 | — | 0.1247 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-dashed-right-6-VP-5-f228489a2b17_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-solid-left-4-VP-0-1b4cacf819c9 | VP-0 | 1 | — | 0.1083 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-solid-left-4-VP-0-1b4cacf819c9_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-solid-left-5-VP-0-00717abdfdec | VP-0 | 1 | — | 0.1152 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-solid-left-5-VP-0-00717abdfdec_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-solid-left-6-VP-0-1dfc9b72cc34 | VP-0 | 1 | — | 0.2051 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-solid-left-6-VP-0-1dfc9b72cc34_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-solid-left-6-VP-2-83a42769a507 | VP-2 | 1 | — | 0.169 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-solid-left-6-VP-2-83a42769a507_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-solid-left-6-VP-3-638a954adc18 | VP-3 | 1 | — | 0.1746 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-solid-left-6-VP-3-638a954adc18_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-solid-left-6-VP-4-c0a8ecef63bc | VP-4 | 1 | — | 0.1824 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-solid-left-6-VP-4-c0a8ecef63bc_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-solid-left-6-VP-5-9ad2f086a68f | VP-5 | 1 | — | 0.1247 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-solid-left-6-VP-5-9ad2f086a68f_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-solid-right-4-VP-0-4acaf63184b1 | VP-0 | 1 | — | 0.1083 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-solid-right-4-VP-0-4acaf63184b1_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-solid-right-5-VP-0-daedde462a04 | VP-0 | 1 | — | 0.1152 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-solid-right-5-VP-0-daedde462a04_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-solid-right-6-VP-0-a5c4f7f21dd8 | VP-0 | 1 | — | 0.2051 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-solid-right-6-VP-0-a5c4f7f21dd8_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-solid-right-6-VP-2-7bfe9fb2c7a2 | VP-2 | 1 | — | 0.169 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-solid-right-6-VP-2-7bfe9fb2c7a2_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-solid-right-6-VP-3-65d2ae75e029 | VP-3 | 1 | — | 0.1746 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-solid-right-6-VP-3-65d2ae75e029_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-solid-right-6-VP-4-41a95216ab51 | VP-4 | 1 | — | 0.1824 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-solid-right-6-VP-4-41a95216ab51_seed1.mcap |
| PP-SWR-094 | SG-01 | S4-ncap-solid-right-6-VP-5-d6da3af91aa1 | VP-5 | 1 | — | 0.1247 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S4-ncap-solid-right-6-VP-5-d6da3af91aa1_seed1.mcap |
| PP-SWR-094 | SG-01 | S5-d-VP-0-a2641b707155 | VP-0 | 1 | — | 0.2035 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S5-d-VP-0-a2641b707155_seed1.mcap |
| PP-SWR-094 | SG-01 | S5-d-VP-1-db3fd74f8bfb | VP-1 | 1 | — | 0.1382 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S5-d-VP-1-db3fd74f8bfb_seed1.mcap |
| PP-SWR-094 | SG-01 | S5-d-VP-2-b54a7ac70200 | VP-2 | 1 | — | 0.162 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S5-d-VP-2-b54a7ac70200_seed1.mcap |
| PP-SWR-094 | SG-01 | S5-d-VP-3-ddbea668861e | VP-3 | 1 | — | 0.1547 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S5-d-VP-3-ddbea668861e_seed1.mcap |
| PP-SWR-094 | SG-01 | S5-d-VP-4-77de79f99d28 | VP-4 | 1 | — | 0.1558 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S5-d-VP-4-77de79f99d28_seed1.mcap |
| PP-SWR-094 | SG-01 | S6-e-VP-1-9be1dfc0f784 | VP-1 | 1 | — | 0.1604 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S6-e-VP-1-9be1dfc0f784_seed1.mcap |
| PP-SWR-094 | SG-01 | S6-e-VP-2-1ea66bc98d89 | VP-2 | 1 | — | 0.1854 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S6-e-VP-2-1ea66bc98d89_seed1.mcap |
| PP-SWR-094 | SG-01 | S6-e-VP-3-9623adcd0e09 | VP-3 | 1 | — | 0.1832 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S6-e-VP-3-9623adcd0e09_seed1.mcap |
| PP-SWR-094 | SG-01 | S6-e-VP-4-2f467a5d37dc | VP-4 | 1 | — | 0.1857 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S6-e-VP-4-2f467a5d37dc_seed1.mcap |
| PP-SWR-094 | SG-01 | S6-e-VP-5-0584f057ac9e | VP-5 | 1 | — | 0.1037 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S6-e-VP-5-0584f057ac9e_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-c-S1c-VP-1-3d8334644eea | VP-1 | 1 | 7.383 | 1.127 | <= 1 | Lệch ngang giữa hai path liên tiếp / ngưỡng của khoảng | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F08-c-S1c-VP-1-3d8334644eea_seed1.mcap |
| PP-SWR-102 | SG-04 | S22-a-VP-0-dbbbdfba0b2e | VP-0 | 1 | 3.259 | 1.374 | <= 1 | Lệch độ cong giữa hai path liên tiếp / ngưỡng của khoảng | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S22-a-VP-0-dbbbdfba0b2e_seed1.mcap |
| PP-SWR-173 | SG-02 | F25-a-S22a-VP-0-85b221025492 | VP-0 | 1 | 4.884 | 3 | = 0 | Chu kỳ path_valid sai thời hạn T_coast sau FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F25-a-S22a-VP-0-85b221025492_seed1.mcap |
| PP-SWR-173 | SG-02 | F25-c-S22a-VP-0-191326001926 | VP-0 | 1 | 4.884 | 3 | = 0 | Chu kỳ path_valid sai thời hạn T_coast sau FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F25-c-S22a-VP-0-191326001926_seed1.mcap |
| PP-SWR-173 | SG-02 | F25-c-S22a-VP-1-42edbe799a5c | VP-1 | 1 | 4.734 | 5 | = 0 | Chu kỳ path_valid sai thời hạn T_coast sau FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F25-c-S22a-VP-1-42edbe799a5c_seed1.mcap |
| PP-SWR-173 | SG-02 | F25-c-S22a-VP-5-dc4b57212bae | VP-5 | 1 | 4.859 | 4 | = 0 | Chu kỳ path_valid sai thời hạn T_coast sau FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F25-c-S22a-VP-5-dc4b57212bae_seed1.mcap |
| PP-SWR-173 | SG-02 | F25-e-S22a-VP-0-2219ed6d348d | VP-0 | 1 | 4.884 | 3 | = 0 | Chu kỳ path_valid sai thời hạn T_coast sau FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F25-e-S22a-VP-0-2219ed6d348d_seed1.mcap |
| PP-SWR-173 | SG-02 | F25-e-S22a-VP-1-39ef91d1dee2 | VP-1 | 1 | 4.734 | 5 | = 0 | Chu kỳ path_valid sai thời hạn T_coast sau FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F25-e-S22a-VP-1-39ef91d1dee2_seed1.mcap |
| PP-SWR-173 | SG-02 | F25-e-S22a-VP-5-fb5ac378351a | VP-5 | 1 | 4.859 | 4 | = 0 | Chu kỳ path_valid sai thời hạn T_coast sau FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F25-e-S22a-VP-5-fb5ac378351a_seed1.mcap |

## Trượt MINOR

| Requirement | Safety goal | Ca | Profile | Seed | Trượt đầu tiên [s] | Giá trị | Ngưỡng | Chi tiết | MCAP |
|---|---|---|---|---|---|---|---|---|---|
| PP-SWR-032 | — | F01-a-S4a_at_lka_activep0-VP-0-c97d4f8c3b33 | VP-0 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F01-a-S4a_at_lka_activep0-VP-0-c97d4f8c3b33_seed1.mcap |
| PP-SWR-032 | — | F01-b-S4a_at_lka_activep0-VP-2-26b730c60966 | VP-2 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F01-b-S4a_at_lka_activep0-VP-2-26b730c60966_seed1.mcap |
| PP-SWR-032 | — | F01-b-S4a_at_lka_activep0-VP-2-26b730c60966 | VP-2 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F01-b-S4a_at_lka_activep0-VP-2-26b730c60966_seed2.mcap |
| PP-SWR-032 | — | F01-b-S4a_at_lka_activep0.2-VP-3-7e4bb0e3caed | VP-3 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F01-b-S4a_at_lka_activep0.2-VP-3-7e4bb0e3caed_seed2.mcap |
| PP-SWR-032 | — | F01-b-S5a_at_elk_activep0-VP-2-795bfb495e44 | VP-2 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F01-b-S5a_at_elk_activep0-VP-2-795bfb495e44_seed1.mcap |
| PP-SWR-032 | — | F01-b-S5a_at_elk_activep0.2-VP-3-43bbc0fa0b87 | VP-3 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F01-b-S5a_at_elk_activep0.2-VP-3-43bbc0fa0b87_seed1.mcap |
| PP-SWR-032 | — | F01-c-S4a_at_lka_activep0.2-VP-5-2e109dc103db | VP-5 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F01-c-S4a_at_lka_activep0.2-VP-5-2e109dc103db_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-5-26df2868e70c | VP-5 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/G01-S4c-VP-5-26df2868e70c_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-0-69e53aeef11a | VP-0 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S12-b-VP-0-69e53aeef11a_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-0-69e53aeef11a | VP-0 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S12-b-VP-0-69e53aeef11a_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-1-4b3e70a50a26 | VP-1 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S12-b-VP-1-4b3e70a50a26_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-1-4b3e70a50a26 | VP-1 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S12-b-VP-1-4b3e70a50a26_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-2-0962daddf5bd | VP-2 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S12-b-VP-2-0962daddf5bd_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-2-0962daddf5bd | VP-2 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S12-b-VP-2-0962daddf5bd_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-3-984dbaa7f733 | VP-3 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S12-b-VP-3-984dbaa7f733_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-4-a4945d3bcd67 | VP-4 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S12-b-VP-4-a4945d3bcd67_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-5-2b777db332c0 | VP-5 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S12-b-VP-5-2b777db332c0_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-5-2b777db332c0 | VP-5 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S12-b-VP-5-2b777db332c0_seed2.mcap |
| PP-SWR-084 | — | F02-e-S4a_at_lka_activep0-VP-2-c5082f1b14ba | VP-2 | 1 | — | 0.5503 | <= 0.2 | Lệch tâm khi LKA hoặc ELK COMPLETED [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F02-e-S4a_at_lka_activep0-VP-2-c5082f1b14ba_seed1.mcap |
| PP-SWR-084 | — | F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0 | VP-3 | 1 | — | 0.5496 | <= 0.2 | Lệch tâm khi LKA hoặc ELK COMPLETED [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0_seed1.mcap |
| PP-SWR-084 | — | F02-e-S5a_at_elk_activep0.2-VP-3-bb766866f0d0 | VP-3 | 1 | — | -0.04386 | >= 0 | DLC nhỏ nhất ở hai phía khi LKA hoặc ELK COMPLETED [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F02-e-S5a_at_elk_activep0.2-VP-3-bb766866f0d0_seed1.mcap |
| PP-SWR-084 | — | F02-e-S5a_at_elk_activep0.2-VP-3-bb766866f0d0 | VP-3 | 1 | — | 0.6205 | <= 0.2 | Lệch tâm khi LKA hoặc ELK COMPLETED [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F02-e-S5a_at_elk_activep0.2-VP-3-bb766866f0d0_seed1.mcap |
| PP-SWR-090 | — | F01-c-S4a_at_lka_activep0-VP-4-914355537c7d | VP-4 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F01-c-S4a_at_lka_activep0-VP-4-914355537c7d_seed1.mcap |
| PP-SWR-090 | — | F02-e-S4a_at_lka_activep0-VP-2-c5082f1b14ba | VP-2 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F02-e-S4a_at_lka_activep0-VP-2-c5082f1b14ba_seed1.mcap |
| PP-SWR-090 | — | F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0 | VP-3 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0_seed1.mcap |
| PP-SWR-090 | — | F02-e-S5a_at_elk_activep0.2-VP-3-bb766866f0d0 | VP-3 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F02-e-S5a_at_elk_activep0.2-VP-3-bb766866f0d0_seed1.mcap |
| PP-SWR-090 | — | F24-e-S20a_at_elk_activep0-VP-2-b88a4ee6d6c8 | VP-2 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F24-e-S20a_at_elk_activep0-VP-2-b88a4ee6d6c8_seed1.mcap |
| PP-SWR-090 | — | F24-e-S20a_at_elk_activep0.2-VP-3-10c014488d32 | VP-3 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F24-e-S20a_at_elk_activep0.2-VP-3-10c014488d32_seed1.mcap |
| PP-SWR-090 | — | S20-a-VP-0-e8f42c436c08 | VP-0 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-a-VP-0-e8f42c436c08_seed1.mcap |
| PP-SWR-090 | — | S20-a-VP-3-5110804c16f4 | VP-3 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-a-VP-3-5110804c16f4_seed1.mcap |
| PP-SWR-090 | — | S20-a-VP-4-81e920fb5e5c | VP-4 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-a-VP-4-81e920fb5e5c_seed1.mcap |
| PP-SWR-090 | — | S20-a-VP-5-c5bc50661089 | VP-5 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-a-VP-5-c5bc50661089_seed1.mcap |
| PP-SWR-090 | — | S20-b-VP-0-af29ec291be2 | VP-0 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-b-VP-0-af29ec291be2_seed1.mcap |
| PP-SWR-090 | — | S20-b-VP-3-2a6f3e117870 | VP-3 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-b-VP-3-2a6f3e117870_seed1.mcap |
| PP-SWR-090 | — | S20-b-VP-5-2790db1df683 | VP-5 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-b-VP-5-2790db1df683_seed1.mcap |
| PP-SWR-090 | — | S20-e-VP-1-d7374cb77d39 | VP-1 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-e-VP-1-d7374cb77d39_seed1.mcap |
| PP-SWR-090 | — | S20-e-VP-3-1446b147b84f | VP-3 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/S20-e-VP-3-1446b147b84f_seed1.mcap |
| PP-SWR-170 | — | F25-a-S22a-VP-0-553a310fc4d7 | VP-0 | 1 | — | 1 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F25-a-S22a-VP-0-553a310fc4d7_seed1.mcap |
| PP-SWR-170 | — | F25-a-S22a-VP-0-85b221025492 | VP-0 | 1 | — | 2 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F25-a-S22a-VP-0-85b221025492_seed1.mcap |
| PP-SWR-170 | — | F25-b-S22a-VP-0-33e0e262751f | VP-0 | 1 | — | 1 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F25-b-S22a-VP-0-33e0e262751f_seed1.mcap |
| PP-SWR-170 | — | F25-b-S22a-VP-1-077cb6030976 | VP-1 | 1 | — | 1 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F25-b-S22a-VP-1-077cb6030976_seed1.mcap |
| PP-SWR-170 | — | F25-b-S22a-VP-5-0aa316c22313 | VP-5 | 1 | — | 1 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F25-b-S22a-VP-5-0aa316c22313_seed1.mcap |
| PP-SWR-170 | — | F25-c-S22a-VP-0-191326001926 | VP-0 | 1 | — | 2 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F25-c-S22a-VP-0-191326001926_seed1.mcap |
| PP-SWR-170 | — | F25-c-S22a-VP-1-42edbe799a5c | VP-1 | 1 | — | 2 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F25-c-S22a-VP-1-42edbe799a5c_seed1.mcap |
| PP-SWR-170 | — | F25-c-S22a-VP-5-dc4b57212bae | VP-5 | 1 | — | 2 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F25-c-S22a-VP-5-dc4b57212bae_seed1.mcap |
| PP-SWR-170 | — | F25-d-S22a-VP-0-deb4c617404b | VP-0 | 1 | — | 1 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F25-d-S22a-VP-0-deb4c617404b_seed1.mcap |
| PP-SWR-170 | — | F25-d-S22a-VP-1-294c7b39bdf1 | VP-1 | 1 | — | 1 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F25-d-S22a-VP-1-294c7b39bdf1_seed1.mcap |
| PP-SWR-170 | — | F25-d-S22a-VP-5-425685eb4bcc | VP-5 | 1 | — | 2 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F25-d-S22a-VP-5-425685eb4bcc_seed1.mcap |
| PP-SWR-170 | — | F25-e-S22a-VP-0-2219ed6d348d | VP-0 | 1 | — | 2 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F25-e-S22a-VP-0-2219ed6d348d_seed1.mcap |
| PP-SWR-170 | — | F25-e-S22a-VP-1-39ef91d1dee2 | VP-1 | 1 | — | 2 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F25-e-S22a-VP-1-39ef91d1dee2_seed1.mcap |
| PP-SWR-170 | — | F25-e-S22a-VP-5-fb5ac378351a | VP-5 | 1 | — | 2 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261118-1546-regression-edb02b8/suite/mcap/F25-e-S22a-VP-5-fb5ac378351a_seed1.mcap |

## Ca không được chấm

| Ca | Seed | Lý do |
|---|---|---|
| S22-b-VP-0-8164b3daec3e | 1 | S22b: chưa quan sát FOLLOW tới giới hạn 30 m rồi hết cửa sổ T_coast |
| S22-b-VP-1-582804600d03 | 1 | S22b: chưa quan sát FOLLOW tới giới hạn 30 m rồi hết cửa sổ T_coast |
| S22-b-VP-2-8d3c37c7f1c4 | 1 | S22b: chưa quan sát FOLLOW tới giới hạn 30 m rồi hết cửa sổ T_coast |
| S22-b-VP-3-f36ffd799338 | 1 | S22b: chưa quan sát FOLLOW tới giới hạn 30 m rồi hết cửa sổ T_coast |
| S22-b-VP-4-7f58abaa6cee | 1 | S22b: chưa quan sát FOLLOW tới giới hạn 30 m rồi hết cửa sổ T_coast |
| S22-b-VP-5-a7e1dee3be4c | 1 | S22b: chưa quan sát FOLLOW tới giới hạn 30 m rồi hết cửa sổ T_coast |

## Trượt ngoài phạm vi chấm của ca (thông tin, không tính vào kết luận)

| Mức | Requirement | Ca | Seed | Giá trị | Ngưỡng |
|---|---|---|---|---|---|
| BLOCKER | PP-SWR-177 | S1b-a-VP-0-c7404a73eb56 | 1 | 78 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-a-VP-1-df4faf423298 | 1 | 78 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-a-VP-2-5fd1b6319fec | 1 | 78 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-a-VP-3-36b37096078b | 1 | 78 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-a-VP-4-fd75cc5de206 | 1 | 78 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-a-VP-5-b5ad4c84dec1 | 1 | 78 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-d-VP-0-74093941d0e2 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-d-VP-1-edc77728a897 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-d-VP-2-b3c56e657294 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-d-VP-3-fd77fdd88288 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-d-VP-4-83863ab7182d | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-d-VP-5-3ed02584a4b0 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-b-VP-0-5a25651bbb89 | 1 | 78 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-b-VP-1-36133639793a | 1 | 78 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-b-VP-2-c2beccb3c0be | 1 | 78 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-b-VP-3-8627376f30ba | 1 | 78 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-b-VP-4-667290c5e76f | 1 | 78 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-b-VP-5-bb2156127552 | 1 | 78 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-c-VP-0-ac7abe9fb75a | 1 | 78 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-c-VP-1-ebeb5c3d2f06 | 1 | 78 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-c-VP-2-da7f60989704 | 1 | 78 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-c-VP-3-8a1debb24625 | 1 | 78 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-c-VP-4-c7f79fe27e88 | 1 | 78 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-c-VP-5-386c875f9855 | 1 | 78 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-e-VP-0-effff41e1a6d | 1 | 73 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-e-VP-1-7cda555f20d9 | 1 | 69 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-e-VP-2-0d9a57672dbe | 1 | 73 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-e-VP-3-30bb0bfbfa4b | 1 | 75 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-e-VP-4-e0ff325a62a7 | 1 | 75 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-e-VP-5-31ee7b79d4ae | 1 | 75 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-a-VP-0-c4b88838b254 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-a-VP-0-1fe61772c0da | 1 | 26 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-a-VP-0-693b15015bfa | 1 | 40 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-a-VP-0-2cdcd516cdc0 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-a-VP-0-e943a9a8b593 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-a-VP-0-faf0b71c9ee2 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-a-VP-0-61a3e032349f | 1 | 78 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-a-VP-0-fdaf9c642e57 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-a-VP-1-ee426779b76a | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-a-VP-2-9d46135c45dc | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-a-VP-3-43335bb8443b | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-a-VP-4-4279474470dc | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S1b-a-VP-5-767416b691d2 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-051 | S2-c-VP-0-b84bf321b14a | 1 | -0.248 | >= 0 |
| BLOCKER | PP-SWR-051 | S2-c-VP-1-1db4613cf0cb | 1 | -0.2249 | >= 0 |
| BLOCKER | PP-SWR-051 | S2-c-VP-2-213efa4e998e | 1 | -0.3424 | >= 0 |
| BLOCKER | PP-SWR-051 | S2-c-VP-3-4e8dc883d0cd | 1 | -0.406 | >= 0 |
| BLOCKER | PP-SWR-051 | S2-c-VP-4-255842c24eca | 1 | -0.4402 | >= 0 |
| BLOCKER | PP-SWR-051 | S2-c-VP-5-9ad0657941fb | 1 | -0.5632 | >= 0 |
| MINOR | PP-SWR-062 | S2-c-VP-5-9ad0657941fb | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-051 | S2-d-VP-5-a311ab7697a8 | 1 | -0.0234 | >= 0 |
| MINOR | PP-SWR-062 | S2-d-VP-5-a311ab7697a8 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-177 | S14-a-VP-0-f1bc024a7604 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S14-a-VP-1-189f915adf7a | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S14-a-VP-2-976728404b33 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S14-a-VP-3-739bc93e6a6b | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S14-a-VP-4-ce770bb357a0 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S14-a-VP-5-804fd37fe7cb | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-0-ff8e4ce04140 | 1 | -1.433 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-0-dc72ffbcfa45 | 1 | -1.24 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-1-c599c50726eb | 1 | -1.478 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-1-9e894e6e0e47 | 1 | -1.262 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-2-d2cc20ee8bbf | 1 | -1.444 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-2-8ea25fd5bd76 | 1 | -1.248 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-3-24dcd5adb2de | 1 | -1.432 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-3-5cf328ad0176 | 1 | -1.239 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-4-a571d2de589d | 1 | -1.427 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-4-f51e1424afde | 1 | -1.237 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-5-3f2b28b63f2e | 1 | -1.427 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-5-845fd11edffe | 1 | -1.237 | >= 0 |
| BLOCKER | PP-SWR-177 | S14-d-VP-0-2720de04e437 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S14-d-VP-1-b36b2b9fccd2 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S14-d-VP-2-b3aad735b079 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S14-d-VP-3-0bcd1450394a | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S14-d-VP-4-16df00c34273 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S14-d-VP-5-a06cc9881367 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S14-a-VP-0-9618aedb20e7 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S14-a-VP-0-3448d3d7dc57 | 1 | 26 | = 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-0-cabfa230312d | 1 | -0.2571 | >= 0 |
| BLOCKER | PP-SWR-177 | S14-a-VP-0-cabfa230312d | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-005 | S14-a-VP-0-3290c39907ee | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-0-3290c39907ee | 1 | -0.1154 | >= 0 |
| BLOCKER | PP-SWR-007 | S14-a-VP-0-3290c39907ee | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-177 | S14-a-VP-0-3290c39907ee | 1 | 40 | = 0 |
| BLOCKER | PP-SWR-177 | S14-a-VP-0-9168560ee20d | 1 | 39 | = 0 |
| MINOR | PP-SWR-062 | S4-c-VP-5-5f07bfc08f00 | 1 | 1 | = 0 |
| MINOR | PP-SWR-062 | S4-ncap-dashed-left-6-VP-5-c678e1434b96 | 1 | 1 | = 0 |
| MINOR | PP-SWR-062 | S4-ncap-dashed-right-6-VP-5-f228489a2b17 | 1 | 1 | = 0 |
| MINOR | PP-SWR-062 | S4-ncap-solid-left-6-VP-5-9ad2f086a68f | 1 | 1 | = 0 |
| MINOR | PP-SWR-062 | S4-ncap-solid-right-6-VP-5-d6da3af91aa1 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-094 | S4b-a-VP-0-8c1a97e41a07 | 1 | 0.1355 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S4b-b-VP-0-c5137f12c89c | 1 | 0.1408 | <= 0.1 |
| MINOR | PP-SWR-090 | S4b-b-VP-3-38f48e10cf5d | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S4b-b-VP-5-085d11c4256e | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S4b-b-VP-5-085d11c4256e | 1 | 1 | = 0 |
| MINOR | PP-SWR-090 | S4b-c-VP-0-5f3bb8bbbdcc | 1 | 1 | <= 0 |
| BLOCKER | PP-SWR-094 | S4b-c-VP-0-5f3bb8bbbdcc | 1 | 0.1496 | <= 0.1 |
| MINOR | PP-SWR-090 | S4b-c-VP-1-6341e6253ac1 | 1 | 1 | <= 0 |
| BLOCKER | PP-SWR-094 | S4b-c-VP-1-6341e6253ac1 | 1 | 0.1027 | <= 0.1 |
| MINOR | PP-SWR-090 | S4b-c-VP-2-f89a9a0c7f96 | 1 | 1 | <= 0 |
| BLOCKER | PP-SWR-094 | S4b-c-VP-2-f89a9a0c7f96 | 1 | 0.1236 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S4b-c-VP-3-23a7856ac085 | 1 | 0.1247 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S4b-c-VP-4-f876104a11e9 | 1 | 0.1288 | <= 0.1 |
| MINOR | PP-SWR-090 | S4b-c-VP-5-e35d853524b2 | 1 | 1 | <= 0 |
| BLOCKER | PP-SWR-094 | S4b-c-VP-5-e35d853524b2 | 1 | 0.1058 | <= 0.1 |
| MINOR | PP-SWR-062 | S4b-c-VP-5-e35d853524b2 | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-094 | S4b-d-VP-0-3b967167e7a7 | 1 | 0.1027 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S4b-d-VP-4-d97f2e36bafa | 1 | 0.1147 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S4b-d-VP-5-d222733913a5 | 1 | 0.1012 | <= 0.1 |
| MINOR | PP-SWR-062 | S4b-d-VP-5-d222733913a5 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-094 | S4b-e-VP-0-3c6fbd348bdd | 1 | 0.1928 | <= 0.1 |
| MINOR | PP-SWR-090 | S4b-e-VP-1-fd25b44661ad | 1 | 1 | <= 0 |
| BLOCKER | PP-SWR-094 | S4b-e-VP-2-8664d4326faa | 1 | 0.157 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S4b-e-VP-3-bc1154b2eab4 | 1 | 0.1628 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S4b-e-VP-4-ee510703be24 | 1 | 0.1646 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S4b-a-VP-0-efce3e9618d5 | 1 | 0.2113 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S4b-a-VP-0-988c423bb77a | 1 | 0.1733 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S4b-a-VP-0-c52c21e9532a | 1 | 0.1478 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S4b-a-VP-0-3fc170b38095 | 1 | 0.1027 | <= 0.1 |
| MINOR | PP-SWR-062 | S5-ncap-solid-left-3-VP-5-4acb5b0a3172 | 1 | 2 | = 0 |
| MINOR | PP-SWR-062 | S5-ncap-solid-right-3-VP-5-5a13dff6278d | 1 | 2 | = 0 |
| MINOR | PP-SWR-062 | S6-b-VP-5-025575367d8c | 1 | 2 | = 0 |
| MINOR | PP-SWR-062 | S6-e-VP-5-0584f057ac9e | 1 | 1 | = 0 |
| MINOR | PP-SWR-062 | S6-ncap-edge-right-3-VP-5-f947a2b37a7b | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-094 | S7-c-VP-0-6f0945db5008 | 1 | 0.1066 | <= 0.1 |
| MINOR | PP-SWR-090 | S7-e-VP-0-026423a10d14 | 1 | 1 | <= 0 |
| BLOCKER | PP-SWR-094 | S7-e-VP-0-026423a10d14 | 1 | 0.1434 | <= 0.1 |
| MINOR | PP-SWR-090 | S7-e-VP-1-daffb04432a6 | 1 | 1 | <= 0 |
| BLOCKER | PP-SWR-094 | S7-e-VP-1-daffb04432a6 | 1 | 0.1027 | <= 0.1 |
| MINOR | PP-SWR-090 | S7-e-VP-2-811b19470645 | 1 | 1 | <= 0 |
| BLOCKER | PP-SWR-094 | S7-e-VP-2-811b19470645 | 1 | 0.1163 | <= 0.1 |
| MINOR | PP-SWR-090 | S7-e-VP-3-d87df3330135 | 1 | 1 | <= 0 |
| BLOCKER | PP-SWR-094 | S7-e-VP-3-d87df3330135 | 1 | 0.1137 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S7-ncap-oncoming-left-2-VP-5-439b6019b6b6 | 1 | 0.1035 | <= 0.1 |
| MINOR | PP-SWR-062 | S7-ncap-oncoming-left-2-VP-5-439b6019b6b6 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-094 | S7-ncap-oncoming-left-3-VP-0-fef4c4db8db4 | 1 | 0.1168 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S7-ncap-oncoming-left-4-VP-0-2f8612617bd6 | 1 | 0.117 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S7-ncap-oncoming-left-5-VP-0-6ae4e2a40d09 | 1 | 0.1177 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S7-ncap-oncoming-left-6-VP-0-c644d22dab80 | 1 | 0.1633 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S7-ncap-oncoming-left-6-VP-2-15659ca78f0a | 1 | 0.1139 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S7-ncap-oncoming-left-6-VP-3-1c689d35c1b8 | 1 | 0.1126 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S7-ncap-oncoming-left-6-VP-4-2a08dfdd25a8 | 1 | 0.1176 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8-ncap-overtaking-left-72-2-VP-0-a23bfe4f2fa5 | 1 | 0.1171 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8-ncap-overtaking-left-72-3-VP-0-e2f0ea7d308e | 1 | 0.1168 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8-ncap-overtaking-left-72-4-VP-0-2b3a6aab2111 | 1 | 0.117 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8-ncap-overtaking-left-72-5-VP-0-5777015be1c0 | 1 | 0.1177 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8-ncap-overtaking-left-72-6-VP-0-0579c18d5198 | 1 | 0.1633 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8-ncap-overtaking-left-72-6-VP-2-edc01f63325f | 1 | 0.1139 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8-ncap-overtaking-left-72-6-VP-3-ed95053b7bad | 1 | 0.1126 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8-ncap-overtaking-left-72-6-VP-4-f47122da8706 | 1 | 0.1176 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8-ncap-overtaking-left-80-2-VP-0-9804f1f6a189 | 1 | 0.1171 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8-ncap-overtaking-left-80-3-VP-0-582335ee824c | 1 | 0.1168 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8-ncap-overtaking-left-80-4-VP-0-55dbe76785a0 | 1 | 0.117 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8-ncap-overtaking-left-80-5-VP-0-e2d4ae4af09d | 1 | 0.1177 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8-ncap-overtaking-left-80-6-VP-0-b156e26a02fd | 1 | 0.1633 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8-ncap-overtaking-left-80-6-VP-2-6b1222966f2b | 1 | 0.1139 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8-ncap-overtaking-left-80-6-VP-3-a76d87b3a74a | 1 | 0.1126 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8-ncap-overtaking-left-80-6-VP-4-0cbde2b617d6 | 1 | 0.1176 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8-ncap-indicated-left-72-5-VP-0-5c3c7e9ca60a | 1 | 0.1178 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8-ncap-indicated-left-72-6-VP-0-aed1782d180f | 1 | 0.1177 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8-ncap-indicated-left-72-7-VP-0-0c6d36281de5 | 1 | 0.1123 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8-ncap-indicated-left-80-5-VP-0-1d4e81b922e5 | 1 | 0.1178 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8-ncap-indicated-left-80-6-VP-0-f4639fd2f64c | 1 | 0.1177 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8-ncap-indicated-left-80-7-VP-0-75eaa0341b8e | 1 | 0.1123 | <= 0.1 |
| MINOR | PP-SWR-055 | S3b-d-VP-5-befbcf67d7a8 | 1 | 0 | > 0 |
| MINOR | PP-SWR-058 | S3b-d-VP-5-befbcf67d7a8 | 1 | 0 | > 0 |
| MINOR | PP-SWR-062 | S3b-d-VP-5-befbcf67d7a8 | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-094 | S8b-c-VP-0-b7f431c8a478 | 1 | 0.24 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8b-c-VP-1-bb7979e8243e | 1 | 0.1672 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8b-c-VP-2-0dfc5ffed8c6 | 1 | 0.2038 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8b-c-VP-3-a1393c0de570 | 1 | 0.2058 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8b-c-VP-4-7888642b1a30 | 1 | 0.2109 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S8b-c-VP-5-95f29b93c5d0 | 1 | 0.121 | <= 0.1 |
| MINOR | PP-SWR-062 | S8b-c-VP-5-95f29b93c5d0 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-051 | S9-a-VP-5-6fda0ebe7bd8 | 1 | -0.115 | >= 0 |
| MINOR | PP-SWR-062 | S9-a-VP-5-6fda0ebe7bd8 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-094 | S9-a-VP-0-964730713cf4 | 1 | 0.1198 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S9-a-VP-0-3f02d6f1ced4 | 1 | 0.1033 | <= 0.1 |
| MINOR | PP-SWR-032 | S12-c-VP-0-425b042b9630 | 1 | 1 | <= 0 |
| BLOCKER | PP-SWR-094 | S12-c-VP-0-425b042b9630 | 1 | 0.1608 | <= 0.1 |
| MINOR | PP-SWR-032 | S12-c-VP-0-425b042b9630 | 2 | 1 | <= 0 |
| BLOCKER | PP-SWR-094 | S12-c-VP-0-425b042b9630 | 2 | 0.1582 | <= 0.1 |
| MINOR | PP-SWR-032 | S12-c-VP-1-c5f495806475 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-1-c5f495806475 | 2 | 1 | <= 0 |
| BLOCKER | PP-SWR-094 | S12-c-VP-1-c5f495806475 | 2 | 0.1257 | <= 0.1 |
| MINOR | PP-SWR-032 | S12-c-VP-2-dcd8acfe5043 | 1 | 1 | <= 0 |
| BLOCKER | PP-SWR-094 | S12-c-VP-2-dcd8acfe5043 | 1 | 0.1348 | <= 0.1 |
| MINOR | PP-SWR-032 | S12-c-VP-2-dcd8acfe5043 | 2 | 1 | <= 0 |
| BLOCKER | PP-SWR-094 | S12-c-VP-2-dcd8acfe5043 | 2 | 0.1361 | <= 0.1 |
| MINOR | PP-SWR-032 | S12-c-VP-3-4b7830a9f53c | 1 | 1 | <= 0 |
| BLOCKER | PP-SWR-094 | S12-c-VP-3-4b7830a9f53c | 1 | 0.1323 | <= 0.1 |
| MINOR | PP-SWR-032 | S12-c-VP-3-4b7830a9f53c | 2 | 1 | <= 0 |
| BLOCKER | PP-SWR-094 | S12-c-VP-3-4b7830a9f53c | 2 | 0.1472 | <= 0.1 |
| MINOR | PP-SWR-032 | S12-c-VP-4-406ed8c312c5 | 1 | 1 | <= 0 |
| BLOCKER | PP-SWR-094 | S12-c-VP-4-406ed8c312c5 | 1 | 0.1352 | <= 0.1 |
| MINOR | PP-SWR-032 | S12-c-VP-4-406ed8c312c5 | 2 | 1 | <= 0 |
| BLOCKER | PP-SWR-094 | S12-c-VP-4-406ed8c312c5 | 2 | 0.1499 | <= 0.1 |
| MINOR | PP-SWR-032 | S12-c-VP-5-7039c477036e | 1 | 1 | <= 0 |
| BLOCKER | PP-SWR-094 | S12-c-VP-5-7039c477036e | 1 | 0.1098 | <= 0.1 |
| MINOR | PP-SWR-032 | S12-c-VP-5-7039c477036e | 2 | 1 | <= 0 |
| BLOCKER | PP-SWR-094 | S12-c-VP-5-7039c477036e | 2 | 0.1453 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S12-d-VP-0-aa6a4007e24f | 1 | 0.2944 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S12-d-VP-0-aa6a4007e24f | 2 | 0.1264 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S12-d-VP-1-32e05ce9da2f | 1 | 0.2715 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S12-d-VP-1-32e05ce9da2f | 2 | 0.1351 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S12-d-VP-2-f8db4bffd193 | 1 | 0.2874 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S12-d-VP-2-f8db4bffd193 | 2 | 0.1876 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S12-d-VP-3-0739ffa64fa8 | 1 | 0.2813 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S12-d-VP-4-6c8c429307ff | 1 | 0.2876 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S12-d-VP-5-6c4d792cde2a | 1 | 0.2883 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S12-d-VP-5-6c4d792cde2a | 2 | 0.2237 | <= 0.1 |
| MINOR | PP-SWR-062 | S13-a-VP-5-4d54367ca2b0 | 1 | 1 | = 0 |
| MINOR | PP-SWR-062 | S13-b-VP-5-72d0771a6181 | 1 | 1 | = 0 |
| MINOR | PP-SWR-062 | S13-c-VP-5-724d6d5db36f | 1 | 1 | = 0 |
| MINOR | PP-SWR-062 | S13-c-elk-VP-5-9fe8e17e251a | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-094 | S13-a-VP-0-4b0094025b0e | 1 | 0.2757 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S13-a-VP-0-585a6a3ace16 | 1 | 0.3508 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S13-a-VP-0-046a0af80c93 | 1 | 0.2441 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S16-c-VP-0-fde743d6df3f | 1 | 0.191 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S16-c-VP-2-70ee4251d683 | 1 | 0.1897 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S16-c-VP-3-7333de786139 | 1 | 0.2219 | <= 0.1 |
| BLOCKER | PP-SWR-086 | S16-c-VP-3-7333de786139 | 1 | -0.3281 | >= -0.3 |
| BLOCKER | PP-SWR-086 | S16-c-VP-4-17c9ae7cbeeb | 1 | -0.3691 | >= -0.3 |
| BLOCKER | PP-SWR-085 | S16-c-VP-5-8588c1885ba1 | 1 | -0.1121 | >= 0 |
| BLOCKER | PP-SWR-086 | S16-c-VP-5-8588c1885ba1 | 1 | -0.4586 | >= -0.3 |
| MINOR | PP-SWR-062 | S16-c-VP-5-8588c1885ba1 | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-085 | S16-d-VP-2-d8db2d5453a8 | 1 | -0.0003709 | >= 0 |
| BLOCKER | PP-SWR-085 | S16-d-VP-3-c4c71c213cb3 | 1 | -0.0528 | >= 0 |
| BLOCKER | PP-SWR-094 | S16-c-VP-0-da72edc4ec56 | 1 | 0.191 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S16-c-VP-0-8573bbceb147 | 1 | 0.1909 | <= 0.1 |
| BLOCKER | PP-SWR-094 | S16-c-VP-0-6f5b10397642 | 1 | 0.1909 | <= 0.1 |
| BLOCKER | PP-SWR-177 | S17-a-VP-0-5105ff294646 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S17-a-VP-1-b9fbf78497f4 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S17-a-VP-2-a0ad82d26dac | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S17-a-VP-3-4dd4051c83b7 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S17-a-VP-4-58d06da5fa48 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S17-a-VP-5-b494108de31a | 1 | 39 | = 0 |
| MINOR | PP-SWR-062 | S17-a-VP-5-b494108de31a | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-051 | S17-b-VP-0-3de8f33b03db | 1 | -0.298 | >= 0 |
| BLOCKER | PP-SWR-177 | S17-b-VP-0-3de8f33b03db | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-051 | S17-b-VP-1-e7d4b9f04c9b | 1 | -0.1362 | >= 0 |
| BLOCKER | PP-SWR-177 | S17-b-VP-1-e7d4b9f04c9b | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-051 | S17-b-VP-2-31d7c4a6ad1f | 1 | -0.2133 | >= 0 |
| BLOCKER | PP-SWR-177 | S17-b-VP-2-31d7c4a6ad1f | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-051 | S17-b-VP-3-d35d81d4965b | 1 | -0.2707 | >= 0 |
| BLOCKER | PP-SWR-177 | S17-b-VP-3-d35d81d4965b | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-051 | S17-b-VP-4-fce608d216a6 | 1 | -0.3233 | >= 0 |
| BLOCKER | PP-SWR-177 | S17-b-VP-4-fce608d216a6 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-051 | S17-b-VP-5-7c84dc0ea45e | 1 | -0.4577 | >= 0 |
| BLOCKER | PP-SWR-177 | S17-b-VP-5-7c84dc0ea45e | 1 | 39 | = 0 |
| MINOR | PP-SWR-062 | S17-b-VP-5-7c84dc0ea45e | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-051 | S17-c-VP-0-ec530a565153 | 1 | -5.581 | >= 0 |
| BLOCKER | PP-SWR-177 | S17-c-VP-0-ec530a565153 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-051 | S17-c-VP-1-2fb27134ba07 | 1 | -5.702 | >= 0 |
| BLOCKER | PP-SWR-177 | S17-c-VP-1-2fb27134ba07 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-051 | S17-c-VP-2-d36a269b1605 | 1 | -5.935 | >= 0 |
| BLOCKER | PP-SWR-177 | S17-c-VP-2-d36a269b1605 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-051 | S17-c-VP-3-23bdadaaa5df | 1 | -6.04 | >= 0 |
| BLOCKER | PP-SWR-177 | S17-c-VP-3-23bdadaaa5df | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-051 | S17-c-VP-4-7235bceb0cae | 1 | -6.074 | >= 0 |
| BLOCKER | PP-SWR-177 | S17-c-VP-4-7235bceb0cae | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-051 | S17-c-VP-5-2fa05512e157 | 1 | -6.284 | >= 0 |
| BLOCKER | PP-SWR-177 | S17-c-VP-5-2fa05512e157 | 1 | 39 | = 0 |
| MINOR | PP-SWR-062 | S17-c-VP-5-2fa05512e157 | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-177 | S17-d-VP-0-e467f84e66b8 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S17-d-VP-1-a9288ab81d0a | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S17-d-VP-2-5903ede95f66 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-051 | S17-d-VP-3-32384fa9491c | 1 | -0.008657 | >= 0 |
| BLOCKER | PP-SWR-177 | S17-d-VP-3-32384fa9491c | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-051 | S17-d-VP-4-0847e3e773ff | 1 | -0.07578 | >= 0 |
| BLOCKER | PP-SWR-177 | S17-d-VP-4-0847e3e773ff | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-051 | S17-d-VP-5-adc239af2eb2 | 1 | -0.3885 | >= 0 |
| BLOCKER | PP-SWR-177 | S17-d-VP-5-adc239af2eb2 | 1 | 39 | = 0 |
| MINOR | PP-SWR-062 | S17-d-VP-5-adc239af2eb2 | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-177 | S17-e-VP-0-ba174f20d191 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S17-e-VP-1-44240971d4fe | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S17-e-VP-2-9daf913922a5 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S17-e-VP-3-07cdc785eb90 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S17-e-VP-4-74ec7f3c45ba | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S17-e-VP-5-f985196e415b | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S17-a-VP-0-1693de53b176 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | S17-a-VP-0-7207c0f721bf | 1 | 39 | = 0 |
| MINOR | PP-SWR-062 | S20-b-VP-5-2790db1df683 | 1 | 2 | = 0 |
| MINOR | PP-SWR-062 | S20-c-VP-5-4c60083ac9aa | 1 | 1 | = 0 |
| MINOR | PP-SWR-062 | S20-d-VP-5-0068791828e3 | 1 | 1 | = 0 |
| MINOR | PP-SWR-062 | S20-e-VP-5-04f6e1b49552 | 1 | 1 | = 0 |
| MINOR | PP-SWR-062 | S20-a-VP-5-c5bc50661089 | 1 | 2 | = 0 |
| MINOR | PP-SWR-090 | S21-b-VP-3-453cc4061626 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S21-c-VP-0-8a44926c5f2c | 1 | 1 | <= 0 |
| BLOCKER | PP-SWR-094 | S21-c-VP-0-8a44926c5f2c | 1 | 0.1434 | <= 0.1 |
| MINOR | PP-SWR-090 | S21-c-VP-1-6ca8cd2330f0 | 1 | 1 | <= 0 |
| BLOCKER | PP-SWR-094 | S21-c-VP-1-6ca8cd2330f0 | 1 | 0.1027 | <= 0.1 |
| MINOR | PP-SWR-090 | S21-c-VP-2-c5c8cbaefcf1 | 1 | 1 | <= 0 |
| BLOCKER | PP-SWR-094 | S21-c-VP-2-c5c8cbaefcf1 | 1 | 0.1163 | <= 0.1 |
| MINOR | PP-SWR-090 | S21-c-VP-3-c4abc77291be | 1 | 1 | <= 0 |
| BLOCKER | PP-SWR-094 | S21-c-VP-3-c4abc77291be | 1 | 0.1137 | <= 0.1 |
| MINOR | PP-SWR-090 | S21-c-VP-4-6c90daf13315 | 1 | 1 | <= 0 |
| BLOCKER | PP-SWR-094 | S21-c-VP-4-6c90daf13315 | 1 | 0.1096 | <= 0.1 |
| MINOR | PP-SWR-090 | S21-c-VP-5-cb4f72656e1d | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S21-c-VP-5-cb4f72656e1d | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-171 | S22-e-VP-0-6a0b15bf41ce | 1 | 6 | = 0 |
| BLOCKER | PP-SWR-171 | S22-e-VP-1-cb77b9982ed7 | 1 | 7 | = 0 |
| BLOCKER | PP-SWR-171 | S22-e-VP-2-7e815a10acd8 | 1 | 6 | = 0 |
| BLOCKER | PP-SWR-171 | S22-e-VP-3-315220d56377 | 1 | 6 | = 0 |
| BLOCKER | PP-SWR-171 | S22-e-VP-4-e573fdd87cfc | 1 | 7 | = 0 |
| BLOCKER | PP-SWR-171 | S22-e-VP-5-876e2407c39d | 1 | 11 | = 0 |
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
| BLOCKER | PP-SWR-177 | F03-c-S1a-VP-0-1c03af025ee4 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F03-c-S1a-VP-1-a5219f0b3fc2 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F03-c-S1a-VP-5-4a0b9685f06c | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F03-a-S1a-VP-0-696cd0fecc6d | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-177 | F03-c-S1c-VP-0-0e2929c3df25 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F03-c-S1c-VP-1-4278b1e68610 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F03-c-S1c-VP-5-ce2933b62cf1 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F03-a-S1c-VP-0-a5eee64bfd3c | 1 | 2 | = 0 |
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
| BLOCKER | PP-SWR-177 | F08-b-S1c-VP-0-4ae7633cf949 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F08-b-S1c-VP-1-297eab73e001 | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F08-b-S1c-VP-5-9d66d718191a | 1 | 39 | = 0 |
| BLOCKER | PP-SWR-177 | F08-c-S1c-VP-0-bca0f1afb997 | 1 | 78 | = 0 |
| BLOCKER | PP-SWR-177 | F08-c-S1c-VP-1-3d8334644eea | 1 | 78 | = 0 |
| BLOCKER | PP-SWR-177 | F08-c-S1c-VP-5-06d7bb8fda8b | 1 | 78 | = 0 |
| BLOCKER | PP-SWR-177 | F15-c-S1a-VP-0-1759e7623f79 | 1 | 16 | = 0 |
| BLOCKER | PP-SWR-177 | F15-c-S1a-VP-1-ee83c26fa37b | 1 | 16 | = 0 |
| BLOCKER | PP-SWR-177 | F15-c-S1a-VP-5-36b99b375e24 | 1 | 16 | = 0 |
| BLOCKER | PP-SWR-177 | F15-c-S1c-VP-0-10538de9a5b7 | 1 | 16 | = 0 |
| BLOCKER | PP-SWR-177 | F15-c-S1c-VP-1-768b8651648e | 1 | 16 | = 0 |
| BLOCKER | PP-SWR-177 | F15-c-S1c-VP-5-8bd5e66f138e | 1 | 16 | = 0 |
| BLOCKER | PP-SWR-124 | F25-c-S22a-VP-0-191326001926 | 1 | 3 | = 0 |
| BLOCKER | PP-SWR-124 | F25-c-S22a-VP-1-42edbe799a5c | 1 | 5 | = 0 |
| BLOCKER | PP-SWR-124 | F25-c-S22a-VP-5-dc4b57212bae | 1 | 4 | = 0 |
| BLOCKER | PP-SWR-124 | F25-e-S22a-VP-0-2219ed6d348d | 1 | 3 | = 0 |
| BLOCKER | PP-SWR-124 | F25-e-S22a-VP-1-39ef91d1dee2 | 1 | 5 | = 0 |
| BLOCKER | PP-SWR-124 | F25-e-S22a-VP-5-fb5ac378351a | 1 | 4 | = 0 |
| BLOCKER | PP-SWR-124 | F25-a-S22a-VP-0-85b221025492 | 1 | 3 | = 0 |
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
| BLOCKER | PP-SWR-051 | S9-a-VP-5-6fda0ebe7bd8-lcc-only | 1 | -0.115 | >= 0 |
| MINOR | PP-SWR-062 | S9-a-VP-5-6fda0ebe7bd8-lcc-only | 1 | 1 | = 0 |

## Bộ theo khía cạnh

| Bộ | Khía cạnh | Lần chạy | Kết luận | BLOCKER | MAJOR | MINOR |
|---|---|---|---|---|---|---|
| B0 | Conformance | — | Đạt C1, C2; Tích hợp được | — | — | — |
| B1 | Nominal | 1004 | Không đạt | 97 | 0 | 7 |
| B2 | Regulatory | 594 | Không đạt | 46 | 0 | 0 |
| B3 | Performance limit | 310 | Không đạt | 35 | 0 | 2 |
| B4 | Robustness | 995 | Không đạt | 69 | 0 | 42 |
| B5 | Degradation and refusal | 399 | Không đạt | 20 | 0 | 14 |
| B6 | Comfort | 1004 | Không đạt | 97 | 0 | 7 |
| B7 | Flexibility | 803 | Không đạt | 81 | 0 | 15 |
| B8 | Compute | 2309 | Không đạt | 201 | 0 | 51 |

## Số lần chạy

```json
{
 "planned": 2309,
 "executed": 2309,
 "failed": 203,
 "failed_out_of_scope": 361,
 "errors": 0,
 "execution_faults": 0,
 "not_judged": 6,
 "partial": false
}
```

## Flexibility

Cùng bản build và bộ calibration trên mọi profile (mục 8.3). Ô là giá trị xấu nhất của profile trên các ca chạy đủ mọi profile; **đậm** là profile tệ nhất của chỉ số. Bộ chạy là B7. Tỉ lệ đạt requirement: số requirement không trượt ở lần chạy nào của profile, chia số requirement được chấm trên profile đó.

| Profile | Lần chạy | Tỉ lệ đạt requirement | Requirement trượt | PP-SWR-002 a_y thêm vào lớn nhất khi đưa về giữa | PP-SWR-004 Jerk ngang RMS của path 0–1 s khi HWA lái | PP-SWR-004 Jerk ngang lớn nhất của path khi HWA lái (trung bình 0,5 s) | PP-SWR-004 Tốc độ quay vô lăng RMS khi HWA lái, vòng kín | PP-SWR-050 Lệch ngang của path so với tâm làn thật, 0–1 s, lớn nhất | PP-SWR-053 Thời gian đưa xe về giữa (lệch ≤ 0,1 m) | PP-SWR-057 Khoảng cách ngang nhỏ nhất từ thân xe tới xe lớn khi ngang hàng | PP-SWR-059 Thời gian từ lúc hết ngang hàng tới lúc lệch ≤ 0,1 m | PP-SWR-081 Thời lượng path LKA tới COMPLETED | PP-SWR-082 Thời lượng path ELK tới COMPLETED | PP-SWR-087 DTLE LKA nhỏ nhất |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VP-0 | 210 | 91.2% | PP-SWR-032, PP-SWR-085, PP-SWR-094 | 1.32 | 0.287 | 1.58 | 0.189 | 1.05 | 3.8 | 0.588 | 1.65 | **4.33** | **4.15** | 0.0205 |
| VP-1 | 145 | 97.1% | PP-SWR-094 | **1.56** | **0.323** | **1.58** | **0.189** | 0.993 | 3.52 | 0.558 | 1.5 | 3.95 | 3.75 | 0.0421 |
| VP-2 | 103 | 85.7% | PP-SWR-032, PP-SWR-084, PP-SWR-085, PP-SWR-090, PP-SWR-094 | 1.36 | 0.287 | 1.58 | 0.189 | 1.04 | 3.76 | 0.483 | 1.7 | 4.17 | 4 | 0.0338 |
| VP-3 | 102 | 85.3% | PP-SWR-032, PP-SWR-084, PP-SWR-085, PP-SWR-090, PP-SWR-094 | 1.31 | 0.288 | 1.57 | 0.189 | 1.05 | 3.82 | 0.433 | 1.67 | 4.22 | 4.08 | 0.000736 |
| VP-4 | 102 | 88.2% | PP-SWR-085, PP-SWR-086, PP-SWR-090, PP-SWR-094 | 1.26 | 0.288 | 1.57 | 0.189 | **1.07** | **3.86** | 0.41 | **1.72** | 4.27 | 3.62 | -0.00279 |
| VP-5 | 141 | 86.1% | PP-SWR-032, PP-SWR-051, PP-SWR-085, PP-SWR-086, PP-SWR-094 | 1.26 | 0.288 | 1.57 | 0.189 | 1.07 | 3.86 | **0.287** | 1.72 | 4.17 | 3.27 | **-0.0221** |

| Chỉ số | Độ chênh lớn nhất giữa profile | Độ chênh nhỏ nhất | Profile tệ nhất |
|---|---|---|---|
| PP-SWR-002 a_y thêm vào lớn nhất khi đưa về giữa | 0.296 | 0 | VP-1 |
| PP-SWR-004 Jerk ngang RMS của path 0–1 s khi HWA lái | 0.0597 | 7.37e-06 | VP-1 |
| PP-SWR-004 Jerk ngang lớn nhất của path khi HWA lái (trung bình 0,5 s) | 0.446 | 0 | VP-1 |
| PP-SWR-004 Tốc độ quay vô lăng RMS khi HWA lái, vòng kín | 0.0137 | 0.000523 | VP-1 |
| PP-SWR-050 Lệch ngang của path so với tâm làn thật, 0–1 s, lớn nhất | 0.146 | 0 | VP-4 |
| PP-SWR-053 Thời gian đưa xe về giữa (lệch ≤ 0,1 m) | 0.34 | 0 | VP-4 |
| PP-SWR-057 Khoảng cách ngang nhỏ nhất từ thân xe tới xe lớn khi ngang hàng | 0.301 | 0.293 | VP-5 |
| PP-SWR-059 Thời gian từ lúc hết ngang hàng tới lúc lệch ≤ 0,1 m | 1.72 | 0 | VP-4 |
| PP-SWR-081 Thời lượng path LKA tới COMPLETED | 0.75 | 0.125 | VP-0 |
| PP-SWR-082 Thời lượng path ELK tới COMPLETED | 1.72 | 0.025 | VP-0 |
| PP-SWR-087 DTLE LKA nhỏ nhất | 0.136 | 0.0132 | VP-5 |

Requirement đạt 100 % trên mọi profile: không (VP-0, VP-1, VP-2, VP-3, VP-4, VP-5)

## Thời gian tính

1825090 chu kỳ. p95 ≤ 2 ms, p99 ≤ 3.98 ms (cận trên của bin), lớn nhất 618 ms. Đo trên máy chạy SIL, gồm adapter; không khẳng định thời gian trên ECU (mục 9.1).

![Thời gian tính](figures/compute.png)

## DTLE theo v_lat

| Kịch bản | v_lat [m/s] | DTLE nhỏ nhất [m] |
|---|---|---|
| S4 | 0 | 0.0679 |
| S4 | 0.2 | 0.0993 |
| S4 | 0.3 | 0.146 |
| S4 | 0.4 | 0.0695 |
| S4 | 0.5 | 0.196 |
| S4 | 0.6 | -0.0221 |
| S4b | 0.2 | 0.109 |
| S4b | 0.3 | 0.0657 |
| S4b | 0.6 | 0.0686 |
| S5 | 0.2 | -0.28 |
| S5 | 0.3 | -0.352 |
| S5 | 0.4 | 0.0207 |
| S5 | 0.5 | 0.0316 |
| S5 | 0.6 | -0.325 |
| S6 | 0.2 | -0.28 |
| S6 | 0.3 | -0.352 |
| S6 | 0.4 | 0.0363 |
| S6 | 0.5 | 0.0983 |
| S6 | 0.6 | -0.36 |
| S7 | 0.2 | -0.162 |
| S7 | 0.3 | 0.144 |
| S7 | 0.4 | 0.156 |
| S7 | 0.5 | 0.205 |
| S7 | 0.6 | 0.0984 |
| S8 | 0.2 | 0.0547 |
| S8 | 0.3 | 0.0753 |
| S8 | 0.4 | 0.0588 |
| S8 | 0.5 | 0.0536 |
| S8 | 0.6 | 0.0388 |
| S8 | 0.7 | 0.0515 |
| S8b | 0.5 | -0.316 |
| S8c | 0.4 | 0.28 |

![DTLE theo v_lat](figures/dtle_v_lat.png)

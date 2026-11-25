# Kết luận: Không đạt

- Planner: pp_lcc 0.3.0 commit 54307f18d7c4 calibration 69e3337d118c t7 quintic (0f506716bd8e) / pp_lkaelk 0.3.0 commit 54307f18d7c4 calibration 69e3337d118c (b6451e1f7d72)
- Simulator: commit 54307f1-dirty (simulator và bên chấm), behavior_checksum/2, run_bundle/1; chưa model nào trong 9 model được validation với dữ liệu thật (Simulation Handbook mục 9, 15)
- Tích hợp được: có
- Đã chạy: 2310 lần chạy; trượt BLOCKER 223, MAJOR 0, MINOR 43; 10 ca không được chấm
- Kết luận chỉ đúng trong phạm vi đã thử, không phải bằng chứng an toàn (Software Qualification Test Specification 3).

## Trượt BLOCKER

| Requirement | Safety goal | Ca | Profile | Seed | Trượt đầu tiên [s] | Giá trị | Ngưỡng | Chi tiết | MCAP |
|---|---|---|---|---|---|---|---|---|---|
| PP-SWR-051 | SG-01 | F02-e-S1a-VP-5-29183b65ffaf | VP-5 | 1 | — | -0.1106 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F02-e-S1a-VP-5-29183b65ffaf_seed1.mcap |
| PP-SWR-051 | SG-01 | F02-e-S1c-VP-5-50d3444b79d5 | VP-5 | 1 | — | -0.1491 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F02-e-S1c-VP-5-50d3444b79d5_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1a-VP-5-9e2995fea291 | VP-5 | 1 | — | -0.2729 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F06-d-S1a-VP-5-9e2995fea291_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1c-VP-5-bdab3c9103b7 | VP-5 | 1 | — | -0.2797 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F06-d-S1c-VP-5-bdab3c9103b7_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-b-S1c-VP-1-297eab73e001 | VP-1 | 1 | — | -0.3463 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F08-b-S1c-VP-1-297eab73e001_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-b-S1c-VP-5-9d66d718191a | VP-5 | 1 | — | -0.1948 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F08-b-S1c-VP-5-9d66d718191a_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1c-VP-0-bca0f1afb997 | VP-0 | 1 | — | -0.9853 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F08-c-S1c-VP-0-bca0f1afb997_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1c-VP-1-3d8334644eea | VP-1 | 1 | — | -1.017 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F08-c-S1c-VP-1-3d8334644eea_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1c-VP-5-06d7bb8fda8b | VP-5 | 1 | — | -1.269 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F08-c-S1c-VP-5-06d7bb8fda8b_seed1.mcap |
| PP-SWR-063 | SG-01 | S19-f-VP-5-9c4f0f44d054 | VP-5 | 1 | — | 0.008746 | = 1 | Tỉ lệ chu kỳ có path hợp lệ báo lane_too_narrow khi khoảng trống thật < free_space_min | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S19-f-VP-5-9c4f0f44d054_seed1.mcap |
| PP-SWR-094 | SG-01 | S12-c-VP-0-425b042b9630 | VP-0 | 1 | — | 0.1717 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S12-c-VP-0-425b042b9630_seed1.mcap |
| PP-SWR-094 | SG-01 | S12-c-VP-2-dcd8acfe5043 | VP-2 | 1 | — | 0.1392 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S12-c-VP-2-dcd8acfe5043_seed1.mcap |
| PP-SWR-094 | SG-01 | S12-c-VP-3-4b7830a9f53c | VP-3 | 1 | — | 0.1343 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S12-c-VP-3-4b7830a9f53c_seed1.mcap |
| PP-SWR-094 | SG-01 | S12-c-VP-4-406ed8c312c5 | VP-4 | 1 | — | 0.1401 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S12-c-VP-4-406ed8c312c5_seed1.mcap |
| PP-SWR-094 | SG-01 | S12-c-VP-5-7039c477036e | VP-5 | 1 | — | 0.1184 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S12-c-VP-5-7039c477036e_seed1.mcap |
| PP-SWR-094 | SG-01 | S12-d-VP-0-aa6a4007e24f | VP-0 | 1 | — | 0.1288 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S12-d-VP-0-aa6a4007e24f_seed1.mcap |
| PP-SWR-094 | SG-01 | S12-d-VP-1-32e05ce9da2f | VP-1 | 1 | — | 0.1169 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S12-d-VP-1-32e05ce9da2f_seed1.mcap |
| PP-SWR-094 | SG-01 | S12-d-VP-2-f8db4bffd193 | VP-2 | 1 | — | 0.1262 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S12-d-VP-2-f8db4bffd193_seed1.mcap |
| PP-SWR-094 | SG-01 | S12-d-VP-3-0739ffa64fa8 | VP-3 | 1 | — | 0.1295 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S12-d-VP-3-0739ffa64fa8_seed1.mcap |
| PP-SWR-094 | SG-01 | S12-d-VP-4-6c8c429307ff | VP-4 | 1 | — | 0.1324 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S12-d-VP-4-6c8c429307ff_seed1.mcap |
| PP-SWR-094 | SG-01 | S12-d-VP-5-6c4d792cde2a | VP-5 | 1 | — | 0.1329 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S12-d-VP-5-6c4d792cde2a_seed1.mcap |
| PP-SWR-094 | SG-01 | S21-a-VP-0-1ce842f22036 | VP-0 | 1 | — | 0.1038 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S21-a-VP-0-1ce842f22036_seed1.mcap |
| PP-SWR-094 | SG-01 | S21-a-VP-0-35f6c34eabb6 | VP-0 | 1 | — | 0.1133 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S21-a-VP-0-35f6c34eabb6_seed1.mcap |
| PP-SWR-094 | SG-01 | S21-a-VP-0-c7c4936bd278 | VP-0 | 1 | — | 0.1133 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S21-a-VP-0-c7c4936bd278_seed1.mcap |
| PP-SWR-094 | SG-01 | S21-a-VP-0-f0fc9b5dece3 | VP-0 | 1 | — | 0.1133 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S21-a-VP-0-f0fc9b5dece3_seed1.mcap |
| PP-SWR-094 | SG-01 | S21-b-VP-0-71135b1aa5aa | VP-0 | 1 | — | 0.1049 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S21-b-VP-0-71135b1aa5aa_seed1.mcap |
| PP-SWR-094 | SG-01 | S21-c-VP-0-8a44926c5f2c | VP-0 | 1 | — | 0.1527 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S21-c-VP-0-8a44926c5f2c_seed1.mcap |
| PP-SWR-094 | SG-01 | S21-c-VP-1-6ca8cd2330f0 | VP-1 | 1 | — | 0.1079 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S21-c-VP-1-6ca8cd2330f0_seed1.mcap |
| PP-SWR-094 | SG-01 | S21-c-VP-2-c5c8cbaefcf1 | VP-2 | 1 | — | 0.1223 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S21-c-VP-2-c5c8cbaefcf1_seed1.mcap |
| PP-SWR-094 | SG-01 | S21-c-VP-3-c4abc77291be | VP-3 | 1 | — | 0.1191 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S21-c-VP-3-c4abc77291be_seed1.mcap |
| PP-SWR-094 | SG-01 | S21-c-VP-4-6c90daf13315 | VP-4 | 1 | — | 0.118 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S21-c-VP-4-6c90daf13315_seed1.mcap |
| PP-SWR-094 | SG-01 | S21-e-VP-0-bb241000f912 | VP-0 | 1 | — | 0.1038 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S21-e-VP-0-bb241000f912_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-a-VP-0-4bc2419e8202 | VP-0 | 1 | — | 0.1913 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-a-VP-0-4bc2419e8202_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-a-VP-0-55e33bb8f45c | VP-0 | 1 | — | 0.1925 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-a-VP-0-55e33bb8f45c_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-a-VP-1-f72dd46a760e | VP-1 | 1 | — | 0.1076 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-a-VP-1-f72dd46a760e_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-a-VP-2-9bb307fa21bf | VP-2 | 1 | — | 0.155 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-a-VP-2-9bb307fa21bf_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-a-VP-3-780a64228b47 | VP-3 | 1 | — | 0.1303 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-a-VP-3-780a64228b47_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-a-VP-4-0de130f39b20 | VP-4 | 1 | — | 0.135 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-a-VP-4-0de130f39b20_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-a-VP-5-b8c0c48677a9 | VP-5 | 1 | — | 0.1062 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-a-VP-5-b8c0c48677a9_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-b-VP-0-91061c99f8fa | VP-0 | 1 | — | 0.1038 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-b-VP-0-91061c99f8fa_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-c-VP-0-6f0945db5008 | VP-0 | 1 | — | 0.13 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-c-VP-0-6f0945db5008_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-d-VP-0-7cf2548b6eea | VP-0 | 1 | — | 0.1038 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-d-VP-0-7cf2548b6eea_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-e-VP-0-026423a10d14 | VP-0 | 1 | — | 0.1527 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-e-VP-0-026423a10d14_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-e-VP-1-daffb04432a6 | VP-1 | 1 | — | 0.1079 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-e-VP-1-daffb04432a6_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-e-VP-2-811b19470645 | VP-2 | 1 | — | 0.1223 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-e-VP-2-811b19470645_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-e-VP-3-d87df3330135 | VP-3 | 1 | — | 0.1191 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-e-VP-3-d87df3330135_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-e-VP-4-cd6bec0337d8 | VP-4 | 1 | — | 0.118 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-e-VP-4-cd6bec0337d8_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-ncap-oncoming-left-2-VP-2-3f770b3a90ee | VP-2 | 1 | — | 0.2067 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-ncap-oncoming-left-2-VP-2-3f770b3a90ee_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-ncap-oncoming-left-2-VP-3-c31a0a7a2f98 | VP-3 | 1 | — | 0.208 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-ncap-oncoming-left-2-VP-3-c31a0a7a2f98_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-ncap-oncoming-left-2-VP-4-71865f211c51 | VP-4 | 1 | — | 0.2144 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-ncap-oncoming-left-2-VP-4-71865f211c51_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-ncap-oncoming-left-2-VP-5-439b6019b6b6 | VP-5 | 1 | — | 0.1835 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-ncap-oncoming-left-2-VP-5-439b6019b6b6_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-ncap-oncoming-left-3-VP-0-fef4c4db8db4 | VP-0 | 1 | — | 0.1851 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-ncap-oncoming-left-3-VP-0-fef4c4db8db4_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-ncap-oncoming-left-3-VP-2-b86270e4aeba | VP-2 | 1 | — | 0.1189 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-ncap-oncoming-left-3-VP-2-b86270e4aeba_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-ncap-oncoming-left-3-VP-3-0d2565c30c21 | VP-3 | 1 | — | 0.1165 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-ncap-oncoming-left-3-VP-3-0d2565c30c21_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-ncap-oncoming-left-3-VP-4-3154e0a50f59 | VP-4 | 1 | — | 0.1201 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-ncap-oncoming-left-3-VP-4-3154e0a50f59_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-ncap-oncoming-left-4-VP-0-2f8612617bd6 | VP-0 | 1 | — | 0.1784 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-ncap-oncoming-left-4-VP-0-2f8612617bd6_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-ncap-oncoming-left-4-VP-2-5ae043bbf6bb | VP-2 | 1 | — | 0.1155 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-ncap-oncoming-left-4-VP-2-5ae043bbf6bb_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-ncap-oncoming-left-4-VP-3-7e40136def20 | VP-3 | 1 | — | 0.1129 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-ncap-oncoming-left-4-VP-3-7e40136def20_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-ncap-oncoming-left-4-VP-4-d964a9cc7fc9 | VP-4 | 1 | — | 0.1137 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-ncap-oncoming-left-4-VP-4-d964a9cc7fc9_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-ncap-oncoming-left-5-VP-0-6ae4e2a40d09 | VP-0 | 1 | — | 0.1731 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-ncap-oncoming-left-5-VP-0-6ae4e2a40d09_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-ncap-oncoming-left-5-VP-2-c55019b6b65d | VP-2 | 1 | — | 0.1121 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-ncap-oncoming-left-5-VP-2-c55019b6b65d_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-ncap-oncoming-left-5-VP-3-ff05492dc190 | VP-3 | 1 | — | 0.1068 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-ncap-oncoming-left-5-VP-3-ff05492dc190_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-ncap-oncoming-left-5-VP-4-15cf5680da16 | VP-4 | 1 | — | 0.11 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-ncap-oncoming-left-5-VP-4-15cf5680da16_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-ncap-oncoming-left-6-VP-0-c644d22dab80 | VP-0 | 1 | — | 0.2051 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-ncap-oncoming-left-6-VP-0-c644d22dab80_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-ncap-oncoming-left-6-VP-1-218f80ec53e5 | VP-1 | 1 | — | 0.1091 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-ncap-oncoming-left-6-VP-1-218f80ec53e5_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-ncap-oncoming-left-6-VP-2-15659ca78f0a | VP-2 | 1 | — | 0.1575 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-ncap-oncoming-left-6-VP-2-15659ca78f0a_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-ncap-oncoming-left-6-VP-3-1c689d35c1b8 | VP-3 | 1 | — | 0.137 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-ncap-oncoming-left-6-VP-3-1c689d35c1b8_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-ncap-oncoming-left-6-VP-4-2a08dfdd25a8 | VP-4 | 1 | — | 0.1412 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-ncap-oncoming-left-6-VP-4-2a08dfdd25a8_seed1.mcap |
| PP-SWR-094 | SG-01 | S7-ncap-oncoming-left-6-VP-5-cab30fbcc9c6 | VP-5 | 1 | — | 0.1053 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S7-ncap-oncoming-left-6-VP-5-cab30fbcc9c6_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-a-VP-0-2046a557f99d | VP-0 | 1 | — | 0.1133 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-a-VP-0-2046a557f99d_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-a-VP-0-3c2b724e844f | VP-0 | 1 | — | 0.1133 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-a-VP-0-3c2b724e844f_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-a-VP-0-732f3a009fb5 | VP-0 | 1 | — | 0.1133 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-a-VP-0-732f3a009fb5_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-b-VP-0-809917bd0037 | VP-0 | 1 | — | 0.1038 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-b-VP-0-809917bd0037_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-c-VP-0-469043666197 | VP-0 | 1 | — | 0.1005 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-c-VP-0-469043666197_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-d-VP-0-1b8a997aaaa7 | VP-0 | 1 | — | 0.1161 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-d-VP-0-1b8a997aaaa7_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-e-VP-0-1606f406bd00 | VP-0 | 1 | — | 0.1038 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-e-VP-0-1606f406bd00_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-indicated-left-72-5-VP-0-5c3c7e9ca60a | VP-0 | 1 | — | 0.1731 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-indicated-left-72-5-VP-0-5c3c7e9ca60a_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-indicated-left-72-5-VP-2-f8e7b7cfa553 | VP-2 | 1 | — | 0.1122 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-indicated-left-72-5-VP-2-f8e7b7cfa553_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-indicated-left-72-5-VP-3-fe1ca0c8225b | VP-3 | 1 | — | 0.1068 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-indicated-left-72-5-VP-3-fe1ca0c8225b_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-indicated-left-72-5-VP-4-032efa958603 | VP-4 | 1 | — | 0.1101 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-indicated-left-72-5-VP-4-032efa958603_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-indicated-left-72-6-VP-0-aed1782d180f | VP-0 | 1 | — | 0.1692 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-indicated-left-72-6-VP-0-aed1782d180f_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-indicated-left-72-6-VP-2-7f2fcaaab1ac | VP-2 | 1 | — | 0.1093 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-indicated-left-72-6-VP-2-7f2fcaaab1ac_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-indicated-left-72-6-VP-3-907f00b272d3 | VP-3 | 1 | — | 0.106 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-indicated-left-72-6-VP-3-907f00b272d3_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-indicated-left-72-6-VP-4-f21b00402c85 | VP-4 | 1 | — | 0.1087 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-indicated-left-72-6-VP-4-f21b00402c85_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-indicated-left-72-7-VP-0-0c6d36281de5 | VP-0 | 1 | — | 0.1915 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-indicated-left-72-7-VP-0-0c6d36281de5_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-indicated-left-72-7-VP-1-9a6bc4ab1329 | VP-1 | 1 | — | 0.1017 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-indicated-left-72-7-VP-1-9a6bc4ab1329_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-indicated-left-72-7-VP-2-30c7cf49785c | VP-2 | 1 | — | 0.1244 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-indicated-left-72-7-VP-2-30c7cf49785c_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-indicated-left-72-7-VP-3-39123b86bcc5 | VP-3 | 1 | — | 0.1254 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-indicated-left-72-7-VP-3-39123b86bcc5_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-indicated-left-72-7-VP-4-26c93a420e55 | VP-4 | 1 | — | 0.1271 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-indicated-left-72-7-VP-4-26c93a420e55_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-indicated-left-80-5-VP-0-1d4e81b922e5 | VP-0 | 1 | — | 0.1731 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-indicated-left-80-5-VP-0-1d4e81b922e5_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-indicated-left-80-5-VP-2-0a5939562854 | VP-2 | 1 | — | 0.1122 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-indicated-left-80-5-VP-2-0a5939562854_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-indicated-left-80-5-VP-3-a2ce50cc7fa7 | VP-3 | 1 | — | 0.1068 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-indicated-left-80-5-VP-3-a2ce50cc7fa7_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-indicated-left-80-5-VP-4-26675ff023c4 | VP-4 | 1 | — | 0.1101 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-indicated-left-80-5-VP-4-26675ff023c4_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-indicated-left-80-6-VP-0-f4639fd2f64c | VP-0 | 1 | — | 0.1692 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-indicated-left-80-6-VP-0-f4639fd2f64c_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-indicated-left-80-6-VP-2-9f1c3de1d808 | VP-2 | 1 | — | 0.1093 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-indicated-left-80-6-VP-2-9f1c3de1d808_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-indicated-left-80-6-VP-3-4d3e803af2b5 | VP-3 | 1 | — | 0.106 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-indicated-left-80-6-VP-3-4d3e803af2b5_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-indicated-left-80-6-VP-4-ca3bba24859a | VP-4 | 1 | — | 0.1087 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-indicated-left-80-6-VP-4-ca3bba24859a_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-indicated-left-80-7-VP-0-75eaa0341b8e | VP-0 | 1 | — | 0.1915 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-indicated-left-80-7-VP-0-75eaa0341b8e_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-indicated-left-80-7-VP-1-205e93d9397d | VP-1 | 1 | — | 0.1017 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-indicated-left-80-7-VP-1-205e93d9397d_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-indicated-left-80-7-VP-2-338f49c571b0 | VP-2 | 1 | — | 0.1244 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-indicated-left-80-7-VP-2-338f49c571b0_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-indicated-left-80-7-VP-3-4a1bb834fafa | VP-3 | 1 | — | 0.1254 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-indicated-left-80-7-VP-3-4a1bb834fafa_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-indicated-left-80-7-VP-4-8e705458f61b | VP-4 | 1 | — | 0.1271 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-indicated-left-80-7-VP-4-8e705458f61b_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-72-2-VP-0-a23bfe4f2fa5 | VP-0 | 1 | — | 0.19 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-72-2-VP-0-a23bfe4f2fa5_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-72-2-VP-1-c9b7d22f637b | VP-1 | 1 | — | 0.1022 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-72-2-VP-1-c9b7d22f637b_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-72-2-VP-2-140522beb382 | VP-2 | 1 | — | 0.1249 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-72-2-VP-2-140522beb382_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-72-2-VP-3-fa6642910351 | VP-3 | 1 | — | 0.12 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-72-2-VP-3-fa6642910351_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-72-2-VP-4-b8133c2779c4 | VP-4 | 1 | — | 0.1238 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-72-2-VP-4-b8133c2779c4_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-72-3-VP-0-e2f0ea7d308e | VP-0 | 1 | — | 0.1851 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-72-3-VP-0-e2f0ea7d308e_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-72-3-VP-2-98eefc9b4522 | VP-2 | 1 | — | 0.1189 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-72-3-VP-2-98eefc9b4522_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-72-3-VP-3-4df50f4a6a53 | VP-3 | 1 | — | 0.1165 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-72-3-VP-3-4df50f4a6a53_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-72-3-VP-4-15652c88e1d4 | VP-4 | 1 | — | 0.1201 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-72-3-VP-4-15652c88e1d4_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-72-4-VP-0-2b3a6aab2111 | VP-0 | 1 | — | 0.1784 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-72-4-VP-0-2b3a6aab2111_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-72-4-VP-2-3233142c2660 | VP-2 | 1 | — | 0.1155 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-72-4-VP-2-3233142c2660_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-72-4-VP-3-c98a77093440 | VP-3 | 1 | — | 0.1129 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-72-4-VP-3-c98a77093440_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-72-4-VP-4-d2f545b90ae3 | VP-4 | 1 | — | 0.1137 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-72-4-VP-4-d2f545b90ae3_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-72-5-VP-0-5777015be1c0 | VP-0 | 1 | — | 0.1731 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-72-5-VP-0-5777015be1c0_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-72-5-VP-2-ebd0c49983ed | VP-2 | 1 | — | 0.1121 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-72-5-VP-2-ebd0c49983ed_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-72-5-VP-3-01faf14c6ab7 | VP-3 | 1 | — | 0.1068 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-72-5-VP-3-01faf14c6ab7_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-72-5-VP-4-5dd9c63ccbb3 | VP-4 | 1 | — | 0.11 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-72-5-VP-4-5dd9c63ccbb3_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-72-6-VP-0-0579c18d5198 | VP-0 | 1 | — | 0.2051 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-72-6-VP-0-0579c18d5198_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-72-6-VP-1-8d20aade2a23 | VP-1 | 1 | — | 0.1091 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-72-6-VP-1-8d20aade2a23_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-72-6-VP-2-edc01f63325f | VP-2 | 1 | — | 0.1575 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-72-6-VP-2-edc01f63325f_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-72-6-VP-3-ed95053b7bad | VP-3 | 1 | — | 0.137 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-72-6-VP-3-ed95053b7bad_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-72-6-VP-4-f47122da8706 | VP-4 | 1 | — | 0.1412 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-72-6-VP-4-f47122da8706_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-72-6-VP-5-7ef6dcd6c783 | VP-5 | 1 | — | 0.1053 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-72-6-VP-5-7ef6dcd6c783_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-80-2-VP-0-9804f1f6a189 | VP-0 | 1 | — | 0.19 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-80-2-VP-0-9804f1f6a189_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-80-2-VP-1-194afdc02ca8 | VP-1 | 1 | — | 0.1022 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-80-2-VP-1-194afdc02ca8_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-80-2-VP-2-19c8af83a747 | VP-2 | 1 | — | 0.1249 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-80-2-VP-2-19c8af83a747_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-80-2-VP-3-ade21f5bc222 | VP-3 | 1 | — | 0.12 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-80-2-VP-3-ade21f5bc222_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-80-2-VP-4-33ecdd0e2ba0 | VP-4 | 1 | — | 0.1238 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-80-2-VP-4-33ecdd0e2ba0_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-80-3-VP-0-582335ee824c | VP-0 | 1 | — | 0.1851 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-80-3-VP-0-582335ee824c_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-80-3-VP-2-2f9ab1e88e1a | VP-2 | 1 | — | 0.1189 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-80-3-VP-2-2f9ab1e88e1a_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-80-3-VP-3-c3fe04b7aa3a | VP-3 | 1 | — | 0.1165 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-80-3-VP-3-c3fe04b7aa3a_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-80-3-VP-4-b1693a5900aa | VP-4 | 1 | — | 0.1201 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-80-3-VP-4-b1693a5900aa_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-80-4-VP-0-55dbe76785a0 | VP-0 | 1 | — | 0.1784 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-80-4-VP-0-55dbe76785a0_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-80-4-VP-2-525d0778d376 | VP-2 | 1 | — | 0.1155 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-80-4-VP-2-525d0778d376_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-80-4-VP-3-a0582d954ec6 | VP-3 | 1 | — | 0.1129 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-80-4-VP-3-a0582d954ec6_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-80-4-VP-4-1f35fe82ad8a | VP-4 | 1 | — | 0.1137 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-80-4-VP-4-1f35fe82ad8a_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-80-5-VP-0-e2d4ae4af09d | VP-0 | 1 | — | 0.1731 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-80-5-VP-0-e2d4ae4af09d_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-80-5-VP-2-c37f27537ba5 | VP-2 | 1 | — | 0.1121 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-80-5-VP-2-c37f27537ba5_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-80-5-VP-3-4307b3c8a0a7 | VP-3 | 1 | — | 0.1068 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-80-5-VP-3-4307b3c8a0a7_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-80-5-VP-4-3a10c5f77fac | VP-4 | 1 | — | 0.11 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-80-5-VP-4-3a10c5f77fac_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-80-6-VP-0-b156e26a02fd | VP-0 | 1 | — | 0.2051 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-80-6-VP-0-b156e26a02fd_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-80-6-VP-1-416330cc6421 | VP-1 | 1 | — | 0.1091 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-80-6-VP-1-416330cc6421_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-80-6-VP-2-6b1222966f2b | VP-2 | 1 | — | 0.1575 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-80-6-VP-2-6b1222966f2b_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-80-6-VP-3-a76d87b3a74a | VP-3 | 1 | — | 0.137 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-80-6-VP-3-a76d87b3a74a_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-80-6-VP-4-0cbde2b617d6 | VP-4 | 1 | — | 0.1412 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-80-6-VP-4-0cbde2b617d6_seed1.mcap |
| PP-SWR-094 | SG-01 | S8-ncap-overtaking-left-80-6-VP-5-86f156f800c1 | VP-5 | 1 | — | 0.1053 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8-ncap-overtaking-left-80-6-VP-5-86f156f800c1_seed1.mcap |
| PP-SWR-094 | SG-01 | S8b-c-VP-0-b7f431c8a478 | VP-0 | 1 | — | 0.2758 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8b-c-VP-0-b7f431c8a478_seed1.mcap |
| PP-SWR-094 | SG-01 | S8b-c-VP-1-bb7979e8243e | VP-1 | 1 | — | 0.1982 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8b-c-VP-1-bb7979e8243e_seed1.mcap |
| PP-SWR-094 | SG-01 | S8b-c-VP-2-0dfc5ffed8c6 | VP-2 | 1 | — | 0.2385 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8b-c-VP-2-0dfc5ffed8c6_seed1.mcap |
| PP-SWR-094 | SG-01 | S8b-c-VP-3-a1393c0de570 | VP-3 | 1 | — | 0.2419 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8b-c-VP-3-a1393c0de570_seed1.mcap |
| PP-SWR-094 | SG-01 | S8b-c-VP-4-7888642b1a30 | VP-4 | 1 | — | 0.2494 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8b-c-VP-4-7888642b1a30_seed1.mcap |
| PP-SWR-094 | SG-01 | S8b-c-VP-5-95f29b93c5d0 | VP-5 | 1 | — | 0.2153 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8b-c-VP-5-95f29b93c5d0_seed1.mcap |
| PP-SWR-094 | SG-01 | S8b-d-VP-0-3a44760c04f9 | VP-0 | 1 | — | 0.1004 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8b-d-VP-0-3a44760c04f9_seed1.mcap |
| PP-SWR-094 | SG-01 | S8b-e-VP-0-da0466a24640 | VP-0 | 1 | — | 0.1004 | <= 0.1 | DLC thật giảm lại lớn nhất sau điểm nhỏ nhất của lần can thiệp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S8b-e-VP-0-da0466a24640_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-c-S1c-VP-0-bca0f1afb997 | VP-0 | 1 | 15.16 | 1.142 | <= 1 | Lệch ngang giữa hai path liên tiếp / ngưỡng của khoảng | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F08-c-S1c-VP-0-bca0f1afb997_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-c-S1c-VP-1-3d8334644eea | VP-1 | 1 | 7.383 | 1.14 | <= 1 | Lệch ngang giữa hai path liên tiếp / ngưỡng của khoảng | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F08-c-S1c-VP-1-3d8334644eea_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-c-S1c-VP-5-06d7bb8fda8b | VP-5 | 1 | 15.21 | 1.142 | <= 1 | Lệch ngang giữa hai path liên tiếp / ngưỡng của khoảng | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F08-c-S1c-VP-5-06d7bb8fda8b_seed1.mcap |
| PP-SWR-172 | SG-01 | F25-a-S22a-VP-0-10572311642a | VP-0 | 1 | — | 2 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-a-S22a-VP-0-10572311642a_seed1.mcap |
| PP-SWR-172 | SG-01 | F25-a-S22a-VP-0-553a310fc4d7 | VP-0 | 1 | — | 2 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-a-S22a-VP-0-553a310fc4d7_seed1.mcap |
| PP-SWR-172 | SG-01 | F25-a-S22a-VP-0-85b221025492 | VP-0 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-a-S22a-VP-0-85b221025492_seed1.mcap |
| PP-SWR-172 | SG-01 | F25-a-S22a-VP-0-f8453b9ef2ea | VP-0 | 1 | — | 2 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-a-S22a-VP-0-f8453b9ef2ea_seed1.mcap |
| PP-SWR-172 | SG-01 | F25-a-S22a-VP-0-fd0265a3660e | VP-0 | 1 | — | 2 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-a-S22a-VP-0-fd0265a3660e_seed1.mcap |
| PP-SWR-172 | SG-01 | F25-a-S22a-VP-1-5c02da94beb1 | VP-1 | 1 | — | 2 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-a-S22a-VP-1-5c02da94beb1_seed1.mcap |
| PP-SWR-172 | SG-01 | F25-a-S22a-VP-5-cc4fc13c3887 | VP-5 | 1 | — | 2 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-a-S22a-VP-5-cc4fc13c3887_seed1.mcap |
| PP-SWR-172 | SG-01 | F25-b-S22a-VP-0-33e0e262751f | VP-0 | 1 | — | 2 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-b-S22a-VP-0-33e0e262751f_seed1.mcap |
| PP-SWR-172 | SG-01 | F25-b-S22a-VP-1-077cb6030976 | VP-1 | 1 | — | 2 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-b-S22a-VP-1-077cb6030976_seed1.mcap |
| PP-SWR-172 | SG-01 | F25-b-S22a-VP-5-0aa316c22313 | VP-5 | 1 | — | 2 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-b-S22a-VP-5-0aa316c22313_seed1.mcap |
| PP-SWR-172 | SG-01 | F25-c-S22a-VP-0-191326001926 | VP-0 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-c-S22a-VP-0-191326001926_seed1.mcap |
| PP-SWR-172 | SG-01 | F25-c-S22a-VP-1-42edbe799a5c | VP-1 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-c-S22a-VP-1-42edbe799a5c_seed1.mcap |
| PP-SWR-172 | SG-01 | F25-c-S22a-VP-5-dc4b57212bae | VP-5 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-c-S22a-VP-5-dc4b57212bae_seed1.mcap |
| PP-SWR-172 | SG-01 | F25-e-S22a-VP-0-2219ed6d348d | VP-0 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-e-S22a-VP-0-2219ed6d348d_seed1.mcap |
| PP-SWR-172 | SG-01 | F25-e-S22a-VP-1-39ef91d1dee2 | VP-1 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-e-S22a-VP-1-39ef91d1dee2_seed1.mcap |
| PP-SWR-172 | SG-01 | F25-e-S22a-VP-5-fb5ac378351a | VP-5 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-e-S22a-VP-5-fb5ac378351a_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-a-VP-0-3020d44fb647 | VP-0 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-a-VP-0-3020d44fb647_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-a-VP-0-83d5ce75cdd2 | VP-0 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-a-VP-0-83d5ce75cdd2_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-a-VP-0-dbbbdfba0b2e | VP-0 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-a-VP-0-dbbbdfba0b2e_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-a-VP-0-fd13d6f6df80 | VP-0 | 1 | — | 2 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-a-VP-0-fd13d6f6df80_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-a-VP-1-12762485cead | VP-1 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-a-VP-1-12762485cead_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-a-VP-2-6f93e1479bbf | VP-2 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-a-VP-2-6f93e1479bbf_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-a-VP-3-c8e1b7502c38 | VP-3 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-a-VP-3-c8e1b7502c38_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-a-VP-4-f629e928ca25 | VP-4 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-a-VP-4-f629e928ca25_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-a-VP-5-5dd741687210 | VP-5 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-a-VP-5-5dd741687210_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-b-VP-0-8164b3daec3e | VP-0 | 1 | — | 2 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-b-VP-0-8164b3daec3e_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-b-VP-1-582804600d03 | VP-1 | 1 | — | 2 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-b-VP-1-582804600d03_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-b-VP-2-8d3c37c7f1c4 | VP-2 | 1 | — | 2 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-b-VP-2-8d3c37c7f1c4_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-b-VP-3-f36ffd799338 | VP-3 | 1 | — | 2 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-b-VP-3-f36ffd799338_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-b-VP-4-7f58abaa6cee | VP-4 | 1 | — | 2 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-b-VP-4-7f58abaa6cee_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-b-VP-5-a7e1dee3be4c | VP-5 | 1 | — | 2 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-b-VP-5-a7e1dee3be4c_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-c-VP-0-382929248db9 | VP-0 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-c-VP-0-382929248db9_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-c-VP-1-04256076f0c7 | VP-1 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-c-VP-1-04256076f0c7_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-c-VP-2-57c34b4fa4a4 | VP-2 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-c-VP-2-57c34b4fa4a4_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-c-VP-3-5d695785b173 | VP-3 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-c-VP-3-5d695785b173_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-c-VP-4-95758244e673 | VP-4 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-c-VP-4-95758244e673_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-c-VP-5-83d02f704be2 | VP-5 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-c-VP-5-83d02f704be2_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-d-VP-0-6d535f20c1aa | VP-0 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-d-VP-0-6d535f20c1aa_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-d-VP-1-5a09734c952b | VP-1 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-d-VP-1-5a09734c952b_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-d-VP-2-aef2a18c2438 | VP-2 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-d-VP-2-aef2a18c2438_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-d-VP-3-fa4a7e125741 | VP-3 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-d-VP-3-fa4a7e125741_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-d-VP-4-19758dc19c63 | VP-4 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-d-VP-4-19758dc19c63_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-d-VP-5-aff2305b7379 | VP-5 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-d-VP-5-aff2305b7379_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-e-VP-0-6a0b15bf41ce | VP-0 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-e-VP-0-6a0b15bf41ce_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-e-VP-1-cb77b9982ed7 | VP-1 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-e-VP-1-cb77b9982ed7_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-e-VP-2-7e815a10acd8 | VP-2 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-e-VP-2-7e815a10acd8_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-e-VP-3-315220d56377 | VP-3 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-e-VP-3-315220d56377_seed1.mcap |
| PP-SWR-172 | SG-01 | S22-e-VP-4-e573fdd87cfc | VP-4 | 1 | — | 1 | = 0 | Chu kỳ còn FOLLOW khi một điều kiện duy trì không thoả | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S22-e-VP-4-e573fdd87cfc_seed1.mcap |
| PP-SWR-176 | SG-01 | F25-a-S22a-VP-0-10572311642a | VP-0 | 1 | — | 2 | = 0 | Chu kỳ vào hoặc còn FOLLOW khi LeadTarget không hợp lệ | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-a-S22a-VP-0-10572311642a_seed1.mcap |
| PP-SWR-176 | SG-01 | F25-a-S22a-VP-0-553a310fc4d7 | VP-0 | 1 | — | 2 | = 0 | Chu kỳ vào hoặc còn FOLLOW khi LeadTarget không hợp lệ | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-a-S22a-VP-0-553a310fc4d7_seed1.mcap |
| PP-SWR-176 | SG-01 | F25-a-S22a-VP-0-85b221025492 | VP-0 | 1 | — | 1 | = 0 | Chu kỳ vào hoặc còn FOLLOW khi LeadTarget không hợp lệ | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-a-S22a-VP-0-85b221025492_seed1.mcap |
| PP-SWR-176 | SG-01 | F25-a-S22a-VP-0-f8453b9ef2ea | VP-0 | 1 | — | 2 | = 0 | Chu kỳ vào hoặc còn FOLLOW khi LeadTarget không hợp lệ | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-a-S22a-VP-0-f8453b9ef2ea_seed1.mcap |
| PP-SWR-176 | SG-01 | F25-a-S22a-VP-0-fd0265a3660e | VP-0 | 1 | — | 2 | = 0 | Chu kỳ vào hoặc còn FOLLOW khi LeadTarget không hợp lệ | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-a-S22a-VP-0-fd0265a3660e_seed1.mcap |
| PP-SWR-176 | SG-01 | F25-a-S22a-VP-1-5c02da94beb1 | VP-1 | 1 | — | 2 | = 0 | Chu kỳ vào hoặc còn FOLLOW khi LeadTarget không hợp lệ | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-a-S22a-VP-1-5c02da94beb1_seed1.mcap |
| PP-SWR-176 | SG-01 | F25-a-S22a-VP-5-cc4fc13c3887 | VP-5 | 1 | — | 2 | = 0 | Chu kỳ vào hoặc còn FOLLOW khi LeadTarget không hợp lệ | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-a-S22a-VP-5-cc4fc13c3887_seed1.mcap |
| PP-SWR-176 | SG-01 | F25-b-S22a-VP-0-33e0e262751f | VP-0 | 1 | — | 2 | = 0 | Chu kỳ vào hoặc còn FOLLOW khi LeadTarget không hợp lệ | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-b-S22a-VP-0-33e0e262751f_seed1.mcap |
| PP-SWR-176 | SG-01 | F25-b-S22a-VP-1-077cb6030976 | VP-1 | 1 | — | 2 | = 0 | Chu kỳ vào hoặc còn FOLLOW khi LeadTarget không hợp lệ | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-b-S22a-VP-1-077cb6030976_seed1.mcap |
| PP-SWR-176 | SG-01 | F25-b-S22a-VP-5-0aa316c22313 | VP-5 | 1 | — | 2 | = 0 | Chu kỳ vào hoặc còn FOLLOW khi LeadTarget không hợp lệ | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-b-S22a-VP-5-0aa316c22313_seed1.mcap |
| PP-SWR-176 | SG-01 | F25-c-S22a-VP-0-191326001926 | VP-0 | 1 | — | 1 | = 0 | Chu kỳ vào hoặc còn FOLLOW khi LeadTarget không hợp lệ | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-c-S22a-VP-0-191326001926_seed1.mcap |
| PP-SWR-176 | SG-01 | F25-c-S22a-VP-1-42edbe799a5c | VP-1 | 1 | — | 1 | = 0 | Chu kỳ vào hoặc còn FOLLOW khi LeadTarget không hợp lệ | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-c-S22a-VP-1-42edbe799a5c_seed1.mcap |
| PP-SWR-176 | SG-01 | F25-c-S22a-VP-5-dc4b57212bae | VP-5 | 1 | — | 1 | = 0 | Chu kỳ vào hoặc còn FOLLOW khi LeadTarget không hợp lệ | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-c-S22a-VP-5-dc4b57212bae_seed1.mcap |
| PP-SWR-176 | SG-01 | F25-e-S22a-VP-0-2219ed6d348d | VP-0 | 1 | — | 1 | = 0 | Chu kỳ vào hoặc còn FOLLOW khi LeadTarget không hợp lệ | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-e-S22a-VP-0-2219ed6d348d_seed1.mcap |
| PP-SWR-176 | SG-01 | F25-e-S22a-VP-1-39ef91d1dee2 | VP-1 | 1 | — | 1 | = 0 | Chu kỳ vào hoặc còn FOLLOW khi LeadTarget không hợp lệ | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-e-S22a-VP-1-39ef91d1dee2_seed1.mcap |
| PP-SWR-176 | SG-01 | F25-e-S22a-VP-5-fb5ac378351a | VP-5 | 1 | — | 1 | = 0 | Chu kỳ vào hoặc còn FOLLOW khi LeadTarget không hợp lệ | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-e-S22a-VP-5-fb5ac378351a_seed1.mcap |

## Trượt MINOR

| Requirement | Safety goal | Ca | Profile | Seed | Trượt đầu tiên [s] | Giá trị | Ngưỡng | Chi tiết | MCAP |
|---|---|---|---|---|---|---|---|---|---|
| PP-SWR-032 | — | F01-c-S4a_at_lka_activep0-VP-4-914355537c7d | VP-4 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F01-c-S4a_at_lka_activep0-VP-4-914355537c7d_seed1.mcap |
| PP-SWR-032 | — | F01-c-S4a_at_lka_activep0-VP-4-914355537c7d | VP-4 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F01-c-S4a_at_lka_activep0-VP-4-914355537c7d_seed2.mcap |
| PP-SWR-032 | — | F01-c-S4a_at_lka_activep0.2-VP-5-2e109dc103db | VP-5 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F01-c-S4a_at_lka_activep0.2-VP-5-2e109dc103db_seed2.mcap |
| PP-SWR-032 | — | F01-c-S5a_at_elk_activep0-VP-4-d7e0b59fbf4d | VP-4 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F01-c-S5a_at_elk_activep0-VP-4-d7e0b59fbf4d_seed1.mcap |
| PP-SWR-032 | — | F01-c-S5a_at_elk_activep0-VP-4-d7e0b59fbf4d | VP-4 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F01-c-S5a_at_elk_activep0-VP-4-d7e0b59fbf4d_seed2.mcap |
| PP-SWR-032 | — | F01-c-S5a_at_elk_activep0.2-VP-5-fbea90d7d4d0 | VP-5 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F01-c-S5a_at_elk_activep0.2-VP-5-fbea90d7d4d0_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-0-944a5944b2f0 | VP-0 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/G01-S4c-VP-0-944a5944b2f0_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-1-d9c02f4d85c9 | VP-1 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/G01-S4c-VP-1-d9c02f4d85c9_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-2-19b08e51426b | VP-2 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/G01-S4c-VP-2-19b08e51426b_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-3-9991783c316d | VP-3 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/G01-S4c-VP-3-9991783c316d_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-4-072664ac9b98 | VP-4 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/G01-S4c-VP-4-072664ac9b98_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-5-26df2868e70c | VP-5 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/G01-S4c-VP-5-26df2868e70c_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-0-69e53aeef11a | VP-0 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S12-b-VP-0-69e53aeef11a_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-1-4b3e70a50a26 | VP-1 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S12-b-VP-1-4b3e70a50a26_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-2-0962daddf5bd | VP-2 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S12-b-VP-2-0962daddf5bd_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-3-984dbaa7f733 | VP-3 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S12-b-VP-3-984dbaa7f733_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-4-a4945d3bcd67 | VP-4 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S12-b-VP-4-a4945d3bcd67_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-5-2b777db332c0 | VP-5 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S12-b-VP-5-2b777db332c0_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-5-2b777db332c0 | VP-5 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S12-b-VP-5-2b777db332c0_seed2.mcap |
| PP-SWR-032 | — | S20-a-VP-2-1a3aca6c43ec | VP-2 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S20-a-VP-2-1a3aca6c43ec_seed1.mcap |
| PP-SWR-062 | — | S19-f-VP-5-9c4f0f44d054 | VP-5 | 1 | — | 1 | = 0 | Requirement trượt ở biên ODD | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S19-f-VP-5-9c4f0f44d054_seed1.mcap |
| PP-SWR-084 | — | F02-e-S4a_at_lka_activep0-VP-2-c5082f1b14ba | VP-2 | 1 | — | 0.6282 | <= 0.2 | Lệch tâm khi LKA hoặc ELK COMPLETED [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F02-e-S4a_at_lka_activep0-VP-2-c5082f1b14ba_seed1.mcap |
| PP-SWR-084 | — | F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0 | VP-3 | 1 | — | -0.03123 | >= 0 | DLC nhỏ nhất ở hai phía khi LKA hoặc ELK COMPLETED [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0_seed1.mcap |
| PP-SWR-084 | — | F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0 | VP-3 | 1 | — | 0.617 | <= 0.2 | Lệch tâm khi LKA hoặc ELK COMPLETED [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0_seed1.mcap |
| PP-SWR-084 | — | F02-e-S5a_at_elk_activep0-VP-2-29b21e6b793a | VP-2 | 1 | — | 0.6125 | <= 0.2 | Lệch tâm khi LKA hoặc ELK COMPLETED [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F02-e-S5a_at_elk_activep0-VP-2-29b21e6b793a_seed1.mcap |
| PP-SWR-084 | — | F02-e-S5a_at_elk_activep0.2-VP-3-bb766866f0d0 | VP-3 | 1 | — | -0.02195 | >= 0 | DLC nhỏ nhất ở hai phía khi LKA hoặc ELK COMPLETED [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F02-e-S5a_at_elk_activep0.2-VP-3-bb766866f0d0_seed1.mcap |
| PP-SWR-084 | — | F02-e-S5a_at_elk_activep0.2-VP-3-bb766866f0d0 | VP-3 | 1 | — | 0.6082 | <= 0.2 | Lệch tâm khi LKA hoặc ELK COMPLETED [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F02-e-S5a_at_elk_activep0.2-VP-3-bb766866f0d0_seed1.mcap |
| PP-SWR-090 | — | F01-c-S5a_at_elk_activep0-VP-4-d7e0b59fbf4d | VP-4 | 2 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F01-c-S5a_at_elk_activep0-VP-4-d7e0b59fbf4d_seed2.mcap |
| PP-SWR-090 | — | F02-e-S4a_at_lka_activep0-VP-2-c5082f1b14ba | VP-2 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F02-e-S4a_at_lka_activep0-VP-2-c5082f1b14ba_seed1.mcap |
| PP-SWR-090 | — | F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0 | VP-3 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0_seed1.mcap |
| PP-SWR-090 | — | F02-e-S5a_at_elk_activep0-VP-2-29b21e6b793a | VP-2 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F02-e-S5a_at_elk_activep0-VP-2-29b21e6b793a_seed1.mcap |
| PP-SWR-090 | — | F02-e-S5a_at_elk_activep0.2-VP-3-bb766866f0d0 | VP-3 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F02-e-S5a_at_elk_activep0.2-VP-3-bb766866f0d0_seed1.mcap |
| PP-SWR-090 | — | G01-S4c-VP-0-944a5944b2f0 | VP-0 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/G01-S4c-VP-0-944a5944b2f0_seed1.mcap |
| PP-SWR-090 | — | G01-S4c-VP-3-9991783c316d | VP-3 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/G01-S4c-VP-3-9991783c316d_seed1.mcap |
| PP-SWR-090 | — | G01-S4c-VP-4-072664ac9b98 | VP-4 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/G01-S4c-VP-4-072664ac9b98_seed1.mcap |
| PP-SWR-090 | — | S12-b-VP-2-0962daddf5bd | VP-2 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/S12-b-VP-2-0962daddf5bd_seed1.mcap |
| PP-SWR-170 | — | F25-c-S22a-VP-0-191326001926 | VP-0 | 1 | — | 1 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-c-S22a-VP-0-191326001926_seed1.mcap |
| PP-SWR-170 | — | F25-c-S22a-VP-1-42edbe799a5c | VP-1 | 1 | — | 1 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-c-S22a-VP-1-42edbe799a5c_seed1.mcap |
| PP-SWR-170 | — | F25-c-S22a-VP-5-dc4b57212bae | VP-5 | 1 | — | 1 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-c-S22a-VP-5-dc4b57212bae_seed1.mcap |
| PP-SWR-170 | — | F25-d-S22a-VP-0-deb4c617404b | VP-0 | 1 | — | 3 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-d-S22a-VP-0-deb4c617404b_seed1.mcap |
| PP-SWR-170 | — | F25-d-S22a-VP-1-294c7b39bdf1 | VP-1 | 1 | — | 3 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-d-S22a-VP-1-294c7b39bdf1_seed1.mcap |
| PP-SWR-170 | — | F25-d-S22a-VP-5-425685eb4bcc | VP-5 | 1 | — | 3 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-d-S22a-VP-5-425685eb4bcc_seed1.mcap |
| PP-SWR-170 | — | F25-e-S22a-VP-5-fb5ac378351a | VP-5 | 1 | — | 1 | = 0 | Chu kỳ đủ điều kiện vào bám xe mà không ở FOLLOW | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261123-1253-regression-54307f1/suite/mcap/F25-e-S22a-VP-5-fb5ac378351a_seed1.mcap |

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
| MINOR | PP-SWR-062 | S7-a-VP-5-b8c0c48677a9 | 1 | 1 | = 0 |
| MINOR | PP-SWR-032 | S7-e-VP-5-c6c6c78dc976 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S7-e-VP-5-c6c6c78dc976 | 1 | 1 | = 0 |
| MINOR | PP-SWR-062 | S7-ncap-oncoming-left-2-VP-5-439b6019b6b6 | 1 | 1 | = 0 |
| MINOR | PP-SWR-062 | S7-ncap-oncoming-left-6-VP-5-cab30fbcc9c6 | 1 | 1 | = 0 |
| MINOR | PP-SWR-032 | S8-ncap-overtaking-left-72-5-VP-5-be49baca0b00 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S8-ncap-overtaking-left-72-5-VP-5-be49baca0b00 | 1 | 1 | = 0 |
| MINOR | PP-SWR-062 | S8-ncap-overtaking-left-72-6-VP-5-7ef6dcd6c783 | 1 | 1 | = 0 |
| MINOR | PP-SWR-062 | S8-ncap-overtaking-left-80-6-VP-5-86f156f800c1 | 1 | 1 | = 0 |
| MINOR | PP-SWR-055 | S3b-d-VP-5-befbcf67d7a8 | 1 | 0 | > 0 |
| MINOR | PP-SWR-058 | S3b-d-VP-5-befbcf67d7a8 | 1 | 0 | > 0 |
| MINOR | PP-SWR-062 | S3b-d-VP-5-befbcf67d7a8 | 1 | 2 | = 0 |
| MINOR | PP-SWR-062 | S8b-c-VP-5-95f29b93c5d0 | 1 | 1 | = 0 |
| MINOR | PP-SWR-090 | S12-c-VP-0-425b042b9630 | 2 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S12-c-VP-2-dcd8acfe5043 | 2 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S12-c-VP-3-4b7830a9f53c | 2 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S12-c-VP-4-406ed8c312c5 | 2 | 1 | <= 0 |
| BLOCKER | PP-SWR-086 | S16-c-VP-5-8588c1885ba1 | 1 | -0.4879 | >= -0.3 |
| MINOR | PP-SWR-062 | S16-c-VP-5-8588c1885ba1 | 1 | 1 | = 0 |
| MINOR | PP-SWR-032 | S21-c-VP-5-cb4f72656e1d | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S21-c-VP-5-cb4f72656e1d | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-176 | S22-a-VP-0-3020d44fb647 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-176 | S22-a-VP-1-12762485cead | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-176 | S22-a-VP-2-6f93e1479bbf | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-176 | S22-a-VP-3-c8e1b7502c38 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-176 | S22-a-VP-4-f629e928ca25 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-176 | S22-a-VP-5-5dd741687210 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-176 | S22-b-VP-0-8164b3daec3e | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-176 | S22-b-VP-1-582804600d03 | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-176 | S22-b-VP-2-8d3c37c7f1c4 | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-176 | S22-b-VP-3-f36ffd799338 | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-176 | S22-b-VP-4-7f58abaa6cee | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-176 | S22-b-VP-5-a7e1dee3be4c | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-176 | S22-c-VP-0-382929248db9 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-176 | S22-c-VP-1-04256076f0c7 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-176 | S22-c-VP-2-57c34b4fa4a4 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-176 | S22-c-VP-3-5d695785b173 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-176 | S22-c-VP-4-95758244e673 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-176 | S22-c-VP-5-83d02f704be2 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-176 | S22-d-VP-0-6d535f20c1aa | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-176 | S22-d-VP-1-5a09734c952b | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-176 | S22-d-VP-2-aef2a18c2438 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-176 | S22-d-VP-3-fa4a7e125741 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-176 | S22-d-VP-4-19758dc19c63 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-176 | S22-d-VP-5-aff2305b7379 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-171 | S22-e-VP-0-6a0b15bf41ce | 1 | 6 | = 0 |
| BLOCKER | PP-SWR-176 | S22-e-VP-0-6a0b15bf41ce | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-171 | S22-e-VP-1-cb77b9982ed7 | 1 | 7 | = 0 |
| BLOCKER | PP-SWR-176 | S22-e-VP-1-cb77b9982ed7 | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-171 | S22-e-VP-2-7e815a10acd8 | 1 | 6 | = 0 |
| BLOCKER | PP-SWR-176 | S22-e-VP-2-7e815a10acd8 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-171 | S22-e-VP-3-315220d56377 | 1 | 6 | = 0 |
| BLOCKER | PP-SWR-176 | S22-e-VP-3-315220d56377 | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-171 | S22-e-VP-4-e573fdd87cfc | 1 | 7 | = 0 |
| BLOCKER | PP-SWR-176 | S22-e-VP-4-e573fdd87cfc | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-171 | S22-e-VP-5-876e2407c39d | 1 | 11 | = 0 |
| BLOCKER | PP-SWR-176 | S22-e-VP-5-876e2407c39d | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-176 | S22-a-VP-0-fd13d6f6df80 | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-176 | S22-a-VP-0-dbbbdfba0b2e | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-176 | S22-a-VP-0-83d5ce75cdd2 | 1 | 1 | = 0 |
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
| B1 | Nominal | 1004 | Không đạt | 129 | 0 | 1 |
| B2 | Regulatory | 594 | Không đạt | 113 | 0 | 0 |
| B3 | Performance limit | 311 | Không đạt | 7 | 0 | 1 |
| B4 | Robustness | 995 | Không đạt | 87 | 0 | 41 |
| B5 | Degradation and refusal | 400 | Không đạt | 65 | 0 | 8 |
| B6 | Comfort | 1004 | Không đạt | 129 | 0 | 1 |
| B7 | Flexibility | 804 | Không đạt | 42 | 0 | 18 |
| B8 | Compute | 2310 | Không đạt | 223 | 0 | 43 |

## Số lần chạy

```json
{
 "planned": 2310,
 "executed": 2310,
 "failed": 235,
 "failed_out_of_scope": 162,
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
| VP-0 | 210 | 97.0% | PP-SWR-094 | **0.441** | 0.287 | 1.58 | 0.0773 | 0.521 | 3.09 | 0.588 | 1.65 | **5.52** | **5.05** | **0.0189** |
| VP-1 | 145 | 97.1% | PP-SWR-094 | 0.441 | 0.282 | **1.58** | **0.0797** | 0.514 | **3.2** | 0.558 | 1.5 | 5.5 | 5.02 | 0.036 |
| VP-2 | 103 | 91.4% | PP-SWR-084, PP-SWR-090, PP-SWR-094 | 0.441 | 0.287 | 1.58 | 0.0777 | 0.519 | 3.11 | 0.483 | 1.7 | 5.42 | 4.95 | 0.0347 |
| VP-3 | 102 | 91.2% | PP-SWR-084, PP-SWR-090, PP-SWR-094 | 0.441 | 0.288 | 1.57 | 0.0772 | 0.521 | 3.09 | 0.433 | 1.67 | 5.35 | 4.9 | 0.019 |
| VP-4 | 102 | 91.2% | PP-SWR-032, PP-SWR-090, PP-SWR-094 | 0.441 | **0.288** | 1.57 | 0.0768 | **0.523** | 3.07 | 0.41 | **1.72** | 5.3 | 4.88 | 0.0194 |
| VP-5 | 142 | 86.1% | PP-SWR-032, PP-SWR-051, PP-SWR-062, PP-SWR-063, PP-SWR-094 | 0.0919 | 0.288 | 1.57 | 0.0492 | 0.404 | 1.95 | **0.287** | 1.72 | 4.65 | 4.42 | 0.0194 |

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
| PP-SWR-082 Thời lượng path ELK tới COMPLETED | 1.38 | 0.15 | VP-0 |
| PP-SWR-087 DTLE LKA nhỏ nhất | 0.18 | 0.00353 | VP-0 |

Requirement đạt 100 % trên mọi profile: không (VP-0, VP-1, VP-2, VP-3, VP-4, VP-5)

## Thời gian tính

1825970 chu kỳ. p95 ≤ 1.58 ms, p99 ≤ 2.51 ms (cận trên của bin), lớn nhất 408 ms. Đo trên máy chạy SIL, gồm adapter; không khẳng định thời gian trên ECU (mục 9.1).

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
| S7 | 0.2 | -0.178 |
| S7 | 0.3 | 0.119 |
| S7 | 0.4 | 0.159 |
| S7 | 0.5 | 0.199 |
| S7 | 0.6 | 0.133 |
| S8 | 0.2 | 0.0794 |
| S8 | 0.3 | 0.119 |
| S8 | 0.4 | 0.0344 |
| S8 | 0.5 | 0.0358 |
| S8 | 0.6 | 0.03 |
| S8 | 0.7 | 0.196 |
| S8b | 0.5 | -0.353 |
| S8c | 0.4 | 0.241 |

![DTLE theo v_lat](figures/dtle_v_lat.png)

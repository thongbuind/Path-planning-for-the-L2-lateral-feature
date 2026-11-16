# Kết luận: Không đạt

- Planner: pp_planner 0.2.0 commit 71fb7c130553 calibration d532993b1b2f t7 quintic (498e6f0cee04)
- Tích hợp được: có
- Đã chạy: 2079 lần chạy; trượt BLOCKER 121, MAJOR 0, MINOR 45
- Kết luận chỉ đúng trong phạm vi đã thử, không phải bằng chứng an toàn (Software Qualification Test Specification 3).

## Trượt BLOCKER

| Requirement | Safety goal | Ca | Profile | Seed | Trượt đầu tiên [s] | Giá trị | Ngưỡng | Chi tiết | MCAP |
|---|---|---|---|---|---|---|---|---|---|
| PP-SWR-005 | SG-02 | S1b-a-VP-0-693b15015bfa | VP-0 | 1 | 8.008 | 1 | = 0 | Chu kỳ cua gắt mà mất path hoặc HWA | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S1b-a-VP-0-693b15015bfa_seed1.mcap |
| PP-SWR-006 | SG-02 | S1b-a-VP-0-693b15015bfa | VP-0 | 1 | 3.958 | -0.1269 | >= 0 | a_y path trừ (aysmax − epsilon_ay), 0–1 s, khi a_y cần > aysmax [m/s²] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S1b-a-VP-0-693b15015bfa_seed1.mcap |
| PP-SWR-007 | SG-01 | S1b-a-VP-0-693b15015bfa | VP-0 | 1 | 8.691 | 1 | = 0 | Lần lốp đè vạch khi cua gắt mà cờ chưa bật | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S1b-a-VP-0-693b15015bfa_seed1.mcap |
| PP-SWR-030 | SG-01 | S14-a-VP-0-3290c39907ee | VP-0 | 1 | 8.008 | 25 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-a-VP-0-3290c39907ee_seed1.mcap |
| PP-SWR-030 | SG-01 | S16-d-VP-0-e29852ad5a1c | VP-0 | 1 | — | — | — | ELK: có REQUEST nhưng thiếu path can thiệp hợp lệ | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S16-d-VP-0-e29852ad5a1c_seed1.mcap |
| PP-SWR-030 | SG-01 | S16-d-VP-3-c4c71c213cb3 | VP-3 | 1 | — | — | — | ELK: có REQUEST nhưng thiếu path can thiệp hợp lệ | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S16-d-VP-3-c4c71c213cb3_seed1.mcap |
| PP-SWR-030 | SG-01 | S1b-a-VP-0-693b15015bfa | VP-0 | 1 | 8.008 | 25 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S1b-a-VP-0-693b15015bfa_seed1.mcap |
| PP-SWR-051 | SG-01 | F02-e-S1a-VP-5-29183b65ffaf | VP-5 | 1 | — | -0.1118 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F02-e-S1a-VP-5-29183b65ffaf_seed1.mcap |
| PP-SWR-051 | SG-01 | F02-e-S1c-VP-5-50d3444b79d5 | VP-5 | 1 | — | -0.1182 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F02-e-S1c-VP-5-50d3444b79d5_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1a-VP-0-1c03af025ee4 | VP-0 | 1 | — | -0.9642 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F03-c-S1a-VP-0-1c03af025ee4_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1a-VP-1-a5219f0b3fc2 | VP-1 | 1 | — | -0.9873 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F03-c-S1a-VP-1-a5219f0b3fc2_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1a-VP-5-4a0b9685f06c | VP-5 | 1 | — | -1.274 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F03-c-S1a-VP-5-4a0b9685f06c_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1c-VP-0-0e2929c3df25 | VP-0 | 1 | — | -0.9815 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F03-c-S1c-VP-0-0e2929c3df25_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1c-VP-1-4278b1e68610 | VP-1 | 1 | — | -0.9932 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F03-c-S1c-VP-1-4278b1e68610_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1c-VP-5-ce2933b62cf1 | VP-5 | 1 | — | -1.279 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F03-c-S1c-VP-5-ce2933b62cf1_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1a-VP-0-5158987ade9c | VP-0 | 1 | — | -1 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F06-a-S1a-VP-0-5158987ade9c_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1c-VP-0-aed66d9b07f6 | VP-0 | 1 | — | -0.9928 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F06-a-S1c-VP-0-aed66d9b07f6_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-b-S1c-VP-5-545957874102 | VP-5 | 1 | — | -0.1125 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F06-b-S1c-VP-5-545957874102_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1a-VP-0-24550cfc95c5 | VP-0 | 1 | — | -1 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F06-d-S1a-VP-0-24550cfc95c5_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1a-VP-1-3a4b29f3fe5b | VP-1 | 1 | — | -1.027 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F06-d-S1a-VP-1-3a4b29f3fe5b_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1a-VP-5-9e2995fea291 | VP-5 | 1 | — | -1.3 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F06-d-S1a-VP-5-9e2995fea291_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1c-VP-0-608ec3b8fc9f | VP-0 | 1 | — | -0.9928 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F06-d-S1c-VP-0-608ec3b8fc9f_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1c-VP-1-40397bd3efa4 | VP-1 | 1 | — | -1.026 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F06-d-S1c-VP-1-40397bd3efa4_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1c-VP-5-bdab3c9103b7 | VP-5 | 1 | — | -1.291 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F06-d-S1c-VP-5-bdab3c9103b7_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-e-S1c-VP-5-87266b531a26 | VP-5 | 1 | — | -0.1366 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F06-e-S1c-VP-5-87266b531a26_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-0-4efddd649b2a | VP-0 | 1 | — | -0.9061 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F08-a-S1c-VP-0-4efddd649b2a_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-0-9d836e616214 | VP-0 | 1 | — | -0.9061 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F08-a-S1c-VP-0-9d836e616214_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-1-9f6496a368b0 | VP-1 | 1 | — | -0.9362 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F08-a-S1c-VP-1-9f6496a368b0_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-1-c098420638d4 | VP-1 | 1 | — | -0.9362 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F08-a-S1c-VP-1-c098420638d4_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-5-5d6c59c69cbe | VP-5 | 1 | — | -1.207 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F08-a-S1c-VP-5-5d6c59c69cbe_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-5-dce61f599c6e | VP-5 | 1 | — | -1.207 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F08-a-S1c-VP-5-dce61f599c6e_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-b-S1c-VP-0-4ae7633cf949 | VP-0 | 1 | — | -0.9738 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F08-b-S1c-VP-0-4ae7633cf949_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-b-S1c-VP-1-297eab73e001 | VP-1 | 1 | — | -0.9956 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F08-b-S1c-VP-1-297eab73e001_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-b-S1c-VP-5-9d66d718191a | VP-5 | 1 | — | -1.276 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F08-b-S1c-VP-5-9d66d718191a_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1a-VP-0-e8ee89e39225 | VP-0 | 1 | — | -0.3729 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F08-c-S1a-VP-0-e8ee89e39225_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1a-VP-1-1657cdf8bd31 | VP-1 | 1 | — | -0.4701 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F08-c-S1a-VP-1-1657cdf8bd31_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1a-VP-5-f71d325809b3 | VP-5 | 1 | — | -0.654 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F08-c-S1a-VP-5-f71d325809b3_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1c-VP-0-bca0f1afb997 | VP-0 | 1 | — | -0.982 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F08-c-S1c-VP-0-bca0f1afb997_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1c-VP-1-3d8334644eea | VP-1 | 1 | — | -1.008 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F08-c-S1c-VP-1-3d8334644eea_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1c-VP-5-06d7bb8fda8b | VP-5 | 1 | — | -1.272 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F08-c-S1c-VP-5-06d7bb8fda8b_seed1.mcap |
| PP-SWR-051 | SG-01 | F17-b-S1c-VP-0-a1cbc36bb0c4 | VP-0 | 1 | — | -0.9897 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F17-b-S1c-VP-0-a1cbc36bb0c4_seed1.mcap |
| PP-SWR-051 | SG-01 | F17-b-S1c-VP-1-0c87d5e3e71f | VP-1 | 1 | — | -0.8732 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F17-b-S1c-VP-1-0c87d5e3e71f_seed1.mcap |
| PP-SWR-051 | SG-01 | F17-b-S1c-VP-5-b18d1d45e3b1 | VP-5 | 1 | — | -1.293 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F17-b-S1c-VP-5-b18d1d45e3b1_seed1.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-3-0970d8d23b03 | VP-3 | 1 | — | -0.03751 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/G01-S1c-VP-3-0970d8d23b03_seed1.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-4-e79aef633429 | VP-4 | 1 | — | -0.06093 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/G01-S1c-VP-4-e79aef633429_seed1.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-5-38898514a806 | VP-5 | 1 | — | -0.1839 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/G01-S1c-VP-5-38898514a806_seed1.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-5-38898514a806 | VP-5 | 2 | — | -0.0244 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/G01-S1c-VP-5-38898514a806_seed2.mcap |
| PP-SWR-051 | SG-01 | S14-a-VP-0-cabfa230312d | VP-0 | 1 | — | -23.37 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-a-VP-0-cabfa230312d_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-0-ff8e4ce04140 | VP-0 | 1 | — | -0.1199 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-e-VP-0-ff8e4ce04140_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-1-c599c50726eb | VP-1 | 1 | — | -0.1905 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-e-VP-1-c599c50726eb_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-2-d2cc20ee8bbf | VP-2 | 1 | — | -0.2353 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-e-VP-2-d2cc20ee8bbf_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-3-24dcd5adb2de | VP-3 | 1 | — | -0.2707 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-e-VP-3-24dcd5adb2de_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-4-a571d2de589d | VP-4 | 1 | — | -0.2818 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-e-VP-4-a571d2de589d_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-5-3f2b28b63f2e | VP-5 | 1 | — | -0.4048 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-e-VP-5-3f2b28b63f2e_seed1.mcap |
| PP-SWR-085 | SG-01 | F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0 | VP-3 | 1 | — | -0.1044 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0_seed1.mcap |
| PP-SWR-085 | SG-01 | S12-c-VP-2-dcd8acfe5043 | VP-2 | 1 | — | -0.07989 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S12-c-VP-2-dcd8acfe5043_seed1.mcap |
| PP-SWR-085 | SG-01 | S12-c-VP-3-4b7830a9f53c | VP-3 | 1 | — | -0.08681 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S12-c-VP-3-4b7830a9f53c_seed1.mcap |
| PP-SWR-085 | SG-01 | S12-c-VP-4-406ed8c312c5 | VP-4 | 1 | — | -0.0853 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S12-c-VP-4-406ed8c312c5_seed1.mcap |
| PP-SWR-085 | SG-01 | S13-b-elk-VP-3-036d4797fb02 | VP-3 | 1 | — | -0.09176 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S13-b-elk-VP-3-036d4797fb02_seed1.mcap |
| PP-SWR-086 | SG-03 | F06-d-S4a_at_lka_activep0-VP-0-a65c5296268d | VP-0 | 1 | — | -0.7176 | >= -0.3 | DTLE vạch nhỏ nhất [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F06-d-S4a_at_lka_activep0-VP-0-a65c5296268d_seed1.mcap |
| PP-SWR-086 | SG-03 | F06-d-S4a_at_lka_activep0.2-VP-1-d522d4dee57a | VP-1 | 1 | — | -0.6405 | >= -0.3 | DTLE vạch nhỏ nhất [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F06-d-S4a_at_lka_activep0.2-VP-1-d522d4dee57a_seed1.mcap |
| PP-SWR-086 | SG-03 | F06-d-S5a_at_elk_activep0-VP-0-f32caea02125 | VP-0 | 1 | — | -0.7071 | >= -0.3 | DTLE vạch nhỏ nhất [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F06-d-S5a_at_elk_activep0-VP-0-f32caea02125_seed1.mcap |
| PP-SWR-086 | SG-03 | F06-d-S5a_at_elk_activep0.2-VP-1-f5395e617721 | VP-1 | 1 | — | -0.6304 | >= -0.3 | DTLE vạch nhỏ nhất [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F06-d-S5a_at_elk_activep0.2-VP-1-f5395e617721_seed1.mcap |
| PP-SWR-086 | SG-03 | S13-b-elk-VP-3-036d4797fb02 | VP-3 | 1 | — | -0.4499 | >= -0.3 | DTLE vạch nhỏ nhất [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S13-b-elk-VP-3-036d4797fb02_seed1.mcap |
| PP-SWR-088 | SG-03 | S12-c-VP-0-425b042b9630 | VP-0 | 1 | — | 0.1899 | >= 0.3 | Khoảng cách ngang nhỏ nhất tới xe mục tiêu [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S12-c-VP-0-425b042b9630_seed1.mcap |
| PP-SWR-088 | SG-03 | S12-c-VP-1-c5f495806475 | VP-1 | 1 | — | 0.1957 | >= 0.3 | Khoảng cách ngang nhỏ nhất tới xe mục tiêu [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S12-c-VP-1-c5f495806475_seed1.mcap |
| PP-SWR-088 | SG-03 | S12-c-VP-2-dcd8acfe5043 | VP-2 | 1 | — | 0.1907 | >= 0.3 | Khoảng cách ngang nhỏ nhất tới xe mục tiêu [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S12-c-VP-2-dcd8acfe5043_seed1.mcap |
| PP-SWR-088 | SG-03 | S12-c-VP-3-4b7830a9f53c | VP-3 | 1 | — | 0.1874 | >= 0.3 | Khoảng cách ngang nhỏ nhất tới xe mục tiêu [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S12-c-VP-3-4b7830a9f53c_seed1.mcap |
| PP-SWR-088 | SG-03 | S12-c-VP-4-406ed8c312c5 | VP-4 | 1 | — | 0.1855 | >= 0.3 | Khoảng cách ngang nhỏ nhất tới xe mục tiêu [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S12-c-VP-4-406ed8c312c5_seed1.mcap |
| PP-SWR-088 | SG-03 | S12-c-VP-5-7039c477036e | VP-5 | 1 | — | 0.1784 | >= 0.3 | Khoảng cách ngang nhỏ nhất tới xe mục tiêu [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S12-c-VP-5-7039c477036e_seed1.mcap |
| PP-SWR-091 | SG-03 | S13-b-elk-VP-3-036d4797fb02 | VP-3 | 1 | — | -0.4499 | >= -0.3 | DTLE vạch khi EPS chậm tới 100 ms [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S13-b-elk-VP-3-036d4797fb02_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-b-S1c-VP-0-4ae7633cf949 | VP-0 | 1 | 18.08 | 0.05689 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F08-b-S1c-VP-0-4ae7633cf949_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-b-S1c-VP-1-297eab73e001 | VP-1 | 1 | 18.08 | 0.05695 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F08-b-S1c-VP-1-297eab73e001_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-b-S1c-VP-5-9d66d718191a | VP-5 | 1 | 18.08 | 0.05688 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F08-b-S1c-VP-5-9d66d718191a_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-c-S1a-VP-0-e8ee89e39225 | VP-0 | 1 | 5.608 | 0.07296 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F08-c-S1a-VP-0-e8ee89e39225_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-c-S1a-VP-1-1657cdf8bd31 | VP-1 | 1 | 5.508 | 0.07302 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F08-c-S1a-VP-1-1657cdf8bd31_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-c-S1a-VP-5-f71d325809b3 | VP-5 | 1 | 5.608 | 0.0729 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F08-c-S1a-VP-5-f71d325809b3_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-c-S1c-VP-0-bca0f1afb997 | VP-0 | 1 | 5.208 | 0.07853 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F08-c-S1c-VP-0-bca0f1afb997_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-c-S1c-VP-1-3d8334644eea | VP-1 | 1 | 5.158 | 0.07843 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F08-c-S1c-VP-1-3d8334644eea_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-c-S1c-VP-5-06d7bb8fda8b | VP-5 | 1 | 5.158 | 0.07872 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F08-c-S1c-VP-5-06d7bb8fda8b_seed1.mcap |
| PP-SWR-100 | SG-04 | S12-c-VP-1-c5f495806475 | VP-1 | 1 | 5.477 | 0.05012 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S12-c-VP-1-c5f495806475_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-a-VP-0-3290c39907ee | VP-0 | 1 | 2.858 | 0.05247 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-a-VP-0-3290c39907ee_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-a-VP-0-cabfa230312d | VP-0 | 1 | 2.858 | 0.05247 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-a-VP-0-cabfa230312d_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-c-VP-0-c8e86866eeb2 | VP-0 | 1 | 12.36 | 0.1414 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-c-VP-0-c8e86866eeb2_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-c-VP-1-ffd30cdab212 | VP-1 | 1 | 12.36 | 0.1407 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-c-VP-1-ffd30cdab212_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-c-VP-2-51734930fc19 | VP-2 | 1 | 12.36 | 0.1408 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-c-VP-2-51734930fc19_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-c-VP-3-cbd4381d8311 | VP-3 | 1 | 12.36 | 0.1409 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-c-VP-3-cbd4381d8311_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-c-VP-4-5cb1a6c30767 | VP-4 | 1 | 12.36 | 0.1408 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-c-VP-4-5cb1a6c30767_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-c-VP-5-1c80d628c800 | VP-5 | 1 | 12.36 | 0.1408 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-c-VP-5-1c80d628c800_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-0-dc72ffbcfa45 | VP-0 | 1 | 3.558 | 0.05817 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-e-VP-0-dc72ffbcfa45_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-0-ff8e4ce04140 | VP-0 | 1 | 3.583 | 0.05641 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-e-VP-0-ff8e4ce04140_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-1-9e894e6e0e47 | VP-1 | 1 | 3.558 | 0.05791 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-e-VP-1-9e894e6e0e47_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-1-c599c50726eb | VP-1 | 1 | 3.583 | 0.05648 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-e-VP-1-c599c50726eb_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-2-8ea25fd5bd76 | VP-2 | 1 | 3.558 | 0.05816 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-e-VP-2-8ea25fd5bd76_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-2-d2cc20ee8bbf | VP-2 | 1 | 3.583 | 0.05644 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-e-VP-2-d2cc20ee8bbf_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-3-24dcd5adb2de | VP-3 | 1 | 3.583 | 0.0564 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-e-VP-3-24dcd5adb2de_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-3-5cf328ad0176 | VP-3 | 1 | 3.558 | 0.05817 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-e-VP-3-5cf328ad0176_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-4-a571d2de589d | VP-4 | 1 | 3.583 | 0.05637 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-e-VP-4-a571d2de589d_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-4-f51e1424afde | VP-4 | 1 | 3.558 | 0.05819 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-e-VP-4-f51e1424afde_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-5-3f2b28b63f2e | VP-5 | 1 | 3.583 | 0.05637 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-e-VP-5-3f2b28b63f2e_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-5-845fd11edffe | VP-5 | 1 | 3.558 | 0.05819 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-e-VP-5-845fd11edffe_seed1.mcap |
| PP-SWR-100 | SG-04 | S1b-a-VP-0-693b15015bfa | VP-0 | 1 | 2.858 | 0.05247 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S1b-a-VP-0-693b15015bfa_seed1.mcap |
| PP-SWR-101 | SG-04 | S14-c-VP-0-c8e86866eeb2 | VP-0 | 1 | 8.559 | 0.01113 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-c-VP-0-c8e86866eeb2_seed1.mcap |
| PP-SWR-101 | SG-04 | S14-c-VP-1-ffd30cdab212 | VP-1 | 1 | 8.559 | 0.0112 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-c-VP-1-ffd30cdab212_seed1.mcap |
| PP-SWR-101 | SG-04 | S14-c-VP-2-51734930fc19 | VP-2 | 1 | 8.559 | 0.01121 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-c-VP-2-51734930fc19_seed1.mcap |
| PP-SWR-101 | SG-04 | S14-c-VP-3-cbd4381d8311 | VP-3 | 1 | 8.559 | 0.0112 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-c-VP-3-cbd4381d8311_seed1.mcap |
| PP-SWR-101 | SG-04 | S14-c-VP-4-5cb1a6c30767 | VP-4 | 1 | 8.559 | 0.01119 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-c-VP-4-5cb1a6c30767_seed1.mcap |
| PP-SWR-101 | SG-04 | S14-c-VP-5-1c80d628c800 | VP-5 | 1 | 8.559 | 0.01119 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-c-VP-5-1c80d628c800_seed1.mcap |
| PP-SWR-101 | SG-04 | S14-e-VP-1-9e894e6e0e47 | VP-1 | 1 | 6.858 | 0.00553 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-e-VP-1-9e894e6e0e47_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-c-VP-0-c8e86866eeb2 | VP-0 | 1 | 8.559 | 0.000619 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-c-VP-0-c8e86866eeb2_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-c-VP-1-ffd30cdab212 | VP-1 | 1 | 8.559 | 0.0006151 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-c-VP-1-ffd30cdab212_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-c-VP-2-51734930fc19 | VP-2 | 1 | 8.559 | 0.000613 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-c-VP-2-51734930fc19_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-c-VP-3-cbd4381d8311 | VP-3 | 1 | 8.559 | 0.0006127 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-c-VP-3-cbd4381d8311_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-c-VP-4-5cb1a6c30767 | VP-4 | 1 | 8.559 | 0.0006125 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-c-VP-4-5cb1a6c30767_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-c-VP-5-1c80d628c800 | VP-5 | 1 | 8.559 | 0.0006125 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-c-VP-5-1c80d628c800_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-e-VP-0-dc72ffbcfa45 | VP-0 | 1 | 6.908 | 0.000316 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-e-VP-0-dc72ffbcfa45_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-e-VP-1-9e894e6e0e47 | VP-1 | 1 | 6.858 | 0.0003053 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-e-VP-1-9e894e6e0e47_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-e-VP-2-8ea25fd5bd76 | VP-2 | 1 | 6.908 | 0.0003159 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-e-VP-2-8ea25fd5bd76_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-e-VP-3-5cf328ad0176 | VP-3 | 1 | 6.908 | 0.000316 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-e-VP-3-5cf328ad0176_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-e-VP-4-f51e1424afde | VP-4 | 1 | 6.908 | 0.0003162 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-e-VP-4-f51e1424afde_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-e-VP-5-845fd11edffe | VP-5 | 1 | 6.908 | 0.0003162 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S14-e-VP-5-845fd11edffe_seed1.mcap |

## Trượt MINOR

| Requirement | Safety goal | Ca | Profile | Seed | Trượt đầu tiên [s] | Giá trị | Ngưỡng | Chi tiết | MCAP |
|---|---|---|---|---|---|---|---|---|---|
| PP-SWR-032 | — | F01-a-S4a_at_lka_activep0-VP-0-c97d4f8c3b33 | VP-0 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F01-a-S4a_at_lka_activep0-VP-0-c97d4f8c3b33_seed1.mcap |
| PP-SWR-032 | — | F01-a-S4a_at_lka_activep0-VP-0-c97d4f8c3b33 | VP-0 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F01-a-S4a_at_lka_activep0-VP-0-c97d4f8c3b33_seed2.mcap |
| PP-SWR-032 | — | F01-a-S5a_at_elk_activep0.2-VP-1-44c9a8a8a61d | VP-1 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F01-a-S5a_at_elk_activep0.2-VP-1-44c9a8a8a61d_seed1.mcap |
| PP-SWR-032 | — | F01-a-S5a_at_elk_activep0.2-VP-1-44c9a8a8a61d | VP-1 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F01-a-S5a_at_elk_activep0.2-VP-1-44c9a8a8a61d_seed2.mcap |
| PP-SWR-032 | — | F01-b-S4a_at_lka_activep0-VP-2-26b730c60966 | VP-2 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F01-b-S4a_at_lka_activep0-VP-2-26b730c60966_seed1.mcap |
| PP-SWR-032 | — | F01-b-S4a_at_lka_activep0-VP-2-26b730c60966 | VP-2 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F01-b-S4a_at_lka_activep0-VP-2-26b730c60966_seed2.mcap |
| PP-SWR-032 | — | F01-b-S4a_at_lka_activep0.2-VP-3-7e4bb0e3caed | VP-3 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F01-b-S4a_at_lka_activep0.2-VP-3-7e4bb0e3caed_seed1.mcap |
| PP-SWR-032 | — | F01-b-S4a_at_lka_activep0.2-VP-3-7e4bb0e3caed | VP-3 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F01-b-S4a_at_lka_activep0.2-VP-3-7e4bb0e3caed_seed2.mcap |
| PP-SWR-032 | — | F01-b-S5a_at_elk_activep0-VP-2-795bfb495e44 | VP-2 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F01-b-S5a_at_elk_activep0-VP-2-795bfb495e44_seed1.mcap |
| PP-SWR-032 | — | F01-b-S5a_at_elk_activep0.2-VP-3-43bbc0fa0b87 | VP-3 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F01-b-S5a_at_elk_activep0.2-VP-3-43bbc0fa0b87_seed1.mcap |
| PP-SWR-032 | — | F01-b-S5a_at_elk_activep0.2-VP-3-43bbc0fa0b87 | VP-3 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F01-b-S5a_at_elk_activep0.2-VP-3-43bbc0fa0b87_seed2.mcap |
| PP-SWR-032 | — | F01-c-S4a_at_lka_activep0-VP-4-914355537c7d | VP-4 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F01-c-S4a_at_lka_activep0-VP-4-914355537c7d_seed1.mcap |
| PP-SWR-032 | — | F01-c-S4a_at_lka_activep0-VP-4-914355537c7d | VP-4 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F01-c-S4a_at_lka_activep0-VP-4-914355537c7d_seed2.mcap |
| PP-SWR-032 | — | F01-c-S4a_at_lka_activep0.2-VP-5-2e109dc103db | VP-5 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F01-c-S4a_at_lka_activep0.2-VP-5-2e109dc103db_seed1.mcap |
| PP-SWR-032 | — | F01-c-S4a_at_lka_activep0.2-VP-5-2e109dc103db | VP-5 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F01-c-S4a_at_lka_activep0.2-VP-5-2e109dc103db_seed2.mcap |
| PP-SWR-032 | — | F01-c-S5a_at_elk_activep0-VP-4-d7e0b59fbf4d | VP-4 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F01-c-S5a_at_elk_activep0-VP-4-d7e0b59fbf4d_seed1.mcap |
| PP-SWR-032 | — | F01-c-S5a_at_elk_activep0-VP-4-d7e0b59fbf4d | VP-4 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F01-c-S5a_at_elk_activep0-VP-4-d7e0b59fbf4d_seed2.mcap |
| PP-SWR-032 | — | F01-c-S5a_at_elk_activep0.2-VP-5-fbea90d7d4d0 | VP-5 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F01-c-S5a_at_elk_activep0.2-VP-5-fbea90d7d4d0_seed1.mcap |
| PP-SWR-032 | — | F01-c-S5a_at_elk_activep0.2-VP-5-fbea90d7d4d0 | VP-5 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F01-c-S5a_at_elk_activep0.2-VP-5-fbea90d7d4d0_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-0-944a5944b2f0 | VP-0 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/G01-S4c-VP-0-944a5944b2f0_seed1.mcap |
| PP-SWR-032 | — | G01-S4c-VP-0-944a5944b2f0 | VP-0 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/G01-S4c-VP-0-944a5944b2f0_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-1-d9c02f4d85c9 | VP-1 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/G01-S4c-VP-1-d9c02f4d85c9_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-2-19b08e51426b | VP-2 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/G01-S4c-VP-2-19b08e51426b_seed1.mcap |
| PP-SWR-032 | — | G01-S4c-VP-2-19b08e51426b | VP-2 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/G01-S4c-VP-2-19b08e51426b_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-3-9991783c316d | VP-3 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/G01-S4c-VP-3-9991783c316d_seed1.mcap |
| PP-SWR-032 | — | G01-S4c-VP-3-9991783c316d | VP-3 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/G01-S4c-VP-3-9991783c316d_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-4-072664ac9b98 | VP-4 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/G01-S4c-VP-4-072664ac9b98_seed1.mcap |
| PP-SWR-032 | — | G01-S4c-VP-4-072664ac9b98 | VP-4 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/G01-S4c-VP-4-072664ac9b98_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-5-26df2868e70c | VP-5 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/G01-S4c-VP-5-26df2868e70c_seed1.mcap |
| PP-SWR-032 | — | G01-S4c-VP-5-26df2868e70c | VP-5 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/G01-S4c-VP-5-26df2868e70c_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-0-69e53aeef11a | VP-0 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S12-b-VP-0-69e53aeef11a_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-0-69e53aeef11a | VP-0 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S12-b-VP-0-69e53aeef11a_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-1-4b3e70a50a26 | VP-1 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S12-b-VP-1-4b3e70a50a26_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-1-4b3e70a50a26 | VP-1 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S12-b-VP-1-4b3e70a50a26_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-2-0962daddf5bd | VP-2 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S12-b-VP-2-0962daddf5bd_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-2-0962daddf5bd | VP-2 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S12-b-VP-2-0962daddf5bd_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-3-984dbaa7f733 | VP-3 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S12-b-VP-3-984dbaa7f733_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-3-984dbaa7f733 | VP-3 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S12-b-VP-3-984dbaa7f733_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-4-a4945d3bcd67 | VP-4 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S12-b-VP-4-a4945d3bcd67_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-4-a4945d3bcd67 | VP-4 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S12-b-VP-4-a4945d3bcd67_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-5-2b777db332c0 | VP-5 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S12-b-VP-5-2b777db332c0_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-5-2b777db332c0 | VP-5 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S12-b-VP-5-2b777db332c0_seed2.mcap |
| PP-SWR-032 | — | S13-a-VP-5-4d54367ca2b0 | VP-5 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S13-a-VP-5-4d54367ca2b0_seed1.mcap |
| PP-SWR-090 | — | F02-e-S5a_at_elk_activep0.2-VP-3-bb766866f0d0 | VP-3 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/F02-e-S5a_at_elk_activep0.2-VP-3-bb766866f0d0_seed1.mcap |
| PP-SWR-090 | — | S5-c-VP-5-fc8939d6aa80 | VP-5 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-2153-regression-71fb7c1/suite/mcap/S5-c-VP-5-fc8939d6aa80_seed1.mcap |

## Trượt ngoài phạm vi chấm của ca (thông tin, không tính vào kết luận)

| Mức | Requirement | Ca | Seed | Giá trị | Ngưỡng |
|---|---|---|---|---|---|
| BLOCKER | PP-SWR-051 | S2-c-VP-0-b84bf321b14a | 1 | -0.1848 | >= 0 |
| BLOCKER | PP-SWR-051 | S2-c-VP-1-1db4613cf0cb | 1 | -0.1727 | >= 0 |
| BLOCKER | PP-SWR-051 | S2-c-VP-2-213efa4e998e | 1 | -0.2814 | >= 0 |
| BLOCKER | PP-SWR-051 | S2-c-VP-3-4e8dc883d0cd | 1 | -0.3422 | >= 0 |
| BLOCKER | PP-SWR-051 | S2-c-VP-4-255842c24eca | 1 | -0.3737 | >= 0 |
| BLOCKER | PP-SWR-051 | S2-c-VP-5-9ad0657941fb | 1 | -0.4967 | >= 0 |
| MINOR | PP-SWR-062 | S2-c-VP-5-9ad0657941fb | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-051 | S2-d-VP-5-a311ab7697a8 | 1 | -0.0234 | >= 0 |
| MINOR | PP-SWR-062 | S2-d-VP-5-a311ab7697a8 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-0-ff8e4ce04140 | 1 | -1.593 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-0-dc72ffbcfa45 | 1 | -1.509 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-1-c599c50726eb | 1 | -1.675 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-1-9e894e6e0e47 | 1 | -1.495 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-2-d2cc20ee8bbf | 1 | -1.675 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-2-8ea25fd5bd76 | 1 | -1.504 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-3-24dcd5adb2de | 1 | -1.593 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-3-5cf328ad0176 | 1 | -1.509 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-4-a571d2de589d | 1 | -1.57 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-4-f51e1424afde | 1 | -1.508 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-5-3f2b28b63f2e | 1 | -1.57 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-5-845fd11edffe | 1 | -1.508 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-0-cabfa230312d | 1 | -0.2619 | >= 0 |
| BLOCKER | PP-SWR-005 | S14-a-VP-0-3290c39907ee | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-0-3290c39907ee | 1 | -0.1269 | >= 0 |
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
| MINOR | PP-SWR-090 | S6-b-VP-0-8cd97b161efa | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S6-ncap-edge-right-5-VP-4-86dc3e882cfa | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S6-ncap-edge-right-5-VP-5-e836ac7fac6e | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S6-ncap-edge-right-5-VP-5-e836ac7fac6e | 1 | 1 | = 0 |
| MINOR | PP-SWR-090 | S6-ncap-edge-right-6-VP-0-96da99cc59a8 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S6-ncap-edge-dashed-right-5-VP-4-042b1d5b2589 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S6-ncap-edge-dashed-right-5-VP-5-e5806c2a0972 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S6-ncap-edge-dashed-right-5-VP-5-e5806c2a0972 | 1 | 1 | = 0 |
| MINOR | PP-SWR-090 | S6-ncap-edge-dashed-right-6-VP-0-cbc6c280715a | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S6-a-VP-0-9fc3dd64df95 | 1 | 1 | <= 0 |
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
| MINOR | PP-SWR-032 | S12-c-VP-0-425b042b9630 | 2 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-1-c5f495806475 | 2 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-2-dcd8acfe5043 | 2 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-3-4b7830a9f53c | 2 | 1 | <= 0 |
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
| BLOCKER | PP-SWR-051 | S17-a-VP-5-b494108de31a | 1 | -0.2419 | >= 0 |
| MINOR | PP-SWR-062 | S17-a-VP-5-b494108de31a | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-051 | S17-b-VP-0-3de8f33b03db | 1 | -0.01854 | >= 0 |
| BLOCKER | PP-SWR-051 | S17-c-VP-0-ec530a565153 | 1 | -5.581 | >= 0 |
| BLOCKER | PP-SWR-051 | S17-c-VP-1-2fb27134ba07 | 1 | -5.702 | >= 0 |
| BLOCKER | PP-SWR-051 | S17-c-VP-2-d36a269b1605 | 1 | -5.945 | >= 0 |
| BLOCKER | PP-SWR-051 | S17-c-VP-3-23bdadaaa5df | 1 | -6.116 | >= 0 |
| BLOCKER | PP-SWR-051 | S17-c-VP-4-7235bceb0cae | 1 | -6.188 | >= 0 |
| BLOCKER | PP-SWR-051 | S17-c-VP-5-2fa05512e157 | 1 | -6.559 | >= 0 |
| MINOR | PP-SWR-062 | S17-c-VP-5-2fa05512e157 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-051 | S17-d-VP-4-0847e3e773ff | 1 | -0.04702 | >= 0 |
| BLOCKER | PP-SWR-051 | S17-d-VP-5-adc239af2eb2 | 1 | -0.6037 | >= 0 |
| MINOR | PP-SWR-062 | S17-d-VP-5-adc239af2eb2 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-051 | S17-e-VP-5-f985196e415b | 1 | -0.2419 | >= 0 |
| BLOCKER | PP-SWR-061 | F08-b-S1c-VP-0-4ae7633cf949 | 1 | 0.05648 | <= 0.05 |
| BLOCKER | PP-SWR-061 | F08-b-S1c-VP-1-297eab73e001 | 1 | 0.05649 | <= 0.05 |
| BLOCKER | PP-SWR-061 | F08-b-S1c-VP-5-9d66d718191a | 1 | 0.05648 | <= 0.05 |

## Bộ theo khía cạnh

| Bộ | Khía cạnh | Lần chạy | Kết luận | BLOCKER | MAJOR | MINOR |
|---|---|---|---|---|---|---|
| B0 | Conformance | — | Đạt C1, C2; Tích hợp được | — | — | — |
| B1 | Nominal | 922 | Không đạt | 5 | 0 | 0 |
| B2 | Regulatory | 594 | Không đạt | 25 | 0 | 0 |
| B3 | Performance limit | 289 | Không đạt | 52 | 0 | 2 |
| B4 | Robustness | 868 | Không đạt | 64 | 0 | 43 |
| B5 | Degradation and refusal | 306 | Không đạt | 52 | 0 | 0 |
| B6 | Comfort | 922 | Không đạt | 5 | 0 | 0 |
| B7 | Flexibility | 803 | Không đạt | 17 | 0 | 21 |
| B8 | Compute | 2079 | Không đạt | 121 | 0 | 45 |

## Số lần chạy

```json
{
 "planned": 2079,
 "executed": 2079,
 "failed": 120,
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
| VP-0 | 210 | 89.7% | PP-SWR-032, PP-SWR-051, PP-SWR-086 | 1.09 | 0.282 | 1.57 | 0.214 | **0.846** | 3.28 | 0.634 | 4.97 | 4.45 | 3.8 | -0.00941 |
| VP-1 | 145 | 90.0% | PP-SWR-032, PP-SWR-051, PP-SWR-086 | **1.21** | **0.287** | **1.57** | 0.211 | 0.773 | 3.23 | 0.611 | **5.02** | 4.17 | 3.5 | 0.00715 |
| VP-2 | 103 | 96.8% | PP-SWR-032 | 1.12 | 0.282 | 1.57 | 0.213 | 0.841 | 3.25 | 0.531 | 5.02 | 4.38 | 3.75 | 0.00277 |
| VP-3 | 102 | 90.0% | PP-SWR-032, PP-SWR-085, PP-SWR-090 | 1.07 | 0.282 | 1.57 | 0.214 | 0.845 | **3.29** | 0.479 | 5 | 4.45 | 3.82 | -0.00949 |
| VP-4 | 102 | 96.7% | PP-SWR-032 | 1.06 | 0.282 | 1.57 | **0.215** | 0.845 | 3.06 | 0.452 | 5 | **4.52** | **3.88** | -0.00993 |
| VP-5 | 141 | 90.6% | PP-SWR-032, PP-SWR-051, PP-SWR-090 | 1.06 | 0.282 | 1.57 | 0.215 | 0.845 | 3.06 | **0.326** | 4 | 4.52 | 3.88 | **-0.0221** |

| Chỉ số | Độ chênh lớn nhất giữa profile | Độ chênh nhỏ nhất | Profile tệ nhất |
|---|---|---|---|
| PP-SWR-002 a_y thêm vào lớn nhất khi đưa về giữa | 0.149 | 0 | VP-1 |
| PP-SWR-004 Jerk ngang RMS của path 0–1 s khi HWA lái | 0.0312 | 5.09e-06 | VP-1 |
| PP-SWR-004 Jerk ngang lớn nhất của path khi HWA lái (trung bình 0,5 s) | 0.242 | 0 | VP-1 |
| PP-SWR-004 Tốc độ quay vô lăng RMS khi HWA lái, vòng kín | 0.0214 | 0.000705 | VP-4 |
| PP-SWR-050 Lệch ngang của path so với tâm làn thật, 0–1 s, lớn nhất | 0.0999 | 0 | VP-0 |
| PP-SWR-053 Thời gian đưa xe về giữa (lệch ≤ 0,1 m) | 2.29 | 0 | VP-3 |
| PP-SWR-057 Khoảng cách ngang nhỏ nhất từ thân xe tới xe lớn khi ngang hàng | 0.308 | 0.242 | VP-5 |
| PP-SWR-059 Thời gian từ lúc hết ngang hàng tới lúc lệch ≤ 0,1 m | 4.85 | 1.02 | VP-1 |
| PP-SWR-081 Thời lượng path LKA tới COMPLETED | 0.525 | 0 | VP-4 |
| PP-SWR-082 Thời lượng path ELK tới COMPLETED | 1.4 | 0 | VP-4 |
| PP-SWR-087 DTLE LKA nhỏ nhất | 0.117 | 0.00805 | VP-5 |

Requirement đạt 100 % trên mọi profile: không (VP-0, VP-1, VP-2, VP-3, VP-4, VP-5)

## Thời gian tính

1696210 chu kỳ. p95 ≤ 1.58 ms, p99 ≤ 3.16 ms (cận trên của bin), lớn nhất 583 ms. Đo trên máy chạy SIL, gồm adapter; không khẳng định thời gian trên ECU (mục 9.1).

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
| S6 | 0.2 | 0.0262 |
| S6 | 0.3 | 0.0288 |
| S6 | 0.4 | 0.0262 |
| S6 | 0.5 | 0.0324 |
| S6 | 0.6 | 0.0176 |
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

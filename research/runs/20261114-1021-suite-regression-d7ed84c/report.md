# Kết luận: Không đạt

- Planner: pp_planner 0.2.0 commit d7ed84c63ad7 calibration d532993b1b2f t7 quintic (e2c59f1412a1)
- Tích hợp được: có
- Đã chạy: 2073 lần chạy; trượt BLOCKER 254, MAJOR 0, MINOR 52
- Kết luận chỉ đúng trong phạm vi đã thử, không phải bằng chứng an toàn (Software Qualification Test Specification 3).

## Trượt BLOCKER

| Requirement | Safety goal | Ca | Profile | Seed | Trượt đầu tiên [s] | Giá trị | Ngưỡng | Chi tiết | MCAP |
|---|---|---|---|---|---|---|---|---|---|
| PP-SWR-005 | SG-02 | S1b-a-VP-0-693b15015bfa | VP-0 | 1 | 8.008 | 1 | = 0 | Chu kỳ cua gắt mà mất path hoặc HWA | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S1b-a-VP-0-693b15015bfa_seed1.mcap |
| PP-SWR-006 | SG-02 | S1b-a-VP-0-693b15015bfa | VP-0 | 1 | 3.958 | -0.143 | >= 0 | a_y path trừ (aysmax − epsilon_ay), 0–1 s, khi a_y cần > aysmax [m/s²] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S1b-a-VP-0-693b15015bfa_seed1.mcap |
| PP-SWR-030 | SG-01 | F20-a-S4a_at_lka_activep0-VP-4-b51d3ad6986a | VP-4 | 1 | 6.377 | 282 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F20-a-S4a_at_lka_activep0-VP-4-b51d3ad6986a_seed1.mcap |
| PP-SWR-030 | SG-01 | F20-a-S4a_at_lka_activep0.2-VP-5-49fe260e4f65 | VP-5 | 1 | 6.552 | 418 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F20-a-S4a_at_lka_activep0.2-VP-5-49fe260e4f65_seed1.mcap |
| PP-SWR-030 | SG-01 | F20-a-S5a_at_elk_activep0-VP-4-04e5ab29da71 | VP-4 | 1 | 6.752 | 410 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F20-a-S5a_at_elk_activep0-VP-4-04e5ab29da71_seed1.mcap |
| PP-SWR-030 | SG-01 | F20-a-S5a_at_elk_activep0.2-VP-5-9244610c5a8c | VP-5 | 1 | 6.927 | 214 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F20-a-S5a_at_elk_activep0.2-VP-5-9244610c5a8c_seed1.mcap |
| PP-SWR-030 | SG-01 | G01-S4c-VP-0-944a5944b2f0 | VP-0 | 1 | 10.65 | 254 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S4c-VP-0-944a5944b2f0_seed1.mcap |
| PP-SWR-030 | SG-01 | G01-S4c-VP-1-d9c02f4d85c9 | VP-1 | 1 | 10.65 | 10 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S4c-VP-1-d9c02f4d85c9_seed1.mcap |
| PP-SWR-030 | SG-01 | G01-S4c-VP-2-19b08e51426b | VP-2 | 1 | 10.65 | 10 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S4c-VP-2-19b08e51426b_seed1.mcap |
| PP-SWR-030 | SG-01 | G01-S4c-VP-3-9991783c316d | VP-3 | 1 | 10.65 | 254 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S4c-VP-3-9991783c316d_seed1.mcap |
| PP-SWR-030 | SG-01 | G01-S4c-VP-4-072664ac9b98 | VP-4 | 1 | 10.65 | 254 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S4c-VP-4-072664ac9b98_seed1.mcap |
| PP-SWR-030 | SG-01 | G01-S4c-VP-5-26df2868e70c | VP-5 | 1 | 10.65 | 254 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S4c-VP-5-26df2868e70c_seed1.mcap |
| PP-SWR-030 | SG-01 | S14-a-VP-0-3290c39907ee | VP-0 | 1 | 8.008 | 25 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-a-VP-0-3290c39907ee_seed1.mcap |
| PP-SWR-030 | SG-01 | S16-d-VP-0-e29852ad5a1c | VP-0 | 1 | — | — | — | ELK: có REQUEST nhưng thiếu path can thiệp hợp lệ | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S16-d-VP-0-e29852ad5a1c_seed1.mcap |
| PP-SWR-030 | SG-01 | S16-d-VP-3-c4c71c213cb3 | VP-3 | 1 | — | — | — | ELK: có REQUEST nhưng thiếu path can thiệp hợp lệ | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S16-d-VP-3-c4c71c213cb3_seed1.mcap |
| PP-SWR-030 | SG-01 | S1b-a-VP-0-693b15015bfa | VP-0 | 1 | 8.008 | 25 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S1b-a-VP-0-693b15015bfa_seed1.mcap |
| PP-SWR-051 | SG-01 | F01-c-S1c-VP-5-0c7c7c8af819 | VP-5 | 1 | — | -0.2071 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-c-S1c-VP-5-0c7c7c8af819_seed1.mcap |
| PP-SWR-051 | SG-01 | F01-c-S1c-VP-5-0c7c7c8af819 | VP-5 | 2 | — | -0.1274 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-c-S1c-VP-5-0c7c7c8af819_seed2.mcap |
| PP-SWR-051 | SG-01 | F02-e-S1a-VP-5-29183b65ffaf | VP-5 | 1 | — | -0.1118 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F02-e-S1a-VP-5-29183b65ffaf_seed1.mcap |
| PP-SWR-051 | SG-01 | F02-e-S1c-VP-5-50d3444b79d5 | VP-5 | 1 | — | -0.1172 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F02-e-S1c-VP-5-50d3444b79d5_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1a-VP-0-1c03af025ee4 | VP-0 | 1 | — | -0.9642 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F03-c-S1a-VP-0-1c03af025ee4_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1a-VP-1-a5219f0b3fc2 | VP-1 | 1 | — | -0.9873 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F03-c-S1a-VP-1-a5219f0b3fc2_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1a-VP-5-4a0b9685f06c | VP-5 | 1 | — | -1.274 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F03-c-S1a-VP-5-4a0b9685f06c_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1c-VP-0-0e2929c3df25 | VP-0 | 1 | — | -0.9763 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F03-c-S1c-VP-0-0e2929c3df25_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1c-VP-1-4278b1e68610 | VP-1 | 1 | — | -0.9852 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F03-c-S1c-VP-1-4278b1e68610_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1c-VP-5-ce2933b62cf1 | VP-5 | 1 | — | -1.282 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F03-c-S1c-VP-5-ce2933b62cf1_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1a-VP-0-1f040b41d9e1 | VP-0 | 1 | — | -0.392 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-a-S1a-VP-0-1f040b41d9e1_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1a-VP-0-3397774191aa | VP-0 | 1 | — | -0.3687 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-a-S1a-VP-0-3397774191aa_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1a-VP-0-5158987ade9c | VP-0 | 1 | — | -0.6649 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-a-S1a-VP-0-5158987ade9c_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1a-VP-0-80f1becb446a | VP-0 | 1 | — | -0.3456 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-a-S1a-VP-0-80f1becb446a_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1a-VP-0-9ae034e25470 | VP-0 | 1 | — | -0.3925 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-a-S1a-VP-0-9ae034e25470_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1a-VP-1-cbe75d17374b | VP-1 | 1 | — | -0.3532 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-a-S1a-VP-1-cbe75d17374b_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1a-VP-5-e8fc0fb072e3 | VP-5 | 1 | — | -0.6535 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-a-S1a-VP-5-e8fc0fb072e3_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1c-VP-0-4e752ad53686 | VP-0 | 1 | — | -0.9817 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-a-S1c-VP-0-4e752ad53686_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1c-VP-0-5178b8cf8034 | VP-0 | 1 | — | -0.4657 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-a-S1c-VP-0-5178b8cf8034_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1c-VP-0-868c0af677ac | VP-0 | 1 | — | -0.278 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-a-S1c-VP-0-868c0af677ac_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1c-VP-0-aed66d9b07f6 | VP-0 | 1 | — | -0.9648 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-a-S1c-VP-0-aed66d9b07f6_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1c-VP-1-b4b47edd75f6 | VP-1 | 1 | — | -0.2848 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-a-S1c-VP-1-b4b47edd75f6_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1c-VP-5-03661768786f | VP-5 | 1 | — | -0.5851 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-a-S1c-VP-5-03661768786f_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-b-S1a-VP-0-46da72dcd782 | VP-0 | 1 | — | -0.3539 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-b-S1a-VP-0-46da72dcd782_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-b-S1a-VP-1-ce7e7e39c2ab | VP-1 | 1 | — | -0.3615 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-b-S1a-VP-1-ce7e7e39c2ab_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-b-S1a-VP-5-cc03ac29fdde | VP-5 | 1 | — | -0.6624 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-b-S1a-VP-5-cc03ac29fdde_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-b-S1c-VP-0-d617705779af | VP-0 | 1 | — | -0.8133 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-b-S1c-VP-0-d617705779af_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-b-S1c-VP-1-6a696f8d0446 | VP-1 | 1 | — | -0.8394 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-b-S1c-VP-1-6a696f8d0446_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-b-S1c-VP-5-545957874102 | VP-5 | 1 | — | -1.115 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-b-S1c-VP-5-545957874102_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1a-VP-0-24550cfc95c5 | VP-0 | 1 | — | -0.6649 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-d-S1a-VP-0-24550cfc95c5_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1a-VP-1-3a4b29f3fe5b | VP-1 | 1 | — | -0.6868 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-d-S1a-VP-1-3a4b29f3fe5b_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1a-VP-5-9e2995fea291 | VP-5 | 1 | — | -0.9682 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-d-S1a-VP-5-9e2995fea291_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1c-VP-0-608ec3b8fc9f | VP-0 | 1 | — | -0.9648 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-d-S1c-VP-0-608ec3b8fc9f_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1c-VP-1-40397bd3efa4 | VP-1 | 1 | — | -1.007 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-d-S1c-VP-1-40397bd3efa4_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1c-VP-5-bdab3c9103b7 | VP-5 | 1 | — | -1.277 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-d-S1c-VP-5-bdab3c9103b7_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-e-S1a-VP-0-32d8e11b13a4 | VP-0 | 1 | — | -0.392 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-e-S1a-VP-0-32d8e11b13a4_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-e-S1a-VP-1-5196def8dd8f | VP-1 | 1 | — | -0.3991 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-e-S1a-VP-1-5196def8dd8f_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-e-S1a-VP-5-a76b71e5c69c | VP-5 | 1 | — | -0.6994 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-e-S1a-VP-5-a76b71e5c69c_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-e-S1c-VP-0-21907f19a036 | VP-0 | 1 | — | -0.9817 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-e-S1c-VP-0-21907f19a036_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-e-S1c-VP-1-1f3d70de82c2 | VP-1 | 1 | — | -0.9986 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-e-S1c-VP-1-1f3d70de82c2_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-e-S1c-VP-5-87266b531a26 | VP-5 | 1 | — | -1.279 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-e-S1c-VP-5-87266b531a26_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-0-4efddd649b2a | VP-0 | 1 | — | -0.9683 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-a-S1c-VP-0-4efddd649b2a_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-0-9d836e616214 | VP-0 | 1 | — | -0.9683 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-a-S1c-VP-0-9d836e616214_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-1-9f6496a368b0 | VP-1 | 1 | — | -0.992 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-a-S1c-VP-1-9f6496a368b0_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-1-c098420638d4 | VP-1 | 1 | — | -0.992 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-a-S1c-VP-1-c098420638d4_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-5-5d6c59c69cbe | VP-5 | 1 | — | -1.269 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-a-S1c-VP-5-5d6c59c69cbe_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-5-dce61f599c6e | VP-5 | 1 | — | -1.269 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-a-S1c-VP-5-dce61f599c6e_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-b-S1c-VP-0-4ae7633cf949 | VP-0 | 1 | — | -0.9576 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-b-S1c-VP-0-4ae7633cf949_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-b-S1c-VP-1-297eab73e001 | VP-1 | 1 | — | -1.006 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-b-S1c-VP-1-297eab73e001_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-b-S1c-VP-5-9d66d718191a | VP-5 | 1 | — | -1.261 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-b-S1c-VP-5-9d66d718191a_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1a-VP-0-e8ee89e39225 | VP-0 | 1 | — | -0.3729 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-c-S1a-VP-0-e8ee89e39225_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1a-VP-1-1657cdf8bd31 | VP-1 | 1 | — | -0.4701 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-c-S1a-VP-1-1657cdf8bd31_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1a-VP-5-f71d325809b3 | VP-5 | 1 | — | -0.654 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-c-S1a-VP-5-f71d325809b3_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1c-VP-0-bca0f1afb997 | VP-0 | 1 | — | -1.066 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-c-S1c-VP-0-bca0f1afb997_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1c-VP-1-3d8334644eea | VP-1 | 1 | — | -1.094 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-c-S1c-VP-1-3d8334644eea_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1c-VP-5-06d7bb8fda8b | VP-5 | 1 | — | -1.312 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-c-S1c-VP-5-06d7bb8fda8b_seed1.mcap |
| PP-SWR-051 | SG-01 | F17-b-S1c-VP-0-a1cbc36bb0c4 | VP-0 | 1 | — | -0.9933 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F17-b-S1c-VP-0-a1cbc36bb0c4_seed1.mcap |
| PP-SWR-051 | SG-01 | F17-b-S1c-VP-1-0c87d5e3e71f | VP-1 | 1 | — | -0.8732 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F17-b-S1c-VP-1-0c87d5e3e71f_seed1.mcap |
| PP-SWR-051 | SG-01 | F17-b-S1c-VP-5-b18d1d45e3b1 | VP-5 | 1 | — | -1.293 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F17-b-S1c-VP-5-b18d1d45e3b1_seed1.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-0-1467a0e9844f | VP-0 | 1 | — | -0.309 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S1c-VP-0-1467a0e9844f_seed1.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-0-1467a0e9844f | VP-0 | 2 | — | -0.1148 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S1c-VP-0-1467a0e9844f_seed2.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-1-15c9123704b8 | VP-1 | 1 | — | -0.3367 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S1c-VP-1-15c9123704b8_seed1.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-1-15c9123704b8 | VP-1 | 2 | — | -0.1691 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S1c-VP-1-15c9123704b8_seed2.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-2-b56ea41bbee2 | VP-2 | 1 | — | -0.4131 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S1c-VP-2-b56ea41bbee2_seed1.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-2-b56ea41bbee2 | VP-2 | 2 | — | -0.2203 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S1c-VP-2-b56ea41bbee2_seed2.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-3-0970d8d23b03 | VP-3 | 1 | — | -0.4643 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S1c-VP-3-0970d8d23b03_seed1.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-3-0970d8d23b03 | VP-3 | 2 | — | -0.2696 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S1c-VP-3-0970d8d23b03_seed2.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-4-e79aef633429 | VP-4 | 1 | — | -0.4879 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S1c-VP-4-e79aef633429_seed1.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-4-e79aef633429 | VP-4 | 2 | — | -0.2911 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S1c-VP-4-e79aef633429_seed2.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-5-38898514a806 | VP-5 | 1 | — | -0.6109 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S1c-VP-5-38898514a806_seed1.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-5-38898514a806 | VP-5 | 2 | — | -0.4141 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S1c-VP-5-38898514a806_seed2.mcap |
| PP-SWR-051 | SG-01 | S12-a-VP-2-748f36869259 | VP-2 | 1 | — | -0.0112 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-a-VP-2-748f36869259_seed1.mcap |
| PP-SWR-051 | SG-01 | S12-a-VP-3-48c884c3f7fc | VP-3 | 1 | — | -0.0618 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-a-VP-3-48c884c3f7fc_seed1.mcap |
| PP-SWR-051 | SG-01 | S12-a-VP-4-e0fb234e6632 | VP-4 | 1 | — | -0.08456 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-a-VP-4-e0fb234e6632_seed1.mcap |
| PP-SWR-051 | SG-01 | S12-a-VP-4-e0fb234e6632 | VP-4 | 2 | — | -0.0291 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-a-VP-4-e0fb234e6632_seed2.mcap |
| PP-SWR-051 | SG-01 | S12-a-VP-5-e7c93cf1d873 | VP-5 | 1 | — | -0.2076 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-a-VP-5-e7c93cf1d873_seed1.mcap |
| PP-SWR-051 | SG-01 | S12-a-VP-5-e7c93cf1d873 | VP-5 | 2 | — | -0.1521 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-a-VP-5-e7c93cf1d873_seed2.mcap |
| PP-SWR-051 | SG-01 | S14-a-VP-0-cabfa230312d | VP-0 | 1 | — | -23.09 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-a-VP-0-cabfa230312d_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-0-ff8e4ce04140 | VP-0 | 1 | — | -0.1199 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-0-ff8e4ce04140_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-1-c599c50726eb | VP-1 | 1 | — | -0.1905 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-1-c599c50726eb_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-2-d2cc20ee8bbf | VP-2 | 1 | — | -0.2353 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-2-d2cc20ee8bbf_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-3-24dcd5adb2de | VP-3 | 1 | — | -0.2707 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-3-24dcd5adb2de_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-4-a571d2de589d | VP-4 | 1 | — | -0.2818 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-4-a571d2de589d_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-5-3f2b28b63f2e | VP-5 | 1 | — | -0.4048 | >= 0 | DLC nhỏ nhất so với làn thật [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-5-3f2b28b63f2e_seed1.mcap |
| PP-SWR-085 | SG-01 | F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0 | VP-3 | 1 | — | -0.1044 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0_seed1.mcap |
| PP-SWR-085 | SG-01 | S13-b-elk-VP-3-036d4797fb02 | VP-3 | 1 | — | -0.09176 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S13-b-elk-VP-3-036d4797fb02_seed1.mcap |
| PP-SWR-086 | SG-03 | S13-b-elk-VP-3-036d4797fb02 | VP-3 | 1 | — | -0.4499 | >= -0.3 | DTLE vạch nhỏ nhất [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S13-b-elk-VP-3-036d4797fb02_seed1.mcap |
| PP-SWR-091 | SG-03 | S13-b-elk-VP-3-036d4797fb02 | VP-3 | 1 | — | -0.4499 | >= -0.3 | DTLE vạch khi EPS chậm tới 100 ms [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S13-b-elk-VP-3-036d4797fb02_seed1.mcap |
| PP-SWR-100 | SG-04 | F01-a-S1c-VP-0-1a5c48a897b2 | VP-0 | 1 | 9.358 | 0.08807 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-a-S1c-VP-0-1a5c48a897b2_seed1.mcap |
| PP-SWR-100 | SG-04 | F01-a-S1c-VP-0-1a5c48a897b2 | VP-0 | 2 | 9.09 | 0.07832 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-a-S1c-VP-0-1a5c48a897b2_seed2.mcap |
| PP-SWR-100 | SG-04 | F01-a-S1c-VP-0-8a235eee47db | VP-0 | 1 | 9.208 | 0.09084 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-a-S1c-VP-0-8a235eee47db_seed1.mcap |
| PP-SWR-100 | SG-04 | F01-a-S1c-VP-0-8a235eee47db | VP-0 | 2 | 9.115 | 0.08418 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-a-S1c-VP-0-8a235eee47db_seed2.mcap |
| PP-SWR-100 | SG-04 | F01-a-S1c-VP-0-c76eb95d20d4 | VP-0 | 1 | 9.158 | 0.09579 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-a-S1c-VP-0-c76eb95d20d4_seed1.mcap |
| PP-SWR-100 | SG-04 | F01-a-S1c-VP-0-c76eb95d20d4 | VP-0 | 2 | 9.115 | 0.08252 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-a-S1c-VP-0-c76eb95d20d4_seed2.mcap |
| PP-SWR-100 | SG-04 | F01-a-S1c-VP-0-d6522b8df405 | VP-0 | 1 | 9.158 | 0.09545 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-a-S1c-VP-0-d6522b8df405_seed1.mcap |
| PP-SWR-100 | SG-04 | F01-a-S1c-VP-0-d6522b8df405 | VP-0 | 2 | 9.115 | 0.08299 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-a-S1c-VP-0-d6522b8df405_seed2.mcap |
| PP-SWR-100 | SG-04 | F01-a-S1c-VP-0-e97744b4881d | VP-0 | 1 | 9.358 | 0.09432 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-a-S1c-VP-0-e97744b4881d_seed1.mcap |
| PP-SWR-100 | SG-04 | F01-a-S1c-VP-0-e97744b4881d | VP-0 | 2 | 9.09 | 0.07905 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-a-S1c-VP-0-e97744b4881d_seed2.mcap |
| PP-SWR-100 | SG-04 | F01-a-S1c-VP-1-cb515e0fbf62 | VP-1 | 1 | 9.158 | 0.09585 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-a-S1c-VP-1-cb515e0fbf62_seed1.mcap |
| PP-SWR-100 | SG-04 | F01-a-S1c-VP-1-cb515e0fbf62 | VP-1 | 2 | 9.115 | 0.08294 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-a-S1c-VP-1-cb515e0fbf62_seed2.mcap |
| PP-SWR-100 | SG-04 | F01-a-S1c-VP-5-76930245ec3c | VP-5 | 1 | 9.158 | 0.09554 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-a-S1c-VP-5-76930245ec3c_seed1.mcap |
| PP-SWR-100 | SG-04 | F01-a-S1c-VP-5-76930245ec3c | VP-5 | 2 | 9.115 | 0.08298 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-a-S1c-VP-5-76930245ec3c_seed2.mcap |
| PP-SWR-100 | SG-04 | F01-b-S1c-VP-0-b2e4e85d36d3 | VP-0 | 1 | 9.508 | 0.09171 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-b-S1c-VP-0-b2e4e85d36d3_seed1.mcap |
| PP-SWR-100 | SG-04 | F01-b-S1c-VP-0-b2e4e85d36d3 | VP-0 | 2 | 9.115 | 0.09661 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-b-S1c-VP-0-b2e4e85d36d3_seed2.mcap |
| PP-SWR-100 | SG-04 | F01-b-S1c-VP-1-f4c4a4ce9541 | VP-1 | 1 | 9.508 | 0.09255 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-b-S1c-VP-1-f4c4a4ce9541_seed1.mcap |
| PP-SWR-100 | SG-04 | F01-b-S1c-VP-1-f4c4a4ce9541 | VP-1 | 2 | 9.115 | 0.09536 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-b-S1c-VP-1-f4c4a4ce9541_seed2.mcap |
| PP-SWR-100 | SG-04 | F01-b-S1c-VP-5-ad8225f5417e | VP-5 | 1 | 9.508 | 0.09151 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-b-S1c-VP-5-ad8225f5417e_seed1.mcap |
| PP-SWR-100 | SG-04 | F01-b-S1c-VP-5-ad8225f5417e | VP-5 | 2 | 9.115 | 0.09662 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-b-S1c-VP-5-ad8225f5417e_seed2.mcap |
| PP-SWR-100 | SG-04 | F01-c-S1c-VP-0-0fdc9fcf3f98 | VP-0 | 1 | 9.358 | 0.08806 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-c-S1c-VP-0-0fdc9fcf3f98_seed1.mcap |
| PP-SWR-100 | SG-04 | F01-c-S1c-VP-0-0fdc9fcf3f98 | VP-0 | 2 | 9.34 | 0.08196 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-c-S1c-VP-0-0fdc9fcf3f98_seed2.mcap |
| PP-SWR-100 | SG-04 | F01-c-S1c-VP-1-8ceef626e241 | VP-1 | 1 | 9.358 | 0.089 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-c-S1c-VP-1-8ceef626e241_seed1.mcap |
| PP-SWR-100 | SG-04 | F01-c-S1c-VP-1-8ceef626e241 | VP-1 | 2 | 9.34 | 0.08935 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-c-S1c-VP-1-8ceef626e241_seed2.mcap |
| PP-SWR-100 | SG-04 | F01-c-S1c-VP-5-0c7c7c8af819 | VP-5 | 1 | 9.358 | 0.08778 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-c-S1c-VP-5-0c7c7c8af819_seed1.mcap |
| PP-SWR-100 | SG-04 | F01-c-S1c-VP-5-0c7c7c8af819 | VP-5 | 2 | 9.34 | 0.08294 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-c-S1c-VP-5-0c7c7c8af819_seed2.mcap |
| PP-SWR-100 | SG-04 | F03-c-S1c-VP-0-0e2929c3df25 | VP-0 | 1 | 10.23 | 0.05577 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F03-c-S1c-VP-0-0e2929c3df25_seed1.mcap |
| PP-SWR-100 | SG-04 | F03-c-S1c-VP-1-4278b1e68610 | VP-1 | 1 | 10.18 | 0.06217 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F03-c-S1c-VP-1-4278b1e68610_seed1.mcap |
| PP-SWR-100 | SG-04 | F03-c-S1c-VP-5-ce2933b62cf1 | VP-5 | 1 | 10.23 | 0.0551 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F03-c-S1c-VP-5-ce2933b62cf1_seed1.mcap |
| PP-SWR-100 | SG-04 | F06-a-S1c-VP-0-4e752ad53686 | VP-0 | 1 | 9.108 | 0.08921 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-a-S1c-VP-0-4e752ad53686_seed1.mcap |
| PP-SWR-100 | SG-04 | F06-a-S1c-VP-0-aed66d9b07f6 | VP-0 | 1 | 17.23 | 0.07644 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-a-S1c-VP-0-aed66d9b07f6_seed1.mcap |
| PP-SWR-100 | SG-04 | F06-b-S1c-VP-0-d617705779af | VP-0 | 1 | 15.21 | 0.08286 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-b-S1c-VP-0-d617705779af_seed1.mcap |
| PP-SWR-100 | SG-04 | F06-b-S1c-VP-1-6a696f8d0446 | VP-1 | 1 | 15.21 | 0.08268 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-b-S1c-VP-1-6a696f8d0446_seed1.mcap |
| PP-SWR-100 | SG-04 | F06-b-S1c-VP-5-545957874102 | VP-5 | 1 | 15.21 | 0.08239 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-b-S1c-VP-5-545957874102_seed1.mcap |
| PP-SWR-100 | SG-04 | F06-d-S1c-VP-0-608ec3b8fc9f | VP-0 | 1 | 17.23 | 0.07644 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-d-S1c-VP-0-608ec3b8fc9f_seed1.mcap |
| PP-SWR-100 | SG-04 | F06-d-S1c-VP-1-40397bd3efa4 | VP-1 | 1 | 17.18 | 0.07372 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-d-S1c-VP-1-40397bd3efa4_seed1.mcap |
| PP-SWR-100 | SG-04 | F06-d-S1c-VP-5-bdab3c9103b7 | VP-5 | 1 | 17.28 | 0.08581 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-d-S1c-VP-5-bdab3c9103b7_seed1.mcap |
| PP-SWR-100 | SG-04 | F06-e-S1c-VP-0-21907f19a036 | VP-0 | 1 | 9.108 | 0.08921 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-e-S1c-VP-0-21907f19a036_seed1.mcap |
| PP-SWR-100 | SG-04 | F06-e-S1c-VP-1-1f3d70de82c2 | VP-1 | 1 | 9.108 | 0.08935 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-e-S1c-VP-1-1f3d70de82c2_seed1.mcap |
| PP-SWR-100 | SG-04 | F06-e-S1c-VP-5-87266b531a26 | VP-5 | 1 | 9.108 | 0.08895 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-e-S1c-VP-5-87266b531a26_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-a-S1c-VP-0-4efddd649b2a | VP-0 | 1 | 21.38 | 0.08404 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-a-S1c-VP-0-4efddd649b2a_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-a-S1c-VP-0-9d836e616214 | VP-0 | 1 | 21.38 | 0.08404 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-a-S1c-VP-0-9d836e616214_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-a-S1c-VP-1-9f6496a368b0 | VP-1 | 1 | 21.38 | 0.08381 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-a-S1c-VP-1-9f6496a368b0_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-a-S1c-VP-1-c098420638d4 | VP-1 | 1 | 21.38 | 0.08381 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-a-S1c-VP-1-c098420638d4_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-a-S1c-VP-5-5d6c59c69cbe | VP-5 | 1 | 21.38 | 0.08412 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-a-S1c-VP-5-5d6c59c69cbe_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-a-S1c-VP-5-dce61f599c6e | VP-5 | 1 | 21.38 | 0.08412 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-a-S1c-VP-5-dce61f599c6e_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-c-S1a-VP-0-e8ee89e39225 | VP-0 | 1 | 5.608 | 0.07296 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-c-S1a-VP-0-e8ee89e39225_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-c-S1a-VP-1-1657cdf8bd31 | VP-1 | 1 | 5.508 | 0.07302 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-c-S1a-VP-1-1657cdf8bd31_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-c-S1a-VP-5-f71d325809b3 | VP-5 | 1 | 5.608 | 0.0729 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-c-S1a-VP-5-f71d325809b3_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-c-S1c-VP-0-bca0f1afb997 | VP-0 | 1 | 5.208 | 0.07176 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-c-S1c-VP-0-bca0f1afb997_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-c-S1c-VP-1-3d8334644eea | VP-1 | 1 | 5.158 | 0.07195 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-c-S1c-VP-1-3d8334644eea_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-c-S1c-VP-5-06d7bb8fda8b | VP-5 | 1 | 5.158 | 0.07173 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F08-c-S1c-VP-5-06d7bb8fda8b_seed1.mcap |
| PP-SWR-100 | SG-04 | G01-S1c-VP-0-1467a0e9844f | VP-0 | 1 | 9.483 | 0.08964 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S1c-VP-0-1467a0e9844f_seed1.mcap |
| PP-SWR-100 | SG-04 | G01-S1c-VP-0-1467a0e9844f | VP-0 | 2 | 9.415 | 0.07733 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S1c-VP-0-1467a0e9844f_seed2.mcap |
| PP-SWR-100 | SG-04 | G01-S1c-VP-1-15c9123704b8 | VP-1 | 1 | 9.483 | 0.08789 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S1c-VP-1-15c9123704b8_seed1.mcap |
| PP-SWR-100 | SG-04 | G01-S1c-VP-1-15c9123704b8 | VP-1 | 2 | 9.44 | 0.0794 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S1c-VP-1-15c9123704b8_seed2.mcap |
| PP-SWR-100 | SG-04 | G01-S1c-VP-2-b56ea41bbee2 | VP-2 | 1 | 9.483 | 0.08938 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S1c-VP-2-b56ea41bbee2_seed1.mcap |
| PP-SWR-100 | SG-04 | G01-S1c-VP-2-b56ea41bbee2 | VP-2 | 2 | 9.415 | 0.07658 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S1c-VP-2-b56ea41bbee2_seed2.mcap |
| PP-SWR-100 | SG-04 | G01-S1c-VP-3-0970d8d23b03 | VP-3 | 1 | 9.483 | 0.08975 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S1c-VP-3-0970d8d23b03_seed1.mcap |
| PP-SWR-100 | SG-04 | G01-S1c-VP-3-0970d8d23b03 | VP-3 | 2 | 9.415 | 0.07755 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S1c-VP-3-0970d8d23b03_seed2.mcap |
| PP-SWR-100 | SG-04 | G01-S1c-VP-4-e79aef633429 | VP-4 | 1 | 9.483 | 0.09038 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S1c-VP-4-e79aef633429_seed1.mcap |
| PP-SWR-100 | SG-04 | G01-S1c-VP-4-e79aef633429 | VP-4 | 2 | 9.415 | 0.07726 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S1c-VP-4-e79aef633429_seed2.mcap |
| PP-SWR-100 | SG-04 | G01-S1c-VP-5-38898514a806 | VP-5 | 1 | 9.483 | 0.09038 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S1c-VP-5-38898514a806_seed1.mcap |
| PP-SWR-100 | SG-04 | G01-S1c-VP-5-38898514a806 | VP-5 | 2 | 9.415 | 0.07726 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S1c-VP-5-38898514a806_seed2.mcap |
| PP-SWR-100 | SG-04 | S12-a-VP-0-090a7e9db19e | VP-0 | 1 | 9.359 | 0.08798 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-a-VP-0-090a7e9db19e_seed1.mcap |
| PP-SWR-100 | SG-04 | S12-a-VP-0-090a7e9db19e | VP-0 | 2 | 9.326 | 0.07927 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-a-VP-0-090a7e9db19e_seed2.mcap |
| PP-SWR-100 | SG-04 | S12-a-VP-0-2b37570aa966 | VP-0 | 1 | 9.359 | 0.08798 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-a-VP-0-2b37570aa966_seed1.mcap |
| PP-SWR-100 | SG-04 | S12-a-VP-0-2b37570aa966 | VP-0 | 2 | 9.326 | 0.07927 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-a-VP-0-2b37570aa966_seed2.mcap |
| PP-SWR-100 | SG-04 | S12-a-VP-0-feba146e418f | VP-0 | 1 | 9.359 | 0.08798 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-a-VP-0-feba146e418f_seed1.mcap |
| PP-SWR-100 | SG-04 | S12-a-VP-0-feba146e418f | VP-0 | 2 | 9.326 | 0.07927 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-a-VP-0-feba146e418f_seed2.mcap |
| PP-SWR-100 | SG-04 | S12-a-VP-1-f78fa9197785 | VP-1 | 1 | 9.359 | 0.0889 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-a-VP-1-f78fa9197785_seed1.mcap |
| PP-SWR-100 | SG-04 | S12-a-VP-1-f78fa9197785 | VP-1 | 2 | 9.326 | 0.08598 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-a-VP-1-f78fa9197785_seed2.mcap |
| PP-SWR-100 | SG-04 | S12-a-VP-2-748f36869259 | VP-2 | 1 | 9.359 | 0.08816 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-a-VP-2-748f36869259_seed1.mcap |
| PP-SWR-100 | SG-04 | S12-a-VP-2-748f36869259 | VP-2 | 2 | 9.326 | 0.07927 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-a-VP-2-748f36869259_seed2.mcap |
| PP-SWR-100 | SG-04 | S12-a-VP-3-48c884c3f7fc | VP-3 | 1 | 9.359 | 0.08792 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-a-VP-3-48c884c3f7fc_seed1.mcap |
| PP-SWR-100 | SG-04 | S12-a-VP-3-48c884c3f7fc | VP-3 | 2 | 9.326 | 0.07927 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-a-VP-3-48c884c3f7fc_seed2.mcap |
| PP-SWR-100 | SG-04 | S12-a-VP-4-e0fb234e6632 | VP-4 | 1 | 9.359 | 0.08771 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-a-VP-4-e0fb234e6632_seed1.mcap |
| PP-SWR-100 | SG-04 | S12-a-VP-4-e0fb234e6632 | VP-4 | 2 | 9.351 | 0.08494 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-a-VP-4-e0fb234e6632_seed2.mcap |
| PP-SWR-100 | SG-04 | S12-a-VP-5-e7c93cf1d873 | VP-5 | 1 | 9.359 | 0.08771 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-a-VP-5-e7c93cf1d873_seed1.mcap |
| PP-SWR-100 | SG-04 | S12-a-VP-5-e7c93cf1d873 | VP-5 | 2 | 9.351 | 0.08494 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-a-VP-5-e7c93cf1d873_seed2.mcap |
| PP-SWR-100 | SG-04 | S12-d-VP-0-aa6a4007e24f | VP-0 | 1 | 0.202 | 0.09038 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-d-VP-0-aa6a4007e24f_seed1.mcap |
| PP-SWR-100 | SG-04 | S12-d-VP-0-aa6a4007e24f | VP-0 | 2 | 0.213 | 0.09451 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-d-VP-0-aa6a4007e24f_seed2.mcap |
| PP-SWR-100 | SG-04 | S12-d-VP-1-32e05ce9da2f | VP-1 | 1 | 0.202 | 0.09658 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-d-VP-1-32e05ce9da2f_seed1.mcap |
| PP-SWR-100 | SG-04 | S12-d-VP-1-32e05ce9da2f | VP-1 | 2 | 0.213 | 0.09083 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-d-VP-1-32e05ce9da2f_seed2.mcap |
| PP-SWR-100 | SG-04 | S12-d-VP-2-f8db4bffd193 | VP-2 | 1 | 0.202 | 0.1052 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-d-VP-2-f8db4bffd193_seed1.mcap |
| PP-SWR-100 | SG-04 | S12-d-VP-2-f8db4bffd193 | VP-2 | 2 | 0.213 | 0.09955 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-d-VP-2-f8db4bffd193_seed2.mcap |
| PP-SWR-100 | SG-04 | S12-d-VP-3-0739ffa64fa8 | VP-3 | 1 | 0.202 | 0.09795 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-d-VP-3-0739ffa64fa8_seed1.mcap |
| PP-SWR-100 | SG-04 | S12-d-VP-3-0739ffa64fa8 | VP-3 | 2 | 0.213 | 0.09624 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-d-VP-3-0739ffa64fa8_seed2.mcap |
| PP-SWR-100 | SG-04 | S12-d-VP-4-6c8c429307ff | VP-4 | 1 | 0.202 | 0.09856 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-d-VP-4-6c8c429307ff_seed1.mcap |
| PP-SWR-100 | SG-04 | S12-d-VP-4-6c8c429307ff | VP-4 | 2 | 0.213 | 0.09747 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-d-VP-4-6c8c429307ff_seed2.mcap |
| PP-SWR-100 | SG-04 | S12-d-VP-5-6c4d792cde2a | VP-5 | 1 | 0.202 | 0.09358 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-d-VP-5-6c4d792cde2a_seed1.mcap |
| PP-SWR-100 | SG-04 | S12-d-VP-5-6c4d792cde2a | VP-5 | 2 | 0.213 | 0.1063 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-d-VP-5-6c4d792cde2a_seed2.mcap |
| PP-SWR-100 | SG-04 | S14-a-VP-0-3290c39907ee | VP-0 | 1 | 2.858 | 0.05247 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-a-VP-0-3290c39907ee_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-a-VP-0-cabfa230312d | VP-0 | 1 | 2.858 | 0.05712 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-a-VP-0-cabfa230312d_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-c-VP-0-c8e86866eeb2 | VP-0 | 1 | 12.36 | 0.141 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-c-VP-0-c8e86866eeb2_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-c-VP-1-ffd30cdab212 | VP-1 | 1 | 12.36 | 0.1403 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-c-VP-1-ffd30cdab212_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-c-VP-2-51734930fc19 | VP-2 | 1 | 12.36 | 0.1404 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-c-VP-2-51734930fc19_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-c-VP-3-cbd4381d8311 | VP-3 | 1 | 12.36 | 0.1404 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-c-VP-3-cbd4381d8311_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-c-VP-4-5cb1a6c30767 | VP-4 | 1 | 12.36 | 0.1404 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-c-VP-4-5cb1a6c30767_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-c-VP-5-1c80d628c800 | VP-5 | 1 | 12.36 | 0.1404 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-c-VP-5-1c80d628c800_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-0-dc72ffbcfa45 | VP-0 | 1 | 3.558 | 0.06703 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-0-dc72ffbcfa45_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-0-ff8e4ce04140 | VP-0 | 1 | 3.583 | 0.05641 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-0-ff8e4ce04140_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-1-9e894e6e0e47 | VP-1 | 1 | 3.558 | 0.0672 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-1-9e894e6e0e47_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-1-c599c50726eb | VP-1 | 1 | 3.583 | 0.05648 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-1-c599c50726eb_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-2-8ea25fd5bd76 | VP-2 | 1 | 3.558 | 0.0672 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-2-8ea25fd5bd76_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-2-d2cc20ee8bbf | VP-2 | 1 | 3.583 | 0.05643 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-2-d2cc20ee8bbf_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-3-24dcd5adb2de | VP-3 | 1 | 3.583 | 0.0564 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-3-24dcd5adb2de_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-3-5cf328ad0176 | VP-3 | 1 | 3.558 | 0.06703 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-3-5cf328ad0176_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-4-a571d2de589d | VP-4 | 1 | 3.583 | 0.05637 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-4-a571d2de589d_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-4-f51e1424afde | VP-4 | 1 | 3.558 | 0.06702 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-4-f51e1424afde_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-5-3f2b28b63f2e | VP-5 | 1 | 3.583 | 0.05637 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-5-3f2b28b63f2e_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-5-845fd11edffe | VP-5 | 1 | 3.558 | 0.06702 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-5-845fd11edffe_seed1.mcap |
| PP-SWR-100 | SG-04 | S1b-a-VP-0-693b15015bfa | VP-0 | 1 | 2.858 | 0.05247 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S1b-a-VP-0-693b15015bfa_seed1.mcap |
| PP-SWR-101 | SG-04 | F06-b-S1c-VP-0-d617705779af | VP-0 | 1 | 15.26 | 0.005008 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-b-S1c-VP-0-d617705779af_seed1.mcap |
| PP-SWR-101 | SG-04 | F06-b-S1c-VP-1-6a696f8d0446 | VP-1 | 1 | 15.26 | 0.00501 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-b-S1c-VP-1-6a696f8d0446_seed1.mcap |
| PP-SWR-101 | SG-04 | S14-c-VP-0-c8e86866eeb2 | VP-0 | 1 | 8.559 | 0.01056 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-c-VP-0-c8e86866eeb2_seed1.mcap |
| PP-SWR-101 | SG-04 | S14-c-VP-1-ffd30cdab212 | VP-1 | 1 | 8.559 | 0.01062 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-c-VP-1-ffd30cdab212_seed1.mcap |
| PP-SWR-101 | SG-04 | S14-c-VP-2-51734930fc19 | VP-2 | 1 | 8.559 | 0.01062 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-c-VP-2-51734930fc19_seed1.mcap |
| PP-SWR-101 | SG-04 | S14-c-VP-3-cbd4381d8311 | VP-3 | 1 | 8.559 | 0.01062 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-c-VP-3-cbd4381d8311_seed1.mcap |
| PP-SWR-101 | SG-04 | S14-c-VP-4-5cb1a6c30767 | VP-4 | 1 | 8.559 | 0.01061 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-c-VP-4-5cb1a6c30767_seed1.mcap |
| PP-SWR-101 | SG-04 | S14-c-VP-5-1c80d628c800 | VP-5 | 1 | 8.559 | 0.01061 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-c-VP-5-1c80d628c800_seed1.mcap |
| PP-SWR-101 | SG-04 | S14-e-VP-0-dc72ffbcfa45 | VP-0 | 1 | 6.908 | 0.005531 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-0-dc72ffbcfa45_seed1.mcap |
| PP-SWR-101 | SG-04 | S14-e-VP-1-9e894e6e0e47 | VP-1 | 1 | 6.808 | 0.005125 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-1-9e894e6e0e47_seed1.mcap |
| PP-SWR-101 | SG-04 | S14-e-VP-2-8ea25fd5bd76 | VP-2 | 1 | 6.908 | 0.005531 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-2-8ea25fd5bd76_seed1.mcap |
| PP-SWR-101 | SG-04 | S14-e-VP-3-5cf328ad0176 | VP-3 | 1 | 6.908 | 0.005531 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-3-5cf328ad0176_seed1.mcap |
| PP-SWR-101 | SG-04 | S14-e-VP-4-f51e1424afde | VP-4 | 1 | 6.908 | 0.00553 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-4-f51e1424afde_seed1.mcap |
| PP-SWR-101 | SG-04 | S14-e-VP-5-845fd11edffe | VP-5 | 1 | 6.908 | 0.00553 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-5-845fd11edffe_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-c-VP-0-c8e86866eeb2 | VP-0 | 1 | 8.559 | 0.000619 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-c-VP-0-c8e86866eeb2_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-c-VP-1-ffd30cdab212 | VP-1 | 1 | 8.559 | 0.0006151 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-c-VP-1-ffd30cdab212_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-c-VP-2-51734930fc19 | VP-2 | 1 | 8.559 | 0.000613 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-c-VP-2-51734930fc19_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-c-VP-3-cbd4381d8311 | VP-3 | 1 | 8.559 | 0.0006127 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-c-VP-3-cbd4381d8311_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-c-VP-4-5cb1a6c30767 | VP-4 | 1 | 8.559 | 0.0006125 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-c-VP-4-5cb1a6c30767_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-c-VP-5-1c80d628c800 | VP-5 | 1 | 8.559 | 0.0006125 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-c-VP-5-1c80d628c800_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-e-VP-0-dc72ffbcfa45 | VP-0 | 1 | 6.858 | 0.0003097 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-0-dc72ffbcfa45_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-e-VP-2-8ea25fd5bd76 | VP-2 | 1 | 6.858 | 0.0003095 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-2-8ea25fd5bd76_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-e-VP-3-5cf328ad0176 | VP-3 | 1 | 6.858 | 0.0003097 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-3-5cf328ad0176_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-e-VP-4-f51e1424afde | VP-4 | 1 | 6.858 | 0.0003095 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-4-f51e1424afde_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-e-VP-5-845fd11edffe | VP-5 | 1 | 6.858 | 0.0003095 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S14-e-VP-5-845fd11edffe_seed1.mcap |
| PP-SWR-130 | — | F15-b-S1a-VP-0-33530d9bbe5f | VP-0 | 1 | 4.133 | 939 | = 0 | Chu kỳ output khác ca tham chiếu cùng seed | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F15-b-S1a-VP-0-33530d9bbe5f_seed1.mcap |
| PP-SWR-130 | — | F15-b-S1a-VP-1-9b183f83f348 | VP-1 | 1 | 4.133 | 939 | = 0 | Chu kỳ output khác ca tham chiếu cùng seed | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F15-b-S1a-VP-1-9b183f83f348_seed1.mcap |
| PP-SWR-130 | — | F15-b-S1a-VP-5-2b2847c2db5e | VP-5 | 1 | 4.133 | 939 | = 0 | Chu kỳ output khác ca tham chiếu cùng seed | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F15-b-S1a-VP-5-2b2847c2db5e_seed1.mcap |
| PP-SWR-130 | — | F15-b-S1c-VP-0-53e5a23843eb | VP-0 | 1 | 4.133 | 699 | = 0 | Chu kỳ output khác ca tham chiếu cùng seed | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F15-b-S1c-VP-0-53e5a23843eb_seed1.mcap |
| PP-SWR-130 | — | F15-b-S1c-VP-1-12fd4e186c3d | VP-1 | 1 | 4.133 | 699 | = 0 | Chu kỳ output khác ca tham chiếu cùng seed | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F15-b-S1c-VP-1-12fd4e186c3d_seed1.mcap |
| PP-SWR-130 | — | F15-b-S1c-VP-5-06d5c0323b74 | VP-5 | 1 | 4.133 | 699 | = 0 | Chu kỳ output khác ca tham chiếu cùng seed | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F15-b-S1c-VP-5-06d5c0323b74_seed1.mcap |
| PP-SWR-130 | — | F15-c-S1a-VP-0-1759e7623f79 | VP-0 | 1 | 4.133 | 955 | = 0 | Chu kỳ output khác ca tham chiếu cùng seed | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F15-c-S1a-VP-0-1759e7623f79_seed1.mcap |
| PP-SWR-130 | — | F15-c-S1a-VP-1-ee83c26fa37b | VP-1 | 1 | 4.133 | 955 | = 0 | Chu kỳ output khác ca tham chiếu cùng seed | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F15-c-S1a-VP-1-ee83c26fa37b_seed1.mcap |
| PP-SWR-130 | — | F15-c-S1a-VP-5-36b99b375e24 | VP-5 | 1 | 4.133 | 955 | = 0 | Chu kỳ output khác ca tham chiếu cùng seed | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F15-c-S1a-VP-5-36b99b375e24_seed1.mcap |
| PP-SWR-130 | — | F15-c-S1c-VP-0-10538de9a5b7 | VP-0 | 1 | 4.133 | 715 | = 0 | Chu kỳ output khác ca tham chiếu cùng seed | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F15-c-S1c-VP-0-10538de9a5b7_seed1.mcap |
| PP-SWR-130 | — | F15-c-S1c-VP-1-768b8651648e | VP-1 | 1 | 4.133 | 715 | = 0 | Chu kỳ output khác ca tham chiếu cùng seed | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F15-c-S1c-VP-1-768b8651648e_seed1.mcap |
| PP-SWR-130 | — | F15-c-S1c-VP-5-8bd5e66f138e | VP-5 | 1 | 4.133 | 715 | = 0 | Chu kỳ output khác ca tham chiếu cùng seed | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F15-c-S1c-VP-5-8bd5e66f138e_seed1.mcap |

## Trượt MINOR

| Requirement | Safety goal | Ca | Profile | Seed | Trượt đầu tiên [s] | Giá trị | Ngưỡng | Chi tiết | MCAP |
|---|---|---|---|---|---|---|---|---|---|
| PP-SWR-032 | — | F01-a-S4a_at_lka_activep0-VP-0-c97d4f8c3b33 | VP-0 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-a-S4a_at_lka_activep0-VP-0-c97d4f8c3b33_seed1.mcap |
| PP-SWR-032 | — | F01-a-S4a_at_lka_activep0-VP-0-c97d4f8c3b33 | VP-0 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-a-S4a_at_lka_activep0-VP-0-c97d4f8c3b33_seed2.mcap |
| PP-SWR-032 | — | F01-a-S4a_at_lka_activep0.2-VP-1-349f439b63ca | VP-1 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-a-S4a_at_lka_activep0.2-VP-1-349f439b63ca_seed2.mcap |
| PP-SWR-032 | — | F01-a-S5a_at_elk_activep0-VP-0-3d5c8cbcdab8 | VP-0 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-a-S5a_at_elk_activep0-VP-0-3d5c8cbcdab8_seed1.mcap |
| PP-SWR-032 | — | F01-a-S5a_at_elk_activep0.2-VP-1-44c9a8a8a61d | VP-1 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-a-S5a_at_elk_activep0.2-VP-1-44c9a8a8a61d_seed1.mcap |
| PP-SWR-032 | — | F01-a-S5a_at_elk_activep0.2-VP-1-44c9a8a8a61d | VP-1 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-a-S5a_at_elk_activep0.2-VP-1-44c9a8a8a61d_seed2.mcap |
| PP-SWR-032 | — | F01-b-S4a_at_lka_activep0-VP-2-26b730c60966 | VP-2 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-b-S4a_at_lka_activep0-VP-2-26b730c60966_seed1.mcap |
| PP-SWR-032 | — | F01-b-S4a_at_lka_activep0-VP-2-26b730c60966 | VP-2 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-b-S4a_at_lka_activep0-VP-2-26b730c60966_seed2.mcap |
| PP-SWR-032 | — | F01-b-S4a_at_lka_activep0.2-VP-3-7e4bb0e3caed | VP-3 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-b-S4a_at_lka_activep0.2-VP-3-7e4bb0e3caed_seed1.mcap |
| PP-SWR-032 | — | F01-b-S4a_at_lka_activep0.2-VP-3-7e4bb0e3caed | VP-3 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-b-S4a_at_lka_activep0.2-VP-3-7e4bb0e3caed_seed2.mcap |
| PP-SWR-032 | — | F01-b-S5a_at_elk_activep0-VP-2-795bfb495e44 | VP-2 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-b-S5a_at_elk_activep0-VP-2-795bfb495e44_seed1.mcap |
| PP-SWR-032 | — | F01-b-S5a_at_elk_activep0.2-VP-3-43bbc0fa0b87 | VP-3 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-b-S5a_at_elk_activep0.2-VP-3-43bbc0fa0b87_seed1.mcap |
| PP-SWR-032 | — | F01-b-S5a_at_elk_activep0.2-VP-3-43bbc0fa0b87 | VP-3 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-b-S5a_at_elk_activep0.2-VP-3-43bbc0fa0b87_seed2.mcap |
| PP-SWR-032 | — | F01-c-S4a_at_lka_activep0-VP-4-914355537c7d | VP-4 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-c-S4a_at_lka_activep0-VP-4-914355537c7d_seed1.mcap |
| PP-SWR-032 | — | F01-c-S4a_at_lka_activep0-VP-4-914355537c7d | VP-4 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-c-S4a_at_lka_activep0-VP-4-914355537c7d_seed2.mcap |
| PP-SWR-032 | — | F01-c-S4a_at_lka_activep0.2-VP-5-2e109dc103db | VP-5 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-c-S4a_at_lka_activep0.2-VP-5-2e109dc103db_seed1.mcap |
| PP-SWR-032 | — | F01-c-S4a_at_lka_activep0.2-VP-5-2e109dc103db | VP-5 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-c-S4a_at_lka_activep0.2-VP-5-2e109dc103db_seed2.mcap |
| PP-SWR-032 | — | F01-c-S5a_at_elk_activep0-VP-4-d7e0b59fbf4d | VP-4 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-c-S5a_at_elk_activep0-VP-4-d7e0b59fbf4d_seed1.mcap |
| PP-SWR-032 | — | F01-c-S5a_at_elk_activep0-VP-4-d7e0b59fbf4d | VP-4 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-c-S5a_at_elk_activep0-VP-4-d7e0b59fbf4d_seed2.mcap |
| PP-SWR-032 | — | F01-c-S5a_at_elk_activep0.2-VP-5-fbea90d7d4d0 | VP-5 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-c-S5a_at_elk_activep0.2-VP-5-fbea90d7d4d0_seed1.mcap |
| PP-SWR-032 | — | F01-c-S5a_at_elk_activep0.2-VP-5-fbea90d7d4d0 | VP-5 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F01-c-S5a_at_elk_activep0.2-VP-5-fbea90d7d4d0_seed2.mcap |
| PP-SWR-032 | — | F06-a-S4a_at_lka_activep0-VP-0-807dfa5e3c00 | VP-0 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-a-S4a_at_lka_activep0-VP-0-807dfa5e3c00_seed1.mcap |
| PP-SWR-032 | — | F06-d-S4a_at_lka_activep0-VP-0-a65c5296268d | VP-0 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-d-S4a_at_lka_activep0-VP-0-a65c5296268d_seed1.mcap |
| PP-SWR-032 | — | F06-e-S4a_at_lka_activep0-VP-2-268a3c31c9ee | VP-2 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F06-e-S4a_at_lka_activep0-VP-2-268a3c31c9ee_seed1.mcap |
| PP-SWR-032 | — | G01-S4c-VP-0-944a5944b2f0 | VP-0 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S4c-VP-0-944a5944b2f0_seed1.mcap |
| PP-SWR-032 | — | G01-S4c-VP-0-944a5944b2f0 | VP-0 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S4c-VP-0-944a5944b2f0_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-1-d9c02f4d85c9 | VP-1 | 1 | — | 4 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S4c-VP-1-d9c02f4d85c9_seed1.mcap |
| PP-SWR-032 | — | G01-S4c-VP-1-d9c02f4d85c9 | VP-1 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S4c-VP-1-d9c02f4d85c9_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-2-19b08e51426b | VP-2 | 1 | — | 3 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S4c-VP-2-19b08e51426b_seed1.mcap |
| PP-SWR-032 | — | G01-S4c-VP-2-19b08e51426b | VP-2 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S4c-VP-2-19b08e51426b_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-3-9991783c316d | VP-3 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S4c-VP-3-9991783c316d_seed1.mcap |
| PP-SWR-032 | — | G01-S4c-VP-3-9991783c316d | VP-3 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S4c-VP-3-9991783c316d_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-4-072664ac9b98 | VP-4 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S4c-VP-4-072664ac9b98_seed1.mcap |
| PP-SWR-032 | — | G01-S4c-VP-4-072664ac9b98 | VP-4 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S4c-VP-4-072664ac9b98_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-5-26df2868e70c | VP-5 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S4c-VP-5-26df2868e70c_seed1.mcap |
| PP-SWR-032 | — | G01-S4c-VP-5-26df2868e70c | VP-5 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/G01-S4c-VP-5-26df2868e70c_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-0-69e53aeef11a | VP-0 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-b-VP-0-69e53aeef11a_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-0-69e53aeef11a | VP-0 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-b-VP-0-69e53aeef11a_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-1-4b3e70a50a26 | VP-1 | 1 | — | 2 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-b-VP-1-4b3e70a50a26_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-1-4b3e70a50a26 | VP-1 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-b-VP-1-4b3e70a50a26_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-2-0962daddf5bd | VP-2 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-b-VP-2-0962daddf5bd_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-2-0962daddf5bd | VP-2 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-b-VP-2-0962daddf5bd_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-3-984dbaa7f733 | VP-3 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-b-VP-3-984dbaa7f733_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-3-984dbaa7f733 | VP-3 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-b-VP-3-984dbaa7f733_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-4-a4945d3bcd67 | VP-4 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-b-VP-4-a4945d3bcd67_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-4-a4945d3bcd67 | VP-4 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-b-VP-4-a4945d3bcd67_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-5-2b777db332c0 | VP-5 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-b-VP-5-2b777db332c0_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-5-2b777db332c0 | VP-5 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S12-b-VP-5-2b777db332c0_seed2.mcap |
| PP-SWR-032 | — | S13-a-VP-5-4d54367ca2b0 | VP-5 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S13-a-VP-5-4d54367ca2b0_seed1.mcap |
| PP-SWR-032 | — | S13-c-VP-2-b3cfb16c6452 | VP-2 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED tại tick đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S13-c-VP-2-b3cfb16c6452_seed1.mcap |
| PP-SWR-090 | — | F02-e-S5a_at_elk_activep0.2-VP-3-bb766866f0d0 | VP-3 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/F02-e-S5a_at_elk_activep0.2-VP-3-bb766866f0d0_seed1.mcap |
| PP-SWR-090 | — | S5-c-VP-5-fc8939d6aa80 | VP-5 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/benchmark/20261114-1020-regression-d7ed84c/suite/mcap/S5-c-VP-5-fc8939d6aa80_seed1.mcap |

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
| BLOCKER | PP-SWR-006 | S14-e-VP-0-dc72ffbcfa45 | 1 | -1.503 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-1-c599c50726eb | 1 | -1.675 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-1-9e894e6e0e47 | 1 | -1.478 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-2-d2cc20ee8bbf | 1 | -1.675 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-2-8ea25fd5bd76 | 1 | -1.498 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-3-24dcd5adb2de | 1 | -1.593 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-3-5cf328ad0176 | 1 | -1.503 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-4-a571d2de589d | 1 | -1.57 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-4-f51e1424afde | 1 | -1.502 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-5-3f2b28b63f2e | 1 | -1.57 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-e-VP-5-845fd11edffe | 1 | -1.502 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-0-cabfa230312d | 1 | -0.243 | >= 0 |
| BLOCKER | PP-SWR-005 | S14-a-VP-0-3290c39907ee | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-0-3290c39907ee | 1 | -0.143 | >= 0 |
| MINOR | PP-SWR-032 | S4b-a-VP-3-72c20a1b5b5d | 1 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S4b-b-VP-0-c5137f12c89c | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S4b-b-VP-1-311647f45960 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S4b-b-VP-2-283a89ab5801 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S4b-b-VP-3-38f48e10cf5d | 1 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S4b-b-VP-5-085d11c4256e | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S4b-b-VP-5-085d11c4256e | 1 | 1 | = 0 |
| MINOR | PP-SWR-090 | S4b-c-VP-0-5f3bb8bbbdcc | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S4b-c-VP-1-6341e6253ac1 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S4b-c-VP-2-f89a9a0c7f96 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S4b-c-VP-3-23a7856ac085 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S4b-c-VP-4-f876104a11e9 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S4b-c-VP-5-e35d853524b2 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S4b-c-VP-5-e35d853524b2 | 1 | 1 | = 0 |
| MINOR | PP-SWR-090 | S4b-e-VP-0-3c6fbd348bdd | 1 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S4b-e-VP-1-fd25b44661ad | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S4b-e-VP-2-8664d4326faa | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S4b-e-VP-3-bc1154b2eab4 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S4b-e-VP-4-ee510703be24 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S4b-e-VP-5-92e694b699d0 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S4b-e-VP-5-92e694b699d0 | 1 | 1 | = 0 |
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
| BLOCKER | PP-SWR-051 | S17-a-VP-5-b494108de31a | 1 | -0.2419 | >= 0 |
| MINOR | PP-SWR-062 | S17-a-VP-5-b494108de31a | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-051 | S17-b-VP-0-3de8f33b03db | 1 | -0.01948 | >= 0 |
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
| BLOCKER | PP-SWR-061 | F03-c-S1c-VP-0-0e2929c3df25 | 1 | 0.05577 | <= 0.05 |
| BLOCKER | PP-SWR-061 | F03-c-S1c-VP-1-4278b1e68610 | 1 | 0.06217 | <= 0.05 |
| BLOCKER | PP-SWR-061 | F03-c-S1c-VP-5-ce2933b62cf1 | 1 | 0.0551 | <= 0.05 |
| BLOCKER | PP-SWR-061 | F06-d-S1c-VP-0-608ec3b8fc9f | 1 | 0.07644 | <= 0.05 |
| BLOCKER | PP-SWR-061 | F06-d-S1c-VP-1-40397bd3efa4 | 1 | 0.07372 | <= 0.05 |
| BLOCKER | PP-SWR-061 | F06-d-S1c-VP-5-bdab3c9103b7 | 1 | 0.08581 | <= 0.05 |
| BLOCKER | PP-SWR-061 | F06-a-S1c-VP-0-aed66d9b07f6 | 1 | 0.07644 | <= 0.05 |
| BLOCKER | PP-SWR-061 | F08-a-S1c-VP-0-9d836e616214 | 1 | 0.06548 | <= 0.05 |
| BLOCKER | PP-SWR-061 | F08-a-S1c-VP-1-c098420638d4 | 1 | 0.06523 | <= 0.05 |
| BLOCKER | PP-SWR-061 | F08-a-S1c-VP-5-dce61f599c6e | 1 | 0.06556 | <= 0.05 |
| BLOCKER | PP-SWR-061 | F08-a-S1c-VP-0-4efddd649b2a | 1 | 0.06548 | <= 0.05 |
| BLOCKER | PP-SWR-061 | F08-a-S1c-VP-1-9f6496a368b0 | 1 | 0.06523 | <= 0.05 |
| BLOCKER | PP-SWR-061 | F08-a-S1c-VP-5-5d6c59c69cbe | 1 | 0.06556 | <= 0.05 |

## Bộ theo khía cạnh

| Bộ | Khía cạnh | Lần chạy | Kết luận | BLOCKER | MAJOR | MINOR |
|---|---|---|---|---|---|---|
| B0 | Conformance | — | Đạt C1, C2; Tích hợp được | — | — | — |
| B1 | Nominal | 922 | Không đạt | 5 | 0 | 1 |
| B2 | Regulatory | 594 | Không đạt | 29 | 0 | 0 |
| B3 | Performance limit | 289 | Không đạt | 55 | 0 | 2 |
| B4 | Robustness | 862 | Không đạt | 194 | 0 | 49 |
| B5 | Degradation and refusal | 306 | Không đạt | 61 | 0 | 0 |
| B6 | Comfort | 922 | Không đạt | 5 | 0 | 1 |
| B7 | Flexibility | 803 | Không đạt | 75 | 0 | 26 |
| B8 | Compute | 2073 | Không đạt | 254 | 0 | 52 |

## Số lần chạy

```json
{
 "planned": 2073,
 "executed": 2073,
 "failed": 216,
 "failed_out_of_scope": 112,
 "errors": 0,
 "execution_faults": 0,
 "partial": false
}
```

## Flexibility

Cùng bản build và bộ calibration trên mọi profile (mục 8.3). Ô là giá trị xấu nhất của profile trên các ca chạy đủ mọi profile; **đậm** là profile tệ nhất của chỉ số. Bộ chạy là B7. Tỉ lệ đạt requirement: số requirement không trượt ở lần chạy nào của profile, chia số requirement được chấm trên profile đó.

| Profile | Lần chạy | Tỉ lệ đạt requirement | Requirement trượt | PP-SWR-002 a_y thêm vào lớn nhất khi đưa về giữa | PP-SWR-004 Jerk ngang RMS của path 0–1 s khi HWA lái | PP-SWR-004 Jerk ngang lớn nhất của path khi HWA lái (trung bình 0,5 s) | PP-SWR-004 Tốc độ quay vô lăng RMS khi HWA lái, vòng kín | PP-SWR-050 Lệch ngang của path so với tâm làn thật, 0–1 s, lớn nhất | PP-SWR-053 Thời gian đưa xe về giữa (lệch ≤ 0,1 m) | PP-SWR-057 Khoảng cách ngang nhỏ nhất từ thân xe tới xe lớn khi ngang hàng | PP-SWR-059 Thời gian từ lúc hết ngang hàng tới lúc lệch ≤ 0,1 m | PP-SWR-081 Thời lượng path LKA tới COMPLETED | PP-SWR-082 Thời lượng path ELK tới COMPLETED | PP-SWR-087 DTLE LKA nhỏ nhất |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VP-0 | 210 | 86.2% | PP-SWR-032, PP-SWR-051, PP-SWR-100, PP-SWR-101 | 1.09 | 0.282 | 1.57 | 0.214 | **0.846** | 3.28 | 0.634 | 4.97 | 4.45 | 3.8 | -0.00941 |
| VP-1 | 145 | 86.7% | PP-SWR-032, PP-SWR-051, PP-SWR-100, PP-SWR-101 | **1.21** | **0.287** | **1.57** | 0.211 | 0.773 | 3.23 | 0.611 | **5.02** | 4.17 | 3.5 | 0.00715 |
| VP-2 | 103 | 96.8% | PP-SWR-032 | 1.12 | 0.282 | 1.57 | 0.213 | 0.841 | 3.25 | 0.531 | 5.02 | 4.38 | 3.75 | 0.00277 |
| VP-3 | 102 | 90.0% | PP-SWR-032, PP-SWR-085, PP-SWR-090 | 1.07 | 0.282 | 1.57 | 0.214 | 0.845 | **3.29** | 0.479 | 5 | 4.45 | 3.82 | -0.00949 |
| VP-4 | 102 | 96.7% | PP-SWR-032 | 1.06 | 0.282 | 1.57 | **0.215** | 0.845 | 3.06 | 0.452 | 5 | **4.52** | **3.88** | -0.00993 |
| VP-5 | 141 | 87.5% | PP-SWR-032, PP-SWR-051, PP-SWR-090, PP-SWR-100 | 1.06 | 0.282 | 1.57 | 0.215 | 0.845 | 3.06 | **0.326** | 4 | 4.52 | 3.88 | **-0.0221** |

| Chỉ số | Độ chênh lớn nhất giữa profile | Độ chênh nhỏ nhất | Profile tệ nhất |
|---|---|---|---|
| PP-SWR-002 a_y thêm vào lớn nhất khi đưa về giữa | 0.149 | 0 | VP-1 |
| PP-SWR-004 Jerk ngang RMS của path 0–1 s khi HWA lái | 0.0312 | 5.09e-06 | VP-1 |
| PP-SWR-004 Jerk ngang lớn nhất của path khi HWA lái (trung bình 0,5 s) | 0.242 | 0 | VP-1 |
| PP-SWR-004 Tốc độ quay vô lăng RMS khi HWA lái, vòng kín | 0.014 | 0.000705 | VP-4 |
| PP-SWR-050 Lệch ngang của path so với tâm làn thật, 0–1 s, lớn nhất | 0.0999 | 0 | VP-0 |
| PP-SWR-053 Thời gian đưa xe về giữa (lệch ≤ 0,1 m) | 2.29 | 0 | VP-3 |
| PP-SWR-057 Khoảng cách ngang nhỏ nhất từ thân xe tới xe lớn khi ngang hàng | 0.308 | 0.242 | VP-5 |
| PP-SWR-059 Thời gian từ lúc hết ngang hàng tới lúc lệch ≤ 0,1 m | 4.85 | 1.02 | VP-1 |
| PP-SWR-081 Thời lượng path LKA tới COMPLETED | 0.525 | 0 | VP-4 |
| PP-SWR-082 Thời lượng path ELK tới COMPLETED | 1.4 | 0 | VP-4 |
| PP-SWR-087 DTLE LKA nhỏ nhất | 0.117 | 0.00805 | VP-5 |

Requirement đạt 100 % trên mọi profile: không (VP-0, VP-1, VP-2, VP-3, VP-4, VP-5)

## Thời gian tính

1690210 chu kỳ. p95 ≤ 1.58 ms, p99 ≤ 3.16 ms (cận trên của bin), lớn nhất 475 ms. Đo trên máy chạy SIL, gồm adapter; không khẳng định thời gian trên ECU (mục 9.1).

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

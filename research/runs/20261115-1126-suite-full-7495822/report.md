# Kết luận: Không đạt

- Planner: pp_planner 0.2.0 commit 74958221c89e calibration d532993b1b2f t7 quintic (8e613387c923)
- Tích hợp được: có
- Đã chạy: 3958 lần chạy; trượt BLOCKER 262, MAJOR 0, MINOR 141
- Kết luận chỉ đúng trong phạm vi đã thử, không phải bằng chứng an toàn (Software Qualification Test Specification 3).

## Trượt BLOCKER

| Requirement | Safety goal | Ca | Profile | Seed | Trượt đầu tiên [s] | Giá trị | Ngưỡng | Chi tiết | MCAP |
|---|---|---|---|---|---|---|---|---|---|
| PP-SWR-005 | SG-02 | S1b-a-VP-0-2450cb59e335 | VP-0 | 1 | 8.008 | 1 | = 0 | Chu kỳ cua gắt mà mất path hoặc HWA | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-2450cb59e335_seed1.mcap |
| PP-SWR-005 | SG-02 | S1b-a-VP-0-45d39dd0be07 | VP-0 | 1 | 7.658 | 1 | = 0 | Chu kỳ cua gắt mà mất path hoặc HWA | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-45d39dd0be07_seed1.mcap |
| PP-SWR-005 | SG-02 | S1b-a-VP-0-66e9cbe67698 | VP-0 | 1 | 7.808 | 1 | = 0 | Chu kỳ cua gắt mà mất path hoặc HWA | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-66e9cbe67698_seed1.mcap |
| PP-SWR-005 | SG-02 | S1b-a-VP-0-693b15015bfa | VP-0 | 1 | 8.008 | 1 | = 0 | Chu kỳ cua gắt mà mất path hoặc HWA | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-693b15015bfa_seed1.mcap |
| PP-SWR-005 | SG-02 | S1b-a-VP-0-7594aab96ea3 | VP-0 | 1 | 7.858 | 1 | = 0 | Chu kỳ cua gắt mà mất path hoặc HWA | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-7594aab96ea3_seed1.mcap |
| PP-SWR-005 | SG-02 | S1b-a-VP-0-8a205ef6f957 | VP-0 | 1 | 8.208 | 1 | = 0 | Chu kỳ cua gắt mà mất path hoặc HWA | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-8a205ef6f957_seed1.mcap |
| PP-SWR-005 | SG-02 | S1b-a-VP-0-bc0ecb5fc06d | VP-0 | 1 | 8.008 | 1 | = 0 | Chu kỳ cua gắt mà mất path hoặc HWA | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-bc0ecb5fc06d_seed1.mcap |
| PP-SWR-005 | SG-02 | S1b-a-VP-1-44b94ef5689d | VP-1 | 1 | 8.008 | 1 | = 0 | Chu kỳ cua gắt mà mất path hoặc HWA | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-1-44b94ef5689d_seed1.mcap |
| PP-SWR-005 | SG-02 | S1b-a-VP-2-bdc9bcec7280 | VP-2 | 1 | 8.008 | 1 | = 0 | Chu kỳ cua gắt mà mất path hoặc HWA | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-2-bdc9bcec7280_seed1.mcap |
| PP-SWR-005 | SG-02 | S1b-a-VP-3-9b3e7230edb4 | VP-3 | 1 | 8.008 | 1 | = 0 | Chu kỳ cua gắt mà mất path hoặc HWA | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-3-9b3e7230edb4_seed1.mcap |
| PP-SWR-005 | SG-02 | S1b-a-VP-4-03713b6fc1cf | VP-4 | 1 | 8.008 | 1 | = 0 | Chu kỳ cua gắt mà mất path hoặc HWA | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-4-03713b6fc1cf_seed1.mcap |
| PP-SWR-005 | SG-02 | S1b-a-VP-5-9c970a207743 | VP-5 | 1 | 8.008 | 1 | = 0 | Chu kỳ cua gắt mà mất path hoặc HWA | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-5-9c970a207743_seed1.mcap |
| PP-SWR-006 | SG-02 | S1b-a-VP-0-2450cb59e335 | VP-0 | 1 | 3.958 | -0.1269 | >= 0 | a_y path trừ (aysmax − epsilon_ay), 0–1 s, khi a_y cần > aysmax [m/s²] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-2450cb59e335_seed1.mcap |
| PP-SWR-006 | SG-02 | S1b-a-VP-0-37cc782177e5 | VP-0 | 1 | 4.333 | -0.05664 | >= 0 | a_y path trừ (aysmax − epsilon_ay), 0–1 s, khi a_y cần > aysmax [m/s²] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-37cc782177e5_seed1.mcap |
| PP-SWR-006 | SG-02 | S1b-a-VP-0-45d39dd0be07 | VP-0 | 1 | 3.683 | -0.02864 | >= 0 | a_y path trừ (aysmax − epsilon_ay), 0–1 s, khi a_y cần > aysmax [m/s²] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-45d39dd0be07_seed1.mcap |
| PP-SWR-006 | SG-02 | S1b-a-VP-0-66e9cbe67698 | VP-0 | 1 | 4.058 | -0.02206 | >= 0 | a_y path trừ (aysmax − epsilon_ay), 0–1 s, khi a_y cần > aysmax [m/s²] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-66e9cbe67698_seed1.mcap |
| PP-SWR-006 | SG-02 | S1b-a-VP-0-693b15015bfa | VP-0 | 1 | 3.958 | -0.1269 | >= 0 | a_y path trừ (aysmax − epsilon_ay), 0–1 s, khi a_y cần > aysmax [m/s²] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-693b15015bfa_seed1.mcap |
| PP-SWR-006 | SG-02 | S1b-a-VP-0-7594aab96ea3 | VP-0 | 1 | 3.958 | -0.127 | >= 0 | a_y path trừ (aysmax − epsilon_ay), 0–1 s, khi a_y cần > aysmax [m/s²] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-7594aab96ea3_seed1.mcap |
| PP-SWR-006 | SG-02 | S1b-a-VP-0-8a205ef6f957 | VP-0 | 1 | 3.958 | -0.1268 | >= 0 | a_y path trừ (aysmax − epsilon_ay), 0–1 s, khi a_y cần > aysmax [m/s²] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-8a205ef6f957_seed1.mcap |
| PP-SWR-006 | SG-02 | S1b-a-VP-0-a4d17e6ba3b6 | VP-0 | 1 | 4.308 | -0.2619 | >= 0 | a_y path trừ (aysmax − epsilon_ay), 0–1 s, khi a_y cần > aysmax [m/s²] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-a4d17e6ba3b6_seed1.mcap |
| PP-SWR-006 | SG-02 | S1b-a-VP-0-ac0daf011b74 | VP-0 | 1 | 4.458 | -0.04329 | >= 0 | a_y path trừ (aysmax − epsilon_ay), 0–1 s, khi a_y cần > aysmax [m/s²] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-ac0daf011b74_seed1.mcap |
| PP-SWR-006 | SG-02 | S1b-a-VP-0-bc0ecb5fc06d | VP-0 | 1 | 3.958 | -0.1269 | >= 0 | a_y path trừ (aysmax − epsilon_ay), 0–1 s, khi a_y cần > aysmax [m/s²] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-bc0ecb5fc06d_seed1.mcap |
| PP-SWR-006 | SG-02 | S1b-a-VP-1-44b94ef5689d | VP-1 | 1 | 3.958 | -0.1271 | >= 0 | a_y path trừ (aysmax − epsilon_ay), 0–1 s, khi a_y cần > aysmax [m/s²] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-1-44b94ef5689d_seed1.mcap |
| PP-SWR-006 | SG-02 | S1b-a-VP-2-bdc9bcec7280 | VP-2 | 1 | 3.958 | -0.127 | >= 0 | a_y path trừ (aysmax − epsilon_ay), 0–1 s, khi a_y cần > aysmax [m/s²] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-2-bdc9bcec7280_seed1.mcap |
| PP-SWR-006 | SG-02 | S1b-a-VP-3-9b3e7230edb4 | VP-3 | 1 | 3.958 | -0.1269 | >= 0 | a_y path trừ (aysmax − epsilon_ay), 0–1 s, khi a_y cần > aysmax [m/s²] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-3-9b3e7230edb4_seed1.mcap |
| PP-SWR-006 | SG-02 | S1b-a-VP-4-03713b6fc1cf | VP-4 | 1 | 3.958 | -0.1269 | >= 0 | a_y path trừ (aysmax − epsilon_ay), 0–1 s, khi a_y cần > aysmax [m/s²] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-4-03713b6fc1cf_seed1.mcap |
| PP-SWR-006 | SG-02 | S1b-a-VP-5-9c970a207743 | VP-5 | 1 | 3.958 | -0.1269 | >= 0 | a_y path trừ (aysmax − epsilon_ay), 0–1 s, khi a_y cần > aysmax [m/s²] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-5-9c970a207743_seed1.mcap |
| PP-SWR-007 | SG-01 | S1b-a-VP-0-2450cb59e335 | VP-0 | 1 | 8.691 | 1 | = 0 | Lần lốp đè vạch khi cua gắt mà cờ chưa bật | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-2450cb59e335_seed1.mcap |
| PP-SWR-007 | SG-01 | S1b-a-VP-0-693b15015bfa | VP-0 | 1 | 8.691 | 1 | = 0 | Lần lốp đè vạch khi cua gắt mà cờ chưa bật | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-693b15015bfa_seed1.mcap |
| PP-SWR-007 | SG-01 | S1b-a-VP-0-bc0ecb5fc06d | VP-0 | 1 | 8.691 | 1 | = 0 | Lần lốp đè vạch khi cua gắt mà cờ chưa bật | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-bc0ecb5fc06d_seed1.mcap |
| PP-SWR-007 | SG-01 | S1b-a-VP-1-44b94ef5689d | VP-1 | 1 | 8.721 | 1 | = 0 | Lần lốp đè vạch khi cua gắt mà cờ chưa bật | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-1-44b94ef5689d_seed1.mcap |
| PP-SWR-007 | SG-01 | S1b-a-VP-2-bdc9bcec7280 | VP-2 | 1 | 8.691 | 1 | = 0 | Lần lốp đè vạch khi cua gắt mà cờ chưa bật | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-2-bdc9bcec7280_seed1.mcap |
| PP-SWR-007 | SG-01 | S1b-a-VP-3-9b3e7230edb4 | VP-3 | 1 | 8.681 | 1 | = 0 | Lần lốp đè vạch khi cua gắt mà cờ chưa bật | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-3-9b3e7230edb4_seed1.mcap |
| PP-SWR-007 | SG-01 | S1b-a-VP-4-03713b6fc1cf | VP-4 | 1 | 8.671 | 1 | = 0 | Lần lốp đè vạch khi cua gắt mà cờ chưa bật | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-4-03713b6fc1cf_seed1.mcap |
| PP-SWR-007 | SG-01 | S1b-a-VP-5-9c970a207743 | VP-5 | 1 | 8.651 | 1 | = 0 | Lần lốp đè vạch khi cua gắt mà cờ chưa bật | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-5-9c970a207743_seed1.mcap |
| PP-SWR-030 | SG-01 | F01-a-S5a_at_elk_activep0.2-VP-3-368cf454ae38 | VP-3 | 2 | — | — | — | ELK: có REQUEST nhưng thiếu path can thiệp hợp lệ | build/benchmark/20261115-1125-full-7495822/suite/mcap/F01-a-S5a_at_elk_activep0.2-VP-3-368cf454ae38_seed2.mcap |
| PP-SWR-030 | SG-01 | F12-g-S4a_at_lka_activep0-VP-4-f96d08bfe295 | VP-4 | 1 | — | — | — | LKA: có REQUEST nhưng thiếu path can thiệp hợp lệ | build/benchmark/20261115-1125-full-7495822/suite/mcap/F12-g-S4a_at_lka_activep0-VP-4-f96d08bfe295_seed1.mcap |
| PP-SWR-030 | SG-01 | F12-g-S4a_at_lka_activep0.2-VP-5-f52e884acad0 | VP-5 | 1 | — | — | — | LKA: có REQUEST nhưng thiếu path can thiệp hợp lệ | build/benchmark/20261115-1125-full-7495822/suite/mcap/F12-g-S4a_at_lka_activep0.2-VP-5-f52e884acad0_seed1.mcap |
| PP-SWR-030 | SG-01 | F12-g-S5a_at_elk_activep0-VP-0-a525c951898a | VP-0 | 1 | — | — | — | ELK: có REQUEST nhưng thiếu path can thiệp hợp lệ | build/benchmark/20261115-1125-full-7495822/suite/mcap/F12-g-S5a_at_elk_activep0-VP-0-a525c951898a_seed1.mcap |
| PP-SWR-030 | SG-01 | F12-g-S5a_at_elk_activep0.2-VP-1-f1a772df9115 | VP-1 | 1 | — | — | — | ELK: có REQUEST nhưng thiếu path can thiệp hợp lệ | build/benchmark/20261115-1125-full-7495822/suite/mcap/F12-g-S5a_at_elk_activep0.2-VP-1-f1a772df9115_seed1.mcap |
| PP-SWR-030 | SG-01 | F21-a-S4a_at_lka_activep0-VP-4-3c68d1fa75be | VP-4 | 1 | 5.452 | 462 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/F21-a-S4a_at_lka_activep0-VP-4-3c68d1fa75be_seed1.mcap |
| PP-SWR-030 | SG-01 | F21-a-S4a_at_lka_activep0.2-VP-5-df26ccc9fe9c | VP-5 | 1 | 5.652 | 454 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/F21-a-S4a_at_lka_activep0.2-VP-5-df26ccc9fe9c_seed1.mcap |
| PP-SWR-030 | SG-01 | F21-a-S5a_at_elk_activep0-VP-0-9b355e4bb1be | VP-0 | 1 | 5.852 | 323 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/F21-a-S5a_at_elk_activep0-VP-0-9b355e4bb1be_seed1.mcap |
| PP-SWR-030 | SG-01 | F21-a-S5a_at_elk_activep0.2-VP-1-fcde26674096 | VP-1 | 1 | 6.052 | 151 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/F21-a-S5a_at_elk_activep0.2-VP-1-fcde26674096_seed1.mcap |
| PP-SWR-030 | SG-01 | F21-d-S4a_at_lka_activep0-VP-4-b7e5b5d9cc21 | VP-4 | 1 | 5.452 | 462 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/F21-d-S4a_at_lka_activep0-VP-4-b7e5b5d9cc21_seed1.mcap |
| PP-SWR-030 | SG-01 | F21-d-S4a_at_lka_activep0.2-VP-5-d83c41d4ac16 | VP-5 | 1 | 5.652 | 454 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/F21-d-S4a_at_lka_activep0.2-VP-5-d83c41d4ac16_seed1.mcap |
| PP-SWR-030 | SG-01 | F21-d-S5a_at_elk_activep0-VP-0-16f865920e99 | VP-0 | 1 | 5.852 | 323 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/F21-d-S5a_at_elk_activep0-VP-0-16f865920e99_seed1.mcap |
| PP-SWR-030 | SG-01 | F21-d-S5a_at_elk_activep0.2-VP-1-fc48f13c34a6 | VP-1 | 1 | 6.052 | 151 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/F21-d-S5a_at_elk_activep0.2-VP-1-fc48f13c34a6_seed1.mcap |
| PP-SWR-030 | SG-01 | S1-a-VP-0-7f05cc7c5b0e | VP-0 | 1 | 9.658 | 33 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1-a-VP-0-7f05cc7c5b0e_seed1.mcap |
| PP-SWR-030 | SG-01 | S14-a-VP-0-1a76bdff67d1 | VP-0 | 1 | 8.208 | 32 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-0-1a76bdff67d1_seed1.mcap |
| PP-SWR-030 | SG-01 | S14-a-VP-0-3290c39907ee | VP-0 | 1 | 8.008 | 25 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-0-3290c39907ee_seed1.mcap |
| PP-SWR-030 | SG-01 | S14-a-VP-0-4710562d1da1 | VP-0 | 1 | 7.858 | 21 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-0-4710562d1da1_seed1.mcap |
| PP-SWR-030 | SG-01 | S14-a-VP-0-e60f61990a26 | VP-0 | 1 | 8.008 | 25 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-0-e60f61990a26_seed1.mcap |
| PP-SWR-030 | SG-01 | S14-a-VP-1-842b126e250e | VP-1 | 1 | 9.058 | 31 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-1-842b126e250e_seed1.mcap |
| PP-SWR-030 | SG-01 | S14-a-VP-1-b20ea61ca33d | VP-1 | 1 | 8.008 | 27 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-1-b20ea61ca33d_seed1.mcap |
| PP-SWR-030 | SG-01 | S14-a-VP-2-8cd97c102366 | VP-2 | 1 | 8.008 | 27 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-2-8cd97c102366_seed1.mcap |
| PP-SWR-030 | SG-01 | S14-a-VP-2-f2b38e633776 | VP-2 | 1 | 8.408 | 35 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-2-f2b38e633776_seed1.mcap |
| PP-SWR-030 | SG-01 | S14-a-VP-3-b2339f06659b | VP-3 | 1 | 8.008 | 25 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-3-b2339f06659b_seed1.mcap |
| PP-SWR-030 | SG-01 | S14-a-VP-4-c420fa437f41 | VP-4 | 1 | 8.008 | 25 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-4-c420fa437f41_seed1.mcap |
| PP-SWR-030 | SG-01 | S14-a-VP-5-767403cd2057 | VP-5 | 1 | 8.658 | 35 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-5-767403cd2057_seed1.mcap |
| PP-SWR-030 | SG-01 | S14-a-VP-5-8e96d7ae88a9 | VP-5 | 1 | 9.558 | 37 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-5-8e96d7ae88a9_seed1.mcap |
| PP-SWR-030 | SG-01 | S14-a-VP-5-a9acbf87bdfa | VP-5 | 1 | 8.008 | 25 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-5-a9acbf87bdfa_seed1.mcap |
| PP-SWR-030 | SG-01 | S16-d-VP-0-e29852ad5a1c | VP-0 | 1 | — | — | — | ELK: có REQUEST nhưng thiếu path can thiệp hợp lệ | build/benchmark/20261115-1125-full-7495822/suite/mcap/S16-d-VP-0-e29852ad5a1c_seed1.mcap |
| PP-SWR-030 | SG-01 | S16-d-VP-3-c4c71c213cb3 | VP-3 | 1 | — | — | — | ELK: có REQUEST nhưng thiếu path can thiệp hợp lệ | build/benchmark/20261115-1125-full-7495822/suite/mcap/S16-d-VP-3-c4c71c213cb3_seed1.mcap |
| PP-SWR-030 | SG-01 | S1b-a-VP-0-2450cb59e335 | VP-0 | 1 | 8.008 | 25 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-2450cb59e335_seed1.mcap |
| PP-SWR-030 | SG-01 | S1b-a-VP-0-45d39dd0be07 | VP-0 | 1 | 7.658 | 21 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-45d39dd0be07_seed1.mcap |
| PP-SWR-030 | SG-01 | S1b-a-VP-0-66e9cbe67698 | VP-0 | 1 | 7.808 | 29 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-66e9cbe67698_seed1.mcap |
| PP-SWR-030 | SG-01 | S1b-a-VP-0-693b15015bfa | VP-0 | 1 | 8.008 | 25 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-693b15015bfa_seed1.mcap |
| PP-SWR-030 | SG-01 | S1b-a-VP-0-7594aab96ea3 | VP-0 | 1 | 7.858 | 21 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-7594aab96ea3_seed1.mcap |
| PP-SWR-030 | SG-01 | S1b-a-VP-0-8a205ef6f957 | VP-0 | 1 | 8.208 | 32 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-8a205ef6f957_seed1.mcap |
| PP-SWR-030 | SG-01 | S1b-a-VP-0-bc0ecb5fc06d | VP-0 | 1 | 8.008 | 25 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-bc0ecb5fc06d_seed1.mcap |
| PP-SWR-030 | SG-01 | S1b-a-VP-1-44b94ef5689d | VP-1 | 1 | 8.008 | 27 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-1-44b94ef5689d_seed1.mcap |
| PP-SWR-030 | SG-01 | S1b-a-VP-2-bdc9bcec7280 | VP-2 | 1 | 8.008 | 27 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-2-bdc9bcec7280_seed1.mcap |
| PP-SWR-030 | SG-01 | S1b-a-VP-3-9b3e7230edb4 | VP-3 | 1 | 8.008 | 25 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-3-9b3e7230edb4_seed1.mcap |
| PP-SWR-030 | SG-01 | S1b-a-VP-4-03713b6fc1cf | VP-4 | 1 | 8.008 | 25 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-4-03713b6fc1cf_seed1.mcap |
| PP-SWR-030 | SG-01 | S1b-a-VP-5-9c970a207743 | VP-5 | 1 | 8.008 | 25 | = 0 | Chu kỳ mà chức năng đang lái khác chức năng chọn theo PP-SWR-030 | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-5-9c970a207743_seed1.mcap |
| PP-SWR-051 | SG-01 | F01-c-S1c-VP-5-0c7c7c8af819 | VP-5 | 7 | — | -0.06021 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F01-c-S1c-VP-5-0c7c7c8af819_seed7.mcap |
| PP-SWR-051 | SG-01 | F02-a-S1a-VP-0-d28b12bad2c2 | VP-0 | 1 | — | -0.2149 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F02-a-S1a-VP-0-d28b12bad2c2_seed1.mcap |
| PP-SWR-051 | SG-01 | F02-a-S1a-VP-1-ac88418fea8c | VP-1 | 1 | — | -0.2407 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F02-a-S1a-VP-1-ac88418fea8c_seed1.mcap |
| PP-SWR-051 | SG-01 | F02-a-S1a-VP-5-85efc03b236b | VP-5 | 1 | — | -0.5169 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F02-a-S1a-VP-5-85efc03b236b_seed1.mcap |
| PP-SWR-051 | SG-01 | F02-a-S1c-VP-0-d497d7b37736 | VP-0 | 1 | — | -0.2147 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F02-a-S1c-VP-0-d497d7b37736_seed1.mcap |
| PP-SWR-051 | SG-01 | F02-a-S1c-VP-1-01d157c30694 | VP-1 | 1 | — | -0.2481 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F02-a-S1c-VP-1-01d157c30694_seed1.mcap |
| PP-SWR-051 | SG-01 | F02-a-S1c-VP-5-182855375bfa | VP-5 | 1 | — | -0.5167 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F02-a-S1c-VP-5-182855375bfa_seed1.mcap |
| PP-SWR-051 | SG-01 | F02-e-S1a-VP-5-29183b65ffaf | VP-5 | 1 | — | -0.1118 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F02-e-S1a-VP-5-29183b65ffaf_seed1.mcap |
| PP-SWR-051 | SG-01 | F02-e-S1c-VP-5-50d3444b79d5 | VP-5 | 1 | — | -0.1182 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F02-e-S1c-VP-5-50d3444b79d5_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-a-S1a-VP-0-dedf6d77ab4c | VP-0 | 1 | — | -0.9642 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F03-a-S1a-VP-0-dedf6d77ab4c_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-a-S1a-VP-5-245abe76af86 | VP-5 | 1 | — | -0.1184 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F03-a-S1a-VP-5-245abe76af86_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-a-S1c-VP-0-f9d8f9a94dd1 | VP-0 | 1 | — | -0.9815 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F03-a-S1c-VP-0-f9d8f9a94dd1_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1a-VP-0-1c03af025ee4 | VP-0 | 1 | — | -0.9642 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F03-c-S1a-VP-0-1c03af025ee4_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1a-VP-1-a5219f0b3fc2 | VP-1 | 1 | — | -0.9873 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F03-c-S1a-VP-1-a5219f0b3fc2_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1a-VP-5-4a0b9685f06c | VP-5 | 1 | — | -1.274 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F03-c-S1a-VP-5-4a0b9685f06c_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1c-VP-0-0e2929c3df25 | VP-0 | 1 | — | -0.9815 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F03-c-S1c-VP-0-0e2929c3df25_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1c-VP-1-4278b1e68610 | VP-1 | 1 | — | -0.9932 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F03-c-S1c-VP-1-4278b1e68610_seed1.mcap |
| PP-SWR-051 | SG-01 | F03-c-S1c-VP-5-ce2933b62cf1 | VP-5 | 1 | — | -1.279 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F03-c-S1c-VP-5-ce2933b62cf1_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1a-VP-0-5158987ade9c | VP-0 | 1 | — | -1 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-a-S1a-VP-0-5158987ade9c_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1a-VP-0-8c9c8f7bad6f | VP-0 | 1 | — | -0.9838 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-a-S1a-VP-0-8c9c8f7bad6f_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1a-VP-0-e051e1862771 | VP-0 | 1 | — | -0.9871 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-a-S1a-VP-0-e051e1862771_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1a-VP-0-e5f80d869c82 | VP-0 | 1 | — | -0.9797 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-a-S1a-VP-0-e5f80d869c82_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1a-VP-0-e772a4a34f07 | VP-0 | 1 | — | -1.004 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-a-S1a-VP-0-e772a4a34f07_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1a-VP-1-0417ab298e11 | VP-1 | 1 | — | -1.027 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-a-S1a-VP-1-0417ab298e11_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1a-VP-1-12f41c1ced49 | VP-1 | 1 | — | -0.9986 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-a-S1a-VP-1-12f41c1ced49_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1a-VP-5-4e41f5501598 | VP-5 | 1 | — | -1.299 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-a-S1a-VP-5-4e41f5501598_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1a-VP-5-5966fdfda248 | VP-5 | 1 | — | -1.3 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-a-S1a-VP-5-5966fdfda248_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1a-VP-5-94a3185c5756 | VP-5 | 1 | — | -1.28 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-a-S1a-VP-5-94a3185c5756_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1c-VP-0-aed66d9b07f6 | VP-0 | 1 | — | -0.9928 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-a-S1c-VP-0-aed66d9b07f6_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1c-VP-0-d8bb75bf2632 | VP-0 | 1 | — | -0.9665 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-a-S1c-VP-0-d8bb75bf2632_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1c-VP-0-d9665ad8fece | VP-0 | 1 | — | -0.9686 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-a-S1c-VP-0-d9665ad8fece_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1c-VP-0-ec3bff52e318 | VP-0 | 1 | — | -0.9972 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-a-S1c-VP-0-ec3bff52e318_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1c-VP-1-d25e44cb4d6d | VP-1 | 1 | — | -0.999 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-a-S1c-VP-1-d25e44cb4d6d_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1c-VP-1-fdf987d32412 | VP-1 | 1 | — | -1.026 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-a-S1c-VP-1-fdf987d32412_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1c-VP-5-57f9065ebaa3 | VP-5 | 1 | — | -0.1366 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-a-S1c-VP-5-57f9065ebaa3_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1c-VP-5-7db7d9c2ded2 | VP-5 | 1 | — | -1.267 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-a-S1c-VP-5-7db7d9c2ded2_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1c-VP-5-7ed7d27ef33f | VP-5 | 1 | — | -1.289 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-a-S1c-VP-5-7ed7d27ef33f_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-a-S1c-VP-5-e3c72b5eac78 | VP-5 | 1 | — | -1.291 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-a-S1c-VP-5-e3c72b5eac78_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-b-S1c-VP-5-545957874102 | VP-5 | 1 | — | -0.1125 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-b-S1c-VP-5-545957874102_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1a-VP-0-24550cfc95c5 | VP-0 | 1 | — | -1 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-d-S1a-VP-0-24550cfc95c5_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1a-VP-1-3a4b29f3fe5b | VP-1 | 1 | — | -1.027 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-d-S1a-VP-1-3a4b29f3fe5b_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1a-VP-5-9e2995fea291 | VP-5 | 1 | — | -1.3 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-d-S1a-VP-5-9e2995fea291_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1c-VP-0-608ec3b8fc9f | VP-0 | 1 | — | -0.9928 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-d-S1c-VP-0-608ec3b8fc9f_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1c-VP-1-40397bd3efa4 | VP-1 | 1 | — | -1.026 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-d-S1c-VP-1-40397bd3efa4_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-d-S1c-VP-5-bdab3c9103b7 | VP-5 | 1 | — | -1.291 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-d-S1c-VP-5-bdab3c9103b7_seed1.mcap |
| PP-SWR-051 | SG-01 | F06-e-S1c-VP-5-87266b531a26 | VP-5 | 1 | — | -0.1366 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-e-S1c-VP-5-87266b531a26_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-0-4efddd649b2a | VP-0 | 1 | — | -0.9061 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F08-a-S1c-VP-0-4efddd649b2a_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-0-9d836e616214 | VP-0 | 1 | — | -0.9061 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F08-a-S1c-VP-0-9d836e616214_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-1-9f6496a368b0 | VP-1 | 1 | — | -0.9362 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F08-a-S1c-VP-1-9f6496a368b0_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-1-c098420638d4 | VP-1 | 1 | — | -0.9362 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F08-a-S1c-VP-1-c098420638d4_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-5-5d6c59c69cbe | VP-5 | 1 | — | -1.207 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F08-a-S1c-VP-5-5d6c59c69cbe_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-a-S1c-VP-5-dce61f599c6e | VP-5 | 1 | — | -1.207 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F08-a-S1c-VP-5-dce61f599c6e_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-b-S1c-VP-0-4ae7633cf949 | VP-0 | 1 | — | -0.9738 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F08-b-S1c-VP-0-4ae7633cf949_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-b-S1c-VP-1-297eab73e001 | VP-1 | 1 | — | -0.9956 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F08-b-S1c-VP-1-297eab73e001_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-b-S1c-VP-5-9d66d718191a | VP-5 | 1 | — | -1.276 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F08-b-S1c-VP-5-9d66d718191a_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1a-VP-0-e8ee89e39225 | VP-0 | 1 | — | -0.3729 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F08-c-S1a-VP-0-e8ee89e39225_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1a-VP-1-1657cdf8bd31 | VP-1 | 1 | — | -0.4701 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F08-c-S1a-VP-1-1657cdf8bd31_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1a-VP-5-f71d325809b3 | VP-5 | 1 | — | -0.654 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F08-c-S1a-VP-5-f71d325809b3_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1c-VP-0-bca0f1afb997 | VP-0 | 1 | — | -0.982 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F08-c-S1c-VP-0-bca0f1afb997_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1c-VP-1-3d8334644eea | VP-1 | 1 | — | -1.008 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F08-c-S1c-VP-1-3d8334644eea_seed1.mcap |
| PP-SWR-051 | SG-01 | F08-c-S1c-VP-5-06d7bb8fda8b | VP-5 | 1 | — | -1.272 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F08-c-S1c-VP-5-06d7bb8fda8b_seed1.mcap |
| PP-SWR-051 | SG-01 | F17-b-S1c-VP-0-a1cbc36bb0c4 | VP-0 | 1 | — | -0.9897 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F17-b-S1c-VP-0-a1cbc36bb0c4_seed1.mcap |
| PP-SWR-051 | SG-01 | F17-b-S1c-VP-1-0c87d5e3e71f | VP-1 | 1 | — | -0.8732 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F17-b-S1c-VP-1-0c87d5e3e71f_seed1.mcap |
| PP-SWR-051 | SG-01 | F17-b-S1c-VP-5-b18d1d45e3b1 | VP-5 | 1 | — | -1.293 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F17-b-S1c-VP-5-b18d1d45e3b1_seed1.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-0-1467a0e9844f | VP-0 | 7 | — | -0.03877 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S1c-VP-0-1467a0e9844f_seed7.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-1-15c9123704b8 | VP-1 | 7 | — | -0.0755 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S1c-VP-1-15c9123704b8_seed7.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-2-b56ea41bbee2 | VP-2 | 7 | — | -0.1447 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S1c-VP-2-b56ea41bbee2_seed7.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-3-0970d8d23b03 | VP-3 | 1 | — | -0.04733 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S1c-VP-3-0970d8d23b03_seed1.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-3-0970d8d23b03 | VP-3 | 7 | — | -0.1936 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S1c-VP-3-0970d8d23b03_seed7.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-4-e79aef633429 | VP-4 | 1 | — | -0.06448 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S1c-VP-4-e79aef633429_seed1.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-4-e79aef633429 | VP-4 | 7 | — | -0.2152 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S1c-VP-4-e79aef633429_seed7.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-5-38898514a806 | VP-5 | 1 | — | -0.1875 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S1c-VP-5-38898514a806_seed1.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-5-38898514a806 | VP-5 | 2 | — | -0.03221 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S1c-VP-5-38898514a806_seed2.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-5-38898514a806 | VP-5 | 4 | — | -0.02785 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S1c-VP-5-38898514a806_seed4.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-5-38898514a806 | VP-5 | 7 | — | -0.3382 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S1c-VP-5-38898514a806_seed7.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-5-38898514a806 | VP-5 | 8 | — | -0.1224 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S1c-VP-5-38898514a806_seed8.mcap |
| PP-SWR-051 | SG-01 | G01-S1c-VP-5-38898514a806 | VP-5 | 10 | — | -0.05893 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S1c-VP-5-38898514a806_seed10.mcap |
| PP-SWR-051 | SG-01 | S1-a-VP-0-c7c9506283e7 | VP-0 | 1 | — | -0.009433 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1-a-VP-0-c7c9506283e7_seed1.mcap |
| PP-SWR-051 | SG-01 | S12-a-VP-5-e7c93cf1d873 | VP-5 | 7 | — | -0.05978 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-a-VP-5-e7c93cf1d873_seed7.mcap |
| PP-SWR-051 | SG-01 | S14-a-VP-0-55aaa0559f68 | VP-0 | 1 | — | -23.37 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-0-55aaa0559f68_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-a-VP-0-704a3b4d5f13 | VP-0 | 1 | — | -24.37 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-0-704a3b4d5f13_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-a-VP-0-cabfa230312d | VP-0 | 1 | — | -23.37 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-0-cabfa230312d_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-a-VP-0-d20fa935d75d | VP-0 | 1 | — | -22.87 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-0-d20fa935d75d_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-a-VP-1-5474a3d546d9 | VP-1 | 1 | — | -23.11 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-1-5474a3d546d9_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-a-VP-2-3a522ed9f6de | VP-2 | 1 | — | -15.2 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-2-3a522ed9f6de_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-a-VP-2-e5955077a54f | VP-2 | 1 | — | -23.41 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-2-e5955077a54f_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-a-VP-3-36b77c51567c | VP-3 | 1 | — | -23.55 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-3-36b77c51567c_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-a-VP-4-081e7f2841e4 | VP-4 | 1 | — | -23.64 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-4-081e7f2841e4_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-a-VP-5-6b3561338f71 | VP-5 | 1 | — | -9.124 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-5-6b3561338f71_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-a-VP-5-b89abf3b879f | VP-5 | 1 | — | -23.77 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-5-b89abf3b879f_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-0-ff8e4ce04140 | VP-0 | 1 | — | -0.1199 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-e-VP-0-ff8e4ce04140_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-1-c599c50726eb | VP-1 | 1 | — | -0.1905 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-e-VP-1-c599c50726eb_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-2-d2cc20ee8bbf | VP-2 | 1 | — | -0.2353 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-e-VP-2-d2cc20ee8bbf_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-3-24dcd5adb2de | VP-3 | 1 | — | -0.2707 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-e-VP-3-24dcd5adb2de_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-4-a571d2de589d | VP-4 | 1 | — | -0.2818 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-e-VP-4-a571d2de589d_seed1.mcap |
| PP-SWR-051 | SG-01 | S14-e-VP-5-3f2b28b63f2e | VP-5 | 1 | — | -0.4048 | >= 0 | DLC nhỏ nhất so với làn thật [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-e-VP-5-3f2b28b63f2e_seed1.mcap |
| PP-SWR-085 | SG-01 | F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0 | VP-3 | 1 | — | -0.1044 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F02-e-S4a_at_lka_activep0.2-VP-3-92b9ffc993c0_seed1.mcap |
| PP-SWR-085 | SG-01 | F03-c-S5a_at_elk_activep0.2-VP-5-456660bb07a5 | VP-5 | 1 | — | -0.1834 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F03-c-S5a_at_elk_activep0.2-VP-5-456660bb07a5_seed1.mcap |
| PP-SWR-085 | SG-01 | S13-b-elk-VP-3-036d4797fb02 | VP-3 | 1 | — | -0.09176 | >= 0 | DLC phía đối diện qua bàn giao EPS [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S13-b-elk-VP-3-036d4797fb02_seed1.mcap |
| PP-SWR-086 | SG-03 | F06-d-S4a_at_lka_activep0-VP-4-1f4ccfa0bddb | VP-4 | 1 | — | -0.7399 | >= -0.3 | DTLE vạch nhỏ nhất [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-d-S4a_at_lka_activep0-VP-4-1f4ccfa0bddb_seed1.mcap |
| PP-SWR-086 | SG-03 | F06-d-S4a_at_lka_activep0.2-VP-5-66f120bb4241 | VP-5 | 1 | — | -0.808 | >= -0.3 | DTLE vạch nhỏ nhất [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-d-S4a_at_lka_activep0.2-VP-5-66f120bb4241_seed1.mcap |
| PP-SWR-086 | SG-03 | F06-d-S5a_at_elk_activep0-VP-0-f32caea02125 | VP-0 | 1 | — | -0.7071 | >= -0.3 | DTLE vạch nhỏ nhất [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-d-S5a_at_elk_activep0-VP-0-f32caea02125_seed1.mcap |
| PP-SWR-086 | SG-03 | F06-d-S5a_at_elk_activep0.2-VP-1-f5395e617721 | VP-1 | 1 | — | -0.6304 | >= -0.3 | DTLE vạch nhỏ nhất [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F06-d-S5a_at_elk_activep0.2-VP-1-f5395e617721_seed1.mcap |
| PP-SWR-086 | SG-03 | S13-b-elk-VP-3-036d4797fb02 | VP-3 | 1 | — | -0.4499 | >= -0.3 | DTLE vạch nhỏ nhất [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S13-b-elk-VP-3-036d4797fb02_seed1.mcap |
| PP-SWR-086 | SG-03 | S5-a-VP-4-af4b59853f61 | VP-4 | 1 | — | -0.6679 | >= -0.3 | DTLE vạch nhỏ nhất [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S5-a-VP-4-af4b59853f61_seed1.mcap |
| PP-SWR-091 | SG-03 | S13-b-elk-VP-3-036d4797fb02 | VP-3 | 1 | — | -0.4499 | >= -0.3 | DTLE vạch khi EPS chậm tới 100 ms [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S13-b-elk-VP-3-036d4797fb02_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-b-S1c-VP-0-4ae7633cf949 | VP-0 | 1 | 18.08 | 0.05689 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F08-b-S1c-VP-0-4ae7633cf949_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-b-S1c-VP-1-297eab73e001 | VP-1 | 1 | 18.08 | 0.05695 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F08-b-S1c-VP-1-297eab73e001_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-b-S1c-VP-5-9d66d718191a | VP-5 | 1 | 18.08 | 0.05688 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F08-b-S1c-VP-5-9d66d718191a_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-c-S1a-VP-0-e8ee89e39225 | VP-0 | 1 | 5.608 | 0.07296 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F08-c-S1a-VP-0-e8ee89e39225_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-c-S1a-VP-1-1657cdf8bd31 | VP-1 | 1 | 5.508 | 0.07302 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F08-c-S1a-VP-1-1657cdf8bd31_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-c-S1a-VP-5-f71d325809b3 | VP-5 | 1 | 5.608 | 0.0729 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F08-c-S1a-VP-5-f71d325809b3_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-c-S1c-VP-0-bca0f1afb997 | VP-0 | 1 | 5.208 | 0.07853 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F08-c-S1c-VP-0-bca0f1afb997_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-c-S1c-VP-1-3d8334644eea | VP-1 | 1 | 5.158 | 0.07843 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F08-c-S1c-VP-1-3d8334644eea_seed1.mcap |
| PP-SWR-100 | SG-04 | F08-c-S1c-VP-5-06d7bb8fda8b | VP-5 | 1 | 5.158 | 0.07872 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/F08-c-S1c-VP-5-06d7bb8fda8b_seed1.mcap |
| PP-SWR-100 | SG-04 | S1-a-VP-0-7f05cc7c5b0e | VP-0 | 1 | 5.208 | 0.06662 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1-a-VP-0-7f05cc7c5b0e_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-a-VP-0-1a76bdff67d1 | VP-0 | 1 | 2.858 | 0.05245 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-0-1a76bdff67d1_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-a-VP-0-3290c39907ee | VP-0 | 1 | 2.858 | 0.05247 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-0-3290c39907ee_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-a-VP-0-4710562d1da1 | VP-0 | 1 | 2.858 | 0.05248 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-0-4710562d1da1_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-a-VP-0-55aaa0559f68 | VP-0 | 1 | 2.858 | 0.05247 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-0-55aaa0559f68_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-a-VP-0-704a3b4d5f13 | VP-0 | 1 | 2.858 | 0.05245 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-0-704a3b4d5f13_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-a-VP-0-cabfa230312d | VP-0 | 1 | 2.858 | 0.05247 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-0-cabfa230312d_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-a-VP-0-d20fa935d75d | VP-0 | 1 | 2.858 | 0.05248 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-0-d20fa935d75d_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-a-VP-0-e60f61990a26 | VP-0 | 1 | 2.858 | 0.05247 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-0-e60f61990a26_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-a-VP-1-5474a3d546d9 | VP-1 | 1 | 2.858 | 0.05246 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-1-5474a3d546d9_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-a-VP-1-b20ea61ca33d | VP-1 | 1 | 2.858 | 0.05246 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-1-b20ea61ca33d_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-a-VP-2-8cd97c102366 | VP-2 | 1 | 2.858 | 0.05247 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-2-8cd97c102366_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-a-VP-2-e5955077a54f | VP-2 | 1 | 2.858 | 0.05247 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-2-e5955077a54f_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-a-VP-3-36b77c51567c | VP-3 | 1 | 2.858 | 0.05248 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-3-36b77c51567c_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-a-VP-3-b2339f06659b | VP-3 | 1 | 2.858 | 0.05248 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-3-b2339f06659b_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-a-VP-4-081e7f2841e4 | VP-4 | 1 | 2.858 | 0.05248 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-4-081e7f2841e4_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-a-VP-4-c420fa437f41 | VP-4 | 1 | 2.858 | 0.05248 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-4-c420fa437f41_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-a-VP-5-767403cd2057 | VP-5 | 1 | 4.308 | 0.05006 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-5-767403cd2057_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-a-VP-5-a9acbf87bdfa | VP-5 | 1 | 2.858 | 0.05248 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-5-a9acbf87bdfa_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-a-VP-5-b89abf3b879f | VP-5 | 1 | 2.858 | 0.05248 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-a-VP-5-b89abf3b879f_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-c-VP-0-c8e86866eeb2 | VP-0 | 1 | 12.36 | 0.1414 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-c-VP-0-c8e86866eeb2_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-c-VP-1-ffd30cdab212 | VP-1 | 1 | 12.36 | 0.1407 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-c-VP-1-ffd30cdab212_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-c-VP-2-51734930fc19 | VP-2 | 1 | 12.36 | 0.1408 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-c-VP-2-51734930fc19_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-c-VP-3-cbd4381d8311 | VP-3 | 1 | 12.36 | 0.1409 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-c-VP-3-cbd4381d8311_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-c-VP-4-5cb1a6c30767 | VP-4 | 1 | 12.36 | 0.1408 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-c-VP-4-5cb1a6c30767_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-c-VP-5-1c80d628c800 | VP-5 | 1 | 12.36 | 0.1408 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-c-VP-5-1c80d628c800_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-0-dc72ffbcfa45 | VP-0 | 1 | 3.558 | 0.05817 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-e-VP-0-dc72ffbcfa45_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-0-ff8e4ce04140 | VP-0 | 1 | 3.583 | 0.05641 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-e-VP-0-ff8e4ce04140_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-1-9e894e6e0e47 | VP-1 | 1 | 3.558 | 0.05791 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-e-VP-1-9e894e6e0e47_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-1-c599c50726eb | VP-1 | 1 | 3.583 | 0.05648 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-e-VP-1-c599c50726eb_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-2-8ea25fd5bd76 | VP-2 | 1 | 3.558 | 0.05816 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-e-VP-2-8ea25fd5bd76_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-2-d2cc20ee8bbf | VP-2 | 1 | 3.583 | 0.05644 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-e-VP-2-d2cc20ee8bbf_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-3-24dcd5adb2de | VP-3 | 1 | 3.583 | 0.0564 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-e-VP-3-24dcd5adb2de_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-3-5cf328ad0176 | VP-3 | 1 | 3.558 | 0.05817 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-e-VP-3-5cf328ad0176_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-4-a571d2de589d | VP-4 | 1 | 3.583 | 0.05637 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-e-VP-4-a571d2de589d_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-4-f51e1424afde | VP-4 | 1 | 3.558 | 0.05819 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-e-VP-4-f51e1424afde_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-5-3f2b28b63f2e | VP-5 | 1 | 3.583 | 0.05637 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-e-VP-5-3f2b28b63f2e_seed1.mcap |
| PP-SWR-100 | SG-04 | S14-e-VP-5-845fd11edffe | VP-5 | 1 | 3.558 | 0.05819 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-e-VP-5-845fd11edffe_seed1.mcap |
| PP-SWR-100 | SG-04 | S1b-a-VP-0-2450cb59e335 | VP-0 | 1 | 2.858 | 0.05247 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-2450cb59e335_seed1.mcap |
| PP-SWR-100 | SG-04 | S1b-a-VP-0-45d39dd0be07 | VP-0 | 1 | 2.758 | 0.05359 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-45d39dd0be07_seed1.mcap |
| PP-SWR-100 | SG-04 | S1b-a-VP-0-66e9cbe67698 | VP-0 | 1 | 8.758 | 0.05071 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-66e9cbe67698_seed1.mcap |
| PP-SWR-100 | SG-04 | S1b-a-VP-0-693b15015bfa | VP-0 | 1 | 2.858 | 0.05247 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-693b15015bfa_seed1.mcap |
| PP-SWR-100 | SG-04 | S1b-a-VP-0-7594aab96ea3 | VP-0 | 1 | 2.858 | 0.05248 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-7594aab96ea3_seed1.mcap |
| PP-SWR-100 | SG-04 | S1b-a-VP-0-8a205ef6f957 | VP-0 | 1 | 2.858 | 0.05245 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-8a205ef6f957_seed1.mcap |
| PP-SWR-100 | SG-04 | S1b-a-VP-0-a4d17e6ba3b6 | VP-0 | 1 | 2.858 | 0.05247 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-a4d17e6ba3b6_seed1.mcap |
| PP-SWR-100 | SG-04 | S1b-a-VP-0-bc0ecb5fc06d | VP-0 | 1 | 2.858 | 0.05247 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-0-bc0ecb5fc06d_seed1.mcap |
| PP-SWR-100 | SG-04 | S1b-a-VP-1-44b94ef5689d | VP-1 | 1 | 2.858 | 0.05246 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-1-44b94ef5689d_seed1.mcap |
| PP-SWR-100 | SG-04 | S1b-a-VP-2-bdc9bcec7280 | VP-2 | 1 | 2.858 | 0.05247 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-2-bdc9bcec7280_seed1.mcap |
| PP-SWR-100 | SG-04 | S1b-a-VP-3-9b3e7230edb4 | VP-3 | 1 | 2.858 | 0.05248 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-3-9b3e7230edb4_seed1.mcap |
| PP-SWR-100 | SG-04 | S1b-a-VP-4-03713b6fc1cf | VP-4 | 1 | 2.858 | 0.05248 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-4-03713b6fc1cf_seed1.mcap |
| PP-SWR-100 | SG-04 | S1b-a-VP-5-9c970a207743 | VP-5 | 1 | 2.858 | 0.05248 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S1b-a-VP-5-9c970a207743_seed1.mcap |
| PP-SWR-100 | SG-04 | S6-a-VP-5-e47a241ce98f | VP-5 | 1 | 10.98 | 0.05254 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S6-a-VP-5-e47a241ce98f_seed1.mcap |
| PP-SWR-101 | SG-04 | S14-c-VP-0-c8e86866eeb2 | VP-0 | 1 | 8.559 | 0.01113 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-c-VP-0-c8e86866eeb2_seed1.mcap |
| PP-SWR-101 | SG-04 | S14-c-VP-1-ffd30cdab212 | VP-1 | 1 | 8.559 | 0.0112 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-c-VP-1-ffd30cdab212_seed1.mcap |
| PP-SWR-101 | SG-04 | S14-c-VP-2-51734930fc19 | VP-2 | 1 | 8.559 | 0.01121 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-c-VP-2-51734930fc19_seed1.mcap |
| PP-SWR-101 | SG-04 | S14-c-VP-3-cbd4381d8311 | VP-3 | 1 | 8.559 | 0.0112 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-c-VP-3-cbd4381d8311_seed1.mcap |
| PP-SWR-101 | SG-04 | S14-c-VP-4-5cb1a6c30767 | VP-4 | 1 | 8.559 | 0.01119 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-c-VP-4-5cb1a6c30767_seed1.mcap |
| PP-SWR-101 | SG-04 | S14-c-VP-5-1c80d628c800 | VP-5 | 1 | 8.559 | 0.01119 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-c-VP-5-1c80d628c800_seed1.mcap |
| PP-SWR-101 | SG-04 | S14-e-VP-1-9e894e6e0e47 | VP-1 | 1 | 6.858 | 0.00553 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-e-VP-1-9e894e6e0e47_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-c-VP-0-c8e86866eeb2 | VP-0 | 1 | 8.559 | 0.000619 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-c-VP-0-c8e86866eeb2_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-c-VP-1-ffd30cdab212 | VP-1 | 1 | 8.559 | 0.0006151 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-c-VP-1-ffd30cdab212_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-c-VP-2-51734930fc19 | VP-2 | 1 | 8.559 | 0.000613 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-c-VP-2-51734930fc19_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-c-VP-3-cbd4381d8311 | VP-3 | 1 | 8.559 | 0.0006127 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-c-VP-3-cbd4381d8311_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-c-VP-4-5cb1a6c30767 | VP-4 | 1 | 8.559 | 0.0006125 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-c-VP-4-5cb1a6c30767_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-c-VP-5-1c80d628c800 | VP-5 | 1 | 8.559 | 0.0006125 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-c-VP-5-1c80d628c800_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-e-VP-0-dc72ffbcfa45 | VP-0 | 1 | 6.908 | 0.000316 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-e-VP-0-dc72ffbcfa45_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-e-VP-1-9e894e6e0e47 | VP-1 | 1 | 6.858 | 0.0003053 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-e-VP-1-9e894e6e0e47_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-e-VP-2-8ea25fd5bd76 | VP-2 | 1 | 6.908 | 0.0003159 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-e-VP-2-8ea25fd5bd76_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-e-VP-3-5cf328ad0176 | VP-3 | 1 | 6.908 | 0.000316 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-e-VP-3-5cf328ad0176_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-e-VP-4-f51e1424afde | VP-4 | 1 | 6.908 | 0.0003162 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-e-VP-4-f51e1424afde_seed1.mcap |
| PP-SWR-102 | SG-04 | S14-e-VP-5-845fd11edffe | VP-5 | 1 | 6.908 | 0.0003162 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | build/benchmark/20261115-1125-full-7495822/suite/mcap/S14-e-VP-5-845fd11edffe_seed1.mcap |

## Trượt MINOR

| Requirement | Safety goal | Ca | Profile | Seed | Trượt đầu tiên [s] | Giá trị | Ngưỡng | Chi tiết | MCAP |
|---|---|---|---|---|---|---|---|---|---|
| PP-SWR-032 | — | F01-a-S4a_at_lka_activep0-VP-0-c97d4f8c3b33 | VP-0 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/F01-a-S4a_at_lka_activep0-VP-0-c97d4f8c3b33_seed1.mcap |
| PP-SWR-032 | — | F01-a-S4a_at_lka_activep0-VP-0-c97d4f8c3b33 | VP-0 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/F01-a-S4a_at_lka_activep0-VP-0-c97d4f8c3b33_seed2.mcap |
| PP-SWR-032 | — | F01-b-S4a_at_lka_activep0-VP-2-26b730c60966 | VP-2 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/F01-b-S4a_at_lka_activep0-VP-2-26b730c60966_seed1.mcap |
| PP-SWR-032 | — | F01-b-S4a_at_lka_activep0-VP-2-26b730c60966 | VP-2 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/F01-b-S4a_at_lka_activep0-VP-2-26b730c60966_seed2.mcap |
| PP-SWR-032 | — | F01-b-S4a_at_lka_activep0.2-VP-3-7e4bb0e3caed | VP-3 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/F01-b-S4a_at_lka_activep0.2-VP-3-7e4bb0e3caed_seed1.mcap |
| PP-SWR-032 | — | F01-b-S4a_at_lka_activep0.2-VP-3-7e4bb0e3caed | VP-3 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/F01-b-S4a_at_lka_activep0.2-VP-3-7e4bb0e3caed_seed2.mcap |
| PP-SWR-032 | — | F01-b-S5a_at_elk_activep0-VP-4-e041939a271d | VP-4 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/F01-b-S5a_at_elk_activep0-VP-4-e041939a271d_seed1.mcap |
| PP-SWR-032 | — | F01-b-S5a_at_elk_activep0-VP-4-e041939a271d | VP-4 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/F01-b-S5a_at_elk_activep0-VP-4-e041939a271d_seed2.mcap |
| PP-SWR-032 | — | F01-b-S5a_at_elk_activep0.2-VP-5-abe49b23f103 | VP-5 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/F01-b-S5a_at_elk_activep0.2-VP-5-abe49b23f103_seed1.mcap |
| PP-SWR-032 | — | F01-b-S5a_at_elk_activep0.2-VP-5-abe49b23f103 | VP-5 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/F01-b-S5a_at_elk_activep0.2-VP-5-abe49b23f103_seed2.mcap |
| PP-SWR-032 | — | F01-c-S4a_at_lka_activep0-VP-4-914355537c7d | VP-4 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/F01-c-S4a_at_lka_activep0-VP-4-914355537c7d_seed1.mcap |
| PP-SWR-032 | — | F01-c-S4a_at_lka_activep0-VP-4-914355537c7d | VP-4 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/F01-c-S4a_at_lka_activep0-VP-4-914355537c7d_seed2.mcap |
| PP-SWR-032 | — | F01-c-S4a_at_lka_activep0.2-VP-5-2e109dc103db | VP-5 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/F01-c-S4a_at_lka_activep0.2-VP-5-2e109dc103db_seed1.mcap |
| PP-SWR-032 | — | F01-c-S4a_at_lka_activep0.2-VP-5-2e109dc103db | VP-5 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/F01-c-S4a_at_lka_activep0.2-VP-5-2e109dc103db_seed2.mcap |
| PP-SWR-032 | — | F01-c-S5a_at_elk_activep0-VP-0-4f81d815da3e | VP-0 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/F01-c-S5a_at_elk_activep0-VP-0-4f81d815da3e_seed1.mcap |
| PP-SWR-032 | — | F01-c-S5a_at_elk_activep0.2-VP-1-5918c01cd972 | VP-1 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/F01-c-S5a_at_elk_activep0.2-VP-1-5918c01cd972_seed1.mcap |
| PP-SWR-032 | — | F10-c-S4a_at_lka_activep0-VP-0-11cc1a987476 | VP-0 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/F10-c-S4a_at_lka_activep0-VP-0-11cc1a987476_seed1.mcap |
| PP-SWR-032 | — | F10-c-S5a_at_elk_activep0.2-VP-3-53f55fc58a43 | VP-3 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/F10-c-S5a_at_elk_activep0.2-VP-3-53f55fc58a43_seed1.mcap |
| PP-SWR-032 | — | G01-S4c-VP-0-944a5944b2f0 | VP-0 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-0-944a5944b2f0_seed1.mcap |
| PP-SWR-032 | — | G01-S4c-VP-0-944a5944b2f0 | VP-0 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-0-944a5944b2f0_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-0-944a5944b2f0 | VP-0 | 3 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-0-944a5944b2f0_seed3.mcap |
| PP-SWR-032 | — | G01-S4c-VP-0-944a5944b2f0 | VP-0 | 4 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-0-944a5944b2f0_seed4.mcap |
| PP-SWR-032 | — | G01-S4c-VP-0-944a5944b2f0 | VP-0 | 5 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-0-944a5944b2f0_seed5.mcap |
| PP-SWR-032 | — | G01-S4c-VP-0-944a5944b2f0 | VP-0 | 7 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-0-944a5944b2f0_seed7.mcap |
| PP-SWR-032 | — | G01-S4c-VP-0-944a5944b2f0 | VP-0 | 8 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-0-944a5944b2f0_seed8.mcap |
| PP-SWR-032 | — | G01-S4c-VP-0-944a5944b2f0 | VP-0 | 9 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-0-944a5944b2f0_seed9.mcap |
| PP-SWR-032 | — | G01-S4c-VP-0-944a5944b2f0 | VP-0 | 10 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-0-944a5944b2f0_seed10.mcap |
| PP-SWR-032 | — | G01-S4c-VP-1-d9c02f4d85c9 | VP-1 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-1-d9c02f4d85c9_seed1.mcap |
| PP-SWR-032 | — | G01-S4c-VP-1-d9c02f4d85c9 | VP-1 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-1-d9c02f4d85c9_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-1-d9c02f4d85c9 | VP-1 | 3 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-1-d9c02f4d85c9_seed3.mcap |
| PP-SWR-032 | — | G01-S4c-VP-1-d9c02f4d85c9 | VP-1 | 4 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-1-d9c02f4d85c9_seed4.mcap |
| PP-SWR-032 | — | G01-S4c-VP-1-d9c02f4d85c9 | VP-1 | 5 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-1-d9c02f4d85c9_seed5.mcap |
| PP-SWR-032 | — | G01-S4c-VP-1-d9c02f4d85c9 | VP-1 | 7 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-1-d9c02f4d85c9_seed7.mcap |
| PP-SWR-032 | — | G01-S4c-VP-1-d9c02f4d85c9 | VP-1 | 8 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-1-d9c02f4d85c9_seed8.mcap |
| PP-SWR-032 | — | G01-S4c-VP-1-d9c02f4d85c9 | VP-1 | 9 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-1-d9c02f4d85c9_seed9.mcap |
| PP-SWR-032 | — | G01-S4c-VP-1-d9c02f4d85c9 | VP-1 | 10 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-1-d9c02f4d85c9_seed10.mcap |
| PP-SWR-032 | — | G01-S4c-VP-2-19b08e51426b | VP-2 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-2-19b08e51426b_seed1.mcap |
| PP-SWR-032 | — | G01-S4c-VP-2-19b08e51426b | VP-2 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-2-19b08e51426b_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-2-19b08e51426b | VP-2 | 3 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-2-19b08e51426b_seed3.mcap |
| PP-SWR-032 | — | G01-S4c-VP-2-19b08e51426b | VP-2 | 4 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-2-19b08e51426b_seed4.mcap |
| PP-SWR-032 | — | G01-S4c-VP-2-19b08e51426b | VP-2 | 5 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-2-19b08e51426b_seed5.mcap |
| PP-SWR-032 | — | G01-S4c-VP-2-19b08e51426b | VP-2 | 7 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-2-19b08e51426b_seed7.mcap |
| PP-SWR-032 | — | G01-S4c-VP-2-19b08e51426b | VP-2 | 8 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-2-19b08e51426b_seed8.mcap |
| PP-SWR-032 | — | G01-S4c-VP-2-19b08e51426b | VP-2 | 9 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-2-19b08e51426b_seed9.mcap |
| PP-SWR-032 | — | G01-S4c-VP-2-19b08e51426b | VP-2 | 10 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-2-19b08e51426b_seed10.mcap |
| PP-SWR-032 | — | G01-S4c-VP-3-9991783c316d | VP-3 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-3-9991783c316d_seed1.mcap |
| PP-SWR-032 | — | G01-S4c-VP-3-9991783c316d | VP-3 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-3-9991783c316d_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-3-9991783c316d | VP-3 | 3 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-3-9991783c316d_seed3.mcap |
| PP-SWR-032 | — | G01-S4c-VP-3-9991783c316d | VP-3 | 4 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-3-9991783c316d_seed4.mcap |
| PP-SWR-032 | — | G01-S4c-VP-3-9991783c316d | VP-3 | 5 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-3-9991783c316d_seed5.mcap |
| PP-SWR-032 | — | G01-S4c-VP-3-9991783c316d | VP-3 | 7 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-3-9991783c316d_seed7.mcap |
| PP-SWR-032 | — | G01-S4c-VP-3-9991783c316d | VP-3 | 8 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-3-9991783c316d_seed8.mcap |
| PP-SWR-032 | — | G01-S4c-VP-3-9991783c316d | VP-3 | 9 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-3-9991783c316d_seed9.mcap |
| PP-SWR-032 | — | G01-S4c-VP-3-9991783c316d | VP-3 | 10 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-3-9991783c316d_seed10.mcap |
| PP-SWR-032 | — | G01-S4c-VP-4-072664ac9b98 | VP-4 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-4-072664ac9b98_seed1.mcap |
| PP-SWR-032 | — | G01-S4c-VP-4-072664ac9b98 | VP-4 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-4-072664ac9b98_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-4-072664ac9b98 | VP-4 | 3 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-4-072664ac9b98_seed3.mcap |
| PP-SWR-032 | — | G01-S4c-VP-4-072664ac9b98 | VP-4 | 4 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-4-072664ac9b98_seed4.mcap |
| PP-SWR-032 | — | G01-S4c-VP-4-072664ac9b98 | VP-4 | 5 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-4-072664ac9b98_seed5.mcap |
| PP-SWR-032 | — | G01-S4c-VP-4-072664ac9b98 | VP-4 | 7 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-4-072664ac9b98_seed7.mcap |
| PP-SWR-032 | — | G01-S4c-VP-4-072664ac9b98 | VP-4 | 8 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-4-072664ac9b98_seed8.mcap |
| PP-SWR-032 | — | G01-S4c-VP-4-072664ac9b98 | VP-4 | 9 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-4-072664ac9b98_seed9.mcap |
| PP-SWR-032 | — | G01-S4c-VP-4-072664ac9b98 | VP-4 | 10 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-4-072664ac9b98_seed10.mcap |
| PP-SWR-032 | — | G01-S4c-VP-5-26df2868e70c | VP-5 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-5-26df2868e70c_seed1.mcap |
| PP-SWR-032 | — | G01-S4c-VP-5-26df2868e70c | VP-5 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-5-26df2868e70c_seed2.mcap |
| PP-SWR-032 | — | G01-S4c-VP-5-26df2868e70c | VP-5 | 3 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-5-26df2868e70c_seed3.mcap |
| PP-SWR-032 | — | G01-S4c-VP-5-26df2868e70c | VP-5 | 4 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-5-26df2868e70c_seed4.mcap |
| PP-SWR-032 | — | G01-S4c-VP-5-26df2868e70c | VP-5 | 5 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-5-26df2868e70c_seed5.mcap |
| PP-SWR-032 | — | G01-S4c-VP-5-26df2868e70c | VP-5 | 7 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-5-26df2868e70c_seed7.mcap |
| PP-SWR-032 | — | G01-S4c-VP-5-26df2868e70c | VP-5 | 8 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-5-26df2868e70c_seed8.mcap |
| PP-SWR-032 | — | G01-S4c-VP-5-26df2868e70c | VP-5 | 9 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-5-26df2868e70c_seed9.mcap |
| PP-SWR-032 | — | G01-S4c-VP-5-26df2868e70c | VP-5 | 10 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/G01-S4c-VP-5-26df2868e70c_seed10.mcap |
| PP-SWR-032 | — | S12-b-VP-0-69e53aeef11a | VP-0 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-0-69e53aeef11a_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-0-69e53aeef11a | VP-0 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-0-69e53aeef11a_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-0-69e53aeef11a | VP-0 | 3 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-0-69e53aeef11a_seed3.mcap |
| PP-SWR-032 | — | S12-b-VP-0-69e53aeef11a | VP-0 | 4 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-0-69e53aeef11a_seed4.mcap |
| PP-SWR-032 | — | S12-b-VP-0-69e53aeef11a | VP-0 | 5 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-0-69e53aeef11a_seed5.mcap |
| PP-SWR-032 | — | S12-b-VP-0-69e53aeef11a | VP-0 | 6 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-0-69e53aeef11a_seed6.mcap |
| PP-SWR-032 | — | S12-b-VP-0-69e53aeef11a | VP-0 | 7 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-0-69e53aeef11a_seed7.mcap |
| PP-SWR-032 | — | S12-b-VP-0-69e53aeef11a | VP-0 | 8 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-0-69e53aeef11a_seed8.mcap |
| PP-SWR-032 | — | S12-b-VP-0-69e53aeef11a | VP-0 | 9 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-0-69e53aeef11a_seed9.mcap |
| PP-SWR-032 | — | S12-b-VP-0-69e53aeef11a | VP-0 | 10 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-0-69e53aeef11a_seed10.mcap |
| PP-SWR-032 | — | S12-b-VP-1-4b3e70a50a26 | VP-1 | 1 | — | 2 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-1-4b3e70a50a26_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-1-4b3e70a50a26 | VP-1 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-1-4b3e70a50a26_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-1-4b3e70a50a26 | VP-1 | 3 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-1-4b3e70a50a26_seed3.mcap |
| PP-SWR-032 | — | S12-b-VP-1-4b3e70a50a26 | VP-1 | 4 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-1-4b3e70a50a26_seed4.mcap |
| PP-SWR-032 | — | S12-b-VP-1-4b3e70a50a26 | VP-1 | 5 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-1-4b3e70a50a26_seed5.mcap |
| PP-SWR-032 | — | S12-b-VP-1-4b3e70a50a26 | VP-1 | 6 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-1-4b3e70a50a26_seed6.mcap |
| PP-SWR-032 | — | S12-b-VP-1-4b3e70a50a26 | VP-1 | 7 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-1-4b3e70a50a26_seed7.mcap |
| PP-SWR-032 | — | S12-b-VP-1-4b3e70a50a26 | VP-1 | 8 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-1-4b3e70a50a26_seed8.mcap |
| PP-SWR-032 | — | S12-b-VP-1-4b3e70a50a26 | VP-1 | 9 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-1-4b3e70a50a26_seed9.mcap |
| PP-SWR-032 | — | S12-b-VP-1-4b3e70a50a26 | VP-1 | 10 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-1-4b3e70a50a26_seed10.mcap |
| PP-SWR-032 | — | S12-b-VP-2-0962daddf5bd | VP-2 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-2-0962daddf5bd_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-2-0962daddf5bd | VP-2 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-2-0962daddf5bd_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-2-0962daddf5bd | VP-2 | 3 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-2-0962daddf5bd_seed3.mcap |
| PP-SWR-032 | — | S12-b-VP-2-0962daddf5bd | VP-2 | 4 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-2-0962daddf5bd_seed4.mcap |
| PP-SWR-032 | — | S12-b-VP-2-0962daddf5bd | VP-2 | 5 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-2-0962daddf5bd_seed5.mcap |
| PP-SWR-032 | — | S12-b-VP-2-0962daddf5bd | VP-2 | 6 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-2-0962daddf5bd_seed6.mcap |
| PP-SWR-032 | — | S12-b-VP-2-0962daddf5bd | VP-2 | 7 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-2-0962daddf5bd_seed7.mcap |
| PP-SWR-032 | — | S12-b-VP-2-0962daddf5bd | VP-2 | 8 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-2-0962daddf5bd_seed8.mcap |
| PP-SWR-032 | — | S12-b-VP-2-0962daddf5bd | VP-2 | 10 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-2-0962daddf5bd_seed10.mcap |
| PP-SWR-032 | — | S12-b-VP-3-984dbaa7f733 | VP-3 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-3-984dbaa7f733_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-3-984dbaa7f733 | VP-3 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-3-984dbaa7f733_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-3-984dbaa7f733 | VP-3 | 3 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-3-984dbaa7f733_seed3.mcap |
| PP-SWR-032 | — | S12-b-VP-3-984dbaa7f733 | VP-3 | 4 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-3-984dbaa7f733_seed4.mcap |
| PP-SWR-032 | — | S12-b-VP-3-984dbaa7f733 | VP-3 | 5 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-3-984dbaa7f733_seed5.mcap |
| PP-SWR-032 | — | S12-b-VP-3-984dbaa7f733 | VP-3 | 6 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-3-984dbaa7f733_seed6.mcap |
| PP-SWR-032 | — | S12-b-VP-3-984dbaa7f733 | VP-3 | 7 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-3-984dbaa7f733_seed7.mcap |
| PP-SWR-032 | — | S12-b-VP-3-984dbaa7f733 | VP-3 | 8 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-3-984dbaa7f733_seed8.mcap |
| PP-SWR-032 | — | S12-b-VP-3-984dbaa7f733 | VP-3 | 9 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-3-984dbaa7f733_seed9.mcap |
| PP-SWR-032 | — | S12-b-VP-3-984dbaa7f733 | VP-3 | 10 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-3-984dbaa7f733_seed10.mcap |
| PP-SWR-032 | — | S12-b-VP-4-a4945d3bcd67 | VP-4 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-4-a4945d3bcd67_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-4-a4945d3bcd67 | VP-4 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-4-a4945d3bcd67_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-4-a4945d3bcd67 | VP-4 | 3 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-4-a4945d3bcd67_seed3.mcap |
| PP-SWR-032 | — | S12-b-VP-4-a4945d3bcd67 | VP-4 | 4 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-4-a4945d3bcd67_seed4.mcap |
| PP-SWR-032 | — | S12-b-VP-4-a4945d3bcd67 | VP-4 | 5 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-4-a4945d3bcd67_seed5.mcap |
| PP-SWR-032 | — | S12-b-VP-4-a4945d3bcd67 | VP-4 | 6 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-4-a4945d3bcd67_seed6.mcap |
| PP-SWR-032 | — | S12-b-VP-4-a4945d3bcd67 | VP-4 | 7 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-4-a4945d3bcd67_seed7.mcap |
| PP-SWR-032 | — | S12-b-VP-4-a4945d3bcd67 | VP-4 | 8 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-4-a4945d3bcd67_seed8.mcap |
| PP-SWR-032 | — | S12-b-VP-4-a4945d3bcd67 | VP-4 | 9 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-4-a4945d3bcd67_seed9.mcap |
| PP-SWR-032 | — | S12-b-VP-4-a4945d3bcd67 | VP-4 | 10 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-4-a4945d3bcd67_seed10.mcap |
| PP-SWR-032 | — | S12-b-VP-5-2b777db332c0 | VP-5 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-5-2b777db332c0_seed1.mcap |
| PP-SWR-032 | — | S12-b-VP-5-2b777db332c0 | VP-5 | 2 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-5-2b777db332c0_seed2.mcap |
| PP-SWR-032 | — | S12-b-VP-5-2b777db332c0 | VP-5 | 3 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-5-2b777db332c0_seed3.mcap |
| PP-SWR-032 | — | S12-b-VP-5-2b777db332c0 | VP-5 | 4 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-5-2b777db332c0_seed4.mcap |
| PP-SWR-032 | — | S12-b-VP-5-2b777db332c0 | VP-5 | 5 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-5-2b777db332c0_seed5.mcap |
| PP-SWR-032 | — | S12-b-VP-5-2b777db332c0 | VP-5 | 6 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-5-2b777db332c0_seed6.mcap |
| PP-SWR-032 | — | S12-b-VP-5-2b777db332c0 | VP-5 | 7 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-5-2b777db332c0_seed7.mcap |
| PP-SWR-032 | — | S12-b-VP-5-2b777db332c0 | VP-5 | 8 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-5-2b777db332c0_seed8.mcap |
| PP-SWR-032 | — | S12-b-VP-5-2b777db332c0 | VP-5 | 10 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S12-b-VP-5-2b777db332c0_seed10.mcap |
| PP-SWR-032 | — | S13-a-VP-5-4d54367ca2b0 | VP-5 | 1 | — | 1 | <= 0 | Lần chưa báo COMPLETED trong T_end_late sau tick đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S13-a-VP-5-4d54367ca2b0_seed1.mcap |
| PP-SWR-090 | — | F02-e-S5a_at_elk_activep0.2-VP-5-ea248f5486c3 | VP-5 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/F02-e-S5a_at_elk_activep0.2-VP-5-ea248f5486c3_seed1.mcap |
| PP-SWR-090 | — | S5-a-VP-5-0a3fb4b675fb | VP-5 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S5-a-VP-5-0a3fb4b675fb_seed1.mcap |
| PP-SWR-090 | — | S5-c-VP-5-fc8939d6aa80 | VP-5 | 1 | — | 1 | <= 0 | Lần báo COMPLETED khi chưa đủ điều kiện | build/benchmark/20261115-1125-full-7495822/suite/mcap/S5-c-VP-5-fc8939d6aa80_seed1.mcap |
| PP-SWR-147 | — | F21-a-S5a_at_elk_activep0-VP-0-9b355e4bb1be | VP-0 | 1 | 15 | 80 | = 0 | Chu kỳ mất path khi còn biên khác đủ tin | build/benchmark/20261115-1125-full-7495822/suite/mcap/F21-a-S5a_at_elk_activep0-VP-0-9b355e4bb1be_seed1.mcap |
| PP-SWR-147 | — | F21-a-S5a_at_elk_activep0.2-VP-1-fcde26674096 | VP-1 | 1 | 10.9 | 244 | = 0 | Chu kỳ mất path khi còn biên khác đủ tin | build/benchmark/20261115-1125-full-7495822/suite/mcap/F21-a-S5a_at_elk_activep0.2-VP-1-fcde26674096_seed1.mcap |
| PP-SWR-147 | — | F21-b-S4a_at_lka_activep0-VP-0-d233f4471102 | VP-0 | 1 | 11.5 | 220 | = 0 | Chu kỳ mất path khi còn biên khác đủ tin | build/benchmark/20261115-1125-full-7495822/suite/mcap/F21-b-S4a_at_lka_activep0-VP-0-d233f4471102_seed1.mcap |
| PP-SWR-147 | — | F21-b-S4a_at_lka_activep0.2-VP-1-866e12ea7e09 | VP-1 | 1 | 12.15 | 194 | = 0 | Chu kỳ mất path khi còn biên khác đủ tin | build/benchmark/20261115-1125-full-7495822/suite/mcap/F21-b-S4a_at_lka_activep0.2-VP-1-866e12ea7e09_seed1.mcap |
| PP-SWR-147 | — | F21-b-S5a_at_elk_activep0-VP-2-97927cee94ce | VP-2 | 1 | 12.9 | 164 | = 0 | Chu kỳ mất path khi còn biên khác đủ tin | build/benchmark/20261115-1125-full-7495822/suite/mcap/F21-b-S5a_at_elk_activep0-VP-2-97927cee94ce_seed1.mcap |
| PP-SWR-147 | — | F21-d-S5a_at_elk_activep0-VP-0-16f865920e99 | VP-0 | 1 | 15 | 80 | = 0 | Chu kỳ mất path khi còn biên khác đủ tin | build/benchmark/20261115-1125-full-7495822/suite/mcap/F21-d-S5a_at_elk_activep0-VP-0-16f865920e99_seed1.mcap |
| PP-SWR-147 | — | F21-d-S5a_at_elk_activep0.2-VP-1-fc48f13c34a6 | VP-1 | 1 | 10.9 | 244 | = 0 | Chu kỳ mất path khi còn biên khác đủ tin | build/benchmark/20261115-1125-full-7495822/suite/mcap/F21-d-S5a_at_elk_activep0.2-VP-1-fc48f13c34a6_seed1.mcap |

## Trượt ngoài phạm vi chấm của ca (thông tin, không tính vào kết luận)

| Mức | Requirement | Ca | Seed | Giá trị | Ngưỡng |
|---|---|---|---|---|---|
| MINOR | PP-SWR-062 | S1-a-VP-0-c7c9506283e7 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-005 | S1-a-VP-0-7f05cc7c5b0e | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-006 | S1-a-VP-0-7f05cc7c5b0e | 1 | -0.6924 | >= 0 |
| BLOCKER | PP-SWR-061 | S1-a-VP-0-7f05cc7c5b0e | 1 | 0.06662 | <= 0.05 |
| BLOCKER | PP-SWR-051 | S1b-a-VP-0-a4d17e6ba3b6 | 1 | -23.37 | >= 0 |
| BLOCKER | PP-SWR-061 | S1b-a-VP-0-66e9cbe67698 | 1 | 0.05071 | <= 0.05 |
| BLOCKER | PP-SWR-061 | S1b-a-VP-1-44b94ef5689d | 1 | 0.0508 | <= 0.05 |
| BLOCKER | PP-SWR-051 | S1b-a-VP-0-ac0daf011b74 | 1 | -30.27 | >= 0 |
| BLOCKER | PP-SWR-051 | S1b-a-VP-0-37cc782177e5 | 1 | -21.93 | >= 0 |
| BLOCKER | PP-SWR-051 | S2-c-VP-0-b84bf321b14a | 1 | -0.1848 | >= 0 |
| BLOCKER | PP-SWR-051 | S2-c-VP-1-1db4613cf0cb | 1 | -0.1727 | >= 0 |
| BLOCKER | PP-SWR-051 | S2-c-VP-2-213efa4e998e | 1 | -0.2814 | >= 0 |
| BLOCKER | PP-SWR-051 | S2-c-VP-3-4e8dc883d0cd | 1 | -0.3422 | >= 0 |
| BLOCKER | PP-SWR-051 | S2-c-VP-4-255842c24eca | 1 | -0.3737 | >= 0 |
| BLOCKER | PP-SWR-051 | S2-c-VP-5-9ad0657941fb | 1 | -0.4967 | >= 0 |
| MINOR | PP-SWR-062 | S2-c-VP-5-9ad0657941fb | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-051 | S2-d-VP-5-a311ab7697a8 | 1 | -0.0234 | >= 0 |
| MINOR | PP-SWR-062 | S2-d-VP-5-a311ab7697a8 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-051 | S2-a-VP-0-1ea06043f20b | 1 | -0.2 | >= 0 |
| MINOR | PP-SWR-062 | S2-a-VP-0-1ea06043f20b | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-051 | S2-a-VP-0-a6c4f9820e1d | 1 | -0.2 | >= 0 |
| MINOR | PP-SWR-062 | S2-a-VP-0-a6c4f9820e1d | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-051 | S2-a-VP-0-fe5cf062c6f6 | 1 | -0.03056 | >= 0 |
| MINOR | PP-SWR-062 | S2-a-VP-0-fe5cf062c6f6 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-051 | S2-a-VP-0-b305a335d646 | 1 | -0.4015 | >= 0 |
| MINOR | PP-SWR-062 | S2-a-VP-0-b305a335d646 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-051 | S2-a-VP-2-519051739866 | 1 | -0.005 | >= 0 |
| MINOR | PP-SWR-062 | S2-a-VP-2-519051739866 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-051 | S2-a-VP-3-caece978d754 | 1 | -0.055 | >= 0 |
| MINOR | PP-SWR-062 | S2-a-VP-3-caece978d754 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-051 | S2-a-VP-4-02da6e2b654c | 1 | -0.077 | >= 0 |
| MINOR | PP-SWR-062 | S2-a-VP-4-02da6e2b654c | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-051 | S2-a-VP-0-21b24147331a | 1 | -0.08262 | >= 0 |
| MINOR | PP-SWR-062 | S2-a-VP-0-21b24147331a | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-051 | S2-a-VP-0-93e8a189cf03 | 1 | -0.1848 | >= 0 |
| BLOCKER | PP-SWR-051 | S2-a-VP-0-e7dc5d38df90 | 1 | -0.1848 | >= 0 |
| BLOCKER | PP-SWR-051 | S2-a-VP-3-2114cd91b6ba | 1 | -0.05907 | >= 0 |
| BLOCKER | PP-SWR-051 | S2-a-VP-4-c8d9d34d9974 | 1 | -0.09226 | >= 0 |
| BLOCKER | PP-SWR-051 | S2-a-VP-5-a4b1698efaa2 | 1 | -0.2153 | >= 0 |
| MINOR | PP-SWR-062 | S2-a-VP-5-a4b1698efaa2 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-051 | S2-a-VP-4-6546d3043f64 | 1 | -0.01122 | >= 0 |
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
| BLOCKER | PP-SWR-006 | S14-a-VP-0-d20fa935d75d | 1 | -0.2619 | >= 0 |
| BLOCKER | PP-SWR-005 | S14-a-VP-0-4710562d1da1 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-0-4710562d1da1 | 1 | -0.127 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-0-704a3b4d5f13 | 1 | -0.2618 | >= 0 |
| BLOCKER | PP-SWR-005 | S14-a-VP-0-1a76bdff67d1 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-0-1a76bdff67d1 | 1 | -0.1268 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-0-55aaa0559f68 | 1 | -0.2619 | >= 0 |
| BLOCKER | PP-SWR-005 | S14-a-VP-0-e60f61990a26 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-0-e60f61990a26 | 1 | -0.1269 | >= 0 |
| BLOCKER | PP-SWR-007 | S14-a-VP-0-e60f61990a26 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-1-5474a3d546d9 | 1 | -0.2661 | >= 0 |
| BLOCKER | PP-SWR-005 | S14-a-VP-1-b20ea61ca33d | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-1-b20ea61ca33d | 1 | -0.1271 | >= 0 |
| BLOCKER | PP-SWR-007 | S14-a-VP-1-b20ea61ca33d | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-061 | S14-a-VP-1-b20ea61ca33d | 1 | 0.0508 | <= 0.05 |
| BLOCKER | PP-SWR-006 | S14-a-VP-2-e5955077a54f | 1 | -0.2619 | >= 0 |
| BLOCKER | PP-SWR-005 | S14-a-VP-2-8cd97c102366 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-2-8cd97c102366 | 1 | -0.127 | >= 0 |
| BLOCKER | PP-SWR-007 | S14-a-VP-2-8cd97c102366 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-3-36b77c51567c | 1 | -0.2619 | >= 0 |
| BLOCKER | PP-SWR-005 | S14-a-VP-3-b2339f06659b | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-3-b2339f06659b | 1 | -0.1269 | >= 0 |
| BLOCKER | PP-SWR-007 | S14-a-VP-3-b2339f06659b | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-4-081e7f2841e4 | 1 | -0.2618 | >= 0 |
| BLOCKER | PP-SWR-005 | S14-a-VP-4-c420fa437f41 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-4-c420fa437f41 | 1 | -0.1269 | >= 0 |
| BLOCKER | PP-SWR-007 | S14-a-VP-4-c420fa437f41 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-5-b89abf3b879f | 1 | -0.2618 | >= 0 |
| BLOCKER | PP-SWR-005 | S14-a-VP-5-a9acbf87bdfa | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-5-a9acbf87bdfa | 1 | -0.1269 | >= 0 |
| BLOCKER | PP-SWR-007 | S14-a-VP-5-a9acbf87bdfa | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-005 | S14-a-VP-5-767403cd2057 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-5-767403cd2057 | 1 | -0.5525 | >= 0 |
| BLOCKER | PP-SWR-061 | S14-a-VP-5-767403cd2057 | 1 | 0.05006 | <= 0.05 |
| BLOCKER | PP-SWR-005 | S14-a-VP-1-842b126e250e | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-1-842b126e250e | 1 | -0.6625 | >= 0 |
| BLOCKER | PP-SWR-005 | S14-a-VP-5-8e96d7ae88a9 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-5-8e96d7ae88a9 | 1 | -0.9936 | >= 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-2-3a522ed9f6de | 1 | -0.1246 | >= 0 |
| BLOCKER | PP-SWR-005 | S14-a-VP-2-f2b38e633776 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-006 | S14-a-VP-2-f2b38e633776 | 1 | -0.3052 | >= 0 |
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
| MINOR | PP-SWR-090 | S4b-a-VP-1-e5e84ab5e4f1 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S4b-a-VP-1-1111785a98d3 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S4b-a-VP-2-6752f6ca660a | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S5-c-VP-5-fc8939d6aa80 | 1 | 1 | = 0 |
| MINOR | PP-SWR-062 | S5-a-VP-5-0a3fb4b675fb | 1 | 1 | = 0 |
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
| MINOR | PP-SWR-090 | S6-a-VP-0-ad9cdfc08b21 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S6-a-VP-3-86fcea031374 | 1 | 1 | <= 0 |
| BLOCKER | PP-SWR-039 | S6-a-VP-5-e47a241ce98f | 1 | 0.1328 | <= 0.05 |
| MINOR | PP-SWR-062 | S6-a-VP-5-e47a241ce98f | 1 | 2 | = 0 |
| MINOR | PP-SWR-090 | S6-a-VP-0-9770331bd650 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S7-c-VP-4-8cb3daf05752 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S7-c-VP-5-4bd69c0394ed | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S7-c-VP-5-4bd69c0394ed | 1 | 1 | = 0 |
| MINOR | PP-SWR-090 | S7-ncap-oncoming-left-6-VP-4-2a08dfdd25a8 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S7-ncap-oncoming-left-6-VP-5-cab30fbcc9c6 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S7-ncap-oncoming-left-6-VP-5-cab30fbcc9c6 | 1 | 1 | = 0 |
| MINOR | PP-SWR-090 | S7-a-VP-2-7cae34338773 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S7-a-VP-4-6dc0aec057a0 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S7-a-VP-5-4ca3819bac03 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S7-a-VP-5-4ca3819bac03 | 1 | 1 | = 0 |
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
| MINOR | PP-SWR-090 | S8-a-VP-2-4e231510c8be | 1 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S8-a-VP-4-0a748aa2bd15 | 1 | 1 | <= 0 |
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
| MINOR | PP-SWR-032 | S12-c-VP-0-425b042b9630 | 3 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-0-425b042b9630 | 4 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-0-425b042b9630 | 5 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-0-425b042b9630 | 6 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-0-425b042b9630 | 7 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-0-425b042b9630 | 8 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-0-425b042b9630 | 9 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-0-425b042b9630 | 10 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-1-c5f495806475 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-1-c5f495806475 | 2 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-1-c5f495806475 | 3 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-1-c5f495806475 | 4 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-1-c5f495806475 | 5 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-1-c5f495806475 | 6 | 1 | <= 0 |
| MINOR | PP-SWR-090 | S12-c-VP-1-c5f495806475 | 7 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-1-c5f495806475 | 8 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-1-c5f495806475 | 9 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-1-c5f495806475 | 10 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-2-dcd8acfe5043 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-2-dcd8acfe5043 | 2 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-2-dcd8acfe5043 | 3 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-2-dcd8acfe5043 | 4 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-2-dcd8acfe5043 | 5 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-2-dcd8acfe5043 | 6 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-2-dcd8acfe5043 | 7 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-2-dcd8acfe5043 | 8 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-2-dcd8acfe5043 | 9 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-2-dcd8acfe5043 | 10 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-3-4b7830a9f53c | 1 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-3-4b7830a9f53c | 2 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-3-4b7830a9f53c | 3 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-3-4b7830a9f53c | 4 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-3-4b7830a9f53c | 5 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-3-4b7830a9f53c | 6 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-3-4b7830a9f53c | 7 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-3-4b7830a9f53c | 8 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-3-4b7830a9f53c | 9 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-3-4b7830a9f53c | 10 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-4-406ed8c312c5 | 1 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-4-406ed8c312c5 | 2 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-4-406ed8c312c5 | 3 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-4-406ed8c312c5 | 4 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-4-406ed8c312c5 | 5 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-4-406ed8c312c5 | 6 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-4-406ed8c312c5 | 7 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-4-406ed8c312c5 | 8 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-4-406ed8c312c5 | 9 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-4-406ed8c312c5 | 10 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-5-7039c477036e | 1 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-5-7039c477036e | 2 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-5-7039c477036e | 3 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-5-7039c477036e | 4 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-5-7039c477036e | 5 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-5-7039c477036e | 6 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-5-7039c477036e | 7 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-5-7039c477036e | 8 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-5-7039c477036e | 9 | 1 | <= 0 |
| MINOR | PP-SWR-032 | S12-c-VP-5-7039c477036e | 10 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S13-a-VP-5-4d54367ca2b0 | 1 | 1 | = 0 |
| MINOR | PP-SWR-032 | S13-a-VP-5-45b8ad4e4d3f | 1 | 1 | <= 0 |
| MINOR | PP-SWR-062 | S13-a-VP-5-45b8ad4e4d3f | 1 | 1 | = 0 |
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
| BLOCKER | PP-SWR-086 | S16-c-VP-0-09788d14c807 | 1 | -0.3822 | >= -0.3 |
| BLOCKER | PP-SWR-086 | S16-c-VP-0-469390ef6e16 | 1 | -0.3824 | >= -0.3 |
| BLOCKER | PP-SWR-086 | S16-c-VP-2-8281c9cb32a8 | 1 | -0.3599 | >= -0.3 |
| BLOCKER | PP-SWR-086 | S16-c-VP-3-9dfbf07e224c | 1 | -0.389 | >= -0.3 |
| BLOCKER | PP-SWR-086 | S16-c-VP-4-ee53cd420735 | 1 | -0.4137 | >= -0.3 |
| BLOCKER | PP-SWR-085 | S16-c-VP-5-5e57f2403757 | 1 | -0.1121 | >= 0 |
| BLOCKER | PP-SWR-086 | S16-c-VP-5-5e57f2403757 | 1 | -0.4586 | >= -0.3 |
| MINOR | PP-SWR-062 | S16-c-VP-5-5e57f2403757 | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-086 | S16-c-VP-2-9b6afc0721d2 | 1 | -0.3596 | >= -0.3 |
| BLOCKER | PP-SWR-086 | S16-c-VP-3-660e5ed42bbc | 1 | -0.3887 | >= -0.3 |
| BLOCKER | PP-SWR-086 | S16-c-VP-4-d242c5eb4b26 | 1 | -0.4135 | >= -0.3 |
| BLOCKER | PP-SWR-085 | S16-c-VP-5-6310cfb86a58 | 1 | -0.1092 | >= 0 |
| BLOCKER | PP-SWR-086 | S16-c-VP-5-6310cfb86a58 | 1 | -0.4583 | >= -0.3 |
| MINOR | PP-SWR-062 | S16-c-VP-5-6310cfb86a58 | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-086 | S16-c-VP-2-c97a192181f9 | 1 | -0.3597 | >= -0.3 |
| BLOCKER | PP-SWR-086 | S16-c-VP-3-847b92f4682e | 1 | -0.3888 | >= -0.3 |
| BLOCKER | PP-SWR-086 | S16-c-VP-4-e33dfb18267c | 1 | -0.4136 | >= -0.3 |
| BLOCKER | PP-SWR-085 | S16-c-VP-5-7f19d55c07e8 | 1 | -0.1093 | >= 0 |
| BLOCKER | PP-SWR-086 | S16-c-VP-5-7f19d55c07e8 | 1 | -0.4584 | >= -0.3 |
| MINOR | PP-SWR-062 | S16-c-VP-5-7f19d55c07e8 | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-086 | S16-c-VP-0-969ec0778f21 | 1 | -0.3838 | >= -0.3 |
| BLOCKER | PP-SWR-086 | S16-c-VP-4-bf8d98a04332 | 1 | -0.415 | >= -0.3 |
| BLOCKER | PP-SWR-086 | S16-c-VP-2-7cd5066eb549 | 1 | -0.3634 | >= -0.3 |
| BLOCKER | PP-SWR-085 | S16-c-VP-5-d8a41775e97e | 1 | -0.1156 | >= 0 |
| BLOCKER | PP-SWR-086 | S16-c-VP-5-d8a41775e97e | 1 | -0.4717 | >= -0.3 |
| MINOR | PP-SWR-062 | S16-c-VP-5-d8a41775e97e | 1 | 2 | = 0 |
| BLOCKER | PP-SWR-086 | S16-c-VP-0-ea32bf0f8dbb | 1 | -0.3829 | >= -0.3 |
| BLOCKER | PP-SWR-086 | S16-c-VP-3-b89de1c40ab6 | 1 | -0.3881 | >= -0.3 |
| BLOCKER | PP-SWR-086 | S16-c-VP-3-cbb09e17c881 | 1 | -0.3924 | >= -0.3 |
| BLOCKER | PP-SWR-086 | S16-c-VP-2-b503e6281a4b | 1 | -0.3635 | >= -0.3 |
| BLOCKER | PP-SWR-086 | S16-c-VP-4-ea9366463c56 | 1 | -0.4124 | >= -0.3 |
| BLOCKER | PP-SWR-085 | S16-c-VP-5-418985fac807 | 1 | -0.1081 | >= 0 |
| BLOCKER | PP-SWR-086 | S16-c-VP-5-418985fac807 | 1 | -0.4562 | >= -0.3 |
| MINOR | PP-SWR-062 | S16-c-VP-5-418985fac807 | 1 | 2 | = 0 |
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
| BLOCKER | PP-SWR-051 | S17-a-VP-5-d4cf759aff3b | 1 | -0.242 | >= 0 |
| MINOR | PP-SWR-062 | S17-a-VP-5-d4cf759aff3b | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-051 | S17-a-VP-5-2f69dde79e39 | 1 | -0.2419 | >= 0 |
| MINOR | PP-SWR-062 | S17-a-VP-5-2f69dde79e39 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-051 | S17-a-VP-5-1bdf42c2e821 | 1 | -0.242 | >= 0 |
| MINOR | PP-SWR-062 | S17-a-VP-5-1bdf42c2e821 | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-061 | F08-b-S1c-VP-0-4ae7633cf949 | 1 | 0.05648 | <= 0.05 |
| BLOCKER | PP-SWR-061 | F08-b-S1c-VP-1-297eab73e001 | 1 | 0.05649 | <= 0.05 |
| BLOCKER | PP-SWR-061 | F08-b-S1c-VP-5-9d66d718191a | 1 | 0.05648 | <= 0.05 |

## Bộ theo khía cạnh

| Bộ | Khía cạnh | Lần chạy | Kết luận | BLOCKER | MAJOR | MINOR |
|---|---|---|---|---|---|---|
| B0 | Conformance | — | Đạt C1, C2; Tích hợp được | — | — | — |
| B1 | Nominal | 1537 | Không đạt | 6 | 0 | 0 |
| B2 | Regulatory | 618 | Không đạt | 33 | 0 | 7 |
| B3 | Performance limit | 675 | Không đạt | 150 | 0 | 3 |
| B4 | Robustness | 1746 | Không đạt | 106 | 0 | 138 |
| B5 | Degradation and refusal | 601 | Không đạt | 150 | 0 | 0 |
| B6 | Comfort | 1537 | Không đạt | 6 | 0 | 0 |
| B7 | Flexibility | 1470 | Không đạt | 48 | 0 | 19 |
| B8 | Compute | 3958 | Không đạt | 262 | 0 | 141 |

## Số lần chạy

```json
{
 "planned": 3958,
 "executed": 3958,
 "failed": 298,
 "failed_out_of_scope": 226,
 "errors": 0,
 "execution_faults": 0,
 "partial": false
}
```

## Flexibility

Cùng bản build và bộ calibration trên mọi profile (mục 8.3). Ô là giá trị xấu nhất của profile trên các ca chạy đủ mọi profile; **đậm** là profile tệ nhất của chỉ số. Bộ chạy là B7. Tỉ lệ đạt requirement: số requirement không trượt ở lần chạy nào của profile, chia số requirement được chấm trên profile đó.

| Profile | Lần chạy | Tỉ lệ đạt requirement | Requirement trượt | PP-SWR-002 a_y thêm vào lớn nhất khi đưa về giữa | PP-SWR-004 Jerk ngang RMS của path 0–1 s khi HWA lái | PP-SWR-004 Jerk ngang lớn nhất của path khi HWA lái (trung bình 0,5 s) | PP-SWR-004 Tốc độ quay vô lăng RMS khi HWA lái, vòng kín | PP-SWR-050 Lệch ngang của path so với tâm làn thật, 0–1 s, lớn nhất | PP-SWR-053 Thời gian đưa xe về giữa (lệch ≤ 0,1 m) | PP-SWR-057 Khoảng cách ngang nhỏ nhất từ thân xe tới xe lớn khi ngang hàng | PP-SWR-059 Thời gian từ lúc hết ngang hàng tới lúc lệch ≤ 0,1 m | PP-SWR-081 Thời lượng path LKA tới COMPLETED | PP-SWR-082 Thời lượng path ELK tới COMPLETED | PP-SWR-087 DTLE LKA nhỏ nhất |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VP-0 | 406 | 83.3% | PP-SWR-030, PP-SWR-032, PP-SWR-051, PP-SWR-086, PP-SWR-100 | 1.09 | 0.282 | 1.57 | 0.214 | **0.846** | 3.28 | 0.634 | 4.97 | 4.45 | 3.8 | -0.00941 |
| VP-1 | 300 | 90.3% | PP-SWR-032, PP-SWR-051, PP-SWR-086 | **1.21** | **0.287** | **1.57** | 0.211 | 0.773 | 3.23 | 0.611 | **5.02** | 4.17 | 3.5 | 0.00715 |
| VP-2 | 159 | 96.8% | PP-SWR-032 | 1.12 | 0.282 | 1.57 | 0.213 | 0.841 | 3.25 | 0.531 | 5.02 | 4.38 | 3.75 | 0.00277 |
| VP-3 | 158 | 90.0% | PP-SWR-030, PP-SWR-032, PP-SWR-085 | 1.07 | 0.282 | 1.57 | 0.214 | 0.845 | **3.29** | 0.479 | 5 | 4.45 | 3.82 | -0.00949 |
| VP-4 | 158 | 93.3% | PP-SWR-032, PP-SWR-086 | 1.06 | 0.282 | 1.57 | **0.215** | 0.845 | 3.06 | 0.452 | 5 | **4.52** | **3.88** | -0.00993 |
| VP-5 | 289 | 84.4% | PP-SWR-032, PP-SWR-051, PP-SWR-086, PP-SWR-090, PP-SWR-100 | 1.06 | 0.282 | 1.57 | 0.215 | 0.845 | 3.06 | **0.326** | 4 | 4.52 | 3.88 | **-0.0221** |

| Chỉ số | Độ chênh lớn nhất giữa profile | Độ chênh nhỏ nhất | Profile tệ nhất |
|---|---|---|---|
| PP-SWR-002 a_y thêm vào lớn nhất khi đưa về giữa | 0.149 | 0 | VP-1 |
| PP-SWR-004 Jerk ngang RMS của path 0–1 s khi HWA lái | 0.049 | 9.61e-10 | VP-1 |
| PP-SWR-004 Jerk ngang lớn nhất của path khi HWA lái (trung bình 0,5 s) | 0.271 | 0 | VP-1 |
| PP-SWR-004 Tốc độ quay vô lăng RMS khi HWA lái, vòng kín | 0.0264 | 0.000169 | VP-4 |
| PP-SWR-050 Lệch ngang của path so với tâm làn thật, 0–1 s, lớn nhất | 0.0999 | 0 | VP-0 |
| PP-SWR-053 Thời gian đưa xe về giữa (lệch ≤ 0,1 m) | 2.29 | 0 | VP-3 |
| PP-SWR-057 Khoảng cách ngang nhỏ nhất từ thân xe tới xe lớn khi ngang hàng | 0.308 | 0.242 | VP-5 |
| PP-SWR-059 Thời gian từ lúc hết ngang hàng tới lúc lệch ≤ 0,1 m | 4.85 | 1.02 | VP-1 |
| PP-SWR-081 Thời lượng path LKA tới COMPLETED | 1.1 | 0 | VP-4 |
| PP-SWR-082 Thời lượng path ELK tới COMPLETED | 1.4 | 0 | VP-4 |
| PP-SWR-087 DTLE LKA nhỏ nhất | 0.117 | 0.00805 | VP-5 |

Requirement đạt 100 % trên mọi profile: không (VP-0, VP-1, VP-2, VP-3, VP-4, VP-5)

## Thời gian tính

3502333 chu kỳ. p95 ≤ 2 ms, p99 ≤ 3.16 ms (cận trên của bin), lớn nhất 2.44e+03 ms. Đo trên máy chạy SIL, gồm adapter; không khẳng định thời gian trên ECU (mục 9.1).

![Thời gian tính](figures/compute.png)

## DTLE theo v_lat

| Kịch bản | v_lat [m/s] | DTLE nhỏ nhất [m] |
|---|---|---|
| S4 | 0 | 0.0679 |
| S4 | 0.2 | 0.0983 |
| S4 | 0.21 | 0.111 |
| S4 | 0.229 | 0.115 |
| S4 | 0.269 | 0.12 |
| S4 | 0.299 | 0.134 |
| S4 | 0.3 | 0.127 |
| S4 | 0.305 | 0.128 |
| S4 | 0.342 | 0.144 |
| S4 | 0.363 | 0.142 |
| S4 | 0.389 | 0.147 |
| S4 | 0.4 | 0.147 |
| S4 | 0.419 | 0.161 |
| S4 | 0.443 | 0.156 |
| S4 | 0.465 | 0.174 |
| S4 | 0.479 | 0.177 |
| S4 | 0.5 | 0.0633 |
| S4 | 0.504 | 0.161 |
| S4 | 0.537 | 0.0625 |
| S4 | 0.554 | 0.109 |
| S4 | 0.58 | 0.0966 |
| S4 | 0.6 | -0.0221 |
| S4b | 0.2 | 0.0916 |
| S4b | 0.217 | 0.0958 |
| S4b | 0.239 | 0.11 |
| S4b | 0.255 | 0.1 |
| S4b | 0.261 | 0.118 |
| S4b | 0.299 | 0.137 |
| S4b | 0.3 | 0.108 |
| S4b | 0.307 | 0.128 |
| S4b | 0.338 | 0.124 |
| S4b | 0.356 | 0.147 |
| S4b | 0.363 | 0.149 |
| S4b | 0.393 | 0.146 |
| S4b | 0.401 | 0.16 |
| S4b | 0.439 | 0.137 |
| S4b | 0.444 | 0.146 |
| S4b | 0.474 | 0.15 |
| S4b | 0.492 | 0.173 |
| S4b | 0.513 | 0.156 |
| S4b | 0.529 | 0.158 |
| S4b | 0.544 | 0.163 |
| S4b | 0.563 | 0.171 |
| S4b | 0.586 | 0.174 |
| S4b | 0.6 | 0.0394 |
| S5 | 0.2 | 0.0326 |
| S5 | 0.21 | 0.0425 |
| S5 | 0.229 | 0.0426 |
| S5 | 0.269 | 0.0409 |
| S5 | 0.299 | 0.0458 |
| S5 | 0.3 | 0.0341 |
| S5 | 0.305 | 0.0437 |
| S5 | 0.342 | 0.0339 |
| S5 | 0.363 | 0.0481 |
| S5 | 0.389 | 0.0485 |
| S5 | 0.4 | 0.0314 |
| S5 | 0.419 | 0.0375 |
| S5 | 0.443 | 0.0469 |
| S5 | 0.465 | 0.0473 |
| S5 | 0.479 | 0.0451 |
| S5 | 0.5 | 0.0396 |
| S5 | 0.504 | 0.047 |
| S5 | 0.537 | 0.0494 |
| S5 | 0.554 | 0.0934 |
| S5 | 0.58 | -0.668 |
| S5 | 0.6 | 0.0408 |
| S6 | 0.2 | 0.0262 |
| S6 | 0.205 | 0.0347 |
| S6 | 0.261 | 0.0333 |
| S6 | 0.292 | 0.0372 |
| S6 | 0.3 | 0.0288 |
| S6 | 0.304 | 0.0287 |
| S6 | 0.357 | 0.0365 |
| S6 | 0.393 | 0.0371 |
| S6 | 0.4 | 0.0262 |
| S6 | 0.418 | 0.0368 |
| S6 | 0.449 | 0.0401 |
| S6 | 0.484 | 0.0328 |
| S6 | 0.5 | 0.0324 |
| S6 | 0.524 | 0.0387 |
| S6 | 0.538 | 0.0387 |
| S6 | 0.593 | 0.0964 |
| S6 | 0.6 | -0.0022 |
| S7 | 0.2 | -0.163 |
| S7 | 0.21 | -0.13 |
| S7 | 0.229 | -0.0134 |
| S7 | 0.269 | 0.125 |
| S7 | 0.299 | 0.136 |
| S7 | 0.3 | 0.134 |
| S7 | 0.305 | 0.136 |
| S7 | 0.342 | 0.147 |
| S7 | 0.363 | 0.153 |
| S7 | 0.389 | 0.16 |
| S7 | 0.4 | 0.156 |
| S7 | 0.419 | 0.169 |
| S7 | 0.443 | 0.173 |
| S7 | 0.465 | 0.184 |
| S7 | 0.479 | 0.188 |
| S7 | 0.5 | 0.186 |
| S7 | 0.504 | 0.193 |
| S7 | 0.537 | 0.194 |
| S7 | 0.554 | 0.2 |
| S7 | 0.58 | 0.205 |
| S7 | 0.6 | 0.0984 |
| S8 | 0.2 | 0.0465 |
| S8 | 0.21 | 0.108 |
| S8 | 0.229 | 0.113 |
| S8 | 0.269 | 0.125 |
| S8 | 0.299 | 0.0623 |
| S8 | 0.3 | 0.0497 |
| S8 | 0.305 | 0.136 |
| S8 | 0.342 | 0.147 |
| S8 | 0.363 | 0.153 |
| S8 | 0.389 | 0.0658 |
| S8 | 0.4 | 0.0546 |
| S8 | 0.419 | 0.169 |
| S8 | 0.443 | 0.173 |
| S8 | 0.465 | 0.184 |
| S8 | 0.479 | 0.188 |
| S8 | 0.5 | 0.0571 |
| S8 | 0.504 | 0.193 |
| S8 | 0.537 | 0.0695 |
| S8 | 0.554 | 0.2 |
| S8 | 0.58 | 0.205 |
| S8 | 0.6 | 0.0624 |
| S8 | 0.7 | 0.0616 |
| S8b | 0.5 | -0.319 |
| S8c | 0.4 | 0.279 |

![DTLE theo v_lat](figures/dtle_v_lat.png)

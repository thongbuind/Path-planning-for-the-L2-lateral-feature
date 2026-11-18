# Lần chạy chính thức

Mỗi dòng do `--record` của `eval.runner`, `eval.matrix`, `eval.sweep`, `eval.study` thêm vào. Không sửa tay, trừ cột Ghi chú.

| Run ID | Loại | Đối tượng | Commit | Thư viện | Kết quả | Ghi chú |
|---|---|---|---|---|---|---|
| 20261111-1024-matrix-M1-b9e5d4d | matrix | M1 | b9e5d4d | libpp_planner trước `pp_version()` | 396 lần chạy; 0 trượt trong phạm vi; 38 trượt PP-SWR-051 ngoài phạm vi | Đăng ký lại sau khi chạy: chạy lúc 10:24 trước commit; mã nguồn không sửa sau lần build dùng cho M1 (kiểm theo thời điểm sửa file); manifest dựng lại. PP-TS-002, PP-PR-001, PP-PR-003 |
| 20261111-1443-suite-regression-ef8bf4b | suite | regression | ef8bf4b | calibration 804d3632d85e | 1428 lần chạy; 168 trượt trong phạm vi (100: 150, 051: 36, 006: 12, 101: 3); 265 trượt ngoài phạm vi | PP-PR-005 (F01 trên S1c, 84), PP-PR-004 (S14e), PP-PR-007 (S14a 130 km/h), PP-PR-008 (S1ba 130 km/h), PP-PR-001 (F06 trên S1c) |
| 20261112-1150-study-PP-TS-014-fe420b5 | study | PP-TS-014 | fe420b5 | calibration 9471757b7105, 098b51e85498, 4590870545f2, 9471757b7105, 098b51e85498, 4590870545f2 | Đứng đầu ở test: V0-m7 | |
| 20261112-1239-matrix-Q4-1bfd184 | matrix | Q4 | 1bfd184 | calibration 1b9b7d6367e8 | 49 lần chạy; 13 trượt trong phạm vi; 13 có trượt ngoài phạm vi | |
| 20261112-1240-matrix-M1-1bfd184 | matrix | M1 | 1bfd184 | calibration 1b9b7d6367e8 | 396 lần chạy; 12 trượt trong phạm vi; 38 có trượt ngoài phạm vi | |
| 20261112-1254-matrix-M1-8418fd9 | matrix | M1 | 8418fd9 | calibration 1b9b7d6367e8 | 396 lần chạy; 0 trượt trong phạm vi; 38 có trượt ngoài phạm vi | |
| 20261112-1418-matrix-Q1-5e8cabc | matrix | Q1 | 5e8cabc | calibration 1b9b7d6367e8 | 24 lần chạy; 0 trượt trong phạm vi; 0 có trượt ngoài phạm vi | |
| 20261112-1418-matrix-Q2-5e8cabc | matrix | Q2 | 5e8cabc | calibration 1b9b7d6367e8 | 12 lần chạy; 0 trượt trong phạm vi; 0 có trượt ngoài phạm vi | |
| 20261112-1419-matrix-Q3-5e8cabc | matrix | Q3 | 5e8cabc | calibration 1b9b7d6367e8 | 12 lần chạy; 2 trượt trong phạm vi; 0 có trượt ngoài phạm vi | |
| 20261112-1421-suite-smoke-0d4f9f2 | suite | smoke | 0d4f9f2 | calibration 1b9b7d6367e8 | {"planned": 113, "executed": 113, "failed": 9, "failed_out_of_scope": 15, "errors": 0, "partial": false} | |
| 20261112-1429-matrix-Q3-6b290e9 | matrix | Q3 | 6b290e9 | calibration 1b9b7d6367e8 | 12 lần chạy; 2 trượt trong phạm vi; 0 có trượt ngoài phạm vi | |
| 20261112-1430-matrix-Q3-f94030c | matrix | Q3 | f94030c | calibration 1b9b7d6367e8 | 12 lần chạy; 0 trượt trong phạm vi; 0 có trượt ngoài phạm vi | |
| 20261112-1436-matrix-Q1-aab64f2 | matrix | Q1 | aab64f2 | calibration 1b9b7d6367e8 | 24 lần chạy; 0 trượt trong phạm vi; 0 có trượt ngoài phạm vi | |
| 20261112-1437-matrix-Q2-aab64f2 | matrix | Q2 | aab64f2 | calibration 1b9b7d6367e8 | 12 lần chạy; 0 trượt trong phạm vi; 0 có trượt ngoài phạm vi | |
| 20261112-1437-matrix-Q3-aab64f2 | matrix | Q3 | aab64f2 | calibration 1b9b7d6367e8 | 12 lần chạy; 0 trượt trong phạm vi; 0 có trượt ngoài phạm vi | |
| 20261112-1437-matrix-M1-aab64f2 | matrix | M1 | aab64f2 | calibration 1b9b7d6367e8 | 396 lần chạy; 0 trượt trong phạm vi; 38 có trượt ngoài phạm vi | |
| 20261112-1445-suite-smoke-aab64f2 | suite | smoke | aab64f2 | calibration 1b9b7d6367e8 | {"planned": 113, "executed": 113, "failed": 9, "failed_out_of_scope": 15, "errors": 0, "partial": false} | |
| 20261113-1803-suite-regression-3c31309 | suite | regression | 3c31309 | calibration 06a80cfe5088 | Không đạt; {"executed": 2073, "failed": 351, "errors": 0} | Xác nhận PP-PR-010, 016, 017, 019, 024–027 (012, 015 một phần); hồi quy PP-TS-016 (chưa đóng). Trượt mới mở PP-PR-030 đến 039 |
| 20261113-1851-matrix-M1-5afcaf5 | matrix | M1 | 5afcaf5 | calibration 06a80cfe5088 | Không đạt; 396 lần chạy; 10 trượt trong phạm vi; 28 có trượt ngoài phạm vi | Hồi quy PP-TS-015: 10 trượt 051 ở F02 e, F06 (phạm vi mới). Commit chỉ thêm .gitignore so với 3c31309 |
| 20261113-1858-matrix-PP-TS-002-5afcaf5 | matrix | PP-TS-002 | 5afcaf5 | calibration 06a80cfe5088 | Đạt trong phạm vi đã thử; 24 lần chạy; 0 trượt trong phạm vi; 0 có trượt ngoài phạm vi | PP-TS-002 điều kiện mở lại: S1b d, ACC on 0/12 chạm vạch |
| 20261113-2255-suite-regression-e99cf08 | suite | regression | e99cf08 | calibration 06a80cfe5088 | Không đạt; {"executed": 2073, "failed": 313, "errors": 0} | Xác nhận PP-PR-029, 032; hồi quy PP-TS-017. Không có trượt mới trong phạm vi; ngoài phạm vi mới: 003 ở S17 b (PP-PR-040) |
| 20261113-2330-matrix-PP-PR-032-e99cf08 | matrix | PP-PR-032 | e99cf08 | calibration 06a80cfe5088 | Không đạt; 42 lần chạy; 4 trượt trong phạm vi; 15 có trượt ngoài phạm vi | PP-PR-032: chỉ còn S16 d (PP-PR-038) |
| 20261113-2339-matrix-PP-PR-032-1014d20 | matrix | PP-PR-032 | 1014d20 | calibration 06a80cfe5088 | Không đạt; 42 lần chạy; 4 trượt trong phạm vi; 15 có trượt ngoài phạm vi | PP-PR-040: jerk S17 b 4,999995 m/s³, 003 hết trượt; còn S16 d (PP-PR-038) |
| 20261113-2341-suite-regression-1014d20 | suite | regression | 1014d20 | calibration 06a80cfe5088 | Không đạt; {"executed": 2073, "failed": 313, "errors": 0} | Đóng PP-PR-040: không trượt mới so với e99cf08; 003 ở S17 hết trượt |
| 20261114-1021-suite-regression-d7ed84c | suite | regression | d7ed84c | calibration d532993b1b2f | Không đạt; {"executed": 2073, "failed": 216, "errors": 0} | Xác nhận PP-PR-041, 042, 038 (F04); B2 chỉ còn S14 e. Trượt mới: F02 e lúc LKA, 085 (PP-PR-044). F21 c, d trên S1c chạy đường khác ca chủ (PP-PR-045) |
| 20261114-1857-study-PP-TS-001-13913da | study | PP-TS-001 | 13913da | calibration 423527103319, 423527103319 | Đứng đầu ở test: J0-shape (14 so với 23 lượt trượt) | PP-TS-001: J0-shape hết trượt 051 ở F06 a, b, e; F06 d, F03 c còn trượt; không trượt mới |
| 20261114-1934-study-PP-TS-003-272a711 | study | PP-TS-003 | 272a711 | calibration 423527103319, 423527103319, 423527103319, 423527103319, b621164e47a8 | Đứng đầu ở test: V0b | V0b ít trượt nhất (3 / 6); chỉ còn S14 e (PP-PR-004). T10 trước T4 gỡ PP-PR-005, 006 |
| 20261114-1952-suite-regression-0776bad | suite | regression | 0776bad | calibration d532993b1b2f | Không đạt; {"executed": 2079, "failed": 134, "errors": 0} | Xác nhận PP-TS-003 V0b (PP-PR-005, 006), PP-PR-030, 031, 034, 035; F06 a, b, e (PP-TS-001). 100: 113 → 30. Trượt mới: S14 d 153, F06 c 051, F06 d lúc LKA/ELK 086, G01 S4c 030, F08 b, S1b a 007 |
| 20261114-2153-suite-regression-71fb7c1 | suite | regression | 71fb7c1 | calibration d532993b1b2f | Không đạt; {"executed": 2079, "failed": 120, "errors": 0} || Xác nhận PP-PR-047 (S14 d), 048 bản 1 (F06 c), 052 (G01 S4c 030), 053 (F20 a). Trượt mới: S12 c 088, 085, 100 (PP-PR-055). 032 tăng 37 → 43: G01 S4c chuyển từ 030 sang 032 (PP-TS-018) |
| 20261114-2252-suite-regression-98a122b | suite | regression | 98a122b | calibration d532993b1b2f | Không đạt; {"executed": 2079, "failed": 115, "errors": 0} || Xác nhận PP-PR-055 (S12 c hết trượt) và đóng 047, 048 (F06 c), 052, 053. Không có trượt mới. Còn lại: 051 47, 032 44, 100 30, 102 12, 101 7 |
| 20261115-1126-suite-full-7495822 | suite | full | 7495822 | calibration d532993b1b2f | Không đạt; {"executed": 3958, "failed": 298, "errors": 0} | |
| 20261116-1548-study-PP-TS-020-04ae8c5 | study | PP-TS-020 | 04ae8c5 | calibration 710fc9d888e0, 80dfc43635bd, 1f38dc9fe751, 7e727740ab76 | Đứng đầu ở test: V1b | |
| 20261116-1607-study-PP-TS-020-d1d50de | study | PP-TS-020 | d1d50de | calibration 710fc9d888e0, 80dfc43635bd, 1f38dc9fe751, 7e727740ab76, 1f38dc9fe751 | Đứng đầu ở test: V1b | |
| 20261116-1702-study-PP-TS-021-f51044d | study | PP-TS-021 | f51044d | calibration 710fc9d888e0, 447a7c5019ae, 8dda0f75cc6d, 710fc9d888e0, 8dda0f75cc6d | Đứng đầu ở test: V2 | |
| 20261116-1724-study-PP-TS-021-0a1d8c9 | study | PP-TS-021 | 0a1d8c9 | calibration 710fc9d888e0, 447a7c5019ae, 8dda0f75cc6d, 710fc9d888e0, 8dda0f75cc6d, d089659bf0fe, 1eeb6681144f | Đứng đầu ở test: V2 | |
| 20261116-1748-study-PP-TS-021-8726b80 | study | PP-TS-021 | 8726b80 | calibration d81989ff72cf, 7c5e808c0ed8, 36447978c6e6, d81989ff72cf, 36447978c6e6, fb3d94ddeaaf, 0338a4e0c740, 7c5e808c0ed8, e0ec4d9230e2 | Đứng đầu ở test: V7 | |
| 20261117-0908-suite-regression-c56f0bf | suite | regression | c56f0bf | calibration 418f18b44dc0 | Không đạt; {"executed": 2085, "failed": 93, "errors": 0} | |
| 20261117-1217-suite-regression-d2e7d27 | suite | regression | d2e7d27 | calibration 418f18b44dc0 | Không đạt; {"executed": 2085, "failed": 90, "errors": 0} | |
| 20261117-1315-study-PP-TS-022-d2e7d27 | study | PP-TS-022 | d2e7d27 | calibration c0c928734b4e, c0c928734b4e | Đứng đầu ở test: V1 | |
| 20261117-2048-suite-full-40cc22b | suite | full | 40cc22b | calibration 418f18b44dc0 | Không đạt; {"executed": 3964, "failed": 204, "errors": 0} | |
| 20261118-1546-suite-regression-edb02b8 | suite | regression | edb02b8 | calibration 6b03f0759737, 6b03f0759737 | Không đạt; {"executed": 2309, "failed": 203, "errors": 0} | |
| 20261118-1712-study-PP-TS-026-3875f8e | study | PP-TS-026 | 3875f8e | calibration 553e26851383, 553e26851383, a7e691e85462, a7e691e85462, d625708cf2d5, d625708cf2d5, a0262f931091, a0262f931091, eccb89e26d9c, eccb89e26d9c | Đứng đầu ở test: V3 | |
| 20261118-1950-suite-regression-e395662 | suite | regression | e395662 | calibration c9618c64d42e, c9618c64d42e | Không đạt; {"executed": 2309, "failed": 90, "errors": 0} | |
| 20261118-2030-suite-regression-e3158a5 | suite | regression | e3158a5 | calibration c9618c64d42e, c9618c64d42e | Không đạt; {"executed": 2309, "failed": 72, "errors": 0} | |
| 20261118-2127-study-PP-TS-020-ac82bb3 | study | PP-TS-020 | ac82bb3 | calibration 0b2fc0aea548, 0b2fc0aea548, b91f2247e78f, b91f2247e78f, 422bdb441e35, 422bdb441e35, 42aa4a2f6fc0, 42aa4a2f6fc0, 422bdb441e35, 422bdb441e35 | Đứng đầu ở test: V1c | |

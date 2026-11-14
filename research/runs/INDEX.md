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

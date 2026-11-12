# Lần chạy chính thức

Mỗi dòng do `--record` của `eval.runner`, `eval.matrix`, `eval.sweep`, `eval.study` thêm vào. Không sửa tay, trừ cột Ghi chú.

| Run ID | Loại | Đối tượng | Commit | Thư viện | Kết quả | Ghi chú |
|---|---|---|---|---|---|---|
| 20261111-1024-matrix-M1-b9e5d4d | matrix | M1 | b9e5d4d | libpp_planner trước `pp_version()` | 396 lần chạy; 0 trượt trong phạm vi; 38 trượt PP-SWR-051 ngoài phạm vi | Đăng ký lại sau khi chạy: chạy lúc 10:24 trước commit; mã nguồn không sửa sau lần build dùng cho M1 (kiểm theo thời điểm sửa file); manifest dựng lại. PP-TS-002, PP-PR-001, PP-PR-003 |
| 20261111-1443-suite-regression-ef8bf4b | suite | regression | ef8bf4b | calibration 804d3632d85e | 1428 lần chạy; 168 trượt trong phạm vi (100: 150, 051: 36, 006: 12, 101: 3); 265 trượt ngoài phạm vi | PP-PR-005 (F01 trên S1c, 84), PP-PR-004 (S14e), PP-PR-007 (S14a 130 km/h), PP-PR-008 (S1ba 130 km/h), PP-PR-001 (F06 trên S1c) |
| 20261112-1150-study-PP-TS-014-fe420b5 | study | PP-TS-014 | fe420b5 | calibration 9471757b7105, 098b51e85498, 4590870545f2, 9471757b7105, 098b51e85498, 4590870545f2 | Đứng đầu ở test: V0-m7 | |
| 20261112-1239-matrix-Q4-1bfd184 | matrix | Q4 | 1bfd184 | calibration 1b9b7d6367e8 | 49 lần chạy; 13 trượt trong phạm vi; 13 có trượt ngoài phạm vi | |
| 20261112-1240-matrix-M1-1bfd184 | matrix | M1 | 1bfd184 | calibration 1b9b7d6367e8 | 396 lần chạy; 12 trượt trong phạm vi; 38 có trượt ngoài phạm vi | |

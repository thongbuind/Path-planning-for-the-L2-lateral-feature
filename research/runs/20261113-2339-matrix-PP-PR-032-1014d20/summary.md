# Kết luận: Không đạt

- Planner: pp_planner 0.2.0 commit 1014d2042d78 calibration 06a80cfe5088 t7 quintic (b0e56591bf91)
- Tích hợp được: có
- Đã chạy: 42 lần chạy; trượt BLOCKER 8, MAJOR 0, MINOR 0
- Kết luận chỉ đúng trong phạm vi đã thử, không phải bằng chứng an toàn (Software Qualification Test Specification 3).

## Trượt BLOCKER

| Requirement | Safety goal | Ca | Profile | Seed | Trượt đầu tiên [s] | Giá trị | Ngưỡng | Chi tiết | MCAP |
|---|---|---|---|---|---|---|---|---|---|
| PP-SWR-030 | SG-01 | S16d | VP-0 | 1 | — | — | — | ELK: có REQUEST nhưng thiếu path can thiệp hợp lệ | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/matrix/PP-PR-032/mcap/S16d_off_VP-0_seed1.mcap |
| PP-SWR-030 | SG-01 | S16d | VP-3 | 1 | — | — | — | ELK: có REQUEST nhưng thiếu path can thiệp hợp lệ | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/matrix/PP-PR-032/mcap/S16d_off_VP-3_seed1.mcap |
| PP-SWR-100 | SG-04 | S16d | VP-1 | 1 | 11.18 | 1.337 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/matrix/PP-PR-032/mcap/S16d_off_VP-1_seed1.mcap |
| PP-SWR-100 | SG-04 | S16d | VP-2 | 1 | 11.33 | 0.425 | <= 0.05 | Lệch ngang giữa hai path liên tiếp [m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/matrix/PP-PR-032/mcap/S16d_off_VP-2_seed1.mcap |
| PP-SWR-101 | SG-04 | S16d | VP-1 | 1 | 11.43 | 0.03352 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/matrix/PP-PR-032/mcap/S16d_off_VP-1_seed1.mcap |
| PP-SWR-101 | SG-04 | S16d | VP-2 | 1 | 11.33 | 0.01253 | <= 0.005 | Lệch hướng giữa hai path liên tiếp [rad] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/matrix/PP-PR-032/mcap/S16d_off_VP-2_seed1.mcap |
| PP-SWR-102 | SG-04 | S16d | VP-1 | 1 | 11.43 | 0.003635 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/matrix/PP-PR-032/mcap/S16d_off_VP-1_seed1.mcap |
| PP-SWR-102 | SG-04 | S16d | VP-2 | 1 | 11.33 | 0.001368 | <= 0.0003 | Lệch độ cong giữa hai path liên tiếp [1/m] | /Users/thongbui.nd/Documents/Tài liệu - Nidai/Thong Bui/vinuni/ADAS/g1-path-planning/build/matrix/PP-PR-032/mcap/S16d_off_VP-2_seed1.mcap |

## Trượt ngoài phạm vi chấm của ca (thông tin, không tính vào kết luận)

| Mức | Requirement | Ca | Seed | Giá trị | Ngưỡng |
|---|---|---|---|---|---|
| BLOCKER | PP-SWR-051 | S17b | 1 | -0.01948 | >= 0 |
| BLOCKER | PP-SWR-051 | S17b | 1 | -0.04464 | >= 0 |
| BLOCKER | PP-SWR-051 | S17b | 1 | -0.115 | >= 0 |
| BLOCKER | PP-SWR-051 | S17b | 1 | -0.1767 | >= 0 |
| BLOCKER | PP-SWR-051 | S17b | 1 | -0.2096 | >= 0 |
| BLOCKER | PP-SWR-051 | S17b | 1 | -0.3326 | >= 0 |
| MINOR | PP-SWR-062 | S17b | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-051 | S17c | 1 | -5.581 | >= 0 |
| BLOCKER | PP-SWR-051 | S17c | 1 | -5.627 | >= 0 |
| BLOCKER | PP-SWR-051 | S17c | 1 | -5.691 | >= 0 |
| BLOCKER | PP-SWR-051 | S17c | 1 | -5.743 | >= 0 |
| BLOCKER | PP-SWR-051 | S17c | 1 | -5.765 | >= 0 |
| BLOCKER | PP-SWR-051 | S17c | 1 | -5.888 | >= 0 |
| MINOR | PP-SWR-062 | S17c | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-051 | S17d | 1 | -0.006265 | >= 0 |
| MINOR | PP-SWR-062 | S17d | 1 | 1 | = 0 |
| BLOCKER | PP-SWR-086 | S16d | 1 | -0.3115 | >= -0.3 |
| BLOCKER | PP-SWR-085 | S16d | 1 | -0.008456 | >= 0 |
| BLOCKER | PP-SWR-086 | S16d | 1 | -0.4219 | >= -0.3 |

## Bộ theo khía cạnh

| Bộ | Khía cạnh | Lần chạy | Kết luận | BLOCKER | MAJOR | MINOR |
|---|---|---|---|---|---|---|
| B0 | Conformance | — | Đạt C1, C2; Tích hợp được | — | — | — |
| B1 | Nominal | 30 | Không đạt | 8 | 0 | 0 |
| B2 | Regulatory | 6 | Đạt trong phạm vi đã thử | 0 | 0 | 0 |
| B3 | Performance limit | 6 | Đạt trong phạm vi đã thử | 0 | 0 | 0 |
| B4 | Robustness | 6 | Đạt trong phạm vi đã thử | 0 | 0 | 0 |
| B5 | Degradation and refusal | 0 | không có ca | — | — | — |
| B6 | Comfort | 30 | Không đạt | 8 | 0 | 0 |
| B7 | Flexibility | 0 | không có ca | — | — | — |
| B8 | Compute | 42 | Không đạt | 8 | 0 | 0 |

## Matrix PP-PR-032

42 runs; 4 with an in-scope failure.

| Chạy | ACC | Profile | Seed | Trượt (trong phạm vi) | Trượt ngoài phạm vi | Lệch xe [m] | DLC min [m] | a_y cần tại xe [m/s²] | v min [m/s] | Báo trước [s] |
|---|---|---|---|---|---|---|---|---|---|---|
| S17a | off | VP-0 | 1 | — | — | 0.298 | 0.507 | 0 | 25 | — |
| S17a | off | VP-1 | 1 | — | — | 0.278 | 0.496 | 0 | 25 | — |
| S17a | off | VP-2 | 1 | — | — | 0.294 | 0.406 | 0 | 25 | — |
| S17a | off | VP-3 | 1 | — | — | 0.3 | 0.351 | 0 | 25 | — |
| S17a | off | VP-4 | 1 | — | — | 0.305 | 0.324 | 0 | 25 | — |
| S17a | off | VP-5 | 1 | — | — | 0.305 | 0.201 | 0 | 25 | — |
| S17b | off | VP-0 | 1 | — | PP-SWR-051 | 0.829 | -0.0195 | 0 | 25 | — |
| S17b | off | VP-1 | 1 | — | PP-SWR-051 | 0.821 | -0.0446 | 0 | 25 | — |
| S17b | off | VP-2 | 1 | — | PP-SWR-051 | 0.819 | -0.115 | 0 | 25 | — |
| S17b | off | VP-3 | 1 | — | PP-SWR-051 | 0.832 | -0.177 | 0 | 25 | — |
| S17b | off | VP-4 | 1 | — | PP-SWR-051 | 0.843 | -0.21 | 0 | 25 | — |
| S17b | off | VP-5 | 1 | — | PP-SWR-051, PP-SWR-062 | 0.843 | -0.333 | 0 | 25 | — |
| S17c | off | VP-0 | 1 | — | PP-SWR-051 | 0.293 | -5.58 | 1.25 | 25 | — |
| S17c | off | VP-1 | 1 | — | PP-SWR-051 | 0.277 | -5.63 | 1.25 | 25 | — |
| S17c | off | VP-2 | 1 | — | PP-SWR-051 | 0.288 | -5.69 | 1.25 | 25 | — |
| S17c | off | VP-3 | 1 | — | PP-SWR-051 | 0.294 | -5.74 | 1.25 | 25 | — |
| S17c | off | VP-4 | 1 | — | PP-SWR-051 | 0.3 | -5.76 | 1.25 | 25 | — |
| S17c | off | VP-5 | 1 | — | PP-SWR-051, PP-SWR-062 | 0.3 | -5.89 | 1.25 | 25 | — |
| S17d | off | VP-0 | 1 | — | — | 0.489 | 0.319 | 0 | 25 | — |
| S17d | off | VP-1 | 1 | — | — | 0.364 | 0.413 | 0 | 25 | — |
| S17d | off | VP-2 | 1 | — | — | 0.47 | 0.232 | 0 | 25 | — |
| S17d | off | VP-3 | 1 | — | — | 0.495 | 0.158 | 0 | 25 | — |
| S17d | off | VP-4 | 1 | — | — | 0.515 | 0.117 | 0 | 25 | — |
| S17d | off | VP-5 | 1 | — | PP-SWR-051, PP-SWR-062 | 0.515 | -0.00626 | 0 | 25 | — |
| S17e | off | VP-0 | 1 | — | — | 0.298 | 0.507 | 0 | 25 | — |
| S17e | off | VP-1 | 1 | — | — | 0.278 | 0.496 | 0 | 25 | — |
| S17e | off | VP-2 | 1 | — | — | 0.294 | 0.406 | 0 | 25 | — |
| S17e | off | VP-3 | 1 | — | — | 0.3 | 0.351 | 0 | 25 | — |
| S17e | off | VP-4 | 1 | — | — | 0.305 | 0.324 | 0 | 25 | — |
| S17e | off | VP-5 | 1 | — | — | 0.305 | 0.201 | 0 | 25 | — |
| S16d | off | VP-0 | 1 | ELK: có REQUEST nhưng thiếu path can thiệp hợp lệ | — | 0 | — | 0 | 20 | — |
| S16d | off | VP-1 | 1 | PP-SWR-100, PP-SWR-101, PP-SWR-102 | PP-SWR-086 | 0 | — | 0 | 20 | — |
| S16d | off | VP-2 | 1 | PP-SWR-100, PP-SWR-101, PP-SWR-102 | PP-SWR-085, PP-SWR-086 | 0 | — | 0 | 20 | — |
| S16d | off | VP-3 | 1 | ELK: có REQUEST nhưng thiếu path can thiệp hợp lệ | — | 0 | — | 0 | 20 | — |
| S16d | off | VP-4 | 1 | — | — | 0 | — | 0 | 20 | — |
| S16d | off | VP-5 | 1 | — | — | 0 | — | 0 | 20 | — |
| S9c | on | VP-0 | 1 | — | — | 0.4 | 0.4 | 0 | 25 | — |
| S9c | on | VP-1 | 1 | — | — | 0.4 | 0.37 | 0 | 25 | — |
| S9c | on | VP-2 | 1 | — | — | 0.4 | 0.295 | 0 | 25 | — |
| S9c | on | VP-3 | 1 | — | — | 0.4 | 0.245 | 0 | 25 | — |
| S9c | on | VP-4 | 1 | — | — | 0.4 | 0.223 | 0 | 25 | — |
| S9c | on | VP-5 | 1 | — | — | 0.4 | 0.1 | 0 | 25 | — |

## Flexibility

Chỉ một profile: không có bảng flexibility (mục 8.3).

## Thời gian tính

30720 chu kỳ. p95 ≤ 0.794 ms, p99 ≤ 1.26 ms (cận trên của bin), lớn nhất 3.66 ms. Đo trên máy chạy SIL, gồm adapter; không khẳng định thời gian trên ECU (mục 9.1).

![Thời gian tính](figures/compute.png)

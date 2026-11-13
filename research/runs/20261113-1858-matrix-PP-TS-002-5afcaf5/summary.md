# Kết luận: Đạt trong phạm vi đã thử

- Planner: pp_planner 0.2.0 commit 5afcaf564f23 calibration 06a80cfe5088 t7 quintic (79449a44eefd)
- Tích hợp được: có
- Đã chạy: 24 lần chạy; trượt BLOCKER 0, MAJOR 0, MINOR 0
- Kết luận chỉ đúng trong phạm vi đã thử, không phải bằng chứng an toàn (Software Qualification Test Specification 3).

## Bộ theo khía cạnh

| Bộ | Khía cạnh | Lần chạy | Kết luận | BLOCKER | MAJOR | MINOR |
|---|---|---|---|---|---|---|
| B0 | Conformance | — | Đạt C1, C2; Tích hợp được | — | — | — |
| B1 | Nominal | 0 | không có ca | — | — | — |
| B2 | Regulatory | 0 | không có ca | — | — | — |
| B3 | Performance limit | 24 | Đạt trong phạm vi đã thử | 0 | 0 | 0 |
| B4 | Robustness | 0 | không có ca | — | — | — |
| B5 | Degradation and refusal | 24 | Đạt trong phạm vi đã thử | 0 | 0 | 0 |
| B6 | Comfort | 0 | không có ca | — | — | — |
| B7 | Flexibility | 0 | không có ca | — | — | — |
| B8 | Compute | 24 | Đạt trong phạm vi đã thử | 0 | 0 | 0 |

## Matrix PP-TS-002

24 runs; 0 with an in-scope failure.

| Chạy | ACC | Profile | Seed | Trượt (trong phạm vi) | Trượt ngoài phạm vi | Lệch xe [m] | DLC min [m] | a_y cần tại xe [m/s²] | v min [m/s] | Báo trước [s] |
|---|---|---|---|---|---|---|---|---|---|---|
| S1bd | ignore_limits | VP-0 | 1 | — | — | 0.0246 | 0.769 | 3.12 | 25 | 0.908 |
| S1bd | ignore_limits | VP-0 | 2 | — | — | 0.0245 | 0.77 | 3.12 | 25 | 0.926 |
| S1bd | ignore_limits | VP-1 | 1 | — | — | 0.0322 | 0.731 | 3.12 | 25 | 0.938 |
| S1bd | ignore_limits | VP-1 | 2 | — | — | 0.0319 | 0.731 | 3.12 | 25 | 0.956 |
| S1bd | ignore_limits | VP-2 | 1 | — | — | 0.0259 | 0.663 | 3.12 | 25 | 0.918 |
| S1bd | ignore_limits | VP-2 | 2 | — | — | 0.0258 | 0.663 | 3.12 | 25 | 0.936 |
| S1bd | ignore_limits | VP-3 | 1 | — | — | 0.0242 | 0.615 | 3.12 | 25 | 0.908 |
| S1bd | ignore_limits | VP-3 | 2 | — | — | 0.0242 | 0.615 | 3.12 | 25 | 0.926 |
| S1bd | ignore_limits | VP-4 | 1 | — | — | 0.0235 | 0.594 | 3.12 | 25 | 0.898 |
| S1bd | ignore_limits | VP-4 | 2 | — | — | 0.0251 | 0.595 | 3.12 | 25 | 0.916 |
| S1bd | ignore_limits | VP-5 | 1 | — | — | 0.0235 | 0.471 | 3.12 | 25 | 0.898 |
| S1bd | ignore_limits | VP-5 | 2 | — | — | 0.0251 | 0.472 | 3.12 | 25 | 0.916 |
| S1bd | on | VP-0 | 1 | — | — | 0.0459 | 0.732 | 2.16 | 20.2 | — |
| S1bd | on | VP-0 | 2 | — | — | 0.0458 | 0.732 | 2.16 | 20.2 | — |
| S1bd | on | VP-1 | 1 | — | — | 0.0506 | 0.7 | 2.15 | 20.1 | — |
| S1bd | on | VP-1 | 2 | — | — | 0.0503 | 0.7 | 2.15 | 20.2 | — |
| S1bd | on | VP-2 | 1 | — | — | 0.0468 | 0.627 | 2.16 | 20.2 | — |
| S1bd | on | VP-2 | 2 | — | — | 0.0466 | 0.627 | 2.16 | 20.2 | — |
| S1bd | on | VP-3 | 1 | — | — | 0.0457 | 0.578 | 2.16 | 20.2 | — |
| S1bd | on | VP-3 | 2 | — | — | 0.0456 | 0.578 | 2.16 | 20.2 | — |
| S1bd | on | VP-4 | 1 | — | — | 0.0454 | 0.557 | 2.16 | 20.2 | — |
| S1bd | on | VP-4 | 2 | — | — | 0.047 | 0.557 | 2.17 | 20.2 | — |
| S1bd | on | VP-5 | 1 | — | — | 0.0454 | 0.434 | 2.16 | 20.2 | — |
| S1bd | on | VP-5 | 2 | — | — | 0.047 | 0.434 | 2.17 | 20.2 | — |

## Flexibility

Chỉ một profile: không có bảng flexibility (mục 8.3).

## Thời gian tính

12480 chu kỳ. p95 ≤ 2 ms, p99 ≤ 3.16 ms (cận trên của bin), lớn nhất 49 ms. Đo trên máy chạy SIL, gồm adapter; không khẳng định thời gian trên ECU (mục 9.1).

![Thời gian tính](figures/compute.png)

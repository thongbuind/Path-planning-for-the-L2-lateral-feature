# Register

Quy trình: [README.md](README.md). Lần chạy chính thức: [runs/INDEX.md](runs/INDEX.md).

## Trade studies

| ID | Câu hỏi | Trạng thái | Quyết định | Hồ sơ |
|---|---|---|---|---|
| PP-TS-001 | T2 xử lý lane model nhảy: J0, J1, J2, J3 | Mở | — | [study](studies/PP-TS-001-lane-jumps/study.md) |
| PP-TS-002 | Khoảng nới a_y 40 % trong 2 s cho PP-SWR-001 | Chờ quyết định | Đề xuất A (giữ nguyên) | [study](studies/PP-TS-002-ay-grace/study.md) |
| PP-TS-003 | Kỹ thuật tạo path HWA: quintic hay QP hợp nhất có cắt cua | Mở | — | [study](studies/PP-TS-003-path-generator/study.md) |
| PP-TS-005 | Sai số khớp đa thức của lane model ở hai đầu cửa sổ | Mở | — | [study](studies/PP-TS-005-lane-fit-error/study.md) |
| PP-TS-004 | Calibration T2, T5, cờ giới hạn (sweep P1) | Mở, cần chạy lại | — | [study](studies/PP-TS-004-p1-calibration/study.md) |

## Problem reports

| ID | Hiện tượng | Trạng thái | Liên quan | Hồ sơ |
|---|---|---|---|---|
| PP-PR-001 | F06: độ cong sai ở xa làm xe ra khỏi làn | Mở | PP-SWR-051, 125 | [report](problems/PP-PR-001-f06-wrong-curvature.md) |
| PP-PR-002 | S1b e: cờ giới hạn bật muộn | Đóng | PP-SWR-007 | [report](problems/PP-PR-002-s1b-late-flag.md) |
| PP-PR-003 | S2c, S2d: đưa về giữa khi xe hướng ra ngoài, lốp đè vạch | Mở | PP-SWR-051, 052 | [report](problems/PP-PR-003-s2-outward-overshoot.md) |
| PP-PR-005 | F01 trên S1c: path nhảy giữa hai chu kỳ khi phần xa bị cắt theo aysmax | Mở, đã tìm nguyên nhân; sửa qua PP-TS-003 | PP-SWR-100, 120 | [report](problems/PP-PR-005-noise-at-aysmax-continuity.md) |
| PP-PR-004 | S14e: giữ làn và liên tục path trên cua chữ S | Mở, đã tìm nguyên nhân; sửa qua PP-TS-005 | PP-SWR-051, 100; 006, 007 | [report](problems/PP-PR-004-s14-s-bend.md) |
| PP-PR-006 | Vào cua vượt aysmax: xe bám trễ, stitching reset làm path nhảy | Mở, đã tìm nguyên nhân | PP-SWR-100 | [report](problems/PP-PR-006-stitch-reset-curve-entry.md) |
| PP-PR-007 | S14a 130 km/h: xe ra khỏi đường sau đoạn vượt aysmax; 051 chấm khi đã ra ngoài | Mở; cần quyết định về requirement | PP-SWR-051 | [report](problems/PP-PR-007-s14a-overspeed-after-limit.md) |
| PP-PR-008 | S1ba 130 km/h: path T7 A trễ so với a_y cần lúc vào cua | Mở, đã tìm nguyên nhân; sửa qua PP-TS-003 | PP-SWR-006 | [report](problems/PP-PR-008-s1ba-fast-curve-entry-lag.md) |
| PP-PR-009 | F03 c: cả bốn vạch nhảy 3,5 m trong 2 s, xe đi theo sang làn bên | Mở; sửa qua PP-TS-001 | PP-SWR-051, 100 | [report](problems/PP-PR-009-f03c-whole-lane-shift.md) |

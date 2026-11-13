# Register

Quy trình: [README.md](README.md). Lần chạy chính thức: [runs/INDEX.md](runs/INDEX.md).

## Trade studies

| ID | Câu hỏi | Trạng thái | Quyết định | Hồ sơ |
|---|---|---|---|---|
| PP-TS-001 | T2 xử lý lane model nhảy: J0, J1, J2, J3 | Mở | — | [study](studies/PP-TS-001-lane-jumps/study.md) |
| PP-TS-002 | Khoảng nới a_y 40 % trong 2 s cho PP-SWR-001 | Chờ quyết định; S1b d đã chạy, vẫn đề xuất A | Đề xuất A (giữ nguyên) | [study](studies/PP-TS-002-ay-grace/study.md) |
| PP-TS-003 | Kỹ thuật tạo path HWA: quintic hay QP hợp nhất có cắt cua | Mở | — | [study](studies/PP-TS-003-path-generator/study.md) |
| PP-TS-005 | Sai số khớp đa thức của lane model ở hai đầu cửa sổ | Mở | — | [study](studies/PP-TS-005-lane-fit-error/study.md) |
| PP-TS-004 | Calibration T2, T5, cờ giới hạn (sweep P1) | Mở, cần chạy lại | — | [study](studies/PP-TS-004-p1-calibration/study.md) |
| PP-TS-006 | T7 tạo path can thiệp LKA, ELK bằng quintic hay QP | Mở | Tích hợp V1 trước | [study](studies/PP-TS-006-intervention-path/study.md) |
| PP-TS-007 | Điều kiện cho phép ELK ở mép đường không có vạch | Đã quyết | V1 | [study](studies/PP-TS-007-road-edge-eligibility/study.md) |
| PP-TS-008 | Nguồn FunctionRequests cho SIL LKA, ELK | Đã quyết | V2 | [study](studies/PP-TS-008-adas-stand-in/study.md) |
| PP-TS-009 | Dự báo xung đột xe làn bên khi trôi chậm | Đã quyết | V1 | [study](studies/PP-TS-009-object-conflict-window/study.md) |
| PP-TS-010 | Thời điểm rút LKA cùng phía trong lần ELK | Đã quyết | V1 | [study](studies/PP-TS-010-same-side-request-handover/study.md) |
| PP-TS-011 | Quyền sở hữu pha can thiệp trong PathStatus | Đã quyết | V1 | [study](studies/PP-TS-011-path-status-phases/study.md) |
| PP-TS-012 | Tuổi của VehicleStateEstimate khi T9 kiểm điều kiện kết thúc | Mở | Kiểm V1 | [study](studies/PP-TS-012-intervention-end-estimate-age/study.md) |
| PP-TS-013 | Path êm trong hành lang an toàn (ý tưởng racing line) | Mở; nguyên mẫu nghiên cứu | — | [study](studies/PP-TS-013-comfort-line/study.md) |
| PP-TS-014 | Liên tục của path khi phần xa ngoài tầm nhìn: V0–V3 | Đóng; hồi quy 20261112-1254-matrix-M1-8418fd9 | Đổi PP-SWR-100 đến 102 về tầm nhìn; T4 một λ trong tầm nhìn | [study](studies/PP-TS-014-continuity-beyond-view/study.md) |
| PP-TS-015 | Phạm vi chấm của ca có ca chủ (lỗi trên ca chủ, ca ghép, S12, S13, S14) | Đóng; hồi quy 20261113-1851-matrix-M1-5afcaf5 | V1 | [study](studies/PP-TS-015-scope-of-hosted-cases/study.md) |
| PP-TS-016 | Chức năng đang lái sau giới hạn 10 s của PP-SWR-083 (mâu thuẫn với 030) | Đã quyết; đã đưa vào; hồi quy 20261113-1803-suite-regression-3c31309 có trượt 030 chưa phân tích | V4 (theo R79, EU 2021/646) | [study](studies/PP-TS-016-function-after-intervention-limit/study.md) |
| PP-TS-017 | Path HWA trong lúc tài xế ghi đè: V0–V4 | Đóng; hồi quy 20261113-2255-suite-regression-e99cf08 | V2b, không chấm liên tục khi ghi đè | [study](studies/PP-TS-017-path-during-driver-override/study.md) |

## Problem reports

| ID | Hiện tượng | Trạng thái | Liên quan | Hồ sơ |
|---|---|---|---|---|
| PP-PR-001 | F06: độ cong sai ở xa làm xe ra khỏi làn | Mở, đã tìm nguyên nhân; sửa qua PP-TS-001 | PP-SWR-051, 125 | [report](problems/PP-PR-001-f06-wrong-curvature.md) |
| PP-PR-002 | S1b e: cờ giới hạn bật muộn | Đóng | PP-SWR-007 | [report](problems/PP-PR-002-s1b-late-flag.md) |
| PP-PR-003 | S2c, S2d: đưa về giữa khi xe hướng ra ngoài, lốp đè vạch | Mở, đã tìm nguyên nhân: stand-in chưa kiểm điều kiện vào HWA; ngưỡng vào mâu thuẫn với `ay_add_max_hwa` | PP-SWR-051, 052 | [report](problems/PP-PR-003-s2-outward-overshoot.md) |
| PP-PR-005 | F01 trên S1c: path nhảy giữa hai chu kỳ khi phần xa bị cắt theo aysmax | Mở, đã tìm nguyên nhân; sửa qua PP-TS-003 | PP-SWR-100, 120 | [report](problems/PP-PR-005-noise-at-aysmax-continuity.md) |
| PP-PR-004 | S14e: giữ làn và liên tục path trên cua chữ S | Mở, đã tìm nguyên nhân; sửa qua PP-TS-005 | PP-SWR-051, 100; 006, 007 | [report](problems/PP-PR-004-s14-s-bend.md) |
| PP-PR-006 | Vào cua vượt aysmax: xe bám trễ, stitching reset làm path nhảy | Mở, đã tìm nguyên nhân | PP-SWR-100 | [report](problems/PP-PR-006-stitch-reset-curve-entry.md) |
| PP-PR-007 | S14a 130 km/h: xe ra khỏi đường sau đoạn vượt aysmax; 051 chấm khi đã ra ngoài | Đã quyết B; chờ ghi giới hạn vào Software Requirements Specification | PP-SWR-051 | [report](problems/PP-PR-007-s14a-overspeed-after-limit.md) |
| PP-PR-008 | S1ba 130 km/h: path T7 A trễ so với a_y cần lúc vào cua | Mở, đã tìm nguyên nhân; sửa qua PP-TS-003 | PP-SWR-006 | [report](problems/PP-PR-008-s1ba-fast-curve-entry-lag.md) |
| PP-PR-009 | F03 c: cả bốn vạch nhảy 3,5 m trong 2 s, xe đi theo sang làn bên | Mở; sửa qua PP-TS-001 | PP-SWR-051, 100 | [report](problems/PP-PR-009-f03c-whole-lane-shift.md) |
| PP-PR-010 | FunctionRequests quá timeout, PathStatus vẫn báo path hợp lệ | Đóng; xác nhận ở 20261113-1803-suite-regression-3c31309 | PP-SWR-145 | [report](problems/PP-PR-010-function-requests-timeout.md) |
| PP-PR-011 | PP-SWR-047 chặn ELK ở các ca S6 chỉ có mép đường | Đã cài PP-TS-007 V1; chưa xác nhận được: bên chấm chưa đo PP-SWR-047 | PP-SWR-047, 086 | [report](problems/PP-PR-011-road-edge-only-qualification.md) |
| PP-PR-012 | Cửa sổ dự báo mặc định có thể bỏ lỡ xung đột S7(a) | Đã cài PP-TS-009 V1; xác nhận một phần: chưa có ca xe ngược chiều không xung đột | PP-SWR-088, 089 | [report](problems/PP-PR-012-slow-oncoming-conflict.md) |
| PP-PR-013 | LKA cùng phía có thể được chọn trước khi yêu cầu rút tới planner | Đã cài PP-TS-010 V1, chờ SIL hai chức năng cùng yêu cầu | PP-SWR-033, ADAS-FS mục 9 | [report](problems/PP-PR-013-same-side-request-handover.md) |
| PP-PR-014 | Lần can thiệp đang chạy khi log dừng bị chấm thời lượng vô hạn | Bỏ; PP-SWR-083 obsolete (PP-TS-016) | PP-SWR-083 | [report](problems/PP-PR-014-intervention-at-run-end.md) |
| PP-PR-015 | Xe bắt đầu trong cua trôi trước Tsteer | Đã sửa; xác nhận một phần: chưa đo v_lat trước Tsteer | S4b, S7(e) | [report](problems/PP-PR-015-curve-driver-initial-lateral-speed.md) |
| PP-PR-016 | Kết quả khoảng hở xe mục tiêu không ghi được JSON | Đóng; xác nhận ở 20261113-1803-suite-regression-3c31309 | PP-SWR-088 | [report](problems/PP-PR-016-traffic-score-json.md) |
| PP-PR-017 | S4b(c), S8(b) kế thừa sai hướng trôi hoặc tốc độ xe mục tiêu | Đóng; xác nhận ở 20261113-1803-suite-regression-3c31309 | Định nghĩa S4b(c), S8(b) | [report](problems/PP-PR-017-anchor-inherits-wrong-parameter.md) |
| PP-PR-018 | T9 dùng v_y trước t0 khi kiểm COMPLETED | Đã cài PP-TS-012 V1; chưa đạt: PP-SWR-032, 090 còn trượt (PP-PR-020) | PP-SWR-032, 090 | [report](problems/PP-PR-018-intervention-completion-state-age.md) |
| PP-PR-019 | ELK mép đường mất path trong tick nhận OFF | Đóng; xác nhận ở 20261113-1803-suite-regression-3c31309 | PP-SWR-037 | [report](problems/PP-PR-019-road-edge-cancellation.md) |
| PP-PR-020 | Tick COMPLETED còn lệch ở một số neo cua và mép đường | Mở | PP-SWR-032, 090 | [report](problems/PP-PR-020-completion-mismatch-on-curves-and-edges.md) |
| PP-PR-021 | Xe rời làn trong cua khi tầm nhìn camera ngắn (Q4) | Đã sửa, xác nhận ở 20261112-1239-matrix-Q4-1bfd184 | PP-SWR-051, 100 | [report](problems/PP-PR-021-short-view-curve-departure.md) |
| PP-PR-022 | S14a tầm nhìn ngắn: ACC đọc LateralLimits rời làn xa hơn | Đã sửa cùng PP-PR-021 | PP-SWR-051, 151, 152 | [report](problems/PP-PR-022-s14a-short-view-acc-on.md) |
| PP-PR-023 | Q3 ở 60 ms vượt tuổi tối đa 45 ms của FunctionRequests | Đã sửa, xác nhận ở 20261112-1430-matrix-Q3-f94030c | PP-SWR-038, 145 | [report](problems/PP-PR-023-function-requests-max-age.md) |
| PP-PR-024 | B0 C2: LongitudinalPlan ở đầu cao của dải làm Trajectory có vô cực | Đóng; xác nhận ở 20261113-1803-suite-regression-3c31309 | Software Qualification Test Specification 11 (C2), PP-SWR-010, 156 | [report](problems/PP-PR-024-longitudinal-plan-range-end.md) |
| PP-PR-025 | Bên chấm không tính performance target jerk ngang PP-SWR-004 | Đóng; xác nhận ở 20261113-1803-suite-regression-3c31309 | PP-SWR-004, Software Qualification Test Specification 8.2 | [report](problems/PP-PR-025-jerk-target-not-measured.md) |
| PP-PR-026 | Output có NaN trong lần chạy kịch bản bị ghi là lỗi bên chấm, không phải trượt | Đóng; xác nhận ở 20261113-1803-suite-regression-3c31309 | Software Qualification Test Specification 8.4 | [report](problems/PP-PR-026-non-finite-output-evaluator-error.md) |
| PP-PR-027 | S8b(c): khối Chức năng ADAS chạy thử gửi REQUEST trong ca không được can thiệp | Đóng; xác nhận ở 20261113-1803-suite-regression-3c31309 | Software Qualification Test Specification 5 (S8b c), ADAS Function Specification mục 6 | [report](problems/PP-PR-027-s8bc-stand-in-request.md) |
| PP-PR-028 | Báo cáo lệch Software Qualification Test Specification 8.3, 8.4: tên kết luận, cách tính flexibility | Đã sửa, chờ xác nhận chính thức | Software Qualification Test Specification 8.3, 8.4, 11 | [report](problems/PP-PR-028-report-lags-test-specification.md) |
| PP-PR-029 | S8b(c): ELK để khoảng cách ngang tới xe sau 0,22 m, dưới 0,3 m; PP-SWR-088 chưa truy về S8b | Đóng; xác nhận ở 20261113-2255-suite-regression-e99cf08 | PP-SWR-088 | [report](problems/PP-PR-029-s8bc-elk-target-clearance.md) |
| PP-PR-030 | F21 a, b, d: HWA thôi lái khi mất hai vạch làn mình, còn vạch làn bên | Mở, đã tìm nguyên nhân: bước 4 của T2 chưa cài | PP-SWR-147, 030 | [report](problems/PP-PR-030-f21-adjacent-line-fallback.md) |
| PP-PR-031 | Bên chấm không có tiêu chí cho PP-SWR-147 và 047 | Mở; chờ sửa bên chấm | PP-SWR-147, 047 | [report](problems/PP-PR-031-evaluator-missing-147-047.md) |
| PP-PR-032 | Khi tài xế ghi đè, path HWA không bắt đầu tại xe (S17, S9 c, S16 d) | Đóng; xác nhận ở 20261113-2255-suite-regression-e99cf08 | PP-SWR-039, 040 | [report](problems/PP-PR-032-driver-override-path-start.md) |
| PP-PR-033 | PP-SWR-032 và 090 đòi tick COMPLETED trùng với trạng thái thật | Mở; cần quyết định về requirement | PP-SWR-032, 090 | [report](problems/PP-PR-033-completion-tick-vs-truth.md) |
| PP-PR-034 | Path HWA vẫn hợp lệ khi IMU hoặc góc lái mất, không hợp lệ | Mở, đã tìm nguyên nhân | PP-SWR-142 | [report](problems/PP-PR-034-hwa-valid-without-imu-steering.md) |
| PP-PR-035 | Counter của lane model: planner không kiểm; nghĩa của counter nhảy chưa rõ | Mở; cần quyết định về requirement | PP-SWR-130 | [report](problems/PP-PR-035-lane-model-counter.md) |
| PP-PR-036 | F16 a, c: message valid = false lệch 1–2 chu kỳ so với mất message | Mở | PP-SWR-130 | [report](problems/PP-PR-036-invalid-flag-one-cycle.md) |
| PP-PR-037 | Can thiệp bị bỏ giữa chừng khi có lỗi input (F02, F20, G01) | Mở | PP-SWR-030, 043, 121, 143 | [report](problems/PP-PR-037-intervention-dropped-during-faults.md) |
| PP-PR-038 | ELK có REQUEST nhưng planner không có path can thiệp (F04, S16) | Mở | PP-SWR-030, 047 | [report](problems/PP-PR-038-elk-request-without-path.md) |
| PP-PR-039 | S13 b, ELK, VP-3: EPS chậm 100 ms, DTLE −0,45 m | Mở | PP-SWR-091, 085, 086 | [report](problems/PP-PR-039-s13b-elk-eps-delay.md) |
| PP-PR-040 | T10 kẹp jerk đúng bằng giới hạn, không có biên (S17 b, 5,000000001 m/s³) | Đã sửa; nháp đạt, chờ xác nhận chính thức | PP-SWR-003, 114, 115 | [report](problems/PP-PR-040-jerk-clamp-without-margin.md) |

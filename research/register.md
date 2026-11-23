# Register

Quy trình: [README.md](README.md). Lần chạy chính thức: [runs/INDEX.md](runs/INDEX.md).

## Đọc trước buổi review

- Hồi quy hai planner [20261122-0758-suite-regression-591e3de](runs/20261122-0758-suite-regression-591e3de/report.md) có 62 trên 2.309 lượt trượt và 28 vi phạm BLOCKER. Ngày 2026-11-23 đã quyết PP-TS-020 (V1a), PP-TS-026 (V4), PP-TS-002 (A) và phạm vi PP-SWR-094 (PP-PR-077); chưa hồi quy.
- So sánh quintic và QP cho HWA, chọn giới hạn tính khả thi trước khi nối path. [PP-TS-003](studies/PP-TS-003-path-generator/study.md)
- Đối chứng kiểm hình dạng lane model và các lỗi kéo dài vẫn cần xử lý. [PP-TS-001](studies/PP-TS-001-lane-jumps/study.md)
- Ngưỡng continuity theo ba đoạn đã vào đặc tả. Còn cần so trộn cả path với trộn theo từng đoạn. [PP-TS-019](studies/PP-TS-019-continuity-scope/study.md)
- Cửa sổ báo `COMPLETED` của LKA/ELK đã vào đặc tả. Cách xử lý phía planner còn chờ kiểm chứng. [PP-TS-018](studies/PP-TS-018-intervention-completion-window/study.md)
- ELK bắt đầu muộn dưới nhiễu mưa. Ca S12c hết trượt trong hồi quy sau khi sửa T2. [PP-PR-055](problems/PP-PR-055-s12c-elk-late-correlated-noise.md)

## Theo dõi xử lý 2026-11-22

Mốc đối chiếu: [hồi quy bb08d77](runs/20261119-0948-suite-regression-bb08d77/report.md). Kết quả xác nhận: [hồi quy 591e3de](runs/20261122-0758-suite-regression-591e3de/report.md).

| Ưu tiên | Đầu việc | Hồ sơ | Kết quả hoặc bước tiếp theo |
|---|---|---|---|
| P0 | Giữ làn khi yaw rate sai và kiểm trần gia tốc ngang | [PP-PR-049](problems/PP-PR-049-yaw-rate-bias-lane-departure.md), [PP-PR-056](problems/PP-PR-056-s1bb-vehicle-ay-above-r79.md), [PP-TS-020](studies/PP-TS-020-path-ay-ceiling/study.md), [PP-TS-027](studies/PP-TS-027-system-lateral-command-limit/study.md) | S1b(b) vượt giới hạn a_y xe. Đã mở TS-027 để so giới hạn tổng lệnh lái cấp hệ thống |
| P0 | Xử lý hình học làn sai kéo dài và phục hồi sau lỗi | [PP-PR-001](problems/PP-PR-001-f06-wrong-curvature.md), [PP-PR-009](problems/PP-PR-009-f03c-whole-lane-shift.md), [PP-PR-044](problems/PP-PR-044-lka-continues-on-jumped-lane.md), [PP-PR-048](problems/PP-PR-048-shape-check-wrong-curvature-after-fault.md), [PP-PR-057](problems/PP-PR-057-f06d-departure-after-fault-end.md), [PP-TS-001](studies/PP-TS-001-lane-jumps/study.md), [PP-TS-022](studies/PP-TS-022-blend-limit/study.md) | F03(c) đạt cả sáu lượt, đã đóng PR-009. F02(e), F06(d) còn trượt |
| P0 | Giữ làn trên cua chữ S | [PP-PR-004](problems/PP-PR-004-s14-s-bend.md), [PP-TS-005](studies/PP-TS-005-lane-fit-error/study.md) | Tái hiện S14(e) và review kế hoạch so sánh sai số hình học của V3 với V2 |
| P0 | Giữ làn và báo giới hạn khi vào cua gắt | [PP-PR-007](problems/PP-PR-007-s14a-overspeed-after-limit.md), [PP-PR-008](problems/PP-PR-008-s1ba-fast-curve-entry-lag.md), [PP-PR-051](problems/PP-PR-051-s1ba-flag-late-vp0.md) | Đã đóng PR-051. S14(a) còn trượt PP-SWR-051. S1b(a) cần xác nhận PP-SWR-006 trên đủ profile và seed |
| P0 | Giữ liên tục độ cong khi chuyển sang FOLLOW | [PP-PR-075](problems/PP-PR-075-s22a-curvature-step.md) | S22(a) đạt PP-SWR-102, đã đóng PR-075 |
| P0 | Giữ làn trong G01 trên S1c | [PP-PR-076](problems/PP-PR-076-g01-s1c-vp5-departure.md) | So VP-5 với ca đối chứng để xác định lỗi ở đầu vào, path hay bám path |
| P1 | Chốt đường về tâm sau can thiệp | [PP-PR-077](problems/PP-PR-077-094-outside-checked-scenarios.md), [PP-TS-026](studies/PP-TS-026-intervention-return/study.md) | Đã mở phạm vi PP-SWR-094 (SRS 1.26) và duyệt V4. Sửa `T_return_object` cùng PP-SWR-088 |

## Trade studies

| ID | Câu hỏi | Trạng thái | Quyết định | Hồ sơ |
|---|---|---|---|---|
| PP-TS-001 | T2 xử lý lane model nhảy: J0, J1, J2, J3 | Đã quyết 2026-11-14 theo 20261114-1857-study-PP-TS-001-13913da; J1 còn mở | J0 kiểm hình dạng | [study](studies/PP-TS-001-lane-jumps/study.md) |
| PP-TS-002 | Khoảng nới a_y 40 % trong 2 s cho PP-SWR-001 | Đóng 2026-11-23 | A (giữ nguyên) | [study](studies/PP-TS-002-ay-grace/study.md) |
| PP-TS-003 | Kỹ thuật tạo path HWA: quintic hay QP hợp nhất có cắt cua | Đã quyết 2026-11-14 theo 20261114-1934-study-PP-TS-003-272a711 | V0b: quintic, T10 trước T4 | [study](studies/PP-TS-003-path-generator/study.md) |
| PP-TS-005 | Sai số khớp đa thức của lane model ở hai đầu cửa sổ | Mở; plan duyệt 2026-11-23, chẩn đoán S14 e trước khi khóa | V1 bỏ; cài V3 chính, V2 đối chứng sau bước chuẩn bị | [study](studies/PP-TS-005-lane-fit-error/study.md) |
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
| PP-TS-018 | Khoảng thời gian báo COMPLETED theo trạng thái thật | V1 phía requirement đã áp dụng (SRS 1.20); hướng phía planner duyệt 2026-11-23 (dùng d₀, ψ₀ của PP-TS-005 V3) | — | [study](studies/PP-TS-018-intervention-completion-window/study.md) |
| PP-TS-019 | Phạm vi của PP-SWR-100 đến 102 và giới hạn trộn của T4 (đoạn gần, phần xa) | Đóng 2026-11-16; phần T4 quyết ở PP-TS-021 | Ba đoạn 0–1 s, 1–2 s, sau 2 s: 0,05 / 0,1 / 0,2 m (SRS 1.22); T4 một λ | [study](studies/PP-TS-019-continuity-scope/study.md) |
| PP-TS-020 | Trần a_y của path HWA so với aysmax khai báo (mức liên tục, R79 5.6.2.1.1) | Đã quyết 2026-11-23; chưa hồi quy | V1a, `ay_margin_hwa` = 0,1 m/s² (SRS 1.26) | [study](studies/PP-TS-020-path-ay-ceiling/study.md) |
| PP-TS-021 | Điểm đầu path HWA khi xe rời path cũ: `stitch_reset` và cách T4 bước 4 trộn | Đã quyết 2026-11-16 theo 20261116-1748-study-PP-TS-021-8726b80; hồi quy 20261117-0908-suite-regression-c56f0bf có trượt mới ở ELK (PP-PR-062) | V7: reset mềm 0,02–0,1 m | [study](studies/PP-TS-021-stitch-start/study.md) |
| PP-TS-022 | T4 bước 4: mỗi điểm của path so với ngưỡng nào khi tính λ (path quay về chậm ở F06 d, F03 c) | Đã quyết 2026-11-17 theo 20261117-1315-study-PP-TS-022-d2e7d27 (V1 trượt 2 / 3, V0 4 / 5; V1 sửa F06 d, không sửa F03 c, S14 e; lệch tâm xấu hơn ở 19 / 36 lượt); chờ hồi quy | V1: mỗi điểm so với ngưỡng của đoạn mình, một λ | [study](studies/PP-TS-022-blend-limit/study.md) |
| PP-TS-023 | Dải đặc tính lái (K, steering ratio, actuator delay) của vehicle profile cho phép chấm flexibility | Mở; hướng duyệt 2026-11-23, chạy sau nhóm sửa planner | — | [study](studies/PP-TS-023-profile-steering-dynamics/study.md) |
| PP-TS-024 | Driver model cho path HWA (T7): tangent point và quy tắc theo a_y, so với Quintic và QP | Mở 2026-11-18; cùng suite PP-T7 với PP-TS-025; kế hoạch nháp, V1/V2 chưa cài | — | [study](studies/PP-TS-024-driver-model-path/study.md) |
| PP-TS-025 | NN và LTV-MPC cho path HWA (T7): so NN warm start với Quintic, QP 150 vòng và QP cùng ngân sách vòng | Mở 2026-11-18; cùng suite PP-T7 với PP-TS-024; kế hoạch nháp, V2–V4 chưa cài | — | [study](studies/PP-TS-025-nn-ltv-mpc-path/study.md) |
| PP-TS-026 | Path LKA, ELK về tâm làn: một quintic hay hai pha (chặn đà rồi về chậm) | Đã quyết 2026-11-23 | V4 | [study](studies/PP-TS-026-intervention-return/study.md) |
| PP-TS-027 | Giới hạn tổng lệnh lái HWA để kiểm a_y xe và khả năng bám làn cấp hệ thống | Mở, V0–V2 đã cài cho SIL. Kế hoạch nháp | — | [study](studies/PP-TS-027-system-lateral-command-limit/study.md) |
| PP-TS-028 | Bộ nhớ của planner trôi theo bias yaw của EgoMotionQuery: V0 đến V3 | Mở 2026-11-23 | — | [study](studies/PP-TS-028-memory-heading-drift/study.md) |

## Problem reports

| ID | Hiện tượng | Trạng thái | Liên quan | Hồ sơ |
|---|---|---|---|---|
| PP-PR-001 | F06: độ cong sai ở xa làm xe ra khỏi làn | Mở, đã tìm nguyên nhân; sửa qua PP-TS-001 | PP-SWR-051, 125 | [report](problems/PP-PR-001-f06-wrong-curvature.md) |
| PP-PR-002 | S1b e: cờ giới hạn bật muộn | Đóng | PP-SWR-007 | [report](problems/PP-PR-002-s1b-late-flag.md) |
| PP-PR-003 | S2c, S2d: đưa về giữa khi xe hướng ra ngoài, lốp đè vạch | Đã sửa 2026-11-23 (cổng vào LCC, hướng A), chờ hồi quy | PP-SWR-051, 052 | [report](problems/PP-PR-003-s2-outward-overshoot.md) |
| PP-PR-005 | F01 trên S1c: path nhảy giữa hai chu kỳ khi phần xa bị cắt theo aysmax | Đóng; xác nhận ở 20261114-1952-suite-regression-0776bad | PP-SWR-100, 120 | [report](problems/PP-PR-005-noise-at-aysmax-continuity.md) |
| PP-PR-004 | S14e: giữ làn và liên tục path trên cua chữ S | Còn mở; sửa qua PP-TS-005 | PP-SWR-051, 100; 006, 007 | [report](problems/PP-PR-004-s14-s-bend.md) |
| PP-PR-006 | Vào cua vượt aysmax: xe bám trễ, stitching reset làm path nhảy | Đóng; xác nhận ở 20261114-1952-suite-regression-0776bad | PP-SWR-100 | [report](problems/PP-PR-006-stitch-reset-curve-entry.md) |
| PP-PR-007 | S14a 130 km/h: xe ra khỏi đường sau đoạn vượt aysmax; 051 chấm khi đã ra ngoài | Phương án B đã vào SRS 1.17; S14 a VP-0 vẫn trượt ở e3158a5, còn mở | PP-SWR-051 | [report](problems/PP-PR-007-s14a-overspeed-after-limit.md) |
| PP-PR-008 | S1ba 130 km/h: path T7 A trễ so với a_y cần lúc vào cua | Còn mở. VP-0 seed 1 đạt ở 591e3de, cần xác nhận đủ profile và seed | PP-SWR-006 | [report](problems/PP-PR-008-s1ba-fast-curve-entry-lag.md) |
| PP-PR-009 | F03 c: cả bốn vạch nhảy 3,5 m trong 2 s, xe đi theo sang làn bên | Đóng, F03 c đạt 6/6 ở 591e3de | PP-SWR-051, 100 | [report](problems/PP-PR-009-f03c-whole-lane-shift.md) |
| PP-PR-010 | FunctionRequests quá timeout, PathStatus vẫn báo path hợp lệ | Đóng; xác nhận ở 20261113-1803-suite-regression-3c31309 | PP-SWR-145 | [report](problems/PP-PR-010-function-requests-timeout.md) |
| PP-PR-011 | PP-SWR-047 chặn ELK ở các ca S6 chỉ có mép đường | Đã cài PP-TS-007 V1; chưa xác nhận được: bên chấm chưa đo PP-SWR-047 | PP-SWR-047, 086 | [report](problems/PP-PR-011-road-edge-only-qualification.md) |
| PP-PR-012 | Cửa sổ dự báo mặc định có thể bỏ lỡ xung đột S7(a) | Đã kiểm cục bộ đối chứng xe ngược chiều ngoài cửa sổ | PP-SWR-088, 089 | [report](problems/PP-PR-012-slow-oncoming-conflict.md) |
| PP-PR-013 | LKA cùng phía có thể được chọn trước khi yêu cầu rút tới planner | Đã cài PP-TS-010 V1, chờ SIL hai chức năng cùng yêu cầu | PP-SWR-033, ADAS-FS mục 9 | [report](problems/PP-PR-013-same-side-request-handover.md) |
| PP-PR-014 | S4(d, e), seed 1: lần can thiệp còn ACTIVE khi log dừng bị chấm thời lượng vô hạn | Bỏ vì đã loại tiêu chí thời lượng PP-SWR-083 | PP-SWR-083 | [Quyết định PP-TS-016](studies/PP-TS-016-function-after-intervention-limit/study.md) |
| PP-PR-015 | Xe bắt đầu trong cua trôi trước Tsteer | Đã đo v_lat trước Tsteer trên bốn neo cua, chờ hồi quy chính thức | S4b, S7(e) | [report](problems/PP-PR-015-curve-driver-initial-lateral-speed.md) |
| PP-PR-016 | Kết quả khoảng hở xe mục tiêu chứa giá trị boolean NumPy nên không ghi được JSON | Đóng sau khi chuyển kết quả sang kiểu Python. Hồi quy ghi được PP-SWR-088 ở mọi lượt S7, S8, S8b | PP-SWR-088 | [Hồi quy 20261113-1803-suite-regression-3c31309](runs/20261113-1803-suite-regression-3c31309/report.md) |
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
| PP-PR-028 | Báo cáo lệch Software Qualification Test Specification 8.3, 8.4: tên kết luận, cách tính flexibility | Đóng; đối chiếu HTML và Markdown trên 20261113-2255-suite-regression-e99cf08 | Software Qualification Test Specification 8.3, 8.4, 11 | [report](problems/PP-PR-028-report-lags-test-specification.md) |
| PP-PR-029 | S8b(c): ELK để khoảng cách ngang tới xe sau 0,22 m, dưới 0,3 m; PP-SWR-088 chưa truy về S8b | Đóng; xác nhận ở 20261113-2255-suite-regression-e99cf08 | PP-SWR-088 | [report](problems/PP-PR-029-s8bc-elk-target-clearance.md) |
| PP-PR-030 | F21 a, b, d: HWA thôi lái khi mất hai vạch làn mình, còn vạch làn bên | Đóng; xác nhận ở 20261114-1021-suite-regression-d7ed84c (trừ F21 c, d trên S1c: PP-PR-045) | PP-SWR-147, 030 | [report](problems/PP-PR-030-f21-adjacent-line-fallback.md) |
| PP-PR-031 | Bên chấm không có tiêu chí cho PP-SWR-147 và 047 | Đóng; xác nhận ở 20261114-1021-suite-regression-d7ed84c | PP-SWR-147, 047 | [report](problems/PP-PR-031-evaluator-missing-147-047.md) |
| PP-PR-032 | Khi tài xế ghi đè, path HWA không bắt đầu tại xe (S17, S9 c, S16 d) | Đóng; xác nhận ở 20261113-2255-suite-regression-e99cf08 | PP-SWR-039, 040 | [report](problems/PP-PR-032-driver-override-path-start.md) |
| PP-PR-033 | PP-SWR-032 và 090 đòi tick COMPLETED trùng với trạng thái thật | Chờ chốt tiêu chí trong PP-TS-018 | PP-SWR-032, 090 | [report](problems/PP-PR-033-completion-tick-vs-truth.md) |
| PP-PR-034 | Path HWA vẫn hợp lệ khi IMU hoặc góc lái mất, không hợp lệ | Đóng; xác nhận ở 20261114-1021-suite-regression-d7ed84c | PP-SWR-142 | [report](problems/PP-PR-034-hwa-valid-without-imu-steering.md) |
| PP-PR-035 | Counter của lane model: planner không kiểm; nghĩa của counter nhảy chưa rõ | Đóng phần F15; S14 d cần phân tích; xác nhận ở 20261114-1952-suite-regression-0776bad | PP-SWR-129, 130 | [report](problems/PP-PR-035-lane-model-counter.md) |
| PP-PR-036 | F16 a, c: message valid = false lệch 1–2 chu kỳ so với mất message | Đã sửa 2026-11-23 (SRS 1.27 tách qualifier FAULT sang PP-SWR-142), chờ hồi quy | PP-SWR-130 | [report](problems/PP-PR-036-invalid-flag-one-cycle.md) |
| PP-PR-037 | Can thiệp bị bỏ giữa chừng khi có lỗi input (F02, F20, G01) | Đã sửa nhánh F02. F20, G01 còn mở | PP-SWR-030, 043, 121, 143 | [report](problems/PP-PR-037-intervention-dropped-during-faults.md) |
| PP-PR-038 | ELK có REQUEST nhưng planner không có path can thiệp (F04, S16) | F04 đóng (PP-SWR-092), xác nhận ở 20261114-1021-suite-regression-d7ed84c. S16 còn mở | PP-SWR-030, 047, 092 | [report](problems/PP-PR-038-elk-request-without-path.md) |
| PP-PR-039 | S13 b, ELK, VP-3: EPS chậm 100 ms, DTLE −0,45 m | Mở | PP-SWR-091, 085, 086 | [report](problems/PP-PR-039-s13b-elk-eps-delay.md) |
| PP-PR-040 | T10 kẹp jerk đúng bằng giới hạn, không có biên (S17 b, 5,000000001 m/s³) | Đóng; hồi quy 20261113-2341-suite-regression-1014d20 | PP-SWR-003, 114, 115 | [report](problems/PP-PR-040-jerk-clamp-without-margin.md) |
| PP-PR-041 | S7: path ELK bị T10 cắt jerk, không kết thúc song song với làn, phần xa nhảy | Đóng; xác nhận ở 20261114-1021-suite-regression-d7ed84c | PP-SWR-100; 085, 088, 115 | [report](problems/PP-PR-041-intervention-candidate-cut-by-t10.md) |
| PP-PR-042 | B2 không có ca cho bài ESF với xe làn bên của R79 | Đóng; xác nhận ở 20261114-1021-suite-regression-d7ed84c | Software Qualification Test Specification 5.1, 5.3 | [report](problems/PP-PR-042-b2-missing-r79-esf-cases.md) |
| PP-PR-043 | B0 C2: bản QP xuất tọa độ path vô cực khi `VehicleStateEstimate` ở đầu dải | Đã sửa, B0 cục bộ đạt; 20261114-1021-suite-regression-d7ed84c chạy bản quintic, chờ B0 chính thức trên bản QP | B0 C2, PP-SWR-043, PP-TS-003 | [report](problems/PP-PR-043-qp-trajectory-float32-overflow.md) |
| PP-PR-044 | F02 e lúc LKA: LKA tiếp tục trên lane model nhảy, DLC phía đối diện −0,10 m | Còn mở. Lỗi c0 giữ lâu hơn `T_confirm` được nhận như thay đổi thật, planner không phân biệt được | PP-SWR-085; 121, 030 | [report](problems/PP-PR-044-lka-continues-on-jumped-lane.md) |
| PP-PR-045 | F21 c, d: đường của anchor thay hình học của ca chủ S1c | Mở | Độ phủ F21; PP-SWR-147, 148, 051 | [report](problems/PP-PR-045-f21-anchor-road-replaces-host.md) |
| PP-PR-046 | F17 b trên S1c: CRC tốc độ sai, xe ra khỏi làn (DLC −0,87 đến −1,29 m) | Đóng 2026-11-23; cùng gốc PP-PR-059 | PP-SWR-051; 142 | [report](problems/PP-PR-046-f17b-speed-crc-leaves-lane.md) |
| PP-PR-047 | S14 d: message LongitudinalPlan đầu tiên sau khi mất bị bỏ theo kiểm counter | Đóng (20261114-2252-suite-regression-98a122b) | PP-SWR-153; 129, 130 | [report](problems/PP-PR-047-longitudinal-plan-first-after-loss.md) |
| PP-PR-048 | F06 c và F06 d lúc LKA, ELK trượt sau khi bật kiểm hình dạng | Đóng phần F06 c; F06 d chuyển sang J1 (20261114-2252-suite-regression-98a122b) | PP-SWR-051, 086; PP-TS-001 | [report](problems/PP-PR-048-shape-check-wrong-curvature-after-fault.md) |
| PP-PR-049 | F08: bias yaw rate làm xe rời làn trên cua | Mở; nguyên nhân gốc ở bộ nhớ T3, T4 dời bằng ego-motion có bias; sửa qua PP-TS-028 | PP-SWR-136; 051, 100 | [report](problems/PP-PR-049-yaw-rate-bias-lane-departure.md) |
| PP-PR-050 | S14 c: độ cong đầu xa của path đổi trong một chu kỳ | Mở | PP-SWR-100 | [report](problems/PP-PR-050-s14c-far-curvature-step.md) |
| PP-PR-051 | S1b a, VP-0: cờ giới hạn chưa bật khi lốp đè vạch | Đóng, S1b a VP-0 seed 1 đạt ở 591e3de | PP-SWR-007 | [report](problems/PP-PR-051-s1ba-flag-late-vp0.md) |
| PP-PR-052 | G01 trên S4c: LKA bị hủy khi vạch còn lại bị loại một frame | Đóng (20261114-2252-suite-regression-98a122b) | PP-SWR-030, 047 | [report](problems/PP-PR-052-g01-s4c-lka-dropped-on-rejected-line.md) |
| PP-PR-053 | Cách chấm PP-SWR-030 mâu thuẫn với PP-SWR-045 (F20 a) | Đóng (20261114-2252-suite-regression-98a122b) | PP-SWR-030, 045 | [report](problems/PP-PR-053-eval-030-ignores-045.md) |
| PP-PR-054 | F17 b và F21 c trên S1c: xe rời làn ở cua chạm aysmax | Không còn tái hiện ở e3158a5: F17 b, F21 c trên S1c đạt | PP-SWR-051 | [report](problems/PP-PR-054-s1c-f17b-f21c-departure.md) |
| PP-PR-056 | S1b b: a_y của xe vượt giới hạn dù a_y path đạt PP-SWR-001 | Mở, khảo sát giới hạn tổng lệnh lái qua PP-TS-027 | R79 5.6.2.1.1, PP-TS-020, PP-TS-027 | [report](problems/PP-PR-056-s1bb-vehicle-ay-above-r79.md) |
| PP-PR-055 | S12 c: ELK bắt đầu trễ 0,8 s vì T2 loại frame nhất quán | Đóng (20261114-2252-suite-regression-98a122b) | PP-SWR-088, 085, 100 | [report](problems/PP-PR-055-s12c-elk-late-correlated-noise.md) |
| PP-PR-057 | F06 d: xe rời làn sau khi lỗi đã hết (T2 loại hình học đúng thêm `T_confirm`, T4 quay về chậm), rồi HWA lái tiếp ở làn bên | Còn mở; cơ chế 2, 3 chờ quyết định | PP-SWR-051, 125, 061; SG-01; PP-TS-001, 005, 021 | [report](problems/PP-PR-057-f06d-departure-after-fault-end.md) |
| PP-PR-058 | Đa thức dời bằng ego-motion mất 1 m tầm nhìn mỗi chu kỳ khi xe đổi hướng (`pp_cubic_move`); kiểm hình dạng của T2 yếu dần | Đã sửa (9cc3c8e); hồi quy 20261117-0908-suite-regression-c56f0bf không có trượt mới do lần sửa này | PP-SWR-121, 122, 124, 125, 018; PP-PR-048, 057 | [report](problems/PP-PR-058-moved-cubic-loses-view-range.md) |
| PP-PR-059 | F17 b: bộ bơm lỗi làm hỏng CRC của mọi khung thay vì 1 trong 10; planner từ chối đúng, PP-SWR-051 bị chấm sai | Đã sửa (644c947); F17 b hết trượt ở 20261117-0908-suite-regression-c56f0bf | PP-SWR-130, 142, 051; PP-PR-046, 054 | [report](problems/PP-PR-059-f17b-crc-every-not-applied.md) |
| PP-PR-060 | Path LKA, ELK dừng sát vạch (DTLE 0,03–0,05 m) dù mới dùng khoảng một phần ba giới hạn a_y, jerk | Mở. Phương án A thử và gỡ 2026-11-17 (lợi 2–3 cm, DLC đối diện giảm 0,4 m, S8 a trượt 090); DTLE do thời điểm REQUEST quyết định | PP-SWR-086, 091, 087; PP-TS-006; PP-PR-039 | [report](problems/PP-PR-060-intervention-path-without-margin.md) |
| PP-PR-061 | Thời gian tính đo bằng đồng hồ thật khi chạy 4 tiến trình: 0,27 % chu kỳ vượt 5 ms do máy | Đã sửa 2026-11-23 (thời gian CPU của luồng), chờ chạy lại | PP-SWR-015, 016 | [report](problems/PP-PR-061-compute-time-wall-clock-under-load.md) |
| PP-PR-062 | Reset mềm của T4 (PP-TS-021 V7) làm ELK bắt đầu muộn ở v_lat cao: S13 a, c, S5 Euro NCAP 0,6 m/s, DTLE −0,33 đến −0,54 m | Đã sửa (fecdbb0): PP-SWR-031 đổi, PP-SWR-049 mới (SRS 1.23). Hồi quy 20261117-1217-suite-regression-d2e7d27: 16 nhóm hết trượt, 7 nhóm trượt mới ở ELK lặp (PP-PR-063) | PP-SWR-085, 086, 091, 090, 100 đến 102, 031; PP-TS-021 | [report](problems/PP-PR-062-soft-reset-elk-start.md) |
| PP-PR-063 | ELK kích hoạt lặp 4–6 lần ở VP-3, VP-4, VP-5 với trôi 0,6 m/s: yêu cầu bị rút khoảng 1 s khi xe còn 0,47 m/s, xe vọt sang phía đối diện | Đóng (56bdc48). Nguyên nhân: khối ADAS chạy thử coi tốc độ quay vô lăng do LKA, ELK tạo ra là ý định tài xế và hủy yêu cầu | PP-SWR-085, 086, 091, 035, 039, 090; PP-TS-008, 010 | [report](problems/PP-PR-063-elk-ping-pong.md) |
| PP-PR-064 | Web live: run gắn với tab, một run toàn cục, không ghi bằng chứng, mất stderr của worker | Đóng; lõi thực thi và workbench đã thay luồng cũ, kiểm lại trên hai planner | Công cụ kiểm thử | [report](problems/PP-PR-064-web-run-lifecycle.md) |
| PP-PR-065 | HUD web: khoảng hở dùng nửa bề rộng làn cố định, lệch tới 1,425 m ở S6b d | Đóng (eb73eee) | Chỉ hiển thị | [report](problems/PP-PR-065-hud-clearance-fixed-lane-width.md) |
| PP-PR-066 | HUD web: tỉ lệ đóng góp lái gán 0,5 khi có lực tài xế | Đóng (eb73eee) | Chỉ hiển thị | [report](problems/PP-PR-066-steering-share-fixed-half.md) |
| PP-PR-067 | Overlay lane model trên web tra tư thế bằng stamp đồng hồ camera; tới 2,5 cm dưới F14 | Đóng (eb73eee) | Chỉ hiển thị | [report](problems/PP-PR-067-lane-overlay-clock-domain.md) |
| PP-PR-068 | SQTS 4.1 mô tả chế độ thời gian thực (python-can `udp_multicast`) chưa có trong code | Đóng 2026-11-19: hướng A, SQTS 1.50 ghi chưa triển khai | SQTS 4.1 | [report](problems/PP-PR-068-realtime-mode-not-implemented.md) |
| PP-PR-069 | Lỗi gắn trigger không được bơm nhưng ca vẫn được chấm như đã bơm | Đóng (f819db1); xác nhận ở 20261118-1546-suite-regression-edb02b8 | SQTS 6, 8.4 | [report](problems/PP-PR-069-uninjected-fault-still-judged.md) |
| PP-PR-070 | S22b rời FOLLOW trước giới hạn 30 m. F25c và F25e báo path mất hiệu lực sớm sau FOLLOW | Phần F25 đóng (e3158a5). S22b vẫn không được chấm vì chưa quan sát được FOLLOW tới 30 m | PP-SWR-170, 173 | [report](problems/PP-PR-070-follow-coast-timing.md) |
| PP-PR-071 | S20a và F24a trên S20a có DLC phía can thiệp giảm lại quá 0,1 m | Đóng (e395662, PP-TS-026) | PP-SWR-094 | [report](problems/PP-PR-071-s20a-dlc-reversal.md) |
| PP-PR-072 | Hành lang can thiệp đi theo nhiễu lane model | Đóng (e395662) | PP-SWR-094, 085 | [report](problems/PP-PR-072-corridor-noise.md) |
| PP-PR-073 | COMPLETED lệch thời điểm khi lane model nhiễu | Mở | PP-SWR-032, 090 | [report](problems/PP-PR-073-completed-under-noise.md) |
| PP-PR-074 | Vào lại FOLLOW chậm sau lỗi LeadTarget | Mở | PP-SWR-170 | [report](problems/PP-PR-074-follow-reentry-after-fault.md) |
| PP-PR-075 | S22 a: độ cong đổi quá ngưỡng giữa hai path | Đóng, S22 a VP-0 seed 1 đạt ở 591e3de | PP-SWR-102 | [report](problems/PP-PR-075-s22a-curvature-step.md) |
| PP-PR-076 | G01 trên S1c, VP-5: DLC âm nhẹ | Mở | PP-SWR-051 | [report](problems/PP-PR-076-g01-s1c-vp5-departure.md) |
| PP-PR-077 | PP-SWR-094 trượt 146 lượt ELK vì xe làn bên (S7, S8, S8b, S12, S21), ngoài phạm vi chấm; tăng từ 97 sau PP-TS-026 V4 | Mở; phạm vi mở rộng ở SRS 1.26, chờ sửa planner | PP-SWR-094; PP-TS-026 | [report](problems/PP-PR-077-094-outside-checked-scenarios.md) |
| PP-PR-078 | `lcc_mode` = COAST khoảng 1 s mỗi lần camera mất một vạch, dù vạch làn mình còn đo được; 200 lượt trượt PP-SWR-177 ngoài phạm vi | Mở; đã tái hiện trên S1b b, nguyên nhân gốc chưa xác nhận | PP-SWR-177, 121, 124 | [report](problems/PP-PR-078-coast-label-while-lines-measured.md) |
| PP-PR-079 | S22 e: vào FOLLOW khi xe trước lệch tâm 0,8 đến 0,9 m, 6 lượt | Mở; chưa phân tích | PP-SWR-171; PP-ASM-025, 026 | [report](problems/PP-PR-079-s22e-follow-entry-off-centre.md) |
| PP-PR-080 | S14 a, VP-0: PP-SWR-051 báo DLC −23 m sau đoạn cua vượt giới hạn; ground truth −2,96 m | Đã sửa phép chiếu 2026-11-23; S14 a đạt 051 ở lượt nháp, chờ hồi quy | PP-SWR-051; 006, 007 | [report](problems/PP-PR-080-s14a-dlc-after-over-limit.md) |
| PP-PR-081 | S19 f: không báo `lane_too_narrow` khi làn hẹp dần trong lúc LCC lái | Mở | PP-SWR-063; 062 | [report](problems/PP-PR-081-s19f-lane-too-narrow-not-set.md) |

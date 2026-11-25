# Software Release Note

| Mục | Nội dung |
|---|---|
| Mã tài liệu | `PP-SRN` |
| Phiên bản | 1.0 |
| Trạng thái | BL1 |
| Tác giả | thongbui |
| Người review | thongbui |
| Cập nhật | 2026-11-23 |

## 1. Purpose and scope {#srn-scope}

- **Mục đích:** Ghi một bản giao của hai path planner: gồm những gì, được kiểm chứng tới đâu, giới hạn đã biết, và tiêu chí nhóm đề xuất để đưa bản giao vào HIL.
- **Phạm vi:** Thư viện `libpp_lcc`, `libpp_lkaelk`, header C, bộ calibration, bằng chứng kiểm chứng trong SIL.
- **Ngoài phạm vi:** Cách build và đóng gói từng bước ([Simulation Runbook](report.html?doc=simulation-runbook&lang=vi#rb-handover) mục 9). Kết quả trên xe.

## 2. References {#srn-references}

| Tài liệu | Phiên bản | Dùng cho |
|---|---|---|
| [Software Requirements Specification](report.html?doc=path-planner-software-requirements-specification&lang=vi) | 1.27 | Requirement, ODD, giả định |
| [Software Architectural Design](report.html?doc=path-planner-software-architectural-design&lang=vi) | 1.14 | Kiến trúc, calibration parameter |
| [Software Detailed Design](report.html?doc=path-planner-software-detailed-design&lang=vi) | 1.30 | Unit và interface của từng unit |
| [Interface Control Document](report.html?doc=path-planner-interface-control-document&lang=vi) | 1.13 | Message và contract gọi hàm |
| [Hazard Analysis and Risk Assessment (HARA)](report.html?doc=path-planner-hazard-analysis-and-risk-assessment&lang=vi) | 1.5 | Safety goal, SOTIF |
| [Unit Test Specification](report.html?doc=path-planner-unit-test-specification&lang=vi) | 1.1 | Ca kiểm unit |
| [Software Qualification Test Specification](report.html?doc=path-planner-software-qualification-test-specification&lang=vi) | 1.51 | Kiểm chứng SWC trong SIL |
| `research/register.md` | — | Trade study, problem report, lần chạy chính thức |

## 3. Nội dung bản giao {#srn-content}

| Thành phần | Nội dung | Nhận diện |
|---|---|---|
| Thư viện | `libpp_lcc` (LCC), `libpp_lkaelk` (LKA, ELK), build từ cùng một commit | `pp_lcc_version()`, `pp_lkaelk_version()`: commit, cờ `-dirty`, 12 ký tự SHA-256 của calibration; `SHA256SUMS` |
| Contract gọi hàm | `interfaces/c/pp_planner.h`; kiểu message sinh từ schema ở `interfaces/c/` | Interface Control Document 1.13 |
| Calibration | `planner/calibration/calibration.yaml`, sinh thành struct hằng lúc build; planner kiểm giới hạn của Software Requirements Specification mục 7 lúc `pp_*_init` | Mã calibration trong chuỗi phiên bản |
| Yêu cầu nền tảng | Trình biên dịch C11; không cấp phát động, không đọc file, không biến toàn cục; vùng nhớ trạng thái do bên gọi cấp (PP-ADR-013) | `pp_*_state_size()` |
| Bản theo nền tảng | macOS (bản đã chấm chính thức); Linux `.so` từ CI | sha256 của từng bản |

## 4. Bằng chứng kiểm chứng {#srn-evidence}

Theo ba chỉ số của quy trình: requirement coverage, code coverage, pass rate.

| Bằng chứng | Kết quả | Nguồn |
|---|---|---|
| Unit test | 17 file, 131 ca, đạt | `ctest`; Unit Test Specification |
| Kiểm tích hợp unit | 20 ca của `pp_lcc_step`, `pp_lkaelk_step`, đạt | Unit Test Specification mục 6 |
| Kiểm chứng SWC (SIL) | Lần chạy chính thức cuối ở mục 8 | Software Qualification Test Specification; `research/runs/` |
| Requirement coverage | Lần chạy chính thức cuối ở mục 8 | Cột Kiểm chứng của Software Requirements Specification; `tools/trace.py` |
| Code coverage | Từ unit test: line 96,9 %, branch 73,3 %; nhánh chưa chạy nhiều nhất ở `pp_lcc.c`, `pp_core.c`, `offset.c` | Unit Test Specification mục 7 |
| Static analysis | Clang analyzer: 2 cảnh báo null pointer, cả hai không xảy ra lúc chạy, sẽ thêm kiểm tra phòng vệ. MISRA C:2012 (cppcheck): 334 lần báo trên 13 luật; 203 báo nhầm, phần còn lại cần sửa hoặc deviation record | Unit Test Specification mục 7 |
| Tính tất định | Golden khớp trên cùng máy | `eval.golden` |
| Interface | Conformance B0 đạt | `eval.conformance` |

## 5. Giới hạn đã biết {#srn-limitations}

| Giới hạn | Ảnh hưởng | Nguồn |
|---|---|---|
| Không có log xe thật; chưa model nào của simulator được validation với dữ liệu thật | Kết luận chỉ đúng trong phạm vi đã thử | Simulation Handbook mục 9, 15 |
| Planner chỉ dùng camera cho cua phía trước | Cua gắt thấy muộn ở tốc độ cao: path ở giới hạn, cờ `lateral_limit_reached` bật, khối dọc phải giảm tốc; xe có thể vượt vạch khi a_y cần > aysmax | Software Requirements Specification mục 5; PP-PR-080 |
| Bias yaw rate trong EgoMotionQuery | Bộ nhớ của planner trôi theo bias; từ khoảng 0,3 °/s xe có thể rời làn trên cua cần đúng aysmax | PP-PR-049, PP-TS-028 |
| Cua chữ S ngắn của R171 ở 130 km/h | Path cắt a_y dưới aysmax − `epsilon_ay` tại khúc cong nhất | PP-PR-004, PP-TS-005 |
| Làn hẹp dần trong lúc LCC lái | `lane_too_narrow` chưa được báo | PP-PR-081 |
| Làn hỗn hợp ô tô và xe máy | Chưa thiết kế riêng | Software Requirements Specification mục 5 |
| Nền tảng đích chưa chọn | Thời gian tính chỉ đo trên máy phát triển, không phải WCET | PP-ASM-019 |
| Calibration chỉ đổi được khi build lại | Tune trên xe cần build lại | PP-TS-029 |
| S, E, C và ASIL là đề xuất của nhóm | Chưa có confirmation review độc lập | PP-ASM-018; HARA |

Problem report đang mở: `research/register.md`.

## 6. Tiêu chí vào HIL {#srn-hil-gate}

Nhóm đề xuất; bản giao vào HIL khi mọi dòng đạt.

| ID | Tiêu chí | Đạt khi |
|---|---|---|
| G1 | Requirement coverage | Mọi requirement Safety và Regulatory có Kiểm chứng Test được chấm ở lần chạy chính thức cuối |
| G2 | BLOCKER | 0 lần trượt BLOCKER ở regression và full của lần chạy chính thức cuối |
| G3 | MAJOR | 0 lần trượt MAJOR, hoặc mỗi lần có giải trình được người phụ trách chấp nhận |
| G4 | Unit test | Mọi ca của Unit Test Specification đạt; mỗi unit có ít nhất ca N, B và I hoặc F |
| G5 | Code coverage | Đã đo statement và branch; mọi nhánh chưa chạy có giải trình. Không đặt ngưỡng phần trăm |
| G6 | Static analysis | Đã chạy kiểm MISRA C:2012; mọi vi phạm luật Required có deviation record |
| G7 | Tất định và nhận diện | Golden khớp; thư viện build từ một commit sạch; sha256 khớp manifest của lần chạy chính thức |
| G8 | Thời gian tính | WCET đo trên ECU đích nhỏ hơn `t_budget` = 5 ms |
| G9 | Interface | Conformance B0 đạt trên bản của nền tảng đích; smoke đạt qua adapter của nền tảng đích |
| G10 | Giới hạn đã biết | Mục 5 đã được người phụ trách xem; mỗi giới hạn có biện pháp ở hệ thống hoặc được chấp nhận |

## 7. Hiện trạng so với tiêu chí {#srn-status}

| ID | Hiện trạng ngày 2026-11-23 |
|---|---|
| G1 | 99/106; còn PP-SWR-132 chưa chấm và 6 requirement chưa có criterion (PP-PR-082) |
| G2 | 20 BLOCKER ở 9f2f367 |
| G3 | Đạt: 0 MAJOR |
| G4 | Đạt phần ca; còn thiếu loại ca ở T3, T4, T6, T9, T10, T11 (Unit Test Specification mục 7) |
| G5 | Đã đo từ unit test; chưa có giải trình cho nhánh chưa chạy; chưa đo khi chạy SIL |
| G6 | Đã chạy; chưa sửa 10.8, 12.1, 9.3, 15.7, 10.7, 8.9 và chưa viết deviation record |
| G7 | Đạt trên macOS |
| G8 | Chưa có ECU đích |
| G9 | Đạt trên macOS và Linux; chưa có adapter của nền tảng đích |
| G10 | Chưa review |

## 8. Lần chạy chính thức {#srn-runs}

| Run ID | Commit | Kết quả |
|---|---|---|
| `20261122-0758-suite-regression-591e3de` | 591e3de | 2.309 lượt; 28 BLOCKER, 0 MAJOR, 42 MINOR |
| `20261123-1254-suite-regression-54307f1` | 54307f1 | 2.310 lượt; 223 BLOCKER (146 PP-SWR-094 sau khi mở phạm vi, 64 PP-SWR-172, 176 do PP-PR-083, 9 PP-SWR-051), 0 MAJOR, 43 MINOR. Requirement coverage 99/106; requirement đạt ở mọi lượt chấm 70/81; pass rate theo lượt 89,8 % |
| `20261123-1435-suite-regression-9f2f367` | 9f2f367 | 2.310 lượt; 20 BLOCKER, 0 MAJOR, 43 MINOR. Requirement coverage 99/106; requirement đạt ở mọi lượt chấm 71/81; pass rate theo lượt 97,7 % |

## Revision history {#revision-history}

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 2026-11-23 | Bản đầu: nội dung bản giao, bằng chứng, giới hạn đã biết, tiêu chí vào HIL do nhóm đề xuất |

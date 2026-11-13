# Mentor Report

| Mục | Nội dung |
|---|---|
| Mã tài liệu | `PP-MR` |
| Phiên bản | 1.3 |
| Trạng thái | BL1 |
| Tác giả | thongbui |
| Người review |   |
| Cập nhật | 2026-11-13 |

## 1. Purpose and scope {#summary-scope}

- **Mục đích:** Tóm tắt thiết kế path planner và hệ thống đánh giá.
- **Phạm vi:** Technical Documents; Path Planner; 8 bộ Benchmark đánh giá Path Planner.

## 2. Hệ thống {#summary-system}

- **Bài toán:** Một path planner cho HWA, LKA, ELK, 20–50 Hz; path smooth, feasible; đổi chức năng không tạo step; chạy được trên lane model thật có lỗi.
- **Chu kỳ 40 Hz:** input check → latency compensation → reference line → arbitration ELK > LKA > HWA → path generation (Frenet) → stitching, continuity → feasibility → output.
- **Input:** LaneModel (ba lane và có nhiều loại mép đường), ObjectList, CAN khung gầm, VehicleStateEstimate, ego-motion, FunctionRequests, LongitudinalPlan, VehicleConfig.
- **Output:** Trajectory (31 điểm, 0–3 s), PathStatus, LateralLimits.
- **ODD:** Đường Việt Nam có vạch hoặc mép đường, làn 2,5–5,5 m; mọi xe gia đình rộng tới 2,5 m kể cả gương (QCVN 09:2015/BGTVT); một bộ calibration cho mọi xe.

## 3. Thiết kế chính {#summary-design}

| Chủ đề | Thiết kế | Phương án bị loại | ADR |
|---|---|---|---|
| Ngang và dọc | Hai khối trao đổi ràng buộc; planner gửi `v_max` để khối dọc giảm tốc trước cua | Gộp một planner; tách hoàn toàn (giữ làm đối chứng) | 001 |
| Trễ lane model | Bù theo stamp lúc chụp bằng ego-motion | Không bù (lệch 0,25 m ở 25 m); bù trễ danh định (0,05 m) | 002 |
| Trễ chưa biết | Theo dõi ở 170 ms, loại ở 250 ms | Một ngưỡng 170 ms | 003 |
| Cờ c0 jump | Planner tự kiểm tính nhất quán của biên ở hai thang; dùng chung cho nhảy vạch, nhận nhầm vạch, làn mở rộng | Dựa vào cờ của lane model | 006 |
| Mất vạch làn mình | Suy tâm làn từ vạch làn bên, mép đường đủ tin; chỉ HWA dùng | Bám path cũ 1s rồi báo không hợp lệ; lane model tự dựng | 011 |
| Không còn biên nào | Bám path cũ tối đa 1 s rồi báo không hợp lệ | 0,5 s; 2 s; 3 s | 009 |
| Dời tâm khi có xe lớn | Dời ra xa phần khoảng hở còn thiếu so với `gap_truck_min`; giới hạn offset theo khoảng trống thật, đúng cho mọi làn và mọi xe | Offset cố định ±0,3 m; cân bằng khoảng hở | 008 |
| Nhiễu và continuity | Bắt đầu từ path cũ, giới hạn tốc độ đổi tham chiếu, phạt jerk; chiếu path về ngưỡng liên tục | Lọc lại cảm biến trong planner | 004, 007 |
| Calibration | Một bộ cho mọi xe; planner chỉ biết xe qua VehicleConfig | Mỗi xe một bộ | 012 |
| Dạng bàn giao | Thư viện C11, API C, không cấp phát động, không I/O, không biến toàn cục; simulator gọi cùng thư viện qua adapter SIL | Python; prototype Python rồi port; C++17 | 013 |
| Trạng thái ngang, pha | Planner tự tính trạng thái ngang; PathStatus có pha riêng cho LKA và ELK | Dùng chung với khối Chức năng ADAS; một pha chung | 014, 015 |

Kỹ thuật lập path chọn bằng benchmark trong ba ứng viên: quintic theo thời lượng, lấy mẫu trong Frenet, QP.

## 4. Tuân thủ {#summary-compliance}

| Văn bản | Nội dung tuân thủ |
|---|---|
| UN R79 | HWA là ACSF B1: a_y ≤ 2,5 m/s² (giới hạn 3), jerk ≤ 5 m/s³, không đè vạch dưới aysmax, không thả lái đột ngột; LKA, ELK là CSF, ESF: can thiệp ≤ 10 s, cảnh báo; ghi đè ≤ 50 N |
| EU 2021/646 (ELKS) | ELK 70–130 km/h, mặc định bật; DTLE theo ELKS |
| Euro NCAP LSS, Safety Assist | DTLE ≥ −0,3 m (vạch), ≥ −0,1 m (mép đường); khoảng cách tới xe làn bên ≥ 0,3 m; ghi đè 3,0 Nm (≤ 3,5 Nm) |
| Đề bài | Lệch giữa hai path liên tiếp ≤ 0,05 m, 0,005 rad, 0,0003 1/m, trong tầm nhìn lane model báo; phần ngoài báo bằng `observed_horizon_s` |
| ISO 26262, ISO 21448 | HARA với ASIL đề xuất; 13 SOTIF triggering condition nối với test case |

Giới hạn quyền lái của LKA (a_y ≤ 3,0, thêm vào ≤ 1,5 m/s²) và ELK (a_y ≤ 4,0, thêm vào ≤ 3,0 m/s², jerk ≤ 10 m/s³) do nhóm tự thống nhất, vì quy định không cho số.

## 5. Kiểm chứng {#summary-verification}

- **Requirement:** 98 requirement (56 Safety, 20 Functional, 14 Interface, 8 Regulatory) chấm đạt hoặc trượt; 14 performance target đo và xếp hạng. Input ngoài dải (FunctionRequests quá tuổi, LongitudinalPlan ngoài dải) xử lý như chưa nhận. Truy vết tự động bằng `tools/trace.py`.
- **Calibration:** Hơn 70 calibration parameter, mỗi tham số có giá trị khởi đầu, dải quét và giới hạn lấy từ requirement.
- **Simulator:** Python và numpy, tất định, bước 1 ms; mô phỏng trễ, jitter, mất message, đồng hồ lệch, CAN có counter, CRC. Không có log xe thật.
- **Test:** 24 kịch bản × 3–5 biến thể, 23 loại lỗi bơm vào, 4 quét (độ trễ, tầm nhìn), vòng hở và vòng kín; bộ tối thiểu 3 × 5 của đề bài. Bộ Hồi quy 2.037 ca, bộ Đầy đủ 3.916 ca, chạy song song 4 tiến trình, kết quả tất định.
- **Kết luận:** Mức trượt suy từ Type của requirement (BLOCKER, MAJOR, MINOR). Kết luận là Không đạt, Không đạt quy định hoặc Đạt trong phạm vi đã thử; không ghi planner là an toàn. Lần chạy trượt có log MCAP.
- **Flexibility:** Cùng bản build và calibration chạy trên 6 vehicle profile. VP-0 là xe tham chiếu, VP-1 đến VP-4 trải từ 3.190 × 1.679 mm đến 5.119 × 2.004 mm (dài tổng thể × rộng thân xe) và VP-5 là profile tổng hợp rộng 2,5 m kể cả gương.
- **Công tâm:** Bên test chỉ thấy planner qua interface; chọn calibration trên bộ chỉnh, chấm trên bộ kiểm.

## 6. An toàn {#summary-safety}

| Safety goal | ASIL đề xuất |
|---|---|
| SG-01 Không can thiệp ngang vượt mức tài xế kiểm soát được | C (do ELK); B với HWA, LKA |
| SG-02 Không mất hỗ trợ đột ngột | B |
| SG-03 ELK can thiệp đủ | A |
| SG-04 Không giật lệnh lái | A |
| SG-05 Không chống lại tài xế | A |

## 7. Bộ tài liệu {#summary-requests}

| Tài liệu | Nội dung |
|---|---|
| [Software Requirements Specification](report.html?doc=path-planner-software-requirements-specification&lang=vi) | Requirement, performance target, ODD, giả định, giới hạn calibration |
| [Software Architectural Design](report.html?doc=path-planner-software-architectural-design&lang=vi) | Kiến trúc, chu kỳ, thiết kế, calibration parameter |
| [Architecture Decision Records](report.html?doc=path-planner-architecture-decision-records&lang=vi) | 15 quyết định, mỗi quyết định có phương án bị loại |
| [Software Detailed Design](report.html?doc=path-planner-software-detailed-design&lang=vi) | Thuật toán T1 đến T11, cấu trúc code |
| [Interface Control Document](report.html?doc=path-planner-interface-control-document&lang=vi) | 11 message, trường, tần số, timeout |
| [ADAS Function Specification](report.html?doc=adas-function-specification&lang=vi) | Khi nào HWA, LKA, ELK được can thiệp |
| [Hazard Analysis and Risk Assessment (HARA)](report.html?doc=path-planner-hazard-analysis-and-risk-assessment&lang=vi) | Hazard, ASIL đề xuất, safety goal, SOTIF |
| [Software Qualification Test Specification](report.html?doc=path-planner-software-qualification-test-specification&lang=vi) | Simulator, test case, tiêu chí, flexibility |

## Revision history {#revision-history}

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 2026-11-10 | Viết lại thành Technical Summary cho bộ tài liệu kỹ thuật BL1 |
| 1.1 | 2026-11-11 | Dời tâm theo PP-ADR-008 mới |
| 1.2 | 2026-11-12 | Liên tục giữa hai path chỉ xét phần trong tầm nhìn; Trajectory thêm `observed_horizon_s` |
| 1.3 | 2026-11-13 | Thêm PP-ADR-013 đến 015; cập nhật số requirement, lỗi, quét; thêm cỡ bộ chạy và cách kết luận |

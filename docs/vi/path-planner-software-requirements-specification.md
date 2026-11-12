# Software Requirements Specification

| Mục | Nội dung |
|---|---|
| Mã tài liệu | `PP-SRS` |
| Phiên bản | 1.10 |
| Trạng thái | BL1 |
| Tác giả | thongbui |
| Người review | thongbui |
| Cập nhật | 2026-11-12 |

## 1. Purpose and scope {#req-scope}

- **Mục đích:** Quy định path planner phải đạt gì, nhìn từ bên ngoài: qua input, output và chuyển động thật của xe trong simulator.
- **Phạm vi:** Path planner cho ba chức năng lateral L2/L2+: HWA, LKA, ELK.
- **Ngoài phạm vi:** Lane model, perception, khối Chức năng ADAS (quyết định khi nào can thiệp), Lateral Controller, EPS, khối dọc. Lực ghi đè ≤ 50 N (R79) thuộc Lateral Controller và EPS.
- **Nội dung:**

| Type | Ý nghĩa | Mục |
|---|---|---|
| Requirement | Bắt buộc, kiểm đạt hoặc trượt. Dùng: "phải", "không được" | 8 |
| Performance target | Đo và xếp hạng, không có ngưỡng đạt. Dùng: "nên" | 9 |
| Calibration parameter | Con số người thiết kế tự chọn. Tài liệu này chỉ ghi giới hạn; giá trị khởi đầu và dải quét ở tài liệu Software Architectural Design | 7 |

## 2. References {#req-references}

| Tài liệu | Dùng cho |
|---|---|
| Đề bài G1 (`G1_Path_Planning.pdf`) | Chức năng, tần số 20–50 Hz, ngưỡng liên tục giữa hai path, kịch bản bắt buộc |
| [UN Regulation No 79, OJ L 2025/3](https://upload.wikimedia.org/wikipedia/commons/f/f3/OJ_L_202500003_of_2025_-_EN_English.pdf) | aysmax và jerk của ACSF B1, thời lượng can thiệp của CSF, không thả lái đột ngột |
| [EU 2021/646 (ELKS)](https://lawplayer.com/eu/act/32021R0646) | Mức lấn vạch của ELK |
| [Euro NCAP LSS Test Protocol v4.3](https://cdn.euroncap.com/cars/assets/euro_ncap_lss_test_protocol_v43_f2ddd5f6d6.pdf), [Assessment Protocol SA v10.4.1](https://cdn.euroncap.com/cars/assets/euro_ncap_assessment_protocol_sa_collision_avoidance_v1041_fafe1dd418.pdf) | DTLE, khoảng cách tới xe ở làn bên |
| [ISO 11270:2014](https://standards.iteh.ai/catalog/standards/iso/808a3e9d-fc87-4892-85d1-6087e2ee3370/iso-11270-2014) | Jerk của LKA |
| [QCVN 09:2015/BGTVT](https://thongtinphapluat.bacgiang.gov.vn/documents/249229/997340/1501942804616_101671520818_VanBanGoc_QCVN%2009.signed.pdf/ada7de78-f0dd-4174-b0a5-1f8a63115728) | Bề rộng xe tối đa |
| ISO 26262, ISO 21448 | Safety requirement, SOTIF |
| EARS (Mavin và cộng sự, 2009) | Mẫu câu requirement |
| [Software Architectural Design](report.html?doc=path-planner-software-architectural-design&lang=vi), [Interface Control Document](report.html?doc=path-planner-interface-control-document&lang=vi), [ADAS Function Specification](report.html?doc=adas-function-specification&lang=vi), [Hazard Analysis and Risk Assessment (HARA)](report.html?doc=path-planner-hazard-analysis-and-risk-assessment&lang=vi), [Software Qualification Test Specification](report.html?doc=path-planner-software-qualification-test-specification&lang=vi) | Cách đáp ứng, schema, khi nào can thiệp, safety goal, cách kiểm chứng |

## 3. Conventions {#req-conventions}

| Mục | Quy ước |
|---|---|
| ID | `PP-SWR-nnn`, dùng chung cho requirement và performance target, đánh theo khối ở bảng dưới. Giả định: `PP-ASM-nnn` (mục 6). Không đánh số lại, không dùng lại; bị bỏ thì ghi `obsolete` |
| Type | Safety (kèm safety goal SG trong HARA), Regulatory, Functional, Interface, Performance |
| Kiểm chứng | Test, Analysis, Inspection, Demonstration. Test mặc định ở vòng hở, đo trên Trajectory; "Test, vòng kín" đo trên xe trong simulator. Mã S, F, Q ở Software Qualification Test Specification; biến thể trong ngoặc; "mọi kịch bản", "mọi lỗi". Cột này là nguồn duy nhất của truy vết |
| Calibration parameter | Viết dạng `ten_tham_so`. Test dùng giá trị trong bộ calibration đang chạy |
| ODD | Mọi requirement phải thoả trong toàn bộ ODD ở mục 5, với cùng một bộ calibration |
| Baseline | BL1 là phiên bản 1.0. Sau BL1, đổi một requirement hoặc giả định phải ghi lý do, liệt kê chỗ bị ảnh hưởng (`tools/trace.py`) và tăng phiên bản |

| Dải ID | Khối |
|---|---|
| 001–009 | Giới hạn a_y của HWA |
| 010–029 | Output và chu kỳ |
| 030–049 | Arbitration |
| 050–079 | HWA |
| 080–099 | LKA, ELK |
| 100–119 | Giới hạn, liên tục, khả thi |
| 120–149 | Chịu lỗi |
| 150–169 | Interface với khối dọc |

## 4. Definitions {#req-definitions}

| Đại lượng | Định nghĩa |
|---|---|
| Chu kỳ | 25 ms (40 Hz) |
| Chức năng đang lái | `active_function` trong PathStatus. "HWA đang lái" nghĩa là `active_function = HWA` |
| Làn thật | Làn xe đang ở, theo ground truth của simulator. Với làn hỗn hợp ô tô và xe máy, là phần dành cho ô tô |
| Lệch ngang của path | Khoảng cách ngang lớn nhất giữa path và tâm làn thật, đo tại cùng vị trí dọc, trên đoạn 0–1 s của path, trừ khi requirement nêu đoạn khác |
| a_y của path | v²·κ tại từng điểm của Trajectory, với v = `longitudinal_velocity`, κ = `curvature` |
| a_y cần | v²·κ của tâm làn thật tại điểm tương ứng trên path |
| Tầm nhìn của lane model | Đoạn camera thật sự quan sát được trên cả hai biên làn đang dùng, trong mô hình cảm biến của simulator. Không tính phần lane model báo dài hơn đoạn đã quan sát |
| a_y cần lớn nhất | Giá trị lớn nhất của a_y cần trên đoạn 0–3 s, chỉ xét phần trong tầm nhìn của lane model |
| a_y thêm vào | a_y của path trừ a_y cần, tại cùng một điểm |
| Jerk ngang của path | Đạo hàm theo thời gian của a_y của path, trung bình trượt 0,5 s |
| Hai path liên tiếp | So trên đoạn thời gian cả hai cùng mô tả, chỉ ở các điểm của path mới nằm trong tầm nhìn mà lane model báo cho frame planner dùng ở chu kỳ đó; chu kỳ không có lane model thì cả path. Path cũ đưa về base_link của path mới bằng chuyển động thật của xe |
| Biên làn đủ tin | Vạch L1, R1: status MEASURED, confidence ≥ `conf_ego`. Vạch L2, R2 hoặc mép đường, khi dùng để suy ra tâm làn: status MEASURED, confidence ≥ `conf_inferred` |
| DLC | Như ADAS Function Specification, mục 5, tính trên làn thật và vị trí thật của xe |
| DTLE | Khoảng cách từ mép ngoài lốp tới mép trong của vạch, nhỏ nhất trong một lần can thiệp; âm là đã vượt vạch (Euro NCAP) |
| Khoảng trống mỗi bên | (bề rộng làn thật − bề rộng xe kể cả gương) / 2 |
| Xe lớn | Vật thể ở làn bên kề, bề rộng ≥ 2,3 m |
| Ngang hàng | Phần dọc của xe lớn chồng lên thân xe |
| Khoảng hở tới xe lớn | Khoảng cách ngang từ thân xe (kể cả gương), khi xe ở tâm làn thật, tới mép gần nhất của xe lớn |
| Điều kiện kết thúc | DLC ≥ 0 ở cả hai phía, trị tuyệt đối của v_lat ≤ `v_lat_end`, trị tuyệt đối của góc lệch so với hướng làn ≤ `heading_end`, trị tuyệt đối của a_y thêm vào ≤ `ay_add_end` |

## 5. Operating conditions (ODD) {#req-odd}

| Điều kiện | Giá trị | Nguồn |
|---|---|---|
| Chức năng | HWA, LKA, ELK. Dải tốc độ và điều kiện kích hoạt ở ADAS Function Specification | — |
| Đường | Có vạch hoặc mép đường. Bề rộng làn 2,5–5,5 m, kể cả làn hỗn hợp ô tô và xe máy 4,5 m | mentor (PP-ASM-015) |
| Xe | Mọi xe gia đình rộng ≤ 2,5 m kể cả gương. Thông số xe đọc từ VehicleConfig | QCVN 09:2015/BGTVT 2.1.1.1 b (PP-ASM-016) |
| Calibration | Một bộ calibration cho mọi xe | nhóm tự thống nhất |
| Tần số | 40 Hz | mentor |

## 6. Assumptions and dependencies {#req-assumptions}

Mỗi dòng ghi requirement nào dựa vào nó và cách kiểm lại khi có xe thật.

| ID | Giả định | Ảnh hưởng tới | Kiểm lại thế nào | Nguồn |
|---|---|---|---|---|
| PP-ASM-001 | Trễ lane model từ lúc camera chụp tới lúc gửi là 100 ± 20 ms | PP-SWR-013, 131, 133, 134 | Đo stamp lúc chụp so với lúc nhận, phân vị 99,9 % | nhóm tự thống nhất |
| PP-ASM-002 | Trễ ObjectList như lane model | PP-SWR-131, 133 | Như PP-ASM-001 | nhóm tự thống nhất |
| PP-ASM-003 | Trễ khung CAN khung gầm khoảng 5 ms, chưa kể trễ bộ lọc | Software Architectural Design mục 3.3 | Đo trên bus | nhóm tự thống nhất |
| PP-ASM-004 | Trễ bộ lọc yaw rate chưa biết; planner coi là 0 nếu không được báo | PP-SWR-138 | Tương quan chéo giữa bản thô và bản đã lọc | mentor |
| PP-ASM-005 | Trễ VehicleStateEstimate khoảng 10 ms | PP-SWR-080, 144 | Đo stamp so với lúc nhận | nhóm tự thống nhất |
| PP-ASM-006 | Trễ FunctionRequests khoảng 20 ms | PP-SWR-038 | Đo stamp so với lúc nhận | nhóm tự thống nhất |
| PP-ASM-007 | Trễ truyền Trajectory và PathStatus khoảng 1 ms | Software Architectural Design mục 3.3 | Đo trên bus | nhóm tự thống nhất |
| PP-ASM-008 | IMU tới planner đã sạch: bias và nhiễu đã được lọc ở phía trước | PP-SWR-124, 135, 136 | Đo bias và nhiễu còn lại khi xe đứng yên và chạy thẳng | mentor |
| PP-ASM-009 | Lane model không gửi cờ báo c0 jump | PP-SWR-121 | Đọc giao thức của lane model thật | nhóm tự thống nhất |
| PP-ASM-010 | Khi mất cả hai vạch, lane model dựng lại vạch tối đa 1 s rồi báo mất | PP-SWR-124 | Đọc thông số lane model | nhóm tự thống nhất |
| PP-ASM-011 | Nhiễu còn lại sau lane model: σ_c0 = 0,03 m, σ_c1 = 0,002 ban ngày; gấp 2,5 lần ban đêm hoặc mưa | PP-SWR-080, 120 | Đo trên xe có ground truth | nhóm tự thống nhất |
| PP-ASM-012 | Đồng hồ lệch tới ±10 ms trước lần đồng bộ đầu; sau đồng bộ gPTP lệch ±50 µs | PP-SWR-132, 137 | Đo lúc khởi động và khi chạy | nhóm tự thống nhất |
| PP-ASM-013 | Ego-motion trả Δx, Δy, Δψ giữa hai thời điểm bất kỳ trong 0,5 s gần nhất | PP-SWR-012, 131 | Thống nhất interface với nhóm ego-motion | nhóm tự thống nhất |
| PP-ASM-014 | Trễ chấp hành của EPS danh định 50 ms | PP-SWR-091 | Đo đáp ứng bậc của EPS | nhóm tự thống nhất |
| PP-ASM-015 | Bề rộng làn trên đường Việt Nam 2,5–5,5 m, kể cả làn hỗn hợp ô tô và xe máy 4,5 m | PP-SWR-062, 063 | Đo trên tuyến thử | mentor |
| PP-ASM-016 | Bề rộng xe, kể cả gương, không vượt 2,5 m | PP-SWR-062, 063 | Đọc VehicleConfig | QCVN 09:2015/BGTVT 2.1.1.1 b |
| PP-ASM-017 | Lateral Controller bù phần trễ sau planner, bằng cách đọc điểm path theo `header.stamp_us` và `time_from_start` (PP-ADR-010) | PP-SWR-012, 086, 091 | Thống nhất với đội Lateral Controller | nhóm tự thống nhất |
| PP-ASM-018 | ASIL của các safety requirement lấy theo kết quả confirmation review của phòng an toàn trên HARA | Mọi requirement loại Safety | Kết quả review của phòng an toàn | nhóm tự thống nhất |
| PP-ASM-019 | Nền tảng đích (ECU, hệ điều hành, middleware, coding standard) chưa biết; planner chỉ cần trình biên dịch C11 (PP-ADR-013) | Mọi requirement, qua cách triển khai | Hỏi mentor nền tảng đích và coding standard | nhóm tự thống nhất |
| PP-ASM-021 | Lateral Controller không dựa vào phần path sau `observed_horizon_s` để tính lệnh lái, hoặc chịu được bước nhảy ở phần đó | PP-SWR-018, 100, 101, 102 | Thống nhất với đội Lateral Controller | nhóm tự thống nhất |
| PP-ASM-020 | Tầm nhìn của lane model thay đổi theo từng vạch và từng frame; điểm đầu, điểm cuối thật chưa biết. Benchmark dùng 0–80 m danh định, quét điểm cuối 10–126 m | PP-SWR-017, 149, 151 | Đọc phân bố `line start distance`, `line end distance` trong log xe thật | nhóm tự thống nhất |

## 7. Calibration parameter limits {#req-calibration-limits}

Chỉ liệt kê tham số mà requirement trỏ tới. Danh mục đầy đủ, giá trị khởi đầu và dải quét ở tài liệu Software Architectural Design.

| Tham số | Ý nghĩa | Giới hạn | Nguồn của giới hạn |
|---|---|---|---|
| `conf_ego` | Độ tin tối thiểu của vạch L1, R1 | 0–1 | — |
| `conf_edge` | Độ tin tối thiểu của mép đường ELK đo trực tiếp | 0–1 | PP-SWR-047 |
| `conf_inferred` | Độ tin tối thiểu của biên dùng để suy ra tâm làn | > `conf_ego` | Biên suy ra cộng thêm sai số của khoảng cách nhớ được |
| `T_coast` | Thời gian bám path cũ khi không còn biên làn đủ tin | 0–1 s | Analysis: lệch dead reckoning 0,06 m sau 1 s (Software Architectural Design Appendix A.4) |
| `free_space_min` | Khoảng trống tối thiểu mỗi bên để HWA khả dụng | ≥ 0 m | PP-SWR-051 |
| `epsilon_ay` | Mức a_y của path được thấp hơn aysmax khi a_y cần vượt aysmax | 0–2,5 m/s² | — |
| `gap_truck_min` | Khoảng hở tới xe lớn mà dưới mức đó HWA dời tâm | > 0 m | — |
| `v_lat_end`, `heading_end`, `ay_add_end` | Ngưỡng của điều kiện kết thúc | ≥ 0 | — |
| `T_end_hold` | Thời gian điều kiện kết thúc phải giữ liên tục trước khi báo COMPLETED | ≥ 0 s | — |

## 8. Requirements {#req-requirements}

### 8.1 Output và chu kỳ {#req-output}

| ID | Yêu cầu | Kiểm chứng | Type | Nguồn |
|---|---|---|---|---|
| PP-SWR-010 | Planner phải gửi Trajectory và PathStatus mỗi chu kỳ | Test: mọi kịch bản | Interface | mentor |
| PP-SWR-011 | Trajectory phải theo định dạng ở Interface Control Document: 31 điểm, bước 0,1 s, phủ 0–3 s, frame_id = base_link | Inspection | Interface | nhóm tự thống nhất (Autoware Trajectory) |
| PP-SWR-012 | `header.stamp_us` của Trajectory phải là thời điểm mà path mô tả, đã bù trễ của lane model | Inspection; Test: Q1 | Interface | nhóm tự thống nhất |
| PP-SWR-014 | `header.counter` phải tăng 1 sau mỗi message, quay vòng 0–255 | Inspection; Test: mọi kịch bản | Interface | nhóm tự thống nhất |
| PP-SWR-018 | `Trajectory.observed_horizon_s` không được lớn hơn thời điểm trên path mà path ra khỏi tầm nhìn lane model báo cho frame planner dùng ở chu kỳ đó quá 0,1 s | Test: mọi kịch bản | Interface | nhóm tự thống nhất |
| PP-SWR-017 | Planner phải nhận lane model với mọi `view_range_end > view_range_start` của từng vạch và mép đường. Phần tầm nhìn vượt 126 m không được làm input bị coi là không hợp lệ | Test: F22 (e), Q4 | Interface | nhóm tự thống nhất |
| PP-SWR-015 | Planner phải ghi thời gian tính của từng chu kỳ | Inspection | Interface | nhóm tự thống nhất |

### 8.2 Arbitration {#req-arbitration}

| ID | Yêu cầu | Kiểm chứng | Type | Nguồn |
|---|---|---|---|---|
| PP-SWR-030 | Planner phải chọn chức năng đang lái theo thứ tự ELK > LKA > HWA, chỉ xét chức năng có state = REQUEST | Test: S9 (a) | Safety, SG-01 | nhóm tự thống nhất |
| PP-SWR-031 | Khi chức năng đang lái đổi, path phải thoả PP-SWR-100 đến 102, trừ lúc LKA hoặc ELK bắt đầu mà xe thật đang lệch khỏi path cũ hơn 0,1 m hoặc 0,1 m/s; khi đó áp PP-SWR-080 | Test: S9, S8c (d) | Safety, SG-04 | đề bài |
| PP-SWR-032 | Khi điều kiện kết thúc của LKA hoặc ELK đã giữ liên tục `T_end_hold`, planner phải đặt pha của chức năng đó thành COMPLETED | Test: S4, S5 | Functional | nhóm tự thống nhất |
| PP-SWR-033 | Sau COMPLETED, planner phải chọn chức năng đang lái theo PP-SWR-030 trong các chức năng còn ở REQUEST, không tính chức năng vừa COMPLETED; không còn chức năng nào thì chọn NONE | Test: S9 (b) | Functional | nhóm tự thống nhất |
| PP-SWR-034 | Nếu chức năng vừa COMPLETED vẫn giữ REQUEST, thì planner không được bắt đầu lần can thiệp mới cho chức năng đó cho tới khi state rời REQUEST rồi quay lại | Test: S16 (a, b) | Functional | nhóm tự thống nhất |
| PP-SWR-035 | Mỗi lần can thiệp mới của LKA hoặc ELK phải có cùng giới hạn như lần đầu, không phụ thuộc số lần đã can thiệp | Test: S16 (c, d, e) | Functional | nhóm tự thống nhất |
| PP-SWR-036 | Khi chức năng đang can thiệp rời REQUEST giữa chừng, planner phải chuyển từ trạng thái hiện tại sang chức năng được chọn theo PP-SWR-030 trong các chức năng còn ở REQUEST | Test: S9 (d), S8c (d) | Functional | nhóm tự thống nhất |
| PP-SWR-037 | Khi chức năng đang can thiệp rời REQUEST giữa chừng qua một message hợp lệ và không còn chức năng đủ điều kiện, planner phải báo `active_function = NONE` với `path_valid = true` nếu các input bắt buộc còn hợp lệ | Test: S9 (d), S8c (d) | Safety, SG-02 | nhóm tự thống nhất |
| PP-SWR-038 | Planner phải phản ánh thay đổi của FunctionRequests vào output trong không quá một chu kỳ kể từ lúc nhận message | Test: S9, Q3 | Functional | nhóm tự thống nhất |
| PP-SWR-039 | Trong khi `driver_override = true`, điểm đầu của path phải trùng vị trí ngang hiện tại của xe, lệch ≤ 0,05 m | Test: S9 (c), S17 | Safety, SG-05 | nhóm tự thống nhất |
| PP-SWR-040 | Khi `driver_override` chuyển về false trong lúc HWA ở REQUEST, điểm đầu của path HWA phải trùng vị trí ngang của xe lúc đó, lệch ≤ 0,05 m | Test: S9 (c), S17 | Safety, SG-05 | nhóm tự thống nhất |
| PP-SWR-041 | Planner phải giữ pha của mỗi chức năng ở COMPLETED tới khi state của chức năng đó rời REQUEST | Test: S16 (a, b) | Functional | nhóm tự thống nhất |
| PP-SWR-042 | Khi HWA rời REQUEST và không chức năng nào ở REQUEST, planner phải đặt `active_function = NONE` và giữ `path_valid = true` | Test: S9 (e), F22 (f) | Safety, SG-02 | nhóm tự thống nhất |
| PP-SWR-043 | Trong khi `path_valid = false`, `active_function` phải bằng NONE | Test: F05, F12 (Lane Model), F20 | Functional | nhóm tự thống nhất |
| PP-SWR-044 | Khi input hồi phục sau lúc `path_valid = false`, điểm đầu của path mới phải khớp trạng thái ngang thật của xe theo dung sai của PP-SWR-080 | Test: F12 (Lane Model, hồi phục) | Functional | nhóm tự thống nhất |
| PP-SWR-045 | Sau khi input hồi phục, planner chỉ được bắt đầu can thiệp LKA hoặc ELK khi state của chức năng đó rời REQUEST rồi quay lại | Test: F12 (Lane Model, hồi phục) | Safety, SG-01 | nhóm tự thống nhất |
| PP-SWR-046 | Nếu VehicleStateEstimate không hợp lệ trong lúc LKA hoặc ELK đang can thiệp, thì planner phải tiếp tục path can thiệp đó tới khi kết thúc | Test: F12 (v_y, trong S5) | Safety, SG-03 | nhóm tự thống nhất |
| PP-SWR-047 | Trong khi tâm làn chỉ suy được từ biên ngoài làn đang chạy, planner không được chọn LKA hoặc ELK. Ngoại lệ cho ELK mép đường khi biên nguy hiểm của làn đang chạy là mép MEASURED với confidence ≥ `conf_edge` và có biên đối diện đủ tin hoặc bề rộng làn đã nhớ | Test: F21 | Safety, SG-01 | mentor, nhóm làm rõ phạm vi ELK mép đường theo PP-TS-007 |

### 8.3 HWA: giới hạn a_y {#req-hwa-lateral-limit}

| ID | Yêu cầu | Kiểm chứng | Type | Nguồn |
|---|---|---|---|---|
| PP-SWR-001 | Trong khi HWA đang lái, a_y của path phải ≤ aysmax = 2,5 m/s² tại mọi điểm | Test: S1, S1b, S12 (a) | Regulatory, SG-01 | R79 5.6.2.1.3 (≤ 3 m/s²) |
| PP-SWR-003 | Trong khi HWA đang lái, jerk ngang của path phải ≤ 5 m/s³ | Test: S1 | Regulatory, SG-01 | R79 5.6.2.1.3 c |
| PP-SWR-005 | Nếu a_y cần lớn nhất > aysmax trong khi HWA đang lái, thì planner phải giữ `path_valid = true` và `active_function = HWA`, trừ khi arbitration chuyển sang LKA hoặc ELK | Test: S1b | Regulatory, SG-02 | R79 5.6.2.2.3 |
| PP-SWR-006 | Nếu a_y cần > aysmax tại một điểm trên đoạn 0–1 s của path trong khi HWA đang lái, thì a_y của path tại điểm đó phải ≥ aysmax − `epsilon_ay` | Test: S1b | Regulatory, SG-02 | R79 5.6.2.2.3 (hỗ trợ trong khả năng); mức `epsilon_ay`: nhóm tự thống nhất |
| PP-SWR-007 | Khi một lốp trước bắt đầu đè vạch trong lúc HWA đang lái và a_y cần lớn nhất > aysmax, `lateral_limit_reached` phải đang là true | Test, vòng kín: S1b | Regulatory, SG-01 | R79 5.6.2.2.3; Annex 8, 3.2.5.2 |
| PP-SWR-009 | Planner phải gửi cùng một giá trị `lateral_limit_reached` trong PathStatus và LateralLimits của cùng chu kỳ | Inspection; Test: S14 | Interface | nhóm tự thống nhất |

### 8.4 HWA: giữ làn và dời tâm {#req-hwa-centering}

| ID | Yêu cầu | Kiểm chứng | Type | Nguồn |
|---|---|---|---|---|
| PP-SWR-051 | Trong khi HWA đang lái, a_y cần lớn nhất ≤ aysmax và khoảng trống mỗi bên ≥ `free_space_min`, DLC ở cả hai phía phải ≥ 0 | Test, vòng kín: S1 | Regulatory, SG-01 | R79 5.6.2.1.1 |
| PP-SWR-052 | Khi HWA bắt đầu lái lúc xe lệch tâm làn tới 0,5 m, chức năng đang lái phải giữ là HWA trong suốt đoạn đưa về giữa | Test: S2 | Functional | nhóm tự thống nhất |
| PP-SWR-054 | Trong khi HWA ở REQUEST và tốc độ xe trong khoảng 0–60 km/h, planner phải tiếp tục gửi path hợp lệ cho HWA | Test: S11 | Functional | nhóm tự thống nhất |
| PP-SWR-055 | Trong khi một xe lớn ngang hàng ở làn bên kề có khoảng hở tới xe lớn < `gap_truck_min` và làn bên kia không có xe lớn ngang hàng, path phải lệch khỏi tâm làn thật về phía xa xe lớn | Test: S3 | Functional | đề bài |
| PP-SWR-056 | Trong khi có xe lớn ngang hàng với khoảng hở tới xe lớn < `gap_truck_min`, path không được lệch khỏi tâm làn thật về phía xe lớn có khoảng hở nhỏ nhất | Test: S3, S3b, S15 | Safety, SG-01 | mentor |
| PP-SWR-058 | Khi xe lớn ở làn bên kề đang tới gần, path phải bắt đầu dời trước lúc xe lớn tới ngang hàng | Test: S3 | Functional | đề bài |

### 8.5 HWA: làn thay đổi và ODD {#req-hwa-lane-change}

| ID | Yêu cầu | Kiểm chứng | Type | Nguồn |
|---|---|---|---|---|
| PP-SWR-060 | Khi một biên làn mở rộng (làn dừng khẩn cấp, tách nhánh, thêm làn), DLC so với biên làn thật ở phía mở rộng phải ≥ 0 | Test, vòng kín: S6b | Safety, SG-01 | mentor |
| PP-SWR-061 | Khi lane model chuyển sang làn mới, path phải thoả PP-SWR-100 đến 102 | Test: S17 | Safety, SG-04 | nhóm tự thống nhất |
| PP-SWR-062 | Mọi requirement ở mục 8 phải thoả trong toàn bộ ODD ở mục 5, với cùng một bộ calibration | Test: S19 | Functional | nhóm tự thống nhất |
| PP-SWR-063 | Khi khoảng trống mỗi bên nhỏ hơn `free_space_min`, planner phải đặt `lane_too_narrow = true` trong PathStatus | Test: S19 (b) | Safety, SG-01 | nhóm tự thống nhất |

### 8.6 LKA và ELK {#req-intervention}

| ID | Yêu cầu | Kiểm chứng | Type | Nguồn |
|---|---|---|---|---|
| PP-SWR-080 | Khi LKA hoặc ELK bắt đầu can thiệp, điểm đầu của path phải khớp trạng thái ngang thật của xe: lệch vị trí ≤ 0,1 m, lệch v_lat ≤ 0,1 m/s | Test: S4, S5, S6 | Functional | đề bài, dung sai do nhóm tự thống nhất |
| PP-SWR-083 | Một lần LKA hoặc ELK phải kết thúc, bằng COMPLETED hoặc bị hủy, trong ≤ 10 s | Test: S4, S4b, S5, S6, S7, S8, S8b (d, e) | Safety, SG-01 | nhóm tự thống nhất, dựa trên R79 5.1.6.1.2.1 (quá 10 s phải cảnh báo âm thanh) |
| PP-SWR-084 | Khi LKA báo COMPLETED, DLC ở phía xe đã trôi về phải ≥ 0 | Test, vòng kín: S4 | Functional | đề bài |
| PP-SWR-085 | Sau một lần LKA hoặc ELK, DLC nhỏ nhất ở phía đối diện phải ≥ 0 | Test, vòng kín: S4, S4b, S5, S6, S7, S8, S8b (d, e) | Safety, SG-01 | đề bài |
| PP-SWR-086 | DTLE nhỏ nhất trong một lần can thiệp phải ≥ −0,3 m với LKA và ELK vạch liền, và ≥ −0,1 m với ELK mép đường | Test, vòng kín: S4, S5, S6 | Regulatory, SG-03 | Euro NCAP Assessment 4.3.2, 4.3.3.3; EU 2021/646 3.6.2 |
| PP-SWR-088 | Trong lúc ELK can thiệp vì xe ở làn bên, khoảng cách ngang nhỏ nhất tới xe đó phải ≥ 0,3 m | Test, vòng kín: S7, S8 | Regulatory, SG-03 | Euro NCAP SA 4.3.3.4 (no impact) là mức tối thiểu, 0,3 m theo LSS 7.4.7, nhóm chọn chặt hơn |
| PP-SWR-089 | Nếu ELK được yêu cầu khi lốp trước đã sang quá 0,3 m qua vạch phía side, thì planner không được bắt đầu can thiệp ELK đó | Test: S8 | Safety, SG-01 | nhóm tự thống nhất |
| PP-SWR-090 | Planner không được báo COMPLETED khi điều kiện kết thúc chưa giữ liên tục `T_end_hold` | Test: S4, S5 | Functional | nhóm tự thống nhất |
| PP-SWR-091 | Khi trễ EPS tới 100 ms, DTLE nhỏ nhất phải vẫn đạt PP-SWR-086 | Test, vòng kín: S13 (a, b) | Safety, SG-03 | nhóm tự thống nhất |

Giới hạn 083 khống chế thời gian planner giữ quyền lái của chức năng can thiệp khi xe chưa ổn định. Khi hết hạn, arbitration nhả chức năng can thiệp và controller áp dụng cơ chế bàn giao hiện có.

### 8.7 Giới hạn, liên tục, khả thi {#req-limits}

| ID | Yêu cầu | Kiểm chứng | Type | Nguồn |
|---|---|---|---|---|
| PP-SWR-100 | Trong khi `path_valid = true`, lệch ngang giữa hai path liên tiếp phải ≤ 0,05 m | Test: mọi kịch bản, mọi lỗi | Safety, SG-04 | đề bài |
| PP-SWR-101 | Trong khi `path_valid = true`, lệch hướng giữa hai path liên tiếp phải ≤ 0,005 rad | Test: mọi kịch bản, mọi lỗi | Safety, SG-04 | đề bài |
| PP-SWR-102 | Trong khi `path_valid = true`, lệch độ cong giữa hai path liên tiếp phải ≤ 0,0003 1/m | Test: mọi kịch bản, mọi lỗi | Safety, SG-04 | đề bài |
| PP-SWR-110 | Trong khi LKA đang lái, a_y của path phải ≤ 3,0 m/s² | Test: S4, S4b | Safety, SG-01 | nhóm tự thống nhất |
| PP-SWR-111 | Trong khi ELK đang lái, a_y của path phải ≤ 4,0 m/s² | Test: S5, S6, S7, S8, S8b (d, e) | Safety, SG-01 | nhóm tự thống nhất |
| PP-SWR-112 | Trong khi LKA đang lái, a_y thêm vào phải ≤ 1,5 m/s² | Test: S4, S4b | Safety, SG-01 | nhóm tự thống nhất |
| PP-SWR-113 | Trong khi ELK đang lái, a_y thêm vào phải ≤ 3,0 m/s² | Test: S5, S6, S7, S8, S8b (d, e) | Safety, SG-01 | nhóm tự thống nhất |
| PP-SWR-114 | Trong khi LKA đang lái, jerk ngang của path phải ≤ 5 m/s³ | Test: S4, S4b | Safety, SG-01 | ISO 11270, cần kiểm số mục |
| PP-SWR-115 | Trong khi ELK đang lái, jerk ngang của path phải ≤ 10 m/s³ | Test: S5, S6, S7, S8, S8b (d, e) | Safety, SG-01 | nhóm tự thống nhất |
| PP-SWR-116 | `front_wheel_angle` tại mọi điểm của path phải ≤ `max_wheel_angle` của VehicleConfig | Test: mọi kịch bản | Safety | VehicleConfig |
| PP-SWR-117 | Tốc độ quay vô lăng suy ra từ path (tốc độ đổi `front_wheel_angle` nhân `steering_ratio`) phải ≤ `max_steering_wheel_rate` của VehicleConfig | Test: mọi kịch bản | Safety | VehicleConfig |

Nguồn của giới hạn quyền lái: R79 không giới hạn a_y của CSF. ELK 4,0 m/s² còn dư dưới giới hạn bám khoảng 4,9 m/s² trên đường ướt μ = 0,5. Giới hạn của LKA và a_y thêm vào do nhóm tự thống nhất.

### 8.8 Chịu lỗi: lane model {#req-lane-faults}

| ID | Yêu cầu | Kiểm chứng | Type | Nguồn |
|---|---|---|---|---|
| PP-SWR-120 | Khi lane model có nhiễu c0, c1 tới mức ban đêm (gấp 2,5 lần ban ngày), path phải thoả giới hạn jerk của chức năng đang lái và PP-SWR-100 đến 102 | Test: F01 | Safety, SG-01 | nhóm tự thống nhất |
| PP-SWR-121 | Khi c0 nhảy 0,3–1,0 m trong một frame, path phải thoả PP-SWR-100 đến 102 | Test: F02 | Safety, SG-04 | đề bài |
| PP-SWR-149 | Khi tầm nhìn của lane model ngắn lại trong chốc lát, khác nhau giữa các vạch, đổi theo từng frame, hoặc được báo dài hơn đoạn đã thật sự quan sát, PP-SWR-051 và 100 đến 102 phải vẫn thoả | Test, vòng kín: F22 (a, b, c, d, e, f) | Safety, SG-01 | đề bài (detection range là một tín hiệu chất lượng) |
| PP-SWR-122 | Khi lane model nhận nhầm vạch làn bên, PP-SWR-051 và 100 đến 102 phải vẫn thoả | Test, vòng kín: F03 | Safety, SG-01 | nhóm tự thống nhất |
| PP-SWR-123 | Khi lane model mất một vạch, PP-SWR-051 và 100 đến 102 phải vẫn thoả | Test, vòng kín: F04 (a–d) | Safety, SG-01 | nhóm tự thống nhất |
| PP-SWR-124 | Khi lane model không còn biên làn đủ tin nào (vạch làn mình, vạch làn bên, mép đường) hoặc không hợp lệ, planner phải giữ `path_valid = true` trong `T_coast` rồi đặt `path_valid = false`, sai lệch thời điểm không quá một chu kỳ | Test: F05, F21 (e), F12 (Lane Model) | Safety, SG-02 | nhóm tự thống nhất |
| PP-SWR-147 | Khi lane model mất cả hai vạch của làn mình mà còn ít nhất một biên làn đủ tin khác, planner phải giữ `path_valid = true` | Test: F21 (a–d) | Functional | mentor |
| PP-SWR-148 | Khi lane model mất cả hai vạch của làn mình mà còn ít nhất một biên làn đủ tin khác, PP-SWR-051 và 100 đến 102 phải vẫn thoả | Test, vòng kín: F21 (a–d) | Safety, SG-01 | nhóm tự thống nhất |

### 8.9 Chịu lỗi: thời gian và toàn vẹn {#req-timing-faults}

| ID | Yêu cầu | Kiểm chứng | Type | Nguồn |
|---|---|---|---|---|
| PP-SWR-126 | Khi message bị mất, lẻ hoặc thành chuỗi, hoặc có jitter ±20 ms, path phải thoả PP-SWR-100 đến 102 và giới hạn jerk của chức năng đang lái | Test: F10 | Safety, SG-04 | nhóm tự thống nhất |
| PP-SWR-127 | Khi message đến muộn hoặc sai thứ tự, path phải thoả PP-SWR-100 đến 102 | Test: F11 | Safety, SG-04 | nhóm tự thống nhất |
| PP-SWR-128 | Trong khi camera gửi 20 Hz và planner chạy 40 Hz, path phải thoả PP-SWR-100 đến 102 ở mọi chu kỳ | Test: mọi kịch bản, F13 | Safety, SG-04 | nhóm tự thống nhất |
| PP-SWR-129 | Nếu message bị lặp (counter lặp), thì output phải giống ca không lỗi cùng seed | Test: F15 (lặp) | Safety | nhóm tự thống nhất |
| PP-SWR-130 | Nếu counter nhảy hoặc đứng yên, valid = false, qualifier FAULT hoặc CRC sai, thì output phải giống ca mất message tương ứng | Test: F15 (nhảy, đứng yên), F16, F17 | Safety | nhóm tự thống nhất |
| PP-SWR-131 | Nếu tuổi của lane model hoặc ObjectList vượt 250 ms, thì planner phải coi input đó không hợp lệ | Test: Q1 (300 ms) | Safety | nhóm tự thống nhất |
| PP-SWR-132 | Nếu stamp của input ở tương lai quá 10 ms, thì planner phải coi input đó không hợp lệ | Test: F19 | Safety | nhóm tự thống nhất |
| PP-SWR-133 | Trong khi tuổi của lane model hoặc ObjectList trong khoảng 170–250 ms, planner phải tiếp tục dùng input đó | Test: Q1 (200 ms) | Functional | nhóm tự thống nhất |
| PP-SWR-134 | Planner phải ghi log số frame lane model và ObjectList có tuổi vượt 170 ms | Inspection | Functional | nhóm tự thống nhất |

Nguồn: 170 ms = trễ giả định lớn nhất 120 ms (PP-ASM-001) cộng 50 ms; 250 ms = trễ lớn nhất benchmark quét (200 ms) cộng 50 ms; 10 ms = lệch đồng hồ lớn nhất trước lần đồng bộ đầu (PP-ASM-012).

### 8.10 Chịu lỗi: input không hợp lệ {#req-invalid-input}

| ID | Yêu cầu | Kiểm chứng | Type | Nguồn |
|---|---|---|---|---|
| PP-SWR-140 | Nếu ObjectList không hợp lệ, thì planner phải đưa phần dời tâm của HWA về 0, vẫn thoả PP-SWR-001, 003 và 100 đến 102 | Test: F12 (Perception, trong S3) | Safety | nhóm tự thống nhất |
| PP-SWR-141 | Nếu ObjectList không hợp lệ, thì planner vẫn phải thực hiện can thiệp ELK được yêu cầu | Test: F12 (Perception, trong S5) | Safety, SG-03 | nhóm tự thống nhất |
| PP-SWR-142 | Nếu IMU, tốc độ hoặc góc lái không hợp lệ, thì planner phải đặt `path_valid = false` trong không quá một chu kỳ | Test: F12 (IMU, tốc độ, góc lái), F17 | Safety | nhóm tự thống nhất |
| PP-SWR-143 | Nếu ego-motion không hợp lệ, thì planner phải đặt `path_valid = false` trong không quá một chu kỳ | Test: F20 | Safety | nhóm tự thống nhất |
| PP-SWR-144 | Nếu VehicleStateEstimate không hợp lệ, thì planner không được bắt đầu can thiệp LKA hoặc ELK mới | Test: F12 (v_y) | Safety | nhóm tự thống nhất |
| PP-SWR-145 | Nếu FunctionRequests quá timeout 75 ms, thì planner phải đặt `active_function = NONE` và `path_valid = false` trong không quá một chu kỳ | Test: F12 (FunctionRequests) | Safety | nhóm tự thống nhất |
| PP-SWR-146 | Nếu VehicleConfig thiếu lúc khởi động, thì planner không được gửi Trajectory | Demonstration | Safety | nhóm tự thống nhất |

### 8.11 Chịu lỗi: tín hiệu xe và đồng hồ {#req-signal-faults}

| ID | Yêu cầu | Kiểm chứng | Type | Nguồn |
|---|---|---|---|---|
| PP-SWR-135 | Khi IMU có nhiễu tới hai lần mức datasheet, PP-SWR-051 và 100 đến 102 phải vẫn thoả | Test, vòng kín: F07 (a, b) | Safety | Bosch SMI230 datasheet |
| PP-SWR-136 | Khi yaw rate có bias tới 0,3 °/s, PP-SWR-051 và 100 đến 102 phải vẫn thoả | Test, vòng kín: F08 (a, b) | Safety | nhóm tự thống nhất |
| PP-SWR-137 | Khi đồng hồ trôi tới ±100 ppm hoặc mất đồng bộ gPTP tới 10 s, PP-SWR-051 và 100 đến 102 phải vẫn thoả | Test, vòng kín: F14 (a, b, c) | Safety | nhóm tự thống nhất |
| PP-SWR-138 | Khi yaw rate đã lọc trễ tới 50 ms mà planner không được báo phần trễ đó, PP-SWR-051 và 100 đến 102 phải vẫn thoả | Test, vòng kín: Q2 (0–50 ms) | Safety | nhóm tự thống nhất |
| PP-SWR-139 | Trong khi tín hiệu CAN bị làm tròn theo factor của DBC, PP-SWR-051 và 100 đến 102 phải vẫn thoả | Test, vòng kín: mọi kịch bản, F18 | Safety | nhóm tự thống nhất |

### 8.12 Interface với khối dọc {#req-longitudinal}

| ID | Yêu cầu | Kiểm chứng | Type | Nguồn |
|---|---|---|---|---|
| PP-SWR-150 | Planner phải gửi LateralLimits mỗi chu kỳ | Test: S14 | Interface | nhóm tự thống nhất |
| PP-SWR-151 | `LateralLimits.v_max` phải bằng √(giới hạn a_y của chức năng đang lái / κ_max), với κ_max là độ cong lớn nhất của tâm làn thật trong tầm nhìn của lane model, tối đa 126 m, sai lệch ≤ 5 % | Test: S14, Q4 | Interface | nhóm tự thống nhất |
| PP-SWR-152 | `LateralLimits.distance` phải bằng khoảng cách dọc tới điểm có κ_max, sai lệch ≤ 5 m | Test: S14 | Interface | nhóm tự thống nhất |
| PP-SWR-153 | Khi LongitudinalPlan hợp lệ, `longitudinal_velocity` và `acceleration` của Trajectory phải lấy theo LongitudinalPlan | Test: S14 | Interface | nhóm tự thống nhất |
| PP-SWR-154 | Nếu LongitudinalPlan mất hoặc quá timeout 75 ms, thì Trajectory phải dùng tốc độ hiện tại không đổi và gia tốc 0 | Test: S14 (d) | Interface | nhóm tự thống nhất |
| PP-SWR-155 | Nếu LongitudinalPlan mất hoặc quá timeout 75 ms, thì planner phải giữ `path_valid = true` | Test: S14 (d) | Safety | nhóm tự thống nhất |

## 9. Performance targets {#req-targets}

Không có ngưỡng đạt. Software Qualification Test Specification đo các chỉ số này để chọn bộ calibration và so sánh kỹ thuật, theo thứ tự ưu tiên: an toàn, quy định, cảm nhận người lái, thời gian tính.

| ID | Yêu cầu | Kiểm chứng | Type | Nguồn |
|---|---|---|---|---|
| PP-SWR-050 | Lệch ngang của path nên nhỏ, trong toàn bộ ODD và khi lane model có lỗi | Test: S1 (a, b, d, e), S6b, S11, S19, F03, F04, F21, F22, Q4 | Performance | đề bài |
| PP-SWR-002 | a_y thêm vào lớn nhất khi HWA đưa xe về giữa hoặc dời tâm nên nhỏ | Test: S2, S3 | Performance | nhóm tự thống nhất |
| PP-SWR-004 | Jerk ngang của path khi HWA đang lái nên nhỏ | Test: S1 | Performance | nhóm tự thống nhất |
| PP-SWR-008 | Thời gian từ lúc a_y cần lớn nhất < aysmax tới lúc `lateral_limit_reached` tắt nên ngắn | Test: S1 (a, b, d, e) | Performance | nhóm tự thống nhất |
| PP-SWR-013 | Phần lệch ngang tăng thêm so với ca trễ 0, khi trễ camera 0–200 ms kèm jitter ±20 ms, nên nhỏ | Test: Q1 | Performance | nhóm tự thống nhất |
| PP-SWR-016 | Phân vị 99 % của thời gian tính mỗi chu kỳ nên nhỏ | Test: mọi kịch bản | Performance | nhóm tự thống nhất |
| PP-SWR-064 | Thời gian từ lúc `lateral_limit_reached` bật tới lúc a_y cần tại vị trí xe vượt aysmax nên dài | Test: S1b | Performance | nhóm tự thống nhất |
| PP-SWR-053 | Thời gian từ lúc HWA bắt đầu lái (xe lệch tâm tới 0,5 m) tới lúc lệch ngang ≤ 0,1 m nên ngắn | Test: S2 | Performance | nhóm tự thống nhất |
| PP-SWR-057 | Khoảng cách ngang nhỏ nhất từ thân xe tới vật ở hai bên trong lúc dời tâm nên lớn | Test: S3, S3b, S15 | Performance | nhóm tự thống nhất |
| PP-SWR-059 | Thời gian từ lúc đuôi xe lớn qua tới lúc lệch ngang ≤ 0,1 m nên ngắn | Test: S3 | Performance | nhóm tự thống nhất |
| PP-SWR-081 | Thời gian từ lúc LKA bắt đầu path can thiệp tới COMPLETED nên ngắn | Test: S4 | Performance | nhóm tự thống nhất |
| PP-SWR-082 | Thời gian từ lúc ELK bắt đầu path can thiệp tới COMPLETED nên ngắn | Test: S5, S6, S7, S8, S8b (d, e) | Performance | nhóm tự thống nhất |
| PP-SWR-087 | DTLE nhỏ nhất của LKA nên lớn | Test, vòng kín: S4 | Performance | nhóm tự thống nhất |
| PP-SWR-125 | Khi lane model có c2 sai, tỉ lệ giữa lệch ngang của path trên đoạn 2–3 s và lệch của một path bám đúng lane model sai đó nên nhỏ | Test: F06 | Performance | đề bài |

## Revision history {#revision-history}

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 2026-11-10 | Refactor thành Software Requirements Specification, baseline BL1. Tách requirement, performance target và giới hạn calibration parameter; thêm ODD (bề rộng làn 2,5–5,5 m, bề rộng xe ≤ 2,5 m kể cả gương), cột Loại kèm safety goal; chốt toàn bộ việc mở cũ của tài liệu (thêm PP-SWR-041 đến 047, 063; thêm PP-ASM-017, 018); bỏ nhãn trạng thái và mục việc mở |
| 1.1 | 2026-11-10 | Thêm PP-ASM-019: nền tảng đích chưa biết, planner chỉ cần trình biên dịch C11 |
| 1.2 | 2026-11-11 | PP-SWR-006 chỉ xét đoạn 0–1 s của path. Lý do: ở tầm xa, đa thức bậc 3 của lane model đọc thấp độ cong của clothoid ngắn (6–11 % ở 72 m), nên không planner nào đảm bảo được; xe chỉ chạy theo phần gần, phần xa được lập lại mỗi chu kỳ |
| 1.3 | 2026-11-11 | PP-SWR-007 lấy mốc của R79: cờ phải đang bật khi lốp trước bắt đầu đè vạch. Lý do: câu cũ đo bằng chính calibration parameter `T_flag`, tăng `T_flag` là đạt. PP-SWR-008 chuyển thành performance target; thêm target PP-SWR-064 (thời gian báo trước); bỏ `delta_ay`, `T_flag` khỏi mục 7; ghi lại nguồn của PP-SWR-006 và `epsilon_ay` |
| 1.4 | 2026-11-11 | PP-SWR-051 chỉ áp dụng khi khoảng trống mỗi bên ≥ `free_space_min`. Lý do: ODD cho làn 2,5 m với xe rộng 2,5 m (PP-SWR-062), khi đó không xe nào giữ được DLC ≥ 0; hành vi đúng là báo `lane_too_narrow` (PP-SWR-063) để HWA không khả dụng. Các requirement dựa vào PP-SWR-051 (122, 123, 135 đến 139, 148) kế thừa điều kiện này |
| 1.5 | 2026-11-11 | PP-SWR-055, 056 viết lại theo khoảng hở tới xe lớn và `gap_truck_min`; thêm định nghĩa Ngang hàng, Khoảng hở tới xe lớn; thêm `gap_truck_min` vào mục 7. Lý do: câu cũ so khoảng hở tới xe lớn với khoảng hở tới biên làn, nên xe lớn ở giữa làn bên thì không dời hoặc dời về phía xe lớn |
| 1.6 | 2026-11-12 | PP-SWR-032, 041 tách pha LKA và ELK. PP-SWR-036, 037 chọn lại theo 030 khi hủy. PP-SWR-047 phân biệt biên trực tiếp và biên ngoài làn. Mục 4 dùng trị tuyệt đối của a_y thêm vào khi kết thúc. Làm rõ nguồn 080, 083, 088, 114 |
| 1.7 | 2026-11-12 | Tầm nhìn của lane model: thêm PP-SWR-017 (nhận mọi tầm nhìn), 149 (chịu lỗi tầm nhìn, F22), PP-ASM-020, định nghĩa Tầm nhìn của lane model; PP-SWR-151 giới hạn 126 m; PP-SWR-050, 151 thêm quét Q4. Lý do: planner phải chạy đúng với mọi tầm nhìn, không chỉ 80 m |
| 1.8 | 2026-11-12 | PP-SWR-042, 149 thêm F22 (f): tầm nhìn tụt lâu, HWA trả lái rồi trở lại |
| 1.9 | 2026-11-12 | PP-SWR-100 đến 102 chỉ xét phần path trong tầm nhìn lane model báo (định nghĩa Hai path liên tiếp); thêm PP-SWR-018 (`observed_horizon_s`), PP-ASM-021. Lý do: phần ngoài tầm nhìn là ngoại suy, giữ nó liên tục làm path không theo được làn khi tầm nhìn ngắn (PP-PR-021, PP-TS-014). Ảnh hưởng: mọi requirement dựa vào PP-SWR-100 đến 102 (031, 061, 120 đến 128, 135 đến 139, 148, 149), Interface Control Document 6.1, Software Detailed Design T4, Software Qualification Test Specification 8.1 |
| 1.10 | 2026-11-12 | PP-SWR-018 chỉ chặn phía trên. Lý do: khi bám reference line cũ (c0 jump, F02) planner báo phần quan sát ngắn hơn tầm nhìn lane model báo; báo ngắn là phía an toàn và bên chấm không biết lúc nào planner bám reference line cũ. Đổi sau lần chạy 20261112-1240-matrix-M1-1bfd184 |

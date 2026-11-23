# Software Requirements Specification

| Mục | Nội dung |
|---|---|
| Mã tài liệu | `PP-SRS` |
| Phiên bản | 1.28 |
| Trạng thái | BL1 |
| Tác giả | thongbui |
| Người review | thongbui |
| Cập nhật | 2026-11-23 |

## 1. Purpose and scope {#req-scope}

- **Mục đích:** Quy định hai path planner phải đạt gì, nhìn từ bên ngoài: qua input, output và chuyển động thật của xe trong simulator.
- **Phạm vi:** Hai planner cho ba chức năng lateral L2/L2+: LCC planner cho LCC (HWA), LKA/ELK planner cho LKA và ELK. Mỗi planner là một khối riêng và phải chạy đúng khi khối kia không chạy.
- **Ngoài phạm vi:** Arbitrator chọn path giữa hai planner (thuộc công ty), lane model, perception, khối Chức năng ADAS (quyết định khi nào can thiệp), Lateral Controller, EPS, khối dọc. Lực ghi đè ≤ 50 N (R79) thuộc Lateral Controller và EPS.
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
| 001–009 | Giới hạn a_y của LCC |
| 010–029 | Output và chu kỳ |
| 030–049 | Chọn can thiệp (LKA/ELK planner) |
| 050–079 | LCC |
| 080–099 | LKA, ELK |
| 100–119 | Giới hạn, liên tục, khả thi |
| 120–149 | Chịu lỗi |
| 150–169 | Interface với khối dọc |
| 170–189 | LCC bám xe trước, ghép với arbitrator |

## 4. Definitions {#req-definitions}

| Đại lượng | Định nghĩa |
|---|---|
| Chu kỳ | 25 ms (40 Hz) |
| Chức năng đang lái | `active_function` trong InterventionStatus (NONE, LKA, ELK). "LCC đang lái" nghĩa là `lcc_mode` trong LccStatus khác NONE |
| Arbitrator | Khối của công ty chọn path của một trong hai planner gửi cho Lateral Controller. Ngoài phạm vi (PP-ASM-022) |
| `lcc_mode` | Chế độ của LCC planner: NONE (LCC không ở REQUEST hoặc path không hợp lệ), LANE (bám tâm làn từ vạch làn mình), INFERRED (bám tâm làn suy ra), FOLLOW (bám xe trước), COAST (bám path cũ vì mất mọi biên) |
| Làn thật | Làn xe đang ở, theo ground truth của simulator. Với làn hỗn hợp ô tô và xe máy, là phần dành cho ô tô |
| Lệch ngang của path | Khoảng cách ngang lớn nhất giữa path và tâm làn thật, đo tại cùng vị trí dọc, trên đoạn 0–1 s của path, trừ khi requirement nêu đoạn khác |
| a_y của path | v²·κ tại từng điểm của Trajectory, với v = `longitudinal_velocity`, κ = `curvature` |
| a_y cần | v²·κ của tâm làn thật tại điểm tương ứng trên path |
| Tầm nhìn của lane model | Đoạn camera thật sự quan sát được trên cả hai biên làn đang dùng, trong mô hình cảm biến của simulator. Không tính phần lane model báo dài hơn đoạn đã quan sát |
| a_y cần lớn nhất | Giá trị lớn nhất của a_y cần trên đoạn 0–3 s, chỉ xét phần trong tầm nhìn của lane model |
| a_y thêm vào | a_y của path trừ a_y cần, tại cùng một điểm |
| Jerk ngang của path | Đạo hàm theo thời gian của a_y của path, trung bình trượt 0,5 s |
| Hai path liên tiếp | Của cùng một planner, cả hai có `Trajectory.header.valid = true`. So trên đoạn thời gian cả hai cùng mô tả, chỉ ở các điểm của path mới nằm trong tầm nhìn mà lane model báo cho frame planner dùng ở chu kỳ đó; chu kỳ không có lane model thì cả path. Path cũ đưa về base_link của path mới bằng chuyển động thật của xe. Không tính cặp path của LCC planner mà path mới thuộc chu kỳ có `driver_override = true` hoặc có LKA hoặc ELK ở REQUEST: khi đó path đi theo xe (PP-SWR-039) |
| Biên làn đủ tin | Vạch L1, R1: status MEASURED, confidence ≥ `conf_ego`. Vạch L2, R2 hoặc mép đường, khi dùng để suy ra tâm làn: status MEASURED, confidence ≥ `conf_inferred` |
| DLC | Như ADAS Function Specification, mục 5, tính trên làn thật và vị trí thật của xe |
| DTLE | Khoảng cách từ mép ngoài lốp tới mép trong của vạch, nhỏ nhất trong một lần can thiệp; âm là đã vượt vạch (Euro NCAP) |
| Khoảng trống mỗi bên | (bề rộng làn thật − bề rộng xe kể cả gương) / 2 |
| Xe lớn | Vật thể ở làn bên kề, bề rộng ≥ 2,3 m |
| Ngang hàng | Phần dọc của xe kia chồng lên thân xe |
| Khoảng hở tới xe lớn | Khoảng cách ngang từ thân xe (kể cả gương), khi xe ở tâm làn thật, tới mép gần nhất của xe lớn |
| Điều kiện kết thúc | DLC ≥ 0 ở cả hai phía, lệch tâm ≤ `d_end`, trị tuyệt đối của v_lat ≤ `v_lat_end`, trị tuyệt đối của góc lệch so với hướng làn ≤ `heading_end`, trị tuyệt đối của a_y thêm vào ≤ `ay_add_end` |
| Lệch tâm | Khoảng cách ngang từ tâm trục sau (gốc `base_link`) tới tâm làn, đo trên làn thật và vị trí thật của xe |
| Tâm làn gốc | Reference line cuối cùng có hai vạch L1, R1 đủ tin, dời theo chuyển động thật của xe; phần ngoài đoạn đã quan sát được ngoại suy theo độ cong cuối |
| Xe trước | Vật thể có `LeadTarget.id` bằng `LongitudinalPlan.target_id` |
| Xe sắp ngang hàng | Vật thể ở làn bên kề mà phần dọc đã ngang hàng, hoặc sẽ ngang hàng trong `ttc_offset_start` |

## 5. Operating conditions (ODD) {#req-odd}

| Điều kiện | Giá trị | Nguồn |
|---|---|---|
| Chức năng | LCC (HWA), LKA, ELK. Dải tốc độ và điều kiện kích hoạt ở ADAS Function Specification | — |
| Mất vạch làn mình | LCC bám xe trước khi mất cả hai vạch: xe trước là xe tải hoặc xe con cách 2–50 m, tốc độ xe mình dưới 60 km/h, tối đa 30 m (mục 8.13) | mentor |
| Đường | Có vạch hoặc mép đường. Bề rộng làn 2,5–5,5 m, kể cả làn hỗn hợp ô tô và xe máy 4,5 m | mentor (PP-ASM-015) |
| Xe | Mọi xe gia đình rộng ≤ 2,5 m kể cả gương. Thông số xe đọc từ VehicleConfig | QCVN 09:2015/BGTVT 2.1.1.1 b (PP-ASM-016) |
| Calibration | Một bộ calibration cho mọi xe | nhóm tự thống nhất |
| Tần số | 40 Hz | mentor |

**Giới hạn quan sát khi vào cua.** Nếu tốc độ khi phát hiện cua đòi hỏi giảm tốc từ trước tầm nhìn của camera, planner vẫn áp PP-SWR-005 đến 007 và xuất giới hạn cho bộ điều khiển dọc. Trong ca S14(a) tại 130 km/h, để vào cua R = 200 m với a_y ≤ 2,5 m/s² cần giảm còn khoảng 80,5 km/h. Với giảm tốc đều 2–3 m/s², cần khoảng 134–201 m, trong khi tầm nhìn danh định là 80 m. PP-SWR-051 vẫn áp ở các chu kỳ đủ điều kiện của requirement (PP-PR-007, phương án B).

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
| PP-ASM-007 | Trễ truyền Trajectory và status của planner (LccStatus, InterventionStatus) khoảng 1 ms | Software Architectural Design mục 3.3 | Đo trên bus | nhóm tự thống nhất |
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
| PP-ASM-021 | Lateral Controller kiểu pure pursuit, nhìn trước tối đa 0,6 s, và không dùng phần path sau `observed_horizon_s` để tính lệnh lái | PP-SWR-018, 100, 101, 102 | Thống nhất với đội Lateral Controller; controller kiểu MPC dùng cả path thì giả định này không đúng | nhóm tự thống nhất, theo Autoware pure pursuit (khoảng nhìn trước tối đa 15 m, khoảng 0,6 s ở 90 km/h) |
| PP-ASM-020 | Tầm nhìn của lane model thay đổi theo từng vạch và từng frame; điểm đầu, điểm cuối thật chưa biết. Benchmark dùng 0–80 m danh định, quét điểm cuối 10–126 m | PP-SWR-017, 149, 151 | Đọc phân bố `line start distance`, `line end distance` trong log xe thật | nhóm tự thống nhất |
| PP-ASM-022 | Arbitrator của công ty chọn path của LKA/ELK planner khi `InterventionStatus.active_function` khác NONE và `Trajectory.header.valid = true`; ngược lại chọn path của LCC planner. Planner không biết path nào được chọn | PP-SWR-039, 040, 180 | Thống nhất quy tắc chọn và trễ chuyển với đội arbitrator | mentor (arbitrator thuộc công ty); quy tắc chọn: nhóm tự thống nhất |
| PP-ASM-023 | Phát hiện lệch làn và gửi yêu cầu LKA, ELK do khối Chức năng ADAS làm theo ADAS Function Specification, không do planner | PP-SWR-030, 031, 047 | Hỏi mentor khối phát hiện lệch làn của công ty | mentor ("planner chỉ bật khi detect thấy lệch làn"); cách chia: nhóm tự thống nhất |
| PP-ASM-024 | LeadTarget do perception gửi, gồm loại xe, vị trí tâm, khoảng cách bumper, heading và vận tốc tương đối của xe trước; 20 Hz, trễ như ObjectList (PP-ASM-002) | PP-SWR-170 đến 177 | Thống nhất message và loại xe với đội perception | mentor (nội dung); tần số, trễ: nhóm tự thống nhất |
| PP-ASM-025 | Điều kiện V3, V4 của bám xe đo theo tâm làn gốc, không theo trục `base_link`: trong cua R = 150 m, xe trước cách 30 m đã lệch y = 3,0 m trong `base_link` | PP-SWR-170, 171 | Hỏi mentor cách đo hai điều kiện này | nhóm tự thống nhất |
| PP-ASM-026 | Ngưỡng 0,8 m của điều kiện M1 còn bị chặn theo khoảng trống mỗi bên trừ `dlc_offset_min`, để path bám xe không đưa xe qua vạch ở làn hẹp | PP-SWR-172 | Hỏi mentor | nhóm tự thống nhất |
| PP-ASM-027 | Khi mất hai vạch làn mình mà còn biên làn bên hoặc mép đường đủ tin, LCC planner dùng tâm làn suy ra (PP-ADR-011) và không bám xe | PP-SWR-147, 148, 170 | Hỏi mentor thứ tự ưu tiên | nhóm tự thống nhất |
| PP-ASM-028 | Ngưỡng cắt 10 cm và 0,15 m/s của mentor áp cho cả LKA và ELK | PP-SWR-032, 084, 090 | Hỏi mentor | nhóm tự thống nhất |
| PP-ASM-029 | Khi path LCC ở trần a_y, Lateral Controller giữ a_y đo trên xe vượt a_y của path không quá 0,3 m/s² − `ay_margin_hwa`, để a_y của xe vẫn trong R79 5.6.2.1.1 | PP-SWR-001, 051; SG-01 | PP-TS-027 trong SIL: a_y của xe lọc theo R79 Annex 8, 2.4 khi path ở trần | R79 5.6.2.1.1; nhóm tự thống nhất (PP-TS-020) |

## 7. Calibration parameter limits {#req-calibration-limits}

Chỉ liệt kê tham số mà requirement trỏ tới. Danh mục đầy đủ, giá trị khởi đầu và dải quét ở tài liệu Software Architectural Design.

| Tham số | Ý nghĩa | Giới hạn | Nguồn của giới hạn |
|---|---|---|---|
| `conf_ego` | Độ tin tối thiểu của vạch L1, R1 | 0–1 | — |
| `conf_edge` | Độ tin tối thiểu của mép đường ELK đo trực tiếp | 0–1 | PP-SWR-047 |
| `conf_inferred` | Độ tin tối thiểu của biên dùng để suy ra tâm làn | > `conf_ego` | Biên suy ra cộng thêm sai số của khoảng cách nhớ được |
| `T_coast` | Thời gian bám path cũ khi không còn biên làn đủ tin | 0–1 s | Analysis: lệch dead reckoning 0,06 m sau 1 s (Software Architectural Design Appendix A.4) |
| `free_space_min` | Khoảng trống tối thiểu mỗi bên để LCC khả dụng | ≥ 0 m | PP-SWR-051 |
| `epsilon_ay` | Mức a_y của path được thấp hơn aysmax khi a_y cần vượt aysmax | 0–2,5 m/s² | — |
| `ay_margin_hwa` | Phần a_y của path LCC được vượt aysmax | 0–0,3 m/s² | R79 5.6.2.1.1 (PP-SWR-001); phần còn lại dành cho controller (PP-ASM-029) |
| `gap_truck_min` | Khoảng hở tới xe lớn mà dưới mức đó LCC dời tâm | > 0 m | — |
| `d_end` | Ngưỡng lệch tâm của điều kiện kết thúc | 0–0,10 m | mentor (cắt khi cách tâm làn dưới 10 cm) |
| `v_lat_end` | Ngưỡng v_lat của điều kiện kết thúc | 0–0,15 m/s | mentor (cắt khi v_lat dưới 0,15 m/s) |
| `heading_end`, `ay_add_end` | Ngưỡng góc lệch và a_y thêm vào của điều kiện kết thúc | ≥ 0 | — |
| `offset_truck` | Độ dời tâm khi tránh một xe lớn | 0–0,10 m | mentor (10 cm) |
| `follow_lat_max` | Lệch ngang lớn nhất giữa xe mình và xe trước để vào bám xe | > 0 m | mentor (tunable) |
| `follow_vlat_max` | Tốc độ ngang lớn nhất của xe trước để vào bám xe | > 0 m/s | mentor (tunable) |
| `T_end_hold` | Thời gian điều kiện kết thúc phải giữ liên tục trước khi báo COMPLETED | ≥ 0 s | — |
| `T_end_margin` | Thời gian planner giữ thêm vì điều kiện được tính trên ước lượng | 0–0,4 s, tức nhỏ hơn 0,5 s của PP-SWR-032 | nhóm tự thống nhất |
| `T_return`, `T_return_object` | Thời lượng đưa xe về tâm làn sau khi đã chặn đà trôi; bản thứ hai cho ELK vì xe làn bên | > 0 s | nhóm tự thống nhất (PP-TS-026) |

## 8. Requirements {#req-requirements}

### 8.1 Output và chu kỳ {#req-output}

| ID | Yêu cầu | Kiểm chứng | Type | Nguồn |
|---|---|---|---|---|
| PP-SWR-010 | Mỗi planner phải gửi Trajectory và status của mình mỗi chu kỳ: LccStatus và LateralLimits với LCC planner, InterventionStatus với LKA/ELK planner | Test: mọi kịch bản | Interface | mentor |
| PP-SWR-011 | Trajectory phải theo định dạng ở Interface Control Document: 31 điểm, bước 0,1 s, phủ 0–3 s, frame_id = base_link | Inspection | Interface | nhóm tự thống nhất (Autoware Trajectory) |
| PP-SWR-012 | `header.stamp_us` của Trajectory phải là thời điểm mà path mô tả, đã bù trễ của lane model | Inspection; Test: Q1 | Interface | nhóm tự thống nhất |
| PP-SWR-014 | `header.counter` phải tăng 1 sau mỗi message, quay vòng 0–255 | Inspection; Test: mọi kịch bản | Interface | nhóm tự thống nhất |
| PP-SWR-018 | `Trajectory.observed_horizon_s` không được lớn hơn thời điểm trên path mà path ra khỏi tầm nhìn lane model báo cho frame planner dùng ở chu kỳ đó quá 0,1 s | Test: mọi kịch bản | Interface | nhóm tự thống nhất |
| PP-SWR-017 | Planner phải nhận lane model với mọi `view_range_end > view_range_start` của từng vạch và mép đường. Phần tầm nhìn vượt 126 m không được làm input bị coi là không hợp lệ | Test: F22 (e), Q4 | Interface | nhóm tự thống nhất |
| PP-SWR-015 | Planner phải ghi thời gian tính của từng chu kỳ | Inspection | Interface | nhóm tự thống nhất |
| PP-SWR-019 | `Trajectory.planner_id` phải là planner đã gửi message đó | Inspection | Interface | nhóm tự thống nhất |

### 8.2 Chọn can thiệp và nối path {#req-arbitration}

PP-SWR-030 đến 038, 041, 045 đến 047, 049 áp cho LKA/ELK planner. PP-SWR-039, 040, 042 áp cho LCC planner. PP-SWR-043, 044, 048 áp cho cả hai. Việc chọn path giữa hai planner thuộc arbitrator của công ty (PP-ASM-022).

| ID | Yêu cầu | Kiểm chứng | Type | Nguồn |
|---|---|---|---|---|
| PP-SWR-030 | LKA/ELK planner phải chọn chức năng đang lái theo thứ tự ELK > LKA, chỉ xét chức năng có state = REQUEST | Test: S9 (a) | Safety, SG-01 | nhóm tự thống nhất |
| PP-SWR-031 | Khi chức năng đang lái của LKA/ELK planner đổi, path phải thoả PP-SWR-100 đến 102, trừ chu kỳ đầu của mỗi lần LKA hoặc ELK bắt đầu; ở chu kỳ đó áp PP-SWR-080 và 049 | Test: S9, S8c (d) | Safety, SG-04 | đề bài; phạm vi ngoại lệ: nhóm tự thống nhất (PP-PR-062) |
| PP-SWR-032 | Khi điều kiện kết thúc của LKA hoặc ELK đã giữ liên tục `T_end_hold`, planner phải đặt pha của chức năng đó thành COMPLETED trong tối đa 0,5 s | Test: S4, S5, S20 | Functional | mentor (ngưỡng cắt 10 cm và 0,15 m/s, PP-ASM-028); nhóm tự thống nhất (PP-TS-018); can thiệp vẫn dưới mốc 10 s của UN R79 5.1.6.1.2.1 |
| PP-SWR-033 | Sau COMPLETED, planner phải chọn chức năng đang lái theo PP-SWR-030 trong các chức năng còn ở REQUEST, không tính chức năng vừa COMPLETED; không còn chức năng nào thì chọn NONE | Test: S9 (b) | Functional | nhóm tự thống nhất |
| PP-SWR-034 | Nếu chức năng vừa COMPLETED vẫn giữ REQUEST, thì planner không được bắt đầu lần can thiệp mới cho chức năng đó cho tới khi state rời REQUEST rồi quay lại | Test: S16 (a, b) | Functional | nhóm tự thống nhất |
| PP-SWR-035 | Mỗi lần can thiệp mới của LKA hoặc ELK phải có cùng giới hạn như lần đầu, không phụ thuộc số lần đã can thiệp | Test: S16 (c, d, e) | Functional | nhóm tự thống nhất |
| PP-SWR-036 | Khi chức năng đang can thiệp rời REQUEST giữa chừng, planner phải chuyển từ trạng thái hiện tại sang chức năng được chọn theo PP-SWR-030 trong các chức năng còn ở REQUEST | Test: S9 (d), S8c (d) | Functional | nhóm tự thống nhất |
| PP-SWR-037 | Khi chức năng đang can thiệp rời REQUEST giữa chừng qua một message hợp lệ và không còn chức năng đủ điều kiện, planner phải báo `active_function = NONE` với `path_valid = true` nếu các input bắt buộc còn hợp lệ | Test: S9 (d), S8c (d) | Safety, SG-02 | nhóm tự thống nhất |
| PP-SWR-038 | Planner phải phản ánh thay đổi của FunctionRequests vào output trong không quá một chu kỳ kể từ lúc nhận message | Test: S9, Q3 | Functional | nhóm tự thống nhất |
| PP-SWR-039 | Trong khi `driver_override = true`, hoặc LKA hoặc ELK ở REQUEST, điểm đầu của path LCC phải trùng vị trí ngang hiện tại của xe, lệch ≤ 0,05 m | Test: S9 (a, c), S17 | Safety, SG-04, SG-05 | nhóm tự thống nhất; vế LKA, ELK: arbitrator có thể chọn path LCC bất kỳ lúc nào (PP-ASM-022) |
| PP-SWR-040 | Khi `driver_override` chuyển về false, hoặc LKA và ELK cùng rời REQUEST, trong lúc LCC ở REQUEST, điểm đầu của path LCC phải trùng vị trí ngang của xe lúc đó, lệch ≤ 0,05 m | Test: S9 (a, c), S17 | Safety, SG-04, SG-05 | nhóm tự thống nhất |
| PP-SWR-041 | Planner phải giữ pha của mỗi chức năng ở COMPLETED tới khi state của chức năng đó rời REQUEST | Test: S16 (a, b) | Functional | nhóm tự thống nhất |
| PP-SWR-042 | Khi LCC rời REQUEST, LCC planner phải đặt `lcc_mode = NONE` và giữ `path_valid = true` | Test: S9 (e), F22 (f) | Safety, SG-02 | nhóm tự thống nhất |
| PP-SWR-043 | Trong khi `path_valid = false`, `lcc_mode` của LCC planner và `active_function` của LKA/ELK planner phải bằng NONE | Test: F05, F12 (Lane Model), F20 | Functional | nhóm tự thống nhất |
| PP-SWR-044 | Khi input hồi phục sau lúc `path_valid = false`, điểm đầu của path mới phải khớp trạng thái ngang thật của xe theo dung sai của PP-SWR-080 | Test: F12 (Lane Model, hồi phục) | Functional | nhóm tự thống nhất |
| PP-SWR-045 | Sau khi input hồi phục, planner chỉ được bắt đầu can thiệp LKA hoặc ELK khi state của chức năng đó rời REQUEST rồi quay lại | Test: F12 (Lane Model, hồi phục) | Safety, SG-01 | nhóm tự thống nhất |
| PP-SWR-046 | Nếu VehicleStateEstimate không hợp lệ trong lúc LKA hoặc ELK đang can thiệp, thì planner phải tiếp tục path can thiệp đó tới khi kết thúc | Test: F12 (v_y, trong S5) | Safety, SG-03 | nhóm tự thống nhất |
| PP-SWR-047 | Trong khi tâm làn chỉ suy được từ biên ngoài làn đang chạy, planner không được chọn LKA hoặc ELK. Ngoại lệ cho ELK mép đường khi biên nguy hiểm của làn đang chạy là mép MEASURED với confidence ≥ `conf_edge` và có biên đối diện đủ tin hoặc bề rộng làn đã nhớ | Test: F21 | Safety, SG-01 | mentor, nhóm làm rõ phạm vi ELK mép đường theo PP-TS-007 |
| PP-SWR-048 | Nếu FunctionRequests có tuổi (t0 trừ `header.stamp_us`) vượt 45 ms, thì planner phải xử lý như chưa nhận được message đó, kể cả cho thời gian timeout của PP-SWR-145 | Test: Q3 | Safety | Interface Control Document 4 (tuổi tối đa 45 ms) |
| PP-SWR-049 | Ở chu kỳ đầu của mỗi lần LKA hoặc ELK bắt đầu, độ cong tại điểm đầu của path phải lệch độ cong thật của xe (yaw rate chia tốc độ) không quá 0,0003 1/m | Test: S4, S4b, S5, S6, S7, S8, S9, S16 | Safety, SG-04 | đề bài (chuyển chức năng không tạo bước nhảy ở lệnh lái); ngưỡng bằng đoạn 0–1 s của PP-SWR-102, nhóm tự thống nhất |

### 8.3 LCC: giới hạn a_y {#req-hwa-lateral-limit}

| ID | Yêu cầu | Kiểm chứng | Type | Nguồn |
|---|---|---|---|---|
| PP-SWR-001 | Trong khi LCC đang lái, a_y của path phải ≤ aysmax + 0,3 m/s² tại mọi điểm, với aysmax = 2,5 m/s² | Test: S1, S1b, S12 (a) | Regulatory, SG-01 | R79 5.6.2.1.1 (+0,3 m/s²), 5.6.2.1.3 (≤ 3 m/s²); PP-TS-020 |
| PP-SWR-003 | Trong khi LCC đang lái, jerk ngang của path phải ≤ 5 m/s³ | Test: S1 | Regulatory, SG-01 | R79 5.6.2.1.3 c |
| PP-SWR-005 | Nếu a_y cần lớn nhất > aysmax trong khi LCC đang lái, thì LCC planner phải giữ `path_valid = true` và `lcc_mode` khác NONE | Test: S1b | Regulatory, SG-02 | R79 5.6.2.2.3 |
| PP-SWR-006 | Nếu a_y cần > aysmax tại một điểm trên đoạn 0–1 s của path trong khi LCC đang lái, thì a_y của path tại điểm đó phải ≥ aysmax − `epsilon_ay` | Test: S1b | Regulatory, SG-02 | R79 5.6.2.2.3 (hỗ trợ trong khả năng); mức `epsilon_ay`: nhóm tự thống nhất |
| PP-SWR-007 | Khi một lốp trước bắt đầu đè vạch trong lúc LCC đang lái và a_y cần lớn nhất > aysmax, `lateral_limit_reached` phải đang là true | Test, vòng kín: S1b | Regulatory, SG-01 | R79 5.6.2.2.3; Annex 8, 3.2.5.2 |
| PP-SWR-009 | LCC planner phải gửi cùng một giá trị `lateral_limit_reached` trong LccStatus và LateralLimits của cùng chu kỳ | Inspection; Test: S14 | Interface | nhóm tự thống nhất |

### 8.4 LCC: giữ làn và dời tâm {#req-hwa-centering}

| ID | Yêu cầu | Kiểm chứng | Type | Nguồn |
|---|---|---|---|---|
| PP-SWR-051 | Trong khi LCC đang lái, a_y cần lớn nhất ≤ aysmax và khoảng trống mỗi bên ≥ `free_space_min`, DLC ở cả hai phía phải ≥ 0 | Test, vòng kín: S1 | Regulatory, SG-01 | R79 5.6.2.1.1 |
| PP-SWR-052 | Khi LCC bắt đầu lái lúc xe lệch tâm làn tới 0,5 m, `lcc_mode` phải khác NONE trong suốt đoạn đưa về giữa | Test: S2 | Functional | nhóm tự thống nhất |
| PP-SWR-054 | Trong khi LCC ở REQUEST và tốc độ xe trong khoảng 0–60 km/h, planner phải tiếp tục gửi path hợp lệ cho LCC | Test: S11 | Functional | nhóm tự thống nhất |
| PP-SWR-055 | Trong khi đúng một xe lớn ngang hàng ở làn bên kề có khoảng hở tới xe lớn < `gap_truck_min`, và làn bên kia không có xe nào ngang hàng hoặc sắp ngang hàng, path phải lệch khỏi tâm làn thật về phía xa xe lớn | Test: S3 | Functional | đề bài; điều kiện làn bên kia: mentor |
| PP-SWR-056 | Trong khi có xe lớn ngang hàng với khoảng hở tới xe lớn < `gap_truck_min`, path không được lệch khỏi tâm làn thật về phía xe lớn có khoảng hở nhỏ nhất | Test: S3, S3b, S15 | Safety, SG-01 | mentor |
| PP-SWR-058 | Khi xe lớn ở làn bên kề đang tới gần, path phải bắt đầu dời trước lúc xe lớn tới ngang hàng | Test: S3 | Functional | đề bài |
| PP-SWR-065 | Trong khi một xe lớn ngang hàng ở một làn bên kề và có xe không phải xe lớn ngang hàng hoặc sắp ngang hàng ở làn bên kia, lệch ngang của path so với tâm làn thật phải ≤ 0,02 m | Test: S3b (b), S15 (c) | Functional | mentor (chỉ dời khi làn bên kia không có xe tới); dung sai: nhóm tự thống nhất |
| PP-SWR-066 | Khi path dời khỏi tâm làn thật vì đúng một xe lớn (PP-SWR-055), lệch ngang lớn nhất của path so với tâm làn thật phải ≤ 0,12 m | Test: S3 (a, b, c) | Functional | mentor (10 cm); dung sai 0,02 m: nhóm tự thống nhất |
| PP-SWR-067 | Khi LCC ở REQUEST, `path_valid = true` và không có điều kiện nào của PP-SWR-124, 142 đến 145, LCC planner phải đặt `lcc_mode` khác NONE | Test: S1, S2, S11 | Safety, SG-02 | nhóm tự thống nhất (trước đây nằm trong PP-SWR-030) |

### 8.5 LCC: làn thay đổi và ODD {#req-hwa-lane-change}

| ID | Yêu cầu | Kiểm chứng | Type | Nguồn |
|---|---|---|---|---|
| PP-SWR-060 | Khi một biên làn mở rộng (làn dừng khẩn cấp, tách nhánh, thêm làn), DLC so với biên làn thật ở phía mở rộng phải ≥ 0 | Test, vòng kín: S6b | Safety, SG-01 | mentor |
| PP-SWR-061 | Khi lane model chuyển sang làn mới, path phải thoả PP-SWR-100 đến 102 | Test: S17 | Safety, SG-04 | nhóm tự thống nhất |
| PP-SWR-062 | Mọi requirement ở mục 8 phải thoả trong toàn bộ ODD ở mục 5, với cùng một bộ calibration | Test: S19 | Functional | nhóm tự thống nhất |
| PP-SWR-063 | Khi khoảng trống mỗi bên nhỏ hơn `free_space_min`, LCC planner phải đặt `lane_too_narrow = true` trong LccStatus | Test: S19 (b, f) | Safety, SG-01 | nhóm tự thống nhất |

### 8.6 LKA và ELK {#req-intervention}

| ID | Yêu cầu | Kiểm chứng | Type | Nguồn |
|---|---|---|---|---|
| PP-SWR-080 | Khi LKA hoặc ELK bắt đầu can thiệp, điểm đầu của path phải khớp trạng thái ngang thật của xe: lệch vị trí ≤ 0,1 m, lệch v_lat ≤ 0,1 m/s | Test: S4, S5, S6 | Functional | đề bài, dung sai do nhóm tự thống nhất |
| PP-SWR-083 | obsolete (1.14, PP-TS-016): R79 5.1.6.1.2.1 và EU 2021/646 Annex I 3.6.4.1.1 cho phép can thiệp dài hơn 10 s, chỉ đòi cảnh báo âm thanh | — | Safety, SG-01 | R79 5.1.6.1.2.1, Annex 8 3.1.1.1; EU 2021/646 Annex I 3.6.4.1.1 |
| PP-SWR-084 | Khi LKA hoặc ELK báo COMPLETED, DLC ở cả hai phía phải ≥ 0 và lệch tâm phải ≤ 2·`d_end` | Test, vòng kín: S4, S5, S6, S20, F24 | Functional | đề bài (DLC); mentor (`d_end`); hệ số 2 chừa sai số ước lượng: nhóm tự thống nhất |
| PP-SWR-085 | Sau một lần LKA hoặc ELK, DLC nhỏ nhất ở phía đối diện phải ≥ 0 | Test, vòng kín: S4, S4b, S5, S6, S7, S8, S8b (c, d, e), S20, S21, F24 | Safety, SG-01 | đề bài |
| PP-SWR-086 | DTLE nhỏ nhất trong một lần can thiệp phải ≥ −0,3 m với LKA và ELK vạch liền, và ≥ −0,1 m với ELK mép đường | Test, vòng kín: S4, S5, S6, S20, F24 | Regulatory, SG-03 | Euro NCAP Assessment 4.3.2, 4.3.3.3; EU 2021/646 3.6.2 |
| PP-SWR-088 | Trong lúc ELK can thiệp vì xe ở làn bên, khoảng cách ngang nhỏ nhất tới xe đó khi hai xe ngang hàng phải ≥ 0,3 m | Test, vòng kín: S7, S8, S8b (c, d, e), S21 | Regulatory, SG-03 | Euro NCAP SA 4.3.3.4 (no impact) là mức tối thiểu, 0,3 m theo LSS 7.4.7, nhóm chọn chặt hơn |
| PP-SWR-089 | Nếu ELK được yêu cầu khi lốp trước đã sang quá 0,3 m qua vạch phía side, thì planner không được bắt đầu can thiệp ELK đó | Test: S8 | Safety, SG-01 | nhóm tự thống nhất |
| PP-SWR-090 | Planner không được báo COMPLETED khi điều kiện kết thúc chưa giữ liên tục `T_end_hold` | Test: S4, S5, S20 | Functional | nhóm tự thống nhất |
| PP-SWR-091 | Khi trễ EPS tới 100 ms, DTLE nhỏ nhất phải vẫn đạt PP-SWR-086 | Test, vòng kín: S13 (a, b) | Safety, SG-03 | nhóm tự thống nhất |
| PP-SWR-092 | Nếu LKA, hoặc ELK với lý do khác mép đường, được yêu cầu về một phía mà vạch làn mình ở phía đó không là biên làn đủ tin trong lane model planner nhận, thì planner không được bắt đầu can thiệp đó | Test: F04 | Safety, SG-01 | EU 2021/646 recital 6, Annex I 3.6.2 (vạch nhìn thấy được); Euro NCAP LSS 7.2.6 |
| PP-SWR-093 | Nếu biên phía nguy hiểm của làn đang chạy báo nhảy ra xa biên thật 0,3–1,0 m trong lúc LKA hoặc ELK đang can thiệp, thì PP-SWR-085 và 086 phải vẫn thoả | Test, vòng kín: F24 (a–e) | Safety, SG-01 | mentor (làn nhảy ra xa, planner đẩy xe về làn rồi kéo ra) |
| PP-SWR-094 | Trong một lần LKA hoặc ELK, sau thời điểm DLC thật phía `side` nhỏ nhất của lần đó, DLC này không được giảm quá 0,1 m so với giá trị lớn nhất đã đạt sau thời điểm đó | Test, vòng kín: S4, S4b, S5, S6, S7, S8, S8b (c, d, e), S12 (b, c, d), S13, S16, S20, S21, F24 | Safety, SG-01 | mentor (hiện tượng đẩy về rồi kéo ra); 0,1 m ≈ 3·σ_c0 ban ngày (PP-ASM-011): nhóm tự thống nhất |

Không có mốc cắt thời lượng. Một lần LKA hoặc ELK kết thúc khi COMPLETED (PP-SWR-032), khi REQUEST rời (PP-SWR-036, 037), khi tài xế ghi đè, hoặc khi không còn đủ điều kiện tiếp tục (PP-SWR-046, 047). Can thiệp dài hơn 10 s được cảnh báo âm thanh ở khối Chức năng ADAS (ADAS Function Specification mục 10).

### 8.7 Giới hạn, liên tục, khả thi {#req-limits}

| ID | Yêu cầu | Kiểm chứng | Type | Nguồn |
|---|---|---|---|---|
| PP-SWR-100 | Trong khi `path_valid = true`, lệch ngang giữa hai path liên tiếp phải ≤ 0,05 m ở đoạn 0–1 s, ≤ 0,1 m ở đoạn 1–2 s, ≤ 0,2 m sau 2 s của path | Test: mọi kịch bản, mọi lỗi | Safety, SG-04 | nhóm tự thống nhất (0–2 s); mentor (sau 2 s) |
| PP-SWR-101 | Trong khi `path_valid = true`, lệch hướng giữa hai path liên tiếp phải ≤ 0,005 rad ở đoạn 0–1 s, ≤ 0,01 rad ở đoạn 1–2 s, ≤ 0,02 rad sau 2 s của path | Test: mọi kịch bản, mọi lỗi | Safety, SG-04 | nhóm tự thống nhất (0–2 s); mentor (sau 2 s) |
| PP-SWR-102 | Trong khi `path_valid = true`, lệch độ cong giữa hai path liên tiếp phải ≤ 0,0003 1/m ở đoạn 0–1 s, ≤ 0,0006 1/m ở đoạn 1–2 s, ≤ 0,0012 1/m sau 2 s của path | Test: mọi kịch bản, mọi lỗi | Safety, SG-04 | nhóm tự thống nhất (0–2 s); mentor (sau 2 s) |
| PP-SWR-110 | Trong khi LKA đang lái, a_y của path phải ≤ 3,0 m/s² | Test: S4, S4b | Safety, SG-01 | nhóm tự thống nhất |
| PP-SWR-111 | Trong khi ELK đang lái, a_y của path phải ≤ 4,0 m/s² | Test: S5, S6, S7, S8, S8b (c, d, e), S20, S21 | Safety, SG-01 | nhóm tự thống nhất |
| PP-SWR-112 | Trong khi LKA đang lái, a_y thêm vào phải ≤ 1,5 m/s² | Test: S4, S4b | Safety, SG-01 | nhóm tự thống nhất |
| PP-SWR-113 | Trong khi ELK đang lái, a_y thêm vào phải ≤ 3,0 m/s² | Test: S5, S6, S7, S8, S8b (c, d, e), S20, S21 | Safety, SG-01 | nhóm tự thống nhất |
| PP-SWR-114 | Trong khi LKA đang lái, jerk ngang của path phải ≤ 5 m/s³ | Test: S4, S4b | Safety, SG-01 | ISO 11270, cần kiểm số mục |
| PP-SWR-115 | Trong khi ELK đang lái, jerk ngang của path phải ≤ 10 m/s³ | Test: S5, S6, S7, S8, S8b (c, d, e), S20, S21 | Safety, SG-01 | nhóm tự thống nhất |
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
| PP-SWR-124 | Khi lane model không còn biên làn đủ tin nào (vạch làn mình, vạch làn bên, mép đường) hoặc không hợp lệ, planner phải giữ `path_valid = true` trong `T_coast` rồi đặt `path_valid = false`, sai lệch thời điểm không quá một chu kỳ. Trong khi LCC planner ở `lcc_mode = FOLLOW`, `T_coast` chưa tính (PP-SWR-170 đến 173) | Test: F05, F21 (e), F12 (Lane Model) | Safety, SG-02 | nhóm tự thống nhất |
| PP-SWR-147 | Khi lane model mất cả hai vạch của làn mình mà còn ít nhất một biên làn đủ tin khác, planner phải giữ `path_valid = true` | Test: F21 (a–d) | Functional | mentor |
| PP-SWR-148 | Khi lane model mất cả hai vạch của làn mình mà còn ít nhất một biên làn đủ tin khác, PP-SWR-051 và 100 đến 102 phải vẫn thoả | Test, vòng kín: F21 (a–d) | Safety, SG-01 | nhóm tự thống nhất |

### 8.9 Chịu lỗi: thời gian và toàn vẹn {#req-timing-faults}

| ID | Yêu cầu | Kiểm chứng | Type | Nguồn |
|---|---|---|---|---|
| PP-SWR-126 | Khi message bị mất, lẻ hoặc thành chuỗi, hoặc có jitter ±20 ms, path phải thoả PP-SWR-100 đến 102 và giới hạn jerk của chức năng đang lái | Test: F10 | Safety, SG-04 | nhóm tự thống nhất |
| PP-SWR-127 | Khi message đến muộn hoặc sai thứ tự, path phải thoả PP-SWR-100 đến 102 | Test: F11 | Safety, SG-04 | nhóm tự thống nhất |
| PP-SWR-128 | Trong khi camera gửi 20 Hz và planner chạy 40 Hz, path phải thoả PP-SWR-100 đến 102 ở mọi chu kỳ | Test: mọi kịch bản, F13 | Safety, SG-04 | nhóm tự thống nhất |
| PP-SWR-129 | Nếu message pub/sub bị lặp, hoặc counter của nó tăng không quá MaxDeltaCounter của Interface Control Document mục 3 so với message nhận trước đó, thì output phải giống ca không lỗi cùng seed | Test: F15 (lặp, nhảy trong giới hạn) | Safety | AUTOSAR PRS E2E R22-11 [PRS_E2E_00591] (OK, OKSOMELOST) |
| PP-SWR-130 | Nếu counter đứng yên hoặc tăng quá MaxDeltaCounter, message pub/sub có valid = false hoặc khung CAN có CRC sai, thì output phải giống ca mất message tương ứng | Test: F15 (nhảy quá giới hạn, đứng yên), F16 (a, c), F17 | Safety | AUTOSAR PRS E2E R22-11 [PRS_E2E_00591] (REPEATED, WRONGSEQUENCE); nhóm tự thống nhất |
| PP-SWR-131 | Nếu tuổi của lane model hoặc ObjectList vượt 250 ms, thì planner phải coi input đó không hợp lệ | Test: Q1 (300 ms) | Safety | nhóm tự thống nhất |
| PP-SWR-132 | Nếu stamp của input ở tương lai quá 10 ms, thì planner phải coi input đó không hợp lệ | Test: F19 | Safety | nhóm tự thống nhất |
| PP-SWR-133 | Trong khi tuổi của lane model hoặc ObjectList trong khoảng 170–250 ms, planner phải tiếp tục dùng input đó | Test: Q1 (200 ms) | Functional | nhóm tự thống nhất |
| PP-SWR-134 | Planner phải ghi log số frame lane model và ObjectList có tuổi vượt 170 ms | Inspection | Functional | nhóm tự thống nhất |

Nguồn: 170 ms = trễ giả định lớn nhất 120 ms (PP-ASM-001) cộng 50 ms; 250 ms = trễ lớn nhất benchmark quét (200 ms) cộng 50 ms; 10 ms = lệch đồng hồ lớn nhất trước lần đồng bộ đầu (PP-ASM-012).

### 8.10 Chịu lỗi: input không hợp lệ {#req-invalid-input}

| ID | Yêu cầu | Kiểm chứng | Type | Nguồn |
|---|---|---|---|---|
| PP-SWR-140 | Nếu ObjectList không hợp lệ, thì LCC planner phải đưa phần dời tâm của LCC về 0, vẫn thoả PP-SWR-001, 003 và 100 đến 102 | Test: F12 (Perception, trong S3) | Safety | nhóm tự thống nhất |
| PP-SWR-141 | Nếu ObjectList không hợp lệ, thì LKA/ELK planner vẫn phải thực hiện can thiệp ELK được yêu cầu | Test: F12 (Perception, trong S5) | Safety, SG-03 | nhóm tự thống nhất |
| PP-SWR-142 | Nếu IMU, tốc độ hoặc góc lái không hợp lệ, kể cả khi khung CAN báo qualifier FAULT, thì planner phải đặt `path_valid = false` trong không quá một chu kỳ | Test: F12 (IMU, tốc độ, góc lái), F16 (b), F17 | Safety | nhóm tự thống nhất |
| PP-SWR-143 | Nếu ego-motion không hợp lệ, thì planner phải đặt `path_valid = false` trong không quá một chu kỳ | Test: F20 | Safety | nhóm tự thống nhất |
| PP-SWR-144 | Nếu VehicleStateEstimate không hợp lệ, thì planner không được bắt đầu can thiệp LKA hoặc ELK mới | Test: F12 (v_y) | Safety | nhóm tự thống nhất |
| PP-SWR-145 | Nếu FunctionRequests quá timeout 75 ms, thì mỗi planner phải đặt `lcc_mode` hoặc `active_function` bằng NONE và `path_valid = false` trong không quá một chu kỳ | Test: F12 (FunctionRequests) | Safety | nhóm tự thống nhất |
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
| PP-SWR-150 | LCC planner phải gửi LateralLimits mỗi chu kỳ | Test: S14 | Interface | nhóm tự thống nhất |
| PP-SWR-151 | `LateralLimits.v_max` phải bằng √(aysmax / κ_max), với κ_max là độ cong lớn nhất của tâm làn thật trong tầm nhìn của lane model, tối đa 126 m, sai lệch ≤ 5 % | Test: S14, Q4 | Interface | nhóm tự thống nhất |
| PP-SWR-152 | `LateralLimits.distance` phải bằng khoảng cách dọc tới điểm có κ_max, sai lệch ≤ 5 m | Test: S14 | Interface | nhóm tự thống nhất |
| PP-SWR-153 | Khi LongitudinalPlan hợp lệ, `longitudinal_velocity` và `acceleration` của Trajectory phải lấy theo LongitudinalPlan | Test: S14 | Interface | nhóm tự thống nhất |
| PP-SWR-154 | Nếu LongitudinalPlan mất hoặc quá timeout 75 ms, thì Trajectory phải dùng tốc độ hiện tại không đổi và gia tốc 0 | Test: S14 (d) | Interface | nhóm tự thống nhất |
| PP-SWR-155 | Nếu LongitudinalPlan mất hoặc quá timeout 75 ms, thì planner phải giữ `path_valid = true` | Test: S14 (d) | Safety | nhóm tự thống nhất |
| PP-SWR-156 | Nếu LongitudinalPlan có `v` hoặc `a` ở bất kỳ điểm nào ngoài dải của Interface Control Document 5.7 (gồm NaN và vô cực), thì planner phải xử lý như chưa nhận được message đó | Test: F23 | Interface | Interface Control Document 5.3, 5.7 |

### 8.13 LCC: bám xe trước {#req-follow}

Khi mất cả hai vạch làn mình mà không còn biên đủ tin khác, LCC planner bám xe trước thay vì bám path cũ. Điều kiện vào và duy trì theo mentor; cách dựng path ở Software Architectural Design mục 6.3.

| ID | Yêu cầu | Kiểm chứng | Type | Nguồn |
|---|---|---|---|---|
| PP-SWR-170 | Khi LCC ở REQUEST, hai vạch L1, R1 đều không đủ tin, không còn biên làn đủ tin khác, và thoả mọi điều kiện V1 đến V6 và M1 đến M6 ở hai bảng dưới, thì LCC planner phải đặt `lcc_mode = FOLLOW` trong không quá một chu kỳ | Test: S22 (a, c, d, e) | Functional | mentor |
| PP-SWR-171 | Nếu một điều kiện V1 đến V6 hoặc M1 đến M6 không thoả, thì LCC planner không được đặt `lcc_mode = FOLLOW` | Test: S23 (a–e) | Safety, SG-01 | mentor |
| PP-SWR-172 | Khi `lcc_mode = FOLLOW` và một điều kiện M1 đến M6 không còn thoả, thì LCC planner phải rời FOLLOW trong không quá một chu kỳ | Test: S22 (b, c, e), F25 (c) | Safety, SG-01 | mentor |
| PP-SWR-173 | Khi LCC planner rời FOLLOW mà lane model vẫn không có biên làn đủ tin nào, thì PP-SWR-124 phải áp dụng, với `T_coast` tính từ lúc rời FOLLOW | Test: S22 (b) | Safety, SG-02 | nhóm tự thống nhất |
| PP-SWR-174 | Khi hai vạch L1, R1 đủ tin trở lại trong lúc `lcc_mode = FOLLOW`, thì `lcc_mode` phải về LANE và path phải thoả PP-SWR-100 đến 102 | Test: S22 (a) | Safety, SG-04 | nhóm tự thống nhất |
| PP-SWR-175 | Trong khi `lcc_mode = FOLLOW`, path phải thoả PP-SWR-001, 003, 051 và 100 đến 102 | Test, vòng kín: S22 (a, c, d) | Safety, SG-01 | nhóm tự thống nhất |
| PP-SWR-176 | Nếu LeadTarget không hợp lệ (mất, quá timeout, quá tuổi hoặc ngoài dải), thì LCC planner không được vào FOLLOW và phải rời FOLLOW trong không quá một chu kỳ | Test: F25 (a, b, d) | Safety, SG-01 | nhóm tự thống nhất |
| PP-SWR-177 | `LccStatus.lcc_mode` phải đúng chế độ mà path của chu kỳ đó được dựng | Test: S22, S23 | Interface | nhóm tự thống nhất |

**Điều kiện vào bám xe** (mentor):

| # | Điều kiện | Ghi chú |
|---|---|---|
| V1 | Xe trước là xe tải hoặc xe con (`LeadTarget.classification` là TRUCK hoặc CAR) | |
| V2 | Khoảng cách `LeadTarget.gap` trong [2 m, 50 m] | Từ bumper trước xe mình tới bumper sau xe trước |
| V3 | Lệch ngang giữa xe mình và xe trước < `follow_lat_max` (1,0 m) | Đo theo tâm làn gốc (PP-ASM-025) |
| V4 | Tốc độ ngang của xe trước < `follow_vlat_max` (0,6 m/s) | Đo theo tâm làn gốc (PP-ASM-025) |
| V5 | `LeadTarget.id` bằng `LongitudinalPlan.target_id` | Xe trước là mục tiêu ACC |
| V6 | Hai vạch làn mình mất trong lúc LCC đang lái | Còn biên làn bên hoặc mép đường đủ tin thì không bám xe (PP-ASM-027) |

**Điều kiện duy trì bám xe** (mentor). Khi vào cũng phải thoả cả sáu điều kiện này:

| # | Điều kiện | Ghi chú |
|---|---|---|
| M1 | Lệch ngang của path so với tâm làn gốc < 0,8 m | Còn bị chặn theo khoảng trống mỗi bên trừ `dlc_offset_min` (PP-ASM-026) |
| M2 | Hai vạch làn mình vẫn mất và có path bám hợp lệ | |
| M3 | Tốc độ xe mình < 60 km/h | `ESC_Speed` |
| M4 | Góc vô lăng < 20° | `SAS_Steering` |
| M5 | Quãng đường đã đi từ lúc vào FOLLOW < 30 m | Tích phân ego-motion |
| M6 | Xe trước vẫn là xe tải hoặc xe con, cùng `id` | |

### 8.14 Ghép với arbitrator {#req-arbitrator}

| ID | Yêu cầu | Kiểm chứng | Type | Nguồn |
|---|---|---|---|---|
| PP-SWR-180 | Trong khi LKA/ELK planner có `active_function = NONE`, `Trajectory.header.valid` của nó phải là false | Test: S9 | Interface | mentor (LKA/ELK chỉ bật khi lệch làn) |
| PP-SWR-181 | Mỗi planner phải thoả mọi requirement của mình khi planner kia không chạy | Inspection; Test: S9 | Interface | mentor (hai planner ghép vào hệ thống của công ty) |

## 9. Performance targets {#req-targets}

Không có ngưỡng đạt. Software Qualification Test Specification đo các chỉ số này để chọn bộ calibration và so sánh kỹ thuật, theo thứ tự ưu tiên: an toàn, quy định, cảm nhận người lái, thời gian tính.

| ID | Yêu cầu | Kiểm chứng | Type | Nguồn |
|---|---|---|---|---|
| PP-SWR-050 | Lệch ngang của path nên nhỏ, trong toàn bộ ODD và khi lane model có lỗi | Test: S1 (a, b, d, e), S6b, S11, S19, F03, F04, F21, F22, Q4 | Performance | đề bài |
| PP-SWR-002 | a_y thêm vào lớn nhất khi LCC đưa xe về giữa hoặc dời tâm nên nhỏ | Test: S2, S3 | Performance | nhóm tự thống nhất |
| PP-SWR-004 | Jerk ngang của path khi LCC đang lái nên nhỏ | Test: S1 | Performance | nhóm tự thống nhất |
| PP-SWR-008 | Thời gian từ lúc a_y cần lớn nhất < aysmax tới lúc `lateral_limit_reached` tắt nên ngắn | Test: S1 (a, b, d, e) | Performance | nhóm tự thống nhất |
| PP-SWR-013 | Phần lệch ngang tăng thêm so với ca trễ 0, khi trễ camera 0–200 ms kèm jitter ±20 ms, nên nhỏ | Test: Q1 | Performance | nhóm tự thống nhất |
| PP-SWR-016 | Phân vị 99 % của thời gian tính mỗi chu kỳ nên nhỏ | Test: mọi kịch bản | Performance | nhóm tự thống nhất |
| PP-SWR-064 | Thời gian từ lúc `lateral_limit_reached` bật tới lúc a_y cần tại vị trí xe vượt aysmax nên dài | Test: S1b | Performance | nhóm tự thống nhất |
| PP-SWR-053 | Thời gian từ lúc LCC bắt đầu lái (xe lệch tâm tới 0,5 m) tới lúc lệch ngang ≤ 0,1 m nên ngắn | Test: S2 | Performance | nhóm tự thống nhất |
| PP-SWR-057 | Khoảng cách ngang nhỏ nhất từ thân xe tới vật ở hai bên trong lúc dời tâm nên lớn | Test: S3, S3b, S15 | Performance | nhóm tự thống nhất |
| PP-SWR-059 | Thời gian từ lúc đuôi xe lớn qua tới lúc lệch ngang ≤ 0,1 m nên ngắn | Test: S3 | Performance | nhóm tự thống nhất |
| PP-SWR-068 | Trong khi LCC đang lái, a_y lớn nhất của xe nên nhỏ | Test, vòng kín: S1, S1b, S14 | Performance | nhóm tự thống nhất |
| PP-SWR-069 | Trong khi LCC đang lái, jerk ngang lớn nhất của xe nên nhỏ | Test, vòng kín: S1, S1b, S14 | Performance | nhóm tự thống nhất |
| PP-SWR-070 | Trong khi LCC đang lái, DLC nhỏ nhất của xe ở hai phía nên lớn | Test, vòng kín: S1, S1b, S2, S3 | Performance | nhóm tự thống nhất |
| PP-SWR-081 | Thời gian từ lúc LKA bắt đầu path can thiệp tới COMPLETED nên ngắn | Test: S4 | Performance | nhóm tự thống nhất |
| PP-SWR-082 | Thời gian từ lúc ELK bắt đầu path can thiệp tới COMPLETED nên ngắn | Test: S5, S6, S7, S8, S8b (c, d, e), S20, S21 | Performance | nhóm tự thống nhất |
| PP-SWR-087 | DTLE nhỏ nhất của LKA nên lớn | Test, vòng kín: S4 | Performance | nhóm tự thống nhất |
| PP-SWR-125 | Khi lane model có c2 sai, tỉ lệ giữa lệch ngang của path trên đoạn 2–3 s và lệch của một path bám đúng lane model sai đó nên nhỏ | Test: F06 | Performance | đề bài |
| PP-SWR-178 | Trong khi `lcc_mode = FOLLOW`, lệch ngang giữa path và vết thật của xe trước, tại cùng vị trí dọc, nên nhỏ | Test: S22 (a, c, d) | Performance | nhóm tự thống nhất |

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
| 1.11 | 2026-11-12 | PP-ASM-021 ghi kiểu controller và thời gian nhìn trước tối đa 0,6 s, để kiểm được các ngưỡng tầm nhìn của khối Chức năng ADAS |
| 1.12 | 2026-11-12 | Thêm PP-SWR-048: FunctionRequests quá tuổi 45 ms xử lý như chưa nhận. Lý do: Q3 ở 60 ms vượt tuổi tối đa của Interface Control Document mà SRS chưa nói planner phải làm gì (PP-PR-023) |
| 1.13 | 2026-11-13 | Thêm PP-SWR-156: LongitudinalPlan ngoài dải xử lý như chưa nhận. Lý do: B0 C2 trượt, plan ở đầu cao của dải float32 làm Trajectory có vô cực (PP-PR-024). Kiểm chứng bằng F23 |
| 1.14 | 2026-11-13 | PP-SWR-083 obsolete và ghi chú mục 8.6 theo PP-TS-016: R79 và EU 2021/646 chỉ đòi cảnh báo khi can thiệp quá 10 s; cắt ở 10 s đi ngược SG-02, SG-03. S8b (c) chuyển thành ca can thiệp ở PP-SWR-082, 085, 111, 113, 115 (PP-PR-027). Ảnh hưởng: Hazard Analysis and Risk Assessment mục 4, Software Architectural Design, Software Detailed Design T7, T9, Software Qualification Test Specification 5, 8.1, Mentor Report |
| 1.15 | 2026-11-13 | PP-SWR-088 chỉ xét lúc hai xe ngang hàng; thêm S8b (c, d, e) vào cột Kiểm chứng; định nghĩa Ngang hàng dùng cho mọi xe. Lý do: khoảng hở ngang khi xe kia còn ở phía sau không cho biết rủi ro va chạm; S8b (c, d, e) là ELK vì xe ở làn bên (PP-PR-029). Ảnh hưởng: Software Qualification Test Specification 8.2, bên chấm |
| 1.16 | 2026-11-13 | Định nghĩa Hai path liên tiếp: không tính cặp path trong lúc tài xế ghi đè. Lý do: khi tài xế lái, PP-SWR-039 và 100 không cùng thoả được; R79 5.6.4.3 ưu tiên tài xế (PP-TS-017, PP-PR-032). Ảnh hưởng: PP-SWR-100 đến 102 và các requirement dựa vào chúng; Software Qualification Test Specification 8.1; bên chấm |
| 1.17 | 2026-11-14 | Mục 5 ghi giới hạn quan sát khi vào cua ở tốc độ cao theo PP-PR-007, phương án B. Giữ phạm vi áp dụng của PP-SWR-051 |
| 1.18 | 2026-11-14 | Thêm PP-SWR-092: không bắt đầu LKA, ELK vạch về phía có vạch làn mình không đủ tin. Lý do: EU 2021/646 không đòi ELKS khi không có vạch; hệ thống trên xe bán ra không can thiệp về phía không nhận ra vạch; hành vi này trước chỉ có ở Software Detailed Design (PP-PR-038). Ảnh hưởng: Software Qualification Test Specification 5 (F04), 8.1; Software Detailed Design T9; bên chấm |
| 1.19 | 2026-11-14 | PP-SWR-129, 130: counter nhảy trong MaxDeltaCounter thì dùng message (như không lỗi), quá giới hạn hoặc đứng yên thì như mất message. Lý do: PP-PR-035, câu cũ hiểu được theo hai cách; theo trạng thái của AUTOSAR E2E Profile 5. Ảnh hưởng: Interface Control Document 1.11 mục 3, 4; Software Detailed Design T1; F15 (thêm g); bên chấm |
| 1.20 | 2026-11-14 | PP-SWR-032: báo COMPLETED trong tối đa 0,5 s sau khi điều kiện giữ đủ `T_end_hold`, thay cho đúng tick. Lý do: PP-TS-018 V1; planner chỉ thấy trạng thái ước lượng nên không báo được đúng tick của chuyển động thật; báo sớm vẫn trượt PP-SWR-090. Ảnh hưởng: PP-SWR-032; S4, S5, S12, S13 |
| 1.21 | 2026-11-16 | PP-SWR-100 đến 102 nới theo mentor: 0,05 → 0,2 m, 0,005 → 0,02 rad, 0,0003 → 0,0012 1/m (cùng hệ số 4); nguồn đổi từ đề bài sang mentor. Lý do: mentor nới SWR-100 lên 0,2 m, 101 và 102 nới tương ứng. Ảnh hưởng: mọi requirement dựa vào PP-SWR-100 đến 102 (031, 061, 120 đến 128, 135 đến 139, 148, 149), Software Qualification Test Specification 8.1, Software Detailed Design T4, Software Architectural Design A.3; PP-SWR-039, 040 (0,05 m) giữ nguyên, không còn trùng ngưỡng với 100 |
| 1.22 | 2026-11-16 | PP-SWR-100 đến 102 chia ba đoạn theo thời gian trên path: 0–1 s giữ 0,05 m, 0,005 rad, 0,0003 1/m; 1–2 s gấp đôi; sau 2 s theo mentor (SRS 1.21). Lý do: controller nhìn trước trong đoạn đầu (PP-ASM-021); ở 25 m/s, lệch 0,2 m tại 15 m làm a_y nhảy khoảng 1,1 m/s² trong một chu kỳ, 0,05 m khoảng 0,28 m/s² (PP-TS-019). Ảnh hưởng: như 1.21; Software Qualification Test Specification 8.1, Software Detailed Design T4, Software Architectural Design A.3, Mentor Report |
| 1.23 | 2026-11-17 | PP-SWR-031: ngoại lệ áp cho chu kỳ đầu của mọi lần LKA, ELK bắt đầu, bỏ điều kiện xe lệch path cũ quá 0,1 m hoặc 0,1 m/s. Thêm PP-SWR-049: độ cong điểm đầu khớp độ cong thật của xe. Lý do: PP-PR-062; path của chức năng trước bám theo xe đang trôi ra, nên khi xe còn trong dung sai, path ELK bị trộn với path hướng ra ngoài và ELK quay vào muộn (DTLE tới −0,54 m). Đề bài chỉ đòi không có bước nhảy ở lệnh lái. Ảnh hưởng: PP-SWR-031, 049, 080, 100 đến 102; Software Qualification Test Specification 8.1; T4, T7 |
| 1.24 | 2026-11-18 | Tách thành hai planner: LCC planner (LCC, tên khác của HWA) và LKA/ELK planner; bỏ arbitration giữa ba chức năng vì arbitrator thuộc công ty (PP-ASM-022). Giữ LKA và ELK riêng, chọn ELK > LKA trong LKA/ELK planner. Điều kiện kết thúc thêm lệch tâm ≤ `d_end` = 10 cm và `v_lat_end` = 0,15 m/s theo mentor; PP-SWR-084 đổi theo đích tâm làn. Dời tâm vì xe lớn: một xe lớn thì lệch 10 cm khi làn bên kia không có xe tới, hai xe lớn thì giữ cách cân bằng (PP-SWR-055, 065, 066). Thêm PP-SWR-093, 094 (biên nhảy lúc can thiệp), 170 đến 178 (LCC bám xe trước), 180, 181, 019, 067 (LCC phải lái khi ở REQUEST, trước đây nằm trong PP-SWR-030); PP-SWR-039, 040 thêm vế LKA, LCC ở REQUEST; PP-ASM-022 đến 028. Lý do: mentor đổi sản phẩm ngày 18/11. Ảnh hưởng: mọi requirement dùng chữ HWA, `active_function`, PathStatus; Interface Control Document, Software Architectural Design, Software Detailed Design, ADAS Function Specification, Hazard Analysis and Risk Assessment, Software Qualification Test Specification, Mentor Report |
| 1.25 | 2026-11-18 | Mục 7: thêm giới hạn của `T_end_margin`, `T_return`, `T_return_object`. Không đổi requirement. Lý do: PP-TS-026, PP-PR-072 |
| 1.26 | 2026-11-23 | PP-SWR-001: trần a_y của path LCC từ aysmax lên aysmax + 0,3 m/s² theo R79 5.6.2.1.1; mục 7 thêm `ay_margin_hwa` (0–0,3 m/s²); thêm PP-ASM-029. Lý do: PP-TS-020 chọn V1a; ở cua cần đúng aysmax, path cần phần a_y để kéo xe về khi xe lệch. PP-SWR-094: cột Kiểm chứng mở sang mọi kịch bản có LKA, ELK (S4b, S7, S8, S8b, S12, S13, S16, S21). Lý do: PP-PR-077; câu requirement áp cho mọi lần can thiệp. Ảnh hưởng: PP-SWR-001, 051, 094; Software Architectural Design mục 6.2, 9, 11; Software Detailed Design T10; Software Qualification Test Specification 5; `calibration.yaml` |
| 1.27 | 2026-11-23 | PP-SWR-130 bỏ qualifier FAULT, chỉ giữ lỗi truyền thông (counter, CRC) và message pub/sub `valid = false`; PP-SWR-142 thêm qualifier FAULT và F16 (b). Lý do: PP-PR-036; qualifier FAULT là cảm biến tự báo hỏng, khác lỗi truyền thông mà E2E bảo vệ, và phản ứng ngay an toàn hơn chờ hết timeout. Ảnh hưởng: PP-SWR-130, 142; Software Qualification Test Specification 6 (F16); `sim/faults/channel.py`. PP-SWR-063: thêm S19 (f), làn hẹp dần trong lúc LCC lái; S19 (b) giờ bị từ chối vào LCC theo ADAS Function Specification mục 7 (PP-PR-003) |
| 1.28 | 2026-11-23 | Thêm performance target PP-SWR-068 (a_y lớn nhất của xe), 069 (jerk ngang lớn nhất của xe), 070 (DLC nhỏ nhất của xe). Lý do: so sánh kỹ thuật sinh path cần chỉ số đo trên chuyển động thật của xe; giá trị đỉnh trên path bị giới hạn khả thi kẹp nên không phân biệt được kỹ thuật; khoảng cách tới biên làn là đại lượng an toàn trực tiếp, lệch khỏi tâm làn (PP-SWR-050) chỉ là đại lượng thay thế (PP-TS-031). Không đổi requirement. Ảnh hưởng: Software Qualification Test Specification 8.2, 9.1, 9.2; bên chấm |

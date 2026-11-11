# Software Architectural Design

| Mục | Nội dung |
|---|---|
| Mã tài liệu | `PP-SAD` |
| Phiên bản | 1.4 |
| Trạng thái | BL1 |
| Tác giả | thongbui |
| Người review | thongbui |
| Cập nhật | 2026-11-11 |

## 1. Purpose and scope {#design-scope}

- **Mục đích:** Mô tả cách path planner đáp ứng Software Requirements Specification: kiến trúc, chu kỳ chạy, thiết kế từng phần và danh mục calibration parameter.
- **Phạm vi:** Reference line, arbitration, path cho HWA, path can thiệp cho LKA và ELK, điều kiện kết thúc, xử lý lỗi input, interface với khối dọc.

## 2. References {#design-references}

| Tài liệu | Dùng cho |
|---|---|
| [Software Requirements Specification](report.html?doc=path-planner-software-requirements-specification&lang=vi) | Requirement, performance target, giới hạn của calibration parameter |
| [Interface Control Document](report.html?doc=path-planner-interface-control-document&lang=vi) | Schema của mọi input, output |
| [Architecture Decision Records](report.html?doc=path-planner-architecture-decision-records&lang=vi) | PP-ADR: phương án đã xét và lý do chọn |
| [Software Detailed Design](report.html?doc=path-planner-software-detailed-design&lang=vi) | Thuật toán chi tiết (T1 … T11) |
| [ADAS Function Specification](report.html?doc=adas-function-specification&lang=vi) | Khi nào HWA, LKA, ELK được yêu cầu |
| [Software Qualification Test Specification](report.html?doc=path-planner-software-qualification-test-specification&lang=vi) | Simulator, khối chạy thử, test case |
| Apollo (Baidu), trajectory stitching; Werling và cộng sự (2010), Frenet | Cách nối path, hệ toạ độ lập path |

## 3. Architecture {#planner-cycle}

### 3.1 Thành phần {#design-components}

| Thành phần | Việc | Input | Output |
|---|---|---|---|
| Input check | Kiểm valid, counter, CRC, timeout, tuổi; message không hợp lệ coi như chưa nhận | Mọi input | Input đã kiểm, cờ hợp lệ |
| Latency compensation | Dời lane model từ lúc chụp tới t0 bằng ego-motion (PP-ADR-002) | LaneModel, EgoMotionQuery | Lane model tại t0 |
| Reference line | Kiểm tính nhất quán của biên, chọn biên đủ tin, tạo tâm làn và biên làn (mục 4) | Lane model tại t0, yaw rate, tốc độ, path cũ | Reference line, khoảng trống mỗi bên |
| Arbitration | Chọn chức năng đang lái và pha can thiệp (mục 5) | FunctionRequests, cờ hợp lệ | `active_function`, `intervention_phase` |
| Path generation | Path HWA (mục 6) hoặc path can thiệp (mục 7), trong Frenet | Reference line, trạng thái xe, LongitudinalPlan, ObjectList | Path ứng viên |
| Stitching và continuity | Nối với path cũ, kiểm PP-SWR-100 đến 102 (mục 9) | Path ứng viên, path cũ | Path đã nối |
| Feasibility | Kiểm a_y, jerk, góc và tốc độ lái theo giới hạn của chức năng; cắt khi vượt (mục 9) | Path đã nối, VehicleConfig | Path cuối, `lateral_limit_reached` |
| Output | Đổi sang `base_link`, lấy mẫu 31 điểm, gửi | Path cuối, trạng thái | Trajectory, PathStatus, LateralLimits |

### 3.2 Cycle sequence {#planner-sequence}

Chu kỳ bắt đầu ở tick t0, mỗi 25 ms. t_c là thời gian tính.

| # | Lúc | Từ → tới | Nội dung | Requirement |
|---|---|---|---|---|
| 1 | t0 | Bộ lập lịch → Planner | Tick chu kỳ | PP-SWR-010 |
| 2 | t0 | Input check → Planner | Message mới nhất đã kiểm của mọi input; LongitudinalPlan của chu kỳ trước | PP-SWR-126 đến 134 |
| 3 | t0 | Planner → Ego-motion | Truy vấn chuyển động từ stamp lúc chụp của lane model tới t0 | PP-SWR-012, 143 |
| 4 | t0 đến t0 + t_c | Planner | Latency compensation, reference line, arbitration, path generation, stitching, feasibility | PP-SWR-030, 100 đến 102, 110 đến 117 |
| 5 | t0 + t_c | Planner → Lateral Controller | Trajectory (`header.stamp_us = t0`), PathStatus | PP-SWR-010, 011, 012 |
| 6 | t0 + t_c | Planner → Chức năng ADAS | PathStatus | PP-SWR-010 |
| 7 | t0 + t_c | Planner → Khối dọc | LateralLimits | PP-SWR-150 |
| 8 | Sau t0 + t_c | Khối dọc → Planner | LongitudinalPlan, dùng ở chu kỳ sau để không có vòng lặp trong cùng chu kỳ | PP-SWR-153 |

**Deadline.** Gửi xong bước 5 đến 7 trước t0 + `t_budget`. Chu kỳ nào tính quá deadline thì vẫn gửi, ghi log overrun; bên nhận đọc path theo stamp nên path gửi muộn vẫn đúng thời điểm.

### 3.3 Latency chain {#latency-chain}

Mọi con số trễ là giả định (Software Requirements Specification mục 6).

| # | Đoạn | Xấu nhất (ms) | Gây ra | Bù |
|---|---|---|---|---|
| 1 | Camera chụp → Lane Model gửi | 120 (PP-ASM-001) | Camera, Lane Model | Planner, theo stamp lúc chụp |
| 2 | Lane Model gửi → planner đọc | 50 (camera 20 Hz) | Nhịp camera | Planner, theo stamp lúc chụp; giữa hai frame dời bằng ego-motion |
| 3 | Planner tính và gửi | 5 (`t_budget`) | Planner | Lateral Controller, đọc path theo stamp (PP-ADR-010) |
| 4 | Truyền Trajectory | 1 (PP-ASM-007) | Pub/sub | Như dòng 3 |
| 5 | Chờ chu kỳ controller | 10 (100 Hz) | Nhịp controller | Như dòng 3 |
| 6 | Controller tính | ? | Lateral Controller | Như dòng 3 |
| 7 | EPS chấp hành | 50 (PP-ASM-014) | EPS | Lateral Controller, chọn điểm path ở thời điểm hiện tại cộng trễ chấp hành |
| 8 | Yaw rate: IMU → planner, song song | 5 + trễ bộ lọc chưa biết (PP-ASM-003, 004) | CAN, bộ lọc | Không bù; planner chịu được tới 50 ms (PP-SWR-138) |
| 9 | FunctionRequests → planner, song song | 45 (PP-ASM-006) | Pub/sub, nhịp planner | Không bù; phản ứng trong một chu kỳ (PP-SWR-038) |

Tổng xấu nhất từ camera tới bánh xe (dòng 1 đến 7, chưa kể dòng 6): 236 ms. Planner bù 170 ms đầu; 66 ms sau planner do Lateral Controller bù (PP-ASM-017).

## 4. Reference line {#reference-line}

| Tình huống | Cách làm | Liên quan |
|---|---|---|
| Hai vạch L1, R1 đủ tin | Tâm làn là trung bình hai đa thức | PP-SWR-050 |
| Mất một vạch | Vạch còn lại dời một nửa bề rộng làn nhớ được | PP-SWR-123 |
| Mất hai vạch làn mình, còn biên khác đủ tin | Suy tâm làn từ vạch L2, R2 và mép đường: mỗi biên cộng khoảng cách nhớ được tới tâm làn, kết hợp theo phương sai. Khoảng cách nhớ được chỉ cập nhật khi hai vạch làn mình đủ tin. Chỉ HWA được lái trên tâm làn suy ra | PP-SWR-047, 147, 148; PP-ADR-011; T2 |
| Không còn biên đủ tin | Bám path cũ, đưa về `base_link` mới, tối đa `T_coast`, rồi `path_valid = false` | PP-SWR-124; PP-ADR-009 |
| Kiểm tính nhất quán của biên | Lane model không gửi cờ c0 jump (PP-ASM-009). Mỗi biên được kiểm ở hai thang. Từng frame: so với biên frame trước đã dời bằng ego-motion; lệch quá `k_jump`·σ là nhảy hoặc nhận nhầm vạch. Thang chậm: độ song song của hai biên (hiệu c1, c2) và bề rộng so với bề rộng nhớ được. Biên không nhất quán thì không dùng, neo tâm làn vào biên còn lại, không cập nhật bề rộng nhớ được. Thay đổi thật của làn được nhận khi cả hai biên cùng xác nhận qua `T_confirm` | PP-SWR-060, 121, 122; PP-ADR-006 |
| Làn mở rộng (làn khẩn cấp, tách nhánh, thêm làn) | Thang chậm phát hiện biên mở rộng; tâm làn neo vào biên ổn định | PP-SWR-060 |
| c0 jump | Nối với path cũ, dời tâm có giới hạn tốc độ | PP-SWR-121 |
| c2 sai ở xa | Kết hợp có trọng số c2 của camera, độ cong r/v và lịch sử path | PP-SWR-125; T5 |
| Lane model đổi làn | Chuyển reference line sang làn mới, nối path | PP-SWR-061 |
| Khoảng trống không đủ | Khoảng trống mỗi bên < `free_space_min` thì `lane_too_narrow = true` | PP-SWR-063 |

### 4.1 Nhiễu còn lại của lane model {#design-noise}

Ba lớp, dùng path của chính planner làm điểm tựa, không lọc lại cảm biến (PP-ADR-007):

| Lớp | Cách làm |
|---|---|
| Bắt đầu từ path cũ | Path mới bắt đầu từ trạng thái của path chu kỳ trước, nên nhiễu một frame chỉ đổi phần xa của path |
| Giới hạn tốc độ đổi tham chiếu | Tâm làn mà path bám được dịch tối đa `ref_rate` |
| Phạt jerk | Path được chọn để ít jerk, không theo dao động nhỏ và nhanh |

Đổi lại path phản ứng chậm hơn khi làn đổi thật; Software Qualification Test Specification đo cả độ rung lẫn độ trễ khi vào cua.

### 4.2 Trạng thái đầu của path {#design-initial-state}

- Trajectory stitching (PP-ADR-004): path mới bắt đầu từ điểm tương ứng trên path cũ. Xe lệch khỏi path cũ hơn `stitch_reset` thì bắt đầu từ trạng thái đo được.
- Lúc LKA hoặc ELK bắt đầu: luôn từ trạng thái đo được (PP-SWR-080); xe đã lệch khỏi path cũ hơn dung sai của PP-SWR-080 thì không nối với path cũ (PP-SWR-031).
- Trạng thái ngang đo được (d0, góc lệch, v_lat) do planner tự tính từ input của mình (PP-ADR-014). Khối Chức năng ADAS tự tính theo cùng công thức.

## 5. Arbitration {#design-arbitration}

- Mỗi chu kỳ chọn chức năng ưu tiên cao nhất đang ở REQUEST: ELK > LKA > HWA. OFF, UNAVAILABLE, FAULT, STANDBY coi như không yêu cầu (PP-SWR-030).
- Planner tự quyết định lúc kết thúc can thiệp, không chờ khối Chức năng ADAS (mục 7.1).
- Nhớ chức năng vừa COMPLETED; chỉ nhận lần mới khi state đã rời REQUEST rồi quay lại (PP-SWR-034, 041).
- FunctionRequests quá timeout: coi cả ba chức năng tắt (PP-SWR-145).
- Khi tài xế ghi đè, khối Chức năng ADAS hủy LKA, ELK và bật `driver_override` trong cùng message. Với vạch liền, LKA được yêu cầu trước ELK, nên hai chức năng có thể cùng ở REQUEST.

### 5.1 Arbitration state {#arbitration-states}

Trạng thái là `active_function`. Mỗi ô ghi trạng thái kế tiếp và việc planner làm; "—" là không đổi hoặc không xảy ra.

| Sự kiện | Đang ở NONE | Đang ở HWA | Đang ở LKA | Đang ở ELK | Requirement |
|---|---|---|---|---|---|
| HWA vào REQUEST | → HWA; path từ trạng thái xe, đưa về giữa | — | Ở lại LKA | Ở lại ELK | PP-SWR-030, 052 |
| HWA rời REQUEST | — | → NONE; `path_valid` giữ true | Ở lại LKA; kết thúc thì về NONE | Ở lại ELK; kết thúc thì về NONE | PP-SWR-033, 042 |
| LKA vào REQUEST | → LKA nếu v_y hợp lệ và tâm làn không phải suy ra | Như NONE; nối path | — | Ở lại ELK | PP-SWR-030, 031, 047, 080, 144 |
| ELK vào REQUEST | → ELK nếu v_y hợp lệ và tâm làn không phải suy ra | Như NONE; nối path | Như NONE; nối path | — | PP-SWR-030, 031, 047, 144 |
| Chức năng đang can thiệp rời REQUEST, kể cả khi tài xế ghi đè | — | — | → HWA nếu HWA ở REQUEST, không thì NONE; `path_valid` giữ true | → LKA nếu LKA ở REQUEST; → HWA nếu chỉ HWA ở REQUEST; không thì NONE | PP-SWR-030, 036, 037 |
| Điều kiện kết thúc giữ đủ `T_end_hold` | — | — | COMPLETED, giữ tới khi LKA rời REQUEST; → HWA nếu HWA ở REQUEST, không thì NONE | COMPLETED; → LKA nếu LKA ở REQUEST; → HWA nếu chỉ HWA ở REQUEST; không thì NONE | PP-SWR-032, 033, 041 |
| `driver_override` bật | Path bám vị trí xe | Ở lại HWA; path bám vị trí xe | Yêu cầu bị hủy: như dòng "rời REQUEST"; path bám vị trí xe | Như LKA | PP-SWR-036, 037, 039 |
| `driver_override` tắt | — | Path HWA mới từ vị trí xe | Không xảy ra | Không xảy ra | PP-SWR-040 |
| Tâm làn chỉ suy được từ biên ngoài làn mình | — | Ở lại HWA | → HWA nếu HWA ở REQUEST, không thì NONE | Như LKA | PP-SWR-047 |
| VehicleStateEstimate không hợp lệ | Không bắt đầu LKA, ELK | Ở lại HWA; không bắt đầu LKA, ELK | Tiếp tục path can thiệp tới khi kết thúc | Như LKA | PP-SWR-046, 144 |
| FunctionRequests quá timeout | `path_valid = false` | → NONE; `path_valid = false` | Như HWA | Như HWA | PP-SWR-145 |
| Path không hợp lệ: hết `T_coast`; IMU, tốc độ, góc lái hoặc ego-motion lỗi | `path_valid = false` | → NONE; `path_valid = false` | Như HWA | Như HWA | PP-SWR-043, 124, 142, 143 |
| Input hồi phục sau lúc path không hợp lệ | Path hợp lệ lại, từ trạng thái thật của xe; → HWA nếu HWA ở REQUEST; LKA, ELK chỉ khi có REQUEST mới | Không xảy ra | Không xảy ra | Không xảy ra | PP-SWR-044, 045 |

## 6. HWA path {#design-hwa}

| Việc | Cách làm | Liên quan |
|---|---|---|
| Bám tâm làn | Bám reference line qua ba lớp ở mục 4.1 | PP-SWR-050, 051 |
| Cua gắt hơn aysmax | Path cong ít hơn đường thật, a_y ≥ aysmax − `epsilon_ay`; bật `lateral_limit_reached` theo `delta_ay`, `T_flag`; gửi `v_max` cho khối dọc để giảm tốc trước cua | PP-SWR-005 đến 007, 151; target 008, 064 |
| Đưa xe về giữa khi vừa bật | Đoạn quintic dài `T_recenter`, vẫn ở HWA | PP-SWR-052; target 002, 053 |
| Dời tâm khi có xe lớn | Gán vật thể vào làn bằng reference line. Bắt đầu khi TTC tới lúc ngang hàng ≤ `ttc_offset_start`; trả về `t_offset_hold` sau khi đuôi xe lớn qua. Mất ObjectList thì đưa offset về 0 | PP-SWR-055, 058, 140; target 059 |
| Độ lớn offset | Công thức ngay dưới bảng (PP-ADR-008) | PP-SWR-051, 055, 056; target 057 |
| Xe khác cắt vào làn | Không phải ELK. Phần ngang dời tâm theo cùng công thức; khối dọc chọn xe đó làm mục tiêu | PP-SWR-055, 056 |
| Làn hẹp | Cùng công thức; khoảng trống nhỏ thì offset tự về 0; không đủ khoảng trống thì báo `lane_too_narrow` | PP-SWR-063 |

**Offset dời tâm, áp cho mọi bề rộng làn và bề rộng xe.**

- Khoảng trống mỗi bên khi ở tâm: s = (W_làn − W_xe) / 2, với W_xe là `vehicle_width` của VehicleConfig.
- Khoảng hở mỗi bên: từ thân xe tới vật gần nhất phía đó (xe ở làn bên, rào chắn, mép đường). Bên trống thì tới biên làn của reference line, không tới mép đường thô, để làn mở rộng không kéo xe về phía đó.
- Giới hạn offset: o_lim = max(0, min(`offset_max`, s − `dlc_offset_min`)).
- Offset: o = (khoảng hở phải − khoảng hở trái) / 2, cắt trong [−o_lim, o_lim]. Dấu của o luôn về phía khoảng hở lớn hơn (PP-SWR-056).

### 6.1 Interface với khối dọc {#acc-stub}

Ngang và dọc là hai khối, trao đổi ràng buộc (PP-ADR-001). Schema ở Interface Control Document; khối dọc chạy thử ở [Software Qualification Test Specification](report.html?doc=path-planner-software-qualification-test-specification&lang=vi#sim-acc).

- Planner gửi LateralLimits: `v_max` theo độ cong lớn nhất trong tầm nhìn và khoảng cách tới đó, để khối dọc giảm tốc trước cua.
- Path dùng v(t), a(t) của LongitudinalPlan chu kỳ trước. Mất hoặc quá timeout thì dùng tốc độ hiện tại không đổi, gia tốc 0; path vẫn hợp lệ (PP-SWR-153 đến 155).

### 6.2 Chiến lược tốc độ trong cua {#curve-strategy}

Theo R171 5.3.7.1.1.1 (tốc độ phải chỉnh theo độ cong) và 5.3.7.1.3 (chiến lược chọn tốc độ phải được mô tả). Phần khối dọc là hành vi khối dọc chạy thử (Software Qualification Test Specification 4.7); khối dọc thật phải cho hành vi tương đương.

| Pha | Bắt đầu khi | Tốc độ | Path planner | Khối dọc | Requirement |
|---|---|---|---|---|---|
| Đường thẳng, cua nhẹ | `v_max` ≥ tốc độ hiện tại | Cao | Bám tâm làn; gửi `v_max` và khoảng cách tới chỗ cong nhất mỗi chu kỳ | Theo tốc độ đặt hoặc xe trước | PP-SWR-150 đến 152 |
| Thấy cua | `v_max` < tốc độ hiện tại | Giảm | Như pha trước; path dùng v(t) của LongitudinalPlan | Giảm tốc theo đường bao, tới chỗ cong nhất với tốc độ ≤ v_max·√(1 − 0,3 / aysmax) | PP-SWR-151 đến 153 |
| Trong cua | Xe tới đoạn cong nhất | Thấp | Bám tâm làn, a_y ≤ aysmax, jerk ≤ 5 m/s³ | Giữ tốc độ dưới đường bao | PP-SWR-001, 003 |
| Chạm giới hạn | a_y cần > aysmax: thấy cua muộn hoặc giảm tốc không kịp | Giữ | Path cong ít hơn đường thật, a_y ≥ aysmax − `epsilon_ay`; bật `lateral_limit_reached`, cờ đã bật khi lốp trước đè vạch | Không tăng tốc khi cờ bật | PP-SWR-005 đến 007 |
| Ra cua | a_y cần lớn nhất < aysmax | Tăng | Tắt `lateral_limit_reached` | Tăng tốc về tốc độ đặt | Target PP-SWR-008 |

## 7. LKA và ELK path {#design-intervention}

| Việc | LKA | ELK | Liên quan |
|---|---|---|---|
| Điểm bắt đầu | Trạng thái đo được lúc kích hoạt (mục 4.2) | Như LKA | PP-SWR-031, 080 |
| Thời lượng | `T_lka`, chọn theo TLC từ khối Chức năng ADAS và giới hạn a_y | `T_elk`, ngắn hơn LKA | Target 081, 082 |
| Đích | Trong làn, DLC phía đã trôi ≥ `dlc_target_lka` | Trong làn, không vọt sang phía đối diện | PP-SWR-084, 085 |
| Siết biên | Không | Biên phía nguy hiểm siết lại để bánh xe không qua vạch phía đó | PP-SWR-086 |
| Tài xế chuyển làn có chủ đích, làn bên có xe đang vượt | — | Chỉ khi khối Chức năng ADAS yêu cầu theo quy tắc chặt; path đưa xe về làn cũ. Lốp trước đã qua vạch quá 0,3 m thì không bắt đầu | PP-SWR-089 |
| Thời lượng tối đa | 10 s | 10 s | PP-SWR-083 |
| Giới hạn | a_y ≤ 3,0; a_y thêm vào ≤ 1,5 m/s²; jerk ≤ 5 m/s³ | a_y ≤ 4,0; a_y thêm vào ≤ 3,0 m/s²; jerk ≤ 10 m/s³ | PP-SWR-110 đến 115 |

### 7.1 Kết thúc can thiệp {#design-completion}

- Sau khi đi hết thời lượng của path, planner kiểm điều kiện kết thúc (Software Requirements Specification mục 4) và độ lệch tới đích. Giữ liên tục `T_end_hold` thì báo COMPLETED (PP-SWR-032, 090).
- Sau COMPLETED, chuyển mượt sang chức năng kế tiếp theo arbitration (PP-SWR-033); không còn chức năng nào thì NONE, controller và EPS tự giảm mô-men.

## 8. Fault handling {#design-faults}

### 8.1 Lane model {#lane-faults}

| Lỗi | Cách làm | Liên quan |
|---|---|---|
| Nhiễu c0, c1 tới mức ban đêm | Ba lớp ở mục 4.1 | PP-SWR-120 |
| c0 jump 0,3–1 m | Kiểm tính nhất quán; nối path, dời tâm có giới hạn | PP-SWR-121 |
| Nhận nhầm vạch làn bên | Kiểm tính nhất quán; không dùng biên nhầm | PP-SWR-122 |
| Mất một vạch | Vạch còn lại cộng bề rộng nhớ được | PP-SWR-123 |
| Mất hai vạch làn mình | Còn biên khác đủ tin: suy tâm làn từ đó. Không còn: bám path cũ tối đa `T_coast` | PP-SWR-124, 147, 148 |
| c2 sai ở xa | Kết hợp c2 với r/v và lịch sử path | PP-SWR-125 |
| Trễ lane model | Bù theo stamp lúc chụp | PP-SWR-012, 131, 133 |

### 8.2 Input không hợp lệ {#design-invalid-input}

| Input | Cách làm | Liên quan |
|---|---|---|
| LaneModel | Như không còn biên đủ tin | PP-SWR-124 |
| ObjectList | Đưa offset của HWA về 0; ELK vẫn chạy (xét làn bên nằm ở khối Chức năng ADAS) | PP-SWR-140, 141 |
| IMU, tốc độ, góc lái, ego-motion | Không bù trễ và không nối path được: `path_valid = false` ngay | PP-SWR-142, 143 |
| VehicleStateEstimate | Không bắt đầu LKA, ELK mới; lần đang chạy tiếp tục | PP-SWR-046, 144 |
| FunctionRequests | Coi cả ba chức năng tắt | PP-SWR-145 |
| LongitudinalPlan | Tốc độ hiện tại không đổi, gia tốc 0 | PP-SWR-154, 155 |
| VehicleConfig thiếu lúc khởi động | Không gửi Trajectory | PP-SWR-146 |

### 8.3 Bậc suy giảm {#degradation}

Gom mục 8.1, 8.2 theo mức chức năng còn lại (R79 Annex 6, 3.4.3: (a) chạy với một phần hệ thống, (c) bỏ chức năng cấp cao). Mỗi bậc chỉ xuống khi điều kiện ở cột "Khi" đúng; điều kiện hết thì trở lại bậc trên.

| Bậc | Khi | Hệ thống làm gì | Chức năng còn | Tài xế | Requirement |
|---|---|---|---|---|---|
| 0 | Hai vạch làn mình đủ tin, mọi input bắt buộc hợp lệ | Tâm làn từ hai vạch | HWA, LKA, ELK | — | — |
| 1 | Mất một vạch làn mình | Vạch còn lại cộng bề rộng nhớ được | HWA; LKA, ELK ở phía còn vạch | — | PP-SWR-123 |
| 2 | Mất hai vạch làn mình, còn vạch làn bên hoặc mép đường đủ tin | Suy tâm làn từ biên đó | HWA | — | PP-SWR-147, 148 |
| 3 | Không còn biên làn đủ tin | Bám path cũ tối đa `T_coast` | Chức năng đang lái | — | PP-SWR-124 |
| 4 | Hết `T_coast`; hoặc IMU, tốc độ, góc lái, ego-motion không hợp lệ | `path_valid = false`; Lateral Controller và EPS giảm mô-men về 0 theo dốc | Không | Yêu cầu cầm lái | PP-SWR-124, 142, 143 |

## 9. Limits, continuity, feasibility {#design-limits}

| Chức năng | a_y | a_y thêm vào | Jerk | Requirement |
|---|---|---|---|---|
| HWA | ≤ 2,5 m/s² | ≤ `ay_add_max_hwa` | ≤ 5 m/s³; mục tiêu `jerk_target_hwa` | PP-SWR-001, 003; target 002, 004 |
| LKA | ≤ 3,0 m/s² | ≤ 1,5 m/s² | ≤ 5 m/s³ | PP-SWR-110, 112, 114 |
| ELK | ≤ 4,0 m/s² | ≤ 3,0 m/s² | ≤ 10 m/s³ | PP-SWR-111, 113, 115 |

- **Feasibility.** Kiểm a_y = v²·κ, jerk, `front_wheel_angle` và tốc độ quay vô lăng theo VehicleConfig. Vượt thì cắt về trong giới hạn và bật `lateral_limit_reached` (PP-SWR-005 đến 008, 116, 117).
- **Continuity.** So path mới với path cũ trên đoạn thời gian cả hai cùng mô tả, sau khi đưa path cũ về `base_link` mới bằng ego-motion, cả lúc đổi chức năng (PP-SWR-100 đến 102).
- **Thời gian tính.** Ghi mỗi chu kỳ; simulator coi là `t_budget` (PP-SWR-015; target 016).

## 10. Edge cases {#design-edge-cases}

Số thứ tự theo mục trường hợp biên của ADAS Function Specification.

| # | Tình huống | Planner làm gì | Liên quan |
|---|---|---|---|
| 1a | HWA đang chạy, ELK được yêu cầu | HWA → ELK → HWA, nối path mỗi lần chuyển | PP-SWR-030, 031, 033 |
| 1b | Xe khác cắt vào làn | Không đổi chức năng; dời tâm; khối dọc giữ khoảng cách | PP-SWR-055, 056 |
| 2 | HWA vào cua gắt hơn aysmax | Cắt path, bật `lateral_limit_reached`, gửi `v_max`; ELK được yêu cầu thì dùng giới hạn ELK | PP-SWR-005 đến 007, 151; target 008, 064 |
| 3 | Tài xế ghi đè HWA | Path bám vị trí xe; lập path mới khi tài xế buông | PP-SWR-039, 040 |
| 4 | ELK khi tài xế chuyển làn có chủ đích | Về làn cũ trong giới hạn ELK, chỉ khi có yêu cầu theo quy tắc chặt | PP-SWR-089, 111 |
| 5 | Yêu cầu bị hủy vì xi-nhan | Dừng path can thiệp, chuyển theo arbitration | PP-SWR-036, 037 |
| 6 | Trôi qua lại nhiều lần | Mỗi yêu cầu mới là một path can thiệp mới, cùng giới hạn | PP-SWR-034, 035 |
| 7 | Lane model đổi làn | Chuyển reference line, nối path | PP-SWR-061 |
| 8 | c0 jump | Nối path, dời tâm có giới hạn | PP-SWR-121 |
| 11 | Mất hai vạch làn mình giữa lúc can thiệp | Còn biên khác đủ tin: LKA, ELK về HWA hoặc NONE. Không còn biên: bám path cũ tối đa `T_coast` | PP-SWR-047, 124 |
| 13b | Tắc đường, tốc độ thấp | HWA chạy tiếp; ở 8 m/s path 3 s chỉ phủ 24 m | PP-SWR-054 |
| 14 | FunctionRequests quá timeout | Coi cả ba chức năng tắt | PP-SWR-145 |
| 16 | Tài xế bẻ lái gấp, LKA và ELK bị chặn | HWA coi như tài xế ghi đè | PP-SWR-039 |

## 11. Calibration parameters {#design-calibration}

Một bộ calibration cho mọi xe. Giá trị khởi đầu là điểm xuất phát; Software Qualification Test Specification quét trong dải và chọn bộ tốt nhất. Giới hạn lấy từ Software Requirements Specification mục 7 và từ requirement.

| Tham số | Đơn vị | Khởi đầu | Dải quét | Giới hạn | Ảnh hưởng |
|---|---|---|---|---|---|
| `conf_ego` | — | 0,6 | 0,4–0,8 | 0–1 | PP-SWR-123, 124 |
| `conf_inferred` | — | 0,8 | 0,7–0,95 | > `conf_ego` | PP-SWR-047, 147, 148 |
| `T_coast` | s | 1,0 | 0,5–1,0 | ≤ 1 s | PP-SWR-124 |
| `free_space_min` | m | 0,1 | 0–0,3 | ≥ 0 | PP-SWR-063 |
| `delta_ay` | m/s² | 0,2 | 0,1–0,4 | ≥ 0 | Target 008, 064 |
| `epsilon_ay` | m/s² | 0,2 | 0–0,5 | 0–2,5 | PP-SWR-006 |
| `T_flag` | s | 0,2 | 0,15–0,5 | > 0 | Target 008, 064 |
| `v_lat_end` | m/s | 0,1 | 0,05–0,2 | ≥ 0 | PP-SWR-032, 090 |
| `heading_end` | ° | 0,5 | 0,3–1,0 | ≥ 0 | PP-SWR-032, 090 |
| `ay_add_end` | m/s² | 0,2 | 0,1–0,3 | ≥ 0 | PP-SWR-032, 090 |
| `T_end_hold` | s | 0,5 | 0,3–1,0 | ≥ 0 | PP-SWR-032, 090 |
| `T_lka` | s | 3,0 | 2,0–4,0 | Giới hạn của PP-SWR-110, 112, 114 | Target 081, 087 |
| `T_elk` | s | 2,0 | 1,0–3,0 | Giới hạn của PP-SWR-111, 113, 115 | Target 082 |
| `dlc_target_lka` | m | 0,5 | 0–0,8 | ≥ 0 (PP-SWR-084) | Target 081, 087 |
| `T_recenter` | s | 3,5 | 2,5–5,0 | Giới hạn của PP-SWR-001, 003 | Target 002, 053 |
| `ay_add_max_hwa` | m/s² | 0,5 | 0,3–1,0 | ≤ 2,5 (PP-SWR-001) | Target 002, 053, 059 |
| `jerk_target_hwa` | m/s³ | 2,5 | 1,5–5,0 | ≤ 5 (PP-SWR-003) | Target 004 |
| `ref_rate` | m/s | 0,1 | 0,05–0,3 | ≥ 0 | Target 050; PP-SWR-120 |
| `stitch_reset` | m | 0,2 | 0,1–0,4 | ≥ 0 | Target 050; PP-SWR-100 |
| `k_jump` | σ | 3 | 2–5 | ≥ 0 | PP-SWR-121, 122 |
| `T_confirm` | s | 1,0 | 0,5–2,0 | ≥ 0 | PP-SWR-060, 061 |
| `offset_max` | m | 0,3 | 0–0,5 | ≥ 0 | PP-SWR-055; target 057 |
| `dlc_offset_min` | m | 0,3 | 0–0,5 | ≥ 0 (PP-SWR-051) | Target 057 |
| `ttc_offset_start` | s | 3,0 | 2,0–4,0 | ≥ 0 | PP-SWR-058 |
| `t_offset_hold` | s | 1,0 | 0–2,0 | ≥ 0 | Target 059 |
| `t_budget` | ms | 5 | — | < 25 (chu kỳ) | Target 016 |

Calibration parameter cấp thuật toán (bộ nhớ biên, trọng số của kỹ thuật lập path, lọc độ cong) ở Software Detailed Design mục 15.

## Appendix A. Analysis {#design-appendix}

**A.1 Sai số bù trễ, 25 m/s** (PP-ADR-002, PP-SWR-012).

| Nguồn sai | Sai lệch ngang của tham chiếu |
|---|---|
| Không bù, trong cua R = 250 m, trễ 100 ms | 0,25 m ở 25 m, 0,5 m ở 50 m |
| Bù bằng trễ danh định, jitter ±20 ms | 0,05 m ở 25 m |
| Đồng hồ lệch ±10 ms trước lần đồng bộ đầu | 0,025 m ở 25 m |
| Sau đồng bộ gPTP, ±50 µs | Không đáng kể |

**A.2 Tuổi tối đa 250 ms** (PP-ADR-003, PP-SWR-131). Ego-motion lưu 0,5 s, đủ để dời 250 ms. Bias xấu nhất 1 °/s làm sai hướng 0,0044 rad sau 250 ms, tức 0,11 m ở 25 m; bias 0,3 °/s chỉ 0,03 m. Sai vận tốc vật thể 0,3 m/s nhân 250 ms ra 0,075 m.

**A.3 Trễ bộ lọc yaw rate 50 ms** (PP-SWR-138). Sai hướng khi bù trễ camera khoảng 1 cm ở 25 m; sai độ cong khi vào clothoid R = 250 m ở 90 km/h khoảng 0,00007 1/m, dưới ngưỡng 0,0003 1/m của PP-SWR-102.

**A.4 Dead reckoning khi không có biên** (PP-ADR-009, `T_coast`). 25 m/s, bias yaw rate 0,3 °/s, nhiễu v_y σ = 0,05 m/s:

| Thời gian | Lệch do bias | Lệch do nhiễu v_y |
|---|---|---|
| 0,5 s | 0,02 m | 0,03 m |
| 1 s | 0,06 m | 0,05 m |
| 2 s | 0,25 m | 0,10 m |
| 3 s | 0,56 m | 0,15 m |

Bias 1 °/s (offset cảm biến thô Bosch SMI230): 0,22 m sau 1 s, 0,87 m sau 2 s.

**A.5 Đưa xe về giữa.** Quintic từ lệch d0 về 0: a_y lớn nhất ≈ 5,77·d0/T². Với d0 = 0,5 m và a_y thêm vào 0,5 m/s², T ≥ 2,4 s.

**A.6 Thời lượng LKA**, quintic từ lúc kích hoạt (TLC = 1,0 s) về tâm làn. Ô ghi a_y lớn nhất [m/s²] / jerk lớn nhất / jerk trung bình 0,5 s [m/s³]:

| v_lat lúc kích hoạt | T = 2 s | T = 3 s | T = 4 s |
|---|---|---|---|
| 0,2 m/s | 1,26 / 6,3 / 2,8 | 0,65 / 2,1 / 1,2 | 0,41 / 1,0 / 0,7 |
| 0,4 m/s | 1,36 / 6,6 / 2,8 | 0,78 / 2,5 / 1,5 | 0,54 / 1,3 / 0,9 |
| 0,6 m/s | 1,47 / 6,9 / 2,9 | 0,91 / 2,8 / 1,7 | 0,66 / 1,5 / 1,1 |

T = 2 s vượt jerk 5 m/s³; T = 4 s đưa xe ra gần vạch hơn (còn 0,10–0,16 m so với 0,13–0,28 m khi T = 3 s). Đây là căn cứ cho giá trị khởi đầu `T_lka` = 3 s.

## Revision history {#revision-history}

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 0.5 | 2026-11-09 | Mục 6.1: thiết kế chi tiết ACC chạy thử. Thêm nguồn ISO 15622:2018 |
| 0.6 | 2026-11-10 | Lane Model gửi ba làn và mép đường riêng; suy tâm làn từ vạch làn bên và mép đường (PP-ADR-011); offset tính theo bề rộng xe |
| 1.0 | 2026-11-10 | Refactor thành Software Architecture and Design, baseline BL1. Thêm thành phần, bảng calibration parameter, công thức offset cho mọi bề rộng làn và xe; chốt mọi ô của arbitration state; schema chuyển sang Interface Control Document; ACC chạy thử chuyển sang Software Qualification Test Specification; phép tính gom vào Appendix A; bỏ nhãn trạng thái và việc mở |
| 1.1 | 2026-11-10 | Cycle sequence dòng 5: PathStatus cũng gửi tới Lateral Controller, khớp Interface Control Document 1.1 |
| 1.2 | 2026-11-10 | Mục 4.2: planner tự tính trạng thái ngang (PP-ADR-014) |
| 1.3 | 2026-11-11 | Truy vết của `lateral_limit_reached`, `delta_ay`, `T_flag` theo SRS 1.3 |
| 1.4 | 2026-11-11 | Thêm mục 6.2 chiến lược tốc độ trong cua (R171 5.3.7.1.3) và mục 8.3 bậc suy giảm (R79 Annex 6, 3.4.3), gom từ các mục đã có |

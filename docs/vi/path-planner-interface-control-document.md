# Interface Control Document

| Mục | Nội dung |
|---|---|
| Mã tài liệu | `PP-ICD` |
| Phiên bản | 1.5 |
| Trạng thái | BL1 |
| Tác giả | thongbui |
| Người review | thongbui |
| Cập nhật | 2026-11-11 |

## 1. Purpose and scope {#icd-scope}

- **Mục đích.** Định nghĩa mọi interface của path planner: message, trường, kiểu, đơn vị, hệ toạ độ, tần số, timeout.
- **Phạm vi.** Input và output trực tiếp của planner: 8 input, 3 output.
- **Ngoài phạm vi.** Interface giữa các khối khác (camera với lane model, khối Chức năng ADAS với HMI, EPS với Lateral Controller). Cách planner dùng dữ liệu nằm ở tài liệu Software Architectural Design.

## 2. References {#icd-references}

| Tài liệu | Dùng cho |
|---|---|
| [Software Requirements Specification](report.html?doc=path-planner-software-requirements-specification&lang=vi) | Requirement về output, timeout, input không hợp lệ |
| [Software Architectural Design](report.html?doc=path-planner-software-architectural-design&lang=vi) | Planner dùng từng input thế nào |
| [ADAS Function Specification](report.html?doc=adas-function-specification&lang=vi) | Ý nghĩa của state, side, tlc trong FunctionRequests |
| Signal list nhóm Motion (`docs/reference/vehicle-signal-list.txt`) | Tín hiệu khung gầm, tần số, đơn vị (mentor) |
| Autoware `autoware_planning_msgs/Trajectory` | Định dạng Trajectory |
| AUTOSAR E2E Profile 1; SAE J1850 | Counter và CRC của khung CAN |
| IEEE 802.1AS (gPTP) | Đồng bộ đồng hồ giữa các ECU |

## 3. Interface overview {#icd-overview}

| Message | Từ → tới | Truyền | Tần số | Timeout | Tuổi tối đa | Mục |
|---|---|---|---|---|---|---|
| LaneModel | Lane Model → Planner | Pub/sub | 20 Hz | 150 ms | 250 ms | 5.1 |
| ObjectList | Perception → Planner | Pub/sub | 20 Hz | 150 ms | 250 ms | 5.2 |
| `IMU_Data`, `SAS_Steering`, `ESC_Speed` | Xe → Planner | CAN | 100, 100, 50 Hz | 30, 30, 60 ms | — | 5.3 |
| VehicleStateEstimate | State Estimator → Planner | Pub/sub | 50 Hz | 60 ms | 30 ms | 5.4 |
| EgoMotionQuery | Planner ↔ Ego-motion | Gọi hàm | Mỗi chu kỳ | — | — | 5.5 |
| FunctionRequests | Chức năng ADAS → Planner | Pub/sub | 40 Hz | 75 ms | 45 ms | 5.6 |
| LongitudinalPlan | Khối dọc → Planner | Pub/sub | 40 Hz | 75 ms | 45 ms | 5.7 |
| VehicleConfig | Cấu hình xe → Planner | Đọc lúc khởi động | — | — | — | 5.8 |
| Trajectory | Planner → Lateral Controller | Pub/sub | 40 Hz | 75 ms | — | 6.1 |
| PathStatus | Planner → Chức năng ADAS, Lateral Controller | Pub/sub | 40 Hz | 75 ms | — | 6.2 |
| LateralLimits | Planner → Khối dọc | Pub/sub | 40 Hz | 75 ms | — | 6.3 |

| Quy tắc | Giá trị | Nguồn |
|---|---|---|
| Tần số khung CAN | Theo signal list | mentor |
| Tần số planner và khối Chức năng ADAS | 40 Hz | mentor |
| Timeout nhận | 3 chu kỳ danh định của message, tức cho phép mất 2 message liên tiếp | nhóm tự thống nhất |
| Tuổi tối đa | Trễ lớn nhất giả định (Software Requirements Specification mục 6) cộng 1 chu kỳ. LaneModel, ObjectList: 250 ms (PP-SWR-131) | nhóm tự thống nhất |

## 4. Common conventions {#header}

**Header của message nội bộ.** Mọi message pub/sub có header này. PathStatus, LateralLimits, FunctionRequests không có `frame_id`.

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| `stamp_us` | uint64 [µs] | Thời điểm dữ liệu mô tả, theo đồng hồ của ECU gửi, đã đồng bộ gPTP. Khung CAN: gán lúc nhận, theo đồng hồ ECU nhận |
| `counter` | uint8 | Tăng 1 mỗi lần gửi, quay vòng 0–255 |
| `valid` | bool | Cờ hợp lệ của cả message |
| `frame_id` | uint8 enum | `BASE_LINK`: tâm trục sau, x tiến, y trái, z lên |

**Kiểu dữ liệu.**

| Loại | Quy ước |
|---|---|
| Đại lượng vật lý | float32, đơn vị SI, trừ thời gian |
| Thời gian | uint64, µs |
| Enum | uint8, mỗi giá trị là một số cố định |
| Mảng | Kích thước cố định: `lines[4]`, `road_edges[2]`, `objects[32]`, `points[31]`, `requests[3]`. Mảng không theo thứ tự cố định có trường đếm số phần tử dùng thật |

**Cách truyền.**

| Cách | Dùng cho |
|---|---|
| CAN | Tín hiệu khung gầm, có DBC, counter, CRC |
| Pub/sub trong bộ nhớ | Đường nội bộ ECU ADAS, giống middleware: có trễ, jitter, có thể mất |
| Gọi hàm | Ego-motion: trả kết quả trong cùng chu kỳ |

**Kiểm tra ở bên nhận.**

- Bên nhận ghi `rx_us`: thời điểm middleware giao message, theo đồng hồ của ECU nhận.
- Quá timeout nhận thì message không hợp lệ. Timeout tính từ `rx_us` của message mới nhất.
- Tuổi = thời điểm hiện tại trừ `stamp_us`. Quá tuổi tối đa thì message không hợp lệ.
- Khung CAN gán stamp lúc nhận, nên chỉ kiểm timeout, counter và CRC.

**Contract gọi hàm của planner.** Planner là thư viện C11 (PP-ADR-013). Bên gọi cấp vùng nhớ trạng thái; planner không cấp phát động, không đọc file, không đọc đồng hồ hệ thống.

| Hàm | Khi nào | Vào | Ra |
|---|---|---|---|
| `pp_state_size` | Trước khởi tạo | — | Số byte vùng nhớ trạng thái |
| `pp_init` | Một lần lúc khởi động | Vùng nhớ trạng thái, VehicleConfig | Kết quả khởi tạo. Sai VehicleConfig hoặc calibration ngoài giới hạn thì planner không gửi Trajectory (PP-SWR-146) |
| `pp_step` | Mỗi chu kỳ 25 ms, tại t0 | t0; với mỗi input: message mới nhất và `rx_us`, hoặc chưa nhận; hàm EgoMotionQuery | Trajectory, PathStatus, LateralLimits, mỗi output kèm cờ có gửi hay không |

Interface được định nghĩa một lần trong `interfaces/schema/` của mã nguồn. Từ đó sinh header C cho planner và kiểu Python cho simulator; cùng định nghĩa dùng được để sinh file `.msg`.

## 5. Input {#icd-input}

### 5.1 LaneModel {#lane-model}

- Vạch của ba làn (làn đang chạy, làn trái, làn phải) và mép đường hai bên, trong `base_link` tại lúc camera chụp.
- `lines[4]` luôn theo thứ tự L2, L1, R1, R2. L1, R1 là hai biên làn đang chạy; L2, R2 là vạch ngoài của làn trái và làn phải. `road_edges[2]` theo thứ tự trái, phải.
- Mỗi vạch và mép đường: y(x) = c0 + c1·x + c2·x² + c3·x³, κ ≈ 2·c2, trong đoạn tầm nhìn đã thật sự quan sát.
- Lane Model báo đúng `status` của từng vạch, không tự dựng vạch làn mình từ vạch làn bên.

| Trường | Kiểu [đơn vị] | Ý nghĩa |
|---|---|---|
| `lines[4].c0` … `c3` | float32 [m], [-], [1/m], [1/m²] | Hệ số đa thức |
| `lines[4].variance` | float32[4] | Phương sai của c0 … c3 |
| `lines[4].view_range_start`, `view_range_end` | float32 [m] | Đoạn quan sát được |
| `lines[4].confidence` | float32 [0..1] | Độ tin cậy |
| `lines[4].type` | uint8 enum { DASHED, SOLID, DOUBLE, UNKNOWN } | Loại vạch sơn |
| `lines[4].crossable` | bool | Được phép vượt, xét theo phía xe đang ở, kể cả vạch kép đứt-liền |
| `lines[4].status` | uint8 enum { MEASURED, PREDICTED, LOST } | Đo, dựng lại, mất |
| `lines[4].predicted_duration` | float32 [s] | Thời gian đã dựng lại |
| `road_edges[2].c0` … `c3`, `variance`, `view_range_start`, `view_range_end`, `confidence`, `status`, `predicted_duration` | Như `lines[4]` | Như `lines[4]` |
| `road_edges[2].type` | uint8 enum { CURB, GRASS_GRAVEL, BARRIER, GUARDRAIL, WALL, UNKNOWN } | Loại mép đường |
| `lane_width` | float32 [m] | Bề rộng làn đang chạy |
| `lane_width_source` | uint8 enum { MEASURED, REMEMBERED } | Bề rộng đo được hay nhớ được |
| `lane_change` | uint8 enum { NONE, LEFT, RIGHT } | Bật sau khi Lane Model đã đánh lại vị trí các vạch theo làn mới |

### 5.2 ObjectList {#perception}

- Phủ cả phía sau nhờ radar góc. Vị trí là tâm vật thể, trong `base_link` tại thời điểm đo.
- Vận tốc so với mặt đất, chiếu lên `base_link`. Xe ngược chiều có vx < 0. `heading` là góc của vector vận tốc.
- `id` ổn định qua các frame.

| Trường | Kiểu [đơn vị] |
|---|---|
| `num_objects` | uint8 [0..32] |
| `objects[32].id` | uint32 |
| `objects[32].x`, `y` | float32 [m] |
| `objects[32].vx`, `vy` | float32 [m/s] |
| `objects[32].heading` | float32 [rad] |
| `objects[32].length`, `width` | float32 [m] |
| `objects[32].existence_probability` | float32 [0..1] |

### 5.3 Chassis CAN {#can}

- Planner đọc yaw rate, a_x, a_y (bản đã lọc), góc và tốc độ quay vô lăng, tốc độ xe và chiều chạy. Mô-men tài xế đi tới khối Chức năng ADAS; tốc độ từng bánh, odometer đi tới Ego-motion.
- ID, vị trí byte và hệ số dưới đây là của simulator. Trên xe thật, lớp nhận đọc DBC của xe và đổi sang cùng đơn vị SI; planner không đổi.
- Bus 500 kbit/s, khung 8 byte. Tải khoảng 250 khung/s, khoảng 7 % băng thông.

| Khung | Tín hiệu | Chu kỳ |
|---|---|---|
| `IMU_Data 0x1A0` | Byte 0–1 YawRate (đã lọc) int16 × 0,01 °/s; byte 2–3 AccelX, byte 4–5 AccelY (đã lọc) int16 × 0,001 m/s² | 10 ms |
| `SAS_Steering 0x1B0` | Byte 0–1 SteeringWheelAngle int16 × 0,1 °; byte 2–3 SteeringWheelSpeed int16 × 0,1 °/s | 10 ms |
| `ESC_Speed 0x1C0` | Byte 0–1 VehicleSpeed uint16 × 0,01 km/h; byte 2 bit 0–1 Direction { FORWARD, REVERSE, STANDSTILL } | 20 ms |

| Mục | Quy ước |
|---|---|
| Byte 6 | Bit 0–3 Counter (0–15), bit 4–5 Qualifier { VALID, INIT, DEGRADED, FAULT }, bit 6–7 dự phòng |
| Byte 7 | CRC-8 SAE J1850 (đa thức 0x1D) trên byte 0–6 cộng Data ID, theo AUTOSAR E2E Profile 1 |
| Data ID | Không gửi, hai bên biết trước: IMU 0x10, góc lái 0x11, ESC 0x12 |
| Thứ tự byte | Intel (little-endian) |
| Dấu | Theo `base_link`: yaw rate, a_y, góc vô lăng dương khi sang trái |
| Đơn vị | Trên CAN theo đơn vị của xe (°, °/s, km/h); lớp nhận đổi sang SI một lần, sau khi kiểm CRC (mentor) |
| Ưu tiên | Tín hiệu nhanh hơn có ID nhỏ hơn |
| Hợp lệ | `valid` = Qualifier VALID, CRC đúng, counter hợp lệ. CRC sai hoặc counter lặp thì bỏ khung; counter nhảy thì ghi nhận mất khung |

### 5.4 VehicleStateEstimate {#state-estimator}

| Trường | Kiểu [đơn vị] | Ý nghĩa |
|---|---|---|
| `lateral_velocity` | float32 [m/s] | v_y tại tâm trục sau. Nếu ước lượng ở trọng tâm: v_y,sau = v_y,trọng tâm − r·l_r |
| `lateral_velocity_variance` | float32 [m²/s²] | Phương sai của v_y |
| `slip_angle` | float32 [rad] | β ≈ v_y / v |

Stamp là thời điểm ước lượng.

### 5.5 EgoMotionQuery {#ego-motion}

| Trường | Kiểu [đơn vị] | Ý nghĩa |
|---|---|---|
| `request.t1_us`, `request.t2_us` | uint64 [µs] | Hai thời điểm, trong 0,5 s gần nhất |
| `response.valid` | bool | Kết quả dùng được hay không (ví dụ bánh xe trượt) |
| `response.dx`, `dy` | float32 [m] | Chuyển động thật của `base_link` từ t1 tới t2, kể cả trượt ngang, trong `base_link` tại t1 |
| `response.dyaw` | float32 [rad] | Góc quay từ t1 tới t2 |

### 5.6 FunctionRequests {#function-requests}

- `requests[3]` theo thứ tự HWA, LKA, ELK. Stamp là thời điểm gửi yêu cầu.
- Planner xử lý OFF, UNAVAILABLE, FAULT như nhau; log phân biệt được.

| Trường | Kiểu [đơn vị] | Ý nghĩa |
|---|---|---|
| `requests[3].state` | uint8 enum { OFF, UNAVAILABLE, STANDBY, REQUEST, FAULT } | OFF: tài xế tắt. UNAVAILABLE: bật nhưng điều kiện chưa thoả. FAULT: lỗi |
| `requests[3].side` | uint8 enum { NONE, LEFT, RIGHT } | Phía xe đang trôi. HWA dùng NONE |
| `requests[3].tlc` | float32 [s] | TLC do khối Chức năng ADAS tính. HWA bỏ qua |
| `requests[3].elk_reason` | uint8 enum { NONE, SOLID_LINE, ROAD_EDGE, ONCOMING, OVERTAKING } | Chỉ ghi log |
| `requests[3].cancel_reason` | uint8 enum { NONE, DRIVER_OVERRIDE, INDICATOR, SPEED, LANE_QUALITY, ESC, FAULT } | Chỉ ghi log |
| `driver_override` | bool | Tài xế đang ghi đè, chung cho message |

### 5.7 LongitudinalPlan {#longitudinal-plan}

| Trường | Kiểu [đơn vị] | Ý nghĩa |
|---|---|---|
| `mode` | uint8 enum { OFF, CRUISE, FOLLOW, CURVE_LIMIT } | Chế độ của khối dọc |
| `points[31].v` | float32 [m/s] | Tốc độ dự kiến, bước 0,1 s, cùng lưới với Trajectory |
| `points[31].a` | float32 [m/s²] | Gia tốc dự kiến |
| `target_id` | uint32 | Vật thể đang bám; 0 nếu không có |

### 5.8 VehicleConfig {#vehicle-config}

- Đọc một lần lúc khởi động. Thiếu thì planner không gửi Trajectory (PP-SWR-146).
- Đây là nguồn duy nhất cho thông số xe: planner không giả định một xe cụ thể.

| Trường | Kiểu [đơn vị] | Ý nghĩa |
|---|---|---|
| `wheelbase` | float32 [m] | Chiều dài cơ sở |
| `rear_axle_to_cg` | float32 [m] | Tâm trục sau tới trọng tâm |
| `vehicle_width` | float32 [m] | Bề rộng kể cả gương, ≤ 2,5 m (QCVN 09:2015/BGTVT 2.1.1.1 b) |
| `steering_ratio` | float32 [-] | Góc vô lăng chia góc bánh trước |
| `max_wheel_angle` | float32 [rad] | Góc bánh trước tối đa |
| `max_steering_wheel_rate` | float32 [rad/s] | Tốc độ quay vô lăng tối đa |
| `actuator_delay` | float32 [s] | Trễ chấp hành danh định của EPS |

## 6. Output {#icd-output}

### 6.1 Trajectory {#trajectory}

- Theo Autoware Trajectory, trong `base_link` tại `header.stamp_us`. `stamp_us` là thời điểm path mô tả, đã bù trễ của lane model.
- 31 điểm, bước 0,1 s, phủ 0–3 s. Bên nhận nội suy tuyến tính theo thời gian giữa hai điểm.
- Bài toán phẳng: pose gồm x, y, yaw. Khi chuyển sang Pose 3D, z = 0 và chỉ quay quanh trục z.

| Trường | Kiểu [đơn vị] | Ý nghĩa |
|---|---|---|
| `points[31].time_from_start` | float32 [s] | Tính từ `header.stamp_us` |
| `points[31].pose.x`, `pose.y` | float32 [m] | Vị trí |
| `points[31].pose.yaw` | float32 [rad] | Hướng tiếp tuyến của path: hướng chuyển động của `base_link`, không phải hướng thân xe. Trong cua hai hướng lệch nhau bằng góc trượt tại trục sau |
| `points[31].longitudinal_velocity_mps` | float32 [m/s] | Theo LongitudinalPlan; thiếu thì tốc độ hiện tại (PP-SWR-153, 154) |
| `points[31].lateral_velocity_mps` | float32 [m/s] | ḋ: tốc độ ngang của path so với reference line, không phải v_y theo thân xe |
| `points[31].acceleration_mps2` | float32 [m/s²] | Theo LongitudinalPlan; thiếu thì 0 |
| `points[31].heading_rate_rps` | float32 [rad/s] | v·κ |
| `points[31].curvature` | float32 [1/m] | Độ cong |
| `points[31].front_wheel_angle_rad` | float32 [rad] | Góc bánh trước gợi ý cho feedforward |
| `points[31].rear_wheel_angle_rad` | float32 [rad] | Luôn bằng 0 |

### 6.2 PathStatus {#path-status}

- Bên nhận: khối Chức năng ADAS và Lateral Controller. Lateral Controller chỉ điều khiển khi `path_valid = true` và `active_function` khác NONE.

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| `path_valid` | bool | Path dùng được. False khi hết `T_coast` hoặc input bắt buộc không hợp lệ (PP-SWR-124, 142 đến 145) |
| `active_function` | uint8 enum { NONE, HWA, LKA, ELK } | Kết quả arbitration: chức năng đang lái. NONE khi `path_valid = false` |
| `intervention_phase` | uint8 enum { NONE, ACTIVE, COMPLETED } | Pha của lần can thiệp LKA hoặc ELK |
| `lateral_limit_reached` | bool | Path đang bị giới hạn vì a_y cần vượt giới hạn của chức năng đang lái (PP-SWR-007, 009; target 008, 064) |
| `lane_too_narrow` | bool | Khoảng trống mỗi bên nhỏ hơn `free_space_min` (PP-SWR-063) |

### 6.3 LateralLimits {#lateral-limits}

| Trường | Kiểu [đơn vị] | Ý nghĩa |
|---|---|---|
| `v_max` | float32 [m/s] | √(giới hạn a_y của chức năng đang lái / κ_max), κ_max là độ cong lớn nhất của đường tham chiếu trong tầm nhìn (PP-SWR-151) |
| `distance` | float32 [m] | Khoảng cách dọc tới điểm có κ_max (PP-SWR-152) |
| `lateral_limit_reached` | bool | Cùng giá trị với PathStatus của cùng chu kỳ (PP-SWR-009) |

## Revision history {#revision-history}

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 2026-11-10 | Refactor thành Interface Control Document, baseline BL1. Thêm bảng tổng quan; gom FunctionRequests, LongitudinalPlan, PathStatus, LateralLimits về đây; thêm `lane_too_narrow` vào PathStatus; VehicleConfig là nguồn duy nhất cho thông số xe, bề rộng ≤ 2,5 m kể cả gương; bỏ nhãn trạng thái |
| 1.1 | 2026-11-10 | PathStatus gửi thêm tới Lateral Controller, để controller không lái khi không có chức năng nào đang lái |
| 1.2 | 2026-11-10 | Bên nhận ghi `rx_us`, timeout tính từ đó; thêm contract gọi hàm của planner (`pp_state_size`, `pp_init`, `pp_step`); interface định nghĩa ở `interfaces/schema/`, sinh header C và kiểu Python |
| 1.3 | 2026-11-10 | Trajectory: `pose.yaw` là hướng tiếp tuyến của path, không phải hướng thân xe; `lateral_velocity_mps` là ḋ so với reference line |
| 1.4 | 2026-11-11 | EgoMotionQuery: `dx`, `dy` là chuyển động thật của `base_link`, kể cả trượt ngang |
| 1.5 | 2026-11-11 | PathStatus `lateral_limit_reached`: trỏ theo SRS 1.3 |

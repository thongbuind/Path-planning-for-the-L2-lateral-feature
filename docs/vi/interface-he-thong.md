# Interface và tín hiệu của Path planner

Tài liệu này ghi hợp đồng trao đổi dữ liệu giữa Path Planner và các khối trên xe. Xem [Thiết kế tính năng Path Planner](report.html?doc=thiet-ke-path-planner&lang=vi) để biết planner dùng các dữ liệu này thế nào khi chạy và khi mất tín hiệu.

## Header và quy ước chung {#header}

### Header của message nội bộ

| Trường | Yêu cầu | Kiểu | Trạng thái |
|---|---|---|---|
| stamp_us | Thời điểm mà dữ liệu mô tả, theo đồng hồ của ECU gửi (đã đồng bộ kiểu gPTP). Với khung CAN: gán lúc nhận, theo đồng hồ của ECU nhận | uint64 (µs) | đã chốt |
| counter | Tăng 1 mỗi lần gửi, quay vòng 0–255, để phát hiện mất hoặc lặp message | uint8 | đã chốt |
| valid | Cờ hợp lệ của cả message | bool | đã chốt |
| frame_id | Hệ toạ độ BASE_LINK: tâm trục sau, x tiến, y trái, z lên | uint8 enum | đã chốt |

### Kiểu dữ liệu

| Loại | Yêu cầu | Kiểu | Trạng thái |
|---|---|---|---|
| Số thực | Mọi đại lượng vật lý, trừ thời gian | float32 | đã chốt |
| Thời gian | Micro giây, số nguyên | uint64 | đã chốt |
| Enum | Mỗi giá trị là một số cố định | uint8 | đã chốt |
| Mảng | Kích thước cố định, kèm trường đếm số phần tử dùng thật | — | đã chốt |
| Kích thước mảng | lines[4], objects[32], points[31], requests[3] | — | đã chốt |

### Cách truyền

| Loại | Dùng cho | — | Trạng thái |
|---|---|---|---|
| CAN | Tín hiệu khung gầm (IMU, tốc độ, góc lái): file DBC, có counter và CRC | — | đã chốt |
| Pub/sub trong bộ nhớ | Các đường nội bộ ECU ADAS, giống middleware: có trễ, jitter, có thể mất | — | đã chốt |
| Truy vấn | Ego-motion: gọi hàm, trả kết quả trong cùng chu kỳ | — | đã chốt |

### Kiểm tra thời gian ở bên nhận

| Quy định | Trạng thái |
|---|---|
| Timeout nhận: đã bao lâu chưa nhận được message mới. Bằng 3 chu kỳ danh định, tức cho phép mất 2 message liên tiếp. | đã chốt |
| Tuổi tối đa: bây giờ trừ stamp_us của message. Bằng độ trễ lớn nhất cộng 1 chu kỳ. | đã chốt |
| Khung CAN gán stamp lúc nhận, nên chỉ có timeout nhận, cộng với counter và CRC. | đã chốt |

Khi triển khai prototype, định nghĩa interface một lần trong `src/` để sinh kiểu Python. Có thể dùng cùng định nghĩa để sinh struct C hoặc file `.msg` sau này. Các trường và quyết định thiết kế được tra ở Research.

## Tín hiệu khung gầm qua CAN {#can}

Planner đọc IMU đã lọc, tốc độ xe từ ESC và góc cùng tốc độ quay vô lăng. Camera và radar đi qua Lane Model hoặc Perception. Mô-men tài xế từ EPS đi tới khối Chức năng ADAS. Tốc độ từng bánh, odometer và bộ đếm vòng bánh dành cho Ego-motion (G4).

IMU gửi yaw rate và gia tốc dọc/ngang đã quy về `base_link`. Gia tốc phụ thuộc vị trí lắp IMU. Logger giữ cả bản thô để đo trễ bộ lọc. ESC tính tốc độ xe từ bốn bánh và gửi chiều chạy. Lớp nhận gán timestamp khi nhận CAN và đổi sang SI một lần. Planner dùng yaw rate để kiểm độ cong và dùng góc lái để ước lượng độ cong đầu của path.

### Khung DBC dự kiến

Bus CAN 500 kbit/s, mỗi khung 8 byte. Mentor cung cấp danh sách tín hiệu và chu kỳ. ID, vị trí byte và hệ số dưới đây là đề xuất để thử giả lập. Thay bằng DBC xe khi có.

| Khung | Tín hiệu | Chu kỳ |
|---|---|---|
| `IMU_Data 0x1A0` | Byte 0–1 YawRate (bản đã lọc) int16 × 0,01 °/s; byte 2–3 AccelX, byte 4–5 AccelY (bản đã lọc) int16 × 0,001 m/s² | 10 ms |
| `SAS_Steering 0x1B0` | Byte 0–1 SteeringWheelAngle int16 × 0,1 °; byte 2–3 SteeringWheelSpeed int16 × 0,1 °/s | 10 ms |
| `ESC_Speed 0x1C0` | Byte 0–1 VehicleSpeed uint16 × 0,01 km/h; byte 2 bit 0–1 Direction {FORWARD, REVERSE, STANDSTILL} | 20 ms |

### Quy ước chung của ba khung

| Mục | Quy ước | — | Trạng thái |
|---|---|---|---|
| Byte 6 | Bit 0–3 Counter (0–15), bit 4–5 Qualifier, bit 6–7 dự phòng | — | đã chốt |
| Byte 7 | CRC-8 SAE J1850 (đa thức 0x1D), tính trên byte 0–6 cộng Data ID của khung, theo kiểu E2E Profile 1 của AUTOSAR | — | đã chốt |
| Data ID | Không gửi đi, hai bên biết trước: IMU 0x10, góc lái 0x11, ESC 0x12 | — | đã chốt |
| Qualifier | Enum 2 bit dùng chung: VALID, INIT, DEGRADED, FAULT | — | đã chốt |
| Thứ tự byte | Intel (little-endian) cho mọi tín hiệu | — | đã chốt |
| Quy ước dấu | Theo base_link: yaw rate dương khi quay trái, a_y dương sang trái, góc vô lăng dương khi đánh lái sang trái | — | đã chốt |
| Đơn vị | Trên CAN giữ đúng đơn vị của xe (°, °/s, km/h). Lớp nhận đổi sang SI (rad, rad/s, m/s) một lần, ngay sau khi kiểm tra CRC. Bên trong planner chỉ dùng SI | — | đề xuất |
| Độ ưu tiên | ID nhỏ hơn được ưu tiên trên bus: tín hiệu nhanh hơn có ID nhỏ hơn | — | đã chốt |
| Tải bus | Khoảng 250 khung/s, khoảng 33 kbit/s, tức khoảng 7% của 500 kbit/s | — | đã chốt |

### Bên nhận kiểm tra

| Quy định | Trạng thái |
|---|---|
| valid ở bên nhận = Qualifier là VALID, CRC đúng và counter hợp lệ. | đã chốt |
| Counter và CRC (E2E), kiểm tra ngay lúc nhận từng khung: CRC sai thì bỏ khung; counter lặp thì bỏ; counter nhảy thì ghi nhận đã mất khung. | đã chốt |
| Chu kỳ khung: IMU 10 ms, góc lái 10 ms, tốc độ ESC 20 ms, theo signal list. | mentor |
| Timeout nhận 3 chu kỳ: IMU và góc lái 30 ms, tốc độ ESC 60 ms. Quá thời gian này thì tín hiệu không hợp lệ. | đã chốt |

Độ trễ CAN thật chưa biết. Giả định chạy thử khoảng 5 ms, chưa kể trễ bộ lọc.

## LaneModel {#lane-model}

Lane Model gửi tối đa bốn vạch trong hệ `base_link` tại lúc camera chụp. L1/R1 là hai biên của làn đang chạy, L2/R2 là hai vạch phía ngoài. Tầm nhìn là điểm đầu và cuối đoạn thật sự quan sát được. Mỗi vạch dùng y(x) = c0 + c1·x + c2·x² + c3·x³, với κ ≈ 2·c2. `crossable` xét theo phía xe đang ở, kể cả vạch kép đứt-liền. Cờ đổi làn bật sau khi đã đánh lại vị trí các vạch. Mảng `lines[4]` luôn theo thứ tự L2, L1, R1, R2.

Dùng [header chung](report.html?doc=interface-he-thong&lang=vi#header).

| Trường | Kiểu, đơn vị và quy ước | Trạng thái |
|---|---|---|
| `lines[4].c0` | float32 [m] | đề bài |
| `lines[4].c1` | float32 [-] | đề bài |
| `lines[4].c2` | float32 [1/m] | đề bài |
| `lines[4].c3` | float32 [1/m²] | đề bài |
| `lines[4].variance` | float32[4] (c0..c3) | đã chốt |
| `lines[4].view_range_start` | float32 [m] | đề bài |
| `lines[4].view_range_end` | float32 [m] | đề bài |
| `lines[4].confidence` | float32 [0..1] | đề bài |
| `lines[4].type` | uint8 enum { DASHED, SOLID, DOUBLE, ROAD_EDGE, BARRIER, UNKNOWN } | đã chốt |
| `lines[4].crossable` | bool | đã chốt |
| `lines[4].status` | uint8 enum { MEASURED, PREDICTED, LOST } | đã chốt |
| `lines[4].predicted_duration` | float32 [s] | đã chốt |
| `lane_width` | float32 [m] | đề bài |
| `lane_width_source` | uint8 enum { MEASURED, REMEMBERED } | đề bài |
| `lane_change` | uint8 enum { NONE, LEFT, RIGHT } | đã chốt |

Tần số, timeout và tuổi dữ liệu xem ở [đầu vào và bù trễ](report.html?doc=thiet-ke-path-planner&lang=vi#planner-inputs). Mức nhiễu, dựng lại vạch và chia việc giữa Lane Model với G1 nằm ở [lỗi Lane Model](report.html?doc=thiet-ke-path-planner&lang=vi#lane-faults). Các mức còn lại dùng cho mô phỏng và cần thay bằng số đo khi có log thật. Bám vệt xe trước khi kẹt xe là hướng mở rộng.

## ObjectList {#perception}

Danh sách bao phủ cả phía sau nhờ radar góc. Vị trí là tâm vật thể. Vận tốc so với mặt đất được chiếu lên `base_link` tại thời điểm đo. Xe ngược chiều có vx < 0. Hướng là góc vector vận tốc trong hệ đó. ID ổn định qua các frame. G1 gán làn từ Lane Model, dự đoán vận tốc không đổi trong tầm nhìn 2–3 s và dùng TTC để dời tâm HWA. Điều kiện an toàn làn bên của ELK thuộc khối Chức năng ADAS.

Dùng [header chung](report.html?doc=interface-he-thong&lang=vi#header).

| Trường | Kiểu, đơn vị và quy ước | Trạng thái |
|---|---|---|
| `num_objects` | uint8 [0..32] | đã chốt |
| `objects[32].id` | uint32 | đã chốt |
| `objects[32].x` | float32 [m] | đã chốt |
| `objects[32].y` | float32 [m] | đã chốt |
| `objects[32].vx` | float32 [m/s] (so với mặt đất) | đã chốt |
| `objects[32].vy` | float32 [m/s] | đã chốt |
| `objects[32].heading` | float32 [rad] | đã chốt |
| `objects[32].length` | float32 [m] | đã chốt |
| `objects[32].width` | float32 [m] | đã chốt |
| `objects[32].existence_probability` | float32 [0..1] | đã chốt |

Cùng mức trễ giả định và các ngưỡng tuổi dữ liệu như LaneModel. Xem [đầu vào planner](report.html?doc=thiet-ke-path-planner&lang=vi#planner-inputs).

## VehicleStateEstimate {#state-estimator}

Dùng [header chung](report.html?doc=interface-he-thong&lang=vi#header).

| Trường | Kiểu, đơn vị và quy ước | Trạng thái |
|---|---|---|
| `lateral_velocity` | float32 [m/s] (tại tâm trục sau) | đề bài |
| `lateral_velocity_variance` | float32 [m²/s²] | đã chốt |
| `slip_angle` | float32 [rad] | đã chốt |

G2 ước lượng vận tốc ngang tại tâm trục sau. Nếu kết quả ở trọng tâm, quy đổi v_y,sau = v_y,trọng tâm − r·l_r. Góc trượt β ≈ v_y / v. Stamp là thời điểm ước lượng. G1 dùng v_y và phương sai khi tính trạng thái đầu cho can thiệp. Timeout nhận 60 ms và tuổi tối đa 30 ms, với trễ giả định khoảng 10 ms ở 50 Hz.

## EgoMotionQuery {#ego-motion}

| Trường | Kiểu, đơn vị và quy ước | Trạng thái |
|---|---|---|
| `request.t1_us` | uint64 [µs] | đã chốt |
| `request.t2_us` | uint64 [µs] | đã chốt |
| `response.valid` | bool | đã chốt |
| `response.dx` | float32 [m] | đã chốt |
| `response.dy` | float32 [m] | đã chốt |
| `response.dyaw` | float32 [rad] | đã chốt |

Truy vấn đồng bộ trong cùng chu kỳ. G4 trả chuyển động từ t1 tới t2, biểu diễn trong `base_link` tại t1, với lịch sử ít nhất 0,5 s. Cờ hợp lệ cho biết kết quả có dùng được hay không, ví dụ khi bánh xe trượt. G1 dùng kết quả để bù trễ, nối path và giữ path cũ trong thời gian T_coast.

## VehicleConfig {#vehicle-config}

| Trường | Kiểu, đơn vị và quy ước | Trạng thái |
|---|---|---|
| `wheelbase` | float32 [m] | đã chốt |
| `rear_axle_to_cg` | float32 [m] | đã chốt |
| `vehicle_width` | float32 [m] | đã chốt |
| `steering_ratio` | float32 [-] | đã chốt |
| `max_wheel_angle` | float32 [rad] | đã chốt |
| `max_steering_wheel_rate` | float32 [rad/s] | đã chốt |
| `actuator_delay` | float32 [s] | đã chốt |

Đọc một lần khi khởi động. Khoảng cách tới trọng tâm tính từ tâm trục sau. Tỉ số lái là góc vô lăng chia góc bánh trước. Tham số chạy thử lấy từ [mô hình xe](report.html?doc=benchmark-evaluation&lang=vi#sim-vehicle) và [Controller và EPS](report.html?doc=benchmark-evaluation&lang=vi#sim-controller).

## Lateral Controller {#trajectory}

Lateral Controller nhận path và tính lệnh lái. Phạm vi G1 kết thúc tại đầu ra [Trajectory](report.html?doc=thiet-ke-path-planner&lang=vi#planner-outputs). Bộ điều khiển dùng thêm tốc độ xe, yaw rate, vận tốc ngang, gia tốc ngang, góc và mô-men lái, cùng chức năng đang hoạt động và mức can thiệp của nó. Path gửi trong `base_link` ở thời điểm stamp. Pose của bài toán phẳng chỉ cần x, y và yaw. Khi chuyển sang Pose 3D, đặt z = 0 và chỉ quay quanh trục z.

Dùng [header chung](report.html?doc=interface-he-thong&lang=vi#header).

| Trường | Kiểu, đơn vị và quy ước | Trạng thái |
|---|---|---|
| `points[31].time_from_start` | float32 [s], tính từ `header.stamp_us` | đã chốt |
| `points[31].pose.x` | float32 [m] | đã chốt |
| `points[31].pose.y` | float32 [m] | đã chốt |
| `points[31].pose.yaw` | float32 [rad] | đã chốt |
| `points[31].longitudinal_velocity_mps` | float32 [m/s] | đề xuất |
| `points[31].lateral_velocity_mps` | float32 [m/s] | đã chốt |
| `points[31].acceleration_mps2` | float32 [m/s²] | đề xuất |
| `points[31].heading_rate_rps` | float32 [rad/s] | đã chốt |
| `points[31].front_wheel_angle_rad` | float32 [rad] | đã chốt |
| `points[31].rear_wheel_angle_rad` | float32 [rad] (luôn = 0) | đã chốt |
| `points[31].curvature` | float32 [1/m] | đã chốt |

Pub/sub ở 40 Hz, timeout 75 ms ở bên nhận, trễ truyền giả định khoảng 1 ms. Quy tắc nội suy, điền tốc độ/gia tốc và điều kiện để path đưa sang controller nằm trong [thiết kế planner](report.html?doc=thiet-ke-path-planner&lang=vi#planner-outputs).

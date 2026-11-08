# Thiết kế tính năng Path Planner

Tài liệu này mô tả **cách path planner của G1 đáp ứng yêu cầu**: nhận gì, gửi gì, chạy thế nào mỗi chu kỳ, lập path cho từng chức năng ra sao, giữ giới hạn và chịu lỗi bằng cách nào. Planner phải đạt gì thì nằm ở tài liệu **Yêu cầu phần mềm Path Planner**; mỗi phần ở đây trỏ về ID yêu cầu (PP-SWR-…) mà nó đáp ứng. Các bảng ghi rõ nội dung đã chốt, đề xuất và còn cần chốt. Tài liệu này là **kế hoạch tính năng**. Cách triển khai thuật toán và việc chọn kỹ thuật lập path nằm ở tài liệu riêng **Triển khai Path Planner**, đang ở trạng thái chờ; các ghi chú thuật toán đã được chuyển sang đó.

**Bài toán theo đề bài.** Một planner duy nhất phục vụ HWA, LKA và ELK. Từ lane model, trạng thái xe (tốc độ, yaw rate, vận tốc ngang) và yêu cầu chức năng, planner tạo ở 20–50 Hz một path smooth và feasible. HWA cần path tâm làn liên tục, êm khi vào cua và khi lane model nhảy. LKA và ELK cần path can thiệp từ trạng thái đang trôi về lại trong làn, với điểm bắt đầu, ngân sách gia tốc ngang và điều kiện kết thúc khác nhau cho từng chức năng. Việc chuyển đổi giữa ba chức năng không được tạo ra step trong steering request. Planner phải chạy được trên output thật của camera, không phải lane model sạch.

**Liên hệ với các tài liệu khác.**

| Tài liệu | Quan hệ với tài liệu này |
|---|---|
| Yêu cầu phần mềm Path Planner | Planner phải đạt gì: yêu cầu có ID, nguồn, cách kiểm chứng và trạng thái. Tài liệu này nói cách làm và trỏ về ID |
| Chức năng ADAS | Quyết định **khi nào** can thiệp. Gửi sang đây `FunctionRequests`: trạng thái từng chức năng, TLC, phía, driver_override. Nhận lại `PathStatus`. Tài liệu này không lặp lại logic kích hoạt |
| Triển khai Path Planner (đang chờ) | Giữ các ghi chú thuật toán và bảng kỹ thuật ứng viên; sẽ viết khi kế hoạch trong tài liệu này xong |
| Benchmark và Evaluation | Đánh giá **công tâm** các kỹ thuật lập path trên cùng điều kiện, với chỉ số và ngưỡng định trước. Việc này **khác test chức năng**: test chức năng kiểm tra từng yêu cầu trong tài liệu Yêu cầu đạt hay trượt trong lúc phát triển; benchmark so sánh các phương án với nhau để chọn và để báo cáo |

## 1. Phạm vi

| Trong phạm vi G1 | Ngoài phạm vi G1 |
|---|---|
| Đường tham chiếu từ lane model (tâm làn, dời tâm, khi mất một vạch) | Làm sạch lane model: khối Lane Model, làm sau |
| Phân xử ELK > LKA > HWA và chuyển tiếp không nhảy bậc | Quyết định khi nào kích hoạt: khối Chức năng ADAS |
| Path HWA, path can thiệp LKA và ELK | Bên trong Lateral Controller và EPS |
| Điều kiện kết thúc can thiệp (COMPLETED); interface với khối dọc (mục 6.1) | Thiết kế ACC, AEB thật. Simulator dùng một ACC chạy thử đơn giản (mục 6.1) |
| Chịu lỗi lane model, lỗi thời gian và lỗi toàn vẹn của input | Ước lượng v_y (G2), ego-motion (G4) |

## 2. Interface

Xem [Interface và tín hiệu của G1](report.html?doc=interface-he-thong&lang=vi) để tra schema, đơn vị và quy ước truyền.

### 2.1 Input {#planner-inputs}

| Nguồn | Nội dung | Tần số, trễ, timeout | Trạng thái |
|---|---|---|---|
| Lane Model | 4 vạch L2, L1, R1, R2: c0–c3 kèm phương sai, tầm nhìn, độ tin cậy, loại vạch, được phép vượt, trạng thái (đo, dựng lại, mất); bề rộng làn; cờ chuyển làn | 20 Hz; trễ giả định 100 ± 20 ms; timeout 150 ms; tuổi tối đa 250 ms (mục 3) | đã chốt |
| Perception | Vật thể: x, y, vx, vy, hướng, dài, rộng, id, xác suất tồn tại | 20 Hz; trễ giả định 100 ± 20 ms; timeout 150 ms | đã chốt |
| CAN khung gầm | Yaw rate, a_x, a_y (bản đã lọc), tốc độ, góc và tốc độ quay vô lăng; có counter, CRC, qualifier | IMU và góc lái 100 Hz, tốc độ 50 Hz; trễ chưa biết | đã chốt |
| Ước lượng trạng thái (G2) | v_y tại tâm trục sau, góc trượt, phương sai | 50 Hz; trễ giả định khoảng 10 ms | đã chốt |
| Ego-motion (G4) | Truy vấn Δx, Δy, Δψ giữa hai thời điểm; lưu ít nhất 0,5 s | Gọi hàm trong cùng chu kỳ | đã chốt |
| Chức năng ADAS | Mỗi chức năng: state { OFF, UNAVAILABLE, STANDBY, REQUEST, FAULT }, side, tlc, elk_reason, cancel_reason; chung: driver_override | 40 Hz; trễ giả định khoảng 20 ms; timeout 75 ms; tuổi tối đa 45 ms | đã chốt |
| ACC chạy thử | LongitudinalPlan: tốc độ và gia tốc dự kiến trong 3 s (mục 6.1) | 40 Hz; timeout 75 ms | đề xuất |
| Cấu hình xe | Chiều dài cơ sở 2,9 m, tâm trục sau tới trọng tâm, bề rộng 1,9 m, tỉ số lái 15, góc bánh tối đa 0,61 rad, tốc độ vô lăng tối đa 6 rad/s, trễ chấp hành 50 ms | Đọc một lần lúc khởi động | đã chốt |

**Thông tin từ mentor.** Các dòng dưới đây mentor đã chốt và không mâu thuẫn với quyết định của nhóm.

| Thông tin | Nội dung | Trạng thái |
|---|---|---|
| Tần số khối L2 | Planner và khối Chức năng ADAS chạy 40 Hz (25 ms), trong khoảng 20–50 Hz của đề bài. Timeout của các message do khối L2 gửi bằng 3 chu kỳ, tức 75 ms | mentor |
| Tín hiệu xe | Theo signal list nhóm Motion: yaw rate, a_x, a_y 100 Hz, có bản thô và bản đã lọc; góc vô lăng và tốc độ quay vô lăng 100 Hz; tốc độ xe 50 Hz; mô-men tài xế 50 Hz (cho khối ADAS). Đơn vị trên xe là °/s, °, km/h; lớp nhận đổi sang SI một lần. Danh sách này dùng chung cho cả bốn nhóm; planner chỉ nhận phần ghi ở bảng trên | mentor |
| IMU | Coi IMU đến planner là đã sạch: bias và nhiễu được ước lượng và lọc ở phía trước. Planner đọc bản đã lọc, và vẫn phải chịu được nhiễu nhẹ còn lại. Các mức nhiễu để thử nằm ở tài liệu Benchmark và Evaluation | mentor |
| Độ trễ | Độ trễ thật của các input chưa biết. Mọi con số trễ trong tài liệu này là giả định để thiết kế. Planner phải có dư cho trễ; benchmark quét nhiều mức trễ (tài liệu Benchmark và Evaluation, mục 4.1) | mentor |

### 2.2 Output {#planner-outputs}

**Path gửi Lateral Controller**, theo Autoware Trajectory, mở rộng thêm:

| Trường | Yêu cầu | Trạng thái |
|---|---|---|
| header | stamp_us là thời điểm path mô tả, đã bù trễ camera; counter quay vòng 0–255; valid; frame_id = base_link | đã chốt |
| points[31] | Bước 0,1 s, phủ 0–3 s. Mỗi điểm: time_from_start, pose (x, y, yaw), longitudinal_velocity, lateral_velocity, acceleration, heading_rate = v·κ, curvature, front_wheel_angle (gợi ý feedforward), rear_wheel_angle = 0 | đã chốt |
| Tần số | 40 Hz. Bên nhận coi path đã cũ sau 75 ms (3 chu kỳ) | mentor |
| Tốc độ và gia tốc dọc | Theo `LongitudinalPlan` khi có dữ liệu hợp lệ; khi thiếu thì theo PP-SWR-154 (mục 6.1) | đề xuất |

**points[31] có đủ chặt chẽ không.** Kiểm tra trên dải tốc độ của HWA, LKA, ELK (10–130 km/h). Bảng này là bằng chứng Analysis cho PP-SWR-011.

| Câu hỏi | Kiểm tra | Kết luận |
|---|---|---|
| Khoảng cách giữa hai điểm | 0,1 s × 36 m/s = 3,6 m ở 130 km/h; 0,28 m ở 10 km/h | Đủ mịn: đoạn cong ngắn nhất cần mô tả (đoạn can thiệp ELK khoảng 1 s) vẫn có khoảng 10 điểm |
| Tầm nhìn | 3 s: 75 m ở 90 km/h, 8 m ở 10 km/h | Đủ cho controller nhìn trước 0,5 s. Ở tốc độ thấp tầm nhìn ngắn, nhưng dưới 10 km/h thì HWA chờ |
| Path can thiệp có nằm trọn trong 3 s không | LKA khoảng 3 s, ELK 1–3 s; đoạn HWA đưa về giữa 3–4 s | Nằm trọn hoặc gần trọn. Phần vượt quá 3 s không cần gửi, vì path được lập lại mỗi 25 ms |
| Nội suy giữa hai điểm | Controller chạy 100 Hz, nội suy giữa các điểm | **Chưa quy định cách nội suy.** Đề xuất: nội suy tuyến tính theo thời gian cho vị trí và yaw; độ cong lấy từ trường curvature, không tính lại từ vị trí |

### PathStatus {#path-status}

Gửi tới khối Chức năng ADAS qua pub/sub ở 40 Hz, timeout 75 ms, trễ giả định khoảng 1 ms. Dùng [header chung](report.html?doc=interface-he-thong&lang=vi#header), không có `frame_id`.

| Trường | Ý nghĩa | Trạng thái |
|---|---|---|
| path_valid (bool) | Path còn tin được. False khi hết T_coast, hoặc khi input bắt buộc không hợp lệ (PP-SWR-124, 142 đến 145) | đã chốt |
| active_function (uint8 enum) | { NONE, HWA, LKA, ELK }: kết quả phân xử, tức chức năng đang thật sự lái | đã chốt |
| intervention_phase (uint8 enum) | { NONE, ACTIVE, COMPLETED }: COMPLETED khi LKA hoặc ELK thoả điều kiện kết thúc (mục 7.1) | đã chốt |
| lateral_limit_reached (bool, dự kiến) | Path đang bị giới hạn vì a_y cần để bám tâm làn vượt ngân sách. Yêu cầu: PP-SWR-007 đến 009. Gửi cả khối ADAS lẫn ACC (mục 6.1) | cần chốt |

**LateralLimits gửi ACC chạy thử**, 40 Hz: v_max theo độ cong, khoảng cách tới đó, lateral_limit_reached (mục 6.1).

Định nghĩa, yêu cầu và lý do của lateral_limit_reached nằm ở tài liệu Yêu cầu phần mềm Path Planner, mục 5.1.

## 3. Chạy mỗi chu kỳ {#planner-cycle}

| Bước | Việc | Trạng thái |
|---|---|---|
| 1. Nhận | Lớp nhận đã kiểm tra từng message lúc đến: valid, counter (lặp thì bỏ, nhảy thì ghi nhận mất), CRC, qualifier, thứ tự stamp. Message có `valid = false` được coi như chưa nhận. Planner chỉ đọc message mới nhất đã qua kiểm tra | đã chốt |
| 2. Kiểm tra thời gian | Quá timeout nhận hoặc quá tuổi tối đa thì input không hợp lệ (mục 8.2; PP-SWR-131 đến 134) | đã chốt |
| 3. Bù trễ | Dời lane model từ lúc chụp tới hiện tại bằng ego-motion. Giữa hai frame camera (planner 40 Hz, camera 20 Hz), cũng dời bằng ego-motion (PP-SWR-012, 013, 128) | đã chốt |
| 4. Đường tham chiếu | Tâm làn từ hai vạch, hoặc một vạch cộng bề rộng nhớ được; kết hợp c2 của camera với r/v và lịch sử path (mục 4) | đã chốt |
| 5. Phân xử | Chọn chức năng đang lái từ FunctionRequests (mục 5) | đã chốt |
| 6. Lập path | Path HWA (mục 6) hoặc path can thiệp (mục 7), trong Frenet (s dọc tâm làn, d lệch ngang, d dương sang trái) | đã chốt |
| 7. Nối và kiểm tra liên tục | So với path chu kỳ trước, đã đưa về base_link mới; giữ ngưỡng liên tục (mục 9.2; PP-SWR-100 đến 102) | đã chốt |
| 8. Kiểm tra khả thi | a_y, jerk, góc và tốc độ lái trong giới hạn (mục 9.1, 9.3); nếu phải cắt thì bật lateral_limit_reached (PP-SWR-007) | đã chốt |
| 9. Gửi | Đổi Frenet sang base_link, lấy mẫu 31 điểm, gửi path và PathStatus. Ghi thời gian tính của chu kỳ (PP-SWR-010, 015) | đã chốt |

**Phân tích sai số bù trễ** (lý do của PP-SWR-012, 013). Bước này quyết định path mô tả làn ở đúng chỗ hay lệch so với thực tế. Lỗi ở đây đi thẳng vào vị trí xe trong làn.

| Nguồn sai | Số liệu ở 25 m/s | Sai lệch ngang của tham chiếu |
|---|---|---|
| Không bù trễ, đường thẳng | Trễ 100 ms, xe đi thêm 2,5 m | Gần 0 ngang, nhưng sai 2,5 m dọc |
| Không bù trễ, trong cua (r = 0,1 rad/s, R = 250 m) | Xe quay 0,01 rad trong 100 ms | 0,25 m ở 25 m phía trước, 0,5 m ở 50 m |
| Bù bằng trễ danh định thay vì stamp | Jitter ±20 ms, sai quay 0,002 rad | 0,05 m ở 25 m |
| Đồng hồ chưa đồng bộ | Lệch tới ±10 ms trước lần đồng bộ đầu | Khoảng 0,025 m ở 25 m |
| Sau đồng bộ gPTP | Sai ±50 µs | Không đáng kể |

Từ bảng này: (1) phải bù theo **stamp lúc chụp**, không theo trễ danh định; (2) ego-motion không hợp lệ thì path không hợp lệ ngay (PP-SWR-143); (3) benchmark có chỉ số riêng cho bù trễ: quét nhiều mức trễ và mất đồng bộ đồng hồ (tài liệu Benchmark và Evaluation, mục 4.1). Cách triển khai chi tiết chờ ở tài liệu Triển khai Path Planner (T1).

**Khi độ trễ chưa biết.** Mentor cho biết độ trễ thật chưa biết. Bù theo stamp lúc chụp không cần biết trước độ trễ, miễn là stamp đúng. Hai chỗ còn phụ thuộc vào con số trễ:

| Chỗ phụ thuộc | Vấn đề | Cách làm | Trạng thái |
|---|---|---|---|
| Tuổi tối đa của lane model và vật thể | Trước đây đặt 170 ms theo trễ giả định. Nếu trễ thật là 200 ms, mọi frame bị coi là cũ, lane model bị coi như mất | Hai ngưỡng, là tham số cấu hình (giải thích ngay dưới bảng) | đã chốt |
| Trễ của yaw rate đã lọc | Bộ lọc làm yaw rate trễ thêm một khoảng chưa biết. Stamp gán lúc nhận khung CAN không chứa phần trễ này | Ba bước ngay dưới | đề xuất |

**Đề xuất cho tuổi tối đa của lane model và vật thể** (lý do của PP-SWR-131 đến 134). Tuổi của một message là thời điểm planner đọc trừ stamp lúc chụp. Planner đọc message mới nhất, mà camera gửi mỗi 50 ms, nên tuổi lớn nhất bằng độ trễ cộng 50 ms.

| Ngưỡng | Giá trị | Khi vượt | Lý do | Trạng thái |
|---|---|---|---|---|
| Ngưỡng theo dõi | 170 ms: trễ giả định lớn nhất 120 ms cộng 50 ms | Vẫn dùng dữ liệu. Ghi log và đếm số frame vượt | Để biết trễ thật có lớn hơn giả định không, mà không làm mất chức năng | đã chốt |
| Ngưỡng loại bỏ | 250 ms: mức trễ lớn nhất benchmark quét (200 ms) cộng 50 ms | Coi input không hợp lệ: lane model xử lý như mất cả hai vạch (bám path cũ tối đa T_coast); vật thể xử lý như mất perception | Xem ba kiểm tra ngay dưới | đã chốt |
| Tuổi âm | Stamp ở tương lai quá 10 ms (bằng mức lệch đồng hồ lớn nhất trước lần đồng bộ đầu) | Coi input không hợp lệ, ghi nhận lỗi đồng hồ | Stamp sai thì bù trễ sẽ sai | đã chốt |

Ba kiểm tra cho ngưỡng 250 ms, ở 25 m/s (số tự tính):

1. **Ego-motion còn đủ lịch sử:** cần dời lane model từ lúc chụp tới bây giờ, tức tối đa 250 ms, trong khi Ego-motion lưu 0,5 s. Còn dư.
2. **Sai số khi dời bằng ego-motion vẫn nhỏ:** với IMU sạch (kịch bản chính), gần như bằng 0. Với bias xấu nhất 1 °/s (0,0175 rad/s), sai hướng sau 250 ms là 0,0044 rad, tức 0,11 m ở 25 m phía trước. Với bias 0,3 °/s, chỉ 0,03 m.
3. **Vật thể vẫn đủ đúng:** sai vận tốc σ = 0,3 m/s ([Mô hình cảm biến](report.html?doc=benchmark-evaluation&lang=vi#sim-sensors)) nhân 250 ms ra 0,075 m, nhỏ so với hộp ±2 m quanh xe mà khối ADAS dùng.

Khi có số đo trễ thật, đặt lại ngưỡng loại bỏ bằng trễ đo được lớn nhất (ví dụ phân vị 99,9 %) cộng 50 ms. Nếu giá trị đó vượt 250 ms thì phải làm lại ba kiểm tra trên.

**Trễ của yaw rate đã lọc: cách giải quyết.**

1. **Ước lượng độ nhạy trước.** Yaw rate dùng ở hai chỗ. (a) Ego-motion để bù trễ camera: sai hướng xe bằng tốc độ đổi yaw rate × trễ × thời gian bù. Ví dụ vào cua yaw rate đổi 0,1 rad/s², trễ 50 ms, bù 0,1 s: sai 0,0005 rad, tức khoảng 1 cm ở 25 m. (b) Độ cong từ r/v: ở 90 km/h, vào clothoid từ đường thẳng tới R = 250 m trong 3 s, độ cong tăng khoảng 0,0013 1/m mỗi giây; trễ 50 ms làm sai khoảng 0,00007 1/m, nhỏ hơn ngưỡng liên tục 0,0003 1/m (mục 9.2). Cả hai đều nhỏ so với lỗi do trễ camera (0,25 m ở 25 m, bảng trên). Đây là số tự tính, không có nguồn.
2. **Đo từ dữ liệu.** Xe có cả bản thô và bản đã lọc ở 100 Hz. Độ trễ của bộ lọc là độ dời thời gian làm hai bản khớp nhau nhất (tương quan chéo); có thể kiểm thêm bằng yaw rate của ground truth. Đo một lần, ghi thành tham số cấu hình; lớp nhận lùi stamp của IMU đúng bằng giá trị đó.
3. **Chứng minh có dư.** Benchmark quét trễ IMU trong khi tham số cấu hình vẫn để 0, tức cố ý sai, để cho thấy path ít bị ảnh hưởng (tài liệu Benchmark và Evaluation, mục 4.1).

### 3.1 Tuần tự trong một chu kỳ {#planner-sequence}

Một chu kỳ bắt đầu ở tick t0 của bộ lập lịch, mỗi 25 ms. Bảng ghi ai gửi gì cho ai, theo thứ tự. t_c là thời gian tính của chu kỳ.

| # | Lúc | Từ → tới | Nội dung | Yêu cầu | Trạng thái |
|---|---|---|---|---|---|
| 1 | t0 | Bộ lập lịch → Planner | Tick chu kỳ | PP-SWR-010 | đã chốt |
| 2 | t0 | Lớp nhận → Planner | Message mới nhất đã qua kiểm tra của LaneModel, ObjectList, khung CAN, VehicleStateEstimate, FunctionRequests; LongitudinalPlan của chu kỳ trước | PP-SWR-126 đến 134 | đã chốt |
| 3 | t0 | Planner → Ego-motion (G4) | Truy vấn Δx, Δy, Δψ từ stamp lúc chụp của lane model tới t0; gọi hàm trong cùng chu kỳ | PP-SWR-012, 143 | đã chốt |
| 4 | t0 | Ego-motion (G4) → Planner | Δx, Δy, Δψ | PP-SWR-012 | đã chốt |
| 5 | t0 đến t0 + t_c | Planner | Bước 3 đến 8 của bảng trên: bù trễ, đường tham chiếu, phân xử, lập path, nối, kiểm khả thi | PP-SWR-030, 100 đến 102, 110 đến 117 | đã chốt |
| 6 | t0 + t_c | Planner → Lateral Controller | Trajectory, header.stamp_us = t0 | PP-SWR-010, 011, 012 | đã chốt |
| 7 | t0 + t_c | Planner → Khối ADAS | PathStatus | PP-SWR-010 | đã chốt |
| 8 | t0 + t_c | Planner → ACC chạy thử | LateralLimits | PP-SWR-150 | đề xuất |
| 9 | sau t0 + t_c | ACC chạy thử → Planner | LongitudinalPlan; planner dùng ở chu kỳ sau, để không có vòng lặp trong cùng chu kỳ (mục 6.1) | PP-SWR-153 | đề xuất |
| 10 | mỗi 10 ms | Lateral Controller | Đọc Trajectory mới nhất ở chu kỳ 100 Hz của nó | — | đã chốt |

**Deadline.** Planner gửi xong bước 6 đến 8 trước t0 + 5 ms. 5 ms bằng thời gian tính mà simulator dùng (mục 9.3) và bằng ngưỡng ở PP-SWR-016. Trạng thái: cần chốt. Chưa quy định khi một chu kỳ tính quá deadline thì bỏ chu kỳ đó hay vẫn gửi muộn (mục 11).

### 3.2 Chuỗi trễ từ cảm biến tới bánh xe {#latency-chain}

Mọi con số trễ là giả định (mục 2.1, theo mentor). Bảng ghi mỗi đoạn trễ do khối nào gây ra và khối nào bù.

| # | Đoạn | Trễ | Xấu nhất (ms) | Gây ra | Bù | Trạng thái |
|---|---|---|---|---|---|---|
| 1 | Camera chụp → Lane Model gửi | 100 ± 20 ms (giả định) | 120 | Camera, Lane Model | Planner, theo stamp lúc chụp (PP-SWR-012) | đã chốt |
| 2 | Lane Model gửi → planner đọc | 0–50 ms: camera 20 Hz, planner đọc frame mới nhất | 50 | Nhịp camera | Planner, theo stamp lúc chụp; giữa hai frame dời bằng ego-motion (PP-SWR-128) | đã chốt |
| 3 | Planner tính và gửi | t_c ≤ 5 ms (mục 3.1) | 5 | Planner | Lateral Controller, đọc path theo header.stamp_us | đề xuất |
| 4 | Truyền Trajectory | khoảng 1 ms (giả định) | 1 | Pub/sub | Như dòng 3 | đề xuất |
| 5 | Chờ chu kỳ controller | 0–10 ms (100 Hz) | 10 | Nhịp controller | Như dòng 3 | đề xuất |
| 6 | Controller tính | chưa biết | ? | Lateral Controller | Như dòng 3 | cần chốt |
| 7 | EPS chấp hành | 50 ms (cấu hình xe) | 50 | EPS | Lateral Controller, chọn điểm path ở thời điểm hiện tại cộng trễ chấp hành | đề xuất |

**Chuỗi song song.** Hai chuỗi dưới chạy song song với chuỗi trên, không cộng vào tổng.

| # | Đoạn | Trễ | Xấu nhất (ms) | Gây ra | Bù | Trạng thái |
|---|---|---|---|---|---|---|
| 8 | Yaw rate: IMU → CAN → planner | khoảng 5 ms (giả định) cộng trễ bộ lọc chưa biết | 5 + ? | CAN, bộ lọc | Planner chịu được tới 50 ms mà không được báo (PP-SWR-138) | đề xuất |
| 9 | FunctionRequests: khối ADAS → planner | khoảng 20 ms (giả định) cộng 0–25 ms chờ chu kỳ | 45 | Pub/sub, nhịp planner | Không bù; planner phản ứng trong một chu kỳ (PP-SWR-038) | đề xuất |

**Tổng, trường hợp xấu nhất** (dòng 1 đến 7, chưa kể dòng 6): 120 + 50 + 5 + 1 + 10 + 50 = 236 ms từ lúc camera chụp tới lúc bánh xe đáp ứng. Planner bù 170 ms đầu (dòng 1, 2) bằng stamp lúc chụp. 66 ms còn lại (dòng 3 đến 7) nằm sau planner.

**Đề xuất:** Lateral Controller bù phần sau planner, bằng cách đọc điểm path theo thời gian hiện tại cộng trễ chấp hành, dựa trên header.stamp_us và time_from_start. Planner không tự dời path tới trước, để hai khối không cùng bù một khoảng trễ. Cần chốt với nhóm Lateral Controller (mục 11).

## 4. Đường tham chiếu

Phần này đáp ứng PP-SWR-050, 060 và 121 đến 125 (tài liệu Yêu cầu phần mềm Path Planner).

| Trường hợp | Cách làm | Trạng thái |
|---|---|---|
| Có hai vạch L1, R1 | Tâm làn là trung bình hai đa thức | đề bài |
| Mất một vạch | Vạch còn lại dời đi một nửa bề rộng làn đã nhớ. Cần thuật toán chi tiết cho từng trường hợp (tài liệu Triển khai Path Planner, T2) | đề bài |
| Mất cả hai vạch | Bám path chu kỳ trước (đưa về base_link mới) tối đa T_coast = 1 s, rồi báo path không hợp lệ (PP-SWR-124) | đã chốt |
| Nhiễu c0, c1 | Lane Model lọc Kalman. G1 vẫn phải có lớp dự phòng cho phần nhiễu còn lại (ngay dưới) | cần chốt |
| c0 jump | Lane Model không gửi cờ báo nhảy. G1 tự phát hiện bằng kiểm tính nhất quán của đường biên (dòng dưới), rồi nối path mới với path cũ và dời tâm có giới hạn, để thoả ngưỡng liên tục (PP-SWR-121). Cần một thuật toán thật êm (tài liệu Triển khai Path Planner, T4) | đã chốt |
| Kiểm tính nhất quán của đường biên | Lane Model không gửi cờ c0 jump: chưa thấy bằng chứng lane model thương mại có cờ này (giao thức CAN của Mobileye có hệ số đa thức, chất lượng, loại vạch, nhưng không có cờ báo nhảy). Nếu sau này có cờ, chỉ dùng làm nguồn thứ hai. Cờ chuyển làn của Lane Model cũng chỉ là nguồn thứ hai. G1 tự kiểm từng đường biên (vạch hoặc mép đường) ở hai thang thời gian. (1) Từng frame: so đường biên mới với đường biên của frame trước đã dời bằng ego-motion. Lệch c0 quá vài lần độ lệch chuẩn (từ phương sai Lane Model gửi kèm) là dấu hiệu c0 jump, hoặc nhận nhầm vạch làn bên. (2) Chậm hơn: hai biên của làn có còn song song không (hiệu c1 và c2 của hai biên), bề rộng làn có lệch khỏi bề rộng nhớ được không. Đây là dấu hiệu làn mở rộng, tách nhánh lối ra, thêm làn. Một biên không nhất quán thì cả hai thang làm chung một việc: không dùng biên đó, neo tâm làn vào biên còn lại cộng bề rộng nhớ được, và không cập nhật bề rộng nhớ được. Thay đổi thật của làn mình (làn hẹp lại, chuyển làn) được nhận khi cả hai biên cùng xác nhận qua nhiều frame. Ví dụ tự tính: mép đường mở rộng 1,5 m trên 100 m, ở 25 m/s chỉ dịch 0,02 m mỗi frame camera, dưới ngưỡng từng frame (khoảng 3 × 0,03 m); nhưng lệch góc 0,015 rad so với vạch kia, khoảng 5 lần nhiễu của hiệu c1 hai vạch (√2 × 0,002), nên thang chậm bắt được ngay | đề xuất |
| Làn mở rộng (mép đường hoặc vạch tự nhiên rộng ra: làn dừng khẩn cấp, tách nhánh, thêm làn) | Yêu cầu: PP-SWR-060. Xe tiếp tục bám làn thật theo biên ổn định. Cách phát hiện: thang chậm của dòng trên | mentor |
| c2 sai ở xa | Kết hợp có trọng số c2 của camera, độ cong từ r/v, và lịch sử path của chính G1 | đã chốt |
| Trạng thái đầu của path | Xem mục 4.2 | cần chốt |

### 4.1 Khi lane model vẫn còn nhiễu

Lane model sau khi lọc vẫn rung nhẹ: mức nhiễu ở mục 8.1 là σ_c0 = 0,03 m, σ_c1 = 0,002 ban ngày, gấp 2,5 lần ban đêm. Nếu path bám từng frame, vô lăng sẽ rung theo. G1 có ba lớp dự phòng. Không lớp nào là lọc lại cảm biến thô; chúng dùng path của chính G1 làm điểm tựa.

| Lớp | Ý chính | Ví dụ |
|---|---|---|
| 1. Bắt đầu từ path cũ | Path mới bắt đầu từ trạng thái của path chu kỳ trước (đã đưa về base_link mới), không từ lane model đo được. Nhiễu của một frame chỉ làm thay đổi phần xa của path | Một frame c0 lệch 0,05 m không làm path đổi ở điểm gần xe |
| 2. Giới hạn tốc độ thay đổi tham chiếu | Tâm làn mà path bám theo chỉ được dịch tối đa một mức mỗi giây. Ví dụ HWA: 0,1 m/s | Nhiễu ±0,03 m giữa hai frame bị nén lại thành dịch rất chậm |
| 3. Phạt jerk trong path | Path được chọn để ít jerk, nên không theo các dao động nhỏ và nhanh | Path vẫn mượt dù tham chiếu rung nhẹ |

Đổi lại, cả ba lớp làm path phản ứng chậm hơn khi làn thay đổi thật (ví dụ vào cua). Benchmark đo cả hai mặt: tốc độ quay vô lăng RMS khi có nhiễu (rung) và độ lệch khi vào cua (chậm). Yêu cầu liên quan: PP-SWR-050, 120. Cách đặt số cụ thể chờ ở tài liệu Triển khai Path Planner (T3).

### 4.2 Trạng thái đầu của path

Path nào cũng phải bắt đầu từ một trạng thái: lệch d0 so với tâm làn, góc lệch, và v_lat. Có hai câu hỏi.

**Câu hỏi 1: lấy trạng thái từ đâu.**

| Phương án | Cách làm | Được | Mất |
|---|---|---|---|
| A. Từ trạng thái đo được | Mỗi chu kỳ tính lại từ lane model, v_y, r | Luôn bám thực tế | Nhiễu đo đi thẳng vào điểm đầu path, gây rung |
| B. Từ path chu kỳ trước | Điểm đầu path mới là điểm tương ứng trên path cũ | Liên tục, không rung | Nếu xe lệch khỏi path cũ (gió, controller bám kém), path mới vẫn bắt đầu từ chỗ sai |
| C. Kết hợp | Dùng B khi xe còn gần path cũ; quay về A khi lệch quá ngưỡng (ví dụ 0,2 m) | Liên tục khi bình thường, vẫn đúng khi lệch lớn | Cần chọn ngưỡng; lúc chuyển từ B sang A có thể có bước nhỏ |

Phương án C là cách nhiều hệ thống lập quỹ đạo dùng, gọi là trajectory stitching (Apollo của Baidu có cơ chế này). **Đề xuất C.** Riêng **lúc bắt đầu can thiệp** LKA hoặc ELK, xe đang trôi thật nên phải tính lại từ trạng thái đo được (A), rồi nối với path HWA đang chạy (nếu có) để không nhảy bậc.

**Câu hỏi 2: ai tính khi dùng trạng thái đo được.**

| Phương án | Được | Mất |
|---|---|---|
| Khối ADAS và G1 dùng **chung một hàm**, cùng input | Hai bên ra cùng một con số: khối ADAS kích hoạt ở TLC 1,0 s thì G1 cũng thấy TLC 1,0 s | Hai khối phụ thuộc chung một thư viện |
| G1 tự tính theo cách riêng | Độc lập | Có thể vênh: khối ADAS thấy TLC 1,0 s, G1 lại thấy 1,3 s và chọn sai thời lượng |
| Khối ADAS gửi luôn trạng thái trong message | Một nguồn duy nhất | Thêm trễ khoảng 20 ms (giả định); G1 vẫn cần tự tính cho HWA mỗi chu kỳ |

**Đề xuất dùng chung một hàm.**

## 5. Phân xử và chuyển tiếp

Yêu cầu: PP-SWR-030 đến 040 (tài liệu Yêu cầu phần mềm Path Planner, mục 4). Bảng dưới ghi cách làm.

| Việc | Cách làm | Yêu cầu | Trạng thái |
|---|---|---|---|
| Chọn chức năng | Mỗi chu kỳ lấy chức năng ưu tiên cao nhất đang ở REQUEST. OFF, UNAVAILABLE, FAULT, STANDBY coi như không yêu cầu | PP-SWR-030 | đã chốt |
| Chuyển tiếp | Khi một chức năng nhận hoặc trả quyền, path mới bắt đầu từ trạng thái của path đang chạy | PP-SWR-031 | đã chốt |
| Kết thúc can thiệp | G1 tự quyết định lúc kết thúc (mục 7.1), không chờ khối ADAS | PP-SWR-032, 033 | đã chốt |
| Không can thiệp lặp | Nhớ chức năng vừa COMPLETED; chỉ nhận lần mới khi state đã rời REQUEST rồi quay lại | PP-SWR-034 | đã chốt |
| Yêu cầu bị hủy giữa chừng | Dừng path can thiệp. Có HWA thì lập path HWA từ trạng thái hiện tại; không có thì báo NONE | PP-SWR-036, 037 | đã chốt |
| Tài xế ghi đè | Trong lúc ghi đè, path bám theo vị trí xe hiện tại. Khi tài xế buông, lập path HWA mới từ vị trí đó | PP-SWR-039, 040 | đã chốt |
| FunctionRequests quá timeout | Coi cả ba chức năng đang tắt | PP-SWR-145 | đã chốt |

Hành vi của Lateral Controller khi active_function = NONE thuộc phạm vi Lateral Controller. G1 chỉ báo đúng trạng thái.

### 5.1 Bảng chuyển trạng thái {#arbitration-states}

Trạng thái là chức năng đang lái (active_function). Mỗi ô ghi trạng thái kế tiếp và việc planner làm; "—" là không xảy ra hoặc không đổi gì. Dấu → chỉ dùng cho lần chuyển do chính sự kiện của dòng đó gây ra, vì sơ đồ trên bản đồ đọc dấu này. Ô có **?** là chưa có yêu cầu nào quyết định: đề xuất ghi ngay trong ô, việc mở ở tài liệu Yêu cầu phần mềm Path Planner, mục 10.

Bảng suy từ PP-SWR-030 đến 040, 124, 142 đến 145, và từ cách khối ADAS hủy yêu cầu khi tài xế ghi đè: khối ADAS gửi OFF và bật driver_override trong cùng một message (tài liệu Chức năng ADAS, mục 5). Với vạch liền, khối ADAS gửi LKA trước rồi mới ELK, nên LKA và ELK có thể cùng ở REQUEST (tài liệu Chức năng ADAS, mục 6).

| Sự kiện | Đang ở NONE | Đang ở HWA | Đang ở LKA (can thiệp) | Đang ở ELK (can thiệp) | Yêu cầu |
|---|---|---|---|---|---|
| HWA vào REQUEST | → HWA; path từ trạng thái xe, đưa về giữa | — | Ở lại LKA | Ở lại ELK | PP-SWR-030, 052, 053 |
| HWA rời REQUEST | — | → NONE. **?** path_valid (đề xuất: giữ true, như PP-SWR-037) | Ở lại LKA; khi kết thúc thì về NONE, không về HWA | Ở lại ELK; khi kết thúc thì về NONE, không về HWA | PP-SWR-030, 033 |
| LKA vào REQUEST | → LKA, nếu v_y hợp lệ | → LKA, nếu v_y hợp lệ; nối path | — | Ở lại ELK | PP-SWR-030, 031, 080, 144 |
| ELK vào REQUEST | → ELK, nếu v_y hợp lệ | → ELK; nối path | → ELK; nối path | — | PP-SWR-030, 031, 144 |
| Chức năng đang can thiệp rời REQUEST, kể cả khi tài xế ghi đè | — | — | → HWA nếu HWA ở REQUEST, không thì NONE; path_valid giữ true | Như LKA. **?** Nếu LKA vẫn ở REQUEST (đề xuất: → LKA, theo PP-SWR-030) | PP-SWR-030, 036, 037 |
| Điều kiện kết thúc thoả | — | — | Báo COMPLETED; → HWA nếu HWA ở REQUEST, không thì NONE. **?** COMPLETED giữ bao lâu (đề xuất: tới khi state của LKA rời REQUEST) | Như LKA. **?** Nếu LKA vẫn ở REQUEST (như dòng trên) | PP-SWR-032, 033, 034 |
| driver_override bật | Path bám vị trí xe | Ở lại HWA; path bám vị trí xe | Yêu cầu bị hủy trong cùng message: như dòng "rời REQUEST"; path bám vị trí xe | Như LKA | PP-SWR-036, 037, 039 |
| driver_override tắt | — | Path HWA mới từ vị trí xe, về tâm làn | Không xảy ra: yêu cầu đã bị hủy | Như LKA | PP-SWR-040 |
| FunctionRequests quá timeout | path_valid = false | → NONE; path_valid = false | Như HWA | Như HWA | PP-SWR-145 |
| VehicleStateEstimate không hợp lệ | — | Ở lại HWA | → HWA nếu HWA ở REQUEST, không thì NONE (suy từ PP-SWR-144). **?** Dừng ngay giữa lần can thiệp có an toàn không | Như LKA | PP-SWR-144 |
| Path không hợp lệ: hết T_coast; IMU, tốc độ, góc lái hoặc ego-motion lỗi | path_valid = false | path_valid = false. **?** active_function (đề xuất: → NONE) | Như HWA | Như HWA | PP-SWR-124, 142, 143 |
| Input hồi phục sau lúc path không hợp lệ | **?** Đề xuất: path hợp lệ lại, lập từ trạng thái thật của xe; chọn chức năng theo PP-SWR-030; LKA, ELK chỉ khi có yêu cầu mới | Như NONE | Như NONE | Như NONE | PP-SWR-030 |

## 6. HWA: giữ tâm làn

| Việc | Cách làm và yêu cầu đáp ứng | Trạng thái |
|---|---|---|
| Bám tâm làn | Bám đường tham chiếu ở mục 4, qua ba lớp dự phòng ở mục 4.1. Yêu cầu: PP-SWR-050, 051, 100 đến 102 | đề bài |
| Giới hạn | Kiểm tra khả thi ở bước 8 của mục 3. Yêu cầu: PP-SWR-001, 003, 004 | đã chốt |
| Cua gắt hơn aysmax | Yêu cầu: PP-SWR-005 đến 008. Thiết kế: path cong ít hơn đường thật nên xe có thể ra sát vạch; planner gửi v_max cho ACC để giảm tốc trước cua (mục 6.1) | cần chốt |
| Đưa xe về giữa làn khi vừa bật HWA | Khối ADAS chỉ cho bật HWA khi xe lệch tâm tới 0,5 m. G1 đưa xe về giữa bằng một đoạn quintic 3–4 s (ví dụ ngay dưới bảng), vẫn trong HWA. Yêu cầu: PP-SWR-002, 052, 053 | đã chốt |
| Dời tâm khi có xe lớn ở làn bên | Gán vật thể vào làn bằng lane model. Dùng TTC tới lúc ngang hàng xe lớn để bắt đầu dời sớm và chậm, trả về sau khi đã vượt qua. Khi mất perception: đưa offset về 0 từ từ | đã chốt |
| Độ lớn offset | **Cân bằng khoảng hở hai bên**: offset = (khoảng hở phải − khoảng hở trái) / 2, giới hạn trong ±0,3 m. Khoảng hở mỗi bên là khoảng cách từ thân xe mình tới vật gần nhất phía đó: xe ở làn bên, rào chắn, mép đường, hoặc, nếu bên đó trống, **biên làn theo đường tham chiếu** (biên ổn định cộng bề rộng nhớ được), không phải mép đường thô. Nhờ vậy mép đường đang mở rộng không làm khoảng hở phía đó lớn lên và không kéo xe về phía chỗ rộng (mentor: path không được dịch về phía widening). Bắt đầu khi TTC tới lúc ngang hàng ≤ 3 s; trả về 1 s sau khi đuôi xe lớn đã qua. Yêu cầu: PP-SWR-002, 055 đến 059 | cần chốt |
| Cả hai bên đều có xe lớn, hoặc bên kia là rào chắn | Theo công thức trên, offset tự nhỏ lại hoặc bằng 0. Ví dụ xe tải bên trái, xe tải bên phải: hai khoảng hở bằng nhau nên offset = 0, xe đi giữa. Xe tải bên trái, rào chắn sát bên phải: offset nhỏ hoặc 0, không đẩy xe về phía rào | cần chốt |
| Làn hẹp | Đề bài nêu offset cho làn hẹp. Cùng công thức cân bằng khoảng hở: khi làn hẹp, khoảng hở hai bên nhỏ, offset chỉ dời xa phía có rào chắn hoặc mép đường | cần chốt |
| Xe khác cắt vào làn | Không phải ELK. Ngang dời tâm, ACC chọn xe đó làm mục tiêu (mục 6.1) | cần chốt |

**Ví dụ tính đoạn đưa xe về giữa** (phân tích cho PP-SWR-053). Xe lệch 0,5 m, quintic về giữa với vận tốc và gia tốc ngang bằng 0 ở cuối. a_y lớn nhất của quintic là khoảng 5,77·d0/T², nên cần T ≥ √(5,77·0,5 / 0,5) ≈ 2,4 s để a_y ≤ 0,5 m/s². Chọn T = 3–4 s để còn dư jerk.

### 6.1 Ngang và dọc: tách hai khối, trao đổi ràng buộc {#acc-stub}

Hai tình huống biên cần cả phần ngang lẫn phần dọc: **xe khác lấn hẳn vào làn mình**, và **cua gấp hơn mức HWA lái được**.

**Trên xe thật** ngang và dọc thường tách thành hai khối, mỗi khối có planner và controller riêng: ACC lo dọc (động cơ, phanh), phần giữ làn lo ngang (EPS). Hai khối **trao đổi ràng buộc** qua lại, chứ không chạy độc lập hoàn toàn. Ngay cả các planner gộp cũng thường tách khi tính: Baidu Apollo EM Planner tối ưu đường đi rồi mới tối ưu tốc độ; Werling và cộng sự (2010) sinh riêng quỹ đạo ngang và quỹ đạo dọc rồi ghép lại.

**Quyết định:** dự án làm như xe thật. G1 là khối ngang. Khối dọc là một **ACC chạy thử đơn giản** trong simulator: không phải sản phẩm của G1, cố định cho mọi phiên bản planner, giống "Controller và EPS chạy thử". G1 định nghĩa interface hai chiều.

| | Tách, có trao đổi ràng buộc (thiết kế chính) | Tách, không trao đổi (chỉ để so sánh, theo ý mentor) |
|---|---|---|
| Cua gắt (R = 200 m, 90 km/h) | Planner gửi tốc độ tối đa theo độ cong: v_max = √(aysmax / κ) = √(2,5 × 200) = 22,4 m/s (80 km/h), cùng khoảng cách tới chỗ cần đạt. ACC giảm từ 25 xuống 22,4 m/s; với 1,5 m/s² mất 1,8 s, khoảng 42 m | ACC không biết gì về cua. Planner cắt path ở aysmax, bật lateral_limit_reached, cảnh báo; xe có thể ra khỏi làn |
| Xe khác lấn vào làn | Ngang dời tâm tối đa 0,3 m. ACC chọn xe đó làm xe mục tiêu và giữ khoảng cách | Như bên trái, nhưng path ngang vẫn tính với tốc độ không đổi trong khi xe đang phanh |
| Cách chạy trong simulator | ACC chạy thử đọc LateralLimits | ACC chạy thử bỏ qua LateralLimits |
| Trạng thái | đã chốt | đã chốt |

**Interface giữa hai khối** (dự kiến):

| Message | Chiều | Nội dung | Tần số | Trạng thái |
|---|---|---|---|---|
| LateralLimits | Planner → ACC | Yêu cầu: PP-SWR-009, 150 đến 152. header; v_max [m/s]: tốc độ tối đa cho phép theo độ cong lớn nhất của đường tham chiếu trong tầm nhìn, tính bằng √(ngân sách a_y của chức năng đang lái / κ); distance [m]: khoảng cách tới điểm có độ cong đó; lateral_limit_reached | 40 Hz | đề xuất |
| LongitudinalPlan | ACC → Planner | header; mode { OFF, CRUISE, FOLLOW, CURVE_LIMIT }; points[31] gồm v [m/s] và a [m/s²], bước 0,1 s, cùng lưới với Trajectory; target_id (xe đang bám, 0 nếu không có) | 40 Hz | đề xuất |

**Ba hệ quả cho G1:**

1. **Path tính theo v(t) của ACC** (PP-SWR-153), không theo tốc độ không đổi nữa. Các trường longitudinal_velocity và acceleration của Trajectory lấy từ LongitudinalPlan.
2. **Mỗi bên dùng message của chu kỳ trước**, để không có vòng lặp trong cùng một chu kỳ. Trễ một chu kỳ 25 ms là chấp nhận được.
3. **LongitudinalPlan mất hoặc quá timeout 75 ms** (PP-SWR-154, 155): planner quay về giả định tốc độ hiện tại không đổi, gia tốc 0. Path vẫn hợp lệ, vì phần ngang không phụ thuộc bắt buộc vào phần dọc.

**ACC chạy thử, thiết kế đơn giản**

| Phần | Cách làm | Trạng thái |
|---|---|---|
| Tốc độ mục tiêu | Nhỏ nhất trong ba giá trị: tốc độ đặt của kịch bản; tốc độ giữ khoảng cách với xe trước; tốc độ cho phép theo cua (từ LateralLimits) | đề xuất |
| Bám xe trước | Xe trước là vật thể gần nhất trong làn mình (gán làn bằng lane model). Khoảng cách mong muốn = 5 m + 1,8 s × v | đề xuất |
| Giảm tốc trước cua | Bắt đầu giảm khi mức giảm tốc cần để đạt v_max trước distance vượt 1,0 m/s² | đề xuất |
| Giới hạn | Gia tốc từ −3,0 tới +1,5 m/s²; jerk ≤ 2,5 m/s³. Không có AEB: phanh khẩn cấp ngoài phạm vi | đề xuất |
| LongitudinalPlan | Dự đoán v(t) trong 3 s bằng cách giữ lệnh gia tốc hiện tại (có giới hạn jerk), không cho tốc độ âm | đề xuất |
| Mất LateralLimits | ACC chỉ dùng tốc độ đặt và xe trước | đề xuất |
| Chấp hành | Mô hình xe nhận lệnh gia tốc qua trễ 0,1 s và khâu bậc một τ = 0,3 s (động cơ và phanh) | đề xuất |

Các giới hạn gia tốc và jerk nên đối chiếu với ISO 15622 (tiêu chuẩn ACC). Tôi chưa đọc bản gốc.

## 7. LKA và ELK: path can thiệp

Yêu cầu: PP-SWR-080 đến 090 và 110 đến 115 (tài liệu Yêu cầu phần mềm Path Planner, mục 6 và 7).

| Việc | LKA | ELK | Trạng thái |
|---|---|---|---|
| Điểm bắt đầu | Trạng thái đo được lúc kích hoạt (mục 4.2), nối với path đang chạy để không nhảy bậc (PP-SWR-080, 031) | Như LKA | đề bài |
| Thời lượng | Chọn theo TLC từ khối ADAS và ngân sách a_y; mục tiêu khoảng 3 s (mục 7.1; PP-SWR-081) | Ngắn hơn, mục tiêu 1–3 s, trong ngân sách ELK (PP-SWR-082) | đề xuất |
| Đích | Về trong làn rồi trả quyền. Tâm làn, hay chỉ tới vị trí DLC ≥ 0,5 m (PP-SWR-084, 085) | Vị trí an toàn trong làn, không vọt sang phía bên kia (PP-SWR-085) | cần chốt |
| Siết biên | Không | Biên phía nguy hiểm (phía side) siết lại; path không được đưa bánh xe qua vạch phía đó (PP-SWR-086) | đề bài |
| Tài xế chuyển làn có chủ đích, làn bên có xe đang vượt | — | Chỉ khi khối ADAS gửi yêu cầu theo quy tắc chặt (tài liệu Chức năng ADAS, mục 3.2, bước 6): xe kia ngang hàng, hoặc xe sau không thể phanh kịp. Khi đó path đưa xe về lại làn cũ (R79 5.1.6.2.3.1 cho phép). Không kéo về nếu lốp trước đã sang quá 0,3 m qua vạch (PP-SWR-089) | đề xuất |
| Kéo dài tối đa | 10 s (PP-SWR-083) | 10 s (PP-SWR-083) | đã chốt |

### 7.1 Điều kiện kết thúc (COMPLETED)

**Căn cứ** cho điều kiện kết thúc ở PP-SWR-090. Không quy định nào cho con số. R79 5.6.2.2.3 và EU 2021/646 3.6.3.1 chỉ đòi không mất hỗ trợ lái đột ngột. Vì vậy tiêu chí chính là **êm lúc trả quyền**: a_y do hệ thống thêm vào phải về gần 0.

**Tính thử** bằng path quintic từ lúc LKA kích hoạt (TLC = 1,0 s) về tâm làn. Mỗi ô ghi a_y lớn nhất / jerk lớn nhất / jerk trung bình trượt 0,5 s:

| v_lat lúc kích hoạt | T = 2 s | T = 3 s | T = 4 s |
|---|---|---|---|
| 0,2 m/s | 1,26 m/s² / 6,3 / 2,8 m/s³ | 0,65 / 2,1 / 1,2 | 0,41 / 1,0 / 0,7 |
| 0,4 m/s | 1,36 / 6,6 / 2,8 | 0,78 / 2,5 / 1,5 | 0,54 / 1,3 / 0,9 |
| 0,6 m/s | 1,47 / 6,9 / 2,9 | 0,91 / 2,8 / 1,7 | 0,66 / 1,5 / 1,1 |

- T = 2 s: jerk đỉnh vượt 5 m/s³.
- T = 3 s: êm, a_y dưới 1 m/s².
- T = 4 s: êm hơn, nhưng xe đi ra gần vạch hơn (còn 0,10–0,16 m so với 0,13–0,28 m khi T = 3 s).

Vậy **T ≈ 3 s cho LKA** (lý do của PP-SWR-081).

**Cách làm.** Sau khi đã đi hết thời lượng T của path, G1 kiểm các điều kiện ở PP-SWR-090, cộng thêm lệch so với đích ≤ 0,1 m, giữ liên tục 0,5 s, rồi báo COMPLETED. Sau đó controller và EPS giảm mô-men từ từ, hoặc G1 chuyển mượt sang HWA (PP-SWR-033). Đích của LKA còn cần chốt (tài liệu Yêu cầu phần mềm Path Planner, mục 10).

## 8. Chịu lỗi

### 8.1 Lỗi lane model {#lane-faults}

Yêu cầu: PP-SWR-120 đến 125 (tài liệu Yêu cầu phần mềm Path Planner, mục 8.1). Bảng dưới ghi cách làm.

| Lỗi (mức còn lại sau Lane Model) | Cách làm | Trạng thái |
|---|---|---|
| Nhiễu c0, c1: σ_c0 = 0,03 m, σ_c1 = 0,002; gấp 2,5 lần ban đêm hoặc mưa | Ba lớp dự phòng ở mục 4.1: bắt đầu từ path cũ, giới hạn tốc độ thay đổi tham chiếu, phạt jerk | cần chốt |
| c0 jump 0,3–1 m | Nối path với path cũ, dời tâm có giới hạn, giữ ngưỡng liên tục | đã chốt |
| Mất một vạch (dựng lại, độ tin giảm về 0 trong 2 s) | Giữ tâm bằng vạch còn lại cộng bề rộng nhớ được | đã chốt |
| Mất cả hai vạch (dựng lại tối đa 1 s) | Bám path cũ tối đa T_coast = 1 s, rồi path không hợp lệ. Tổng khoảng 2 s không có vạch thật, khoảng 50 m ở 25 m/s | đã chốt |
| c2 sai tới ±0,0005 1/m ở xa | Kết hợp c2 với r/v và lịch sử path, có trọng số | đã chốt |
| Trễ giả định 100 ± 20 ms; trễ thật chưa biết | Bù trễ bằng ego-motion theo stamp lúc chụp (mục 3) | đã chốt |

**Phân tích cho T_coast = 1 s** (lý do của PP-SWR-124). Không quy định nào cho con số này. Hai nguồn liên quan chỉ cho nguyên tắc: R79 5.6.2.2.3 (không thả lái đột ngột) và R171 theo bản tóm tắt (tiếp tục hỗ trợ trong khả năng, hoặc kết thúc từ từ). Con số 1 s đến từ tính sai số dead reckoning. Khi không có vạch, xe chỉ biết mình đi đâu nhờ ego-motion, mà ego-motion tích luỹ sai. Với bias yaw rate 0,3 °/s (khoảng 0,005 rad/s, một mức lỗi bơm vào của benchmark) và nhiễu v_y σ = 0,05 m/s ([Mô hình cảm biến](report.html?doc=benchmark-evaluation&lang=vi#sim-sensors)), ở 25 m/s:

| Thời gian không có vạch | Lệch do bias yaw rate | Lệch do nhiễu v_y | Đọc số |
|---|---|---|---|
| 0,5 s | 0,02 m | 0,03 m | Không đáng kể |
| 1 s | 0,06 m | 0,05 m | Vẫn nhỏ so với khoảng trống trong làn (khoảng 0,8 m mỗi bên) |
| 2 s | 0,25 m | 0,10 m | Bắt đầu đáng kể |
| 3 s | 0,56 m | 0,15 m | Có thể chạm vạch |

Lane Model đã dựng lại vạch tối đa 1 s, G1 bám thêm 1 s, tổng khoảng 2 s và lệch khoảng 0,3 m. Ngưỡng này nên kiểm lại với nhóm G4, vì đó là chủ đề dead reckoning của họ.

Theo mentor, IMU đến planner đã sạch, nên ở kịch bản chính phần lệch do bias gần như bằng 0 và 1 s càng an toàn. Mức xấu nhất là bias chưa bù 1 °/s (offset của cảm biến thô Bosch SMI230 ở 25 °C): lệch 0,22 m sau 1 s và 0,87 m sau 2 s, tức có thể chạm vạch nếu Lane Model đã dựng lại 1 s trước đó. Benchmark chạy mức này để xem biên an toàn.

### 8.2 Input không hợp lệ hoặc quá thời gian

Yêu cầu: PP-SWR-124 và 140 đến 146 (tài liệu Yêu cầu phần mềm Path Planner, mục 8.3). Lớp nhận đánh dấu input không hợp lệ ở bước 1 và 2 của mục 3. Planner rẽ nhánh theo input bị mất:

| Input | Cách làm | Trạng thái |
|---|---|---|
| Lane Model | Như mất cả hai vạch (mục 8.1) | đã chốt |
| Perception | Chỉ ảnh hưởng phần dời tâm của HWA. Phần xét làn bên của ELK nằm ở khối ADAS | đã chốt |
| IMU, tốc độ, góc lái, ego-motion | Không bù trễ và không nối path được, nên báo path không hợp lệ ngay | đã chốt |
| Ước lượng trạng thái (v_y) | Chỉ chặn LKA và ELK | đã chốt |
| Chức năng ADAS | Coi cả ba chức năng tắt | đã chốt |
| ACC (LongitudinalPlan) | Như mục 6.1 | đề xuất |
| Cấu hình xe thiếu lúc khởi động | Không khởi động | đã chốt |

## 9. Giới hạn và ràng buộc

Yêu cầu về ngân sách a_y, jerk, liên tục và khả thi nằm ở tài liệu Yêu cầu phần mềm Path Planner, mục 5.1 và 7 (PP-SWR-001 đến 004, 100 đến 102, 110 đến 117). Phần dưới ghi cách planner giữ các giới hạn đó.

### 9.1 Ngân sách theo chức năng

Bước 8 của mục 3 kiểm a_y, a_y thêm vào và jerk của path theo ngân sách của chức năng đang lái. Path vượt ngân sách thì được cắt về trong ngân sách, và lateral_limit_reached được bật (PP-SWR-005 đến 008).

### 9.2 Liên tục giữa hai path liên tiếp

Bước 7 của mục 3 so path mới với path chu kỳ trước, trên đoạn thời gian cả hai cùng mô tả (theo header.stamp và time_from_start), sau khi đưa path cũ về base_link của path mới bằng ego-motion. Việc so áp dụng cả lúc đổi chức năng. Ngưỡng: PP-SWR-100 đến 102.

### 9.3 Khả thi

| Ràng buộc | Cách làm | Yêu cầu | Trạng thái |
|---|---|---|---|
| Góc bánh trước, tốc độ quay vô lăng | Kiểm ở bước 8 của mục 3, trên front_wheel_angle của từng điểm | PP-SWR-116, 117 | đã chốt |
| Liên hệ a_y và độ cong | a_y ≈ v²·κ; ngân sách a_y được kiểm qua độ cong của path | PP-SWR-001, 110, 111 | đề bài |
| Thời gian tính | Đo bằng đồng hồ của máy và ghi mỗi chu kỳ; giả lập coi là 5 ms | PP-SWR-015, 016 | đã chốt |

## 10. Trường hợp biên: phần của Path Planner

Cùng số thứ tự với mục 8 của tài liệu Chức năng ADAS.

| # | Tình huống | Path Planner làm gì | Yêu cầu | Trạng thái |
|---|---|---|---|---|
| 1a | HWA đang chạy, ELK được yêu cầu | Chuyển HWA sang ELK, xong quay về HWA; nối path ở mỗi lần chuyển | PP-SWR-030, 031, 033 | cần chốt |
| 1b | Xe khác cắt vào làn, xe mình ở giữa | Không đổi chức năng. Ngang dời tâm, ACC giữ khoảng cách (mục 6.1) | PP-SWR-055 đến 057 | cần chốt |
| 2 | HWA vào cua gắt hơn aysmax | Cắt path trong aysmax, bật lateral_limit_reached; nếu ELK được yêu cầu thì dùng ngân sách ELK. Gửi v_max cho ACC (mục 6.1) | PP-SWR-005 đến 008, 151 | cần chốt |
| 3 | Tài xế ghi đè HWA | Path bám vị trí hiện tại; lập path mới từ đó khi tài xế buông | PP-SWR-039, 040 | đã chốt |
| 4 | ELK khi tài xế chuyển làn có chủ đích, xe đang vượt | Path về lại làn cũ trong ngân sách ELK, chỉ khi khối ADAS gửi yêu cầu theo quy tắc chặt | PP-SWR-089, 111 | đề xuất |
| 5 | Yêu cầu bị hủy vì xi-nhan | Dừng path can thiệp; về HWA nếu có, không thì NONE | PP-SWR-036, 037 | đã chốt |
| 6 | Trôi qua lại nhiều lần | Mỗi yêu cầu mới là một path can thiệp mới | PP-SWR-034, 035 | đã chốt |
| 7 | Lane model báo chuyển làn | Đổi đường tham chiếu sang làn mới, nối path | PP-SWR-061 | đã chốt |
| 8 | c0 jump | Nối path, dời tâm có giới hạn | PP-SWR-121 | đã chốt |
| 11 | Mất cả hai vạch giữa lúc can thiệp | Bám path cũ tối đa T_coast = 1 s, rồi báo path không hợp lệ | PP-SWR-124 | đã chốt |
| 13b | Tắc đường, tốc độ thấp | HWA chạy tiếp nếu đang bật. Ở 8 m/s tầm nhìn 3 s chỉ còn 24 m; dưới 3–5 m/s mô hình xe chuyển sang kinematic | PP-SWR-054 | đề xuất |
| 14 | FunctionRequests quá timeout 75 ms | Coi cả ba chức năng tắt | PP-SWR-145 | đã chốt |
| 16 | Tài xế bẻ lái gấp, khối ADAS chặn cả LKA và ELK | HWA (nếu đang bật) coi như tài xế ghi đè | PP-SWR-039 | đề xuất |

## 11. Còn cần chốt

Việc mở của các yêu cầu (ngưỡng, đích của LKA, phân bổ biên DTLE…) nằm ở tài liệu Yêu cầu phần mềm Path Planner, mục 10. Dưới đây chỉ còn việc mở của thiết kế.

1. **Cách nội suy** giữa các điểm của path (mục 2.2).
2. **Lớp dự phòng khi lane model còn nhiễu** (mục 4.1).
3. **Trạng thái đầu của path** (mục 4.2): phương án C và dùng chung một hàm với khối ADAS.
4. **Dời tâm của HWA**: công thức cân bằng khoảng hở, lúc bắt đầu (TTC 3 s) và lúc trả về (chờ 1 s) (mục 6).
5. **Interface với khối dọc** (mục 6.1): các trường của LateralLimits và LongitudinalPlan; thông số ACC chạy thử.
6. **Điều kiện kết thúc** (mục 7.1): cách kiểm lệch so với đích.
7. **Deadline của chu kỳ** (mục 3.1): t0 + 5 ms; khi một chu kỳ tính quá deadline thì bỏ chu kỳ hay gửi muộn.
8. **Bù trễ sau planner** (mục 3.2): đề xuất Lateral Controller bù 66 ms sau planner, planner không dời path tới trước. Cần chốt với nhóm Lateral Controller.
9. **Ô chưa rõ của bảng chuyển trạng thái** (mục 5.1): sáu việc mở ở tài liệu Yêu cầu phần mềm Path Planner, mục 10.

## Nguồn

- Đề bài G1 (`G1_Path_Planning.pdf`)
- [Interface và tín hiệu của G1](report.html?doc=interface-he-thong&lang=vi) và [Thiết kế môi trường giả lập](report.html?doc=benchmark-evaluation&lang=vi#simulation-design)
- [UN Regulation No 79, OJ L 2025/3](https://upload.wikimedia.org/wikipedia/commons/f/f3/OJ_L_202500003_of_2025_-_EN_English.pdf)
- [Commission Implementing Regulation (EU) 2021/646, ELKS](https://lawplayer.com/eu/act/32021R0646)
- [Euro NCAP LSS Test Protocol v4.3](https://cdn.euroncap.com/cars/assets/euro_ncap_lss_test_protocol_v43_f2ddd5f6d6.pdf)
- [ISO 11270:2014, trang tóm tắt](https://standards.iteh.ai/catalog/standards/iso/808a3e9d-fc87-4892-85d1-6087e2ee3370/iso-11270-2014) (chưa đọc bản gốc)
- [UN Regulation No 171 (DCAS)](https://eur-lex.europa.eu/eli/reg/2025/1899/oj/eng) (chưa đọc được bản gốc)
- Werling, Ziegler, Kammel, Thrun (2010), Optimal trajectory generation for dynamic street scenarios in a Frenet frame, ICRA

# Yêu cầu phần mềm Path Planner

Tài liệu này ghi **path planner của G1 phải đạt gì**, nhìn từ bên ngoài: qua input, output và chuyển động thật của xe trong simulator. Mỗi yêu cầu là một câu, có ID, nguồn, cách kiểm chứng và trạng thái. Tài liệu không nói planner làm thế nào; phần đó nằm ở tài liệu Thiết kế tính năng Path Planner. Bên đánh giá chỉ dựa vào tài liệu này để chấm planner.

**Liên hệ với các tài liệu khác.**

| Tài liệu | Quan hệ với tài liệu này |
|---|---|
| Chức năng ADAS | Quyết định khi nào can thiệp, gửi `FunctionRequests`. Các yêu cầu ở đây bắt đầu từ lúc planner nhận yêu cầu đó |
| Thiết kế tính năng Path Planner | Cách planner đáp ứng các yêu cầu ở đây. Mỗi phần thiết kế trỏ về ID nó đáp ứng. Interface của planner định nghĩa ở mục 2 của tài liệu đó |
| Interface và tín hiệu của G1 | Schema, đơn vị, quy ước truyền của các message được nhắc ở đây |
| Benchmark và Evaluation | Kiểm chứng các yêu cầu ở đây. Mỗi mã kịch bản (S…), lỗi (F…) và quét độ trễ (Q…) trong cột Kiểm chứng nằm ở mục 3, 4 và 4.1 của tài liệu đó. Cột Yêu cầu ở các bảng đó được sinh từ cột Kiểm chứng ở đây |

## 1. Quy ước {#req-conventions}

| Mục | Quy ước |
|---|---|
| ID | `PP-SWR-nnn`. Số đánh theo khối, chừa chỗ để chèn: 001–009 giới hạn a_y của HWA; 010–029 output và chu kỳ; 030–049 phân xử; 050–079 HWA; 080–099 LKA và ELK; 100–119 giới hạn, liên tục, khả thi; 120–149 chịu lỗi; 150–169 khối dọc. ID không đánh số lại và không dùng lại. Yêu cầu bị bỏ thì giữ dòng và ghi `obsolete` |
| Câu yêu cầu | Theo mẫu EARS: "X phải …"; "Khi <sự kiện>, X phải …"; "Trong khi <trạng thái>, X phải …"; "Nếu <lỗi>, thì X phải …". `phải`, `không được`: bắt buộc. `nên`: khuyến nghị, chỉ ghi vào báo cáo, không tính đạt hay trượt |
| Kiểm chứng | Test (chạy kịch bản hoặc bơm lỗi), Analysis (phép tính), Inspection (soát tài liệu, code, log), Demonstration (chạy cho xem). Test mặc định ở vòng hở và đo trên Trajectory; đo ở vòng kín thì ghi "Test, vòng kín". Sau "Test:" là danh sách mã, cách nhau bằng dấu phẩy: kịch bản S…, lỗi F…, quét độ trễ Q… (tài liệu Benchmark và Evaluation, mục 3, 4, 4.1). Biến thể hoặc chi tiết ghi trong ngoặc ngay sau mã: S1 (a, b), F12 (Perception). Không ghi khoảng (S4 đến S8); liệt kê từng mã. Từ khoá: "mọi kịch bản", "mọi lỗi", "chưa có kịch bản". Nhiều phương pháp cách nhau bằng dấu chấm phẩy. Cột này là nguồn duy nhất của truy vết; cột Yêu cầu ở benchmark được sinh từ đây |
| Nguồn | `đề bài`, `mentor`, văn bản kèm số mục, hoặc "nhóm" khi là quyết định của nhóm (lý do ghi ở phần Lý do) |
| Trạng thái | `đề xuất`, `cần chốt`, `đã chốt` |

## 2. Định nghĩa {#req-definitions}

| Đại lượng | Định nghĩa | Trạng thái |
|---|---|---|
| Chu kỳ | 25 ms, chu kỳ của planner | mentor |
| Chức năng đang lái | Giá trị `active_function` trong PathStatus. "HWA đang lái" nghĩa là `active_function = HWA` | đã chốt |
| Lệch ngang của path | Khoảng cách ngang lớn nhất giữa path và tâm làn thật, đo tại cùng vị trí dọc, trên đoạn 0–1 s của path. Yêu cầu nêu đoạn khác thì đo trên đoạn đó | đề xuất |
| a_y của path | v²·κ tại từng điểm của Trajectory, với v là longitudinal_velocity và κ là curvature của điểm đó | đề xuất |
| a_y cần | v²·κ của tâm làn thật tại điểm tương ứng trên path, với v như trên | đề xuất |
| a_y cần lớn nhất | Giá trị lớn nhất của a_y cần trên đoạn path phủ (0–3 s), chỉ xét phần nằm trong tầm nhìn của lane model | đề xuất |
| a_y thêm vào | a_y của path trừ a_y cần, tại cùng một điểm | đề xuất |
| Jerk ngang của path | Đạo hàm theo thời gian của a_y của path, lấy trung bình trượt 0,5 s | đã chốt |
| Hai path liên tiếp | So trên đoạn thời gian cả hai cùng mô tả (theo header.stamp_us và time_from_start), sau khi đưa path cũ về base_link của path mới bằng chuyển động thật của xe | đề xuất |
| DLC | Như ở tài liệu Chức năng ADAS, mục 3, nhưng tính trên làn thật và vị trí thật của xe trong simulator | đề xuất |
| DTLE | Khoảng cách từ mép ngoài lốp tới mép trong của vạch, nhỏ nhất trong một lần can thiệp; âm là đã vượt vạch (Euro NCAP) | đã chốt |
| Xe lớn | Vật thể ở làn bên kề có bề rộng ≥ 2,3 m (xe tải, xe buýt) | đề xuất |
| δ | Dung sai quanh aysmax dùng cho cờ lateral_limit_reached | cần chốt |
| ε | Mức a_y của path được phép thấp hơn aysmax khi a_y cần vượt aysmax | cần chốt |
| T_flag | Thời gian tối đa từ lúc a_y cần lớn nhất qua ngưỡng tới lúc cờ lateral_limit_reached đổi giá trị | cần chốt |

**Lý do**

- **Lệch ngang của path, đoạn 0–1 s.** Controller nhìn trước khoảng 0,5 s (tài liệu Thiết kế, mục 2.2), nên phần gần quyết định xe đi đâu. Phần xa (2–3 s) chỉ đo ở yêu cầu về độ cong ước lượng sai.
- **Hai path liên tiếp, đo bằng chuyển động thật.** Planner tự dùng ego-motion để so (tài liệu Thiết kế, mục 9.2). Bên đánh giá dùng chuyển động thật để sai số của ego-motion cũng bị tính.
- **Xe lớn ≥ 2,3 m.** Xe con phổ biến rộng dưới 2,0 m; xe tải và xe buýt khoảng 2,5 m (kịch bản S3 dùng 2,5 m). 2,3 m nằm giữa hai nhóm. Chưa có văn bản nào cho số này.

## 3. Output và chu kỳ {#req-output}

| ID | Yêu cầu | Kiểm chứng | Nguồn | Trạng thái |
|---|---|---|---|---|
| PP-SWR-010 | Planner phải gửi Trajectory và PathStatus mỗi chu kỳ | Test: mọi kịch bản | mentor | đã chốt |
| PP-SWR-011 | Trajectory phải theo định dạng ở tài liệu Thiết kế, mục 2.2: 31 điểm, bước 0,1 s, phủ 0–3 s, frame_id = base_link | Inspection; Analysis: bảng "points[31] có đủ chặt chẽ không" ở tài liệu Thiết kế, mục 2.2 | nhóm | đã chốt |
| PP-SWR-012 | header.stamp_us của Trajectory phải là thời điểm mà path mô tả, đã bù trễ của lane model | Inspection; Test: Q1 | nhóm | đã chốt |
| PP-SWR-013 | Khi trễ camera trong khoảng 0–200 ms, kèm jitter ±20 ms, lệch ngang của path phải không lớn hơn ca trễ 0 quá 0,05 m | Test: Q1 | nhóm | đề xuất |
| PP-SWR-014 | header.counter phải tăng 1 sau mỗi message, quay vòng 0–255 | Inspection; Test: mọi kịch bản | nhóm | đã chốt |
| PP-SWR-015 | Planner phải ghi thời gian tính của từng chu kỳ | Inspection | nhóm | đã chốt |
| PP-SWR-016 | Phân vị 99 % của thời gian tính mỗi chu kỳ, trên máy phát triển, phải ≤ 5 ms | Test: mọi kịch bản | nhóm | cần chốt |

**Lý do**

- **PP-SWR-010.** Mentor chốt planner chạy 40 Hz, trong khoảng 20–50 Hz của đề bài.
- **PP-SWR-012, 013.** Bù theo stamp lúc chụp thì sai số còn lại chỉ đến từ ego-motion. Phân tích ở tài liệu Thiết kế, mục 3: bù bằng trễ danh định thay vì stamp làm sai khoảng 0,05 m ở 25 m. Yêu cầu 013 đòi planner không kém hơn mức đó trên cả dải trễ benchmark quét, trừ mức 300 ms (đã quá ngưỡng loại bỏ ở PP-SWR-131).
- **PP-SWR-016.** Chu kỳ là 25 ms. Simulator coi thời gian tính là 5 ms. Python trên laptop chỉ dùng để so sánh giữa các kỹ thuật, không khẳng định chạy được trên ECU.

## 4. Phân xử và chuyển tiếp {#req-arbitration}

| ID | Yêu cầu | Kiểm chứng | Nguồn | Trạng thái |
|---|---|---|---|---|
| PP-SWR-030 | Planner phải chọn chức năng đang lái theo thứ tự ELK > LKA > HWA, chỉ xét chức năng có state = REQUEST | Test: S9 (a) | nhóm | đã chốt |
| PP-SWR-031 | Khi chức năng đang lái đổi, path phải thoả PP-SWR-100 đến 102 | Test: S9, S8c (d) | đề bài | đã chốt |
| PP-SWR-032 | Khi LKA hoặc ELK thoả điều kiện kết thúc ở PP-SWR-090, planner phải đặt intervention_phase = COMPLETED | Test: S4, S5 | nhóm | đã chốt |
| PP-SWR-033 | Sau COMPLETED, nếu HWA ở REQUEST thì planner phải chuyển chức năng đang lái sang HWA, nếu không thì sang NONE | Test: S9 (b) | nhóm | đã chốt |
| PP-SWR-034 | Nếu chức năng vừa COMPLETED vẫn giữ REQUEST, thì planner không được bắt đầu lần can thiệp mới cho chức năng đó cho tới khi state rời REQUEST rồi quay lại | Test: S16 (a, b) | nhóm | đã chốt |
| PP-SWR-035 | Mỗi lần can thiệp mới của LKA hoặc ELK phải được lập với cùng giới hạn như lần đầu, không phụ thuộc số lần đã can thiệp trước đó | Test: S16 (c, d, e) | nhóm | đã chốt |
| PP-SWR-036 | Khi chức năng đang can thiệp rời REQUEST giữa chừng và HWA ở REQUEST, planner phải dừng path can thiệp và chuyển sang HWA từ trạng thái hiện tại | Test: S9 (d), S8c (d) | nhóm | đã chốt |
| PP-SWR-037 | Khi chức năng đang can thiệp rời REQUEST giữa chừng và HWA không ở REQUEST, planner phải đặt active_function = NONE và giữ path_valid = true | Test: S9 (d), S8c (d) | nhóm | đã chốt |
| PP-SWR-038 | Planner phải phản ánh thay đổi của FunctionRequests vào output trong không quá một chu kỳ kể từ lúc nhận message | Test: S9, Q3 | nhóm | đề xuất |
| PP-SWR-039 | Trong khi driver_override = true, điểm đầu của path phải trùng vị trí ngang hiện tại của xe, lệch ≤ 0,05 m | Test: S9 (c), S17 | nhóm | đề xuất |
| PP-SWR-040 | Khi driver_override chuyển về false trong lúc HWA ở REQUEST, path HWA phải bắt đầu từ vị trí xe lúc đó và đưa xe về tâm làn trong giới hạn PP-SWR-002 | Test: S9 (c), S17 | nhóm | đã chốt |

**Lý do**

- **PP-SWR-031.** Đề bài: việc chuyển giữa ba chức năng không được tạo step trong steering request.
- **PP-SWR-034.** Tránh can thiệp lặp khi khối ADAS chưa kịp hạ yêu cầu sau khi xe đã về trong làn.
- **PP-SWR-037.** Khi không chức năng nào lái, Lateral Controller và EPS giảm mô-men từ từ. Path vẫn hợp lệ để bên nhận có điểm tựa trong lúc giảm. Hành vi của controller lúc đó thuộc phạm vi Lateral Controller.
- **PP-SWR-038.** Một chu kỳ là mức benchmark đang dùng cho phản ứng với input quá timeout (tài liệu Benchmark và Evaluation, mục 5.5). Dùng cùng mức cho thay đổi yêu cầu.
- **PP-SWR-039.** Không kéo ngược tài xế. 0,05 m bằng ngưỡng lệch ngang giữa hai path liên tiếp (PP-SWR-100). Hành vi đã chốt; con số là đề xuất.

## 5. HWA {#req-hwa}

### 5.1 Giới hạn a_y và lateral_limit_reached {#req-hwa-lateral-limit}

| ID | Yêu cầu | Kiểm chứng | Nguồn | Trạng thái |
|---|---|---|---|---|
| PP-SWR-001 | Trong khi HWA đang lái, a_y của path phải ≤ aysmax = 2,5 m/s² tại mọi điểm | Test: S1, S1b, S12 (a) | R79 5.6.2.1.3 | đã chốt |
| PP-SWR-002 | Trong khi HWA đưa xe về giữa làn hoặc dời tâm, a_y thêm vào phải ≤ 0,5 m/s² tại mọi điểm | Test: S2, S3 | nhóm | đã chốt |
| PP-SWR-003 | Trong khi HWA đang lái, jerk ngang của path phải ≤ 5 m/s³ | Test: S1 | R79 5.6.2.1.3 c | đã chốt |
| PP-SWR-004 | Trong khi HWA đang lái, jerk ngang của path nên ≤ 2,5 m/s³ | Test: S1 | nhóm | đã chốt |
| PP-SWR-005 | Nếu a_y cần lớn nhất > aysmax trong khi HWA đang lái, thì planner phải giữ path_valid = true và active_function = HWA, trừ khi phân xử chuyển quyền sang LKA hoặc ELK | Test: S1b | R79 5.6.2.2.3 | cần chốt |
| PP-SWR-006 | Nếu a_y cần > aysmax tại một điểm của path trong khi HWA đang lái, thì a_y của path tại điểm đó phải ≥ aysmax − ε | Test: S1b | R79 5.6.2.2.3 | cần chốt |
| PP-SWR-007 | Khi a_y cần lớn nhất > aysmax + δ, planner phải đặt lateral_limit_reached = true trong thời gian T_flag | Test: S1b | nhóm | cần chốt |
| PP-SWR-008 | Khi a_y cần lớn nhất < aysmax − δ, planner phải đặt lateral_limit_reached = false trong thời gian T_flag | Test: S1 (a, b, d, e) | nhóm | cần chốt |
| PP-SWR-009 | Planner phải gửi cùng một giá trị lateral_limit_reached trong PathStatus và LateralLimits của cùng chu kỳ | Inspection; Test: S14 | nhóm | đề xuất |

**Lý do**

- **PP-SWR-001.** R79 5.6.2.1.3: aysmax của B1 tối đa 3 m/s² với xe M1. Nhóm chọn 2,5 m/s², thấp hơn mức tối đa 0,5 m/s². R79 còn cho vượt aysmax 0,3 m/s², hoặc 40 % trong tối đa 2 s (xem mục 10).
- **PP-SWR-002.** Kiểm tra bằng tính toán ở tài liệu Chức năng ADAS, mục 6.1.
- **PP-SWR-003, 004.** R79 5.6.2.1.3 c, với B1, cho 5 m/s³. Mức 2,5 m/s³ là mục tiêu tiện nghi của nhóm, không có trong quy định, nên chỉ ở mức "nên".
- **PP-SWR-005, 006.** R79 5.6.2.2.3: khi chạm giới hạn, hệ thống không được thả lái đột ngột và phải hỗ trợ trong khả năng.
- **PP-SWR-007, 008.** Chỉ planner biết path đang bị giới hạn. Khối ADAS dùng cờ này để cảnh báo tài xế khi lốp bắt đầu đè vạch (R79 5.6.2.2.3; tài liệu Chức năng ADAS, mục 7). Planner chỉ ước lượng được độ cong qua camera, nên ước lượng của nó lệch so với a_y cần. Không có dải ± δ thì cờ bật tắt liên tục khi a_y cần ở gần aysmax. Trong dải này, cờ mang giá trị nào cũng đạt.
- **PP-SWR-009.** ACC dùng cờ cùng với v_max để giảm tốc trước cua (tài liệu Thiết kế, mục 6.1). Khi ACC đã giảm đủ, a_y cần lớn nhất giảm và cờ tắt theo PP-SWR-008.

**Ví dụ (tham khảo).** Xe chạy 90 km/h (25 m/s) vào cua R = 200 m. a_y cần = 25² / 200 = 3,1 m/s², lớn hơn aysmax = 2,5 m/s², nên path phải cong ít hơn đường thật. Phần a_y thiếu là 0,6 m/s². Xe lệch ra phía ngoài cua khoảng ½ · 0,6 · 1² = 0,3 m sau 1 s và 1,2 m sau 2 s, tức ra khỏi làn. Nếu ACC giảm tốc xuống v_max = √(2,5 × 200) = 22,4 m/s thì a_y cần còn 2,5 m/s², đúng bằng aysmax.

### 5.2 Bám tâm làn và đưa về giữa {#req-hwa-centering}

| ID | Yêu cầu | Kiểm chứng | Nguồn | Trạng thái |
|---|---|---|---|---|
| PP-SWR-050 | Trong khi HWA đang lái, a_y cần lớn nhất ≤ aysmax và không có xe lớn ở làn bên kề, lệch ngang của path phải ≤ 0,1 m | Test: S1 (a, b, d, e), S11 | đề bài | đề xuất |
| PP-SWR-051 | Trong khi HWA đang lái và a_y cần lớn nhất ≤ aysmax, DLC ở cả hai phía phải ≥ 0 | Test, vòng kín: S1 | R79 5.6.2.1.1 | đã chốt |
| PP-SWR-052 | Khi HWA bắt đầu lái lúc xe lệch tâm làn tới 0,5 m, chức năng đang lái phải giữ là HWA trong suốt đoạn đưa về giữa | Test: S2 | nhóm | đã chốt |
| PP-SWR-053 | Khi HWA bắt đầu lái lúc xe lệch tâm làn tới 0,5 m, lệch ngang của path phải về ≤ 0,1 m trong 5 s | Test: S2 | nhóm | đề xuất |
| PP-SWR-054 | Trong khi HWA ở REQUEST và tốc độ xe trong khoảng 0–60 km/h, planner phải tiếp tục gửi path hợp lệ cho HWA | Test: S11 | nhóm | đề xuất |

**Lý do**

- **PP-SWR-050.** Đề bài đòi path tâm làn liên tục và êm. Phần "liên tục" là PP-SWR-100 đến 102; phần "êm" là PP-SWR-003, 004. Yêu cầu này lượng hoá phần "bám tâm". 0,1 m bằng khoảng 3 lần độ lệch chuẩn nhiễu c0 của camera ban ngày (3 × 0,03 = 0,09 m), và bằng mức benchmark đã dùng cho nhận nhầm vạch và làn mở rộng. Với làn 3,5 m và xe rộng 1,9 m, khoảng trống mỗi bên là 0,8 m; 0,1 m là khoảng 12 % khoảng trống đó.
- **PP-SWR-051.** R79 5.6.2.1.1: dưới aysmax, hệ thống phải giữ xe không đè vạch. Đây là yêu cầu cấp xe, đo ở vòng kín, gồm cả sai số bám của controller chạy thử.
- **PP-SWR-052.** Đưa xe về giữa là việc của HWA, không mượn LKA.
- **PP-SWR-053.** Đưa 0,5 m về giữa với a_y thêm vào ≤ 0,5 m/s² cần ít nhất khoảng 2,4 s (phép tính ở tài liệu Thiết kế, mục 6). 5 s để dư cho path chậm lại vì giới hạn jerk.
- **PP-SWR-054.** Tắc đường trên cao tốc (S11). Dưới 10 km/h tầm nhìn 3 s ngắn, nhưng HWA vẫn phải giữ làn khi tài xế đang bật.

### 5.3 Dời tâm khi có xe lớn ở làn bên {#req-hwa-offset}

| ID | Yêu cầu | Kiểm chứng | Nguồn | Trạng thái |
|---|---|---|---|---|
| PP-SWR-055 | Trong khi có xe lớn ở làn bên kề, lệch của path khỏi tâm làn thật phải ≤ 0,3 m | Test: S3, S3b, S15 | đề bài | cần chốt |
| PP-SWR-056 | Trong khi dời tâm, path chỉ được dời về phía có khoảng hở lớn hơn | Test: S3b, S15 | mentor | cần chốt |
| PP-SWR-057 | Trong khi dời tâm, DLC của xe theo path phải ≥ 0,3 m ở cả hai phía | Test: S3b, S15 | nhóm | cần chốt |
| PP-SWR-058 | Khi xe lớn ở làn bên kề đang tới gần, path phải bắt đầu dời trước lúc xe lớn tới ngang hàng | Test: S3 | đề bài | cần chốt |
| PP-SWR-059 | Sau khi đuôi xe lớn đã qua, lệch ngang của path phải về ≤ 0,1 m trong 4 s | Test: S3 | nhóm | đề xuất |

**Lý do**

- **PP-SWR-055, 058.** Đề bài: HWA dời tâm khi vượt xe lớn, dời sớm. Mức 0,3 m là của nhóm.
- **PP-SWR-056.** Mentor (S3b): không đẩy xe về phía xe ở bên kia. Khoảng hở mỗi bên là khoảng cách từ thân xe mình tới vật gần nhất phía đó, hoặc tới biên làn thật nếu bên đó trống.
- **PP-SWR-059.** Trả 0,3 m về với a_y thêm vào ≤ 0,5 m/s² cần ít nhất √(5,77 × 0,3 / 0,5) ≈ 1,9 s (cùng công thức ở tài liệu Thiết kế, mục 6). 4 s để dư cho một khoảng chờ trước khi trả về.

### 5.4 Làn thay đổi {#req-hwa-lane-change}

| ID | Yêu cầu | Kiểm chứng | Nguồn | Trạng thái |
|---|---|---|---|---|
| PP-SWR-060 | Khi một biên làn mở rộng (làn dừng khẩn cấp, tách nhánh, thêm làn), lệch ngang của path về phía mở rộng phải ≤ 0,1 m | Test: S6b | mentor | đề xuất |
| PP-SWR-061 | Khi lane model chuyển sang làn mới, path phải thoả PP-SWR-100 đến 102 | Test: S17 | nhóm | đã chốt |

**Lý do**

- **PP-SWR-060.** Mentor: path không được dịch về phía làn mở rộng. 0,1 m là ngưỡng benchmark đang dùng (tài liệu Benchmark và Evaluation, mục 5.5).

## 6. LKA và ELK {#req-intervention}

| ID | Yêu cầu | Kiểm chứng | Nguồn | Trạng thái |
|---|---|---|---|---|
| PP-SWR-080 | Khi LKA hoặc ELK bắt đầu can thiệp, điểm đầu của path phải khớp trạng thái ngang thật của xe: lệch vị trí ≤ 0,1 m, lệch v_lat ≤ 0,1 m/s | Test: S4, S5, S6 | đề bài | đề xuất |
| PP-SWR-081 | Thời gian từ lúc LKA bắt đầu path can thiệp tới COMPLETED nên ≤ 4 s | Test: S4 | nhóm | đề xuất |
| PP-SWR-082 | Thời gian từ lúc ELK bắt đầu path can thiệp tới COMPLETED nên ≤ 3,5 s | Test: S5, S6, S7, S8, S8b (d, e) | nhóm | đề xuất |
| PP-SWR-083 | Một lần LKA hoặc ELK phải kết thúc, bằng COMPLETED hoặc bị hủy, trong ≤ 10 s | Test: S4, S4b, S5, S6, S7, S8, S8b (d, e) | R79 5.1.6.1.2.1 | đã chốt |
| PP-SWR-084 | Khi LKA báo COMPLETED, DLC ở phía xe đã trôi về phải ≥ 0,5 m | Test: S4 | đề bài | cần chốt |
| PP-SWR-085 | Sau một lần LKA hoặc ELK, DLC nhỏ nhất ở phía đối diện phải ≥ 0,3 m | Test: S4, S4b, S5, S6, S7, S8, S8b (d, e) | đề bài | đề xuất |
| PP-SWR-086 | DTLE nhỏ nhất trong một lần can thiệp phải ≥ −0,3 m với LKA và ELK vạch liền, và ≥ −0,1 m với ELK mép đường | Test, vòng kín: S4, S5, S6 | Euro NCAP Assessment 4.3.2, 4.3.3.3; EU 2021/646 3.6.2 | đã chốt |
| PP-SWR-087 | DTLE nhỏ nhất của LKA nên ≥ 0 ở chế độ B, ban ngày | Test, vòng kín: S4 | nhóm | đề xuất |
| PP-SWR-088 | Trong lúc ELK can thiệp vì xe ở làn bên, khoảng cách ngang nhỏ nhất tới xe đó phải ≥ 0,3 m | Test, vòng kín: S7, S8 | Euro NCAP 4.3.3.4; LSS 7.4.7 | đã chốt |
| PP-SWR-089 | Nếu ELK được yêu cầu khi lốp trước đã sang quá 0,3 m qua vạch phía side, thì planner không được lập path kéo xe về làn cũ | Test: S8 | nhóm | đề xuất |
| PP-SWR-090 | Planner chỉ được báo COMPLETED sau khi các điều kiện sau giữ liên tục 0,5 s: v_lat trong ±0,1 m/s, góc lệch so với hướng làn trong ±0,5°, a_y thêm vào ≤ 0,2 m/s² | Test: S4, S5 | nhóm | đề xuất |
| PP-SWR-091 | Khi trễ EPS tới 100 ms, DTLE nhỏ nhất phải vẫn đạt PP-SWR-086 | Test, vòng kín: S13 (a, b) | nhóm | đề xuất |

**Lý do**

- **PP-SWR-080.** Đề bài: path can thiệp đi từ trạng thái đang trôi. 0,1 m bằng khoảng 3 lần σ_c0 = 0,03 m của camera ban ngày. 0,1 m/s bằng 2 lần σ = 0,05 m/s của v_y (tài liệu Benchmark và Evaluation, mục Mô hình cảm biến).
- **PP-SWR-081, 082.** Tính thử ở tài liệu Thiết kế, mục 7.1: path LKA khoảng 3 s là êm, a_y dưới 1 m/s². Cộng 0,5 s giữ điều kiện ở PP-SWR-090 và dư 0,5 s ra 4 s. ELK có mục tiêu 1–3 s, cộng 0,5 s ra 3,5 s.
- **PP-SWR-083.** R79 5.1.6.1.2.1: can thiệp quá 10 s phải có âm thanh.
- **PP-SWR-084.** Đề bài: "back inside the lane, then release to the driver". Còn bàn đích là DLC ≥ 0,5 m hay tâm làn (mục 10).
- **PP-SWR-085.** Đề bài: "no overshoot into the other lane".
- **PP-SWR-086.** Yêu cầu cấp xe, đo ở vòng kín, gồm cả controller và EPS chạy thử. Phần biên dành cho planner chưa được phân bổ (mục 10).
- **PP-SWR-089.** R79 5.1.6.2.3.1 cho phép ELK đưa xe về làn cũ. Khi lốp đã sang quá xa thì kéo về nguy hiểm hơn để xe đi tiếp.
- **PP-SWR-090.** Không quy định nào cho con số. R79 5.6.2.2.3 và EU 2021/646 3.6.3.1 chỉ đòi không mất hỗ trợ lái đột ngột, nên tiêu chí chính là êm lúc trả quyền: a_y thêm vào về gần 0.
- **PP-SWR-091.** Trễ chấp hành danh định là 50 ms (cấu hình xe). 100 ms là gấp đôi, để planner có dư khi bộ chấp hành chậm hơn dự kiến; mức 150 ms chỉ ghi số. Controller chạy thử giữ cố định cho mọi phiên bản planner, nên khác biệt giữa các planner phản ánh phần dư của chính planner.

## 7. Giới hạn, liên tục, khả thi {#req-limits}

| ID | Yêu cầu | Kiểm chứng | Nguồn | Trạng thái |
|---|---|---|---|---|
| PP-SWR-100 | Trong khi path_valid = true, lệch ngang giữa hai path liên tiếp phải ≤ 0,05 m | Test: mọi kịch bản, mọi lỗi | đề bài | đã chốt |
| PP-SWR-101 | Trong khi path_valid = true, lệch hướng giữa hai path liên tiếp phải ≤ 0,005 rad | Test: mọi kịch bản, mọi lỗi | đề bài | đã chốt |
| PP-SWR-102 | Trong khi path_valid = true, lệch độ cong giữa hai path liên tiếp phải ≤ 0,0003 1/m | Test: mọi kịch bản, mọi lỗi | đề bài | đã chốt |
| PP-SWR-110 | Trong khi LKA đang lái, a_y của path phải ≤ 3,0 m/s² | Test: S4, S4b | nhóm | đã chốt |
| PP-SWR-111 | Trong khi ELK đang lái, a_y của path phải ≤ 4,0 m/s² | Test: S5, S6, S7, S8, S8b (d, e) | nhóm | đã chốt |
| PP-SWR-112 | Trong khi LKA đang lái, a_y thêm vào phải ≤ 1,5 m/s² | Test: S4, S4b | nhóm | đã chốt |
| PP-SWR-113 | Trong khi ELK đang lái, a_y thêm vào phải ≤ 3,0 m/s² | Test: S5, S6, S7, S8, S8b (d, e) | nhóm | đã chốt |
| PP-SWR-114 | Trong khi LKA đang lái, jerk ngang của path phải ≤ 5 m/s³ | Test: S4, S4b | ISO 11270 (nguồn thứ cấp) | đã chốt |
| PP-SWR-115 | Trong khi ELK đang lái, jerk ngang của path phải ≤ 10 m/s³ | Test: S5, S6, S7, S8, S8b (d, e) | nhóm | đã chốt |
| PP-SWR-116 | front_wheel_angle tại mọi điểm của path phải ≤ 0,61 rad | Test: mọi kịch bản | cấu hình xe | đã chốt |
| PP-SWR-117 | Tốc độ quay vô lăng suy ra từ path (tốc độ đổi front_wheel_angle nhân tỉ số lái 15) phải ≤ 6 rad/s | Test: mọi kịch bản | cấu hình xe | đã chốt |

**Lý do**

- **PP-SWR-100 đến 102.** Đề bài: không được tạo step trong steering request, kể cả lúc đổi chức năng và lúc lane model nhảy. Lệch hướng 0,005 rad gây lệch ngang khoảng 6 cm ở điểm nhìn trước 0,5 s. Lệch độ cong 0,0003 1/m làm vô lăng nhảy khoảng 0,75°.
- **PP-SWR-110, 111.** R79 không giới hạn a_y của CSF. 4,0 m/s² cho ELK để còn dư trên đường ướt μ = 0,5, giới hạn bám khoảng 4,9 m/s².
- **PP-SWR-112, 113.** Kiểm tra bằng tính toán ở tài liệu Chức năng ADAS, mục 6.1.
- **PP-SWR-114, 115.** LKA theo ISO 11270, mới đọc trang tóm tắt. ELK không có số trong quy định.
- **PP-SWR-116, 117.** Góc bánh tối đa và tốc độ vô lăng tối đa lấy từ cấu hình xe (tài liệu Thiết kế, mục 2.1).

Lực ghi đè (≤ 50 N theo R79 5.6.2.1.3 a, 5.1.6.1.3, 5.1.6.2.8; EU 2021/646 3.6.3.1) thuộc Lateral Controller và EPS, không phải yêu cầu của planner.

## 8. Chịu lỗi {#req-faults}

### 8.1 Lỗi lane model {#req-lane-faults}

| ID | Yêu cầu | Kiểm chứng | Nguồn | Trạng thái |
|---|---|---|---|---|
| PP-SWR-120 | Khi lane model có nhiễu c0, c1 tới mức ban đêm (gấp 2,5 lần ban ngày), path phải thoả giới hạn jerk của chức năng đang lái và PP-SWR-100 đến 102 | Test: F01 | nhóm | đã chốt |
| PP-SWR-121 | Khi c0 nhảy 0,3–1,0 m trong một frame, path phải thoả PP-SWR-100 đến 102 | Test: F02 | đề bài | đã chốt |
| PP-SWR-122 | Khi lane model nhận nhầm vạch làn bên, lệch ngang của path phải ≤ 0,1 m | Test: F03 | nhóm | đề xuất |
| PP-SWR-123 | Khi lane model mất một vạch, lệch ngang của path phải ≤ 0,1 m, trừ lúc bề rộng làn đang đổi | Test: F04 (a–d) | nhóm | đề xuất |
| PP-SWR-124 | Khi lane model mất cả hai vạch hoặc không hợp lệ, planner phải giữ path_valid = true trong T_coast = 1 s rồi đặt path_valid = false, sai lệch thời điểm không quá một chu kỳ | Test: F05, F12 (Lane Model) | nhóm | đã chốt |
| PP-SWR-125 | Khi lane model có c2 sai, lệch ngang của path trên đoạn 2–3 s nên ≤ 50 % lệch của một path bám đúng lane model sai đó | Test: F06 | đề bài | đề xuất |

**Lý do**

- **PP-SWR-120.** Nhiễu còn lại sau Lane Model: σ_c0 = 0,03 m, σ_c1 = 0,002 ban ngày, gấp 2,5 lần ban đêm hoặc mưa.
- **PP-SWR-121.** Đề bài: path êm khi lane model nhảy. Lane Model không gửi cờ báo nhảy.
- **PP-SWR-122, 123.** Cùng mức 0,1 m với PP-SWR-050. Khi bề rộng làn đổi đúng lúc mất vạch, tâm làn dựng từ một vạch có thể lệch hơn; ca này chỉ ghi số.
- **PP-SWR-124.** T_coast = 1 s tính từ sai số dead reckoning: lệch khoảng 0,06 m sau 1 s với bias yaw rate 0,3 °/s ở 25 m/s (phân tích ở tài liệu Thiết kế, mục 8.1). Không quy định nào cho con số này; R79 5.6.2.2.3 chỉ đòi không thả lái đột ngột.
- **PP-SWR-125.** Đề bài đòi đo c2 sai. Một path bám đúng lane model sai là mốc tệ nhất có thể tính được ở phía đánh giá. 50 % là mức để thấy rõ planner có kết hợp nguồn khác hay không; chưa có văn bản nào cho số này.

### 8.2 Lỗi thời gian và toàn vẹn {#req-timing-faults}

| ID | Yêu cầu | Kiểm chứng | Nguồn | Trạng thái |
|---|---|---|---|---|
| PP-SWR-126 | Khi message bị mất, lẻ hoặc thành chuỗi, hoặc có jitter ±20 ms, path phải thoả PP-SWR-100 đến 102 và giới hạn jerk của chức năng đang lái | Test: F10 | nhóm | đã chốt |
| PP-SWR-127 | Khi message đến muộn hoặc sai thứ tự, path phải thoả PP-SWR-100 đến 102 | Test: F11 | nhóm | đã chốt |
| PP-SWR-128 | Trong khi camera gửi 20 Hz và planner chạy 40 Hz, path phải thoả PP-SWR-100 đến 102 ở mọi chu kỳ | Test: mọi kịch bản, F13 | nhóm | đã chốt |
| PP-SWR-129 | Nếu message bị lặp (counter lặp), thì output phải giống ca không lỗi cùng seed | Test: F15 (lặp) | nhóm | đã chốt |
| PP-SWR-130 | Nếu counter nhảy hoặc đứng yên, valid = false, qualifier FAULT hoặc CRC sai, thì output phải giống ca mất message tương ứng | Test: F15 (nhảy, đứng yên), F16, F17 | nhóm | đã chốt |
| PP-SWR-131 | Nếu tuổi của lane model hoặc ObjectList vượt 250 ms, thì planner phải coi input đó không hợp lệ | Test: Q1 (300 ms) | nhóm | đã chốt |
| PP-SWR-132 | Nếu stamp của input ở tương lai quá 10 ms, thì planner phải coi input đó không hợp lệ | Test: F19 | nhóm | đã chốt |
| PP-SWR-133 | Trong khi tuổi của lane model hoặc ObjectList trong khoảng 170–250 ms, planner phải tiếp tục dùng input đó | Test: Q1 (200 ms) | nhóm | đã chốt |
| PP-SWR-134 | Planner phải ghi log số frame lane model và ObjectList có tuổi vượt 170 ms | Inspection | nhóm | đã chốt |

**Lý do**

- **PP-SWR-131 đến 134.** Độ trễ thật chưa biết (mentor). 170 ms là trễ giả định lớn nhất 120 ms cộng 50 ms. 250 ms là mức trễ lớn nhất benchmark quét (200 ms) cộng 50 ms. Ba kiểm tra cho ngưỡng 250 ms ở tài liệu Thiết kế, mục 3. 10 ms bằng mức lệch đồng hồ lớn nhất trước lần đồng bộ đầu.

### 8.3 Input không hợp lệ hoặc quá thời gian {#req-invalid-input}

| ID | Yêu cầu | Kiểm chứng | Nguồn | Trạng thái |
|---|---|---|---|---|
| PP-SWR-140 | Nếu ObjectList không hợp lệ, thì planner phải đưa phần dời tâm của HWA về 0 trong giới hạn PP-SWR-002 | Test: F12 (Perception, trong S3) | nhóm | đã chốt |
| PP-SWR-141 | Nếu ObjectList không hợp lệ, thì planner vẫn phải thực hiện can thiệp ELK được yêu cầu | Test: F12 (Perception, trong S5) | nhóm | đã chốt |
| PP-SWR-142 | Nếu IMU, tốc độ hoặc góc lái không hợp lệ, thì planner phải đặt path_valid = false trong không quá một chu kỳ | Test: F12 (IMU, tốc độ, góc lái), F17 | nhóm | đã chốt |
| PP-SWR-143 | Nếu ego-motion không hợp lệ, thì planner phải đặt path_valid = false trong không quá một chu kỳ | Test: F20 | nhóm | đã chốt |
| PP-SWR-144 | Nếu VehicleStateEstimate không hợp lệ, thì planner phải tiếp tục HWA và không được chọn LKA hoặc ELK làm chức năng đang lái | Test: F12 (v_y) | nhóm | đã chốt |
| PP-SWR-145 | Nếu FunctionRequests quá timeout 75 ms, thì planner phải đặt active_function = NONE và path_valid = false trong không quá một chu kỳ | Test: F12 (FunctionRequests) | nhóm | đã chốt |
| PP-SWR-146 | Nếu cấu hình xe thiếu lúc khởi động, thì planner không được gửi Trajectory | Demonstration | nhóm | đã chốt |

**Lý do**

- **PP-SWR-140, 141.** Việc xét xe ở làn bên cho ELK nằm ở khối ADAS, nên ELK ở G1 không cần ObjectList.
- **PP-SWR-142, 143.** Thiếu IMU, tốc độ, góc lái hoặc ego-motion thì không bù trễ và không nối path được.
- **PP-SWR-145.** Báo path không hợp lệ để bên nhận giảm mô-men từ từ.

### 8.4 Lỗi tín hiệu xe và đồng hồ {#req-signal-faults}

| ID | Yêu cầu | Kiểm chứng | Nguồn | Trạng thái |
|---|---|---|---|---|
| PP-SWR-135 | Khi IMU có nhiễu tới hai lần mức datasheet, PP-SWR-050 và 100 đến 102 phải vẫn thoả | Test: F07 (a, b) | nhóm | đề xuất |
| PP-SWR-136 | Khi yaw rate có bias tới 0,3 °/s, PP-SWR-050 và 100 đến 102 phải vẫn thoả | Test: F08 (a, b) | nhóm | đề xuất |
| PP-SWR-137 | Khi đồng hồ trôi tới ±100 ppm hoặc mất đồng bộ gPTP tới 10 s, PP-SWR-050 và 100 đến 102 phải vẫn thoả | Test: F14 (a, b, c) | nhóm | đề xuất |
| PP-SWR-138 | Khi yaw rate đã lọc trễ tới 50 ms mà planner không được báo phần trễ đó, PP-SWR-050 và 100 đến 102 phải vẫn thoả | Test: Q2 (0–50 ms) | nhóm | đề xuất |
| PP-SWR-139 | Trong khi tín hiệu CAN bị làm tròn theo factor của DBC, PP-SWR-050 và 100 đến 102 phải vẫn thoả | Test: mọi kịch bản, F18 | nhóm | đề xuất |

**Lý do**

- **Chung cho PP-SWR-135 đến 139.** Các lỗi này có trên xe thật ở mức nêu trong yêu cầu. Không đặt ngưỡng mới: các ngưỡng bám tâm và liên tục đã có phải vẫn đạt. Ngưỡng không lấy từ phép tính trong tài liệu Thiết kế, để không chấm planner theo chính giả định của nó. Mức xấu nhất của benchmark (F08 c, Q2 100 ms) chỉ ghi số.
- **PP-SWR-135.** F07 a theo datasheet Bosch SMI230; b gấp đôi để có dư. Mentor: IMU đến planner đã sạch, nên đây là mức kiểm biên.
- **PP-SWR-136.** 0,3 °/s là bias còn lại khi bù chưa hết. 1 °/s là offset của cảm biến thô chưa bù, chỉ ghi số.
- **PP-SWR-137.** Trôi 100 ppm trong 10 s chỉ lệch 1 ms, nhỏ hơn jitter ±20 ms mà PP-SWR-126 đã đòi chịu được.
- **PP-SWR-138.** Trễ thật của bộ lọc chưa biết (mentor). 50 ms là mức giữa của dải benchmark quét; 100 ms chỉ ghi số. Chưa có văn bản nào cho số này.
- **PP-SWR-139.** Làm tròn luôn có trên xe thật. Câu "không ảnh hưởng đáng kể" ở benchmark được lượng hoá bằng các ngưỡng đã có.

## 9. Interface với khối dọc {#req-longitudinal}

| ID | Yêu cầu | Kiểm chứng | Nguồn | Trạng thái |
|---|---|---|---|---|
| PP-SWR-150 | Planner phải gửi LateralLimits mỗi chu kỳ | Test: S14 | nhóm | đề xuất |
| PP-SWR-151 | LateralLimits.v_max phải bằng √(ngân sách a_y của chức năng đang lái / κ_max), với κ_max là độ cong lớn nhất của tâm làn thật trong tầm nhìn của lane model, sai lệch ≤ 5 % | Test: S14 | nhóm | đề xuất |
| PP-SWR-152 | LateralLimits.distance phải bằng khoảng cách dọc tới điểm có κ_max, sai lệch ≤ 5 m | Test: S14 | nhóm | đề xuất |
| PP-SWR-153 | Khi LongitudinalPlan hợp lệ, longitudinal_velocity và acceleration của Trajectory phải lấy theo LongitudinalPlan | Test: S14 | nhóm | đề xuất |
| PP-SWR-154 | Nếu LongitudinalPlan mất hoặc quá timeout 75 ms, thì Trajectory phải dùng tốc độ hiện tại không đổi và gia tốc 0 | Test: S14 (d) | nhóm | đề xuất |
| PP-SWR-155 | Nếu LongitudinalPlan mất hoặc quá timeout 75 ms, thì planner phải giữ path_valid = true | Test: S14 (d) | nhóm | đề xuất |

**Lý do**

- **PP-SWR-151.** Sai 5 % ở v làm sai khoảng 10 % ở a_y, tức khoảng 0,25 m/s² ở mức 2,5 m/s². Chưa có văn bản nào cho số này.
- **PP-SWR-152.** 5 m bằng khoảng hai điểm của path ở 90 km/h (bước 0,1 s, 2,5 m mỗi điểm).
- **PP-SWR-155.** Phần ngang không phụ thuộc bắt buộc vào phần dọc (quyết định ở tài liệu Thiết kế, mục 6.1).

## 10. Còn cần chốt {#req-open}

Hạn chung: trước khi viết code phần liên quan.

| Việc | Chặn yêu cầu | Người trả lời |
|---|---|---|
| Giá trị δ. Phải lớn hơn sai số ước lượng a_y cần do nhiễu c2 của camera, ở 90–130 km/h | PP-SWR-007, 008 | Nhóm G1, tính từ mô hình nhiễu camera (tài liệu Benchmark và Evaluation, mục 9) |
| Giá trị ε | PP-SWR-006 | Nhóm G1 |
| Giá trị T_flag. Phải tính cả trễ lane model (giả định, tài liệu Thiết kế, mục 2.1) và một chu kỳ | PP-SWR-007, 008 | Nhóm G1; cập nhật khi có số trễ thật |
| Cờ lateral_limit_reached có cần thời gian giữ tối thiểu để không bật tắt liên tục hay không | PP-SWR-007, 008 | Nhóm G1, cùng khối ADAS (phần cảnh báo) |
| v_max hiện nhắm đúng ngân sách a_y. Sau khi ACC giảm tốc, a_y cần lớn nhất nằm ngay trong dải aysmax ± δ, nên cờ không chắc sẽ tắt | PP-SWR-008, 009, 151 | Nhóm G1 |
| Dung sai vượt aysmax của R79 (0,3 m/s², hoặc 40 % trong tối đa 2 s) áp cho a_y của path hay cho a_y đo trên xe. Tài liệu Benchmark và Evaluation, mục 5.2, đang áp cho path | PP-SWR-001 | Nhóm G1, đối chiếu bản gốc R79 5.6.2.1.3 |
| Đích của LKA: DLC ≥ 0,5 m (trả quyền sớm, đúng ý đề bài) hay tâm làn (lâu hơn) | PP-SWR-084 | Nhóm G1 |
| Khi LKA hoặc ELK bắt đầu lúc path HWA đang chạy mà xe đã lệch khỏi path đó, PP-SWR-031 (liên tục với path cũ) và PP-SWR-080 (khớp trạng thái thật) có thể không cùng thoả được. Cần chọn yêu cầu nào ưu tiên | PP-SWR-031, 080 | Nhóm G1 |
| Phân bổ biên DTLE ở PP-SWR-086 cho path, sai số bám của controller và trễ EPS | PP-SWR-086 | Nhóm G1, cùng nhóm Lateral Controller |
| Planner làm gì khi không được kéo xe về làn cũ | PP-SWR-089 | Nhóm G1, cùng khối ADAS |
| Khối ADAS biết LKA, ELK không khả dụng bằng cách nào khi VehicleStateEstimate không hợp lệ | PP-SWR-144 | Nhóm G1, cùng khối ADAS |
| Định nghĩa xe lớn (≥ 2,3 m) | PP-SWR-055 đến 059 | Nhóm G1 |
| Khi ELK kết thúc hoặc bị hủy mà LKA vẫn ở REQUEST: chuyển sang LKA (theo PP-SWR-030) hay sang HWA (theo PP-SWR-033, 036). Đề xuất: theo PP-SWR-030 | PP-SWR-030, 033, 036 | Nhóm G1, cùng khối ADAS |
| intervention_phase giữ COMPLETED bao lâu. Đề xuất: tới khi state của chức năng đó rời REQUEST, khớp với PP-SWR-034 | PP-SWR-032, 034 | Nhóm G1, cùng khối ADAS |
| path_valid khi HWA rời REQUEST và không chức năng nào lái. Đề xuất: giữ true, như PP-SWR-037 | PP-SWR-030, 037 | Nhóm G1 |
| active_function khi path không hợp lệ. Đề xuất: NONE | PP-SWR-124, 142, 143 | Nhóm G1, cùng khối ADAS |
| Planner làm gì khi input hồi phục sau lúc path không hợp lệ. Đề xuất: lập path từ trạng thái thật của xe; chọn chức năng theo PP-SWR-030; LKA, ELK chỉ khi có yêu cầu mới | PP-SWR-124, 142, 143 | Nhóm G1 |
| Dừng ngay một lần can thiệp khi VehicleStateEstimate không hợp lệ (PP-SWR-144) có an toàn không, nhất là giữa lúc ELK tránh xe | PP-SWR-144 | Nhóm G1 |

## Nguồn

- Đề bài G1 (`G1_Path_Planning.pdf`)
- [Thiết kế tính năng Path Planner](report.html?doc=thiet-ke-path-planner&lang=vi), [Chức năng ADAS](report.html?doc=chuc-nang-adas&lang=vi), [Benchmark và Evaluation](report.html?doc=benchmark-evaluation&lang=vi)
- [UN Regulation No 79, OJ L 2025/3](https://upload.wikimedia.org/wikipedia/commons/f/f3/OJ_L_202500003_of_2025_-_EN_English.pdf)
- [Commission Implementing Regulation (EU) 2021/646, ELKS](https://lawplayer.com/eu/act/32021R0646)
- [Euro NCAP LSS Test Protocol v4.3](https://cdn.euroncap.com/cars/assets/euro_ncap_lss_test_protocol_v43_f2ddd5f6d6.pdf)
- [Euro NCAP Assessment Protocol Safety Assist Collision Avoidance v10.4.1](https://cdn.euroncap.com/cars/assets/euro_ncap_assessment_protocol_sa_collision_avoidance_v1041_fafe1dd418.pdf)
- [ISO 11270:2014, trang tóm tắt](https://standards.iteh.ai/catalog/standards/iso/808a3e9d-fc87-4892-85d1-6087e2ee3370/iso-11270-2014) (chưa đọc bản gốc)
- Mavin và cộng sự (2009), Easy Approach to Requirements Syntax (EARS), IEEE International Requirements Engineering Conference

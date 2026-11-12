# Architecture Decision Records

| Mục | Nội dung |
|---|---|
| Mã tài liệu | `PP-ADR` |
| Phiên bản | 1.4 |
| Trạng thái | BL1 |
| Tác giả | thongbui |
| Người review | thongbui |
| Cập nhật | 2026-11-12 |

## 1. Purpose and scope {#adr-scope}

- **Mục đích:** Ghi vì sao path planner được thiết kế như ở tài liệu Software Architectural Design: phương án đã xét, quyết định, hệ quả.
- **Phạm vi:** Quyết định thiết kế của path planner.

## 2. References {#adr-references}

| Tài liệu | Dùng cho |
|---|---|
| [Software Requirements Specification](report.html?doc=path-planner-software-requirements-specification&lang=vi) | Requirement và giả định mà quyết định đáp ứng |
| [Software Architectural Design](report.html?doc=path-planner-software-architectural-design&lang=vi) | Cách làm, trỏ về PP-ADR |
| [Software Qualification Test Specification](report.html?doc=path-planner-software-qualification-test-specification&lang=vi) | Test case so sánh các phương án |
| Nygard (2011), Documenting Architecture Decisions | Khuôn ghi quyết định |
| Werling và cộng sự (2010); Apollo (Baidu) | Tham chiếu cho PP-ADR-001, 004 |

## 3. Conventions {#adr-format}

| Mục | Quy ước |
|---|---|
| ID | `PP-ADR-nnn`, đánh theo thứ tự. Không đánh số lại, không dùng lại |
| Nội dung | Năm phần: bối cảnh, phương án đã xét, quyết định, hệ quả (được và mất), liên quan |
| Thay quyết định | Giữ quyết định cũ, ghi "bị thay bởi PP-ADR-…" ở dòng Quyết định, và ghi quyết định mới thành mục mới |

## 4. Danh sách {#adr-list}

| ID | Quyết định |
|---|---|
| PP-ADR-001 | Tách khối ngang và dọc, trao đổi ràng buộc |
| PP-ADR-002 | Bù trễ theo stamp lúc chụp |
| PP-ADR-003 | Hai ngưỡng tuổi dữ liệu: theo dõi và loại bỏ |
| PP-ADR-004 | Trajectory stitching, quay về trạng thái đo khi lệch xa |
| PP-ADR-005 | Dùng chung một hàm tính trạng thái ngang với khối Chức năng ADAS |
| PP-ADR-006 | Planner tự kiểm tính nhất quán của đường biên |
| PP-ADR-007 | Ba lớp chống nhiễu dựa trên path cũ |
| PP-ADR-008 | Offset dời tâm theo khoảng hở tới xe lớn, giới hạn theo khoảng trống thật |
| PP-ADR-009 | Bám path cũ tối đa `T_coast` rồi báo path không hợp lệ |
| PP-ADR-010 | Lateral Controller bù trễ sau planner |
| PP-ADR-011 | Planner suy tâm làn từ vạch làn bên và mép đường |
| PP-ADR-012 | Một bộ calibration cho mọi xe |
| PP-ADR-013 | Planner là thư viện C11 có API C, tách adapter theo nền tảng |
| PP-ADR-014 | Planner tự tính trạng thái ngang, không dùng chung với khối Chức năng ADAS |
| PP-ADR-015 | PathStatus có pha riêng cho LKA và ELK |

## 5. Các quyết định {#adr-decisions}

### PP-ADR-001 Tách khối ngang và dọc, trao đổi ràng buộc {#adr-001}

| Mục | Nội dung |
|---|---|
| Bối cảnh | Xe khác lấn vào làn và cua gắt hơn mức HWA lái được cần cả phần ngang lẫn phần dọc. Path planner chỉ là khối ngang |
| Phương án | A) Một planner gộp ngang và dọc. B) Hai khối, trao đổi ràng buộc qua LateralLimits và LongitudinalPlan. C) Hai khối, không trao đổi |
| Quyết định | B. Khối dọc là ACC chạy thử trong simulator, cố định cho mọi phiên bản planner. C giữ làm đối chứng ở S14 (mentor) |
| Hệ quả | Được: giống xe thật; khối dọc giảm tốc được trước cua. Mất: thêm hai interface; mỗi bên dùng message chu kỳ trước, trễ 25 ms; cần đường lui khi mất LongitudinalPlan |
| Liên quan | PP-SWR-009, 150 đến 155; Software Architectural Design mục 6.1; S14 |

### PP-ADR-002 Bù trễ theo stamp lúc chụp {#adr-002}

| Mục | Nội dung |
|---|---|
| Bối cảnh | Lane model trễ 100 ± 20 ms (PP-ASM-001). Không bù thì trong cua R = 250 m tham chiếu lệch 0,25 m ở 25 m |
| Phương án | A) Không bù. B) Bù bằng trễ danh định: còn lệch 0,05 m ở 25 m do jitter. C) Bù theo stamp lúc chụp bằng ego-motion |
| Quyết định | C |
| Hệ quả | Được: không cần biết trước độ trễ; sai số còn lại chỉ từ ego-motion. Mất: phụ thuộc ego-motion và đồng bộ đồng hồ; ego-motion lỗi thì path không hợp lệ ngay |
| Liên quan | PP-SWR-012, 013, 143; PP-ASM-001, 012, 013; Software Architectural Design Appendix A.1 |

### PP-ADR-003 Hai ngưỡng tuổi dữ liệu: theo dõi và loại bỏ {#adr-003}

| Mục | Nội dung |
|---|---|
| Bối cảnh | Độ trễ thật chưa biết (mentor). Một ngưỡng 170 ms sẽ coi mọi frame là cũ nếu trễ thật là 200 ms |
| Phương án | A) Một ngưỡng 170 ms. B) Theo dõi 170 ms (vẫn dùng, ghi log) và loại bỏ 250 ms (coi input không hợp lệ) |
| Quyết định | B |
| Hệ quả | Được: không mất chức năng khi trễ thật lớn hơn giả định một chút; log cho biết trễ thật. Mất: có số đo trễ thật lớn hơn thì phải đặt lại ngưỡng loại bỏ |
| Liên quan | PP-SWR-131 đến 134; PP-ASM-001, 002; Software Architectural Design Appendix A.2 |

### PP-ADR-004 Trajectory stitching, quay về trạng thái đo khi lệch xa {#adr-004}

| Mục | Nội dung |
|---|---|
| Bối cảnh | Path bắt đầu từ trạng thái đo thì nhiễu đi thẳng vào path; bắt đầu từ path cũ thì sai khi xe đã lệch |
| Phương án | A) Từ trạng thái đo mỗi chu kỳ. B) Từ điểm tương ứng trên path cũ. C) B khi xe gần path cũ, A khi lệch quá `stitch_reset` |
| Quyết định | C, như trajectory stitching của Apollo. Lúc LKA, ELK bắt đầu luôn dùng A |
| Hệ quả | Được: liên tục khi bình thường, đúng khi lệch lớn. Mất: lúc chuyển từ B sang A có thể có bước nhỏ; khi LKA, ELK bắt đầu lúc xe đã lệch, PP-SWR-080 được ưu tiên hơn PP-SWR-031 |
| Liên quan | PP-SWR-031, 080; Software Architectural Design mục 4.2 |

### PP-ADR-005 Dùng chung một hàm tính trạng thái ngang với khối Chức năng ADAS {#adr-005}

| Mục | Nội dung |
|---|---|
| Bối cảnh | Khối Chức năng ADAS (tính TLC) và planner (lập path can thiệp) cần cùng trạng thái ngang đo được |
| Phương án | A) Chung một hàm, cùng input. B) Planner tự tính. C) Khối Chức năng ADAS gửi trạng thái trong message |
| Quyết định | A. Bị thay bởi PP-ADR-014 |
| Hệ quả | Được: hai bên cùng một con số. Mất: hai khối phụ thuộc chung một thư viện. B có thể vênh (TLC 1,0 s so với 1,3 s); C thêm khoảng 20 ms trễ và planner vẫn phải tự tính cho HWA |
| Liên quan | PP-SWR-080; Software Architectural Design mục 4.2 |

### PP-ADR-006 Planner tự kiểm tính nhất quán của đường biên {#adr-006}

| Mục | Nội dung |
|---|---|
| Bối cảnh | Lane model không gửi cờ c0 jump (PP-ASM-009); giao thức CAN của Mobileye cũng không có cờ này |
| Phương án | A) Dựa vào cờ của lane model. B) Planner tự kiểm mỗi biên ở hai thang: từng frame so với frame trước đã dời bằng ego-motion, và chậm hơn qua độ song song và bề rộng làn |
| Quyết định | B. Cờ, nếu sau này có, chỉ là nguồn thứ hai |
| Hệ quả | Được: không phụ thuộc nhà cung cấp camera; một cơ chế cho c0 jump, nhận nhầm vạch và làn mở rộng. Mất: thêm logic và calibration parameter; thay đổi thật của làn được nhận sau `T_confirm` |
| Liên quan | PP-SWR-060, 121, 122; PP-ASM-009; Software Architectural Design mục 4 |

### PP-ADR-007 Ba lớp chống nhiễu dựa trên path cũ {#adr-007}

| Mục | Nội dung |
|---|---|
| Bối cảnh | Lane model sau khi lọc vẫn rung nhẹ (PP-ASM-011); path bám từng frame thì vô lăng rung theo |
| Phương án | A) Lọc lại cảm biến trong planner. B) Bắt đầu từ path cũ, giới hạn tốc độ đổi tham chiếu, phạt jerk |
| Quyết định | B |
| Hệ quả | Được: path êm dưới nhiễu mà không làm lại việc của lane model. Mất: phản ứng chậm hơn khi làn đổi thật; Software Qualification Test Specification đo cả hai mặt |
| Liên quan | PP-SWR-120; target PP-SWR-050; Software Architectural Design mục 4.1 |

### PP-ADR-008 Offset dời tâm theo khoảng hở tới xe lớn, giới hạn theo khoảng trống thật {#adr-008}

| Mục | Nội dung |
|---|---|
| Bối cảnh | HWA dời tâm khi có xe lớn ở làn bên (đề bài). Path không được dịch về phía làn mở rộng (mentor). Planner phải chạy cho mọi bề rộng làn 2,5–5,5 m và mọi xe rộng tới 2,5 m |
| Phương án | A) Khoảng hở tới mép đường thô, offset cố định ±0,3 m. B) Cân bằng khoảng hở hai bên, bên trống lấy biên làn của reference line. C) Dời ra xa xe lớn phần khoảng hở còn thiếu so với `gap_truck_min`; xe lớn ở cả hai bên thì cân bằng hai khoảng hở. B và C đều giới hạn offset theo khoảng trống thật |
| Quyết định | C (2026-11-11, thay B). Công thức ở Software Architectural Design mục 6; o_lim = max(0, min(`offset_max`, s − `dlc_offset_min`)), s = (W_làn − W_xe) / 2. B bị bỏ vì xe lớn ở giữa làn bên thì khoảng hở tới nó lớn hơn khoảng hở tới biên làn: B không dời, hoặc dời về phía xe lớn |
| Hệ quả | Được: luôn dời ra xa xe lớn, càng gần càng dời nhiều; không dịch về phía làn mở rộng; xe lớn ở hai bên thì đứng giữa; đúng với mọi làn và mọi xe, không có ca trái với PP-SWR-051. Mất: thêm calibration `gap_truck_min`; phụ thuộc chất lượng reference line; làn hẹp với xe rộng thì gần như không dời được |
| Liên quan | PP-SWR-051, 055, 056, 060, 062; target 057; Software Architectural Design mục 6 |

### PP-ADR-009 Bám path cũ tối đa `T_coast` rồi báo path không hợp lệ {#adr-009}

| Mục | Nội dung |
|---|---|
| Bối cảnh | Không còn biên đủ tin nào thì vị trí xe trong làn chỉ dựa vào ego-motion, mà ego-motion tích luỹ sai. Không quy định nào cho con số; R79 5.6.2.2.3 chỉ đòi không thả lái đột ngột |
| Phương án | Bám path cũ 0,5 s, 1 s, 2 s hoặc 3 s. Với bias yaw rate 0,3 °/s ở 25 m/s, lệch lần lượt 0,02, 0,06, 0,25 và 0,56 m |
| Quyết định | `T_coast` ≤ 1 s, khởi đầu 1 s |
| Hệ quả | Được: lệch nhỏ so với khoảng trống trong làn. Mất: cộng 1 s lane model đã dựng lại vạch (PP-ASM-010) thì có khoảng 2 s không có vạch thật |
| Liên quan | PP-SWR-124; PP-ASM-008, 010; Software Architectural Design Appendix A.4 |

### PP-ADR-010 Lateral Controller bù trễ sau planner {#adr-010}

| Mục | Nội dung |
|---|---|
| Bối cảnh | Từ lúc planner gửi path tới lúc bánh xe đáp ứng còn khoảng 66 ms (Software Architectural Design mục 3.3) |
| Phương án | A) Planner dời path tới trước một khoảng bằng trễ sau planner. B) Lateral Controller đọc điểm path theo thời gian hiện tại cộng trễ chấp hành, dựa trên `header.stamp_us` và `time_from_start` |
| Quyết định | B |
| Hệ quả | Được: hai khối không cùng bù một khoảng trễ; planner không cần biết trễ của EPS. Mất: phụ thuộc đội Lateral Controller dùng stamp đúng cách (PP-ASM-017) |
| Liên quan | PP-SWR-012; PP-ASM-007, 014, 017; Software Architectural Design mục 3.3 |

### PP-ADR-011 Planner suy tâm làn từ vạch làn bên và mép đường {#adr-011}

| Mục | Nội dung |
|---|---|
| Bối cảnh | Lane model gửi vạch của ba làn và mép đường. Có lúc làn mình mất cả hai vạch mà vạch làn bên hoặc mép đường vẫn đo được (mentor) |
| Phương án | A) Bám path cũ `T_coast` rồi báo không hợp lệ, bỏ qua biên khác. B) Lane model dựng lại vạch làn mình và gửi PREDICTED. C) Planner suy tâm làn từ mọi biên đủ tin còn lại, kết hợp theo phương sai; biên suy ra cần độ tin `conf_inferred` > `conf_ego` |
| Quyết định | C (mentor). Chỉ HWA lái trên tâm làn suy ra; LKA, ELK cần vạch làn mình đủ tin (mentor) |
| Hệ quả | Được: HWA chạy tiếp khi làn mình mất vạch; mở rộng từ cơ chế "một vạch cộng bề rộng nhớ được"; planner giữ toàn bộ phần kiểm tính nhất quán. Mất: tâm làn suy từ biên xa có sai số lớn hơn; sai khi bề rộng làn bên đổi trong lúc mất vạch. A bỏ phí dữ liệu; B làm planner không phân biệt được vạch đo với vạch dựng |
| Liên quan | PP-SWR-047, 124, 147, 148; PP-ADR-006, 009; Software Architectural Design mục 4 |

### PP-ADR-012 Một bộ calibration cho mọi xe {#adr-012}

| Mục | Nội dung |
|---|---|
| Bối cảnh | Hệ thống phải tích hợp được lên mọi xe gia đình, kể cả xe chưa ra mắt |
| Phương án | A) Mỗi xe một bộ calibration. B) Một bộ calibration chung; planner chỉ biết xe qua VehicleConfig |
| Quyết định | B |
| Hệ quả | Được: lên xe mới không phải chỉnh lại; chứng minh được planner tổng quát. Mất: bộ chung có thể kém tối ưu cho từng xe; mọi công thức phải tham số hoá theo VehicleConfig |
| Liên quan | PP-SWR-062, 116, 117; Software Architectural Design mục 11; Software Qualification Test Specification (flexibility) |

### PP-ADR-013 Planner là thư viện C11 có API C, tách adapter theo nền tảng {#adr-013}

| Mục | Nội dung |
|---|---|
| Bối cảnh | Mentor cần đưa được planner vào hệ thống thật để kiểm. Nền tảng đích chưa biết (PP-ASM-019). Benchmark phải chấm đúng mã sẽ bàn giao |
| Phương án | A) Python. B) Prototype Python rồi port sang C. C) C11, API C, adapter riêng cho từng nền tảng. D) C++17 |
| Quyết định | C. Theo một phần MISRA C:2012. Không cấp phát động, không đọc file, không biến toàn cục; bên gọi cấp vùng nhớ trạng thái. Calibration sinh thành struct hằng lúc build. Simulator gọi cùng thư viện qua adapter SIL |
| Hệ quả | Được: mọi nền tảng gọi được C (AUTOSAR Classic, Adaptive, Linux, QNX, ROS 2); cùng mã nguồn chạy ở SIL và trên đích; thời gian chạy tất định. Mất: thử thuật toán chậm hơn Python; đổi calibration phải build lại; công cụ miễn phí chỉ kiểm được một phần MISRA C:2012 |
| Liên quan | PP-ASM-019; Interface Control Document mục 4; Software Detailed Design mục 3 |

### PP-ADR-014 Planner tự tính trạng thái ngang, không dùng chung với khối Chức năng ADAS {#adr-014}

| Mục | Nội dung |
|---|---|
| Bối cảnh | Đề bài yêu cầu một path planner e2e. Planner phải đưa được vào hệ thống thật (PP-ADR-013), nơi khối Chức năng ADAS do đội khác làm |
| Phương án | A) Chung một hàm với khối Chức năng ADAS (PP-ADR-005). B) Planner tự tính từ input của mình. C) Khối Chức năng ADAS gửi trạng thái trong message |
| Quyết định | B. Khối Chức năng ADAS tự tính theo ADAS Function Specification mục 5: cùng công thức, khác mã |
| Hệ quả | Được: planner tự đứng, không phụ thuộc mã của khối khác; khối Chức năng ADAS chạy thử trong simulator độc lập với planner. Mất: TLC của khối Chức năng ADAS và trạng thái ngang của planner có thể vênh (ví dụ 1,0 s so với 1,3 s); planner phải chịu được độ vênh này, PP-SWR-080 vẫn đo trên trạng thái thật của xe |
| Liên quan | Thay PP-ADR-005; PP-ADR-013; PP-SWR-080; Software Architectural Design mục 4.2; Software Detailed Design mục 9 |

### PP-ADR-015 PathStatus có pha riêng cho LKA và ELK {#adr-015}

| Mục | Nội dung |
|---|---|
| Bối cảnh | Tại tick ELK COMPLETED, T9 có thể chọn LKA đang REQUEST theo PP-SWR-033. Khối Chức năng ADAS phải nhận ra chức năng nào vừa hoàn tất |
| Phương án | A) Một pha chung đi cùng `active_function`. B) Pha riêng cho từng chức năng |
| Quyết định | B. PathStatus có `lka_phase` và `elk_phase`. Mỗi pha giữ COMPLETED tới khi yêu cầu tương ứng rời REQUEST |
| Hệ quả | Một message có thể công bố ELK COMPLETED cùng LKA ACTIVE. Bên phát và bên nhận phải dùng cùng phiên bản schema |
| Liên quan | PP-TS-011, PP-SWR-032, 033, 041, Interface Control Document mục 6.2 |

## Revision history {#revision-history}

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 2026-11-10 | Refactor thành Architecture Decision Records, baseline BL1. Mọi quyết định là đã quyết; PP-ADR-008 giới hạn offset theo khoảng trống thật; PP-ADR-009 dùng `T_coast` ≤ 1 s; thêm PP-ADR-012; bỏ nhãn trạng thái và việc mở |
| 1.1 | 2026-11-10 | Thêm PP-ADR-013: planner là thư viện C11 có API C, tách adapter theo nền tảng |
| 1.2 | 2026-11-10 | Thêm PP-ADR-014: planner tự tính trạng thái ngang; PP-ADR-005 bị thay |
| 1.3 | 2026-11-11 | PP-ADR-008 chọn C thay B: dời theo khoảng hở tới xe lớn so với `gap_truck_min` |
| 1.4 | 2026-11-12 | Thêm PP-ADR-015 về pha riêng cho LKA và ELK trong PathStatus |

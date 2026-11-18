# Architecture Decision Records

| Mục | Nội dung |
|---|---|
| Mã tài liệu | `PP-ADR` |
| Phiên bản | 1.7 |
| Trạng thái | BL1 |
| Tác giả | thongbui |
| Người review | thongbui |
| Cập nhật | 2026-11-18 |

## 1. Purpose and scope {#adr-scope}

- **Mục đích:** Ghi vì sao hai path planner được thiết kế như ở tài liệu Software Architectural Design: phương án đã xét, quyết định, hệ quả.
- **Phạm vi:** Quyết định thiết kế của LCC planner và LKA/ELK planner.

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
| PP-ADR-004 | Trajectory stitching, chuyển dần về trạng thái đo khi lệch xa |
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
| PP-ADR-016 | Tách LCC planner và LKA/ELK planner; arbitrator thuộc công ty |
| PP-ADR-017 | Giữ LKA và ELK là hai chức năng riêng trong LKA/ELK planner |
| PP-ADR-018 | Bám xe trước bằng reference line ảo dựng từ vết xe trước |
| PP-ADR-019 | Hành lang can thiệp cập nhật bất đối xứng khi biên nhảy |
| PP-ADR-020 | Dời 10 cm khi một xe lớn, hai xe lớn giữ cân bằng khoảng hở |

## 5. Các quyết định {#adr-decisions}

### PP-ADR-001 Tách khối ngang và dọc, trao đổi ràng buộc {#adr-001}

| Mục | Nội dung |
|---|---|
| Bối cảnh | Xe khác lấn vào làn và cua gắt hơn mức LCC lái được cần cả phần ngang lẫn phần dọc. Path planner chỉ là khối ngang |
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

### PP-ADR-004 Trajectory stitching, chuyển dần về trạng thái đo khi lệch xa {#adr-004}

| Mục | Nội dung |
|---|---|
| Bối cảnh | Path bắt đầu từ trạng thái đo thì nhiễu đi thẳng vào path; bắt đầu từ path cũ thì sai khi xe đã lệch |
| Phương án | A) Từ trạng thái đo mỗi chu kỳ. B) Từ điểm tương ứng trên path cũ. C) B khi xe gần path cũ, A khi lệch quá `stitch_reset`. D) Trộn B và A theo độ lệch: chỉ B dưới `stitch_soft_min`, chỉ A từ `stitch_reset`, tuyến tính ở giữa |
| Quyết định | D (PP-TS-021, 2026-11-16; trước đó C, như trajectory stitching của Apollo). Lúc LKA, ELK bắt đầu luôn dùng A |
| Hệ quả | Được: liên tục khi bình thường, đúng khi lệch lớn, không đổi qua lại giữa A và B quanh ngưỡng. Mất: khi xe lệch path cũ, path mang một phần sai số của lane model (cua chữ S, PP-PR-004); lúc LKA, ELK bắt đầu, path không nối với path cũ, lệnh lái vẫn liên tục vì độ cong đầu lấy từ xe (PP-SWR-049) |
| Liên quan | PP-SWR-031, 049, 080, 100; Software Architectural Design mục 4.2; PP-TS-021; PP-PR-062 |

### PP-ADR-005 Dùng chung một hàm tính trạng thái ngang với khối Chức năng ADAS {#adr-005}

| Mục | Nội dung |
|---|---|
| Bối cảnh | Khối Chức năng ADAS (tính TLC) và planner (lập path can thiệp) cần cùng trạng thái ngang đo được |
| Phương án | A) Chung một hàm, cùng input. B) Planner tự tính. C) Khối Chức năng ADAS gửi trạng thái trong message |
| Quyết định | A. Bị thay bởi PP-ADR-014 |
| Hệ quả | Được: hai bên cùng một con số. Mất: hai khối phụ thuộc chung một thư viện. B có thể vênh (TLC 1,0 s so với 1,3 s); C thêm khoảng 20 ms trễ và planner vẫn phải tự tính cho LCC |
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
| Bối cảnh | LCC dời tâm khi có xe lớn ở làn bên (đề bài). Path không được dịch về phía làn mở rộng (mentor). Planner phải chạy cho mọi bề rộng làn 2,5–5,5 m và mọi xe rộng tới 2,5 m |
| Phương án | A) Khoảng hở tới mép đường thô, offset cố định ±0,3 m. B) Cân bằng khoảng hở hai bên, bên trống lấy biên làn của reference line. C) Dời ra xa xe lớn phần khoảng hở còn thiếu so với `gap_truck_min`; xe lớn ở cả hai bên thì cân bằng hai khoảng hở. B và C đều giới hạn offset theo khoảng trống thật |
| Quyết định | C (2026-11-11, thay B). Công thức ở Software Architectural Design mục 6; o_lim = max(0, min(`offset_max`, s − `dlc_offset_min`)), s = (W_làn − W_xe) / 2. B bị bỏ vì xe lớn ở giữa làn bên thì khoảng hở tới nó lớn hơn khoảng hở tới biên làn: B không dời, hoặc dời về phía xe lớn. Dòng một xe lớn bị thay bởi PP-ADR-020 (2026-11-18) |
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
| Quyết định | C (mentor). Chỉ LCC lái trên tâm làn suy ra; LKA, ELK cần vạch làn mình đủ tin (mentor) |
| Hệ quả | Được: LCC chạy tiếp khi làn mình mất vạch; mở rộng từ cơ chế "một vạch cộng bề rộng nhớ được"; planner giữ toàn bộ phần kiểm tính nhất quán. Mất: tâm làn suy từ biên xa có sai số lớn hơn; sai khi bề rộng làn bên đổi trong lúc mất vạch. A bỏ phí dữ liệu; B làm planner không phân biệt được vạch đo với vạch dựng |
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
| Quyết định | B. PathStatus có `lka_phase` và `elk_phase`; từ Interface Control Document 1.13 là InterventionStatus của LKA/ELK planner (PP-ADR-016). Mỗi pha giữ COMPLETED tới khi yêu cầu tương ứng rời REQUEST |
| Hệ quả | Một message có thể công bố ELK COMPLETED cùng LKA ACTIVE. Bên phát và bên nhận phải dùng cùng phiên bản schema |
| Liên quan | PP-TS-011, PP-SWR-032, 033, 041, Interface Control Document mục 6.2 |

### PP-ADR-016 Tách LCC planner và LKA/ELK planner; arbitrator thuộc công ty {#adr-016}

| Mục | Nội dung |
|---|---|
| Bối cảnh | Mentor (2026-11-18) đưa arbitrator ra khỏi phạm vi thực tập: công ty đã có, nhóm viết hai planner để ghép vào. Bộ 1 cho LCC, bộ 2 cho LKA và ELK |
| Phương án | A) Một planner ba chức năng, arbitration trong planner (thiết kế trước). B) Hai planner độc lập, mỗi planner một thư viện C11, arbitrator của công ty chọn path. C) Hai planner trong một thư viện, hai API |
| Quyết định | B. Hai thư viện cùng mã lõi (input check, T2, T4, T6, T10, T11), biên dịch riêng, không chia sẻ trạng thái lúc chạy. Contract gọi hàm riêng (`pp_lcc_`, `pp_lkaelk_`). Quy tắc chọn của arbitrator là giả định PP-ASM-022. Mỗi planner phải đúng khi planner kia không chạy (PP-SWR-181) |
| Hệ quả | Được: khớp cách công ty ghép; kiểm thử riêng từng planner; bỏ phần arbitration giữa LCC, LKA, ELK. Mất: sinh hai bộ schema, API, adapter; path của LCC planner phải sẵn sàng từ vị trí thật của xe mọi lúc (PP-SWR-039, 040); thời gian tính hai planner cộng lại trong một chu kỳ; kết quả benchmark trước đó không so trực tiếp được |
| Liên quan | PP-ASM-022; PP-SWR-019, 039, 040, 180, 181; Software Architectural Design mục 3; Interface Control Document mục 4, 6 |

### PP-ADR-017 Giữ LKA và ELK là hai chức năng riêng trong LKA/ELK planner {#adr-017}

| Mục | Nội dung |
|---|---|
| Bối cảnh | Mentor đề nghị gộp LKA và ELK thành một chức năng vì thời gian còn lại ngắn. LKA là CSF (R79 2.3.4.2 c). ELK vạch và mép đường là CSF theo ELKS (EU 2021/646); ELK với xe ở làn bên là ESF (R79 2.3.4.3 a). Euro NCAP chấm hai bộ test riêng (LSS 7.2.4, 7.2.5). Tài liệu, mã nguồn và test của hai chức năng đã có riêng |
| Phương án | A) Gộp thành một chức năng, một ngưỡng kích hoạt. B) Hai chức năng riêng, chọn ELK > LKA trong cùng planner |
| Quyết định | B (2026-11-18). Ngưỡng cắt 10 cm và 0,15 m/s của mentor áp cho cả hai (PP-ASM-028) |
| Hệ quả | Được: đúng bản chất hành vi và tiêu chuẩn; giữ test và tài liệu đã có; giới hạn a_y, jerk, DTLE và pha riêng từng chức năng. Mất: thêm một bước chọn nhỏ (ELK > LKA); giữ hai bộ tham số `T_lka`, `T_elk` |
| Liên quan | PP-SWR-030 đến 041, 110 đến 115; Software Architectural Design mục 5, 7; ADAS Function Specification mục 3, 9 |

### PP-ADR-018 Bám xe trước bằng reference line ảo dựng từ vết xe trước {#adr-018}

| Mục | Nội dung |
|---|---|
| Bối cảnh | Mentor: khi mất cả hai vạch làn mình, LCC bám xe trước tối đa 30 m. Input: tâm xe trước, khoảng cách bumper, heading, vận tốc tương đối. Trong cua, y của xe trước trong `base_link` lệch tới 3,0 m ở 30 m (R = 150 m) |
| Phương án | A) Đoạn Hermite từ xe mình tới vị trí hiện tại của xe trước. B) Vết xe trước: lưu vị trí xe trước theo thời gian, dời bằng ego-motion, khớp đa thức. C) Bám path cũ tới hết `T_coast` |
| Quyết định | B, điều kiện vào và duy trì đo theo tâm làn gốc. A bị bỏ vì trong cua đường nối cắt vào trong; vết cho đường đi đúng chỗ xe trước đã đi. C không bám được quá 1 s (PP-ADR-009) |
| Hệ quả | Được: path đi theo chỗ xe trước đã đi; không cần mô hình xe trước. Mất: bộ đệm vết cỡ cố định (`trail_n`); vết phải ghi từ lúc còn vạch; chất lượng phụ thuộc nhiễu vị trí xe trước; tối đa 30 m |
| Liên quan | PP-SWR-170 đến 178; PP-ASM-024, 025, 027; Software Architectural Design mục 6.3; Software Detailed Design mục 5.1 (T12) |

### PP-ADR-019 Hành lang can thiệp cập nhật bất đối xứng khi biên nhảy {#adr-019}

| Mục | Nội dung |
|---|---|
| Bối cảnh | Mentor: ở mép đường lane model có thể báo biên nhảy ra xa hơn thực tế, nên planner đẩy xe về làn rồi kéo ra. Path can thiệp lấy mẫu trên reference line của từng chu kỳ, nên biên nhảy thì path dời theo. Điều kiện kết thúc mới (10 cm, 0,15 m/s) cũng tính trên reference line đó |
| Phương án | A) Giữ reference line từng chu kỳ, dựa vào T2 lọc nhảy. B) Hành lang chốt lúc bắt đầu; biên dịch vào phía xe nhận ngay, dịch ra xa chờ `T_confirm`. C) Hành lang cố định tới hết can thiệp |
| Quyết định | B. A bỏ vì T2 nhận thay đổi thật sau `T_confirm`, trong lúc đó path đã dời. C bỏ vì không theo được thay đổi thật của làn |
| Hệ quả | Được: biên nhảy ra xa không kéo xe ra; biên dịch vào vẫn nhận ngay; không báo COMPLETED sai. Mất: làn rộng ra thật thì xe vẫn về tâm làn cũ ít nhất `T_confirm`; thêm trạng thái hành lang |
| Liên quan | PP-SWR-084, 093, 094; Software Architectural Design mục 7.2; Software Detailed Design T9 bước 7 |

### PP-ADR-020 Dời 10 cm khi một xe lớn, hai xe lớn giữ cân bằng khoảng hở {#adr-020}

| Mục | Nội dung |
|---|---|
| Bối cảnh | PP-ADR-008 dời theo phần khoảng hở còn thiếu so với `gap_truck_min`. Mentor (2026-11-18): tránh xe tải bằng cách lệch 10 cm về phía còn lại nếu làn bên cạnh không có xe tới |
| Phương án | A) Giữ PP-ADR-008. B) Mọi ca lệch cố định 10 cm; hai bên có xe thì không lệch. C) Một xe lớn: lệch 10 cm khi làn bên kia không có xe tới; hai xe lớn: giữ cân bằng của PP-ADR-008 |
| Quyết định | C. Thay PP-ADR-008 ở dòng một xe lớn. Hai xe lớn giữ cân bằng vì mentor chưa nêu ca này và cân bằng không bao giờ dời về phía xe có khoảng hở nhỏ hơn (PP-SWR-056) |
| Hệ quả | Được: khớp mentor; vẫn xử lý được ca hai xe tải. Mất: một xe lớn rất gần thì 10 cm không đủ đạt `gap_truck_min`; ưu tiên an toàn bên kia (PP-SWR-065) |
| Liên quan | PP-SWR-055, 056, 065, 066; Software Architectural Design mục 6 |

## Revision history {#revision-history}

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 2026-11-10 | Refactor thành Architecture Decision Records, baseline BL1. Mọi quyết định là đã quyết; PP-ADR-008 giới hạn offset theo khoảng trống thật; PP-ADR-009 dùng `T_coast` ≤ 1 s; thêm PP-ADR-012; bỏ nhãn trạng thái và việc mở |
| 1.1 | 2026-11-10 | Thêm PP-ADR-013: planner là thư viện C11 có API C, tách adapter theo nền tảng |
| 1.2 | 2026-11-10 | Thêm PP-ADR-014: planner tự tính trạng thái ngang; PP-ADR-005 bị thay |
| 1.3 | 2026-11-11 | PP-ADR-008 chọn C thay B: dời theo khoảng hở tới xe lớn so với `gap_truck_min` |
| 1.4 | 2026-11-12 | Thêm PP-ADR-015 về pha riêng cho LKA và ELK trong PathStatus |
| 1.5 | 2026-11-16 | PP-ADR-004 chọn D thay C: trộn path cũ và trạng thái đo theo độ lệch. Lý do: PP-TS-021 (20261116-1748-study-PP-TS-021-8726b80); với C, xe đứng sát dưới `stitch_reset` và controller kéo thêm a_y (PP-PR-056); ngưỡng nhỏ thì path đổi qua lại mỗi chu kỳ |
| 1.6 | 2026-11-17 | PP-ADR-004: hệ quả lúc LKA, ELK bắt đầu theo SRS 1.23 (PP-PR-062) |
| 1.7 | 2026-11-18 | Thêm PP-ADR-016 đến 020: tách hai planner, giữ LKA và ELK riêng, bám xe trước, hành lang can thiệp, dời 10 cm (thay một phần PP-ADR-008); PP-ADR-015 chuyển sang InterventionStatus. Lý do: mentor đổi sản phẩm ngày 18/11 (SRS 1.24) |

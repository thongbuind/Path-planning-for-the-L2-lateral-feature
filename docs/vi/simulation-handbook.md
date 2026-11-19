# Simulation Handbook

| Mục | Nội dung |
|---|---|
| Mã tài liệu | `SIM-HB` |
| Phiên bản | 1.0 |
| Trạng thái | v1 |
| Tác giả | thongbui |
| Người review | thongbui |
| Cập nhật | 2026-11-19 |

## 1. Purpose and scope {#hb-scope}

- **Mục đích.** Ghi lại simulator và bên chấm của Path Planning tin được tới đâu: có gì, làm gì, giả định gì, đã kiểm chứng gì, chưa validation gì. Bố cục theo UN R171 Annex 5 §4.1.
- **Dùng để.** Tìm lỗi của hai path planner ở mức requirement. So sánh phiên bản planner. Chứng minh planner tích hợp được (B0).
- **Không dùng để.** Chứng nhận kiểu loại. Ước lượng năng lực của xe thật. Suy ra WCET của ECU. Kết luận cho xe hoặc điều kiện ngoài miền dùng của từng model (mục 9).
- **Phạm vi.** Simulator (`sim/`), adapter SIL, bên chấm (`eval/`), lõi thực thi (`execution/`), workbench. SUT là cặp thư viện `libpp_lcc` và `libpp_lkaelk` (PP-ADR-016).
- **Ngoài phạm vi.** Requirement của planner (Software Requirements Specification). Thiết kế phép thử (Software Qualification Test Specification).
- **Nội dung.** Mục 3 đến 9 mô tả công cụ. Mục 10 đến 16 là đánh giá độ tin cậy. Mục 17 là kết luận. Mục 18 là yêu cầu của chính công cụ (`SIM-REQ`).

## 2. References {#hb-references}

| Tài liệu | Dùng cho |
|---|---|
| UN R171 (OJ L 2025/1899) §8.2.1, Annex 3 §4.2, Annex 5. Bản text: `docs/reference/standards/un-r171-oj-l-2025-1899.txt` | Khung credibility assessment: năm thuộc tính, quản lý M&S, verification, validation, uncertainty |
| ISO 26262-8:2018 mục 11 | Tool confidence: TI, TD, TCL. Chưa có bản chính thức trong thư viện chuẩn của dự án; mục 11 dùng cách hiểu của nhóm |
| ISO 21448:2022 | Giới hạn của kết luận: còn tình huống nguy hiểm chưa biết |
| [Software Qualification Test Specification](report.html?doc=path-planner-software-qualification-test-specification&lang=vi) | Cấu hình dùng cho planner (mục 4), tiêu chí đạt (mục 8), kiểm bên chấm (mục 12) |
| [Software Requirements Specification](report.html?doc=path-planner-software-requirements-specification&lang=vi) | Requirement của planner; nguồn của mọi criterion |
| [Interface Control Document](report.html?doc=path-planner-interface-control-document&lang=vi) | Interface duy nhất bên chấm được quan sát |
| Roy, C. J. (2005), Review of code and solution verification procedures for computational simulation, Journal of Computational Physics 205(1), 131–156 | Code verification, calculation verification |
| ASAM OpenSCENARIO XML 1.3.1, OpenDRIVE 1.8.1 | Định dạng kịch bản và đường |

## 3. Quản lý M&S {#hb-management}

| Mục | Quy định |
|---|---|
| Phiên bản toolchain | Simulator, bên chấm, adapter và lõi thực thi cùng một commit git. Thư viện planner có chuỗi `pp_version()` (tên, phiên bản, commit, mã bộ calibration) và sha256 |
| Truy từ kết quả về phiên bản | Mỗi kết quả có `manifest.json`: lệnh, commit và cây làm việc sạch hay không, sha256 và `pp_version` của từng thư viện, sha256 của mọi file benchmark và calibration, seed, phiên bản Python và numpy, `simulator` (mục 6) |
| Định danh ca và hành vi | `case_hash` (ResolvedCase theo `c14n/1`) và `behavior_checksum/2` (mục 6) |
| Review trước khi dùng kết quả | Lần chạy chính thức `--record` đòi cây làm việc đã commit và thư viện build từ đúng commit. Trước baseline: `eval.selfcheck` (planner mồi), `eval.golden check`, `tools/trace.py`, CI |
| Thay đổi simulator hoặc bên chấm | Sửa làm đổi hành vi phải đi qua problem report `PP-PR`, ghi checksum cũ và mới, và ghi lại mốc golden. Sửa giữ hành vi phải giữ nguyên `behavior_checksum` |
| Kết quả cũ | Giữ nguyên ở `research/runs/`. Không so `behavior_checksum` khác phiên bản |

Quyết định về nền tảng:

| Quyết định | Lý do |
|---|---|
| CLI, web, suite dùng chung một hàm thực thi và một định dạng kết quả | Một nguồn sự thật; đo bằng `behavior_checksum` |
| Chấm lại bằng cách chạy lại tất định; MCAP chỉ để xem | MCAP làm tròn 6 chữ số; lưu trace mọi lượt suite tốn khoảng 15 GB |
| Run độc lập với tab trình duyệt; bundle bất biến | Đóng tab không mất run; kết quả không bị sửa sau khi ghi |
| Một server cục bộ cộng tiến trình worker, không database | Một người dùng, máy 8 GB |
| Giữ MCAP writer tự viết, không dùng esmini | Writer đọc được bằng Foxglove; hai việc đó không phục vụ câu hỏi kiểm thử hiện tại |
| Không có debug channel trong output của planner | Chấm hộp đen; lý do hành vi lấy từ interface |
| Mô hình xe, cảm biến và stand-in tăng độ chi tiết theo câu hỏi kiểm thử | Ảnh đẹp không phải thước đo độ tin cậy |

## 4. Kinh nghiệm và năng lực {#hb-competence}

| Vai trò | Người | Ghi chú |
|---|---|---|
| Xây công cụ | thongbui | Một người |
| Validate và verify công cụ | thongbui | Cùng người xây, không có reviewer độc lập |
| Dùng công cụ để đánh giá planner | thongbui; mentor đọc báo cáo | |

Biện pháp bù cho việc một người kiêm các vai:

- Bộ planner mồi cố ý sai ở mười điểm (PM-01 đến PM-10): bên chấm phải bắt được trước khi kết quả được dùng (mục 12).
- Golden set: 14 ca có `behavior_checksum` cố định; mọi thay đổi giữ hành vi phải giữ nguyên.
- CI chạy trên máy khác và hệ điều hành khác với máy phát triển.
- Mentor đọc kết quả và tài liệu này.

## 5. Nguồn gốc dữ liệu đầu vào {#hb-inputs}

Nguồn chi tiết của từng tham số nằm ở cột Nguồn tham số của mục 9. Tóm tắt theo loại:

| Dữ liệu | Nguồn | Ghi chú |
|---|---|---|
| Kích thước, khối lượng, bán kính quay vòng của VP-1 đến VP-4 | Thông số kỹ thuật công bố của hãng | VP-0 là giá trị điển hình; VP-5 là profile biên |
| Độ cứng lốp, mô-men quán tính, tỉ số lái, trễ chấp hành | nhóm tự thống nhất | Không có dữ liệu xe thật; cùng giá trị cho mọi profile |
| Nhiễu IMU | Bosch SMI230 (bản giới thiệu sản phẩm 2018) | Cảm biến thô, nên là cận trên của tín hiệu đã lọc |
| Nhiễu camera, ObjectList, tốc độ, góc lái, v_y | nhóm tự thống nhất | Chưa có số đo camera thật (PP-ASM-020) |
| Điều kiện kịch bản LKA, ELK | Euro NCAP LSS Test Protocol v4.3, EU 2021/646 Annex I Part 2, UN R79 Annex 8, UN R171 Annex 4 | Bản đã tải ở `docs/reference/standards/` |
| Hành vi ACC chạy thử | ISO 15622:2018 | Phần còn lại: nhóm tự thống nhất |
| Calibration của planner | `planner/calibration/calibration.yaml`, sha256 ghi trong manifest | |
| Kịch bản, đường, lỗi | `benchmark/` (OpenSCENARIO 1.3.1, OpenDRIVE 1.8.1), sha256 ghi trong manifest | |

Tham số không có nguồn ngoài nhóm: độ cứng lốp, I_z, tỉ số lái, trễ chấp hành, hằng số EPS, tầm nhìn camera 0 đến 80 m, mọi tham số của stand-in. Quét nhiều mức khi có thể (Q1 đến Q4) và ghi ở mục 16.

## 6. Nguồn gốc dữ liệu đầu ra {#hb-outputs}

Mỗi lần chạy một ca để lại một bundle (`build/runs/<run_id>/`):

| File | Nội dung |
|---|---|
| `manifest.json` | Provenance (mục 3), `bundle` (`run_id`, `parent_run_id`, `case_hash`, `behavior_checksum`, phiên bản schema, `time_domains`, `recipe`), `simulator` (commit, phiên bản checksum, danh sách model và trạng thái validation) |
| `resolved-case.json` | Scenario mà simulator thực sự nhận, theo `c14n/1`, kèm sha256 mọi file đầu vào |
| `evaluation.json` | Criterion, performance target, issue, kèm commit của bên chấm |
| `execution.json` | Trạng thái, lớp lỗi, `complete`, file bắt buộc còn thiếu |
| `trace.mcap` | Log để xem bằng Foxglove, làm tròn 6 chữ số; không dùng để chấm |
| `frames.ndjson.gz` | Run live: luồng khung hình để playback |
| `worker.log`, `SHA256SUMS` | Stdout, stderr của worker; sha256 mọi file, ghi cuối cùng |

| Quy tắc | Nội dung |
|---|---|
| Ghi bundle | Vào thư mục tạm, đổi tên sau khi ghi `SHA256SUMS`; không sửa sau đó |
| `case_hash` | sha256 của Scenario chuẩn hóa `c14n/1`: key sắp thứ tự, float theo `repr`, không NaN |
| `behavior_checksum/2` | Băm toàn bộ RunLog trừ thời gian tính và đầu vào; float IEEE-754 binary64; cùng ca, seed, thư viện, commit, máy thì cùng checksum, không đổi theo số tiến trình, observer, tốc độ phát |
| Seed | `numpy.random.SeedSequence.spawn`, một luồng riêng cho từng kênh; chạy lại tất định |
| Miền đồng hồ | Mọi thời điểm ở miền `sim` (đồng hồ chung). Ngoại lệ: `stamp_us` và `rx_us` của planner ở miền `adas`, `lane_capture_us` ở miền `camera` (`manifest.bundle.time_domains`) |
| Lần chạy chính thức | `--record` sao chép manifest và kết quả vào `research/runs/<run-id>/` và thêm một dòng vào `research/runs/INDEX.md` |

## 7. Toolchain {#hb-toolchain}

| Lớp | Package | Vai trò |
|---|---|---|
| Lõi thực thi chung | `execution/` | Tiến trình worker, timeout, cancel, bundle, `c14n`. Chỉ import thư viện chuẩn |
| Server | `workbench/` | API cục bộ trên `127.0.0.1`; không import code của SUT |
| Simulator | `sim/` | Scheduler 1 ms, đồng hồ ECU, kênh, mô hình xe, cảm biến, stand-in, lỗi |
| Adapter SIL | `adapters/sil/` | Nạp hai thư viện C qua ctypes, cấu trúc theo `interfaces/c/pp_planner.h` |
| Bên chấm | `eval/` | Criterion, kết luận, báo cáo, planner mồi, golden, studies |
| Kịch bản | `benchmark/` | OpenSCENARIO, OpenDRIVE, lỗi, suite |
| Giao diện | `web/simulation/` | UI tĩnh gọi HTTP, không import code |

Quy tắc import được giữ bằng `tests/test_import_rules.py`.

| Khối | Thật hay chạy thử |
|---|---|
| LCC planner, LKA/ELK planner | Thật: thư viện C của SUT |
| Arbitrator | Chạy thử (PP-ASM-022); thuộc phía kiểm thử |
| Chức năng ADAS (LKA, ELK, bám xe), tài xế | Chạy thử |
| Lateral Controller, EPS, ACC | Chạy thử |
| Mô hình xe, cảm biến, kênh, đồng hồ | Mô hình |

Chế độ chạy: tất định một tiến trình mỗi lượt, bước 1 ms. Vòng kín (path qua controller và EPS vào mô hình xe) và vòng hở (xe đi theo quỹ đạo định sẵn). Chế độ thời gian thực nhiều tiến trình chưa triển khai. Môi trường: máy phát triển macOS arm64, Python 3.13, numpy 2.x; CI trên Ubuntu.

Một lần chạy: dựng ca (`resolve`), mô phỏng (`simulate`), chấm (`evaluate`), ghi bundle (`write`).

## 8. Capability matrix {#hb-capability}

| Mục | Hỗ trợ |
|---|---|
| Kịch bản | 28 họ: S1, S1b, S2, S3, S3b, S4, S4b, S5, S6, S6b, S7, S8, S8b, S8c, S9 đến S17, S19 đến S23; mỗi họ có anchor, dải và biến thể |
| Lỗi | 24 lỗi: F01 đến F08, F10 đến F25 (lane model, IMU, kênh, đồng hồ, ego-motion, LeadTarget...), có thể ghép và gắn vào sự kiện của planner |
| Vehicle profile | 6: VP-0 đến VP-5 |
| Đường | Tập con OpenDRIVE 1.8.1: đường cong, làn đổi bề rộng, vạch liền, đứt, kép, mép đường, rào chắn |
| Kịch bản | Tập con OpenSCENARIO 1.3.1, một ego; mở rộng riêng bằng `pp:*` |
| Vòng chạy | Vòng kín, vòng hở |
| Giao thông | Xe theo kịch bản, không phản ứng với xe thử |
| Môi trường | μ mặt đường, nhiễu ObjectList, trễ camera, gió ngang, đường nghiêng |
| Bên chấm | Criterion theo Software Requirements Specification, performance target, kiểm B0, kiểm bên chấm bằng planner mồi |

Ngoài khả năng của công cụ:

| Điều không hỗ trợ | Hệ quả cho kết luận |
|---|---|
| Xe giao thông phản ứng với xe thử | Không kết luận về tương tác hai chiều |
| OpenSCENARIO đa ego, điều kiện phức tạp, nút giao | Chỉ ca viết trong tập con |
| Chế độ thời gian thực nhiều tiến trình | Không kiểm jitter của hệ điều hành |
| Chuyển tải, hệ treo, mặt đường gồ ghề, phanh gấp | Chỉ đúng ở a_y thấp của LCC, LKA, ELK (mục 9.1) |
| Chấm lại từ MCAP | Chấm lại bằng chạy lại tất định |
| Hai hệ điều hành cho cùng bit | `behavior_checksum` chỉ so trong cùng máy |

## 9. Giả định, giới hạn và nguồn uncertainty theo model {#hb-models}

Mỗi model có đủ sáu ý theo `SIM-REQ-120`. Trạng thái validation của cả chín model được ghi vào manifest và báo cáo (`SIM-REQ-121`).

### 9.1 Mô hình xe {#hb-model-vehicle}

| Mục | Nội dung |
|---|---|
| Mục đích | Tạo chuyển động thật của xe trong vòng kín để đo DLC, a_y, lệch tâm |
| Giả định | Bicycle động lực học: trạng thái x, y, ψ, v_y, r; lốp tuyến tính F = C·α, mỗi trục ≤ μ·F_z; RK4 bước 1 ms; l_f = l_r = chiều dài cơ sở / 2; dưới 3 m/s chuyển dần sang kinematic; tốc độ dọc là đầu vào |
| Nguồn tham số | VP-1 đến VP-4: thông số công bố. C_f = 100.000 và C_r = 140.000 N/rad trên 2000 kg, I_z = 0,83·m·l_f·l_r, tỉ số lái 15, trễ chấp hành 50 ms: nhóm tự thống nhất (Software Qualification Test Specification 4.4) |
| Miền dùng | a_y thấp của LCC, LKA, ELK (tới khoảng aysmax); tốc độ từ 3 m/s đến 130 km/h; μ 0,5 đến 1,0. Ngoài miền: bỏ qua chuyển tải, hệ treo, gồ ghề, phanh gấp, bão hòa lốp mạnh |
| Verification | `test_steady_state_yaw_rate` so r = v·δ / (L + K·v²), sai tương đối 1e-3; hội tụ RK4 (mục 13); độ nhạy tham số (mục 14) |
| Validation | Chưa validation: không có dữ liệu xe thật |

### 9.2 Lateral Controller và EPS chạy thử {#hb-model-controller}

| Mục | Nội dung |
|---|---|
| Mục đích | Biến path thành góc lái trong vòng kín, cố định cho mọi phiên bản planner |
| Giả định | Controller 100 Hz: δ = L·κ + K·v²·κ + k_y·e_y + k_ψ·e_ψ, điểm nhìn trước 0,5 s. EPS bám góc yêu cầu: trễ thuần theo `actuator_delay`, khâu bậc một τ = 0,1 s, giới hạn tốc độ và góc. Path quá 75 ms hoặc không hợp lệ thì giữ lệnh cuối, EPS trả quyền lái trong 1 s. EPS nhận góc, không nhận mô-men như EPS L2 thật |
| Nguồn tham số | nhóm tự thống nhất; K lấy từ mô hình xe; k_y, k_ψ chỉnh một lần rồi cố định |
| Miền dùng | Path hợp lệ và tới đúng tần số; mô-men tài xế dưới `torque_override` hoặc đã định sẵn theo ca |
| Verification | `tests/sim/stand_ins/test_lateral_controller.py` (12 test); S1a: lệch tâm xe thật 0,009 m |
| Validation | Chưa validation: stand-in theo đặc tả, không có khối thật để đối chiếu |

### 9.3 ACC chạy thử {#hb-model-acc}

| Mục | Nội dung |
|---|---|
| Mục đích | Cấp LongitudinalPlan và tốc độ dọc cho LCC planner, đóng vòng dọc |
| Giả định | Chế độ OFF, CRUISE, FOLLOW, CURVE_LIMIT; lệnh gia tốc nhỏ nhất của ba luật; gia tốc từ −3,0 đến +1,5 m/s², jerk ≤ 2,5 m/s³; không có AEB; chấp hành trễ 0,1 s và khâu bậc một τ = 0,3 s |
| Nguồn tham số | Cấu trúc và khoảng thời gian bám 1,8 s theo ISO 15622:2018 6.1, 6.2; hệ số và giới hạn: nhóm tự thống nhất |
| Miền dùng | Chạy dọc đường của kịch bản; xe mục tiêu cùng chiều |
| Verification | `tests/sim/stand_ins/test_acc.py` (10 test) |
| Validation | Chưa validation: stand-in theo đặc tả, không có khối thật để đối chiếu |

### 9.4 Tài xế và Chức năng ADAS chạy thử {#hb-model-adas}

| Mục | Nội dung |
|---|---|
| Mục đích | Tạo lần trôi làn, FunctionRequests (LCC, LKA, ELK) và LeadTarget để chấm planner |
| Giả định | Tài xế giả đặt cung trôi rồi thả lực điều khiển; stand-in LKA, ELK tính DLC, TLC, ý định, nguy cơ; chế độ B dùng tín hiệu lý tưởng, chế độ A dùng message nhận được; stand-in bám xe gửi LeadTarget từ ground truth; yêu cầu định sẵn cho ca không cần stand-in |
| Nguồn tham số | Euro NCAP LSS 7.2.2 đến 7.2.5, EU 2021/646 Annex I Part 2 5.3.3.1, ADAS Function Specification; còn lại nhóm tự thống nhất |
| Miền dùng | Các ca đã viết ở Software Qualification Test Specification 5; không đại diện cách phát hiện lệch làn của khối thật |
| Verification | `tests/sim/stand_ins/test_adas_function.py`, `test_driver.py`, `test_hwa_view_gate.py`, `tests/sim/test_adas_harness.py` |
| Validation | Chưa validation: stand-in theo đặc tả, không có khối thật để đối chiếu |

### 9.5 Arbitrator chạy thử {#hb-model-arbitrator}

| Mục | Nội dung |
|---|---|
| Mục đích | Chọn path của LCC planner hay của LKA/ELK planner cho vòng kín |
| Giả định | Chọn LKA/ELK planner khi `active_function` khác NONE và `Trajectory.header.valid = true`, ngược lại chọn LCC planner (PP-ASM-022); không trễ chuyển |
| Nguồn tham số | Giả định của nhóm; arbitrator thật thuộc hệ thống của công ty, chưa có xác nhận |
| Miền dùng | Kết luận về chuyển path chỉ đúng với quy tắc đã giả định |
| Verification | `test_arbitrator_picks_lka_elk_only_while_it_drives_with_a_valid_trajectory` và `test_arbitrator_reports_none_when_lcc_is_not_driving` (`tests/sim/test_follow_mechanisms.py`); ca S5 a |
| Validation | Chưa validation: quy tắc thật của hệ thống chưa được xác nhận |

### 9.6 Camera và lane model {#hb-model-camera}

| Mục | Nội dung |
|---|---|
| Mục đích | Tạo lane model mà planner nhận, kể cả lỗi |
| Giả định | Hình học làn trong tầm nhìn đưa về `base_link`, khớp đa thức bậc 3 cho từng vạch và mép đường; tầm nhìn danh định 0 đến 80 m, riêng từng vạch; trễ chụp đến gửi 100 ms; báo σ_c0 = 0,03 m, σ_c1 = 0,002 (mức F01 a); vạch vắng báo LOST. Mốc không nhiễu có ở mọi kịch bản |
| Nguồn tham số | nhóm tự thống nhất, chờ số đo camera thật (PP-ASM-020). Điểm đầu 0 m là giả định lạc quan vì nắp capo che đường gần xe. Trễ 100 ms dưới mức xấu nhất 120 ms của PP-ASM-001; mức khác quét ở Q1 |
| Miền dùng | Đường là tập con OpenDRIVE (mục 8); không có chói nắng, vạch mờ theo ảnh hay lỗi nhận dạng theo nội dung ảnh |
| Verification | `tests/sim/test_sensors.py`, `tests/sim/test_road.py`, `tests/sim/test_lane_widening.py`; kiểm bên chấm bằng ca F01 đến F06 |
| Validation | Chưa validation: không có log camera thật có ground truth |

### 9.7 Cảm biến đối tượng và traffic {#hb-model-objects}

| Mục | Nội dung |
|---|---|
| Mục đích | Tạo ObjectList và LeadTarget cho S7, S8, S22, S23 và các ca có xe khác |
| Giả định | Vật thể của kịch bản đưa về `base_link`; tầm phát hiện 150 m phía trước, 80 m phía sau; nhiễu x, y, vx, vy, kích thước; bỏ sót 2 % frame; vật thể ảo 0,05 lần/s; mưa nhân σ với 1,5. Xe giao thông đi theo kịch bản, không phản ứng |
| Nguồn tham số | nhóm tự thống nhất; đồng bộ xe mục tiêu S7, S8 theo Euro NCAP LSS 7.2.4.3, 7.2.4.4 |
| Miền dùng | Xe chạy theo kịch bản trên cùng đường; không có tương tác hai chiều |
| Verification | `tests/sim/test_traffic.py`, `tests/sim/test_follow_mechanisms.py` |
| Validation | Chưa validation: không có log cảm biến thật |

### 9.8 Đồng hồ ECU, kênh truyền, lỗi timing {#hb-model-timing}

| Mục | Nội dung |
|---|---|
| Mục đích | Cho planner thấy trễ, jitter, mất gói, stamp lệch đồng hồ như trên xe |
| Giả định | Scheduler bước 1 ms, thứ tự cố định; kênh có trễ cộng jitter đều và xác suất mất; bên nhận giữ message mới nhất và kiểm counter, CRC, qualifier; bus CAN ảo theo DBC. Đồng hồ ECU: trôi tới ±100 ppm, lệch đầu ±10 ms, đồng bộ kiểu gPTP mỗi 125 ms với sai số ±50 µs |
| Nguồn tham số | nhóm tự thống nhất (Software Qualification Test Specification 4.2, 4.3) |
| Miền dùng | **Kịch bản danh định chạy đồng hồ lý tưởng, không làm tròn CAN** (`realism` tắt). Trôi đồng hồ, mất đồng bộ và làm tròn CAN chỉ có ở F14, F15 đến F19 và ca nào bật `pp:can_bus` hoặc `pp:realism` |
| Verification | `tests/sim/test_runtime.py`, `test_faults.py`, `test_fault_mechanisms.py`; ca F10 đến F19 |
| Validation | Chưa validation: không có log thời gian của xe thật |

### 9.9 Fault injector {#hb-model-faults}

| Mục | Nội dung |
|---|---|
| Mục đích | Bơm lỗi vào lane model, IMU, kênh, đồng hồ, ego-motion, LeadTarget đúng thời điểm theo ca hoặc theo sự kiện của planner |
| Giả định | Lỗi có hình dạng do bên test chọn, mức theo datasheet hoặc quét; trigger theo sự kiện (`lka_active`, `elk_active`, `lcc_follow`...) |
| Nguồn tham số | Bosch SMI230 cho nhiễu IMU; còn lại nhóm tự thống nhất |
| Miền dùng | Lỗi trong danh mục F01 đến F25; không bao phủ lỗi chưa biết |
| Verification | `fault_hits`: mỗi lượt ghi số lần lỗi thật sự được bơm; lỗi không được bơm thì criterion phụ thuộc thành `not_judged` (SIM-REQ-062); test `test_fault_never_injected_is_not_judged_as_passed` |
| Validation | Không áp dụng: không phải mô hình vật lý; kiểm bằng `fault_hits` và `not_judged` |

## 10. Criticality assessment {#hb-criticality}

Theo UN R171 Annex 5 §3.5.5: hai trục là hậu quả nếu quyết định dựa trên kết quả sai, và mức kết quả mô phỏng ảnh hưởng tới quyết định. Trục hậu quả lấy theo mức của Software Qualification Test Specification 8.4.

| Thành phần | Ảnh hưởng tới kết luận về planner | Hậu quả nếu sai | Mức |
|---|---|---|---|
| Evaluator (criterion, kết luận) | Significant: quyết định đạt hoặc trượt | BLOCKER (Safety): Significant | Đầy đủ |
| Mô hình xe, Lateral Controller, EPS | Significant ở vòng kín | Significant với requirement Safety | Verification đầy đủ; validation chưa làm được |
| Arbitrator chạy thử | Significant ở vòng kín | Significant với ca chuyển LCC, LKA, ELK | Verification theo PP-ASM-022; quy tắc thật chưa xác nhận |
| Camera và lỗi lane | Moderate | Significant với ca ELK, LKA | Verification và sensitivity một phần |
| Đồng hồ ECU, kênh, lỗi timing | Moderate | Significant với ca lỗi timing | Một phần |
| Cảm biến đối tượng, traffic | Moderate cho S7, S8 | Moderate | Một phần |
| Fault injector | Significant: lỗi không được bơm thì ca đạt giả | Significant | Đầy đủ (`fault_hits`, `NEVER_S`) |
| Supervisor, bundle, provenance | Minor với hành vi; Significant với truy vết | Moderate | Test vòng đời và checksum |
| MCAP writer | Negligible: chỉ để xem | Minor | Round-trip test (`tests/sim/test_mcap.py`) |
| UI workbench | Negligible vì không tính verdict (SIM-REQ-080) | Minor | Không cần đánh giá đầy đủ |

## 11. Tool confidence {#hb-tool-confidence}

Theo ISO 26262-8:2018 mục 11. Tool impact: TI1 là tool không thể làm lọt lỗi vào sản phẩm, TI2 là có thể. Tool error detection: TD1 là bắt được với độ tin cao, TD3 là khó bắt. Bảng dưới theo cách hiểu của nhóm vì chưa có bản chuẩn chính thức để đối chiếu bảng TCL.

| Tool | TI | Lý do | Cách phát hiện lỗi của tool | TD | TCL |
|---|---|---|---|---|---|
| Evaluator | TI2 | Lỗi có thể biến planner sai thành đạt | Planner mồi PM-01 đến PM-10; ca biên có giá trị tính tay | TD2: chỉ phủ mười loại lỗi cố ý | TCL2 |
| Simulator (mô hình xe, cảm biến) | TI2 | Model sai có thể che lỗi planner | Ca giải tích, sanity check; không có dữ liệu thật | TD3 | TCL3: không qualify được; kết luận giới hạn ở "trong phạm vi đã thử" |
| Fault injector | TI2 | Lỗi không được bơm thì ca đạt giả | `fault_hits`, thời điểm bơm thật, issue `not_judged` | TD1 | TCL1 |
| Supervisor, bundle, provenance | TI2 | Ghi nhầm thư viện thì bằng chứng gắn sai bản | sha256, chạy lại cùng checksum, `SHA256SUMS` | TD1 | TCL1 |
| `tools/trace.py` | TI2 | Thiếu truy vết làm requirement chưa thử trông như đã thử | Cảnh báo mồ côi, review | TD2 | TCL2 |
| UI workbench | TI1 | Không vào verdict | — | — | TCL1 |

Phương pháp qualify cho TCL2 và TCL3 là "validation of the software tool": planner mồi (mục 12) và ca giải tích (mục 12, 13).

## 12. Code verification {#hb-code-verification}

Hai việc đã làm ở mục 13 và 14 (hội tụ bộ giải, độ nhạy tham số) thuộc cùng khung. Bảng này gom phần còn lại, trên commit `36c5c25` và các commit sau đó.

| Hạng mục (Annex 5 §3.6.2) | Bằng chứng | Kết quả |
|---|---|---|
| Unit test của simulator, bên chấm, lõi thực thi, workbench | `python -m pytest` | 528 test trong 52 file, đạt hết |
| Unit test của planner | `ctest --test-dir build/planner` | 17/17 đạt |
| Ca giải tích | `test_steady_state_yaw_rate`: r = v·δ / (L + K·v²) và a_y = v·r | Khớp trong sai số tương đối 1e-3 (r) và 2e-3 (a_y) |
| Hội tụ bộ giải | Mục 13 | Bậc 4,0 ở tốc độ quay và a_y |
| Ranh giới giữa các package | `tests/test_import_rules.py` | Đạt |
| Bên chấm bắt được lỗi cố ý | `eval.selfcheck --jobs 2` ngày 19/11/2026 | 10/10 planner mồi bị báo đúng requirement và mức; PM-00 (đối chứng) trượt PP-SWR-006, 039, 080, 090 nhưng không trượt requirement nào của mười lỗi cố ý |
| Conformance của planner | `eval.conformance` | Đạt C1, C2; Tích hợp được; `C1.layout` không kiểm được từ file thư viện |
| Tất định | `eval.golden check` ở `--jobs 1`, 2, 4 | 14 ca, 41 kết quả, mọi đường cùng checksum |
| Sanity check (§3.6.2 c) | a_y ≈ v·r ở trạng thái ổn định trong `test_steady_state_yaw_rate`; DLC thật tính từ hình học đường | Một phần: chưa có kiểm chéo cho mọi đại lượng |
| Quét dải tham số tìm vùng mất ổn định (§3.6.2 b) | Q1 đến Q4 quét trễ camera, trễ yaw rate, trễ FunctionRequests, tầm nhìn; mục 14 quét ±20 % tham số xe | Một phần: chưa quét tham số mô hình xe để tìm vùng mất ổn định |

## 13. Calculation verification {#hb-calculation}

Lệnh `python3 -m eval.verify_sim calculation`, commit `36c5c25`, thư viện planner build từ `e3158a5`, seed 1. Mốc so sánh là lời giải mịn hơn: 1/16 ms cho mô hình xe đứng riêng, 0,25 ms cho vòng kín.

**Mô hình xe đứng riêng (RK4, ba đầu vào hở).** Góc lái được giữ nguyên trong từng mili giây như bước 1 ms của simulator, nên sai khác là của bộ giải.

| Đầu vào | Vị trí [m] | Hướng [rad] | Tốc độ quay [rad/s] | a_y [m/s²] | Bậc quan sát của tốc độ quay và a_y |
|---|---|---|---|---|---|
| Ôm cua ổn định, 8 s | 2,1e-11 | 5,4e-13 | 3,0e-13 | 1,5e-11 | 4,0 |
| Bước góc lái 0,02 rad, 6 s | 1,7e-12 | 8,0e-14 | 5,1e-13 | 1,9e-11 | 4,0 |
| Góc lái hình sin 0,4 Hz, 10 s | 3,8e-12 | 7,9e-14 | 3,5e-13 | 2,0e-11 | 4,0 |

Sai số ở bước 1 ms. Vị trí và hướng ở mức sai số làm tròn của số thực 64 bit (không quá 2,5e-11 m ở mọi bước), nên bậc của chúng không quan sát được. Tốc độ quay và a_y có bậc 4,0: giảm bước một nửa thì sai số giảm 16 lần, đúng với RK4.

**Vòng kín (cả hai planner), bước 1, 0,5 và 0,25 ms.** Pha của cảm biến và các khối được bốc trên lưới 1 ms cho mọi bước, nên các sự kiện trùng nhau và chỉ khác số bước con của vật lý.

| Ca (criterion theo dõi) | Khoảng cách tới lời giải 0,25 ms, bước 1 ms [mm] | Như trên, bước 0,5 ms [mm] | Giá trị criterion ở 1; 0,5; 0,25 ms [m] | Sai số ước tính của bước 1 ms [mm] |
|---|---|---|---|---|
| S1a (PP-SWR-051, DLC) | 0,105 | 0,035 | 0,78916; 0,78914; 0,78913 | 0,14 |
| S1c (PP-SWR-051, DLC) | 0,767 | 0,256 | 0,74791; 0,74791; 0,74791 | 1,0 |
| S5a (PP-SWR-086, DTLE) | 1,05 | 0,35 | 0,04391; 0,04454; 0,04486 | 1,4 |

- Ở cả ba ca, ở cả ba bước, không requirement nào trong phạm vi chấm bị trượt: kết luận không đổi theo bước.
- Khoảng cách của bước 1 ms bằng đúng ba lần khoảng cách của bước 0,5 ms: sai số của vòng kín là bậc 1 theo bước, thấp hơn bậc 4 của RK4 đứng riêng. Nguyên nhân chưa được tách; giả thuyết là lệnh lái được giữ nguyên trong một bước.
- Sai số ước tính của bước 1 ms là 4/3 khoảng cách đã đo (ngoại suy bậc 1): dưới 1,5 mm, tức dưới 1 % biên tới ngưỡng của criterion.
- Giới hạn: ba ca, một seed. Chu kỳ lấy mẫu của cảm biến và của planner cố định theo thiết kế, nên sai số do chúng không nằm trong phép đo này.

## 14. Sensitivity {#hb-sensitivity}

Lệnh `python3 -m eval.verify_sim sensitivity`, commit `36c5c25`, thư viện planner build từ `e3158a5`, seed 1. Mỗi tham số của mô hình xe nhân 0,8 và 1,2 trên ba ca: 24 lượt. Planner vẫn nhận VehicleConfig danh định. Giá trị chính là DLC nhỏ nhất (PP-SWR-051) ở S1a, S1c và DTLE nhỏ nhất (PP-SWR-086) ở S5a. Giá trị danh định: 0,78916 m, 0,74791 m, 0,04391 m.

| Tham số | Ca | Δ giá trị chính ở ×0,8 [mm] | Δ giá trị chính ở ×1,2 [mm] | Lệch quỹ đạo lớn nhất [m] |
|---|---|---|---|---|
| Độ cứng lốp trước C_f | S1a | −2,5 | +1,0 | 0,008 |
| Độ cứng lốp trước C_f | S1c | −9,3 | +4,9 | 0,028 |
| Độ cứng lốp trước C_f | S5a | −0,5 | −0,9 | 0,145 |
| Độ cứng lốp sau C_r | S1a | −3,7 | +2,1 | 0,003 |
| Độ cứng lốp sau C_r | S1c | −14,1 | +9,1 | 0,028 |
| Độ cứng lốp sau C_r | S5a | −4,7 | −0,5 | 0,107 |
| Mô-men quán tính I_z | S1a | +0,5 | −0,5 | 0,002 |
| Mô-men quán tính I_z | S1c | +0,2 | −0,4 | 0,012 |
| Mô-men quán tính I_z | S5a | +2,4 | −3,5 | 0,009 |
| Trễ EPS thật | S1a | +0,2 | −0,2 | 0,001 |
| Trễ EPS thật | S1c | +0,1 | 0,0 | 0,005 |
| Trễ EPS thật | S5a | +1,1 | −1,2 | 0,008 |

- Không lượt nào đổi kết luận: requirement trong phạm vi không trượt ở lượt danh định thì không trượt ở lượt nào của 24 lượt.
- Độ cứng lốp ảnh hưởng nhiều nhất: giá trị chính đổi tới 14 mm, quỹ đạo ELK ở S5a lệch tới 0,145 m. I_z và trễ EPS thật đổi giá trị chính không quá 3,5 mm.
- Giới hạn: ba ca, một seed; cả ba ca còn xa ngưỡng (DLC 0,75 m so với 0; DTLE 0,044 m so với −0,3 m), nên chưa biết độ nhạy ở ca sát ngưỡng. Mức ±20 % không phải dải có nguồn (PP-TS-023). Độ cứng lốp trước và sau đổi riêng nên hệ số thiếu lái K đổi theo.

## 15. Validation {#hb-validation}

Dự án không có dữ liệu xe thật. Mọi model ở mục 9 ghi "chưa validation". Hai simulator cho cùng kết quả cũng không chứng minh khớp xe thật.

Dữ liệu cần có để validation sau này:

| Dữ liệu | Dùng để kiểm |
|---|---|
| Vòng tròn ổn định và đáp ứng góc lái bậc thang của xe đích | Mô hình xe (độ cứng lốp, I_z, K) |
| Log camera có ground truth | Sai số lane model theo cự ly, tầm nhìn, trễ |
| Log EPS: yêu cầu và phản hồi | Trễ, giới hạn tốc độ, hằng số thời gian |
| Log đồng hồ ECU và độ trễ kênh | Mô hình timing |
| Quy tắc arbitrator của hệ thống | Arbitrator chạy thử |

Thước đo validation (MoP) và ngưỡng tương quan theo Annex 5 §3.6.5.2 và §3.6.5.5 chỉ đặt khi có dữ liệu.

## 16. Uncertainty {#hb-uncertainty}

| Nguồn | Loại | Xử lý hiện tại | Ghi chú |
|---|---|---|---|
| Nhiễu cảm biến, jitter, mất gói, pha khởi động | Aleatory | Seed; nhiều seed cho ô có nhiễu (Software Qualification Test Specification 5.2) | Mô hình ngẫu nhiên không cản việc chạy lại tất định (`SeedSequence.spawn`) |
| Tham số không có nguồn | Epistemic | Quét nhiều mức khi có thể (Q1 đến Q4); sensitivity ở mục 14 | Độ cứng lốp, I_z, trễ EPS chỉ quét ±20 % trên ba ca |
| Cấu trúc model: bicycle, lốp tuyến tính, stand-in | Epistemic | Không | Giả định và miền dùng ở mục 9 |
| Đặc tính lái giống nhau giữa các profile | Epistemic | Không | Flexibility chỉ đúng với một đặc tính lái; quét K, tỉ số lái, trễ chấp hành theo dải có nguồn chưa làm (PP-TS-023) |
| Đồng hồ lý tưởng ở ca danh định | Epistemic | Chỉ F14 và ca bật `realism` có trôi | Kết luận về timing chỉ đúng ở ca lỗi |
| Quy tắc arbitrator của hệ thống | Epistemic | Một quy tắc cố định | Kết luận về chuyển path chỉ đúng với quy tắc đã giả định |
| Sai số rời rạc hóa | Số học | Đo ở mục 13 | |
| Khác nhau giữa hai hệ điều hành | Số học | `behavior_checksum` chỉ so trong cùng máy | CI chỉ so hai lần chạy trong cùng một job |

## 17. Kết luận độ tin cậy {#hb-conclusion}

Năm thuộc tính của Annex 5 §1.1:

| Thuộc tính | Kết luận | Bằng chứng |
|---|---|---|
| Capability | Làm được trong phạm vi mục 8 | Capability matrix; 28 họ kịch bản, 24 lỗi, 6 profile |
| Accuracy | Chưa đánh giá | Không có dữ liệu xe thật (mục 15) |
| Correctness | Một phần | Verification ở mục 12 đến 14; planner mồi; chưa qualify simulator theo ISO 26262-8 (TCL3) |
| Usability | Làm được | Runbook, quy trình `PP-TS`, `PP-PR`, CI, golden set |
| Fit for purpose | Ở mức lập luận | Kết luận Không đạt có giá trị trong phạm vi model; kết luận Đạt chỉ trong phạm vi đã thử, không phải bằng chứng an toàn |

## 18. Yêu cầu nền tảng {#hb-requirements}

Yêu cầu của chính công cụ kiểm thử, không phải của planner. Số do người thiết kế công cụ chọn là tham số công cụ ở Appendix A.

| ID | Yêu cầu | Kiểm chứng | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| SIM-REQ-001 | Nền tảng phải chạy mọi ResolvedCase qua cùng một hàm thực thi, dù yêu cầu đến từ CLI, web hay suite | Test: checksum ba đường bằng nhau trên golden set | Đạt | `eval.golden check` ngày 19/11/2026: 14 ca, 41 kết quả (ba đường runner, suite, live); mọi đường cùng checksum với runner |
| SIM-REQ-002 | Nền tảng phải gán cho mỗi lần thực thi một `run_id` chưa từng dùng | Test | Đạt | `test_run_ids_are_unique` |
| SIM-REQ-003 | Khi observer ngắt kết nối, nền tảng phải tiếp tục run tới một trạng thái kết thúc | Test | Đạt | `test_observer_leaving_does_not_stop_the_run`, `test_run_survives_a_closed_tab_and_reconnect_resumes` |
| SIM-REQ-004 | Nền tảng phải chỉ dừng một run khi nhận lệnh cancel có đúng `run_id` của run đó | Test | Đạt | `test_cancel_stops_only_that_run` |
| SIM-REQ-005 | Khi nhận lệnh cancel, nền tảng phải đưa run về CANCELLED trong tối đa T_cancel + 1 s | Test | Đạt | `test_cancel_kills_a_worker_that_ignores_sigterm`; đo ngày 18/11/2026: CANCELLED sau 0,11 s |
| SIM-REQ-006 | Nếu worker thoát khác 0 hoặc chết vì tín hiệu, thì nền tảng phải ghi FAILED kèm một lớp lỗi trong `SUT_EXECUTION`, `SIM_ERROR`, `EVAL_ERROR`, `INFRA` | Test | Đạt | `test_failures_are_classified`, `test_external_kill_is_infra`, `test_planner_crash_is_sut_execution` |
| SIM-REQ-007 | Nếu một run vượt T_timeout, thì nền tảng phải dừng worker và ghi TIMED_OUT | Test | Đạt | `test_timeout`, `test_paused_time_is_not_counted_against_the_timeout` |
| SIM-REQ-008 | Nền tảng phải ghi mọi stderr và mọi stdout ngoài giao thức của worker vào `worker.log` của run | Test | Đạt | `test_worker_log_keeps_stderr_and_stray_stdout` |
| SIM-REQ-009 | Trong khi đã có N_max run ở RUNNING hoặc PAUSED, nền tảng phải giữ run mới ở QUEUED | Test | Đạt | `test_queue_respects_max_running` |
| SIM-REQ-010 | Khi observer kết nối lại với `from = s`, nền tảng phải gửi mọi sự kiện có `seq` lớn hơn s | Test | Đạt | `test_reconnect_resumes_after_the_last_seq` |
| SIM-REQ-011 | Khi nhận lại yêu cầu tạo run có cùng `Idempotency-Key`, nền tảng phải trả `run_id` đã tạo thay vì tạo run mới | Test | Đạt | `test_idempotency_key_returns_the_same_run`, `test_idempotency_key` |
| SIM-REQ-012 | Nếu worker không còn tồn tại, thì nền tảng phải cập nhật trạng thái run trong tối đa T_state | Test | Đạt | `test_external_kill_is_infra`; đo ngày 18/11/2026: trạng thái cập nhật sau 0,11 s |
| SIM-REQ-020 | Khi một run kết thúc, nền tảng phải để lại một bundle theo schema bundle v1, ở mọi trạng thái kết thúc | Test | Đạt | `test_completed_run_leaves_a_complete_verified_bundle`, `test_complete_bundle_from_the_live_worker` |
| SIM-REQ-021 | Nền tảng phải ghi bundle vào thư mục tạm và chỉ đổi sang tên chính thức sau khi đã ghi `SHA256SUMS` | Test | Đạt | Ghi vào thư mục tạm ở `execution/bundle.py`; `test_recovery_finalizes_only_own_stale_folders` |
| SIM-REQ-022 | Nếu run không hoàn tất, thì `execution.json` phải có `complete = false`, lý do và danh sách file bắt buộc còn thiếu | Test | Đạt | `test_planner_crash_is_sut_execution` (`complete` sai, file đã ghi được giữ) |
| SIM-REQ-023 | Manifest phải ghi `run_id`, `parent_run_id`, `case_hash`, `behavior_checksum`, sha256 và chuỗi version của từng thư viện SUT, commit và trạng thái cây làm việc, phiên bản Python và numpy, phiên bản các schema | Inspection, Test | Đạt | `test_complete_bundle_from_the_live_worker` |
| SIM-REQ-024 | Nền tảng không được sửa file nào trong một bundle đã đổi sang tên chính thức | Test | Đạt | `execution.bundle.verify` sau mỗi run; `test_completed_run_leaves_a_complete_verified_bundle` |
| SIM-REQ-025 | Nền tảng phải tính `case_hash` trên ResolvedCase chuẩn hóa theo `c14n/1` | Test | Đạt | `test_c14n_is_independent_of_key_order_and_keeps_float_bits`, `test_case_hash_ignores_name_and_notes_only` |
| SIM-REQ-026 | Evaluator không được dùng giá trị đã làm tròn để hiển thị khi chấm | Inspection | Đạt | Inspection: bên chấm đọc RunLog trong bộ nhớ, không đọc lại MCAP (`eval/metrics.py`) |
| SIM-REQ-027 | Evaluator không được thay giá trị thiếu bằng 0 hay bằng một giá trị hợp lệ | Test | Một phần | Criterion có `applicable = false` khi thiếu đại lượng (Inspection); chưa có test riêng cho ca mất input |
| SIM-REQ-028 | Mỗi giá trị thời gian trong bundle phải ghi kèm miền đồng hồ: `sim`, `camera` hoặc `adas` | Inspection, Test | Đạt | `manifest.bundle.time_domains`; `test_complete_bundle_from_the_live_worker` kiểm từng trường nêu trong đó có thật trong `trace.mcap` |
| SIM-REQ-029 | Khi chạy lại từ `recipe`, nếu `case_hash` tính lại khác bản gốc, thì nền tảng phải dừng và báo "ca đã đổi" | Test | Đạt | `test_rerun_reproduces_the_checksum_and_stops_on_a_changed_case` |
| SIM-REQ-040 | Với cùng ResolvedCase, seed, sha256 của mọi thư viện SUT và commit simulator trên cùng máy, hai lần chạy phải cho cùng `behavior_checksum` | Test trên golden set | Đạt | `eval.golden check`: checksum khớp mốc ghi ngày 18/11/2026, cùng máy và cùng thư viện |
| SIM-REQ-041 | `behavior_checksum` không được đổi theo số tiến trình song song hay cách tạo tiến trình | Test: `--jobs 1` và `--jobs 4` | Đạt | `eval.golden check` ở `--jobs 1`, `--jobs 2`, `--jobs 4`: cùng mốc |
| SIM-REQ-042 | Có hay không có observer không được làm đổi `behavior_checksum` | Test | Đạt | Đường live (có observer) và đường runner (không observer) cùng checksum trên golden set |
| SIM-REQ-043 | Tốc độ phát và việc tạm dừng không được làm đổi `behavior_checksum` | Test: 0,5×, max, pause rồi resume | Đạt | Đo ngày 17/11/2026: live ở tốc độ tối đa, 2×, 4× có tạm dừng và đổi tốc độ cùng checksum; golden chạy đường live ở tốc độ tối đa |
| SIM-REQ-044 | Observer không được chạy giữa hai lần đọc đồng hồ đo thời gian tính của SUT | Inspection | Đạt | Inspection `sim/harness.py`: observer được gọi sau khi chu kỳ đã ghi vào log, ngoài các lần đọc đồng hồ quanh planner |
| SIM-REQ-045 | Mô hình ngẫu nhiên phải lấy số ngẫu nhiên từ luồng tách theo seed của run | Inspection, Test | Đạt | `test_seeds_are_reproducible` |
| SIM-REQ-060 | Evaluator phải chấm chỉ từ output qua interface của SUT, thời gian tính và ground truth của simulator | Inspection | Đạt | `test_python_import_rules` (`eval` không import `planner`) |
| SIM-REQ-061 | Nếu tiền điều kiện của ca không đạt ở phía test, thì evaluator phải báo `not_judged` cho criterion liên quan | Test | Đạt | `test_case_issues_execution_and_not_judged` |
| SIM-REQ-062 | Nếu một lỗi được cấu hình nhưng không được bơm trong run, thì evaluator phải báo `not_judged` cho criterion phụ thuộc lỗi đó | Test | Đạt | `test_fault_never_injected_is_not_judged_as_passed` |
| SIM-REQ-063 | Evaluator không được tính run có lớp lỗi `SIM_ERROR`, `EVAL_ERROR` hay `INFRA` vào tỉ lệ đạt | Test | Một phần | Lỗi bên chấm và lỗi thực thi của planner không vào tỉ lệ đạt (`test_case_issues_execution_and_not_judged`); run `SIM_ERROR`, `INFRA` ở workbench không có `evaluation.json`; chưa có test riêng ở mức tỉ lệ đạt của suite |
| SIM-REQ-064 | Nền tảng chỉ được dùng kết quả benchmark khi selfcheck phát hiện mọi planner mồi theo Software Qualification Test Specification 12 | Test | Đạt | `eval.selfcheck` ngày 19/11/2026: 10/10 planner mồi bị báo đúng requirement và mức; `test_suite_matches_the_table_of_section_12`, `test_conformance_baits_are_detected` |
| SIM-REQ-065 | Khi một criterion đo theo thời gian bị trượt, evaluator phải ghi `first_fail_s` | Test | Một phần | Criterion ghi `first_fail_s` (`test_conclusion.py`); độ chính xác của bước nhảy tới lần trượt đo tay ngày 18/11/2026 (lệch tối đa nửa chu kỳ planner); chưa có test tự động cho phần nhảy |
| SIM-REQ-080 | Workbench không được tự tính verdict; workbench chỉ hiển thị evaluation đọc từ bundle | Inspection | Đạt | Inspection ngày 18/11/2026, xem lại trên trình duyệt ngày 19/11/2026: kết luận và evaluator lấy từ `evaluation.json` của bundle |
| SIM-REQ-081 | Khi người dùng mở một run đã ghi để xem, workbench không được chạy SUT | Test | Một phần | Đo ngày 18/11/2026: phát lại không sinh worker; chưa có test tự động |
| SIM-REQ-082 | Khi người dùng mở lại một ca để chạy lại, workbench phải hiển thị `behavior_checksum` mới có bằng bản gốc hay không | Demonstration | Đạt | `test_rerun_with_the_same_behaviour_matches`, `test_rerun_with_another_behaviour_is_reported` |
| SIM-REQ-083 | Workbench phải gắn nhãn nguồn (truth hoặc perception) cho mọi giá trị trên scene và biểu đồ | Inspection | Đạt | Inspection ngày 18/11/2026, xem lại ngày 19/11/2026 (màn Điều tra: nguồn dữ liệu khi phát lại) |
| SIM-REQ-084 | Workbench không được vẽ giá trị thiếu thành 0 | Inspection | Đạt | Inspection ngày 18/11/2026 |
| SIM-REQ-085 | Workbench phải hiển thị trạng thái thực thi và kết luận đánh giá ở hai vị trí riêng | Inspection | Đạt | Inspection ngày 18/11/2026, xem lại ngày 19/11/2026 (danh sách Run: cột Thực thi và cột Kết luận riêng) |
| SIM-REQ-086 | Workbench phải tính khoảng hở hiển thị theo bề rộng làn tại vị trí xe | Test | Đạt | `test_clearance_follows_a_lane_that_widens` |
| SIM-REQ-087 | Workbench không được hiển thị tỉ lệ đóng góp lái khi không có đại lượng vật lý định nghĩa tỉ lệ đó | Inspection | Đạt | `test_steering_share_is_never_invented` |
| SIM-REQ-088 | Workbench phải đặt overlay lane model theo tư thế xe tại thời điểm lấy mẫu toàn cục của khung camera | Test | Đạt | `test_lane_model_is_placed_at_the_global_capture_time` |
| SIM-REQ-089 | Workbench phải hiển thị định danh của mọi thư viện SUT trong một run hoặc một lần chạy suite | Test | Một phần | Đo ngày 18/11/2026: hiển thị cả hai thư viện; chưa có test tự động |
| SIM-REQ-090 | Khi SUT có nhiều thành phần, workbench phải hiển thị output trạng thái của từng thành phần | Inspection | Đạt | Inspection ngày 18/11/2026, xem lại ngày 19/11/2026 (màn Điều tra: output của từng planner, arbitrator chạy thử) |
| SIM-REQ-100 | Nền tảng phải cài và chạy được trên Linux và macOS theo các lệnh ghi trong README và runbook, không dùng Docker | Demonstration | Một phần | macOS: cài và chạy theo README và Simulation Runbook trên máy phát triển; Linux: chưa chạy, chờ CI |
| SIM-REQ-101 | Mỗi push lên `main` phải chạy build planner, pytest, quy tắc import và conformance B0 trong CI | Inspection | Một phần | `.github/workflows/tests.yml` có đủ bước (build, test C, pytest gồm quy tắc import, B0, golden); chưa chạy trên GitHub |
| SIM-REQ-102 | Nền tảng phải xóa run thường cũ nhất khi `build/runs` vượt N_keep run hoặc S_max | Test | Đạt | `test_retention_keeps_newest_and_pinned` |
| SIM-REQ-103 | Nền tảng không được xóa run đã được ghim | Test | Đạt | `test_retention_keeps_newest_and_pinned` |
| SIM-REQ-104 | Nền tảng không được ghi dữ liệu run vào thư mục mà `web/build-static.cjs` xuất bản | Inspection | Đạt | `test_static_build_copies_only_the_placeholder`; dữ liệu run ở `build/runs` |
| SIM-REQ-105 | Server phải chỉ nghe trên `127.0.0.1` và từ chối yêu cầu thay đổi trạng thái có Origin lạ | Inspection, Test | Đạt | `test_foreign_origin_is_refused`; Inspection: chỉ bind `127.0.0.1` |
| SIM-REQ-106 | Bản web xuất bản công khai không được chứa mã nội bộ của kế hoạch | Test | Đạt | `test_placeholder_has_no_internal_codes`, `test_workbench_screens_do_not_show_internal_codes` |
| SIM-REQ-120 | Mỗi model của simulator phải có mục trong Simulation Handbook ghi mục đích, giả định, nguồn tham số, miền dùng, verification đã làm và trạng thái validation | Inspection | Đạt | Mục 9: chín model; `test_handbook_has_an_entry_for_every_model` |
| SIM-REQ-121 | Mỗi báo cáo kết luận về SUT phải ghi phiên bản simulator và trạng thái validation của các model đã dùng | Inspection | Đạt | `eval/credibility.py`; `test_every_conclusion_names_the_simulator` |
| SIM-REQ-122 | Nếu một run dùng tham số ngoài miền dùng đã khai báo của model, thì evaluation phải gắn cảnh báo | Test | Chưa làm | Ưu tiên P2; chưa có khai báo miền dùng đọc được bằng máy |
| SIM-REQ-140 | Lõi thực thi `execution/` không được import `interfaces`, `planner`, `adapters`, `sim`, `eval`, `benchmark` hay `workbench` | Test quy tắc import | Đạt | `test_python_import_rules` |
| SIM-REQ-141 | Server workbench không được import gói nào của một SUT cụ thể | Test quy tắc import | Đạt | `test_python_import_rules` |
| SIM-REQ-142 | Thêm một SUT mới không được cần sửa `execution/` hay `workbench/` | Analysis | Đạt | Analysis: mục 10 của Simulation Runbook liệt kê năm thứ phải thêm; `test_python_import_rules` giữ `execution/` và `workbench/` không import gói của SUT |

## Appendix A. Tham số công cụ {#hb-appendix}

| Tham số | Nghĩa | Giá trị khởi đầu | Dải | Nguồn |
|---|---|---|---|---|
| N_max | Số run chạy đồng thời tối đa | 2 | 1–4 | nhóm tự thống nhất; trần theo Software Qualification Test Specification 4.1 (8 GB, tối đa 4 tiến trình) |
| T_timeout | Thời gian thật tối đa của một run, không tính lúc PAUSED | 6 × thời lượng mô phỏng + 30 s; mặc định 1800 s | — | nhóm tự thống nhất |
| T_cancel | Chờ worker thoát sau SIGTERM trước khi SIGKILL | 2 s | 1–10 s | nhóm tự thống nhất |
| T_state | Thời gian tối đa để trạng thái run phản ánh worker đã chết | 5 s | 1–10 s | nhóm tự thống nhất |
| N_keep | Số run thường giữ trong `build/runs` | 50 | ≥ 10 | nhóm tự thống nhất |
| S_max | Dung lượng tối đa của `build/runs` | 2 GB | ≥ 0,5 GB | nhóm tự thống nhất |

## Revision history {#revision-history}

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 2026-11-19 | Bản đầu: bố cục theo UN R171 Annex 5 §4.1; chín model và trạng thái validation; criticality, tool confidence; verification, sensitivity; 58 yêu cầu nền tảng |

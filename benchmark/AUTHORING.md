# Viết kịch bản, lỗi và ca ghép

Hướng dẫn cho người hoặc agent thêm ca vào benchmark. Định nghĩa ca nằm ở [Software Qualification Test Specification](../docs/vi/path-planner-software-qualification-test-specification.md) mục 5, 6. Quy tắc bên chấm và bên bị chấm ở `CLAUDE.md`, mục "Planner và đánh giá phát triển độc lập".

## Nguyên tắc

- Benchmark là bên chấm. Không chọn đường, mức lỗi hay ngưỡng để planner dễ qua. Không sửa ca sau khi đã thấy kết quả.
- Kết quả mong đợi (`pp:expected_outcome`: `drive`, `drive_limited`, `refuse`) suy từ Software Requirements Specification và ADAS Function Specification, không suy từ cách planner đang làm.
- Mỗi ca chỉ ghi điều quan sát được ở output. Không đọc biến nội bộ của planner.
- Mã kịch bản, lỗi, ca ghép cố định: không đánh số lại, không dùng lại.
- Thiếu cơ chế trong `sim/` hoặc `eval/` thì báo lại, không tự thêm. Danh sách cơ chế đã có ở bảng cuối file.

## Các bước

1. Đọc dòng của mã trong Software Qualification Test Specification mục 5 hoặc 6 và các requirement ở cột Kiểm chứng của Software Requirements Specification.
2. Tạo file trong đúng thư mục của mã (bảng Phân chia file). Kịch bản mới cần ba file: `<mã>.xosc` (tham số danh định), `<mã>.anchors.xosc` (một bộ cụ thể cho mỗi biến thể a, b, c...), `<mã>.ranges.xosc` (dải để lấy mẫu). Chép cấu trúc từ một mã gần giống, ví dụ S4 cho ca trôi làn, S3 cho ca có xe khác, F20 cho lỗi ngoài lane model.
3. Đường mới: `roads/<mã><biến thể>.xodr`, OpenDRIVE 1.8.1.
4. Kiểm nhanh:

```bash
python3 -m eval.check_case S11
python3 -m eval.check_case S11 --run
python3 -m eval.check_case F05 --host S4 a --at lka_active+0.2 --run
```

`check_case` kiểm XSD, nạp từng biến thể, nhãn L0–L5 và kết quả mong đợi, truy vết trong Software Requirements Specification. `--run` chạy một lần mỗi biến thể, seed 1. Ca trượt vì planner là kết quả, không phải lỗi của ca. Ca trượt vì `check_case` báo vấn đề thì sửa ca.

`scenario_id` của mọi biến thể phải là mã của file (`check_case` kiểm). Không đặt mã của kịch bản mẫu.

5. Báo lại trong báo cáo cuối: file đã tạo, kết quả `check_case`, các dòng cần thêm ở file dùng chung (bảng dưới). Không tự sửa file dùng chung.

## Phân chia file

| File | Ai sửa |
|---|---|
| `scenarios/<mã>.*`, `faults/<mã>.*`, `roads/<mã>*.xodr`, `combinations/<mã>.yaml` của mã được giao | Agent được giao mã đó |
| `suites/*.json`, `suites/*.yaml`, `README.md`, `AUTHORING.md` | Người tích hợp. Agent ghi đề xuất trong báo cáo |
| `docs/vi/*` (Software Qualification Test Specification mục 5, 6; cột Kiểm chứng của Software Requirements Specification) | Người tích hợp, sau khi chủ dự án duyệt |
| `sim/`, `eval/`, `planner/`, `interfaces/`, `tests/` | Không sửa khi làm ca. Thiếu cơ chế thì báo |

## Làm song song

- Mỗi agent làm trong một git worktree riêng, nhánh riêng, tách từ cùng commit. Hai agent không bao giờ được giao cùng một mã.
- Agent không commit lên nhánh chính và không chạy suite (smoke, regression, full). Chỉ chạy `check_case`.
- Máy 8 GB: `check_case --run` chạy lần lượt từng biến thể; không chạy nhiều tiến trình.

## Cơ chế đã có

| Cần | Cách khai báo | Dùng cho |
|---|---|---|
| Lỗi bắt đầu theo pha của planner | JSON lỗi thêm `"trigger": "lka_active"`, `"elk_active"` hoặc `"intervention_active"`; `start_s` tính từ chu kỳ đầu PathStatus báo pha ACTIVE. Runner: `--at lka_active+0.2` | Mục 6, ba thời điểm bơm |
| Ghép nhiều lỗi | `combinations/G<nn>.yaml`: `hosts`, `faults`, `sim`. Runner: `--fault` lặp lại | Mục 6.2 |
| Ma sát, trễ EPS thật, nhiễu perception, trễ camera | Thuộc tính `pp:road_mu`, `pp:eps_delay_s`, `pp:perception_noise_scale`, `pp:camera_latency_ms` | S12, S13, G01 |
| Tốc độ xe khác đổi theo thời gian | `CustomCommandAction type="pp:traffic_speed:v1"`: `{"entity": "Car1", "profile": [[0, 8.3], [10, 0], ...]}` | S11 |
| ACC bám xe trước | `pp:acc` `on`; FOLLOW theo mục 4.7 | S11, S14 |
| Tài xế trôi nhiều lần, bẻ rồi trả | `pp:departure:v1` thêm `"repeats": [[t_start, 1 hoặc -1], ...]` | S16, S8c |
| Xe đổi làn | Camera tự đánh chỉ số lại vạch và bật `lane_change` khi trục sau qua nửa làn; evaluator chấm theo làn mới. Lỗi `lane_change_late` cho cờ trễ một frame | S17, S8b |
| Chuỗi FunctionRequests định sẵn | `CustomCommandAction type="pp:requests:v1"`: `{"events": [{"at_s": 3.0, "requests": [["REQUEST", "NONE", "NONE"], ["REQUEST", "LEFT", "NONE"], ["OFF", "NONE", "NONE"]], "driver_override": false}]}`; thứ tự HWA, LKA, ELK; tên enum theo Interface Control Document 5.6; chỉ ở chế độ scripted | S9, S16 |
| FunctionRequests theo pha của planner | Thêm `"trigger": "lka_completed"` (hoặc `*_active`, `*_completed`) vào một event của `pp:requests:v1`; `at_s` tính từ lần đầu pha đó xuất hiện | S16 a, b, e |
| Đánh lái lặp theo pha | `pp:departure:v1` thêm `"repeat_trigger": "lka_completed"`: lần lặp thứ k bắt đầu sau lần thứ k của pha; hệ số trong `repeats` nhân cả độ cong và mô-men | S16 c, d, S8c d |
| Tài xế giữ mô-men ghi đè | `pp:departure:v1` thêm `"torque_windows": [[t0, t1], ...]`; ≥ 3,0 Nm (`torque_override`) thì EPS theo tài xế | S17, S9 c |
| Bật, tắt theo biến thể | Lệnh: `"enabled": $tham_số` trong JSON. Xe khác: `<Property name="pp:present" value="$tham_số" />` trong Vehicle | S10, S14 b–d, S17 e |
| Ca khối ADAS không được can thiệp | `pp:expect_intervention` = `none`; REQUEST nào cũng làm ca không chấm planner | S8b a–c, S8c a–c, S10 |
| Profile cố định theo biến thể | Thêm mã vào `own_profile` của `suites/scope.yaml` (người tích hợp) | S19 |
| Bề rộng làn đổi dọc đường, tách nhánh, thêm làn | Đa thức `width` của lane trong OpenDRIVE (xem S6b) | S6b |
| Rào chắn, mép đường, nhiều làn | OpenDRIVE `objects`, `lanes` (xem S6 d) | S6, S15 |
| Xe khác đổi làn, cắt vào | `CustomCommandAction type="pp:traffic_lateral:v1"`: `{"entity": "Car1", "start_s": 4.0, "duration_s": 3.0, "target_offset_m": 0.0}` | S3b, S8b, S11 d |

Chưa có:

| Thiếu | Ảnh hưởng |
|---|---|
| Mô hình độ cao mặt đường | S1b d chỉ mô phỏng tầm nhìn (đã ghi trong mục 5) |

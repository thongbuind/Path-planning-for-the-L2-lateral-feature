# PP-PR-024 LongitudinalPlan ở đầu cao của dải làm Trajectory có vô cực

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã sửa, chờ xác nhận chính thức |
| Mở ngày | 2026-11-12 |
| Requirement bị ảnh hưởng | Software Qualification Test Specification 11, C2 (hai đầu dải của input); Interface Control Document 4, 5.7; PP-SWR-010, 154, 156 |
| Tái hiện | Lần chạy nháp: `python3 -m eval.conformance --planner build/planner/libpp_planner.dylib`, thư viện build lúc 12:38 ngày 2026-11-12, chưa có lần chạy chính thức |

## 1. Hiện tượng

- B0 trượt C2.robust: khi LongitudinalPlan mang giá trị ở đầu cao của dải kiểu float32 (Software Qualification Test Specification 11, "Trường còn lại"), chu kỳ 0 gửi Trajectory có `points[11].pose.x = inf`.
- C2 trượt nghĩa là Bị chặn: `eval.suite` dừng sau B0, không chạy ca nào.

## 2. Nguyên nhân

- Interface Control Document 5.7 không ghi dải của `v`, `a`, nên C2 dùng dải của kiểu float32 (±FLT_MAX).
- Planner nhận LongitudinalPlan chỉ theo timeout và tuổi, không kiểm giá trị.
- T11 (`pp_speed_profile`) chỉ chặn dưới `v` ở 0, rồi cộng dồn s = Σ v·0,1 s. Với v = FLT_MAX, s ở điểm 11 bằng 1,1·FLT_MAX, vượt float32 khi ghi `pose.x`, thành vô cực.

## 3. Cách sửa

Chọn 2026-11-13: kiểm dải và bỏ LongitudinalPlan ngoài dải, như input chưa nhận.

| Chỗ sửa | Nội dung |
|---|---|
| Software Requirements Specification 1.13 | Thêm PP-SWR-156 |
| Interface Control Document 1.10, mục 5.7 | `v` 0–182,04 m/s, `a` ±32,767 m/s², lấy theo dải tốc độ và AccelX của mục 5.3 |
| Software Detailed Design 1.9, T1 bước 1 | Bỏ cả message khi có một điểm ngoài dải; T11 dùng PP-SWR-154 |
| `interfaces/schema/inputs/longitudinal_plan.yaml` | `LONGITUDINAL_PLAN_V_MAX_MPS`, `LONGITUDINAL_PLAN_A_MAX_MPS2` |
| `planner/src/pp_planner.c` | `longitudinal_plan_in_range` trong `check_inputs` |
| `tests/planner/c/test_step.c` | `test_longitudinal_plan_range`: trong dải, hai đầu dải, ±FLT_MAX, NaN, vô cực, một điểm hỏng |
| Software Qualification Test Specification 1.33, mục 6 | Thêm F23; kiểm chứng PP-SWR-156 |
| `sim/faults/channel.py` | Lỗi kênh `out_of_range` trên LongitudinalPlan |
| `sim/harness.py`, `eval/metrics.py` | Plan ngoài dải tính là không dùng được; tiêu chí PP-SWR-156 |
| `benchmark/faults/F23.*`, `benchmark/suites/full.json`, `regression.json` | Bốn biến thể a–d |

## 4. Xác nhận

Chưa có lần chạy chính thức. Lần chạy nháp 2026-11-13 (thư viện `ecf2f153aeef-dirty`): B0 đạt C1, C2. Cần chạy lại B0 và F23 với thư viện build từ commit có bản sửa.

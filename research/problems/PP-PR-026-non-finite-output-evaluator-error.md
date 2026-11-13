# PP-PR-026 Output có NaN trong lần chạy kịch bản bị ghi là lỗi bên chấm

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã sửa, chờ xác nhận chính thức |
| Mở ngày | 2026-11-13 |
| Requirement bị ảnh hưởng | Software Qualification Test Specification 8.4 (lỗi thực thi của planner: output có NaN hoặc vô cực, BLOCKER) |
| Tái hiện | Lần chạy nháp: F23 a trên S1a, seed 1, thư viện `build/planner-qp/libpp_planner.dylib` build 2026-11-12, chưa có PP-SWR-156 |

## 1. Hiện tượng

- Planner gửi Trajectory có vô cực. `eval.metrics` dừng ở `road.project`: `ValueError: cannot convert float NaN to integer`.
- `eval.suite` ghi lần chạy là `error` (lỗi bên chấm), không phải trượt của planner. Lần chạy không có mức BLOCKER và không có requirement nào trượt.
- B0 C2 bắt được NaN, vô cực ở chuỗi input của bộ conformance. Trong kịch bản S, F thì không bắt được.

## 2. Nguyên nhân

- `eval.metrics.execution_fault` đã báo lỗi thực thi khi output có NaN hoặc vô cực (Software Qualification Test Specification 8.4), nhưng chạy sau các chỉ số khác.
- Các chỉ số chiếu Trajectory lên đường thật (`_path_truth`, `_continuity`, `_entry_errors`, `observed_horizon_s`) giả định mọi điểm hữu hạn. Với vô cực, `road.project` dừng trước khi tới `execution_fault`.
- `eval.suite` bắt exception đó và ghi `error` (lỗi bên chấm).

## 3. Cách sửa

Chọn 2026-11-13: kiểm output hữu hạn một lần mỗi chu kỳ ở đầu `evaluate`. Chu kỳ có NaN hoặc vô cực không được chiếu lên đường; `execution_fault` vẫn báo lỗi thực thi như cũ. Không thêm requirement: Software Qualification Test Specification 8.4 đã quy định.

| Chỗ sửa | Nội dung |
|---|---|
| `eval/metrics.py` | `_finite_outputs`; mảng `finite` ở đầu `evaluate`; bỏ chu kỳ không hữu hạn ở `paths`, PP-SWR-100 đến 102, PP-SWR-018, `_entry_errors`, path của lần can thiệp; `execution_fault` chỉ chạy trên chu kỳ hỏng đầu tiên |
| `tests/eval/test_intervention_metrics.py` | Vô cực ở chu kỳ bắt đầu can thiệp và giữa lần can thiệp: chấm xong, có một lỗi thực thi |

Thời gian chấm không đổi: kiểm hữu hạn 108 ms trên 2,4 s cho S1 a (1.120 chu kỳ), thay cho lần duyệt mọi chu kỳ của `execution_fault`.

## 4. Xác nhận

Chưa có lần chạy chính thức. Lần chạy nháp 2026-11-13, F23 a với thư viện của mục Tái hiện: chấm xong, trượt "Lỗi thực thi: trajectory.points[11].pose.x không hữu hạn tại t = 4.033 s" và PP-SWR-156.

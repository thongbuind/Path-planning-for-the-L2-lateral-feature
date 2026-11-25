# PP-PR-080 S14 a, VP-0: PP-SWR-051 báo DLC −23 m sau đoạn cua vượt giới hạn

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã sửa, chờ hồi quy |
| Mở ngày | 2026-11-23 |
| Requirement bị ảnh hưởng | PP-SWR-051; PP-SWR-006, 007 |
| Tái hiện | [20261122-0758-suite-regression-591e3de](../runs/20261122-0758-suite-regression-591e3de/report.md), `S14-a-VP-0-cabfa230312d`, seed 1 |

## 1. Hiện tượng

- Bên chấm báo PP-SWR-051 = −23,07 m, nhưng `vehicle_offset_max_m` = 0,43 m. Hai số không khớp nhau.
- Ground truth trong MCAP: 130 km/h, ACC đọc LateralLimits, vào cua R = 200 m. Xe giảm tốc từ 36,1 xuống 21,5 m/s. Lốp phải qua vạch lúc khoảng 7,2 s (v ≈ 26,7 m/s, a_y cần ≈ 3,6 m/s²), cuối log lệch −3,59 m, `dlc_right_m` = −2,96 m.
- Lúc rời làn, a_y cần lớn hơn aysmax; PP-SWR-007 đạt (cờ bật trước khi lốp đè vạch). PP-SWR-006 trượt từ 4,883 s.
- PP-SWR-051 chỉ chấm chu kỳ có a_y cần ≤ aysmax. Ở cuối log, tốc độ đã giảm nên a_y cần tại xe về dưới aysmax, trong khi xe vẫn ở làn bên.

## 2. Nguyên nhân

Xác nhận 2026-11-23 cho phần 1. Hai phần, cả hai phía đánh giá:

1. Độ lớn: vòng chấm PP-SWR-051 trong `eval/metrics.py` bỏ qua mẫu không được chấm nhưng giữ `s_hint` của mẫu chấm cuối. Sau đoạn a_y cần > aysmax dài vài giây, `road.project` chỉ tìm trong ±20 m quanh vị trí cũ, nên lệch ngang sai hàng chục mét. Vòng tính `_path_truth` có cùng lỗi sau các chu kỳ path không hợp lệ. Chiếu liên tục cho DLC nhỏ nhất −0,97 m lúc 7,93 s, khi a_y cần > aysmax.
2. Phạm vi: PP-SWR-051 được chấm ngay khi a_y cần về dưới aysmax, kể cả khi xe đang ở ngoài làn vì đoạn vượt giới hạn trước đó (R79 5.6.2.1.1 chỉ đòi không vượt vạch khi a_y dưới aysmax). Chưa có luật cho khoảng hồi phục sau đoạn vượt giới hạn.

## 3. Cách sửa

- Phần 1, đã sửa 2026-11-23: đặt lại `s_hint` sau mỗi mẫu hoặc chu kỳ không chấm (`eval/metrics.py`, hai vòng). Kết quả không đổi khi không có khoảng ngắt. Test `tests/eval/test_projection_gap.py`: trượt trước khi sửa, đạt sau khi sửa; `tests/eval`, `tests/execution` 311 test đạt.
- Phần 2: sau khi sửa phần 1, S14 a đạt PP-SWR-051 (DLC nhỏ nhất +0,11 m trên các đoạn được chấm). Xe rời làn khi a_y cần > aysmax, cờ đã bật (PP-SWR-007 đạt); sau đó bên chấm tính theo làn mới qua `lane_index_changes`. Chưa cần luật hồi phục riêng; mở lại nếu có ca xe còn ngoài làn khi được chấm lại.

- Phần 1: sửa phép chiếu cho khớp ground truth; thêm unit test so DLC của bên chấm với `dlc_left_m`, `dlc_right_m`.
- Phần 2: người phụ trách chọn luật, áp cho mọi kịch bản, ghi ở Software Qualification Test Specification 8.1 kèm lý do. Đây là đổi phép chấm sau khi đã thấy kết quả.
- Hành vi planner (PP-SWR-006 trượt, ACC giảm tốc muộn khi camera thấy cua R = 200 m ở 130 km/h) xét riêng ở nhóm sửa planner.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| Lượt nháp 2026-11-23, thư viện có V1a | S14 a VP-0 seed 1: PP-SWR-051 +0,11 m đạt; PP-SWR-006 vẫn trượt (−0,19), xét ở nhóm sửa planner |

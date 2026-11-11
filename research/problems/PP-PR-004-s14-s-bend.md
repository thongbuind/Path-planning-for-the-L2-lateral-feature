# PP-PR-004 S14e: giữ làn và liên tục path trên cua chữ S

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở, cần tái hiện chính thức |
| Mở ngày | 2026-11-11 |
| Requirement cần kiểm tra | PP-SWR-051, 100; kiểm tra thêm PP-SWR-006, 007 |
| Tái hiện | `python3 -m eval.runner S14 e --acc on --seed 1` và `--acc ignore_limits`; VP-0 |
| Nguồn ghi nhận | Kiểm chứng tích hợp bộ smoke ASAM; chưa có lần chạy chính thức |

## 1. Hiện tượng

Ca S14e mới trên cua chữ S R171 được bộ smoke gắn cờ về giữ làn và tính liên tục của path ở cả hai chế độ ACC. Cần xác nhận thêm giới hạn a_y khi ACC đọc LateralLimits và thời điểm cờ giới hạn khi ACC bỏ qua LateralLimits.

Đây là ghi nhận để điều tra, chưa phải kết luận benchmark. Số liệu nháp giữ trong `build/suites/smoke/`; chưa dùng để chọn thuật toán, calibration hay đổi requirement.

Lần chạy nháp `build/suites/smoke-20261111-1425` (VP-0, seed 1), sau khi sửa eval:

| Ca | DLC nhỏ nhất | Lệch ngang giữa hai path | a_y path lớn nhất | a_y cần lớn nhất | Tốc độ nhỏ nhất |
|---|---|---|---|---|---|
| S14e, ACC đọc LateralLimits | −0,31 m | 0,054 m | 2,30 m/s² | 2,74 m/s² | 28,3 m/s |
| S14e, ACC bỏ qua | −1,99 m | 0,080 m | 2,50 m/s² | 3,49 m/s² | 36,1 m/s |
| S1f (cùng cua chữ S, 90 km/h) | 0,61 m (đạt) | 0,047 m (sát 0,05) | 2,50 m/s² | 1,67 m/s² | 25,0 m/s |

- Với ACC bật, khối dọc đã giảm đúng về khoảng √(2,2 × 374) ≈ 28,7 m/s, a_y path chưa chạm aysmax, nhưng xe vẫn ra khỏi làn 0,31 m.
- Ở S1f, a_y path chạm aysmax trong khi đường chỉ cần 1,67 m/s².

## 2. Nguyên nhân


Chưa phân tích. Giả thuyết mạnh nhất: cua chữ S của R171 có hai cung ngược chiều rất ngắn (57,1 m và 5,1 m) trong tầm nhìn 80 m; đa thức bậc 3 của lane model không biểu diễn được, nên độ cong path sai (khớp với nhận xét của Chalmers về đa thức bậc 3; xem `docs/reference/standards/`). Kiểm trước: sai số giữa vạch của lane model và vạch thật dọc cua chữ S, rồi độ cong T5. Chưa quy cho ACC: ACC đã giảm đúng tốc độ.

## 3. Cách sửa

Chưa chọn. Giữ nguyên kịch bản và tiêu chí trong lúc xác nhận. Không sửa riêng cơ chế cho S14e.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

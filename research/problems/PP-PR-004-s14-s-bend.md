# PP-PR-004 S14e: giữ làn và liên tục path trên cua chữ S

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở, đã tìm nguyên nhân; chờ PP-TS-005 |
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

Đã phân tích bằng hình học thuần (không cần planner): khớp đa thức bậc 3 lên vạch thật trên 0–80 m, như camera mô phỏng (Software Qualification Test Specification 4.5), tại từng vị trí xe dọc cua chữ S.

| Vị trí xe s | Độ cong tại xe, lane model | Độ cong thật | Sai vị trí vạch 0–30 m |
|---|---|---|---|
| 200 m | +0,00275 | +0,00127 | 0,068 m |
| 240 m | −0,00129 | +0,00101 | 0,113 m |
| 250 m | −0,00293 | +0,00010 | 0,113 m |
| 260 m | −0,00355 | −0,00092 | 0,059 m |

- Đa thức bậc 3 không biểu diễn được hai cung ngược chiều ngắn (57,1 m và 5,1 m) trong cùng tầm nhìn; sai lớn nhất ở hai đầu cửa sổ khớp, gồm cả ngay tại xe.
- Ở s = 240–250 m độ cong tại xe sai cả dấu. Ở 30 m/s, sai 0,003 1/m là sai 2,7 m/s² a_y.
- Đây là giới hạn của interface lane model dạng đa thức (SOTIF), không phải lỗi của ACC hay của adapter ASAM. Không sửa camera mô phỏng sau khi thấy kết quả.

## 3. Cách sửa

Có nhiều cách, mở PP-TS-005. QP hợp nhất (PP-TS-003) không sửa được vì vẫn dựa trên reference line sai.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| 20261111-1443-suite-regression-ef8bf4b | Tái hiện trên mốc V0: S14e trượt PP-SWR-051 (24 lần) và 100 (18 lần), cả 6 profile |

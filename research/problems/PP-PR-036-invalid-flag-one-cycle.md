# PP-PR-036 F16 a, c: message valid = false lệch 1–2 chu kỳ so với mất message

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở; chưa xác nhận được: harness bỏ khung valid = false, F16 không kiểm planner. Chờ trả harness về và sửa ở planner |
| Mở ngày | 2026-11-13 |
| Requirement bị ảnh hưởng | PP-SWR-130 |
| Tái hiện | [20261113-1803-suite-regression-3c31309](../runs/20261113-1803-suite-regression-3c31309/report.md): F16 a (lane model), F16 c (FunctionRequests) trên S1a, S1c |

## 1. Hiện tượng

| Ca | Chu kỳ khác ca tham chiếu | Trượt đầu tiên |
|---|---|---|
| F16 a, lane model `valid = false` 0,5 s | 2 | 4,233 s |
| F16 c, FunctionRequests `valid = false` 0,5 s | 1 | 4,033 s |
| F16 b, IMU qualifier FAULT | Đạt | — |

## 2. Nguyên nhân

Lớp nhận SIL ghi đè mẫu hợp lệ đang giữ khi nhận message `valid = false`. Ca song sinh bỏ frame đó và vẫn dùng mẫu hợp lệ trước đến timeout. Cùng sai khác ở F16(b) khi qualifier là FAULT.

## 3. Cách sửa

- Bỏ message không hợp lệ ở lớp nhận SIL trước khi nó thay mẫu gần nhất của lane model, FunctionRequests hoặc chassis. Bộ đếm khung CAN vẫn do lớp giải mã quản lý.
- Ca song sinh vẫn bỏ đúng các frame bị tác động. So toàn bộ output theo PP-SWR-130 như trước.

**Xem lại cách sửa (2026-11-14).** Interface Control Document 5.3: lớp nhận chỉ bỏ khung khi CRC sai hoặc counter lặp; khung có qualifier FAULT tới planner với `valid = false`, và PP-SWR-130 đòi planner xử lý như mất message. Bỏ khung `valid = false` ở `sim/harness.py` làm planner không còn nhận cờ này, nên F16 đạt mà không kiểm planner. Đề xuất: trả harness về như cũ, sửa ở planner (giữ mẫu hợp lệ cuối tới timeout).

## 4. Xác nhận

Trong SIL cục bộ, 24/24 lượt F16 đạt PP-SWR-130. Cả sáu lượt F16(b) có điều kiện chấm PP-SWR-142 đều đạt.

| Run ID | Kết quả |
|---|---|
| [20261114-1021-suite-regression-d7ed84c](../runs/20261114-1021-suite-regression-d7ed84c/report.md) | Không xác nhận. F16 a, b, c đạt 130 ở 24/24 lượt, nhưng `_receive_valid` trong `sim/harness.py` vẫn bỏ khung `valid = false` trước khi tới planner, nên kết quả đạt không kiểm hành vi của planner |

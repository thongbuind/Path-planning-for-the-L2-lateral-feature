# PP-PR-036 F16 a, c: message valid = false lệch 1–2 chu kỳ so với mất message

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã sửa, chờ hồi quy |
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

**2026-11-14.** Phần planner đã làm cùng PP-PR-035: T1 giữ message pub/sub dùng được gần nhất; message `valid = false` bị bỏ như mất message. Còn lại: bỏ việc lọc khung `valid = false` ở `sim/harness.py` (`_receive_valid`) để F16 kiểm planner; chờ người dùng đồng ý.

## 4. Xác nhận

Trong SIL cục bộ, 24/24 lượt F16 đạt PP-SWR-130. Cả sáu lượt F16(b) có điều kiện chấm PP-SWR-142 đều đạt.

| Run ID | Kết quả |
|---|---|
| [20261114-1021-suite-regression-d7ed84c](../runs/20261114-1021-suite-regression-d7ed84c/report.md) | Không xác nhận. F16 a, b, c đạt 130 ở 24/24 lượt, nhưng `_receive_valid` trong `sim/harness.py` vẫn bỏ khung `valid = false` trước khi tới planner, nên kết quả đạt không kiểm hành vi của planner |
| Sửa 2026-11-23, người phụ trách duyệt | `sim/harness.py` bỏ `_receive_valid`: lane model, LeadTarget, FunctionRequests và khung chassis có `valid = false` tới planner như Interface Control Document 5.3; lớp giải mã CAN vẫn bỏ khung CRC sai và counter lặp. `tests/sim` 147 test đạt. Chờ chạy lại F16 |
| Lượt nháp 2026-11-23, S1 a seed 1 | F16 a, c đạt PP-SWR-130. F16 b (IMU qualifier FAULT) trượt 1 chu kỳ lúc 4,008 s: planner đặt `path_valid = false` ngay ở khung FAULT đầu tiên, ca mất khung đặt ở chu kỳ sau khi hết timeout. Hai chu kỳ sau đó giống nhau |

## 5. Mâu thuẫn requirement (2026-11-23)

- PP-SWR-130 đòi qualifier FAULT cho output giống ca mất message. PP-SWR-142 đòi IMU, tốc độ, góc lái không hợp lệ thì `path_valid = false` trong không quá một chu kỳ. Planner hiện coi qualifier FAULT là cảm biến không hợp lệ và phản ứng sớm hơn ca mất khung một chu kỳ.
- Chờ người phụ trách chọn: giữ PP-SWR-130 và sửa planner, hoặc tách qualifier FAULT khỏi PP-SWR-130 (lỗi truyền thông theo E2E) sang PP-SWR-142 (cảm biến tự báo lỗi).
- 2026-11-23, người phụ trách chọn tách: SRS 1.27 bỏ qualifier FAULT khỏi PP-SWR-130, thêm vào PP-SWR-142 với F16 (b). `sim/faults/channel.py` không còn dựng ca mất khung cho qualifier FAULT trên kênh chassis. Lượt nháp F16 b: PP-SWR-142 đạt.

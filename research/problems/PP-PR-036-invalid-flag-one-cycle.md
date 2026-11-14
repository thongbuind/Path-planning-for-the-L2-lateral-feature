# PP-PR-036 F16 a, c: message valid = false lệch 1–2 chu kỳ so với mất message

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã sửa lớp nhận simulator, chờ hồi quy chính thức |
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

## 4. Xác nhận

Trong SIL cục bộ, 24/24 lượt F16 đạt PP-SWR-130. Cả sáu lượt F16(b) có điều kiện chấm PP-SWR-142 đều đạt.

| Run ID | Kết quả |
|---|---|

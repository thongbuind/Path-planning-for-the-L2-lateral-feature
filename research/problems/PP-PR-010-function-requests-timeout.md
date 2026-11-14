# PP-PR-010 FunctionRequests quá timeout vẫn báo path hợp lệ

| Mục | Nội dung |
|---|---|
| Trạng thái | Đóng; xác nhận ở 20261113-1803-suite-regression-3c31309 |
| Mở ngày | 2026-11-11 |
| Requirement bị ảnh hưởng | PP-SWR-145 |
| Tái hiện | Chẩn đoán nháp `diag-pp-swr-145-s1a-seed1` trên baseline `9b12b83`, S1a, seed 1, T7 quintic |

## 1. Hiện tượng

Chạy S1a bằng SIL và ngừng phát FunctionRequests từ 1,5 s. Ở các chu kỳ đã quá timeout 75 ms, PathStatus trả `active_function = NONE` và `path_valid = true`. `Trajectory.header.valid` cũng là true.

## 2. Nguyên nhân

`check_inputs()` bỏ FunctionRequests quá hạn. `plan_path()` vẫn tạo path hợp lệ từ các input còn lại. `pp_arbitrate()` chỉ đặt `active_function = NONE` và T11 dùng cờ hợp lệ của `plan_path()`.

## 3. Cách sửa

Ngày 2026-11-11, người dùng duyệt áp PP-SWR-145 tại chỗ xác định tính hợp lệ của output để PathStatus và Trajectory cùng phản ánh timeout.

T1 theo dõi thời gian từ lần nhận FunctionRequests hợp lệ gần nhất. Khi quá timeout, T9/T11 gửi NONE và vô hiệu path ở cả hai output.

## 4. Xác nhận

Unit test API `test_function_requests_timeout_and_recovery` kiểm trước, đúng và sau mốc timeout, rồi cấp lại message hợp lệ. Xác nhận SIL chính thức cần cây sạch và hai thư viện từ cùng commit.

Xác nhận chính thức [20261113-1803-suite-regression-3c31309](../runs/20261113-1803-suite-regression-3c31309/report.md): PP-SWR-145 đo ở 6 lần chạy, đạt.

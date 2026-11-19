# PP-PR-061 Thời gian tính đo bằng đồng hồ thật khi chạy nhiều tiến trình

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở; lỗi ở phía đánh giá |
| Mở ngày | 2026-11-17 |
| Requirement bị ảnh hưởng | PP-SWR-015; target PP-SWR-016; Software Qualification Test Specification 9.1 |
| Tái hiện | [20261115-1126-suite-full-7495822](../runs/20261115-1126-suite-full-7495822/report.md), `--jobs 4` |

## 1. Hiện tượng

- Lần chạy full, 3,5 triệu chu kỳ: 0,27 % chu kỳ vượt `t_budget` = 5 ms; 2 311 trên 3 952 lượt có ít nhất một chu kỳ vượt; lớn nhất 2 443 ms (S15 b, VP-4).
- Lượt đơn cùng planner, một tiến trình (S1 a + F06 d, 2026-11-16): 1 120 chu kỳ, không chu kỳ nào vượt khoảng 2 ms; trung bình khoảng 0,4 ms.

## 2. Nguyên nhân

Bên chấm đo đồng hồ thật của máy, gồm cả adapter (ghi chú `compute_time_note`). Khi chạy 4 tiến trình trên máy 8 GB, hệ điều hành ngắt tiến trình giữa chu kỳ; phần vượt là của máy, không phải của planner.

## 3. Cách sửa

Phía đánh giá, người dùng quyết định: đo thời gian CPU của luồng gọi `pp_step` thay cho đồng hồ thật, hoặc chấm khía cạnh thời gian tính (B8) trên một lượt chạy một tiến trình. Trước đó, số lớn nhất và p99 của B8 không dùng được để kết luận về planner.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

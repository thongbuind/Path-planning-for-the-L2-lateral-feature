# PP-PR-005 Nhiễu lane model trên cua chạm aysmax: path nhảy giữa hai chu kỳ

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở, đã tìm nguyên nhân; chờ PP-TS-003 |
| Mở ngày | 2026-11-11 |
| Requirement bị ảnh hưởng | PP-SWR-100 (qua PP-SWR-120) |
| Tái hiện | Lần chạy nháp `build/suites/smoke-20261111-1425`: F01 a, b, c trên đường chủ S1c, ACC tắt, VP-0, seed 1 |

## 1. Hiện tượng

| Ca | Lệch ngang giữa hai path liên tiếp (giới hạn 0,05 m) | DLC nhỏ nhất |
|---|---|---|
| S1c không nhiễu | 0,020 m | 0,48 m |
| S1c + F01 a (nhiễu ban ngày) | 0,095 m | 0,40 m |
| S1c + F01 c (nhiễu ban đêm × 2,5) | 0,088 m | 0,09 m |
| S1a + F01 a–c (cua nhẹ) | Đạt | Đạt |

- M1 chạy S1c + F01 c với ACC đọc LateralLimits và không trượt: xe giảm tốc nên a_y cần xuống dưới aysmax.
- Lần này ACC tắt, a_y cần đúng bằng aysmax (2,5 m/s²) suốt cung tròn.

## 2. Nguyên nhân

Đã phân tích trên lần chạy nháp S1c + F01 a, seed 1 (script chẩn đoán đọc Trajectory và PathStatus từng chu kỳ):

- Giả thuyết cờ bật tắt xen kẽ là sai: cờ đổi một lần trong cả ca.
- 16 chu kỳ vượt 0,05 m, đều ở đoạn clothoid vào cua (t = 9–11,2 s), khi phần xa của path bị T10 cắt về aysmax (14–17 trong 31 điểm).
- Ở chu kỳ xấu nhất, hai path gần như trùng ở 0–0,6 s, rồi lệch tăng tuyến tính: 0,016 m ở 0,9 s; 0,053 m ở 1,8 s; 0,089 m ở 2,7 s. Path mới vào trần aysmax chậm hơn path cũ một chút (a_y 2,466 so với 2,500 ở 0,9 s), tạo chênh lệch hướng; sau đó cả hai bị giữ ở trần nên chênh lệch hướng không mất đi.
- Cơ chế chung: path bị cắt là cung tròn chạy theo đà, không còn hội tụ về reference line; mọi khác biệt nhỏ ở đầu (nhiễu) lớn dần theo thời gian. T4 nối path trước T10, nên không còn gì giữ liên tục sau khi cắt.

## 3. Cách sửa

Đưa ràng buộc liên tục với path cũ và ràng buộc a_y vào cùng một bài toán: QP hợp nhất của PP-TS-003. Không vá riêng T10.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| 20261111-1443-suite-regression-ef8bf4b | Tái hiện trên mốc V0: F01 a, b, c trên S1c trượt PP-SWR-100 ở 84 lần chạy, cả 6 profile |

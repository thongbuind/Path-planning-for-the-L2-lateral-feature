# PP-PR-005 Nhiễu lane model trên cua chạm aysmax: path nhảy giữa hai chu kỳ

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở, cần tái hiện chính thức |
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

Chưa phân tích. Giả thuyết: khi a_y cần sát aysmax, nhiễu c2 làm phần cắt theo aysmax của T10 bật và tắt xen kẽ giữa các chu kỳ, nên path nhảy. Kiểm trước: chuỗi `lateral_limit_reached` và a_y của path theo chu kỳ trong đoạn cung tròn.

## 3. Cách sửa

Chưa chọn. Sửa cơ chế chung của T10 hoặc T4, không sửa riêng cho ca này.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

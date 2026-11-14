# PP-PR-044 F02 e lúc LKA đang lái: LKA tiếp tục trên lane model nhảy, xe sang phía đối diện

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-14 |
| Requirement bị ảnh hưởng | PP-SWR-085; liên quan 121, 030 |
| Tái hiện | [20261114-1021-suite-regression-d7ed84c](../runs/20261114-1021-suite-regression-d7ed84c/report.md): F02-e-S4a_at_lka_activep0.2, VP-3, seed 1 |

## 1. Hiện tượng

| Lần chạy | Kết quả |
|---|---|
| 20261113-2341-suite-regression-1014d20 | LKA bị bỏ giữa chừng: trượt 030 (39 chu kỳ), 084 (−0,15 m), 090 |
| 20261114-1021-suite-regression-d7ed84c | LKA chạy tới COMPLETED, nhưng DLC phía đối diện −0,104 m: trượt 085 |

- Lỗi mới duy nhất trong phạm vi của lần chạy d7ed84c so với 1014d20.

## 2. Nguyên nhân

Chưa phân tích hết. Đã tách:

| Thư viện | PP-SWR-085 | a_y lớn nhất path LKA |
|---|---|---|
| d7ed84c | −0,104 m | 1,11 m/s² |
| d7ed84c, tắt bản sửa PP-PR-041 (lần chạy nháp) | −0,519 m | 1,34 m/s² |

- Không do PP-PR-041: bỏ bản sửa đó thì trượt nặng hơn.
- Xuất hiện cùng bản sửa PP-PR-037 (giữ can thiệp khi F02). Giả thuyết: c0 nhảy 0,3–1,0 m lúc LKA đang lái, path can thiệp lấy mẫu trên reference line đã dời, nên kéo xe về phía đối diện.

## 3. Cách sửa

Chưa quyết. Cần xem log: T2 có nhận bước nhảy (k_jump) không, và reference line của path can thiệp có dời theo c0 không.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

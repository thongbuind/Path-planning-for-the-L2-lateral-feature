# PP-PR-017 Neo kế thừa sai hướng trôi hoặc tốc độ xe mục tiêu

| Mục | Nội dung |
|---|---|
| Trạng thái | Đóng; xác nhận ở 20261113-1803-suite-regression-3c31309 |
| Mở ngày | 2026-11-12 |
| Requirement bị ảnh hưởng | Định nghĩa S4b(c), S8(b) trong Software Qualification Test Specification mục 5 |
| Tái hiện | Đọc hai neo bằng `eval.loader.load` |

## 1. Hiện tượng

S4b(c) trôi về phía ngoài của cung như S4b(b). Xe mục tiêu S8(b) chạy 80 km/h như S8(a).

## 2. Nguyên nhân

Tập giá trị của hai neo bỏ sót tham số cần ghi đè từ neo danh định.

## 3. Cách sửa

Ghi rõ hướng trái, vào trong cung ở S4b(c), và tốc độ xe mục tiêu 20 m/s ở S8(b), theo định nghĩa đã có. Kiểm lại các giá trị sau khi nạp.

## 4. Xác nhận

Chạy unit test kiểm tham số hai neo. Sinh lại manifest trước khi chạy SIL.

Xác nhận chính thức [20261113-1803-suite-regression-3c31309](../runs/20261113-1803-suite-regression-3c31309/report.md): S4b(c), S8(b) chạy đúng tham số; không có trượt trong phạm vi.

# PP-PR-016 Kết quả khoảng hở xe mục tiêu không ghi được JSON

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã sửa, chờ xác nhận chính thức |
| Mở ngày | 2026-11-12 |
| Requirement bị ảnh hưởng | PP-SWR-088 |
| Tái hiện | S7(a–d), S8(a–e) khi ghi kết quả SIL |

## 1. Hiện tượng

Chương trình tính được khoảng hở ngang và in ra kết quả nhưng lỗi lúc ghi JSON.

## 2. Nguyên nhân

Phép chiếu dùng mẫu ground truth NumPy, trả scalar NumPy sang phép so ngưỡng. Kết quả so sánh có kiểu bool của NumPy.

## 3. Cách sửa

Chuyển giá trị và kết quả so sánh sang kiểu Python tại nơi tạo Criterion.

## 4. Xác nhận

Unit test serialize kết quả có PP-SWR-088. Chạy lại neo xe mục tiêu bằng cùng đầu vào.

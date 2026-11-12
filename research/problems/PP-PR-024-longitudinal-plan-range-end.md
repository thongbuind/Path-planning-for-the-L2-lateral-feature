# PP-PR-024 LongitudinalPlan ở đầu cao của dải làm Trajectory có vô cực

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-12 |
| Requirement bị ảnh hưởng | Software Qualification Test Specification 11, C2 (hai đầu dải của input); Interface Control Document 4, 5.7; PP-SWR-010 |
| Tái hiện | Lần chạy nháp: `python3 -m eval.conformance --planner build/planner/libpp_planner.dylib`, thư viện build lúc 12:38 ngày 2026-11-12, chưa có lần chạy chính thức |

## 1. Hiện tượng

- B0 trượt C2.robust: khi LongitudinalPlan mang giá trị ở đầu cao của dải kiểu float32 (Software Qualification Test Specification 11, "Trường còn lại"), chu kỳ 0 gửi Trajectory có `points[11].pose.x = inf`.
- C2 trượt nghĩa là Bị chặn: `eval.suite` dừng sau B0, không chạy ca nào.

## 2. Nguyên nhân

Chưa phân tích. Giả thuyết: planner dùng tốc độ của LongitudinalPlan để tích phân vị trí trên lưới 0,1 s mà không kiểm dải, nên v·t tràn float32.

## 3. Cách sửa

Chưa quyết định. Hướng cần xét: kiểm dải và bỏ LongitudinalPlan ngoài dải vật lý (như input không hợp lệ), hoặc kẹp tốc độ theo giới hạn của ODD.

## 4. Xác nhận

Chưa có.

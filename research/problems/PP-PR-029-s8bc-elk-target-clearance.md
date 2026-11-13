# PP-PR-029 S8b(c): ELK để khoảng cách ngang tới xe sau dưới 0,3 m

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở; chờ quyết định về truy vết |
| Mở ngày | 2026-11-13 |
| Requirement bị ảnh hưởng | PP-SWR-088 (cột Kiểm chứng: S7, S8; chưa có S8b) |
| Tái hiện | Lần chạy nháp 2026-11-13: `python3 -m eval.runner S8b c --seed 1`, VP-0, thư viện build từ `1f61551` có sửa đổi |

## 1. Hiện tượng

- S8b(c) chuyển thành ca can thiệp (PP-PR-027). Planner lái ELK, đưa xe về làn cũ, không va chạm (`no_impact`), DTLE −0,29 m.
- Khoảng cách ngang nhỏ nhất từ thân xe tới xe sau trong lúc ELK lái là 0,22 m. Ngưỡng của PP-SWR-088 là ≥ 0,3 m.
- Bên chấm xếp lần trượt này ngoài phạm vi, vì cột Kiểm chứng của PP-SWR-088 chỉ có S7, S8.

## 2. Nguyên nhân

Chưa phân tích. Hai câu hỏi tách riêng:

- Truy vết: PP-SWR-088 nói "trong lúc ELK can thiệp vì xe ở làn bên". S8b (c, d, e) là ELK vì xe ở làn bên, nhưng không có trong cột Kiểm chứng. Đây là lỗ hổng truy vết của Software Requirements Specification, không phải của bên chấm.
- Planner: REQUEST tới sau lúc lốp chạm vạch (chế độ B 4,91 s, lốp chạm vạch 4,58 s), nên path ELK bắt đầu khi xe đã lấn sang làn bên. Cần xem path ELK có kéo xe về đủ sớm không, hay giới hạn a_y, jerk của ELK (PP-SWR-111, 113, 115) không cho kéo nhanh hơn.

## 3. Cách sửa

- Truy vết: thêm S8b (c, d, e) vào cột Kiểm chứng của PP-SWR-088. Cần người duyệt.
- Planner: phân tích sau khi có lần chạy chính thức; sửa cơ chế chung, không riêng cho S8b.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

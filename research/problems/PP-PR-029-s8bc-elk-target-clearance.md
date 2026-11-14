# PP-PR-029 S8b(c): ELK để khoảng cách ngang tới xe sau dưới 0,3 m

| Mục | Nội dung |
|---|---|
| Trạng thái | Đóng; xác nhận ở 20261113-2255-suite-regression-e99cf08 |
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

Ước lượng 2026-11-13 (tính tay, chưa có log chính thức):

- Bên chấm (`_target_geometry`) đo khoảng hở ngang trong suốt lần ELK, kể cả khi xe sau còn ở phía sau theo phương dọc.
- Xe sau tâm tại 3,175 m nên mép trong cách vạch 0,475 m. Lúc REQUEST, xe đã trôi ra 0,5 m/s × 0,33 s ≈ 0,17 m kể từ lúc lốp chạm vạch. Khoảng hở ngang lúc REQUEST vào khoảng 0,2–0,26 m, đã dưới 0,3 m trước khi planner được lái.
- Nếu đúng, không planner nào đạt PP-SWR-088 ở S8b(c) theo cách đo hiện tại. Thêm S8b(c) vào cột Kiểm chứng như hiện tại sẽ tạo một test không đạt được.
- Cần quyết định trước khi sửa truy vết: PP-SWR-088 đo khi hai xe chồng nhau theo phương dọc, hay tính từ trạng thái lúc REQUEST. Euro NCAP SA 4.3.3.4 chỉ đòi không va chạm.

Quyết định: thongbui, 2026-11-13. PP-SWR-088 đo khi xe ở làn bên ngang hàng với xe mình (phần dọc của xe kia chồng lên thân xe), theo nghĩa Ngang hàng đã có ở Software Requirements Specification. Lý do: khoảng hở ngang khi xe kia còn ở phía sau không cho biết rủi ro va chạm. Đã đưa vào: Software Requirements Specification 1.15 (PP-SWR-088, định nghĩa Ngang hàng), Software Qualification Test Specification 1.36 mục 8.2, `eval/metrics.py` (`_target_geometry`), hai unit test mới; `tools/trace.py` không lỗi.

## 3. Cách sửa

- Truy vết: thêm S8b (c, d, e) vào cột Kiểm chứng của PP-SWR-088. Người dùng duyệt 2026-11-13, cùng lúc với cách đo khi ngang hàng.
- Planner: phân tích sau khi có lần chạy chính thức; sửa cơ chế chung, không riêng cho S8b.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

Xác nhận chính thức [20261113-2255-suite-regression-e99cf08](../runs/20261113-2255-suite-regression-e99cf08/report.md): PP-SWR-088 chấm trong phạm vi ở S8b c, d, e (18 lần chạy), đạt hết: khoảng hở khi ngang hàng 0,79–1,13 m. ELK kéo xe về kịp trước khi xe sau tới ngang.

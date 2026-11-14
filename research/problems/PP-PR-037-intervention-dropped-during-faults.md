# PP-PR-037 Can thiệp bị bỏ giữa chừng khi có lỗi input (PP-SWR-030)

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã sửa nhánh F02. F20, G01 còn mở |
| Mở ngày | 2026-11-13 |
| Requirement bị ảnh hưởng | PP-SWR-030; liên quan 043, 121, 143 |
| Tái hiện | [20261113-1803-suite-regression-3c31309](../runs/20261113-1803-suite-regression-3c31309/report.md): F02 a–e, F20 a trên S4a, S5a lúc đang can thiệp; G01 S4c |

## 1. Hiện tượng

| Ca | Trượt 030 | Ghi chú |
|---|---|---|
| F02 (c0 nhảy) lúc LKA, ELK đang lái | 2–39 chu kỳ, 20 lần chạy | Khoảng 1 s (gần `T_confirm`); khối Chức năng ADAS gửi REQUEST lần hai. Ở ELK còn trượt 100 (0,06–0,42 m), 101, 102 |
| F20 a (ego-motion không hợp lệ) lúc LKA, ELK | 214–418 chu kỳ, 4 lần chạy | Path không hợp lệ theo PP-SWR-143 |
| G01 S4c (đêm mưa, F04 a) lúc LKA | 10–254 chu kỳ, 6 lần chạy | Kèm 032 |

## 2. Nguyên nhân

Hai nguyên nhân khác nhau.

**F20: mâu thuẫn giữa requirement.** PP-SWR-143 bắt `path_valid = false`, PP-SWR-043 bắt khi đó chức năng là NONE. PP-SWR-030 lại bắt chọn LKA vì còn REQUEST. Không planner nào thoả cả ba. Bên chấm đang chấm 030 ở cả các chu kỳ mà 043 bắt buộc NONE.

**F02: giả thuyết, cần log.**
- T2 loại vạch nhảy, nên reference line chuyển sang coast.
- Khi coast, can thiệp chỉ tiếp tục nếu `coast_ok` (`pp_planner.c`): `old.valid && !outside_boundary(&lane, conf_inferred)`.
- `outside_boundary` trả true khi có bất kỳ L2, R2 hoặc mép đường nào được đo đủ tin. Trên S4a nhiều làn thì luôn có, nên LKA, ELK bị bỏ suốt cửa sổ xác nhận.
- PP-SWR-047 chỉ cấm LKA, ELK khi tâm làn chỉ suy được từ biên ngoài làn. Coast trên reference line đã nhớ của làn mình không thuộc trường hợp đó. Có thể `coast_ok` đang thay tạm cho bước 4 của T2 chưa cài (PP-PR-030).

G01 S4c: chưa phân tích; có thể cùng cơ chế với F02 hoặc với PP-PR-038 (mất một vạch).

Nguồn liên quan:

| Văn bản | Mục | Nội dung |
|---|---|---|
| R171 | 5.3.5.1.1 | Tránh dao động nhanh giữa stand-by và active |
| R171 | Annex 3, 4.1.3.2 (a), (b) | Không chấm dứt hỗ trợ ngay khi vạch tạm thời không thấy; tránh mất trợ lực lái đột ngột |
| EU 2021/646 | Annex I Part 2, 3.6.3.1 | Không mất hỗ trợ lái đáng kể đột ngột (sau ghi đè) |

## 3. Cách sửa

- F20: sửa PP-SWR-030 (hoặc cách chấm): chỉ áp khi planner được phép có path hợp lệ; các chu kỳ mà 043 bắt NONE không tính cho 030.
- F02: giữ can thiệp đang chạy khi T2 coast trên reference line của làn ego và path cũ còn hợp lệ. Nếu reference line có cờ `inferred`, PP-SWR-047 vẫn chặn can thiệp.
- Làm cùng PP-PR-030, vì cả hai dựa vào bước 4 của T2.

## 4. Xác nhận

Hồi quy cục bộ trên bảy lượt F02(a, b, d, e) từng trượt PP-SWR-030, gồm LKA và ELK, đã hết trượt ở cả bảy lượt. Cần hồi quy đầy đủ trên baseline sạch. F20 và G01 vẫn cần phân tích riêng.

| Run ID | Kết quả |
|---|---|

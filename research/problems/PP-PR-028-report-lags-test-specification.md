# PP-PR-028 Báo cáo benchmark lệch Software Qualification Test Specification 8.3, 8.4

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã sửa, chờ xác nhận chính thức |
| Mở ngày | 2026-11-13 |
| Requirement bị ảnh hưởng | Software Qualification Test Specification 8.3 (flexibility), 8.4 (tên kết luận), 11 (B0) |
| Tái hiện | Lần chạy nháp `20261113-1218-full-ecf2f15`, `report.md` |

## 1. Hiện tượng

- Kết luận ghi "Bị chặn". Software Qualification Test Specification 1.30 đã đổi tên thành Không đạt, Không đạt quy định, Đạt trong phạm vi đã thử. B0 cũng ghi "Bị chặn" thay cho "Không đạt" của mục 11.
- Bảng flexibility ghi tỉ lệ lần chạy đạt trên mọi lần chạy. Mục 8.3 quy định tỉ lệ requirement đạt trên từng profile, trên bộ chạy B7. Số lần chạy mỗi profile khác nhau nhiều (VP-0 1052, VP-2 440), nên tỉ lệ lần chạy không so được giữa profile.

## 2. Nguyên nhân

- `eval/conclusion.py`, `eval/suite.py`, `eval/conformance.py` chưa theo bản 1.30.
- `eval/presentation.flexibility` đếm lần chạy không trượt, lấy mọi lần chạy.

## 3. Cách sửa

| Chỗ sửa | Nội dung |
|---|---|
| `eval/conclusion.py` | Tên kết luận theo mục 8.4; `level_of` dùng chung |
| `eval/suite.py`, `eval/conformance.py` | B0 trượt C1 hoặc C2: "Không đạt" |
| `eval/presentation.py` | Flexibility chỉ trên lần chạy thuộc B7; tỉ lệ = requirement không trượt ở lần chạy nào của profile chia requirement được chấm trên profile; thêm cột requirement trượt |
| `tests/eval/test_conclusion.py`, `test_compare.py`, `test_flexibility.py` | Theo tên mới; kiểm cách tính flexibility |

Chưa sửa: trang B7 của dashboard HTML (`eval/report_html.py`) vẫn hiện số lần chạy đạt trên số lần chạy, có ghi rõ đơn vị. Đổi trang này kéo theo chuỗi song ngữ, làm riêng.

## 4. Xác nhận

Chưa có lần chạy chính thức. Unit test đạt 2026-11-13.

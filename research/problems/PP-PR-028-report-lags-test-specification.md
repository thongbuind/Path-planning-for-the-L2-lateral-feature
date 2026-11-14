# PP-PR-028 Báo cáo benchmark lệch Software Qualification Test Specification 8.3, 8.4

| Mục | Nội dung |
|---|---|
| Trạng thái | Đóng |
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
| `eval/report_html.py`, `eval/report_strings.py` | Bảng B7 dùng cùng dữ liệu chấm theo requirement với báo cáo Markdown. Hiển thị số requirement đạt trên số đã chấm và tỉ lệ cho từng profile, ở cả bản Việt và bản Anh |
| `tests/eval/test_conclusion.py`, `test_compare.py`, `test_flexibility.py` | Theo tên mới; kiểm cách tính flexibility |
| `tests/eval/test_report_html.py` | Kiểm cách đếm requirement duy nhất, phạm vi chấm và profile chưa có requirement được chấm |

## 4. Xác nhận

Ngày 2026-11-14, xuất lại dashboard bằng dữ liệu đã lưu của lần hồi quy chính thức [20261113-2255-suite-regression-e99cf08](../runs/20261113-2255-suite-regression-e99cf08/report.md). Kết luận tính lại trùng báo cáo lưu qua 2.073 lượt. Bảng B7 trong cả hai bản HTML khớp Markdown trên 803 lượt B7 và sáu profile. VP-0 đạt 23/29 requirement (79,3%).

Kiểm thêm nhánh B0 trượt C2 bằng dữ liệu test. Kết luận B0 hiện “Không đạt”. Các kiểm tra liên quan đạt 45/45.

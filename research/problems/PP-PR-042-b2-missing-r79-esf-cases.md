# PP-PR-042 B2 không có ca cho bài ESF với xe làn bên của R79

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở, đã sửa bên chấm trong cây làm việc; chờ xác nhận |
| Mở ngày | 2026-11-14 |
| Requirement bị ảnh hưởng | Không có requirement nào trượt; độ phủ của B2 (Software Qualification Test Specification 5.1, 5.3) |
| Tái hiện | Lần chạy nháp `build/benchmark/20261114-0018-full-1014d20`, trang B2: "ESF với xe làn bên, chưa có lần chạy". Cùng tình trạng ở [20261113-2341-suite-regression-1014d20](../runs/20261113-2341-suite-regression-1014d20/report.md) |

## 1. Hiện tượng

- Mục 5.1 gán bài R79 Annex 8, 3.3.1, 3.3.2 cho S7, S8. Báo cáo B2 ghi bài này "chưa có lần chạy" và tính 8/11 bài đạt.
- Các ca S7 (a–e), S8 (a–e) có chạy trong regression (75 lần) và full (148 lần), nhưng ở các bộ khác. S7 a trượt PP-SWR-100 ở 4 lần trong full (PP-PR-041). Nếu được tính, bài này trượt.

## 2. Nguyên nhân

- `benchmark/suites/aspects.yaml`: B2 gồm lưới protocol và các neo S1, S1b, S14, S5, S9. Không có neo S7, S8.
- Ca S7, S8 của lưới Euro NCAP mang nhãn protocol Euro NCAP LSS. `eval/report_html.py` (`test_of`) chỉ gán ca protocol vào hàng của chính văn bản đó. Đúng: hình học của lưới Euro NCAP không phải điểm thử của R79.
- Kết quả: hàng R79 không có ca nào.

## 3. Cách sửa

Bên chấm, không đổi planner:

- `aspects.yaml`: B2 thêm neo S7 (a, b, c, d, e), S8 (a, b, c, d, e). Không gồm S8 late (bài bổ sung của PP-SWR-089, không phải điểm thử của R79).
- Software Qualification Test Specification 1.38, mục 5.1: hàng R79 ghi biến thể theo hai điểm thử. 3.3.1 (xe làn bên áp sát, không chủ ý): S7, S8 (a, b, e). 3.3.2 (chuyển làn chủ ý): S8 (c, d).
- Test `tests/eval/test_aspects_regulatory.py`: mọi hàng SIL của mục 5.1 có ca trong B2.
- Đây là bổ sung độ phủ cho một bài chưa có ca, không chọn ca theo kết quả: đã biết trước bài này sẽ trượt cho tới khi PP-PR-041 được xác nhận.

Lần chạy nháp ngày 2026-11-14 (`build/pr041-b2`): bài ESF với xe làn bên có 60 lần chạy, đạt 60 khi có bản sửa PP-PR-041. Chưa phải xác nhận chính thức.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

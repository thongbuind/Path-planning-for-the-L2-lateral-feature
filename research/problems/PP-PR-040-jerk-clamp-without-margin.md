# PP-PR-040 T10 kẹp jerk đúng bằng giới hạn, không có biên

| Mục | Nội dung |
|---|---|
| Trạng thái | Đã sửa; nháp đạt, chờ xác nhận chính thức |
| Mở ngày | 2026-11-13 |
| Requirement bị ảnh hưởng | PP-SWR-003 (cùng cơ chế: 115 với ELK, 114 với LKA) |
| Tái hiện | [20261113-2255-suite-regression-e99cf08](../runs/20261113-2255-suite-regression-e99cf08/report.md): S17 b, VP-2 đến VP-5, seed 1 |

## 1. Hiện tượng

- PP-SWR-003, jerk ngang lớn nhất của path khi HWA lái: 5,000000001 m/s³, ngưỡng ≤ 5 m/s³. Ngoài phạm vi (cột Kiểm chứng của 003 chỉ có S1).
- Lần hồi quy trước ([20261113-1803-suite-regression-3c31309](../runs/20261113-1803-suite-regression-3c31309/report.md)): 1,9–2,2 m/s³ trên cùng ca.
- Xuất hiện từ PP-TS-017: khi tài xế đổi làn nhanh, path "giữ độ lệch" phải chặn vận tốc ngang lớn của xe, nên T10 cắt jerk tới đúng giới hạn.

## 2. Nguyên nhân

`planner/src/feasibility.c` dòng 104: jerk mỗi bước kẹp trong `ay_prev ± jerk_max·dt`, không nhân `PP_LIMIT_SCALE`. Giới hạn a_y và độ cong (dòng 77, 95) đã nhân `PP_LIMIT_SCALE`. Path lại truyền qua interface dạng float32, nên giá trị kẹp sát giới hạn có thể vượt một lượng làm tròn.

## 3. Cách sửa

- T10: nhân `PP_LIMIT_SCALE` cho jerk như cho a_y, để path luôn có biên dưới giới hạn. Sửa chung cho HWA, LKA, ELK.
- Không đổi ngưỡng và cách chấm của bên chấm.
- Câu hỏi riêng, chưa đề xuất làm: trong lúc ghi đè, path có nên chặn vận tốc ngang của xe mạnh tới giới hạn jerk không (PP-TS-017). Khi tài xế lái, path chỉ để controller không kéo ngược; chặn nhẹ hơn có thể hợp hơn.

Đã sửa 2026-11-13:

| Chỗ sửa | Nội dung |
|---|---|
| `planner/src/feasibility.c` | Bước jerk = `PP_LIMIT_SCALE`·`jerk_max`·dt, như a_y. Software Detailed Design T10 đã ghi "mỗi giới hạn chừa 10⁻⁶ tương đối"; code chưa làm với jerk, nên không sửa tài liệu |
| `tests/planner/c/test_feasibility.c` | `test_jerk_stays_below_limit_after_float32`: lưới 40 tốc độ × 11 mức a_y đầu, bước ngược chiều; đo jerk trên điểm float32. Trước khi sửa: trượt (vượt giới hạn); sau khi sửa: đạt |

- 14/14 unit test C đạt.
- Lần chạy nháp 2026-11-13 (`benchmark/suites/PP-PR-032.yaml`, `e99cf08` có sửa đổi): jerk lớn nhất ở S17 b 4,999995 m/s³ (trước 5,000000001), PP-SWR-003 không còn trượt; các tiêu chí khác như [20261113-2330-matrix-PP-PR-032-e99cf08](../runs/20261113-2330-matrix-PP-PR-032-e99cf08/summary.md).

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

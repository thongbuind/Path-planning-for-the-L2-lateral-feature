# PP-PR-076 G01 trên S1c, VP-5: DLC âm nhẹ

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-18 |
| Requirement bị ảnh hưởng | PP-SWR-051 |
| Tái hiện | [20261118-2030-suite-regression-e3158a5](../runs/20261118-2030-suite-regression-e3158a5/report.md), `G01-S1c-VP-5-38898514a806`, seed 1, 2 |

## 1. Hiện tượng

PP-SWR-051: DLC nhỏ nhất −0,030 m (seed 1) và −0,003 m (seed 2). Lỗi này đã có ở baseline 20261118-1546-suite-regression-edb02b8.

## 2. Nguyên nhân

Chưa phân tích. Giả thuyết: S1c cần a_y đúng bằng aysmax nên không còn biên để kéo xe về, giống PP-PR-049, cộng thêm nhiễu của G01.

Trong [hồi quy bb08d77](../runs/20261119-0948-suite-regression-bb08d77/report.md), DLC nhỏ nhất của cả hai seed xuất hiện ở 21,991 s. Tại chu kỳ planner gần nhất, path còn hợp lệ, `lcc_mode = LANE` và cờ giới hạn đang bật. Gia tốc ngang thật khoảng 2,50–2,51 m/s² ở 25 m/s.

## 3. Cách sửa

Chưa làm. Xem lại sau khi có quyết định của PP-TS-020.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| 20261118-2030-suite-regression-e3158a5 | Còn trượt, BLOCKER |
| [20261119-0948-suite-regression-bb08d77](../runs/20261119-0948-suite-regression-bb08d77/report.md) | VP-5 seed 1 và 2 còn trượt PP-SWR-051 |

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

## 3. Cách sửa

Chưa làm. Xem lại sau khi có quyết định của PP-TS-020.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| 20261118-2030-suite-regression-e3158a5 | Còn trượt, BLOCKER |

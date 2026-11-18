# PP-PR-073 COMPLETED lệch thời điểm khi lane model nhiễu

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-18 |
| Requirement bị ảnh hưởng | PP-SWR-032, 090 |
| Tái hiện | [20261118-1546-suite-regression-edb02b8](../runs/20261118-1546-suite-regression-edb02b8/report.md) |

## 1. Hiện tượng

S12, F01, G01: PP-SWR-032 trượt 20 lần, PP-SWR-090 trượt 9 lần (có F02 e).

## 2. Nguyên nhân

Điều kiện kết thúc tính trên ước lượng nhiễu nên đứt quãng hoặc đạt sớm hơn trạng thái thật. `T_end_margin` 0,1 s giảm báo sớm nhưng không xử lý được nhiễu.

## 3. Cách sửa

Chưa làm. Hướng xem: dung sai có trễ cho điều kiện kết thúc; cần đo lại PP-SWR-032 và 090 cùng lúc.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|
| 20261118-2030-suite-regression-e3158a5 | Còn trượt, mức MINOR |

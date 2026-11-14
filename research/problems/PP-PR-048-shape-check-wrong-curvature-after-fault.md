# PP-PR-048 F06 c (sai c3) và F06 d lúc LKA, ELK trượt sau khi bật kiểm hình dạng

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở, đã khoanh vùng |
| Mở ngày | 2026-11-14 |
| Requirement bị ảnh hưởng | PP-SWR-051; PP-SWR-086; PP-TS-001 |
| Tái hiện | [20261114-1952-suite-regression-0776bad](../runs/20261114-1952-suite-regression-0776bad/report.md): F06 c trên S1a, S1c; F06 d trên S4a, S5a lúc LKA, ELK |

## 1. Hiện tượng

- F06 c (c3 + 4·10⁻⁶ 1/m² trên mọi vạch, 1 s): DLC −0,97 đến −1,27 m ở 6 lượt. Đạt ở d7ed84c (trước khi bật kiểm hình dạng).
- Log F06 c trên S1a, VP-1: lỗi kéo dài 4,0–5,0 s, nhưng độ cong cuối path tiếp tục tăng tới 0,0018 1/m sau khi lỗi hết; xe trôi 0,8 m lúc 7,4 s rồi rời làn.
- F06 d lúc LKA, ELK: PP-SWR-086 trượt, DTLE không đo được (NaN), 4 lượt.
- Lần chạy nháp cùng commit 13913da (thư viện J0 và J0 kiểm hình dạng của PP-TS-001), F06 c trên S1a seed 1: J0 đạt (DLC 0,38 m), J0 kiểm hình dạng trượt (−0,97 m). F06 d lúc LKA: J0 trượt 032, J0 kiểm hình dạng trượt 086.

## 2. Nguyên nhân

- Giả thuyết, chưa kiểm: lỗi kéo dài 1 s, bằng `T_confirm`; hình dạng sai được nhận đúng lúc lỗi sắp hết. Khi lỗi hết, hình dạng đúng lại bị coi là bước nhảy so với bộ nhớ, nên bị loại thêm `T_confirm`. R2 (quay về vị trí cũ thì nhận ngay) chỉ so c0, không so hình dạng.
- F06 c không có trong bộ chạy của PP-TS-001.

## 3. Cách sửa

- Kiểm giả thuyết bằng log của bộ nhớ biên (unit test T2 với chuỗi frame như F06 c).
- Hướng chung: R2 so cả hình dạng với bộ nhớ trước thay đổi.
- Sau khi sửa: chạy lại PP-TS-001 có thêm F06 c và F06 d lúc LKA, ELK (mở lại khóa, ghi lý do).

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

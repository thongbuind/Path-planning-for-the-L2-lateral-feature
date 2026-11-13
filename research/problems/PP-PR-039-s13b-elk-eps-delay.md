# PP-PR-039 S13 b, ELK, VP-3: EPS chậm 100 ms, DTLE −0,45 m

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-13 |
| Requirement bị ảnh hưởng | PP-SWR-091, 085, 086, 100, 102 |
| Tái hiện | [20261113-1803-suite-regression-3c31309](../runs/20261113-1803-suite-regression-3c31309/report.md): `S13-b-elk-VP-3`, seed 1 |

## 1. Hiện tượng

| Tiêu chí | Giá trị | Ngưỡng |
|---|---|---|
| PP-SWR-091 DTLE vạch khi EPS chậm tới 100 ms | −0,45 m | ≥ −0,3 m |
| PP-SWR-086 DTLE vạch | −0,45 m | ≥ −0,3 m |
| PP-SWR-085 DLC phía đối diện qua bàn giao EPS | −0,09 m | ≥ 0 |
| PP-SWR-100 | 0,097 m | ≤ 0,05 m |
| PP-SWR-102 | 0,0004 1/m | ≤ 0,0003 1/m |

Chỉ 1 trong 6 profile. Các profile khác của S13 b ELK đạt.

## 2. Nguyên nhân

Chưa phân tích. Cần log: path ELK đã đủ sớm chưa, hay xe bám trễ vì EPS chậm (giống PP-PR-006), và vì sao chỉ VP-3.

Nguồn: DTLE −0,3 m theo Euro NCAP SA 4.3.2 và EU 2021/646 Annex I Part 2, 3.6.2; mức trễ EPS 100 ms của PP-SWR-091 là nhóm tự thống nhất.

## 3. Cách sửa

Sau khi có nguyên nhân. Sửa cơ chế chung, không riêng cho VP-3.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

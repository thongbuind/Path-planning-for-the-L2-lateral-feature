# PP-PR-086 S14 e: QP ADMM 150 vòng lệch 0,23 m so với nghiệm 1000 vòng

| Mục | Nội dung |
|---|---|
| Trạng thái | Mở |
| Mở ngày | 2026-11-25 |
| Requirement bị ảnh hưởng | Không trượt requirement; ảnh hưởng chất lượng nghiệm của `qp_jerk_admm` (PP-TS-031 H2 đến H4) |
| Tái hiện | [20261125-0007-study-PP-TS-031-074a928](../runs/20261125-0007-study-PP-TS-031-074a928/summary.md), `output_diff.json`: S14e [acc=ignore_limits, loop=open], seed 3, 4 |

## 1. Hiện tượng

- Cua chữ S của S1f ở 130 km/h, khúc R = 374 m cần 3,5 m/s², vượt aysmax.
- Lệch output 0–1 s so với `qp_jerk_admm_it1000_ref`, vòng hở:

| Số vòng | Lệch lớn nhất [m] | Chu kỳ khác / so được |
|---|---|---|
| 25 | 0,16 | 485 / 876 |
| 50 | 0,40 | 488 / 876 |
| 150 | 0,23 | 459 / 876 |

- Các lượt vòng hở khác của phần test dưới 2,5 mm ở 150 vòng. Không giảm đều theo số vòng.

## 2. Nguyên nhân

Chưa phân tích. Giả thuyết: ràng buộc a_y chạm cứng ở mọi điểm của khúc cua, ADMM chưa hội tụ trong 150 vòng, và warm start mang nghiệm chưa hội tụ sang chu kỳ sau. Chưa kiểm nghiệm 1000 vòng đã hội tụ hay chưa.

## 3. Cách sửa

Chưa làm.

## 4. Xác nhận

| Run ID | Kết quả |
|---|---|

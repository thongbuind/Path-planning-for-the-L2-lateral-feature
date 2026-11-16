# Study PP-TS-003

Plan: `research/studies/PP-TS-003-path-generator/plan.yaml`, locked 2026-11-14; suite PP-TS-003.

Coi như ngang nhau khi chênh nhỏ hơn: PP-SWR-050 0.005, PP-SWR-051 0.01, PP-SWR-002 0.05

## tuning

| Bộ | Trượt | PP-SWR-050 | PP-SWR-125 | PP-SWR-002 | PP-SWR-053 | PP-SWR-003 |
|---|---|---|---|---|---|---|
| V0b | 3 | 0.5016 | 0.1621 | 0.1881 | 3.286 | 1.789 |
| V1b | 4 | 0.5544 | 0.1966 | 0.2153 | 0.943 | 4.814 |
| V1 | 6 | 0.5544 | 0.1966 | 0.2153 | 0.943 | 4.814 |
| V0 | 7 | 0.7858 | 0.1683 | 0.1881 | 3.286 | 1.789 |
| V2 | 14 | 1.383 | 0.5636 | 0.1094 | 3.326 | 4.864 |

- V0b: Như V0, T10 cắt path ứng viên trước khi T4 trộn, rồi kiểm lại
- V1b: Như V1, T10 cắt path ứng viên trước khi T4 trộn, rồi kiểm lại
- V1: QP hợp nhất (T7 C), phạt a_y vượt 2,0 m/s²
- V0: Quintic theo thời lượng (T7 A), T4 trộn, T10 cắt
- V2: QP hợp nhất (T7 C), phạt thẳng a_y² (qp_a_comfort = 0)

## test

| Bộ | Trượt | PP-SWR-050 | PP-SWR-125 | PP-SWR-002 | PP-SWR-053 | PP-SWR-003 |
|---|---|---|---|---|---|---|
| V0b | 6 | 0.4507 | 0.02785 | 0.4482 | 3.101 | 3.343 |
| V1b | 8 | 0.6028 | 0.03126 | 0.4935 | 2.221 | 4.51 |
| V1 | 10 | 0.6028 | 0.03126 | 0.4935 | 2.221 | 4.511 |
| V0 | 14 | 0.8857 | 0.02785 | 0.4482 | 3.101 | 3.209 |
| V2 | 24 | 1.477 | 0.2342 | 1.073 | 2.491 | 4.499 |

- V0b: Như V0, T10 cắt path ứng viên trước khi T4 trộn, rồi kiểm lại
- V1b: Như V1, T10 cắt path ứng viên trước khi T4 trộn, rồi kiểm lại
- V1: QP hợp nhất (T7 C), phạt a_y vượt 2,0 m/s²
- V0: Quintic theo thời lượng (T7 A), T4 trộn, T10 cắt
- V2: QP hợp nhất (T7 C), phạt thẳng a_y² (qp_a_comfort = 0)

- tuning V0: S12a:PP-SWR-100, S14e [acc=on]:PP-SWR-051, S14e [acc=on]:PP-SWR-100, S1c_F01a:PP-SWR-100
- test V0: S12d:PP-SWR-100, S14e [acc=ignore_limits]:PP-SWR-100, S14e [acc=ignore_limits]:PP-SWR-101, S14e [acc=ignore_limits]:PP-SWR-102, S1c_F01b:PP-SWR-100, S1c_F01c:PP-SWR-051, S1c_F01c:PP-SWR-100, S1c_F06e:PP-SWR-100
- tuning V0b: S14e [acc=on]:PP-SWR-051, S14e [acc=on]:PP-SWR-100
- test V0b: S14e [acc=ignore_limits]:PP-SWR-100, S14e [acc=ignore_limits]:PP-SWR-101, S14e [acc=ignore_limits]:PP-SWR-102
- tuning V1: S14e [acc=on]:PP-SWR-100, S14e [acc=on]:PP-SWR-102, S1be:PP-SWR-100
- test V1: S14e [acc=ignore_limits]:PP-SWR-051, S14e [acc=ignore_limits]:PP-SWR-100, S14e [acc=ignore_limits]:PP-SWR-101, S14e [acc=ignore_limits]:PP-SWR-102, S1bb:PP-SWR-100
- tuning V1b: S14e [acc=on]:PP-SWR-100, S14e [acc=on]:PP-SWR-102
- test V1b: S14e [acc=ignore_limits]:PP-SWR-051, S14e [acc=ignore_limits]:PP-SWR-100, S14e [acc=ignore_limits]:PP-SWR-101, S14e [acc=ignore_limits]:PP-SWR-102
- tuning V2: S12a:PP-SWR-051, S14e [acc=on]:PP-SWR-100, S14e [acc=on]:PP-SWR-101, S1ba:PP-SWR-100, S1be:PP-SWR-100, S1c_F01a:PP-SWR-051, S1c_F06b:PP-SWR-051, S1c_F06b:PP-SWR-100
- test V2: S14c:PP-SWR-100, S14e [acc=ignore_limits]:PP-SWR-051, S14e [acc=ignore_limits]:PP-SWR-100, S14e [acc=ignore_limits]:PP-SWR-101, S14e [acc=ignore_limits]:PP-SWR-102, S1bb:PP-SWR-005, S1bb:PP-SWR-006, S1bb:PP-SWR-007, S1bc:PP-SWR-100, S1bc:PP-SWR-102, S1c:PP-SWR-051, S1c_F01b:PP-SWR-051, S1c_F01c:PP-SWR-051, S1c_F06e:PP-SWR-051

# Study PP-TS-030

Plan: `research/studies/PP-TS-030-elk-object-return/plan.yaml`, locked 2026-11-23; suite PP-TS-030.

Coi như ngang nhau khi chênh nhỏ hơn: PP-SWR-082 0.25

## tuning

| Bộ | Trượt | PP-SWR-050 | PP-SWR-125 | PP-SWR-002 | PP-SWR-053 | PP-SWR-003 |
|---|---|---|---|---|---|---|
| V1 | 0 | — | — | — | — | 0 |
| V2 | 0 | — | — | — | — | 0 |
| V3 | 2 | — | — | — | — | 0 |
| V0 | 13 | — | — | — | — | 0 |

- V1: Về hai tốc độ; nhanh tới 0,2 m trước tâm trong 2 s, giữ vận tốc, chậm tới tâm trong T_return
- V2: Về hai tốc độ; nhanh tới 0,2 m trước tâm trong 1,5 s, giữ vận tốc, chậm tới tâm trong T_return
- V3: Đối chứng của PP-PR-077; một quintic, T_return_object 4 s
- V0: Bản hiện tại; đoạn về tâm một quintic, T_return_object 2 s

## test

| Bộ | Trượt | PP-SWR-050 | PP-SWR-125 | PP-SWR-002 | PP-SWR-053 | PP-SWR-003 |
|---|---|---|---|---|---|---|
| V1 | 0 | — | — | — | — | 0 |
| V2 | 0 | — | — | — | — | 0 |
| V3 | 0 | — | — | — | — | 0 |
| V0 | 22 | — | — | — | — | 0 |

- V1: Về hai tốc độ; nhanh tới 0,2 m trước tâm trong 2 s, giữ vận tốc, chậm tới tâm trong T_return
- V2: Về hai tốc độ; nhanh tới 0,2 m trước tâm trong 1,5 s, giữ vận tốc, chậm tới tâm trong T_return
- V3: Đối chứng của PP-PR-077; một quintic, T_return_object 4 s
- V0: Bản hiện tại; đoạn về tâm một quintic, T_return_object 2 s

- tuning V0: S12c:PP-SWR-094, S21a:PP-SWR-094, S7a:PP-SWR-094, S7b:PP-SWR-094, S8a:PP-SWR-094, S8b:PP-SWR-094, S8bc:PP-SWR-094
- test V0: S21b:PP-SWR-094, S21c:PP-SWR-094, S21e:PP-SWR-094, S7c:PP-SWR-094, S7d:PP-SWR-094, S7e:PP-SWR-094, S8bd:PP-SWR-094, S8be:PP-SWR-094, S8c:PP-SWR-094, S8d:PP-SWR-094, S8e:PP-SWR-094
- tuning V3: S8bc:PP-SWR-088

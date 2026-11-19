# Study PP-TS-022

Plan: `research/studies/PP-TS-022-blend-limit/plan.yaml`, locked 2026-11-17; suite PP-TS-022.

Coi như ngang nhau khi chênh nhỏ hơn: PP-SWR-050 0.005, PP-SWR-051 0.01

## tuning

| Bộ | Trượt | PP-SWR-050 | PP-SWR-125 | PP-SWR-002 | PP-SWR-053 | PP-SWR-003 |
|---|---|---|---|---|---|---|
| V1 | 2 | 1.077 | 1.101 | 0.3347 | 0.833 | 1.28 |
| V0 | 4 | 1.085 | 0.9782 | 0.3348 | 0.833 | 0.8727 |

- V1: Một λ; mỗi điểm so với ngưỡng của đoạn mình
- V0: Một λ; mọi điểm so với ngưỡng đoạn 0–1 s (bản hiện tại)

## test

| Bộ | Trượt | PP-SWR-050 | PP-SWR-125 | PP-SWR-002 | PP-SWR-053 | PP-SWR-003 |
|---|---|---|---|---|---|---|
| V1 | 3 | 1.148 | 1.127 | 0.4482 | 3.131 | 1.755 |
| V0 | 5 | 1.689 | 0.8885 | 0.4482 | 3.131 | 1.753 |

- V1: Một λ; mỗi điểm so với ngưỡng của đoạn mình
- V0: Một λ; mọi điểm so với ngưỡng đoạn 0–1 s (bản hiện tại)

- tuning V0: S1a_F03c:PP-SWR-051, S1a_F06d:PP-SWR-051
- test V0: S14e [acc=on]:PP-SWR-051, S1c_F03c:PP-SWR-051, S1c_F06d:PP-SWR-051
- tuning V1: S1a_F03c:PP-SWR-051
- test V1: S14e [acc=on]:PP-SWR-051, S1c_F03c:PP-SWR-051

# Study PP-TS-021

Plan: `research/studies/PP-TS-021-stitch-start/plan.yaml`, locked 2026-11-16; suite PP-TS-021.

Coi như ngang nhau khi chênh nhỏ hơn: PP-SWR-050 0.005, PP-SWR-051 0.01

## tuning

| Bộ | Trượt | PP-SWR-050 | PP-SWR-125 | PP-SWR-002 | PP-SWR-053 | PP-SWR-003 |
|---|---|---|---|---|---|---|
| V2 | 4 | 0.2991 | — | 0.3647 | 0.776 | 1.252 |
| V4 | 4 | 0.3086 | — | 0.3613 | 0.776 | 1.749 |
| V0 | 4 | 0.5016 | — | 0.1881 | 3.286 | 1.21 |
| V3 | 4 | 0.5334 | — | 0.1881 | 3.286 | 1.207 |
| V1 | 6 | 0.4835 | — | 0.3686 | 1.083 | 1.395 |

- V2: stitch_reset 0 m, luôn bắt đầu từ trạng thái đo
- V4: stitch_reset 0 m và trộn theo từng đoạn
- V0: stitch_reset 0,2 m; T4 bước 4 một λ cho cả path (bản hiện tại)
- V3: T4 bước 4 trộn theo từng đoạn 0–1 s, 1–2 s, sau 2 s
- V1: stitch_reset 0,1 m

## test

| Bộ | Trượt | PP-SWR-050 | PP-SWR-125 | PP-SWR-002 | PP-SWR-053 | PP-SWR-003 |
|---|---|---|---|---|---|---|
| V2 | 2 | 0.8236 | 0.03179 | 0.4512 | 3.061 | 1.77 |
| V4 | 4 | 0.8297 | 0.0484 | 0.4512 | 3.061 | 1.789 |
| V0 | 5 | 0.4511 | 0.02785 | 0.4482 | 3.101 | 1.809 |
| V1 | 6 | 0.443 | 0.02785 | 0.4482 | 3.101 | 1.794 |
| V3 | 6 | 0.4879 | 0.05299 | 0.4482 | 3.101 | 1.812 |

- V2: stitch_reset 0 m, luôn bắt đầu từ trạng thái đo
- V4: stitch_reset 0 m và trộn theo từng đoạn
- V0: stitch_reset 0,2 m; T4 bước 4 một λ cho cả path (bản hiện tại)
- V1: stitch_reset 0,1 m
- V3: T4 bước 4 trộn theo từng đoạn 0–1 s, 1–2 s, sau 2 s

- tuning V0: S1ba [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1, S1bb [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1
- test V0: S14e [acc=on]:PP-SWR-051, S1ba [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1, S1bb [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1
- tuning V1: S1ba [acc=ignore_limits]:PP-SWR-100, S1ba [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1, S1bb [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1
- test V1: S14e [acc=on]:PP-SWR-051, S1ba [acc=ignore_limits]:PP-SWR-100, S1ba [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1, S1bb [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1
- tuning V2: S1bb [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1, S2b:PP-SWR-100
- test V2: S1bb [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1
- tuning V3: S1ba [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1, S1bb [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1
- test V3: S14e [acc=on]:PP-SWR-051, S14e [acc=on]:PP-SWR-100, S1ba [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1, S1bb [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1
- tuning V4: S1bb [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1, S2b:PP-SWR-100
- test V4: S1bb [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1, S1c_F06e:PP-SWR-051

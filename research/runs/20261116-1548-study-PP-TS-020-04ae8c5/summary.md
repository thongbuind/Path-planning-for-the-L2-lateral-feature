# Study PP-TS-020

Plan: `research/studies/PP-TS-020-path-ay-ceiling/plan.yaml`, locked 2026-11-16; suite PP-TS-020.

Coi như ngang nhau khi chênh nhỏ hơn: PP-SWR-050 0.005, PP-SWR-051 0.01

## tuning

| Bộ | Trượt | PP-SWR-050 | PP-SWR-125 | PP-SWR-002 | PP-SWR-053 | PP-SWR-003 |
|---|---|---|---|---|---|---|
| V1a | 0 | 0.1233 | — | 0.1881 | 3.286 | 0.8759 |
| V1c | 0 | 0.1278 | — | 0.1881 | 3.286 | 0.8759 |
| V1b | 0 | 0.1284 | — | 0.1881 | 3.286 | 0.8759 |
| V0 | 4 | 0.5035 | — | 0.1881 | 3.286 | 0.8759 |

- V1a: Trần a_y của path HWA = aysmax + 0,1 m/s²
- V1c: Trần a_y của path HWA = aysmax + 0,3 m/s²
- V1b: Trần a_y của path HWA = aysmax + 0,2 m/s²
- V0: Trần a_y của path HWA = aysmax (bản hiện tại)

## test

| Bộ | Trượt | PP-SWR-050 | PP-SWR-125 | PP-SWR-002 | PP-SWR-053 | PP-SWR-003 |
|---|---|---|---|---|---|---|
| V1b | 6 | 0.2757 | 0.02817 | 0.09404 | 1.981 | 2.953 |
| V1c | 6 | 0.2757 | 0.02817 | 0.09404 | 1.981 | 2.953 |
| V1a | 8 | 0.2757 | 0.02817 | 0.09404 | 1.981 | 2.953 |
| V0 | 10 | 0.4511 | 0.02817 | 0.09404 | 1.981 | 2.953 |

- V1b: Trần a_y của path HWA = aysmax + 0,2 m/s²
- V1c: Trần a_y của path HWA = aysmax + 0,3 m/s²
- V1a: Trần a_y của path HWA = aysmax + 0,1 m/s²
- V0: Trần a_y của path HWA = aysmax (bản hiện tại)

- tuning V0: S1c_F08a [profile=VP-5]:PP-SWR-051, S1c_F08a:PP-SWR-051
- test V0: S1c_F06e [profile=VP-5]:PP-SWR-051, S1c_F08b [profile=VP-5]:PP-SWR-051, S1c_F08b:PP-SWR-051, S1c_F17b [profile=VP-5]:PP-SWR-051, S1c_F17b:PP-SWR-051
- test V1a: S1c_F08b [profile=VP-5]:PP-SWR-051, S1c_F08b:PP-SWR-051, S1c_F17b [profile=VP-5]:PP-SWR-051, S1c_F17b:PP-SWR-051
- test V1b: S1bb [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1, S1c_F17b [profile=VP-5]:PP-SWR-051, S1c_F17b:PP-SWR-051
- test V1c: S1bb [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1, S1c_F17b [profile=VP-5]:PP-SWR-051, S1c_F17b:PP-SWR-051

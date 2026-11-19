# Study PP-TS-020

Plan: `research/studies/PP-TS-020-path-ay-ceiling/plan.yaml`, locked 2026-11-16; suite PP-TS-020.

Coi như ngang nhau khi chênh nhỏ hơn: PP-SWR-050 0.005, PP-SWR-051 0.01

## tuning

| Bộ | Trượt | PP-SWR-050 | PP-SWR-125 | PP-SWR-002 | PP-SWR-053 | PP-SWR-003 |
|---|---|---|---|---|---|---|
| V1a | 0 | 0.1191 | — | 0.3347 | 0.833 | 0.9661 |
| V1c | 2 | 0.1208 | — | 0.3347 | 0.833 | 0.9661 |
| V1b | 2 | 0.1217 | — | 0.3347 | 0.833 | 0.9661 |
| V0 | 4 | 0.3713 | — | 0.3347 | 0.833 | 0.9661 |
| V2 | 4 | 0.3713 | — | 0.3347 | 0.833 | 0.9661 |

- V1a: Trần a_y của path HWA = aysmax + 0,1 m/s²
- V1c: Trần a_y của path HWA = aysmax + 0,3 m/s²
- V1b: Trần a_y của path HWA = aysmax + 0,2 m/s²
- V0: Trần a_y của path HWA = aysmax (bản hiện tại)
- V2: Trần aysmax + 0,2 m/s² khi cờ giới hạn tắt; aysmax khi cờ bật

## test

| Bộ | Trượt | PP-SWR-050 | PP-SWR-125 | PP-SWR-002 | PP-SWR-053 | PP-SWR-003 |
|---|---|---|---|---|---|---|
| V1c | 4 | 0.3767 | 0.05299 | 0.09404 | 1.981 | 1.581 |
| V1b | 4 | 0.3767 | 0.05342 | 0.09404 | 1.981 | 1.581 |
| V1a | 5 | 0.3767 | 0.05389 | 0.09404 | 1.981 | 1.581 |
| V2 | 8 | 0.3767 | 0.05342 | 0.09404 | 1.981 | 1.581 |
| V0 | 8 | 0.3767 | 0.05442 | 0.09404 | 1.981 | 1.581 |

- V1c: Trần a_y của path HWA = aysmax + 0,3 m/s²
- V1b: Trần a_y của path HWA = aysmax + 0,2 m/s²
- V1a: Trần a_y của path HWA = aysmax + 0,1 m/s²
- V2: Trần aysmax + 0,2 m/s² khi cờ giới hạn tắt; aysmax khi cờ bật
- V0: Trần a_y của path HWA = aysmax (bản hiện tại)

- tuning V0: S1c_F08a [profile=VP-5]:PP-SWR-051, S1c_F08a:PP-SWR-051
- test V0: S1bb [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1, S1c_F06e [profile=VP-5]:PP-SWR-051, S1c_F08b [profile=VP-5]:PP-SWR-051, S1c_F08b:PP-SWR-051
- test V1a: S1bb [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1, S1c_F08b [profile=VP-5]:PP-SWR-051, S1c_F08b:PP-SWR-051
- tuning V1b: S1ba [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1
- test V1b: S1bb [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1, S1bc [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1
- tuning V1c: S1ba [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1
- test V1c: S1bb [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1, S1bc [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1
- tuning V2: S1c_F08a [profile=VP-5]:PP-SWR-051, S1c_F08a:PP-SWR-051
- test V2: S1bb [acc=ignore_limits]:PP-TS-020/R79-5.6.2.1.1, S1c_F06e [profile=VP-5]:PP-SWR-051, S1c_F08b [profile=VP-5]:PP-SWR-051, S1c_F08b:PP-SWR-051

# Study PP-TS-026

Plan: `research/studies/PP-TS-026-intervention-return/plan.yaml`, locked 2026-11-18; suite PP-TS-026.

Coi như ngang nhau khi chênh nhỏ hơn: PP-SWR-081 0.25, PP-SWR-082 0.25, PP-SWR-087 0.02

## tuning

| Bộ | Trượt | PP-SWR-050 | PP-SWR-125 | PP-SWR-002 | PP-SWR-053 | PP-SWR-003 |
|---|---|---|---|---|---|---|
| V3 | 4 | — | — | — | — | 0 |
| V4 | 4 | — | — | — | — | 0 |
| V2 | 5 | — | — | — | — | 0 |
| V1 | 14 | — | — | — | — | 0 |
| V0 | 18 | — | — | — | — | 0 |

- V3: Hai pha, chặn đà 1,5 s (LKA), 1,0 s (ELK), về tâm 4 s
- V4: Hai pha, chặn đà 1,25 s (LKA), 0,75 s (ELK), về tâm 4 s
- V2: Hai pha, chặn đà 1,5 s (LKA), 1,0 s (ELK), về tâm 3 s
- V1: Một quintic dài hơn, T_lka 4 s, T_elk 3 s
- V0: Một quintic về tâm, T_lka 3 s, T_elk 2 s (bản hiện tại)

## test

| Bộ | Trượt | PP-SWR-050 | PP-SWR-125 | PP-SWR-002 | PP-SWR-053 | PP-SWR-003 |
|---|---|---|---|---|---|---|
| V3 | 6 | — | — | — | — | 0 |
| V4 | 6 | — | — | — | — | 0 |
| V2 | 10 | — | — | — | — | 0 |
| V1 | 32 | — | — | — | — | 0 |
| V0 | 34 | — | — | — | — | 0 |

- V3: Hai pha, chặn đà 1,5 s (LKA), 1,0 s (ELK), về tâm 4 s
- V4: Hai pha, chặn đà 1,25 s (LKA), 0,75 s (ELK), về tâm 4 s
- V2: Hai pha, chặn đà 1,5 s (LKA), 1,0 s (ELK), về tâm 3 s
- V1: Một quintic dài hơn, T_lka 4 s, T_elk 3 s
- V0: Một quintic về tâm, T_lka 3 s, T_elk 2 s (bản hiện tại)

- tuning V0: S13a-elk:PP-SWR-094, S20a:PP-SWR-094, S20b:PP-SWR-090, S20b:PP-SWR-094, S4c:PP-SWR-094, S5c [profile=VP-4]:PP-SWR-094, S5c:PP-SWR-094, S6a:PP-SWR-094, S6b:PP-SWR-094
- test V0: S13a:PP-SWR-094, S13b-elk:PP-SWR-094, S13b:PP-SWR-094, S13c-elk:PP-SWR-094, S13c:PP-SWR-094, S20a [profile=VP-2]:PP-SWR-094, S20c:PP-SWR-094, S20d:PP-SWR-094, S20e:PP-SWR-090, S20e:PP-SWR-094, S5b:PP-SWR-094, S5d:PP-SWR-094, S5f:PP-SWR-094, S6b [profile=VP-4]:PP-SWR-094, S6c:PP-SWR-032, S6c:PP-SWR-094, S6d:PP-SWR-094, S6e:PP-SWR-094
- tuning V1: S13a-elk:PP-SWR-094, S20a:PP-SWR-094, S20b:PP-SWR-090, S20b:PP-SWR-094, S4c:PP-SWR-094, S5c:PP-SWR-094, S6b:PP-SWR-094
- test V1: S13a:PP-SWR-094, S13b-elk:PP-SWR-094, S13b:PP-SWR-094, S13c-elk:PP-SWR-094, S13c:PP-SWR-094, S20a [profile=VP-2]:PP-SWR-094, S20c:PP-SWR-094, S20d:PP-SWR-094, S20e:PP-SWR-094, S5b:PP-SWR-094, S5d:PP-SWR-094, S5f:PP-SWR-094, S6b [profile=VP-4]:PP-SWR-094, S6c:PP-SWR-094, S6d:PP-SWR-094, S6e:PP-SWR-094
- tuning V2: S20a:PP-SWR-090, S20b:PP-SWR-090, S20b:PP-SWR-094
- test V2: S13c-elk:PP-SWR-094, S13c:PP-SWR-094, S20c:PP-SWR-094, S20d:PP-SWR-090, S20e:PP-SWR-094
- tuning V3: S20a:PP-SWR-090, S20b:PP-SWR-090
- test V3: S20a [profile=VP-2]:PP-SWR-090, S20d:PP-SWR-090, S20e:PP-SWR-090
- tuning V4: S20a:PP-SWR-090, S20b:PP-SWR-032, S20b:PP-SWR-090
- test V4: S20a [profile=VP-2]:PP-SWR-090, S20d:PP-SWR-090, S20e:PP-SWR-090

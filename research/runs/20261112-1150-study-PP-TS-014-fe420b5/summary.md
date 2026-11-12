# Study PP-TS-014

Plan: `research/studies/PP-TS-014-continuity-beyond-view/plan.yaml`, locked 2026-11-12; suite PP-TS-014.

Coi như ngang nhau khi chênh nhỏ hơn: PP-SWR-050 0.005, PP-SWR-051 0.01

## tuning

| Bộ | Trượt | PP-SWR-050 | PP-SWR-125 | PP-SWR-002 | PP-SWR-053 | PP-SWR-003 |
|---|---|---|---|---|---|---|
| V0-m9 | 2 | 2.145 | — | — | — | 1.053 |
| V0-m8 | 4 | 2.882 | — | — | — | 1.069 |
| V0-m7 | 5 | 4.039 | — | — | — | 1.045 |
| V1-m9 | 9 | 0.4085 | — | — | — | 2.756 |
| V1-m8 | 9 | 0.4085 | — | — | — | 2.899 |
| V1-m7 | 14 | 2.078 | — | — | — | 2.97 |

- V0-m9: Bản hiện tại, cont_margin 0,9
- V0-m8: Bản hiện tại, cont_margin 0,8
- V0-m7: Bản hiện tại, cont_margin 0,7
- V1-m9: T4 một λ cho từng điểm, cont_margin 0,9
- V1-m8: T4 một λ cho từng điểm, cont_margin 0,8
- V1-m7: T4 một λ cho từng điểm, cont_margin 0,7

## test

| Bộ | Trượt | PP-SWR-050 | PP-SWR-125 | PP-SWR-002 | PP-SWR-053 | PP-SWR-003 |
|---|---|---|---|---|---|---|
| V0-m7 | 14 | 2.719 | 0.8131 | 0.1881 | 3.261 | 2.59 |
| V0-m8 | 18 | 1.879 | 0.8247 | 0.1881 | 3.261 | 2.598 |
| V0-m9 | 21 | 1.362 | 0.8789 | 0.1881 | 3.281 | 2.603 |
| V1-m7 | 31 | 0.4007 | 0.9463 | 0.1881 | 3.261 | 3.892 |
| V1-m9 | 34 | 0.4007 | 0.9463 | 0.1881 | 3.281 | 3.713 |
| V1-m8 | 34 | 0.4007 | 0.9463 | 0.1881 | 3.281 | 3.8 |

- V0-m7: Bản hiện tại, cont_margin 0,7
- V0-m8: Bản hiện tại, cont_margin 0,8
- V0-m9: Bản hiện tại, cont_margin 0,9
- V1-m7: T4 một λ cho từng điểm, cont_margin 0,7
- V1-m9: T4 một λ cho từng điểm, cont_margin 0,9
- V1-m8: T4 một λ cho từng điểm, cont_margin 0,8

- tuning V0-m7: S1c [camera_view_m=30]:PP-SWR-051, S1f [camera_view_m=30]:PP-SWR-051, S1f [camera_view_m=40]:PP-SWR-051
- test V0-m7: S14e [acc=ignore_limits]:PP-SWR-051, S14e [acc=on]:PP-SWR-051, S14e [camera_view_m=126, acc=ignore_limits]:PP-SWR-051, S1c_F06b:PP-SWR-100, S1c_F06e:PP-SWR-100, S1f [camera_view_m=35]:PP-SWR-051, S1f [camera_view_m=60]:PP-SWR-100
- tuning V0-m8: S1f [camera_view_m=30]:PP-SWR-051, S1f [camera_view_m=40]:PP-SWR-051
- test V0-m8: S14e [acc=ignore_limits]:PP-SWR-051, S14e [acc=ignore_limits]:PP-SWR-100, S14e [acc=on]:PP-SWR-051, S14e [camera_view_m=126, acc=ignore_limits]:PP-SWR-051, S14e [camera_view_m=126, acc=ignore_limits]:PP-SWR-100, S1c_F06b:PP-SWR-100, S1c_F06e:PP-SWR-100, S1f [camera_view_m=35]:PP-SWR-051, S1f [camera_view_m=60]:PP-SWR-100
- tuning V0-m9: S1f [camera_view_m=30]:PP-SWR-051
- test V0-m9: S14e [acc=ignore_limits]:PP-SWR-051, S14e [acc=ignore_limits]:PP-SWR-100, S14e [acc=on]:PP-SWR-051, S14e [acc=on]:PP-SWR-100, S14e [camera_view_m=126, acc=ignore_limits]:PP-SWR-051, S14e [camera_view_m=126, acc=ignore_limits]:PP-SWR-100, S1c_F06b:PP-SWR-100, S1c_F06b:PP-SWR-101, S1c_F06e:PP-SWR-100, S1f [camera_view_m=35]:PP-SWR-051, S1f [camera_view_m=60]:PP-SWR-100
- tuning V1-m7: S1c [camera_view_m=30]:PP-SWR-100, S1c [camera_view_m=30]:PP-SWR-101, S1c_F22c:PP-SWR-100, S1c_F22c:PP-SWR-101, S1f [camera_view_m=30]:PP-SWR-051, S1f [camera_view_m=30]:PP-SWR-100, S1f [camera_view_m=40]:PP-SWR-100
- test V1-m7: S14a [acc=ignore_limits]:PP-SWR-100, S14e [acc=ignore_limits]:PP-SWR-100, S14e [acc=ignore_limits]:PP-SWR-101, S14e [acc=on]:PP-SWR-051, S14e [acc=on]:PP-SWR-100, S14e [camera_view_m=126, acc=ignore_limits]:PP-SWR-051, S14e [camera_view_m=126, acc=ignore_limits]:PP-SWR-100, S1bd:PP-SWR-100, S1c_F06b:PP-SWR-100, S1c_F06b:PP-SWR-101, S1c_F06e:PP-SWR-100, S1c_F06e:PP-SWR-101, S1c_F22f:PP-SWR-100, S1c_F22f:PP-SWR-101, S1f [camera_view_m=35]:PP-SWR-100, S1f [camera_view_m=60]:PP-SWR-100
- tuning V1-m8: S1c [camera_view_m=30]:PP-SWR-100, S1c_F22c:PP-SWR-100, S1c_F22c:PP-SWR-101, S1f [camera_view_m=30]:PP-SWR-100, S1f [camera_view_m=40]:PP-SWR-100
- test V1-m8: S14a [acc=ignore_limits]:PP-SWR-100, S14e [acc=ignore_limits]:PP-SWR-100, S14e [acc=ignore_limits]:PP-SWR-101, S14e [acc=on]:PP-SWR-051, S14e [acc=on]:PP-SWR-100, S14e [acc=on]:PP-SWR-101, S14e [acc=on]:PP-SWR-102, S14e [camera_view_m=126, acc=ignore_limits]:PP-SWR-051, S14e [camera_view_m=126, acc=ignore_limits]:PP-SWR-100, S1bd:PP-SWR-100, S1c_F06b:PP-SWR-100, S1c_F06b:PP-SWR-101, S1c_F06e:PP-SWR-100, S1c_F06e:PP-SWR-101, S1c_F22f:PP-SWR-100, S1c_F22f:PP-SWR-101, S1f [camera_view_m=35]:PP-SWR-100, S1f [camera_view_m=60]:PP-SWR-100
- tuning V1-m9: S1c [camera_view_m=30]:PP-SWR-100, S1c_F22c:PP-SWR-100, S1c_F22c:PP-SWR-101, S1f [camera_view_m=30]:PP-SWR-100, S1f [camera_view_m=40]:PP-SWR-100
- test V1-m9: S14a [acc=ignore_limits]:PP-SWR-100, S14e [acc=ignore_limits]:PP-SWR-100, S14e [acc=ignore_limits]:PP-SWR-101, S14e [acc=on]:PP-SWR-051, S14e [acc=on]:PP-SWR-100, S14e [acc=on]:PP-SWR-101, S14e [acc=on]:PP-SWR-102, S14e [camera_view_m=126, acc=ignore_limits]:PP-SWR-051, S14e [camera_view_m=126, acc=ignore_limits]:PP-SWR-100, S14e [camera_view_m=126, acc=on]:PP-SWR-100, S1bd:PP-SWR-100, S1c_F06b:PP-SWR-100, S1c_F06b:PP-SWR-101, S1c_F06e:PP-SWR-100, S1c_F06e:PP-SWR-101, S1c_F22f:PP-SWR-100, S1f [camera_view_m=35]:PP-SWR-100, S1f [camera_view_m=60]:PP-SWR-100

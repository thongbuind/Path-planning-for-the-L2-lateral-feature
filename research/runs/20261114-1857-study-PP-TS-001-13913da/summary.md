# Study PP-TS-001

Plan: `research/studies/PP-TS-001-lane-jumps/plan.yaml`, locked 2026-11-14; suite PP-TS-001.

Coi như ngang nhau khi chênh nhỏ hơn: PP-SWR-050 0.005, PP-SWR-051 0.01

## tuning

| Bộ | Trượt | PP-SWR-050 | PP-SWR-125 | PP-SWR-002 | PP-SWR-053 | PP-SWR-003 |
|---|---|---|---|---|---|---|
| J0-shape | 8 | 1.873 | 0.02808 | — | — | 1.377 |
| J0 | 12 | 1.873 | 1.008 | — | — | 1.377 |

- J0-shape: Thêm kiểm tại 50% và 75% đoạn quan sát chung sau bù ego-motion
- J0: Kiểm độ lệch c0 giữa hai frame

## test

| Bộ | Trượt | PP-SWR-050 | PP-SWR-125 | PP-SWR-002 | PP-SWR-053 | PP-SWR-003 |
|---|---|---|---|---|---|---|
| J0-shape | 14 | 1.874 | 1.032 | — | — | 1.58 |
| J0 | 23 | 1.874 | 1.099 | — | — | 1.58 |

- J0-shape: Thêm kiểm tại 50% và 75% đoạn quan sát chung sau bù ego-motion
- J0: Kiểm độ lệch c0 giữa hai frame

- tuning J0: S1c_F01c:PP-SWR-100, S1c_F03c:PP-SWR-051, S1c_F03c:PP-SWR-100, S1c_F06a:PP-SWR-051, S1c_F06e:PP-SWR-051, S1c_F06e:PP-SWR-100
- test J0: S1a_F06a:PP-SWR-051, S1a_F06d:PP-SWR-051, S1c_F01b:PP-SWR-100, S1c_F03c:PP-SWR-051, S1c_F03c:PP-SWR-100, S1c_F06b:PP-SWR-051, S1c_F06b:PP-SWR-100, S1c_F06b:PP-SWR-101, S1c_F06d:PP-SWR-051, S1c_F06d:PP-SWR-100, S1c_F06e:PP-SWR-051, S1c_F06e:PP-SWR-100
- tuning J0-shape: S1c_F01c:PP-SWR-100, S1c_F03c:PP-SWR-051, S1c_F03c:PP-SWR-100, S1c_F06e:PP-SWR-100
- test J0-shape: S1a_F06d:PP-SWR-051, S1c_F01b:PP-SWR-100, S1c_F03c:PP-SWR-051, S1c_F03c:PP-SWR-100, S1c_F06d:PP-SWR-051, S1c_F06d:PP-SWR-100, S1c_F06e:PP-SWR-100

# Q1: PP-SWR-050 so với camera_latency_ms = 0

| Chạy | camera_latency_ms | PP-SWR-050 | Ở mức gốc | Tăng thêm |
|---|---|---|---|---|
| S1a [camera_jitter_ms=20, camera_latency_ms=0] | 0 | 0.015 | 0.015 | +0.000 |
| S1a [camera_jitter_ms=20, camera_latency_ms=50] | 50 | 0.015 | 0.015 | +0.000 |
| S1a [camera_jitter_ms=20] | 100 | 0.015 | 0.015 | +0.000 |
| S1a [camera_jitter_ms=20, camera_latency_ms=150] | 150 | 0.015 | 0.015 | +0.000 |
| S1a [camera_jitter_ms=20, camera_latency_ms=200] | 200 | 0.015 | 0.015 | +0.000 |
| S1a [camera_jitter_ms=20, camera_latency_ms=300] | 300 | 0.000 | 0.015 | -0.015 |
| S1c [camera_jitter_ms=20, camera_latency_ms=0] | 0 | 0.351 | 0.351 | +0.000 |
| S1c [camera_jitter_ms=20, camera_latency_ms=50] | 50 | 0.368 | 0.351 | +0.017 |
| S1c [camera_jitter_ms=20] | 100 | 0.381 | 0.351 | +0.030 |
| S1c [camera_jitter_ms=20, camera_latency_ms=150] | 150 | 0.393 | 0.351 | +0.042 |
| S1c [camera_jitter_ms=20, camera_latency_ms=200] | 200 | 0.402 | 0.351 | +0.051 |
| S1c [camera_jitter_ms=20, camera_latency_ms=300] | 300 | 0.000 | 0.351 | -0.351 |
| S1f [camera_jitter_ms=20, camera_latency_ms=0] | 0 | 0.266 | 0.266 | +0.000 |
| S1f [camera_jitter_ms=20, camera_latency_ms=50] | 50 | 0.274 | 0.266 | +0.008 |
| S1f [camera_jitter_ms=20] | 100 | 0.267 | 0.266 | +0.001 |
| S1f [camera_jitter_ms=20, camera_latency_ms=150] | 150 | 0.288 | 0.266 | +0.022 |
| S1f [camera_jitter_ms=20, camera_latency_ms=200] | 200 | 0.265 | 0.266 | -0.001 |
| S1f [camera_jitter_ms=20, camera_latency_ms=300] | 300 | 0.000 | 0.266 | -0.266 |
| S2b [camera_jitter_ms=20, camera_latency_ms=0] | 0 | 0.400 | 0.400 | +0.000 |
| S2b [camera_jitter_ms=20, camera_latency_ms=50] | 50 | 0.400 | 0.400 | +0.000 |
| S2b [camera_jitter_ms=20] | 100 | 0.400 | 0.400 | +0.000 |
| S2b [camera_jitter_ms=20, camera_latency_ms=150] | 150 | 0.400 | 0.400 | +0.000 |
| S2b [camera_jitter_ms=20, camera_latency_ms=200] | 200 | 0.400 | 0.400 | +0.000 |
| S2b [camera_jitter_ms=20, camera_latency_ms=300] | 300 | 0.000 | 0.400 | -0.400 |

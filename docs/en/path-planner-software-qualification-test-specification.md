# Software Qualification Test Specification

| Field | Value |
|---|---|
| Document ID | `PP-SQTS` |
| Version | 1.1 |
| Status | BL1 |
| Author | thongbui |
| Reviewer | thongbui |
| Last updated | 2026-11-10 |

## 1. Purpose and scope {#test-scope}

- **Purpose.** Specify how to verify the path planner: simulation environment, test cases, fault injection, pass criteria, metrics, calibration selection, and technique comparison.
- **Scope.** Black-box testing against the Software Requirements Specification: pass or fail for requirements, measurement and ranking for performance targets, and flexibility across vehicles.
- **Out of scope.** Planner unit tests and real-vehicle testing. There are no logs from real vehicles; all tests run in the simulator.

## 2. References {#test-references}

| Document | Use |
|---|---|
| [Software Requirements Specification](report.html?doc=path-planner-software-requirements-specification&lang=en) | Requirements, performance targets, and ODD; the Verification column is the source of traceability |
| [Interface Control Document](report.html?doc=path-planner-interface-control-document&lang=en) | The only interfaces the test system may observe |
| [ADAS Function Specification](report.html?doc=adas-function-specification&lang=en) | Thresholds for the ADAS Functions stub |
| G1 assignment | Minimum set of 3 scenarios × 5 fault states; metrics for comparing techniques |
| Euro NCAP LSS Test Protocol v4.3 | Test speed of 72 km/h, drift along an arc of R = 1200 m, v_lat of 0.2–0.6 m/s |
| Bosch SMI230 (2018 product brief) | IMU noise and bias levels |
| ISO 15622:2018 | ACC stub |

## 3. Test principles {#test-principles}

- **Independence.** The test system observes the planner only through the interfaces in the Interface Control Document (inputs, outputs, and computation time). It does not read internal variables or rely on internal mechanisms or thresholds. The planner does not read scenario names, ground truth, seeds, or test configuration.
- **Predefinition.** Fix scenarios, seeds, criteria, and ranking order before running the tests. If anything changes, record why and rerun all techniques.
- **Separate tuning and scoring.** Select calibration on the tuning set; take official scores from the test set (different seeds and some scenarios not used during tuning). Give each technique the same tuning effort budget.
- **No test-specific behavior.** Add new cases only on the test side. If a case fails, fix the planner's general mechanism and rerun the entire suite.
- **Complete, reproducible reporting.** Report all scenarios and seeds, including the worst case. Include the code version, scenario file, and seed with each result.
- **Priorities.** Safety first, then regulatory compliance, driver experience, and computation time. Measure actual vehicle motion relative to the actual lane.

## 4. Test environment {#simulation-design}

### 4.1 Execution modes {#benchmark-run}

| Item | Specification |
|---|---|
| Scoring mode | Deterministic, single process, 1 ms step. The same seed gives the same result. Official metrics come from this mode |
| Real-time mode | One process per ECU, real sockets, and the `python-can` `udp_multicast` virtual CAN bus. For integration checks only |
| Open loop | The vehicle follows a predefined trajectory independently of the path; measure path quality |
| Closed loop | The path goes through the Lateral Controller and EPS stubs into the vehicle model. The stubs are fixed across all techniques |
| Smoothness | Always measured on planner output, including in closed loop |
| ADAS Functions stub | Mode B (reads ground truth) for scoring the planner; mode A (reads noisy messages) for reporting the full chain. Log both measured and ground-truth TLC |
| Noise-free baseline | Each scenario has a noise-free run to separate algorithm errors from noise effects |
| IMU | Main scenarios use clean IMU signals (mentor). IMU noise and bias are introduced through fault injection |
| Rate | Planner and ADAS Functions: 40 Hz. Vehicle signals follow the signal list (mentor) |
| Seed | One main seed per run, with separate streams for each channel; 10 seeds per cell with noise |
| Log | One MCAP file per run, sufficient for replay; view in Foxglove |
| 8 GB RAM machine | Run in small batches |

### 4.2 Scheduler and clocks {#sim-scheduler}

| Item | Specification |
|---|---|
| Architecture | Components communicate only through interfaces. The two modes share code and differ only in transport and scheduling layers. Pure Python plus numpy |
| Step | 1 ms. Order within each step: integrate the vehicle model, sample sensors, deliver due messages, then run scheduled modules in fixed priority order |
| Phase offset | Each module starts at a random phase determined by the seed |
| Transport channel | Latency = nominal latency + uniform jitter. Messages can be lost with a specified probability. The receiver retains the latest message and checks counter, CRC, and qualifier on receipt |
| Channel fault injection | Burst loss, added latency, duplication, reordering, transmission stoppage, invalid CRC, and stuck counter |
| Planner computation time | Simulated as 5 ms; measure actual time separately |
| Seed | `numpy.random.SeedSequence.spawn` |
| ECU clocks | Each ECU drifts by up to ±100 ppm, with initial offset up to ±10 ms. gPTP-like synchronization every 125 ms; error after synchronization up to ±50 µs |

### 4.3 Virtual CAN bus {#sim-can}

Chassis signals pass through a virtual CAN bus using the DBC in the Interface Control Document: quantization using the scaling factor, fixed period, counter, CRC, and timeout. Use `cantools` and the `python-can` virtual bus. Fault injection: dropped frames, invalid CRC, repeated or skipped counters, and transmission stoppage.

### 4.4 Vehicle model and vehicle profiles {#sim-vehicle}

| Item | Specification |
|---|---|
| Model | Dynamic bicycle model with linear tires F = C·α; states x, y, ψ, v_y, r; RK4 with a 1 ms step |
| Grip limit | Lateral force per axle ≤ μ·F_z; μ = 1.0 dry, 0.5 wet |
| Low speed | Gradually blend into the kinematic model over 3–5 m/s |
| Longitudinal speed | From the ACC stub (Section 4.7). Scenarios with HWA run with ACC enabled; scenarios with only LKA or ELK and scenario S11 maintain the scenario-defined speed |
| Lane drift sources | Simulated driver adds a small steering angle offset, or a constant lateral force from road cross slope or crosswind |

**Vehicle profiles.** The planner receives the profile through VehicleConfig. VP-0 is the default for all scenarios; VP-1 through VP-5 are used for S19 and the flexibility suite (Section 8.3).

| Profile | Vehicle | Wheelbase (m) | Body width / width including mirrors (m) | Mass (kg) | Turning radius (m) | Maximum wheel angle (rad) |
|---|---|---|---|---|---|---|
| VP-0 | Midsize electric vehicle, typical values | 2.90 | — / 1.90 | 2000 | — | 0.61 |
| VP-1 | 3,190 × 1,679 mm | 2.075 | 1.679 / 1.96 | 857 | 4.05 | 0.54 |
| VP-2 | 4,241 × 1,834 mm | 2.730 | 1.834 / 2.11 | 1600 | 5.5 | 0.52 |
| VP-3 | 4,750 × 1,934 mm | 2.950 | 1.934 / 2.21 | 2540 | 6.2 | 0.50 |
| VP-4 | 5,119 × 2,004 mm | 3.150 | 2.004 / 2.254 | 2932 | 7.33 | 0.44 |
| VP-5 | Synthetic: as VP-4, with maximum width | 3.150 | — / 2.50 | 2932 | 7.33 | 0.44 |

| Parameter | Derivation | Source |
|---|---|---|
| Wheelbase, body width, mass, turning radius | Reference values for VP-1 through VP-4 | Published vehicle specifications |
| Width including mirrors | VP-1 through VP-3 add 0.28 m to body width. VP-4 uses 2.254 m with mirrors and 2.004 m without mirrors. | Team simulation assumption |
| Maximum wheel angle | asin(wheelbase / turning radius) | team agreement |
| Mass distribution | l_f = l_r = wheelbase / 2 | team agreement |
| Tire cornering stiffness | C_f = 100 000·m/2000, C_r = 140 000·m/2000 N/rad; maintains understeer coefficient K ≈ 0.0029 rad/(m/s²) for every profile | team agreement |
| Moment of inertia | I_z = 0.83·m·l_f·l_r (typically 0.8–1.1 for passenger cars) | team agreement |
| Steering ratio, maximum steering wheel rate, actuation delay | 15; 6 rad/s; 50 ms for all profiles | team agreement |

Ignore load transfer in cornering, suspension, and road roughness: their effects are small at HWA and LKA a_y levels.

### 4.5 Sensor models {#sim-sensors}

The test system sets fault levels using datasheets or other documentation, independently of planner assumptions. Sweep multiple levels when no source is available.

| Channel | Generation | Level |
|---|---|---|
| Lane model | Transform visible lane geometry into `base_link` and fit a cubic polynomial to each marking across the three lanes and to each road edge; inject faults per Section 6 | Section 6 |
| ObjectList | Transform scenario objects into `base_link` | x: σ = 0.2 m + 1 % of distance; y: σ = 0.1 m + 0.5 %; vx, vy: σ = 0.3 and 0.2 m/s; size σ = 0.1 m; missed detections in 2 % of frames; ghost objects at 0.05 per second, lasting 0.2 s; rain: σ × 1.5 |
| Yaw rate | Clean in the main scenarios | Fault injection: σ = 0.07 or 0.14 °/s (0.02 °/s/√Hz × √12 or √50 Hz); bias 0.1 / 0.3 / 1 °/s |
| a_x, a_y | Clean in the main scenarios; on a cross slope, still includes g·sin(slope angle) | Fault injection: σ = 0.004 or 0.008 m/s²; bias up to 0.2 m/s² |
| Speed | From the vehicle model before CAN encoding | σ = 0.02 m/s; scale error ±0.5 % |
| Steering wheel angle | Same as above | σ = 0.001 rad; zero offset ±0.01 rad |
| VehicleStateEstimate | Ground-truth v_y plus noise | σ = 0.05 m/s |
| Ego-motion | Integrate the CAN signals themselves, so errors arise naturally when IMU faults are injected | — |

Basis: IMU noise and bias follow the Bosch SMI230 (raw sensor, so these are upper bounds for filtered signals). The team agreed on the noise levels for speed, steering angle, perception, and v_y.

### 4.6 Lateral Controller and EPS stubs {#sim-controller}

Closed-loop test equipment, fixed across all planner versions.

| Part | Specification |
|---|---|
| Controller | 100 Hz. Read a path point by `stamp_us + time_from_start` and transform it into current `base_link`. δ = L·κ + K·v²·κ + k_y·e_y + k_ψ·e_ψ; tune k_y and k_ψ once and keep them fixed |
| Path sampling time | κ at current time plus `actuator_delay` (PP-ADR-010); e_y and e_ψ at a 0.5 s lookahead point |
| Understeer coefficient K | From the simulator's vehicle model (Section 4.4), without using VehicleConfig |
| Invalid path or 75 ms timeout | Hold the last command and signal that control has stopped; EPS hands steering back to the driver over 1 s |
| EPS | Track the requested steering wheel angle: pure delay per `actuator_delay`, first-order response with τ = 0.1 s, rate and angle limits per VehicleConfig. When not controlling, blend to the simulated driver's angle over 1 s |

The simulated EPS takes an angle for simplicity. EPS in a real L2 vehicle typically takes torque. The values are typical and do not come from measurements of a specific EPS.

### 4.7 ACC stub {#sim-acc}

The simulator's longitudinal module belongs to the test system and is fixed across all planner versions (PP-ADR-001). Its interface with the planner is in the [Interface Control Document](report.html?doc=path-planner-interface-control-document&lang=en#longitudinal-plan).

| Part | Design | Source |
|---|---|---|
| Mode | OFF, CRUISE, FOLLOW, CURVE_LIMIT. Switch automatically according to the lowest command | ISO 15622:2018 6.1 |
| Acceleration command | Minimum of three commands: set speed, lead vehicle, and curve speed envelope. Then limit acceleration and jerk | ISO 15622:2018 6.1 |
| Target vehicle selection | Corridor width is vehicle width plus 0.2 m on each side. Follow Trajectory for 3 s, then continue along the lane model center. Select a vehicle whose body is in the corridor now or after 1 s; consider only same-direction objects that have previously traveled at least 1 m/s. Drop a selected vehicle once it has been outside the corridor widened by 0.3 m on each side for more than 1 s | team agreement |
| Stationary objects | Do not respond to objects that have never moved | ISO 15622:2018 6.2.2 |
| Lead vehicle following | c_des = 5 m + τ·v, τ = 1.8 s. a = 0.5·(c − c_des) + 1.0·(v_lead − v); limit the contribution from gap error to ±1.0 m/s² | τ: ISO 15622:2018 6.2.3.1 (1.5–2.2 s); remaining values: team agreement |
| Curve speed | v_t = v_max·√(1 − 0.3 / 2.5), reserving 0.3 m/s² of a_y for HWA to correct deviation. v_allowed = √(v_t² + 2·2.0·max(0, d − 0.5·v)), where d is the distance to the point of maximum curvature. If v_max changes by no more than 5 %, decrease d by the distance traveled | team agreement |
| `lateral_limit_reached` | Do not accelerate while the flag is set | team agreement |
| Limits | Acceleration −3.0 to +1.5 m/s²; jerk ≤ 2.5 m/s³; no AEB | team agreement |
| LongitudinalPlan | Propagate the above law for 3 s and sample v(t) and a(t) on a 0.1 s grid | team agreement |
| LateralLimits lost; ACC disabled | Do not accelerate. If ACC is disabled, send OFF, current speed, and zero acceleration | team agreement |
| Actuation | Pass the acceleration command through a 0.1 s delay and a first-order response with τ = 0.3 s | team agreement |

## 5. Test cases {#benchmark-scenarios}

**Minimum set required by the assignment.** HWA curve tracking (S1), LKA lane drift (S4), and ELK with an oncoming vehicle (S7), each under 5 conditions: no fault, noise (F01), c0 jump (F02), loss of one marking (F04), and incorrect c2 (F06).

- Euro NCAP LSS test speed: 72 km/h. Induce drift along an arc of R = 1200 m, then hold v_lat. Also test 90 km/h.
- Use 3–5 variants per scenario, from easy to difficult, with at least one at the requirement boundary. Run scenarios that apply to both sides on both sides.
- Defaults: 3.5 m lane, profile VP-0.
- The Requirement column is generated by `python3 tools/trace.py --write` from the Verification column of the Software Requirements Specification. Do not edit it by hand. IDs are fixed: do not renumber or reuse them.

| # | Scenario | Variants | Requirement |
|---|---|---|---|
| S1 | HWA tracks a curve | 90 km/h, clothoid curve entry. a) R = 1000 m (curve a_y 0.6 m/s²); b) R = 500 m (1.25); c) R = 250 m (2.5, reaches aysmax); d) S-curve, R = 500 m; e) 130 km/h, R = 1000 m (1.3) | PP-SWR-001, 003, 004, 008 (a, b, d, e), 050 (a, b, d, e), 051 (closed loop) |
| S1b | HWA on a curve requiring more than aysmax | a) 90 km/h, R = 200 m (3.1 m/s²); b) 90 km/h, R = 150 m (4.2); c) 110 km/h, R = 300 m (3.1); d) R = 200 m immediately after a crest, with 40 m of camera visibility | PP-SWR-001, 005, 006, 007 |
| S2 | HWA activates with the vehicle off center | a) 0.2 m offset, 0° heading error; b) 0.4 m, 1°; c) 0.5 m, 2° outward; d) 0.4 m on a curve with R = 500 m; e) 0.5 m at 130 km/h | PP-SWR-002, 052, 053 |
| S3 | HWA offsets the center when passing a truck in an adjacent lane | Truck width 2.5 m. a) 5 m/s slower; b) 2 m/s slower; c) 10 m/s slower; d) truck 0.1 m from the marking; e) truck encroaches 0.3 m beyond the marking | PP-SWR-002, 055, 058, 059 |
| S3b | A large vehicle overtakes from behind in a narrow lane | Truck is 5 m/s faster and detected only by corner radar before drawing alongside. a) opposite side empty, lane 3.5 m; b) passenger car on the opposite side; c) truck on the opposite side; d) as a, lane 3.0 m; e) as c, lane 2.75 m | PP-SWR-055, 056, 057 |
| S4 | LKA for lane drift on a straight road | a) 72 km/h, dashed marking, v_lat 0.2 m/s; b) 72 km/h, solid marking, 0.4; c) 90 km/h, 0.6; d) crosswind-induced drift; e) cross slope-induced drift | PP-SWR-032, 080, 081, 083, 084 (closed loop), 085 (closed loop), 086 (closed loop), 087 (closed loop), 090, 110, 112, 114 |
| S4b | LKA for lane drift in a curve | 90 km/h. a) R = 1000 m, outward drift at 0.3 m/s; b) R = 500 m, outward; c) R = 500 m, inward; d) R = 250 m, outward, with only 0.5 m/s² remaining within the LKA limit; e) outward drift in the clothoid | PP-SWR-083, 085 (closed loop), 110, 112, 114 |
| S5 | Solid-marking ELK with LKA disabled | a) 72 km/h, v_lat 0.2; b) 0.4; c) 0.6; d) 90 km/h, 0.4; e) double marking | PP-SWR-032, 080, 082, 083, 085 (closed loop), 086 (closed loop), 090, 111, 113, 115 |
| S6 | Road-edge ELK | Passenger side. a) road edge only, v_lat 0.2; b) road edge only, 0.6; c) dashed center marking with no marking by the edge; d) barrier as the road edge; e) 90 km/h, 0.4 | PP-SWR-080, 082, 083, 085 (closed loop), 086 (closed loop), 111, 113, 115 |
| S6b | Lane widening | HWA enabled. a) emergency lane widens by 1.5 m over 100 m on the right; b) exit branch; c) new lane on the left; d) widening on a curve with R = 500 m; e) widening while offsetting the center due to a truck on the other side | PP-SWR-050, 060 (closed loop) |
| S7 | ELK for an oncoming vehicle | Other vehicle 1.5 m from the inner edge of the center marking, with 10 % overlap without intervention. a) both at 72 km/h, v_lat 0.2; b) 0.4; c) 0.6; d) other vehicle at 90 km/h; e) on a curve with R = 500 m | PP-SWR-082, 083, 085 (closed loop), 088 (closed loop), 111, 113, 115 |
| S8 | ELK for an overtaking vehicle | a) other vehicle at 80 km/h, ego vehicle at 72 km/h, drift at 0.2 m/s; b) both at 72 km/h, drift at 0.4; c) turn indicator 1.0 ± 0.5 s before steering, 0.5 m/s; d) as c, 0.7 m/s; e) other vehicle at 100 km/h, drift at 0.4 | PP-SWR-082, 083, 085 (closed loop), 088 (closed loop), 089, 111, 113, 115 |
| S8b | Signaled lane change with a rear vehicle at different distances | a) 20 m away, 2.2 m/s faster; b) 10 m, 2.2 m/s; c) 20 m, 8 m/s; d) 12 m, 10 m/s (TTC 1.2 s); e) 30 m, 14 m/s (requires 3.3 m/s²). a–c: no intervention; d, e: intervene per ADAS Function Specification Section 6, step 5 | PP-SWR-082 (d, e), 083 (d, e), 085 (d, e, closed loop), 111 (d, e), 113 (d, e), 115 (d, e) |
| S8c | Sudden evasive steering with a vehicle in the adjacent lane | No turn indicator. a) v_lat 1.2 m/s; b) 1.5 m/s; c) steer and immediately steer back; d) steer during LKA intervention | PP-SWR-031 (d), 036 (d), 037 (d) |
| S9 | Function transitions | a) LKA to ELK; b) ELK finishes and returns to HWA; c) HWA overridden, then override released; d) request cancelled due to turn indicator; e) driver switches off HWA mid-curve at R = 500 m | PP-SWR-030 (a), 031, 033 (b), 036 (d), 037 (d), 038, 039 (c), 040 (c), 042 (e) |
| S10 | Travel close to a marking without drifting | a) DLC 0.2 m, v_lat near 0; b) DLC 0.4 m; c) cut a curve with R = 500 m; d) drive offset to one side when a truck is present; e) as a, at night, mode A |   |
| S11 | Motorway traffic congestion | HWA enabled. a) 0–30 km/h; b) 0–60 km/h; c) stop for 10 s, then resume; d) another vehicle cuts in at 20 km/h | PP-SWR-050, 054 |
| S12 | Rain | μ = 0.5, nighttime camera noise, perception noise × 1.5. a) S1c; b) S4c; c) S7c; d) S4b-d | PP-SWR-001 (a) |
| S13 | Slow EPS | S4c and S5c with EPS delay of a) 75 ms; b) 100 ms; c) 150 ms | PP-SWR-091 (a, b, closed loop) |
| S14 | Lateral and longitudinal modules exchange constraints | Run twice: ACC reads and ignores LateralLimits, respectively. a) S1b-a; b) another vehicle encroaches by 0.5 m; c) both; d) loss of LongitudinalPlan mid-curve | PP-SWR-009, 150, 151, 152, 153, 154 (d), 155 (d) |
| S15 | Center offset with objects on both sides | a) trucks on both sides; b) truck and barrier; c) truck and passenger car; d) trucks on both sides, lane 3.0 m; e) barriers on both sides | PP-SWR-055, 056, 057 |
| S16 | Repeated interventions | a) LKA COMPLETED, REQUEST holds for another 1 s; b) as a, REQUEST clears for 0.2 s, then returns; c) three drifts at 0.4 m/s, 2 s apart; d) as c, with solid-marking ELK; e) second intervention starts 0.2 s after COMPLETED | PP-SWR-034 (a, b), 035 (c, d, e), 041 (a, b) |
| S17 | Driver changes lanes with HWA enabled | The lane model switches lanes as the vehicle crosses the marking. a) straight road at 90 km/h, 4 s; b) 2.5 s; c) curve with R = 500 m; d) two consecutive lane changes; e) lane change flag delayed by one frame | PP-SWR-039, 040, 061 |
| S19 | Lane width and vehicle width | HWA at 90 km/h, straight road then curve with R = 500 m. a) lane 2.5 m, VP-1; b) lane 2.5 m, VP-5; c) lane 5.5 m, VP-2; d) lane 3.0 m, VP-4, 2.5 m-wide truck in an adjacent lane traveling 5 m/s slower; e) as d, with trucks on both sides | PP-SWR-050, 062, 063 (b) |

## 6. Fault injection {#benchmark-faults}

Inject each fault at three times: during steady HWA operation, at LKA or ELK activation, and during an intervention. The Requirement column is generated as in Section 5.

| ID | Group | Fault | Level or form | Requirement |
|---|---|---|---|---|
| F01 | Lane model | c0 and c1 noise | a) daytime σ_c0 = 0.03 m, σ_c1 = 0.002; b) × 1.5; c) night or rain × 2.5 | PP-SWR-120 |
| F02 | Lane model | c0 jump without a flag | a) 0.3 m; b) 0.6 m; c) 1.0 m within one frame; d) jump and return after one frame; e) jump and hold | PP-SWR-121 |
| F03 | Lane model | Misidentified adjacent-lane marking | a) left marking jumps to L2 in one frame; b) as a, lasting 0.5 s; c) both markings jump to the adjacent lane with no lane change flag; d) old marking or crack offset by 0.5 m, lasting 2 s; e) as a, during ELK | PP-SWR-050, 122 (closed loop) |
| F04 | Lane model | Loss of one marking | a) left; b) right; c) confidence drops to 0 over 2 s; d) immediate loss; e) loss while lane width changes | PP-SWR-050, 123 (a–d, closed loop) |
| F05 | Lane model | Loss of all boundaries: both ego-lane markings, adjacent-lane markings, and road edges | a) reconstruct for 0.5 s, then lose them; b) reconstruct for 1 s, then lose them; c) lose them for 0.5 s, then recover; d) loss mid-curve at R = 500 m | PP-SWR-043, 124 |
| F06 | Lane model | Incorrect curvature | a) c2 +0.0005 1/m on a straight road; b) −0.0005 1/m in a curve; c) incorrect c3; d) error lasts 2 s; e) error on curve entry | PP-SWR-125 |
| F07 | IMU | Noise | a) yaw-rate σ = 0.07 °/s, a_y σ = 0.004 m/s²; b) 0.14 °/s and 0.008 m/s² | PP-SWR-135 (a, b, closed loop) |
| F08 | IMU | Yaw-rate bias | a) 0.1 °/s; b) 0.3 °/s; c) 1 °/s (uncompensated raw sensor) | PP-SWR-136 (a, b, closed loop) |
| F09 | Timing | Latency | Sweeps in Section 6.1 |   |
| F10 | Timing | Jitter, message loss | a) single loss; b) burst of 2; c) burst of 5; d) jitter ±20 ms | PP-SWR-126 |
| F11 | Timing | Late or out of order | Message arrives after a newer message | PP-SWR-127 |
| F12 | Timing | Transmission stops | Stop each input for longer than its timeout, then resume transmission (recovery) | PP-SWR-043 (Lane Model), 044 (Lane Model, recovery), 045 (Lane Model, recovery), 046 (v_y, in S5), 124 (Lane Model), 140 (Perception, in S3), 141 (Perception, in S5), 142 (IMU, speed, steering angle), 144 (v_y), 145 (FunctionRequests) |
| F13 | Timing | Camera slower than planner | 20 Hz versus 40 Hz, always present | PP-SWR-128 |
| F14 | Timing | Loss of clock synchronization | a) drift ±20 ppm; b) ±100 ppm; c) loss of gPTP for 10 s | PP-SWR-137 (a, b, c, closed loop) |
| F15 | Integrity | Counter repeats, skips, or is stuck | On each channel | PP-SWR-129 (repeat), 130 (skip, stuck) |
| F16 | Integrity | Invalid flag | `valid = false`, qualifier FAULT | PP-SWR-130 |
| F17 | Integrity | Incorrect CRC | CAN frame | PP-SWR-130, 142 |
| F18 | Integrity | CAN quantization | Per DBC scaling factor, always present | PP-SWR-139 (closed loop) |
| F19 | Timing | Future timestamp | a) lane model +5 ms; b) +15 ms; c) +50 ms; d) one frame at +50 ms; e) ObjectList +15 ms | PP-SWR-132 |
| F20 | Ego-motion | Invalid result | a) once; b) continuously; c) every other cycle; d) as b, during LKA | PP-SWR-043, 143 |
| F21 | Lane model | Both ego-lane markings lost, other boundaries remain | a) L2 and R2 remain, confidence ≥ `conf_inferred`; b) only L2 remains; c) only the right road edge remains for 5 s; d) as a, on a curve with R = 500 m; e) as a, with confidence between `conf_ego` and `conf_inferred` | PP-SWR-047, 050, 124 (e), 147 (a–d), 148 (a–d, closed loop) |

### 6.1 Latency sweeps

Actual latency is unknown (mentor), so sweep multiple levels. Change latency only in the simulator; keep the planner configuration fixed.

| ID | Sweep | Levels | Requirement |
|---|---|---|---|
| Q1 | Camera latency (lane model, objects) | 0 / 50 / 100 / 150 / 200 / 300 ms, each with ±20 ms jitter | PP-SWR-012, 013, 131 (300 ms), 133 (200 ms) |
| Q2 | Filtered yaw-rate latency not reported to the planner | 0 / 25 / 50 / 100 ms | PP-SWR-138 (0–50 ms, closed loop) |
| Q3 | FunctionRequests latency | 20 / 40 / 60 ms | PP-SWR-038 |

### 6.2 Fault combinations

1. Run each scenario and variant with each fault individually, at all three times, in open and closed loop. For faults with multiple levels, run all levels on the hardest variant and the middle level on the remaining variants.
2. Combined "rainy night" case: noise × 2.5, μ = 0.5, loss of one marking, and camera latency of 150 ms.

### 6.3 IDs without traceability to planner requirements {#benchmark-trace-exempt}

| ID | Reason |
|---|---|
| S10 | Tests the ADAS Functions module: no unintended activation while the vehicle travels near the marking without drifting. Used to select `tlc_lka` (Section 7) |
| F09 | Groups the latency sweeps; traceability is in Q1, Q2, and Q3 |

## 7. Calibration sweeps {#test-calibration}

| ID | Parameter | Sweep method | Selection basis |
|---|---|---|---|
| P1 | Planner calibration parameters (Software Architectural Design Section 11) | Sweep each parameter over its range with the others at their initial values, then sweep combinations around the best set | Meet all requirements on all profiles, then use performance targets in the priority order in Section 9 |
| P2 | ADAS Functions module `tlc_lka` | 0.6 / 1.0 / 1.5 s on S4 through S8 and S10 | Compare minimum DTLE (S4–S8) with the number of unintended activations (S10, target 0) |
| P3 | Other ADAS Functions calibration parameters | Same as P1 | Same as P2 |

Select on the tuning set and score on the test set. Use one calibration set for all profiles.

## 8. Pass criteria and metrics {#test-criteria}

### 8.1 Requirements: pass or fail {#benchmark-pass-fail}

A requirement passes when it passes in every scenario, variant, seed, and profile specified in the Verification column of the Software Requirements Specification.

| Metric | Measurement | Threshold | Requirement |
|---|---|---|---|
| Minimum DTLE | Outer tire edge to inner marking edge, minimum over the intervention | ≥ −0.3 m (LKA, solid-marking ELK); ≥ −0.1 m (road-edge ELK) | PP-SWR-086, 091 |
| Clearance to adjacent-lane vehicle | Minimum lateral distance between the two vehicles | ≥ 0.3 m | PP-SWR-088 |
| DLC relative to actual lane | Minimum on each side | ≥ 0 | PP-SWR-051, 060, 084, 085, 122, 123, 148 |
| a_y, added a_y, jerk | On the path, according to the function in control; 0.5 s average jerk | Per PP-SWR-001, 003, 110 to 115 | PP-SWR-001, 003, 110 to 115 |
| Wheel angle and steering wheel rate | On the path | Per the profile's VehicleConfig | PP-SWR-116, 117 |
| Continuity | Differences in lateral position, heading, and curvature between consecutive paths, every cycle | ≤ 0.05 m; ≤ 0.005 rad; ≤ 0.0003 1/m | PP-SWR-100 to 102 |
| Intervention duration | From REQUEST to COMPLETED or cancellation | ≤ 10 s | PP-SWR-083 |
| Fault response | Time when `path_valid` or `active_function` changes | Per requirement, timing error ≤ one cycle | PP-SWR-124, 142 to 145, 147 |
| Output and arbitration | PathStatus values for each event | Per requirement | PP-SWR-010 to 015, 030 to 047, 063 |

### 8.2 Performance targets: measurement and ranking {#benchmark-metrics}

No pass thresholds. Report the worst value across all seeds and the degradation relative to the noise-free baseline.

| Metric | Measurement | Preferred direction | Target |
|---|---|---|---|
| Lateral deviation | Path relative to actual lane center, over 0–1 s | Smaller | PP-SWR-050 |
| HWA added a_y | Maximum during recentering or center offset | Smaller | PP-SWR-002 |
| HWA lateral jerk | Peak and RMS | Smaller | PP-SWR-004 |
| Added lateral deviation due to latency | Q1 relative to zero latency | Smaller | PP-SWR-013 |
| Computation time | Host wall clock: mean, p95, p99, maximum | Smaller | PP-SWR-016 |
| Recentering time | From HWA start until lateral deviation ≤ 0.1 m | Shorter | PP-SWR-053 |
| Clearance during center offset | Minimum lateral distance to objects on each side | Larger | PP-SWR-057 |
| Return time after a large vehicle passes | From when the rear of the large vehicle passes until lateral deviation ≤ 0.1 m | Shorter | PP-SWR-059 |
| LKA and ELK duration | From intervention path start to COMPLETED | Shorter | PP-SWR-081, 082 |
| LKA DTLE | As in Section 8.1 | Larger | PP-SWR-087 |
| Incorrect curvature | Lateral deviation over 2–3 s divided by the deviation of a path following the erroneous lane model exactly | Smaller | PP-SWR-125 |
| RMS steering wheel rate | Closed loop | Smaller | Secondary metric for PP-SWR-004 |

ADAS Functions module metrics (calibration selection in P2 and P3): number of unintended activations in S10; difference in activation timing between modes A and B.

### 8.3 Flexibility {#benchmark-flexibility}

- **Test set.** The assignment's minimum set, plus S2, S3, S5, S6, and S19, on VP-0 through VP-5. Use the same build and calibration set.
- **Score.** (1) Requirement pass rate per profile, which must be 100 % on all profiles. (2) Variation of each performance target across profiles: maximum, minimum, and worst profile.
- **Presentation.** Profile × metric table, marking the worst profile for each metric.

## 9. Ranking and technique comparison {#test-ranking}

| Step | Criterion |
|---|---|
| 1 | Meet all requirements in Section 8.1 on all profiles. Reject a failing technique even if it is smoother |
| 2 | Safety performance targets: lateral deviation, clearance, LKA DTLE |
| 3 | Driver experience performance targets: added a_y, jerk, recentering and return times, intervention duration |
| 4 | Flexibility: variation across profiles |
| 5 | Computation time |

- Candidates: duration-based quintic or clothoid; Frenet sampling (Werling 2010); QP or MPC (Software Detailed Design). Run each technique with its own best calibration set (Section 7).
- Report results in a comparison table and reject at least one technique with a quantitative rationale (assignment).
- Python computation time is for comparing techniques only and does not establish that a technique can run on an ECU.

## 10. Results presentation {#test-reporting}

| Type | Contents |
|---|---|
| Summary table | One row per technique: requirement pass or fail and worst value of each performance target across all seeds |
| Time series | d(t) of the path and vehicle with both lane boundaries; a_y; jerk; function in control; timing of function transitions and fault injection |
| Continuity | Differences between consecutive paths by cycle, with threshold lines |
| By v_lat | Minimum DTLE by v_lat for S4–S8, as in Euro NCAP |
| Latency sweep | Metric by latency level, one curve per technique |
| Flexibility | Profile × metric table |
| Computation time | Histogram with p95 and p99 |

## Appendix A. Data sources {#test-appendix}

- [autotijd.be, Volkswagen Golf 1.5L eTSI 115 hp](https://autotijd.be/en/dimensions/volkswagen/golf/15l-etsi-115-hp): width 1789 mm without mirrors, 2073 mm with mirrors; used only for the width difference attributable to mirrors.
- [ISO 15622:2018, preview](https://cdn.standards.iteh.ai/samples/71515/46b6e07bde1f4c6f91cd143563bdc70f/ISO-15622-2018.pdf); [Euro NCAP LSS Test Protocol v4.3](https://cdn.euroncap.com/cars/assets/euro_ncap_lss_test_protocol_v43_f2ddd5f6d6.pdf); Bosch SMI230, 2018 product brief.

## Revision history {#revision-history}

| Version | Date | Changes |
|---|---|---|
| 0.4 | 2026-11-09 | Vehicle model, Longitudinal speed row: all scenarios with HWA run with the ACC stub enabled |
| 0.5 | 2026-11-10 | Added S19 and F21; F05 is loss of all boundaries; moved the ACC stub from the Software Architectural Design |
| 1.0 | 2026-11-10 | Restructured as the Software Qualification Test Specification, baseline BL1. Added vehicle profiles VP-0 through VP-5 with sources and scored flexibility; separated pass criteria (requirements) from ranking metrics (performance targets); added calibration sweeps P1 through P3; removed real-log replay (no logs), status labels, and open items |
| 1.1 | 2026-11-10 | Lateral Controller stub: separated sampling times for κ and errors, recorded the source of K, and specified that the controller signals that control has stopped while EPS hands steering back |

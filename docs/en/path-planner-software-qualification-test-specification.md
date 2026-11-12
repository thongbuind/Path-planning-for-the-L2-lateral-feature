# Software Qualification Test Specification

| Field | Value |
|---|---|
| Document ID | `PP-SQTS` |
| Version | 1.19 |
| Status | BL1 |
| Author | thongbui |
| Reviewer | thongbui |
| Last updated | 2026-11-12 |

## 1. Purpose and scope {#test-scope}

- **Purpose.** Specify how to verify the path planner, covering the simulation environment, test cases, fault injection, pass criteria, severity, metrics, calibration selection, and comparisons of techniques and planners.
- **Additional checks.** Check planner conformance to the call contract and verify the evaluator with deliberately faulty planner stubs.
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
| UN R79 Annex 8, UN R171 Annex 4, EU 2021/646 Annex I Part 2, Euro NCAP Assessment Protocol SA v10.4.1 | Tests specified in these documents (Section 5.1). Local copies are in `docs/reference/standards/` |
| Euro NCAP Assessment Protocol SA v10.4.1, Sections 4.3.2 and 4.3.3.6 | LSS score (Section 9.2) |
| ISO 21448:2022 | Limits of the conclusion given unknown hazardous situations (Sections 3, 8.4) |
| ISO 26262-8:2018, Section 11 | Confidence in software tools, applied to evaluator checks (Section 12) |
| Menzel, Bagschik, Maurer, Scenarios for Development, Test and Validation of Automated Vehicles, IEEE IV 2018 (PEGASUS) | Three scenario levels: functional, logical, and concrete (Section 5.2) |
| ASAM OpenSCENARIO XML 1.x, ASAM OpenDRIVE 1.x | Logical scenario and road formats (Section 5.2) |
| Published specifications for VinFast VF 3, VF 6, VF 8, VF 9 | Vehicle profiles (Section 4.4) |

## 3. Test principles {#test-principles}

- **Independence.** The test system observes the planner only through the interfaces in the Interface Control Document (inputs, outputs, and computation time). It does not read internal variables or rely on internal mechanisms or thresholds. The planner does not read scenario names, ground truth, seeds, or test configuration.
- **Predefinition.** Fix scenarios, seeds, criteria, and ranking order before running the tests. If anything changes, record why and rerun all techniques.
- **Separate tuning and scoring.** Select calibration on the tuning set; take official scores from the test set (different seeds and some scenarios not used during tuning). Give each technique the same tuning effort budget.
- **No test-specific behavior.** Add new cases only on the test side. If a case fails, fix the planner's general mechanism and rerun the entire suite.
- **Complete, reproducible reporting.** Report all scenarios and seeds, including the worst case. Include the code version, scenario file, and seed with each result.
- **Priorities.** Safety first, then regulatory compliance, driver experience, and computation time. Measure actual vehicle motion relative to the actual lane.
- **Limits of the conclusion.** The benchmark can show that a planner is blocked. A finding of no blocking failures applies only within the scope tested. Demonstrating safety requires evidence beyond this scope (ISO 21448).
- **Learning from results.** The planner and test teams learn from each other through results, problem reports, logs, and requirements while keeping each side's implementation independent.

## 4. Test environment {#simulation-design}

### 4.1 Execution modes {#benchmark-run}

| Item | Specification |
|---|---|
| Scoring mode | Deterministic, single process, 1 ms step. The same seed gives the same result. Official metrics come from this mode |
| Real-time mode | One process per ECU, real sockets, and the `python-can` `udp_multicast` virtual CAN bus. For integration checks only |
| Open loop | The vehicle follows a predefined trajectory independently of the path; measure path quality |
| Closed loop | The path goes through the Lateral Controller and EPS stubs into the vehicle model. The stubs are fixed across all techniques |
| Smoothness | Always measured on planner output, including in closed loop |
| ADAS Functions stub | Mode B uses ideal signals from ground truth to score the planner. Mode A uses received messages to compare activation timing. Arbitration and late-request cases can use predefined FunctionRequests sequences. See Section 4.8 |
| Noise-free baseline | Each scenario has a noise-free run to separate algorithm errors from noise effects |
| IMU | Main scenarios use clean IMU signals (mentor). IMU noise and bias are introduced through fault injection |
| Rate | Planner and ADAS Functions: 40 Hz. Vehicle signals follow the signal list (mentor) |
| Seed | One main seed per run, with separate streams for each channel; 10 seeds per cell with noise |
| Log | One MCAP file per run, sufficient for replay; view in Foxglove |
| 8 GB RAM machine | Run in small batches |

### 4.2 Scheduler and clocks {#sim-scheduler}

| Item | Specification |
|---|---|
| Architecture | Components communicate only through interfaces. The two modes share code and differ only in transport and scheduling. The simulator uses Python and numpy. The planner runs as a C library through the SIL adapter (PP-ADR-013) |
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
| Lane drift sources | The simulated driver sets a steering angle to create a drift arc, then releases the steering input. Crosswind and cross slope produce a sustained lateral force at the center of gravity. See Section 4.8 |
| Initial state | A vehicle starting in a curve begins in steady-state cornering at the local curvature. The simulated driver holds the corresponding steering angle |

**Vehicle profiles.** The planner receives the profile through VehicleConfig. VP-0 is the default for all scenarios; VP-1 through VP-5 are used for S19 and the flexibility suite (Section 8.3).

| Profile | Vehicle | Wheelbase (m) | Body width / width including mirrors (m) | Mass (kg) | Turning radius (m) | Maximum wheel angle (rad) |
|---|---|---|---|---|---|---|
| VP-0 | Midsize electric vehicle, typical values | 2.90 | — / 1.90 | 2000 | — | 0.61 |
| VP-1 | VinFast VF 3 | 2.075 | 1.679 / 1.96 | 857 | 4.05 | 0.54 |
| VP-2 | VinFast VF 6 | 2.730 | 1.834 / 2.11 | 1600 | 5.5 | 0.52 |
| VP-3 | VinFast VF 8 (2022) | 2.950 | 1.934 / 2.21 | 2540 | 6.2 | 0.50 |
| VP-4 | VinFast VF 9 | 3.150 | 2.004 / 2.254 | 2932 | 7.33 | 0.44 |
| VP-5 | Synthetic: as VP-4, with maximum width | 3.150 | — / 2.50 | 2932 | 7.33 | 0.44 |

| Parameter | Derivation | Source |
|---|---|---|
| Wheelbase, body width, mass, turning radius | Published specifications | VF 3, VF 6, VF 8, VF 9: bonbanh.com and VinFast brochures; VF 9 width of 2.254 m: Vietnam News; 2.004 m: bonbanh (Appendix A) |
| Width including mirrors | VF 9: interpret 2.254 m as including mirrors and 2.004 m as excluding them. VF 3, VF 6, VF 8: body width + 0.28 m, based on Volkswagen's published difference with and without mirrors for the Golf 8 (1.789 / 2.073 m) | team agreement |
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
| Lane model | Transform visible lane geometry into `base_link` and fit a degree-3 polynomial to each marking across the three lanes and to each road edge. Inject faults per Section 6. Nominal view range is 0–80 m per marking. Fit each marking only over its observed segment. The scenario sets the start and end points, with Q4 sweeping end points from 10 to 126 m and F22 injecting view-range faults. Capture-to-publish latency is 100 ms | With no fault, report σ_c0 = 0.03 m and σ_c1 = 0.002 (level F01 a). See Section 6 for fault levels |
| ObjectList | Transform scenario objects into `base_link` at the same period and latency as the lane model. Detection range is 150 m ahead and 80 m behind. `existence_probability` is 0.95 for real objects and 0.6 for ghost objects (team agreement) | σ_x = 0.2 m + 1% of distance, σ_y = 0.1 m + 0.5%, σ_vx = 0.3 m/s, σ_vy = 0.2 m/s, and size σ = 0.1 m. Miss detections in 2% of frames. Generate ghost objects at 0.05 per second for 0.2 s each. In rain, multiply σ by 1.5 |
| Yaw rate | Clean in the main scenarios | Fault injection: σ = 0.07 or 0.14 °/s (0.02 °/s/√Hz × √12 or √50 Hz); bias 0.1 / 0.3 / 1 °/s |
| a_x, a_y | Clean in the main scenarios; on a cross slope, still includes g·sin(slope angle) | Fault injection: σ = 0.004 or 0.008 m/s²; bias up to 0.2 m/s² |
| Speed | From the vehicle model before CAN encoding | σ = 0.02 m/s; scale error ±0.5 % |
| Steering wheel angle | Same as above | σ = 0.001 rad, offset from 0 of ±0.01 rad |
| VehicleStateEstimate | Ground-truth v_y plus noise | σ = 0.05 m/s |
| Ego-motion | Integrate speed and yaw rate from the CAN signals and include v_y from VehicleStateEstimate to capture lateral slip (Interface Control Document 5.5). Errors arise naturally when IMU or v_y faults are injected | — |

Traffic travels in the direction of increasing or decreasing `s`. An oncoming vehicle has negative `vx` when the vehicles are aligned. Lateral moves use a time-based quintic, with lateral velocity and acceleration of the move equal to 0 at both ends. The S7 and S8 targets maintain the lateral offset specified by Euro NCAP LSS 7.2.4.3 and 7.2.4.4. ObjectList has 32 slots, and `num_objects` counts occupied slots.

Roads have dashed, solid, and double markings and fixed edges. LaneModel represents the edge of the marking or face of the barrier nearest the vehicle. For double markings, `crossable` follows the line nearest the vehicle. Absent boundaries are reported as LOST.

IMU noise and bias follow the Bosch SMI230. These raw sensor values bound the filtered signals from above. The team set the noise levels for speed, steering angle, perception, and v_y. Nominal camera latency is 100 ms, below the 120 ms worst case of PP-ASM-001. Q1 sweeps other latencies. The team set the 0–80 m view range pending measurements from the real camera (PP-ASM-020). A start point of 0 m is optimistic because the hood obscures the road close to the vehicle.

### 4.6 Lateral Controller and EPS stubs {#sim-controller}

Closed-loop test equipment, fixed across all planner versions.

| Part | Specification |
|---|---|
| Controller | 100 Hz. Read a path point by `stamp_us + time_from_start` and transform it into current `base_link`. δ = L·κ + K·v²·κ + k_y·e_y + k_ψ·e_ψ; tune k_y and k_ψ once and keep them fixed |
| Path sampling time | κ at current time plus `actuator_delay` (PP-ADR-010); e_y and e_ψ at a 0.5 s lookahead point |
| Heading error | e_ψ compares path `pose.yaw` with the direction of vehicle motion at `base_link`, given by body heading plus atan(v_y / v). `pose.yaw` describes the path tangent (Interface Control Document 6.1) |
| Understeer coefficient K | From the simulator's vehicle model (Section 4.4), without using VehicleConfig |
| Invalid path or 75 ms timeout | Hold the last command and signal that control has stopped; EPS hands steering back to the driver over 1 s |
| EPS | Track the requested steering wheel angle with pure delay `actuator_delay`, first-order response with τ = 0.1 s, and rate and angle limits from VehicleConfig. When control stops, blend to the simulated driver's angle over 1 s. At startup, the simulated driver already holds the steering angle, so no handover occurs |

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
| Tracking law | For set speed, a = 0.4·(v_set − v). For the speed envelope, a = dv_allowed/dt + 1.0·(v_allowed − v) | team agreement |
| `lateral_limit_reached` | Do not accelerate while the flag is set | team agreement |
| Limits | Acceleration −3.0 to +1.5 m/s²; jerk ≤ 2.5 m/s³; no AEB | team agreement |
| LongitudinalPlan | Propagate the above law for 3 s and sample v(t) and a(t) on a 0.1 s grid | team agreement |
| LateralLimits lost (75 ms timeout, as with PathStatus) or ACC disabled | Do not accelerate. If ACC is disabled, send OFF, current speed, and acceleration of 0 | team agreement |
| Actuation | Pass the acceleration command through a 0.1 s delay and a first-order response with τ = 0.3 s | team agreement |

### 4.8 Simulated driver and ADAS Functions stub {#sim-adas-function}

| Part | Specification | Source |
|---|---|---|
| HWA view-range condition | When enabled by the scenario (F22), scripted HWA leaves REQUEST for UNAVAILABLE if lookahead time for L1 and R1 stays below `t_view_hwa` for more than `t_view_hold`. It resumes automatically once the range is sufficient. Read speed from the speed signal | ADAS Function Specification Sections 7 and 13 (initial values) |
| LKA and ELK stub | Compute DLC, TLC, intent, and hazards from the supplied signals. Publish FunctionRequests at 40 Hz. Read intervention results from PathStatus | ADAS Function Specification Sections 5–9 and 12, PP-ADR-014, PP-TS-008 |
| Mode A | Read sensor messages after delay and fault injection. Compensate for motion since measurement with EgoMotionQuery. Use this mode to compare activation timing | Sections 4.1, 4.5 |
| Mode B | Use the same 20 Hz lane and object sampling cadence. Take geometry and kinematics from the simulator without injecting errors into the stub's signals. Compensate for motion using the actual pose. Score the planner from the FunctionRequests it receives, ICD outputs, and ground truth | Sections 4.1, 4.5 |
| Log | Record TLC from modes A and B for the same vehicle state. Log the received FunctionRequests and receipt time at every planner tick | Section 8.2, Interface Control Document Section 4 |
| Steering angle during drift | Set the steering angle for the sum of the drift-arc and road curvatures. At release, restore the target steering angle for tracking the road curvature and let the bicycle model integrate the motion | Euro NCAP LSS 7.2.2, EU 2021/646 Annex I Part 2, 5.3.3.1.2 |
| Initialization in a curve | Use the curvature of the offset path as the nominal curvature. Initially align rear-axle motion with the offset path tangent, accounting for the bicycle model's slip angle | Section 4.4 model, PP-PR-015 |
| Steering onset | Euro NCAP tests have a 2 s straight segment from T0 to Tsteer | Euro NCAP LSS 4.2.1 |
| Release of steering input | At Tsteer + R·asin(v_lat/v)/v. In the drift-arc anchors, release occurs between 2.576 and 3.800 s. Report actual v_lat at intervention onset to check the protocol tolerance of ±0.05 m/s | Euro NCAP LSS 7.2.2.1–7.2.2.4, 7.2.3, 7.4.3, EU 2021/646 Annex I Part 2, 5.3.3.1.2–5.3.3.1.3 |
| S8(c, d) turn indicator | Switch on at 1.0 s, which is 1.0 s before Tsteer. Hold until the end of the run | Euro NCAP LSS 7.2.4.4.5 for onset. The team set the switch-off time |
| Hands and torque | Sample at 50 Hz. Apply 1.0 N·m in the steering direction through the drift arc. Set torque to 0 afterward. Use passive hands for Euro NCAP and hands off for the EU grid | ADAS Function Specification Sections 8, 12. Euro NCAP LSS 7.2.2.4. EU 2021/646 Annex I Part 2, 5.3.3.1.2 |
| S4(d) crosswind | Apply a constant 300 N at the center of gravity toward the right from 2.0 s to the end of the 20 s run, equivalent to 0.15 m/s² initially for VP-0 | team agreement, model in Section 4.4 |
| S4(e) cross slope | Apply a 2% leftward downslope from 2.0 s to the end of the 20 s run, equivalent to about 1.15° | team agreement, model in Section 4.4 |
| S6(d) barrier | 0.2 m wide, 0.8 m high, along the road. The face nearest the vehicle coincides with the right lane boundary | team agreement |
| S7 and S8 target vehicles | 1.9 m wide and 4.8 m long. The target center is 1.5 m from the inner marking edge. Synchronize with the nominal trajectory without intervention. Use 10% front overlap in S7 and align the front of the target with the test vehicle's rear axle in S8 | The team set the dimensions. Euro NCAP LSS 7.2.4.3–7.2.4.4 for synchronization |
| S8 late | Keep the vehicle drifting and publish ELK REQUEST from the instant the nominal trajectory takes the tire 0.45 m beyond the marking. Verify actual DLC on receipt per Section 8.1 | 0.3 m from PP-SWR-089. The team set a 0.15 m margin for model error |
| v_lat in additional anchors | S4b(b–e) uses 0.3 m/s as in S4b(a). S5(e), S6(c, d), and S7(d, e) use 0.4 m/s | team agreement within the Euro NCAP LSS 7.2.4–7.2.5 range |
| Run length and duration | Start at s = 100 m on a 1,200 m road. Drift-arc anchors run for 17 s, with S8 late running for 10 s | team agreement |
| S4(d, e) repeated drift | Lateral force persists after COMPLETED. A new intervention is eligible once the reactivation conditions are met. Score each intervention | ADAS Function Specification Section 9, PP-SWR-035 |

## 5. Test cases {#benchmark-scenarios}

**Minimum set required by the assignment.** HWA curve tracking (S1), LKA lane drift (S4), and ELK with an oncoming vehicle (S7), each under 5 conditions: no fault, noise (F01), c0 jump (F02), loss of one marking (F04), and incorrect c2 (F06).

- Euro NCAP LSS test speed: 72 km/h. Induce drift along an arc of R = 1200 m, then hold v_lat. Also test 90 km/h.
- The table lists the concrete anchor cases. These cover every protocol test point in Section 5.1 plus at least one variant at the requirement boundary. Generate other concrete cases from the parameter ranges (Section 5.2). Run applicable scenarios on both sides.
- Default to a 3.5 m lane and profile VP-0. Use a 100 m entry clothoid unless the variant specifies another length.
- The Requirement column is generated by `python3 tools/trace.py --write` from the Verification column of the Software Requirements Specification. Do not edit it by hand. IDs are fixed: do not renumber or reuse them.

| # | Scenario | Variants | Requirement |
|---|---|---|---|
| S1 | HWA tracks a curve | 90 km/h with clothoid curve entry. a) R = 1000 m (curve a_y 0.6 m/s²). b) R = 500 m (1.25). c) R = 250 m (2.5, reaches aysmax). d) S-curve, R = 500 m. e) 130 km/h, R = 1000 m (1.3). f) R171 Annex 4, 4.2.4.1 S-curve (R = 787 m then 374 m). g) R = 300 m (2.08 m/s², 83% of aysmax) | PP-SWR-001, 003, 004, 008 (a, b, d, e), 050 (a, b, d, e), 051 (closed loop) |
| S1b | HWA on a curve requiring more than aysmax | a) 90 km/h, R = 200 m (3.1 m/s²). b) 90 km/h, R = 150 m (4.2). c) 110 km/h, R = 300 m (3.1). d) R = 200 m immediately after a crest, with a 40 m camera range throughout the run (flat road with simulated visibility). e) As a with a 60 m clothoid. f) 90 km/h, R = 230 m (2.72 m/s², within aysmax + 0.1 to + 0.4) | PP-SWR-001, 005, 006, 007 (closed loop), 064 |
| S2 | HWA activates with the vehicle off center | 90 km/h. Measure offset and heading error when HWA takes control. a) 0.2 m offset, 0° heading error. b) 0.4 m, 1° inward. c) 0.5 m, 2° outward. d) 0.4 m on the outside of a curve with R = 500 m. e) 0.5 m at 130 km/h | PP-SWR-002, 052, 053 |
| S3 | HWA offsets the center when passing a truck in an adjacent lane | Truck width 2.5 m. a) 5 m/s slower. b) 2 m/s slower. c) 10 m/s slower. d) Truck 0.1 m from the marking. e) Truck encroaches 0.3 m beyond the marking | PP-SWR-002, 055, 056, 057, 058, 059 |
| S3b | A large vehicle overtakes from behind in a narrow lane | Truck is 5 m/s faster and detected only by corner radar before drawing alongside. a) Opposite side empty, lane 3.5 m. b) Passenger car on the opposite side. c) Truck on the opposite side. d) As a, lane 3.0 m. e) As c, lane 2.75 m | PP-SWR-056, 057 |
| S4 | LKA for lane drift on a straight road | a) 72 km/h, dashed marking, v_lat 0.2 m/s; b) 72 km/h, solid marking, 0.4; c) 90 km/h, 0.6; d) crosswind-induced drift; e) cross slope-induced drift | PP-SWR-032, 080, 081, 083, 084 (closed loop), 085 (closed loop), 086 (closed loop), 087 (closed loop), 090, 110, 112, 114 |
| S4b | LKA for lane drift in a curve | 90 km/h. a) R = 1000 m, outward drift at 0.3 m/s; b) R = 500 m, outward; c) R = 500 m, inward; d) R = 250 m, outward, with only 0.5 m/s² remaining within the LKA limit; e) outward drift in the clothoid | PP-SWR-083, 085 (closed loop), 110, 112, 114 |
| S5 | Solid-marking ELK with LKA disabled | a) 72 km/h, v_lat 0.2. b) 0.4. c) 0.6. d) 90 km/h, 0.4. e) Double marking. f) 72 km/h, 0.5 | PP-SWR-032, 080, 082, 083, 085 (closed loop), 086 (closed loop), 090, 111, 113, 115 |
| S6 | Road-edge ELK | Passenger side. a) road edge only, v_lat 0.2; b) road edge only, 0.6; c) dashed center marking with no marking by the edge; d) barrier as the road edge; e) 90 km/h, 0.4 | PP-SWR-080, 082, 083, 085 (closed loop), 086 (closed loop), 111, 113, 115 |
| S6b | Lane widening | HWA enabled. a) emergency lane widens by 1.5 m over 100 m on the right; b) exit branch; c) new lane on the left; d) widening on a curve with R = 500 m; e) widening while offsetting the center due to a truck on the other side | PP-SWR-050, 060 (closed loop) |
| S7 | ELK for an oncoming vehicle | Other vehicle 1.5 m from the inner edge of the center marking, with 10 % overlap without intervention. a) both at 72 km/h, v_lat 0.2; b) 0.4; c) 0.6; d) other vehicle at 90 km/h; e) on a curve with R = 500 m | PP-SWR-082, 083, 085 (closed loop), 088 (closed loop), 111, 113, 115 |
| S8 | ELK for an overtaking vehicle | a) Other vehicle at 80 km/h, ego vehicle at 72 km/h, drift at 0.2 m/s. b) Both at 72 km/h, drift at 0.4. c) Turn indicator 1.0 ± 0.5 s before steering, 0.5 m/s. d) As c, 0.7 m/s. e) Other vehicle at 100 km/h, drift at 0.4. The additional late case injects ELK REQUEST after the front tire has crossed the marking | PP-SWR-082, 083, 085 (closed loop), 088 (closed loop), 089, 111, 113, 115 |
| S8b | Signaled lane change with a rear vehicle at different distances | a) 20 m away, 2.2 m/s faster; b) 10 m, 2.2 m/s; c) 20 m, 8 m/s; d) 12 m, 10 m/s (TTC 1.2 s); e) 30 m, 14 m/s (requires 3.3 m/s²). a–c: no intervention; d, e: intervene per ADAS Function Specification Section 6, step 5 | PP-SWR-082 (d, e), 083 (d, e), 085 (d, e, closed loop), 111 (d, e), 113 (d, e), 115 (d, e) |
| S8c | Sudden evasive steering with a vehicle in the adjacent lane | No turn indicator. a) v_lat 1.2 m/s; b) 1.5 m/s; c) steer and immediately steer back; d) steer during LKA intervention | PP-SWR-031 (d), 036 (d), 037 (d) |
| S9 | Function transitions | a) LKA to ELK; b) ELK finishes and returns to HWA; c) HWA overridden, then override released; d) request cancelled due to turn indicator; e) driver switches off HWA mid-curve at R = 500 m | PP-SWR-030 (a), 031, 033 (b), 036 (d), 037 (d), 038, 039 (c), 040 (c), 042 (e) |
| S10 | Travel close to a marking without drifting | a) DLC 0.2 m, v_lat near 0; b) DLC 0.4 m; c) cut a curve with R = 500 m; d) drive offset to one side when a truck is present; e) as a, at night, mode A |   |
| S11 | Motorway traffic congestion | HWA enabled. a) 0–30 km/h; b) 0–60 km/h; c) stop for 10 s, then resume; d) another vehicle cuts in at 20 km/h | PP-SWR-050, 054 |
| S12 | Rain | μ = 0.5, nighttime camera noise, perception noise × 1.5. a) S1c; b) S4c; c) S7c; d) S4b-d | PP-SWR-001 (a) |
| S13 | Slow EPS | S4c and S5c with EPS delay of a) 75 ms; b) 100 ms; c) 150 ms | PP-SWR-091 (a, b, closed loop) |
| S14 | Lateral and longitudinal modules exchange constraints | Run twice, once with ACC reading LateralLimits and once with ACC ignoring it. a) S1b-a. b) Another vehicle encroaches by 0.5 m. c) Both. d) Loss of LongitudinalPlan mid-curve. e) S1f S-curve at 130 km/h (the R = 374 m segment requires 3.5 m/s²) | PP-SWR-009, 150, 151, 152, 153, 154 (d), 155 (d) |
| S15 | Center offset with objects on both sides | a) Trucks on both sides. b) Truck and barrier. c) Truck and passenger car. d) Trucks on both sides, lane 3.0 m. e) Barriers on both sides | PP-SWR-056, 057 |
| S16 | Repeated interventions | a) LKA COMPLETED, REQUEST holds for another 1 s; b) as a, REQUEST clears for 0.2 s, then returns; c) three drifts at 0.4 m/s, 2 s apart; d) as c, with solid-marking ELK; e) second intervention starts 0.2 s after COMPLETED | PP-SWR-034 (a, b), 035 (c, d, e), 041 (a, b) |
| S17 | Driver changes lanes with HWA enabled | The lane model switches lanes as the vehicle crosses the marking. a) straight road at 90 km/h, 4 s; b) 2.5 s; c) curve with R = 500 m; d) two consecutive lane changes; e) lane change flag delayed by one frame | PP-SWR-039, 040, 061 |
| S19 | Lane width and vehicle width | HWA at 90 km/h, straight road then curve with R = 500 m. a) lane 2.5 m, VP-1; b) lane 2.5 m, VP-5; c) lane 5.5 m, VP-2; d) lane 3.0 m, VP-4, 2.5 m-wide truck in an adjacent lane traveling 5 m/s slower; e) as d, with trucks on both sides | PP-SWR-050, 062, 063 (b) |

### 5.1 Regulatory and assessment test cases {#benchmark-regulatory}

The table maps each protocol test to a scenario. Tests assigned to other modules (Lateral Controller, EPS, ADAS Functions) are marked "None".

| Document and section | Test | Protocol test points | Pass criteria | Scenario | Notes |
|---|---|---|---|---|---|
| R79 Annex 8, 3.2.1 and R171 Annex 4, 4.2.5.1.1.1.1 | Lane keeping in a curve | Hands off at constant speed. The curve requires 80–90% of aysmax | The front tire does not cross the outer edge of the marking. Jerk ≤ 5 m/s³ | S1 (g) | aysmax is constant over 10–130 km/h, so test one range |
| R79 Annex 8, 3.2.2 and R171 Annex 4, 4.2.5.1.1.1.2 | Maximum a_y | The curve requires > aysmax + 0.3 m/s². Disable curve deceleration | a_y within the R79 5.6.2.1.1 limits and jerk ≤ 5 m/s³ | S1b (a, b, c), ACC ignores LateralLimits | |
| R79 Annex 8, 3.2.5 | Lane departure warning | The curve requires aysmax + 0.1 to + 0.4 m/s² | Warn by the time the front tire crosses the marking and continue assistance | S1b (f) | Warning uses `lateral_limit_reached` |
| R79 Annex 8, 3.1, 3.2.3, 3.2.4 | CSF warning, override force, hands off | — | — | None | ADAS Functions, Lateral Controller, EPS |
| R79 Annex 8, 3.3.1, 3.3.2 | ESF with an adjacent-lane vehicle | An adjacent-lane vehicle approaches. The driver intentionally changes lanes | Stay in the original lane and warn no later than intervention onset | S7, S8 | ADAS Functions is responsible for the warning |
| R79 Annex 8, 3.3.3 to 3.3.5 | ESF with objects in the road, missing markings, or incorrect response | — | — | None | Outside the ELK function and the project's ODD |
| R171 Annex 4, 4.2.4.1, 4.2.5.1.1.2 | Lane position, extended tests | Standard S-curve and multiple curvatures and speeds. At least one case exceeds declared a_y. Include markings, road edges, and a single marking | Stay in the lane with stable motion | S1 (f), S14 (e), F04, F21 | R171 requires ≥ 90% of tests to pass (Annex 3 Appendix 4). The project requires all tests to pass |
| R171 5.3.7.1.1.1, 5.3.7.1.3 | Adjust speed to curvature | — | A speed strategy is defined and can be described | S14 | Software Architectural Design Section 6.2 |
| EU 2021/646 Annex I Part 2, 5.3.3 and 3.6.2 | ELK lane keeping | Solid marking, left and right. 72 ± 1 km/h. Drift arc R ≥ 1200 m followed by hands off. v_lat 0.2 and 0.5 ± 0.05 m/s | DTLM stays within the −0.3 m departure limit | S5 (a, f) | Section 3.6.2 gives v_lat ranges of 0.2–0.5 m/s up to 100 km/h and 0.2–0.3 m/s above 100 km/h |
| EU 2021/646 Annex I Part 2, 5.3.2 | ELK override | Driver overrides during intervention | Steering assistance does not drop abruptly after override | S9 (c) | EPS is responsible for force ≤ 50 N |
| EU 2021/646 Annex I Part 2, 4.3 and Euro NCAP LSS 7.2.6 | LDW | — | — | None | ADAS Functions is responsible for the warning |
| Euro NCAP LSS 7.2.3, 7.2.5 and SA 4.3.2 | LKA with dashed and solid markings | 72 km/h, drift arc R = 1200 m, v_lat 0.2–0.6 m/s in 0.1 m/s steps, both sides | DTLE ≥ −0.3 m | S4 | |
| Euro NCAP LSS 7.2.4.1, 7.2.4.2 and SA 4.3.3 | ELK with a road edge or solid marking | Passenger-side road edge alone, or a dashed center marking with no marking at the edge. Solid marking on either side. v_lat 0.2–0.6 m/s in 0.1 m/s steps | DTLE ≥ −0.1 m for road edges and ≥ −0.3 m for markings | S5, S6 | |
| Euro NCAP LSS 7.2.4.3 and SA 4.3.3.4 | ELK with an oncoming vehicle | Other vehicle 1.5 m from the inner edge of the center marking, with 10% overlap without intervention. Driver side, v_lat 0.2–0.6 m/s | No collision | S7 | |
| Euro NCAP LSS 7.2.4.4 and SA 4.3.3.4 | ELK with an overtaking vehicle | Both at 72 km/h, and 80 versus 72 km/h. Unintentional drift v_lat 0.2–0.6 m/s. Intentional drift with turn indicator at 1.0 ± 0.5 s, v_lat 0.5–0.7 m/s, and arc R = 800 m | No collision | S8 | |
| R79 Annex 8, 2.4 | Measuring a_y and jerk | At the center of gravity, sample at ≥ 100 Hz. Apply a fourth-order Butterworth filter with 0.5 Hz cutoff. Jerk is a 0.5 s moving average of the derivative | — | Closed-loop HWA, LKA, ELK | Score Trajectory. Report vehicle measurements for information (Section 8.2) |

Each row of the protocol grid is defined in `*.protocol.xosc` and runs in the regression and full suites. The Euro NCAP grid uses both sides for markings, the passenger side for road edges, and the driver side for target vehicles. It uses a width of 3.7 m between the inner edges per Section 6.1.3.1 so all profiles use the same geometry. The EU grid uses both sides and v_lat of 0.2 and 0.5 m/s. Anchor cases and coverage samples use separate distributions.

### 5.2 Functional, logical, and concrete scenarios {#benchmark-scenario-levels}

The three PEGASUS scenario levels also form the framework of ISO 34502.

| Level | Definition | Location |
|---|---|---|
| Functional | Written description of the road, ego vehicle, other vehicles, faults, and pass criteria | Section 5 tables |
| Logical | Range of values for each parameter | `benchmark/scenarios/` contains ASAM OpenSCENARIO XML scenarios (`.xosc`) with `ParameterDeclarations`, parameter ranges (`ParameterValueDistribution` with `DistributionRange` or `DistributionSet`), and ASAM OpenDRIVE roads (`.xodr`) |
| Concrete | One value for every parameter | Generated from the logical scenario. Variants a, b, c, and so on in Section 5 are concrete anchors with fixed IDs |

| Group | Common parameters | Range |
|---|---|---|
| Road | Lane width and boundary type on each side | 2.5–5.5 m (Software Requirements Specification Section 5). Dashed, solid, and double markings, and road edges |
| Ego vehicle | Speed and vehicle profile | Operating range of the function (ADAS Function Specification Section 7). VP-0 to VP-5 |
| Sensors and timing | Lane model noise and camera latency | F01 and Q1 |
| Longitudinal module | ACC mode | Reads or ignores LateralLimits |

Scenario-specific parameters (radius, v_lat, other vehicles, and so on) and their ranges are declared in the scenario files. Where a protocol specifies a range, use the test points in Section 5.1.

**Selecting concrete cases**

1. Anchors. Use every variant in Section 5.
2. Boundaries. Use each parameter at the minimum and maximum of its range with the other parameters at nominal values.
3. Pairwise. Use all pairs of minimum, nominal, and maximum values for any two parameters.
4. Random. Use Latin hypercube sampling within the ranges with a fixed seed.

| Suite | Coverage | When to run |
|---|---|---|
| Smoke | Anchors, VP-0, one seed | On every code change |
| Regression | Anchors and boundaries, all profiles, two seeds | For each major planner change and before closing a trade study |
| Full | All four selection methods, all profiles, ten seeds per cell with noise (Section 4.1) | Before each baseline |

These suites define test depth. Section 5.3 defines the aspects tested. Each aspect can run at any of the three depths.

### 5.3 Test suites by aspect {#benchmark-aspects}

Each concrete case has two labels, difficulty and expected outcome. The test team assigns them using the Software Requirements Specification and the ADAS Function Specification. The aspect suites select cases by these labels.

**Difficulty.** If a case fits several levels, use the highest.

| Level | Case conditions | Examples |
|---|---|---|
| L0 | Inside the ODD, away from its limits, with no faults and required a_y ≤ aysmax | S1 (a), S4 (a) |
| L1 | At least one parameter is at the limit of the ODD or function range, such as lane width, speed, vehicle width, or lookahead time | S19 (a) |
| L2 | Inside the ODD, with required steering authority above the function's limit | S1b, S14 |
| L3 | One fault from Section 6 | F01 to F22, Q1 to Q4 |
| L4 | Fault combination from Section 6.2 | Night and rain case |
| L5 | Outside the ODD or the function's operating range | Q4 with lookahead below `t_view_hwa` |

**Expected outcome.** Record the code from the second column in the scenario.

| Outcome | Code | Observable output |
|---|---|---|
| Drive | `drive` | Valid path for the function selected under PP-SWR-030 on every cycle, except where a requirement allows otherwise |
| Drive with limits | `drive_limited` | Same as Drive, with flags set as required, including `lateral_limit_reached` (PP-SWR-007) and `lane_too_narrow` (PP-SWR-063) |
| Refuse | `refuse` | Do not start the function (PP-SWR-047, 089, 146), or report `path_valid = false` and `active_function = NONE` within the required time (PP-SWR-124, 142 to 145) |

Score both directions.

- **Missed refusal.** If the planner keeps driving in a Refuse case, fail the case's requirement.
- **Unnecessary refusal.** In a Drive or Drive with limits case, fail PP-SWR-030 if `active_function` differs from the function selected under PP-SWR-030 and none of the conditions in PP-SWR-124, 142 to 145 applies.

**Aspects**

| Suite | Question | Coverage |
|---|---|---|
| B0 Conformance | Does the planner satisfy the call contract? | Section 11. Run before any other suite. Uses no scenarios |
| B1 Nominal | Does it drive correctly under nominal conditions? | L0 |
| B2 Regulatory | Does it pass the protocol tests? | Protocol grid in Section 5.1 |
| B3 Performance limit | Does it behave correctly at the ODD boundary and beyond steering authority limits? | L1, L2 |
| B4 Robustness | Does it behave correctly under sensor, timing, and integrity faults? | L3, L4 |
| B5 Degradation and refusal | Does it degrade and refuse at the right times while avoiding unnecessary refusals? | Drive with limits and Refuse cases, L5, and S10 |
| B6 Comfort | Is the path smooth? | Driver experience performance targets (Section 8.2) on B1 cases |
| B7 Flexibility | Does the same build and calibration work on all vehicles? | Section 8.3 |
| B8 Compute | How long does the planner take to compute? | PP-SWR-016 on every case |

## 6. Fault injection {#benchmark-faults}

Inject each fault at three times: during steady HWA operation, at LKA or ELK activation, and during an intervention. Fault timing follows frame capture time. The lane model sends no flag (PP-ASM-009). The Requirement column is generated as in Section 5.

| ID | Group | Fault | Level or form | Requirement |
|---|---|---|---|---|
| F01 | Lane model | c0 and c1 noise | a) daytime σ_c0 = 0.03 m, σ_c1 = 0.002; b) × 1.5; c) night or rain × 2.5 | PP-SWR-120 |
| F02 | Lane model | c0 jump without a flag | The entire lane model jumps in one frame. a) 0.3 m. b) 0.6 m. c) 1.0 m. In a–c, hold for 1 s before returning. d) 0.6 m, return after one frame. e) 0.6 m, hold | PP-SWR-121 |
| F03 | Lane model | Misidentified adjacent-lane marking | a) left marking jumps to L2 in one frame; b) as a, lasting 0.5 s; c) both markings jump to the adjacent lane with no lane change flag; d) old marking or crack offset by 0.5 m, lasting 2 s; e) as a, during ELK | PP-SWR-050, 122 (closed loop) |
| F04 | Lane model | Loss of one marking | a) Immediate loss on the left. b) Immediate loss on the right. c) Left-side confidence falls to 0 over 2 s. d) Right-side confidence falls to 0 over 2 s. e) Loss while lane width changes | PP-SWR-050, 123 (a–d, closed loop) |
| F05 | Lane model | Loss of all boundaries: both ego-lane markings, adjacent-lane markings, and road edges | a) reconstruct for 0.5 s, then lose them; b) reconstruct for 1 s, then lose them; c) lose them for 0.5 s, then recover; d) loss mid-curve at R = 500 m | PP-SWR-043, 124 |
| F06 | Lane model | Incorrect curvature | All markings. a) c2 +0.0005 1/m on a straight road. b) −0.0005 1/m in a curve. c) c3 +4·10⁻⁶ 1/m², with the same curvature error as a at 40 m. d) As a, for 2 s. e) As a, during curve entry. Cases a, b, c, and e last 1 s | PP-SWR-125 |
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
| F21 | Lane model | Both ego-lane markings lost, other boundaries remain | a) L2 and R2 remain, confidence ≥ `conf_inferred`. b) Only L2 remains. c) Only the right road edge outside the ego-lane corridor remains, for 5 s. d) As a, on a curve with R = 500 m. e) As a, with confidence between `conf_ego` and `conf_inferred` | PP-SWR-047, 050, 124 (e), 147 (a–d), 148 (a–d, closed loop) |
| F22 | Lane model | Short or changing view range without a flag | Enable the HWA view-range condition (Section 4.8). Ego vehicle travels at 25 m/s. a) All markings shortened to 30 m for 0.5 s, below `t_view_hold`, so HWA remains in control. b) Only R1 shortened to 30 m until the run ends. c) All markings shortened to 30 m for 2 s on curve entry. d) Alternate 30 m and nominal range each frame for 2 s. e) Report 150 m using the same polynomial for 1 s on curve entry, extrapolating beyond the observed segment. f) All markings shortened to 15 m for 3 s (0.6 s lookahead). HWA leaves REQUEST after `t_view_hold` and then returns | PP-SWR-017 (e), 042 (f), 050, 149 (a, b, c, d, e, f, closed loop) |

### 6.1 Latency and view-range sweeps

Actual latency (mentor) and view range (PP-ASM-020) are unknown, so sweep multiple levels. Vary only simulator settings and keep the planner configuration fixed.

| ID | Sweep | Levels | Requirement |
|---|---|---|---|
| Q1 | Camera latency (lane model, objects) | 0 / 50 / 100 / 150 / 200 / 300 ms, each with ±20 ms jitter | PP-SWR-012, 013, 131 (300 ms), 133 (200 ms) |
| Q2 | Filtered yaw-rate latency not reported to the planner | 0 / 25 / 50 / 100 ms | PP-SWR-138 (0–50 ms, closed loop) |
| Q3 | FunctionRequests latency | 20 / 40 / 60 ms | PP-SWR-038 |
| Q4 | Camera view range | End points 10 / 20 / 40 / 80 / 126 m and start points 0 / 5 / 10 m. Run on S1 (a, c, f) and S14 (a, e). Include lookahead times below `t_view_hwa` to evaluate the algorithm's capability. Run `python3 -m eval.matrix Q4` | PP-SWR-017, 050, 151 |

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
| Minimum DTLE | Minimum over the intervention from the outer edge of the front tire to the inner edge of the marking or to the road edge | ≥ −0.3 m (LKA and solid-marking ELK), ≥ −0.1 m (road-edge ELK) | PP-SWR-086, 091 |
| Clearance to adjacent-lane vehicle | Minimum lateral distance between the vehicles during ELK triggered by the adjacent-lane vehicle | ≥ 0.3 m | PP-SWR-088 |
| DLC relative to actual lane | Minimum on each side. For PP-SWR-051, measure only when actual free space on each side is ≥ `free_space_min` | ≥ 0 | PP-SWR-051, 060, 122, 123, 148 |
| Drift-side DLC at LKA completion | Actual DLC on the requested side when LKA reports COMPLETED | ≥ 0 | PP-SWR-084 |
| Opposite-side DLC | Minimum DLC on the opposite side from intervention onset through the 1 s EPS handover after COMPLETED or cancellation. End the window at the next independent intervention | ≥ 0 | PP-SWR-085 |
| `lane_too_narrow` in a narrow lane | When actual free space on each side is < `free_space_min`, measure the fraction of valid-path cycles reporting `lane_too_narrow` | = 1 | PP-SWR-063 |
| a_y, added a_y, jerk | Measure on Trajectory for the function in control. Compute required a_y from actual lane curvature at the path point. Average jerk over 0.5 s | Per PP-SWR-001, 003, 110 to 115 | PP-SWR-001, 003, 110 to 115 |
| Wheel angle and steering wheel rate | On the path | Per the profile's VehicleConfig | PP-SWR-116, 117 |
| Continuity | Differences in lateral position, heading, and curvature between consecutive paths every cycle. Evaluate the new path within the reported lane model view range, transforming to t0 using actual vehicle motion. If no lane model is available, use the entire path | ≤ 0.05 m, ≤ 0.005 rad, ≤ 0.0003 1/m | PP-SWR-100 to 102 |
| Observed horizon | Compare `observed_horizon_s` with the time when the path leaves the reported lane model view range, on every cycle with a valid path and a lane model | ≤ 0.1 s | PP-SWR-018 |
| Intervention duration | From REQUEST to COMPLETED or cancellation | ≤ 10 s | PP-SWR-083 |
| Start of the intervention path | At the start tick, compare rear-axle position and v_lat with ground truth in the lane frame | ≤ 0.1 m and ≤ 0.1 m/s | PP-SWR-080 |
| Completion | At each tick, track DLC, front-axle v_lat, body heading relative to the lane, and added a_y of the path in use | Report COMPLETED for the correct function on the tick when `T_end_hold` is met | PP-SWR-032, 090 |
| Late ELK REQUEST | Measure front-tire DLC at the requested-side marking when the planner receives REQUEST. S8 late injects the request based on the nominal trajectory and verifies the condition using vehicle ground truth in SIL | Do not start ELK if DLC < −0.3 m | PP-SWR-089 |
| Fault response | Time when `path_valid` or `active_function` changes | Per requirement, timing error ≤ one cycle | PP-SWR-124, 142 to 145, 147 |
| Output and arbitration | PathStatus values for each event | Per requirement | PP-SWR-010 to 015, 030 to 047 |
| Limit flag at marking contact | `lateral_limit_reached` when the front tire first touches the marking while HWA is in control and maximum required a_y > aysmax | true | PP-SWR-007 |
| Center offset near a large vehicle | Mean path offset from the actual lane center over 0–1 s, positive away from the large vehicle with the least clearance. Score when HWA is in control and a large vehicle is alongside with clearance < `gap_truck_min`. For 055, take the minimum when no large vehicle is alongside on the opposite side. For 058, take the minimum on the first alongside cycle. For 056, take the greatest offset toward the large vehicle. The body extends from rear axle − 1 m to front axle + 1 m | 055 and 058 > 0. 056 ≤ 0 | PP-SWR-055, 056, 058 |

SIL approximates the outer edge of the front tire using half of `vehicle_width` at the front axle. Including the mirrors in the width makes DLC and DTLE conservative by about 0.1–0.15 m. When investigating an S6 failure within this band, check the geometric approximation. Apply the thresholds specified in the requirements.

A case expected to intervene must deliver REQUEST to the planner and produce a path for the corresponding function. If either is missing, fail the case and report the missing step.

For PP-SWR-083, score each intervention whose end is observed or that has reached the 10 s limit. If the log ends while the intervention is still ACTIVE before the limit, report the observed duration. A case that requires intervention must have at least one intervention with a sufficient scoring window.

When LKA or ELK starts and the actual state deviates from the previous path by more than 0.1 m or 0.1 m/s, apply PP-SWR-080 on that tick per PP-SWR-031. Continue scoring continuity for subsequent path pairs.

### 8.2 Performance targets: measurement and ranking {#benchmark-metrics}

No pass thresholds. Report the worst value across all seeds and the degradation relative to the noise-free baseline.

| Metric | Measurement | Preferred direction | Target |
|---|---|---|---|
| Lateral deviation | Path relative to actual lane center, over 0–1 s | Smaller | PP-SWR-050 |
| HWA added a_y | Maximum during recentering or center offset | Smaller | PP-SWR-002 |
| HWA lateral jerk | Peak and RMS | Smaller | PP-SWR-004 |
| Added lateral deviation due to latency | Q1 relative to latency 0 | Smaller | PP-SWR-013 |
| Computation time | Host wall clock: mean, p95, p99, maximum | Smaller | PP-SWR-016 |
| Warning lead time | Minimum time from the limit flag being set until required a_y at the vehicle position exceeds aysmax | Longer | PP-SWR-064 |
| Time to clear the flag | Maximum time from maximum required a_y dropping below aysmax until the flag clears | Shorter | PP-SWR-008 |
| Recentering time | From HWA start until lateral deviation ≤ 0.1 m | Shorter | PP-SWR-053 |
| Clearance during center offset | Minimum lateral distance from the actual vehicle body at the rear and front axles to the edge of the large vehicle while alongside | Larger | PP-SWR-057 |
| Return time after a large vehicle passes | From the end of the alongside interval until the actual vehicle's lateral deviation is ≤ 0.1 m | Shorter | PP-SWR-059 |
| LKA and ELK duration | From intervention path start to COMPLETED | Shorter | PP-SWR-081, 082 |
| LKA DTLE | As in Section 8.1 | Larger | PP-SWR-087 |
| Incorrect curvature | Lateral deviation over 2–3 s divided by the deviation of a path following the erroneous lane model exactly | Smaller | PP-SWR-125 |
| RMS steering wheel rate | Closed loop | Smaller | Secondary metric for PP-SWR-004 |

ADAS Functions module metrics (calibration selection in P2 and P3): number of unintended activations in S10; difference in activation timing between modes A and B.

For S7 and S8, report whether the test vehicle collided with the target per Euro NCAP SA 4.3.3.4. For LKA and ELK, report a_y and jerk from vehicle ground truth using R79 Annex 8, 2.4. Both results are informational.

Also report measurements during HWA control per R79 Annex 8, 2.4. Measure a_y at the center of gravity from ground truth at 1 kHz, using a causal fourth-order Butterworth filter with a 0.5 Hz cutoff initialized at steady state. Jerk is a 0.5 s moving average of the derivative. Report the longest interval with a_y > aysmax + 0.3 m/s² and whether the R79 5.6.2.1.1 limits are met (above aysmax + 0.3 for at most 2 s, with a_y ≤ min(1.4·aysmax, 3.3) m/s²). These values are informational pending a corresponding requirement.

### 8.3 Flexibility {#benchmark-flexibility}

- **Test set.** The assignment's minimum set, plus S2, S3, S5, S6, and S19, on VP-0 through VP-5. Use the same build and calibration set.
- **Score.** (1) Requirement pass rate per profile, which must be 100 % on all profiles. (2) Variation of each performance target across profiles: maximum, minimum, and worst profile.
- **Presentation.** Profile × metric table, marking the worst profile for each metric.

### 8.4 Severity and verdict {#benchmark-severity}

Derive the severity of each failure from the Software Requirements Specification Type column.

| Severity | Applies to | Rationale |
|---|---|---|
| BLOCKER | Requirements of type Safety or with a safety goal, requirements of type Interface, failures of C1 or C2 (Section 11), and planner execution failures | A safety goal is violated or the receiver cannot use the output |
| MAJOR | Requirements of type Regulatory without a safety goal | Fails type approval |
| MINOR | Requirements of type Functional without a safety goal | Incorrect function behavior without a safety goal violation |
| — | Performance targets | Measure and rank only (Section 8.2) |

- One failure on any case, profile, or seed suffices, as in Section 8.1.
- Planner execution failures include a process stopping during `pp_init` or `pp_step`, a call failing to return, and NaN or infinity in the output. Report simulator and evaluator errors separately and leave the affected case unscored.

| Verdict | When |
|---|---|
| Blocked | At least one BLOCKER failure |
| Fails approval | No BLOCKER failures and at least one MAJOR failure |
| No blocking failures found within the tested scope | No BLOCKER or MAJOR failures |

- Set the Integration-ready flag if C3 passes (Section 11).
- Limit the report's verdict to the tested scope (Section 3).

## 9. Ranking and comparison {#test-ranking}

### 9.1 Comparing techniques within one planner {#technique-comparison}

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

### 9.2 Comparing planners {#planner-comparison}

- Include every planner submitted as a C library that passes C1 and C2 (Section 11).
- Compare the planners directly against each other.
- Run every planner with the same benchmark version, concrete cases, profiles, and seeds.

| Tier | Measure | Ranking |
|---|---|---|
| 1 | Verdict from Section 8.4 | Rank no blocking failures found first, followed by Fails approval and Blocked. Among blocked planners, fewer failed BLOCKER requirements ranks higher |
| 2 | Euro NCAP LSS score and pass rates for MAJOR and MINOR requirements | Higher Euro NCAP score first. Break ties with the higher mean pass rate |
| 3 | Performance targets in the four groups from Section 9.1, steps 2 to 5 | Pairwise win score within each group. Proceed to the next group only on a tie |

**Euro NCAP LSS score** (Euro NCAP SA v10.4.1, Sections 4.3.2, 4.3.3.6).

| Test | Scenario | Points |
|---|---|---|
| LKA with a dashed marking | S4 | 0.25 |
| LKA with a solid marking | S4 | 0.25 |
| ELK with only a road edge | S6 | 0.25 |
| ELK with a dashed center marking and no marking at the road edge | S6 | 0.25 |
| ELK with a solid marking | S5 | 0.50 |
| ELK with an oncoming vehicle | S7 | 0.50 |
| ELK with an overtaking vehicle | S8 | 0.50 |

- Award the points for a row when every corresponding case in the protocol grid (Section 5.1) meets the protocol criteria, as in Euro NCAP's scoring by combination.
- Score each profile separately. Use the lowest profile score as the planner score, with one calibration set across vehicles.
- Scoring eligibility conditions (ESC and default ELK enablement) and HMI points are the responsibility of other modules and are outside this scoring scope.

**Pass rate.** For each requirement, divide passing runs by runs that score the requirement. Average across requirements with equal weights.

**Pairwise win score**

- Pair runs by concrete case, profile, and seed. For flexibility, pair by concrete case and seed and use the variation across profiles.
- For each performance target and pair of planners, compute the difference for each matched unit in the preferred direction specified in Section 8.2.
- Planner A beats B when the 95% confidence interval for the mean difference lies entirely in the direction favoring A. Bootstrap the paired units with 10 000 resamples and a fixed seed (team agreement). Otherwise record a tie.
- A planner's score in a group is wins minus losses across all metrics in that group and all other planners (Copeland's method). Metrics have equal weight.

## 10. Results presentation {#test-reporting}

| Type | Contents |
|---|---|
| Verdict | At the start of the report, give the verdict from Section 8.4 and the Integration-ready flag. For Blocked, list every BLOCKER failure with its requirement ID, safety goal, case ID, profile, seed, first failure time, and MCAP file |
| Planner comparison | Report the verdict, Euro NCAP score, pass rate, pairwise win score per group, and absolute values for all metrics (Section 9.2) |
| Summary table | One row per technique: requirement pass or fail and worst value of each performance target across all seeds |
| Time series | d(t) of the path and vehicle with both lane boundaries; a_y; jerk; function in control; timing of function transitions and fault injection |
| Continuity | Differences between consecutive paths by cycle, with threshold lines |
| By v_lat | Minimum DTLE by v_lat for S4–S8, as in Euro NCAP |
| Latency sweep | Metric by latency level, one curve per technique |
| Flexibility | Profile × metric table |
| Computation time | Histogram with p95 and p99 |

## 11. Planner conformance {#planner-conformance}

- A planner under test is a C11 library conforming to `interfaces/c/pp_planner.h` (Interface Control Document Section 4, PP-ADR-013). The test team receives the built library and its `pp_version` string.
- Suite B0 checks what can be observed through the call contract. Algorithms, internal state, code structure, and MISRA compliance are outside its scope.

| Level | Check | Source | On failure |
|---|---|---|---|
| C1 API | Export `pp_state_size`, `pp_init`, `pp_step`, and `pp_version`. Build with `pp_types.h` from the same schema version. Struct sizes and layouts match the generated header. The planner runs with state memory aligned to `PP_STATE_ALIGNMENT` | Interface Control Document Section 4 | Blocked. Skip other suites |
| C2 Contract | `pp_init` does not return OK when VehicleConfig is missing or out of range. In that case no cycle publishes Trajectory. Each `pp_step` fills every output. Counters, timestamps, enum values, array sizes, and the 31 points over 0–3 s follow the Interface Control Document. Outputs contain no NaN or infinity. Missing inputs, `valid = false`, or values at the ends of a range do not stop the planner. `pp_version` returns a stable string with the version, commit, and calibration set ID | Interface Control Document Sections 4, 6. PP-SWR-010, 011, 014, 146 | Blocked. Skip other suites |
| C3 Integration | The same input sequence produces bitwise identical output. Two interleaved instances give the same output as separate runs. The planner stays within its state memory, checked with guard bytes at each end. The symbol table contains no dynamic allocation, file reads, or system clock reads | Interface Control Document Section 4, PP-ADR-013 | Run other suites and leave the Integration-ready flag unset |

## 12. Evaluator checks {#evaluator-check}

- The benchmark is a verification tool, so it must demonstrate that it detects faults (ISO 26262-8:2018, Section 11).
- The test team maintains a set of deliberately faulty planner stubs. Each is a C library implementing `pp_planner.h` with one deliberate defect.
- Use the benchmark only when it reports the expected requirement and severity for every stub below. Additional failures do not affect this check.
- Rerun the faulty planner stubs after any change to `sim/`, `eval/`, or `benchmark/`.

| ID | Deliberate defect | Expected finding |
|---|---|---|
| PM-01 | Add a 0.1 m lateral jump to the path every 40 cycles | PP-SWR-100, BLOCKER |
| PM-02 | Leave a_y unconstrained by aysmax | PP-SWR-001, BLOCKER |
| PM-03 | Keep `path_valid = true` when ego-motion is invalid | PP-SWR-143, BLOCKER |
| PM-04 | Always set `path_valid = false` when HWA is in REQUEST | PP-SWR-030 (unnecessary refusal), BLOCKER |
| PM-05 | Leave the PathStatus counter unchanged | C2 (PP-SWR-014), BLOCKER |
| PM-06 | Publish Trajectory even when `pp_init` reports invalid VehicleConfig | C2 (PP-SWR-146), BLOCKER |
| PM-07 | Store state in a global variable | C3 |
| PM-08 | Write beyond the end of state memory | C3 |
| PM-09 | Read the system clock | C3 |

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
| 1.2 | 2026-11-10 | Section 4.2 runs the planner in the simulator through the SIL adapter (PP-ADR-013) |
| 1.3 | 2026-11-10 | Section 4.6 measures e_ψ for the Lateral Controller stub against the direction of vehicle motion, per the meaning of `pose.yaw` in Interface Control Document 6.1 |
| 1.4 | 2026-11-11 | Section 4.5 includes v_y from VehicleStateEstimate in ego-motion per Interface Control Document 5.5 |
| 1.5 | 2026-11-11 | Specified initial state in curves, EPS at startup, camera range and delay, and the 100 m clothoid. Added S1b e (60 m clothoid). Specified S2 measurement at HWA takeover, speed, and variant b heading direction. Specified F02, F04, and F06 fault shapes |
| 1.6 | 2026-11-11 | Section 8 scores PP-SWR-007 at tire contact with the marking. Added warning lead time (PP-SWR-064) and flag clear time (PP-SWR-008) per Software Requirements Specification 1.3 |
| 1.7 | 2026-11-11 | Section 4.7 specifies the set-speed and curve-envelope tracking laws and the LateralLimits timeout |
| 1.8 | 2026-11-11 | Section 5.1 maps R79 Annex 8, R171 Annex 4, EU 2021/646, and Euro NCAP tests to scenarios. Added anchors S1 f and g, S1b f, S5 f, and S14 e. Section 5.2 specifies the three scenario levels, ASAM OpenSCENARIO and OpenDRIVE formats, concrete case selection, and smoke, regression, and full suites |
| 1.9 | 2026-11-11 | Section 8.2 reports vehicle a_y and jerk per R79 Annex 8, 2.4 for information |
| 1.10 | 2026-11-11 | Section 8.1 scores PP-SWR-051 only with sufficient actual free space and adds a row for PP-SWR-063, per Software Requirements Specification 1.4 |
| 1.11 | 2026-11-11 | S1b d uses a 40 m visible range throughout the run on a flat road |
| 1.12 | 2026-11-11 | Section 4.5 specifies ObjectList detection ranges and `existence_probability`. Section 8.1 scores PP-SWR-055, 056, and 058 per Software Requirements Specification 1.5. Section 8.2 specifies metrics for targets 057 and 059 |
| 1.13 | 2026-11-11 | Section 4 adds driver, traffic, road boundaries, and a two-mode LKA and ELK stub. Section 8 adds the DLC window, DTLE geometry, missing-intervention cases, and closed-loop LKA and ELK metrics |
| 1.14 | 2026-11-12 | F21(c) uses a road edge outside the ego-lane corridor per PP-SWR-047 and PP-TS-007 |
| 1.15 | 2026-11-12 | Specified driver input, target vehicles, S4–S8 anchors, and the protocol grids. Added measurement windows, completion conditions, and the late ELK REQUEST case |
| 1.16 | 2026-11-12 | Section 4.5 specifies separate view ranges and scenario-controlled start and end points for each marking. Section 6 adds F22 (view-range fault) and Q4 (view-range sweep) |
| 1.17 | 2026-11-12 | Section 4.8 adds the HWA view-range condition to the simulator. Section 6 enables it for F22, sets 30 m for variant b, adds variant f (HWA hands back control and then resumes), and runs Q4 through `eval.matrix` |
| 1.18 | 2026-11-12 | Section 5.3 adds aspect suites B0–B8, difficulty labels L0–L5, expected outcomes, and scoring in both directions. Section 8.4 adds severity and verdicts. Section 9 separates technique comparison (9.1) from planner comparison (9.2). Section 10 puts the verdict at the start of the report. Section 11 adds planner conformance. Section 12 checks the evaluator with faulty planner stubs |
| 1.19 | 2026-11-12 | Section 8.1 scores continuity within the reported lane model view range (Software Requirements Specification 1.9) and adds the `observed_horizon_s` metric (PP-SWR-018) |

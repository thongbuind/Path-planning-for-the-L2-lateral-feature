# Software Requirements Specification

| Field | Value |
|---|---|
| Document ID | `PP-SRS` |
| Version | 1.13 |
| Status | BL1 |
| Author | thongbui |
| Reviewer | thongbui |
| Last updated | 2026-11-13 |

## 1. Purpose and scope {#req-scope}

- **Purpose:** Specify what the path planner must achieve as observed externally through its inputs, outputs, and the vehicle's actual motion in the simulator.
- **Scope:** Path planner for three L2/L2+ lateral functions: HWA, LKA, and ELK.
- **Out of scope:** Lane model, perception, the ADAS Functions module (deciding when to intervene), Lateral Controller, EPS, and the longitudinal module. The override force of ≤ 50 N (R79) is the responsibility of the Lateral Controller and EPS.
- **Contents:**

| Type | Meaning | Section |
|---|---|---|
| Requirement | Mandatory, verified as pass or fail. Uses "shall" or "shall not" | 8 |
| Performance target | Measured and ranked, without a pass threshold. Uses "should" | 9 |
| Calibration parameter | A value selected by the designer. This document specifies limits only; initial values and sweep ranges are in the Software Architectural Design | 7 |

## 2. References {#req-references}

| Document | Use |
|---|---|
| G1 assignment (`G1_Path_Planning.pdf`) | Functions, 20–50 Hz rate, continuity limits between consecutive paths, mandatory scenarios |
| [UN Regulation No 79, OJ L 2025/3](https://upload.wikimedia.org/wikipedia/commons/f/f3/OJ_L_202500003_of_2025_-_EN_English.pdf) | ACSF B1 aysmax and jerk, CSF intervention duration, no sudden removal of steering assistance |
| [EU 2021/646 (ELKS)](https://lawplayer.com/eu/act/32021R0646) | Permitted lane marking encroachment for ELK |
| [Euro NCAP LSS Test Protocol v4.3](https://cdn.euroncap.com/cars/assets/euro_ncap_lss_test_protocol_v43_f2ddd5f6d6.pdf), [Assessment Protocol SA v10.4.1](https://cdn.euroncap.com/cars/assets/euro_ncap_assessment_protocol_sa_collision_avoidance_v1041_fafe1dd418.pdf) | DTLE, distance to an adjacent-lane vehicle |
| [ISO 11270:2014](https://standards.iteh.ai/catalog/standards/iso/808a3e9d-fc87-4892-85d1-6087e2ee3370/iso-11270-2014) | LKA jerk |
| [QCVN 09:2015/BGTVT](https://thongtinphapluat.bacgiang.gov.vn/documents/249229/997340/1501942804616_101671520818_VanBanGoc_QCVN%2009.signed.pdf/ada7de78-f0dd-4174-b0a5-1f8a63115728) | Maximum vehicle width |
| ISO 26262, ISO 21448 | Safety requirements, SOTIF |
| EARS (Mavin et al., 2009) | Requirement sentence patterns |
| [Software Architectural Design](report.html?doc=path-planner-software-architectural-design&lang=en), [Interface Control Document](report.html?doc=path-planner-interface-control-document&lang=en), [ADAS Function Specification](report.html?doc=adas-function-specification&lang=en), [Hazard Analysis and Risk Assessment (HARA)](report.html?doc=path-planner-hazard-analysis-and-risk-assessment&lang=en), [Software Qualification Test Specification](report.html?doc=path-planner-software-qualification-test-specification&lang=en) | How requirements are met, schemas, when to intervene, safety goals, and verification methods |

## 3. Conventions {#req-conventions}

| Item | Convention |
|---|---|
| ID | `PP-SWR-nnn` is shared by requirements and performance targets, assigned in blocks as shown below. Assumptions use `PP-ASM-nnn` (Section 6). Do not renumber or reuse IDs; mark withdrawn entries `obsolete` |
| Type | Safety (with safety goal SG in the HARA), Regulatory, Functional, Interface, Performance |
| Verification | Test, Analysis, Inspection, Demonstration. Tests are open loop by default and measure Trajectory; "Test, closed loop" measures the vehicle in the simulator. S, F, and Q IDs are in the Software Qualification Test Specification; variants are in parentheses; "all scenarios", "all faults". This column is the sole source of traceability |
| Calibration parameter | Written as `parameter_name`. Tests use the values in the active calibration set |
| ODD | All requirements shall be met throughout the ODD in Section 5 using the same calibration set |
| Baseline | BL1 is version 1.0. After BL1, changing a requirement or assumption requires recording the reason, listing affected items (`tools/trace.py`), and incrementing the version |

| ID range | Block |
|---|---|
| 001–009 | HWA a_y limits |
| 010–029 | Output and cycle |
| 030–049 | Arbitration |
| 050–079 | HWA |
| 080–099 | LKA, ELK |
| 100–119 | Limits, continuity, feasibility |
| 120–149 | Fault tolerance |
| 150–169 | Interface with the longitudinal module |

## 4. Definitions {#req-definitions}

| Quantity | Definition |
|---|---|
| Cycle | 25 ms (40 Hz) |
| Function in control | `active_function` in PathStatus. "HWA is in control" means `active_function = HWA` |
| Actual lane | The lane occupied by the vehicle, according to simulator ground truth. In a mixed car and motorcycle lane, the part intended for cars |
| Lateral path deviation | Maximum lateral distance between the path and the actual lane center, measured at the same longitudinal position over the 0–1 s segment of the path, unless the requirement specifies a different segment |
| Path a_y | v²·κ at each Trajectory point, where v = `longitudinal_velocity` and κ = `curvature` |
| Required a_y | v²·κ of the actual lane center at the corresponding point on the path |
| Lane model view range | The segment the simulated camera actually observes on both lane boundaries in use. Exclude any reported extension beyond the observed segment |
| Maximum required a_y | Maximum required a_y over 0–3 s, considering only the portion within the lane model's visible range |
| Added a_y | Path a_y minus required a_y at the same point |
| Path lateral jerk | Time derivative of path a_y, with a 0.5 s moving average |
| Consecutive paths | Compare over the time interval both paths describe. Use points of the new path within the view range reported for the lane model frame used in that cycle, or the entire path if no lane model is available. Transform the previous path into the new path's base_link using the vehicle's actual motion |
| Reliable lane boundary | L1 and R1 markings: status MEASURED, confidence ≥ `conf_ego`. L2 and R2 markings or road edges, when used to infer the lane center: status MEASURED, confidence ≥ `conf_inferred` |
| DLC | As in ADAS Function Specification Section 5, calculated using the actual lane and actual vehicle position |
| DTLE | Minimum distance from the outer edge of the tire to the inner edge of the lane marking during an intervention; negative means the marking has been crossed (Euro NCAP) |
| Free space on each side | (actual lane width − vehicle width including mirrors) / 2 |
| Large vehicle | Object in an adjacent lane with width ≥ 2.3 m |
| Alongside | The longitudinal extent of the large vehicle overlaps the ego vehicle body |
| Clearance to a large vehicle | Lateral distance from the ego vehicle body, including mirrors, when centered in the actual lane, to the nearest edge of the large vehicle |
| Termination conditions | DLC ≥ 0 on both sides, magnitude of v_lat ≤ `v_lat_end`, magnitude of heading error relative to the lane ≤ `heading_end`, and magnitude of added a_y ≤ `ay_add_end` |

## 5. Operating conditions (ODD) {#req-odd}

| Condition | Value | Source |
|---|---|---|
| Functions | HWA, LKA, ELK. Speed ranges and activation conditions are in the ADAS Function Specification | — |
| Road | Lane markings or road edges. Lane width 2.5–5.5 m, including mixed car and motorcycle lanes of 4.5 m | mentor (PP-ASM-015) |
| Vehicle | All passenger cars with width ≤ 2.5 m including mirrors. Vehicle parameters are read from VehicleConfig | QCVN 09:2015/BGTVT 2.1.1.1 b (PP-ASM-016) |
| Calibration | One calibration set for all vehicles | team agreement |
| Rate | 40 Hz | mentor |

## 6. Assumptions and dependencies {#req-assumptions}

Each row identifies the requirements that depend on the assumption and how to recheck it once a real vehicle is available.

| ID | Assumption | Affects | How to recheck | Source |
|---|---|---|---|---|
| PP-ASM-001 | Lane model latency from camera capture to publication is 100 ± 20 ms | PP-SWR-013, 131, 133, 134 | Measure elapsed time from the capture timestamp to receipt; use the 99.9th percentile | team agreement |
| PP-ASM-002 | ObjectList latency is the same as the lane model's | PP-SWR-131, 133 | Same as PP-ASM-001 | team agreement |
| PP-ASM-003 | Chassis CAN frame latency is about 5 ms, excluding filter latency | Software Architectural Design Section 3.3 | Measure on the bus | team agreement |
| PP-ASM-004 | Yaw-rate filter latency is unknown. The planner assumes 0 if it is not provided | PP-SWR-138 | Cross-correlate raw and filtered signals | mentor |
| PP-ASM-005 | VehicleStateEstimate latency is about 10 ms | PP-SWR-080, 144 | Measure timestamp to receipt time | team agreement |
| PP-ASM-006 | FunctionRequests latency is about 20 ms | PP-SWR-038 | Measure timestamp to receipt time | team agreement |
| PP-ASM-007 | Trajectory and PathStatus transmission latency is about 1 ms | Software Architectural Design Section 3.3 | Measure on the bus | team agreement |
| PP-ASM-008 | The IMU signal reaching the planner is already filtered for bias and noise upstream | PP-SWR-124, 135, 136 | Measure residual bias and noise while stationary and driving straight | mentor |
| PP-ASM-009 | The lane model does not publish a c0 jump flag | PP-SWR-121 | Read the production lane model protocol | team agreement |
| PP-ASM-010 | When both markings are lost, the lane model reconstructs them for up to 1 s, then reports them lost | PP-SWR-124 | Read the lane model specification | team agreement |
| PP-ASM-011 | Residual lane model noise: σ_c0 = 0.03 m, σ_c1 = 0.002 in daytime; 2.5 times the daytime level at night or in rain | PP-SWR-080, 120 | Measure on the vehicle with ground truth | team agreement |
| PP-ASM-012 | Clock offset is up to ±10 ms before first synchronization and ±50 µs after gPTP synchronization | PP-SWR-132, 137 | Measure at startup and during operation | team agreement |
| PP-ASM-013 | Ego-motion returns Δx, Δy, and Δψ between any two timestamps within the most recent 0.5 s | PP-SWR-012, 131 | Agree on the interface with the ego-motion team | team agreement |
| PP-ASM-014 | Nominal EPS actuation latency is 50 ms | PP-SWR-091 | Measure the EPS step response | team agreement |
| PP-ASM-015 | Lane width on Vietnamese roads is 2.5–5.5 m, including mixed car and motorcycle lanes of 4.5 m | PP-SWR-062, 063 | Measure on the test route | mentor |
| PP-ASM-016 | Vehicle width including mirrors does not exceed 2.5 m | PP-SWR-062, 063 | Read VehicleConfig | QCVN 09:2015/BGTVT 2.1.1.1 b |
| PP-ASM-017 | The Lateral Controller compensates post-planner latency by reading path points using `header.stamp_us` and `time_from_start` (PP-ADR-010) | PP-SWR-012, 086, 091 | Confirm with the Lateral Controller team | team agreement |
| PP-ASM-018 | ASIL ratings for safety requirements follow the safety department's confirmation review of the HARA | All Safety requirements | Safety department review outcome | team agreement |
| PP-ASM-019 | The target platform (ECU, operating system, middleware, coding standard) is unknown. The planner requires only a C11 compiler (PP-ADR-013) | All requirements, through implementation | Ask the mentor for the target platform and coding standard | team agreement |
| PP-ASM-021 | The Lateral Controller uses pure pursuit with a maximum lookahead of 0.6 s and computes steering commands using only the path through `observed_horizon_s` | PP-SWR-018, 100, 101, 102 | Confirm with the Lateral Controller team. An MPC controller that uses the full path would invalidate this assumption | team agreement, based on Autoware pure pursuit (maximum lookahead distance of 15 m, about 0.6 s at 90 km/h) |
| PP-ASM-020 | The lane model view range varies by marking and frame. Actual start and end points are unknown. The benchmark uses a nominal 0–80 m and sweeps end points from 10 to 126 m | PP-SWR-017, 149, 151 | Read the distributions of `line start distance` and `line end distance` in real vehicle logs | team agreement |

## 7. Calibration parameter limits {#req-calibration-limits}

Only parameters referenced by requirements are listed here. The full catalog, initial values, and sweep ranges are in the Software Architectural Design.

| Parameter | Meaning | Limit | Basis for the limit |
|---|---|---|---|
| `conf_ego` | Minimum confidence of L1 and R1 markings | 0–1 | — |
| `conf_edge` | Minimum confidence of a directly measured road edge for ELK | 0–1 | PP-SWR-047 |
| `conf_inferred` | Minimum confidence of a boundary used to infer the lane center | > `conf_ego` | Inference adds the error of the stored offset |
| `T_coast` | Time to follow the previous path when no reliable lane boundary remains | 0–1 s | Analysis: dead-reckoning deviation of 0.06 m after 1 s (Software Architectural Design Appendix A.4) |
| `free_space_min` | Minimum free space on each side for HWA availability | ≥ 0 m | PP-SWR-051 |
| `epsilon_ay` | Amount by which path a_y may be below aysmax when required a_y exceeds aysmax | 0–2.5 m/s² | — |
| `gap_truck_min` | Clearance below which HWA offsets the lane center away from a large vehicle | > 0 m | — |
| `v_lat_end`, `heading_end`, `ay_add_end` | Termination condition thresholds | ≥ 0 | — |
| `T_end_hold` | Time for which the termination conditions must hold continuously before reporting COMPLETED | ≥ 0 s | — |

## 8. Requirements {#req-requirements}

### 8.1 Output and cycle {#req-output}

| ID | Requirement | Verification | Type | Source |
|---|---|---|---|---|
| PP-SWR-010 | The planner shall publish Trajectory and PathStatus every cycle | Test: all scenarios | Interface | mentor |
| PP-SWR-011 | Trajectory shall follow the format in the Interface Control Document: 31 points at 0.1 s intervals, spanning 0–3 s, frame_id = base_link | Inspection | Interface | team agreement (Autoware Trajectory) |
| PP-SWR-012 | Trajectory `header.stamp_us` shall be the time represented by the path, with lane model latency compensated | Inspection; Test: Q1 | Interface | team agreement |
| PP-SWR-014 | `header.counter` shall increment by 1 after every message and wrap over 0–255 | Inspection; Test: all scenarios | Interface | team agreement |
| PP-SWR-018 | `Trajectory.observed_horizon_s` shall be no more than 0.1 s later than the point in time when the path leaves the view range reported by the lane model frame used in that cycle | Test: all scenarios | Interface | team agreement |
| PP-SWR-017 | The planner shall accept a lane model with any `view_range_end > view_range_start` for each marking and road edge. A view range beyond 126 m shall not invalidate the input | Test: F22 (e), Q4 | Interface | team agreement |
| PP-SWR-015 | The planner shall record computation time for every cycle | Inspection | Interface | team agreement |

### 8.2 Arbitration {#req-arbitration}

| ID | Requirement | Verification | Type | Source |
|---|---|---|---|---|
| PP-SWR-030 | The planner shall select the function in control in the priority order ELK > LKA > HWA, considering only functions with state = REQUEST | Test: S9 (a) | Safety, SG-01 | team agreement |
| PP-SWR-031 | When the function in control changes, the path shall satisfy PP-SWR-100 to 102, except when LKA or ELK starts and the actual vehicle deviates from the previous path by more than 0.1 m or 0.1 m/s. In that case, apply PP-SWR-080 | Test: S9, S8c (d) | Safety, SG-04 | assignment |
| PP-SWR-032 | When the LKA or ELK termination conditions have held continuously for `T_end_hold`, the planner shall set that function's phase to COMPLETED | Test: S4, S5 | Functional | team agreement |
| PP-SWR-033 | After COMPLETED, the planner shall select the function in control according to PP-SWR-030 from the functions still in REQUEST, excluding the one just marked COMPLETED. If no function remains, select NONE | Test: S9 (b) | Functional | team agreement |
| PP-SWR-034 | If the function just marked COMPLETED remains in REQUEST, the planner shall not start a new intervention for that function until its state leaves REQUEST and returns to it | Test: S16 (a, b) | Functional | team agreement |
| PP-SWR-035 | Each new LKA or ELK intervention shall have the same limits as the first, regardless of the number of prior interventions | Test: S16 (c, d, e) | Functional | team agreement |
| PP-SWR-036 | When the intervening function leaves REQUEST mid-intervention, the planner shall transition from the current state to the function selected under PP-SWR-030 from those still in REQUEST | Test: S9 (d), S8c (d) | Functional | team agreement |
| PP-SWR-037 | When the intervening function leaves REQUEST mid-intervention through a valid message and no eligible function remains, the planner shall report `active_function = NONE` with `path_valid = true` if the required inputs remain valid | Test: S9 (d), S8c (d) | Safety, SG-02 | team agreement |
| PP-SWR-038 | The planner shall reflect changes in FunctionRequests in its output within one cycle of receiving the message | Test: S9, Q3 | Functional | team agreement |
| PP-SWR-039 | While `driver_override = true`, the start of the path shall match the vehicle's current lateral position with an error of ≤ 0.05 m | Test: S9 (c), S17 | Safety, SG-05 | team agreement |
| PP-SWR-040 | When `driver_override` changes to false while HWA is in REQUEST, the start of the HWA path shall match the vehicle's lateral position at that time with an error of ≤ 0.05 m | Test: S9 (c), S17 | Safety, SG-05 | team agreement |
| PP-SWR-041 | The planner shall keep each function's phase at COMPLETED until that function leaves REQUEST | Test: S16 (a, b) | Functional | team agreement |
| PP-SWR-042 | When HWA leaves REQUEST and no function is in REQUEST, the planner shall set `active_function = NONE` and keep `path_valid = true` | Test: S9 (e), F22 (f) | Safety, SG-02 | team agreement |
| PP-SWR-043 | While `path_valid = false`, `active_function` shall equal NONE | Test: F05, F12 (Lane Model), F20 | Functional | team agreement |
| PP-SWR-044 | When inputs recover after `path_valid = false`, the start of the new path shall match the vehicle's actual lateral state within the tolerances in PP-SWR-080 | Test: F12 (Lane Model, recovery) | Functional | team agreement |
| PP-SWR-045 | After input recovery, the planner shall start an LKA or ELK intervention only after the state of that function leaves REQUEST and returns to it | Test: F12 (Lane Model, recovery) | Safety, SG-01 | team agreement |
| PP-SWR-046 | If VehicleStateEstimate becomes invalid during LKA or ELK intervention, the planner shall continue that intervention path until it ends | Test: F12 (v_y, in S5) | Safety, SG-03 | team agreement |
| PP-SWR-047 | While the lane center can only be inferred from boundaries outside the ego lane, the planner shall not select LKA or ELK. Road-edge ELK is allowed if the hazard-side boundary of the ego lane is a MEASURED edge with confidence ≥ `conf_edge` and a reliable opposite boundary or stored lane width is available | Test: F21 | Safety, SG-01 | mentor, with the scope of road-edge ELK clarified by the team in PP-TS-007 |
| PP-SWR-048 | If the age of FunctionRequests (t0 minus `header.stamp_us`) exceeds 45 ms, the planner shall treat the message as missing, including for the PP-SWR-145 timeout | Test: Q3 | Safety | Interface Control Document 4 (maximum age of 45 ms) |

### 8.3 HWA: a_y limits {#req-hwa-lateral-limit}

| ID | Requirement | Verification | Type | Source |
|---|---|---|---|---|
| PP-SWR-001 | While HWA is in control, path a_y shall be ≤ aysmax = 2.5 m/s² at every point | Test: S1, S1b, S12 (a) | Regulatory, SG-01 | R79 5.6.2.1.3 (≤ 3 m/s²) |
| PP-SWR-003 | While HWA is in control, path lateral jerk shall be ≤ 5 m/s³ | Test: S1 | Regulatory, SG-01 | R79 5.6.2.1.3 c |
| PP-SWR-005 | If maximum required a_y > aysmax while HWA is in control, the planner shall keep `path_valid = true` and `active_function = HWA`, unless arbitration switches to LKA or ELK | Test: S1b | Regulatory, SG-02 | R79 5.6.2.2.3 |
| PP-SWR-006 | If required a_y > aysmax at a point in the 0–1 s segment of the path while HWA is in control, path a_y at that point shall be ≥ aysmax − `epsilon_ay` | Test: S1b | Regulatory, SG-02 | R79 5.6.2.2.3 (assistance within available capability). The team set `epsilon_ay` |
| PP-SWR-007 | When a front tire starts to touch the marking while HWA is in control and maximum required a_y > aysmax, `lateral_limit_reached` shall already be true | Test, closed loop: S1b | Regulatory, SG-01 | R79 5.6.2.2.3 and Annex 8, 3.2.5.2 |
| PP-SWR-009 | The planner shall publish the same `lateral_limit_reached` value in PathStatus and LateralLimits for the same cycle | Inspection; Test: S14 | Interface | team agreement |

### 8.4 HWA: lane keeping and center offset {#req-hwa-centering}

| ID | Requirement | Verification | Type | Source |
|---|---|---|---|---|
| PP-SWR-051 | While HWA is in control, maximum required a_y ≤ aysmax, and free space on each side is ≥ `free_space_min`, DLC on both sides shall be ≥ 0 | Test, closed loop: S1 | Regulatory, SG-01 | R79 5.6.2.1.1 |
| PP-SWR-052 | When HWA takes control with the vehicle up to 0.5 m from the lane center, the function in control shall remain HWA throughout recentering | Test: S2 | Functional | team agreement |
| PP-SWR-054 | While HWA is in REQUEST and vehicle speed is within 0–60 km/h, the planner shall continue publishing a valid path for HWA | Test: S11 | Functional | team agreement |
| PP-SWR-055 | While a large vehicle is alongside in an adjacent lane with clearance < `gap_truck_min` and no large vehicle is alongside on the opposite side, the path shall be offset from the actual lane center away from the large vehicle | Test: S3 | Functional | assignment |
| PP-SWR-056 | While a large vehicle is alongside with clearance < `gap_truck_min`, the path shall not be offset from the actual lane center toward the large vehicle with the smallest clearance | Test: S3, S3b, S15 | Safety, SG-01 | mentor |
| PP-SWR-058 | When a large vehicle in an adjacent lane is approaching, the path shall begin shifting before the large vehicle draws alongside | Test: S3 | Functional | assignment |

### 8.5 HWA: lane changes and ODD {#req-hwa-lane-change}

| ID | Requirement | Verification | Type | Source |
|---|---|---|---|---|
| PP-SWR-060 | When one lane boundary widens outward (emergency stopping lane, branch, or added lane), DLC relative to the actual lane boundary on the widening side shall be ≥ 0 | Test, closed loop: S6b | Safety, SG-01 | mentor |
| PP-SWR-061 | When the lane model switches to a new lane, the path shall satisfy PP-SWR-100 to 102 | Test: S17 | Safety, SG-04 | team agreement |
| PP-SWR-062 | All requirements in Section 8 shall be met throughout the ODD in Section 5 using the same calibration set | Test: S19 | Functional | team agreement |
| PP-SWR-063 | When free space on each side is less than `free_space_min`, the planner shall set `lane_too_narrow = true` in PathStatus | Test: S19 (b) | Safety, SG-01 | team agreement |

### 8.6 LKA and ELK {#req-intervention}

| ID | Requirement | Verification | Type | Source |
|---|---|---|---|---|
| PP-SWR-080 | When LKA or ELK starts intervening, the start of the path shall match the vehicle's actual lateral state within position error ≤ 0.1 m and v_lat error ≤ 0.1 m/s | Test: S4, S5, S6 | Functional | assignment, with tolerances set by the team |
| PP-SWR-083 | The duration of an LKA or ELK intervention, ending in COMPLETED or cancellation, shall be ≤ 10 s | Test: S4, S4b, S5, S6, S7, S8, S8b (d, e) | Safety, SG-01 | team agreement based on R79 5.1.6.1.2.1 (audible warning required beyond 10 s) |
| PP-SWR-084 | When LKA reports COMPLETED, DLC on the side toward which the vehicle drifted shall be ≥ 0 | Test, closed loop: S4 | Functional | assignment |
| PP-SWR-085 | After an LKA or ELK intervention, minimum DLC on the opposite side shall be ≥ 0 | Test, closed loop: S4, S4b, S5, S6, S7, S8, S8b (d, e) | Safety, SG-01 | assignment |
| PP-SWR-086 | Minimum DTLE during an intervention shall be ≥ −0.3 m for LKA and solid-marking ELK, and ≥ −0.1 m for road-edge ELK | Test, closed loop: S4, S5, S6 | Regulatory, SG-03 | Euro NCAP Assessment 4.3.2, 4.3.3.3; EU 2021/646 3.6.2 |
| PP-SWR-088 | During an ELK intervention for an adjacent-lane vehicle, minimum lateral clearance to that vehicle shall be ≥ 0.3 m | Test, closed loop: S7, S8 | Regulatory, SG-03 | Euro NCAP SA 4.3.3.4 (no impact) is the minimum. The team adopted the stricter 0.3 m from LSS 7.4.7 |
| PP-SWR-089 | If ELK is requested when the front tire is already more than 0.3 m beyond the marking on the requested side, the planner shall not start that ELK intervention | Test: S8 | Safety, SG-01 | team agreement |
| PP-SWR-090 | The planner shall not report COMPLETED until the termination conditions have held continuously for `T_end_hold` | Test: S4, S5 | Functional | team agreement |
| PP-SWR-091 | When EPS latency is up to 100 ms, minimum DTLE shall still satisfy PP-SWR-086 | Test, closed loop: S13 (a, b) | Safety, SG-03 | team agreement |

Limit 083 caps the time the planner keeps the intervening function in control while the vehicle is still unsettled. At the timeout, arbitration releases the intervening function and the controller applies its existing handover mechanism.

### 8.7 Limits, continuity, feasibility {#req-limits}

| ID | Requirement | Verification | Type | Source |
|---|---|---|---|---|
| PP-SWR-100 | While `path_valid = true`, lateral deviation between consecutive paths shall be ≤ 0.05 m | Test: all scenarios, all faults | Safety, SG-04 | assignment |
| PP-SWR-101 | While `path_valid = true`, heading difference between consecutive paths shall be ≤ 0.005 rad | Test: all scenarios, all faults | Safety, SG-04 | assignment |
| PP-SWR-102 | While `path_valid = true`, curvature difference between consecutive paths shall be ≤ 0.0003 1/m | Test: all scenarios, all faults | Safety, SG-04 | assignment |
| PP-SWR-110 | While LKA is in control, path a_y shall be ≤ 3.0 m/s² | Test: S4, S4b | Safety, SG-01 | team agreement |
| PP-SWR-111 | While ELK is in control, path a_y shall be ≤ 4.0 m/s² | Test: S5, S6, S7, S8, S8b (d, e) | Safety, SG-01 | team agreement |
| PP-SWR-112 | While LKA is in control, added a_y shall be ≤ 1.5 m/s² | Test: S4, S4b | Safety, SG-01 | team agreement |
| PP-SWR-113 | While ELK is in control, added a_y shall be ≤ 3.0 m/s² | Test: S5, S6, S7, S8, S8b (d, e) | Safety, SG-01 | team agreement |
| PP-SWR-114 | While LKA is in control, path lateral jerk shall be ≤ 5 m/s³ | Test: S4, S4b | Safety, SG-01 | ISO 11270, section number to be verified |
| PP-SWR-115 | While ELK is in control, path lateral jerk shall be ≤ 10 m/s³ | Test: S5, S6, S7, S8, S8b (d, e) | Safety, SG-01 | team agreement |
| PP-SWR-116 | `front_wheel_angle` at every path point shall be ≤ `max_wheel_angle` from VehicleConfig | Test: all scenarios | Safety | VehicleConfig |
| PP-SWR-117 | The steering wheel rate derived from the path (rate of change of `front_wheel_angle` times `steering_ratio`) shall be ≤ `max_steering_wheel_rate` from VehicleConfig | Test: all scenarios | Safety | VehicleConfig |

Basis for steering authority limits: R79 does not limit CSF a_y. ELK at 4.0 m/s² leaves margin below the grip limit of about 4.9 m/s² on a wet road at μ = 0.5. The team agreed on the LKA limits and the added a_y limits.

### 8.8 Fault tolerance: lane model {#req-lane-faults}

| ID | Requirement | Verification | Type | Source |
|---|---|---|---|---|
| PP-SWR-120 | When lane model c0 and c1 noise reaches nighttime levels (2.5 times the daytime level), the path shall satisfy the active function's jerk limit and PP-SWR-100 to 102 | Test: F01 | Safety, SG-01 | team agreement |
| PP-SWR-121 | When c0 jumps by 0.3–1.0 m in one frame, the path shall satisfy PP-SWR-100 to 102 | Test: F02 | Safety, SG-04 | assignment |
| PP-SWR-149 | When the lane model view range briefly shortens, differs by marking, varies by frame, or is reported beyond the actually observed segment, PP-SWR-051 and 100 to 102 shall still be met | Test, closed loop: F22 (a, b, c, d, e, f) | Safety, SG-01 | assignment (detection range is a quality signal) |
| PP-SWR-122 | When the lane model misidentifies an adjacent-lane marking, PP-SWR-051 and 100 to 102 shall still be met | Test, closed loop: F03 | Safety, SG-01 | team agreement |
| PP-SWR-123 | When the lane model loses one marking, PP-SWR-051 and 100 to 102 shall still be met | Test, closed loop: F04 (a–d) | Safety, SG-01 | team agreement |
| PP-SWR-124 | When the lane model has no reliable lane boundary left (ego-lane markings, adjacent-lane markings, or road edges) or is invalid, the planner shall keep `path_valid = true` for `T_coast`, then set `path_valid = false` with a timing error of no more than one cycle | Test: F05, F21 (e), F12 (Lane Model) | Safety, SG-02 | team agreement |
| PP-SWR-147 | When the lane model loses both ego-lane markings but at least one other reliable lane boundary remains, the planner shall keep `path_valid = true` | Test: F21 (a–d) | Functional | mentor |
| PP-SWR-148 | When the lane model loses both ego-lane markings but at least one other reliable lane boundary remains, PP-SWR-051 and 100 to 102 shall still be met | Test, closed loop: F21 (a–d) | Safety, SG-01 | team agreement |

### 8.9 Fault tolerance: timing and integrity {#req-timing-faults}

| ID | Requirement | Verification | Type | Source |
|---|---|---|---|---|
| PP-SWR-126 | When messages are lost individually or in bursts, or have ±20 ms jitter, the path shall satisfy PP-SWR-100 to 102 and the active function's jerk limit | Test: F10 | Safety, SG-04 | team agreement |
| PP-SWR-127 | When messages arrive late or out of order, the path shall satisfy PP-SWR-100 to 102 | Test: F11 | Safety, SG-04 | team agreement |
| PP-SWR-128 | While the camera publishes at 20 Hz and the planner runs at 40 Hz, the path shall satisfy PP-SWR-100 to 102 every cycle | Test: all scenarios, F13 | Safety, SG-04 | team agreement |
| PP-SWR-129 | If a message is duplicated (repeated counter), the output shall match the fault-free case with the same seed | Test: F15 (repeat) | Safety | team agreement |
| PP-SWR-130 | If the counter skips or is stuck, valid = false, the qualifier is FAULT, or the CRC is incorrect, the output shall match the corresponding message loss case | Test: F15 (skip, stuck), F16, F17 | Safety | team agreement |
| PP-SWR-131 | If the age of the lane model or ObjectList exceeds 250 ms, the planner shall treat that input as invalid | Test: Q1 (300 ms) | Safety | team agreement |
| PP-SWR-132 | If an input timestamp is more than 10 ms in the future, the planner shall treat that input as invalid | Test: F19 | Safety | team agreement |
| PP-SWR-133 | While the age of the lane model or ObjectList is within 170–250 ms, the planner shall continue using that input | Test: Q1 (200 ms) | Functional | team agreement |
| PP-SWR-134 | The planner shall log the number of lane model and ObjectList frames with an age greater than 170 ms | Inspection | Functional | team agreement |

Basis: 170 ms = maximum assumed latency of 120 ms (PP-ASM-001) plus 50 ms; 250 ms = maximum latency swept in the benchmark (200 ms) plus 50 ms; 10 ms = maximum clock offset before initial synchronization (PP-ASM-012).

### 8.10 Fault tolerance: invalid input {#req-invalid-input}

| ID | Requirement | Verification | Type | Source |
|---|---|---|---|---|
| PP-SWR-140 | If ObjectList is invalid, the planner shall return the HWA center offset to 0 while still meeting PP-SWR-001, 003, and 100 to 102 | Test: F12 (Perception, in S3) | Safety | team agreement |
| PP-SWR-141 | If ObjectList is invalid, the planner shall still perform the requested ELK intervention | Test: F12 (Perception, in S5) | Safety, SG-03 | team agreement |
| PP-SWR-142 | If IMU, speed, or steering angle is invalid, the planner shall set `path_valid = false` within one cycle | Test: F12 (IMU, speed, steering angle), F17 | Safety | team agreement |
| PP-SWR-143 | If ego-motion is invalid, the planner shall set `path_valid = false` within one cycle | Test: F20 | Safety | team agreement |
| PP-SWR-144 | If VehicleStateEstimate is invalid, the planner shall not start a new LKA or ELK intervention | Test: F12 (v_y) | Safety | team agreement |
| PP-SWR-145 | If FunctionRequests exceeds its 75 ms timeout, the planner shall set `active_function = NONE` and `path_valid = false` within one cycle | Test: F12 (FunctionRequests) | Safety | team agreement |
| PP-SWR-146 | If VehicleConfig is missing at startup, the planner shall not publish Trajectory | Demonstration | Safety | team agreement |

### 8.11 Fault tolerance: vehicle signals and clocks {#req-signal-faults}

| ID | Requirement | Verification | Type | Source |
|---|---|---|---|---|
| PP-SWR-135 | When IMU noise is up to twice the datasheet level, PP-SWR-051 and 100 to 102 shall still be met | Test, closed loop: F07 (a, b) | Safety | Bosch SMI230 datasheet |
| PP-SWR-136 | When yaw-rate bias is up to 0.3 °/s, PP-SWR-051 and 100 to 102 shall still be met | Test, closed loop: F08 (a, b) | Safety | team agreement |
| PP-SWR-137 | When clock drift is up to ±100 ppm or gPTP synchronization is lost for up to 10 s, PP-SWR-051 and 100 to 102 shall still be met | Test, closed loop: F14 (a, b, c) | Safety | team agreement |
| PP-SWR-138 | When filtered yaw rate is delayed by up to 50 ms without that delay being reported to the planner, PP-SWR-051 and 100 to 102 shall still be met | Test, closed loop: Q2 (0–50 ms) | Safety | team agreement |
| PP-SWR-139 | While CAN signals are quantized according to the DBC scaling factor, PP-SWR-051 and 100 to 102 shall still be met | Test, closed loop: all scenarios, F18 | Safety | team agreement |

### 8.12 Interface with the longitudinal module {#req-longitudinal}

| ID | Requirement | Verification | Type | Source |
|---|---|---|---|---|
| PP-SWR-150 | The planner shall publish LateralLimits every cycle | Test: S14 | Interface | team agreement |
| PP-SWR-151 | `LateralLimits.v_max` shall equal √(a_y limit of the function in control / κ_max), within 5% error. κ_max is the maximum curvature of the actual lane center within the lane model's view range, up to 126 m | Test: S14, Q4 | Interface | team agreement |
| PP-SWR-152 | `LateralLimits.distance` shall equal the longitudinal distance to the point with κ_max, with error ≤ 5 m | Test: S14 | Interface | team agreement |
| PP-SWR-153 | When LongitudinalPlan is valid, Trajectory `longitudinal_velocity` and `acceleration` shall be taken from LongitudinalPlan | Test: S14 | Interface | team agreement |
| PP-SWR-154 | If LongitudinalPlan is missing or exceeds its 75 ms timeout, Trajectory shall use the current speed held constant with acceleration set to 0 | Test: S14 (d) | Interface | team agreement |
| PP-SWR-155 | If LongitudinalPlan is missing or exceeds its 75 ms timeout, the planner shall keep `path_valid = true` | Test: S14 (d) | Safety | team agreement |
| PP-SWR-156 | If `v` or `a` at any LongitudinalPlan point is outside the range specified in Interface Control Document 5.7, including NaN or infinity, the planner shall treat the message as missing | Test: F23 | Interface | Interface Control Document 5.3, 5.7 |

## 9. Performance targets {#req-targets}

There are no pass thresholds. The Software Qualification Test Specification measures these metrics to select a calibration set and compare techniques in this priority order: safety, regulatory compliance, driver experience, and computation time.

| ID | Requirement | Verification | Type | Source |
|---|---|---|---|---|
| PP-SWR-050 | Lateral path deviation should be small throughout the ODD and under lane model faults | Test: S1 (a, b, d, e), S6b, S11, S19, F03, F04, F21, F22, Q4 | Performance | assignment |
| PP-SWR-002 | Maximum added a_y during HWA recentering or center offset should be small | Test: S2, S3 | Performance | team agreement |
| PP-SWR-004 | Path lateral jerk while HWA is in control should be small | Test: S1 | Performance | team agreement |
| PP-SWR-008 | The time from when maximum required a_y drops below aysmax until `lateral_limit_reached` clears should be short | Test: S1 (a, b, d, e) | Performance | team agreement |
| PP-SWR-013 | Additional lateral deviation relative to the zero-latency case should be small when camera latency is 0–200 ms with ±20 ms jitter | Test: Q1 | Performance | team agreement |
| PP-SWR-016 | The 99th percentile of computation time per cycle should be low | Test: all scenarios | Performance | team agreement |
| PP-SWR-064 | The time from when `lateral_limit_reached` is set until required a_y at the vehicle's position exceeds aysmax should be long | Test: S1b | Performance | team agreement |
| PP-SWR-053 | The time from HWA taking control (with the vehicle up to 0.5 m off center) to lateral deviation ≤ 0.1 m should be short | Test: S2 | Performance | team agreement |
| PP-SWR-057 | Minimum lateral clearance from the vehicle body to objects on either side while offsetting the center should be large | Test: S3, S3b, S15 | Performance | team agreement |
| PP-SWR-059 | The time from when the rear of the large vehicle has passed to lateral deviation ≤ 0.1 m should be short | Test: S3 | Performance | team agreement |
| PP-SWR-081 | The time from the start of the LKA intervention path to COMPLETED should be short | Test: S4 | Performance | team agreement |
| PP-SWR-082 | The time from the start of the ELK intervention path to COMPLETED should be short | Test: S5, S6, S7, S8, S8b (d, e) | Performance | team agreement |
| PP-SWR-087 | Minimum LKA DTLE should be large | Test, closed loop: S4 | Performance | team agreement |
| PP-SWR-125 | When lane model c2 is incorrect, the ratio of the path's lateral deviation over 2–3 s to the deviation of a path that follows the erroneous lane model exactly should be small | Test: F06 | Performance | assignment |

## Revision history {#revision-history}

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-11-10 | Restructured as the Software Requirements Specification, baseline BL1. Separated requirements, performance targets, and calibration parameter limits; added the ODD (lane width 2.5–5.5 m, vehicle width ≤ 2.5 m including mirrors) and the Type column with safety goals; closed all previous open items (added PP-SWR-041 to 047, 063, and PP-ASM-017, 018); removed status labels and the open items section |
| 1.1 | 2026-11-10 | Added PP-ASM-019. The target platform is unknown and the planner requires only a C11 compiler |
| 1.2 | 2026-11-11 | Restricted PP-SWR-006 to the 0–1 s segment of the path. At long range, the lane model's cubic polynomial underestimates the curvature of short clothoids (6–11% at 72 m), so the planner cannot guarantee the requirement there. The vehicle follows the near segment, and the far segment is replanned each cycle |
| 1.3 | 2026-11-11 | Aligned PP-SWR-007 with R79. The flag must be set when a front tire starts to touch the marking. The old requirement measured against `T_flag` itself, so increasing `T_flag` could make it pass. Moved PP-SWR-008 to the performance targets and added PP-SWR-064 for warning lead time. Removed `delta_ay` and `T_flag` from Section 7. Updated the sources for PP-SWR-006 and `epsilon_ay` |
| 1.4 | 2026-11-11 | PP-SWR-051 applies only when free space on each side is ≥ `free_space_min`. The ODD permits a 2.5 m vehicle in a 2.5 m lane (PP-SWR-062), in which case a vehicle cannot maintain DLC ≥ 0. Report `lane_too_narrow` (PP-SWR-063) to make HWA unavailable. Requirements that refer to PP-SWR-051 (122, 123, 135 to 139, 148) inherit this condition |
| 1.5 | 2026-11-11 | Rewrote PP-SWR-055 and 056 using the clearance to a large vehicle and `gap_truck_min`. Defined alongside and clearance to a large vehicle. Added `gap_truck_min` to Section 7. Comparing clearance to the vehicle with clearance to the lane boundary could leave the path centered or shift it toward a large vehicle centered in the adjacent lane |
| 1.6 | 2026-11-12 | PP-SWR-032 and 041 separate the LKA and ELK phases. PP-SWR-036 and 037 reselect per 030 on cancellation. PP-SWR-047 distinguishes direct boundaries from boundaries outside the ego lane. Section 4 uses the magnitude of added a_y for completion. Clarified sources for 080, 083, 088, and 114 |
| 1.7 | 2026-11-12 | Added lane model view range to the definitions, PP-SWR-017 for accepting view ranges, PP-SWR-149 for view-range faults (F22), and PP-ASM-020. PP-SWR-151 caps the range at 126 m. PP-SWR-050 and 151 include the Q4 sweep. The planner must work across view ranges beyond the nominal 80 m |
| 1.8 | 2026-11-12 | Added F22 (f) to PP-SWR-042 and 149. A sustained loss of view range causes HWA to hand back control and then become available again |
| 1.9 | 2026-11-12 | PP-SWR-100 to 102 evaluate the path within the reported lane model view range, as defined under consecutive paths. Added PP-SWR-018 (`observed_horizon_s`) and PP-ASM-021. Beyond the view range the path is extrapolated. Enforcing continuity there can prevent tracking the lane when the view range is short (PP-PR-021, PP-TS-014). This affects all requirements that depend on PP-SWR-100 to 102 (031, 061, 120 to 128, 135 to 139, 148, 149), Interface Control Document 6.1, Software Detailed Design T4, and Software Qualification Test Specification 8.1 |
| 1.10 | 2026-11-12 | PP-SWR-018 now specifies only an upper bound. When the planner follows the previous reference line after a c0 jump (F02), it may conservatively report a shorter observed horizon than the lane model would indicate. The evaluator cannot observe when the planner follows the previous line. Changed after run 20261112-1240-matrix-M1-1bfd184 |
| 1.11 | 2026-11-12 | PP-ASM-021 specifies the controller type and a maximum lookahead of 0.6 s so the ADAS Functions module’s view-range thresholds can be verified |
| 1.12 | 2026-11-12 | Added PP-SWR-048 to treat FunctionRequests older than 45 ms as missing. Q3 at 60 ms exceeds the Interface Control Document’s maximum age. PP-PR-023 identified the missing planner response requirement |
| 1.13 | 2026-11-13 | Added PP-SWR-156 to treat out-of-range LongitudinalPlan messages as missing. B0 C2 failed because a plan near the upper float32 limit produced infinite Trajectory values (PP-PR-024). Verified by F23 |

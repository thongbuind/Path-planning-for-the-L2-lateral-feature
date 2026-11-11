# Software Architectural Design

| Field | Value |
|---|---|
| Document ID | `PP-SAD` |
| Version | 1.1 |
| Status | BL1 |
| Author | thongbui |
| Reviewer | thongbui |
| Last updated | 2026-11-10 |

## 1. Purpose and scope {#design-scope}

- **Purpose:** Describe how the path planner meets the Software Requirements Specification: architecture, execution cycle, component design, and calibration parameter catalog.
- **Scope:** Reference line, arbitration, HWA path, LKA and ELK intervention paths, termination conditions, input fault handling, and the interface with the longitudinal module.

## 2. References {#design-references}

| Document | Use |
|---|---|
| [Software Requirements Specification](report.html?doc=path-planner-software-requirements-specification&lang=en) | Requirements, performance targets, and calibration parameter limits |
| [Interface Control Document](report.html?doc=path-planner-interface-control-document&lang=en) | Schemas for all inputs and outputs |
| [Architecture Decision Records](report.html?doc=path-planner-architecture-decision-records&lang=en) | PP-ADRs: alternatives considered and rationale |
| [Software Detailed Design](report.html?doc=path-planner-software-detailed-design&lang=en) | Detailed algorithms (T1 … T11) |
| [ADAS Function Specification](report.html?doc=adas-function-specification&lang=en) | When HWA, LKA, and ELK are requested |
| [Software Qualification Test Specification](report.html?doc=path-planner-software-qualification-test-specification&lang=en) | Simulator, stubs, and test cases |
| Apollo (Baidu), trajectory stitching; Werling et al. (2010), Frenet | Path stitching and path planning coordinates |

## 3. Architecture {#planner-cycle}

### 3.1 Components {#design-components}

| Component | Responsibility | Input | Output |
|---|---|---|---|
| Input check | Check valid flag, counter, CRC, timeout, and age. Treat invalid messages as not received | All inputs | Checked inputs and validity flags |
| Latency compensation | Transform the lane model from capture time to t0 using ego-motion (PP-ADR-002) | LaneModel, EgoMotionQuery | Lane model at t0 |
| Reference line | Check boundary consistency, select reliable boundaries, and construct the lane center and boundaries (Section 4) | Lane model at t0, yaw rate, speed, previous path | Reference line and free space on each side |
| Arbitration | Select the function in control and the intervention phase (Section 5) | FunctionRequests, validity flags | `active_function`, `intervention_phase` |
| Path generation | Generate an HWA path (Section 6) or intervention path (Section 7) in Frenet coordinates | Reference line, vehicle state, LongitudinalPlan, ObjectList | Candidate path |
| Stitching and continuity | Stitch to the previous path and check PP-SWR-100 to 102 (Section 9) | Candidate path, previous path | Stitched path |
| Feasibility | Check a_y, jerk, steering angle, and steering rate against function limits; clip when exceeded (Section 9) | Stitched path, VehicleConfig | Final path, `lateral_limit_reached` |
| Output | Convert to `base_link`, sample 31 points, and publish | Final path, state | Trajectory, PathStatus, LateralLimits |

### 3.2 Cycle sequence {#planner-sequence}

A cycle starts at tick t0 every 25 ms. t_c is the computation time.

| # | Time | From → to | Contents | Requirement |
|---|---|---|---|---|
| 1 | t0 | Scheduler → Planner | Cycle tick | PP-SWR-010 |
| 2 | t0 | Input check → Planner | Latest checked message for each input; LongitudinalPlan from the previous cycle | PP-SWR-126 to 134 |
| 3 | t0 | Planner → Ego-motion | Query motion from the lane model capture timestamp to t0 | PP-SWR-012, 143 |
| 4 | t0 to t0 + t_c | Planner | Latency compensation, reference line, arbitration, path generation, stitching, feasibility | PP-SWR-030, 100 to 102, 110 to 117 |
| 5 | t0 + t_c | Planner → Lateral Controller | Trajectory (`header.stamp_us = t0`), PathStatus | PP-SWR-010, 011, 012 |
| 6 | t0 + t_c | Planner → ADAS Functions | PathStatus | PP-SWR-010 |
| 7 | t0 + t_c | Planner → Longitudinal module | LateralLimits | PP-SWR-150 |
| 8 | After t0 + t_c | Longitudinal module → Planner | LongitudinalPlan, used in the next cycle to avoid a loop within the same cycle | PP-SWR-153 |

**Deadline.** Finish publishing steps 5 to 7 before t0 + `t_budget`. If computation overruns the deadline, still publish and log the overrun. The receiver reads the path by its timestamp, so a late path still represents the correct time.

### 3.3 Latency chain {#latency-chain}

All latency values are assumptions (Software Requirements Specification Section 6).

| # | Segment | Worst case (ms) | Source | Compensation |
|---|---|---|---|---|
| 1 | Camera capture → Lane Model publication | 120 (PP-ASM-001) | Camera, Lane Model | Planner, using the capture timestamp |
| 2 | Lane Model publication → planner read | 50 (camera at 20 Hz) | Camera cadence | Planner, using the capture timestamp; transform between frames using ego-motion |
| 3 | Planner computation and publication | 5 (`t_budget`) | Planner | Lateral Controller, reads the path by its timestamp (PP-ADR-010) |
| 4 | Trajectory transmission | 1 (PP-ASM-007) | Pub/sub | Same as row 3 |
| 5 | Wait for controller cycle | 10 (100 Hz) | Controller cadence | Same as row 3 |
| 6 | Controller computation | ? | Lateral Controller | Same as row 3 |
| 7 | EPS actuation | 50 (PP-ASM-014) | EPS | Lateral Controller, selects the point on the path at current time plus actuation latency |
| 8 | Yaw rate: IMU → planner, in parallel | 5 + unknown filter latency (PP-ASM-003, 004) | CAN, filter | No compensation; planner tolerates up to 50 ms (PP-SWR-138) |
| 9 | FunctionRequests → planner, in parallel | 45 (PP-ASM-006) | Pub/sub, planner cadence | No compensation; respond within one cycle (PP-SWR-038) |

Worst-case total from camera to wheels (rows 1 to 7, excluding row 6): 236 ms. The planner compensates the first 170 ms; the Lateral Controller compensates the 66 ms after the planner (PP-ASM-017).

## 4. Reference line {#reference-line}

| Situation | Design | Related items |
|---|---|---|
| L1 and R1 are both reliable | The lane center is the mean of the two polynomials | PP-SWR-050 |
| One marking is lost | Offset the remaining marking by half the stored lane width | PP-SWR-123 |
| Both ego-lane markings are lost, but other reliable boundaries remain | Infer the lane center from L2, R2, and road edges. Add the stored offset to the lane center to each boundary and fuse the estimates by variance. Update stored offsets only when both ego-lane markings are reliable. Only HWA may steer using the inferred lane center | PP-SWR-047, 147, 148; PP-ADR-011; T2 |
| No reliable boundary remains | Follow the previous path transformed into the new `base_link` for up to `T_coast`, then set `path_valid = false` | PP-SWR-124; PP-ADR-009 |
| Boundary consistency check | Lane model does not publish a c0 jump flag (PP-ASM-009). Check each boundary at two time scales. Frame by frame: compare to the previous frame's boundary transformed by ego-motion; a difference above `k_jump`·σ indicates a jump or misidentified marking. Slow scale: check parallelism of the two boundaries (differences in c1 and c2) and width against the stored width. Discard an inconsistent boundary, anchor the lane center to the other boundary, and do not update the stored width. Accept a genuine change to the lane when both boundaries confirm it over `T_confirm` | PP-SWR-060, 121, 122; PP-ADR-006 |
| Lane widening (emergency lane, branch, or added lane) | The slow check detects the widening boundary; anchor the lane center to the stable boundary | PP-SWR-060 |
| c0 jump | Stitch to the previous path and rate-limit the center shift | PP-SWR-121 |
| Incorrect c2 at long range | Fuse camera c2, curvature r/v, and path history using weights | PP-SWR-125; T5 |
| Lane model switches lanes | Switch the reference line to the new lane and stitch the path | PP-SWR-061 |
| Insufficient free space | If free space on each side is < `free_space_min`, set `lane_too_narrow = true` | PP-SWR-063 |

### 4.1 Residual lane model noise {#design-noise}

Three layers use the planner's own path as a reference, without filtering the sensors again (PP-ADR-007):

| Layer | Design |
|---|---|
| Start from the previous path | The new path starts at the state from the previous cycle's path, so noise in one frame changes only the farther portion of the path |
| Rate-limit reference changes | The lane center followed by the path can shift by at most `ref_rate` |
| Penalize jerk | Select a path with low jerk so it does not follow small, rapid fluctuations |

The trade-off is slower response when the lane actually changes. The Software Qualification Test Specification measures both oscillation and lag at curve entry.

### 4.2 Path initial state {#design-initial-state}

- Trajectory stitching (PP-ADR-004): the new path starts from the corresponding point on the previous path. If the vehicle deviates from the previous path by more than `stitch_reset`, start from the measured state.
- When LKA or ELK starts, always use the measured state (PP-SWR-080). If the vehicle has deviated from the previous path beyond the tolerance in PP-SWR-080, do not stitch to the previous path (PP-SWR-031).
- The measured lateral state (d0, heading error, v_lat) is calculated by a function shared with the ADAS Functions module (PP-ADR-005).

## 5. Arbitration {#design-arbitration}

- Each cycle, select the highest-priority function in REQUEST: ELK > LKA > HWA. Treat OFF, UNAVAILABLE, FAULT, and STANDBY as no request (PP-SWR-030).
- The planner decides when to end the intervention without waiting for the ADAS Functions module (Section 7.1).
- Remember the function just marked COMPLETED. Accept a new intervention only after its state leaves REQUEST and then returns to it (PP-SWR-034, 041).
- If FunctionRequests times out, treat all three functions as OFF (PP-SWR-145).
- When the driver overrides, the ADAS Functions module cancels LKA and ELK and sets `driver_override` in the same message. For solid markings, LKA is requested before ELK, so both functions may be in REQUEST at once.

### 5.1 Arbitration state {#arbitration-states}

The state is `active_function`. Each cell gives the next state and planner action. "—" means no change or cannot occur.

| Event | In NONE | In HWA | In LKA | In ELK | Requirement |
|---|---|---|---|---|---|
| HWA enters REQUEST | → HWA; start the path from the vehicle state and recenter | — | Remain in LKA | Remain in ELK | PP-SWR-030, 052 |
| HWA leaves REQUEST | — | → NONE; `path_valid` remains true | Remain in LKA; switch to NONE when it ends | Remain in ELK; switch to NONE when it ends | PP-SWR-033, 042 |
| LKA enters REQUEST | → LKA if v_y is valid and the lane center is not inferred | Same as NONE; stitch the path | — | Remain in ELK | PP-SWR-030, 031, 047, 080, 144 |
| ELK enters REQUEST | → ELK if v_y is valid and the lane center is not inferred | Same as NONE; stitch the path | Same as NONE; stitch the path | — | PP-SWR-030, 031, 047, 144 |
| The intervening function leaves REQUEST, including during driver override | — | — | → HWA if HWA is in REQUEST, otherwise NONE; `path_valid` remains true | → LKA if LKA is in REQUEST; → HWA if only HWA is in REQUEST; otherwise NONE | PP-SWR-030, 036, 037 |
| Termination conditions hold for `T_end_hold` | — | — | COMPLETED, held until LKA leaves REQUEST; → HWA if HWA is in REQUEST, otherwise NONE | COMPLETED; → LKA if LKA is in REQUEST; → HWA if only HWA is in REQUEST; otherwise NONE | PP-SWR-032, 033, 041 |
| `driver_override` is set | The path follows the vehicle position | Remain in HWA; the path follows the vehicle position | Request cancelled: same as the "leaves REQUEST" row; the path follows the vehicle position | Same as LKA | PP-SWR-036, 037, 039 |
| `driver_override` is cleared | — | New HWA path from the vehicle position | Cannot occur | Cannot occur | PP-SWR-040 |
| Lane center can only be inferred from boundaries outside the ego lane | — | Remain in HWA | → HWA if HWA is in REQUEST, otherwise NONE | Same as LKA | PP-SWR-047 |
| VehicleStateEstimate is invalid | Do not start LKA or ELK | Remain in HWA; do not start LKA or ELK | Continue the intervention path until it ends | Same as LKA | PP-SWR-046, 144 |
| FunctionRequests times out | `path_valid = false` | → NONE; `path_valid = false` | Same as HWA | Same as HWA | PP-SWR-145 |
| Path is invalid: `T_coast` expires or IMU, speed, steering angle, or ego-motion is faulty | `path_valid = false` | → NONE; `path_valid = false` | Same as HWA | Same as HWA | PP-SWR-043, 124, 142, 143 |
| Inputs recover after the path was invalid | The path becomes valid again and starts from the actual vehicle state; → HWA if HWA is in REQUEST; LKA and ELK only on a new REQUEST | Cannot occur | Cannot occur | Cannot occur | PP-SWR-044, 045 |

## 6. HWA path {#design-hwa}

| Responsibility | Design | Related items |
|---|---|---|
| Track the lane center | Follow the reference line through the three layers in Section 4.1 | PP-SWR-050, 051 |
| Curve requiring more lateral acceleration than aysmax allows | The path is less curved than the road, with a_y ≥ aysmax − `epsilon_ay`. Set `lateral_limit_reached` using `delta_ay` and `T_flag`; send `v_max` to the longitudinal module to slow down before the curve | PP-SWR-005 to 008, 151 |
| Recenter on activation | A quintic segment of duration `T_recenter`, still in HWA | PP-SWR-052; targets 002, 053 |
| Offset the center near a large vehicle | Assign objects to lanes using the reference line. Start when TTC until drawing alongside is ≤ `ttc_offset_start`; return `t_offset_hold` after the rear of the large vehicle passes. If ObjectList is lost, return the offset to 0 | PP-SWR-055, 058, 140; target 059 |
| Offset magnitude | Formula immediately below (PP-ADR-008) | PP-SWR-051, 055, 056; target 057 |
| Another vehicle cuts into the lane | This is not ELK. The lateral module offsets the center using the same formula; the longitudinal module selects that vehicle as its target | PP-SWR-055, 056 |
| Narrow lane | Use the same formula. The offset falls to 0 as free space becomes small; report `lane_too_narrow` when free space is insufficient | PP-SWR-063 |

**Center offset for any lane width and vehicle width.**

- Free space on each side when centered: s = (W_lane − W_vehicle) / 2, where W_vehicle is `vehicle_width` from VehicleConfig.
- Clearance on each side: from the vehicle body to the nearest object on that side (adjacent-lane vehicle, barrier, or road edge). On an unoccupied side, use the reference line's lane boundary rather than the raw road edge so that lane widening does not pull the vehicle toward it.
- Offset limit: o_lim = max(0, min(`offset_max`, s − `dlc_offset_min`)).
- Offset: o = (right clearance − left clearance) / 2, clamped to [−o_lim, o_lim]. The sign of o always points toward the greater clearance (PP-SWR-056).

### 6.1 Interface with the longitudinal module {#acc-stub}

Lateral and longitudinal planning use separate modules that exchange constraints (PP-ADR-001). The Interface Control Document defines the schema; the [Software Qualification Test Specification](report.html?doc=path-planner-software-qualification-test-specification&lang=en#sim-acc) defines the longitudinal stub.

- The planner sends LateralLimits: `v_max` based on the maximum visible curvature and the distance to it, so the longitudinal module can slow the vehicle before a curve.
- The path uses v(t) and a(t) from the previous cycle's LongitudinalPlan. If missing or timed out, use the current speed held constant and zero acceleration; the path remains valid (PP-SWR-153 to 155).

## 7. LKA and ELK paths {#design-intervention}

| Aspect | LKA | ELK | Related items |
|---|---|---|---|
| Starting point | Measured state at activation (Section 4.2) | Same as LKA | PP-SWR-031, 080 |
| Duration | `T_lka`, selected based on TLC from the ADAS Functions module and a_y limits | `T_elk`, shorter than LKA | Targets 081, 082 |
| Target | Inside the lane, with DLC on the drift side ≥ `dlc_target_lka` | Inside the lane, without overshooting to the opposite side | PP-SWR-084, 085 |
| Boundary tightening | None | Tighten the boundary on the hazard side so the wheels do not cross that marking | PP-SWR-086 |
| Intentional lane change with an overtaking vehicle in the adjacent lane | — | Only if the ADAS Functions module requests it under strict conditions; the path returns the vehicle to its original lane. Do not start if the front tire is already more than 0.3 m beyond the marking | PP-SWR-089 |
| Maximum duration | 10 s | 10 s | PP-SWR-083 |
| Limits | a_y ≤ 3.0; added a_y ≤ 1.5 m/s²; jerk ≤ 5 m/s³ | a_y ≤ 4.0; added a_y ≤ 3.0 m/s²; jerk ≤ 10 m/s³ | PP-SWR-110 to 115 |

### 7.1 Intervention termination {#design-completion}

- Once the path duration has elapsed, the planner checks the termination conditions (Software Requirements Specification Section 4) and the deviation from the target. If the conditions hold continuously for `T_end_hold`, report COMPLETED (PP-SWR-032, 090).
- After COMPLETED, transition smoothly to the next function according to arbitration (PP-SWR-033). If no function remains, select NONE; the controller and EPS ramp down torque on their own.

## 8. Fault handling {#design-faults}

### 8.1 Lane model {#lane-faults}

| Fault | Handling | Related items |
|---|---|---|
| c0 and c1 noise up to nighttime levels | Three layers in Section 4.1 | PP-SWR-120 |
| c0 jump of 0.3–1 m | Check consistency, stitch the path, and rate-limit the center shift | PP-SWR-121 |
| Misidentified adjacent-lane marking | Check consistency and reject the wrong boundary | PP-SWR-122 |
| One marking is lost | Use the remaining marking and stored lane width | PP-SWR-123 |
| Both ego-lane markings are lost | If other reliable boundaries remain, infer the lane center from them. Otherwise, follow the previous path for up to `T_coast` | PP-SWR-124, 147, 148 |
| Incorrect c2 at long range | Fuse c2 with r/v and path history | PP-SWR-125 |
| Lane model latency | Compensate from the capture timestamp | PP-SWR-012, 131, 133 |

### 8.2 Invalid input {#design-invalid-input}

| Input | Handling | Related items |
|---|---|---|
| LaneModel | Treat as no reliable boundaries remaining | PP-SWR-124 |
| ObjectList | Return the HWA offset to 0. ELK continues (the ADAS Functions module assesses the adjacent lane) | PP-SWR-140, 141 |
| IMU, speed, steering angle, ego-motion | Latency compensation and path stitching are unavailable; set `path_valid = false` immediately | PP-SWR-142, 143 |
| VehicleStateEstimate | Do not start a new LKA or ELK intervention; continue one already in progress | PP-SWR-046, 144 |
| FunctionRequests | Treat all three functions as OFF | PP-SWR-145 |
| LongitudinalPlan | Hold current speed constant with zero acceleration | PP-SWR-154, 155 |
| VehicleConfig missing at startup | Do not publish Trajectory | PP-SWR-146 |

## 9. Limits, continuity, feasibility {#design-limits}

| Function | a_y | Added a_y | Jerk | Requirement |
|---|---|---|---|---|
| HWA | ≤ 2.5 m/s² | ≤ `ay_add_max_hwa` | ≤ 5 m/s³; target `jerk_target_hwa` | PP-SWR-001, 003; targets 002, 004 |
| LKA | ≤ 3.0 m/s² | ≤ 1.5 m/s² | ≤ 5 m/s³ | PP-SWR-110, 112, 114 |
| ELK | ≤ 4.0 m/s² | ≤ 3.0 m/s² | ≤ 10 m/s³ | PP-SWR-111, 113, 115 |

- **Feasibility.** Check a_y = v²·κ, jerk, `front_wheel_angle`, and steering wheel rate against VehicleConfig. If limits are exceeded, clip to within the limits and set `lateral_limit_reached` (PP-SWR-005 to 008, 116, 117).
- **Continuity.** Compare the new path with the previous one over the time interval both describe, after transforming the previous path into the new `base_link` using ego-motion. Do this during function transitions as well (PP-SWR-100 to 102).
- **Computation time.** Record it every cycle; the simulator assumes `t_budget` (PP-SWR-015; target 016).

## 10. Edge cases {#design-edge-cases}

Numbers follow the Edge cases section of the ADAS Function Specification.

| # | Situation | Planner action | Related items |
|---|---|---|---|
| 1a | HWA is active and ELK is requested | HWA → ELK → HWA, stitching at each transition | PP-SWR-030, 031, 033 |
| 1b | Another vehicle cuts into the lane | Keep the active function and offset the center. The longitudinal module maintains distance | PP-SWR-055, 056 |
| 2 | HWA enters a curve that requires more lateral acceleration than aysmax allows | Clip the path, set `lateral_limit_reached`, and send `v_max`. Use ELK limits if ELK is requested | PP-SWR-005 to 008, 151 |
| 3 | Driver overrides HWA | The path follows the vehicle position; plan a new path when the driver releases the override | PP-SWR-039, 040 |
| 4 | ELK during an intentional lane change | Return to the original lane within ELK limits, only on a request made under strict conditions | PP-SWR-089, 111 |
| 5 | Request cancelled due to turn indicator | Stop the intervention path and transition according to arbitration | PP-SWR-036, 037 |
| 6 | Repeated drift from side to side | Generate a new intervention path for each new request, with the same limits | PP-SWR-034, 035 |
| 7 | Lane model switches lanes | Switch the reference line and stitch the path | PP-SWR-061 |
| 8 | c0 jump | Stitch the path and rate-limit the center shift | PP-SWR-121 |
| 11 | Both ego-lane markings lost during intervention | If other reliable boundaries remain, LKA or ELK transitions to HWA or NONE. If no boundaries remain, follow the previous path for up to `T_coast` | PP-SWR-047, 124 |
| 13b | Stop-and-go traffic at low speed | HWA continues; at 8 m/s the 3 s path covers only 24 m | PP-SWR-054 |
| 14 | FunctionRequests times out | Treat all three functions as OFF | PP-SWR-145 |
| 16 | Driver makes a sudden evasive maneuver; LKA and ELK are suppressed | HWA treats it as driver override | PP-SWR-039 |

## 11. Calibration parameters {#design-calibration}

One calibration set for all vehicles. Initial values are starting points. The Software Qualification Test Specification sweeps the ranges and selects the best set. Limits come from Software Requirements Specification Section 7 and the requirements.

| Parameter | Unit | Initial value | Sweep range | Limit | Affected items |
|---|---|---|---|---|---|
| `conf_ego` | — | 0.6 | 0.4–0.8 | 0–1 | PP-SWR-123, 124 |
| `conf_inferred` | — | 0.8 | 0.7–0.95 | > `conf_ego` | PP-SWR-047, 147, 148 |
| `T_coast` | s | 1.0 | 0.5–1.0 | ≤ 1 s | PP-SWR-124 |
| `free_space_min` | m | 0.1 | 0–0.3 | ≥ 0 | PP-SWR-063 |
| `delta_ay` | m/s² | 0.2 | 0.1–0.4 | ≥ 0 | PP-SWR-007, 008 |
| `epsilon_ay` | m/s² | 0.2 | 0–0.5 | 0–2.5 | PP-SWR-006 |
| `T_flag` | s | 0.2 | 0.15–0.5 | > 0 | PP-SWR-007, 008 |
| `v_lat_end` | m/s | 0.1 | 0.05–0.2 | ≥ 0 | PP-SWR-032, 090 |
| `heading_end` | ° | 0.5 | 0.3–1.0 | ≥ 0 | PP-SWR-032, 090 |
| `ay_add_end` | m/s² | 0.2 | 0.1–0.3 | ≥ 0 | PP-SWR-032, 090 |
| `T_end_hold` | s | 0.5 | 0.3–1.0 | ≥ 0 | PP-SWR-032, 090 |
| `T_lka` | s | 3.0 | 2.0–4.0 | Limits in PP-SWR-110, 112, 114 | Targets 081, 087 |
| `T_elk` | s | 2.0 | 1.0–3.0 | Limits in PP-SWR-111, 113, 115 | Target 082 |
| `dlc_target_lka` | m | 0.5 | 0–0.8 | ≥ 0 (PP-SWR-084) | Targets 081, 087 |
| `T_recenter` | s | 3.5 | 2.5–5.0 | Limits in PP-SWR-001, 003 | Targets 002, 053 |
| `ay_add_max_hwa` | m/s² | 0.5 | 0.3–1.0 | ≤ 2.5 (PP-SWR-001) | Targets 002, 053, 059 |
| `jerk_target_hwa` | m/s³ | 2.5 | 1.5–5.0 | ≤ 5 (PP-SWR-003) | Target 004 |
| `ref_rate` | m/s | 0.1 | 0.05–0.3 | ≥ 0 | Target 050; PP-SWR-120 |
| `stitch_reset` | m | 0.2 | 0.1–0.4 | ≥ 0 | Target 050; PP-SWR-100 |
| `k_jump` | σ | 3 | 2–5 | ≥ 0 | PP-SWR-121, 122 |
| `T_confirm` | s | 1.0 | 0.5–2.0 | ≥ 0 | PP-SWR-060, 061 |
| `offset_max` | m | 0.3 | 0–0.5 | ≥ 0 | PP-SWR-055; target 057 |
| `dlc_offset_min` | m | 0.3 | 0–0.5 | ≥ 0 (PP-SWR-051) | Target 057 |
| `ttc_offset_start` | s | 3.0 | 2.0–4.0 | ≥ 0 | PP-SWR-058 |
| `t_offset_hold` | s | 1.0 | 0–2.0 | ≥ 0 | Target 059 |
| `t_budget` | ms | 5 | — | < 25 (cycle period) | Target 016 |

Algorithm-level calibration parameters (stored boundaries, path generation weights, and curvature filtering) are in Software Detailed Design Section 15.

## Appendix A. Analysis {#design-appendix}

**A.1 Latency compensation error at 25 m/s** (PP-ADR-002, PP-SWR-012).

| Error source | Lateral reference error |
|---|---|
| No compensation on a curve with R = 250 m and 100 ms latency | 0.25 m at 25 m, 0.5 m at 50 m |
| Nominal latency compensation with ±20 ms jitter | 0.05 m at 25 m |
| Clock offset of ±10 ms before first synchronization | 0.025 m at 25 m |
| After gPTP synchronization, ±50 µs | Negligible |

**A.2 Maximum age of 250 ms** (PP-ADR-003, PP-SWR-131). Ego-motion retains 0.5 s of history, enough to transform by 250 ms. The worst-case bias of 1 °/s causes a heading error of 0.0044 rad after 250 ms, or 0.11 m at 25 m; a 0.3 °/s bias gives only 0.03 m. An object velocity error of 0.3 m/s over 250 ms gives 0.075 m.

**A.3 Yaw-rate filter latency of 50 ms** (PP-SWR-138). The heading error during camera latency compensation corresponds to about 1 cm at 25 m. Curvature error on entry to a clothoid with R = 250 m at 90 km/h is about 0.00007 1/m, below the PP-SWR-102 limit of 0.0003 1/m.

**A.4 Dead reckoning without boundaries** (PP-ADR-009, `T_coast`). At 25 m/s, yaw-rate bias 0.3 °/s, v_y noise σ = 0.05 m/s:

| Time | Deviation due to bias | Deviation due to v_y noise |
|---|---|---|
| 0.5 s | 0.02 m | 0.03 m |
| 1 s | 0.06 m | 0.05 m |
| 2 s | 0.25 m | 0.10 m |
| 3 s | 0.56 m | 0.15 m |

Bias of 1 °/s (raw Bosch SMI230 sensor offset): 0.22 m after 1 s, 0.87 m after 2 s.

**A.5 Recentering.** For a quintic from offset d0 to 0, maximum a_y ≈ 5.77·d0/T². With d0 = 0.5 m and added a_y of 0.5 m/s², T ≥ 2.4 s.

**A.6 LKA duration**, using a quintic from activation (TLC = 1.0 s) to lane center. Cells give maximum a_y [m/s²] / maximum jerk / 0.5 s average jerk [m/s³]:

| v_lat at activation | T = 2 s | T = 3 s | T = 4 s |
|---|---|---|---|
| 0.2 m/s | 1.26 / 6.3 / 2.8 | 0.65 / 2.1 / 1.2 | 0.41 / 1.0 / 0.7 |
| 0.4 m/s | 1.36 / 6.6 / 2.8 | 0.78 / 2.5 / 1.5 | 0.54 / 1.3 / 0.9 |
| 0.6 m/s | 1.47 / 6.9 / 2.9 | 0.91 / 2.8 / 1.7 | 0.66 / 1.5 / 1.1 |

T = 2 s exceeds the 5 m/s³ jerk limit. T = 4 s brings the vehicle closer to the marking (0.10–0.16 m of clearance versus 0.13–0.28 m at T = 3 s). This is the basis for the initial value `T_lka` = 3 s.

## Revision history {#revision-history}

| Version | Date | Changes |
|---|---|---|
| 0.5 | 2026-11-09 | Section 6.1: detailed ACC stub design. Added ISO 15622:2018 as a reference |
| 0.6 | 2026-11-10 | Lane Model publishes three lanes and separate road edges; infer the lane center from adjacent-lane markings and road edges (PP-ADR-011); calculate offset using vehicle width |
| 1.0 | 2026-11-10 | Restructured as Software Architecture and Design, baseline BL1. Added components, the calibration parameter table, and the offset formula for any lane and vehicle width. Finalized all arbitration state cells; moved schemas to the Interface Control Document and the ACC stub to the Software Qualification Test Specification; consolidated calculations in Appendix A; removed status labels and open items |
| 1.1 | 2026-11-10 | Cycle sequence row 5: also publish PathStatus to the Lateral Controller, consistent with Interface Control Document 1.1 |

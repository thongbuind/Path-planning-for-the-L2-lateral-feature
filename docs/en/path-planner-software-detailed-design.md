# Software Detailed Design

| Field | Value |
|---|---|
| Document ID | `PP-SDD` |
| Version | 1.0 |
| Status | BL1 |
| Author | thongbui |
| Reviewer | thongbui |
| Last updated | 2026-11-10 |

## 1. Purpose and scope {#dd-scope}

- **Purpose.** Specify the algorithm for each path planner component in enough detail to implement it.
- **Scope.** The eleven units T1 through T11, code structure, and algorithm-level calibration parameters.
- **Out of scope.** Architecture and decisions (Software Architectural Design, Architecture Decision Records); simulator and stub code (Software Qualification Test Specification).

## 2. References {#dd-references}

| Document | Use |
|---|---|
| [Software Architectural Design](report.html?doc=path-planner-software-architectural-design&lang=en) | Components, cycle, and design-level calibration parameters |
| [Software Requirements Specification](report.html?doc=path-planner-software-requirements-specification&lang=en) | Requirements, definitions, and calibration parameter limits |
| [Interface Control Document](report.html?doc=path-planner-interface-control-document&lang=en) | Messages and fields |
| [Software Qualification Test Specification](report.html?doc=path-planner-software-qualification-test-specification&lang=en) | Selection of the path planning technique and calibration |
| Werling, Ziegler, Kammel, Thrun (2010), ICRA | Quintic polynomials, Frenet sampling, and Frenet-to-Cartesian conversion |

## 3. Units and code structure {#dd-units}

Notation: s is the longitudinal coordinate along the reference line, d is the lateral offset (positive to the left), t ∈ [0, 3] s is time along the path, and v(t) comes from LongitudinalPlan.

| Unit | Component in the Software Architectural Design | Module (`src/planner/`) |
|---|---|---|
| T1 Latency compensation | Input check, Latency compensation | `input_check.py`, `latency.py` |
| T2 Reference line | Reference line | `reference_line.py` |
| T3 Reference shaping | Reference line (noise mitigation layer) | `reference_line.py` |
| T4 Stitching and continuity | Stitching and continuity | `stitching.py` |
| T5 Curvature fusion | Reference line | `curvature.py` |
| T6 Lateral state | Path generation (initial state) | `src/common/lateral_state.py`, shared with the ADAS Functions module |
| T7 Path generation | Path generation | `generators/quintic.py`, `generators/frenet_sampling.py`, `generators/qp.py` |
| T8 Offset | Path generation (HWA) | `offset.py` |
| T9 Arbitration | Arbitration | `arbitration.py` |
| T10 Feasibility | Feasibility | `feasibility.py` |
| T11 Output | Output | `output.py` |

- Message types are defined once in `src/interfaces/` per the Interface Control Document.
- All calibration parameters are in one file, `config/calibration.yaml`. At startup, the planner checks that each value is within the limits in Software Requirements Specification Section 7. If any value is out of range, the planner does not publish Trajectory, as when VehicleConfig is missing.
- The planner does not import from the simulator or test code.

## 4. T1 Latency compensation {#dd-t1}

| Step | Action |
|---|---|
| 1 | Input check: discard messages with an invalid CRC or repeated counter; record a loss when the counter skips; treat `valid = false` as not received. Input is invalid if it exceeds the timeout, age > 250 ms, or its timestamp is > 10 ms in the future. Log age > 170 ms (PP-SWR-131 to 134) |
| 2 | Take the latest LaneModel with timestamp t_c. Query ego-motion from t_c to t0. If invalid, set `path_valid = false` (PP-SWR-143) |
| 3 | For each marking and road edge, sample y(x) every 1 m within the visible range. Transform the samples to `base_link` at t0 using p_new = R(−Δψ)·(p_old − [Δx, Δy]); refit a cubic polynomial by least squares; shift the visible range by Δx |
| 4 | Between camera frames, repeat steps 2–3 with the latest frame. Do not carry over the polynomial transformed in the previous cycle (PP-SWR-128) |
| 5 | On receipt, shift the IMU timestamp back by `imu_filter_delay`. Measure this value once on the vehicle: sweep 0–200 ms and take the delay that maximizes the cross-correlation between raw and filtered yaw rate |

## 5. T2 Reference line {#dd-t2}

**State retained across cycles:** stored lane width w_mem and, for each boundary k ∈ {L2, L1, R1, R2, left road edge, right road edge}, the offset o_k from the boundary to the ego-lane center and its uncertainty σ_o,k.

| Step | Action |
|---|---|
| 1 | Check each boundary for consistency (table below). A boundary is reliable if it satisfies the conditions in Software Requirements Specification Section 4 and is consistent |
| 2 | If both L1 and R1 are reliable, lane center = (y_L1 + y_R1) / 2. Update w_mem and all o_k using a low-pass filter with time constant `tau_mem`, only when the measured width is within 2.5–5.5 m; reset σ_o,k = `sigma_mem0` |
| 3 | If only one of L1 and R1 is reliable, lane center = that boundary ∓ w_mem/2. Do not update the stored values |
| 4 | If neither ego-lane marking is reliable but other reliable boundaries remain, each boundary supplies a candidate center y_k − o_k. Fuse the coefficients using weights 1 / (σ_c0,k² + σ_o,k²). Set the inferred-center flag (PP-SWR-047). Increase σ_o,k² by `q_mem` per second |
| 5 | If no reliable boundary remains, use the previous path transformed by ego-motion for up to `T_coast`, then set `path_valid = false` |
| 6 | The reference line's lane boundaries are the lane center ± w/2, used for clearance (T8) and the corridor (T7). Free space on each side = (w − `vehicle_width`) / 2; if below `free_space_min`, set `lane_too_narrow = true` |

**Consistency checks**

| Time scale | Check | Inconsistent when |
|---|---|---|
| Frame by frame | Compare the new boundary at x = 0 with the previous frame's boundary transformed by ego-motion | c0 difference > `k_jump`·√(σ_new² + σ_old²) |
| Slow: parallelism | Difference between the c1 values of the two ego-lane boundaries, low-pass filtered with `tau_mem` | Difference > `parallel_max`; reject the boundary whose heading changed relative to its own history |
| Slow: width | Measured lane width against w_mem | Difference > `width_dev_max` for longer than `T_confirm` |

**Accepting genuine changes to the lane**

| Change | Condition | Handling |
|---|---|---|
| Lane change | Both boundaries jump in the same direction by approximately w_mem, or the lane model sets `lane_change`; confirm within one frame | Reassign L1 and R1 to the new lane; shift the reference line by one lane width; T4 maintains path continuity (PP-SWR-061) |
| Lane narrowing | One boundary moves inward continuously and remains parallel to its own history for `T_confirm` | Accept the new width; shift the center accordingly, subject to the T3 rate limit |
| Lane widening | One boundary moves outward | Do not accept it: anchor the center using the stable boundary and w_mem (PP-SWR-060). Reset w_mem only when both boundaries yield a newly measured width and neither boundary is still moving |

## 6. T3 Reference shaping {#dd-t3}

- Keep a smoothed reference line r(s) and transform it from the previous cycle into the new `base_link` using ego-motion.
- At each s sample spaced 1 m apart: r(s) ← r(s) + clamp(r_raw(s) − r(s), ±`ref_rate`·Δt).
- When T2 recognizes a lane change, shift r(s) by exactly the jump before applying the rate limit so the path is not pulled along by the jump.
- The path follows r(s); the T7 jerk weight filters the remaining noise (PP-SWR-120).

## 7. T4 Stitching and continuity {#dd-t4}

| Step | Action |
|---|---|
| 1 | Transform the previous cycle's path into `base_link` at t0 using ego-motion |
| 2 | Initial state (d, ḋ, d̈) = the previous path's state at t0, expressed relative to the new reference line. If the measured state (T6) differs by more than `stitch_reset`, use it instead. Always use the measured state when LKA or ELK starts (PP-SWR-080) |
| 3 | T7 generates a candidate path from the initial state |
| 4 | Project to satisfy the continuity limits. Find the maximum difference between the candidate and previous paths over their shared time interval for lateral offset Δd, heading Δψ, and curvature Δκ. λ = min(1, `cont_margin`·0.05/Δd, `cont_margin`·0.005/Δψ, `cont_margin`·0.0003/Δκ). Published path = previous path + λ·(candidate path − previous path) |
| 5 | Skip step 4 when PP-SWR-031 permits it (LKA or ELK starts after the vehicle has deviated) and when the previous path is invalid |

- A convex combination of two paths that both satisfy a_y and jerk limits (linear constraints on d̈ and d⃛) still satisfies the limits.
- c0 jump: T2 rejects the jumping boundary so the reference line does not jump. If the change is genuine, step 4 moves the path to the new position over multiple cycles (PP-SWR-121).

## 8. T5 Curvature fusion {#dd-t5}

- Estimate the lane center curvature κ(s) at points spaced 2 m apart within the visible range.
- Each point uses a one-dimensional Kalman filter. Prior: κ(s) from the previous cycle, shifted by distance traveled, with `q_kappa`·Δs added to the variance.
- Camera measurement: κ_cam = 2·c2 + 6·c3·x, variance 4·σ_c2² + 36·x²·σ_c3².
- Vehicle measurement at s = 0: κ_r = r / v, variance (`sigma_r` / v)²; use only at v > 5 m/s.
- If a measurement differs from the prior by more than `k_jump`·σ, reduce its weight by a factor of 10 instead of discarding it so the planner can still follow genuine curves (PP-SWR-125).

## 9. T6 Lateral state {#dd-t6}

A function shared with the ADAS Functions module (PP-ADR-005). Inputs: lane model at t0, v_y, r, v, and VehicleConfig.

| Quantity | Formula |
|---|---|
| d0 | −c0 of the lane center (d0 = 0 when the vehicle is at the lane center) |
| Heading error relative to the lane | −atan(c1 of the lane center) |
| v_lat relative to the lane center | v_y + r·x_f − v·y_c'(x_f), as in ADAS Function Specification Section 5 |
| DLC and TLC on both sides, and uncertainty | As in ADAS Function Specification Section 5 |

## 10. T7 Path generation {#dd-t7}

**Common interface** for all techniques: `generate(initial state, reference line, target d, corridor, limits, v(t)) → d(t)` on a 0.1 s grid spanning 0–3 s. The corridor is [right boundary + `vehicle_width`/2, left boundary − `vehicle_width`/2]. ELK tightens the boundary on the hazard side so the wheels do not cross that marking.

| Function | Target d | Duration |
|---|---|---|
| HWA lane keeping | T8 offset (0 when no large vehicle is present) | `T_hwa` |
| HWA recentering | 0 | `T_recenter` |
| LKA | Point at which DLC on the drift side = `dlc_target_lka` | `T_lka`, shortened when TLC is small |
| ELK | Within the lane, at least `dlc_target_lka` from the boundary on the hazard side | `T_elk` |

**Three candidate techniques** (assignment: select one and give reasons for rejecting at least one alternative; select per Software Qualification Test Specification Section 9):

| Technique | Algorithm | Calibration |
|---|---|---|
| A. Duration-based quintic | Use a fifth-degree d(t) from the initial state to (target d, 0, 0) over T. If a limit is exceeded, increase T in 0.25 s steps up to `T_max`. If a limit is still exceeded, pass the path to T10 for clipping and set the flag | `T_max` |
| B. Frenet sampling | Generate quintics with final d within target d ± `d_sample_span` in steps of `d_sample_step`, with T from `T_set`. Discard paths that exceed limits or leave the corridor. Select the path minimizing J = `w_jerk`·∫d⃛² + `w_time`·T + `w_dev`·(final d − target d)² + `w_cons`·∫(d − d_old)² | `d_sample_span`, `d_sample_step`, `T_set`, `w_jerk`, `w_time`, `w_dev`, `w_cons` |
| C. QP | Decision variables d_k at 31 points. Minimize Σ `w_jerk`·(Δ³d_k)² + `w_dev`·(d_k − target d)² subject to a fixed initial state, d_k inside the corridor, and absolute values of added a_y and jerk within the function limits (linearized using v(t)). If there is no solution, relax the corridor, then pass to T10 | `w_jerk`, `w_dev` |

All techniques share T2 through T6 and T8 through T11. Only T7 varies, allowing comparison under identical conditions in the Software Qualification Test Specification.

## 11. T8 Offset {#dd-t8}

| Step | Action |
|---|---|
| 1 | Assign objects to lanes using the reference line's boundaries. A large vehicle has width ≥ 2.3 m (Software Requirements Specification Section 4) |
| 2 | Start when TTC until drawing alongside the large vehicle is ≤ `ttc_offset_start`. End `t_offset_hold` after the large vehicle's rear has passed the ego vehicle's front |
| 3 | Clearance on each side: from the vehicle body (± `vehicle_width`/2 about the lane center) to the nearest edge of an object on that side within the alongside window. On an unoccupied side, use the reference line's lane boundary |
| 4 | s = (w − `vehicle_width`) / 2. o_lim = max(0, min(`offset_max`, s − `dlc_offset_min`)) |
| 5 | o = (right clearance − left clearance) / 2, clamped to [−o_lim, o_lim]; change o by at most `ref_rate` per second |
| 6 | If ObjectList is invalid, return o to 0 at the same rate (PP-SWR-140) |

## 12. T9 Arbitration {#dd-t9}

State retained across cycles: `active_function`, `intervention_phase`, COMPLETED flags for LKA and ELK (held until the function leaves REQUEST), previous cycle state, and the invalid path flag.

| Step | Action |
|---|---|
| 1 | If FunctionRequests times out, treat all three functions as OFF |
| 2 | Clear the COMPLETED flag for any function that has left REQUEST |
| 3 | Candidates are functions in REQUEST without a COMPLETED flag. LKA and ELK also require valid v_y, a lane center that is not inferred, and a new REQUEST after input recovery. Exception: an intervention in progress continues if only v_y is invalid (PP-SWR-046) |
| 4 | Select the highest-priority candidate: ELK > LKA > HWA. If there is none, select NONE |
| 5 | If an ongoing intervention meets the end conditions for `T_end_hold`, set it to COMPLETED, set its flag, and select again using steps 3–4 |
| 6 | If `path_valid = false`, set `active_function = NONE` |

The result matches the arbitration state table in Software Architectural Design Section 5.1. Unit tests verify each cell of that table.

## 13. T10 Feasibility and limits {#dd-t10}

| Step | Action |
|---|---|
| 1 | Across the 31 points: a_y = v²·κ; added a_y = a_y − v²·κ_ref; jerk = time derivative of a_y, averaged over 0.5 s; `front_wheel_angle` = atan(`wheelbase`·κ); steering wheel rate = `steering_ratio` × rate of change of wheel angle |
| 2 | If the active function or VehicleConfig limits are exceeded, clip κ to the limit and reintegrate d(t). Keep a_y ≥ aysmax − `epsilon_ay` when the required a_y exceeds aysmax (PP-SWR-006) |
| 3 | Set `lateral_limit_reached` when the maximum required a_y within the visible range is > aysmax + `delta_ay`; clear it when < aysmax − `delta_ay`. The condition must hold on consecutive cycles for `T_flag` / 2 |
| 4 | LateralLimits: κ_max is the greatest absolute value of κ(s) from T5 within the visible range; `v_max` = √(function's a_y limit / κ_max); `distance` = s at κ_max |

## 14. T11 Output {#dd-t11}

- Sample at t_k = 0.1·k, k = 0…30; obtain s(t) by integrating v(t).
- Convert (s, d) to (x, y, yaw, κ) in `base_link` using the Frenet-to-Cartesian formulas from Werling (2010).
- `heading_rate` = v·κ; `lateral_velocity` = ḋ; `front_wheel_angle` from T10; `rear_wheel_angle` = 0.
- Set `header.stamp_us` = t0 and increment `counter` by 1.
- Publish Trajectory, PathStatus, and LateralLimits; record computation time and log an overrun if it exceeds `t_budget`.

## 15. Algorithm-level calibration parameters {#dd-calibration}

Supplement to Software Architectural Design Section 11; use the same sweep method (Software Qualification Test Specification, P1).

| Parameter | Unit | Initial value | Sweep range | Unit ID |
|---|---|---|---|---|
| `imu_filter_delay` | ms | 0 | Measure on the vehicle | T1 |
| `tau_mem` | s | 2.0 | 0.5–5.0 | T2 |
| `sigma_mem0` | m | 0.05 | 0.03–0.1 | T2 |
| `q_mem` | m²/s | 0.001 | 0.0002–0.005 | T2 |
| `parallel_max` | rad | 0.008 | 0.005–0.015 | T2 |
| `width_dev_max` | m | 0.3 | 0.2–0.5 | T2 |
| `cont_margin` | — | 0.9 | 0.7–1.0 | T4 |
| `q_kappa` | 1/m³ | 1·10⁻⁹ | 1·10⁻¹⁰–1·10⁻⁸ | T5 |
| `sigma_r` | rad/s | 0.002 | 0.001–0.005 | T5 |
| `T_hwa` | s | 3.0 | 2.0–4.0 | T7 |
| `T_max` | s | 5.0 | 4.0–8.0 | T7 |
| `d_sample_span`, `d_sample_step` | m | 0.3; 0.05 | 0.2–0.5; 0.025–0.1 | T7 B |
| `T_set` | s | 1.5 to 4.0, in steps of 0.5 | — | T7 B |
| `w_jerk`, `w_time`, `w_dev`, `w_cons` | — | 1; 0.1; 1; 1 | 0.1–10 per weight | T7 B, C |

## Revision history {#revision-history}

| Version | Date | Changes |
|---|---|---|
| 0.3 | 2026-11-10 | Notes on T1 through T8 and a table of candidate techniques |
| 1.0 | 2026-11-10 | Rewritten as the Software Detailed Design, baseline BL1: algorithms for 11 units, code structure, and algorithm-level calibration parameters |

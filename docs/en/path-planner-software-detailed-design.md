# Software Detailed Design

| Field | Value |
|---|---|
| Document ID | `PP-SDD` |
| Version | 1.7 |
| Status | BL1 |
| Author | thongbui |
| Reviewer | thongbui |
| Last updated | 2026-11-12 |

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

| Unit | Component in the Software Architectural Design | Module (`planner/src/`) |
|---|---|---|
| T1 Latency compensation | Input check, Latency compensation | `input_check.c`, `latency.c` |
| T2 Reference line | Reference line | `reference_line.c` |
| T3 Reference shaping | Reference line (noise mitigation layer) | `reference_line.c` |
| T4 Stitching and continuity | Stitching and continuity | `stitching.c` |
| T5 Curvature fusion | Reference line | `curvature.c` |
| T6 Lateral state | Path generation (initial state) | `lateral_state.c`, internal to the planner (PP-ADR-014) |
| T7 Path generation | Path generation | `generators/quintic.c`, `generators/qp.c`, `intervention.c` |
| T8 Offset | Path generation (HWA) | `offset.c` |
| T9 Arbitration | Arbitration | `arbitration.c` |
| T10 Feasibility | Feasibility | `feasibility.c` |
| T11 Output | Output | `output.c` |

- C11 with a subset of MISRA C:2012 (PP-ADR-013). The caller supplies memory for the state. The planner uses no dynamic allocation, file reads, or global variables.
- Message types come from the generated C headers in `interfaces/c/`, per the Interface Control Document. The call contract is in `interfaces/c/pp_planner.h`.
- All calibration parameters are in `planner/calibration/calibration.yaml`. The build generates a constant C struct from this file. At `pp_init`, the planner checks each value against the limits in Software Requirements Specification Section 7. Out-of-range calibration blocks publication of Trajectory, as does a missing VehicleConfig.
- The planner uses only `interfaces/c/` and has no calls into the simulator or test code.
- Shared numerical routines (cubic polynomial fitting and 4×4 systems) are in `pp_math.c`. The planner computes in double precision. Only the interface structs use float32.

## 4. T1 Latency compensation {#dd-t1}

| Step | Action |
|---|---|
| 1 | Input check: discard messages with an invalid CRC or repeated counter; record a loss when the counter skips; treat `valid = false` as not received. Input is invalid if it exceeds the timeout, age > 250 ms, or its timestamp is > 10 ms in the future. Log age > 170 ms (PP-SWR-131 to 134) |
| 2 | Take the latest LaneModel with timestamp t_c. Query ego-motion from t_c to t0. If invalid, set `path_valid = false` (PP-SWR-143) |
| 3 | For each marking and road edge, sample y(x) every 1 m within the visible range. Transform the samples to `base_link` at t0 using p_new = R(−Δψ)·(p_old − [Δx, Δy]). Refit a degree-3 polynomial by least squares and shift the visible range by Δx |
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
| 5 | If no reliable boundary remains, including when the lane model is invalid, follow the previous reference line transformed by ego-motion for up to `T_coast`. Stitch to the previous path through T4. Then set `path_valid = false` |
| 6 | The reference line's lane boundaries are the lane center ± w/2, used for clearance (T8) and the corridor (T7). Free space on each side = (w − `vehicle_width`) / 2; if below `free_space_min`, set `lane_too_narrow = true` |

**Consistency checks**

| Time scale | Check | Inconsistent when |
|---|---|---|
| Frame by frame | At x = 0, compare the new boundary with its stored value, transformed by ego-motion each cycle | c0 difference > `k_jump`·√(σ_new² + σ_old²) |
| Slow: parallelism | Difference between the c1 values of the two ego-lane boundaries, low-pass filtered with `tau_mem` | Difference > `parallel_max`; reject the boundary whose heading changed relative to its own history |
| Slow: width | Measured lane width against w_mem | Difference > `width_dev_max` for longer than `T_confirm` |

- Reject inconsistent boundaries and retain the stored value. The new position becomes a candidate. Accept it as a genuine change once it remains consistent with itself for `T_confirm`. Keep the previous position for another `T_confirm` and accept an immediate return to it during that period.

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
| 1 | Transform the previous cycle's path into `base_link` at t0 using ego-motion. A path older than the Trajectory timeout (75 ms) is invalid |
| 2 | Initial state (d, ḋ, d̈) = the previous path's state at t0, expressed relative to the new reference line. If the measured state (T6) differs by more than `stitch_reset`, use it instead. Always use the measured state when LKA or ELK starts (PP-SWR-080) |
| 3 | T7 generates a candidate path from the initial state |
| 4 | Project to satisfy the continuity limits. Find the maximum difference between the candidate and previous paths over their shared time interval for lateral offset Δd, heading Δψ, and curvature Δκ. λ = min(1, `cont_margin`·0.05/Δd, `cont_margin`·0.005/Δψ, `cont_margin`·0.0003/Δκ). Published path = previous path + λ·(candidate path − previous path) |
| 5 | Skip step 4 when PP-SWR-031 permits it (LKA or ELK starts after the vehicle has deviated) and when the previous path is invalid |

- Step 2 finds the previous path point at t0 with Hermite interpolation using the tangent directions. Chord interpolation cuts inside the curve by κ·L²·f(1−f)/2 and pulls the initial point inward each cycle.
- Step 4 blends the 31 Cartesian points using the measurement convention in PP-SWR-100 to 102.
- A convex combination of two paths that both satisfy a_y and jerk limits (linear constraints on d̈ and d⃛) still satisfies the limits.
- c0 jump: T2 rejects the jumping boundary so the reference line does not jump. If the change is genuine, step 4 moves the path to the new position over multiple cycles (PP-SWR-121).

## 8. T5 Curvature fusion {#dd-t5}

- Estimate the lane center curvature κ(s) at points spaced 2 m apart within the visible range.
- Each point uses a one-dimensional Kalman filter. Prior: κ(s) from the previous cycle, shifted by distance traveled, with `q_kappa`·Δs added to the variance.
- The camera measures κ_cam = 2·c2 + 6·c3·x with variance 4·σ_c2² + 36·x²·σ_c3², floored at `sigma_kappa_min`² because the lane model can report zero variance for c2 and c3. Update only on a new frame.
- Vehicle measurement at s = 0: κ_r = r / v, variance (`sigma_r` / v)²; use only at v > 5 m/s.
- If a measurement differs from the prior by more than `k_jump`·σ, reduce its weight by a factor of 10 instead of discarding it so the planner can still follow genuine curves (PP-SWR-125).
- Fit κ(s) over the observed segment to κ = a + b·x, using inverse variance as the weight and s ≈ x. Set c2 = a/2 and c3 = b/6 in the reference line.

## 9. T6 Lateral state {#dd-t6}

The planner computes the lateral state independently of the ADAS Functions module (PP-ADR-014). It uses the lane model at t0, v_y, r, v, and VehicleConfig.

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
| HWA recentering | 0 | `T_recenter`. Start when HWA is in REQUEST and was not in control on the previous cycle. End when lateral offset is ≤ `recenter_done` or HWA leaves REQUEST |
| LKA | Point where DLC on the drift side = `dlc_target_lka`, constrained between the lane center and that side | Start from `T_lka` |
| ELK | Within the corridor defined by the hazard-side boundary, at least `dlc_target_lka` from that boundary if space allows | Start from `T_elk` |

LKA and ELK use technique A in both builds. When T9 selects a new intervention, T7 builds a quintic from the measured state (PP-SWR-080). If the initial path fails the checks, T7 tests durations on the `intervention_T_step` grid. The maximum duration is the time remaining in the 10 s since receiving REQUEST (PP-SWR-083).

- Evaluate the a_y, added a_y, and jerk limits in PP-SWR-110 to 115. Prefer candidates that meet the limits and reduce front-tire encroachment beyond the corridor. When the vehicle is drifting out, TLC reduces the projected remaining clearance to the boundary. T10 checks the path after blending it with the previous path.
- Keep the quintic coefficients and start time throughout the intervention. Each cycle, sample at the elapsed time using the current reference line. After the quintic duration, the lateral samples hold the target with zero lateral velocity until T9 completes or cancels the intervention.
- For road-edge ELK, construct the reference line from the hazard-side edge and a reliable opposite boundary. If the opposite boundary is lost, reuse the stored lane width if the edge remains MEASURED and matches the previously associated edge after ego-motion compensation. A measured marking outside the ego lane on the same side disqualifies the edge as an ego-lane corridor boundary (PP-SWR-047).

**Three candidate techniques** (assignment: select one and give reasons for rejecting at least one alternative; select per Software Qualification Test Specification Section 9):

| Technique | Algorithm | Calibration |
|---|---|---|
| A. Duration-based quintic | Use a fifth-degree d(t) from the initial state to (target d, 0, 0) over T. If `ay_add_max_hwa` or `jerk_target_hwa` is exceeded, increase T in 0.25 s steps up to `T_max`. T10 clips the path to the hard limits | `T_max` |
| B. Frenet sampling | Generate quintics with final d within target d ± `d_sample_span` in steps of `d_sample_step`, with T from `T_set`. Discard paths that exceed limits or leave the corridor. Select the path minimizing J = `w_jerk`·∫d⃛² + `w_time`·T + `w_dev`·(final d − target d)² + `w_cons`·∫(d − d_old)² | `d_sample_span`, `d_sample_step`, `T_set`, `w_jerk`, `w_time`, `w_dev`, `w_cons` |
| C. Unified QP | The condensed formulation uses lateral jerk j_k as the decision variable over 30 steps. Exact integration from the T4 initial state gives d, ḋ, and d̈. Minimize `qp_w_jerk`·Σj² + `qp_w_dev`·Σ ramp·(d − o)² + `qp_w_cont`·Σ(d − d_old)² + the terminal costs `qp_w_term_d`·(d − o)² + `qp_w_term_v`·ḋ² + `qp_w_comfort`·Σσ² + `qp_w_corridor`·Σe². Here o is the T8 offset, and d_old is the previous path projected onto the new reference line and shifted by the change in o since the previous cycle. Linear constraints use a_y = d̈/q² + v²κ_ref/q, with q = 1 − κ_ref·d evaluated on the previous path as in T11. The magnitude of a_y is limited to `qp_ay_margin`·aysmax. At points where the required a_y > aysmax − epsilon_ay/2, constrain a_y to [aysmax − epsilon_ay/2, aysmax] (PP-SWR-006) and exclude those points from σ. At other points, a_y above `qp_a_comfort` contributes to σ. When d leaves the corridor (lane width − vehicle width − `qp_corridor_margin`), the excess contributes to e. Constrain path jerk (j + v³·dκ_ref/ds) to ±0.9 times the HWA jerk limit. Curve cutting emerges when the constraints bind. Solve with ADMM, adaptive ρ per row block (a_y ×10 and jerk ×0.1), a fixed `qp_iters` iterations, and a warm start from the previous cycle. The block-diagonal KKT matrix requires factoring one 30×30 block. T4 then blends as in technique A and T10 checks the final path | Section 15 |

For HWA, `PP_T7` selects `quintic` or `qp` at build time. The selection is reported by `pp_version()` (PP-TS-003). Both builds use quintic paths for LKA and ELK. PP-TS-006 tracks the comparison of intervention techniques.

## 11. T8 Offset {#dd-t8}

| Step | Action |
|---|---|
| 1 | Assign objects to lanes using the reference line's boundaries. A large vehicle has width ≥ 2.3 m (Software Requirements Specification Section 4) |
| 2 | Start when TTC until drawing alongside the large vehicle is ≤ `ttc_offset_start`. End `t_offset_hold` after the large vehicle's rear has passed the ego vehicle's front |
| 3 | On each side, measure from the vehicle body (± `vehicle_width`/2 about the lane center) to the nearest edge of the large vehicle within the alongside window. Use the smallest clearance if several vehicles qualify. Hold the last value for `t_offset_hold` |
| 4 | s = (w − `vehicle_width`) / 2. o_lim = max(0, min(`offset_max`, s − `dlc_offset_min`)). Clearance shortfall h = max(0, `gap_truck_min` − clearance) |
| 5 | Compute o per Software Architectural Design Section 6. With a large vehicle on one side, shift away by h. With vehicles on both sides, balance the clearances. Positive o points left. Clamp o to [−o_lim, o_lim] and limit the change to `ref_rate` per second |
| 6 | If ObjectList is invalid, return o to 0 at the same rate (PP-SWR-140) |

## 12. T9 Arbitration {#dd-t9}

LKA and ELK each retain their phase, time of receipt of REQUEST, side, ELK reason, start time for the completion-condition hold, and REQUEST inhibit flag. PathStatus publishes `lka_phase` and `elk_phase` per PP-ADR-015.

| Step | Action |
|---|---|
| 1 | Check the FunctionRequests timeout from receipt. After 75 ms, invalidate the path in both PathStatus and Trajectory (PP-SWR-145) |
| 2 | When a function leaves REQUEST, clear its phase and inhibit flag. On receipt of a new ELK REQUEST, block the request if the front tire has crossed the requested-side marking by more than 0.3 m (PP-SWR-089) |
| 3 | During an ACTIVE intervention, evaluate completion from the DLC on both sides, v_lat, heading error, and the magnitude of added a_y on the path in use at t0. Extrapolate v_y to t0 linearly from the two latest valid VehicleStateEstimate messages. Set COMPLETED once the conditions hold continuously for `T_end_hold`. Hold the phase until the function leaves REQUEST (PP-SWR-032, 041, 090) |
| 4 | Select among eligible REQUESTs in order ELK > LKA > HWA. LKA and ELK need reliable boundaries per PP-SWR-047. A new intervention requires valid v_y. If only v_y is lost during an intervention, continue sampling its quintic (PP-SWR-046). Cancel if eligibility is lost or the PP-SWR-083 time limit is reached |
| 5 | On completion or cancellation, select the next function in the same cycle. If no candidate remains, report NONE and keep a valid handover path when inputs allow. Road-edge ELK still evaluates the direct-boundary corridor on the tick that receives OFF. Blend with T4 per PP-SWR-031, 036, 037 |
| 6 | Report NONE when the path is invalid. Block held intervention REQUESTs until the function leaves REQUEST and requests again (PP-SWR-043, 045) |

The result matches the arbitration state table in Software Architectural Design Section 5.1. Unit tests verify each cell of that table.

## 13. T10 Feasibility and limits {#dd-t10}

| Step | Action |
|---|---|
| 1 | Across the 31 points: a_y = v²·κ; added a_y = a_y − v²·κ_ref; jerk = time derivative of a_y, averaged over 0.5 s; `front_wheel_angle` = atan(`wheelbase`·κ); steering wheel rate = `steering_ratio` × rate of change of wheel angle |
| 2 | If the active function or VehicleConfig limits are exceeded, clip κ to the limit and reintegrate d(t). Keep a_y ≥ aysmax − `epsilon_ay` when the required a_y exceeds aysmax (PP-SWR-006) |
| 3 | Set `lateral_limit_reached` when the maximum required a_y within the visible range is > aysmax + `delta_ay`; clear it when < aysmax − `delta_ay`. The condition must hold on consecutive cycles for `T_flag` / 2 |
| 4 | For LateralLimits, κ_max is the largest magnitude of κ(s) within the visible range. `v_max` = √(function's a_y limit / κ_max). `distance` is s at κ_max |

- Step 2 also clips curvature at point 0 while retaining its position. Jerk is clipped at each 0.1 s step, stricter than the requirement's 0.5 s average. Each limit has a relative margin of 10⁻⁶ to prevent the published float32 value from exceeding it.
- Steps 3 and 4 use the greater curvature of the camera reference line and T5 as a conservative input for the flag and `v_max` sent to the longitudinal module. The path still follows the T5 curvature.

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
| `sigma_kappa_min` | 1/m | 1·10⁻⁴ | 5·10⁻⁵–5·10⁻⁴ | T5 |
| `T_hwa` | s | 3.0 | 2.0–4.0 | T7 |
| `T_max` | s | 5.0 | 4.0–8.0 | T7 |
| `intervention_T_step` | s | 0.25 | 0.1–0.5 | T7 A |
| `recenter_done` | m | 0.1 | 0.05–0.2 | T7 |
| `d_sample_span`, `d_sample_step` | m | 0.3; 0.05 | 0.2–0.5; 0.025–0.1 | T7 B |
| `T_set` | s | 1.5 to 4.0, in steps of 0.5 | — | T7 B |
| `w_jerk`, `w_time`, `w_dev`, `w_cons` | — | 1; 0.1; 1; 1 | 0.1–10 per weight | T7 B |
| `qp_w_jerk`, `qp_w_dev`, `qp_T_ramp` | —; —; s | 1; 0.3; 1.0 | 0.3–3; 0.1–3; 0.5–2 | T7 C |
| `qp_w_term_d`, `qp_w_term_v` | — | 10; 10 | 0–50 | T7 C |
| `qp_w_comfort`, `qp_w_corridor` | — | 5; 500 | 1–50; 100–5000 | T7 C |
| `qp_w_cont` | — | 200 | 0–2000 | T7 C |
| `qp_a_comfort` | m/s² | 2.0 | 0–2.5 (0 penalizes a_y² directly) | T7 C |
| `qp_ay_margin` | — | 1.0 | 0.95–1.0 | T7 C |
| `qp_corridor_margin` | m | 0.3 | 0.1–0.5 | T7 C |
| `qp_iters`, `qp_rho0` | — | 150; 1.0 | 75–300; 0.1–10 | T7 C |

## Revision history {#revision-history}

| Version | Date | Changes |
|---|---|---|
| 0.3 | 2026-11-10 | Notes on T1 through T8 and a table of candidate techniques |
| 1.0 | 2026-11-10 | Rewritten as the Software Detailed Design, baseline BL1: algorithms for 11 units, code structure, and algorithm-level calibration parameters |
| 1.1 | 2026-11-10 | Moved the implementation to C11 (PP-ADR-013), with `planner/src/*.c` modules, message types from `interfaces/c/`, and a calibration struct generated at build time |
| 1.2 | 2026-11-10 | T6 is internal to the planner (PP-ADR-014) |
| 1.3 | 2026-11-11 | Implementation notes on `pp_math.c` and double precision. T2 stores boundaries, accepts changes after `T_confirm`, and follows the previous reference line even when the lane model is invalid. T4 uses Hermite interpolation and blends Cartesian points. T5 floors camera variance, updates only on new frames, and refits c2 and c3. T7 defines recentering start and end and uses `ay_add_max_hwa` and `jerk_target_hwa` as targets. T10 clips point 0, adds a float32 margin, and uses the larger curvature for the flag and LateralLimits. Added `sigma_kappa_min` and `recenter_done` |
| 1.4 | 2026-11-11 | T2 accepts a new position only after it is stable for `T_confirm`. After acceptance, an edge returning to the old position within `T_confirm` is accepted immediately |
| 1.5 | 2026-11-11 | Reworked T7 C as a unified condensed QP solved by ADMM (PP-TS-003). Added T7 C calibration and build-time technique selection |
| 1.6 | 2026-11-11 | T7 C uses `qp_w_cont` for continuity with the previous path, and T4 still blends. Added the T11 a_y formula, the PP-SWR-006 a_y band, jerk constraints, and ρ per row block. Set `qp_ay_margin` to 1.0. T8 uses clearance to large vehicles and `gap_truck_min`. T7 C shifts the previous path by the latest offset change |
| 1.7 | 2026-11-12 | T7 uses quintic paths for LKA and ELK in both builds. T9 tracks separate phases, applies PP-SWR-145 at the output, and reselects a function in the same cycle on completion or cancellation |

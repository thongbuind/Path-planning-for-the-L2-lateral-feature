# Path Planner Feature Design

This report describes **how the G1 path planner meets its requirements**. It covers inputs, outputs, the planning cycle, paths for each feature, limits and fault handling. **Path Planner Software Requirements** defines what the planner must achieve. Each design section references the requirement IDs (PP-SWR-…) it addresses. Tables distinguish agreed items, proposals and open decisions. This is the **feature plan**. Algorithm implementation and technique selection belong to the separate **Path Planner Implementation** report, currently pending, which now contains the algorithm notes.

**Assignment scope.** One planner serves HWA, LKA and ELK. Using the lane model, vehicle state (speed, yaw rate and lateral velocity) and feature requests, it produces a smooth and feasible path at 20–50 Hz. HWA needs a continuous lane-center path that stays smooth on curve entry and through lane model jumps. LKA and ELK need paths that intervene from a drifting state and bring the vehicle back into its lane. Each feature has its own starting conditions, lateral acceleration budget and completion conditions. Transitions among the three features shall avoid steps in the steering request. The planner must work with actual camera outputs, including residual lane model errors.

**Relationship to other reports**

| Report | Relationship to this report |
|---|---|
| Path Planner Software Requirements | Defines what the planner must achieve, with requirement IDs, sources, verification methods and statuses. This design describes how and references those IDs |
| ADAS Functions | Determines **when** to intervene. It sends `FunctionRequests` with each feature's state, TLC, side and driver_override, and receives `PathStatus`. See that report for activation logic |
| Path Planner Implementation (Pending) | Holds algorithm notes and candidate techniques. Implementation design follows completion of this feature plan |
| Benchmark and Evaluation | Compares planning techniques **fairly** under the same conditions, with predefined metrics and thresholds. **Functional tests** check pass or fail for individual requirements during development. The benchmark compares alternatives for selection and reporting |

## 1. Scope

| In G1 scope | Outside G1 scope |
|---|---|
| Reference path from the lane model, including lane center, center offset and loss of one marking | Lane model filtering, handled by Lane Model upstream |
| ELK > LKA > HWA arbitration and transitions without steps | Activation decisions, handled by ADAS Functions |
| HWA path and LKA and ELK intervention paths | Lateral Controller and EPS internals |
| Intervention completion (COMPLETED) and interface to the longitudinal module (Section 6.1) | Production ACC and AEB design. The simulator uses a simple ACC stub (Section 6.1) |
| Lane model, timing and input integrity fault handling | v_y estimation (G2) and ego motion (G4) |

## 2. Interfaces

See [G1 Interfaces and Signals](report.html?doc=g1-interfaces-and-signals&lang=vi) for schemas, units and transport conventions.

### 2.1 Inputs {#planner-inputs}

| Source | Contents | Rate, delay and timeout | Status |
|---|---|---|---|
| Lane Model | 4 markings L2, L1, R1, R2 with c0–c3 and variances, view range, confidence, marking type, crossability and status (measured, predicted or lost). Lane width and lane change flag | 20 Hz. Assumed delay 100 ± 20 ms, timeout 150 ms and maximum age 250 ms (Section 3) | agreed |
| Perception | Object x, y, vx, vy, heading, length, width, id and existence probability | 20 Hz. Assumed delay 100 ± 20 ms and timeout 150 ms | agreed |
| Chassis CAN | Filtered yaw rate, a_x and a_y, speed, steering wheel angle and rate. Counter, CRC and qualifier | IMU and steering at 100 Hz and speed at 50 Hz. Delay unknown | mentor |
| Vehicle State Estimation (G2) | v_y at the rear axle center, sideslip angle and variance | 50 Hz. Assumed delay about 10 ms | agreed |
| Ego-motion (G4) | Query Δx, Δy and Δψ between two times. At least 0.5 s of history | Function call within the same cycle | agreed |
| ADAS Functions | Per feature, state { OFF, UNAVAILABLE, STANDBY, REQUEST, FAULT }, side, tlc, elk_reason and cancel_reason. Shared driver_override | 40 Hz. Assumed delay about 20 ms, timeout 75 ms and maximum age 45 ms | agreed |
| ACC stub | LongitudinalPlan with planned speed and acceleration over 3 s (Section 6.1) | 40 Hz. Timeout 75 ms | proposed |
| Vehicle Configuration | Wheelbase 2.9 m, distance from rear axle center to center of gravity, width 1.9 m, steering ratio 15, maximum wheel angle 0.61 rad, maximum steering wheel rate 6 rad/s and actuator delay 50 ms | Read once at startup | agreed |

**Mentor inputs.** The entries below are agreed with the mentor and consistent with the team decisions.

| Item | Details | Status |
|---|---|---|
| L2 module rates | The planner and ADAS Functions run at 40 Hz (25 ms), within the assignment's 20–50 Hz range. The timeout for messages sent by L2 modules is 3 cycles, or 75 ms | mentor |
| Vehicle signals | The Motion signal list includes raw and filtered yaw rate, a_x and a_y at 100 Hz, steering wheel angle and rate at 100 Hz, vehicle speed at 50 Hz and driver torque at 50 Hz for ADAS Functions. Vehicle units are °/s, ° and km/h. The receiver converts to SI once. All four teams use the same list. The planner receives only the signals in the table above | mentor |
| IMU | Treat the IMU input to the planner as filtered. Upstream processing estimates bias and filters noise. The planner reads the filtered signal and must tolerate light residual noise. Test noise levels are in Benchmark and Evaluation | mentor |
| Delay | Actual input delays are unknown. All delay values in this report are design assumptions. The planner must allow for delay variation. The benchmark sweeps multiple delay levels (Benchmark and Evaluation, Section 4.1) | mentor |

### 2.2 Outputs {#planner-outputs}

**Path sent to Lateral Controller.** The format extends Autoware Trajectory.

| Field | Requirement | Status |
|---|---|---|
| header | stamp_us is the time represented by the path after camera delay compensation. counter wraps over 0–255. Includes valid and frame_id = base_link | agreed |
| points[31] | 0.1 s spacing over 0–3 s. Each point has time_from_start, pose (x, y, yaw), longitudinal_velocity, lateral_velocity, acceleration, heading_rate = v·κ, curvature, front_wheel_angle (feedforward hint) and rear_wheel_angle = 0 | agreed |
| Rate | 40 Hz. The receiver considers the path stale after 75 ms (3 cycles) | mentor |
| Longitudinal speed and acceleration | Use `LongitudinalPlan` when valid data is available. Otherwise follow PP-SWR-154 (Section 6.1) | proposed |

**Are points[31] dense enough?** The checks cover the HWA, LKA and ELK speed range (10–130 km/h). The table provides Analysis evidence for PP-SWR-011.

| Question | Check | Conclusion |
|---|---|---|
| Distance between points | 0.1 s × 36 m/s = 3.6 m at 130 km/h and 0.28 m at 10 km/h | Resolution is sufficient. The shortest curve the path must describe (an ELK intervention segment of about 1 s) still has about 10 points |
| Horizon | 3 s covers 75 m at 90 km/h and 8 m at 10 km/h | Covers the controller's 0.5 s lookahead. Distance is short at low speed. HWA waits below 10 km/h |
| Whether the entire intervention fits within 3 s | About 3 s for LKA, 1–3 s for ELK and 3–4 s for HWA recentering | Fits entirely or almost entirely. The planner sends only the first 3 s because it replans every 25 ms |
| Interpolation between points | The controller runs at 100 Hz and interpolates between points | **Interpolation method is open.** The proposal uses linear interpolation in time for position and yaw, and reads curvature directly from the curvature field |

### PathStatus {#path-status}

Sent to ADAS Functions via pub/sub at 40 Hz, with a 75 ms timeout and assumed delay of about 1 ms. Uses the [common header](report.html?doc=g1-interfaces-and-signals&lang=vi#header) without `frame_id`.

| Field | Meaning | Status |
|---|---|---|
| path_valid (bool) | Path remains reliable. False when T_coast expires or a required input is invalid (PP-SWR-124, 142 through 145) | agreed |
| active_function (uint8 enum) | { NONE, HWA, LKA, ELK }. The arbitration result identifying the feature that controls steering | agreed |
| intervention_phase (uint8 enum) | { NONE, ACTIVE, COMPLETED }. COMPLETED when LKA or ELK meets its completion conditions (Section 7.1) | agreed |
| lateral_limit_reached (bool, planned) | The path is limited because required a_y to track the lane center exceeds the budget. See PP-SWR-007 through 009. Send to ADAS Functions and ACC (Section 6.1) | to be agreed |

**LateralLimits sent to the ACC stub.** At 40 Hz, send curvature-based v_max, distance to that point and lateral_limit_reached (Section 6.1).

See Path Planner Software Requirements, Section 5.1, for the definition, requirements and rationale for lateral_limit_reached.

## 3. Planning cycle {#planner-cycle}

| Step | Action | Status |
|---|---|---|
| 1. Receive | The receiver has checked each incoming message for valid, counter (discard repeats and record skips as losses), CRC, qualifier and timestamp order. Treat messages with `valid = false` as unreceived. The planner reads only the latest checked message | agreed |
| 2. Check timing | An input is invalid if it exceeds the receive timeout or maximum age (Section 8.2 and PP-SWR-131 through 134) | agreed |
| 3. Compensate delay | Transform the lane model from capture time to the present using ego motion. Apply the same transformation between camera frames (planner 40 Hz, camera 20 Hz) (PP-SWR-012, 013, 128) | agreed |
| 4. Build reference path | Derive the lane center from two markings or one marking plus remembered width. Fuse camera c2 with r/v and path history (Section 4) | agreed |
| 5. Arbitrate | Select the controlling feature from FunctionRequests (Section 5) | agreed |
| 6. Generate path | Generate an HWA path (Section 6) or intervention path (Section 7) in Frenet coordinates (s along the lane center, d lateral offset, positive to the left) | agreed |
| 7. Stitch and check continuity | Compare with the previous cycle's path transformed to the new base_link. Enforce continuity limits (Section 9.2 and PP-SWR-100 through 102) | agreed |
| 8. Check feasibility | Check a_y, jerk, steering angle and rate against their limits (Sections 9.1 and 9.3). Set lateral_limit_reached if clipping is necessary (PP-SWR-007) | agreed |
| 9. Publish | Convert from Frenet to base_link, sample 31 points and publish the path and PathStatus. Log cycle computation time (PP-SWR-010, 015) | agreed |

**Delay compensation error analysis** (rationale for PP-SWR-012, 013). This step determines whether the reference is aligned with the true lane. Error here directly affects the vehicle's position in the lane.

| Error source | Values at 25 m/s | Lateral reference error |
|---|---|---|
| Uncompensated delay on a straight road | With 100 ms delay the vehicle travels another 2.5 m | Nearly zero lateral error and 2.5 m longitudinal error |
| Uncompensated delay on a curve (r = 0.1 rad/s, R = 250 m) | The vehicle rotates 0.01 rad in 100 ms | 0.25 m at 25 m ahead and 0.5 m at 50 m |
| Compensation using nominal delay | ±20 ms jitter causes 0.002 rad rotation error | 0.05 m at 25 m |
| Unsynchronized clocks | Up to ±10 ms offset before initial synchronization | About 0.025 m at 25 m |
| After gPTP synchronization | ±50 µs error | Negligible |

The table gives three results. (1) Compensation must use the **capture stamp**. (2) Invalid ego motion makes the path invalid immediately (PP-SWR-143). (3) The benchmark measures delay compensation separately by sweeping delay and loss of clock synchronization (Benchmark and Evaluation, Section 4.1). Implementation details are pending in Path Planner Implementation (T1).

**Unknown delay.** The mentor indicates that actual delay is unknown. An accurate capture stamp supports compensation without an advance estimate of delay. Two choices still depend on the delay value.

| Dependency | Problem | Approach | Status |
|---|---|---|---|
| Maximum age of lane model and object data | The previous threshold was 170 ms based on assumed delay. At 200 ms actual delay, every frame would be stale and the lane model would be treated as lost | Two configurable thresholds, described below | agreed |
| Filtered yaw rate delay | The filter adds an unknown delay. The CAN reception stamp excludes it | Three steps below | proposed |

**Proposed maximum age for lane model and object data** (rationale for PP-SWR-131 through 134). Message age is planner read time minus the capture stamp. The planner reads the newest message and the camera sends every 50 ms, so maximum age is delay plus 50 ms.

| Threshold | Value | On crossing | Rationale | Status |
|---|---|---|---|---|
| Monitoring threshold | 170 ms, the maximum assumed delay of 120 ms plus 50 ms | Keep using the data. Log and count frames over the threshold | Detect actual delay above the assumption while retaining functionality | agreed |
| Discard threshold | 250 ms, the largest benchmark sweep delay (200 ms) plus 50 ms | Mark the input invalid. Treat lane model loss as loss of both markings and follow the previous path for up to T_coast. Treat missing objects as loss of perception | See the three checks below | agreed |
| Negative age | Stamp more than 10 ms in the future (the maximum clock offset before initial synchronization) | Mark the input invalid and record a clock fault | Incorrect stamps cause incorrect delay compensation | agreed |

Three calculated checks for the 250 ms threshold at 25 m/s follow.

1. **Sufficient ego-motion history.** Transform the lane model from capture time to now, up to 250 ms. Ego-motion retains 0.5 s, leaving margin.
2. **Small ego-motion transform error.** Error is nearly zero with clean IMU signals in the main scenario. With worst-case bias of 1 °/s (0.0175 rad/s), heading error after 250 ms is 0.0044 rad, or 0.11 m at 25 m ahead. At 0.3 °/s bias, the lateral error is only 0.03 m.
3. **Adequate object accuracy.** A velocity error of σ = 0.3 m/s ([Sensor Models](report.html?doc=benchmark-evaluation&lang=vi#sim-sensors)) over 250 ms gives 0.075 m, small compared with the ±2 m buffer ADAS Functions uses around the vehicle.

Once measured delays are available, set the discard threshold to the maximum measured delay (for example the 99.9th percentile) plus 50 ms. If the value exceeds 250 ms, repeat the three checks above.

**Handling filtered yaw rate delay**

1. **Estimate sensitivity.** Yaw rate is used in two places. (a) For ego-motion compensation of camera delay, heading error is yaw acceleration × filter delay × compensation interval. On curve entry with 0.1 rad/s² yaw acceleration, 50 ms filter delay and 0.1 s compensation, error is 0.0005 rad, about 1 cm at 25 m. (b) For curvature from r/v, consider a clothoid from a straight road to R = 250 m in 3 s at 90 km/h. Curvature grows by about 0.0013 1/m each second. A 50 ms delay causes about 0.00007 1/m error, below the 0.0003 1/m continuity threshold (Section 9.2). Both effects are small compared with camera delay error (0.25 m at 25 m, table above). These are project calculations without an external source.
2. **Measure from data.** The vehicle has raw and filtered signals at 100 Hz. Estimate filter delay by finding the time shift that maximizes cross-correlation. Ground-truth yaw rate can provide a second check. Measure once and store the result as a configuration parameter. The receiver subtracts that value from the IMU stamp.
3. **Verify margin.** Sweep IMU filter delay while deliberately keeping the configuration parameter at 0 to check that the path is only slightly affected (Benchmark and Evaluation, Section 4.1).

### 3.1 Sequence within a cycle {#planner-sequence}

Each cycle starts at scheduler tick t0, every 25 ms. The table lists the messages in order. t_c is the cycle's computation time.

| # | Time | From → to | Contents | Requirements | Status |
|---|---|---|---|---|---|
| 1 | t0 | Scheduler → Planner | Cycle tick | PP-SWR-010 | agreed |
| 2 | t0 | Receiver → Planner | Latest checked LaneModel, ObjectList, CAN frames, VehicleStateEstimate and FunctionRequests messages, plus LongitudinalPlan from the previous cycle | PP-SWR-126 through 134 | agreed |
| 3 | t0 | Planner → Ego-motion (G4) | Query Δx, Δy and Δψ from the lane model capture stamp to t0. Call within the same cycle | PP-SWR-012, 143 | agreed |
| 4 | t0 | Ego-motion (G4) → Planner | Δx, Δy, Δψ | PP-SWR-012 | agreed |
| 5 | t0 to t0 + t_c | Planner | Steps 3 through 8 above, covering delay compensation, reference path, arbitration, path generation, stitching and feasibility | PP-SWR-030, 100 through 102, 110 through 117 | agreed |
| 6 | t0 + t_c | Planner → Lateral Controller | Trajectory, header.stamp_us = t0 | PP-SWR-010, 011, 012 | agreed |
| 7 | t0 + t_c | Planner → ADAS Functions | PathStatus | PP-SWR-010 | agreed |
| 8 | t0 + t_c | Planner → ACC stub | LateralLimits | PP-SWR-150 | proposed |
| 9 | after t0 + t_c | ACC stub → Planner | LongitudinalPlan. The planner uses it in the next cycle to avoid a loop within the same cycle (Section 6.1) | PP-SWR-153 | proposed |
| 10 | every 10 ms | Lateral Controller | Read the latest Trajectory in its 100 Hz cycle | — | agreed |

**Deadline.** The planner sends steps 6 through 8 before t0 + 5 ms. The 5 ms matches both the simulator's computation time (Section 9.3) and the threshold in PP-SWR-016. Status: to be agreed. Whether to drop or publish a cycle that misses its deadline is open (Section 11).

### 3.2 Delay chain from sensor to wheels {#latency-chain}

All delay values are assumptions (Section 2.1, based on mentor input). The tables identify which module introduces and compensates each delay.

| # | Segment | Delay | Worst case (ms) | Source | Compensation | Status |
|---|---|---|---|---|---|---|
| 1 | Camera capture → Lane Model publish | 100 ± 20 ms (assumed) | 120 | Camera, Lane Model | Planner, using the capture stamp (PP-SWR-012) | agreed |
| 2 | Lane Model publish → planner read | 0–50 ms. Camera at 20 Hz and planner reads the latest frame | 50 | Camera cadence | Planner, using the capture stamp and ego motion between frames (PP-SWR-128) | agreed |
| 3 | Planner computes and publishes | t_c ≤ 5 ms (Section 3.1) | 5 | Planner | Lateral Controller reads the path against header.stamp_us | proposed |
| 4 | Trajectory transmission | About 1 ms (assumed) | 1 | Pub/sub | Same as row 3 | proposed |
| 5 | Wait for controller cycle | 0–10 ms (100 Hz) | 10 | Controller cadence | Same as row 3 | proposed |
| 6 | Controller computation | Unknown | ? | Lateral Controller | Same as row 3 | to be agreed |
| 7 | EPS actuation | 50 ms (vehicle configuration) | 50 | EPS | Lateral Controller selects the path point at current time plus actuator delay | proposed |

**Parallel chains.** The two chains below run in parallel with the one above. Their delays are excluded from its total.

| # | Segment | Delay | Worst case (ms) | Source | Compensation | Status |
|---|---|---|---|---|---|---|
| 8 | Yaw rate from IMU → CAN → planner | About 5 ms (assumed) plus unknown filter delay | 5 + ? | CAN, filter | Planner tolerates up to 50 ms without being told the delay (PP-SWR-138) | proposed |
| 9 | FunctionRequests from ADAS Functions → planner | About 20 ms (assumed) plus 0–25 ms wait for cycle | 45 | Pub/sub, planner cadence | No compensation. The planner responds within one cycle (PP-SWR-038) | proposed |

**Worst-case total** (rows 1 through 7, excluding row 6). Camera capture to wheel response takes 120 + 50 + 5 + 1 + 10 + 50 = 236 ms. The planner compensates the first 170 ms (rows 1 and 2) using the capture stamp. The remaining 66 ms (rows 3 through 7) begin when the planner computes the path.

**Proposal.** Lateral Controller compensates the delay after the planner by reading the path point at current time plus actuator delay, using header.stamp_us and time_from_start. The planner leaves that forward shift to the controller so each delay is compensated once. Confirm with the Lateral Controller team (Section 11).

## 4. Reference path

This section addresses PP-SWR-050, 060 and 121 through 125 (Path Planner Software Requirements).

| Case | Approach | Status |
|---|---|---|
| Both L1 and R1 available | Lane center is the average of the two polynomials | assignment |
| One marking lost | Shift the remaining marking by half the remembered lane width. The detailed algorithm for each case is pending (Path Planner Implementation, T2) | assignment |
| Both markings lost | Follow the previous cycle's path, transformed into the new base_link, for up to T_coast = 1 s. Then report the path invalid (PP-SWR-124) | agreed |
| c0 and c1 noise | Lane Model applies a Kalman filter. G1 still needs a fallback for residual noise, described below | to be agreed |
| c0 jump | Lane Model supplies no jump flag. G1 detects jumps with the boundary consistency check below, stitches the new path to the old one and limits the center shift to meet continuity thresholds (PP-SWR-121). A smooth stitching algorithm is pending (Path Planner Implementation, T4) | agreed |
| Boundary consistency check | Lane Model supplies no c0 jump flag. Such a flag has yet to be documented for commercial lane models. Mobileye CAN exposes polynomial coefficients, quality and marking type, with no jump flag. Treat a future jump flag and the existing Lane Model lane change flag as secondary sources. G1 checks each boundary (marking or road edge) at two time scales. (1) Per frame, compare the new boundary with the previous frame's boundary after an ego-motion transform. A c0 change of more than a few standard deviations (from Lane Model variance) indicates a c0 jump or misidentification of an adjacent marking. (2) At a slower time scale, check parallelism using the c1 and c2 differences across boundaries and compare lane width with remembered width. This detects lane widening, an exit split or an added lane. When a boundary is inconsistent, both checks discard it, anchor the lane center to the stable boundary plus remembered width and freeze the remembered width. Accept a real change in the current lane (narrowing or a lane change) when both boundaries confirm it across multiple frames. A road edge widening by 1.5 m over 100 m at 25 m/s moves by only 0.02 m per camera frame, below the per-frame threshold (about 3 × 0.03 m). Its 0.015 rad angle difference from the other marking is about 5 times the noise in the c1 difference (√2 × 0.002), so the slower check detects it immediately | proposed |
| Lane widening at a road edge or marking, such as an emergency shoulder, split or added lane | PP-SWR-060. The vehicle continues to follow the true lane using the stable boundary. Detect widening with the slower check above | mentor |
| Incorrect c2 farther ahead | Weighted combination of camera c2, curvature from r/v and G1 path history | agreed |
| Initial path state | See Section 4.2 | to be agreed |

### 4.1 Residual lane model noise

The filtered lane model still fluctuates. Section 8.1 gives noise of σ_c0 = 0.03 m and σ_c1 = 0.002 in daylight, 2.5 times higher at night. A path that follows every frame would cause steering oscillation. G1 uses three fallback layers based on its own path. Raw sensor filtering stays upstream.

| Layer | Approach | Example |
|---|---|---|
| 1. Start from the previous path | Start from the state on the previous cycle's path after transforming it into the new base_link. Noise in a single frame changes only the far part of the path | A 0.05 m c0 error in one frame leaves the path near the vehicle unchanged |
| 2. Limit reference rate of change | Limit the distance the reference lane center can shift per second. An example for HWA is 0.1 m/s | ±0.03 m noise between frames becomes a slow shift |
| 3. Penalize path jerk | Select a low-jerk path that avoids following small, fast oscillations | The path stays smooth with slight reference fluctuations |

All three layers slow the response to real lane changes, such as curve entry. The benchmark measures both RMS steering wheel rate under noise (oscillation) and deviation on curve entry (slow response). Related requirements are PP-SWR-050 and 120. Parameter values are pending in Path Planner Implementation (T3).

### 4.2 Initial path state

Each path starts from lateral offset d0 from the lane center, heading error and v_lat. Two decisions are open.

**Question 1. Where does the initial state come from?**

| Option | Approach | Benefit | Trade-off |
|---|---|---|---|
| A. Measured state | Recalculate each cycle from lane model, v_y and r | Follows actual vehicle state | Measurement noise directly affects the start of the path and causes oscillation |
| B. Previous cycle's path | Start the new path at the corresponding point on the previous path | Continuous and free of oscillation | If the vehicle deviates from the previous path due to wind or tracking error, the new path starts in the wrong place |
| C. Hybrid | Use B while the vehicle remains close to the previous path. Switch to A above a deviation threshold (for example 0.2 m) | Continuous in normal operation and accurate under large deviations | Requires a threshold. Switching from B to A can cause a small step |

Many trajectory planners use option C, known as trajectory stitching. Baidu Apollo has this mechanism. **Option C is proposed.** When LKA or ELK **starts intervening**, the vehicle is drifting, so recompute from the measured state (A) and stitch to any active HWA path to avoid a step.

**Question 2. Which module computes the measured state?**

| Option | Benefit | Trade-off |
|---|---|---|
| ADAS Functions and G1 use **one shared function** with the same inputs | Both produce the same result. If ADAS Functions activates at TLC 1.0 s, G1 also sees 1.0 s | Both modules depend on one shared library |
| G1 computes it independently | Independent modules | Can disagree. ADAS Functions may see TLC 1.0 s while G1 sees 1.3 s and picks the wrong duration |
| ADAS Functions includes the state in its message | One source | Adds about 20 ms of assumed delay. G1 still needs to compute the state for HWA every cycle |

**The proposal uses one shared function.**

## 5. Arbitration and transitions

See PP-SWR-030 through 040 (Path Planner Software Requirements, Section 4). The table gives the design.

| Task | Approach | Requirements | Status |
|---|---|---|---|
| Select feature | Each cycle, select the highest-priority feature in REQUEST. OFF, UNAVAILABLE, FAULT and STANDBY carry no request | PP-SWR-030 | agreed |
| Transition | When a feature takes or returns control, start the new path from the active path state | PP-SWR-031 | agreed |
| Complete an intervention | G1 determines completion independently of ADAS Functions (Section 7.1) | PP-SWR-032, 033 | agreed |
| Prevent repeated intervention | Remember the feature that reached COMPLETED. Accept a new intervention only after it leaves and re-enters REQUEST | PP-SWR-034 | agreed |
| Request canceled during intervention | End the intervention path. Generate an HWA path from the current state if HWA is available, otherwise report NONE | PP-SWR-036, 037 | agreed |
| Driver override | During override, the path follows the current vehicle position. On release, generate a new HWA path from that position | PP-SWR-039, 040 | agreed |
| FunctionRequests timeout | Treat all three features as off | PP-SWR-145 | agreed |

Lateral Controller owns its behavior when active_function = NONE. G1 reports the state.

### 5.1 State transition table {#arbitration-states}

The state is the controlling feature (active_function). Each cell gives the next state and planner action. “—” means the event cannot occur or changes nothing. The map diagram reads the → symbol, which marks only transitions caused by that row's event. A cell with **?** has no deciding requirement. Its proposal appears in the cell and the open decision is in Path Planner Software Requirements, Section 10.

The table follows PP-SWR-030 through 040, 124 and 142 through 145, and the ADAS override behavior. ADAS Functions sends OFF and sets driver_override in the same message (ADAS Functions, Section 5). For a solid line, ADAS Functions requests LKA before ELK, so both can be in REQUEST (ADAS Functions, Section 6).

| Event | In NONE | In HWA | In LKA (intervening) | In ELK (intervening) | Requirements |
|---|---|---|---|---|---|
| HWA enters REQUEST | → HWA. Start from vehicle state and recenter | — | Remain in LKA | Remain in ELK | PP-SWR-030, 052, 053 |
| HWA leaves REQUEST | — | → NONE. **?** path_valid (proposal keeps true, as in PP-SWR-037) | Remain in LKA. On completion, return to NONE | Remain in ELK. On completion, return to NONE | PP-SWR-030, 033 |
| LKA enters REQUEST | → LKA if v_y is valid | → LKA if v_y is valid. Stitch the path | — | Remain in ELK | PP-SWR-030, 031, 080, 144 |
| ELK enters REQUEST | → ELK if v_y is valid | → ELK. Stitch the path | → ELK. Stitch the path | — | PP-SWR-030, 031, 144 |
| Intervening feature leaves REQUEST, including on driver override | — | — | → HWA if HWA is in REQUEST, otherwise NONE. Keep path_valid true | Same as LKA. **?** If LKA is still in REQUEST, proposed → LKA under PP-SWR-030 | PP-SWR-030, 036, 037 |
| Completion conditions met | — | — | Report COMPLETED. → HWA if HWA is in REQUEST, otherwise NONE. **?** How long to hold COMPLETED (proposal holds it until LKA leaves REQUEST) | Same as LKA. **?** If LKA is still in REQUEST (same as above) | PP-SWR-032, 033, 034 |
| driver_override set | Path follows vehicle position | Remain in HWA. Path follows vehicle position | Request canceled in the same message. Follow the row for leaving REQUEST. Path follows vehicle position | Same as LKA | PP-SWR-036, 037, 039 |
| driver_override cleared | — | Generate new HWA path from vehicle position to lane center | Cannot occur because the request was canceled | Same as LKA | PP-SWR-040 |
| FunctionRequests timeout | path_valid = false | → NONE. path_valid = false | Same as HWA | Same as HWA | PP-SWR-145 |
| VehicleStateEstimate invalid | — | Remain in HWA | → HWA if HWA is in REQUEST, otherwise NONE (from PP-SWR-144). **?** Whether stopping immediately during intervention is safe | Same as LKA | PP-SWR-144 |
| Invalid path due to T_coast expiry or an IMU, speed, steering angle or ego-motion fault | path_valid = false | path_valid = false. **?** active_function (proposed → NONE) | Same as HWA | Same as HWA | PP-SWR-124, 142, 143 |
| Input recovers after the path becomes invalid | **?** Proposed behavior makes the path valid again and generates it from true vehicle state. Select the feature under PP-SWR-030. LKA or ELK requires a new request | Same as NONE | Same as NONE | Same as NONE | PP-SWR-030 |

## 6. HWA lane centering

| Task | Approach and requirements addressed | Status |
|---|---|---|
| Track lane center | Follow the reference in Section 4 through the three fallback layers in Section 4.1. See PP-SWR-050, 051 and 100 through 102 | assignment |
| Enforce limits | Use the feasibility check in Section 3, step 8. See PP-SWR-001, 003 and 004 | agreed |
| Curve exceeds aysmax | See PP-SWR-005 through 008. The path curves less than the road, so the vehicle may approach a marking. The planner sends v_max to ACC to slow before the curve (Section 6.1) | to be agreed |
| Recenter when HWA is first enabled | ADAS Functions allows HWA entry up to 0.5 m off center. G1 uses a 3–4 s quintic segment (example below) while HWA continues to control. See PP-SWR-002, 052 and 053 | agreed |
| Offset beside a large vehicle | Assign objects to lanes using the lane model. Use TTC until alongside to start shifting early and gradually, then return to center after passing. On perception loss, ramp the offset back to 0 | agreed |
| Offset magnitude | **Balance clearance on both sides.** offset = (right clearance − left clearance) / 2, limited to ±0.3 m. Clearance on each side is the distance from the ego body to the nearest vehicle, barrier or road edge. If the side is clear, use the **reference lane boundary** from the stable boundary and remembered width. Using this reference avoids increasing clearance or pulling the vehicle toward a widening road edge, as required by the mentor. Start when TTC until alongside ≤ 3 s. Return 1 s after the rear of the large vehicle has passed. See PP-SWR-002 and 055 through 059 | to be agreed |
| Large vehicles on both sides or a barrier opposite | The formula reduces the offset or gives 0. Two trucks with equal clearance give offset = 0, keeping ego centered. A truck on the left and a close barrier on the right give little or zero offset to avoid steering toward the barrier | to be agreed |
| Narrow lane | The assignment calls for offset in narrow lanes. Use the same clearance-balancing formula. Small clearances limit the shift to moving away from a barrier or road edge | to be agreed |
| Another vehicle cuts into the lane | Lateral planning offsets the center and ACC selects the vehicle as its target (Section 6.1). ELK stays inactive for this case | to be agreed |

**Recentering calculation** (analysis for PP-SWR-053). Start 0.5 m off center and use a quintic to reach center with zero final lateral velocity and acceleration. Peak quintic a_y is about 5.77·d0/T². Thus T ≥ √(5.77·0.5 / 0.5) ≈ 2.4 s to stay at a_y ≤ 0.5 m/s². Select T = 3–4 s for jerk margin.

### 6.1 Separate lateral and longitudinal modules with shared constraints {#acc-stub}

Two edge cases need both lateral and longitudinal planning. **Another vehicle cuts fully into the ego lane**, or **the curve is tighter than HWA can track**.

**In the vehicle**, lateral and longitudinal functions usually run as separate modules with their own planners and controllers. ACC controls longitudinal motion through the motor and brakes. Lane keeping controls lateral motion through EPS. The modules **exchange constraints**. Even integrated planners often separate the calculations. Baidu Apollo EM Planner optimizes the path and then the speed. Werling et al. (2010) generate separate lateral and longitudinal trajectories and combine them.

**Decision.** The project follows the vehicle architecture. G1 is the lateral module. The longitudinal module is a **simple ACC stub** in the simulator, outside G1's deliverables and fixed across planner versions like the test Controller and EPS. G1 defines the two-way interface.

| | Separate modules with shared constraints (primary design) | Separate modules without shared constraints (comparison requested by the mentor) |
|---|---|---|
| Tight curve (R = 200 m, 90 km/h) | The planner sends curvature-based speed limit v_max = √(aysmax / κ) = √(2.5 × 200) = 22.4 m/s (80 km/h) and the distance by which to reach it. ACC slows from 25 to 22.4 m/s. At 1.5 m/s² it takes 1.8 s and about 42 m | ACC receives no curve information. The planner clips the path at aysmax and sets lateral_limit_reached, prompting a warning. The vehicle may leave the lane |
| Another vehicle encroaches into the lane | Lateral planning offsets the center by up to 0.3 m. ACC selects the other vehicle as its target and keeps its distance | Same response, with lateral planning assuming constant speed while the vehicle brakes |
| Simulator setup | The ACC stub reads LateralLimits | The ACC stub ignores LateralLimits |
| Status | agreed | agreed |

**Proposed interface between modules**

| Message | Direction | Contents | Rate | Status |
|---|---|---|---|---|
| LateralLimits | Planner → ACC | See PP-SWR-009 and 150 through 152. header. v_max [m/s] is the speed limit at the largest reference curvature within view, √(controlling feature's a_y budget / κ). distance [m] is distance to the point of that curvature. lateral_limit_reached | 40 Hz | proposed |
| LongitudinalPlan | ACC → Planner | header. mode { OFF, CRUISE, FOLLOW, CURVE_LIMIT }. points[31] contain v [m/s] and a [m/s²] at 0.1 s intervals on the Trajectory grid. target_id is the tracked vehicle, or 0 when absent | 40 Hz | proposed |

**Effects on G1**

1. **Plan using ACC's v(t)** (PP-SWR-153). Take the Trajectory longitudinal_velocity and acceleration fields from LongitudinalPlan in place of a constant-speed assumption.
2. **Each side uses the previous cycle's message** to avoid a loop within the same cycle. One cycle of delay (25 ms) is acceptable.
3. **If LongitudinalPlan is missing or exceeds the 75 ms timeout** (PP-SWR-154, 155), keep current speed constant and use acceleration 0. The path remains valid because longitudinal planning is optional for lateral planning.

**Simple ACC stub design**

| Part | Approach | Status |
|---|---|---|
| Target speed | Minimum of scenario set speed, speed that maintains the gap to the lead vehicle and the curve speed limit from LateralLimits | proposed |
| Follow lead vehicle | Select the closest object in the ego lane using lane assignments from the lane model. Desired gap = 5 m + 1.8 s × v | proposed |
| Slow before curves | Start decelerating when required deceleration to reach v_max before distance exceeds 1.0 m/s² | proposed |
| Limits | Acceleration from −3.0 to +1.5 m/s² and jerk ≤ 2.5 m/s³. AEB and emergency braking are outside scope | proposed |
| LongitudinalPlan | Predict v(t) over 3 s by holding the current jerk-limited acceleration command and keeping speed nonnegative | proposed |
| Loss of LateralLimits | ACC uses only the set speed and the lead vehicle | proposed |
| Actuation | The vehicle model receives the acceleration command through a 0.1 s delay and a first-order element with τ = 0.3 s for motor and brakes | proposed |

Check the acceleration and jerk limits against ISO 15622 (ACC). Review of the original text is pending.

## 7. LKA and ELK intervention paths

See PP-SWR-080 through 090 and 110 through 115 (Path Planner Software Requirements, Sections 6 and 7).

| Task | LKA | ELK | Status |
|---|---|---|---|
| Starting point | Measured state at activation (Section 4.2), stitched to the active path to avoid a step (PP-SWR-080, 031) | Same as LKA | assignment |
| Duration | Select from the TLC supplied by ADAS Functions and the a_y budget. Target about 3 s (Section 7.1 and PP-SWR-081) | Shorter, targeting 1–3 s within the ELK budget (PP-SWR-082) | proposed |
| Target | Return inside the lane and hand control back. Target is open between lane center and a position with DLC ≥ 0.5 m (PP-SWR-084, 085) | A safe position inside the lane without overshoot to the opposite side (PP-SWR-085) | to be agreed |
| Tighten boundary | No | Tighten the boundary on the hazardous side indicated by side. The path shall keep the tire from crossing that marking (PP-SWR-086) | assignment |
| Intentional lane change with an overtaking vehicle in the adjacent lane | — | Act only when ADAS Functions requests it under the stricter rule (ADAS Functions, Section 3.2, step 6). The other vehicle is alongside or cannot brake in time. Return the vehicle to its previous lane as permitted by R79 5.1.6.2.3.1. Withhold the return path if a front tire is already more than 0.3 m across the marking (PP-SWR-089) | proposed |
| Maximum duration | 10 s (PP-SWR-083) | 10 s (PP-SWR-083) | agreed |

### 7.1 Completion conditions (COMPLETED)

**Basis** for the PP-SWR-090 completion conditions. The values are design choices. R79 5.6.2.2.3 and EU 2021/646 3.6.3.1 require avoiding abrupt loss of steering assistance. The main criterion is a **smooth handover**, with added a_y returning close to zero.

**Example calculation** uses a quintic path from LKA activation (TLC = 1.0 s) to lane center. Each cell lists peak a_y / peak jerk / 0.5 s moving-average jerk.

| v_lat at activation | T = 2 s | T = 3 s | T = 4 s |
|---|---|---|---|
| 0.2 m/s | 1.26 m/s² / 6.3 / 2.8 m/s³ | 0.65 / 2.1 / 1.2 | 0.41 / 1.0 / 0.7 |
| 0.4 m/s | 1.36 / 6.6 / 2.8 | 0.78 / 2.5 / 1.5 | 0.54 / 1.3 / 0.9 |
| 0.6 m/s | 1.47 / 6.9 / 2.9 | 0.91 / 2.8 / 1.7 | 0.66 / 1.5 / 1.1 |

- At T = 2 s, peak jerk exceeds 5 m/s³.
- At T = 3 s, the path is smooth and a_y stays below 1 m/s².
- At T = 4 s, the path is smoother and the vehicle comes closer to the marking (0.10–0.16 m clearance versus 0.13–0.28 m at T = 3 s).

This gives **T ≈ 3 s for LKA** (rationale for PP-SWR-081).

**Approach.** Once path duration T has elapsed, G1 checks the PP-SWR-090 conditions and deviation from the target ≤ 0.1 m. After the conditions hold continuously for 0.5 s, it reports COMPLETED. The controller and EPS then ramp down torque, or G1 transitions smoothly to HWA (PP-SWR-033). The LKA target remains open (Path Planner Software Requirements, Section 10).

## 8. Fault handling

### 8.1 Lane model faults {#lane-faults}

See PP-SWR-120 through 125 (Path Planner Software Requirements, Section 8.1). The table gives the design.

| Fault remaining after Lane Model | Approach | Status |
|---|---|---|
| c0 and c1 noise with σ_c0 = 0.03 m and σ_c1 = 0.002, 2.5 times higher at night or in rain | Three fallback layers from Section 4.1. Start from the previous path, limit reference rate of change and penalize jerk | to be agreed |
| c0 jump of 0.3–1 m | Stitch to the previous path, limit center shift and enforce continuity thresholds | agreed |
| One marking lost (predicted, confidence decays to 0 over 2 s) | Keep the lane center using the remaining marking plus remembered width | agreed |
| Both markings lost (predicted for up to 1 s) | Follow the previous path for up to T_coast = 1 s and then mark the path invalid. Total time without real markings is about 2 s, or about 50 m at 25 m/s | agreed |
| Incorrect c2 by up to ±0.0005 1/m at long range | Fuse c2, r/v and path history with weights | agreed |
| Assumed delay of 100 ± 20 ms, actual delay unknown | Compensate with ego motion using the capture stamp (Section 3) | agreed |

**Analysis for T_coast = 1 s** (rationale for PP-SWR-124). The duration is a design choice. The references provide principles. R79 5.6.2.2.3 requires avoiding abrupt release, and the R171 summary calls for continued assistance within available limits or gradual termination. The 1 s value comes from dead-reckoning error. Without markings, the vehicle relies on ego motion, which accumulates error. At 25 m/s, consider a yaw rate bias of 0.3 °/s (about 0.005 rad/s, an injected benchmark fault) and v_y noise σ = 0.05 m/s ([Sensor Models](report.html?doc=benchmark-evaluation&lang=vi#sim-sensors)).

| Time without markings | Deviation from yaw rate bias | Deviation from v_y noise | Interpretation |
|---|---|---|---|
| 0.5 s | 0.02 m | 0.03 m | Negligible |
| 1 s | 0.06 m | 0.05 m | Still small relative to lane clearance (about 0.8 m on each side) |
| 2 s | 0.25 m | 0.10 m | Becoming significant |
| 3 s | 0.56 m | 0.15 m | May touch a marking |

Lane Model already predicts markings for up to 1 s and G1 follows the previous path for another 1 s, for about 2 s in total and about 0.3 m of deviation. Check the threshold with G4, which owns dead reckoning.

The mentor treats the IMU input as filtered, so bias contributes nearly zero deviation in the main scenario, leaving more margin at 1 s. The worst case is uncompensated bias of 1 °/s (raw Bosch SMI230 sensor offset at 25 °C). Deviation is 0.22 m after 1 s and 0.87 m after 2 s, enough to reach a marking if Lane Model already predicted it for 1 s. The benchmark tests this case to assess the safety margin.

### 8.2 Invalid or timed-out inputs

See PP-SWR-124 and 140 through 146 (Path Planner Software Requirements, Section 8.3). The receiver flags invalid inputs in Section 3, steps 1 and 2. The planner responds according to the missing input.

| Input | Approach | Status |
|---|---|---|
| Lane Model | Treat as loss of both markings (Section 8.1) | agreed |
| Perception | Only HWA center offset is affected. ADAS Functions assesses adjacent-lane safety for ELK | agreed |
| IMU, speed, steering angle or ego motion | Report the path invalid immediately because delay compensation and path stitching cannot proceed | agreed |
| Vehicle State Estimation (v_y) | Suppress LKA and ELK only | agreed |
| ADAS Functions | Treat all three features as off | agreed |
| ACC (LongitudinalPlan) | Follow Section 6.1 | proposed |
| Vehicle configuration missing at startup | Prevent startup | agreed |

## 9. Limits and constraints

Path Planner Software Requirements, Sections 5.1 and 7, define the a_y and jerk budgets and continuity and feasibility requirements (PP-SWR-001 through 004, 100 through 102 and 110 through 117). The planner enforces them as described below.

### 9.1 Budget by feature

Section 3, step 8 checks path a_y, added a_y and jerk against the controlling feature's budget. Clip a path that exceeds the budget and set lateral_limit_reached (PP-SWR-005 through 008).

### 9.2 Continuity between consecutive paths

Section 3, step 7 compares the new and previous paths over their shared time interval, using header.stamp and time_from_start. First transform the previous path into the new path's base_link using ego motion. The comparison also applies on feature transitions. See PP-SWR-100 through 102 for thresholds.

### 9.3 Feasibility

| Constraint | Approach | Requirements | Status |
|---|---|---|---|
| Front wheel angle and steering wheel rate | Check front_wheel_angle at each point in Section 3, step 8 | PP-SWR-116, 117 | agreed |
| Relationship between a_y and curvature | a_y ≈ v²·κ. Check the a_y budget from path curvature | PP-SWR-001, 110, 111 | assignment |
| Computation time | Measure on the host clock and log each cycle. The simulator uses 5 ms | PP-SWR-015, 016 | agreed |

## 10. Path Planner edge cases

Case numbers match ADAS Functions, Section 8.

| # | Situation | Path Planner response | Requirements | Status |
|---|---|---|---|---|
| 1a | HWA active and ELK requested | Transition from HWA to ELK, then back to HWA on completion. Stitch the path at each transition | PP-SWR-030, 031, 033 | to be agreed |
| 1b | Another vehicle cuts in while ego is centered | Keep the controlling feature. Lateral planning offsets the center and ACC maintains distance (Section 6.1) | PP-SWR-055 through 057 | to be agreed |
| 2 | HWA enters a curve beyond aysmax | Clip the path to aysmax and set lateral_limit_reached. Use the ELK budget if ELK is requested. Send v_max to ACC (Section 6.1) | PP-SWR-005 through 008, 151 | to be agreed |
| 3 | Driver overrides HWA | Follow current vehicle position and generate a new path from it when the driver releases | PP-SWR-039, 040 | agreed |
| 4 | ELK during an intentional lane change with an overtaking vehicle | Return to the previous lane within the ELK budget only when ADAS Functions requests it under the stricter rule | PP-SWR-089, 111 | proposed |
| 5 | Request canceled by turn signal | Stop the intervention path and return to HWA if available, otherwise NONE | PP-SWR-036, 037 | agreed |
| 6 | Repeated drift back and forth | Generate a new intervention path for each new request | PP-SWR-034, 035 | agreed |
| 7 | Lane model reports a lane change | Move the reference to the new lane and stitch the path | PP-SWR-061 | agreed |
| 8 | c0 jump | Stitch the path and limit center shift | PP-SWR-121 | agreed |
| 11 | Both markings lost during intervention | Follow the previous path for up to T_coast = 1 s, then report an invalid path | PP-SWR-124 | agreed |
| 13b | Low-speed congestion | HWA continues if enabled. At 8 m/s the 3 s horizon covers just 24 m. Below 3–5 m/s the vehicle model switches to kinematic | PP-SWR-054 | proposed |
| 14 | FunctionRequests exceeds the 75 ms timeout | Treat all three features as off | PP-SWR-145 | agreed |
| 16 | Driver steers sharply and ADAS Functions suppresses LKA and ELK | HWA, if enabled, treats this as a driver override | PP-SWR-039 | proposed |

## 11. Open decisions

Path Planner Software Requirements, Section 10, tracks open requirements such as thresholds, the LKA target and DTLE margin allocation. This list covers design decisions.

1. **Interpolation** between path points (Section 2.2).
2. **Fallback layers for residual lane model noise** (Section 4.1).
3. **Initial path state** (Section 4.2). Option C and a shared function with ADAS Functions.
4. **HWA center offset** (Section 6). Clearance-balancing formula, start timing (TTC 3 s) and return timing (wait 1 s).
5. **Longitudinal interface** (Section 6.1). Fields of LateralLimits and LongitudinalPlan, and ACC stub parameters.
6. **Completion conditions** (Section 7.1). How to check deviation from the target.
7. **Cycle deadline** (Section 3.1). t0 + 5 ms. Decide whether to drop or publish a cycle that misses the deadline.
8. **Delay after the planner** (Section 3.2). Proposal assigns the 66 ms after the planner to Lateral Controller, leaving the planner path at its current timestamp. Confirm with the Lateral Controller team.
9. **Unresolved cells in the transition table** (Section 5.1). Six open items in Path Planner Software Requirements, Section 10.

## References

- G1 assignment (`G1_Path_Planning.pdf`)
- [G1 Interfaces and Signals](report.html?doc=g1-interfaces-and-signals&lang=vi) and [Simulation Environment Design](report.html?doc=benchmark-evaluation&lang=vi#simulation-design)
- [UN Regulation No 79, OJ L 2025/3](https://upload.wikimedia.org/wikipedia/commons/f/f3/OJ_L_202500003_of_2025_-_EN_English.pdf)
- [Commission Implementing Regulation (EU) 2021/646, ELKS](https://lawplayer.com/eu/act/32021R0646)
- [Euro NCAP LSS Test Protocol v4.3](https://cdn.euroncap.com/cars/assets/euro_ncap_lss_test_protocol_v43_f2ddd5f6d6.pdf)
- [ISO 11270:2014 summary](https://standards.iteh.ai/catalog/standards/iso/808a3e9d-fc87-4892-85d1-6087e2ee3370/iso-11270-2014) (original text pending review)
- [UN Regulation No 171 (DCAS)](https://eur-lex.europa.eu/eli/reg/2025/1899/oj/eng) (original text pending review)
- Werling, Ziegler, Kammel, Thrun (2010), Optimal trajectory generation for dynamic street scenarios in a Frenet frame, ICRA

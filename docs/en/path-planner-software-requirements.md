# Path Planner Software Requirements

This report defines **what the G1 path planner must achieve**, as observed through its inputs, outputs and actual vehicle motion in the simulator. Each requirement has one sentence, an ID, a source, a verification method and a status. Path Planner Feature Design describes the implementation. Evaluation uses this report as the sole basis for scoring the planner.

**Relationship to other reports**

| Report | Relationship to this report |
|---|---|
| ADAS Functions | Determines when to intervene and sends `FunctionRequests`. These requirements apply from receipt of that message |
| Path Planner Feature Design | Describes how the planner meets these requirements. Each part references the IDs it addresses. Section 2 defines the planner interfaces |
| G1 Interfaces and Signals | Defines the schemas, units and transport conventions of the messages cited here |
| Benchmark and Evaluation | Verifies these requirements. Scenario (S…), fault (F…) and delay sweep (Q…) IDs in the Verification column refer to Sections 3, 4 and 4.1 of that report. The Requirements column in its tables is generated from the Verification column here |

## 1. Conventions {#req-conventions}

| Item | Convention |
|---|---|
| ID | `PP-SWR-nnn`. Number by group and leave room for insertions. 001–009 HWA a_y limits, 010–029 outputs and cycle, 030–049 arbitration, 050–079 HWA, 080–099 LKA and ELK, 100–119 limits, continuity and feasibility, 120–149 fault handling, and 150–169 longitudinal module. Keep IDs stable and unique. Keep removed requirements in the table and mark them `obsolete` |
| Requirement wording | Use the EARS patterns “X shall …”, “When <event>, X shall …”, “While <state>, X shall …” and “If <fault>, then X shall …”. `shall` and `shall not` are mandatory. `should` marks a recommendation that is reported without affecting the pass/fail result |
| Verification | Test runs scenarios or injects faults. Analysis uses calculations. Inspection checks documents, code or logs. Demonstration shows behavior during a run. Tests default to open loop and measure Trajectory. Mark closed-loop measurements as “Test, closed loop”. After “Test:” list comma-separated scenario S…, fault F… and delay sweep Q… IDs (Benchmark and Evaluation, Sections 3, 4 and 4.1). Put variants or details in parentheses immediately after the ID, as in S1 (a, b) or F12 (Perception). List each ID individually in place of ranges such as S4 to S8. Keywords are “all scenarios”, “all faults” and “no scenario yet”. Separate multiple methods with semicolons. This column is the sole source of traceability. The benchmark Requirements column is generated from it |
| Source | `assignment`, `mentor`, a reference with its section number, or “team” for a team decision (see Rationale) |
| Status | `proposed`, `to be agreed`, `agreed` |

## 2. Definitions {#req-definitions}

| Quantity | Definition | Status |
|---|---|---|
| Cycle | 25 ms planner cycle | mentor |
| Controlling feature | The `active_function` value in PathStatus. “HWA controls” means `active_function = HWA` | agreed |
| Path lateral deviation | Maximum lateral distance from the path to the true lane center at the same longitudinal position, measured over the 0–1 s portion of the path. Use the interval stated by a requirement when it specifies one | proposed |
| Path a_y | v²·κ at each Trajectory point, where v is longitudinal_velocity and κ is curvature at that point | proposed |
| Required a_y | v²·κ of the true lane center at the corresponding path point, with v as defined above | proposed |
| Maximum required a_y | Maximum required a_y over the path horizon (0–3 s), within the lane model view range | proposed |
| Added a_y | Path a_y minus required a_y at the same point | proposed |
| Path lateral jerk | Time derivative of path a_y, with a 0.5 s moving average | agreed |
| Consecutive paths | Compare over the overlapping time interval using header.stamp_us and time_from_start. Transform the previous path into the new path's base_link using true vehicle motion | proposed |
| DLC | As defined in ADAS Functions, Section 3, evaluated against the true lane and vehicle position in the simulator | proposed |
| DTLE | Minimum distance from the outer edge of the tire to the inner edge of the marking during an intervention. A negative value indicates encroachment (Euro NCAP) | agreed |
| Large vehicle | Object in an immediately adjacent lane with width ≥ 2.3 m, such as a truck or bus | proposed |
| δ | Tolerance around aysmax for the lateral_limit_reached flag | to be agreed |
| ε | Allowed shortfall of path a_y below aysmax when required a_y exceeds aysmax | to be agreed |
| T_flag | Maximum time from the maximum required a_y crossing the threshold to lateral_limit_reached changing value | to be agreed |

**Rationale**

- **Path lateral deviation over 0–1 s.** The controller looks ahead about 0.5 s (Path Planner Feature Design, Section 2.2), so the near part determines where the vehicle goes. The far part (2–3 s) is measured only in the requirement for incorrect curvature estimates.
- **Consecutive paths measured with true motion.** The planner uses ego motion for its own comparison (Path Planner Feature Design, Section 9.2). Evaluation uses true motion so errors in the ego-motion estimate count toward the result.
- **Large vehicle ≥ 2.3 m.** Typical passenger cars are under 2.0 m wide. Trucks and buses are about 2.5 m wide (S3 uses 2.5 m). The 2.3 m value separates the two groups. The value has no cited regulatory source.

## 3. Outputs and cycle {#req-output}

| ID | Requirement | Verification | Source | Status |
|---|---|---|---|---|
| PP-SWR-010 | The planner shall send Trajectory and PathStatus every cycle | Test: all scenarios | mentor | agreed |
| PP-SWR-011 | Trajectory shall follow Path Planner Feature Design, Section 2.2, with 31 points at 0.1 s intervals covering 0–3 s and frame_id = base_link | Inspection; Analysis: “Are points[31] dense enough?” table in Path Planner Feature Design, Section 2.2 | team | agreed |
| PP-SWR-012 | Trajectory header.stamp_us shall be the time represented by the path after lane model delay compensation | Inspection; Test: Q1 | team | agreed |
| PP-SWR-013 | With camera delay between 0–200 ms and ±20 ms jitter, the path lateral deviation shall exceed the 0-delay case by at most 0.05 m | Test: Q1 | team | proposed |
| PP-SWR-014 | header.counter shall increment by 1 after every message and wrap over 0–255 | Inspection; Test: all scenarios | team | agreed |
| PP-SWR-015 | The planner shall log computation time for every cycle | Inspection | team | agreed |
| PP-SWR-016 | The 99th percentile of per-cycle computation time on the development machine shall be ≤ 5 ms | Test: all scenarios | team | to be agreed |

**Rationale**

- **PP-SWR-010.** The mentor set the planner rate to 40 Hz, within the assignment's 20–50 Hz range.
- **PP-SWR-012, 013.** Compensating from the capture stamp leaves only ego-motion error. Path Planner Feature Design, Section 3, calculates about 0.05 m of error at 25 m when compensation uses nominal delay in place of the stamp. Requirement 013 sets that as the upper bound over the full benchmark delay sweep, except 300 ms, which exceeds the discard threshold in PP-SWR-131.
- **PP-SWR-016.** The cycle is 25 ms. The simulator models computation as 5 ms. Python on a laptop supports comparison between techniques. ECU runtime is outside this measurement.

## 4. Arbitration and transitions {#req-arbitration}

| ID | Requirement | Verification | Source | Status |
|---|---|---|---|---|
| PP-SWR-030 | The planner shall select the controlling feature in ELK > LKA > HWA order, considering only features with state = REQUEST | Test: S9 (a) | team | agreed |
| PP-SWR-031 | When the controlling feature changes, the path shall satisfy PP-SWR-100 through 102 | Test: S9, S8c (d) | assignment | agreed |
| PP-SWR-032 | When LKA or ELK meets the completion conditions in PP-SWR-090, the planner shall set intervention_phase = COMPLETED | Test: S4, S5 | team | agreed |
| PP-SWR-033 | After COMPLETED, the planner shall switch the controlling feature to HWA if HWA is in REQUEST, otherwise to NONE | Test: S9 (b) | team | agreed |
| PP-SWR-034 | If a feature remains in REQUEST after COMPLETED, the planner shall wait for its state to leave and re-enter REQUEST before starting a new intervention for that feature | Test: S16 (a, b) | team | agreed |
| PP-SWR-035 | Each new LKA or ELK intervention shall use the same limits as the first, regardless of previous intervention count | Test: S16 (c, d, e) | team | agreed |
| PP-SWR-036 | When an intervening feature leaves REQUEST before completion and HWA is in REQUEST, the planner shall end the intervention path and transition to HWA from the current state | Test: S9 (d), S8c (d) | team | agreed |
| PP-SWR-037 | When an intervening feature leaves REQUEST before completion and HWA is outside REQUEST, the planner shall set active_function = NONE and keep path_valid = true | Test: S9 (d), S8c (d) | team | agreed |
| PP-SWR-038 | The planner shall reflect FunctionRequests changes in its output within one cycle of message receipt | Test: S9, Q3 | team | proposed |
| PP-SWR-039 | While driver_override = true, the path shall start within 0.05 m of the vehicle's current lateral position | Test: S9 (c), S17 | team | proposed |
| PP-SWR-040 | When driver_override becomes false while HWA is in REQUEST, the HWA path shall start at the current vehicle position and recenter within the limit in PP-SWR-002 | Test: S9 (c), S17 | team | agreed |

**Rationale**

- **PP-SWR-031.** The assignment requires transitions among the three features to avoid step changes in the steering request.
- **PP-SWR-034.** Prevents repeat interventions while ADAS Functions is still clearing the request after the vehicle returns inside the lane.
- **PP-SWR-037.** When no feature controls, Lateral Controller and EPS ramp down torque. Keeping the path valid gives the receiver a reference during ramp-down. This controller behavior is within Lateral Controller scope.
- **PP-SWR-038.** One cycle is the benchmark response target for a timed-out input (Benchmark and Evaluation, Section 5.5). The same target applies to request changes.
- **PP-SWR-039.** Prevents steering against the driver. The 0.05 m threshold matches the lateral deviation limit between consecutive paths (PP-SWR-100). The behavior is agreed. The value is proposed.

## 5. HWA {#req-hwa}

### 5.1 a_y limit and lateral_limit_reached {#req-hwa-lateral-limit}

| ID | Requirement | Verification | Source | Status |
|---|---|---|---|---|
| PP-SWR-001 | While HWA controls, path a_y shall be ≤ aysmax = 2.5 m/s² at every point | Test: S1, S1b, S12 (a) | R79 5.6.2.1.3 | agreed |
| PP-SWR-002 | While HWA recenters or offsets the center, added a_y shall be ≤ 0.5 m/s² at every point | Test: S2, S3 | team | agreed |
| PP-SWR-003 | While HWA controls, path lateral jerk shall be ≤ 5 m/s³ | Test: S1 | R79 5.6.2.1.3 c | agreed |
| PP-SWR-004 | While HWA controls, path lateral jerk should be ≤ 2.5 m/s³ | Test: S1 | team | agreed |
| PP-SWR-005 | If maximum required a_y > aysmax while HWA controls, then the planner shall keep path_valid = true and active_function = HWA unless arbitration hands control to LKA or ELK | Test: S1b | R79 5.6.2.2.3 | to be agreed |
| PP-SWR-006 | If required a_y > aysmax at a path point while HWA controls, then path a_y at that point shall be ≥ aysmax − ε | Test: S1b | R79 5.6.2.2.3 | to be agreed |
| PP-SWR-007 | When maximum required a_y > aysmax + δ, the planner shall set lateral_limit_reached = true within T_flag | Test: S1b | team | to be agreed |
| PP-SWR-008 | When maximum required a_y < aysmax − δ, the planner shall set lateral_limit_reached = false within T_flag | Test: S1 (a, b, d, e) | team | to be agreed |
| PP-SWR-009 | The planner shall send the same lateral_limit_reached value in PathStatus and LateralLimits in the same cycle | Inspection; Test: S14 | team | proposed |

**Rationale**

- **PP-SWR-001.** R79 5.6.2.1.3 caps B1 aysmax at 3 m/s² for M1 vehicles. The team selects 2.5 m/s², 0.5 m/s² below the cap. R79 also allows exceeding aysmax by 0.3 m/s², or by 40% for up to 2 s (see Section 10).
- **PP-SWR-002.** See the calculation in ADAS Functions, Section 6.1.
- **PP-SWR-003, 004.** R79 5.6.2.1.3 c allows 5 m/s³ for B1. The team's 2.5 m/s³ comfort target is a recommendation.
- **PP-SWR-005, 006.** R79 5.6.2.2.3 requires continued assistance within available limits and prohibits abrupt release when the limit is reached.
- **PP-SWR-007, 008.** Only the planner knows whether the path is limited. ADAS Functions uses the flag to warn the driver when a tire starts to overlap the marking (R79 5.6.2.2.3 and ADAS Functions, Section 7). The planner estimates curvature from the camera, so its estimate differs from required a_y. The ± δ band prevents flag oscillation when required a_y is close to aysmax. Either flag value passes inside the band.
- **PP-SWR-009.** ACC uses the flag with v_max to slow before a curve (Path Planner Feature Design, Section 6.1). Once ACC slows enough, maximum required a_y falls and the flag clears under PP-SWR-008.

**Illustrative example.** At 90 km/h (25 m/s) on a curve with R = 200 m, required a_y = 25² / 200 = 3.1 m/s², above aysmax = 2.5 m/s². The path must therefore curve less than the road. The a_y shortfall is 0.6 m/s². The vehicle moves outward about ½ · 0.6 · 1² = 0.3 m after 1 s and 1.2 m after 2 s, leaving its lane. If ACC slows to v_max = √(2.5 × 200) = 22.4 m/s, required a_y falls to 2.5 m/s², equal to aysmax.

### 5.2 Lane centering and recentering {#req-hwa-centering}

| ID | Requirement | Verification | Source | Status |
|---|---|---|---|---|
| PP-SWR-050 | While HWA controls with maximum required a_y ≤ aysmax and no large vehicle in an adjacent lane, path lateral deviation shall be ≤ 0.1 m | Test: S1 (a, b, d, e), S11 | assignment | proposed |
| PP-SWR-051 | While HWA controls with maximum required a_y ≤ aysmax, DLC on both sides shall be ≥ 0 | Test, closed loop: S1 | R79 5.6.2.1.1 | agreed |
| PP-SWR-052 | When HWA starts controlling with the vehicle up to 0.5 m off center, HWA shall remain the controlling feature throughout recentering | Test: S2 | team | agreed |
| PP-SWR-053 | When HWA starts controlling with the vehicle up to 0.5 m off center, path lateral deviation shall fall to ≤ 0.1 m within 5 s | Test: S2 | team | proposed |
| PP-SWR-054 | While HWA is in REQUEST at 0–60 km/h, the planner shall continue to send a valid HWA path | Test: S11 | team | proposed |

**Rationale**

- **PP-SWR-050.** The assignment requires a continuous, smooth lane-center path. PP-SWR-100 through 102 cover continuity and PP-SWR-003 and 004 cover smoothness. This requirement quantifies centering. The 0.1 m threshold is about 3 daytime camera c0 standard deviations (3 × 0.03 = 0.09 m) and matches the benchmark for misdetected markings and lane widening. A 3.5 m lane and 1.9 m vehicle leave 0.8 m of clearance on each side. The 0.1 m threshold is about 12% of that clearance.
- **PP-SWR-051.** R79 5.6.2.1.1 requires the system to keep the vehicle clear of markings below aysmax. This vehicle-level requirement is measured in closed loop, including tracking error from the test controller.
- **PP-SWR-052.** HWA handles recentering on its own.
- **PP-SWR-053.** Recentering from 0.5 m at added a_y ≤ 0.5 m/s² takes at least about 2.4 s (Path Planner Feature Design, Section 6). The 5 s limit gives the path time to respect the jerk limit.
- **PP-SWR-054.** Highway congestion (S11). Below 10 km/h, the 3 s horizon covers little distance. HWA still needs to maintain its lane when enabled by the driver.

### 5.3 Center offset beside a large vehicle {#req-hwa-offset}

| ID | Requirement | Verification | Source | Status |
|---|---|---|---|---|
| PP-SWR-055 | While a large vehicle is in an adjacent lane, the path's deviation from the true lane center shall be ≤ 0.3 m | Test: S3, S3b, S15 | assignment | to be agreed |
| PP-SWR-056 | While offsetting the center, the path shall shift only toward the side with more clearance | Test: S3b, S15 | mentor | to be agreed |
| PP-SWR-057 | While offsetting the center, DLC of the vehicle following the path shall be ≥ 0.3 m on both sides | Test: S3b, S15 | team | to be agreed |
| PP-SWR-058 | When a large vehicle in an adjacent lane is approaching, the path shall start shifting before the large vehicle is alongside | Test: S3 | assignment | to be agreed |
| PP-SWR-059 | After the rear of the large vehicle has passed, path lateral deviation shall return to ≤ 0.1 m within 4 s | Test: S3 | team | proposed |

**Rationale**

- **PP-SWR-055, 058.** The assignment requires HWA to offset early when passing a large vehicle. The team sets the 0.3 m limit.
- **PP-SWR-056.** Mentor guidance for S3b is to avoid steering toward a vehicle on the opposite side. Clearance is the distance from the ego vehicle body to the nearest object on that side, or to the true lane boundary if that side is clear.
- **PP-SWR-059.** Returning 0.3 m at added a_y ≤ 0.5 m/s² takes at least √(5.77 × 0.3 / 0.5) ≈ 1.9 s (same formula as Path Planner Feature Design, Section 6). The 4 s limit includes a wait before returning.

### 5.4 Lane changes and widening {#req-hwa-lane-change}

| ID | Requirement | Verification | Source | Status |
|---|---|---|---|---|
| PP-SWR-060 | When one lane boundary widens at an emergency shoulder, a split or an added lane, path lateral deviation toward the widened side shall be ≤ 0.1 m | Test: S6b | mentor | proposed |
| PP-SWR-061 | When the lane model switches to a new lane, the path shall satisfy PP-SWR-100 through 102 | Test: S17 | team | agreed |

**Rationale**

- **PP-SWR-060.** Mentor guidance is to avoid shifting toward the widened side. The 0.1 m threshold matches the current benchmark (Benchmark and Evaluation, Section 5.5).

## 6. LKA and ELK {#req-intervention}

| ID | Requirement | Verification | Source | Status |
|---|---|---|---|---|
| PP-SWR-080 | When LKA or ELK starts intervening, the path shall start within 0.1 m and 0.1 m/s of the vehicle's true lateral position and v_lat, respectively | Test: S4, S5, S6 | assignment | proposed |
| PP-SWR-081 | The time from the start of an LKA intervention path to COMPLETED should be ≤ 4 s | Test: S4 | team | proposed |
| PP-SWR-082 | The time from the start of an ELK intervention path to COMPLETED should be ≤ 3.5 s | Test: S5, S6, S7, S8, S8b (d, e) | team | proposed |
| PP-SWR-083 | An LKA or ELK intervention shall end in COMPLETED or cancellation within ≤ 10 s | Test: S4, S4b, S5, S6, S7, S8, S8b (d, e) | R79 5.1.6.1.2.1 | agreed |
| PP-SWR-084 | When LKA reports COMPLETED, DLC on the side of the preceding drift shall be ≥ 0.5 m | Test: S4 | assignment | to be agreed |
| PP-SWR-085 | After an LKA or ELK intervention, minimum DLC on the opposite side shall be ≥ 0.3 m | Test: S4, S4b, S5, S6, S7, S8, S8b (d, e) | assignment | proposed |
| PP-SWR-086 | Minimum DTLE during an intervention shall be ≥ −0.3 m for LKA and solid-line ELK, and ≥ −0.1 m for road-edge ELK | Test, closed loop: S4, S5, S6 | Euro NCAP Assessment 4.3.2, 4.3.3.3; EU 2021/646 3.6.2 | agreed |
| PP-SWR-087 | Minimum DTLE for LKA should be ≥ 0 in mode B in daylight | Test, closed loop: S4 | team | proposed |
| PP-SWR-088 | During ELK intervention for a vehicle in the adjacent lane, minimum lateral clearance to that vehicle shall be ≥ 0.3 m | Test, closed loop: S7, S8 | Euro NCAP 4.3.3.4; LSS 7.4.7 | agreed |
| PP-SWR-089 | If ELK is requested when a front tire is already more than 0.3 m beyond the marking indicated by side, the planner shall not generate a path that pulls the vehicle back into its previous lane | Test: S8 | team | proposed |
| PP-SWR-090 | The planner shall report COMPLETED only after v_lat within ±0.1 m/s, heading error relative to the lane within ±0.5° and added a_y ≤ 0.2 m/s² all hold continuously for 0.5 s | Test: S4, S5 | team | proposed |
| PP-SWR-091 | With EPS delay up to 100 ms, minimum DTLE shall still satisfy PP-SWR-086 | Test, closed loop: S13 (a, b) | team | proposed |

**Rationale**

- **PP-SWR-080.** The assignment requires the intervention path to start from the drifting state. The 0.1 m limit is about 3 times the daytime camera σ_c0 = 0.03 m. The 0.1 m/s limit is 2 times the v_y σ = 0.05 m/s (Benchmark and Evaluation, Sensor Models).
- **PP-SWR-081, 082.** Path Planner Feature Design, Section 7.1, calculates that an LKA path of about 3 s is smooth with a_y below 1 m/s². Add the 0.5 s hold in PP-SWR-090 and a 0.5 s margin to get 4 s. ELK targets 1–3 s plus 0.5 s, yielding 3.5 s.
- **PP-SWR-083.** R79 5.1.6.1.2.1 requires an audible warning for interventions longer than 10 s.
- **PP-SWR-084.** The assignment says “back inside the lane, then release to the driver”. The target is open between DLC ≥ 0.5 m and lane center (Section 10).
- **PP-SWR-085.** The assignment says “no overshoot into the other lane”.
- **PP-SWR-086.** This vehicle-level requirement is measured in closed loop with the test controller and EPS. The planner's share of the margin remains to be allocated (Section 10).
- **PP-SWR-089.** R79 5.1.6.2.3.1 permits ELK to return the vehicle to the original lane. Once the tire has crossed too far, pulling back is riskier than continuing.
- **PP-SWR-090.** The numerical values are design choices. R79 5.6.2.2.3 and EU 2021/646 3.6.3.1 require avoiding abrupt loss of steering assistance. Added a_y should therefore approach zero for a smooth handover.
- **PP-SWR-091.** Nominal actuator delay is 50 ms (vehicle configuration). The 100 ms case doubles it to give the planner margin for a slower actuator. Record the 150 ms result for information. The test controller is fixed across planner versions so differences reflect each planner's margin.

## 7. Limits, continuity and feasibility {#req-limits}

| ID | Requirement | Verification | Source | Status |
|---|---|---|---|---|
| PP-SWR-100 | While path_valid = true, lateral difference between consecutive paths shall be ≤ 0.05 m | Test: all scenarios, all faults | assignment | agreed |
| PP-SWR-101 | While path_valid = true, heading difference between consecutive paths shall be ≤ 0.005 rad | Test: all scenarios, all faults | assignment | agreed |
| PP-SWR-102 | While path_valid = true, curvature difference between consecutive paths shall be ≤ 0.0003 1/m | Test: all scenarios, all faults | assignment | agreed |
| PP-SWR-110 | While LKA controls, path a_y shall be ≤ 3.0 m/s² | Test: S4, S4b | team | agreed |
| PP-SWR-111 | While ELK controls, path a_y shall be ≤ 4.0 m/s² | Test: S5, S6, S7, S8, S8b (d, e) | team | agreed |
| PP-SWR-112 | While LKA controls, added a_y shall be ≤ 1.5 m/s² | Test: S4, S4b | team | agreed |
| PP-SWR-113 | While ELK controls, added a_y shall be ≤ 3.0 m/s² | Test: S5, S6, S7, S8, S8b (d, e) | team | agreed |
| PP-SWR-114 | While LKA controls, path lateral jerk shall be ≤ 5 m/s³ | Test: S4, S4b | ISO 11270 (secondary source) | agreed |
| PP-SWR-115 | While ELK controls, path lateral jerk shall be ≤ 10 m/s³ | Test: S5, S6, S7, S8, S8b (d, e) | team | agreed |
| PP-SWR-116 | front_wheel_angle shall be ≤ 0.61 rad at every path point | Test: all scenarios | vehicle configuration | agreed |
| PP-SWR-117 | The steering wheel rate inferred from the path (rate of change of front_wheel_angle times steering ratio 15) shall be ≤ 6 rad/s | Test: all scenarios | vehicle configuration | agreed |

**Rationale**

- **PP-SWR-100 through 102.** The assignment prohibits steering request steps, including on feature changes and lane model jumps. A heading difference of 0.005 rad causes about 6 cm of lateral difference at a 0.5 s lookahead. A curvature difference of 0.0003 1/m produces a steering wheel step of about 0.75°.
- **PP-SWR-110, 111.** R79 sets no a_y limit for CSF. The 4.0 m/s² ELK limit leaves a margin on wet roads with μ = 0.5 and a grip limit of about 4.9 m/s².
- **PP-SWR-112, 113.** See the calculation in ADAS Functions, Section 6.1.
- **PP-SWR-114, 115.** The LKA value comes from the ISO 11270 summary. The regulations give no ELK value.
- **PP-SWR-116, 117.** Maximum wheel angle and steering wheel rate come from the vehicle configuration (Path Planner Feature Design, Section 2.1).

Lateral Controller and EPS own the override force limit (≤ 50 N under R79 5.6.2.1.3 a, 5.1.6.1.3 and 5.1.6.2.8, and EU 2021/646 3.6.3.1).

## 8. Fault handling {#req-faults}

### 8.1 Lane model faults {#req-lane-faults}

| ID | Requirement | Verification | Source | Status |
|---|---|---|---|---|
| PP-SWR-120 | When lane model c0 and c1 noise reaches nighttime levels (2.5 times daytime), the path shall meet the controlling feature's jerk limit and PP-SWR-100 through 102 | Test: F01 | team | agreed |
| PP-SWR-121 | When c0 jumps by 0.3–1.0 m in one frame, the path shall meet PP-SWR-100 through 102 | Test: F02 | assignment | agreed |
| PP-SWR-122 | When the lane model misidentifies a marking from an adjacent lane, path lateral deviation shall be ≤ 0.1 m | Test: F03 | team | proposed |
| PP-SWR-123 | When the lane model loses one marking, path lateral deviation shall be ≤ 0.1 m except while lane width changes | Test: F04 (a–d) | team | proposed |
| PP-SWR-124 | When the lane model loses both markings or is invalid, the planner shall keep path_valid = true for T_coast = 1 s and then set path_valid = false, with timing error of at most one cycle | Test: F05, F12 (Lane Model) | team | agreed |
| PP-SWR-125 | When the lane model has incorrect c2, path lateral deviation over 2–3 s should be ≤ 50% of the deviation of a path that exactly follows that incorrect lane model | Test: F06 | assignment | proposed |

**Rationale**

- **PP-SWR-120.** Residual noise after Lane Model is σ_c0 = 0.03 m and σ_c1 = 0.002 in daylight, and 2.5 times higher at night or in rain.
- **PP-SWR-121.** The assignment requires a smooth path when the lane model jumps. Lane Model supplies no jump flag.
- **PP-SWR-122, 123.** The 0.1 m limit matches PP-SWR-050. If lane width changes as a marking disappears, a center reconstructed from one marking may deviate more. Record that result for information.
- **PP-SWR-124.** T_coast = 1 s follows from dead-reckoning error of about 0.06 m after 1 s with a yaw rate bias of 0.3 °/s at 25 m/s (Path Planner Feature Design, Section 8.1). The duration is a design choice. R79 5.6.2.2.3 requires avoiding abrupt release.
- **PP-SWR-125.** The assignment requires testing incorrect c2. Following the incorrect lane model exactly gives a worst-case reference that evaluation can calculate. The 50% design target shows whether the planner uses information from other sources.

### 8.2 Timing and integrity faults {#req-timing-faults}

| ID | Requirement | Verification | Source | Status |
|---|---|---|---|---|
| PP-SWR-126 | When messages are lost individually or in bursts, or have ±20 ms jitter, the path shall satisfy PP-SWR-100 through 102 and the controlling feature's jerk limit | Test: F10 | team | agreed |
| PP-SWR-127 | When a message arrives late or out of order, the path shall satisfy PP-SWR-100 through 102 | Test: F11 | team | agreed |
| PP-SWR-128 | While the camera sends at 20 Hz and the planner runs at 40 Hz, the path shall satisfy PP-SWR-100 through 102 on every cycle | Test: all scenarios, F13 | team | agreed |
| PP-SWR-129 | If a message is duplicated (repeated counter), the output shall match the fault-free case with the same seed | Test: F15 (repeat) | team | agreed |
| PP-SWR-130 | If the counter skips or stalls, valid = false, the qualifier is FAULT or the CRC fails, the output shall match the corresponding message-loss case | Test: F15 (skip, stall), F16, F17 | team | agreed |
| PP-SWR-131 | If lane model or ObjectList age exceeds 250 ms, the planner shall treat that input as invalid | Test: Q1 (300 ms) | team | agreed |
| PP-SWR-132 | If an input stamp is more than 10 ms in the future, the planner shall treat that input as invalid | Test: F19 | team | agreed |
| PP-SWR-133 | While lane model or ObjectList age is within 170–250 ms, the planner shall continue using that input | Test: Q1 (200 ms) | team | agreed |
| PP-SWR-134 | The planner shall log the count of lane model and ObjectList frames older than 170 ms | Inspection | team | agreed |

**Rationale**

- **PP-SWR-131 through 134.** Actual delay is unknown (mentor). The 170 ms threshold is the assumed maximum delay of 120 ms plus 50 ms. The 250 ms threshold is the largest benchmark sweep delay (200 ms) plus 50 ms. Path Planner Feature Design, Section 3, gives three checks for 250 ms. The 10 ms threshold is the maximum clock offset before initial synchronization.

### 8.3 Invalid or timed-out inputs {#req-invalid-input}

| ID | Requirement | Verification | Source | Status |
|---|---|---|---|---|
| PP-SWR-140 | If ObjectList is invalid, the planner shall return the HWA center offset to 0 within the limit in PP-SWR-002 | Test: F12 (Perception, in S3) | team | agreed |
| PP-SWR-141 | If ObjectList is invalid, the planner shall still perform a requested ELK intervention | Test: F12 (Perception, in S5) | team | agreed |
| PP-SWR-142 | If IMU, speed or steering angle is invalid, the planner shall set path_valid = false within one cycle | Test: F12 (IMU, speed, steering angle), F17 | team | agreed |
| PP-SWR-143 | If ego motion is invalid, the planner shall set path_valid = false within one cycle | Test: F20 | team | agreed |
| PP-SWR-144 | If VehicleStateEstimate is invalid, the planner shall continue HWA and shall not select LKA or ELK as the controlling feature | Test: F12 (v_y) | team | agreed |
| PP-SWR-145 | If FunctionRequests exceeds the 75 ms timeout, the planner shall set active_function = NONE and path_valid = false within one cycle | Test: F12 (FunctionRequests) | team | agreed |
| PP-SWR-146 | If vehicle configuration is missing at startup, the planner shall not send Trajectory | Demonstration | team | agreed |

**Rationale**

- **PP-SWR-140, 141.** ADAS Functions assesses adjacent vehicles for ELK, so G1 can perform ELK without ObjectList.
- **PP-SWR-142, 143.** Delay compensation and path stitching require IMU, speed, steering angle and ego motion.
- **PP-SWR-145.** Reporting an invalid path lets the receiver ramp down torque.

### 8.4 Vehicle signal and clock faults {#req-signal-faults}

| ID | Requirement | Verification | Source | Status |
|---|---|---|---|---|
| PP-SWR-135 | When IMU noise reaches twice the datasheet level, the path shall still satisfy PP-SWR-050 and 100 through 102 | Test: F07 (a, b) | team | proposed |
| PP-SWR-136 | When yaw rate has bias up to 0.3 °/s, the path shall still satisfy PP-SWR-050 and 100 through 102 | Test: F08 (a, b) | team | proposed |
| PP-SWR-137 | When clock drift reaches ±100 ppm or gPTP synchronization is lost for up to 10 s, the path shall still satisfy PP-SWR-050 and 100 through 102 | Test: F14 (a, b, c) | team | proposed |
| PP-SWR-138 | When filtered yaw rate is delayed by up to 50 ms without the planner being told of the delay, the path shall still satisfy PP-SWR-050 and 100 through 102 | Test: Q2 (0–50 ms) | team | proposed |
| PP-SWR-139 | While CAN signals are quantized according to the DBC scale, the path shall still satisfy PP-SWR-050 and 100 through 102 | Test: all scenarios, F18 | team | proposed |

**Rationale**

- **PP-SWR-135 through 139.** These faults occur at the stated levels on real vehicles. Existing centering and continuity limits still apply. The thresholds are independent of the design calculations so the planner is evaluated independently of its own assumptions. Record the worst benchmark cases (F08 c, Q2 100 ms) for information.
- **PP-SWR-135.** F07 a follows the Bosch SMI230 datasheet. Variant b doubles it for margin. The mentor indicates that the IMU signal reaches the planner already filtered, so this checks the boundary.
- **PP-SWR-136.** Residual bias after incomplete compensation is 0.3 °/s. The 1 °/s offset of the uncompensated raw sensor is recorded for information only.
- **PP-SWR-137.** A drift of 100 ppm over 10 s gives just 1 ms of offset, below the ±20 ms jitter already covered by PP-SWR-126.
- **PP-SWR-138.** Actual filter delay is unknown (mentor). The 50 ms value is the middle of the benchmark sweep. Record the 100 ms result for information. The value has no cited regulatory source.
- **PP-SWR-139.** Quantization occurs on real vehicles. Existing thresholds quantify the benchmark's “no significant effect” criterion.

## 9. Interface to the longitudinal module {#req-longitudinal}

| ID | Requirement | Verification | Source | Status |
|---|---|---|---|---|
| PP-SWR-150 | The planner shall send LateralLimits every cycle | Test: S14 | team | proposed |
| PP-SWR-151 | LateralLimits.v_max shall equal √(controlling feature a_y budget / κ_max), where κ_max is the maximum curvature of the true lane center within the lane model view range, with error ≤ 5% | Test: S14 | team | proposed |
| PP-SWR-152 | LateralLimits.distance shall equal the longitudinal distance to the point with κ_max, with error ≤ 5 m | Test: S14 | team | proposed |
| PP-SWR-153 | When LongitudinalPlan is valid, Trajectory longitudinal_velocity and acceleration shall come from LongitudinalPlan | Test: S14 | team | proposed |
| PP-SWR-154 | If LongitudinalPlan is missing or exceeds the 75 ms timeout, Trajectory shall use current speed held constant and acceleration 0 | Test: S14 (d) | team | proposed |
| PP-SWR-155 | If LongitudinalPlan is missing or exceeds the 75 ms timeout, the planner shall keep path_valid = true | Test: S14 (d) | team | proposed |

**Rationale**

- **PP-SWR-151.** An error of 5% in v gives about 10% error in a_y, or about 0.25 m/s² at 2.5 m/s². The value has no cited regulatory source.
- **PP-SWR-152.** At 90 km/h, 5 m is about two path points (0.1 s spacing, 2.5 m per point).
- **PP-SWR-155.** Lateral planning can run without a longitudinal plan (Path Planner Feature Design, Section 6.1).

## 10. Open decisions {#req-open}

Resolve each item before implementing the related code.

| Item | Blocked requirements | Owner |
|---|---|---|
| δ value. It must exceed the required a_y estimation error due to camera c2 noise at 90–130 km/h | PP-SWR-007, 008 | G1 team, from the camera noise model (Benchmark and Evaluation, Section 9) |
| ε value | PP-SWR-006 | G1 team |
| T_flag value. Include assumed lane model delay (Path Planner Feature Design, Section 2.1) and one cycle | PP-SWR-007, 008 | G1 team. Update when actual delay is available |
| Whether lateral_limit_reached needs a minimum hold time to avoid oscillation | PP-SWR-007, 008 | G1 team with ADAS Functions (warnings) |
| v_max currently targets the exact a_y budget. After ACC slows down, maximum required a_y lies in the aysmax ± δ band, so the flag may stay set | PP-SWR-008, 009, 151 | G1 team |
| Whether the R79 tolerance above aysmax (0.3 m/s², or 40% for up to 2 s) applies to path a_y or measured vehicle a_y. Benchmark and Evaluation, Section 5.2, currently applies it to the path | PP-SWR-001 | G1 team, check the original R79 5.6.2.1.3 text |
| LKA target. Choose DLC ≥ 0.5 m (early handover as intended by the assignment) or lane center (longer) | PP-SWR-084 | G1 team |
| When LKA or ELK starts while an HWA path is active and the vehicle has deviated from it, PP-SWR-031 (continuity with the previous path) and PP-SWR-080 (matching the true state) may conflict. Choose which requirement takes priority | PP-SWR-031, 080 | G1 team |
| Allocate the PP-SWR-086 DTLE margin among path, controller tracking error and EPS delay | PP-SWR-086 | G1 team with Lateral Controller team |
| Planner behavior when it cannot pull the vehicle back into the original lane | PP-SWR-089 | G1 team with ADAS Functions |
| How ADAS Functions learns that LKA and ELK are unavailable when VehicleStateEstimate is invalid | PP-SWR-144 | G1 team with ADAS Functions |
| Large vehicle definition (≥ 2.3 m) | PP-SWR-055 through 059 | G1 team |
| If ELK completes or is canceled with LKA still in REQUEST, choose LKA (PP-SWR-030) or HWA (PP-SWR-033 and 036). Proposed choice is PP-SWR-030 | PP-SWR-030, 033, 036 | G1 team with ADAS Functions |
| How long intervention_phase stays COMPLETED. Proposed duration is until that feature leaves REQUEST, matching PP-SWR-034 | PP-SWR-032, 034 | G1 team with ADAS Functions |
| path_valid when HWA leaves REQUEST and no feature controls. Proposed value is true, as in PP-SWR-037 | PP-SWR-030, 037 | G1 team |
| active_function when the path is invalid. Proposed value is NONE | PP-SWR-124, 142, 143 | G1 team with ADAS Functions |
| Planner behavior when input recovers after an invalid path. Proposed behavior is to plan from true vehicle state, select the feature per PP-SWR-030 and require a new request for LKA or ELK | PP-SWR-124, 142, 143 | G1 team |
| Whether ending an intervention immediately on invalid VehicleStateEstimate (PP-SWR-144) is safe, especially during ELK avoidance | PP-SWR-144 | G1 team |

## References

- G1 assignment (`G1_Path_Planning.pdf`)
- [Path Planner Feature Design](report.html?doc=path-planner-feature-design&lang=vi), [ADAS Functions](report.html?doc=adas-functions&lang=vi), [Benchmark and Evaluation](report.html?doc=benchmark-evaluation&lang=vi)
- [UN Regulation No 79, OJ L 2025/3](https://upload.wikimedia.org/wikipedia/commons/f/f3/OJ_L_202500003_of_2025_-_EN_English.pdf)
- [Commission Implementing Regulation (EU) 2021/646, ELKS](https://lawplayer.com/eu/act/32021R0646)
- [Euro NCAP LSS Test Protocol v4.3](https://cdn.euroncap.com/cars/assets/euro_ncap_lss_test_protocol_v43_f2ddd5f6d6.pdf)
- [Euro NCAP Assessment Protocol Safety Assist Collision Avoidance v10.4.1](https://cdn.euroncap.com/cars/assets/euro_ncap_assessment_protocol_sa_collision_avoidance_v1041_fafe1dd418.pdf)
- [ISO 11270:2014 summary](https://standards.iteh.ai/catalog/standards/iso/808a3e9d-fc87-4892-85d1-6087e2ee3370/iso-11270-2014) (original text pending review)
- Mavin et al. (2009), Easy Approach to Requirements Syntax (EARS), IEEE International Requirements Engineering Conference

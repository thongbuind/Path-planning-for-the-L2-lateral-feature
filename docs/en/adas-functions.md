# ADAS Functions — When HWA, LKA and ELK May Intervene

This report specifies the **ADAS Functions** module **at its output boundary**. It defines which requests the module sends to the Path Planner in each situation and the numerical thresholds for those requests. The assignment places this module outside G1 scope. The project still needs a simulation stub so test scenarios can determine when to activate each feature.

**Production module and simulation stub.** The production module reads the lane model, detected objects, vehicle signals and driver inputs. It handles filtering, driver intent monitoring and the HMI before sending requests. The G1 simulator stub **classifies situations using the thresholds in this report** and sends the same `FunctionRequests` message as the production module. It operates without an in-cabin camera, machine learning or a production HMI.

**Relationship to the other two reports**

| Report | Question it answers | Connection to this report |
|---|---|---|
| ADAS Functions (this report) | **When** each feature requests intervention and on which side | Sends `FunctionRequests` to the Path Planner and receives `PathStatus` |
| Path Planner Feature Design | **How** to intervene, including arbitration, path generation, a_y and jerk limits, completion and fault handling | Uses TLC, side and driver_override from this report. Reports COMPLETED and the controlling feature back |
| Benchmark and Evaluation | **How to evaluate** the planner using scenarios, fault injection, metrics and pass thresholds | Uses the ADAS stub in mode B (Section 9) to evaluate G1 and mode A to test the full chain. Runs all three LKA TLC threshold candidates |

## 1. Regulatory and test references

| Reference | Description | Application |
|---|---|---|
| UN R79, OJ L 2025/3 | Steering equipment approval regulation, mandatory for vehicles subject to UNECE type approval | HWA is ACSF Category B1 (Section 5.6.2). LKA and boundary-triggered ELK are CSF (Section 5.1.6.1). Object-triggered ELK is ESF (Section 5.1.6.2). Covers the 50 N override force and warnings |
| EU 2021/646 (ELKS) | EU regulation requiring ELKS on all new vehicles, applicable from 6 July 2022 | 70–130 km/h operating range, default activation, deactivation procedure and permitted intervention suppression conditions |
| Euro NCAP LSS Test Protocol v4.3 and Assessment Protocol Safety Assist v10.4.1 | Voluntary star-rating tests targeted by manufacturers | Test scenarios (72 km/h, v_lat 0.2–0.6 m/s), DTLE thresholds, 3.5 Nm override torque and ELK with a turn signal active |
| ISO 17361:2017 (LDWS) | Lane departure warning standard | The warning must occur between the earliest and latest warning lines. **Based on secondary sources** (Section 6.1) |
| ISO 21448:2022 (SOTIF) | Safety of the intended functionality, addressing risks from sensor and algorithm limitations in the absence of faults | Basis for Section 3.1. Identify conditions that degrade perception and prevent unintended activation. **Original text pending review.** The standard gives no numerical thresholds |
| UN R171 (DCAS) | New regulation for combined lateral and longitudinal driver assistance, the category covering HWA | Conditions for entering the active state. **Original text pending review** |

The features map to the regulatory categories below.

| Feature | Regulatory category | How it is enabled | Status |
|---|---|---|---|
| HWA | ACSF Category B1 (R79), continuous assistance to keep the vehicle in its lane. Also within R171 scope when combined with ACC | The driver presses a button with ACC already on. A single action disables it (R79 5.6.2.1.2) | agreed |
| LKA | Lane-marking-based CSF (R79 2.3.4.2 c) | On by default. The driver can disable it in a menu | agreed |
| ELK for solid lines and road edges | CSF and ELKS | On at each vehicle start. Deactivation requires at least two deliberate actions. It is reenabled at the next startup (EU 2021/646, Annex I, 3.2.1) | agreed |
| ELK for oncoming and overtaking vehicles | ESF (R79 2.3.4.3 a), collision avoidance for vehicles in adjacent lanes | Same as above | agreed |

## 2. Responsibilities of ADAS Functions and G1 {#adas-role}

| Task | ADAS Functions | G1 Path Planner |
|---|---|---|
| Read settings for the HWA button and LKA and ELK menus | Reads them | Has no access |
| Check eligibility, including speed, ACC, marking quality, ESC and input faults | Checks it (Section 4) | Receives only the resulting state of each feature |
| Filter noise and fuse sensor sources | Uses markings already filtered by Lane Model, v_y estimated by Vehicle State Estimation (G2) and motion computed by Ego-motion (G4). Each producer sends variances. **Handles residual errors** using variances, the rules in Section 3.1, the boundary consistency check shared with G1, and each marking's status and confidence | Uses upstream estimates and handles residual lane model errors (Path Planner Software Requirements, Section 8) |
| Compute DLC, v_lat and TLC on both sides, including uncertainty | Computes them (Section 3) | Uses TLC to choose path duration |
| Assess danger beyond the marking | Assesses it (Sections 3.2 and 6) | — |
| Infer driver intent | Infers it (Section 5) | Receives only driver_override |
| Warn the driver under R79 | Issues warnings (Section 7) | Reports when the path reaches the a_y limit |
| Arbitrate, generate the path, enforce limits, detect completion and handle faults | — | Performs these tasks (Path Planner Feature Design) |
| Brake or reduce speed (ACC, AEB) | Outside G1 scope | Outside G1 scope. As in the vehicle, separate lateral and longitudinal modules exchange constraints. The simulator uses an ACC stub (Path Planner Feature Design, Section 6.1) |
| Limit steering torque and keep override force ≤ 50 N | — | The **path must stay within the budgets** for a_y, jerk, steering angle and steering rate (Path Planner Software Requirements, Sections 5.1 and 7). The controller can then track it within the torque limit and the driver can still override |

## 3. Quantities computed by ADAS Functions

v is vehicle speed, v_y is lateral velocity at the rear axle center, r is yaw rate, x_f is the distance from the rear axle center to the front axle (the wheelbase) and W is vehicle width. The left marking in base_link is `y_L(x) = c0 + c1·x + c2·x² + c3·x³`, with y positive to the left.

| Quantity | Calculation | Meaning | Status |
|---|---|---|---|
| DLC_L | `y_L(x_f) − W/2` | Remaining distance from the outer edge of the front left tire to the inner edge of the left marking. Uses the Euro NCAP DTLE definition under a different name | proposed |
| v_lat_L | `v_y + r·x_f − v·y_L'(x_f)`, with `y_L'(x) = c1 + 2·c2·x + 3·c3·x²` | Rate at which DLC_L decreases, or the vehicle's closing speed toward the left marking. Uses marking angle from the camera, v_y from state estimation and r from the IMU | proposed |
| TLC_L | `DLC_L / v_lat_L` if v_lat_L ≥ 0.05 m/s, otherwise infinity | Time to reach the marking, assuming constant v_lat (the same assumption as for DTLE) | proposed |
| Right side | Symmetric formulas `DLC_R = −y_R(x_f) − W/2` and `v_lat_R = −(v_y + r·x_f) + v·y_R'(x_f)` |   | proposed |

**Checks on the v_lat formula**

- On a straight road (c2 = c3 = 0, r = 0, v_y = 0) at v = 25 m/s with c1 = −0.016 rad (the left marking angles inward), v_lat_L = −25·(−0.016) = **0.40 m/s**. This is one drift speed in the Euro NCAP test.
- When the vehicle follows a curve exactly, r = v·κ and the marking has c1 = 0 and c2 = κ/2. Then `r·x_f = v·κ·x_f` and `v·y_L'(x_f) = v·κ·x_f`. The terms cancel and v_lat = 0, as expected.

### 3.1 Uncertainty in DLC, v_lat and TLC

**Responsibilities.** The data producers filter noise and fuse sources **once**. Lane Model Kalman-filters the marking coefficients, Vehicle State Estimation (G2) estimates v_y and Ego-motion (G4) computes motion. Each sends variances. ADAS Functions and G1 use the same filtered data to avoid inconsistent lane estimates. Both **must handle residual errors**. ADAS Functions propagates variance to DLC, v_lat and TLC, then accounts for uncertainty in its decisions.

**First-order variance propagation** assumes the coefficients are uncorrelated.

- `σ_DLC ≈ √(σ_c0² + x_f²·σ_c1²)`
- `σ_vlat ≈ √(v²·σ_c1² + σ_vy²)`
- `σ_TLC ≈ TLC·√((σ_DLC/DLC)² + (σ_vlat/v_lat)²)`

Use the Lane Model noise levels in [Path Planner Feature Design](report.html?doc=path-planner-feature-design&lang=vi#lane-faults) (σ_c0 = 0.03 m, σ_c1 = 0.002 in daylight and 2.5 times higher at night or in rain). Set x_f = 2.9 m, v = 25 m/s, DLC = 0.40 m and v_lat = 0.40 m/s (TLC = 1.0 s), and neglect σ_vy.

| Condition | σ_DLC | σ_vlat | σ_TLC | Interpretation |
|---|---|---|---|---|
| Daylight | 0.031 m | 0.05 m/s | 0.15 s | True TLC is in the 0.7–1.3 s interval (±2σ). This is reliable enough for activation |
| Night or rain | 0.077 m | 0.125 m/s | 0.37 s | The ±2σ interval is 0.3–1.7 s. A slow drift of 0.2 m/s is nearly indistinguishable from noise |

The c1 marking angle error multiplied by speed dominates the c0 distance error. At 25 m/s, a c1 error of 0.002 rad produces a v_lat error of 0.05 m/s.

**Basis for the rules below.** The regulations and standards supply general principles. The numerical thresholds are design choices.

- **ISO 21448 (SOTIF)** calls for analysis of conditions that degrade perception, such as night, rain and faded markings, and measures to prevent them from triggering an incorrect intervention.
- **Euro NCAP** (Assessment 4.3.3.5) requires manufacturers to demonstrate that the system avoids interventions the driver does not intend.

The 2σ confidence threshold and persistence across frames are standard estimation techniques. Tune the design values below using the benchmark.

| Rule | Threshold | Rationale | Status |
|---|---|---|---|
| Confirm drift toward the marking | v_lat − 2·σ_vlat ≥ 0.05 m/s | Prevent activation when noise flips the sign of v_lat. Requires v_lat ≥ 0.15 m/s in daylight and ≥ 0.30 m/s at night | proposed |
| Drift direction is uncertain | Use the DLC threshold alone (LKA uses DLC ≤ 0.1 m) | Still detects slow drift at night when the tire is close to the marking. DLC has much less noise than v_lat | proposed |
| Excessive noise makes the feature unavailable | σ_TLC > 0.5 s or marking confidence < 0.6 | Report UNAVAILABLE when estimates are unreliable | proposed |
| Require two camera frames | LKA activation condition holds on two consecutive lane model updates (about 50–100 ms) | Prevent activation from one faulty frame. ELK is exempt because it already triggers late | proposed |

### 3.2 Assessing vehicles in adjacent lanes for object-triggered ELK

This section determines whether the ego vehicle can safely encroach into the adjacent lane.

**Step 1. Select objects.** From the perception list, select objects in the lane toward which the ego vehicle is drifting. Assign lanes using the lane model, as G1 does. Consider only objects with existence_probability ≥ 0.7 observed for at least 3 consecutive frames.

**Step 2. Predict positions.** Assume constant object velocity over the same 2–3 s horizon as G1. Use the longitudinal position x relative to the ego vehicle.

**Step 3. Set the conflict window.** The ego vehicle starts encroaching after TLC seconds. Without intervention it remains partly in the adjacent lane for about 2 s longer. The window is `[TLC, TLC + 2.0 s]`.

**Step 4. Check for overlap.** Extend a box around the ego vehicle body by 2 m at each end. The adjacent lane is **unsafe** if an object enters this box at any point during the conflict window.

**Step 5. Activate.** Object-triggered ELK sends REQUEST when TLC ≤ 0.8 s and the adjacent lane is unsafe. Apply the stricter rule in step 6 when the driver **intentionally changes lanes** with the turn signal on.

**Step 6. Handle an intentional lane change.** Drivers who signal and change lanes often expect the trailing vehicle to brake. Pulling the vehicle back every time another vehicle approaches from behind would obstruct the driver. With the turn signal on, ELK intervenes only when the trailing vehicle **cannot reasonably brake in time**, indicated by any of these conditions.

- The other vehicle is alongside. It overlaps the ego vehicle body expanded by 1 m during [TLC, TLC + 1 s].
- TTC from the trailing vehicle to the rear of the ego vehicle is ≤ 1.5 s.
- The trailing vehicle needs more than 3 m/s² deceleration to avoid contact. Compute it as `Δv² / (2·distance)`.

In all other cases, issue only a blind-spot-style warning.

The examples use 72 km/h (20 m/s), as in the Euro NCAP test.

| Case | Inputs | Calculation | Result |
|---|---|---|---|
| Oncoming vehicle | At 20 m/s, 90 m ahead. Closing speed is 40 m/s | With TLC = 0.8 s, the window is 0.8–2.8 s. The oncoming vehicle closes by 32–112 m in that window, which includes 90 m | Unsafe. ELK REQUEST |
| Distant oncoming vehicle | Same, 200 m ahead | It remains 88 m away after 2.8 s | Safe. LKA may still intervene if enabled |
| Overtaking vehicle, distracted driver | At 80 km/h, 2.2 m/s faster than ego. Its front is 7 m behind the ego vehicle's rear | In 2.8 s it gains 6.2 m and its front is 0.8 m behind the ego vehicle's rear, inside the 2 m margin | Unsafe. ELK REQUEST |
| Overtaking vehicle, driver signaling, large rear gap | Same, 20 m away | The trailing vehicle needs only 0.12 m/s² deceleration and TTC is 9 s | Warning only |
| Overtaking vehicle, driver signaling, small rear gap | 5 m/s faster, 5 m away | Required deceleration is 2.5 m/s² and TTC is 1.0 s ≤ 1.5 s | ELK REQUEST |
| Vehicle alongside at the same speed | Relative speed is 0 | Always inside the box | Unsafe. ELK REQUEST even with the turn signal on |

The Euro NCAP overtaking test with the turn signal on aligns the front of the overtaking vehicle with the ego vehicle's rear axle at the point of collision. This meets the first condition (alongside), so step 6 still passes the test.

**Rationale for the 0.8 s threshold, earlier than the 0.6 s threshold for solid-line ELK.** A small solid-line encroachment may be safe. Euro NCAP permits up to 0.3 m. Contact with an adjacent vehicle is a collision. Euro NCAP counts the test as a failure if lateral clearance between the two vehicles drops below 0.3 m. Triggering at 0.8 s leaves 0.09–0.29 m between the tire edge and the marking.

## 4. General feature eligibility

If any applicable condition below fails, the feature shall withhold REQUEST even if the situation appears to call for intervention.

**Basis for the values.** EU ELKS provides the 65–70–130 km/h speed range. The other numerical values are design choices. R79 5.6.2.3.1.1 requires manufacturers to declare activation conditions and operating limits. R171 lists conditions for entering the active state and examples of manufacturer-declared conditions, including lane width, road type, time of day and weather.

| Condition | HWA | LKA | ELK | Basis | Status |
|---|---|---|---|---|---|
| Settings | Driver pressed the button and ACC is on | On in the menu (default on) | On (default on, reenabled at each startup) | R79 5.6.2.1.2 and EU 2021/646 3.2.1 | agreed |
| Speed | 10–130 km/h. Below 10 km/h, HWA waits and ACC continues to control the vehicle | Activates from 70 km/h. During deceleration it stays eligible until speed drops below 65 km/h. Maximum 130 km/h | Same as LKA | EU 2021/646 3.6.1 specifies operation over at least 70–130 km/h and a lower hysteresis threshold of 65 km/h. R79 B1 limits start at 10 km/h | agreed |
| Marking on the side of drift | Two markings or one marking plus remembered lane width | MEASURED status, confidence ≥ 0.6, view range ≥ 20 m | Same as LKA. For a road edge, type ROAD_EDGE or BARRIER and confidence ≥ 0.7 | Design values to avoid intervention from ghost markings | to be agreed |
| Low-confidence marking or road edge | — | If the previous row fails, send UNAVAILABLE and withhold intervention | Same as LKA. An unstable road-edge measurement makes ELK UNAVAILABLE on that side. The planner has no obligation to generate a path from an unreliable edge | Mentor guidance assigns primary responsibility to the L2 driver. Acting on uncertain inputs poses more risk than withholding intervention | mentor |
| ESC | HWA continues while ESC is intervening | Suppress when ESC is intervening or off | Same as LKA | EU 2021/646 3.2.2 and 3.3.2 allow automatic deactivation when ESC is off and suppression during ESC intervention | agreed |
| Input fault | Invalid lane model, objects, speed or steering angle makes the feature unavailable | Same as HWA | Object-triggered ELK requires only valid perception | Path Planner card, invalid input section | to be agreed |

**Additional HWA entry conditions.** HWA can enter its active state on a button press only when these conditions also hold. Otherwise ADAS Functions rejects the request and notifies the driver. The entry values for center offset, heading error and clearance to the markings are manufacturer-defined and declared for approval (R79 5.6.2.3.1.1). **No numerical requirements were found for these values.**

| Condition | Threshold | Rationale | Status |
|---|---|---|---|
| Vehicle inside the lane | DLC ≥ 0.2 m on both sides | HWA starts only when the vehicle is clear of the markings | to be agreed |
| Center offset | Absolute value ≤ 0.5 m | G1 recenters from 0.5 m with added a_y ≤ 0.5 m/s² in about 3–4 s (Path Planner Feature Design) | to be agreed |
| Heading error relative to lane | ≤ 2° | At 25 m/s, 2° corresponds to v_lat of 0.87 m/s, close to the intentional threshold of 1.0 m/s | to be agreed |
| Hands on the steering wheel | Yes | R79 5.6.2.2.5 requires B1 to detect hands on the wheel | agreed |
| Turn signal | Off | HWA stays out of the active state while the driver intends to change lanes | agreed |

## 5. Driver intent monitoring

Euro NCAP calls this DIM (Driver Intention Monitoring). It distinguishes deliberate encroachment from distracted drift to suppress unwanted interventions. ADAS Functions uses only signals available in the vehicle, including driver torque (EPS), steering wheel angle and rate, the turn signal and vehicle speed.

R79 limits override force to **50 N measured at the steering wheel rim**. With a rim radius of about 0.19 m, 50 N corresponds to about **9.5 Nm**. Euro NCAP has a tighter limit. A system using dashed-line LKA as ELK without DIM must have an override torque **≤ 3.5 Nm**.

| Situation | Observable signal | Threshold | ADAS Functions decision | Basis | Status |
|---|---|---|---|---|---|
| Distracted drift | Small driver torque, nearly stationary steering wheel and turn signal off | Absolute T_drv < 0.5 Nm and steering wheel rate < 15 °/s for 0.5 s | Unintentional. Activation allowed | Euro NCAP requires steering wheel rate within 0 ± 15 °/s before drift, with the driver holding the wheel passively | agreed |
| Signaled lane change | Turn signal toward the side of drift is on or went off less than 2 s ago | — | Intentional. Suppress LKA and boundary-triggered ELK. Object-triggered ELK follows the stricter rule in Section 3.2, step 6 | Euro NCAP tests overtaking ELK even when the driver signals 1.0 ± 0.5 s before steering, with v_lat 0.5–0.7 m/s and no collision permitted | agreed |
| Unsignaled lane change | Driver actively steers toward the marking | T_drv ≥ 1.5 Nm toward the marking for ≥ 0.2 s, or steering wheel rate ≥ 30 °/s toward the marking | Same as above | Design values between passive torque (0.5 Nm) and override torque (3.0 Nm) | agreed |
| Driver override during intervention | Driver torque opposes the system | T_drv ≥ 3.0 Nm against the intervention for ≥ 0.1 s | Cancel the request, send OFF and set driver_override. Suppress same-side reactivation for 3 s | R79 5.1.6 requires override at any time by deliberate action. The 3.0 Nm threshold is below Euro NCAP's 3.5 Nm and well below the torque equivalent of R79's 50 N | agreed |
| Sharp steering to avoid an obstacle | High v_lat, turn signal off | v_lat > 1.0 m/s | Treat it as intentional evasive steering. **Suppress both LKA and ELK**, including when a vehicle is in the adjacent lane. Warn only. The driver takes priority because they may see a hazard ahead that the system misses | Euro NCAP tests unintentional drift up to 0.6 m/s and intentional lane changes up to 0.7 m/s. R79 5.1.6 always permits driver override | proposed |
| Hands off the steering wheel | Torque stays near zero | Absolute T_drv < 0.3 Nm | HWA issues a visual warning after 10 s, a red visual warning and sound after 15 s, and switches off after 30 s. LKA and ELK can still intervene because the driver may be unable to steer | R79 5.6.2.2.5 sets the latest times. Visual warning at 15 s, audible warning at 30 s, switch-off 30 s after the audible warning starts. The project chooses earlier responses. At 25 m/s the vehicle covers 250 m in 10 s without hands on the wheel | proposed |

**Deliberate steering toward another vehicle.** The system must yield. If the driver holds the steering wheel with torque ≥ 3.0 Nm, ELK cancels. R79 requires this because the driver remains responsible at L2.

Safety here requires three measures.

1. Limit the a_y budget (Path Planner Feature Design) so a false activation cannot push the vehicle into a situation the driver cannot handle in time.
2. Allow driver override at all times with force ≤ 50 N.
3. Log each override and warning in ADAS Functions.

## 6. Decision table for sending REQUEST

Every 25 ms (40 Hz, as for the full L2 module), ADAS Functions checks both sides and each feature. It sends REQUEST when general eligibility (Section 4), driver intent (Section 5), uncertainty (Section 3.1) and the feature-specific conditions below permit it. The feature must also be outside any waiting period after override or COMPLETED.

**What lies beyond the marking.** ADAS Functions uses the lane model fields type and crossable together with the object list.

| Beyond the marking | Example | Responsible feature | Status |
|---|---|---|---|
| Empty lane, crossable marking (crossable = true, usually dashed) | Multilane highway with an empty adjacent lane | LKA if enabled. With LKA off, the system withholds intervention | agreed |
| Non-crossable marking (crossable = false for SOLID or DOUBLE) | Solid line between opposing directions | LKA first (higher TLC), then ELK if LKA is off or insufficient | agreed |
| Road edge (ROAD_EDGE, BARRIER) | Dirt shoulder, grass or rigid barrier | ELK | agreed |
| Oncoming or overtaking vehicle in the conflict window (Section 3.2) | Oncoming vehicle on a two-way road or vehicle approaching from behind in the next lane | ELK. With the turn signal on, apply Section 3.2, step 6 | agreed |

**Activation thresholds.** The benchmark compares three LKA candidates. Each ELK case uses a single value.

| Feature | Activation condition | Basis | Status |
|---|---|---|---|
| LKA | TLC ≤ T_LKA or DLC ≤ 0.1 m with v_lat ≥ 0.05 m/s. Also require 0.1 ≤ v_lat ≤ 1.0 m/s. Test T_LKA of 0.6 s (late), 1.0 s (middle) and 1.5 s (early) | Euro NCAP requires DTLE ≥ −0.3 m at v_lat 0.2–0.6 m/s. ISO 17361 permits warnings from approximately TLC 1.5 s onward | to be agreed |
| ELK for solid lines | TLC ≤ 0.6 s to the marking | Euro NCAP and EU 2021/646 require DTLE ≥ −0.3 m | to be agreed |
| ELK for road edges | TLC ≤ 0.6 s to the road edge | Euro NCAP requires DTLE ≥ −0.1 m, permitting only part of the front wheel beyond the edge | to be agreed |
| ELK for oncoming or overtaking vehicles | TLC ≤ 0.8 s to the dividing marking and the adjacent lane is unsafe (Section 3.2) | Euro NCAP requires collision avoidance. Lateral clearance below 0.3 m fails the test | to be agreed |

### 6.1 TLC threshold notes

- The references give **required outcomes** (Euro NCAP and ELKS allow marking encroachment ≤ 0.3 m and road-edge encroachment ≤ 0.1 m and require no contact) and an **earliest warning limit** (ISO 17361 allows warnings from approximately TLC 1.5 s onward). The TLC threshold is a design choice between these limits.
- With 0.2 s delay, the physical minimum TLC is about 0.4 s for LKA to pass Euro NCAP, 0.4–0.7 s for LKA to avoid touching the marking and 0.3–0.5 s for road-edge ELK.
- Nighttime noise (σ_TLC ≈ 0.37 s) requires about 0.3–0.4 s of additional margin.
- LKA is earlier and gentler (1.5 m/s²). ELK is later and stronger (3.0 m/s²) and provides the final safety net.
- Run all three LKA candidates on S4–S8 (encroachment) and S10 (unwanted activation) before selecting one.

**Requests on both sides.** This occurs only in narrow lanes or when the vehicle drifts to the opposite side after a correction. ADAS Functions sends the side with lower TLC. G1 still arbitrates with ELK > LKA > HWA priority.

**Return to STANDBY and reactivate**

| Event | ADAS Functions response | Status |
|---|---|---|
| G1 reports COMPLETED | Set the feature to STANDBY. Reactivate on the same side when DLC has reached ≥ 0.3 m and starts falling again, or after 2 s | agreed |
| Driver override | Send OFF immediately. Suppress same-side reactivation for 3 s except for object-triggered ELK | agreed |
| Speed drops below 65 km/h during intervention | Keep REQUEST until G1 reports COMPLETED. Suppress new activation | agreed |
| The marking on that side disappears during intervention | Keep REQUEST. G1 follows the previous path for up to T_coast = 1 s and then reports an invalid path | agreed |

## 7. Driver warnings sent to the HMI

The simulator records these warnings in the log for verification. It has no production HMI.

| Event | Warning | Basis | Status |
|---|---|---|---|
| Each LKA or ELK intervention | Show a warning light immediately for at least 1 s or until intervention ends | R79 5.1.6.1.1 and EU 2021/646 3.6.4.1 | agreed |
| Intervention longer than 10 s | Audible warning until intervention ends | R79 5.1.6.1.2.1 | agreed |
| Second intervention within 180 s without driver steering | Audible warning from the second intervention. From the third, each warning lasts at least 10 s longer than the previous one | R79 5.1.6.1.2.2 | agreed |
| Object-triggered ELK (ESF) | Visual warning plus sound or vibration throughout the intervention | R79 5.1.6.2.6 | agreed |
| Signaled lane change with time for the trailing vehicle to brake (Section 3.2, step 6) | Blind-spot-style warning only | Design choice | proposed |
| HWA reaches aysmax and a front tire starts overlapping a marking | Keep assisting within available limits and avoid abrupt release. Show a light with sound or vibration. Use G1's lateral_limit_reached flag and DLC | R79 5.6.2.2.3 | agreed |
| G1 reports an invalid path | Request driver takeover and ramp down torque | Team convention | agreed |
| Driver disables ELK | Continuous visual indication while ELK is off | EU 2021/646 3.2.3 | agreed |

## 8. ADAS Functions edge cases

This table covers the ADAS Functions response. See the identically numbered cases in Path Planner Feature Design for G1 path and transition behavior.

**Lateral and longitudinal responsibilities.** G1 handles lateral motion. ACC and AEB handle braking and deceleration. As in the vehicle, separate lateral and longitudinal modules exchange constraints. The simulator uses an ACC stub (Path Planner Feature Design, Section 6.1).

| # | Situation | ADAS Functions response | Status |
|---|---|---|---|
| 1a | HWA active and ego drifts toward an occupied adjacent lane, for example because crosswind exceeds HWA authority | Send ELK REQUEST as usual. EU 2021/646 3.3.2 permits ELKS suppression while another feature controls lateral motion. The project keeps ELKS eligible | to be agreed |
| 1b | HWA active and ego centered, while **another vehicle** encroaches into the ego lane | **Withhold ELK** because ego is not drifting (high TLC). G1 offsets the center and ACC selects the other vehicle as its target (Path Planner Feature Design, Section 6.1) | to be agreed |
| 2 | HWA enters a curve beyond aysmax | Use lateral_limit_reached and DLC. Warn when the tire starts overlapping the marking (R79 5.6.2.2.3). Send ELK if the ELK threshold is reached and the other side is unsafe | to be agreed |
| 3 | Driver overrides HWA | Set driver_override when T_drv ≥ 3.0 Nm. HWA stays enabled | agreed |
| 4 | Driver signals a lane change and an overtaking vehicle approaches from behind | Follow Section 3.2, step 6. Send ELK REQUEST only when the other vehicle is alongside, rear TTC ≤ 1.5 s or the trailing vehicle needs more than 3 m/s² deceleration. Otherwise warn only. Withhold the request if a front tire is already more than 0.3 m across the marking | proposed |
| 5 | Driver signals and deliberately crosses a solid line or moves onto the shoulder | Withhold activation before intervention. During intervention, send OFF with cancel_reason = INDICATOR to return control to the driver. Object-triggered ELK follows Section 3.2, step 6 | proposed |
| 6 | Vehicle drifts back and forth between the markings (drowsy driver) | Treat each drift as a new request with the same thresholds. Reactivate under Section 6. Escalate warnings under R79 from the second intervention within 180 s. Log the count | proposed |
| 7 | Driver completes a lane change and the lane model reports lane_change | Cancel pending requests and recalculate DLC and TLC from the new lane. Suppress activation for 1 s | agreed |
| 8 | c0 jump changes DLC by 0.3–1 m in one frame | Lane Model supplies no jump flag. The boundary consistency check shared with G1 flags the frame (Path Planner Feature Design, Section 4). Withhold activation and cancellation based on that frame. Predict DLC from the last value and vehicle motion. Use the new DLC once the immediately following frame confirms it (difference below 0.1 m). If DLC is genuinely small because the lane narrows, activate as usual. Report UNAVAILABLE if unconfirmed after 0.5 s | proposed |
| 9 | Ghost object | Consider only objects with existence ≥ 0.7 and at least 3 consecutive observations (0.15 s) | agreed |
| 10 | Oncoming vehicle in the adjacent lane with no ego drift | Withhold ELK. It requires both TLC ≤ 0.8 s and an unsafe adjacent lane | agreed |
| 11 | Both markings disappear during intervention | Keep REQUEST. Request driver takeover when G1 reports an invalid path | agreed |
| 12 | ESC intervenes during LKA or ELK intervention | Send OFF and yield to ESC | agreed |
| 13 | Speed drops below 65 km/h during intervention | Keep the active request until COMPLETED. Suppress new activation | agreed |
| 13b | Highway congestion, 0–60 km/h | LKA and ELK are UNAVAILABLE. HWA remains eligible when enabled (10–130 km/h), providing Traffic Jam Assist. With HWA off, lateral assistance is unavailable | proposed |
| 15 | Driver presses HWA while 0.4 m off center | Allow HWA entry (below 0.5 m) | agreed |
| 16 | Driver steers sharply (v_lat > 1.0 m/s) to avoid an obstacle and the adjacent lane is occupied | Suppress both LKA and ELK and warn only (Section 5) | proposed |

## 9. ADAS stub inputs

| Mode | Stub inputs | Example at night with 0.4 m/s drift | Strength | Limitation |
|---|---|---|---|---|
| A. Read the same messages as G1 | Lane model, objects and CAN from the sensor models, with injected noise, delay and dropped frames | Measured TLC varies by ±0.37 s, so LKA may trigger a few hundred ms early or late across runs. A c0 jump can cause a false activation | Represents vehicle behavior. Camera errors affect both activation and the path | If the vehicle encroaches by 0.35 m, it is hard to isolate the planner from late activation |
| B. Read scenario ground truth | DLC, v_lat and other vehicle positions directly from the simulator without noise | LKA triggers on true TLC and the threshold under test (Section 6) | Isolates planner error | Less representative of the vehicle |

**Agreed.** Implement both modes and select one with a flag in the scenario file. Score G1 in mode B and report full-chain robustness in mode A. Always log measured and true TLC.

Both modes get driver signals (torque, steering wheel rate and turn signal) and settings (HWA button and LKA and ELK menus) from the simulated driver and scenario file.

**Driver signal frequencies and units** come from the mentor's Motion signal list.

| Signal | Vehicle signal name | Frequency | Vehicle unit | Use | Status |
|---|---|---|---|---|---|
| Driver torque | Driver steering torque | 50 Hz | Nm | Distraction, intention, override and hands-off detection (Section 5). The 0.1 s override hold is 5 samples and the 0.2 s intention hold is 10 samples | mentor |
| Steering wheel angle | Steering wheel angle | 100 Hz | ° | Scenarios and logging | mentor |
| Steering wheel rate | Steering wheel speed | 100 Hz | °/s | The 15 °/s and 30 °/s thresholds in Section 5 use vehicle units directly | mentor |
| Vehicle speed | Vehicle speed | 50 Hz | km/h | The 65–130 km/h range in Section 4 uses vehicle units directly | mentor |
| Turn signal, HWA button and ESC flag | Pending. The list currently covers only Motion | — | — | Sections 4 and 5 and edge case 12 | to be agreed |

ADAS Functions runs at 40 Hz, so it receives 1 or 2 torque samples per cycle. Thresholds use elapsed hold time.

## 10. ADAS stub outputs {#function-requests}

The stub sends the production `FunctionRequests` message over pub/sub at 40 Hz. The assumed delay is about 20 ms, the timeout is 75 ms and maximum age is 45 ms. Use the [common header](report.html?doc=g1-interfaces-and-signals&lang=vi#header) without `frame_id`. The stamp is the request send time. The `requests[3]` array is ordered HWA, LKA, ELK.

| Field | Type | Purpose | Status |
|---|---|---|---|
| state (per feature) | uint8 enum { OFF, UNAVAILABLE, STANDBY, REQUEST, FAULT } | OFF means the driver disabled it. UNAVAILABLE means enabled but an eligibility condition fails (below 70 km/h, poor markings or excessive noise). FAULT indicates a fault. G1 treats OFF, UNAVAILABLE and FAULT the same. Logs and scenarios distinguish them | agreed |
| side (per feature) | uint8 enum { NONE, LEFT, RIGHT } | Side of drift. ELK uses it to tighten the boundary. HWA uses NONE | agreed |
| tlc (per feature) | float32, s | ADAS computes it and G1 uses it to select path duration. HWA ignores it | agreed |
| elk_reason (per feature) | uint8 enum { NONE, SOLID_LINE, ROAD_EDGE, ONCOMING, OVERTAKING } | Logging only | agreed |
| driver_override | bool, shared by the message | Driver is overriding (T_drv ≥ 3.0 Nm) | agreed |
| cancel_reason (per feature) | uint8 enum { NONE, DRIVER_OVERRIDE, INDICATOR, SPEED, LANE_QUALITY, ESC, FAULT } | Records why a request was canceled, for logging only | agreed |

The stub receives `PathStatus` from G1 with path_valid, active_function and intervention_phase (agreed), and lateral_limit_reached (to be agreed). See Path Planner Software Requirements, Section 5.1, for the flag's definition, requirement and rationale.

In addition to the message to G1, the stub records a `HmiStatus` message for logging and evaluation. It contains visual and audible warnings, the hands-off warning level and the intervention count within 180 s.

## 11. Open decisions

1. **Activation thresholds** (Section 6). Compare 0.6 / 1.0 / 1.5 s for LKA in the benchmark. Use 0.6 s for solid-line and road-edge ELK and 0.8 s for object-triggered ELK.
2. **Marking quality** and **input faults** in general eligibility (Section 4).
3. **HWA entry conditions** (Section 4). DLC ≥ 0.2 m, center offset ≤ 0.5 m and angle ≤ 2°. These are design values.
4. **Object-triggered ELK** (Section 3.2). Window [TLC, TLC + 2 s], box extended by 2 m, and the stricter signaled rule (alongside, TTC ≤ 1.5 s or required deceleration > 3 m/s²).
5. **Uncertainty** (Section 3.1). Confirm direction with v_lat − 2σ, report UNAVAILABLE when σ_TLC > 0.5 s and require two frames for LKA.
6. **Sharp steering** (Section 5). Suppress ELK as well and warn only.
7. **Hands off the steering wheel** (Section 5). 10 / 15 / 30 s.
8. **ELK while HWA is active** (edge case 1a). Keep ELK eligible.
9. **Another vehicle cuts into the ego lane** (edge case 1b). G1 offsets the center and ACC maintains distance. Withhold ELK.

## References

- [UN Regulation No 79, OJ L 2025/3](https://upload.wikimedia.org/wikipedia/commons/f/f3/OJ_L_202500003_of_2025_-_EN_English.pdf), also available on [EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202500003)
- [Commission Implementing Regulation (EU) 2021/646, ELKS](https://eur-lex.europa.eu/eli/reg_impl/2021/646/2021-04-20/eng), consulted via the [LawPlayer copy](https://lawplayer.com/eu/act/32021R0646)
- [Euro NCAP LSS Test Protocol v4.3](https://cdn.euroncap.com/cars/assets/euro_ncap_lss_test_protocol_v43_f2ddd5f6d6.pdf)
- [Euro NCAP Assessment Protocol Safety Assist Collision Avoidance v10.4.1](https://cdn.euroncap.com/cars/assets/euro_ncap_assessment_protocol_sa_collision_avoidance_v1041_fafe1dd418.pdf)
- [ISO 17361:2017 summary](https://standards.iteh.ai/catalog/standards/iso/c3d927a6-f4e1-4b4d-91d2-548cf5953983/iso-17361-2017) (warning-zone figures from secondary sources, original text pending review)
- ISO 21448:2022, Road vehicles — Safety of the intended functionality (original text pending review)
- [UN Regulation No 171 (DCAS), EUR-Lex](https://eur-lex.europa.eu/eli/reg/2025/1899/oj/eng) (original text pending review)

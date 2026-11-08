# ADAS Functions: When HWA, LKA and ELK Intervene

This document specifies the **ADAS Functions** module at its output boundary. It defines which requests the module sends to G1 in each situation and the numerical thresholds for those requests. The assignment places this module outside G1 scope. The project needs a simulation stub to determine when to activate each feature in test scenarios.

**Production module and simulation stub.** The production module processes the lane model, detected objects, vehicle signals and driver inputs. It handles filtering, driver intent monitoring and the HMI before sending requests. The G1 simulator stub **classifies situations using the thresholds in this document** and emits the same `FunctionRequests` message as the production module. It uses no in-cabin camera, machine learning or production HMI.

## 1. Regulatory and test references

| Reference | Description | Application |
|---|---|---|
| UN R79, OJ L 2025/3 | Steering equipment approval regulation, mandatory for vehicles subject to UNECE type approval | HWA limits (ACSF Category B1, Section 5.6.2), LKA and boundary-triggered ELK limits (CSF, Section 5.1.6.1), and object-triggered ELK limits (ESF, Section 5.1.6.2). Override force of 50 N |
| EU 2021/646 (ELKS) | EU regulation requiring ELKS on new vehicles, applicable from 6 July 2022 | 70–130 km/h operating range, default activation, deactivation procedure and permitted intervention suppression conditions |
| Euro NCAP LSS Test Protocol v4.3 and Safety Assist Assessment Protocol v10.4.1 | Voluntary star-rating tests targeted by vehicle manufacturers | Test scenarios (72 km/h and v_lat of 0.2–0.6 m/s), DTLE thresholds, override torque of 3.5 Nm, and ELK with the turn signal on |
| ISO 11270:2014 (LKAS) | LKA performance standard | The paywalled primary text has not been reviewed. Secondary sources are used for reference only: a_y ≤ 3 m/s², jerk ≤ 5 m/s³ |

The three features map to regulatory concepts as follows.

| Feature | Regulatory concept | How it is enabled | Status |
|---|---|---|---|
| HWA | ACSF Category B1 (R79): continuous assistance to keep the vehicle in its lane | The driver presses a button with ACC active. The driver can deactivate it in one action (R79 5.6.2.1.2) | Agreed |
| LKA | Lane marking-based CSF (R79 2.3.4.2 c) | Enabled by default. The driver can disable it in the menu | Agreed |
| ELK for solid markings and road edges | CSF and ELKS | Enabled by default at every vehicle start. Disabling it requires at least two deliberate actions. It re-enables at the next start (EU 2021/646, Annex I, 3.2.1) | Agreed |
| ELK for oncoming or overtaking vehicles | ESF (R79 2.3.4.3 a): collision avoidance with adjacent-lane vehicles | Same as above | Agreed |

## 2. Responsibilities of ADAS Functions and G1

| Task | ADAS Functions | G1 Path Planner |
|---|---|---|
| Read feature settings from the HWA button and LKA and ELK menus | Owns the task | Does not receive settings |
| Check general conditions for speed, ACC, lane marking quality, ESC and input faults | Checks conditions (Section 4) | Receives the resulting state of each feature |
| Compute DLC, v_lat and TLC for both sides | Computes them (Section 3) | Reuses TLC to select the path duration |
| Assess hazards beyond the marking (marking type, road edge, oncoming or overtaking traffic) | Assesses hazards (Section 6) | Outside G1 scope |
| Infer driver intent from turn signal, torque, steering wheel rate, override and hands-off status | Infers intent (Section 5) | Does not receive these signals |
| Warn the driver with visual and audible warnings under R79 | Sends warnings (Section 8) | Outside G1 scope |
| Arbitrate ELK > LKA > HWA | Sends requests for all three features | Arbitrates |
| Plan the path using the starting point, a_y budget, duration and target position | Outside module scope | Plans the path within Section 7 limits |
| Tighten the boundary on the hazardous side during ELK | Sends the side | Tightens the boundary |
| Determine when the intervention is complete (COMPLETED) | Receives the completion status | Determines completion |
| Smooth transitions when the active feature changes or a request is cancelled mid-intervention | Outside module scope | Smooths transitions |
| Apply an HWA lane-center offset for a large vehicle in an adjacent lane | Outside module scope | Uses Perception and TTC |
| Limit steering torque and ensure override force ≤ 50 N | Controller and EPS responsibility | Controller and EPS responsibility. G1's a_y budget must be consistent with this limit |

## 3. Quantities computed by ADAS Functions

Let v be vehicle speed, v_y lateral velocity at the rear axle center, r yaw rate, x_f the distance from the rear axle center to the front axle (the wheelbase), and W vehicle width. In base_link, the left boundary is `y_L(x) = c0 + c1·x + c2·x² + c3·x³`, with y positive to the left.

| Quantity | Calculation | Meaning | Status |
|---|---|---|---|
| DLC_L | `y_L(x_f) − W/2` | Remaining distance from the outer edge of the left front tire to the inner edge of the left marking. During drift, the front tire reaches the marking first. This is equivalent to the Euro NCAP DTLE definition under a different name | Proposed |
| v_lat_L | `v_y + r·x_f − v·y_L'(x_f)`, with `y_L'(x) = c1 + 2·c2·x + 3·c3·x²` | Rate at which DLC_L decreases, i.e., the closing speed toward the left marking. Use a low-pass filter of about 0.1 s to reduce c1 noise | Proposed |
| TLC_L | `DLC_L / v_lat_L` if v_lat_L ≥ 0.05 m/s, otherwise infinity | Time until the tire reaches the marking, assuming constant v_lat (the same assumption as DTLE) | Proposed |
| Right side | By symmetry, `DLC_R = −y_R(x_f) − W/2` and `v_lat_R = −(v_y + r·x_f) + v·y_R'(x_f)` |   | Proposed |

**Check of the v_lat formula.**

- Straight road (c2 = c3 = 0, r = 0, v_y = 0) with v = 25 m/s and c1 = −0.016 rad (the left marking converges toward the vehicle). Then v_lat_L = −25·(−0.016) = **0.40 m/s**, one of the Euro NCAP test drift rates.
- Vehicle tracking a curve correctly. Here r = v·κ, c1 = 0 and c2 = κ/2 for the marking. Then `r·x_f = v·κ·x_f` and `v·y_L'(x_f) = v·κ·x_f`. These terms cancel, yielding v_lat = 0 as expected.

**Adjacent-lane object assessment for ELK.** ADAS Functions uses the same lane assignment and motion prediction as G1. It assumes constant object velocity and uses the lane model to assign each object to the left or right lane. It considers only objects with existence_probability ≥ 0.7.

The **conflict window** is `[TLC, TLC + 2.0 s]`. It starts when the vehicle begins encroaching into the adjacent lane and ends about 2 s later, during which the ego vehicle would still partially occupy that lane without intervention. The adjacent lane is **unsafe** if an object's longitudinal extent overlaps the ego vehicle's body, expanded by 2 m at each end, during this window.

Example at 72 km/h (20 m/s), as in the Euro NCAP test:

- **Oncoming vehicle.** It also travels at 20 m/s, giving a closing speed of 40 m/s. With TLC = 0.8 s, the window is 0.8–2.8 s. An oncoming vehicle 40–112 m ahead is classified as a hazard.
- **Overtaking vehicle.** It travels at 80 km/h, approximately 2.2 m/s faster than the ego vehicle. Over 2.8 s it gains about 6.2 m. It is classified as a hazard if its front end is no more than 2 m + 6.2 m ≈ 8 m behind the ego vehicle's rear end.

## 4. General feature eligibility

A feature may send REQUEST only if all applicable conditions below are met, even when the scenario otherwise calls for intervention.

| Condition | HWA | LKA | ELK | Basis | Status |
|---|---|---|---|---|---|
| Settings | The driver has pressed the button and ACC is active | Enabled in the menu (on by default) | Enabled (on by default and re-enabled at each vehicle start) | R79 5.6.2.1.2 and EU 2021/646 3.2.1 | Agreed |
| Speed | 10–130 km/h. Below 10 km/h, HWA stays in standby while ACC continues controlling the vehicle | Eligible from 70 km/h and remains eligible during deceleration until speed drops below 65 km/h. Maximum 130 km/h | Same as LKA | EU 2021/646 requires ELKS to operate over at least 70–130 km/h, with hysteresis down to 65 km/h. The R79 B1 limit table starts at 10 km/h | Proposed |
| Marking on the drift side | Two boundaries, or one boundary plus the last known lane width | status MEASURED, confidence ≥ 0.6 and visibility range ≥ 20 m | Same as LKA. For road edges, require type ROAD_EDGE or BARRIER and confidence ≥ 0.7 | Project criteria to avoid interventions caused by false lane markings | Proposed |
| ESC | HWA continues during ESC intervention | Inhibit while ESC is intervening or disabled | Same as LKA | EU 2021/646 3.2.2 and 3.3.2 | Proposed |
| Input fault | An invalid lane model, object list, speed or steering angle makes the feature unavailable | Same as HWA | Object-triggered ELK requires valid perception only | Invalid input handling on the Path Planner card | Proposed |

**Additional conditions for HWA engagement.** When the driver presses the button, ADAS Functions permits engagement only if the additional conditions below are met. Otherwise it rejects the request and notifies the driver.

| Condition | Threshold | Rationale | Status |
|---|---|---|---|
| Vehicle within its lane | DLC ≥ 0.2 m on both sides | HWA starts with the tires clear of the markings. G1's return-to-center transition handles small offsets only | Proposed |
| Lane-center offset | Absolute offset ≤ 0.5 m | Limit for G1's return-to-center transition at the comfort a_y limit | To be agreed |
| Heading error relative to the lane | ≤ 2° | Same rationale as above | Proposed |
| Hands on the steering wheel | Required | R79 B1 requires hands-on detection | Proposed |
| Turn signal | Off | HWA does not engage during an intended lane change | Proposed |

## 5. Driver intent monitoring

Euro NCAP calls this DIM (Driver Intention Monitoring). It distinguishes deliberate line crossings from inadvertent drift and suppresses unwanted interventions. ADAS Functions uses only signals available on the vehicle, including driver torque from EPS, steering wheel angle and angular rate, turn signal and vehicle speed.

R79 limits override force to **50 N measured at the steering wheel rim**. At a rim radius of approximately 0.19 m, 50 N corresponds to about **9.5 Nm**. Euro NCAP sets a tighter limit for systems that use dashed-line LKA as ELK without DIM, requiring override torque **≤ 3.5 Nm**.

| Situation | Observable indicators | Threshold | ADAS Functions decision | Basis | Status |
|---|---|---|---|---|---|
| Inadvertent drift | Low driver torque, steering wheel almost stationary, turn signal off | \|T_drv\| < 0.5 Nm and steering wheel rate < 15 °/s for 0.5 s | Inadvertent drift. Permit activation | — | — |
| Lane change with turn signal | Turn signal toward the drift side, or switched off less than 2 s ago | — | Intentional. Inhibit LKA and boundary-triggered ELK. **Object-triggered ELK remains available** | Euro NCAP tests overtaking-vehicle ELK with the turn signal activated 1.0 ± 0.5 s before steering, at v_lat of 0.5–0.7 m/s, and requires collision avoidance | Proposed |
| Lane change without turn signal | Driver actively steers toward the marking | T_drv ≥ 1.5 Nm toward the marking for ≥ 0.2 s, or steering wheel rate ≥ 30 °/s toward the marking | Same as above | Project threshold between passive torque (0.5 Nm) and override torque (3.0 Nm). The regulation supplies no numeric threshold | Proposed |
| Driver override during intervention | Driver torque opposes system steering | T_drv ≥ 3.0 Nm against the intervention for ≥ 0.1 s | Cancel the request, send OFF and inhibit reactivation on the same side for 3 s | R79 5.1.6 requires deliberate driver override at any time. The 3.0 Nm threshold is below 3.5 Nm from Euro NCAP and well below the equivalent of the R79 50 N limit | Proposed |
| Abrupt evasive steering | High v_lat with the turn signal off | v_lat > 1.0 m/s | Treat as intentional. Inhibit LKA and boundary-triggered ELK. Object-triggered ELK remains available | Euro NCAP tests inadvertent drift up to 0.6 m/s and LDW up to 1.0 m/s | Proposed |
| Hands off the steering wheel | Sustained near-zero torque | \|T_drv\| < 0.3 Nm | HWA shows a visual warning at 15 s, a red visual warning plus sound at 30 s, and disengages at 60 s. LKA and ELK can still intervene because the driver may be incapacitated | — | — |

**Deliberate steering toward another vehicle.** If the driver holds opposing steering torque ≥ 3.0 Nm, ELK cancels and yields to the driver. R79 requires driver override because the driver remains responsible at Level 2.

The design addresses safety in three ways.

1. Limit the a_y budget (Section 7) so that an erroneous intervention leaves time for the driver to respond.
2. Allow the driver to override at any time with force ≤ 50 N.
3. Log overrides and warnings in ADAS Functions.

An erroneous ELK intervention, for example due to a false detection, is considered more hazardous than a missed intervention because the system itself introduces the abrupt steering action.

## 6. Decision table for sending REQUEST

Every 20 ms, ADAS Functions evaluates each side and feature. A feature sends REQUEST if the general conditions in Section 4 hold, driver intent in Section 5 permits intervention, the feature is outside the hold-off period following an override or COMPLETED, and its specific conditions below are met.

**What lies beyond the marking.** ADAS Functions uses the lane model's type and crossable fields and the object list.

| Beyond the marking | Example | Responsible feature | Status |
|---|---|---|---|
| Clear adjacent lane and crossable marking (crossable = true, typically dashed) | Multilane highway with an empty adjacent lane | LKA if enabled. Otherwise no intervention | Agreed |
| Non-crossable marking (crossable = false: SOLID, DOUBLE) | Solid center marking separating directions of travel | LKA first at the longer TLC threshold. ELK if LKA is disabled or insufficient | Agreed |
| Road edge (ROAD_EDGE, BARRIER) | Unpaved shoulder, grass or rigid barrier | ELK | Agreed |
| Oncoming or overtaking vehicle in the conflict window (Section 3) | Approaching vehicle on a two-way road, or a vehicle approaching from behind in the adjacent lane | ELK, even if the turn signal is on | Agreed |

**Activation thresholds.**

| Feature | Activation condition | Basis | Status |
|---|---|---|---|
| LKA | TLC ≤ 1.0 s, or DLC ≤ 0.1 m with v_lat ≥ 0.05 m/s. Also require 0.1 ≤ v_lat ≤ 1.0 m/s | Euro NCAP allows at most 0.3 m of encroachment past the inner edge of the marking (DTLE ≥ −0.3 m) at v_lat of 0.2–0.6 m/s | Proposed |
| ELK for a solid marking | TLC ≤ 0.6 s to the marking | Euro NCAP and EU 2021/646 specify DTLE ≥ −0.3 m | Proposed |
| ELK for a road edge | TLC ≤ 0.6 s to the road edge | Euro NCAP specifies DTLE ≥ −0.1 m, allowing only part of the front wheel beyond the edge | Proposed |
| ELK for an oncoming or overtaking vehicle | TLC ≤ 0.8 s to the dividing marking and adjacent lane unsafe | Euro NCAP requires collision avoidance. The test fails if lateral clearance between the two vehicles is below 0.3 m | Proposed |

**Analytical check of thresholds.** Assume v_lat remains constant until activation, followed by 0.2 s of camera, planner and EPS delay. The opposing a_y then ramps up at the jerk limit until reaching the Section 7 budget. The table gives the furthest tire-edge position relative to the inner edge of the marking. A negative value means the tire has not reached the marking.

| Case | v_lat 0.2 m/s | 0.4 m/s | 0.6 m/s | 1.0 m/s | Requirement |
|---|---|---|---|---|---|
| LKA, TLC 1.0 s, a_y 1.5 m/s², jerk 5 m/s³ | −0.12 m | −0.21 m | −0.28 m | −0.32 m | ≥ −0.3 m relative to the marking |
| ELK, TLC 0.6 s, a_y 3.0 m/s², jerk 10 m/s³ | −0.05 m | −0.08 m | −0.10 m | −0.09 m | Road edge: ≥ −0.1 m relative to the edge |
| Object-triggered ELK, TLC 0.8 s, a_y 3.0 m/s², jerk 10 m/s³ | −0.09 m | −0.16 m | −0.22 m | −0.29 m | No collision |

At nominal settings, all three cases keep the vehicle within the lane with a margin to the requirements. This margin accounts for timing jitter, c0 and c1 noise, and wet roads. Verify these values in closed-loop simulation.

**Requests on both sides.** This occurs only in a narrow lane or when the vehicle drifts to the opposite side after a correction. ADAS Functions sends the side with the lower TLC. G1 still arbitrates with priority ELK > LKA > HWA.

**Returning to STANDBY and reactivation.**

| Event | ADAS Functions action | Status |
|---|---|---|
| G1 reports COMPLETED | Return the feature to STANDBY. Reactivate on the same side when DLC reaches ≥ 0.3 m and then falls again, or after 2 s | Proposed |
| Driver override | Send OFF immediately. Inhibit reactivation on the same side for 3 s, except for object-triggered ELK | Proposed |
| Speed drops below 65 km/h during intervention | Hold REQUEST until G1 reports COMPLETED. Suppress new activations | Proposed |
| Marking on the intervention side is lost | Hold REQUEST. G1 follows the previous path for at most T_coast = 1 s, then reports an invalid path | Proposed |

## 7. Intervention limits for G1

G1 applies these budgets during path planning. They are listed here for context and will be added to the Path Planner card once agreed.

| Limit | HWA | LKA | ELK | Basis | Status |
|---|---|---|---|---|---|
| Total a_y (including cornering) | ≤ 3.0 m/s². Select aysmax = 2.5 m/s² to allow margin | ≤ 3.0 m/s² | ≤ 4.0 m/s² | R79 5.6.2.1.3 caps B1 aysmax at 3 m/s² for M1 vehicles and permits exceedance by 0.3 m/s², or 40% for up to 2 s. For LKA and ELK, R79 specifies no CSF a_y limit. The 4.0 m/s² budget leaves margin on wet roads at μ = 0.5 (grip limit about 4.9 m/s²) | Proposed |
| System-induced a_y (excluding cornering) | Return to center and lane-center offset: ≤ 0.5 m/s² | ≤ 1.5 m/s² | ≤ 3.0 m/s² | See the check in Section 6. ISO 11270 (secondary source) suggests total a_y ≤ 3 m/s² for LKA | Proposed |
| Lateral jerk | ≤ 5 m/s³ over a 0.5 s moving average. Comfort target ≤ 2.5 m/s³ | ≤ 5 m/s³ | ≤ 10 m/s³ | R79 5.6.2.1.3 c for B1. LKA: ISO 11270 (secondary source). ELK has no specified regulatory value | Proposed |
| Intervention duration | Continuous | Target 2–4 s, maximum 10 s | Target 1–3 s, maximum 10 s | R79 5.1.6.1.2.1 requires an audible warning through the end of an intervention that exceeds 10 s | Proposed |
| Override force (controller and EPS responsibility) | ≤ 50 N | ≤ 50 N, override torque ≤ 3.5 Nm | ≤ 50 N | R79 5.6.2.1.3 a, 5.1.6.1.3 and 5.1.6.2.8, EU 2021/646 3.6.3.1, and Euro NCAP | Agreed |
| Lane containment | HWA must prevent the vehicle from crossing the marking while a_y is below aysmax (R79 5.6.2.1.1) | Return the vehicle to within its lane | ESF may steer across a marking only when returning the vehicle to its original lane (R79 5.1.6.2.3.1) | R79 | Assignment |

**LKA and ELK completion criteria.** G1 determines completion. These criteria are still marked *To be agreed* on the Path Planner card. The proposal is to report COMPLETED when all the following hold continuously for 0.5 s.

- v_lat toward the marking ≤ 0.1 m/s.
- Heading error relative to the lane ≤ 0.5°.
- DLC ≥ 0.3 m.
- For ELK, distance from the lane centerline ≤ 0.3 m.

For example, LKA starts at 25 m/s with v_lat of 0.4 m/s. About 2.5 s later the conditions are met and G1 reports COMPLETED.

## 8. Driver warnings sent to the HMI

The simulator logs the following events for verification in place of a production HMI.

| Event | Warning | Basis | Status |
|---|---|---|---|
| Every LKA or ELK intervention | Immediate visual warning for at least 1 s or through the end of the intervention | R79 5.1.6.1.1 and EU 2021/646 3.6.4.1 | Agreed |
| Intervention longer than 10 s | Audible warning through the end of the intervention | R79 5.1.6.1.2.1 | Agreed |
| Second intervention within 180 s without driver steering | Audible warning from the second intervention onward. Starting with the third, each warning lasts at least 10 s longer than the previous one | R79 5.1.6.1.2.2 | Agreed |
| Object-triggered ELK (ESF) | Visual warning and either audible or haptic warning from the start to the end of the intervention | R79 5.1.6.2.6 | Agreed |
| HWA reaches aysmax and a front tire starts to encroach on the marking | Continue assistance within the available limits and avoid abrupt release. Issue a visual warning with an audible or haptic warning | R79 5.6.2.2.3 | Agreed |
| G1 reports an invalid path | Request driver takeover and ramp down torque gradually | ADAS Functions card | Agreed |
| Driver disables ELK | Continuous visual indication while ELK is off | EU 2021/646 3.2.3 | Agreed |

## 9. Edge cases

| # | Situation | Expected behavior | Owner | Status |
|---|---|---|---|---|
| 1 | HWA is active and an adjacent vehicle cuts in | ADAS Functions sends ELK REQUEST for that side. G1 switches to ELK and returns to HWA when done. EU 2021/646 3.3.2 permits ELKS suppression while another feature controls lateral motion. The project keeps object-triggered ELK available | Both | To be agreed |
| 2 | HWA enters a curve requiring more than aysmax | G1 plans within its limits, and the vehicle may approach the marking. ADAS Functions warns the driver (Section 8). ELK intervenes if drift continues to the ELK TLC threshold and the adjacent side is unsafe | Both | Proposed |
| 3 | Driver overrides HWA by steering to a different position in the lane | HWA stays enabled. G1 yields to the driver and plans from the current position when the driver releases control. An override flag is needed (Section 10) | Both | To be agreed |
| 4 | Driver turns on the turn signal while an overtaking vehicle approaches from behind | ELK can still intervene (overtaking-vehicle ELK test with the turn signal on) | ADAS Functions | Proposed |
| 5 | Driver signals and deliberately crosses a solid marking or moves onto the shoulder for an emergency stop | Inhibit LKA and boundary-triggered ELK | ADAS Functions | Proposed |
| 6 | Vehicle drifts back and forth between the markings because the driver is drowsy | Count each correction as a new intervention and escalate audible warnings under the 180 s rule | ADAS Functions | Agreed |
| 7 | Driver completes a lane change and the lane model changes its reference lane (lane_change) | ADAS Functions cancels pending requests, recomputes DLC and TLC for the new lane, and suppresses activation for 1 s. G1 changes its reference path continuously | Both | Proposed |
| 8 | A c0 jump creates a spurious 0.3–1 m DLC step | Use c0_jump to ignore TLC in that frame. Do not activate or cancel based on a single frame containing the jump | ADAS Functions | Proposed |
| 9 | False detection with low existence_probability appearing in only 1–2 frames | Consider only objects with existence ≥ 0.7 detected for at least three consecutive frames (0.15 s) | ADAS Functions | Proposed |
| 10 | Oncoming vehicle in the adjacent lane while the ego vehicle is not drifting | No intervention. ELK requires both TLC ≤ 0.8 s and an unsafe adjacent lane | ADAS Functions | Agreed |
| 11 | Both boundaries are lost during intervention | ADAS Functions holds REQUEST. G1 follows the previous path for at most 1 s and then reports it invalid. ADAS Functions requests driver takeover | Both | Agreed |
| 12 | ESC intervenes for slip during LKA or ELK intervention | ADAS Functions sends OFF and yields to ESC | ADAS Functions | Proposed |
| 13 | Speed drops below 65 km/h during intervention | Complete the current intervention and inhibit new activations | ADAS Functions | Proposed |
| 14 | FunctionRequests exceeds the 60 ms receive timeout | G1 treats all three features as off and reports an invalid path, as specified on the Path Planner card | G1 | Agreed |
| 15 | Driver requests HWA while the vehicle is 0.4 m off center | HWA can engage because the offset is below 0.5 m. G1 returns to center with a_y ≤ 0.5 m/s² | Both | Proposed |

## 10. Simulation stub outputs

The stub publishes the same `FunctionRequests` message as the production module at 50 Hz. The agreed per-feature fields are state, side, tlc and elk_reason.

The following extensions are proposed to support the situations above. The schema on the card still needs a corresponding update if these proposals are accepted.

| Field | Type | Rationale | Status |
|---|---|---|---|
| Add UNAVAILABLE and FAULT to state | uint8 enum { OFF, UNAVAILABLE, STANDBY, REQUEST, FAULT } | OFF means the driver disabled the feature. UNAVAILABLE means it is enabled but general conditions are unmet (e.g., below 70 km/h or poor lane marking quality). FAULT indicates a fault. G1 handles all three as OFF, while logs and test scenarios can distinguish them | To be agreed |
| driver_override | bool, shared by the message | Indicates driver override (T_drv ≥ 3.0 Nm). G1 yields to the driver and replans HWA from the current position on release (edge case 3) | To be agreed |
| cancel_reason | uint8 enum { NONE, DRIVER_OVERRIDE, INDICATOR, SPEED, LANE_QUALITY, ESC, FAULT }, per feature | Records why a request was cancelled, for logging only | Proposed |

The stub also records a `HmiStatus` message for logging and evaluation, separate from the G1 interface. It contains visual and audible warning status, hands-off warning level, and the intervention count over 180 s.

## 11. Worked decision examples

**Example 1. Inadvertent drift on a highway with a dashed marking and an empty adjacent lane.** v = 25 m/s (90 km/h), LKA enabled and HWA off. The simulated vehicle has W = 1.9 m and x_f = L = 2.9 m (Vehicle Model card).

- t = 0. The left marking at the front axle is y_L(x_f) = 1.80 m, so DLC_L = 1.80 − 0.95 = 0.85 m. v_lat_L = 0.40 m/s and TLC = 2.1 s. T_drv = 0.2 Nm, steering wheel rate is 3 °/s and the turn signal is off. The module classifies the drift as inadvertent and stays in standby.
- t ≈ 1.1 s. DLC_L = 0.40 m and TLC = 1.0 s. All conditions hold, so send **LKA REQUEST, side LEFT, tlc 1.0**. G1 selects LKA and the visual warning turns on.
- t ≈ 3.6 s. G1 reports COMPLETED. ADAS Functions returns LKA to STANDBY. With no remaining requests, control returns to the driver.

**Example 2. Same drift as Example 1, with an oncoming vehicle.** A two-way road has a dashed center marking and an oncoming vehicle travelling at 20 m/s, 90 m away.

- t ≈ 1.1 s. Send LKA REQUEST as above (TLC = 1.0 s).
- ADAS Functions also checks object-triggered ELK. When TLC reaches 0.8 s, the conflict window is 0.8–2.8 s. At a closing speed of 45 m/s, the closing distance over this interval spans 36–126 m, covering the 90 m separation. The adjacent lane is unsafe, so send **ELK REQUEST, side LEFT, elk_reason ONCOMING**.
- G1 transitions from LKA to the higher-priority ELK and uses the 3.0 m/s² budget.

**Example 3. Intentional steering with the turn signal on and an overtaking vehicle in the adjacent lane.** v = 20 m/s, left turn signal on, T_drv = 1.8 Nm to the left, v_lat = 0.6 m/s. The overtaking vehicle travels at 22.2 m/s in the left lane with its front end 7 m behind the ego vehicle's rear end.

- The turn signal inhibits LKA and boundary-triggered ELK.
- Object-triggered ELK still checks the hazard. At TLC = 0.8 s the conflict window is 0.8–2.8 s. The overtaking vehicle gains 1.8–6.2 m and closes to 0.8 m behind the ego vehicle, entering its envelope expanded by 2 m. Send **ELK REQUEST**.
- The driver holds the steering wheel and increases T_drv to 3.4 Nm against ELK for 0.1 s. Treat this as an override. Send **ELK OFF** with driver_override = true, issue the warning and inhibit ELK reactivation for 3 s. Deliberate driver control takes priority.

## 12. Open decisions

1. **Activation thresholds.** LKA at TLC 1.0 s, solid-marking and road-edge ELK at 0.6 s, and object-triggered ELK at 0.8 s. Decide whether to retain the thresholds or revise them after closed-loop testing.
2. **Intervention budgets** (Section 7). HWA total a_y of 2.5 m/s², LKA adds 1.5 m/s², ELK adds 3.0 m/s² with a total of 4.0 m/s², and jerk limits of 5 / 5 / 10 m/s³. Confirm before adding them to the Path Planner card.
3. **ELK while HWA is active** (edge case 1). Decide whether to keep object-triggered ELK available as proposed.
4. **Driver intent thresholds.** Passive torque of 0.5 Nm, intentional torque of 1.5 Nm, override torque of 3.0 Nm, and a 3 s hold-off after override.
5. **Maximum offset for HWA engagement.** 0.5 m.
6. **Output extensions** (Section 10). Decide whether to add UNAVAILABLE and FAULT to state and add driver_override to the schema.
7. **Inputs to the simulation stub.** The proposal is to consume the same lane model, objects and CAN messages as G1, including injected faults. Camera faults would then affect activation as they would on the vehicle, making it harder to separate G1 performance from activation faults. The other option is to use scenario ground truth.

## References

- [UN Regulation No 79, OJ L 2025/3](https://upload.wikimedia.org/wikipedia/commons/f/f3/OJ_L_202500003_of_2025_-_EN_English.pdf), [EUR-Lex version](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202500003)
- [Commission Implementing Regulation (EU) 2021/646, ELKS](https://eur-lex.europa.eu/eli/reg_impl/2021/646/2021-04-20/eng), consulted via the [LawPlayer copy](https://lawplayer.com/eu/act/32021R0646)
- [Euro NCAP LSS Test Protocol v4.3](https://cdn.euroncap.com/cars/assets/euro_ncap_lss_test_protocol_v43_f2ddd5f6d6.pdf)
- [Euro NCAP Assessment Protocol Safety Assist Collision Avoidance v10.4.1](https://cdn.euroncap.com/cars/assets/euro_ncap_assessment_protocol_sa_collision_avoidance_v1041_fafe1dd418.pdf)
- [ISO 11270:2014 summary](https://standards.iteh.ai/catalog/standards/iso/808a3e9d-fc87-4892-85d1-6087e2ee3370/iso-11270-2014) (primary text pending review)

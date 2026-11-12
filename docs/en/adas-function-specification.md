# ADAS Function Specification

| Field | Value |
|---|---|
| Document ID | `ADAS-FS` |
| Version | 1.4 |
| Status | BL1 |
| Author | thongbui |
| Reviewer | thongbui |
| Last updated | 2026-11-12 |

## 1. Purpose and scope {#adas-scope}

- **Purpose:** Specify when the ADAS Functions module sends HWA, LKA, and ELK requests to the path planner, for which side, and at which thresholds.
- **Scope:** Availability conditions, driver intent, activation, termination and reactivation decisions, driver warnings, and the `FunctionRequests` message.
- **Out of scope:** Path planning, arbitration, and a_y limits (Software Architectural Design); production HMI; the longitudinal module.
- **In the simulator:** The stub uses the thresholds in this document and sends the same `FunctionRequests` as the real module. There is no in-cabin camera or real HMI. The Software Qualification Test Specification defines how stub inputs are selected (modes A and B).

## 2. References {#adas-references}

| Document | Use |
|---|---|
| [UN R79, OJ L 2025/3](https://upload.wikimedia.org/wikipedia/commons/f/f3/OJ_L_202500003_of_2025_-_EN_English.pdf) | HWA is ACSF B1 (5.6.2), LKA and marking-based ELK are CSF (5.1.6.1), and object-based ELK is ESF (5.1.6.2); override and warnings |
| [EU 2021/646 (ELKS)](https://eur-lex.europa.eu/eli/reg_impl/2021/646/2021-04-20/eng) | 70–130 km/h speed range, default enablement, deactivation, and permitted suppression conditions |
| [Euro NCAP LSS Test Protocol v4.3](https://cdn.euroncap.com/cars/assets/euro_ncap_lss_test_protocol_v43_f2ddd5f6d6.pdf), [Assessment Protocol SA v10.4.1](https://cdn.euroncap.com/cars/assets/euro_ncap_assessment_protocol_sa_collision_avoidance_v1041_fafe1dd418.pdf) | Test scenarios, DTLE, 3.5 Nm override torque, ELK with turn indicator active, and DIM |
| [ISO 17361:2017](https://standards.iteh.ai/catalog/standards/iso/c3d927a6-f4e1-4b4d-91d2-548cf5953983/iso-17361-2017) (summary page) | No warning earlier than approximately 1.5 s TLC |
| ISO 21448:2022 (SOTIF) | No unintended intervention when perception quality is poor |
| [UN R171 (DCAS)](https://eur-lex.europa.eu/eli/reg/2025/1899/oj/eng) (summary page) | Manufacturer-declared conditions for entering active mode |
| [Interface Control Document](report.html?doc=path-planner-interface-control-document&lang=en), [Software Requirements Specification](report.html?doc=path-planner-software-requirements-specification&lang=en), [Software Architectural Design](report.html?doc=path-planner-software-architectural-design&lang=en) | `FunctionRequests` and `PathStatus` schemas; planner requirements; how the planner intervenes |

## 3. Regulatory classification {#adas-classification}

| Function | Regulatory classification | Enablement and disablement |
|---|---|---|
| HWA | ACSF Category B1 (R79); falls under R171 when combined with ACC | Enabled by the driver using a button, with ACC already enabled; disabled in one action (R79 5.6.2.1.2) |
| LKA | Lane marking-based CSF (R79 2.3.4.2 c) | Enabled by default; disabled through a menu |
| ELK, solid marking and road edge | CSF and ELKS | Enabled by default at each startup; requires at least two actions to disable (EU 2021/646 Annex I 3.2.1) |
| ELK, oncoming and overtaking vehicles | ESF (R79 2.3.4.3 a) | Same as above |

## 4. Division of responsibilities with the path planner {#adas-role}

| Responsibility | ADAS Functions module | Path planner |
|---|---|---|
| Settings (HWA button, LKA and ELK menu) | Reads them | Has no access to them |
| Availability conditions (Section 7) | Checks them | Receives the result through `state` |
| DLC, v_lat, and TLC with uncertainty (Section 5) | Calculates them independently of the planner (PP-ADR-014) | Uses TLC to select the path duration and computes its own lateral state |
| Hazard beyond the lane marking (Section 6) | Evaluates it | Does not evaluate it |
| Driver intent (Section 8) | Infers it | Receives `driver_override` |
| Driver warnings (Section 10) | Sends them to HMI | Reports `lateral_limit_reached` and `path_valid` |
| Arbitration, path, limits, and intervention termination | Does not handle these | Handles these |
| Sensor filtering | Does not filter again. The lane model, state estimator, and ego-motion already filter their outputs and include variances. Must tolerate residual errors | Same as the ADAS Functions module |

## 5. Quantities calculated by the ADAS Functions module {#adas-quantities}

v: speed; v_y: lateral velocity at the rear axle center; r: yaw rate; x_f: wheelbase; W: `vehicle_width`. Left marking y_L(x) = c0 + c1·x + c2·x² + c3·x³, with y positive to the left.

| Quantity | Calculation |
|---|---|
| DLC_L | y_L(x_f) − W/2: from the outer edge of the left front tire to the inner edge of the left lane marking (as in Euro NCAP DTLE) |
| v_lat_L | v_y + r·x_f − v·y_L'(x_f), with y_L'(x) = c1 + 2·c2·x + 3·c3·x² |
| TLC_L | DLC_L / v_lat_L when v_lat_L ≥ 0.05 m/s; otherwise infinity |
| Right side | DLC_R = −y_R(x_f) − W/2; v_lat_R = −(v_y + r·x_f) + v·y_R'(x_f) |
| Uncertainty | σ_DLC ≈ √(σ_c0² + x_f²·σ_c1²); σ_vlat ≈ √(v²·σ_c1² + σ_vy²); σ_TLC ≈ TLC·√((σ_DLC/DLC)² + (σ_vlat/v_lat)²) |

**Rules for using uncertainty** (ISO 21448: no unintended intervention when perception quality is poor; Euro NCAP Assessment 4.3.3.5: no intervention contrary to driver intent):

| Rule | Condition |
|---|---|
| Confirmed drift toward the marking | v_lat − `k_sigma`·σ_vlat ≥ 0.05 m/s |
| Drift direction uncertain | Use only the LKA DLC threshold (`dlc_lka`) |
| Excessive noise | σ_TLC > `sigma_tlc_max` or the lane marking is unreliable: UNAVAILABLE |
| LKA confirmation | The activation condition holds for `n_confirm` consecutive lane model updates. Does not apply to ELK |

## 6. What lies beyond the lane marking {#adas-beyond-line}

| Beyond the lane marking | Function responsible |
|---|---|
| Crossable marking (`crossable = true`), empty adjacent lane | LKA if enabled; if LKA is disabled, no intervention |
| Non-crossable marking (`crossable = false`) | LKA first; ELK if LKA is disabled or insufficient |
| Road edge (`road_edges[]`) | ELK |
| Oncoming or overtaking vehicle in the conflict window | ELK |

**Assessing adjacent-lane vehicles** (object-based ELK):

1. Use the lane model to assign objects to lanes. Select objects in the lane on the side toward which the ego vehicle is drifting, with `existence_probability` ≥ `exist_min` and at least `n_track` consecutive detections.
2. Predict longitudinal positions at constant velocity.
3. Conflict window: [TLC, TLC + `t_conflict`].
4. The adjacent lane is unsafe if, during the window, an object lies inside the box around the ego vehicle body, extended at each end by `box_margin`.
5. If the driver signals a lane change, ELK intervenes only when a vehicle approaching from behind cannot brake in time, meaning any of three conditions holds: the other vehicle is alongside (box extended by `abreast_margin` during [TLC, TLC + 1 s]); its TTC to the rear of the ego vehicle is ≤ `ttc_rear`; or it needs a deceleration Δv² / (2·distance) > `decel_rear`. Otherwise, warn only. The Euro NCAP test with the turn indicator active is the alongside case, so it still passes.

## 7. Availability conditions {#adas-availability}

If the conditions are not met, the function shall not send REQUEST. Except for the speed range (EU ELKS), the regulations do not specify numerical values; R79 5.6.2.3.1.1 leaves them to the manufacturer to declare.

| Condition | HWA | LKA | ELK | Source |
|---|---|---|---|---|
| Settings | Enabled by the driver, with ACC enabled | Enabled in the menu | Enabled | R79 5.6.2.1.2; EU 2021/646 3.2.1 |
| Speed | 10–130 km/h; wait below 10 km/h | Activates from 70 km/h, remains active until speed falls below 65 km/h, up to 130 km/h | Same as LKA | EU 2021/646 3.6.1; R79 B1 |
| Lane boundaries | Two markings, one marking plus stored lane width, or a lane center the planner infers from adjacent-lane markings and road edges | Marking on the drift side is MEASURED with confidence ≥ `conf_ego` and visible range ≥ `view_min` | Same as LKA. Road-edge ELK uses a directly MEASURED edge with confidence ≥ `conf_edge`. It also needs a reliable opposite boundary, or the stored lane width if the edge has already been associated with the ego lane | mentor, PP-SWR-047, PP-TS-007 |
| Unreliable boundary | — | UNAVAILABLE | UNAVAILABLE on that side | mentor |
| Free space | `lane_too_narrow = false` | — | — | PP-SWR-063 |
| ESC | HWA continues if ESC intervenes | Suppressed if ESC intervenes or is disabled | Same as LKA | EU 2021/646 3.2.2, 3.3.2 |
| Inputs | Valid LaneModel, IMU, speed, and steering angle | Same as HWA, plus VehicleStateEstimate | Same as LKA; object-based intervention also requires ObjectList | PP-SWR-140 to 144 |
| `path_valid` | — | true | true | PP-SWR-043 |

**HWA entry.** When the driver presses the button, HWA enters active mode only if these additional conditions are met. Otherwise, reject entry and notify the driver:

| Condition | Threshold | Source |
|---|---|---|
| Vehicle within lane | DLC ≥ `hwa_entry_dlc` on both sides | team agreement |
| Offset from lane center | ≤ `hwa_entry_offset` | team agreement |
| Heading error relative to lane | ≤ `hwa_entry_heading` | team agreement |
| Hands on steering wheel | Yes | R79 5.6.2.2.5 |
| Turn indicator | Off | team agreement |

## 8. Driver intent {#adas-driver-intention}

Following Euro NCAP DIM, use only signals available on the vehicle: driver torque, steering wheel angle and angular rate, and turn indicator. The R79 override force of 50 N corresponds to about 9.5 Nm at a steering wheel rim radius of 0.19 m.

| Situation | Condition | Outcome | Source |
|---|---|---|---|
| Inattentive driver, unintentional drift | Torque < `torque_passive` and steering wheel rate < 15 °/s for 0.5 s | Activation permitted | Euro NCAP: steering wheel rate 0 ± 15 °/s before drifting |
| Signaled lane change | Turn indicator toward the drift side, or switched off less than `t_indicator` ago | Suppress LKA and marking-based ELK; object-based ELK follows Section 6, step 5 | Euro NCAP (turn indicator 1.0 ± 0.5 s before steering) |
| Unsignaled lane change | Torque ≥ `torque_intent` toward the marking for 0.2 s; or steering wheel rate ≥ 30 °/s toward the marking | Same as above | team agreement |
| Override during intervention | Torque ≥ `torque_override` against the intervention for 0.1 s | Send OFF and set `driver_override`; do not reactivate on the same side for `t_reactivate_override` | R79 5.1.6; Euro NCAP ≤ 3.5 Nm |
| Sudden evasive steering | v_lat > `v_lat_swerve`, turn indicator off | Suppress both LKA and ELK, even if there is a vehicle in the adjacent lane; warn only | R79 5.1.6: the driver can always override |
| Hands off the steering wheel | Torque continuously < 0.3 Nm | HWA: visual warning after `t_hands_off_visual`, audible warning after `t_hands_off_acoustic`, and switch off after `t_hands_off_off`. LKA and ELK can still intervene | R79 5.6.2.2.5 (latest permitted timing) |

If the driver holds the steering wheel with torque ≥ `torque_override`, cancel all interventions, even if the driver deliberately steers toward another vehicle: at L2, the driver remains responsible.

## 9. Activation and termination {#adas-activation}

Evaluate each side and function every 25 ms cycle. Send REQUEST when the availability conditions are met, driver intent does not suppress activation, uncertainty permits it, no waiting period is in effect, and the condition below is met.

| Function | Activation condition | Source of limit |
|---|---|---|
| LKA | TLC ≤ `tlc_lka`, or DLC ≤ `dlc_lka` with v_lat ≥ 0.05 m/s; and 0.1 ≤ v_lat ≤ 1.0 m/s | Euro NCAP: DTLE ≥ −0.3 m at v_lat of 0.2–0.6 m/s; ISO 17361: no earlier than 1.5 s TLC |
| ELK, solid marking | TLC ≤ `tlc_elk_line` to that marking | Euro NCAP, EU 2021/646: DTLE ≥ −0.3 m |
| ELK, road edge | TLC ≤ `tlc_elk_line` to the road edge | Euro NCAP: DTLE ≥ −0.1 m |
| ELK, oncoming or overtaking vehicle | TLC ≤ `tlc_elk_object` to the marking, and the adjacent lane is unsafe (Section 6) | Euro NCAP: no collision, lateral clearance ≥ 0.3 m |

- If both sides request intervention, send the side with the shorter TLC.
- ELK is still requested while HWA is active (EU 2021/646 3.3.2 permits suppression; this project does not suppress it).
- If another vehicle cuts in and the ego vehicle is not drifting, do not request ELK. The planner offsets the target center and the longitudinal module maintains clearance.

| Event | ADAS Functions module action |
|---|---|
| Planner reports COMPLETED for a function | That function returns to STANDBY. Reactivate on the same side once DLC has reached ≥ `dlc_rearm` and then decreases again, or after `t_rearm` |
| Planner reports ELK ACTIVE | Return same-side LKA to STANDBY. Suppress new LKA requests on that side while ELK is ACTIVE |
| Planner reports ELK COMPLETED | Apply the LKA reactivation conditions for COMPLETED on the same side, even if LKA is already in STANDBY |
| Driver override | Send OFF immediately. Wait `t_reactivate_override`, except for object-based ELK |
| Speed falls below 65 km/h during intervention | Hold REQUEST until COMPLETED; do not start a new intervention |
| One marking is lost during intervention, and the remaining one is reliable | Hold REQUEST; the planner uses the remaining marking plus stored lane width |
| Both ego-lane markings are lost during intervention, and another reliable boundary remains | Cancel marking-based intervention. Road-edge ELK continues if the remaining boundaries meet the conditions in Section 7 |
| No reliable boundary remains during intervention | Hold REQUEST; the planner follows the previous path for up to `T_coast`, then marks it invalid (PP-SWR-124) |

### 9.1 Function states {#adas-modes}

Values of `state` in `FunctionRequests` ([Interface Control Document 5.6](report.html?doc=path-planner-interface-control-document&lang=en#function-requests)). Under R79, OFF corresponds to off mode, STANDBY and UNAVAILABLE to standby mode, and REQUEST to active mode.

| From | To | When | Function | Source |
|---|---|---|---|---|
| OFF | STANDBY | Enabled in the menu or enabled by default at startup | LKA, ELK | Section 3 |
| STANDBY | UNAVAILABLE | An availability condition is unmet | LKA, ELK | Section 7 |
| UNAVAILABLE | STANDBY | All availability conditions are met again | LKA, ELK | Section 7 |
| STANDBY | REQUEST | Activation conditions are met and driver intent allows intervention | LKA, ELK | Sections 8, 9 |
| REQUEST | STANDBY | The planner reports COMPLETED | LKA, ELK | Section 9 |
| REQUEST | OFF | The driver overrides steering | LKA, ELK | Sections 8, 9 |
| OFF | STANDBY | `t_reactivate_override` expires after the override | LKA, ELK | Section 9 |
| OFF | REQUEST | The driver presses the button while ACC is on and the availability and HWA entry conditions are met | HWA | Sections 3, 7 |
| REQUEST | OFF | The driver's hands are off the steering wheel for more than `t_hands_off_off`, or the driver switches it off with one action | HWA | Sections 3, 8 |
| REQUEST | UNAVAILABLE | An availability condition is unmet | HWA | Section 7 |
| UNAVAILABLE | REQUEST | Availability and HWA entry conditions are met again. HWA resumes automatically | HWA | team agreement, as in Toyota LTA and Volvo Pilot Assist |
| Any state | FAULT | The ADAS Functions module has a fault | HWA, LKA, ELK | Interface Control Document 5.6 |

## 10. Driver warnings {#adas-warnings}

In the simulator, warnings are only logged via the `HmiStatus` message.

| Event | Warning | Source |
|---|---|---|
| Each LKA or ELK intervention | Visual indicator, held for at least 1 s or until the intervention ends | R79 5.1.6.1.1; EU 2021/646 3.6.4.1 |
| Intervention longer than 10 s | Audible warning until the end of the intervention | R79 5.1.6.1.2.1 |
| Second intervention within 180 s without driver steering input | Audible warning from the second intervention; from the third onward, each warning is at least 10 s longer than the previous one | R79 5.1.6.1.2.2 |
| Object-based ELK (ESF) | Visual warning and either an audible or haptic warning throughout the intervention | R79 5.1.6.2.6 |
| Signaled lane change when a vehicle behind can still brake in time | Blind spot warning, without steering intervention | team agreement |
| HWA reaches aysmax and a front tire starts to touch the lane marking | Maintain assistance as far as possible; visual warning with audible or haptic warning. Use `lateral_limit_reached` and DLC | R79 5.6.2.2.3 |
| `path_valid = false` | Prompt the driver to take over steering | team agreement |
| `lane_too_narrow = true` when the driver presses the HWA button | Indicate that HWA is unavailable | team agreement |
| HWA enters UNAVAILABLE | The HWA indicator changes to standby. HWA resumes automatically when the conditions are met | team agreement |
| HWA enters OFF because the driver's hands are off the wheel | Indicate that HWA is off. The driver must press the button to re-enable it | R79 5.6.2.2.5 |
| Driver disables ELK | Continuous visual indicator | EU 2021/646 3.2.3 |

## 11. Edge cases {#adas-edge-cases}

Numbers match the planner's Edge cases section in the Software Architectural Design.

| # | Situation | ADAS Functions module action |
|---|---|---|
| 1a | HWA is active and the vehicle drifts toward an occupied adjacent lane | Request ELK as usual |
| 1b | Another vehicle encroaches on the ego lane while the ego vehicle is centered | Do not request ELK (large TLC) |
| 2 | HWA enters a curve that requires more lateral acceleration than aysmax allows | Warn when the tire starts to touch the marking; request ELK if the ELK threshold is reached and the other side is hazardous |
| 3 | Driver overrides HWA | Set `driver_override`; HWA remains enabled |
| 4 | Signaled lane change with a vehicle overtaking from behind | Follow Section 6, step 5; do not request intervention if the front tire is already more than 0.3 m beyond the marking |
| 5 | Turn indicator active, with intentional contact with a solid marking or departure onto the shoulder | No intervention in progress: do not activate. Intervention in progress: send OFF with `cancel_reason = INDICATOR` |
| 6 | Repeated drift from side to side | Each drift is a new request with the same thresholds; escalate warnings per R79 |
| 7 | Lane model reports `lane_change` | Cancel pending requests and recalculate for the new lane; do not activate for 1 s |
| 8 | A c0 jump causes a DLC jump | The consistency check shared with the planner flags the jumping frame. Do not activate or cancel based on it; use the new DLC if the next frame confirms it. If unconfirmed after 0.5 s, set UNAVAILABLE |
| 9 | Ghost object | Filter with `exist_min` and `n_track` |
| 10 | Oncoming vehicle, but no ego vehicle drift | Do not request ELK |
| 11 | Both ego-lane markings lost during intervention | If another reliable boundary remains, cancel LKA and ELK; HWA continues. If no boundary remains, hold REQUEST; prompt the driver to take over when `path_valid = false` |
| 12 | ESC intervenes during LKA or ELK intervention | Send OFF; yield to ESC |
| 13 | Speed below 65 km/h during intervention | Hold the request until COMPLETED |
| 13b | Stop-and-go traffic at 0–60 km/h | LKA and ELK are UNAVAILABLE; HWA continues if enabled |
| 15 | Driver presses the HWA button with a 0.4 m offset from lane center | Allow HWA entry if ≤ `hwa_entry_offset` |
| 16 | Sudden evasive steering with a vehicle in the adjacent lane | Suppress LKA and ELK; warn only |

## 12. Interface {#function-requests}

- **Output.** Send `FunctionRequests` to the path planner at 40 Hz; see the schema in the [Interface Control Document](report.html?doc=path-planner-interface-control-document&lang=en#function-requests). Receive `PathStatus` in return.
- **Log.** `HmiStatus`: visual and audible warnings, hands-off warning level, and intervention count within 180 s. For evaluation only.
- **Driver signals**, from the Motion team's signal list (mentor):

| Signal | Rate | Vehicle unit | Use |
|---|---|---|---|
| Driver torque | 50 Hz | Nm | Section 8 |
| Steering wheel angle | 100 Hz | ° | Log |
| Steering wheel rate | 100 Hz | °/s | Section 8 |
| Vehicle speed | 50 Hz | km/h | Section 7 |
| Turn indicator, HWA button, ESC status | Not in the signal list; the simulator reads them from the scenario file | — | Sections 7, 8 |

The module runs at 40 Hz, so it receives 1–2 torque samples per cycle. Thresholds use hold times rather than cycle counts.

## 13. Calibration parameters {#adas-calibration}

One set for all vehicles. The Software Qualification Test Specification sweeps the ranges; for `tlc_lka`, test three levels to select one.

| Parameter | Unit | Initial value | Sweep range | Limit |
|---|---|---|---|---|
| `tlc_lka` | s | 1.0 | 0.6; 1.0; 1.5 | ≤ 1.5 (ISO 17361) |
| `dlc_lka` | m | 0.1 | 0–0.2 | ≥ 0 |
| `tlc_elk_line` | s | 0.6 | 0.4–0.8 | DTLE per PP-SWR-086 |
| `tlc_elk_object` | s | 0.8 | 0.6–1.0 | Lateral clearance per PP-SWR-088 |
| `k_sigma` | — | 2 | 1–3 | ≥ 0 |
| `sigma_tlc_max` | s | 0.5 | 0.3–0.7 | > 0 |
| `n_confirm` | frame | 2 | 1–3 | ≥ 1 |
| `conf_ego` | — | 0.6 | 0.4–0.8 | 0–1 |
| `conf_edge` | — | 0.7 | 0.5–0.9 | 0–1 |
| `view_min` | m | 20 | 15–30 | > 0 |
| `exist_min` | — | 0.7 | 0.5–0.9 | 0–1 |
| `n_track` | frame | 3 | 2–5 | ≥ 1 |
| `t_conflict` | s | 3.0 | 1.5–3.0 | > 0 (PP-TS-009) |
| `box_margin` | m | 2.0 | 1.0–3.0 | ≥ 0 |
| `abreast_margin` | m | 1.0 | 0.5–2.0 | ≥ 0 |
| `ttc_rear` | s | 1.5 | 1.0–2.0 | > 0 |
| `decel_rear` | m/s² | 3.0 | 2.0–4.0 | > 0 |
| `hwa_entry_dlc` | m | 0.2 | 0–0.3 | ≥ 0 |
| `hwa_entry_offset` | m | 0.5 | 0.3–0.7 | ≥ 0 |
| `hwa_entry_heading` | ° | 2 | 1–3 | ≥ 0 |
| `torque_passive` | Nm | 0.5 | 0.3–1.0 | < `torque_intent` |
| `torque_intent` | Nm | 1.5 | 1.0–2.5 | < `torque_override` |
| `torque_override` | Nm | 3.0 | 2.0–3.5 | ≤ 3.5 (Euro NCAP); ≤ 9.5 (R79 50 N) |
| `t_indicator` | s | 2.0 | 1.0–3.0 | ≥ 0 |
| `v_lat_swerve` | m/s | 1.0 | 0.8–1.5 | > 0.7 (Euro NCAP intentional lane change) |
| `t_reactivate_override` | s | 3.0 | 1.0–5.0 | ≥ 0 |
| `dlc_rearm` | m | 0.3 | 0.2–0.5 | ≥ 0 |
| `t_rearm` | s | 2.0 | 1.0–3.0 | ≥ 0 |
| `t_hands_off_visual` | s | 10 | 5–15 | ≤ 15 (R79 5.6.2.2.5) |
| `t_hands_off_acoustic` | s | 15 | 10–30 | ≤ 30 (R79 5.6.2.2.5) |
| `t_hands_off_off` | s | 30 | 20–60 | ≤ 30 s after the audible warning begins (R79 5.6.2.2.5) |

## Appendix A. Analysis {#adas-appendix}

**A.1 Checking the v_lat formula.** On a straight road at v = 25 m/s and c1 = −0.016, v_lat_L = 0.40 m/s, one of the Euro NCAP drift rates. When the vehicle follows a curve exactly (r = v·κ, c1 = 0, c2 = κ/2), r·x_f and v·y_L'(x_f) cancel, giving v_lat = 0.

**A.2 Uncertainty** with σ_c0 = 0.03 m, σ_c1 = 0.002 (daytime, PP-ASM-011), x_f = 2.9 m, v = 25 m/s, DLC = 0.40 m, and v_lat = 0.40 m/s:

| Condition | σ_DLC | σ_vlat | σ_TLC | TLC ±2σ interval |
|---|---|---|---|---|
| Daytime | 0.031 m | 0.05 m/s | 0.15 s | 0.7–1.3 s |
| Night or rain (×2.5) | 0.077 m | 0.125 m/s | 0.37 s | 0.3–1.7 s |

Most noise comes from c1 multiplied by speed. With `k_sigma` = 2, confirming the drift direction requires v_lat ≥ 0.15 m/s in daytime and ≥ 0.30 m/s at night.

**A.3 Adjacent-lane vehicles** at 72 km/h, with `tlc_elk_object` = 0.8 s and a window of 0.8–2.8 s:

| Case | Outcome |
|---|---|
| Oncoming vehicle at 20 m/s, 90 m away: closes by 32–112 m during the window | Unsafe: ELK |
| Same as above, 200 m away: 88 m remain after 2.8 s | Safe: no ELK |
| Overtaking vehicle is 2.2 m/s faster, with its front 7 m behind the ego vehicle's rear: 0.8 m remain after 2.8 s | Unsafe: ELK |
| Same as above, with turn indicator active and a 20 m gap: requires 0.12 m/s² deceleration, TTC 9 s | Warn only |
| Turn indicator active, 5 m/s faster and 5 m away: requires 2.5 m/s², TTC 1.0 s | ELK |

**A.4 TLC thresholds.** With 0.2 s latency, LKA needs about 0.4 s TLC to meet Euro NCAP DTLE; LKA needs 0.4–0.7 s to avoid contact with the marking; road-edge ELK needs 0.3–0.5 s. Nighttime noise requires another 0.3–0.4 s. `tlc_elk_object` is earlier than `tlc_elk_line` because contact with an adjacent-lane vehicle is a collision; 0.8 s keeps the tire edge 0.09–0.29 m from the marking.

## Revision history {#revision-history}

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-11-10 | Restructured as the ADAS Function Specification, baseline BL1. Made all team-selected thresholds calibration parameters (Section 13); HWA can use an inferred lane center, while LKA and ELK require reliable ego-lane markings (mentor); added `lane_too_narrow` to HWA availability; moved the `FunctionRequests` schema to the Interface Control Document; consolidated calculation examples in Appendix A; removed status labels and open items |
| 1.1 | 2026-11-10 | The ADAS Functions module computes the lateral state and checks consistency independently of the planner (PP-ADR-014). It has its own `conf_ego` calibration, bounded by 0–1 |
| 1.2 | 2026-11-11 | Section 9.1 consolidates the state transitions in Sections 3, 7, 8, and 9. HWA resumes automatically from UNAVAILABLE. After a hands-off or driver-initiated shutdown, the driver must press the button to restart it (Sections 9.1, 10) |
| 1.3 | 2026-11-11 | Section 9 handles COMPLETED by function and withdraws the same-side LKA REQUEST on ELK completion |
| 1.4 | 2026-11-12 | Section 7 specifies the conditions for direct ELK boundaries. Section 9 withdraws same-side LKA from ELK ACTIVE onward. Section 13 sets `t_conflict` before verification per PP-TS-009 |

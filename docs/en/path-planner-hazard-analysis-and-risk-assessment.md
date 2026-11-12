# Hazard Analysis and Risk Assessment (HARA)

| Field | Value |
|---|---|
| Document ID | `PP-HARA` |
| Version | 1.2 |
| Status | Awaiting confirmation review |
| Author | thongbui |
| Reviewer |   |
| Last updated | 2026-11-11 |

## 1. Purpose and scope {#safety-scope}

- **Purpose.** Analyze hazards and assess risks for the HWA, LKA, and ELK lateral steering assistance system under ISO 26262-3 (concept phase). Propose S, E, C, ASIL ratings, and safety goals for confirmation review by the safety department.
- **Scope.** Item definition, operational situations, hazards, hazardous events, safety goals, SOTIF triggering conditions (ISO 21448), and path planner safety mechanisms.
- **Out of scope.** Functional safety concept, ASIL allocation to individual modules, technical safety concept; ACC and AEB; sensor and EPS hardware faults.
- **Expected response from the safety department.** Confirm or revise S, E, C, and ASIL in Section 6; confirm the safety goals in Section 7; respond to the points in Section 10.

## 2. References {#safety-references}

| Document | Use |
|---|---|
| ISO 26262-3:2018, Section 6 and Annex B | HARA process, S, E, and C scales, and ASIL table |
| ISO 26262-2:2018 | Confirmation review |
| ISO 21448:2022 | SOTIF triggering conditions |
| [UN R79, OJ L 2025/3](https://upload.wikimedia.org/wikipedia/commons/f/f3/OJ_L_202500003_of_2025_-_EN_English.pdf) | ACSF B1, CSF, and ESF classification; aysmax; 50 N override force; warnings; no sudden removal of steering assistance (5.6.2.2.3) |
| [EU 2021/646 (ELKS)](https://eur-lex.europa.eu/eli/reg_impl/2021/646/2021-04-20/eng) | Mandatory ELK, speed range |
| Euro NCAP LSS v4.3, Assessment Protocol SA v10.4.1 | Test scenarios, 3.5 Nm override torque, DTLE |
| Software Requirements Specification, Software Architectural Design, ADAS Function Specification, Software Qualification Test Specification | Requirements, how they are met, and verification (accompanying documents; not required to read this document) |

## 3. Item definition {#safety-item}

**Functions**

| Function | Description | R79 classification | Enablement |
|---|---|---|---|
| HWA | Continuously keeps the vehicle at the lane center, shifting the target when a large vehicle is in an adjacent lane | ACSF Category B1 | Enabled by the driver using a button; requires ACC to be enabled and hands on the steering wheel |
| LKA | Steers the vehicle back into the lane when it drifts toward a lane marking without driver intent | CSF | Enabled by default |
| ELK | Provides emergency steering when the vehicle is about to cross a solid lane marking, leave the road edge, or collide with an oncoming or overtaking vehicle in an adjacent lane | CSF, ESF; ELKS | Enabled by default at each startup |

**Boundaries and interfaces**

| Part | Details |
|---|---|
| Within the item | ADAS Functions module (decides when to intervene); path planner (lateral path planning and arbitration); Lateral Controller; EPS (actuation) |
| Inputs from outside the item | Lane model (camera), perception (camera, radar), state estimator (v_y), ego-motion, chassis CAN (yaw rate, speed, steering angle, driver torque), longitudinal module (ACC) |
| Outputs | Steering torque or angle via EPS; HMI warnings (visual, audible, haptic) |
| Fault response | The path planner sets `path_valid = false`; the Lateral Controller and EPS ramp torque down to 0; the HMI prompts the driver to take over steering |

**Steering authority limits** (safety mechanism applied in the path planner)

| Function | Total a_y | Added a_y | Jerk | Duration of a single intervention |
|---|---|---|---|---|
| HWA | ≤ 2.5 m/s² (R79 allows up to 3 m/s²) | ≤ 0.5 m/s² (initial value) | ≤ 5 m/s³ (R79) | Continuous |
| LKA | ≤ 3.0 m/s² | ≤ 1.5 m/s² | ≤ 5 m/s³ | ≤ 10 s (R79) |
| ELK | ≤ 4.0 m/s² | ≤ 3.0 m/s² | ≤ 10 m/s³ | ≤ 10 s (R79) |

The driver can override at any time. The ADAS Functions module cancels the intervention when driver torque is ≥ 3.0 Nm for 0.1 s, below the Euro NCAP limit of 3.5 Nm and well below the R79 limit of 50 N (about 9.5 Nm).

**Operating conditions**

| Condition | Value |
|---|---|
| Speed | HWA: 10–130 km/h. LKA and ELK activate from 70 km/h, remain active until speed falls below 65 km/h, and operate up to 130 km/h |
| Road | Reliable markings or road edges; lane width 2.5–5.5 m, including mixed car and motorcycle lanes in Vietnam |
| Vehicle | Any passenger car up to 2.5 m wide, including mirrors (QCVN 09:2015/BGTVT) |
| Driver | Level L2: the driver supervises and remains responsible for driving; HWA requires hands on the steering wheel |

**Assumptions**

- Inputs from outside the item have validity flags, counters, and CRC. Invalid input is detected within one 25 ms cycle.
- EPS ramps torque down when the path is invalid, without suddenly releasing torque.
- The L2 driver remains attentive and holds the steering wheel when HWA is enabled.

## 4. Operational situations {#safety-situations}

Exposure E per ISO 26262-3, Annex B:

| Basis | E1 | E2 | E3 | E4 | Use |
|---|---|---|---|---|---|
| Duration | — | Less than 1 % of driving time | 1–10 % | More than 10 % | OS-01 to OS-04, OS-06 |
| Frequency | Less than once per year for most drivers | A few times per year | At least once per month | On almost every trip | OS-05, OS-07 |

| ID | Situation | Proposed E | Rationale |
|---|---|---|---|
| OS-01 | Motorway at 90–130 km/h with a vehicle alongside in an adjacent lane | E3 | Vehicles alongside are common but do not account for most driving time |
| OS-02 | Two-way road at 70–90 km/h with an oncoming vehicle in the adjacent lane | E3 | Common outside urban areas in Vietnam; oncoming vehicles occupy the conflict zone for a small share of driving time |
| OS-03 | Lane next to a road edge, shoulder, or barrier at 70–130 km/h | E4 | Most roads have a lane next to the edge |
| OS-04 | HWA is steering through a motorway curve with R ≤ 500 m | E3 | Curves of this radius account for a small share of motorway length |
| OS-05 | Unintended drift toward an oncoming or overtaking vehicle | E1 | Requires both an inattentive driver and another vehicle in the conflict zone |
| OS-06 | HWA is steering on a motorway | E4 | Main HWA operating situation |
| OS-07 | The driver steers to avoid an obstacle in the lane | E2 | A few times per year |

## 5. Hazard identification {#safety-hazards}

A hazard is vehicle-level malfunctioning behavior derived from functional failure modes: unnecessary, wrong-direction, excessive, insufficient, or late intervention; sudden loss of assistance; abrupt steering; or opposing the driver.

| ID | Vehicle-level hazard | Contributing functional failure |
|---|---|---|
| H1 | Unintended lateral steering intervention: unnecessary, in the wrong direction, or excessive | The path follows a misidentified marking; incorrect arbitration; the path exceeds steering authority limits |
| H2 | Sudden loss of steering assistance while a function is keeping the vehicle on course | The path becomes invalid suddenly or is cut short without warning |
| H3 | Insufficient or late intervention when ELK needs to intervene | The intervention path is too weak or starts too late |
| H4 | Abrupt steering command | Step change in the path when switching functions or when the lane model jumps |
| H5 | Opposition to the driver during override or obstacle avoidance | The path pulls the vehicle back into the lane while the driver steers out |

## 6. Hazardous events and proposed ASIL ratings {#safety-hara}

**Scales.** S0: no injuries; S1: light to moderate injuries; S2: severe injuries, with survival likely; S3: life-threatening injuries. C0: generally controllable; C1: ≥ 99 % of drivers can avoid harm; C2: ≥ 90 %; C3: < 90 %. ASIL ratings are taken from ISO 26262-3 Table 4.

**Controllability rationale.** The added a_y budget limits lateral displacement before the driver reacts: displacement ≈ ½·a·t². In 1 s: HWA at 0.5 m/s² displaces the vehicle by 0.25 m; LKA at 1.5 m/s² by 0.75 m; ELK at 3.0 m/s² by 1.5 m. Hazard H1 is therefore split into events according to each function's steering authority.

| ID | Hazard | Function | Situation | Consequence | S | E | C | ASIL |
|---|---|---|---|---|---|---|---|---|
| HE-01 | H1 | HWA, LKA | OS-01 | High-speed side collision, loss of control | S3 | E3 | C2 | B |
| HE-02 | H1 | HWA, LKA | OS-02 | Head-on collision | S3 | E3 | C2 | B |
| HE-03 | H1 | HWA, LKA | OS-03 | Runs onto the shoulder or strikes a barrier at a shallow angle | S2 | E4 | C2 | B |
| HE-08 | H1 | ELK | OS-01, OS-02 | Side or head-on collision | S3 | E3 | C3 | C |
| HE-04 | H2 | HWA | OS-04 | Lane departure in a curve and collision with an adjacent-lane vehicle | S3 | E3 | C2 | B |
| HE-05 | H3 | ELK | OS-05 | Side or head-on collision | S3 | E1 | C3 | A |
| HE-06 | H4 | HWA | OS-06 | Abrupt steering and slight lateral deviation | S2 | E4 | C1 | A |
| HE-07 | H5 | HWA, LKA, ELK | OS-07 | Collision with an obstacle | S3 | E2 | C2 | A |

**Rationale**

| ID | S | C |
|---|---|---|
| HE-01, HE-02 | A collision with another vehicle at 70–130 km/h can lead to loss of control and secondary collisions | Added a_y ≤ 1.5 m/s²; the L2 driver holds the steering wheel and can override with 3 Nm |
| HE-03 | A run onto the shoulder or a shallow-angle barrier impact often causes severe injuries but is rarely fatal | Same as HE-01 |
| HE-08 | Same as HE-01, HE-02 | Added a_y of up to 3.0 m/s² displaces the vehicle by 1.5 m in 1 s, faster than most drivers can react |
| HE-04 | Lane departure in a curve at high speed | The driver is holding the steering wheel (HWA); R79 requires a warning and prohibits sudden removal of assistance |
| HE-05 | Same as HE-02 | Driver inattention is a condition of the situation. At L2 this is equivalent to a vehicle without ELK; see Section 10 |
| HE-06 | Abrupt steering within steering authority limits produces a small deviation | The driver holds the steering wheel; the step change is bounded by the a_y limit and EPS rotation rate |
| HE-07 | Collision with an obstacle at high speed | The intervention is cancelled at driver torque ≥ 3 Nm; steering authority is limited |

## 7. Safety goals {#safety-goals}

The FTTIs for SG-01 and SG-02 are estimated as the time for the vehicle to travel laterally through the 0.5 m remaining clearance to the marking under acceleration a: t = √(2·0.5 / a). The team agreed on the FTTIs for SG-04 and SG-05; they have not been calculated.

| ID | Safety goal | Hazardous event | Proposed ASIL | Safe state | Proposed FTTI |
|---|---|---|---|---|---|
| SG-01 | Prevent unintended lateral steering intervention beyond what the driver can control | HE-01, HE-02, HE-03, HE-08 | C | Disable lateral assistance, ramp torque down to 0 without suddenly releasing it (as in SG-02), and warn the driver | 0.5 s (a = 3.0 m/s²: 0.58 s) |
| SG-02 | Prevent sudden loss of steering assistance while a function is steering | HE-04 | B | Continue assistance as far as possible, then ramp torque down and issue a warning (R79 5.6.2.2.3) | 0.5 s (a = 2.5 m/s²: 0.63 s) |
| SG-03 | Intervene sufficiently to keep the vehicle in its lane when ELK is requested | HE-05 | A | Warn the driver | — |
| SG-04 | Prevent step changes in steering commands | HE-06 | A | Mark the path invalid and ramp torque down | 0.1 s (team agreement) |
| SG-05 | Do not oppose the driver during override | HE-07 | A | Cancel the intervention | 0.3 s (team agreement) |

## 8. SOTIF triggering conditions {#safety-sotif}

Sensor and algorithm limitations when no fault is present. Each condition has a mitigation in the path planner and is verified by a test case (S) or fault injection (F) in the Software Qualification Test Specification.

| ID | Triggering condition | Potential limitation | Mitigation | Verification |
|---|---|---|---|---|
| TC-01 | Old lane markings, cracks, or tar seams resembling markings | The lane model misidentifies a marking | Check boundary consistency at two time scales | F03 |
| TC-02 | Lane widening: emergency lane, branch, or added lane | The path shifts toward the widening | Anchor the lane center to the stable boundary | S6b |
| TC-03 | Night or rain | Lane model noise increases by a factor of 2.5 | Start from the previous path, rate-limit reference changes, and penalize jerk | F01, S12 |
| TC-04 | A crest obstructs visibility ahead of a curve | The curve is detected late | Limit a_y; set `lateral_limit_reached`; the longitudinal module slows the vehicle | S1b |
| TC-05 | A curve requires more lateral acceleration than aysmax allows | The path is truncated, and the vehicle approaches the lane marking | Same as TC-04 | S1b |
| TC-06 | Wet road, μ = 0.5 | Available tire grip is lower than the a_y limit | The ELK a_y limit of 4.0 m/s² is below the grip limit of 4.9 m/s² | S12 |
| TC-07 | Large vehicle in an adjacent lane, narrow lane, or objects on both sides | Center offset in the wrong direction or too close to an object | Shift away from the large vehicle based on the clearance to it. Stay centered with large vehicles on both sides. Limit the offset to the actual free space | S3, S3b, S15 |
| TC-08 | Traffic congestion at low speed | The path covers only a short distance | HWA continues; LKA and ELK are unavailable | S11 |
| TC-09 | Crosswind or road cross slope | The vehicle drifts even though the path is correct | Closed-loop Lateral Controller; LKA intervention | S4 |
| TC-10 | Prolonged loss of all lane boundaries | Dead reckoning accumulates error | Follow the previous path for up to 1 s, then mark it invalid | F05 |
| TC-11 | Incorrect curvature estimate at long range | The path follows a false curve | Fuse camera curvature with yaw rate and path history | F06 |
| TC-12 | Ego-lane markings are missing, but adjacent-lane markings or road edges remain visible | The lane center inferred from distant boundaries is offset | Require higher confidence for the boundaries used in inference; only HWA uses the inferred center | F21 |
| TC-13 | Narrow lane with a wide vehicle | Insufficient free space to keep the vehicle in the lane | Set `lane_too_narrow`; HWA is unavailable | S19 |

## 9. Path planner safety mechanisms {#safety-mechanisms}

| Mechanism | Safety goal | Requirement |
|---|---|---|
| Limit a_y, added a_y, and jerk by function | SG-01 | PP-SWR-001, 003, 110 to 115 |
| Arbitrate by priority, considering only functions in REQUEST | SG-01 | PP-SWR-030, 047 |
| Check lane boundary consistency | SG-01 | PP-SWR-121, 122, 148 |
| Maintain assistance at the limit; follow the previous path for up to 1 s when boundaries are lost | SG-02 | PP-SWR-005, 006, 037, 124 |
| Check continuity between consecutive paths every cycle | SG-04 | PP-SWR-031, 100 to 102, 126 to 128 |
| Mark the path invalid within one cycle when input is invalid | SG-01, SG-04 | PP-SWR-142, 143, 145 |
| Make the path follow the vehicle position during driver override | SG-05 | PP-SWR-039, 040 |
| Limit DTLE and distance to adjacent-lane vehicles | SG-03 | PP-SWR-086, 088 |

## 10. Open points for reviewer {#safety-open-points}

| # | Point for the safety department to address |
|---|---|
| 1 | Confirm or revise S, E, C, and ASIL in Section 6 |
| 2 | C3 for HE-08: ELK adds up to 3.0 m/s² of a_y, displacing the vehicle by 1.5 m in 1 s |
| 3 | E3 for OS-01 (vehicle alongside in an adjacent motorway lane) and OS-02 (oncoming vehicle on a two-way road) on Vietnamese roads |
| 4 | S2 for HE-03: Vietnamese shoulders often have few barriers and may have motorcycles, pedestrians, ditches, or trees. If classified as S3, HE-03 rises to ASIL C |
| 5 | S2 for HE-06: a slight deviation within the lane alone may be S1 (and therefore QM). S2 accounts for deviation into an occupied adjacent lane |
| 6 | HE-05 (insufficient ELK intervention): the team proposes ASIL A, from the table for S3, E1, C3. An alternative is QM: at L2, insufficient ELK intervention is equivalent to a vehicle without ELK, and the driver remains responsible for driving |
| 7 | Method for demonstrating C: test with drivers or rely on published controllability studies |
| 8 | FTTIs in Section 7: SG-01 and SG-02 are estimated from kinematics; SG-04 and SG-05 are agreed by the team; SG-03 has no FTTI yet. Check against the detection and response times of the path planner, Lateral Controller, and EPS |
| 9 | SOTIF acceptance criterion (number of unintended interventions over distance); the Software Qualification Test Specification currently requires 0 across all test cases |
| 10 | Triggering conditions without test cases: tunnels, shadows, sun glare, temporary roadwork markings, and mixed car and motorcycle lanes. The team will add test cases; please confirm whether the list is complete |

## Revision history {#revision-history}

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-11-10 | Rewritten as the HARA for the safety department. Made the item definition self-contained; added operational situations, proposed S, E, C, ASIL ratings, safe states, and FTTIs; split out HE-08 for ELK; added TC-13, safety mechanisms, and open points |
| 1.1 | 2026-11-10 | Added frequency-based E classification; recorded the basis for the SG-04 and SG-05 FTTIs; specified no sudden torque release in the SG-01 safe state; split the open points; added questions about S for HE-03 and HE-06; revised the ASIL rationale for HE-05 |
| 1.2 | 2026-11-11 | Updated TC-07 for the revised center offset (PP-ADR-008) |

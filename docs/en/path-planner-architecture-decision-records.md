# Architecture Decision Records

| Field | Value |
|---|---|
| Document ID | `PP-ADR` |
| Version | 1.4 |
| Status | BL1 |
| Author | thongbui |
| Reviewer | thongbui |
| Last updated | 2026-11-12 |

## 1. Purpose and scope {#adr-scope}

- **Purpose:** Explain why the path planner is designed as described in the Software Architectural Design: alternatives considered, decisions, and consequences.
- **Scope:** Path planner design decisions.

## 2. References {#adr-references}

| Document | Use |
|---|---|
| [Software Requirements Specification](report.html?doc=path-planner-software-requirements-specification&lang=en) | Requirements and assumptions addressed by the decisions |
| [Software Architectural Design](report.html?doc=path-planner-software-architectural-design&lang=en) | Design details with references to the PP-ADRs |
| [Software Qualification Test Specification](report.html?doc=path-planner-software-qualification-test-specification&lang=en) | Test cases for comparing the alternatives |
| Nygard (2011), Documenting Architecture Decisions | Decision record format |
| Werling et al. (2010); Apollo (Baidu) | References for PP-ADR-001, 004 |

## 3. Conventions {#adr-format}

| Item | Convention |
|---|---|
| ID | Assign `PP-ADR-nnn` sequentially. Do not renumber or reuse IDs |
| Contents | Five parts: context, alternatives considered, decision, consequences (benefits and trade-offs), and related items |
| Superseding a decision | Keep the old decision, note "superseded by PP-ADR-…" in its Decision row, and record the new decision in a new section |

## 4. Decision index {#adr-list}

| ID | Decision |
|---|---|
| PP-ADR-001 | Separate the lateral and longitudinal modules and exchange constraints |
| PP-ADR-002 | Compensate latency using the capture timestamp |
| PP-ADR-003 | Use two data-age thresholds: monitor and reject |
| PP-ADR-004 | Stitch trajectories and reset to the measured state when deviation is large |
| PP-ADR-005 | Share one lateral-state calculation with the ADAS Functions module |
| PP-ADR-006 | Check boundary consistency in the planner |
| PP-ADR-007 | Use three layers of noise mitigation based on the previous path |
| PP-ADR-008 | Set the center offset from the clearance to a large vehicle and limit it to actual free space |
| PP-ADR-009 | Follow the previous path for up to `T_coast`, then mark the path invalid |
| PP-ADR-010 | Compensate post-planner latency in the Lateral Controller |
| PP-ADR-011 | Infer the lane center from adjacent-lane markings and road edges in the planner |
| PP-ADR-012 | Use one calibration set for all vehicles |
| PP-ADR-013 | Use a C11 planner library with a C API and separate platform adapters |
| PP-ADR-014 | Calculate the lateral state independently in the planner and the ADAS Functions module |
| PP-ADR-015 | Report separate LKA and ELK phases in PathStatus |

## 5. Decisions {#adr-decisions}

### PP-ADR-001 Separate the lateral and longitudinal modules and exchange constraints {#adr-001}

| Field | Value |
|---|---|
| Context | When another vehicle encroaches on the lane or a curve is tighter than HWA can steer through, both lateral and longitudinal action are needed. The path planner is the lateral module only |
| Alternatives | A) One combined lateral and longitudinal planner. B) Two modules exchanging constraints through LateralLimits and LongitudinalPlan. C) Two modules without an exchange |
| Decision | B. The longitudinal module is the simulator's ACC stub, fixed across all planner versions. Retain C as the comparison baseline in S14 (mentor) |
| Consequences | Benefit: resembles a real vehicle; the longitudinal module can slow down before a curve. Trade-off: two additional interfaces; each side uses a message from the previous cycle, adding 25 ms of latency; a fallback is needed when LongitudinalPlan is lost |
| Related items | PP-SWR-009, 150 to 155; Software Architectural Design Section 6.1; S14 |

### PP-ADR-002 Compensate latency using the capture timestamp {#adr-002}

| Field | Value |
|---|---|
| Context | Lane model latency is 100 ± 20 ms (PP-ASM-001). Without compensation, the reference deviates by 0.25 m at 25 m on a curve with R = 250 m |
| Alternatives | A) No compensation. B) Compensate nominal latency: 0.05 m of deviation remains at 25 m due to jitter. C) Compensate from the capture timestamp using ego-motion |
| Decision | C |
| Consequences | Benefit: latency need not be known in advance; residual error comes only from ego-motion. Trade-off: depends on ego-motion and clock synchronization; an ego-motion fault invalidates the path immediately |
| Related items | PP-SWR-012, 013, 143; PP-ASM-001, 012, 013; Software Architectural Design Appendix A.1 |

### PP-ADR-003 Use two data-age thresholds: monitor and reject {#adr-003}

| Field | Value |
|---|---|
| Context | Actual latency is unknown (mentor). A single 170 ms threshold would mark every frame stale if actual latency were 200 ms |
| Alternatives | A) A single 170 ms threshold. B) Monitor at 170 ms (keep using the input and log it) and reject at 250 ms (treat the input as invalid) |
| Decision | B |
| Consequences | Benefit: the feature stays available when actual latency is slightly higher than assumed; logs reveal actual latency. Trade-off: the rejection threshold must be reset if measured latency is higher |
| Related items | PP-SWR-131 to 134; PP-ASM-001, 002; Software Architectural Design Appendix A.2 |

### PP-ADR-004 Stitch trajectories and reset to the measured state when deviation is large {#adr-004}

| Field | Value |
|---|---|
| Context | Starting the path from the measured state passes noise directly into it. Starting from the previous path is inaccurate once the vehicle has deviated |
| Alternatives | A) Start from the measured state every cycle. B) Start from the corresponding point on the previous path. C) Use B when the vehicle is close to the previous path and A when deviation exceeds `stitch_reset` |
| Decision | C, as in Apollo trajectory stitching. Always use A when LKA or ELK starts |
| Consequences | Benefit: continuity in normal operation and an accurate initial state after a large deviation. Trade-off: switching from B to A can cause a small step change. If LKA or ELK starts after the vehicle has deviated, PP-SWR-080 takes precedence over PP-SWR-031 |
| Related items | PP-SWR-031, 080; Software Architectural Design Section 4.2 |

### PP-ADR-005 Share one lateral-state calculation with the ADAS Functions module {#adr-005}

| Field | Value |
|---|---|
| Context | The ADAS Functions module (for TLC) and the planner (for intervention paths) need the same measured lateral state |
| Alternatives | A) Share a function with the same inputs. B) Have the planner calculate it independently. C) Have the ADAS Functions module publish the state in a message |
| Decision | A. Superseded by PP-ADR-014 |
| Consequences | Benefit: both modules use the same value. Trade-off: both depend on a shared library. B can give inconsistent results (TLC of 1.0 s versus 1.3 s); C adds about 20 ms of latency, and the planner still has to calculate the state for HWA |
| Related items | PP-SWR-080; Software Architectural Design Section 4.2 |

### PP-ADR-006 Check boundary consistency in the planner {#adr-006}

| Field | Value |
|---|---|
| Context | The lane model does not publish a c0 jump flag (PP-ASM-009); the Mobileye CAN protocol also has no such flag |
| Alternatives | A) Rely on a lane model flag. B) Check each boundary at two time scales in the planner: frame by frame against the previous frame transformed using ego-motion, and on a slower scale using parallelism and lane width |
| Decision | B. If a flag becomes available later, use it only as a secondary source |
| Consequences | Benefit: no dependency on the camera vendor; one mechanism for c0 jumps, misidentified markings, and lane widening. Trade-off: extra logic and calibration parameters; genuine lane changes are recognized after `T_confirm` |
| Related items | PP-SWR-060, 121, 122; PP-ASM-009; Software Architectural Design Section 4 |

### PP-ADR-007 Use three layers of noise mitigation based on the previous path {#adr-007}

| Field | Value |
|---|---|
| Context | The filtered lane model still fluctuates slightly (PP-ASM-011). A path that follows each frame causes the steering wheel to oscillate as well |
| Alternatives | A) Filter the sensor data again in the planner. B) Start from the previous path, rate-limit reference changes, and penalize jerk |
| Decision | B |
| Consequences | Benefit: smooth paths under noise without duplicating the lane model's work. Trade-off: slower response to genuine lane changes; the Software Qualification Test Specification measures both effects |
| Related items | PP-SWR-120; target PP-SWR-050; Software Architectural Design Section 4.1 |

### PP-ADR-008 Set the center offset from the clearance to a large vehicle and limit it to actual free space {#adr-008}

| Field | Value |
|---|---|
| Context | HWA shifts the target away from a large vehicle in an adjacent lane (assignment). The path must not shift toward a widening lane (mentor). The planner must operate for all lane widths of 2.5–5.5 m and all vehicles up to 2.5 m wide |
| Alternatives | A) Use clearance to the raw road edge and a fixed offset of ±0.3 m. B) Balance clearances on both sides, using the reference line's lane boundary on an unoccupied side. C) Shift away from the large vehicle by the shortfall from `gap_truck_min`. Balance the clearances when there are large vehicles on both sides. B and C both limit the offset to actual free space |
| Decision | C (2026-11-11, supersedes B). See the formula in Software Architectural Design Section 6. o_lim = max(0, min(`offset_max`, s − `dlc_offset_min`)), s = (W_lane − W_vehicle) / 2. With a large vehicle centered in the adjacent lane, the clearance to it exceeds the clearance to the lane boundary. B can then leave the path centered or shift it toward the large vehicle |
| Consequences | The path shifts away from the large vehicle, with a larger offset at smaller clearances. Lane widening does not pull the path toward that side. The path stays centered with large vehicles on both sides. It works for every lane and vehicle and respects PP-SWR-051. This adds `gap_truck_min` and depends on reference line quality. A wide vehicle in a narrow lane has little room to shift |
| Related items | PP-SWR-051, 055, 056, 060, 062; target 057; Software Architectural Design Section 6 |

### PP-ADR-009 Follow the previous path for up to `T_coast`, then mark the path invalid {#adr-009}

| Field | Value |
|---|---|
| Context | When no reliable boundary remains, the vehicle's position in the lane depends solely on ego-motion, which accumulates error. No regulation specifies a duration; R79 5.6.2.2.3 only requires that steering assistance not be removed suddenly |
| Alternatives | Follow the previous path for 0.5 s, 1 s, 2 s, or 3 s. With a yaw-rate bias of 0.3 °/s at 25 m/s, the respective deviations are 0.02, 0.06, 0.25, and 0.56 m |
| Decision | `T_coast` ≤ 1 s, initially 1 s |
| Consequences | Benefit: small deviation relative to the free space in the lane. Trade-off: including the 1 s for which the lane model already reconstructs the markings (PP-ASM-010), there are about 2 s without measured markings |
| Related items | PP-SWR-124; PP-ASM-008, 010; Software Architectural Design Appendix A.4 |

### PP-ADR-010 Compensate post-planner latency in the Lateral Controller {#adr-010}

| Field | Value |
|---|---|
| Context | About 66 ms elapse between path publication and wheel response (Software Architectural Design Section 3.3) |
| Alternatives | A) Have the planner advance the path by the post-planner latency. B) Have the Lateral Controller read the path at the current time plus actuation latency, using `header.stamp_us` and `time_from_start` |
| Decision | B |
| Consequences | Benefit: the two modules do not compensate the same latency twice; the planner does not need to know EPS latency. Trade-off: the Lateral Controller team must use the timestamp correctly (PP-ASM-017) |
| Related items | PP-SWR-012; PP-ASM-007, 014, 017; Software Architectural Design Section 3.3 |

### PP-ADR-011 Infer the lane center from adjacent-lane markings and road edges in the planner {#adr-011}

| Field | Value |
|---|---|
| Context | The lane model publishes markings for three lanes and road edges. Both ego-lane markings can disappear while adjacent-lane markings or road edges are still measured (mentor) |
| Alternatives | A) Follow the previous path for `T_coast`, then mark it invalid, ignoring other boundaries. B) Have the lane model reconstruct the ego-lane markings and publish PREDICTED. C) Infer the lane center from all remaining reliable boundaries in the planner and fuse the estimates by variance; inference requires confidence `conf_inferred` > `conf_ego` |
| Decision | C (mentor). Only HWA steers using an inferred lane center; LKA and ELK need reliable ego-lane markings (mentor) |
| Consequences | Benefit: HWA continues when the ego-lane markings are lost; extends the "one marking plus stored width" mechanism; the planner retains all consistency checks. Trade-off: a center inferred from distant boundaries has larger errors and is wrong if adjacent-lane widths change while markings are missing. A discards usable data; B prevents the planner from distinguishing measured markings from reconstructed ones |
| Related items | PP-SWR-047, 124, 147, 148; PP-ADR-006, 009; Software Architectural Design Section 4 |

### PP-ADR-012 Use one calibration set for all vehicles {#adr-012}

| Field | Value |
|---|---|
| Context | The system must integrate into any passenger car, including models that have not been released yet |
| Alternatives | A) One calibration set per vehicle. B) One shared calibration set; the planner obtains vehicle information only through VehicleConfig |
| Decision | B |
| Consequences | Benefit: no recalibration when integrating a new vehicle; demonstrates that the planner generalizes. Trade-off: the shared set can be less optimal for individual vehicles; all formulas must be parameterized by VehicleConfig |
| Related items | PP-SWR-062, 116, 117; Software Architectural Design Section 11; Software Qualification Test Specification (flexibility) |

### PP-ADR-013 Use a C11 planner library with a C API and separate platform adapters {#adr-013}

| Field | Value |
|---|---|
| Context | The mentor needs to integrate the planner into a real system for verification. The target platform is unknown (PP-ASM-019). The benchmark must evaluate the code that will be delivered |
| Alternatives | A) Python. B) Prototype in Python, then port to C. C) C11 with a C API and a separate adapter per platform. D) C++17 |
| Decision | C. Apply a subset of MISRA C:2012. The caller supplies state memory. The planner uses no dynamic allocation, file reads, or global variables. Calibration is generated as a constant struct at build time. The simulator calls the same library through the SIL adapter |
| Consequences | Platforms with C support can call the planner (AUTOSAR Classic, Adaptive, Linux, QNX, ROS 2). SIL and the target run the same source code with deterministic execution time. Algorithm trials take longer than in Python. Calibration changes require a rebuild. Free tools can check only part of MISRA C:2012 |
| Related items | PP-ASM-019, Interface Control Document Section 4, Software Detailed Design Section 3 |

### PP-ADR-014 Calculate the lateral state independently in the planner and the ADAS Functions module {#adr-014}

| Field | Value |
|---|---|
| Context | The assignment requires an end-to-end path planner. It must integrate into a real system (PP-ADR-013) where another team supplies the ADAS Functions module |
| Alternatives | A) Share a function with the ADAS Functions module (PP-ADR-005). B) Have the planner calculate the state from its own inputs. C) Have the ADAS Functions module publish the state in a message |
| Decision | B. The ADAS Functions module computes its own state as specified in ADAS Function Specification Section 5. Each module implements the same formulas independently |
| Consequences | The planner has no code dependency on the other module. The ADAS Functions stub in the simulator is independent of the planner. The module's TLC and the planner's lateral-state estimate can disagree (for example, 1.0 s versus 1.3 s). The planner must tolerate the discrepancy. PP-SWR-080 is still evaluated against the vehicle's actual state |
| Related items | Supersedes PP-ADR-005. See PP-ADR-013, PP-SWR-080, Software Architectural Design Section 4.2, and Software Detailed Design Section 9 |

### PP-ADR-015 Report separate LKA and ELK phases in PathStatus {#adr-015}

| Field | Value |
|---|---|
| Context | When ELK reaches COMPLETED, T9 can select LKA if it is in REQUEST under PP-SWR-033. The ADAS Functions module must identify which function just completed |
| Alternatives | A) Use a shared phase with `active_function`. B) Use a separate phase for each function |
| Decision | B. PathStatus has `lka_phase` and `elk_phase`. Each phase stays at COMPLETED until its request leaves REQUEST |
| Consequences | One message can report ELK COMPLETED and LKA ACTIVE. The sender and receiver must use the same schema version |
| Related items | PP-TS-011, PP-SWR-032, 033, 041, Interface Control Document Section 6.2 |

## Revision history {#revision-history}

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-11-10 | Restructured as Architecture Decision Records, baseline BL1. All decisions are final; PP-ADR-008 limits the offset to actual free space; PP-ADR-009 uses `T_coast` ≤ 1 s; added PP-ADR-012; removed status labels and open items |
| 1.1 | 2026-11-10 | Added PP-ADR-013 for the C11 library, C API, and separate platform adapters |
| 1.2 | 2026-11-10 | Added PP-ADR-014 for independent lateral-state calculation in the planner. Superseded PP-ADR-005 |
| 1.3 | 2026-11-11 | Selected C in PP-ADR-008, superseding B. The offset is based on the clearance shortfall from `gap_truck_min` |
| 1.4 | 2026-11-12 | Added PP-ADR-015 for separate LKA and ELK phases in PathStatus |

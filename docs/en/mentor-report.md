# Mentor Report

| Field | Value |
|---|---|
| Document ID | `PP-MR` |
| Version | 1.1 |
| Status | BL1 |
| Author | thongbui |
| Reviewer |   |
| Last updated | 2026-11-11 |

## 1. Purpose and scope {#summary-scope}

- **Purpose:** Summarize the path planner design and the evaluation system.
- **Scope:** The path planner for HWA, LKA, and ELK and the baseline technical documents.

## 2. System {#summary-system}

- **Problem:** One path planner for HWA, LKA, and ELK, running at 20–50 Hz. Paths must be smooth and feasible, feature transitions must not introduce step changes, and the planner must operate with real lane model faults.
- **40 Hz cycle:** Input check → latency compensation → reference line → arbitration (ELK > LKA > HWA) → path generation (Frenet) → stitching and continuity → feasibility → output.
- **Input:** LaneModel (three lanes and multiple types of road edge), ObjectList, chassis CAN, VehicleStateEstimate, ego-motion, FunctionRequests, LongitudinalPlan, VehicleConfig.
- **Output:** Trajectory (31 points, 0–3 s), PathStatus, LateralLimits.
- **ODD:** Vietnamese roads with lane markings or road edges; lane widths of 2.5–5.5 m; all passenger cars up to 2.5 m wide, including mirrors (QCVN 09:2015/BGTVT); one calibration set for all vehicles.

## 3. Key design decisions {#summary-design}

| Topic | Design | Rejected alternatives | ADR |
|---|---|---|---|
| Lateral and longitudinal planning | Two modules exchange constraints; the planner sends `v_max` so the longitudinal module can slow the vehicle before a curve | One combined planner; completely independent modules (retained as a comparison baseline) | 001 |
| Lane model latency | Compensate from the capture timestamp using ego-motion | No compensation (0.25 m deviation at 25 m); nominal latency compensation (0.05 m) | 002 |
| Unknown latency | Monitor at 170 ms; reject at 250 ms | A single 170 ms threshold | 003 |
| c0 jump flag | The planner checks boundary consistency at two time scales, using the same check for marking jumps, misidentified markings, and lane widening | Rely on a lane model flag | 006 |
| Loss of ego-lane markings | Infer the lane center from reliable adjacent-lane markings and road edges; only HWA uses it | Follow the previous path for 1 s, then mark it invalid; have the lane model reconstruct the markings | 011 |
| No remaining boundaries | Follow the previous path for up to 1 s, then mark it invalid | 0.5 s; 2 s; 3 s | 009 |
| Center offset near a large vehicle | Shift away by the shortfall from `gap_truck_min`. Limit the offset to the actual free space for any lane and vehicle | Fixed offset of ±0.3 m. Balancing clearances | 008 |
| Noise and continuity | Start from the previous path, rate-limit reference changes, and penalize jerk; project the path to satisfy continuity limits | Filter sensor data again in the planner | 004, 007 |
| Calibration | One set for all vehicles; the planner obtains vehicle information only through VehicleConfig | One set per vehicle | 012 |

Select the planning technique by benchmarking three candidates: duration-based quintic polynomials, Frenet sampling, and QP.

## 4. Compliance {#summary-compliance}

| Reference | Compliance criteria |
|---|---|
| UN R79 | HWA is ACSF B1: a_y ≤ 2.5 m/s² (limit: 3), jerk ≤ 5 m/s³, no driving onto the lane marking below aysmax, and no sudden removal of steering assistance. LKA and ELK are CSF and ESF: interventions ≤ 10 s and driver warnings. Override force ≤ 50 N |
| EU 2021/646 (ELKS) | ELK operates at 70–130 km/h and is enabled by default; DTLE follows ELKS |
| Euro NCAP LSS, Safety Assist | DTLE ≥ −0.3 m (lane marking), ≥ −0.1 m (road edge); distance to an adjacent-lane vehicle ≥ 0.3 m; override torque 3.0 Nm (≤ 3.5 Nm) |
| Assignment | Deviation between consecutive paths ≤ 0.05 m, 0.005 rad, 0.0003 1/m |
| ISO 26262, ISO 21448 | HARA with proposed ASIL ratings; 13 SOTIF triggering conditions linked to test cases |

The team agreed on the steering authority limits for LKA (a_y ≤ 3.0 m/s², added a_y ≤ 1.5 m/s²) and ELK (a_y ≤ 4.0 m/s², added a_y ≤ 3.0 m/s², jerk ≤ 10 m/s³) because the regulations do not specify numerical values.

## 5. Verification {#summary-verification}

- **Requirements:** 94 pass/fail requirements (53 Safety, 22 Functional, 11 Interface, 8 Regulatory); 12 performance targets are measured and ranked. Traceability is automated with `tools/trace.py`.
- **Calibration:** More than 70 calibration parameters, each with an initial value, a sweep range, and limits derived from requirements.
- **Simulator:** Deterministic Python and numpy simulation with a 1 ms step; models latency, jitter, message loss, clock skew, and CAN with counters and CRC. No logs from real vehicles.
- **Tests:** 24 scenarios × 3–5 variants, 21 types of injected faults, 3 latency sweeps, open-loop and closed-loop testing, and the assignment's minimum 3 × 5 test set.
- **Flexibility:** The same build and calibration run on 6 vehicle profiles: VinFast VF 3, VF 6, VF 8, VF 9, a reference vehicle, and a synthetic 2.5 m-wide vehicle.
- **Fairness:** The test system observes the planner only through its interfaces. Select the calibration on the tuning set and score it on the test set.

## 6. Safety {#summary-safety}

| Safety goal | Proposed ASIL |
|---|---|
| SG-01 No lateral intervention beyond what the driver can control | C (due to ELK); B for HWA and LKA |
| SG-02 No sudden loss of assistance | B |
| SG-03 Sufficient ELK intervention | A |
| SG-04 No step changes in steering commands | A |
| SG-05 Do not oppose the driver | A |

## 7. Document set {#summary-requests}

| Document | Contents |
|---|---|
| [Software Requirements Specification](report.html?doc=path-planner-software-requirements-specification&lang=en) | Requirements, performance targets, ODD, assumptions, and calibration limits |
| [Software Architectural Design](report.html?doc=path-planner-software-architectural-design&lang=en) | Architecture, cycle sequence, design, and calibration parameters |
| [Architecture Decision Records](report.html?doc=path-planner-architecture-decision-records&lang=en) | 12 decisions, each with rejected alternatives |
| [Software Detailed Design](report.html?doc=path-planner-software-detailed-design&lang=en) | Algorithms T1 through T11 and code structure |
| [Interface Control Document](report.html?doc=path-planner-interface-control-document&lang=en) | 11 messages, fields, rates, and timeouts |
| [ADAS Function Specification](report.html?doc=adas-function-specification&lang=en) | When HWA, LKA, and ELK may intervene |
| [Hazard Analysis and Risk Assessment (HARA)](report.html?doc=path-planner-hazard-analysis-and-risk-assessment&lang=en) | Hazards, proposed ASIL ratings, safety goals, and SOTIF |
| [Software Qualification Test Specification](report.html?doc=path-planner-software-qualification-test-specification&lang=en) | Simulator, test cases, criteria, and flexibility |

## Revision history {#revision-history}

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-11-10 | Rewritten as the Technical Summary for the BL1 technical document set |
| 1.1 | 2026-11-11 | Updated the center offset to follow the revised PP-ADR-008 |

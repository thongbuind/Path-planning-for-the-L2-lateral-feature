# Path Planner Benchmark and Evaluation

This report defines **the simulation environment and evaluation of the G1 path planner**. It specifies scenarios, injected faults, metrics, pass thresholds and how to compare techniques. The assignment calls for comparisons of smoothness, limit violations, lane encroachment, response to injected faults and computation time per cycle.

**Relationship to the other two reports**

| Report | Relationship to this report |
|---|---|
| Path Planner Feature Design | Supplies **requirements to satisfy**, including a_y and jerk budgets, continuity thresholds, completion conditions and responses to input faults. Benchmark evaluation uses observable requirements. Planner internals are outside the evaluation criteria. Section 5 gives a metric for each requirement |
| ADAS Functions | Defines **when to activate**. The benchmark uses the ADAS stub in mode B (scenario ground truth) to score G1 and mode A (noisy messages) to test the full chain. It also measures the metrics needed to select TLC thresholds |

## 0. Fair comparison and functional tests

**Functional tests and the benchmark answer different questions.**

| | Functional tests | Benchmark and Evaluation |
|---|---|---|
| Question | Does a planner version pass each requirement? | How do techniques compare under the same conditions? |
| When to run | Throughout development, on each code change | Once alternatives are available and when finalizing report results |
| Who uses the results | Developers fixing defects | Technique decision makers, mentors and report readers |
| Changes after seeing results | Fix code when a test fails | Freeze scenarios and thresholds once results are seen |

**Fair comparison rules**

| Rule | Details | Status |
|---|---|---|
| Define in advance | Finalize scenarios, seeds, metrics, pass thresholds and ranking order **before** running any technique. Record the reason for a change and rerun all techniques | proposed |
| Use the same conditions | All techniques use the same scenarios, seeds, test controller and ACC stub with fixed parameters, and the same ADAS stub in mode B | agreed |
| Tune fairly | Give each technique the same tuning effort and access to the **tuning scenario set**. Score on the **held-out scenario set**, which has different seeds and some scenarios excluded from tuning. This limits overfitting to the scoring set | proposed |
| Report all results | Report every scenario and seed, including the worst case | proposed |
| Make results reproducible | Record the code version, scenario file and seed with each result. Reruns must reproduce the values | agreed |
| Design for general behavior | Add new scenarios and faults on the evaluation side only. The planner shall not have a branch that exists solely to pass one scenario. When a case fails, fix the general mechanism and rerun the full set | agreed |
| Evaluate independently | Develop benchmark and planner independently as requirements-based black-box testing. Observe the planner only through its inputs, outputs and computation time. Keep planner internals, internal thresholds and configuration outside evaluation. Derive observable pass criteria from the assignment, regulations and driver expectations. Evaluation sets simulator and fault levels from real data or references. The planner shall not read scenario names, ground truth, seeds or benchmark configuration | agreed |
| Prioritize users and safety | Select metrics and rank first by safety (no collision, lane departure or wrong-way intervention), then compliance, then driver experience (smoothness, stability, avoidance of unwanted intervention, predictability and yielding to override), then performance. Measure true vehicle motion against the true lane in the simulator | proposed |

## 1. Minimum assignment set

The prototype must run at least the set below before any extensions.

| Scenario | Fault-free | Noise | c0 jump | One marking lost | Incorrect c2 |
|---|---|---|---|---|---|
| HWA tracks a curve | yes | yes | yes | yes | yes |
| LKA lane drift | yes | yes | yes | yes | yes |
| ELK with an oncoming vehicle | yes | yes | yes | yes | yes |

The set has 3 scenarios and 5 fault conditions. Each cell produces the paths for each technique and accompanying plots.

## 2. How to run {#benchmark-run}

See [Simulation Environment Design](report.html?doc=benchmark-evaluation&lang=vi#simulation-design) for shared module configuration.

| Item | Rule | Status |
|---|---|---|
| Scoring mode | Run deterministically in one process at 1 ms steps, as fast as the simulation clock allows. The same seed gives the same result. Use this mode for official metrics | agreed |
| Real-time mode | Run each ECU in its own process on the wall clock with real sockets. The virtual CAN bus uses `python-can` with `udp_multicast`, which runs on macOS. Use this nondeterministic mode only for integration checks | agreed |
| Open loop | The planner receives scenario data and the vehicle follows the prescribed scenario trajectory. Measure path quality alone | agreed |
| Closed loop | The path goes through the test controller and EPS to the vehicle model. Use a fixed controller across techniques so it does not mask planner errors | agreed |
| Measure smoothness on the path | Use planner output for smoothness metrics in both modes. Closed loop adds true vehicle motion metrics | agreed |
| ADAS stub | Score G1 in mode B and report full-chain robustness in mode A. Log measured and true TLC | agreed |
| Noise-free scenario | Provide a noise-free baseline for each scenario to separate algorithm errors from noise effects | agreed |
| Default IMU | Use clean IMU signals for the main scenario because IMU input to the planner is treated as filtered. Inject IMU noise and bias as faults (Section 4) | mentor |
| Rates | Run the planner and ADAS stub at 40 Hz. Follow the vehicle signal list (IMU and steering angle at 100 Hz, speed at 50 Hz) | mentor |
| Seed | One main seed per run generates separate random streams for each channel and sensor. Use 10 seeds for each noisy cell | agreed |
| Log | One MCAP file per run records all messages with stamps and counters for replay. View in Foxglove | agreed |
| Machine resources | On the 8 GB RAM machine, run small batches and ask before large batches | agreed |

### 2.1 Real log replay (open loop)

The assignment requires the planner to run on actual outputs, including real sensor artifacts. If the mentor supplies vehicle logs, add log replay to the benchmark. This is **for reference only** because the logs have limited ground truth (gt). It does not affect the main ranking.

| Item | Details | Status |
|---|---|---|
| Data | Ego vehicle signals are always available (Motion signal list). The gt column has limited data and serves as reference only | mentor |
| Replay mode | In open loop, the planner reads the log and the vehicle follows the recorded motion. Closed-loop replay is unavailable because the logged vehicle cannot be controlled | proposed |
| Additional inputs | Logs must include camera outputs (lane model and objects). The current signal list covers Motion. Ask the mentor whether logs include camera outputs | to be agreed |

**Metrics with limited ground truth**

| Metric | Requires gt | Method | Status |
|---|---|---|---|
| Smoothness, a_y and jerk limits, continuity thresholds and computation time | No | Follow Sections 5.2, 5.3, 5.4 and 5.7, measuring the path | proposed |
| Path oscillation under real noise | No | Compare jerk and suggested steering wheel rate from the real log against the same metrics in a similar simulation scenario | proposed |
| Delay compensation self-consistency | No | Transform the previous frame's lane model to the next frame time using ego motion and compare it with the next measured lane model. A large difference suggests incorrect compensation or actual delay outside the assumption | proposed |
| v_lat and TLC | Yes, “Ego lateral speed relative to the line” column | Compare v_lat computed from inputs with gt v_lat | proposed |
| Filtered yaw rate delay | Partly | Cross-correlate raw and filtered signals. Use gt “Ego yaw rate” as a second check (Path Planner Feature Design, Section 3) | proposed |
| Ego motion | Yes, gt position and yaw | Measure Δx, Δy and Δψ error over 0.5 s to check the T_coast assumption | proposed |
| Other vehicle cases | Yes, Target column | Lateral clearance and TTC to the other vehicle for object-triggered ELK | proposed |

**Unavailable metrics.** Lane encroachment (DTLE) and deviation from true lane center require ground-truth lane geometry. All closed-loop metrics require a controllable vehicle. The steering robot column and a target vehicle suggest the log may come from a proving ground. If confirmed, prioritize segments corresponding to S4–S8.

## 3. Scenario catalog {#benchmark-scenarios}

Each scenario has a configuration file and a seed. See [vehicle model](report.html?doc=benchmark-evaluation&lang=vi#sim-vehicle) for how to generate lane drift.

Use Euro NCAP LSS v4.3 parameters where possible. The test vehicle travels at 72 km/h and starts drifting on an arc of R = 1200 m, then holds v_lat constant. Use v_lat 0.2–0.6 m/s in 0.1 m/s steps. Add 90 km/h to match the examples in the reports, given Vietnam's maximum highway speed of 120 km/h.

**Each scenario type has 3–5 variants** to show the planner's response as one parameter changes. Variants range from easy to difficult and include at least one at a rule boundary. For two-sided scenarios, run every variant on both left and right. Default lane width is 3.5 m.

`python3 tools/trace.py --write` generates the Requirements column in the source from the Verification column in Path Planner Software Requirements. It is machine-generated. Requirements applying to all scenarios or faults are listed once outside these rows.

| # | Scenario | Variants | What to measure | Requirements | Status |
|---|---|---|---|---|---|
| S1 | HWA tracks a curve | 90 km/h, clothoid entry. a) R = 1000 m (curve a_y about 0.6 m/s²). b) R = 500 m (1.25). c) R = 250 m (2.5, at aysmax). d) S-curve with R = 500 m then reversed direction. e) 130 km/h, R = 1000 m (1.3) | Lane centering, smoothness and a_y limit | PP-SWR-001, 003, 004, 008 (a, b, d, e), 050 (a, b, d, e), 051 (closed loop) | assignment |
| S1b | HWA on a curve beyond aysmax | a) 90 km/h, R = 200 m (a_y about 3.1 m/s²). b) 90 km/h, R = 150 m (4.2). c) 110 km/h, R = 300 m (3.1). d) R = 200 m just after a crest with only 40 m camera view | Path stays within aysmax, lateral_limit_reached is set and steering assistance continues without abrupt release | PP-SWR-001, 005, 006, 007 | proposed |
| S2 | HWA enabled with vehicle off center | a) 0.2 m offset, 0° heading error. b) 0.4 m, 1°. c) 0.5 m, 2° outward. d) 0.4 m on a curve with R = 500 m. e) 0.5 m at 130 km/h | Recentering segment with added a_y ≤ 0.5 m/s² and no step | PP-SWR-002, 052, 053 | proposed |
| S3 | HWA offsets while ego passes a truck in an adjacent lane | Truck is 2.5 m wide. a) 5 m/s slower. b) 2 m/s slower (longer alongside). c) 10 m/s slower. d) Truck stays 0.1 m from the marking. e) Truck encroaches 0.3 m into the ego lane | Start offset early based on TTC, stay at offset ≤ 0.3 m and return after passing | PP-SWR-002, 055, 058, 059 | assignment |
| S3b | HWA with a large vehicle overtaking from behind, an optional vehicle on the opposite side and narrow lanes | Truck approaches from behind at 5 m/s faster than ego. Only corner radar detects it before it is alongside. a) Opposite side clear, 3.5 m lane. b) Passenger car alongside on the opposite side. c) Truck on opposite side. d) As a, 3.0 m lane. e) As c, 2.75 m lane | Offset late but smoothly. Avoid steering toward the opposite vehicle. DLC ≥ 0.3 m on both sides | PP-SWR-055, 056, 057 | mentor |
| S4 | LKA drift on a straight road | a) 72 km/h, dashed line, v_lat 0.2 m/s. b) 72 km/h, solid line, 0.4. c) 90 km/h, 0.6. d) Crosswind drift. e) Road cross-slope drift | DTLE, smoothness and completion conditions | PP-SWR-032, 080, 081, 083, 084, 085, 086 (closed loop), 087 (closed loop), 090, 110, 112, 114 | assignment, Euro NCAP |
| S4b | LKA drift on a curve | 90 km/h. a) R = 1000 m, outward drift at 0.3 m/s. b) R = 500 m, outward 0.3. c) R = 500 m, inward 0.3. d) R = 250 m, outward 0.3. Curve a_y already uses 2.5 m/s² of the total LKA budget of 3.0, leaving 0.5 m/s² to correct. e) Outward drift on clothoid entry | DTLE, total a_y within budget, lateral_limit_reached when the budget is exhausted, and outward versus inward drift | PP-SWR-083, 085, 110, 112, 114 | mentor |
| S5 | Solid-line ELK with LKA off | a) 72 km/h, v_lat 0.2. b) 0.4. c) 0.6. d) 90 km/h, 0.4. e) Double marking | DTLE ≥ −0.3 m | PP-SWR-032, 080, 082, 083, 085, 086 (closed loop), 090, 111, 113, 115 | Euro NCAP |
| S6 | Road-edge ELK | Passenger side. a) Road edge only, v_lat 0.2. b) Road edge only, 0.6. c) Dashed center marking and no edge marking. d) Barrier at the road edge. e) 90 km/h, 0.4 | DTLE ≥ −0.1 m | PP-SWR-080, 082, 083, 085, 086 (closed loop), 111, 113, 115 | Euro NCAP |
| S6b | Lane widening | A road edge or marking widens with HWA enabled. a) Right emergency shoulder widens 1.5 m over 100 m. b) Exit splits and right marking follows it. c) Lane added on left. d) Widening on a curve with R = 500 m. e) Widening while HWA offsets for a truck on the opposite side | Path does not shift toward the widened side. Lateral deviation from true lane center ≤ 0.1 m | PP-SWR-060 | mentor |
| S7 | Oncoming-vehicle ELK | Other vehicle is in adjacent lane, 1.5 m from the inner edge of the center marking, on the driver side. Without intervention the vehicles meet with 10% width overlap. a) Both 72 km/h, v_lat 0.2. b) 0.4. c) 0.6. d) Other vehicle at 90 km/h. e) On a curve with R = 500 m | No collision | PP-SWR-082, 083, 085, 088 (closed loop), 111, 113, 115 | assignment, Euro NCAP |
| S8 | Overtaking-vehicle ELK | a) Other vehicle at 80 km/h and ego at 72 km/h, unintentional drift at 0.2 m/s. b) Both at 72 km/h, drift at 0.4. c) Signaled lane change (signal on 1.0 ± 0.5 s before steering) at 0.5 m/s. d) As c, 0.7 m/s. e) Other vehicle at 100 km/h, drift at 0.4 | No collision, including with the turn signal on | PP-SWR-082, 083, 085, 088 (closed loop), 089, 111, 113, 115 | Euro NCAP |
| S8b | Signaled lane change with different trailing gaps | Required trailing deceleration is (speed difference)² / (2 × distance). a) 20 m gap, 2.2 m/s faster, 0.12 m/s² needed. b) 10 m, 2.2 m/s, 0.24 m/s². c) 20 m, 8 m/s, 1.6 m/s², TTC 2.5 s. d) 12 m, 10 m/s, TTC 1.2 s. e) 30 m, 14 m/s, 3.3 m/s² needed, TTC 2.1 s | a, b and c shall **warn only**. d (TTC ≤ 1.5 s) and e (more than 3 m/s² needed) shall intervene under ADAS Functions, Section 3.2, step 6 | PP-SWR-082 (d, e), 083 (d, e), 085 (d, e), 111 (d, e), 113 (d, e), 115 (d, e) | proposed |
| S8c | Sharp evasive steering with an occupied adjacent lane | Turn signal off. a) v_lat 1.2 m/s. b) 1.5 m/s. c) Steer sharply and immediately unwind (pothole avoidance). d) Steer sharply during LKA intervention | Warn only. Ramp down an intervention already in progress | PP-SWR-031 (d), 036 (d), 037 (d) | proposed |
| S9 | Feature transitions | a) LKA to ELK mid-intervention. b) ELK completes and returns to HWA. c) Driver overrides and releases HWA. d) Turn signal cancels the request mid-intervention. e) Driver disables HWA mid-curve at R = 500 m | No step at any transition | PP-SWR-030 (a), 031, 033 (b), 036 (d), 037 (d), 038, 039 (c), 040 (c) | assignment |
| S10 | Driving near a marking without drift | a) DLC 0.2 m, v_lat near zero. b) DLC 0.4 m. c) Cut a curve at R = 500 m. d) Driver stays off center beside a truck. e) As a at night, ADAS stub in mode A | **No intervention allowed.** Count false activations to select a TLC threshold | | proposed |
| S11 | Highway congestion | HWA enabled. a) Stop-and-go at 0–30 km/h. b) 0–60 km/h. c) Stop for 10 s and resume. d) Another vehicle cuts in at 20 km/h | HWA maintains the lane. LKA and ELK are unavailable | PP-SWR-050, 054 | proposed |
| S12 | Rain | Vehicle model uses μ = 0.5, night or rain camera noise and 1.5 times perception noise. a) Rerun S1c. b) S4c. c) S7c. d) S4b-d | Safety margin with reduced grip | PP-SWR-001 (a) | agreed |
| S13 | Slow EPS | Rerun S4c and S5c with EPS delay a) 75 ms, b) 100 ms, c) 150 ms in place of 50 ms | Planner robustness to slower actuation | PP-SWR-091 (a, b, closed loop) | agreed |
| S14 | Lateral and longitudinal constraint exchange | Two runs, with the ACC stub reading LateralLimits (main design) and ignoring it (comparison). a) Tight curve S1b-a. b) Other vehicle encroaches 0.5 m into ego lane. c) Both together. d) Lose LongitudinalPlan mid-curve | Compare both using minimum DLC, clearance to the other vehicle, a_y and deceleration, with no prior ranking | PP-SWR-009, 150, 151, 152, 153, 154 (d), 155 (d) | agreed |
| S15 | Center offset with objects on both sides | a) Trucks on both sides. b) Truck and opposite barrier. c) Truck and opposite passenger car. d) Trucks on both sides in a 3.0 m lane. e) Barriers on both sides (work zone) | Avoid shifting toward the closer object. Keep DLC ≥ 0.3 m on both sides and log minimum lateral clearance to objects on each side | PP-SWR-055, 056, 057 | proposed |
| S16 | Repeated interventions | The ADAS stub sends a prescribed FunctionRequests sequence. a) LKA reports COMPLETED and ADAS holds REQUEST for 1 s longer. b) As a, then REQUEST is absent for 0.2 s and returns when the vehicle drifts again. c) Drift back and forth three times, v_lat 0.4 m/s, 2 s apart. d) As c with solid-line ELK. e) Second intervention starts 0.2 s after COMPLETED | a) Suppress repeat intervention while REQUEST is held. b–e) Each intervention meets the same DTLE, a_y, jerk and duration limits as the first | PP-SWR-034 (a, b), 035 (c, d, e) | proposed |
| S17 | Driver changes lanes with HWA enabled | The driver signals, overrides HWA and moves into the adjacent lane. Lane Model switches lanes when the vehicle crosses the marking and sets the lane change flag. a) Straight road at 90 km/h, change in 4 s. b) Quick change in 2.5 s. c) Curve with R = 500 m. d) Two consecutive lane changes. e) Lane change flag arrives one frame after Lane Model switches lanes | Path continuity every cycle around the lane switch. During override the path follows vehicle position. After release HWA returns to the new lane center | PP-SWR-039, 040, 061 | proposed |

Narrow widths of 3.0 m and 2.75 m are design values. Check them against Vietnamese road standards (Section 8).

## 4. Fault injection catalog {#benchmark-faults}

Inject each fault at three times. During steady HWA, at LKA or ELK activation, and during an intervention. Each fault has 3–5 levels or variants.

Keep fault IDs stable and unique. `python3 tools/trace.py --write` generates the Requirements column in the source from the Verification column in Path Planner Software Requirements. It is machine-generated. Requirements applying to all scenarios or faults are listed once outside these rows.

| ID | Group | Fault | Level or variant | Expected response | Requirements | Status |
|---|---|---|---|---|---|---|
| F01 | Lane model | c0 and c1 noise | a) Daylight σ_c0 = 0.03 m, σ_c1 = 0.002. b) 1.5 times daylight. c) Night or rain, 2.5 times daylight | Path remains stable with jerk within limits | PP-SWR-120 | agreed |
| F02 |   | c0 jump | a) 0.3 m. b) 0.6 m. c) 1.0 m in one frame. d) Jump then return after one frame. e) Jump and stay. Lane Model supplies no jump flag | Avoid steps by meeting continuity thresholds. Limit the path's lateral shift rate | PP-SWR-121 | assignment |
| F03 |   | Misidentified adjacent marking | a) Left marking jumps to L2 for one frame, width 3.5 → 7 m. b) As a for 0.5 s. c) Both markings jump to the adjacent lane and lane center shifts 3.5 m with no lane change flag. d) Misidentify an old marking or crack offset 0.5 m for 2 s. e) As a during ELK | Keep path lateral deviation from true lane center ≤ 0.1 m. Suppress activation and cancellation based on the false marking | PP-SWR-122 | mentor |
| F04 |   | One marking lost | a) Left. b) Right. c) Confidence decays to 0 over 2 s before loss. d) Immediate loss. e) Loss while lane width changes | Keep tracking true lane center. Log lateral deviation from true lane center and relative to the fault-free case. Meet continuity thresholds | PP-SWR-123 (a–d) | assignment, mentor |
| F05 |   | Both markings lost | a) Predict for 0.5 s then lose. b) Predict for 1 s then lose. c) Lose for 0.5 s then recover. d) Lose mid-curve at R = 500 m | Set path_valid = false at T_coast = 1 s after loss. Log lateral deviation from true lane center before that time | PP-SWR-124 | agreed |
| F06 |   | Incorrect curvature estimate | a) c2 +0.0005 1/m on a straight road. b) −0.0005 1/m on a curve. c) Correct c2 with incorrect c3. d) Error persists for 2 s. e) Error on curve entry | Avoid following the false curve. Log lateral deviation from true lane center 2–3 s ahead | PP-SWR-125 | assignment, mentor |
| F07 | IMU | Noise | Main scenarios use clean IMU. a) Yaw rate σ = 0.07 °/s, a_y σ = 0.004 m/s². b) σ = 0.14 °/s and 0.008 m/s² ([Sensor Models](report.html?doc=benchmark-evaluation&lang=vi#sim-sensors), from the Bosch SMI230 datasheet) | Keep jerk within limits and log lateral deviation relative to the fault-free case | PP-SWR-135 (a, b) | mentor |
| F08 |   | Yaw rate bias | a) 0.1 °/s. b) 0.3 °/s. c) 1 °/s, uncompensated raw sensor offset and worst case | Log lateral deviation from true lane center and relative to the fault-free case. For c, also measure lateral deviation after 1 s and 2 s without markings | PP-SWR-136 (a, b) | mentor |
| F09 | Timing | Delay | Sweep in Section 4.1 | Lateral deviation from true lane center at each delay |   | mentor |
| F10 |   | Jitter and message loss | a) Single loss. b) Burst of 2 messages. c) Burst of 5 messages. d) ±20 ms jitter | Keep the path smooth by meeting continuity and jerk limits | PP-SWR-126 | agreed |
| F11 |   | Late or out-of-order message | Message arrives after a newer message | Keep the path independent of stale data. Meet continuity thresholds and log deviation from the fault-free case | PP-SWR-127 | agreed |
| F12 |   | Transmission stops | Stop each input in turn until its timeout expires | Match the required path_valid, active_function and HWA offset in the invalid-input table (Path Planner Software Requirements, Section 8.3) | PP-SWR-124 (Lane Model), 140 (Perception, in S3), 141 (Perception, in S5), 142 (IMU, speed, steering angle), 144 (v_y), 145 (FunctionRequests) | agreed |
| F13 |   | Camera slower than planner | 20 Hz versus 40 Hz, always present | Meet continuity thresholds every planner cycle, with no step pattern at the camera rate | PP-SWR-128 | agreed |
| F14 |   | Clock synchronization loss | a) ±20 ppm drift. b) ±100 ppm. c) gPTP synchronization lost for 10 s | Log lateral deviation from true lane center and relative to synchronized clocks. Incorrect stamps should add no path deviation | PP-SWR-137 (a, b, c) | agreed |
| F15 | Integrity | Counter repeat, skip or stall | On each channel | With a duplicate message, match the fault-free path. With a skipped or stalled counter, match the corresponding message-loss case | PP-SWR-129 (repeat), 130 (skip, stall) | agreed |
| F16 |   | Invalid flag or fault qualifier | valid = false, qualifier FAULT | Match the corresponding message-loss case | PP-SWR-130 | agreed |
| F17 |   | Incorrect CRC | CAN frame | Match the corresponding frame-loss case | PP-SWR-130, 142 | agreed |
| F18 |   | CAN quantization | By DBC scale, always present | No significant effect | PP-SWR-139 | agreed |
| F19 | Timing | Future timestamp | a) Lane model stamp 5 ms ahead of the planner clock. b) 15 ms. c) 50 ms. d) One frame only, 50 ms ahead. e) ObjectList stamp 15 ms ahead | a) Keep using the input. b, c and e) Treat the corresponding input as invalid. d) Treat as a single dropped frame | PP-SWR-132 | proposed |
| F20 | Ego-motion | Invalid result | a) One failed query. b) Continuous failures. c) Failure every other cycle. d) As b during LKA intervention | Set path_valid = false within one cycle of the failed query | PP-SWR-143 | proposed |

**Add cases on the evaluation side only.** New cases such as misidentified markings, lane widening and c0 jumps without a Lane Model flag test the planner's general behavior. The planner must handle these cases without scenario-specific branches. The benchmark scores only observable outputs through the interface and is independent of the implementation.

### 4.1 Delay sweeps

Actual delay is unknown according to the mentor. Sweep multiple values to see how performance degrades as delay increases. Change only the actual delay in the simulator. Use the same planner configuration at every level and in every run.

Keep fault IDs stable and unique. `python3 tools/trace.py --write` generates the Requirements column in the source from the Verification column in Path Planner Software Requirements. It is machine-generated. Requirements applying to all scenarios or faults are listed once outside these rows.

| ID | Sweep | Levels | What to measure | Requirements | Status |
|---|---|---|---|---|---|
| Q1 | Camera delay (lane model and objects) | 0 / 50 / 100 / 150 / 200 / 300 ms, each with ±20 ms jitter. The 300 ms case exceeds plausible camera delay and checks how the planner responds to stale data | Path lateral deviation from true lane center at 0, 25 and 50 m on a straight road and on a curve with R = 250 m. For every delay, the path must stay inside the lane or path_valid = false | PP-SWR-012, 013, 131 (300 ms), 133 (200 ms) | proposed |
| Q2 | Filtered yaw rate delay | 0 / 25 / 50 / 100 ms | Path lateral deviation from true lane center on a straight road and on clothoid entry. Compare with camera delay effects | PP-SWR-138 (0–50 ms) | proposed |
| Q3 | Delay from ADAS Functions to planner | 20 / 40 / 60 ms | Start of the intervention path relative to the ADAS Functions decision, and DTLE in S4c and S5c | PP-SWR-038 | proposed |

Plot metrics against delay, with one curve per technique. A flatter curve indicates better delay tolerance.

### 4.2 Combined faults

The full cross-product of scenario × variant × fault × level × timing × open and closed loop × seed is too large. Proposed coverage follows.

1. Run each scenario and variant with **one fault at a time**, at all three timings, in open and closed loop. For faults with multiple levels, run every level on the hardest scenario variant and the middle level on the others.
2. Add several **realistic worst-case combinations** such as rain at night, with 2.5 times noise, μ = 0.5, one marking lost and 150 ms delay.
3. On the 8 GB RAM machine, run small batches with one scenario per batch and ask before running large batches.

### 4.3 IDs outside planner requirement traceability {#benchmark-trace-exempt}

Every scenario, fault and sweep must verify at least one planner requirement. List exceptions here with a reason. `tools/trace.py` suppresses missing-trace warnings for these IDs and warns if a requirement references one.

| ID | Reason |
|---|---|
| S10 | Tests ADAS Functions for unwanted activation while driving near a marking without drift. Used to select TLC thresholds (Section 5.6). ADAS Functions requirements do not yet have IDs |
| F09 | Summary row for the delay sweep. Q1, Q2 and Q3 contain details and traceability (Section 4.1) |

## 5. Metrics and pass thresholds

### 5.1 Safety and encroachment

| Metric | Measurement | Pass threshold | Basis | Status |
|---|---|---|---|---|
| Minimum DTLE | Minimum distance from the outer tire edge to the inner marking edge during an intervention | LKA ≥ −0.3 m, solid-line ELK ≥ −0.3 m and road-edge ELK ≥ −0.1 m | Euro NCAP Assessment 4.3.2 and 4.3.3.3, EU 2021/646 3.6.2 | agreed |
| Design target for DTLE | Same as above | LKA ≥ 0 (clear of the marking) in mode B in daylight | Tighter than the regulatory threshold to leave noise margin | proposed |
| Collision with an adjacent vehicle | Minimum lateral clearance between the vehicles | No contact and clearance ≥ 0.3 m | Euro NCAP 4.3.3.4 and LSS 7.4.7 | agreed |
| Opposite-side overshoot | Minimum DLC on the opposite side after intervention | ≥ 0.3 m to avoid overshooting toward the opposite side | Assignment wording “no overshoot into the other lane” | proposed |
| HWA keeps clear of markings | Minimum DLC while a_y is below aysmax | ≥ 0 | R79 5.6.2.1.1 | agreed |

### 5.2 Limits

| Metric | Measurement | Pass threshold | Status |
|---|---|---|---|
| a_y budget violations | Measure total and added a_y on the path by controlling feature | Stay within total limits of HWA 2.5 / LKA 3.0 / ELK 4.0 m/s² and added limits of HWA 0.5 / LKA 1.5 / ELK 3.0 m/s². HWA may exceed aysmax under R79 (0.3 m/s², or 40% for up to 2 s) | agreed |
| Jerk violations | 0.5 s moving average of lateral jerk | HWA and LKA ≤ 5 m/s³, ELK ≤ 10 m/s³ | agreed |
| Steering angle and rate | Suggested front wheel angle on the path. Also measure at EPS in closed loop | Front wheel angle ≤ 0.61 rad and steering wheel rate ≤ 6 rad/s | agreed |
| Intervention duration | From REQUEST to COMPLETED | ≤ 10 s | agreed |
| Logging | Count violations and log maximum exceedance and duration for each | — | assignment |

### 5.3 Smoothness and comfort

| Metric | Measurement | Threshold or use | Status |
|---|---|---|---|
| Peak and RMS lateral jerk | On planner path by feature | Compare techniques. HWA target ≤ 2.5 m/s³ | assignment |
| Peak and RMS a_y | On the path | Compare techniques | assignment |
| RMS steering wheel rate | Closed loop | Compare steering oscillation under noise | proposed |
| Handover smoothness | Added a_y at COMPLETED | ≤ 0.2 m/s² | proposed |

### 5.4 Continuity between paths

| Metric | Measurement | Pass threshold | Status |
|---|---|---|---|
| Lateral, heading and curvature difference between consecutive paths | Over the shared interval after transforming the previous path into the new base_link | ≤ 0.05 m, ≤ 0.005 rad and ≤ 0.0003 1/m each cycle, including feature changes and c0 jumps | agreed |
| Logging | Fraction of cycles that pass, maximum values and violating cycles | — | agreed |

### 5.5 Fault response

| Metric | Measurement | Pass threshold | Status |
|---|---|---|---|
| Time to report an invalid path | From Lane Model reporting loss of both markings to path_valid = false | T_coast = 1 s with at most one cycle (25 ms) of timing error | agreed |
| Response to input timeout | From timeout expiry to the behavior in the invalid-input table | Within one cycle | agreed |
| c0 jump | Maximum lateral difference between consecutive paths around the jump frame and center shift rate | Meet continuity thresholds | agreed |
| Misidentified marking | Maximum lateral deviation from true lane center during the fault and frames from fault onset to deviation falling below 0.1 m | Deviation ≤ 0.1 m, continuity thresholds met and no activation or cancellation due to the wrong marking | proposed |
| Lane widening (S6b) | Lateral deviation from the path to true lane center | Deviation ≤ 0.1 m, with no shift toward the widened side | proposed |
| Delay sweep (Section 4.1) | Metrics at each delay | Report a degradation curve for each technique | proposed |
| Incorrect c2 | Deviation from true lane center 2–3 s ahead | Compare techniques | assignment |
| Comparison with noise-free baseline | Compare each metric in a faulted cell with the fault-free cell for the same scenario | Report degradation | agreed |

### 5.6 Activation metrics for selecting TLC thresholds

| Metric | Measurement | Use | Status |
|---|---|---|---|
| Unwanted activation | Number of LKA or ELK activations in S10 | Ensure the TLC threshold does not trigger too early. Target 0 | proposed |
| Activation timing difference | Mode A versus mode B, same seed | Measure how camera noise affects activation timing | proposed |
| DTLE by TLC threshold | Run S4 through S8 with **three LKA thresholds of 0.6 / 1.0 / 1.5 s** | Ensure the TLC threshold does not trigger too late | agreed |
| Comparison of three candidates | Compare encroachment (S4–S8) and unwanted activation count (S10) for each candidate | Select the LKA threshold after collecting data | agreed |

### 5.7 Computation time

| Metric | Measurement | Threshold | Status |
|---|---|---|---|
| Computation time per cycle | Measure on the host clock, independently of simulation time. Report mean, p95, p99 and maximum | Report each technique. Proposed p99 ≤ 5 ms on the development machine to leave margin within the 25 ms cycle | to be agreed |
| Note | Python on a laptop is slower and more variable than C on an ECU. These measurements **compare techniques**. ECU performance requires its own measurements | — | proposed |

### 5.8 Path tracking (closed loop only)

| Metric | Measurement | Use | Status |
|---|---|---|---|
| Lateral and heading tracking error | Closed loop | Check whether the test controller masks planner errors. Exclude from the planner score | proposed |

## 6. Technique comparison

| Rule | Details | Status |
|---|---|---|
| Same conditions | Use the same scenarios, seeds and fixed test controller parameters for every technique | agreed |
| Ranking order | 1. Pass all safety thresholds (5.1). 2. Stay within limits (5.2) and meet continuity thresholds (5.4). 3. Fault response (5.5). 4. Smoothness (5.3). 5. Computation time (5.7). Reject a technique that fails step 1 or 2 even if it is smoother | proposed |
| Candidates | See Path Planner Implementation (Pending) for time-parameterized quintic or clothoid, Frenet sampling (Werling 2010) and QP or MPC. Add a 7th-order polynomial variant if zero final jerk is required | assignment |
| Report results | Provide a comparison table and at least one rejected technique with a quantitative reason | assignment |

## 7. Reporting results

| Format | Contents |
|---|---|
| Summary table | One row per technique. Columns give Section 5 metrics, pass/fail and worst value across seeds |
| Time series | Path and vehicle d(t) with both lane boundaries, a_y, jerk, controlling feature, feature transitions and injection time |
| Continuity plot | Lateral, heading and curvature differences between consecutive paths each cycle, with threshold lines |
| Plot by v_lat | Minimum DTLE versus v_lat for S4–S8 in the Euro NCAP presentation format |
| Computation time distribution | Histogram with p95 and p99 |

## 8. Open decisions

1. **Fair comparison rules** (Section 0). Predefine settings and keep tuning and held-out scenario sets separate.
2. **Test speeds.** 72 km/h under Euro NCAP, with 90 km/h added.
3. **Opposite-side overshoot definition.** Opposite DLC ≥ 0.3 m.
4. **S10** (driving near a marking without drift) and the target of 0 unwanted activations.
5. **Computation time threshold.** p99 ≤ 5 ms on the development machine.
6. **Combined worst cases** (Section 4).
7. **Technique ranking order** (Section 6).
8. **LKA target DTLE ≥ 0**, tighter than Euro NCAP.
9. **Scenarios S8b, S8c and S15**.
10. **Scenario variants and fault levels** (Sections 3 and 4).
11. **Narrow lane widths** of 3.0 m and 2.75 m. Check against Vietnamese road standards.
12. **Deviation threshold of 0.1 m** for misidentified markings and lane widening.
13. **Delay sweep levels** (Section 4.1).
14. **Real logs.** Ask whether the mentor can supply them and whether they contain camera data (Section 2.1).
15. **Source for lane model fault levels** (Section 4). σ_c0, σ_c1, c0 jump and c2 error currently match planner assumptions and lack measured sources. Use a source independent of the planner, such as real logs or lane camera error documentation.
16. **Pass thresholds for rows that log deviation only** (Section 4). One marking lost, both markings lost before T_coast expires, incorrect c2, IMU noise, yaw rate bias, delay, late or out-of-order messages, and clock synchronization loss. Current measurements of lateral deviation relative to true lane center or the fault-free case compare techniques but are insufficient for pass/fail. Derive thresholds from user safety requirements, such as remaining tire-to-marking clearance, and cite the source.

## 9. Simulation environment design {#simulation-design}

The modules below are shared across G1 prototype runs. [How to run](report.html?doc=benchmark-evaluation&lang=vi#benchmark-run) defines run modes and logging. The [ACC stub](report.html?doc=path-planner-feature-design&lang=vi#acc-stub) design describes constraint exchange between the lateral and longitudinal modules.

### Scheduler {#sim-scheduler}

**Two-mode architecture**

| Item | Requirement | — | Status |
| --- | --- | --- | --- |
| Shared code | Components communicate only through their interfaces and are shared between modes. Only transport and scheduling change | — | agreed |
| Language | Plain Python plus numpy. ROS 2 is outside scope | — | agreed |
| Real-time pub/sub transport | UDP on localhost. Binary-encode each message according to its schema | — | agreed |

**Scheduling**

| Item | Requirement | — | Status |
| --- | --- | --- | --- |
| Time step | Fixed 1 ms. Integrate the vehicle model each step. Delay and jitter have 1 ms resolution. Include CAN frame transmission time in the delay | ms | agreed |
| Phase offset | Each module starts at a random phase offset within its period, generated from the seed | — | agreed |
| Order within a step | Integrate the vehicle model, sample sensors, deliver due messages and then run scheduled modules in fixed priority order | — | agreed |
| Channel | Delay = nominal delay + uniformly distributed jitter, with a probability of loss. The receiver keeps the latest message (last-is-best) and checks counter, CRC and qualifier on receipt | — | agreed |
| Fault injection | Attach faults to each channel as defined by the scenario. Support burst loss, extra delay, duplication, reordering, transmission stops, bad CRC and stalled counters | — | agreed |
| Planner computation time | Model as 5 ms of simulation time. Measure actual code computation time separately for the assignment metric | ms | agreed |
| Seed | Use `numpy.random.SeedSequence.spawn` to split streams from the main seed (Section 2) | — | agreed |

**Clocks**

| Item | Requirement | Unit | Status |
| --- | --- | --- | --- |
| Independent clocks | Each ECU has its own clock with drift up to ±100 ppm and an initial offset generated from the seed | ppm | agreed |
| Synchronization | Use gPTP-style correction every 125 ms with a small residual error after each correction | ms | agreed |
| stamp_us | Use the sending ECU clock. Stamp CAN frames on the receiving ECU clock | — | agreed |
| Injected fault | On synchronization loss, one ECU clock drifts relative to the others | — | agreed |
| Initial offset | Up to ±10 ms before initial synchronization | ms | agreed |
| Post-synchronization error | Up to ±50 µs | µs | agreed |
| Real-time mode | Processes on the same machine share the OS clock. Simulate separate ECU clocks on top of it | — | agreed |

### Virtual CAN bus {#sim-can}

**Requirements**

| Rule | Status |
| --- | --- |
| Chassis signals travel over virtual CAN using the [DBC frames](report.html?doc=g1-interfaces-and-signals&lang=vi#can). | agreed |
| Model actual effects, including quantization by scale, fixed periods, counter, CRC and timeout. | agreed |
| Support frame loss, bad CRC, repeated or skipped counters and transmission stops. | agreed |
| Use cantools to read DBC and encode and decode frames, and python-can for the virtual bus. | agreed |

### Vehicle model {#sim-vehicle}

**Model**

| Field | Requirement | Unit | Status |
| --- | --- | --- | --- |
| Type | Dynamic bicycle model with linear tires F = C·α. State is x, y, ψ, v_y and r | — | agreed |
| Grip limit | Lateral force per axle stays within μ·F_z. Use μ = 1.0 on dry roads and 0.5 on wet roads (rain scenario) | — | agreed |
| Low speed | Blend into the kinematic model over 3–5 m/s to avoid division by near-zero speed and maintain a continuous state | m/s | agreed |
| Longitudinal speed | The ACC stub acceleration command passes through a 0.1 s delay and a first-order element with τ = 0.3 s. Scenarios may prescribe speed when ACC is unnecessary | m/s | proposed |
| Input | Front wheel angle from the test EPS | rad | agreed |
| Source of lane drift | The simulated driver adds a small steering offset, or road cross-slope or crosswind adds a constant lateral force. Select per scenario | — | agreed |
| Integration | RK4 with the scheduler's 1 ms step | ms | agreed |

**Parameters**

Typical values for a midsize electric vehicle

| Parameter | Value | Unit | Status |
| --- | --- | --- | --- |
| Mass m | 2000 | kg | agreed |
| Moment of inertia I_z | 3500 | kg·m² | agreed |
| Wheelbase L | 2.9 | m | agreed |
| l_f, l_r | 1.45 and 1.45 | m | agreed |
| C_f, C_r (per axle) | 100 000 and 140 000 | N/rad | agreed |
| Vehicle width | 1.9 | m | agreed |
| Steering ratio | 15 | — | agreed |

**Plausibility checks**

| Quantity | Value | Unit | Status |
| --- | --- | --- | --- |
| Understeer gradient K | m/L · (l_r/C_f − l_f/C_r) ≈ 0.0029, about 1.6°/g | rad/(m/s²) | agreed |
| Characteristic speed | √(L/K) ≈ 32 m/s, about 115 km/h. Passenger cars are typically 70–110 km/h | m/s | agreed |
| I_z / (m · l_f · l_r) | ≈ 0.83. Passenger cars are typically 0.8–1.1 | — | agreed |

**Intentional omissions**

| Rule | Status |
| --- | --- |
| Omit cornering load transfer, suspension bounce, steering column compliance and road roughness. Their effects are small at HWA and LKA lateral accelerations. | agreed |

The values are typical for a midsize electric vehicle. Measurements for a specific vehicle are pending. The planner reads the same parameters through [VehicleConfig](report.html?doc=g1-interfaces-and-signals&lang=vi#vehicle-config).

### Sensor models {#sim-sensors}

**Requirements**

| Rule | Status |
| --- | --- |
| Lane model uses lane geometry within view, transforms it into base_link, fits a cubic polynomial to each marking and injects faults from the [fault injection catalog](report.html?doc=benchmark-evaluation&lang=vi#benchmark-faults). This replaces Lane Model in simulation. Evaluation sets fault levels from real data or references, independently of the planner's fault assumptions. | agreed |
| Read objects from the scenario, transform them into base_link and send them using the [ObjectList interface](report.html?doc=g1-interfaces-and-signals&lang=vi#perception). | agreed |
| Main scenarios use clean IMU values from the vehicle model, subject only to DBC quantization. Inject IMU noise and bias under Section 4. See the chassis signal table for datasheet-based levels. | mentor |
| Read speed and steering angle from the vehicle model. Add the noise and bias in the chassis signal table before CAN encoding and quantize using the DBC scale. | agreed |

**Chassis signals**

Each sample has white noise. Select fixed bias from the seed and hold it for the run.

| Signal | White noise σ and fixed bias | Unit | Status |
| --- | --- | --- | --- |
| Yaw rate, main scenario | Clean, with σ = 0 and bias = 0 | °/s | mentor |
| Yaw rate, injected fault | Noise σ = 0.07 or 0.14 (density 0.02 °/s/√Hz times √12 Hz or √50 Hz). Bias 0.1 / 0.3 / 1. The 1 °/s value is the uncompensated raw sensor offset at 25 °C and represents the worst case | °/s | proposed |
| a_x, a_y, main scenario | Clean, with σ = 0 and bias = 0. On a cross-sloped road, measured a_y includes the physical component g·sin(slope angle) | m/s² | mentor |
| a_x, a_y, injected fault | Noise σ = 0.004 or 0.008 (0.12 mg/√Hz times √12 Hz or √50 Hz). Bias up to 0.2 (20 mg offset at 25 °C) | m/s² | proposed |
| Speed v | σ = 0.02 m/s and scale error up to ±0.5% (tire radius) | m/s | agreed |
| Steering wheel angle | σ = 0.001 and zero offset up to ±0.01 (about 0.6°) | rad | agreed |

**Perception**

| Fault | Level | Unit | Status |
| --- | --- | --- | --- |
| Longitudinal position x | σ = 0.2 + 1% of range | m | agreed |
| Lateral position y | σ = 0.1 + 0.5% of range | m | agreed |
| Velocity vx, vy | σ = 0.3 and 0.2 | m/s | agreed |
| Size | σ = 0.1 for length and width | m | agreed |
| Missed detection | 2% of frames per object | — | agreed |
| Ghost object | Average 0.05 events per second, lasting about 0.2 s with low existence probability | 1/s | agreed |
| Rain | Multiply σ by 1.5 in the scenario with μ = 0.5 and increased camera noise | — | agreed |

**G2 and G4 stubs**

| Rule | Status |
| --- | --- |
| Vehicle State Estimation uses true v_y plus noise with σ = 0.05 m/s. Send σ² in the variance field. | agreed |
| Ego-motion integrates motion from the CAN signals without extra noise. Injected IMU noise or bias therefore produces ego-motion error through the normal integration process. | agreed |

Generate all noise and bias from the seeded random streams in Section 2.

IMU noise levels come from the Bosch SMI230 datasheet (automotive AEC-Q100 Grade 2 inertial sensor, 2018 product brief). Gyro noise density is 0.02 °/s/√Hz, with offset ±1 °/s at 25 °C and another ±1 °/s over temperature. Acceleration noise density is 0.12 mg/√Hz, with offset ±20 mg. These are raw sensor values and provide upper bounds because filtered vehicle signals are cleaner. Convert noise density to σ assuming an ideal filter with 12 Hz bandwidth (the lowest SMI230 setting) or 50 Hz (half the 100 Hz sample rate). Speed, steering angle and perception noise levels are typical design values with sources pending.

### Test Controller and EPS {#sim-controller}

**Requirements**

| Rule | Status |
| --- | --- |
| Use only as a closed-loop test fixture outside G1 deliverables. | agreed |
| Accept the [Trajectory interface](report.html?doc=g1-interfaces-and-signals&lang=vi#trajectory). | agreed |
| Keep it simple and fixed. Tune gains once and use them for all planner versions under comparison so the controller does not mask planner errors. | agreed |

**Controller**

| Item | Requirement | Unit | Status |
| --- | --- | --- | --- |
| Rate | 100 Hz, faster than the 40 Hz planner. Interpolate between consecutive paths | Hz | agreed |
| Read path | Select points by stamp_us + time_from_start and transform into the current base_link using Ego-motion | — | agreed |
| Steering law | δ = L·κ + K·v²·κ + k_y·e_y + k_ψ·e_ψ. The first two terms are curvature feedforward with K ≈ 0.0029 from the vehicle model. The last two are feedback on lateral and heading errors | rad | agreed |
| Lookahead point | Compute errors at the point 0.5 s ahead on the path to compensate for EPS delay | s | agreed |
| Gains k_y, k_ψ | Tune once in simulation and keep fixed | — | agreed |
| Output | Requested steering wheel angle | rad | agreed |
| Invalid path or 75 ms timeout | Hold the last command, then return steering control within 1 s | s | agreed |

**EPS**

| Item | Requirement | Unit | Status |
| --- | --- | --- | --- |
| Interface | Angle control tracks the requested steering wheel angle | — | agreed |
| Pure delay | 50 | ms | agreed |
| Inertia | First-order element with time constant τ = 0.1 s | s | agreed |
| Rate limit | 6 rad/s at the steering wheel, about 340°/s | rad/s | agreed |
| Angle limit | 0.61 rad at the wheel, about 35° | rad | agreed |
| Controller releases control | Transition the steering angle to the simulated driver's angle over 1 s | s | agreed |
| Output | Front wheel angle = steering wheel angle / 15. Send it to the vehicle model | rad | agreed |

**Limits and extensions**

| Rule | Status |
| --- | --- |
| The simulated EPS takes an angle for simplicity. Vehicle L2 EPS typically takes torque. | agreed |
| Parameters are typical test values. Measurements for a specific EPS are pending. | agreed |
| Use [scenario S13](report.html?doc=benchmark-evaluation&lang=vi#benchmark-scenarios) to test slower actuation. | agreed |

## References

- G1 assignment (`G1_Path_Planning.pdf`), Prototype focus
- Bosch, SMI230 combined inertial sensor for motion detection, 2018 product brief (IMU noise and offset levels)
- Motion signal list and mentor discussions
- [Euro NCAP LSS Test Protocol v4.3](https://cdn.euroncap.com/cars/assets/euro_ncap_lss_test_protocol_v43_f2ddd5f6d6.pdf)
- [Euro NCAP Assessment Protocol Safety Assist Collision Avoidance v10.4.1](https://cdn.euroncap.com/cars/assets/euro_ncap_assessment_protocol_sa_collision_avoidance_v1041_fafe1dd418.pdf)
- [Commission Implementing Regulation (EU) 2021/646, ELKS](https://lawplayer.com/eu/act/32021R0646)
- [UN Regulation No 79, OJ L 2025/3](https://upload.wikimedia.org/wikipedia/commons/f/f3/OJ_L_202500003_of_2025_-_EN_English.pdf)

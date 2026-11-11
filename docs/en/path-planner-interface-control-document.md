# Interface Control Document

| Field | Value |
|---|---|
| Document ID | `PP-ICD` |
| Version | 1.1 |
| Status | BL1 |
| Author | thongbui |
| Reviewer | thongbui |
| Last updated | 2026-11-10 |

## 1. Purpose and scope {#icd-scope}

- **Purpose.** Define all path planner interfaces: messages, fields, types, units, coordinate frames, rates, and timeouts.
- **Scope.** The planner's direct inputs and outputs: 8 inputs and 3 outputs.
- **Out of scope.** Interfaces between other modules (camera to lane model, ADAS Functions module to HMI, EPS to Lateral Controller). The Software Architectural Design describes how the planner uses the data.

## 2. References {#icd-references}

| Document | Use |
|---|---|
| [Software Requirements Specification](report.html?doc=path-planner-software-requirements-specification&lang=en) | Output, timeout, and invalid input requirements |
| [Software Architectural Design](report.html?doc=path-planner-software-architectural-design&lang=en) | How the planner uses each input |
| [ADAS Function Specification](report.html?doc=adas-function-specification&lang=en) | Meaning of state, side, and tlc in FunctionRequests |
| Motion team's signal list (`docs/reference/vehicle-signal-list.txt`) | Chassis signals, rates, and units (mentor) |
| Autoware `autoware_planning_msgs/Trajectory` | Trajectory format |
| AUTOSAR E2E Profile 1; SAE J1850 | CAN frame counter and CRC |
| IEEE 802.1AS (gPTP) | Clock synchronization across ECUs |

## 3. Interface overview {#icd-overview}

| Message | From → to | Transport | Rate | Timeout | Maximum age | Section |
|---|---|---|---|---|---|---|
| LaneModel | Lane Model → Planner | Pub/sub | 20 Hz | 150 ms | 250 ms | 5.1 |
| ObjectList | Perception → Planner | Pub/sub | 20 Hz | 150 ms | 250 ms | 5.2 |
| `IMU_Data`, `SAS_Steering`, `ESC_Speed` | Vehicle → Planner | CAN | 100, 100, 50 Hz | 30, 30, 60 ms | — | 5.3 |
| VehicleStateEstimate | State Estimator → Planner | Pub/sub | 50 Hz | 60 ms | 30 ms | 5.4 |
| EgoMotionQuery | Planner ↔ Ego-motion | Function call | Each cycle | — | — | 5.5 |
| FunctionRequests | ADAS Functions → Planner | Pub/sub | 40 Hz | 75 ms | 45 ms | 5.6 |
| LongitudinalPlan | Longitudinal module → Planner | Pub/sub | 40 Hz | 75 ms | 45 ms | 5.7 |
| VehicleConfig | Vehicle Configuration → Planner | Read at startup | — | — | — | 5.8 |
| Trajectory | Planner → Lateral Controller | Pub/sub | 40 Hz | 75 ms | — | 6.1 |
| PathStatus | Planner → ADAS Functions, Lateral Controller | Pub/sub | 40 Hz | 75 ms | — | 6.2 |
| LateralLimits | Planner → Longitudinal module | Pub/sub | 40 Hz | 75 ms | — | 6.3 |

| Rule | Value | Source |
|---|---|---|
| CAN frame rates | As specified in the signal list | mentor |
| Planner and ADAS Functions rates | 40 Hz | mentor |
| Receive timeout | 3 nominal message periods, allowing 2 consecutive missed messages | team agreement |
| Maximum age | Maximum assumed latency (Software Requirements Specification Section 6) plus 1 cycle. LaneModel and ObjectList: 250 ms (PP-SWR-131) | team agreement |

## 4. Common conventions {#header}

**Internal message header.** Every pub/sub message has this header. PathStatus, LateralLimits, and FunctionRequests omit `frame_id`.

| Field | Type | Meaning |
|---|---|---|
| `stamp_us` | uint64 [µs] | Time represented by the data, on the transmitting ECU's gPTP-synchronized clock. CAN frames are timestamped on receipt using the receiving ECU's clock |
| `counter` | uint8 | Increments by 1 with each transmission and wraps over 0–255 |
| `valid` | bool | Validity flag for the entire message |
| `frame_id` | uint8 enum | `BASE_LINK`: center of the rear axle, x forward, y left, z up |

**Data types.**

| Type | Convention |
|---|---|
| Physical quantities | float32, SI units, except for time |
| Time | uint64, µs |
| Enum | uint8, each value has a fixed numeric code |
| Array | Fixed size: `lines[4]`, `road_edges[2]`, `objects[32]`, `points[31]`, `requests[3]`. Arrays without a fixed ordering have a field counting the elements actually used |

**Transport.**

| Method | Use |
|---|---|
| CAN | Chassis signals, with DBC, counter, and CRC |
| In-memory pub/sub | Within the ADAS ECU, like middleware: latency, jitter, and possible message loss |
| Function call | Ego-motion: returns the result in the same cycle |

**Receiver checks.**

- A message is invalid if the receive timeout has elapsed.
- Age = current time minus `stamp_us`. A message is invalid if it exceeds the maximum age.
- CAN frames are timestamped on receipt, so check only timeout, counter, and CRC.

The interfaces are defined once in `src/` to generate Python types. The same definitions can generate C structs or `.msg` files.

## 5. Input {#icd-input}

### 5.1 LaneModel {#lane-model}

- Markings for three lanes (ego, left, and right) and road edges on both sides, in `base_link` at camera capture time.
- `lines[4]` is always ordered L2, L1, R1, R2. L1 and R1 bound the ego lane; L2 and R2 are the outer markings of the left and right lanes. `road_edges[2]` is ordered left, right.
- For each marking and road edge: y(x) = c0 + c1·x + c2·x² + c3·x³, κ ≈ 2·c2, within the range actually observed.
- Lane Model reports the actual `status` of each marking and does not reconstruct ego-lane markings from adjacent-lane markings.

| Field | Type [unit] | Meaning |
|---|---|---|
| `lines[4].c0` … `c3` | float32 [m], [-], [1/m], [1/m²] | Polynomial coefficients |
| `lines[4].variance` | float32[4] | Variances of c0 … c3 |
| `lines[4].view_range_start`, `view_range_end` | float32 [m] | Observed range |
| `lines[4].confidence` | float32 [0..1] | Confidence |
| `lines[4].type` | uint8 enum { DASHED, SOLID, DOUBLE, UNKNOWN } | Type of painted marking |
| `lines[4].crossable` | bool | Whether crossing is permitted from the vehicle's side, including combined dashed and solid double markings |
| `lines[4].status` | uint8 enum { MEASURED, PREDICTED, LOST } | Measured, reconstructed, or lost |
| `lines[4].predicted_duration` | float32 [s] | Time for which the marking has been reconstructed |
| `road_edges[2].c0` … `c3`, `variance`, `view_range_start`, `view_range_end`, `confidence`, `status`, `predicted_duration` | Same as `lines[4]` | Same as `lines[4]` |
| `road_edges[2].type` | uint8 enum { CURB, GRASS_GRAVEL, BARRIER, GUARDRAIL, WALL, UNKNOWN } | Road edge type |
| `lane_width` | float32 [m] | Ego-lane width |
| `lane_width_source` | uint8 enum { MEASURED, REMEMBERED } | Measured or stored lane width |
| `lane_change` | uint8 enum { NONE, LEFT, RIGHT } | Set after Lane Model reindexes the markings for the new lane |

### 5.2 ObjectList {#perception}

- Corner radars provide rear coverage as well. Position refers to the object's center, in `base_link` at measurement time.
- Velocity is relative to the ground and projected into `base_link`. Oncoming vehicles have vx < 0. `heading` is the angle of the velocity vector.
- `id` remains stable across frames.

| Field | Type [unit] |
|---|---|
| `num_objects` | uint8 [0..32] |
| `objects[32].id` | uint32 |
| `objects[32].x`, `y` | float32 [m] |
| `objects[32].vx`, `vy` | float32 [m/s] |
| `objects[32].heading` | float32 [rad] |
| `objects[32].length`, `width` | float32 [m] |
| `objects[32].existence_probability` | float32 [0..1] |

### 5.3 Chassis CAN {#can}

- The planner reads yaw rate, a_x, and a_y (filtered), steering wheel angle and angular rate, vehicle speed, and direction of travel. Driver torque goes to the ADAS Functions module; individual wheel speeds and odometer readings go to Ego-motion.
- The IDs, byte positions, and scaling factors below are for the simulator. In a real vehicle, the receiver reads the vehicle's DBC and converts to the same SI units; the planner is unchanged.
- 500 kbit/s bus, 8-byte frames. Load is about 250 frames/s, or about 7 % of bandwidth.

| Frame | Signals | Period |
|---|---|---|
| `IMU_Data 0x1A0` | Bytes 0–1 YawRate (filtered), int16 × 0.01 °/s; bytes 2–3 AccelX, bytes 4–5 AccelY (filtered), int16 × 0.001 m/s² | 10 ms |
| `SAS_Steering 0x1B0` | Bytes 0–1 SteeringWheelAngle, int16 × 0.1 °; bytes 2–3 SteeringWheelSpeed, int16 × 0.1 °/s | 10 ms |
| `ESC_Speed 0x1C0` | Bytes 0–1 VehicleSpeed, uint16 × 0.01 km/h; byte 2 bits 0–1 Direction { FORWARD, REVERSE, STANDSTILL } | 20 ms |

| Item | Convention |
|---|---|
| Byte 6 | Bits 0–3 Counter (0–15), bits 4–5 Qualifier { VALID, INIT, DEGRADED, FAULT }, bits 6–7 reserved |
| Byte 7 | SAE J1850 CRC-8 (polynomial 0x1D) over bytes 0–6 plus Data ID, per AUTOSAR E2E Profile 1 |
| Data ID | Not transmitted; both sides know it in advance: IMU 0x10, steering angle 0x11, ESC 0x12 |
| Byte order | Intel (little-endian) |
| Sign | Per `base_link`: yaw rate, a_y, and steering wheel angle are positive to the left |
| Units | CAN uses the vehicle's units (°, °/s, km/h). The receiver converts to SI once, after verifying the CRC (mentor) |
| Priority | Higher-rate signals have lower IDs |
| Validity | `valid` requires Qualifier VALID, a correct CRC, and a valid counter. Discard a frame with a CRC error or repeated counter; record frame loss if the counter skips |

### 5.4 VehicleStateEstimate {#state-estimator}

| Field | Type [unit] | Meaning |
|---|---|---|
| `lateral_velocity` | float32 [m/s] | v_y at the rear axle center. If estimated at the center of gravity: rear-axle v_y = center-of-gravity v_y − r·l_r |
| `lateral_velocity_variance` | float32 [m²/s²] | Variance of v_y |
| `slip_angle` | float32 [rad] | β ≈ v_y / v |

The timestamp is the estimation time.

### 5.5 EgoMotionQuery {#ego-motion}

| Field | Type [unit] | Meaning |
|---|---|---|
| `request.t1_us`, `request.t2_us` | uint64 [µs] | Two timestamps within the most recent 0.5 s |
| `response.valid` | bool | Whether the result is usable (for example, when the wheels slip) |
| `response.dx`, `dy` | float32 [m] | Motion from t1 to t2, in `base_link` at t1 |
| `response.dyaw` | float32 [rad] | Rotation angle from t1 to t2 |

### 5.6 FunctionRequests {#function-requests}

- `requests[3]` is ordered HWA, LKA, ELK. The timestamp is the request transmission time.
- The planner handles OFF, UNAVAILABLE, and FAULT the same way; the log distinguishes them.

| Field | Type [unit] | Meaning |
|---|---|---|
| `requests[3].state` | uint8 enum { OFF, UNAVAILABLE, STANDBY, REQUEST, FAULT } | OFF: disabled by the driver. UNAVAILABLE: enabled but conditions are not met. FAULT: a fault is present |
| `requests[3].side` | uint8 enum { NONE, LEFT, RIGHT } | Side toward which the vehicle is drifting. HWA uses NONE |
| `requests[3].tlc` | float32 [s] | TLC calculated by the ADAS Functions module. HWA ignores it |
| `requests[3].elk_reason` | uint8 enum { NONE, SOLID_LINE, ROAD_EDGE, ONCOMING, OVERTAKING } | For logging only |
| `requests[3].cancel_reason` | uint8 enum { NONE, DRIVER_OVERRIDE, INDICATOR, SPEED, LANE_QUALITY, ESC, FAULT } | For logging only |
| `driver_override` | bool | Driver override in progress, shared by the whole message |

### 5.7 LongitudinalPlan {#longitudinal-plan}

| Field | Type [unit] | Meaning |
|---|---|---|
| `mode` | uint8 enum { OFF, CRUISE, FOLLOW, CURVE_LIMIT } | Longitudinal module mode |
| `points[31].v` | float32 [m/s] | Planned speed at 0.1 s intervals on the same time grid as Trajectory |
| `points[31].a` | float32 [m/s²] | Planned acceleration |
| `target_id` | uint32 | Object being followed; 0 if none |

### 5.8 VehicleConfig {#vehicle-config}

- Read once at startup. If missing, the planner does not publish Trajectory (PP-SWR-146).
- This is the sole source of vehicle parameters. The planner does not assume a specific vehicle.

| Field | Type [unit] | Meaning |
|---|---|---|
| `wheelbase` | float32 [m] | Wheelbase |
| `rear_axle_to_cg` | float32 [m] | Distance from the rear axle center to the center of gravity |
| `vehicle_width` | float32 [m] | Width including mirrors, ≤ 2.5 m (QCVN 09:2015/BGTVT 2.1.1.1 b) |
| `steering_ratio` | float32 [-] | Steering wheel angle divided by front wheel angle |
| `max_wheel_angle` | float32 [rad] | Maximum front wheel angle |
| `max_steering_wheel_rate` | float32 [rad/s] | Maximum steering wheel angular rate |
| `actuator_delay` | float32 [s] | Nominal EPS actuation delay |

## 6. Output {#icd-output}

### 6.1 Trajectory {#trajectory}

- Follows Autoware Trajectory, in `base_link` at `header.stamp_us`. `stamp_us` is the time represented by the path, after lane model latency compensation.
- 31 points at 0.1 s intervals, covering 0–3 s. The receiver interpolates linearly in time between points.
- Planar problem: pose comprises x, y, and yaw. When converting to a 3D Pose, z = 0 and rotation is only about the z axis.

| Field | Type [unit] | Meaning |
|---|---|---|
| `points[31].time_from_start` | float32 [s] | Relative to `header.stamp_us` |
| `points[31].pose.x`, `pose.y` | float32 [m] | Position |
| `points[31].pose.yaw` | float32 [rad] | Heading |
| `points[31].longitudinal_velocity_mps` | float32 [m/s] | From LongitudinalPlan; use current speed if missing (PP-SWR-153, 154) |
| `points[31].lateral_velocity_mps` | float32 [m/s] | Lateral velocity |
| `points[31].acceleration_mps2` | float32 [m/s²] | From LongitudinalPlan; 0 if missing |
| `points[31].heading_rate_rps` | float32 [rad/s] | v·κ |
| `points[31].curvature` | float32 [1/m] | Curvature |
| `points[31].front_wheel_angle_rad` | float32 [rad] | Suggested front wheel angle for feedforward |
| `points[31].rear_wheel_angle_rad` | float32 [rad] | Always 0 |

### 6.2 PathStatus {#path-status}

- Receivers: the ADAS Functions module and the Lateral Controller. The Lateral Controller controls steering only when `path_valid = true` and `active_function` is not NONE.

| Field | Type | Meaning |
|---|---|---|
| `path_valid` | bool | Whether the path is usable. False when `T_coast` expires or a required input is invalid (PP-SWR-124, 142 to 145) |
| `active_function` | uint8 enum { NONE, HWA, LKA, ELK } | Arbitration result: the function in control. NONE when `path_valid = false` |
| `intervention_phase` | uint8 enum { NONE, ACTIVE, COMPLETED } | Phase of the LKA or ELK intervention |
| `lateral_limit_reached` | bool | The path is being limited because the required a_y exceeds the active function's limit (PP-SWR-007 to 009) |
| `lane_too_narrow` | bool | Free space on each side is less than `free_space_min` (PP-SWR-063) |

### 6.3 LateralLimits {#lateral-limits}

| Field | Type [unit] | Meaning |
|---|---|---|
| `v_max` | float32 [m/s] | √(active function's a_y limit / κ_max), where κ_max is the maximum curvature of the reference line within the visible range (PP-SWR-151) |
| `distance` | float32 [m] | Longitudinal distance to the point with κ_max (PP-SWR-152) |
| `lateral_limit_reached` | bool | Same value as in PathStatus for the same cycle (PP-SWR-009) |

## Revision history {#revision-history}

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-11-10 | Restructured as the Interface Control Document, baseline BL1. Added the overview table; consolidated FunctionRequests, LongitudinalPlan, PathStatus, and LateralLimits here; added `lane_too_narrow` to PathStatus; made VehicleConfig the sole source of vehicle parameters, with width ≤ 2.5 m including mirrors; removed status labels |
| 1.1 | 2026-11-10 | Also publish PathStatus to the Lateral Controller so it does not steer when no function is in control |

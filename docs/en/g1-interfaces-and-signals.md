# G1 Interfaces and Signals

This report defines the data contract between the Path Planner and other onboard modules. See [Path Planner Feature Design](report.html?doc=path-planner-feature-design&lang=vi) for how the planner uses these inputs during normal operation and signal loss.

## Header and common conventions {#header}

### Internal message header

| Field | Requirement | Type | Status |
|---|---|---|---|
| stamp_us | Time represented by the data, on the sending ECU clock with gPTP-style synchronization. For a CAN frame, the receiving ECU assigns the timestamp at reception using its own clock | uint64 (µs) | agreed |
| counter | Increments by 1 per transmission and wraps over 0–255 to detect missing or repeated messages | uint8 | agreed |
| valid | Validity flag for the whole message | bool | agreed |
| frame_id | BASE_LINK coordinate frame at the rear axle center, with x forward, y left and z up | uint8 enum | agreed |

### Data types

| Category | Requirement | Type | Status |
|---|---|---|---|
| Real number | All physical quantities except time | float32 | agreed |
| Time | Integer microseconds | uint64 | agreed |
| Enum | A fixed numeric value for each member | uint8 | agreed |
| Array | Fixed size with a count of elements in use | — | agreed |
| Array sizes | lines[4], objects[32], points[31], requests[3] | — | agreed |

### Transport

| Transport | Use | — | Status |
|---|---|---|---|
| CAN | Chassis signals (IMU, speed and steering angle) defined in a DBC file, with a counter and CRC | — | agreed |
| In-memory pub/sub | Internal ADAS ECU links with middleware-like delay, jitter and possible message loss | — | agreed |
| Query | Ego motion uses a function call that returns within the same cycle | — | agreed |

### Receiver timing checks

| Rule | Status |
|---|---|
| The receive timeout measures the time since the last new message. It is 3 nominal periods, allowing 2 consecutive missed messages. | agreed |
| Maximum age is the current time minus the message stamp_us. The limit is the maximum delay plus 1 period. | agreed |
| The receiver timestamps CAN frames at reception. It checks the receive timeout, counter and CRC. | agreed |

For the prototype, define interfaces once in `src/` to generate the Python types. The same definitions can later generate C structs or `.msg` files. The Research reports record the fields and design decisions.

## Chassis signals over CAN {#can}

The planner reads filtered IMU signals, vehicle speed from the ESC and the steering wheel angle and rate. Camera and radar data pass through Lane Model or Perception. Driver torque from the EPS goes to ADAS Functions. Individual wheel speeds, odometer readings and wheel revolution counts go to Ego-motion (G4).

The IMU sends yaw rate and longitudinal and lateral acceleration expressed in `base_link`. Acceleration depends on the IMU mounting position. The logger retains raw signals to measure filter delay. The ESC calculates vehicle speed from all four wheels and sends the direction of travel. The receiver assigns the timestamp on CAN reception and converts to SI once. The planner uses yaw rate to check curvature and steering angle to estimate initial path curvature.

### Proposed DBC frames

The CAN bus runs at 500 kbit/s with 8 bytes per frame. The mentor supplies the signal list and periods. The IDs, byte positions and scales below are proposed for simulation. Use the vehicle DBC when it becomes available.

| Frame | Signals | Period |
|---|---|---|
| `IMU_Data 0x1A0` | Bytes 0–1 carry filtered YawRate (int16 × 0.01 °/s). Bytes 2–3 carry filtered AccelX and bytes 4–5 carry filtered AccelY (int16 × 0.001 m/s²) | 10 ms |
| `SAS_Steering 0x1B0` | Bytes 0–1 carry SteeringWheelAngle (int16 × 0.1 °). Bytes 2–3 carry SteeringWheelSpeed (int16 × 0.1 °/s) | 10 ms |
| `ESC_Speed 0x1C0` | Bytes 0–1 carry VehicleSpeed (uint16 × 0.01 km/h). Byte 2 bits 0–1 carry Direction {FORWARD, REVERSE, STANDSTILL} | 20 ms |

### Conventions shared by the three frames

| Item | Convention | — | Status |
|---|---|---|---|
| Byte 6 | Bits 0–3 are the Counter (0–15), bits 4–5 are the Qualifier and bits 6–7 are reserved | — | agreed |
| Byte 7 | CRC-8 SAE J1850 (polynomial 0x1D) over bytes 0–6 and the frame Data ID, following the AUTOSAR E2E Profile 1 approach | — | agreed |
| Data ID | Both endpoints know the ID in advance. It is omitted from the frame. IMU 0x10, steering angle 0x11, ESC 0x12 | — | agreed |
| Qualifier | Shared 2-bit enum with VALID, INIT, DEGRADED and FAULT values | — | agreed |
| Byte order | Intel (little-endian) for all signals | — | agreed |
| Sign convention | Follows base_link. Yaw rate is positive in a left turn, a_y is positive toward the left and steering wheel angle is positive when steering left | — | agreed |
| Units | CAN retains the vehicle units (°, °/s, km/h). The receiver converts to SI (rad, rad/s, m/s) once, immediately after the CRC check. The planner uses SI throughout | — | mentor |
| Priority | Lower IDs have higher bus priority. Faster signals use lower IDs | — | agreed |
| Bus load | About 250 frames/s and 33 kbit/s, roughly 7% of 500 kbit/s | — | agreed |

### Receiver checks

| Rule | Status |
|---|---|
| The receiver sets valid when Qualifier is VALID, the CRC matches and the counter is valid. | agreed |
| The receiver checks the counter and CRC (E2E) on each incoming frame. It discards frames with a bad CRC or repeated counter. It records frame loss when the counter skips. | agreed |
| Frame periods from the signal list are 10 ms for IMU, 10 ms for steering angle and 20 ms for ESC speed. | mentor |
| The receive timeout is 3 periods, or 30 ms for IMU and steering angle and 60 ms for ESC speed. After that interval the signal becomes invalid. | agreed |

Actual CAN delay is unknown. The simulation assumes about 5 ms, excluding filter delay.

## LaneModel {#lane-model}

Lane Model sends up to four markings in the `base_link` frame at camera capture. L1/R1 bound the current lane and L2/R2 are the outer markings. The view range gives the endpoints of the observed segment. Each marking uses y(x) = c0 + c1·x + c2·x² + c3·x³, with κ ≈ 2·c2. `crossable` is evaluated from the side where the vehicle is traveling, including for a dashed-solid double marking. The lane change flag is set after the markings have been reassigned. The `lines[4]` array always uses the order L2, L1, R1, R2.

Uses the [common header](report.html?doc=g1-interfaces-and-signals&lang=vi#header).

| Field | Type, unit and convention | Status |
|---|---|---|
| `lines[4].c0` | float32 [m] | assignment |
| `lines[4].c1` | float32 [-] | assignment |
| `lines[4].c2` | float32 [1/m] | assignment |
| `lines[4].c3` | float32 [1/m²] | assignment |
| `lines[4].variance` | float32[4] (c0..c3) | agreed |
| `lines[4].view_range_start` | float32 [m] | assignment |
| `lines[4].view_range_end` | float32 [m] | assignment |
| `lines[4].confidence` | float32 [0..1] | assignment |
| `lines[4].type` | uint8 enum { DASHED, SOLID, DOUBLE, ROAD_EDGE, BARRIER, UNKNOWN } | agreed |
| `lines[4].crossable` | bool | agreed |
| `lines[4].status` | uint8 enum { MEASURED, PREDICTED, LOST } | agreed |
| `lines[4].predicted_duration` | float32 [s] | agreed |
| `lane_width` | float32 [m] | assignment |
| `lane_width_source` | uint8 enum { MEASURED, REMEMBERED } | assignment |
| `lane_change` | uint8 enum { NONE, LEFT, RIGHT } | agreed |

See [inputs and delay compensation](report.html?doc=path-planner-feature-design&lang=vi#planner-inputs) for frequency, timeout and data age. See [Lane Model faults](report.html?doc=path-planner-feature-design&lang=vi#lane-faults) for noise levels, marking reconstruction and the division of work between Lane Model and G1. The remaining values are for simulation. Replace them with measurements when real logs are available. Following the lead vehicle's track in congestion is a possible extension.

## ObjectList {#perception}

Corner radars provide rear coverage. The position refers to the object center. Ground-relative velocities are projected onto `base_link` at measurement time. Oncoming vehicles have vx < 0. Heading is the angle of the velocity vector in that frame. IDs remain stable across frames. G1 assigns lanes from Lane Model, predicts motion at constant velocity over a 2–3 s horizon and uses TTC for the HWA center offset. ADAS Functions handles ELK adjacent-lane safety.

Uses the [common header](report.html?doc=g1-interfaces-and-signals&lang=vi#header).

| Field | Type, unit and convention | Status |
|---|---|---|
| `num_objects` | uint8 [0..32] | agreed |
| `objects[32].id` | uint32 | agreed |
| `objects[32].x` | float32 [m] | agreed |
| `objects[32].y` | float32 [m] | agreed |
| `objects[32].vx` | float32 [m/s] (ground-relative) | agreed |
| `objects[32].vy` | float32 [m/s] | agreed |
| `objects[32].heading` | float32 [rad] | agreed |
| `objects[32].length` | float32 [m] | agreed |
| `objects[32].width` | float32 [m] | agreed |
| `objects[32].existence_probability` | float32 [0..1] | agreed |

The assumed delay and data age thresholds match LaneModel. See [planner inputs](report.html?doc=path-planner-feature-design&lang=vi#planner-inputs).

## VehicleStateEstimate {#state-estimator}

Uses the [common header](report.html?doc=g1-interfaces-and-signals&lang=vi#header).

| Field | Type, unit and convention | Status |
|---|---|---|
| `lateral_velocity` | float32 [m/s] (at the rear axle center) | assignment |
| `lateral_velocity_variance` | float32 [m²/s²] | agreed |
| `slip_angle` | float32 [rad] | agreed |

G2 estimates lateral velocity at the rear axle center. If the estimate is at the center of gravity, convert it using v_y,rear = v_y,cg − r·l_r. The sideslip angle is β ≈ v_y / v. The stamp is the time of estimation. G1 uses v_y and its variance to calculate the initial state for intervention. The receive timeout is 60 ms and the maximum age is 30 ms, assuming a delay of about 10 ms at 50 Hz.

## EgoMotionQuery {#ego-motion}

| Field | Type, unit and convention | Status |
|---|---|---|
| `request.t1_us` | uint64 [µs] | agreed |
| `request.t2_us` | uint64 [µs] | agreed |
| `response.valid` | bool | agreed |
| `response.dx` | float32 [m] | agreed |
| `response.dy` | float32 [m] | agreed |
| `response.dyaw` | float32 [rad] | agreed |

The query is synchronous and returns within the same cycle. G4 returns motion from t1 to t2 expressed in `base_link` at t1, with at least 0.5 s of history. The validity flag indicates whether the result can be used, including when wheel slip occurs. G1 uses it for delay compensation, path stitching and keeping the previous path during T_coast.

## VehicleConfig {#vehicle-config}

| Field | Type, unit and convention | Status |
|---|---|---|
| `wheelbase` | float32 [m] | agreed |
| `rear_axle_to_cg` | float32 [m] | agreed |
| `vehicle_width` | float32 [m] | agreed |
| `steering_ratio` | float32 [-] | agreed |
| `max_wheel_angle` | float32 [rad] | agreed |
| `max_steering_wheel_rate` | float32 [rad/s] | agreed |
| `actuator_delay` | float32 [s] | agreed |

The planner reads this configuration once at startup. The distance to the center of gravity is measured from the rear axle center. The steering ratio is the steering wheel angle divided by the front wheel angle. Test parameters come from the [vehicle model](report.html?doc=benchmark-evaluation&lang=vi#sim-vehicle) and [Controller and EPS](report.html?doc=benchmark-evaluation&lang=vi#sim-controller).

## Lateral Controller {#trajectory}

Lateral Controller receives the path and calculates the steering command. G1 scope ends at the [Trajectory](report.html?doc=path-planner-feature-design&lang=vi#planner-outputs) output. The controller also uses vehicle speed, yaw rate, lateral velocity, lateral acceleration, steering angle and torque, and the active feature and its intervention level. The path is expressed in `base_link` at the timestamp. The planar pose uses x, y and yaw. To convert to a 3D pose, set z = 0 and rotate around the z axis only.

Uses the [common header](report.html?doc=g1-interfaces-and-signals&lang=vi#header).

| Field | Type, unit and convention | Status |
|---|---|---|
| `points[31].time_from_start` | float32 [s], relative to `header.stamp_us` | agreed |
| `points[31].pose.x` | float32 [m] | agreed |
| `points[31].pose.y` | float32 [m] | agreed |
| `points[31].pose.yaw` | float32 [rad] | agreed |
| `points[31].longitudinal_velocity_mps` | float32 [m/s] | proposed |
| `points[31].lateral_velocity_mps` | float32 [m/s] | agreed |
| `points[31].acceleration_mps2` | float32 [m/s²] | proposed |
| `points[31].heading_rate_rps` | float32 [rad/s] | agreed |
| `points[31].front_wheel_angle_rad` | float32 [rad] | agreed |
| `points[31].rear_wheel_angle_rad` | float32 [rad] (always = 0) | agreed |
| `points[31].curvature` | float32 [1/m] | agreed |

Pub/sub runs at 40 Hz, with a 75 ms receive timeout and an assumed transmission delay of about 1 ms. The [planner design](report.html?doc=path-planner-feature-design&lang=vi#planner-outputs) specifies interpolation, how speed and acceleration are populated, and when the path can be sent to the controller.

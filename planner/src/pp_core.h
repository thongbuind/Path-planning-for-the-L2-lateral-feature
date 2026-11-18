/*
 * Core shared by the two planners (PP-ADR-016): state common to both, T1 input check, the
 * frame every cycle starts from (T2 reference line, T5 curvature fusion, ego-motion, old
 * path for T4) and the Trajectory header. Each planner builds this file into its own library;
 * the two share no state at run time.
 */

#ifndef PP_CORE_H
#define PP_CORE_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "curvature.h"
#include "feasibility.h"
#include "input_check.h"
#include "pp_calibration.h"
#include "pp_planner.h"
#include "pp_types.h"
#include "reference_line.h"
#include "stitching.h"

#define PP_US_PER_S (1.0e6)

/* FunctionRequests order, ICD 5.6. */
#define PP_FUNCTION_LCC (0U)
#define PP_FUNCTION_LKA (1U)
#define PP_FUNCTION_ELK (2U)

/* T1: last accepted message of each pub/sub input and its counter check (ICD 4). */
typedef struct {
    pp_counter_check_t lane_model_check;
    pp_counter_check_t object_list_check;
    pp_counter_check_t lead_target_check;
    pp_counter_check_t vehicle_state_check;
    pp_counter_check_t function_requests_check;
    pp_counter_check_t longitudinal_plan_check;
    pp_received_lane_model_t lane_model;
    pp_received_object_list_t object_list;          /* LCC planner only */
    pp_received_lead_target_t lead_target;          /* LCC planner only */
    pp_received_vehicle_state_estimate_t vehicle_state;
    pp_received_function_requests_t function_requests;
    pp_received_longitudinal_plan_t longitudinal_plan;
} pp_held_inputs_t;

/* First member of the state of each planner. */
typedef struct {
    uint32_t magic;                 /* Marks memory that init has set up, per planner */
    bool initialized;               /* init returned OK */
    pp_held_inputs_t held;          /* T1: accepted pub/sub messages */
    pp_vehicle_config_t vehicle;    /* Copy of VehicleConfig, read once (ICD 5.8) */
    const pp_calibration_t *cal;    /* Built-in calibration data set */
    uint8_t trajectory_counter;     /* Header counters, wrap at 256 (ICD 4) */
    uint8_t status_counter;
    uint8_t lateral_limits_counter;
    pp_reference_memory_t ref_mem;  /* T2 memory */
    pp_previous_path_t prev_path;   /* T4: path sent in the previous cycle */
    pp_limit_flag_t limit_flag;     /* T10: lateral_limit_reached */
    bool requests_clock_set;
    uint64_t last_requests_us;      /* PP-SWR-145, most recent usable receive time */
    bool has_prev_t0;               /* t0 of the previous cycle, for ego-motion between cycles */
    uint64_t prev_t0_us;
    pp_curvature_t curv;            /* T5 estimate */
    bool t5_has_stamp;              /* Capture stamp of the last frame T5 used */
    uint64_t t5_stamp_us;
} pp_core_state_t;

/* The newest delivered message of each input; NULL for an input the planner does not have. */
typedef struct {
    uint64_t t0_us;
    const pp_received_lane_model_t *lane_model;
    const pp_received_object_list_t *object_list;
    const pp_received_lead_target_t *lead_target;
    const pp_received_imu_signals_t *imu;
    const pp_received_steering_signals_t *steering;
    const pp_received_speed_signals_t *speed;
    const pp_received_vehicle_state_estimate_t *vehicle_state;
    const pp_received_function_requests_t *function_requests;
    const pp_received_longitudinal_plan_t *longitudinal_plan;
} pp_common_inputs_t;

/* Newest message of each input that passed the input check, or NULL. */
typedef struct {
    const pp_lane_model_t *lane_model;
    const pp_object_list_t *object_list;
    const pp_lead_target_t *lead_target;
    const pp_speed_signals_t *speed;
    const pp_imu_signals_t *imu;
    const pp_steering_signals_t *steering;
    const pp_vehicle_state_estimate_t *vehicle_state;
    const pp_function_requests_t *function_requests;
    uint64_t requests_rx_us;
    bool requests_timed_out;
    const pp_longitudinal_plan_t *longitudinal_plan;
} pp_usable_inputs_t;

/* What every cycle starts from, after T1, T2 and T5. */
typedef struct {
    bool forward;                   /* ESC_Speed says forward */
    bool chassis_valid;             /* forward and IMU, steering and speed all usable (PP-SWR-142) */
    bool moved;                     /* since_last is valid */
    pp_motion_t since_last;         /* Ego-motion since the previous cycle */
    pp_old_path_t old;              /* T4 step 1 */
    double dt;                      /* [s] */
    double v;                       /* [m/s] */
    double v_y;                     /* [m/s] 0 when VehicleStateEstimate is not usable */
    double yaw_rate;                /* [rad/s] */
    pp_lane_at_t0_t lane;
    bool lane_ok;                   /* A lane model was usable and moved to t0 */
    pp_reference_line_t ref;        /* T2, then T5 */
    pp_reference_line_t camera_ref; /* T2 before T5, for T10 steps 3, 4 */
} pp_frame_t;

bool pp_core_vehicle_config_valid(const pp_vehicle_config_t *cfg);

/*
 * init of both planners. `state` holds a struct of `needed` bytes whose first member is
 * pp_core_state_t. Anything but OK: the planner never sends a Trajectory (PP-SWR-146).
 */
pp_init_result_t pp_core_init(void *state, size_t state_size, size_t needed, uint32_t magic,
                              const pp_vehicle_config_t *vehicle_config);

/* State memory that init has set up (whether or not initialisation succeeded), or NULL. */
pp_core_state_t *pp_core_prepared(void *state, uint32_t magic);

uint8_t pp_core_next_counter(uint8_t *counter);

/* T1: counter check; the accepted message is held until replaced. */
void pp_core_hold_inputs(pp_core_state_t *core, const pp_common_inputs_t *in);
void pp_core_check_inputs(const pp_core_state_t *core, const pp_common_inputs_t *in,
                          pp_usable_inputs_t *out);
void pp_core_check_requests_timeout(pp_core_state_t *core, uint64_t t0_us, pp_usable_inputs_t *out);

/* T1 step 2: motion from `capture_us` to t0. False when not available (PP-SWR-143). */
bool pp_core_motion_to_t0(uint64_t capture_us, uint64_t t0_us, pp_ego_motion_fn ego_motion,
                          void *context, pp_motion_t *motion);

/* T1, T2, T5 and the old path; on a car that does not drive forward only the memories reset. */
void pp_core_frame(pp_core_state_t *core, const pp_usable_inputs_t *in, uint64_t t0_us,
                   pp_ego_motion_fn ego_motion, void *context, pp_frame_t *frame);

pp_lateral_state_t pp_core_measure_lateral(const pp_reference_line_t *ref, double v, double v_y,
                                           double yaw_rate);

/* x up to which T4 keeps the path continuous: the observed range, or all of it while coasting. */
double pp_core_continuity_limit(const pp_reference_line_t *ref);

/* PP-SWR-018: time on the path where it leaves the view range of its reference line. */
float pp_core_observed_horizon(const pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],
                               const pp_reference_line_t *ref);

/*
 * T11: the Trajectory of this cycle, header.valid = `valid`, and the path kept for T4 of the
 * next cycle.
 */
void pp_core_publish_trajectory(pp_core_state_t *core, uint64_t t0_us, bool valid,
                                const pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],
                                const pp_reference_line_t *ref, pp_planner_id_t planner,
                                pp_trajectory_t *out);

#endif /* PP_CORE_H */

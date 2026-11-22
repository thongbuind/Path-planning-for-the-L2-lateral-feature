/* Hai planner dùng chung kiểu core và thuật toán, mỗi instance giữ state riêng (PP-ADR-016). */

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

#define PP_FUNCTION_LCC (0U)
#define PP_FUNCTION_LKA (1U)
#define PP_FUNCTION_ELK (2U)

typedef struct {
    pp_counter_check_t lane_model_check;
    pp_counter_check_t object_list_check;
    pp_counter_check_t lead_target_check;
    pp_counter_check_t vehicle_state_check;
    pp_counter_check_t function_requests_check;
    pp_counter_check_t longitudinal_plan_check;
    pp_received_lane_model_t lane_model;
    pp_received_object_list_t object_list;
    pp_received_lead_target_t lead_target;
    pp_received_vehicle_state_estimate_t vehicle_state;
    pp_received_function_requests_t function_requests;
    pp_received_longitudinal_plan_t longitudinal_plan;
} pp_held_inputs_t;

typedef struct {
    uint32_t magic;
    bool initialized;
    pp_held_inputs_t held;
    pp_vehicle_config_t vehicle;  /* Sao chép VehicleConfig một lần lúc khởi tạo. */
    const pp_calibration_t *cal;
    uint8_t trajectory_counter;  /* Counter header quay vòng tại 256 (ICD 4). */
    uint8_t status_counter;
    uint8_t lateral_limits_counter;
    pp_reference_memory_t ref_mem;
    pp_previous_path_t prev_path;
    pp_limit_flag_t limit_flag;
    bool requests_clock_set;
    uint64_t last_requests_us;
    bool has_prev_t0;
    uint64_t prev_t0_us;
    pp_curvature_t curv;
    bool t5_has_stamp;
    uint64_t t5_stamp_us;
} pp_core_state_t;

/* Input mới nhất đã giao; NULL khi planner chưa nhận. */
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

/* Input mới nhất vượt kiểm tra nhận. NULL nếu không dùng được. */
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

typedef struct {
    bool forward;
    bool chassis_valid;
    bool moved;
    pp_motion_t since_last;
    pp_old_path_t old;
    double dt;
    double v;
    double v_y;  /* [m/s] Dùng 0 khi VehicleStateEstimate không dùng được. */
    double yaw_rate;
    pp_lane_at_t0_t lane;
    bool lane_ok;
    pp_reference_line_t ref;
    pp_reference_line_t camera_ref;
} pp_frame_t;

bool pp_core_vehicle_config_valid(const pp_vehicle_config_t *cfg);

/* Core đọc cùng bố cục vì state của mỗi họ mở đầu bằng pp_core_state_t. Khởi tạo khác OK thì
 * không phát Trajectory. */
pp_init_result_t pp_core_init(void *state, size_t state_size, size_t needed, uint32_t magic,
                              const pp_vehicle_config_t *vehicle_config);

/* Trả state khi init đã đặt marker, kể cả khi init báo lỗi; thiếu marker thì trả NULL. */
pp_core_state_t *pp_core_prepared(void *state, uint32_t magic);

uint8_t pp_core_next_counter(uint8_t *counter);

void pp_core_hold_inputs(pp_core_state_t *core, const pp_common_inputs_t *in);
void pp_core_check_inputs(const pp_core_state_t *core, const pp_common_inputs_t *in,
                          pp_usable_inputs_t *out);
void pp_core_check_requests_timeout(pp_core_state_t *core, uint64_t t0_us, pp_usable_inputs_t *out);

bool pp_core_motion_to_t0(uint64_t capture_us, uint64_t t0_us, pp_ego_motion_fn ego_motion,
                          void *context, pp_motion_t *motion);

/* T1/T2/T5 và path cũ; khi xe không tiến chỉ reset bộ nhớ. */
void pp_core_frame(pp_core_state_t *core, const pp_usable_inputs_t *in, uint64_t t0_us,
                   pp_ego_motion_fn ego_motion, void *context, pp_frame_t *frame);

pp_lateral_state_t pp_core_measure_lateral(const pp_reference_line_t *ref, double v, double v_y,
                                           double yaw_rate);

/* T4 giữ liên tục tới hết vùng quan sát. Khi COAST dùng toàn path. */
double pp_core_continuity_limit(const pp_reference_line_t *ref);

float pp_core_observed_horizon(const pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],
                               const pp_reference_line_t *ref);

void pp_core_publish_trajectory(pp_core_state_t *core, uint64_t t0_us, bool valid,
                                const pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],
                                const pp_reference_line_t *ref, pp_planner_id_t planner,
                                pp_trajectory_t *out);

#endif

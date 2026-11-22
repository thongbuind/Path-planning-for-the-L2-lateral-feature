/* Sinh từ interfaces/gen.py và interfaces/schema. */

#ifndef PP_TYPES_H
#define PP_TYPES_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define PP_COUNTER_MODULO (256U)
typedef uint8_t pp_frame_id_t;
#define PP_FRAME_ID_BASE_LINK ((pp_frame_id_t)0U)
typedef uint8_t pp_side_t;
#define PP_SIDE_NONE ((pp_side_t)0U)
#define PP_SIDE_LEFT ((pp_side_t)1U)
#define PP_SIDE_RIGHT ((pp_side_t)2U)

#define PP_IMU_TIMEOUT_US (30000ULL)
#define PP_STEERING_TIMEOUT_US (30000ULL)
#define PP_SPEED_TIMEOUT_US (60000ULL)
typedef uint8_t pp_direction_t;
#define PP_DIRECTION_FORWARD ((pp_direction_t)0U)
#define PP_DIRECTION_REVERSE ((pp_direction_t)1U)
#define PP_DIRECTION_STANDSTILL ((pp_direction_t)2U)

#define PP_EGO_MOTION_WINDOW_US (500000ULL) /* t1 và t2 trong 0,5 s vừa qua. */

#define PP_FUNCTIONS (3U) /* Thứ tự requests: LCC, LKA, ELK. */
#define PP_FUNCTION_REQUESTS_TIMEOUT_US (75000ULL)
#define PP_FUNCTION_REQUESTS_MAX_DELTA_COUNTER (4U) /* Bước counter lớn nhất theo ICD 4: floor((75 + 25) / 25), với thời gian tính bằng ms. */
#define PP_FUNCTION_REQUESTS_MAX_AGE_US (45000ULL)
typedef uint8_t pp_request_state_t;
#define PP_REQUEST_STATE_OFF ((pp_request_state_t)0U)
#define PP_REQUEST_STATE_UNAVAILABLE ((pp_request_state_t)1U)
#define PP_REQUEST_STATE_STANDBY ((pp_request_state_t)2U)
#define PP_REQUEST_STATE_REQUEST ((pp_request_state_t)3U)
#define PP_REQUEST_STATE_FAULT ((pp_request_state_t)4U)
typedef uint8_t pp_elk_reason_t;
#define PP_ELK_REASON_NONE ((pp_elk_reason_t)0U)
#define PP_ELK_REASON_SOLID_LINE ((pp_elk_reason_t)1U)
#define PP_ELK_REASON_ROAD_EDGE ((pp_elk_reason_t)2U)
#define PP_ELK_REASON_ONCOMING ((pp_elk_reason_t)3U)
#define PP_ELK_REASON_OVERTAKING ((pp_elk_reason_t)4U)
typedef uint8_t pp_cancel_reason_t;
#define PP_CANCEL_REASON_NONE ((pp_cancel_reason_t)0U)
#define PP_CANCEL_REASON_DRIVER_OVERRIDE ((pp_cancel_reason_t)1U)
#define PP_CANCEL_REASON_INDICATOR ((pp_cancel_reason_t)2U)
#define PP_CANCEL_REASON_SPEED ((pp_cancel_reason_t)3U)
#define PP_CANCEL_REASON_LANE_QUALITY ((pp_cancel_reason_t)4U)
#define PP_CANCEL_REASON_ESC ((pp_cancel_reason_t)5U)
#define PP_CANCEL_REASON_FAULT ((pp_cancel_reason_t)6U)

#define PP_LANE_LINES (4U) /* Thứ tự lines: L2, L1, R1, R2. */
#define PP_ROAD_EDGES (2U) /* Thứ tự road_edges: trái, phải. */
#define PP_LANE_MODEL_TIMEOUT_US (150000ULL)
#define PP_LANE_MODEL_MAX_DELTA_COUNTER (3U) /* Bước counter lớn nhất theo ICD 4: floor((150 + 25) / 50), với thời gian tính bằng ms. */
#define PP_LANE_MODEL_MAX_AGE_US (250000ULL)
typedef uint8_t pp_line_type_t;
#define PP_LINE_TYPE_DASHED ((pp_line_type_t)0U)
#define PP_LINE_TYPE_SOLID ((pp_line_type_t)1U)
#define PP_LINE_TYPE_DOUBLE ((pp_line_type_t)2U)
#define PP_LINE_TYPE_UNKNOWN ((pp_line_type_t)3U)
typedef uint8_t pp_line_status_t;
#define PP_LINE_STATUS_MEASURED ((pp_line_status_t)0U)
#define PP_LINE_STATUS_PREDICTED ((pp_line_status_t)1U)
#define PP_LINE_STATUS_LOST ((pp_line_status_t)2U)
typedef uint8_t pp_road_edge_type_t;
#define PP_ROAD_EDGE_TYPE_CURB ((pp_road_edge_type_t)0U)
#define PP_ROAD_EDGE_TYPE_GRASS_GRAVEL ((pp_road_edge_type_t)1U)
#define PP_ROAD_EDGE_TYPE_BARRIER ((pp_road_edge_type_t)2U)
#define PP_ROAD_EDGE_TYPE_GUARDRAIL ((pp_road_edge_type_t)3U)
#define PP_ROAD_EDGE_TYPE_WALL ((pp_road_edge_type_t)4U)
#define PP_ROAD_EDGE_TYPE_UNKNOWN ((pp_road_edge_type_t)5U)
typedef uint8_t pp_lane_width_source_t;
#define PP_LANE_WIDTH_SOURCE_MEASURED ((pp_lane_width_source_t)0U)
#define PP_LANE_WIDTH_SOURCE_REMEMBERED ((pp_lane_width_source_t)1U)

#define PP_LEAD_TARGET_TIMEOUT_US (150000ULL)
#define PP_LEAD_TARGET_MAX_DELTA_COUNTER (3U) /* Bước counter lớn nhất theo ICD 4: floor((150 + 25) / 50), với thời gian tính bằng ms. */
#define PP_LEAD_TARGET_MAX_AGE_US (250000ULL)
typedef uint8_t pp_lead_class_t; /* Chỉ dùng CAR và TRUCK cho FOLLOW (PP-SWR-170, 176). */
#define PP_LEAD_CLASS_UNKNOWN ((pp_lead_class_t)0U)
#define PP_LEAD_CLASS_CAR ((pp_lead_class_t)1U)
#define PP_LEAD_CLASS_TRUCK ((pp_lead_class_t)2U)
#define PP_LEAD_CLASS_MOTORCYCLE ((pp_lead_class_t)3U)
#define PP_LEAD_CLASS_OTHER ((pp_lead_class_t)4U)

#define PP_LONGITUDINAL_PLAN_POINTS (31U) /* Cùng lưới 0,1 s với Trajectory. */
#define PP_LONGITUDINAL_PLAN_TIMEOUT_US (75000ULL)
#define PP_LONGITUDINAL_PLAN_MAX_DELTA_COUNTER (4U) /* Bước counter lớn nhất theo ICD 4: floor((75 + 25) / 25), với thời gian tính bằng ms. */
#define PP_LONGITUDINAL_PLAN_MAX_AGE_US (45000ULL)
#define PP_LONGITUDINAL_PLAN_V_MAX_MPS (182.04F) /* Biên trên của v, theo ESC_Speed tối đa 655,35 km/h (ICD 5.3). */
#define PP_LONGITUDINAL_PLAN_A_MAX_MPS2 (32.767F) /* Biên của |a| theo miền AccelX của IMU_Data (ICD 5.3). */
typedef uint8_t pp_longitudinal_mode_t;
#define PP_LONGITUDINAL_MODE_OFF ((pp_longitudinal_mode_t)0U)
#define PP_LONGITUDINAL_MODE_CRUISE ((pp_longitudinal_mode_t)1U)
#define PP_LONGITUDINAL_MODE_FOLLOW ((pp_longitudinal_mode_t)2U)
#define PP_LONGITUDINAL_MODE_CURVE_LIMIT ((pp_longitudinal_mode_t)3U)

#define PP_MAX_OBJECTS (32U)
#define PP_OBJECT_LIST_TIMEOUT_US (150000ULL)
#define PP_OBJECT_LIST_MAX_DELTA_COUNTER (3U) /* Bước counter lớn nhất theo ICD 4: floor((150 + 25) / 50), với thời gian tính bằng ms. */
#define PP_OBJECT_LIST_MAX_AGE_US (250000ULL)

#define PP_MAX_VEHICLE_WIDTH_M (2.5F) /* Tính cả gương, QCVN 09:2015/BGTVT 2.1.1.1 b. */

#define PP_VEHICLE_STATE_TIMEOUT_US (60000ULL)
#define PP_VEHICLE_STATE_MAX_DELTA_COUNTER (4U) /* Bước counter lớn nhất theo ICD 4: floor((60 + 25) / 20), với thời gian tính bằng ms. */
#define PP_VEHICLE_STATE_MAX_AGE_US (30000ULL)

#define PP_INTERVENTION_STATUS_TIMEOUT_US (75000ULL)
typedef uint8_t pp_intervention_function_t;
#define PP_INTERVENTION_FUNCTION_NONE ((pp_intervention_function_t)0U)
#define PP_INTERVENTION_FUNCTION_LKA ((pp_intervention_function_t)1U)
#define PP_INTERVENTION_FUNCTION_ELK ((pp_intervention_function_t)2U)
typedef uint8_t pp_intervention_phase_t;
#define PP_INTERVENTION_PHASE_NONE ((pp_intervention_phase_t)0U)
#define PP_INTERVENTION_PHASE_ACTIVE ((pp_intervention_phase_t)1U)
#define PP_INTERVENTION_PHASE_COMPLETED ((pp_intervention_phase_t)2U)

#define PP_LCC_STATUS_TIMEOUT_US (75000ULL)
typedef uint8_t pp_lcc_mode_t; /* Cách LCC dựng path (PP-SWR-177). */
#define PP_LCC_MODE_NONE ((pp_lcc_mode_t)0U)
#define PP_LCC_MODE_LANE ((pp_lcc_mode_t)1U)
#define PP_LCC_MODE_INFERRED ((pp_lcc_mode_t)2U)
#define PP_LCC_MODE_FOLLOW ((pp_lcc_mode_t)3U)
#define PP_LCC_MODE_COAST ((pp_lcc_mode_t)4U)

#define PP_TRAJECTORY_POINTS (31U)
#define PP_TRAJECTORY_STEP_S (0.1F)
#define PP_TRAJECTORY_HORIZON_S (3.0F)
#define PP_TRAJECTORY_TIMEOUT_US (75000ULL)
typedef uint8_t pp_planner_id_t; /* Planner đã phát message (PP-SWR-019). */
#define PP_PLANNER_ID_LCC ((pp_planner_id_t)0U)
#define PP_PLANNER_ID_LKA_ELK ((pp_planner_id_t)1U)

#define PP_PLANNER_PERIOD_US (25000ULL)
typedef uint8_t pp_init_result_t;
#define PP_INIT_RESULT_OK ((pp_init_result_t)0U)
#define PP_INIT_RESULT_BAD_ARGUMENT ((pp_init_result_t)1U)
#define PP_INIT_RESULT_BAD_VEHICLE_CONFIG ((pp_init_result_t)2U)
#define PP_INIT_RESULT_BAD_CALIBRATION ((pp_init_result_t)3U)

typedef struct {
    uint64_t stamp_us; /* [us]; Thời điểm mà dữ liệu mô tả, theo đồng hồ bên phát (gPTP). */
    uint8_t counter; /* Tăng 1 mỗi lần phát, quay vòng tại 256. */
    bool valid; /* Hiệu lực của toàn message. */
    pp_frame_id_t frame_id; /* BASE_LINK có gốc tại tâm trục sau; x tiến, y trái, z lên. */
} pp_header_t;

/* Header không có frame_id, dùng cho trạng thái, yêu cầu và chassis signals. (ICD 4) */
typedef struct {
    uint64_t stamp_us; /* [us] */
    uint8_t counter;
    bool valid;
} pp_basic_header_t;

typedef struct {
    float x; /* [m] */
    float y; /* [m] */
    float yaw; /* [rad] */
} pp_pose2d_t;

/* IMU_Data đã lọc, chu kỳ 10 ms; stamp lấy lúc nhận. (ICD 5.3) */
typedef struct {
    pp_basic_header_t header;
    float yaw_rate_rps; /* [rad/s] */
    float accel_x_mps2; /* [m/s^2] */
    float accel_y_mps2; /* [m/s^2] */
} pp_imu_signals_t;

/* ImuSignals đã nhận; present = false nếu chưa có message. */
typedef struct {
    bool present;
    uint64_t rx_us; /* [us] Thời điểm nhận theo đồng hồ bên nhận. */
    pp_imu_signals_t message;
} pp_received_imu_signals_t;

/* SAS_Steering chu kỳ 10 ms; dương về trái. (ICD 5.3) */
typedef struct {
    pp_basic_header_t header;
    float steering_wheel_angle_rad; /* [rad] */
    float steering_wheel_rate_rps; /* [rad/s] */
} pp_steering_signals_t;

/* SteeringSignals đã nhận; present = false nếu chưa có message. */
typedef struct {
    bool present;
    uint64_t rx_us; /* [us] Thời điểm nhận theo đồng hồ bên nhận. */
    pp_steering_signals_t message;
} pp_received_steering_signals_t;

/* ESC_Speed chu kỳ 20 ms. (ICD 5.3) */
typedef struct {
    pp_basic_header_t header;
    float speed_mps; /* [m/s] */
    pp_direction_t direction;
} pp_speed_signals_t;

/* SpeedSignals đã nhận; present = false nếu chưa có message. */
typedef struct {
    bool present;
    uint64_t rx_us; /* [us] Thời điểm nhận theo đồng hồ bên nhận. */
    pp_speed_signals_t message;
} pp_received_speed_signals_t;

typedef struct {
    uint64_t t1_us; /* [us] */
    uint64_t t2_us; /* [us] */
} pp_ego_motion_request_t;

/* Chuyển động base_link từ t1 đến t2, có trượt ngang, biểu diễn trong base_link tại t1. (ICD 5.5) */
typedef struct {
    bool valid; /* Có thể là false khi bánh xe bị trượt. */
    float dx; /* [m] */
    float dy; /* [m] */
    float dyaw; /* [rad] */
} pp_ego_motion_response_t;

typedef struct {
    pp_request_state_t state;
    pp_side_t side; /* Phía xe đang lệch. LCC dùng NONE. */
    float tlc; /* [s]; Khối ADAS tính TLC. LCC không dùng giá trị này. */
    pp_elk_reason_t elk_reason; /* ROAD_EDGE chọn mép đường đã quan sát cho ELK. Giá trị khác chỉ dùng ghi log. */
    pp_cancel_reason_t cancel_reason; /* Chỉ dùng ghi log. */
} pp_function_request_t;

typedef struct {
    pp_basic_header_t header; /* stamp_us theo thời điểm phát. */
    pp_function_request_t requests[PP_FUNCTIONS];
    bool driver_override;
} pp_function_requests_t;

/* FunctionRequests đã nhận; present = false nếu chưa có message. */
typedef struct {
    bool present;
    uint64_t rx_us; /* [us] Thời điểm nhận theo đồng hồ bên nhận. */
    pp_function_requests_t message;
} pp_received_function_requests_t;

/* y(x) = c0 + c1 x + c2 x² + c3 x³ trong base_link lúc chụp. (ICD 5.1) */
typedef struct {
    float c0; /* [m] */
    float c1; /* [-] */
    float c2; /* [1/m] */
    float c3; /* [1/m^2] */
    float variance[4]; /* Phương sai theo thứ tự c0 tới c3. */
    float view_range_start; /* [m] */
    float view_range_end; /* [m] */
    float confidence; /* [0..1] */
    pp_line_type_t type;
    bool crossable;
    pp_line_status_t status;
    float predicted_duration; /* [s] */
} pp_lane_line_t;

typedef struct {
    float c0; /* [m] */
    float c1; /* [-] */
    float c2; /* [1/m] */
    float c3; /* [1/m^2] */
    float variance[4];
    float view_range_start; /* [m] */
    float view_range_end; /* [m] */
    float confidence; /* [0..1] */
    pp_road_edge_type_t type;
    pp_line_status_t status;
    float predicted_duration; /* [s] */
} pp_road_edge_t;

typedef struct {
    pp_header_t header; /* stamp_us theo thời điểm chụp. */
    pp_lane_line_t lines[PP_LANE_LINES];
    pp_road_edge_t road_edges[PP_ROAD_EDGES];
    float lane_width; /* [m] */
    pp_lane_width_source_t lane_width_source;
    pp_side_t lane_change; /* Đặt sau khi Lane Model đổi ID vạch theo làn mới. */
} pp_lane_model_t;

/* LaneModel đã nhận; present = false nếu chưa có message. */
typedef struct {
    bool present;
    uint64_t rx_us; /* [us] Thời điểm nhận theo đồng hồ bên nhận. */
    pp_lane_model_t message;
} pp_received_lane_model_t;

/* Tâm xe mục tiêu của ACC, trong base_link lúc đo. header.valid = false khi không có xe mục tiêu. (ICD 5.9) */
typedef struct {
    pp_header_t header;
    uint32_t id; /* Ổn định giữa các frame; dùng để so với LongitudinalPlan.target_id. */
    pp_lead_class_t classification;
    float x; /* [m] */
    float y; /* [m] */
    float gap; /* [m]; Từ cản trước xe ego tới cản sau xe mục tiêu. */
    float heading; /* [rad]; Hướng xe mục tiêu so với trục x của base_link. */
    float vx_rel; /* [m/s]; Vận tốc xe mục tiêu trừ vận tốc ego, chiếu lên trục dọc base_link. */
    float vy_rel; /* [m/s]; Thành phần ngang của vận tốc tương đối trong base_link. */
    float existence_probability; /* [0..1] */
} pp_lead_target_t;

/* LeadTarget đã nhận; present = false nếu chưa có message. */
typedef struct {
    bool present;
    uint64_t rx_us; /* [us] Thời điểm nhận theo đồng hồ bên nhận. */
    pp_lead_target_t message;
} pp_received_lead_target_t;

typedef struct {
    float v; /* [m/s] */
    float a; /* [m/s^2] */
} pp_longitudinal_point_t;

typedef struct {
    pp_header_t header;
    pp_longitudinal_mode_t mode;
    pp_longitudinal_point_t points[PP_LONGITUDINAL_PLAN_POINTS];
    uint32_t target_id; /* 0 khi không có mục tiêu. */
} pp_longitudinal_plan_t;

/* LongitudinalPlan đã nhận; present = false nếu chưa có message. */
typedef struct {
    bool present;
    uint64_t rx_us; /* [us] Thời điểm nhận theo đồng hồ bên nhận. */
    pp_longitudinal_plan_t message;
} pp_received_longitudinal_plan_t;

/* Tâm vật thể trong base_link lúc đo; vận tốc so với mặt đất. (ICD 5.2) */
typedef struct {
    uint32_t id; /* Ổn định giữa các frame. */
    float x; /* [m] */
    float y; /* [m] */
    float vx; /* [m/s] */
    float vy; /* [m/s] */
    float heading; /* [rad]; Góc của vector vận tốc. */
    float length; /* [m] */
    float width; /* [m] */
    float existence_probability; /* [0..1] */
} pp_object_t;

typedef struct {
    pp_header_t header;
    uint8_t num_objects;
    pp_object_t objects[PP_MAX_OBJECTS];
} pp_object_list_t;

/* ObjectList đã nhận; present = false nếu chưa có message. */
typedef struct {
    bool present;
    uint64_t rx_us; /* [us] Thời điểm nhận theo đồng hồ bên nhận. */
    pp_object_list_t message;
} pp_received_object_list_t;

/* Nguồn tham số xe của planner. (ICD 5.8) */
typedef struct {
    float wheelbase; /* [m] */
    float rear_axle_to_cg; /* [m] */
    float vehicle_width; /* [m]; Tính cả gương. */
    float steering_ratio; /* [-] */
    float max_wheel_angle; /* [rad] */
    float max_steering_wheel_rate; /* [rad/s] */
    float actuator_delay; /* [s]; Độ trễ danh định của EPS. */
} pp_vehicle_config_t;

typedef struct {
    pp_header_t header; /* stamp_us theo thời điểm ước lượng. */
    float lateral_velocity; /* [m/s]; v_y tại tâm trục sau. */
    float lateral_velocity_variance; /* [m^2/s^2] */
    float slip_angle; /* [rad] */
} pp_vehicle_state_estimate_t;

/* VehicleStateEstimate đã nhận; present = false nếu chưa có message. */
typedef struct {
    bool present;
    uint64_t rx_us; /* [us] Thời điểm nhận theo đồng hồ bên nhận. */
    pp_vehicle_state_estimate_t message;
} pp_received_vehicle_state_estimate_t;

typedef struct {
    pp_basic_header_t header;
    bool path_valid; /* Đầu vào đủ hợp lệ để dựng path khi có yêu cầu. Cờ có thể true khi chưa can thiệp. */
    pp_intervention_function_t active_function; /* NONE khi thiếu yêu cầu hoặc path_valid là false. */
    pp_intervention_phase_t lka_phase;
    pp_intervention_phase_t elk_phase;
    bool lateral_limit_reached; /* Path bị cắt theo giới hạn a_y hoặc jerk khi LKA/ELK hoạt động. Chỉ dùng ghi log. */
} pp_intervention_status_t;

typedef struct {
    pp_basic_header_t header;
    float v_max; /* [m/s] */
    float distance; /* [m]; Khoảng cách tới điểm có kappa_max. */
    bool lateral_limit_reached; /* Cùng giá trị với LccStatus trong chu kỳ này. */
} pp_lateral_limits_t;

typedef struct {
    pp_basic_header_t header;
    bool path_valid;
    pp_lcc_mode_t lcc_mode; /* NONE khi LCC không ở REQUEST hoặc path_valid là false. */
    float follow_distance; /* [m]; Quãng đường từ đầu FOLLOW, bằng 0 ở mode khác. Chỉ dùng để ghi log và hiển thị. */
    bool lateral_limit_reached;
    bool lane_too_narrow;
} pp_lcc_status_t;

typedef struct {
    float time_from_start; /* [s] */
    pp_pose2d_t pose; /* base_link tại header.stamp_us; yaw là hướng tiếp tuyến của path. */
    float longitudinal_velocity_mps; /* [m/s] */
    float lateral_velocity_mps; /* [m/s]; d_dot theo đường tham chiếu; khác v_y của thân xe. */
    float acceleration_mps2; /* [m/s^2] */
    float heading_rate_rps; /* [rad/s] */
    float curvature; /* [1/m] */
    float front_wheel_angle_rad; /* [rad] */
    float rear_wheel_angle_rad; /* [rad]; Luôn bằng 0. */
} pp_trajectory_point_t;

typedef struct {
    pp_header_t header; /* stamp_us = t0 trong khung BASE_LINK. */
    pp_trajectory_point_t points[PP_TRAJECTORY_POINTS];
    float observed_horizon_s; /* [s]; Thời gian tới lúc path rời phạm vi lane model đã quan sát. Các điểm sau đó được ngoại suy (PP-SWR-018). */
    pp_planner_id_t planner_id;
} pp_trajectory_t;

/* Input LCC: message nhận mới nhất kèm rx_us, hoặc vắng nếu chưa nhận. (ICD 4) */
typedef struct {
    uint64_t t0_us; /* [us] */
    pp_received_lane_model_t lane_model;
    pp_received_object_list_t object_list;
    pp_received_lead_target_t lead_target;
    pp_received_imu_signals_t imu;
    pp_received_steering_signals_t steering;
    pp_received_speed_signals_t speed;
    pp_received_vehicle_state_estimate_t vehicle_state;
    pp_received_function_requests_t function_requests;
    pp_received_longitudinal_plan_t longitudinal_plan;
} pp_lcc_inputs_t;

/* Đầu ra của một chu kỳ LCC, kèm cờ phát riêng cho từng message. (ICD 4) */
typedef struct {
    bool trajectory_sent;
    pp_trajectory_t trajectory;
    bool lcc_status_sent;
    pp_lcc_status_t lcc_status;
    bool lateral_limits_sent;
    pp_lateral_limits_t lateral_limits;
} pp_lcc_outputs_t;

/* Input LKA/ELK: message nhận mới nhất kèm rx_us, hoặc vắng nếu chưa nhận. (ICD 4) */
typedef struct {
    uint64_t t0_us; /* [us] */
    pp_received_lane_model_t lane_model;
    pp_received_imu_signals_t imu;
    pp_received_steering_signals_t steering;
    pp_received_speed_signals_t speed;
    pp_received_vehicle_state_estimate_t vehicle_state;
    pp_received_function_requests_t function_requests;
    pp_received_longitudinal_plan_t longitudinal_plan;
} pp_lka_elk_inputs_t;

/* Đầu ra của một chu kỳ LKA/ELK, kèm cờ phát riêng cho từng message. (ICD 4) */
typedef struct {
    bool trajectory_sent;
    pp_trajectory_t trajectory;
    bool intervention_status_sent;
    pp_intervention_status_t intervention_status;
} pp_lka_elk_outputs_t;

#ifdef __cplusplus
}
#endif

#endif

#ifndef PP_FEASIBILITY_H
#define PP_FEASIBILITY_H

#include <stdbool.h>
#include <stdint.h>

#include "pp_calibration.h"
#include "pp_path.h"
#include "pp_types.h"
#include "reference_line.h"

#define PP_AYSMAX (2.5)  /* [m/s²] Theo PP-SWR-001 và R79 5.6.2.1.3. */
#define PP_JERK_MAX_HWA (5.0)  /* [m/s³] Theo PP-SWR-003 và R79 5.6.2.1.3 c. */
#define PP_AY_MAX_LKA (3.0)
#define PP_AY_MAX_ELK (4.0)
#define PP_AY_ADD_MAX_LKA (1.5)
#define PP_AY_ADD_MAX_ELK (3.0)
#define PP_JERK_MAX_LKA (5.0)
#define PP_JERK_MAX_ELK (10.0)
#define PP_JERK_WINDOW_S (0.5)

typedef struct {
    double ay_max;
    double jerk_max;
    double ay_add_max;
    double ay_support;  /* [m/s²] Trợ giúp yêu cầu khi cua gắt; 0 tắt trợ giúp. */
} pp_function_limits_t;

/* HWA dùng aysmax + ay_margin_hwa. Khi limit_reached, chỉ dùng aysmax (PP-TS-020). */
pp_function_limits_t pp_hwa_path_limits(const pp_calibration_t *cal, bool limit_reached);

typedef struct {
    double ay_max;
    double ay_add_max;
    double jerk_max;
    double ay_need_max;
} pp_path_check_t;

void pp_feasibility_check(const pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],
                          const pp_ref_samples_t *ref, pp_path_check_t *out);

/* Giới hạn độ cong theo chức năng và VehicleConfig. Tích phân lại từ điểm trước chỗ cắt, giữ pose
 * điểm 0. */
bool pp_feasibility_limit(pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],
                          const pp_ref_samples_t *ref, const pp_function_limits_t *limits,
                          const pp_vehicle_config_t *vehicle);

typedef struct {
    bool reached;
    uint8_t on_cycles;
    uint8_t off_cycles;
} pp_limit_flag_t;

void pp_limit_flag_reset(pp_limit_flag_t *flag);
void pp_limit_flag_update(pp_limit_flag_t *flag, double ay_need_max, double ay_limit,
                          const pp_calibration_t *cal, double cycle_s);

typedef struct {
    double kappa_max;
    double distance;
    double v_max;
} pp_curve_limit_t;

void pp_curve_limit(const pp_reference_line_t *ref, double ay_limit, pp_curve_limit_t *out);

/* Cờ giới hạn và LateralLimits lấy độ cong cần lớn hơn giữa đường camera và ước lượng T5 trong tầm
 * nhìn. */
double pp_ay_need_max(const pp_reference_line_t *ref, const pp_speed_profile_t *speed);

#endif

/*
 * T10 Feasibility and limits (Software Detailed Design section 13; Software Architectural
 * Design section 9).
 *
 * Hard limits are only those of the requirements: a_y and jerk of the function that
 * drives (PP-SWR-001, 003) and wheel angle and steering wheel rate of VehicleConfig
 * (PP-SWR-116, 117). ay_add_max_hwa and jerk_target_hwa are targets that T7 meets by a
 * longer duration, not limits cut here. Only HWA limits exist so far; the curvature of
 * the reference line stands in for T5 Curvature fusion.
 */

#ifndef PP_FEASIBILITY_H
#define PP_FEASIBILITY_H

#include <stdbool.h>
#include <stdint.h>

#include "pp_calibration.h"
#include "pp_path.h"
#include "pp_types.h"
#include "reference_line.h"

#define PP_AYSMAX (2.5)                /* [m/s^2] PP-SWR-001, R79 5.6.2.1.3 */
#define PP_JERK_MAX_HWA (5.0)          /* [m/s^3] PP-SWR-003, R79 5.6.2.1.3 c */
#define PP_JERK_WINDOW_S (0.5)         /* Software Requirements Specification 4 */

typedef struct {
    double ay_max;                     /* [m/s^2] */
    double jerk_max;                   /* [m/s^3] */
} pp_function_limits_t;

/* Step 1 on the 31 points. */
typedef struct {
    double ay_max;                     /* Largest |a_y| of the path */
    double ay_add_max;                 /* Largest |a_y - v^2 kappa_ref| */
    double jerk_max;                   /* Largest |jerk|, moving mean over 0.5 s */
    double ay_need_max;                /* Largest |v^2 kappa_ref| within the view range */
} pp_path_check_t;

void pp_feasibility_check(const pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],
                          const pp_ref_samples_t *ref, pp_path_check_t *out);

/*
 * Step 2: cuts the curvature to the limits of the function and of VehicleConfig, point
 * by point from the start, and integrates the path again from the first changed point.
 * Point 0 keeps its pose. Returns true when the path changed.
 */
bool pp_feasibility_limit(pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],
                          const pp_ref_samples_t *ref, const pp_function_limits_t *limits,
                          const pp_vehicle_config_t *vehicle);

/* Step 3: lateral_limit_reached with hysteresis delta_ay and confirmation T_flag / 2. */
typedef struct {
    bool reached;
    uint8_t on_cycles;
    uint8_t off_cycles;
} pp_limit_flag_t;

void pp_limit_flag_reset(pp_limit_flag_t *flag);
void pp_limit_flag_update(pp_limit_flag_t *flag, double ay_need_max, double ay_limit,
                          const pp_calibration_t *cal, double cycle_s);

/*
 * Step 4: largest |kappa| of the reference line within the view range (every 2 m, the
 * grid of T5), its distance, and v_max = sqrt(ay_limit / kappa_max).
 */
typedef struct {
    double kappa_max;
    double distance;                   /* [m] along the reference line */
    double v_max;                      /* [m/s] */
} pp_curve_limit_t;

void pp_curve_limit(const pp_reference_line_t *ref, double ay_limit, pp_curve_limit_t *out);

/*
 * Largest v^2 |kappa| of a reference line along the path's s(t), within its observed
 * range. The flag and LateralLimits take the larger of the camera reference line and
 * the T5-fused one: they warn the longitudinal block, so the safe side is used.
 */
double pp_ay_need_max(const pp_reference_line_t *ref, const pp_speed_profile_t *speed);

#endif /* PP_FEASIBILITY_H */

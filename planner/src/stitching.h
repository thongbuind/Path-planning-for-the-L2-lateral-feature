#ifndef PP_STITCHING_H
#define PP_STITCHING_H

#include <stdbool.h>
#include <stdint.h>

#include "lateral_state.h"
#include "pp_calibration.h"
#include "pp_planner.h"
#include "reference_line.h"

/* Cùng một lambda dùng cho toàn path; từng điểm vẫn được so với giới hạn của khoảng thời gian
 * tương ứng. */
#define PP_CONT_LATERAL_M (0.05)
#define PP_CONT_HEADING_RAD (0.005)
#define PP_CONT_CURVATURE (0.0003)
#define PP_CONT_BAND_1_2_S (2.0)
#define PP_CONT_BAND_AFTER_2_S (4.0)

typedef struct {
    bool valid;
    uint64_t t0_us;
    pp_trajectory_point_t points[PP_TRAJECTORY_POINTS];
} pp_previous_path_t;

typedef struct {
    bool valid;
    double shift_s;
    double x[PP_TRAJECTORY_POINTS];
    double y[PP_TRAJECTORY_POINTS];
    double yaw[PP_TRAJECTORY_POINTS];
    double kappa[PP_TRAJECTORY_POINTS];
    double v[PP_TRAJECTORY_POINTS];
    double a[PP_TRAJECTORY_POINTS];
    double d_dot[PP_TRAJECTORY_POINTS];
} pp_old_path_t;

typedef struct {
    double x;
    double y;
    double yaw;
    double kappa;
    double v;
    double a;
    double d_dot;
} pp_path_sample_t;

void pp_stitch_remember(pp_previous_path_t *prev, uint64_t t0_us, bool valid,
                        const pp_trajectory_point_t points[PP_TRAJECTORY_POINTS]);

/* Thiếu path cũ, quá timeout hoặc thiếu ego-motion đều khiến trạng thái stitch không hợp lệ. */
void pp_stitch_move_old(const pp_previous_path_t *prev, uint64_t t0_us,
                        pp_ego_motion_fn ego_motion, void *context, pp_old_path_t *out);

bool pp_stitch_sample_old(const pp_old_path_t *old, double t, pp_path_sample_t *out);

bool pp_stitch_start(const pp_old_path_t *old, const pp_reference_line_t *ref,
                     const pp_lateral_state_t *measured, const pp_calibration_t *cal,
                     pp_lateral_state_t *start);

/* Trọng số trạng thái đo là 0 tới soft_min, 1 từ reset, tuyến tính ở giữa. Khi reset <= soft_min
 * thì dùng ngưỡng cứng. */
double pp_stitch_soft_weight(double deviation, double soft_min, double reset);

/* Tính lambda từ lệch ngang, hướng và độ cong trên khoảng thời gian chung, chỉ xét điểm trong tầm
 * nhìn. */
double pp_stitch_blend(const pp_old_path_t *old, const pp_calibration_t *cal, double wheelbase,
                       double x_limit,
                       pp_trajectory_point_t points[PP_TRAJECTORY_POINTS]);

#endif

#ifndef PP_PATH_H
#define PP_PATH_H

#include <stdbool.h>

#include "pp_types.h"

/* Lấy bước lưới từ các hằng số chính xác. 0.1F có sai số khi nâng lên double. */
#define PP_GRID_STEP_S ((double)PP_TRAJECTORY_HORIZON_S / (double)(PP_TRAJECTORY_POINTS - 1U))

typedef struct {
    double v[PP_TRAJECTORY_POINTS];
    double a[PP_TRAJECTORY_POINTS];
    double s[PP_TRAJECTORY_POINTS];
} pp_speed_profile_t;

typedef struct {
    double d[PP_TRAJECTORY_POINTS];
    double d_dot[PP_TRAJECTORY_POINTS];
    double d_ddot[PP_TRAJECTORY_POINTS];
} pp_lateral_path_t;

/* T11 lấy mẫu đường tham chiếu tại từng điểm của Trajectory để T7 và T10 dùng. */
typedef struct {
    double kappa[PP_TRAJECTORY_POINTS];
    double theta[PP_TRAJECTORY_POINTS];
    bool in_view[PP_TRAJECTORY_POINTS];
} pp_ref_samples_t;

#endif

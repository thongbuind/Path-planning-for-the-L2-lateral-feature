/* Path data shared by T7 Path generation and T11 Output, on the 0.1 s Trajectory grid. */

#ifndef PP_PATH_H
#define PP_PATH_H

#include <stdbool.h>

#include "pp_types.h"

/* Grid step in double, from exact constants (0.1F itself is not exact). */
#define PP_GRID_STEP_S ((double)PP_TRAJECTORY_HORIZON_S / (double)(PP_TRAJECTORY_POINTS - 1U))

/* v(t), a(t) and s(t) = integral of v (Software Detailed Design section 3). */
typedef struct {
    double v[PP_TRAJECTORY_POINTS];
    double a[PP_TRAJECTORY_POINTS];
    double s[PP_TRAJECTORY_POINTS];
} pp_speed_profile_t;

/* d(t) and its time derivatives against the reference line. */
typedef struct {
    double d[PP_TRAJECTORY_POINTS];
    double d_dot[PP_TRAJECTORY_POINTS];
    double d_ddot[PP_TRAJECTORY_POINTS];
} pp_lateral_path_t;

/* Reference line under each Trajectory point (from T11), for T7 and T10. */
typedef struct {
    double kappa[PP_TRAJECTORY_POINTS];      /* [1/m] */
    double theta[PP_TRAJECTORY_POINTS];      /* [rad] tangent heading */
    bool in_view[PP_TRAJECTORY_POINTS];      /* Within the observed range of the lane model */
} pp_ref_samples_t;

#endif /* PP_PATH_H */

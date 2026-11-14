/*
 * T6 Lateral state (Software Detailed Design section 9). Planner's own computation,
 * not shared with the ADAS function block (PP-ADR-014).
 *
 * The state is taken at the base_link origin, because the Trajectory describes
 * base_link poses (Interface Control Document 6.1). DLC and TLC are not needed yet.
 */

#ifndef PP_LATERAL_STATE_H
#define PP_LATERAL_STATE_H

#include "reference_line.h"

typedef struct {
    double d;                     /* [m] lateral offset from the reference line, left positive */
    double d_dot;                 /* [m/s] */
    double d_ddot;                /* [m/s^2] */
    double heading;               /* [rad] vehicle heading relative to the reference line */
} pp_lateral_state_t;

/*
 * foot: reference point at s = 0 (pp_ref_walk_begin). v: speed, v_y: lateral velocity
 * at base_link, yaw_rate: from the IMU.
 */
void pp_lateral_state(const pp_ref_point_t *foot, double v, double v_y, double yaw_rate,
                      pp_lateral_state_t *out);

#endif /* PP_LATERAL_STATE_H */

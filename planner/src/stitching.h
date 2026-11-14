/*
 * T4 Stitching and continuity (Software Detailed Design section 7; PP-ADR-004).
 *
 * Implemented: steps 1 to 5 for HWA. The LKA and ELK start case of step 2 and
 * step 5 (PP-SWR-031, 080) comes with those functions.
 */

#ifndef PP_STITCHING_H
#define PP_STITCHING_H

#include <stdbool.h>
#include <stdint.h>

#include "lateral_state.h"
#include "pp_calibration.h"
#include "pp_planner.h"
#include "reference_line.h"

/* Continuity limits between two consecutive paths. */
#define PP_CONT_LATERAL_M (0.05)       /* PP-SWR-100 */
#define PP_CONT_HEADING_RAD (0.005)    /* PP-SWR-101 */
#define PP_CONT_CURVATURE (0.0003)     /* PP-SWR-102 */

/* Path sent in the previous cycle, kept in the state. */
typedef struct {
    bool valid;
    uint64_t t0_us;
    pp_trajectory_point_t points[PP_TRAJECTORY_POINTS];
} pp_previous_path_t;

/* Previous path moved to base_link at the new t0 (step 1). */
typedef struct {
    bool valid;
    double shift_s;                       /* New t0 minus old t0 [s] */
    double x[PP_TRAJECTORY_POINTS];
    double y[PP_TRAJECTORY_POINTS];
    double yaw[PP_TRAJECTORY_POINTS];
    double kappa[PP_TRAJECTORY_POINTS];
    double v[PP_TRAJECTORY_POINTS];
    double a[PP_TRAJECTORY_POINTS];
    double d_dot[PP_TRAJECTORY_POINTS];
} pp_old_path_t;

/* Old path at a time after the new t0. */
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

/*
 * Step 1. Not valid when there is no previous path, it is older than the Trajectory
 * timeout (Interface Control Document 6.1), or ego-motion is not available.
 */
void pp_stitch_move_old(const pp_previous_path_t *prev, uint64_t t0_us,
                        pp_ego_motion_fn ego_motion, void *context, pp_old_path_t *out);

/* Between points: position by cubic Hermite along the headings, other values linear in
 * time; beyond the old horizon along a circular arc. Returns false when t lies beyond
 * the old horizon. */
bool pp_stitch_sample_old(const pp_old_path_t *old, double t, pp_path_sample_t *out);

/*
 * Step 2: start state from the old path at t0, against the new reference line. When it
 * is more than stitch_reset away from the measured state, the measured one is used.
 * Returns true when the old path gave the start state.
 */
bool pp_stitch_start(const pp_old_path_t *old, const pp_reference_line_t *ref,
                     const pp_lateral_state_t *measured, const pp_calibration_t *cal,
                     pp_lateral_state_t *start);

/*
 * Step 4: sent path = old + lambda (candidate - old), lambda from the largest lateral,
 * heading and curvature difference on the common time span, at the points with x <= x_limit
 * (end of the lane model view range; INFINITY while coasting). Changes `points` in place
 * and returns lambda; 1 when the old path is not valid (step 5).
 */
double pp_stitch_blend(const pp_old_path_t *old, const pp_calibration_t *cal, double wheelbase,
                       double x_limit,
                       pp_trajectory_point_t points[PP_TRAJECTORY_POINTS]);

#endif /* PP_STITCHING_H */

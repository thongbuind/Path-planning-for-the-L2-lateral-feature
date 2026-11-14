/*
 * T11 Output (Software Detailed Design section 14): speed profile, Frenet to
 * Cartesian conversion and the 31 Trajectory points. Front wheel angle as in T10
 * step 1; limits of T10 are not applied yet.
 */

#ifndef PP_OUTPUT_H
#define PP_OUTPUT_H

#include <stdint.h>

#include "pp_path.h"
#include "pp_types.h"
#include "reference_line.h"

/*
 * v(t), a(t) from LongitudinalPlan, shifted from its stamp to t0. plan NULL: current
 * speed and zero acceleration (Interface Control Document 6.1; PP-SWR-153, 154).
 */
void pp_speed_profile(const pp_longitudinal_plan_t *plan, uint64_t t0_us, double speed,
                      pp_speed_profile_t *out);

/*
 * (s, d) to (x, y, yaw, kappa) in base_link at t0 (Werling et al. 2010). `samples`
 * (may be NULL) receives the reference line under each point. False if a point cannot
 * be represented by finite float32 interface values.
 */
bool pp_output_points(const pp_reference_line_t *ref, const pp_lateral_path_t *path,
                      const pp_speed_profile_t *speed, double wheelbase,
                      pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],
                      pp_ref_samples_t *samples);

/* Time grid only, for a Trajectory that is sent with header.valid = false. */
void pp_output_empty_points(pp_trajectory_point_t points[PP_TRAJECTORY_POINTS]);

#endif /* PP_OUTPUT_H */

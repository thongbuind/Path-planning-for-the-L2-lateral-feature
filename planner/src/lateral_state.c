/* T6 Lateral state (lateral_state.h). */

#include "lateral_state.h"

#include <math.h>

void pp_lateral_state(const pp_ref_point_t *foot, double v, double v_y, double yaw_rate,
                      pp_lateral_state_t *out)
{
    const double c = cos(foot->theta);
    const double s = sin(foot->theta);
    /* Origin relative to the foot, along the reference normal (-sin, cos). */
    out->d = (foot->x * s) - (foot->y * c);
    /* Vehicle heading is 0 in base_link. */
    out->heading = -foot->theta;
    out->d_dot = (v * sin(out->heading)) + (v_y * cos(out->heading));
    /* d_ddot = v * d(heading)/dt, with d(heading)/dt = r - s_dot * kappa_ref. */
    const double q = 1.0 - (foot->kappa * out->d);
    const double s_dot = (q > 0.0) ? ((v * cos(out->heading)) / q) : v;
    out->d_ddot = v * cos(out->heading) * (yaw_rate - (s_dot * foot->kappa));
}

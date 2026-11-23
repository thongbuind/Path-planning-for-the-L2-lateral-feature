#include <math.h>
#include <stddef.h>

#include "driver_shape.h"

bool lab_driver_bump(const pp_lateral_path_t *base, double end, double peak, double offset, double corridor,
                     pp_lateral_path_t *out)
{
    bool ok = (base != NULL) && (out != NULL) && (peak > 0.0) && (end > peak) && isfinite(offset)
              && (corridor > 0.0);
    if (ok) {
        *out = *base;
        for (size_t k = 0U; ok && (k < PP_TRAJECTORY_POINTS); k++) {
            const double t = (double)k * PP_GRID_STEP_S;
            if (t <= end) {
                const bool rising = t <= peak;
                const double duration = rising ? peak : (end - peak);
                const double du_dt = (rising ? 1.0 : -1.0) / duration;
                const double u = rising ? (t / duration) : ((end - t) / duration);
                const double v = 1.0 - u;
                const double u2 = u * u;
                const double v2 = v * v;
                /* s(u) = 35u⁴ − 84u⁵ + 70u⁶ − 20u⁷; s' = 140u³v³; s'' = 420u²v²(1 − 2u). */
                out->d[k] += offset * u2 * u2 * (35.0 + (u * (-84.0 + (u * (70.0 - (20.0 * u))))));
                out->d_dot[k] += offset * 140.0 * u2 * u * v2 * v * du_dt;
                out->d_ddot[k] += offset * 420.0 * u2 * v2 * (1.0 - (2.0 * u)) * du_dt * du_dt;
                ok = fabs(out->d[k]) <= corridor;
            }
        }
    }
    return ok;
}

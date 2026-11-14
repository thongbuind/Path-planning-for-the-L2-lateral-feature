/* T7 Path generation, technique A (quintic.h). */

#include "quintic.h"

#include <string.h>

bool pp_quintic_solve(double d0, double v0, double a0, double d1, double duration,
                      pp_quintic_t *out)
{
    const double T = duration;
    bool ok = T > 0.0;
    (void)memset(out, 0, sizeof(*out));
    if (ok) {
        const double T2 = T * T;
        const double T3 = T2 * T;
        /* Remaining position, velocity and acceleration to reach (d1, 0, 0). */
        const double h = d1 - (d0 + (v0 * T) + (0.5 * a0 * T2));
        const double dv = -(v0 + (a0 * T));
        const double da = -a0;
        out->a[0] = d0;
        out->a[1] = v0;
        out->a[2] = 0.5 * a0;
        out->a[3] = ((10.0 * h) - (4.0 * dv * T) + (0.5 * da * T2)) / T3;
        out->a[4] = ((-15.0 * h) + (7.0 * dv * T) - (da * T2)) / (T3 * T);
        out->a[5] = ((6.0 * h) - (3.0 * dv * T) + (0.5 * da * T2)) / (T3 * T2);
        out->duration = T;
    }
    return ok;
}

void pp_quintic_eval(const pp_quintic_t *q, double t, double *d, double *d_dot,
                     double *d_ddot)
{
    const double tc = (t < q->duration) ? t : q->duration;
    const double *a = q->a;
    *d = a[0] + (tc * (a[1] + (tc * (a[2] + (tc * (a[3] + (tc * (a[4] + (tc * a[5])))))))));
    *d_dot = a[1] + (tc * ((2.0 * a[2]) + (tc * ((3.0 * a[3]) + (tc * ((4.0 * a[4])
             + (tc * 5.0 * a[5])))))));
    *d_ddot = (2.0 * a[2]) + (tc * ((6.0 * a[3]) + (tc * ((12.0 * a[4]) + (tc * 20.0 * a[5])))));
    if (t >= q->duration) {
        /* End state is (d1, 0, 0): hold it. */
        *d_dot = 0.0;
        *d_ddot = 0.0;
    }
}

bool pp_generate_quintic(const pp_lateral_state_t *start, double d_target, double duration,
                         pp_lateral_path_t *out)
{
    pp_quintic_t q;
    const bool ok = pp_quintic_solve(start->d, start->d_dot, start->d_ddot, d_target,
                                     duration, &q);
    (void)memset(out, 0, sizeof(*out));
    if (ok) {
        for (uint32_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
            const double t = (double)k * PP_GRID_STEP_S;
            pp_quintic_eval(&q, t, &out->d[k], &out->d_dot[k], &out->d_ddot[k]);
        }
    }
    return ok;
}

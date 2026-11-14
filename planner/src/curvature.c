/* T5 Curvature fusion (curvature.h). PP-SWR-125. */

#include "curvature.h"

#include <math.h>
#include <string.h>

#define PP_YAW_MIN_SPEED_MPS (5.0)     /* Software Detailed Design 8 */
#define PP_OUTLIER_WEIGHT (0.1)        /* "giảm trọng số đi 10 lần" */

void pp_curvature_reset(pp_curvature_t *c)
{
    (void)memset(c, 0, sizeof(*c));
}

void pp_curvature_predict(pp_curvature_t *c, double ds, const pp_calibration_t *cal)
{
    pp_curvature_t old = *c;
    const double shift = ds / PP_KAPPA_STEP_M;
    const double q = (double)cal->q_kappa * fabs(ds);

    for (uint32_t i = 0U; i < PP_KAPPA_POINTS; i++) {
        const double src = (double)i + shift;      /* Point i now was at src before */
        c->valid[i] = false;
        if ((src >= 0.0) && (src <= (double)(PP_KAPPA_POINTS - 1U))) {
            const uint32_t j = (uint32_t)floor(src);
            const uint32_t k = (j + 1U < PP_KAPPA_POINTS) ? (j + 1U) : j;
            if (old.valid[j] && old.valid[k]) {
                const double f = src - (double)j;
                c->kappa[i] = old.kappa[j] + (f * (old.kappa[k] - old.kappa[j]));
                c->var[i] = fmax(old.var[j], old.var[k]) + q;
                c->valid[i] = true;
            }
        }
    }
}

static void update_point(pp_curvature_t *c, uint32_t i, double z, double r,
                         const pp_calibration_t *cal)
{
    if (!c->valid[i]) {
        c->kappa[i] = z;
        c->var[i] = r;
        c->valid[i] = true;
    } else {
        const double innovation = z - c->kappa[i];
        const double total = c->var[i] + r;
        const double limit = (double)cal->k_jump;
        double gain = c->var[i] / total;
        if ((innovation * innovation) > (limit * limit * total)) {
            gain *= PP_OUTLIER_WEIGHT;              /* still follows a real curve, slowly */
        }
        c->kappa[i] += gain * innovation;
        c->var[i] *= (1.0 - gain);
    }
}

void pp_curvature_update_camera(pp_curvature_t *c, const pp_cubic_t *centre, double var_c2,
                                double var_c3, double x_start, double x_end,
                                const pp_calibration_t *cal)
{
    const double floor_var = (double)cal->sigma_kappa_min * (double)cal->sigma_kappa_min;
    for (uint32_t i = 0U; i < PP_KAPPA_POINTS; i++) {
        const double x = (double)i * PP_KAPPA_STEP_M;
        if ((x >= x_start) && (x <= x_end)) {
            const double z = (2.0 * centre->c[2]) + (6.0 * centre->c[3] * x);
            const double r = fmax((4.0 * var_c2) + (36.0 * x * x * var_c3), floor_var);
            update_point(c, i, z, r, cal);
        }
    }
}

void pp_curvature_update_yaw(pp_curvature_t *c, double yaw_rate, double v,
                             const pp_calibration_t *cal)
{
    if (v > PP_YAW_MIN_SPEED_MPS) {
        const double sigma = (double)cal->sigma_r / v;
        update_point(c, 0U, yaw_rate / v, sigma * sigma, cal);
    }
}

bool pp_curvature_fit(const pp_curvature_t *c, double x_end, double *c2, double *c3)
{
    double sw = 0.0;
    double sx = 0.0;
    double sxx = 0.0;
    double sy = 0.0;
    double sxy = 0.0;
    uint32_t n = 0U;
    for (uint32_t i = 0U; i < PP_KAPPA_POINTS; i++) {
        const double x = (double)i * PP_KAPPA_STEP_M;
        if (c->valid[i] && (x <= x_end) && (c->var[i] > 0.0)) {
            const double w = 1.0 / c->var[i];
            sw += w;
            sx += w * x;
            sxx += w * x * x;
            sy += w * c->kappa[i];
            sxy += w * x * c->kappa[i];
            n++;
        }
    }
    const double det = (sw * sxx) - (sx * sx);
    const bool ok = (n >= 2U) && (fabs(det) > (1.0e-12 * sw * sxx));
    if (ok) {
        const double b = ((sw * sxy) - (sx * sy)) / det;
        const double a = (sy - (b * sx)) / sw;
        *c2 = 0.5 * a;
        *c3 = b / 6.0;
    }
    return ok;
}

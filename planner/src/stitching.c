/* T4 Stitching and continuity (stitching.h). PP-SWR-100 to 102. */

#include "stitching.h"

#include <math.h>
#include <string.h>

#include "pp_math.h"
#include "pp_path.h"

#define PP_US_PER_S (1.0e6)
#define PP_STRAIGHT_KAPPA (1.0e-9)
#define PP_MIN_Q (0.1)                /* Smallest 1 - kappa_ref d, as in T11 */

static double wrap_angle(double angle)
{
    return atan2(sin(angle), cos(angle));
}

void pp_stitch_remember(pp_previous_path_t *prev, uint64_t t0_us, bool valid,
                        const pp_trajectory_point_t points[PP_TRAJECTORY_POINTS])
{
    prev->valid = valid;
    prev->t0_us = t0_us;
    (void)memcpy(prev->points, points, sizeof(prev->points));
}

void pp_stitch_move_old(const pp_previous_path_t *prev, uint64_t t0_us,
                        pp_ego_motion_fn ego_motion, void *context, pp_old_path_t *out)
{
    (void)memset(out, 0, sizeof(*out));
    bool ok = prev->valid && (ego_motion != NULL) && (prev->t0_us < t0_us)
              && ((t0_us - prev->t0_us) <= PP_TRAJECTORY_TIMEOUT_US);
    pp_ego_motion_response_t motion;
    (void)memset(&motion, 0, sizeof(motion));
    if (ok) {
        const pp_ego_motion_request_t request = {prev->t0_us, t0_us};
        ego_motion(context, &request, &motion);
        ok = motion.valid && (isfinite(motion.dx) != 0) && (isfinite(motion.dy) != 0)
             && (isfinite(motion.dyaw) != 0);
    }
    if (ok) {
        const double dx = (double)motion.dx;
        const double dy = (double)motion.dy;
        const double dyaw = (double)motion.dyaw;
        const double c = cos(dyaw);
        const double s = sin(dyaw);
        out->shift_s = (double)(t0_us - prev->t0_us) / PP_US_PER_S;
        for (uint32_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
            const pp_trajectory_point_t *p = &prev->points[k];
            const double px = (double)p->pose.x - dx;
            const double py = (double)p->pose.y - dy;
            out->x[k] = (c * px) + (s * py);              /* p_new = R(-dyaw) (p_old - d) */
            out->y[k] = (-s * px) + (c * py);
            out->yaw[k] = wrap_angle((double)p->pose.yaw - dyaw);
            out->kappa[k] = (double)p->curvature;
            out->v[k] = (double)p->longitudinal_velocity_mps;
            out->a[k] = (double)p->acceleration_mps2;
            out->d_dot[k] = (double)p->lateral_velocity_mps;
        }
        out->valid = true;
    }
}

bool pp_stitch_sample_old(const pp_old_path_t *old, double t, pp_path_sample_t *out)
{
    const double tau = t + old->shift_s;                  /* Time on the old path */
    const double last = (double)(PP_TRAJECTORY_POINTS - 1U);
    const double index = tau / PP_GRID_STEP_S;
    const bool inside = index <= (last + 1.0e-9);

    if (inside) {
        const double clamped = pp_clamp(index, 0.0, last);
        uint32_t i = (uint32_t)floor(clamped);
        if (i >= (PP_TRAJECTORY_POINTS - 1U)) {
            i = PP_TRAJECTORY_POINTS - 2U;
        }
        const uint32_t j = i + 1U;
        const double f = clamped - (double)i;
        /*
         * Cubic Hermite on position with the heading as tangent. A straight chord lies
         * inside a curve (kappa L^2 f (1 - f) / 2, 0.6 mm at R = 1000 m) and would pull
         * every stitched start inwards (Software Detailed Design 7, step 2).
         */
        const double chord = hypot(old->x[j] - old->x[i], old->y[j] - old->y[i]);
        const double f2 = f * f;
        const double f3 = f2 * f;
        const double h00 = (2.0 * f3) - (3.0 * f2) + 1.0;
        const double h10 = f3 - (2.0 * f2) + f;
        const double h01 = (-2.0 * f3) + (3.0 * f2);
        const double h11 = f3 - f2;
        out->x = (h00 * old->x[i]) + (h10 * chord * cos(old->yaw[i]))
                 + (h01 * old->x[j]) + (h11 * chord * cos(old->yaw[j]));
        out->y = (h00 * old->y[i]) + (h10 * chord * sin(old->yaw[i]))
                 + (h01 * old->y[j]) + (h11 * chord * sin(old->yaw[j]));
        out->yaw = wrap_angle(old->yaw[i] + (f * wrap_angle(old->yaw[j] - old->yaw[i])));
        out->kappa = old->kappa[i] + (f * (old->kappa[j] - old->kappa[i]));
        out->v = old->v[i] + (f * (old->v[j] - old->v[i]));
        out->a = old->a[i] + (f * (old->a[j] - old->a[i]));
        out->d_dot = old->d_dot[i] + (f * (old->d_dot[j] - old->d_dot[i]));
    } else {
        /* Beyond the old horizon: continue along the arc of the last point. */
        const uint32_t n = PP_TRAJECTORY_POINTS - 1U;
        const double length = old->v[n] * ((index - last) * PP_GRID_STEP_S);
        const double k = old->kappa[n];
        const double yaw = old->yaw[n] + (k * length);
        if (fabs(k) > PP_STRAIGHT_KAPPA) {
            out->x = old->x[n] + ((sin(yaw) - sin(old->yaw[n])) / k);
            out->y = old->y[n] - ((cos(yaw) - cos(old->yaw[n])) / k);
        } else {
            out->x = old->x[n] + (length * cos(old->yaw[n]));
            out->y = old->y[n] + (length * sin(old->yaw[n]));
        }
        out->yaw = wrap_angle(yaw);
        out->kappa = k;
        out->v = old->v[n];
        out->a = 0.0;
        out->d_dot = old->d_dot[n];
    }
    return inside;
}

bool pp_stitch_start(const pp_old_path_t *old, const pp_reference_line_t *ref,
                     const pp_lateral_state_t *measured, const pp_calibration_t *cal,
                     pp_lateral_state_t *start)
{
    bool from_old = false;
    *start = *measured;

    if (old->valid) {
        pp_path_sample_t p;
        pp_ref_point_t foot;
        double d = 0.0;
        (void)pp_stitch_sample_old(old, 0.0, &p);
        pp_ref_project(ref, p.x, p.y, &foot, &d);

        /* Cartesian to Frenet (Werling et al. 2010). */
        const double dtheta = wrap_angle(p.yaw - foot.theta);
        const double q = fmax(1.0 - (foot.kappa * d), PP_MIN_Q);
        const double c = cos(dtheta);
        const double t = tan(dtheta);
        const double d1 = q * t;                                         /* dd/ds */
        const double d2 = (-((foot.dkappa * d) + (foot.kappa * d1)) * t)
                          + ((q / (c * c)) * (((p.kappa * q) / c) - foot.kappa)); /* d2d/ds2 */
        const double s_dot = (p.v * c) / q;
        if (fabs(d - measured->d) <= (double)cal->stitch_reset) {
            start->d = d;
            start->d_dot = d1 * s_dot;
            start->d_ddot = (d2 * s_dot * s_dot) + (d1 * p.a);
            start->heading = dtheta;
            from_old = true;
        }
    }
    return from_old;
}

static void blend_point(pp_trajectory_point_t *c, const pp_path_sample_t *o, double lambda,
                        double wheelbase)
{
    const double kappa = o->kappa + (lambda * ((double)c->curvature - o->kappa));
    c->pose.x = (float)(o->x + (lambda * ((double)c->pose.x - o->x)));
    c->pose.y = (float)(o->y + (lambda * ((double)c->pose.y - o->y)));
    c->pose.yaw = (float)wrap_angle(o->yaw + (lambda * wrap_angle((double)c->pose.yaw - o->yaw)));
    c->lateral_velocity_mps = (float)(o->d_dot + (lambda * ((double)c->lateral_velocity_mps - o->d_dot)));
    c->curvature = (float)kappa;
    c->heading_rate_rps = (float)((double)c->longitudinal_velocity_mps * kappa);
    c->front_wheel_angle_rad = (float)atan(wheelbase * kappa);
}

double pp_stitch_blend(const pp_old_path_t *old, const pp_calibration_t *cal, double wheelbase,
                       double x_limit, pp_trajectory_point_t points[PP_TRAJECTORY_POINTS])
{
    double lambda = 1.0;

    if (old->valid) {
        pp_path_sample_t samples[PP_TRAJECTORY_POINTS];
        double lateral = 0.0;
        double heading = 0.0;
        double curvature = 0.0;

        for (uint32_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
            const pp_trajectory_point_t *c = &points[k];
            const bool common = pp_stitch_sample_old(old, (double)k * PP_GRID_STEP_S, &samples[k]);
            /* PP-SWR-100 to 102 hold within the lane model view range (SRS 4). */
            if (common && ((double)c->pose.x <= x_limit)) {
                const pp_path_sample_t *o = &samples[k];
                const double yaw = (double)c->pose.yaw;
                const double ex = o->x - (double)c->pose.x;
                const double ey = o->y - (double)c->pose.y;
                lateral = fmax(lateral, fabs((-sin(yaw) * ex) + (cos(yaw) * ey)));
                heading = fmax(heading, fabs(wrap_angle(yaw - o->yaw)));
                curvature = fmax(curvature, fabs((double)c->curvature - o->kappa));
            }
        }

        const double margin = (double)cal->cont_margin;
        if (lateral > 0.0) {
            lambda = fmin(lambda, (margin * PP_CONT_LATERAL_M) / lateral);
        }
        if (heading > 0.0) {
            lambda = fmin(lambda, (margin * PP_CONT_HEADING_RAD) / heading);
        }
        if (curvature > 0.0) {
            lambda = fmin(lambda, (margin * PP_CONT_CURVATURE) / curvature);
        }

        if (lambda < 1.0) {
            for (uint32_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
                blend_point(&points[k], &samples[k], lambda, wheelbase);
            }
        }
    }
    return lambda;
}

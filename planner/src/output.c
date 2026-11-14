/* T11 Output (output.h). PP-SWR-011, 012. */

#include "output.h"

#include <float.h>
#include <math.h>
#include <string.h>

#include "pp_math.h"

#define PP_US_PER_S (1.0e6)
/* Below this speed d' = d_dot / s_dot is taken at this speed, to stay finite. */
#define PP_FRENET_MIN_SPEED_MPS (1.0)
/* Smallest 1 - kappa_ref * d: the path must stay on the inner side of the centre of curvature. */
#define PP_FRENET_MIN_Q (0.1)

void pp_speed_profile(const pp_longitudinal_plan_t *plan, uint64_t t0_us, double speed,
                      pp_speed_profile_t *out)
{
    const double step = PP_GRID_STEP_S;
    (void)memset(out, 0, sizeof(*out));

    for (uint32_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        double v = speed;
        double a = 0.0;
        if (plan != NULL) {
            /* Plan time of this Trajectory point. */
            const double shift = (t0_us >= plan->header.stamp_us)
                ? ((double)(t0_us - plan->header.stamp_us) / PP_US_PER_S)
                : (-(double)(plan->header.stamp_us - t0_us) / PP_US_PER_S);
            const double last = (double)(PP_LONGITUDINAL_PLAN_POINTS - 1U);
            const double index = pp_clamp((((double)k * step) + shift) / step, 0.0, last);
            const uint32_t i = (uint32_t)floor(index);
            const uint32_t j = (i + 1U < PP_LONGITUDINAL_PLAN_POINTS) ? (i + 1U) : i;
            const double f = index - (double)i;
            const pp_longitudinal_point_t *p = plan->points;
            v = (double)p[i].v + (f * ((double)p[j].v - (double)p[i].v));
            a = (double)p[i].a + (f * ((double)p[j].a - (double)p[i].a));
        }
        out->v[k] = fmax(v, 0.0);
        out->a[k] = a;
        if (k > 0U) {
            out->s[k] = out->s[k - 1U] + (0.5 * (out->v[k - 1U] + out->v[k]) * step);
        }
    }
}

static double wrap_angle(double angle)
{
    return atan2(sin(angle), cos(angle));
}

bool pp_output_points(const pp_reference_line_t *ref, const pp_lateral_path_t *path,
                      const pp_speed_profile_t *speed, double wheelbase,
                      pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],
                      pp_ref_samples_t *samples)
{
    pp_ref_walker_t walker;
    pp_ref_point_t r;
    pp_ref_walk_begin(&walker, ref, &r);

    for (uint32_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        pp_ref_walk_to(&walker, speed->s[k], &r);
        if (samples != NULL) {
            samples->kappa[k] = r.kappa;
            samples->theta[k] = r.theta;
            samples->in_view[k] = !walker.on_arc;
        }

        const double d = path->d[k];
        const double s_dot = fmax(speed->v[k], PP_FRENET_MIN_SPEED_MPS);
        const double d1 = path->d_dot[k] / s_dot;                                  /* dd/ds */
        const double d2 = (path->d_ddot[k] - (d1 * speed->a[k])) / (s_dot * s_dot); /* d2d/ds2 */
        const double q = fmax(1.0 - (r.kappa * d), PP_FRENET_MIN_Q);
        const double dtheta = atan(d1 / q);
        const double c = cos(dtheta);
        const double kappa = (((((d2 + (((r.dkappa * d) + (r.kappa * d1)) * tan(dtheta))) * c * c)
                               / q) + r.kappa) * c) / q;
        const double x = r.x - (d * sin(r.theta));
        const double y = r.y + (d * cos(r.theta));
        const double yaw = wrap_angle(r.theta + dtheta);
        const double heading_rate = speed->v[k] * kappa;
        const double fields[] = {x, y, yaw, speed->v[k], path->d_dot[k], speed->a[k], heading_rate, kappa};
        for (size_t i = 0U; i < sizeof(fields) / sizeof(fields[0]); i++) {
            if (!(fabs(fields[i]) <= (double)FLT_MAX)) {
                return false;
            }
        }

        pp_trajectory_point_t *pt = &points[k];
        (void)memset(pt, 0, sizeof(*pt));
        pt->time_from_start = (float)((double)k * PP_GRID_STEP_S);
        pt->pose.x = (float)x;
        pt->pose.y = (float)y;
        pt->pose.yaw = (float)yaw;
        pt->longitudinal_velocity_mps = (float)speed->v[k];
        pt->lateral_velocity_mps = (float)path->d_dot[k];                 /* d_dot (ICD 6.1) */
        pt->acceleration_mps2 = (float)speed->a[k];
        pt->heading_rate_rps = (float)heading_rate;
        pt->curvature = (float)kappa;
        pt->front_wheel_angle_rad = (float)atan(wheelbase * kappa);
        pt->rear_wheel_angle_rad = 0.0F;
    }
    return true;
}

void pp_output_empty_points(pp_trajectory_point_t points[PP_TRAJECTORY_POINTS])
{
    for (uint32_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        (void)memset(&points[k], 0, sizeof(points[k]));
        points[k].time_from_start = (float)((double)k * PP_GRID_STEP_S);
    }
}

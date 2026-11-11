/* T10 Feasibility and limits (feasibility.h). PP-SWR-001, 003, 005 to 009, 116, 117, 151, 152. */

#include "feasibility.h"

#include <math.h>
#include <string.h>

#include "pp_math.h"

#define PP_MIN_SPEED_MPS (1.0)         /* Curvature limits from a_y are taken at least at this speed */
#define PP_CHANGED_KAPPA (1.0e-9)      /* [1/m] smaller changes count as unchanged */
#define PP_CURVE_STEP_M (2.0)          /* Grid of T5 (Software Detailed Design 8) */
#define PP_CURVE_MAX_STEPS (200U)      /* Bounds the work: 400 m */
#define PP_KAPPA_FLOOR (1.0e-5)        /* [1/m] below this v_max is that of R = 100 km */
/* Cut slightly inside each limit so the float32 value sent never exceeds it. */
#define PP_LIMIT_SCALE (1.0 - 1.0e-6)

void pp_feasibility_check(const pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],
                          const pp_ref_samples_t *ref, pp_path_check_t *out)
{
    double ay[PP_TRAJECTORY_POINTS];
    const uint32_t window = (uint32_t)lround(PP_JERK_WINDOW_S / PP_GRID_STEP_S);
    (void)memset(out, 0, sizeof(*out));

    for (uint32_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        const double v = (double)points[k].longitudinal_velocity_mps;
        const double need = v * v * ref->kappa[k];
        ay[k] = v * v * (double)points[k].curvature;
        out->ay_max = fmax(out->ay_max, fabs(ay[k]));
        out->ay_add_max = fmax(out->ay_add_max, fabs(ay[k] - need));
        if (ref->in_view[k]) {
            out->ay_need_max = fmax(out->ay_need_max, fabs(need));
        }
    }
    /* Jerk of a_y, moving mean over 0.5 s = mean slope over `window` steps. */
    for (uint32_t k = 0U; (k + window) < PP_TRAJECTORY_POINTS; k++) {
        const double mean = (ay[k + window] - ay[k]) / ((double)window * PP_GRID_STEP_S);
        out->jerk_max = fmax(out->jerk_max, fabs(mean));
    }
}

bool pp_feasibility_limit(pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],
                          const pp_ref_samples_t *ref, const pp_function_limits_t *limits,
                          const pp_vehicle_config_t *vehicle)
{
    const double dt = PP_GRID_STEP_S;
    const double wheelbase = (double)vehicle->wheelbase;
    const double kappa_wheel = tan((double)vehicle->max_wheel_angle) / wheelbase;
    const double wheel_step = PP_LIMIT_SCALE * ((double)vehicle->max_steering_wheel_rate
                                                / (double)vehicle->steering_ratio) * dt;
    double kappa[PP_TRAJECTORY_POINTS];
    uint32_t first_changed = PP_TRAJECTORY_POINTS;

    /* Point 0 keeps its pose; its curvature is cut too (after T4 it may exceed slightly). */
    {
        const double v0 = fmax((double)points[0].longitudinal_velocity_mps, PP_MIN_SPEED_MPS);
        const double limit0 = PP_LIMIT_SCALE * fmin(limits->ay_max / (v0 * v0), kappa_wheel);
        const double wanted0 = (double)points[0].curvature;
        kappa[0] = pp_clamp(wanted0, -limit0, limit0);
        if (fabs(kappa[0] - wanted0) > PP_CHANGED_KAPPA) {
            points[0].curvature = (float)kappa[0];
            points[0].heading_rate_rps = (float)((double)points[0].longitudinal_velocity_mps * kappa[0]);
            points[0].front_wheel_angle_rad = (float)atan(wheelbase * kappa[0]);
            first_changed = 1U;
        }
    }
    for (uint32_t k = 1U; k < PP_TRAJECTORY_POINTS; k++) {
        const double wanted = (double)points[k].curvature;
        const double v = fmax((double)points[k].longitudinal_velocity_mps, PP_MIN_SPEED_MPS);
        const double v_prev = fmax((double)points[k - 1U].longitudinal_velocity_mps,
                                   PP_MIN_SPEED_MPS);
        const double limit = PP_LIMIT_SCALE
                             * fmin(limits->ay_max / (v * v), kappa_wheel);   /* PP-SWR-001, 116 */
        double c = pp_clamp(wanted, -limit, limit);

        /* Jerk per step (PP-SWR-003); stricter than the 0.5 s mean of the requirement. */
        const double ay_prev = v_prev * v_prev * kappa[k - 1U];
        const double ay = pp_clamp(v * v * c, ay_prev - (limits->jerk_max * dt),
                                   ay_prev + (limits->jerk_max * dt));
        c = ay / (v * v);

        /* Steering wheel rate (PP-SWR-117). */
        const double wheel_prev = atan(wheelbase * kappa[k - 1U]);
        const double wheel = pp_clamp(atan(wheelbase * c), wheel_prev - wheel_step,
                                      wheel_prev + wheel_step);
        c = pp_clamp(tan(wheel) / wheelbase, -limit, limit);

        kappa[k] = c;
        if ((fabs(c - wanted) > PP_CHANGED_KAPPA) && (first_changed == PP_TRAJECTORY_POINTS)) {
            first_changed = k;
        }
    }

    /* Integrate the path again from the point before the first change. */
    for (uint32_t k = first_changed; k < PP_TRAJECTORY_POINTS; k++) {
        const pp_trajectory_point_t *a = &points[k - 1U];
        pp_trajectory_point_t *b = &points[k];
        const double v = (double)b->longitudinal_velocity_mps;
        const double ds = 0.5 * ((double)a->longitudinal_velocity_mps + v) * dt;
        const double yaw_a = (double)a->pose.yaw;
        const double yaw_b = yaw_a + (0.5 * (kappa[k - 1U] + kappa[k]) * ds);
        const double mid = 0.5 * (yaw_a + yaw_b);
        b->pose.x = (float)((double)a->pose.x + (ds * cos(mid)));
        b->pose.y = (float)((double)a->pose.y + (ds * sin(mid)));
        b->pose.yaw = (float)atan2(sin(yaw_b), cos(yaw_b));
        b->curvature = (float)kappa[k];
        b->heading_rate_rps = (float)(v * kappa[k]);
        b->front_wheel_angle_rad = (float)atan(wheelbase * kappa[k]);
        /* d_dot against the reference line (Interface Control Document 6.1). */
        b->lateral_velocity_mps = (float)(v * sin(yaw_b - ref->theta[k]));
    }
    return first_changed < PP_TRAJECTORY_POINTS;
}

void pp_limit_flag_reset(pp_limit_flag_t *flag)
{
    (void)memset(flag, 0, sizeof(*flag));
}

void pp_limit_flag_update(pp_limit_flag_t *flag, double ay_need_max, double ay_limit,
                          const pp_calibration_t *cal, double cycle_s)
{
    /* Condition must hold in consecutive cycles over T_flag / 2 (Software Detailed Design 13). */
    /* The tolerance keeps float32 calibration (0.2F > 0.2) from adding a cycle. */
    const double wanted = ceil(((0.5 * (double)cal->T_flag) / cycle_s) - 1.0e-6);
    const uint8_t cycles = (wanted < 1.0) ? 1U : ((wanted > 255.0) ? 255U : (uint8_t)wanted);
    const double band = (double)cal->delta_ay;

    if (!flag->reached) {
        flag->on_cycles = (ay_need_max > (ay_limit + band))
                          ? (uint8_t)((flag->on_cycles < 255U) ? (flag->on_cycles + 1U) : 255U) : 0U;
        if (flag->on_cycles >= cycles) {
            flag->reached = true;      /* PP-SWR-007 */
            flag->on_cycles = 0U;
        }
    } else {
        flag->off_cycles = (ay_need_max < (ay_limit - band))
                           ? (uint8_t)((flag->off_cycles < 255U) ? (flag->off_cycles + 1U) : 255U) : 0U;
        if (flag->off_cycles >= cycles) {
            flag->reached = false;     /* PP-SWR-008 */
            flag->off_cycles = 0U;
        }
    }
}

void pp_curve_limit(const pp_reference_line_t *ref, double ay_limit, pp_curve_limit_t *out)
{
    pp_ref_walker_t walker;
    pp_ref_point_t p;
    (void)memset(out, 0, sizeof(*out));
    pp_ref_walk_begin(&walker, ref, &p);
    out->kappa_max = fabs(p.kappa);

    for (uint32_t i = 1U; (i <= PP_CURVE_MAX_STEPS) && !walker.on_arc; i++) {
        const double s = (double)i * PP_CURVE_STEP_M;
        pp_ref_walk_to(&walker, s, &p);
        if (!walker.on_arc && (fabs(p.kappa) > out->kappa_max)) {
            out->kappa_max = fabs(p.kappa);
            out->distance = s;
        }
    }
    out->v_max = sqrt(ay_limit / fmax(out->kappa_max, PP_KAPPA_FLOOR));   /* PP-SWR-151 */
}

double pp_ay_need_max(const pp_reference_line_t *ref, const pp_speed_profile_t *speed)
{
    pp_ref_walker_t walker;
    pp_ref_point_t p;
    double need = 0.0;
    pp_ref_walk_begin(&walker, ref, &p);
    for (uint32_t k = 0U; (k < PP_TRAJECTORY_POINTS) && !walker.on_arc; k++) {
        pp_ref_walk_to(&walker, speed->s[k], &p);
        if (!walker.on_arc) {
            need = fmax(need, speed->v[k] * speed->v[k] * fabs(p.kappa));
        }
    }
    return need;
}

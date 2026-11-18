/* T12 Bám xe trước (follow.h). */

#include "follow.h"

#include <math.h>
#include <string.h>

void pp_follow_reset(pp_follow_state_t *st)
{
    (void)memset(st, 0, sizeof(*st));
}

static bool lead_usable(const pp_lead_target_t *lead, const pp_calibration_t *cal)
{
    return (lead != NULL) && isfinite(lead->x) && isfinite(lead->y) && isfinite(lead->gap)
           && isfinite(lead->heading) && isfinite(lead->vx_rel) && isfinite(lead->vy_rel)
           && isfinite(lead->existence_probability)
           && (lead->existence_probability >= cal->exist_min)
           && (lead->x > 0.0F);                                       /* PP-SWR-176 */
}

static bool lead_class_ok(const pp_lead_target_t *lead)
{
    return (lead->classification == PP_LEAD_CLASS_CAR) || (lead->classification == PP_LEAD_CLASS_TRUCK);
}

/* base_link at the previous cycle to base_link now: p_new = R(-dyaw) (p_old - [dx, dy]). */
static void move_point(const pp_motion_t *m, double *x, double *y)
{
    const double px = *x - m->dx;
    const double py = *y - m->dy;
    const double c = cos(m->dyaw);
    const double s = sin(m->dyaw);
    *x = (c * px) + (s * py);
    *y = (-s * px) + (c * py);
}

/* Original lane centre at x, extended along its end curvature outside the observed range. */
static void origin_at(const pp_follow_state_t *st, double x, double *y, double *slope)
{
    const double xc = pp_clamp(x, st->origin_start, st->origin_end);
    const double dx = x - xc;
    *y = pp_cubic_value(&st->origin, xc) + (pp_cubic_slope(&st->origin, xc) * dx)
         + (0.5 * pp_cubic_bend(&st->origin, xc) * dx * dx);
    *slope = pp_cubic_slope(&st->origin, xc) + (pp_cubic_bend(&st->origin, xc) * dx);
}

/* Lateral offset of a point from the original lane centre, left positive. */
static double origin_offset(const pp_follow_state_t *st, double px, double py)
{
    double yc = 0.0;
    double slope = 0.0;
    origin_at(st, px, &yc, &slope);
    return (py - yc) / hypot(1.0, slope);
}

/* Speed of the lead across the original lane centre at the lead (ground speed in base_link). */
static double lead_normal_speed(const pp_follow_state_t *st, const pp_follow_input_t *in,
                                const pp_lead_target_t *lead, double xl)
{
    double yc = 0.0;
    double slope = 0.0;
    origin_at(st, xl, &yc, &slope);
    const double theta = atan(slope);
    const double vx_ground = in->v + (double)lead->vx_rel;
    const double vy_ground = in->v_y + (double)lead->vy_rel;
    return (-sin(theta) * vx_ground) + (cos(theta) * vy_ground);
}

void pp_follow_observe(pp_follow_state_t *st, const pp_follow_input_t *in,
                       const pp_calibration_t *cal)
{
    /* Original lane centre: moved by ego-motion, refreshed while the lane lines are trusted. */
    if (st->origin_valid) {
        pp_cubic_t moved;
        double lo = 0.0;
        double hi = 0.0;
        if (in->moved && pp_cubic_move(&st->origin, st->origin_start, st->origin_end, &in->since_last,
                                       &moved, &lo, &hi)) {
            st->origin = moved;
            st->origin_start = lo;
            st->origin_end = hi;
        } else {
            st->origin_valid = false;                              /* Cannot be moved: dropped */
        }
    }
    if (in->lane_trusted && (in->lane_ref != NULL)) {
        st->origin = in->lane_ref->centre;
        st->origin_start = in->lane_ref->view_start;
        st->origin_end = in->lane_ref->view_end;
        st->origin_width = in->lane_ref->width;
        st->origin_valid = true;
    }

    /* Trail of the lead centre. */
    const uint32_t capacity = (cal->trail_n < (float)PP_FOLLOW_TRAIL_MAX)
                              ? (uint32_t)cal->trail_n : PP_FOLLOW_TRAIL_MAX;
    if (!in->moved) {
        st->n = 0U;                                                /* Cannot be moved: dropped */
    } else {
        uint32_t kept = 0U;
        for (uint32_t i = 0U; i < st->n; i++) {
            double x = st->x[i];
            double y = st->y[i];
            move_point(&in->since_last, &x, &y);
            if (x >= 0.0) {                                        /* Behind the car: dropped */
                st->x[kept] = x;
                st->y[kept] = y;
                kept++;
            }
        }
        st->n = kept;
    }
    /* V5 (the lead is the ACC target) is an entry condition; the trail records any usable car or truck,
     * so a one-cycle gap of the ACC target does not throw the trail away (M6 keeps the id). */
    const bool recordable = lead_usable(in->lead, cal) && lead_class_ok(in->lead);
    if (!recordable) {
        st->n = 0U;
        st->has_stamp = false;
        st->trail_id = 0U;
        st->vn_count = 0U;
        return;
    }
    if ((in->lead->id != st->trail_id) || !st->has_stamp) {
        st->n = 0U;
        st->trail_id = in->lead->id;
        st->vn_count = 0U;
    }
    if (!st->has_stamp || (in->lead->header.stamp_us != st->last_stamp_us)) {
        st->last_stamp_us = in->lead->header.stamp_us;
        st->has_stamp = true;
        if (in->lead_moved) {
            double x = (double)in->lead->x;
            double y = (double)in->lead->y;
            move_point(&in->lead_motion, &x, &y);
            if (st->origin_valid) {      /* V4 on a low-pass: one vy_rel carries 0.2 m/s of noise against 0.6 */
                const double vn = lead_normal_speed(st, in, in->lead, x);
                st->vn_filt = (st->vn_count == 0U) ? vn : (st->vn_filt + (PP_FOLLOW_VN_ALPHA * (vn - st->vn_filt)));
                st->vn_count++;
            }
            const bool spaced = (st->n == 0U)
                                || (hypot(x - st->x[st->n - 1U], y - st->y[st->n - 1U])
                                    >= (double)cal->trail_spacing);
            if (spaced && (x >= 0.0)) {
                if (st->n >= capacity) {                           /* Full: oldest dropped */
                    (void)memmove(&st->x[0], &st->x[1], (size_t)(capacity - 1U) * sizeof(double));
                    (void)memmove(&st->y[0], &st->y[1], (size_t)(capacity - 1U) * sizeof(double));
                    st->n = capacity - 1U;
                }
                st->x[st->n] = x;
                st->y[st->n] = y;
                st->n++;
            }
        }
    }
}

bool pp_follow_candidate(const pp_follow_state_t *st, const pp_follow_input_t *in,
                         const pp_calibration_t *cal, const pp_vehicle_config_t *vehicle,
                         pp_reference_line_t *ref)
{
    const pp_lead_target_t *lead = in->lead;
    if (!lead_usable(lead, cal) || !lead_class_ok(lead) || !st->origin_valid || !in->lead_moved
        || (in->steering == NULL) || (in->plan == NULL) || (st->n < 4U)) {
        return false;
    }
    /* M3, M4, M5, M6 (and V1). */
    if ((in->v >= PP_FOLLOW_SPEED_MAX_MPS)
        || (fabs((double)in->steering->steering_wheel_angle_rad) >= PP_FOLLOW_WHEEL_ANGLE_MAX_RAD)
        || (st->active && ((lead->id != st->id) || (st->distance_m >= PP_FOLLOW_DISTANCE_MAX_M)))) {
        return false;
    }
    double xl = (double)lead->x;
    double yl = (double)lead->y;
    move_point(&in->lead_motion, &xl, &yl);
    if (!st->active) {
        /* V2, V5; V3, V4 measured on the original lane centre (PP-ASM-025). */
        /* V3 on the mean over the lead and its latest trail points: a single position of the lead
         * carries 0.25 m of noise at 30 m, against a threshold of 1 m. */
        double d_sum = origin_offset(st, xl, yl);
        uint32_t d_count = 1U;
        for (uint32_t k = 0U; (k < PP_FOLLOW_V3_POINTS) && (k < st->n); k++) {
            d_sum += origin_offset(st, st->x[st->n - 1U - k], st->y[st->n - 1U - k]);
            d_count++;
        }
        const double d_lead = d_sum / (double)d_count;
        const double d_ego = origin_offset(st, 0.0, 0.0);
        const double v_normal = (st->vn_count >= 3U) ? st->vn_filt : lead_normal_speed(st, in, lead, xl);
        if (((double)lead->gap < PP_FOLLOW_GAP_MIN_M) || ((double)lead->gap > PP_FOLLOW_GAP_MAX_M)
            || (in->plan->target_id == 0U) || (lead->id != in->plan->target_id)
            || (fabs(d_lead - d_ego) >= (double)cal->follow_lat_max)
            || (fabs(v_normal) >= (double)cal->follow_vlat_max)) {
            return false;
        }
    }

    /* Step 4: cubic through the trail and the lead, anchored at the car and along the lead. */
    pp_cubic_fit_t fit;
    const double heading = (double)lead->heading;
    const double x_end = xl + (2.0 * cos(heading));
    pp_cubic_fit_begin(&fit, 0.0, fmax(x_end, xl + 3.0));
    for (uint32_t i = 0U; i < 5U; i++) {
        pp_cubic_fit_add(&fit, 0.0, 0.0);
    }
    for (uint32_t i = 1U; i <= 3U; i++) {
        pp_cubic_fit_add(&fit, 0.5 * (double)i, 0.0);
    }
    for (uint32_t i = 0U; i < st->n; i++) {
        pp_cubic_fit_add(&fit, st->x[i], st->y[i]);
    }
    pp_cubic_fit_add(&fit, xl, yl);
    /* The line continues beyond the lead along its heading (SDD 5.1 step 4): anchors with a weight
     * comparable to the trail, so the noise of the trail does not turn into the heading at the lead. */
    const uint32_t end_weight = (st->n / 2U) + 5U;
    for (uint32_t k = 1U; k <= 3U; k++) {
        for (uint32_t w = 0U; w < end_weight; w++) {
            pp_cubic_fit_add(&fit, xl + ((double)k * cos(heading)), yl + ((double)k * sin(heading)));
        }
    }
    /* The trail is a short, nearly straight stretch: the u^3 term would only amplify noise into the
     * curvature at the lead, which the path then follows (the line continues as an arc from there).
     * Forcing that coefficient to zero makes the fit a parabola. */
    for (uint32_t k = 0U; k < PP_CUBIC_TERMS; k++) {
        fit.ata.m[PP_CUBIC_TERMS - 1U][k] = 0.0;
        fit.ata.m[k][PP_CUBIC_TERMS - 1U] = 0.0;
    }
    fit.ata.m[PP_CUBIC_TERMS - 1U][PP_CUBIC_TERMS - 1U] = 1.0;
    fit.aty[PP_CUBIC_TERMS - 1U] = 0.0;
    pp_cubic_t centre;
    if (!pp_cubic_fit_solve(&fit, &centre)) {
        return false;
    }
    /* M2: root-mean-square residual over the trail and the lead. The largest residual would trip on
     * one noisy sample of a good trail (position noise of a lead vehicle at 30 m is about 0.25 m). */
    double squares = pow(pp_cubic_value(&centre, xl) - yl, 2.0);
    for (uint32_t i = 0U; i < st->n; i++) {
        squares += pow(pp_cubic_value(&centre, st->x[i]) - st->y[i], 2.0);
    }
    if (sqrt(squares / (double)(st->n + 1U)) > (double)cal->trail_fit_max) {
        return false;                                              /* M2 */
    }
    (void)memset(ref, 0, sizeof(*ref));
    ref->valid = true;
    ref->centre = centre;
    ref->width = (st->origin_width > (double)vehicle->vehicle_width) ? st->origin_width
                 : ((double)vehicle->vehicle_width + 0.2);
    ref->view_start = 0.0;
    ref->view_end = xl;                                            /* observed_horizon_s: to the lead */
#ifdef PP_REF_SAMPLED
    pp_ref_sample_cubic(ref);
#endif
    return true;
}

bool pp_follow_path_within(const pp_follow_state_t *st, const pp_trajectory_point_t *points,
                           const pp_calibration_t *cal, const pp_vehicle_config_t *vehicle)
{
    const double free_space = 0.5 * (st->origin_width - (double)vehicle->vehicle_width);
    const double limit = fmin(PP_FOLLOW_PATH_DEV_M, free_space - (double)cal->dlc_offset_min);
    bool ok = st->origin_valid && (limit > 0.0);
    for (uint32_t k = 0U; ok && (k < PP_TRAJECTORY_POINTS); k++) {
        ok = fabs(origin_offset(st, (double)points[k].pose.x, (double)points[k].pose.y)) < limit;  /* M1 */
    }
    return ok;
}

void pp_follow_commit(pp_follow_state_t *st, bool active, const pp_lead_target_t *lead, double ds)
{
    if (active && !st->active) {
        st->id = (lead != NULL) ? lead->id : 0U;
        st->distance_m = 0.0;
    } else if (active) {
        st->distance_m += ds;                                      /* M5 */
    } else {
        st->distance_m = 0.0;
    }
    st->active = active;
}

#include "intervention.h"

#include <math.h>
#include <stddef.h>
#include <string.h>

#include "output.h"
#include "pp_math.h"

#define PP_US_PER_S (1.0e6)
#define PP_ELK_LATE_M (0.3)       /* PP-SWR-089 */
#define PP_MARK_DTLE_ALLOW_M (0.3) /* PP-SWR-086 */
#define PP_CUT_PENALTY (1.0e3)    /* [m] ranks a candidate T10 would cut after every uncut one */

static const uint32_t EGO_LINES[PP_ROAD_EDGES] = {PP_LINE_L1, PP_LINE_R1};
static const uint32_t OUTER_LINES[PP_ROAD_EDGES] = {PP_LINE_L2, PP_LINE_R2};

double pp_intervention_vy_at_t0(pp_lateral_velocity_history_t *history,
                                const pp_vehicle_state_estimate_t *state, uint64_t t0_us)
{
    if (state == NULL) {
        history->valid = false;
        return 0.0;
    }
    const uint64_t stamp_us = state->header.stamp_us;
    const double value = state->lateral_velocity;
    if (stamp_us > t0_us) {
        return value;
    }
    if (!history->valid || (stamp_us < history->stamp_us)) {
        *history = (pp_lateral_velocity_history_t){true, stamp_us, value, 0.0};
    } else if (stamp_us > history->stamp_us) {
        const uint64_t elapsed = stamp_us - history->stamp_us;
        history->rate = (elapsed <= PP_VEHICLE_STATE_TIMEOUT_US)
                        ? (value - history->value) * PP_US_PER_S / (double)elapsed : 0.0;
        history->stamp_us = stamp_us;
        history->value = value;
    } else {
        /* Another planner cycle reading the same received estimate. */
    }
    return history->value + history->rate * (double)(t0_us - stamp_us) / PP_US_PER_S;
}

static bool measured_at(const pp_boundary_t *b, double x, double min_confidence)
{
    return b->present && (b->status == PP_LINE_STATUS_MEASURED) && (b->confidence >= min_confidence)
           && (b->view_start <= x) && (b->view_end >= x);
}

static double normal_scale(const pp_cubic_t *p, double x)
{
    return 1.0 / hypot(1.0, pp_cubic_slope(p, x));
}

static bool remembered_edge(const pp_boundary_t *before, const pp_boundary_t *now,
                            const pp_motion_t *motion, double front, double k_sigma)
{
    pp_cubic_t moved;
    double lo = 0.0;
    double hi = 0.0;
    if (!before->present || (motion == NULL)
        || !pp_cubic_move(&before->poly, before->view_start, before->view_end, motion, &moved, &lo, &hi)
        || (front < lo) || (front > hi)) {
        return false;
    }
    const double a = pp_cubic_value(&moved, front);
    const double b = pp_cubic_value(&now->poly, front);
    const double variance = before->variance[0] + now->variance[0]
                            + (front * front * (before->variance[1] + now->variance[1]));
    return fabs(a - b) <= (k_sigma * sqrt(fmax(0.0, variance))) + 1.0e-6;
}

void pp_road_edge_references(pp_edge_memory_t *mem, const pp_lane_at_t0_t *lane,
                            const pp_reference_line_t *camera_ref, const pp_motion_t *motion,
                            const pp_vehicle_config_t *vehicle, const pp_calibration_t *cal,
                            pp_reference_line_t refs[PP_ROAD_EDGES])
{
    (void)memset(refs, 0, PP_ROAD_EDGES * sizeof(*refs));
    if (lane->lane_change != PP_SIDE_NONE) {
        (void)memset(mem, 0, sizeof(*mem));
    }
    const double front = (double)vehicle->wheelbase;
    for (uint32_t side = 0U; side < PP_ROAD_EDGES; side++) {
        const uint32_t other = (PP_ROAD_EDGES - 1U) - side;
        const double sign = (side == 0U) ? 1.0 : -1.0;
        const pp_boundary_t *edge = &lane->boundary[PP_LANE_LINES + side];
        const bool outer_seen = measured_at(&lane->boundary[OUTER_LINES[side]], front, cal->conf_ego);
        if (!measured_at(edge, front, cal->conf_edge) || outer_seen) {
            mem->edge[side].present = false;                            /* F21 */
            continue;
        }
        pp_reference_line_t *ref = &refs[side];
        const pp_boundary_t *opposite = &lane->boundary[EGO_LINES[other]];
        bool opposite_seen = !camera_ref->line_rejected[other] && measured_at(opposite, front, cal->conf_ego);
        if (!opposite_seen && !measured_at(&lane->boundary[OUTER_LINES[other]], front, cal->conf_ego)) {
            opposite = &lane->boundary[PP_LANE_LINES + other];
            opposite_seen = measured_at(opposite, front, cal->conf_edge);
        }
        if (opposite_seen) {
            for (uint32_t k = 0U; k < PP_CUBIC_TERMS; k++) {
                ref->centre.c[k] = 0.5 * (edge->poly.c[k] + opposite->poly.c[k]);
            }
            ref->width = sign * (pp_cubic_value(&edge->poly, front) - pp_cubic_value(&opposite->poly, front))
                         * normal_scale(&ref->centre, front);
            ref->view_start = fmax(edge->view_start, opposite->view_start);
            ref->view_end = fmin(edge->view_end, opposite->view_end);
        } else if (remembered_edge(&mem->edge[side], edge, motion, front, cal->k_jump)) {
            ref->width = mem->width[side];
            ref->centre = edge->poly;
            ref->centre.c[0] -= sign * ref->width / (2.0 * normal_scale(&edge->poly, front));
            ref->view_start = edge->view_start;
            ref->view_end = edge->view_end;
        } else {
            /* No association of this edge to the ego-lane corridor. */
        }
        ref->valid = (ref->width >= (double)vehicle->vehicle_width) && (ref->width <= PP_LANE_WIDTH_MAX_M);
        if (ref->valid) {
            mem->edge[side] = *edge;
            mem->width[side] = ref->width;
            ref->lane_too_narrow = (0.5 * (ref->width - (double)vehicle->vehicle_width)) < (double)cal->free_space_min;
#ifdef PP_REF_SAMPLED
            pp_ref_sample_cubic(ref);
#endif
        } else {
            mem->edge[side].present = false;
        }
    }
}

bool pp_intervention_line_trusted(const pp_lane_at_t0_t *lane, const pp_reference_line_t *ref,
                                  pp_side_t side, const pp_vehicle_config_t *vehicle,
                                  const pp_calibration_t *cal)
{
    if ((side != PP_SIDE_LEFT) && (side != PP_SIDE_RIGHT)) {
        return false;
    }
    const uint32_t index = (side == PP_SIDE_LEFT) ? 0U : 1U;
    return ref->valid && !ref->coasting && !ref->inferred && !ref->line_rejected[index]
           && (ref->width >= (double)vehicle->vehicle_width)
           && measured_at(&lane->boundary[EGO_LINES[index]], vehicle->wheelbase, cal->conf_ego);
}

bool pp_elk_past_marking(const pp_lane_at_t0_t *lane, pp_side_t side,
                         const pp_vehicle_config_t *vehicle, const pp_calibration_t *cal)
{
    if ((side != PP_SIDE_LEFT) && (side != PP_SIDE_RIGHT)) {
        return false;
    }
    const pp_boundary_t *mark = &lane->boundary[(side == PP_SIDE_LEFT) ? PP_LINE_L1 : PP_LINE_R1];
    const double x = (double)vehicle->wheelbase;
    if (!measured_at(mark, x, cal->conf_ego)) {
        return false;
    }
    const double sign = (side == PP_SIDE_LEFT) ? 1.0 : -1.0;
    const double dlc = sign * pp_cubic_value(&mark->poly, x) * normal_scale(&mark->poly, x)
                       - 0.5 * (double)vehicle->vehicle_width;
    return dlc < -PP_ELK_LATE_M;                                         /* PP-SWR-089 */
}

bool pp_intervention_settled(const pp_reference_line_t *ref, const pp_lateral_state_t *ego,
                             const pp_old_path_t *old, double v, double v_y, double yaw_rate,
                             const pp_vehicle_config_t *vehicle, const pp_calibration_t *cal)
{
    if (!ref->valid || ref->coasting || !old->valid) {
        return false;
    }
    pp_ref_point_t front;
    double d_front = 0.0;
    const double x = (double)vehicle->wheelbase;
    pp_ref_project(ref, x, 0.0, &front, &d_front);
    const double v_lat = ((v_y + yaw_rate * x) * cos(front.theta)) - (v * sin(front.theta));
    pp_path_sample_t applied;
    (void)pp_stitch_sample_old(old, 0.0, &applied);
    pp_ref_point_t ref_at_path;
    double d_path;
    pp_ref_project(ref, applied.x, applied.y, &ref_at_path, &d_path);
    const double ay_add = applied.v * applied.v * (applied.kappa - ref_at_path.kappa);
    return fabs(d_front) <= 0.5 * (ref->width - (double)vehicle->vehicle_width)
           && fabs(ego->d) <= (double)cal->d_end                          /* PP-SWR-032, PP-ASM-028 */
           && fabs(v_lat) <= (double)cal->v_lat_end && fabs(ego->heading) <= (double)cal->heading_end
           && fabs(ay_add) <= (double)cal->ay_add_end;                    /* PP-SWR-032, 090 */
}

static void sample_profile(const pp_intervention_path_t *path, double elapsed, pp_lateral_path_t *out)
{
    for (uint32_t i = 0U; i < PP_TRAJECTORY_POINTS; i++) {
        const double t = elapsed + (double)i * PP_GRID_STEP_S;
        if (path->two_phase && (t >= path->profile.duration)) {
            pp_quintic_eval(&path->back, t - path->profile.duration, &out->d[i], &out->d_dot[i], &out->d_ddot[i]);
        } else {
            pp_quintic_eval(&path->profile, t, &out->d[i], &out->d_dot[i], &out->d_ddot[i]);
        }
    }
}

/* One quintic to the centre, or (T_return > 0, car still moving outward) an arrest in `duration`
 * that ends with zero speed, acceleration and jerk, then a slow return in T_return (PP-TS-026). */
static void build_path(pp_intervention_path_t *path, const pp_lateral_state_t *start, double sign,
                       double target, double duration, double t_return)
{
    path->two_phase = false;
    if (t_return <= 0.0) {
        (void)pp_quintic_solve(start->d, start->d_dot, start->d_ddot, target, duration, &path->profile);
    } else if ((sign * start->d_dot) <= 0.0) {
        (void)pp_quintic_solve(start->d, start->d_dot, start->d_ddot, target, t_return, &path->profile);
    } else {
        const double peak = start->d + (0.4 * start->d_dot * duration)
                            + (0.05 * start->d_ddot * duration * duration);
        (void)pp_quintic_solve(start->d, start->d_dot, start->d_ddot, peak, duration, &path->profile);
        (void)pp_quintic_solve(peak, 0.0, 0.0, target, t_return, &path->back);
        path->two_phase = true;
    }
}

static double candidate_score(const pp_intervention_path_t *profile, const pp_reference_line_t *ref,
                              const pp_speed_profile_t *speed, const pp_function_limits_t *limits,
                              const pp_vehicle_config_t *vehicle, double sign, double allowed_crossing,
                              double crossing_d)
{
    pp_lateral_path_t lateral;
    pp_trajectory_point_t points[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t refs;
    pp_path_check_t check;
    sample_profile(profile, 0.0, &lateral);
    if (!pp_output_points(ref, &lateral, speed, vehicle->wheelbase, points, &refs)) {
        return INFINITY;
    }
    pp_feasibility_check(points, &refs, &check);
    const double authority = fmax(check.ay_max / limits->ay_max,
        fmax(check.ay_add_max / limits->ay_add_max, check.jerk_max / limits->jerk_max));
    if (authority > 1.0) {
        return INFINITY;
    }
    /* Within the limits means T10 step 2 leaves the path as it is: T10 cuts jerk per
     * 0.1 s step and the steering wheel rate, stricter than the 0.5 s mean above. A cut
     * candidate no longer ends parallel to the lane (PP-PR-041), so it is only a fallback. */
    pp_trajectory_point_t limited[PP_TRAJECTORY_POINTS];
    (void)memcpy(limited, points, sizeof(limited));
    const double cut = pp_feasibility_limit(limited, &refs, limits, vehicle) ? PP_CUT_PENALTY : 0.0;
    const double half = 0.5 * (ref->width - (double)vehicle->vehicle_width);
    double intrusion = 0.0;
    for (uint32_t i = 0U; i < PP_TRAJECTORY_POINTS; i++) {
        const pp_pose2d_t *pose = &points[i].pose;
        pp_ref_point_t foot;
        double front_d;
        pp_ref_project(ref, (double)pose->x + (double)vehicle->wheelbase * cos(pose->yaw),
                       (double)pose->y + (double)vehicle->wheelbase * sin(pose->yaw), &foot, &front_d);
        intrusion = fmax(intrusion, fmax((sign * front_d) - crossing_d - allowed_crossing,
                                        (-sign * front_d) - half));
    }
    return cut + intrusion;
}

void pp_intervention_begin(pp_intervention_path_t *path, const pp_intervention_request_t *req,
                           double tlc, uint64_t t0_us, const pp_reference_line_t *ref,
                           const pp_lateral_state_t *start, const pp_speed_profile_t *speed,
                           const pp_function_limits_t *limits, const pp_vehicle_config_t *vehicle,
                           const pp_calibration_t *cal, bool elk)
{
    const double sign = (req->side == PP_SIDE_LEFT) ? 1.0 : -1.0;
    const double half = 0.5 * (ref->width - (double)vehicle->vehicle_width);
    const double target = 0.0;                                         /* Lane centre (PP-SWR-084) */
    const double max_duration = (double)cal->intervention_T_max;      /* Software Detailed Design 15 */
    const double step = (double)cal->intervention_T_step;
    const double duration = fmin(elk ? (double)cal->T_elk : (double)cal->T_lka, max_duration);
    const double t_return = (double)cal->T_return;
    path->start_us = t0_us;
    build_path(path, start, sign, target, duration, t_return);
    const double allowed_crossing = elk ? 0.0 : PP_MARK_DTLE_ALLOW_M;
    /* When the ADAS block estimates a nearer crossing, favour candidates that
     * reverse the outward motion earlier (Software Detailed Design 10). */
    pp_ref_point_t front;
    double front_d;
    pp_ref_project(ref, vehicle->wheelbase, 0.0, &front, &front_d);
    double crossing_d = half;
    if (isfinite(tlc) && (sign * start->d_dot > 0.0)) {
        crossing_d = fmin(half, (sign * front_d) + (sign * start->d_dot * fmax(0.0, tlc)));
    }
    double best = candidate_score(path, ref, speed, limits, vehicle, sign, allowed_crossing, crossing_d);
    const uint32_t count = (uint32_t)floor(max_duration / step);
    for (uint32_t n = 1U; (n <= count) && (best > 0.0); n++) {
        const double t = (double)n * step;
        pp_intervention_path_t candidate = *path;
        build_path(&candidate, start, sign, target, t, t_return);
        const double score = candidate_score(&candidate, ref, speed, limits, vehicle, sign, allowed_crossing, crossing_d);
        if (score < best) {
            best = score;
            *path = candidate;
        }
    }
}

void pp_intervention_sample(const pp_intervention_path_t *path, uint64_t t0_us,
                            pp_lateral_path_t *out)
{
    const double elapsed = (t0_us >= path->start_us) ? (double)(t0_us - path->start_us) / PP_US_PER_S : 0.0;
    sample_profile(path, elapsed, out);
}

void pp_corridor_reset(pp_corridor_t *c)
{
    (void)memset(c, 0, sizeof(*c));
}

/* y of the hazard-side edge of a reference line at x. */
static double hazard_edge_y(const pp_reference_line_t *ref, double sign, double x)
{
    return pp_cubic_value(&ref->centre, x)
           + (sign * 0.5 * ref->width * hypot(1.0, pp_cubic_slope(&ref->centre, x)));
}

static void adopt(pp_corridor_t *c, const pp_reference_line_t *live)
{
    c->ref = *live;
    c->valid = true;
    c->pending = false;
    c->pending_s = 0.0;
}

const pp_reference_line_t *pp_corridor_update(pp_corridor_t *c, const pp_reference_line_t *live,
                                              const pp_motion_t *motion, bool started,
                                              pp_side_t side, double front_x,
                                              const pp_calibration_t *cal, double dt)
{
    const double sign = (side == PP_SIDE_LEFT) ? 1.0 : -1.0;
    bool moved = c->valid && !started && (motion != NULL) && live->valid && !live->coasting
                 && !c->ref.coasting;
    if (moved) {
        pp_cubic_t centre;
        double lo = 0.0;
        double hi = 0.0;
        moved = pp_cubic_move(&c->ref.centre, c->ref.view_start, c->ref.view_end, motion, &centre, &lo, &hi);
        if (moved) {
            c->ref.centre = centre;
            c->ref.view_start = lo;
            c->ref.view_end = hi;
        }
    }
    if (!moved || !live->valid || live->coasting) {
        adopt(c, live);                                  /* Start, or nothing to compare with */
        return &c->ref;
    }
    const double x = pp_clamp(front_x, fmax(c->ref.view_start, live->view_start),
                              fmin(c->ref.view_end, live->view_end));
    const double tol = (double)cal->corridor_tol;
    const double away = sign * (hazard_edge_y(live, sign, x) - hazard_edge_y(&c->ref, sign, x));
    const double opposite = fabs(hazard_edge_y(live, -sign, x) - hazard_edge_y(&c->ref, -sign, x));

    if (away <= tol) {
        adopt(c, live);       /* Consistent, or the edge moved toward the car: taken at once */
    } else {
        const double edge_now = hazard_edge_y(live, sign, x);
        if (!c->pending || (fabs(edge_now - c->candidate_edge) > tol)) {
            c->pending = true;                           /* New candidate position */
            c->pending_s = 0.0;
            c->candidate_edge = edge_now;
        } else {
            c->pending_s += dt;
        }
        if (c->pending_s >= (double)cal->T_confirm) {
            if (opposite > tol) {
                adopt(c, live);                          /* The whole lane moved: not a jump */
            } else {
                const double shift = fmin(away, (double)cal->ref_rate * dt);
                c->ref.centre.c[0] += sign * 0.5 * shift;        /* Hazard edge only slides */
                c->ref.width += shift;
            }
        }
    }
#ifdef PP_REF_SAMPLED
    pp_ref_sample_cubic(&c->ref);
#endif
    return &c->ref;
}

/* PP-TS-013 experiment. Included only in the temporary copy of pp_planner.c. */

enum { RESEARCH_HWA, RESEARCH_ELIGIBLE, RESEARCH_APPLIED, RESEARCH_COUNTERS };
static uint64_t research_counts[RESEARCH_COUNTERS];

void pp_research_reset(void);
uint64_t pp_research_count(unsigned index);

void pp_research_reset(void)
{
    (void)memset(research_counts, 0, sizeof(research_counts));
}

uint64_t pp_research_count(unsigned index)
{
    return (index < RESEARCH_COUNTERS) ? research_counts[index] : 0U;
}

/* Unit lateral displacement at the intermediate waypoint. The correction
 * has zero first and second derivatives at both ends and at the join. */
static void research_bump(double waypoint_s, pp_lateral_path_t *bump)
{
    const double end_s = PP_TRAJECTORY_HORIZON_S;
    pp_quintic_t rise, fall;
    (void)pp_quintic_solve(0.0, 0.0, 0.0, 1.0, waypoint_s, &rise);
    (void)pp_quintic_solve(1.0, 0.0, 0.0, 0.0, end_s - waypoint_s, &fall);
    for (uint32_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        const double t = (double)k * PP_GRID_STEP_S;
        if (t <= waypoint_s) {
            pp_quintic_eval(&rise, t, &bump->d[k], &bump->d_dot[k], &bump->d_ddot[k]);
        } else {
            pp_quintic_eval(&fall, t - waypoint_s, &bump->d[k], &bump->d_dot[k], &bump->d_ddot[k]);
        }
    }
}

static bool research_lateral_candidate(const pp_lateral_path_t *base, const pp_lateral_path_t *bump,
                                       double delta, double half, pp_lateral_path_t *candidate)
{
    for (uint32_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        candidate->d[k] = base->d[k] + delta * bump->d[k];
        candidate->d_dot[k] = base->d_dot[k] + delta * bump->d_dot[k];
        candidate->d_ddot[k] = base->d_ddot[k] + delta * bump->d_ddot[k];
        if (fabs(candidate->d[k]) > half) {
            return false;
        }
    }
    return true;
}

static double research_comfort_score(const pp_trajectory_point_t points[PP_TRAJECTORY_POINTS])
{
    double peak = 0.0;
    double squared_jerk = 0.0;
    double ay[PP_TRAJECTORY_POINTS];
    for (uint32_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        const double v = (double)points[k].longitudinal_velocity_mps;
        ay[k] = v * v * (double)points[k].curvature;
        peak = fmax(peak, fabs(ay[k]));
    }
    const uint32_t window = (uint32_t)lround(PP_JERK_WINDOW_S / PP_GRID_STEP_S);
    for (uint32_t k = window; k < PP_TRAJECTORY_POINTS; k++) {
        const double jerk = (ay[k] - ay[k - window]) / ((double)window * PP_GRID_STEP_S);
        squared_jerk += jerk * jerk;
    }
    return peak + 0.2 * sqrt(squared_jerk / (double)(PP_TRAJECTORY_POINTS - window));
}

static bool research_geometry_ok(const pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],
                                 const pp_reference_line_t *ref, const pp_old_path_t *old,
                                 double half)
{
    for (uint32_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        const pp_pose2d_t *pose = &points[k].pose;
        if ((double)pose->x > ref->view_end) {
            return false;
        }
        pp_ref_point_t foot;
        double d;
        pp_ref_project(ref, (double)pose->x, (double)pose->y, &foot, &d);
        if (!isfinite(d) || fabs(d) > half) {
            return false;
        }
        pp_path_sample_t previous;
        if (pp_stitch_sample_old(old, (double)k * PP_GRID_STEP_S, &previous)) {
            const double yaw = (double)pose->yaw;
            const double ex = previous.x - (double)pose->x;
            const double ey = previous.y - (double)pose->y;
            const double delta_yaw = yaw - previous.yaw;
            if (fabs(-sin(yaw) * ex + cos(yaw) * ey) > PP_CONT_LATERAL_M
                || fabs(atan2(sin(delta_yaw), cos(delta_yaw))) > PP_CONT_HEADING_RAD
                || fabs((double)points[k].curvature - previous.kappa) > PP_CONT_CURVATURE) {
                return false;
            }
        }
    }
    return true;
}

static void research_try_quintic(const pp_state_t *s, const pp_usable_inputs_t *in,
                                  const pp_lane_at_t0_t *lane, const pp_reference_line_t *camera_ref,
                                  const pp_speed_profile_t *speed, const pp_old_path_t *old,
                                  double offset, const pp_lateral_path_t *base, pp_cycle_result_t *out)
{
    if (out->arbitration.active_function != PP_ACTIVE_FUNCTION_HWA) {
        return;
    }
    research_counts[RESEARCH_HWA]++;
    const pp_reference_line_t *ref = &out->ref;
    if (s->recentering || !old->valid || offset != 0.0 || in->object_list == NULL
        || in->object_list->num_objects != 0U || !out->samples.in_view[PP_TRAJECTORY_POINTS - 1U]
        || !pp_intervention_line_trusted(lane, ref, PP_SIDE_LEFT, &s->vehicle, s->cal)
        || !pp_intervention_line_trusted(lane, ref, PP_SIDE_RIGHT, &s->vehicle, s->cal)) {
        return;
    }
    const double need = fmax(pp_ay_need_max(camera_ref, speed), pp_ay_need_max(ref, speed));
    const double room = 0.5 * (ref->width - (double)s->vehicle.vehicle_width)
                      - (double)s->cal->dlc_offset_min;
    const double half = fmin((double)s->cal->offset_max, room);
    if (half <= 0.0 || need >= PP_AYSMAX - 0.5 * (double)s->cal->epsilon_ay) {
        return;
    }
    research_counts[RESEARCH_ELIGIBLE]++;

    static const double waypoint_times[] = {1.0, 1.5, 2.0};
    static const double deltas[] = {-0.30, -0.20, -0.10, -0.05, 0.05, 0.10, 0.20, 0.30};
    const double wheelbase = (double)s->vehicle.wheelbase;
    const double baseline_score = research_comfort_score(out->points);
    double best_score = baseline_score - 0.005;
    bool applied = false;
    for (size_t i = 0U; i < sizeof(waypoint_times) / sizeof(waypoint_times[0]); i++) {
        pp_lateral_path_t bump;
        research_bump(waypoint_times[i], &bump);
        for (size_t j = 0U; j < sizeof(deltas) / sizeof(deltas[0]); j++) {
            pp_lateral_path_t lateral;
            if (!research_lateral_candidate(base, &bump, deltas[j], half, &lateral)) {
                continue;
            }
            pp_trajectory_point_t points[PP_TRAJECTORY_POINTS];
            pp_ref_samples_t samples;
            pp_output_points(ref, &lateral, speed, wheelbase, points, &samples);
            (void)pp_stitch_blend(old, s->cal, wheelbase, continuity_limit(ref), points);
            (void)pp_feasibility_limit(points, &samples, &PP_HWA_LIMITS, &s->vehicle);
            const double score = research_comfort_score(points);
            if (!(score < best_score)) {
                continue;
            }
            pp_path_check_t check;
            pp_feasibility_check(points, &samples, &check);
            if (check.ay_max <= PP_AYSMAX && check.jerk_max <= PP_JERK_MAX_HWA
                && research_geometry_ok(points, ref, old, half)) {
                (void)memcpy(out->points, points, sizeof(points));
                out->samples = samples;
                best_score = score;
                applied = true;
            }
        }
    }
    research_counts[RESEARCH_APPLIED] += applied ? 1U : 0U;
}

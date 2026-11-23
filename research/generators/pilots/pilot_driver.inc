static uint64_t pilot_calls;
static uint64_t pilot_eligible;
static uint64_t pilot_applied;

void pp_potential_reset(void);
uint64_t pp_potential_count(unsigned index);

void pp_potential_reset(void)
{
    pilot_calls = pilot_eligible = pilot_applied = 0;
}

uint64_t pp_potential_count(unsigned index)
{
    return index == 0 ? pilot_calls : (index == 1 ? pilot_eligible : pilot_applied);
}

/* Smoothstep hai bên đỉnh. d và ba đạo hàm đầu bằng 0 tại hai đầu. */
static bool pilot_bump(const pp_lateral_path_t *base, double end, double peak, double offset,
                       double corridor, pp_lateral_path_t *out)
{
    *out = *base;
    for (size_t k = 0; k < PP_TRAJECTORY_POINTS; ++k) {
        const double t = (double)k * PP_GRID_STEP_S;
        if (t > end) {
            break;
        }
        const double duration = t <= peak ? peak : end - peak;
        const double du_dt = t <= peak ? 1.0 / duration : -1.0 / duration;
        const double u = t <= peak ? t / duration : (end - t) / duration;
        const double v = 1.0 - u;
        const double u2 = u * u;
        const double v2 = v * v;
        out->d[k] += offset * u2 * u2 * (35.0 + u * (-84.0 + u * (70.0 - 20.0 * u)));
        out->d_dot[k] += offset * 140.0 * u2 * u * v2 * v * du_dt;
        out->d_ddot[k] += offset * 420.0 * u2 * v2 * (1.0 - 2.0 * u) * du_dt * du_dt;
        if (fabs(out->d[k]) > corridor) {
            return false;
        }
    }
    return true;
}

#if PP_POTENTIAL_DRIVER == 1
/* Điểm ứng viên nằm trên biên trong, nơi hướng biên song song tia từ base_link tới điểm đó. */
static double pilot_tangent(const pp_reference_line_t *ref, const pp_speed_profile_t *speed,
                            double end, double *side)
{
    pp_ref_walker_t walker;
    pp_ref_point_t point;
    pp_ref_walk_begin(&walker, ref, &point);
    double prev_angle = 0.0;
    double prev_side = 0.0;
    double prev_t = 0.0;
    for (size_t k = 8; k <= 20; ++k) {
        const double t = (double)k * PP_GRID_STEP_S;
        if (t + 0.8 > end) {
            break;
        }
        pp_ref_walk_to(&walker, speed->s[k], &point);
        if (walker.on_arc || fabs(point.kappa) < 0.0005) {
            prev_side = 0.0;
            continue;
        }
        const double dir = copysign(1.0, point.kappa);
        const double half_width = 0.5 * ref->width * dir;
        const double x = point.x - half_width * sin(point.theta);
        const double y = point.y + half_width * cos(point.theta);
        const double angle = point.theta - atan2(y, x);
        if (dir == prev_side && prev_angle * angle <= 0.0 && angle != prev_angle) {
            const double peak = prev_t + (t - prev_t) * prev_angle / (prev_angle - angle);
            if (peak >= 1.0 && peak <= 2.0) {
                *side = dir;
                return peak;
            }
        }
        prev_angle = angle;
        prev_side = dir;
        prev_t = t;
    }
    return 0.0;
}
#endif

static void pilot_driver(const pp_lcc_state_t *s, const pp_usable_inputs_t *in,
                         const pp_reference_line_t *ref, const pp_speed_profile_t *speed,
                         const pp_lcc_goal_t *goal, bool follow, double target,
                         const pp_lateral_path_t *base, pp_lcc_cycle_t *out)
{
    if (!goal->requested) {
        return;
    }
    ++pilot_calls;
    if (follow || goal->start_from_car || s->recentering || fabs(target) > 0.025
        || ref->coasting || ref->inferred || ref->line_rejected[0] || ref->line_rejected[1]
        || in->object_list == NULL || in->object_list->num_objects != 0) {
        return;
    }
    size_t last = 0;
    while (last + 1 < PP_TRAJECTORY_POINTS && out->samples.in_view[last + 1]) {
        ++last;
    }
    const double end = (double)last * PP_GRID_STEP_S;
    const double corridor = 0.5 * (ref->width - (double)s->core.vehicle.vehicle_width) - 0.30;
    pp_path_check_t base_check;
    pp_feasibility_check(out->points, &out->samples, &base_check);
    if (end < 2.0 || corridor <= 0.0 || base_check.ay_need_max >= PP_AYSMAX - 0.1
        || base_check.ay_need_max < 0.4) {
        return;
    }
    ++pilot_eligible;
    const double amplitude = fmin(0.20, 0.5 * corridor);
    double peaks[24];
    double offsets[24];
    size_t count;
#if PP_POTENTIAL_DRIVER == 1
    double side = 0.0;
    peaks[0] = pilot_tangent(ref, speed, end, &side);
    if (peaks[0] == 0.0) {
        return;
    }
    offsets[0] = side * amplitude;
    offsets[1] = 0.5 * offsets[0];
    peaks[1] = peaks[0];
    count = 2;
#elif PP_POTENTIAL_DRIVER == 2
    for (size_t i = 0; i < 4; ++i) {
        peaks[i] = end * (i < 2 ? 0.40 : 0.60);
        offsets[i] = (i % 2 == 0 ? amplitude : -amplitude);
    }
    count = 4;
    double best = base_check.ay_max + 0.10 * base_check.jerk_max;
#else
    const double fractions[] = {0.35, 0.50, 0.65};
    const double amplitudes[] = {0.04, 0.08, 0.12, 0.16};
    count = 0;
    for (size_t i = 0; i < sizeof(fractions) / sizeof(fractions[0]); ++i) {
        for (size_t k = 0; k < sizeof(amplitudes) / sizeof(amplitudes[0]); ++k) {
            const double magnitude = fmin(amplitude, amplitudes[k]);
            peaks[count] = peaks[count + 1] = end * fractions[i];
            offsets[count] = magnitude;
            offsets[count + 1] = -magnitude;
            count += 2;
        }
    }
    double best = base_check.ay_max + 0.10 * base_check.jerk_max;
#endif
    bool applied = false;
    for (size_t i = 0; i < count; ++i) {
        pp_lateral_path_t lateral;
        pp_trajectory_point_t points[PP_TRAJECTORY_POINTS];
        pp_ref_samples_t samples;
        if (!pilot_bump(base, end, peaks[i], offsets[i], corridor, &lateral)
            || !pp_output_points(ref, &lateral, speed, (double)s->core.vehicle.wheelbase,
                                 points, &samples)) {
            continue;
        }
        pp_path_check_t check;
        pp_feasibility_check(points, &samples, &check);
        if (check.ay_max > PP_AYSMAX || check.jerk_max > (double)s->core.cal->jerk_target_hwa) {
            continue;
        }
#if PP_POTENTIAL_DRIVER >= 2
        const double score = check.ay_max + 0.10 * check.jerk_max;
        if (score > best - 0.005 || check.ay_max > base_check.ay_max - 0.005) {
            continue;
        }
        best = score;
#endif
        (void)memcpy(out->points, points, sizeof(points));
        out->samples = samples;
        applied = true;
#if PP_POTENTIAL_DRIVER == 1
        break;
#endif
    }
    pilot_applied += applied;
}

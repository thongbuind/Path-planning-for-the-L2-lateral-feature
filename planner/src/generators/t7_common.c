#include <math.h>
#include <stddef.h>
#include <string.h>

#include "feasibility.h"
#include "generators/quintic.h"
#include "generators/t7_common.h"
#include "output.h"

#define PP_T_STEP_S (0.25)
#define PP_T_MAX_STEPS (32U)  /* Giới hạn số lần thử bất kể calibration T_max. */

bool pp_t7_quintic_search(const pp_calibration_t *cal, const pp_t7_input_t *in, pp_lateral_path_t *lateral,
                          pp_trajectory_point_t points[PP_TRAJECTORY_POINTS], pp_ref_samples_t *samples,
                          uint32_t *tries)
{
    const double wheelbase = (double)in->vehicle->wheelbase;
    double duration = in->recentering ? (double)cal->T_recenter : (double)cal->T_hwa;
    bool ok = false;
    bool done = false;
    uint32_t i = 0U;

    for (i = 0U; (i < PP_T_MAX_STEPS) && !done; i++) {
        pp_path_check_t check;
        ok = pp_generate_quintic(in->start, in->d_target, duration, lateral)
             && pp_output_points(in->ref, lateral, in->speed, wheelbase, points, samples);
        done = !ok;
        if (ok) {
            pp_feasibility_check(points, samples, &check);
            const bool targets_met = (check.ay_add_max <= (double)cal->ay_add_max_hwa)
                                     && (check.jerk_max <= (double)cal->jerk_target_hwa);
            done = targets_met || ((duration + PP_T_STEP_S) > ((double)cal->T_max + 1.0e-9));
            duration += PP_T_STEP_S;
        }
    }
    if (tries != NULL) {
        *tries = i;
    }
    return ok;
}

void pp_t7_qp_problem(const pp_calibration_t *cal, const pp_t7_input_t *in, pp_qp_problem_t *pb)
{
    const pp_reference_line_t *ref = in->ref;
    const pp_speed_profile_t *speed = in->speed;
    const pp_old_path_t *old = in->old;
    pp_ref_walker_t walker;
    pp_ref_point_t r;
    (void)memset(pb, 0, sizeof(*pb));
    pb->start = *in->start;
    pb->d_target = in->d_target;
    pb->ay_limit = PP_AYSMAX * (double)cal->qp_ay_margin;
    pb->jerk_limit = 0.9 * PP_JERK_MAX_HWA;
    const double half = fmax(0.0, (0.5 * ref->width) - (0.5 * (double)in->vehicle->vehicle_width)
                                  - (double)cal->qp_corridor_margin);
    pp_ref_walk_begin(&walker, ref, &r);
    for (size_t k = 0U; k < PP_QP_N; k++) {
        const size_t idx = k + 1U;
        pp_ref_walk_to(&walker, speed->s[idx], &r);
        pb->v[k] = speed->v[idx];
        pb->kappa[k] = r.kappa;
        pb->dkappa[k] = r.dkappa;
        pb->d_max[k] = half;
        pb->d_min[k] = -half;
        pp_path_sample_t sample;
        if (in->from_old && old->valid && pp_stitch_sample_old(old, (double)idx * PP_GRID_STEP_S, &sample)
            && (sample.x <= ref->view_end)) {
            pp_ref_point_t foot;
            pp_ref_project(ref, sample.x, sample.y, &foot, &pb->d_old[k]);
            pb->has_old[k] = isfinite(pb->d_old[k]);
        }
    }
}

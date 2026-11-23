#include <math.h>
#include <stddef.h>
#include <string.h>

#include "feasibility.h"
#include "generators/pp_t7.h"
#include "generators/qp.h"
#include "output.h"

void pp_t7_reset(pp_t7_ws_t *ws)
{
    if (ws != NULL) {
        pp_qp_reset(&ws->qp);
    }
}

bool pp_t7_generate(pp_t7_ws_t *ws, const pp_calibration_t *cal, const pp_t7_input_t *in,
                    pp_trajectory_point_t points[PP_TRAJECTORY_POINTS], pp_ref_samples_t *samples)
{
    const pp_reference_line_t *ref = in->ref;
    const pp_speed_profile_t *speed = in->speed;
    const pp_old_path_t *old = in->old;
    pp_qp_problem_t pb;
    pp_lateral_path_t lateral;
    pp_ref_walker_t walker;
    pp_ref_point_t r;
    (void)memset(&pb, 0, sizeof(pb));
    pb.start = *in->start;
    pb.d_target = in->d_target;
    pb.ay_limit = PP_AYSMAX * (double)cal->qp_ay_margin;
    pb.jerk_limit = 0.9 * PP_JERK_MAX_HWA;
    const double half = fmax(0.0, (0.5 * ref->width) - (0.5 * (double)in->vehicle->vehicle_width)
                                  - (double)cal->qp_corridor_margin);
    pp_ref_walk_begin(&walker, ref, &r);
    for (size_t k = 0U; k < PP_QP_N; k++) {
        const size_t idx = k + 1U;
        pp_ref_walk_to(&walker, speed->s[idx], &r);
        pb.v[k] = speed->v[idx];
        pb.kappa[k] = r.kappa;
        pb.dkappa[k] = r.dkappa;
        pb.d_max[k] = half;
        pb.d_min[k] = -half;
        pp_path_sample_t sample;
        if (in->from_old && old->valid && pp_stitch_sample_old(old, (double)idx * PP_GRID_STEP_S, &sample)
            && (sample.x <= ref->view_end)) {
            pp_ref_point_t foot;
            pp_ref_project(ref, sample.x, sample.y, &foot, &pb.d_old[k]);
            pb.has_old[k] = isfinite(pb.d_old[k]);
        }
    }
    const bool ok = pp_generate_qp(&ws->qp, cal, &pb, &lateral)
                    && pp_output_points(ref, &lateral, speed, (double)in->vehicle->wheelbase, points, samples);
    if (!ok) {
        pp_qp_reset(&ws->qp);
    }
    return ok;
}

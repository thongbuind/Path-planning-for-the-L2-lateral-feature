#include <stddef.h>
#include <stdint.h>

#include "feasibility.h"
#include "generators/pp_t7.h"
#include "generators/quintic.h"
#include "output.h"

#define PP_T_STEP_S (0.25)
#define PP_T_MAX_STEPS (32U)  /* Giới hạn số lần thử bất kể calibration T_max. */

void pp_t7_reset(pp_t7_ws_t *ws)
{
    if (ws != NULL) {
        ws->unused = 0U;
    }
}

bool pp_t7_generate(pp_t7_ws_t *ws, const pp_calibration_t *cal, const pp_t7_input_t *in,
                    pp_trajectory_point_t points[PP_TRAJECTORY_POINTS], pp_ref_samples_t *samples)
{
    const double wheelbase = (double)in->vehicle->wheelbase;
    double duration = in->recentering ? (double)cal->T_recenter : (double)cal->T_hwa;
    bool ok = false;
    bool done = false;
    (void)ws;

    for (uint32_t i = 0U; (i < PP_T_MAX_STEPS) && !done; i++) {
        pp_lateral_path_t lateral;
        pp_path_check_t check;
        ok = pp_generate_quintic(in->start, in->d_target, duration, &lateral)
             && pp_output_points(in->ref, &lateral, in->speed, wheelbase, points, samples);
        done = !ok;
        if (ok) {
            pp_feasibility_check(points, samples, &check);
            const bool targets_met = (check.ay_add_max <= (double)cal->ay_add_max_hwa)
                                     && (check.jerk_max <= (double)cal->jerk_target_hwa);
            done = targets_met || ((duration + PP_T_STEP_S) > ((double)cal->T_max + 1.0e-9));
            duration += PP_T_STEP_S;
        }
    }
    return ok;
}

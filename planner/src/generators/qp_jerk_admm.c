#include <math.h>
#include <stddef.h>
#include <stdint.h>

#include "generators/pp_t7.h"
#include "generators/qp.h"
#include "generators/t7_common.h"
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
    pp_qp_problem_t pb;
    pp_lateral_path_t lateral;
    pp_t7_qp_problem(cal, in, &pb);
    const bool ok = pp_generate_qp(&ws->qp, cal, &pb, &lateral)
                    && pp_output_points(in->ref, &lateral, in->speed, (double)in->vehicle->wheelbase, points,
                                        samples);
    if (!ok) {
        pp_qp_reset(&ws->qp);
    }
    return ok;
}

#ifdef PP_T7_TELEMETRY
void pp_t7_report(const pp_t7_ws_t *ws, pp_t7_telemetry_t *out)
{
    out->work = ws->qp.iterations;
    out->fallback = 0U;
    out->infer_ops = 0U;
    pp_qp_stats(&ws->qp, &out->residual, &out->slack);
}
#endif

/* MLP xuất thẳng chuỗi jerk. Chỉ sửa trong thư mục này (research/generators/README.md). */

#include <math.h>
#include <stddef.h>
#include <stdint.h>

#include "generators/pp_t7.h"
#include "generators/qp.h"
#include "generators/t7_common.h"
#include "mlp_features.h"
#include "mlp_infer.h"
#include "output.h"
#include "weights.h"

#define N PP_QP_N

void pp_t7_reset(pp_t7_ws_t *ws)
{
    if (ws != NULL) {
        ws->work = 0U;
        ws->fallback = 0U;
        ws->infer_ops = 0U;
        ws->clamped = 0U;
    }
}

bool pp_t7_generate(pp_t7_ws_t *ws, const pp_calibration_t *cal, const pp_t7_input_t *in,
                    pp_trajectory_point_t points[PP_TRAJECTORY_POINTS], pp_ref_samples_t *samples)
{
    pp_qp_problem_t pb;
    pp_lateral_path_t lateral;
    double features[MLP_FEATURES];
    double jerk[N];
    pp_t7_qp_problem(cal, in, &pb);
    mlp_features(&pb, features);
    ws->fallback = mlp_jerk(&MLP_MODEL, features, jerk, &ws->infer_ops);
    ws->work = (ws->fallback == MLP_OK) ? 1U : 0U;
    ws->clamped = 0U;
    bool ok = ws->fallback == MLP_OK;
    if (ok) {
        ws->clamped = mlp_clamp_jerk(&pb, jerk);
        ok = mlp_integrate(&pb, jerk, &lateral);
        if (!ok) {
            ws->fallback = MJD_NOT_FINITE_PATH;
        }
    }
    return ok && pp_output_points(in->ref, &lateral, in->speed, (double)in->vehicle->wheelbase, points, samples);
}

#ifdef PP_T7_TELEMETRY
void pp_t7_report(const pp_t7_ws_t *ws, pp_t7_telemetry_t *out)
{
    out->work = ws->work;
    out->fallback = ws->fallback;
    out->infer_ops = ws->infer_ops;
    out->residual = NAN;
    out->slack = NAN;
}
#endif

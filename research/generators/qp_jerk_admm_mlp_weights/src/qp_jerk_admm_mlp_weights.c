/* qp_jerk_admm với trọng số do MLP chọn. Chỉ sửa trong thư mục này (research/generators/README.md). */

#include <math.h>
#include <stddef.h>
#include <stdint.h>

#include "generators/pp_t7.h"
#include "generators/qp.h"
#include "generators/t7_common.h"
#include "mlp_features.h"
#include "mlpw_infer.h"
#include "mlpw_step.h"
#include "output.h"
#include "weights.h"

void pp_t7_reset(pp_t7_ws_t *ws)
{
    if (ws != NULL) {
        pp_qp_reset(&ws->qp);
        ws->have_u = false;
        ws->fallback = 0U;
        ws->infer_ops = 0U;
        for (size_t k = 0U; k < MLPW_WEIGHTS; k++) {
            ws->u[k] = 0.0;
        }
    }
}

const mlpw_model_t *mlpw_model(const pp_calibration_t *cal)
{
    const double level = log10(fmax((double)cal->mlpw_regularisation, 1.0e-30));
    size_t best = 0U;
    for (size_t i = 1U; i < MLPW_MODEL_COUNT; i++) {
        if (fabs(level - mlpw_levels[i]) < fabs(level - mlpw_levels[best])) {
            best = i;
        }
    }
    return mlpw_models[best];
}

static double clamp(double v, double lo, double hi)
{
    return (v < lo) ? lo : ((v > hi) ? hi : v);
}

/* Dải kẹp của u từ calibration của generator. */
static void limits(const pp_calibration_t *cal, double lo[MLPW_OUTPUTS], double hi[MLPW_OUTPUTS])
{
    lo[0] = log((double)cal->mlpw_w_dev_min);
    hi[0] = log((double)cal->mlpw_w_dev_max);
    lo[1] = log((double)cal->mlpw_w_jerk_min);
    hi[1] = log((double)cal->mlpw_w_jerk_max);
    lo[2] = (double)cal->mlpw_a_comfort_min;
    hi[2] = (double)cal->mlpw_a_comfort_max;
}

static void default_u(const pp_calibration_t *cal, double u[MLPW_OUTPUTS])
{
    u[0] = log((double)cal->qp_w_dev);
    u[1] = log((double)cal->qp_w_jerk);
    u[2] = (double)cal->qp_a_comfort;
}

uint32_t mlpw_target(const pp_calibration_t *cal, const pp_qp_problem_t *pb, double target[MLPW_OUTPUTS],
                     uint32_t *ops)
{
    double features[MLP_FEATURES];
    double lo[MLPW_OUTPUTS];
    double hi[MLPW_OUTPUTS];
    mlp_features(pb, features);
    const uint32_t code = mlpw_infer(mlpw_model(cal), features, target, ops);
    if (code != MLPW_OK) {
        default_u(cal, target);
    }
    limits(cal, lo, hi);
    for (size_t k = 0U; k < MLPW_OUTPUTS; k++) {
        target[k] = clamp(target[k], lo[k], hi[k]);
    }
    return code;
}

void mlpw_apply(pp_t7_ws_t *ws, const pp_calibration_t *cal, const double target[MLPW_OUTPUTS],
                pp_calibration_t *out)
{
    double lo[MLPW_OUTPUTS];
    double hi[MLPW_OUTPUTS];
    if (!ws->have_u) {
        default_u(cal, ws->u);
        ws->have_u = true;
    }
    limits(cal, lo, hi);
    const double rate[MLPW_OUTPUTS] = {(double)cal->mlpw_rate_log, (double)cal->mlpw_rate_log,
                                       (double)cal->mlpw_rate_ac};
    for (size_t k = 0U; k < MLPW_OUTPUTS; k++) {
        const double step = clamp(target[k] - ws->u[k], -rate[k], rate[k]);
        ws->u[k] = clamp(ws->u[k] + step, lo[k], hi[k]);
    }
    *out = *cal;
    out->qp_w_dev = (float)exp(ws->u[0]);
    out->qp_w_jerk = (float)exp(ws->u[1]);
    out->qp_a_comfort = (float)ws->u[2];
}

bool pp_t7_generate(pp_t7_ws_t *ws, const pp_calibration_t *cal, const pp_t7_input_t *in,
                    pp_trajectory_point_t points[PP_TRAJECTORY_POINTS], pp_ref_samples_t *samples)
{
    pp_qp_problem_t pb;
    pp_lateral_path_t lateral;
    pp_calibration_t chosen;
    double target[MLPW_OUTPUTS];
    pp_t7_qp_problem(cal, in, &pb);
    ws->fallback = mlpw_target(cal, &pb, target, &ws->infer_ops);
    mlpw_apply(ws, cal, target, &chosen);
    const bool ok = pp_generate_qp(&ws->qp, &chosen, &pb, &lateral)
                    && pp_output_points(in->ref, &lateral, in->speed, (double)in->vehicle->wheelbase, points,
                                        samples);
    if (!ok) {
        pp_qp_reset(&ws->qp);  /* Trọng số giữ nguyên: chúng không gây lỗi và vẫn là điểm xuất phát hợp lệ. */
    }
    return ok;
}

#ifdef PP_T7_TELEMETRY
void pp_t7_report(const pp_t7_ws_t *ws, pp_t7_telemetry_t *out)
{
    out->work = ws->qp.iterations;
    out->fallback = ws->fallback;
    out->infer_ops = ws->infer_ops;
    pp_qp_stats(&ws->qp, &out->residual, &out->slack);
}
#endif

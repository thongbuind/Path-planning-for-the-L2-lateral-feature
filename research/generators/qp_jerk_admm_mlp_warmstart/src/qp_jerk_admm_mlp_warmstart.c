/* qp_jerk_admm với warm start do MLP dự đoán. Chỉ sửa trong thư mục này (research/generators/README.md). */

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
/* Hàm dịch của luồng A, dùng nguyên; nguồn shift.c có trong generator.cmake. */
#include "../../qp_jerk_admm_shift_warmstart/src/shift.h"

#define N PP_QP_N

void pp_t7_reset(pp_t7_ws_t *ws)
{
    if (ws != NULL) {
        pp_qp_reset(&ws->qp);
        ws->follow_last = false;
        ws->fallback = 0U;
        ws->infer_ops = 0U;
        ws->shifted = false;
    }
}

/* Nghiệm trước dịch được khi đó là lần giải của chu kỳ trước trên cùng đường tham chiếu và điểm đầu nằm trên
 * path cũ: cùng điều kiện với qp_jerk_admm_shift_warmstart. */
static bool can_shift(const pp_t7_ws_t *ws, const pp_t7_input_t *in)
{
    return ws->qp.warm && (ws->qp.rho > 0.0) && !in->start_from_car && in->from_old && (in->old != NULL)
           && in->old->valid && (in->follow == ws->follow_last) && isfinite(in->old->shift_s)
           && (in->old->shift_s > 0.0);
}

/* Dịch các khối N phần tử của x từ khối first (0 jerk, 1 nới a_y, 2 nới hành lang). Chỉ dịch biến gốc:
 * luồng A đo được dịch cả biến đối ngẫu y làm warm start tệ hơn, nên y giữ nguyên như qp_jerk_admm. */
static void shift(pp_qp_ws_t *qp, size_t first, double dt)
{
    for (size_t b = first; b < 3U; b++) {
        (void)sws_shift_hold(&qp->x[b * N], &qp->x[b * N], N, PP_GRID_STEP_S, dt);
    }
}

bool pp_t7_generate(pp_t7_ws_t *ws, const pp_calibration_t *cal, const pp_t7_input_t *in,
                    pp_trajectory_point_t points[PP_TRAJECTORY_POINTS], pp_ref_samples_t *samples)
{
    pp_qp_problem_t pb;
    pp_lateral_path_t lateral;
    double features[MLP_FEATURES];
    double seed[N];
    pp_t7_qp_problem(cal, in, &pb);
    const bool shiftable = can_shift(ws, in);
    /* qmw_seed_mode = 1: chỉ suy luận khi không có nghiệm trước dịch được (khởi động, override, đổi follow). */
    if ((cal->qmw_seed_mode > 0.5F) && shiftable) {
        ws->fallback = QMW_SHIFT_PREFERRED;
        ws->infer_ops = 0U;
    } else {
        mlp_features(&pb, features);
        ws->fallback = mlp_jerk(&MLP_MODEL, features, seed, &ws->infer_ops);
    }
    bool solved = false;
    if (ws->fallback == MLP_OK) {
        (void)mlp_clamp_jerk(&pb, seed);
        ws->shifted = shiftable && (cal->qmw_slack_shift > 0.5F);
        if (ws->shifted) {
            shift(&ws->qp, 1U, in->old->shift_s);  /* Jerk lấy từ MLP; chỉ dịch hai khối biến nới. */
        }
        solved = pp_generate_qp_seeded(&ws->qp, cal, &pb, seed, &lateral);
    } else {
        /* Ngoài miền hoặc QMW_SHIFT_PREFERRED: warm start dịch thời gian của luồng A (sws_shift_vars = 1: ba
         * khối x, không dịch y). */
        ws->shifted = shiftable;
        if (shiftable) {
            shift(&ws->qp, 0U, in->old->shift_s);
        }
        solved = pp_generate_qp(&ws->qp, cal, &pb, &lateral);
    }
    const bool ok = solved && pp_output_points(in->ref, &lateral, in->speed, (double)in->vehicle->wheelbase,
                                               points, samples);
    if (!ok) {
        pp_qp_reset(&ws->qp);
    }
    ws->follow_last = in->follow;
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

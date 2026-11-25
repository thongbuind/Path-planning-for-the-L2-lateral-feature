/* qp_jerk_admm với warm start dịch thời gian. Chỉ sửa trong thư mục này (research/generators/README.md). */

#include <math.h>
#include <stddef.h>
#include <stdint.h>

#include "generators/pp_t7.h"
#include "generators/qp.h"
#include "generators/t7_common.h"
#include "output.h"
#include "shift.h"

#define N PP_QP_N

void pp_t7_reset(pp_t7_ws_t *ws)
{
    if (ws != NULL) {
        pp_qp_reset(&ws->qp);
        ws->follow_last = false;
        ws->fallback = SWS_NO_WARM;
    }
}

/* Nghiệm trước chỉ dịch được khi nó là lần giải của chu kỳ có path cũ, và điểm đầu nằm trên path cũ. */
static uint32_t shift_reason(const pp_t7_ws_t *ws, const pp_t7_input_t *in)
{
    uint32_t reason = SWS_SHIFTED;
    if (!ws->qp.warm || !(ws->qp.rho > 0.0)) {
        reason = SWS_NO_WARM;
    } else if (in->start_from_car) {
        reason = SWS_FROM_CAR;
    } else if (!in->from_old || !in->old->valid) {
        reason = SWS_NOT_FROM_OLD;
    } else if (in->follow != ws->follow_last) {
        reason = SWS_FOLLOW_CHANGED;
    } else if (!(isfinite(in->old->shift_s) && (in->old->shift_s > 0.0))) {
        reason = SWS_BAD_SHIFT;
    } else {
    }
    return reason;
}

/* Dịch từng khối N phần tử của x (jerk, nới a_y, nới hành lang) và y (8 nhóm hàng), cùng một dt. Mọi
 * khối đều theo chỉ số thời gian k nên dịch cùng một công thức. */
static void shift_blocks(double *v, size_t blocks, double dt)
{
    for (size_t b = 0U; b < blocks; b++) {
        (void)sws_shift_hold(&v[b * N], &v[b * N], N, PP_GRID_STEP_S, dt);
    }
}

bool pp_t7_generate(pp_t7_ws_t *ws, const pp_calibration_t *cal, const pp_t7_input_t *in,
                    pp_trajectory_point_t points[PP_TRAJECTORY_POINTS], pp_ref_samples_t *samples)
{
    pp_qp_problem_t pb;
    pp_lateral_path_t lateral;
    pp_t7_qp_problem(cal, in, &pb);
    ws->fallback = shift_reason(ws, in);
    if (ws->fallback == SWS_SHIFTED) {
        const double dt = in->old->shift_s;
        const float vars = cal->sws_shift_vars;
        shift_blocks(ws->qp.x, (vars < 0.5F) ? 1U : 3U, dt);
        if (vars > 1.5F) {
            shift_blocks(ws->qp.y, PP_QP_ROWS / N, dt);
        }
    }
    const bool ok = pp_generate_qp(&ws->qp, cal, &pb, &lateral)
                    && pp_output_points(in->ref, &lateral, in->speed, (double)in->vehicle->wheelbase, points,
                                        samples);
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
    out->infer_ops = 0U;
    pp_qp_stats(&ws->qp, &out->residual, &out->slack);
}
#endif

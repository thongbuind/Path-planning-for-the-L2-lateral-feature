/* Teacher của luồng C: lái như qp_jerk_admm, ghi đặc trưng và nhãn 1000 vòng. Chỉ sửa trong thư mục này. */

#include <math.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "generators/pp_t7.h"
#include "generators/qp.h"
#include "generators/t7_common.h"
#include "mlp_features.h"
#ifdef TEACHER_DRIVE_MLP
#include "mlp_infer.h"
#include "weights.h"
#endif
#include "output.h"

#define N PP_QP_N
#define DT PP_GRID_STEP_S
#define QP_MIN_Q (0.1)  /* Như qp.c. */

void pp_t7_reset(pp_t7_ws_t *ws)
{
    if (ws != NULL) {
        pp_qp_reset(&ws->qp);
        ws->ref.warm = false;
        ws->ref.rho = 0.0;
    }
}

void teacher_pack_problem(const pp_qp_problem_t *pb, double out[TR_PROBLEM_SIZE])
{
    out[0] = pb->start.d;
    out[1] = pb->start.d_dot;
    out[2] = pb->start.d_ddot;
    out[3] = pb->start.heading;
    out[4] = pb->d_target;
    for (size_t k = 0U; k < N; k++) {
        out[5U + k] = pb->v[k];
        out[5U + N + k] = pb->kappa[k];
        out[5U + (2U * N) + k] = pb->dkappa[k];
        out[5U + (3U * N) + k] = pb->d_max[k];
        out[5U + (4U * N) + k] = pb->d_min[k];
        out[5U + (5U * N) + k] = pb->d_old[k];
        out[5U + (6U * N) + k] = pb->has_old[k] ? 1.0 : 0.0;
    }
    out[5U + (7U * N)] = pb->ay_limit;
    out[6U + (7U * N)] = pb->jerk_limit;
}

static double ramp(const pp_calibration_t *cal, size_t k)
{
    return fmin(1.0, ((double)(k + 1U) * DT) / (double)cal->qp_T_ramp);
}

static double max_abs(const double *v, size_t n)
{
    double m = 0.0;
    for (size_t i = 0U; i < n; i++) {
        m = fmax(m, fabs(v[i]));
    }
    return m;
}

void teacher_check(const pp_qp_ws_t *ws, const pp_calibration_t *cal, const pp_qp_problem_t *pb,
                   double d_target_before, bool warm_before, double *dual, double *viol_ay, double *viol_jerk)
{
    const double d0 = pb->start.d;
    const double v0 = pb->start.d_dot;
    const double a0 = pb->start.d_ddot;
    const double eps = 0.5 * (double)cal->epsilon_ay;
    const double keep = pb->ay_limit - eps;
    const double shift = warm_before ? (pb->d_target - d_target_before) : 0.0;
    const double *j = &ws->x[0];
    const double *y = ws->y;
    double rd[N];
    double d_free[N];
    double q[N];
    *viol_ay = 0.0;
    *viol_jerk = 0.0;
    /* Giới hạn hàng a_y và jerk, chép từ bounds() của qp.c. */
    for (size_t k = 0U; k < N; k++) {
        const double t = (double)(k + 1U) * DT;
        d_free[k] = d0 + (v0 * t) + (0.5 * a0 * t * t);
        const double need = pb->v[k] * pb->v[k] * pb->kappa[k];
        rd[k] = ((double)cal->qp_w_dev * ramp(cal, k) * (d_free[k] - pb->d_target))
                + (pb->has_old[k] ? ((double)cal->qp_w_cont * (d_free[k] - (pb->d_old[k] + shift))) : 0.0);
        const double d_bar = pb->has_old[k] ? pb->d_old[k] : d_free[k];
        const double qk = fmax(1.0 - (pb->kappa[k] * d_bar), QP_MIN_Q);
        const double q2 = qk * qk;
        const double ref = need / qk;
        const double lo_ay = (need > keep) ? (fmin(need, pb->ay_limit) - eps) : -pb->ay_limit;
        const double hi_ay = (need < -keep) ? (fmax(need, -pb->ay_limit) + eps) : pb->ay_limit;
        const double lo_a = (q2 * (lo_ay - ref)) - a0;
        const double hi_a = (q2 * (hi_ay - ref)) - a0;
        const double jerk_ref = pb->v[k] * pb->v[k] * pb->v[k] * pb->dkappa[k];
        double a = 0.0;
        for (size_t i = 0U; i <= k; i++) {
            a += ws->ma[k][i] * j[i];
        }
        *viol_ay = fmax(*viol_ay, fmax(lo_a - a, a - hi_a));
        *viol_jerk = fmax(*viol_jerk, fmax((-pb->jerk_limit - jerk_ref) - j[k], j[k] - (pb->jerk_limit - jerk_ref)));
    }
    const double v_free_end = v0 + (a0 * (double)N * DT);
    for (size_t i = 0U; i < N; i++) {
        double sum = 0.0;
        for (size_t k = i; k < N; k++) {
            sum += ws->md[k][i] * rd[k];
        }
        q[i] = sum + ((double)cal->qp_w_term_d * ws->md[N - 1U][i] * (d_free[N - 1U] - pb->d_target))
               + ((double)cal->qp_w_term_v * ws->mv[i] * v_free_end);
    }
    /* Residual đối ngẫu P x + q + Aᵀ y trên cả ba khối biến, chuẩn hóa như next_rho() của qp.c. */
    double px[3U * N];
    double aty[3U * N];
    double r[3U * N];
    double qa[3U * N];
    for (size_t i = 0U; i < N; i++) {
        double sum = 0.0;
        for (size_t b = 0U; b < N; b++) {
            sum += ws->p[i][b] * j[b];
        }
        px[i] = sum;
        px[N + i] = (double)cal->qp_w_comfort * ws->x[N + i];
        px[(2U * N) + i] = (double)cal->qp_w_corridor * ws->x[(2U * N) + i];
        double at = 0.0;
        for (size_t k = i; k < N; k++) {
            at += ws->ma[k][i] * (y[k] + y[N + k] + y[(2U * N) + k]);
            at += ws->md[k][i] * (y[(5U * N) + k] + y[(6U * N) + k]);
        }
        aty[i] = at + y[(7U * N) + i];
        aty[N + i] = -y[N + i] + y[(2U * N) + i] + y[(3U * N) + i];
        aty[(2U * N) + i] = y[(4U * N) + i] - y[(5U * N) + i] + y[(6U * N) + i];
        qa[i] = q[i];
        qa[N + i] = 0.0;
        qa[(2U * N) + i] = 0.0;
    }
    for (size_t i = 0U; i < (3U * N); i++) {
        r[i] = px[i] + qa[i] + aty[i];
    }
    *dual = max_abs(r, 3U * N)
            / fmax(fmax(max_abs(px, 3U * N), max_abs(aty, 3U * N)), fmax(max_abs(qa, 3U * N), 1.0e-9));
}

/* Nghiệm nhãn: chuỗi warm start riêng, TEACHER_REF_ITERS vòng, cùng bài toán và trọng số. */
static void label(pp_t7_ws_t *ws, const pp_calibration_t *cal, const pp_qp_problem_t *pb)
{
    double *rec = ws->record;
    teacher_chain_t *chain = &ws->ref;
    pp_qp_ws_t solver;
    (void)memset(&solver, 0, sizeof(solver));
    (void)memcpy(solver.x, chain->x, sizeof(solver.x));
    (void)memcpy(solver.z, chain->z, sizeof(solver.z));
    (void)memcpy(solver.y, chain->y, sizeof(solver.y));
    solver.rho = chain->rho;
    solver.d_target = chain->d_target;
    solver.warm = chain->warm;
    pp_calibration_t ref_cal = *cal;
    ref_cal.qp_iters = (float)TEACHER_REF_ITERS;
    const bool warm_flag = chain->warm;  /* bounds() của qp.c dời path cũ theo cờ này. */
    rec[TR_REF_WARM] = (warm_flag && (chain->rho > 0.0)) ? 1.0 : 0.0;
    rec[TR_REF_DTARGET] = chain->d_target;
    pp_lateral_path_t lateral;
    const bool ok = pp_generate_qp(&solver, &ref_cal, pb, &lateral);
    rec[TR_LABEL_OK] = ok ? 1.0 : 0.0;
    if (ok) {
        double dual = NAN;
        double viol_ay = NAN;
        double viol_jerk = NAN;
        pp_qp_stats(&solver, &rec[TR_PRIMAL], &rec[TR_SLACK]);
        teacher_check(&solver, &ref_cal, pb, chain->d_target, warm_flag, &dual, &viol_ay, &viol_jerk);
        rec[TR_DUAL] = dual;
        rec[TR_VIOL_AY] = viol_ay;
        rec[TR_VIOL_JERK] = viol_jerk;
        rec[TR_VIOLATION] = fmax(viol_ay, viol_jerk);
        (void)memcpy(&rec[TR_LABEL], solver.x, sizeof(double) * N);
        (void)memcpy(chain->x, solver.x, sizeof(chain->x));
        (void)memcpy(chain->z, solver.z, sizeof(chain->z));
        (void)memcpy(chain->y, solver.y, sizeof(chain->y));
        chain->rho = solver.rho;
        chain->d_target = solver.d_target;
        chain->warm = solver.warm;
    } else {
        chain->warm = false;
        chain->rho = 0.0;
        rec[TR_PRIMAL] = NAN;
        rec[TR_DUAL] = NAN;
        rec[TR_VIOLATION] = NAN;
        rec[TR_VIOL_AY] = NAN;
        rec[TR_VIOL_JERK] = NAN;
        rec[TR_SLACK] = NAN;
        for (size_t k = 0U; k < N; k++) {
            rec[TR_LABEL + k] = NAN;
        }
    }
}

bool pp_t7_generate(pp_t7_ws_t *ws, const pp_calibration_t *cal, const pp_t7_input_t *in,
                    pp_trajectory_point_t points[PP_TRAJECTORY_POINTS], pp_ref_samples_t *samples)
{
    pp_qp_problem_t pb;
    pp_lateral_path_t lateral;
    double *rec = ws->record;
    pp_t7_qp_problem(cal, in, &pb);
    rec[TR_LAYOUT] = TEACHER_LAYOUT;
    rec[TR_SIZE] = (double)TR_DOUBLES;
    rec[TR_COUNT] += 1.0;
    rec[TR_FROM_OLD] = in->from_old ? 1.0 : 0.0;
    rec[TR_RECENTERING] = in->recentering ? 1.0 : 0.0;
    rec[TR_FOLLOW] = in->follow ? 1.0 : 0.0;
    rec[TR_FROM_CAR] = in->start_from_car ? 1.0 : 0.0;
    rec[TR_SHIFT_S] = (in->old != NULL && in->old->valid) ? in->old->shift_s : NAN;
    rec[TR_DRIVE_WARM] = (ws->qp.warm && (ws->qp.rho > 0.0)) ? 1.0 : 0.0;
    mlp_features(&pb, &rec[TR_FEATURES]);
    teacher_pack_problem(&pb, &rec[TR_PROBLEM]);
    label(ws, cal, &pb);

#ifdef TEACHER_DRIVE_MLP
    /* Vòng DAgger: lái bằng mlp_jerk_direct (MLP vòng trước) để nhãn phủ các trạng thái do chính MLP gây ra;
     * ngoài miền thì lái bằng QP như dưới (chỉ để thu dữ liệu). TR_DRIVE_ITERS = 0 đánh dấu chu kỳ MLP lái. */
    double jerk[N];
    if (mlp_jerk(&MLP_MODEL, &rec[TR_FEATURES], jerk, NULL) == MLP_OK) {
        (void)mlp_clamp_jerk(&pb, jerk);
        const bool driven = mlp_integrate(&pb, jerk, &lateral);
        pp_qp_reset(&ws->qp);
        rec[TR_DRIVE_OK] = driven ? 1.0 : 0.0;
        rec[TR_DRIVE_ITERS] = 0.0;
        for (size_t k = 0U; k < N; k++) {
            rec[TR_DRIVE + k] = driven ? jerk[k] : NAN;
        }
        return driven && pp_output_points(in->ref, &lateral, in->speed, (double)in->vehicle->wheelbase, points,
                                          samples);
    }
#endif
    /* Lái: giống hệt qp_jerk_admm. */
    const bool solved = pp_generate_qp(&ws->qp, cal, &pb, &lateral);
    rec[TR_DRIVE_OK] = solved ? 1.0 : 0.0;
    rec[TR_DRIVE_ITERS] = (double)ws->qp.iterations;
    for (size_t k = 0U; k < N; k++) {
        rec[TR_DRIVE + k] = solved ? ws->qp.x[k] : NAN;
    }
    const bool ok = solved && pp_output_points(in->ref, &lateral, in->speed, (double)in->vehicle->wheelbase,
                                               points, samples);
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

/* Công cụ offline của qp_jerk_admm_mlp_weights: giải lại bài toán QP của một cửa sổ (bố cục TR_PROBLEM của teacher)
 * bằng đúng qp.c của planner, với trọng số (qp_w_dev, qp_w_jerk, qp_a_comfort) cho trước. Không vào planner; chỉ
 * resolve.py nạp qua ctypes để tạo nhãn lưới trọng số. Calibration còn lại là giá trị mặc định (pp_calibration). */

#include <math.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#include "generators/qp.h"
#include "pp_calibration.h"

#define N PP_QP_N
#define DT PP_GRID_STEP_S
#define QP_MIN_Q (0.1)  /* Như qp.c. */

/* Số double của một bài toán theo bố cục TR_PROBLEM (research/generators/mlp/common.py). */
#define RESOLVE_PROBLEM_SIZE (5U + (7U * N) + 2U)
/* stats: primal, dual, vi phạm hàng a_y cứng, vi phạm hàng jerk cứng, slack. */
#define RESOLVE_STATS (5U)

int mlpw_problem_size(void);
int mlpw_horizon(void);
int mlpw_resolve(const double *problem, int warm, double d_target_before, double w_dev, double w_jerk,
                 double a_comfort, int iters, double *jerk, double *stats);

int mlpw_problem_size(void)
{
    return (int)RESOLVE_PROBLEM_SIZE;
}

int mlpw_horizon(void)
{
    return (int)N;
}

static void unpack(const double *p, pp_qp_problem_t *pb)
{
    (void)memset(pb, 0, sizeof(*pb));
    pb->start.d = p[0];
    pb->start.d_dot = p[1];
    pb->start.d_ddot = p[2];
    pb->start.heading = p[3];
    pb->d_target = p[4];
    for (size_t k = 0U; k < N; k++) {
        pb->v[k] = p[5U + k];
        pb->kappa[k] = p[5U + N + k];
        pb->dkappa[k] = p[5U + (2U * N) + k];
        pb->d_max[k] = p[5U + (3U * N) + k];
        pb->d_min[k] = p[5U + (4U * N) + k];
        pb->d_old[k] = p[5U + (5U * N) + k];
        pb->has_old[k] = p[5U + (6U * N) + k] > 0.5;
    }
    pb->ay_limit = p[5U + (7U * N)];
    pb->jerk_limit = p[6U + (7U * N)];
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

/* Residual đối ngẫu tương đối và vi phạm hàng cứng của nghiệm trong ws: cùng công thức với teacher_check của
 * qp_jerk_admm_teacher (giới hạn và q tính lại như bounds() của qp.c). */
static void check(const pp_qp_ws_t *ws, const pp_calibration_t *cal, const pp_qp_problem_t *pb, double shift,
                  double *dual, double *viol_ay, double *viol_jerk)
{
    const double d0 = pb->start.d;
    const double v0 = pb->start.d_dot;
    const double a0 = pb->start.d_ddot;
    const double eps = 0.5 * (double)cal->epsilon_ay;
    const double keep = pb->ay_limit - eps;
    const double *j = &ws->x[0];
    const double *y = ws->y;
    double rd[N];
    double d_free[N];
    double q[N];
    *viol_ay = 0.0;
    *viol_jerk = 0.0;
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

/* Giải khởi động lạnh (x, y = 0, rho = qp_rho0) với iters vòng. warm và d_target_before tái tạo phép dời path cũ
 * của bounds() trong qp.c (shift = d_target − d_target_before khi chuỗi nhãn của teacher đang warm). Trả 1 nếu nghiệm
 * hữu hạn; jerk nhận N phần tử, stats nhận RESOLVE_STATS phần tử. */
int mlpw_resolve(const double *problem, int warm, double d_target_before, double w_dev, double w_jerk,
                 double a_comfort, int iters, double *jerk, double *stats)
{
    static pp_qp_ws_t ws;  /* Chỉ công cụ offline (một luồng); planner không dùng tệp này. */
    pp_qp_problem_t pb;
    pp_lateral_path_t path;
    pp_calibration_t cal = pp_calibration;
    unpack(problem, &pb);
    cal.qp_w_dev = (float)w_dev;
    cal.qp_w_jerk = (float)w_jerk;
    cal.qp_a_comfort = (float)a_comfort;
    cal.qp_iters = (float)iters;
    (void)memset(&ws, 0, sizeof(ws));
    /* warm = true với rho = 0: qp.c vẫn khởi động lạnh nhưng bounds() dời path cũ như chuỗi nhãn của teacher. */
    ws.warm = (warm != 0);
    ws.rho = 0.0;
    ws.d_target = d_target_before;
    const double shift = (warm != 0) ? (pb.d_target - d_target_before) : 0.0;
    const bool ok = pp_generate_qp(&ws, &cal, &pb, &path);
    for (size_t k = 0U; k < N; k++) {
        jerk[k] = ok ? ws.x[k] : NAN;
    }
    if (ok) {
        double slack = 0.0;
        pp_qp_stats(&ws, &stats[0], &slack);
        check(&ws, &cal, &pb, shift, &stats[1], &stats[2], &stats[3]);
        stats[4] = slack;
    } else {
        for (size_t i = 0U; i < RESOLVE_STATS; i++) {
            stats[i] = NAN;
        }
    }
    return ok ? 1 : 0;
}

/* T7 technique C: unified QP solved by ADMM (generators/qp.h). */

#include <math.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "generators/qp.h"

#define N PP_QP_N
#define DT PP_GRID_STEP_S
#define QP_INF (1.0e9)
#define QP_MIN_Q (0.1)            /* Smallest 1 - kappa d, as in T11 */
#define QP_SIGMA (1.0e-6)          /* ADMM regularisation of x */
#define QP_ALPHA (1.6)             /* Over-relaxation */
#define QP_RHO_EVERY (25U)         /* Iterations between rho updates */
#define QP_RHO_MIN (1.0e-3)
#define QP_RHO_MAX (1.0e4)
#define QP_RHO_CHANGE (5.0)        /* Refactor only when rho changes by this factor */
/* rho of each row block relative to ws->rho (row scaling as in OSQP): the a_y rows bind
 * near aysmax and need a stiffer penalty, the jerk rows a softer one. Equal within the
 * pairs a-s, a+s and d-e, d+e, so the KKT matrix stays block diagonal. */
static const double rho_block[8] = {10.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.1};

void pp_qp_reset(pp_qp_ws_t *ws)
{
    if (ws != NULL) {
        ws->warm = false;
        ws->rho = 0.0;
    }
}

/* Exact integration of piecewise-constant jerk: d''(t_k), d(t_k), d'(t_N) per unit jerk. */
static void integrators(pp_qp_ws_t *ws)
{
    for (size_t k = 0U; k < N; k++) {
        const double t = (double)(k + 1U) * DT;
        for (size_t i = 0U; i < N; i++) {
            const double tau = t - ((double)i * DT);
            const bool before = i <= k;
            ws->ma[k][i] = before ? DT : 0.0;
            ws->md[k][i] = before ? (((tau * tau * tau) - ((tau - DT) * (tau - DT) * (tau - DT))) / 6.0)
                                  : 0.0;
        }
    }
    for (size_t i = 0U; i < N; i++) {
        const double tau = ((double)N * DT) - ((double)i * DT);
        ws->mv[i] = ((tau * tau) - ((tau - DT) * (tau - DT))) / 2.0;
    }
}

static double ramp(const pp_calibration_t *cal, size_t k)
{
    const double t = (double)(k + 1U) * DT;
    return fmin(1.0, t / (double)cal->qp_T_ramp);
}

/* P_jj = w_jerk dt I + Md' (w_dev R + w_cont C) Md + w_term_d md md' + w_term_v mv mv',
 * C the points where the previous path is known. */
static void jerk_cost(pp_qp_ws_t *ws, const pp_calibration_t *cal, const pp_qp_problem_t *pb)
{
    for (size_t a = 0U; a < N; a++) {
        for (size_t b = 0U; b < N; b++) {
            double sum = 0.0;
            for (size_t k = 0U; k < N; k++) {
                const double w = ((double)cal->qp_w_dev * ramp(cal, k))
                                 + (pb->has_old[k] ? (double)cal->qp_w_cont : 0.0);
                sum += w * ws->md[k][a] * ws->md[k][b];
            }
            ws->p[a][b] = sum
                + ((double)cal->qp_w_term_d * ws->md[N - 1U][a] * ws->md[N - 1U][b])
                + ((double)cal->qp_w_term_v * ws->mv[a] * ws->mv[b])
                + ((a == b) ? ((double)cal->qp_w_jerk * DT) : 0.0);
        }
    }
}

/* Cholesky of K_jj = P_jj + sigma I + rho (ra Ma'Ma + rd Md'Md + rj I), ra, rd, rj the sums of
 * rho_block over the rows of a and d and the jerk rows. False if not positive definite. */
static bool factor(pp_qp_ws_t *ws)
{
    for (size_t a = 0U; a < N; a++) {
        for (size_t b = 0U; b <= a; b++) {
            double ata = 0.0;
            for (size_t k = 0U; k < N; k++) {
                ata += ((rho_block[0] + rho_block[1] + rho_block[2]) * ws->ma[k][a] * ws->ma[k][b])
                       + ((rho_block[5] + rho_block[6]) * ws->md[k][a] * ws->md[k][b]);
            }
            double sum = ws->p[a][b] + (ws->rho * ata) + ((a == b) ? (QP_SIGMA + (rho_block[7] * ws->rho)) : 0.0);
            for (size_t c = 0U; c < b; c++) {
                sum -= ws->l[a][c] * ws->l[b][c];
            }
            if (a == b) {
                if (!(sum > 0.0)) {
                    return false;
                }
                ws->l[a][a] = sqrt(sum);
            } else {
                ws->l[a][b] = sum / ws->l[b][b];
            }
        }
        for (size_t b = a + 1U; b < N; b++) {
            ws->l[a][b] = 0.0;
        }
    }
    return true;
}

static void chol_solve(const pp_qp_ws_t *ws, double r[N])
{
    for (size_t a = 0U; a < N; a++) {
        double sum = r[a];
        for (size_t c = 0U; c < a; c++) {
            sum -= ws->l[a][c] * r[c];
        }
        r[a] = sum / ws->l[a][a];
    }
    for (size_t i = N; i > 0U; i--) {
        const size_t a = i - 1U;
        double sum = r[a];
        for (size_t c = a + 1U; c < N; c++) {
            sum -= ws->l[c][a] * r[c];
        }
        r[a] = sum / ws->l[a][a];
    }
}

/* z = A x, rows in 8 blocks: a, a-s, a+s, s, e, d-e, d+e, j (a = Ma j, d = Md j). */
static void mul_a(const pp_qp_ws_t *ws, const double x[3U * N], double z[PP_QP_ROWS])
{
    const double *j = &x[0];
    const double *s = &x[N];
    const double *e = &x[2U * N];
    for (size_t k = 0U; k < N; k++) {
        double a = 0.0;
        double d = 0.0;
        for (size_t i = 0U; i <= k; i++) {
            a += ws->ma[k][i] * j[i];
            d += ws->md[k][i] * j[i];
        }
        z[k] = a;
        z[N + k] = a - s[k];
        z[(2U * N) + k] = a + s[k];
        z[(3U * N) + k] = s[k];
        z[(4U * N) + k] = e[k];
        z[(5U * N) + k] = d - e[k];
        z[(6U * N) + k] = d + e[k];
        z[(7U * N) + k] = j[k];
    }
}

/* out = A' y. */
static void mul_at(const pp_qp_ws_t *ws, const double y[PP_QP_ROWS], double out[3U * N])
{
    for (size_t i = 0U; i < N; i++) {
        double sum = 0.0;
        for (size_t k = i; k < N; k++) {
            sum += ws->ma[k][i] * (y[k] + y[N + k] + y[(2U * N) + k]);
            sum += ws->md[k][i] * (y[(5U * N) + k] + y[(6U * N) + k]);
        }
        out[i] = sum + y[(7U * N) + i];
        out[N + i] = -y[N + i] + y[(2U * N) + i] + y[(3U * N) + i];
        out[(2U * N) + i] = y[(4U * N) + i] - y[(5U * N) + i] + y[(6U * N) + i];
    }
}

static double rho_row(const pp_qp_ws_t *ws, size_t r)
{
    return rho_block[r / N] * ws->rho;
}

static double clamp(double v, double lo, double hi)
{
    return (v < lo) ? lo : ((v > hi) ? hi : v);
}

static double max_abs(const double *v, size_t n)
{
    double m = 0.0;
    for (size_t i = 0U; i < n; i++) {
        m = fmax(m, fabs(v[i]));
    }
    return m;
}

typedef struct {
    double q[3U * N];
    double lo[PP_QP_ROWS];
    double hi[PP_QP_ROWS];
    double d_free[N];              /* d(t_k) with zero jerk */
} qp_data_t;

static void bounds(const pp_qp_ws_t *ws, const pp_calibration_t *cal, const pp_qp_problem_t *pb,
                   qp_data_t *data)
{
    const double d0 = pb->start.d;
    const double v0 = pb->start.d_dot;
    const double a0 = pb->start.d_ddot;
    const double ac = (double)cal->qp_a_comfort;
    const double eps = 0.5 * (double)cal->epsilon_ay;                 /* PP-SWR-006 */
    const double keep = pb->ay_limit - eps;
    /* The previous path moved with the change of the T8 offset, so continuity does not hold
     * the path against a target that moves (at most ref_rate dt per cycle). */
    const double shift = ws->warm ? (pb->d_target - ws->d_target) : 0.0;
    double rd[N];
    for (size_t k = 0U; k < N; k++) {
        const double t = (double)(k + 1U) * DT;
        const double d_free = d0 + (v0 * t) + (0.5 * a0 * t * t);
        data->d_free[k] = d_free;
        const double need = pb->v[k] * pb->v[k] * pb->kappa[k];
        rd[k] = ((double)cal->qp_w_dev * ramp(cal, k) * (d_free - pb->d_target))
                + (pb->has_old[k] ? ((double)cal->qp_w_cont * (d_free - (pb->d_old[k] + shift))) : 0.0);
        /* a_y of the path as T11 writes it (s_dot = v): d''/q^2 + v^2 kappa / q, q = 1 - kappa d
         * taken at the previous path (else the zero-jerk path), so the rows stay linear. Bounds
         * on a_y map to bounds on d'' - a0 = Ma j. */
        const double d_bar = pb->has_old[k] ? pb->d_old[k] : d_free;
        const double q = fmax(1.0 - (pb->kappa[k] * d_bar), QP_MIN_Q);
        const double q2 = q * q;
        const double ref = need / q;
        /* |a_y| <= limit; where the need is beyond it, keep assisting near the limit. */
        const double lo_ay = (need > keep) ? (fmin(need, pb->ay_limit) - eps) : -pb->ay_limit;
        const double hi_ay = (need < -keep) ? (fmax(need, -pb->ay_limit) + eps) : pb->ay_limit;
        data->lo[k] = (q2 * (lo_ay - ref)) - a0;
        data->hi[k] = (q2 * (hi_ay - ref)) - a0;
        /* Lateral jerk of the path: v^3 dkappa/ds + j (constant v over a step). */
        const double jerk_ref = pb->v[k] * pb->v[k] * pb->v[k] * pb->dkappa[k];
        data->lo[(7U * N) + k] = -pb->jerk_limit - jerk_ref;
        data->hi[(7U * N) + k] = pb->jerk_limit - jerk_ref;
        /* Comfort level only where the need is within the limit: beyond it the band above sets a_y. */
        const bool beyond = (need > keep) || (need < -keep);
        data->lo[N + k] = -QP_INF;
        data->hi[N + k] = beyond ? QP_INF : ((q2 * (ac - ref)) - a0);
        data->lo[(2U * N) + k] = beyond ? -QP_INF : ((q2 * (-ac - ref)) - a0);
        data->hi[(2U * N) + k] = QP_INF;
        data->lo[(3U * N) + k] = 0.0;
        data->hi[(3U * N) + k] = QP_INF;
        data->lo[(4U * N) + k] = 0.0;
        data->hi[(4U * N) + k] = QP_INF;
        data->lo[(5U * N) + k] = -QP_INF;
        data->hi[(5U * N) + k] = pb->d_max[k] - d_free;
        data->lo[(6U * N) + k] = pb->d_min[k] - d_free;
        data->hi[(6U * N) + k] = QP_INF;
    }
    const double v_free_end = v0 + (a0 * (double)N * DT);
    for (size_t i = 0U; i < N; i++) {
        double sum = 0.0;
        for (size_t k = i; k < N; k++) {
            sum += ws->md[k][i] * rd[k];
        }
        data->q[i] = sum
            + ((double)cal->qp_w_term_d * ws->md[N - 1U][i] * (data->d_free[N - 1U] - pb->d_target))
            + ((double)cal->qp_w_term_v * ws->mv[i] * v_free_end);
        data->q[N + i] = 0.0;
        data->q[(2U * N) + i] = 0.0;
    }
}

/* rho from the ratio of the scaled primal and dual residuals (OSQP). */
static double next_rho(const pp_qp_ws_t *ws, const pp_calibration_t *cal, const qp_data_t *data)
{
    double ax[PP_QP_ROWS];
    double px[3U * N];
    double aty[3U * N];
    double rp[PP_QP_ROWS];
    double rdual[3U * N];
    mul_a(ws, ws->x, ax);
    mul_at(ws, ws->y, aty);
    for (size_t a = 0U; a < N; a++) {
        double sum = 0.0;
        for (size_t b = 0U; b < N; b++) {
            sum += ws->p[a][b] * ws->x[b];
        }
        px[a] = sum;
        px[N + a] = (double)cal->qp_w_comfort * ws->x[N + a];
        px[(2U * N) + a] = (double)cal->qp_w_corridor * ws->x[(2U * N) + a];
    }
    for (size_t r = 0U; r < PP_QP_ROWS; r++) {
        rp[r] = ax[r] - ws->z[r];
    }
    for (size_t i = 0U; i < (3U * N); i++) {
        rdual[i] = px[i] + data->q[i] + aty[i];
    }
    const double prim = max_abs(rp, PP_QP_ROWS)
        / fmax(fmax(max_abs(ax, PP_QP_ROWS), max_abs(ws->z, PP_QP_ROWS)), 1.0e-9);
    const double dual = max_abs(rdual, 3U * N)
        / fmax(fmax(max_abs(px, 3U * N), max_abs(aty, 3U * N)), fmax(max_abs(data->q, 3U * N), 1.0e-9));
    return clamp(ws->rho * sqrt(prim / fmax(dual, 1.0e-12)), QP_RHO_MIN, QP_RHO_MAX);
}

static void iterate(pp_qp_ws_t *ws, const pp_calibration_t *cal, const qp_data_t *data)
{
    double rhs[3U * N];
    double at[3U * N];
    double xt[3U * N];
    double zt[PP_QP_ROWS];
    double w[PP_QP_ROWS];
    for (size_t r = 0U; r < PP_QP_ROWS; r++) {
        w[r] = (rho_row(ws, r) * ws->z[r]) - ws->y[r];
    }
    mul_at(ws, w, at);
    for (size_t i = 0U; i < (3U * N); i++) {
        rhs[i] = (QP_SIGMA * ws->x[i]) - data->q[i] + at[i];
    }
    chol_solve(ws, rhs);
    const double ks = (double)cal->qp_w_comfort + QP_SIGMA
                      + ((rho_block[1] + rho_block[2] + rho_block[3]) * ws->rho);
    const double ke = (double)cal->qp_w_corridor + QP_SIGMA
                      + ((rho_block[4] + rho_block[5] + rho_block[6]) * ws->rho);
    for (size_t i = 0U; i < N; i++) {
        xt[i] = rhs[i];
        xt[N + i] = rhs[N + i] / ks;
        xt[(2U * N) + i] = rhs[(2U * N) + i] / ke;
    }
    mul_a(ws, xt, zt);
    for (size_t i = 0U; i < (3U * N); i++) {
        ws->x[i] = (QP_ALPHA * xt[i]) + ((1.0 - QP_ALPHA) * ws->x[i]);
    }
    for (size_t r = 0U; r < PP_QP_ROWS; r++) {
        const double zr = (QP_ALPHA * zt[r]) + ((1.0 - QP_ALPHA) * ws->z[r]);
        const double rho = rho_row(ws, r);
        const double zn = clamp(zr + (ws->y[r] / rho), data->lo[r], data->hi[r]);
        ws->y[r] += rho * (zr - zn);
        ws->z[r] = zn;
    }
}

bool pp_generate_qp(pp_qp_ws_t *ws, const pp_calibration_t *cal, const pp_qp_problem_t *pb,
                    pp_lateral_path_t *out)
{
    bool ok = (ws != NULL) && (cal != NULL) && (pb != NULL) && (out != NULL);
    if (ok) {
        qp_data_t data;
        integrators(ws);
        jerk_cost(ws, cal, pb);
        if (!ws->warm || !(ws->rho > 0.0)) {
            (void)memset(ws->x, 0, sizeof(ws->x));
            (void)memset(ws->y, 0, sizeof(ws->y));
            ws->rho = (double)cal->qp_rho0;
        }
        bounds(ws, cal, pb, &data);
        /* Warm start: previous z and y, z moved into this cycle's bounds. */
        double ax[PP_QP_ROWS];
        mul_a(ws, ws->x, ax);
        for (size_t r = 0U; r < PP_QP_ROWS; r++) {
            ws->z[r] = clamp(ax[r], data.lo[r], data.hi[r]);
        }
        ok = factor(ws);
        const uint32_t iters = (uint32_t)fmax(1.0, (double)cal->qp_iters);
        for (uint32_t it = 1U; ok && (it <= iters); it++) {
            iterate(ws, cal, &data);
            if (((it % QP_RHO_EVERY) == 0U) && (it < iters)) {
                const double rho = next_rho(ws, cal, &data);
                if ((rho > (QP_RHO_CHANGE * ws->rho)) || (rho < (ws->rho / QP_RHO_CHANGE))) {
                    ws->rho = rho;
                    ok = factor(ws);
                }
            }
        }
        /* Lateral path by exact integration of the jerks from the start state. */
        out->d[0] = pb->start.d;
        out->d_dot[0] = pb->start.d_dot;
        out->d_ddot[0] = pb->start.d_ddot;
        for (size_t k = 0U; ok && (k < N); k++) {
            const double j = ws->x[k];
            out->d[k + 1U] = out->d[k] + (out->d_dot[k] * DT) + (0.5 * out->d_ddot[k] * DT * DT)
                             + ((j * DT * DT * DT) / 6.0);
            out->d_dot[k + 1U] = out->d_dot[k] + (out->d_ddot[k] * DT) + (0.5 * j * DT * DT);
            out->d_ddot[k + 1U] = out->d_ddot[k] + (j * DT);
            ok = isfinite(out->d[k + 1U]) && isfinite(out->d_dot[k + 1U]) && isfinite(out->d_ddot[k + 1U]);
        }
        ws->warm = ok;
        ws->d_target = pb->d_target;
    }
    return ok;
}

/* Unit tests of planner/src/generators/qp.c (T7 technique C). */

#include <math.h>
#include <string.h>

#include "generators/qp.h"
#include "pp_calibration.h"
#include "pp_test.h"

#define N PP_QP_N

static pp_qp_ws_t ws;   /* test only: the planner keeps it in the caller's state */

static void problem(pp_qp_problem_t *pb, double d0, double kappa, double half)
{
    (void)memset(pb, 0, sizeof(*pb));
    pb->start.d = d0;
    pb->ay_limit = 2.5;
    pb->jerk_limit = 4.5;
    for (size_t k = 0U; k < N; k++) {
        pb->v[k] = 25.0;
        pb->kappa[k] = kappa;
        pb->d_max[k] = half;
        pb->d_min[k] = -half;
    }
}

/* a_y as T11 writes the path (s_dot = v): d''/q^2 + v^2 kappa / q, q = 1 - kappa d. */
static double ay(const pp_qp_problem_t *pb, const pp_lateral_path_t *p, size_t k)
{
    const double q = 1.0 - (pb->kappa[k - 1U] * p->d[k]);
    return (p->d_ddot[k] / (q * q)) + ((pb->v[k - 1U] * pb->v[k - 1U] * pb->kappa[k - 1U]) / q);
}

static void test_recentre_without_overshoot(void)
{
    pp_qp_problem_t pb;
    pp_lateral_path_t p;
    problem(&pb, 0.5, 0.0, 0.5);
    pp_qp_reset(&ws);
    PP_CHECK(pp_generate_qp(&ws, &pp_calibration, &pb, &p));
    double d_min = 1.0;
    double a_max = 0.0;
    for (size_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        d_min = fmin(d_min, p.d[k]);
        a_max = fmax(a_max, fabs(p.d_ddot[k]));
    }
    PP_CHECK_NEAR(p.d[0], 0.5, 1e-12);
    PP_CHECK(p.d[N] < 0.1);                 /* back near the centre within 3 s */
    PP_CHECK(d_min > -0.03);                /* no overshoot */
    PP_CHECK(a_max <= 0.5);                 /* ay_add_max_hwa */
}

static void test_curve_at_limit_keeps_the_hard_limit(void)
{
    pp_qp_problem_t pb;
    pp_lateral_path_t p;
    problem(&pb, 0.0, 1.0 / 250.0, 0.5);    /* needs 2.5 m/s^2 */
    pp_qp_reset(&ws);
    PP_CHECK(pp_generate_qp(&ws, &pp_calibration, &pb, &p));
    for (size_t k = 1U; k < PP_TRAJECTORY_POINTS; k++) {
        PP_CHECK(fabs(ay(&pb, &p, k)) <= (pb.ay_limit + 2e-3));
    }
}

static void test_curve_beyond_limit_assists_at_the_limit(void)
{
    pp_qp_problem_t pb;
    pp_lateral_path_t p;
    problem(&pb, 0.0, 1.0 / 200.0, 0.5);    /* needs 3.1 m/s^2 */
    pb.start.d_ddot = pb.ay_limit - (25.0 * 25.0 / 200.0);  /* previous path already at the limit */
    pp_qp_reset(&ws);
    PP_CHECK(pp_generate_qp(&ws, &pp_calibration, &pb, &p));
    for (size_t k = 1U; k < PP_TRAJECTORY_POINTS; k++) {
        PP_CHECK(fabs(ay(&pb, &p, k)) <= (pb.ay_limit + 1e-2));
    }
    PP_CHECK(ay(&pb, &p, 10U) > (2.5 - 0.2));  /* PP-SWR-006: within epsilon_ay of aysmax */
    PP_CHECK(p.d[N] < -0.5);                    /* drifts out, as R79 allows */
}

static void test_continuity_with_old_path(void)
{
    pp_qp_problem_t pb;
    pp_lateral_path_t p;
    problem(&pb, 0.3, 0.0, 0.5);
    for (size_t k = 0U; k < N; k++) {
        pb.has_old[k] = true;
        pb.d_old[k] = 0.3;                      /* old path stays off centre */
    }
    pp_qp_reset(&ws);
    PP_CHECK(pp_generate_qp(&ws, &pp_calibration, &pb, &p));
    for (size_t k = 1U; k < PP_TRAJECTORY_POINTS; k++) {
        PP_CHECK(fabs(p.d[k] - 0.3) <= 0.05);  /* soft: T4 still blends */
    }
}

static void test_deterministic(void)
{
    pp_qp_problem_t pb;
    pp_lateral_path_t a;
    pp_lateral_path_t b;
    problem(&pb, 0.2, 1.0 / 400.0, 0.5);
    pp_qp_reset(&ws);
    PP_CHECK(pp_generate_qp(&ws, &pp_calibration, &pb, &a));
    pp_qp_reset(&ws);
    PP_CHECK(pp_generate_qp(&ws, &pp_calibration, &pb, &b));
    PP_CHECK(memcmp(a.d, b.d, sizeof(a.d)) == 0);
}

int main(void)
{
    test_recentre_without_overshoot();
    test_curve_at_limit_keeps_the_hard_limit();
    test_curve_beyond_limit_assists_at_the_limit();
    test_continuity_with_old_path();
    test_deterministic();
    return PP_TEST_RESULT();
}

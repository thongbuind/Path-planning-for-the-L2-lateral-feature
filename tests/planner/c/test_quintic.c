/* Unit tests of T7 technique A (planner/src/generators/quintic.c). */

#include "generators/quintic.h"
#include "pp_test.h"

static void test_boundary_conditions(void)
{
    pp_quintic_t q;
    double d;
    double v;
    double a;
    PP_CHECK(pp_quintic_solve(-0.4, 0.2, -0.1, 0.0, 3.0, &q));
    pp_quintic_eval(&q, 0.0, &d, &v, &a);
    PP_CHECK_NEAR(d, -0.4, 1e-12);
    PP_CHECK_NEAR(v, 0.2, 1e-12);
    PP_CHECK_NEAR(a, -0.1, 1e-12);
    q.duration = 1e9;                                     /* evaluate the polynomial at T */
    pp_quintic_eval(&q, 3.0, &d, &v, &a);
    PP_CHECK_NEAR(d, 0.0, 1e-12);
    PP_CHECK_NEAR(v, 0.0, 1e-12);
    PP_CHECK_NEAR(a, 0.0, 1e-12);
}

static void test_holds_after_duration(void)
{
    pp_quintic_t q;
    double d;
    double v;
    double a;
    PP_CHECK(pp_quintic_solve(0.3, 0.0, 0.0, 0.0, 2.0, &q));
    pp_quintic_eval(&q, 2.5, &d, &v, &a);
    PP_CHECK_NEAR(d, 0.0, 1e-12);
    PP_CHECK_NEAR(v, 0.0, 1e-12);
    PP_CHECK_NEAR(a, 0.0, 1e-12);
}

static void test_rejects_zero_duration(void)
{
    pp_quintic_t q;
    PP_CHECK(!pp_quintic_solve(0.3, 0.0, 0.0, 0.0, 0.0, &q));
}

static void test_grid(void)
{
    const pp_lateral_state_t start = {0.5, 0.0, 0.0, 0.0};
    pp_lateral_path_t path;
    PP_CHECK(pp_generate_quintic(&start, 0.0, 3.0, &path));
    PP_CHECK_NEAR(path.d[0], 0.5, 1e-12);
    PP_CHECK_NEAR(path.d[15], 0.25, 1e-12);               /* symmetric at T/2 */
    PP_CHECK_NEAR(path.d[30], 0.0, 1e-9);
}

int main(void)
{
    test_boundary_conditions();
    test_holds_after_duration();
    test_rejects_zero_duration();
    test_grid();
    return PP_TEST_RESULT();
}

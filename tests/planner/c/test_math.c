/* Unit tests of planner/src/pp_math.c. */

#include "pp_math.h"
#include "pp_test.h"

static void test_fit_recovers_exact_cubic(void)
{
    const pp_cubic_t truth = {{1.75, -0.02, 5.0e-4, -2.0e-6}};
    pp_cubic_fit_t fit;
    pp_cubic_t out;
    pp_cubic_fit_begin(&fit, 2.0, 80.0);
    for (int i = 0; i <= 78; i++) {
        const double x = 2.0 + (double)i;
        pp_cubic_fit_add(&fit, x, pp_cubic_value(&truth, x));
    }
    PP_CHECK(pp_cubic_fit_solve(&fit, &out));
    PP_CHECK_NEAR(out.c[0], truth.c[0], 1e-9);
    PP_CHECK_NEAR(out.c[1], truth.c[1], 1e-10);
    PP_CHECK_NEAR(out.c[2], truth.c[2], 1e-11);
    PP_CHECK_NEAR(out.c[3], truth.c[3], 1e-12);
}

static void test_fit_needs_four_samples(void)
{
    pp_cubic_fit_t fit;
    pp_cubic_t out;
    pp_cubic_fit_begin(&fit, 0.0, 2.0);
    pp_cubic_fit_add(&fit, 0.0, 1.0);
    pp_cubic_fit_add(&fit, 1.0, 1.0);
    pp_cubic_fit_add(&fit, 2.0, 1.0);
    PP_CHECK(!pp_cubic_fit_solve(&fit, &out));
}

static void test_solve4_singular(void)
{
    const pp_mat4_t a = {{{1, 2, 3, 4}, {2, 4, 6, 8}, {0, 1, 0, 0}, {0, 0, 1, 0}}};
    const double b[4] = {1, 2, 3, 4};
    double x[4];
    PP_CHECK(!pp_solve4(&a, b, x));
}

static void test_derivatives(void)
{
    const pp_cubic_t p = {{1.0, 2.0, 3.0, 4.0}};
    PP_CHECK_NEAR(pp_cubic_value(&p, 2.0), 1.0 + 4.0 + 12.0 + 32.0, 1e-12);
    PP_CHECK_NEAR(pp_cubic_slope(&p, 2.0), 2.0 + 12.0 + 48.0, 1e-12);
    PP_CHECK_NEAR(pp_cubic_bend(&p, 2.0), 6.0 + 48.0, 1e-12);
    PP_CHECK_NEAR(pp_cubic_third(&p), 24.0, 1e-12);
}

int main(void)
{
    test_fit_recovers_exact_cubic();
    test_fit_needs_four_samples();
    test_solve4_singular();
    test_derivatives();
    return PP_TEST_RESULT();
}

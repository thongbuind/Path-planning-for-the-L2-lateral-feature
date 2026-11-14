/* Unit tests of T5 Curvature fusion (planner/src/curvature.c). */

#include <string.h>

#include "curvature.h"
#include "pp_test.h"

static pp_cubic_t centre_with_kappa(double kappa0, double slope)
{
    const pp_cubic_t c = {{0.0, 0.0, 0.5 * kappa0, slope / 6.0}};
    return c;
}

static void test_first_measurement_initialises(void)
{
    pp_curvature_t c;
    pp_curvature_reset(&c);
    const pp_cubic_t centre = centre_with_kappa(0.001, 1e-5);
    pp_curvature_update_camera(&c, &centre, 0.0, 0.0, 0.0, 80.0, &pp_calibration);
    PP_CHECK(c.valid[0] && c.valid[40] && !c.valid[41]);          /* 0 to 80 m */
    PP_CHECK_NEAR(c.kappa[10], 0.001 + (1e-5 * 20.0), 1e-12);
    const double floor_var = (double)pp_calibration.sigma_kappa_min * (double)pp_calibration.sigma_kappa_min;
    PP_CHECK_NEAR(c.var[10], floor_var, 1e-15);                   /* reported 0: floor */
}

static void test_outlier_gets_a_tenth_of_the_weight(void)
{
    pp_curvature_t c;
    pp_curvature_reset(&c);
    const pp_cubic_t right = centre_with_kappa(0.001, 0.0);
    const pp_cubic_t wrong = centre_with_kappa(0.002, 0.0);       /* +0.001: c2 +0.0005 (F06) */
    pp_curvature_update_camera(&c, &right, 0.0, 0.0, 0.0, 80.0, &pp_calibration);
    const double prior = c.kappa[5];
    const double var = c.var[5];
    const double r = (double)pp_calibration.sigma_kappa_min * (double)pp_calibration.sigma_kappa_min;
    pp_curvature_update_camera(&c, &wrong, 0.0, 0.0, 0.0, 80.0, &pp_calibration);
    /* |innovation| = 0.001 > k_jump sigma (3 * 1.4e-4): gain / 10. */
    const double gain = 0.1 * var / (var + r);
    PP_CHECK_NEAR(c.kappa[5], prior + (gain * 0.001), 1e-12);
}

static void test_predict_shifts_by_distance(void)
{
    pp_curvature_t c;
    pp_curvature_reset(&c);
    const pp_cubic_t centre = centre_with_kappa(0.0, 1e-5);       /* kappa = 1e-5 s */
    pp_curvature_update_camera(&c, &centre, 0.0, 0.0, 0.0, 80.0, &pp_calibration);
    pp_curvature_predict(&c, 3.0, &pp_calibration);               /* 1.5 grid steps */
    PP_CHECK_NEAR(c.kappa[0], 1e-5 * 3.0, 1e-12);
    PP_CHECK_NEAR(c.kappa[10], 1e-5 * 23.0, 1e-12);
    PP_CHECK(!c.valid[40]);                                       /* no prior beyond 80 m */
    PP_CHECK(c.var[10] > (double)pp_calibration.sigma_kappa_min * (double)pp_calibration.sigma_kappa_min);
}

static void test_fit_recovers_line(void)
{
    pp_curvature_t c;
    double c2 = 0.0;
    double c3 = 0.0;
    pp_curvature_reset(&c);
    const pp_cubic_t centre = centre_with_kappa(0.002, -1e-5);
    pp_curvature_update_camera(&c, &centre, 0.0, 0.0, 0.0, 80.0, &pp_calibration);
    PP_CHECK(pp_curvature_fit(&c, 80.0, &c2, &c3));
    PP_CHECK_NEAR(c2, centre.c[2], 1e-12);
    PP_CHECK_NEAR(c3, centre.c[3], 1e-12);
}

static void test_yaw_rate_only_above_5_mps(void)
{
    pp_curvature_t c;
    pp_curvature_reset(&c);
    pp_curvature_update_yaw(&c, 0.01, 4.0, &pp_calibration);
    PP_CHECK(!c.valid[0]);
    pp_curvature_update_yaw(&c, 0.025, 25.0, &pp_calibration);
    PP_CHECK(c.valid[0]);
    PP_CHECK_NEAR(c.kappa[0], 0.001, 1e-12);
}

int main(void)
{
    test_first_measurement_initialises();
    test_outlier_gets_a_tenth_of_the_weight();
    test_predict_shifts_by_distance();
    test_fit_recovers_line();
    test_yaw_rate_only_above_5_mps();
    return PP_TEST_RESULT();
}

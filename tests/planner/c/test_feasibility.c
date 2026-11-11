/* Unit tests of T10 Feasibility and limits (planner/src/feasibility.c). */

#include <string.h>

#include "feasibility.h"
#include "pp_test.h"

static const pp_vehicle_config_t VP0 = {2.9F, 1.45F, 1.9F, 15.0F, 0.61F, 6.0F, 0.05F};
static const pp_function_limits_t HWA = {PP_AYSMAX, PP_JERK_MAX_HWA};

/* Points on the x axis with curvature kappa0 at point 0 and kappa elsewhere. */
static void path(pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS], double v, double kappa0,
                 double kappa)
{
    for (unsigned k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        (void)memset(&pts[k], 0, sizeof(pts[k]));
        pts[k].time_from_start = (float)((double)k * PP_GRID_STEP_S);
        pts[k].pose.x = (float)(v * (double)k * PP_GRID_STEP_S);
        pts[k].longitudinal_velocity_mps = (float)v;
        pts[k].curvature = (float)((k == 0U) ? kappa0 : kappa);
    }
}

static pp_ref_samples_t ref_samples(double kappa)
{
    pp_ref_samples_t r;
    (void)memset(&r, 0, sizeof(r));
    for (unsigned k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        r.kappa[k] = kappa;
        r.in_view[k] = true;
    }
    return r;
}

static void test_check(void)
{
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    pp_path_check_t c;
    const pp_ref_samples_t ref = ref_samples(0.003);
    path(pts, 25.0, 0.004, 0.004);
    pp_feasibility_check(pts, &ref, &c);
    PP_CHECK_NEAR(c.ay_max, 2.5, 1e-6);
    PP_CHECK_NEAR(c.ay_add_max, 0.625, 1e-6);
    PP_CHECK_NEAR(c.ay_need_max, 1.875, 1e-9);
    PP_CHECK_NEAR(c.jerk_max, 0.0, 1e-9);
}

static void test_cut_to_aysmax_and_integrate_again(void)
{
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    const pp_ref_samples_t ref = ref_samples(0.006);
    path(pts, 25.0, 0.004, 0.006);                         /* wants 3.75 m/s^2 */
    PP_CHECK(pp_feasibility_limit(pts, &ref, &HWA, &VP0));
    for (unsigned k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        const double v = (double)pts[k].longitudinal_velocity_mps;
        PP_CHECK(v * v * (double)pts[k].curvature <= PP_AYSMAX + 1e-6);   /* PP-SWR-001 */
    }
    PP_CHECK_NEAR(pts[0].pose.x, 0.0, 0.0);                /* point 0 stays */
    /* Circle of radius 250 m: after 75 m, y = R (1 - cos(s / R)). */
    PP_CHECK_NEAR(pts[30].pose.y, 250.0 * (1.0 - cos(75.0 / 250.0)), 1e-3);
    PP_CHECK_NEAR(pts[30].pose.yaw, 75.0 / 250.0, 1e-5);
    PP_CHECK_NEAR(pts[30].front_wheel_angle_rad, atan(2.9 * 0.004), 1e-6);
}

static void test_point0_curvature_is_cut_too(void)
{
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    const pp_ref_samples_t ref = ref_samples(0.006);
    path(pts, 25.0, 0.006, 0.006);
    PP_CHECK(pp_feasibility_limit(pts, &ref, &HWA, &VP0));
    PP_CHECK_NEAR(625.0 * (double)pts[0].curvature, PP_AYSMAX, 1e-5);
    PP_CHECK_NEAR(pts[0].pose.x, 0.0, 0.0);
    PP_CHECK_NEAR(pts[0].pose.y, 0.0, 0.0);
}

static void test_jerk_is_limited(void)
{
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    const pp_ref_samples_t ref = ref_samples(0.0);
    path(pts, 25.0, 0.0, 0.003);                           /* a_y step 0 -> 1.875 in 0.1 s */
    PP_CHECK(pp_feasibility_limit(pts, &ref, &HWA, &VP0));
    PP_CHECK_NEAR(625.0 * (double)pts[1].curvature, 0.5, 1e-5);   /* 5 m/s^3 * 0.1 s */
    PP_CHECK_NEAR(625.0 * (double)pts[2].curvature, 1.0, 1e-5);
    PP_CHECK_NEAR(625.0 * (double)pts[10].curvature, 1.875, 1e-5);
}

static void test_steering_wheel_rate_is_limited(void)
{
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    const pp_ref_samples_t ref = ref_samples(0.0);
    path(pts, 2.0, 0.0, 0.1);                              /* slow, sharp: wheel rate binds */
    PP_CHECK(pp_feasibility_limit(pts, &ref, &HWA, &VP0));
    const double step = (6.0 / 15.0) * 0.1;                /* PP-SWR-117 */
    PP_CHECK_NEAR(pts[1].front_wheel_angle_rad, step, 1e-6);
    PP_CHECK_NEAR(pts[2].front_wheel_angle_rad, 2.0 * step, 1e-6);
}

static void test_path_within_limits_is_untouched(void)
{
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    const pp_ref_samples_t ref = ref_samples(0.001);
    path(pts, 25.0, 0.001, 0.001);
    PP_CHECK(!pp_feasibility_limit(pts, &ref, &HWA, &VP0));
    PP_CHECK_NEAR(pts[30].pose.y, 0.0, 0.0);
}

static void test_flag_hysteresis_and_confirmation(void)
{
    pp_limit_flag_t f;
    pp_limit_flag_reset(&f);
    const double dt = 0.025;                               /* T_flag / 2 = 0.1 s: 4 cycles */
    for (int i = 0; i < 3; i++) {
        pp_limit_flag_update(&f, 3.0, PP_AYSMAX, &pp_calibration, dt);
    }
    PP_CHECK(!f.reached);
    pp_limit_flag_update(&f, 3.0, PP_AYSMAX, &pp_calibration, dt);
    PP_CHECK(f.reached);                                   /* PP-SWR-007 */
    for (int i = 0; i < 10; i++) {
        pp_limit_flag_update(&f, 2.4, PP_AYSMAX, &pp_calibration, dt);   /* inside the band */
    }
    PP_CHECK(f.reached);
    for (int i = 0; i < 4; i++) {
        pp_limit_flag_update(&f, 2.2, PP_AYSMAX, &pp_calibration, dt);
    }
    PP_CHECK(!f.reached);                                  /* PP-SWR-008 */
}

static void test_curve_limit(void)
{
    pp_reference_line_t ref;
    pp_curve_limit_t c;
    (void)memset(&ref, 0, sizeof(ref));
    ref.valid = true;
    ref.view_end = 80.0;
    pp_curve_limit(&ref, PP_AYSMAX, &c);                   /* straight */
    PP_CHECK_NEAR(c.v_max, 500.0, 1e-6);

    ref.centre.c[3] = 1.0e-6;                              /* kappa = 6e-6 x grows ahead */
    pp_curve_limit(&ref, PP_AYSMAX, &c);
    PP_CHECK(c.distance >= 76.0);
    PP_CHECK_NEAR(c.kappa_max, 6.0e-6 * c.distance, 2e-6);
    PP_CHECK_NEAR(c.v_max, sqrt(PP_AYSMAX / c.kappa_max), 1e-9);
}

static void test_ay_need_max_within_view(void)
{
    pp_reference_line_t ref;
    pp_speed_profile_t sp;
    (void)memset(&ref, 0, sizeof(ref));
    ref.valid = true;
    ref.centre.c[2] = 0.5 / 200.0;                         /* R about 200 m near the car */
    ref.view_end = 40.0;
    for (unsigned k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        sp.v[k] = 25.0;
        sp.a[k] = 0.0;
        sp.s[k] = 25.0 * (double)k * PP_GRID_STEP_S;
    }
    const double need = pp_ay_need_max(&ref, &sp);
    PP_CHECK(need > 3.0 && need <= 625.0 / 200.0 + 1e-9);   /* only points up to 40 m */
}

int main(void)
{
    test_ay_need_max_within_view();
    test_check();
    test_cut_to_aysmax_and_integrate_again();
    test_point0_curvature_is_cut_too();
    test_jerk_is_limited();
    test_steering_wheel_rate_is_limited();
    test_path_within_limits_is_untouched();
    test_flag_hysteresis_and_confirmation();
    test_curve_limit();
    return PP_TEST_RESULT();
}

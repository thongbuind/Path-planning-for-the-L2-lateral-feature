#include <string.h>

#include "feasibility.h"
#include "pp_test.h"

static const pp_vehicle_config_t VP0 = {2.9F, 1.45F, 1.9F, 15.0F, 0.61F, 6.0F, 0.05F};
static const pp_function_limits_t HWA = {PP_AYSMAX, PP_JERK_MAX_HWA, 0.0, 0.0};

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

static void test_curve_support(double sign)
{
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    const double v = 25.0;
    pp_ref_samples_t ref = ref_samples(sign * 0.005);
    pp_function_limits_t limits = HWA;
    limits.ay_support = 2.4;
    path(pts, v, 0.0, 0.0);
    ref.in_view[0] = false;
    PP_CHECK(pp_feasibility_limit(pts, &ref, &limits, &VP0));
    PP_CHECK_NEAR(pts[0].curvature, 0.0, 1e-9);
    PP_CHECK_NEAR(sign * v * v * (double)pts[1].curvature, 0.5, 1e-5);
    PP_CHECK_NEAR(sign * v * v * (double)pts[10].curvature, limits.ay_support, 1e-5);
    PP_CHECK(sign * (double)pts[11].curvature < sign * (double)pts[10].curvature);
}

static void test_cut_to_aysmax_and_integrate_again(void)
{
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    const pp_ref_samples_t ref = ref_samples(0.006);
    path(pts, 25.0, 0.004, 0.006);
    PP_CHECK(pp_feasibility_limit(pts, &ref, &HWA, &VP0));
    for (unsigned k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        const double v = (double)pts[k].longitudinal_velocity_mps;
        PP_CHECK(v * v * (double)pts[k].curvature <= PP_AYSMAX + 1e-6);
    }
    PP_CHECK_NEAR(pts[0].pose.x, 0.0, 0.0);
    /* Với R = 250 m và s = 75 m, điểm cuối có y = R × (1 - cos(s/R)). */
    PP_CHECK_NEAR(pts[30].pose.y, 250.0 * (1.0 - cos(75.0 / 250.0)), 1e-3);
    PP_CHECK_NEAR(pts[30].pose.yaw, 75.0 / 250.0, 1e-5);
    PP_CHECK_NEAR(pts[30].front_wheel_angle_rad, atan(2.9 * 0.004), 1e-6);
}

static void test_hwa_path_ceiling_follows_margin(void)
{
    pp_calibration_t cal = pp_calibration;
    cal.ay_margin_hwa = 0.0F;
    pp_function_limits_t limits = pp_hwa_path_limits(&cal, false);
    PP_CHECK_NEAR(limits.ay_max, PP_AYSMAX, 0.0);
    PP_CHECK_NEAR(limits.jerk_max, PP_JERK_MAX_HWA, 0.0);
    PP_CHECK_NEAR(limits.ay_add_max, 0.0, 0.0);

    cal.ay_margin_hwa = 0.2F;
    PP_CHECK_NEAR(pp_hwa_path_limits(&cal, true).ay_max, PP_AYSMAX, 0.0);
    limits = pp_hwa_path_limits(&cal, false);
    PP_CHECK_NEAR(limits.ay_max, PP_AYSMAX + 0.2, 1e-7);

    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    const pp_ref_samples_t ref = ref_samples(0.0048);
    path(pts, 25.0, 0.0048, 0.0048);
    PP_CHECK(pp_feasibility_limit(pts, &ref, &limits, &VP0));
    for (unsigned k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        const double v = (double)pts[k].longitudinal_velocity_mps;
        PP_CHECK(v * v * (double)pts[k].curvature <= limits.ay_max + 1e-6);
    }
    PP_CHECK_NEAR(625.0 * (double)pts[30].curvature, PP_AYSMAX + 0.2, 1e-5);

    path(pts, 25.0, 0.0042, 0.0042);
    PP_CHECK(!pp_feasibility_limit(pts, &ref, &limits, &VP0));
    PP_CHECK_NEAR(625.0 * (double)pts[30].curvature, 2.625, 1e-5);
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
    path(pts, 25.0, 0.0, 0.003);
    PP_CHECK(pp_feasibility_limit(pts, &ref, &HWA, &VP0));
    PP_CHECK_NEAR(625.0 * (double)pts[1].curvature, 0.5, 1e-5);
    PP_CHECK_NEAR(625.0 * (double)pts[2].curvature, 1.0, 1e-5);
    PP_CHECK_NEAR(625.0 * (double)pts[10].curvature, 1.875, 1e-5);
}

/* PP-PR-040: đo jerk trên các điểm float32 trong cả cửa sổ 0,5 s như bên chấm. */
static void test_jerk_stays_below_limit_after_float32(void)
{
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    const pp_ref_samples_t ref = ref_samples(0.0);
    unsigned at_limit = 0U;
    double worst = 0.0;
    for (unsigned iv = 0U; iv < 40U; iv++) {
        const double v = 12.0 + (0.613 * (double)iv);
        for (unsigned ia = 0U; ia < 11U; ia++) {
            const double a0 = -2.4 + (0.47 * (double)ia);
            const double a1 = (a0 > 0.0) ? -2.45 : 2.45;
            path(pts, v, a0 / (v * v), a1 / (v * v));
            (void)pp_feasibility_limit(pts, &ref, &HWA, &VP0);
            pp_path_check_t c;
            pp_feasibility_check(pts, &ref, &c);
            at_limit += (c.jerk_max > 0.99 * PP_JERK_MAX_HWA) ? 1U : 0U;
            worst = fmax(worst, c.jerk_max);
        }
    }
    PP_CHECK(at_limit > 0U);
    PP_CHECK(worst <= PP_JERK_MAX_HWA);
}

static void test_steering_wheel_rate_is_limited(void)
{
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    const pp_ref_samples_t ref = ref_samples(0.0);
    path(pts, 2.0, 0.0, 0.1);
    PP_CHECK(pp_feasibility_limit(pts, &ref, &HWA, &VP0));
    const double step = (6.0 / 15.0) * 0.1;
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
    const double dt = 0.025;
    for (int i = 0; i < 3; i++) {
        pp_limit_flag_update(&f, 3.0, PP_AYSMAX, &pp_calibration, dt);
    }
    PP_CHECK(!f.reached);
    pp_limit_flag_update(&f, 3.0, PP_AYSMAX, &pp_calibration, dt);
    PP_CHECK(f.reached);
    for (int i = 0; i < 10; i++) {
        pp_limit_flag_update(&f, 2.4, PP_AYSMAX, &pp_calibration, dt);
    }
    PP_CHECK(f.reached);
    for (int i = 0; i < 4; i++) {
        pp_limit_flag_update(&f, 2.2, PP_AYSMAX, &pp_calibration, dt);
    }
    PP_CHECK(!f.reached);
}

static void test_curve_limit(void)
{
    pp_reference_line_t ref;
    pp_curve_limit_t c;
    (void)memset(&ref, 0, sizeof(ref));
    ref.valid = true;
    ref.view_end = 80.0;
    pp_curve_limit(&ref, PP_AYSMAX, &c);
    PP_CHECK_NEAR(c.v_max, 500.0, 1e-6);

    ref.centre.c[3] = 1.0e-6;
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
    ref.centre.c[2] = 0.5 / 200.0;
    ref.view_end = 40.0;
    for (unsigned k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        sp.v[k] = 25.0;
        sp.a[k] = 0.0;
        sp.s[k] = 25.0 * (double)k * PP_GRID_STEP_S;
    }
    const double need = pp_ay_need_max(&ref, &sp);
    PP_CHECK(need > 3.0 && need <= 625.0 / 200.0 + 1e-9);
}

int main(void)
{
    test_ay_need_max_within_view();
    test_check();
    test_curve_support(1.0);
    test_curve_support(-1.0);
    test_cut_to_aysmax_and_integrate_again();
    test_hwa_path_ceiling_follows_margin();
    test_point0_curvature_is_cut_too();
    test_jerk_is_limited();
    test_jerk_stays_below_limit_after_float32();
    test_steering_wheel_rate_is_limited();
    test_path_within_limits_is_untouched();
    test_flag_hysteresis_and_confirmation();
    test_curve_limit();
    return PP_TEST_RESULT();
}

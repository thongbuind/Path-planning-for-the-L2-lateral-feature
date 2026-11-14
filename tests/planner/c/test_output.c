/* Unit tests of T6 Lateral state and T11 Output (lateral_state.c, output.c). */

#include <float.h>
#include <string.h>

#include "lateral_state.h"
#include "output.h"
#include "pp_test.h"

static pp_reference_line_t straight(double c0)
{
    pp_reference_line_t ref;
    (void)memset(&ref, 0, sizeof(ref));
    ref.valid = true;
    ref.centre.c[0] = c0;
    ref.width = 3.5;
    ref.view_end = 80.0;
    return ref;
}

static void test_lateral_state_offset_and_heading(void)
{
    pp_reference_line_t ref = straight(0.4);              /* centre 0.4 m to the left */
    ref.centre.c[1] = 0.01;                               /* lane heads 0.01 rad left */
    pp_ref_walker_t w;
    pp_ref_point_t foot;
    pp_lateral_state_t st;
    pp_ref_walk_begin(&w, &ref, &foot);
    pp_lateral_state(&foot, 25.0, 0.0, 0.0, &st);
    PP_CHECK_NEAR(st.d, -0.4 * cos(atan(0.01)), 1e-6);
    PP_CHECK_NEAR(st.heading, -atan(0.01), 1e-9);
    PP_CHECK_NEAR(st.d_dot, 25.0 * sin(-atan(0.01)), 1e-9);
}

static void test_speed_profile_constant_and_shifted(void)
{
    pp_speed_profile_t sp;
    pp_speed_profile(NULL, 1000000U, 25.0, &sp);
    PP_CHECK_NEAR(sp.v[30], 25.0, 1e-12);
    PP_CHECK_NEAR(sp.s[30], 75.0, 1e-9);

    pp_longitudinal_plan_t plan;
    (void)memset(&plan, 0, sizeof(plan));
    plan.header.stamp_us = 975000U;                       /* one planner cycle before t0 */
    for (unsigned k = 0U; k < PP_LONGITUDINAL_PLAN_POINTS; k++) {
        plan.points[k].v = (float)(20.0 + (double)k);     /* +1 m/s per 0.1 s */
        plan.points[k].a = 10.0F;
    }
    pp_speed_profile(&plan, 1000000U, 0.0, &sp);
    PP_CHECK_NEAR(sp.v[0], 20.25, 1e-6);                  /* 25 ms into the plan */
    PP_CHECK_NEAR(sp.v[30], 50.0, 1e-6);                  /* clamped to the last point */
    PP_CHECK_NEAR(sp.a[5], 10.0, 1e-6);
}

static void test_points_on_straight_centre(void)
{
    const pp_reference_line_t ref = straight(0.0);
    pp_lateral_path_t path;
    pp_speed_profile_t sp;
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    (void)memset(&path, 0, sizeof(path));
    pp_speed_profile(NULL, 0U, 20.0, &sp);
    PP_CHECK(pp_output_points(&ref, &path, &sp, 2.9, pts, NULL));
    PP_CHECK_NEAR(pts[0].pose.x, 0.0, 1e-6);
    PP_CHECK_NEAR(pts[10].pose.x, 20.0, 1e-4);
    PP_CHECK_NEAR(pts[10].pose.y, 0.0, 1e-6);
    PP_CHECK_NEAR(pts[30].time_from_start, 3.0, 1e-6);
    PP_CHECK_NEAR(pts[30].curvature, 0.0, 1e-9);
    PP_CHECK_NEAR(pts[30].rear_wheel_angle_rad, 0.0, 0.0);
}

static void test_points_follow_curve_with_offset(void)
{
    /* Centre is a circle of radius 500 m; path 0.2 m left of it, constant. */
    const double radius = 500.0;
    pp_reference_line_t ref = straight(0.0);
    ref.centre.c[2] = 1.0 / (2.0 * radius);
    ref.view_end = 2.0;                                   /* rest from the arc continuation */
    pp_lateral_path_t path;
    pp_speed_profile_t sp;
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    (void)memset(&path, 0, sizeof(path));
    for (unsigned k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        path.d[k] = 0.2;
    }
    pp_speed_profile(NULL, 0U, 25.0, &sp);
    PP_CHECK(pp_output_points(&ref, &path, &sp, 2.9, pts, NULL));
    PP_CHECK_NEAR(pts[0].pose.y, 0.2, 1e-6);
    /* Curvature of a parallel at offset d inside a left curve: 1 / (R - d). */
    PP_CHECK_NEAR(pts[20].curvature, 1.0 / (radius - 0.2), 1e-6);
    PP_CHECK_NEAR(pts[20].heading_rate_rps, 25.0 / (radius - 0.2), 1e-5);
    PP_CHECK_NEAR(pts[20].front_wheel_angle_rad, atan(2.9 / (radius - 0.2)), 1e-6);
}

static void test_output_rejects_position_outside_float32(void)
{
    const pp_reference_line_t ref = straight(0.0);
    pp_lateral_path_t path = {0};
    pp_speed_profile_t speed;
    pp_trajectory_point_t points[PP_TRAJECTORY_POINTS];
    pp_speed_profile(NULL, 0U, 20.0, &speed);
    path.d[10] = 2.0 * (double)FLT_MAX;
    PP_CHECK(!pp_output_points(&ref, &path, &speed, 2.9, points, NULL));
}

int main(void)
{
    test_lateral_state_offset_and_heading();
    test_speed_profile_constant_and_shifted();
    test_points_on_straight_centre();
    test_points_follow_curve_with_offset();
    test_output_rejects_position_outside_float32();
    return PP_TEST_RESULT();
}

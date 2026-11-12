/* Unit tests of T4 Stitching and continuity (planner/src/stitching.c). */

#include <string.h>

#include "pp_path.h"
#include "pp_test.h"
#include "stitching.h"

#define T_OLD (10000000ULL)
#define SPEED (25.0)

/* Moves 25 m/s straight ahead; invalid when the context says so. */
static void straight_motion(void *context, const pp_ego_motion_request_t *request,
                            pp_ego_motion_response_t *response)
{
    const bool *valid = (const bool *)context;
    response->valid = (valid == NULL) || *valid;
    response->dx = (float)(SPEED * (double)(request->t2_us - request->t1_us) * 1e-6);
    response->dy = 0.0F;
    response->dyaw = 0.0F;
}

static pp_previous_path_t straight_path(double y0, double kappa)
{
    pp_previous_path_t prev;
    (void)memset(&prev, 0, sizeof(prev));
    prev.valid = true;
    prev.t0_us = T_OLD;
    for (unsigned k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        pp_trajectory_point_t *p = &prev.points[k];
        const double t = (double)k * PP_GRID_STEP_S;
        p->time_from_start = (float)t;
        p->pose.x = (float)(SPEED * t);
        p->pose.y = (float)y0;
        p->curvature = (float)kappa;
        p->longitudinal_velocity_mps = (float)SPEED;
    }
    return prev;
}

static pp_reference_line_t straight_ref(void)
{
    pp_reference_line_t ref;
    (void)memset(&ref, 0, sizeof(ref));
    ref.valid = true;
    ref.width = 3.5;
    ref.view_end = 80.0;
    return ref;
}

static void test_move_old(void)
{
    const pp_previous_path_t prev = straight_path(0.5, 0.0);
    pp_old_path_t old;
    pp_stitch_move_old(&prev, T_OLD + PP_PLANNER_PERIOD_US, straight_motion, NULL, &old);
    PP_CHECK(old.valid);
    PP_CHECK_NEAR(old.shift_s, 0.025, 1e-12);
    PP_CHECK_NEAR(old.x[4], 10.0 - 0.625, 1e-5);
    PP_CHECK_NEAR(old.y[4], 0.5, 1e-6);

    pp_path_sample_t p;
    PP_CHECK(pp_stitch_sample_old(&old, 0.0, &p));        /* old point at 25 ms is the car now */
    PP_CHECK_NEAR(p.x, 0.0, 1e-5);
    PP_CHECK(!pp_stitch_sample_old(&old, 3.0, &p));       /* beyond the old horizon */
    PP_CHECK_NEAR(p.x, (SPEED * 3.025) - 0.625, 1e-4);    /* continued along the last point */
    PP_CHECK_NEAR(p.y, 0.5, 1e-6);
}

static void test_sample_on_curve_stays_on_the_arc(void)
{
    /* Old path exactly on a left circle R = 1000 m; a chord would be 0.6 mm inside. */
    const double radius = 1000.0;
    pp_previous_path_t prev = straight_path(0.0, 1.0 / radius);
    for (unsigned k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        const double a = SPEED * (double)k * PP_GRID_STEP_S / radius;
        prev.points[k].pose.x = (float)(radius * sin(a));
        prev.points[k].pose.y = (float)(radius * (1.0 - cos(a)));
        prev.points[k].pose.yaw = (float)a;
    }
    pp_old_path_t old;
    pp_stitch_move_old(&prev, T_OLD + PP_PLANNER_PERIOD_US, straight_motion, NULL, &old);
    pp_path_sample_t p;
    (void)pp_stitch_sample_old(&old, 0.0, &p);
    /* Exact point at 25 ms on the circle, moved by the straight ego-motion of 0.625 m. */
    const double a = SPEED * 0.025 / radius;
    PP_CHECK_NEAR(p.x, (radius * sin(a)) - 0.625, 2e-5);
    PP_CHECK_NEAR(p.y, radius * (1.0 - cos(a)), 2e-5);
}

static void test_old_path_not_usable(void)
{
    pp_old_path_t old;
    pp_previous_path_t prev = straight_path(0.0, 0.0);
    pp_stitch_move_old(&prev, T_OLD + PP_TRAJECTORY_TIMEOUT_US + 1U, straight_motion, NULL, &old);
    PP_CHECK(!old.valid);                                 /* older than the Trajectory timeout */
    bool no = false;
    pp_stitch_move_old(&prev, T_OLD + PP_PLANNER_PERIOD_US, straight_motion, &no, &old);
    PP_CHECK(!old.valid);                                 /* ego-motion not valid */
    prev.valid = false;
    pp_stitch_move_old(&prev, T_OLD + PP_PLANNER_PERIOD_US, straight_motion, NULL, &old);
    PP_CHECK(!old.valid);
    PP_CHECK_NEAR(pp_stitch_blend(&old, &pp_calibration, 2.9, prev.points), 1.0, 0.0);
}

static void test_start_from_old_path_or_reset(void)
{
    const pp_reference_line_t ref = straight_ref();
    const pp_lateral_state_t measured = {0.0, 0.0, 0.0, 0.0};
    pp_lateral_state_t start;
    pp_old_path_t old;

    pp_previous_path_t prev = straight_path(0.1, 0.0);
    pp_stitch_move_old(&prev, T_OLD + PP_PLANNER_PERIOD_US, straight_motion, NULL, &old);
    PP_CHECK(pp_stitch_start(&old, &ref, &measured, &pp_calibration, &start));
    PP_CHECK_NEAR(start.d, 0.1, 1e-6);
    PP_CHECK_NEAR(start.d_dot, 0.0, 1e-9);
    PP_CHECK_NEAR(start.d_ddot, 0.0, 1e-9);

    prev = straight_path(0.1 + (double)pp_calibration.stitch_reset, 0.0);
    pp_stitch_move_old(&prev, T_OLD + PP_PLANNER_PERIOD_US, straight_motion, NULL, &old);
    PP_CHECK(!pp_stitch_start(&old, &ref, &measured, &pp_calibration, &start));
    PP_CHECK_NEAR(start.d, 0.0, 0.0);                      /* reset to the measured state */
}

static void test_start_curvature_gives_lateral_acceleration(void)
{
    /* Old path bends 0.002 1/m on a straight reference: d_ddot = v^2 kappa. */
    const pp_reference_line_t ref = straight_ref();
    const pp_lateral_state_t measured = {0.0, 0.0, 0.0, 0.0};
    pp_lateral_state_t start;
    pp_old_path_t old;
    pp_previous_path_t prev = straight_path(0.0, 0.002);
    pp_stitch_move_old(&prev, T_OLD + PP_PLANNER_PERIOD_US, straight_motion, NULL, &old);
    PP_CHECK(pp_stitch_start(&old, &ref, &measured, &pp_calibration, &start));
    PP_CHECK_NEAR(start.d_ddot, SPEED * SPEED * 0.002, 1e-6);
}

static void test_blend_limits_the_jump(void)
{
    pp_previous_path_t prev = straight_path(0.0, 0.0);
    pp_old_path_t old;
    pp_stitch_move_old(&prev, T_OLD + PP_PLANNER_PERIOD_US, straight_motion, NULL, &old);

    /* Candidate 0.5 m left of the old path. */
    pp_previous_path_t cand = straight_path(0.5, 0.0);
    const double margin = (double)pp_calibration.cont_margin;
    const double lambda = pp_stitch_blend(&old, &pp_calibration, 2.9, cand.points);
    PP_CHECK_NEAR(lambda, margin * PP_CONT_LATERAL_M / 0.5, 1e-6);
    PP_CHECK_NEAR(cand.points[10].pose.y, margin * PP_CONT_LATERAL_M, 1e-6);
    PP_CHECK(cand.points[30].pose.y <= PP_CONT_LATERAL_M);

    /* Candidate equal to the old path: unchanged. */
    pp_previous_path_t same = straight_path(0.0, 0.0);
    PP_CHECK_NEAR(pp_stitch_blend(&old, &pp_calibration, 2.9, same.points), 1.0, 1e-9);
}

/* PP-TS-014: candidate equal to the old path near the car, 0.5 m away from 2 s on. */
static void test_blend_far_change(void)
{
    pp_previous_path_t prev = straight_path(0.0, 0.0);
    pp_old_path_t old;
    pp_stitch_move_old(&prev, T_OLD + PP_PLANNER_PERIOD_US, straight_motion, NULL, &old);
    pp_previous_path_t cand = straight_path(0.0, 0.0);
    for (unsigned k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        cand.points[k].pose.y = (float)(0.01 * (double)k);          /* near: 0.01 m per point */
    }
    for (unsigned k = 20U; k < PP_TRAJECTORY_POINTS; k++) {
        cand.points[k].pose.y = 0.5F;
    }
    const double limit = (double)pp_calibration.cont_margin * PP_CONT_LATERAL_M;
    (void)pp_stitch_blend(&old, &pp_calibration, 2.9, cand.points);
    for (unsigned k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        PP_CHECK((double)cand.points[k].pose.y <= limit + 1e-6);    /* each point within the limit */
    }
#ifdef PP_T4_PER_TIME
    PP_CHECK_NEAR(cand.points[3].pose.y, 0.03, 1e-6);              /* near part kept (V1) */
#else
    PP_CHECK(cand.points[3].pose.y < 0.004F);                       /* scaled with the far change */
#endif
}

int main(void)
{
    test_move_old();
    test_sample_on_curve_stays_on_the_arc();
    test_old_path_not_usable();
    test_start_from_old_path_or_reset();
    test_start_curvature_gives_lateral_acceleration();
    test_blend_limits_the_jump();
    test_blend_far_change();
    return PP_TEST_RESULT();
}

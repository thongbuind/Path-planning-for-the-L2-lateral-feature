/* L0 của contract T7 (generators/pp_t7.h): chạy với generator được chọn lúc build (PP_T7). */

#include <math.h>
#include <string.h>

#include "generators/pp_t7.h"
#include "output.h"
#include "pp_calibration.h"
#include "pp_test.h"

#if defined(PP_T7_QUINTIC_DURATION)
_Static_assert(PP_T7_SUPPORT_FLOOR == 1, "quintic_duration keeps the PP-SWR-006 support floor");
#elif defined(PP_T7_QP_JERK_ADMM)
_Static_assert(PP_T7_SUPPORT_FLOOR == 0, "qp_jerk_admm has no PP-SWR-006 support floor");
#endif

static const pp_vehicle_config_t VP0 = {2.9F, 1.45F, 1.9F, 15.0F, 0.61F, 6.0F, 0.05F};

static pp_t7_ws_t ws_a;
static pp_t7_ws_t ws_b;

typedef struct {
    pp_reference_line_t ref;
    pp_lateral_state_t start;
    pp_speed_profile_t speed;
    pp_old_path_t old;
    pp_t7_input_t in;
} fixture_t;

static void setup(fixture_t *fx, double d0, double kappa)
{
    (void)memset(fx, 0, sizeof(*fx));
    fx->ref.valid = true;
    fx->ref.centre.c[2] = 0.5 * kappa;
    fx->ref.width = 3.5;
    fx->ref.view_end = 80.0;
    fx->start.d = d0;
    pp_speed_profile(NULL, 0U, 20.0, &fx->speed);
    fx->in.ref = &fx->ref;
    fx->in.start = &fx->start;
    fx->in.speed = &fx->speed;
    fx->in.old = &fx->old;
    fx->in.from_old = false;
    fx->in.recentering = true;
    fx->in.d_target = 0.0;
    fx->in.vehicle = &VP0;
}

static bool generate(pp_t7_ws_t *ws, const fixture_t *fx, pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS])
{
    pp_ref_samples_t samples;
    (void)memset(pts, 0, sizeof(pp_trajectory_point_t) * PP_TRAJECTORY_POINTS);
    return pp_t7_generate(ws, &pp_calibration, &fx->in, pts, &samples);
}

static void test_path_starts_at_start_and_moves_to_target(void)
{
    fixture_t fx;
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    setup(&fx, 0.3, 0.0);
    pp_t7_reset(&ws_a);
    PP_CHECK(generate(&ws_a, &fx, pts));
    PP_CHECK_NEAR(pts[0].pose.x, 0.0, 1e-6);
    PP_CHECK_NEAR(pts[0].pose.y, 0.3, 1e-6);
    PP_CHECK(fabs((double)pts[PP_TRAJECTORY_POINTS - 1U].pose.y) < 0.3);
    for (size_t k = 1U; k < PP_TRAJECTORY_POINTS; k++) {
        PP_CHECK(pts[k].pose.x > pts[k - 1U].pose.x);
        PP_CHECK(isfinite(pts[k].pose.y) && isfinite(pts[k].curvature));
    }
}

static void test_on_target_stays_on_target(void)
{
    fixture_t fx;
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    setup(&fx, 0.0, 0.0);
    pp_t7_reset(&ws_a);
    PP_CHECK(generate(&ws_a, &fx, pts));
    for (size_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        PP_CHECK_NEAR(pts[k].pose.y, 0.0, 1e-3);
    }
}

/* Sau reset, kết quả chỉ phụ thuộc input: cùng input trên hai ws cho path giống từng bit. */
static void test_reset_makes_output_depend_on_input_only(void)
{
    fixture_t fx;
    pp_trajectory_point_t first[PP_TRAJECTORY_POINTS];
    pp_trajectory_point_t again[PP_TRAJECTORY_POINTS];
    pp_trajectory_point_t other[PP_TRAJECTORY_POINTS];
    setup(&fx, 0.4, 0.002);
    pp_t7_reset(&ws_a);
    PP_CHECK(generate(&ws_a, &fx, first));

    fixture_t moved;
    setup(&moved, -0.5, -0.001);
    PP_CHECK(generate(&ws_a, &moved, other));
    pp_t7_reset(&ws_a);
    PP_CHECK(generate(&ws_a, &fx, again));
    PP_CHECK(memcmp(first, again, sizeof(first)) == 0);

    (void)memset(&ws_b, 0xA5, sizeof(ws_b));
    pp_t7_reset(&ws_b);
    PP_CHECK(generate(&ws_b, &fx, again));
    PP_CHECK(memcmp(first, again, sizeof(first)) == 0);
}

/* Input không hữu hạn thì không có path, và ws vẫn dùng tiếp được như sau reset. */
static void test_non_finite_start_fails_and_recovers(void)
{
    fixture_t fx;
    fixture_t bad;
    pp_trajectory_point_t fresh[PP_TRAJECTORY_POINTS];
    pp_trajectory_point_t after[PP_TRAJECTORY_POINTS];
    setup(&fx, 0.2, 0.001);
    pp_t7_reset(&ws_b);
    PP_CHECK(generate(&ws_b, &fx, fresh));

    setup(&bad, NAN, 0.001);
    pp_t7_reset(&ws_a);
    PP_CHECK(generate(&ws_a, &fx, after));
    PP_CHECK(!generate(&ws_a, &bad, after));
    PP_CHECK(generate(&ws_a, &fx, after));
    PP_CHECK(memcmp(fresh, after, sizeof(fresh)) == 0);
}

#ifdef PP_T7_TELEMETRY
/* Telemetry qua state của LCC được kiểm ở test_lcc_step; ở đây chỉ kiểm generator khai báo khối lượng việc. */
static void test_telemetry_reports_work(void)
{
    fixture_t fx;
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    pp_t7_telemetry_t tm;
    setup(&fx, 0.3, 0.001);
    pp_t7_reset(&ws_a);
    PP_CHECK(generate(&ws_a, &fx, pts));
    (void)memset(&tm, 0, sizeof(tm));
    pp_t7_report(&ws_a, &tm);
    PP_CHECK(tm.work > 0U);
}
#endif

int main(void)
{
#ifdef PP_T7_TELEMETRY
    test_telemetry_reports_work();
#endif
    test_path_starts_at_start_and_moves_to_target();
    test_on_target_stays_on_target();
    test_reset_makes_output_depend_on_input_only();
    test_non_finite_start_fails_and_recovers();
    return PP_TEST_RESULT();
}

/* L0 riêng của quintic_tangent_point. Contract chung đã có ở tests/planner/c/test_t7_contract.c. */

#include <math.h>
#include <string.h>

#include "feasibility.h"
#include "generators/pp_t7.h"
#include "generators/t7_common.h"
#include "output.h"
#include "pp_calibration.h"
#include "pp_test.h"

static const pp_vehicle_config_t VP0 = {2.9F, 1.45F, 1.9F, 15.0F, 0.61F, 6.0F, 0.05F};
static pp_t7_ws_t ws;

#define SPEED (20.0)
/* Cua với tiếp điểm ở khoảng 1,5 s: sqrt(2·R·h) = 30 m với h = 1,75 m, nên R ≈ 257 m. */
#define KAPPA_TP15 (1.0 / 257.0)
#define CYCLE_S (0.025)
/* Đủ chu kỳ để biên độ tăng theo ref_rate tới 0,2 m (2 s). */
#define RAMP_CYCLES (100U)

typedef struct {
    pp_reference_line_t ref;
    pp_lateral_state_t start;
    pp_speed_profile_t speed;
    pp_old_path_t old;
    pp_object_list_t objects;
    pp_t7_input_t in;
} fixture_t;

static void setup(fixture_t *fx, double kappa)
{
    (void)memset(fx, 0, sizeof(*fx));
    fx->ref.valid = true;
    fx->ref.centre.c[2] = 0.5 * kappa;
    fx->ref.width = 3.5;
    fx->ref.view_end = 80.0;
    pp_speed_profile(NULL, 0U, SPEED, &fx->speed);
    fx->old.valid = true;  /* Chỉ shift_s được generator dùng: thời gian giữa hai chu kỳ. */
    fx->old.shift_s = CYCLE_S;
    fx->in.ref = &fx->ref;
    fx->in.start = &fx->start;
    fx->in.speed = &fx->speed;
    fx->in.old = &fx->old;
    fx->in.objects = &fx->objects;
    fx->in.vehicle = &VP0;
}

typedef struct {
    pp_trajectory_point_t mine[PP_TRAJECTORY_POINTS];
    pp_trajectory_point_t base[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
    pp_lateral_path_t lateral;
    bool ok;
} result_t;

static void run(const pp_calibration_t *cal, const fixture_t *fx, result_t *r)
{
    pp_ref_samples_t base_samples;
    pp_t7_reset(&ws);
    for (uint32_t i = 0U; i < RAMP_CYCLES; i++) {
        r->ok = pp_t7_generate(&ws, cal, &fx->in, r->mine, &r->samples);
    }
    PP_CHECK(pp_t7_quintic_search(cal, &fx->in, &r->lateral, r->base, &base_samples, NULL));
    PP_CHECK(memcmp(r->samples.kappa, base_samples.kappa, sizeof(base_samples.kappa)) == 0);
    PP_CHECK(memcmp(r->samples.in_view, base_samples.in_view, sizeof(base_samples.in_view)) == 0);
}

static double max_shift(const result_t *r)
{
    double m = 0.0;
    for (size_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        m = fmax(m, hypot((double)r->mine[k].pose.x - (double)r->base[k].pose.x,
                          (double)r->mine[k].pose.y - (double)r->base[k].pose.y));
    }
    return m;
}

/* Tiếp điểm kiểm độc lập: đi dày theo s trên vạch trong, tìm chỗ tiếp tuyến đi qua base_link. */
static double brute_tangent_s(const pp_reference_line_t *ref, double side)
{
    pp_ref_walker_t walker;
    pp_ref_point_t p;
    pp_ref_walk_begin(&walker, ref, &p);
    double f_prev = -1.0;
    for (double s = 1.0; s < 60.0; s += 0.01) {
        pp_ref_walk_to(&walker, s, &p);
        const double h = side * 0.5 * ref->width;
        const double bx = p.x - (h * sin(p.theta));
        const double by = p.y + (h * cos(p.theta));
        const double f = side * ((bx * sin(p.theta)) - (by * cos(p.theta)));
        if ((f_prev < 0.0) && (f >= 0.0)) {
            return s;
        }
        f_prev = f;
    }
    return 0.0;
}

static void test_tangent_point_on_known_arc(void)
{
    const double sides[] = {1.0, -1.0};
    for (size_t i = 0U; i < 2U; i++) {
        fixture_t fx;
        result_t r;
        setup(&fx, sides[i] * KAPPA_TP15);
        run(&pp_calibration, &fx, &r);
        const double expected = brute_tangent_s(&fx.ref, sides[i]) / SPEED;
        PP_CHECK_NEAR(expected, 1.5, 0.05);
        const double found = lab_qtp_tangent_time(r.base, &r.lateral, &r.samples, sides[i], 1.75, 1.0, 2.0, 30U);
        PP_CHECK_NEAR(found, expected, 0.01);
        /* Phía ngoài không có tiếp điểm. */
        PP_CHECK(lab_qtp_tangent_time(r.base, &r.lateral, &r.samples, -sides[i], 1.75, 1.0, 2.0, 30U) == 0.0);
        /* Cửa sổ không chứa tiếp điểm thì không trả gì. */
        PP_CHECK(lab_qtp_tangent_time(r.base, &r.lateral, &r.samples, sides[i], 1.75, 1.0, 1.3, 30U) == 0.0);
    }
}

/* Trên cua có tiếp điểm trong cửa sổ: path dời về phía trong, đỉnh gần tiếp điểm, không quá biên độ,
 * điểm 0 giữ nguyên, về lại path gốc ở cuối tầm nhìn, mọi giá trị hữu hạn. */
static void test_correction_moves_inside_bounded_and_continuous(void)
{
    const double sides[] = {1.0, -1.0};
    for (size_t i = 0U; i < 2U; i++) {
        fixture_t fx;
        result_t r;
        setup(&fx, sides[i] * KAPPA_TP15);
        run(&pp_calibration, &fx, &r);
        PP_CHECK(r.ok);
        PP_CHECK(ws.fallback == 0U);
        PP_CHECK(ws.work >= 2U);
        PP_CHECK(memcmp(&r.mine[0], &r.base[0], sizeof(r.mine[0])) == 0);
        size_t k_peak = 0U;
        double peak = 0.0;
        for (size_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
            PP_CHECK(isfinite(r.mine[k].pose.x) && isfinite(r.mine[k].pose.y) && isfinite(r.mine[k].curvature));
            /* Lệch ngang có dấu theo pháp tuyến của path gốc. */
            const double yaw = (double)r.base[k].pose.yaw;
            const double lat = (-sin(yaw) * ((double)r.mine[k].pose.x - (double)r.base[k].pose.x))
                               + (cos(yaw) * ((double)r.mine[k].pose.y - (double)r.base[k].pose.y));
            PP_CHECK(sides[i] * lat >= -1e-4);
            if (fabs(lat) > peak) {
                peak = fabs(lat);
                k_peak = k;
            }
        }
        PP_CHECK(peak > 0.02);
        PP_CHECK(peak <= (double)pp_calibration.qtp_amplitude_m + 1e-3);
        PP_CHECK((k_peak >= 13U) && (k_peak <= 17U));
        PP_CHECK(hypot((double)r.mine[30].pose.x - (double)r.base[30].pose.x,
                       (double)r.mine[30].pose.y - (double)r.base[30].pose.y) < 1e-4);
        /* Độ cong đổi từ từ: mỗi bước 0,1 s, phần hiệu chỉnh thêm không quá jerk_target_hwa·dt/v². */
        for (size_t k = 1U; k < PP_TRAJECTORY_POINTS; k++) {
            const double step = fabs((double)r.mine[k].curvature - (double)r.mine[k - 1U].curvature);
            const double step_base = fabs((double)r.base[k].curvature - (double)r.base[k - 1U].curvature);
            PP_CHECK(step <= step_base + (((double)pp_calibration.jerk_target_hwa * 0.1) / (SPEED * SPEED)));
        }
        pp_path_check_t check;
        pp_feasibility_check(r.mine, &r.samples, &check);
        PP_CHECK(check.ay_max <= PP_AYSMAX);
        PP_CHECK(check.jerk_max <= (double)pp_calibration.jerk_target_hwa);
    }
}

static void test_straight_road_matches_base(void)
{
    fixture_t fx;
    result_t r;
    setup(&fx, 0.0);
    fx.start.d = 0.3;
    run(&pp_calibration, &fx, &r);
    PP_CHECK(r.ok);
    PP_CHECK(ws.fallback == 8U);
    PP_CHECK(memcmp(r.mine, r.base, sizeof(r.mine)) == 0);
}

/* Mỗi điều kiện của PP-TS-024 2.4 (và dữ liệu thiếu) cho đúng path quintic_duration và đúng mã. */
static void test_fallbacks_give_base_path(void)
{
    for (uint32_t c = 1U; c <= 11U; c++) {
        fixture_t fx;
        result_t r;
        pp_calibration_t cal = pp_calibration;
        uint32_t expected = c;
        setup(&fx, KAPPA_TP15);
        switch (c) {
        case 1U: fx.in.follow = true; break;
        case 2U: fx.in.start_from_car = true; break;
        case 3U: fx.in.recentering = true; break;
        case 4U: fx.in.d_target = 0.1; break;
        case 5U: fx.ref.coasting = true; break;
        case 6U: fx.in.objects = NULL; break;
        case 7U: fx.ref.view_end = 15.0; break;
        case 8U: fx.ref.centre.c[2] = 0.5 * 0.0005; break;
        case 9U: fx.ref.centre.c[2] = 0.5 * 0.0062; break;
        case 10U: cal.qtp_center_s = 1.0F; break;
        default: fx.ref.width = 2.5; break;
        }
        run(&cal, &fx, &r);
        PP_CHECK(r.ok);
        if (ws.fallback != expected) {
            (void)fprintf(stderr, "fallback case %u gave %u\n", (unsigned)c, (unsigned)ws.fallback);
        }
        PP_CHECK(ws.fallback == expected);
        PP_CHECK(memcmp(r.mine, r.base, sizeof(r.mine)) == 0);
    }
    /* Dữ liệu không hữu hạn. */
    fixture_t fx;
    result_t r;
    setup(&fx, KAPPA_TP15);
    fx.ref.width = NAN;
    pp_t7_reset(&ws);
    PP_CHECK(pp_t7_generate(&ws, &pp_calibration, &fx.in, r.mine, &r.samples));
    PP_CHECK(ws.fallback == 13U);
    PP_CHECK(ws.amp == 0.0);
}

/* Biên độ tăng theo ref_rate tới biên độ đích; giữ khi tiếp điểm còn trước cuối cửa sổ; tiếp điểm mất thì
 * thả về path gốc. Không có path cũ thì không tăng. Một điều kiện fallback thả ngay. */
static void test_ramp_hold_and_release(void)
{
    fixture_t fx;
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
    const double step = (double)pp_calibration.ref_rate * CYCLE_S;
    setup(&fx, KAPPA_TP15);
    pp_t7_reset(&ws);
    PP_CHECK(pp_t7_generate(&ws, &pp_calibration, &fx.in, pts, &samples));
    PP_CHECK(ws.fallback == 0U);
    PP_CHECK_NEAR(ws.amp, step, 1e-12);
    for (uint32_t i = 0U; i < RAMP_CYCLES; i++) {
        PP_CHECK(pp_t7_generate(&ws, &pp_calibration, &fx.in, pts, &samples));
    }
    PP_CHECK_NEAR(ws.amp, (double)pp_calibration.qtp_amplitude_m, 1e-9);

    /* Đang giữ: cửa sổ [1,6; 1,75] không chứa tiếp điểm 1,5 s nhưng vẫn giữ vì tiếp điểm ở trước cuối cửa sổ. */
    pp_calibration_t cal = pp_calibration;
    cal.qtp_center_s = 1.675F;
    cal.qtp_window_half_s = 0.075F;
    PP_CHECK(pp_t7_generate(&ws, &cal, &fx.in, pts, &samples));
    PP_CHECK(ws.fallback == 0U);
    pp_t7_reset(&ws);
    PP_CHECK(pp_t7_generate(&ws, &cal, &fx.in, pts, &samples));
    PP_CHECK(ws.fallback == 10U);

    /* Cuối cửa sổ ở 1,0 s: tiếp điểm 1,5 s mất, thả ngay về path gốc. */
    pp_t7_reset(&ws);
    for (uint32_t i = 0U; i < 10U; i++) {
        PP_CHECK(pp_t7_generate(&ws, &pp_calibration, &fx.in, pts, &samples));
    }
    cal.qtp_center_s = 1.0F;
    cal.qtp_window_half_s = 0.0F;
    PP_CHECK(pp_t7_generate(&ws, &cal, &fx.in, pts, &samples));
    PP_CHECK((ws.fallback == 10U) && (ws.amp == 0.0));

    /* Không có path cũ: không có thời gian giữa hai chu kỳ nên không bắt đầu. */
    fx.old.valid = false;
    pp_t7_reset(&ws);
    PP_CHECK(pp_t7_generate(&ws, &pp_calibration, &fx.in, pts, &samples));
    PP_CHECK(ws.fallback == 11U);

    /* Đang hiệu chỉnh mà FOLLOW bật: thả ngay. */
    fx.old.valid = true;
    pp_t7_reset(&ws);
    for (uint32_t i = 0U; i < 10U; i++) {
        PP_CHECK(pp_t7_generate(&ws, &pp_calibration, &fx.in, pts, &samples));
    }
    PP_CHECK(ws.amp > 0.0);
    fx.in.follow = true;
    PP_CHECK(pp_t7_generate(&ws, &pp_calibration, &fx.in, pts, &samples));
    PP_CHECK((ws.fallback == 1U) && (ws.amp == 0.0));
}

/* Vật thể ở làn bên phía trong cua chặn hiệu chỉnh; vật thể ở làn bên phía ngoài hay ở xa thì không. */
static void test_objects_by_side(void)
{
    const double ys[] = {3.5, -3.5, 3.5};
    const double xs[] = {20.0, 20.0, 200.0};
    const uint32_t expected[] = {6U, 0U, 0U};
    for (size_t i = 0U; i < 3U; i++) {
        fixture_t fx;
        result_t r;
        setup(&fx, KAPPA_TP15);
        fx.objects.num_objects = 1U;
        fx.objects.objects[0].x = (float)xs[i];
        fx.objects.objects[0].y = (float)(ys[i] + (0.5 * KAPPA_TP15 * xs[i] * xs[i]));
        fx.objects.objects[0].length = 4.5F;
        fx.objects.objects[0].width = 1.8F;
        fx.objects.objects[0].existence_probability = 0.9F;
        run(&pp_calibration, &fx, &r);
        PP_CHECK(ws.fallback == expected[i]);
    }
}

/* Biên độ không vượt hành lang (làn hẹp) cũng không vượt calibration; nửa ngắn làm biên độ nhỏ lại theo T³. */
static void test_amplitude_bound(void)
{
    fixture_t fx;
    result_t r;
    pp_calibration_t cal = pp_calibration;
    cal.qtp_amplitude_m = 0.5F;
    setup(&fx, KAPPA_TP15);
    fx.ref.width = 3.0;
    run(&cal, &fx, &r);
    const double corridor = (0.5 * (3.0 - 1.9)) - (double)cal.dlc_offset_min;
    PP_CHECK(ws.fallback == 0U);
    PP_CHECK(max_shift(&r) <= corridor + 1e-3);

    /* Tầm nhìn 2,3 s: nửa sau 0,8 s, jerk cho biên độ tối đa 2,5·0,8³/52,5 ≈ 0,024 m. */
    setup(&fx, KAPPA_TP15);
    fx.ref.view_end = 2.3 * SPEED + 0.5;
    run(&cal, &fx, &r);
    PP_CHECK((ws.fallback == 0U) || (ws.fallback == 11U) || (ws.fallback == 12U));
    PP_CHECK(max_shift(&r) <= 0.03);
}

int main(void)
{
    test_tangent_point_on_known_arc();
    test_correction_moves_inside_bounded_and_continuous();
    test_straight_road_matches_base();
    test_fallbacks_give_base_path();
    test_objects_by_side();
    test_ramp_hold_and_release();
    test_amplitude_bound();
    return PP_TEST_RESULT();
}

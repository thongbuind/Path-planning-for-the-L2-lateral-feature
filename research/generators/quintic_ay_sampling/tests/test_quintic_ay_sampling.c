/* L0 riêng của quintic_ay_sampling. Contract chung đã có ở tests/planner/c/test_t7_contract.c. */

#include <math.h>
#include <string.h>

#include "driver_shape.h"
#include "feasibility.h"
#include "generators/pp_t7.h"
#include "generators/t7_common.h"
#include "output.h"
#include "pp_calibration.h"
#include "pp_test.h"

static const pp_vehicle_config_t VP0 = {2.9F, 1.45F, 1.9F, 15.0F, 0.61F, 6.0F, 0.05F};

typedef struct {
    pp_reference_line_t ref;
    pp_lateral_state_t start;
    pp_speed_profile_t speed;
    pp_old_path_t old;
    pp_object_list_t objects;
    pp_t7_input_t in;
} fixture_t;

static fixture_t fx;
static pp_t7_ws_t ws;

/* Cua ngắn: kappa(s) = kappa0 sin²(pi (s - s0)/len) trên [s0, s0 + len], 0 ngoài đoạn đó. Node lấy mẫu
 * mỗi 2 m; theta tích phân đúng công thức Hermite của node nên closure bằng 0. */
static double bell(double s, double kappa0, double s0, double len, double *dkappa)
{
    double kappa = 0.0;
    *dkappa = 0.0;
    if ((s > s0) && (s < (s0 + len))) {
        const double w = acos(-1.0) / len;
        const double phase = w * (s - s0);
        kappa = kappa0 * sin(phase) * sin(phase);
        *dkappa = kappa0 * w * sin(2.0 * phase);
    }
    return kappa;
}

static void setup_curve(double kappa0, double v, double s0, double len)
{
    (void)memset(&fx, 0, sizeof(fx));
    pp_reference_line_t *ref = &fx.ref;
    pp_ref_nodes_t *nd = &ref->nodes;
    ref->valid = true;
    ref->sampled = true;
    ref->width = 3.5;
    ref->view_end = 200.0;
    nd->n = PP_REF_NODES;
    nd->origin = 0U;
    for (uint32_t i = 0U; i < nd->n; i++) {
        nd->s[i] = (double)i * PP_REF_STEP_M;
        nd->kappa[i] = bell(nd->s[i], kappa0, s0, len, &nd->dkappa[i]);
        if (i > 0U) {
            const double h = PP_REF_STEP_M;
            const double ki = nd->kappa[i - 1U];
            const double kj = nd->kappa[i];
            nd->theta[i] = nd->theta[i - 1U]
                           + (h * ((0.5 * (ki + kj)) + (h * (nd->dkappa[i - 1U] - nd->dkappa[i]) / 12.0)));
            const double mid = 0.5 * (nd->theta[i - 1U] + nd->theta[i]);
            nd->x[i] = nd->x[i - 1U] + (h * cos(mid));
            nd->y[i] = nd->y[i - 1U] + (h * sin(mid));
        }
    }
    pp_speed_profile(NULL, 0U, v, &fx.speed);
    fx.in.ref = ref;
    fx.in.start = &fx.start;
    fx.in.speed = &fx.speed;
    fx.in.old = &fx.old;
    fx.in.objects = &fx.objects;
    fx.in.vehicle = &VP0;
}

/* Đường thẳng không lấy mẫu node, tầm nhìn view_end [m]. */
static void setup_straight(double view_end, double v)
{
    (void)memset(&fx, 0, sizeof(fx));
    fx.ref.valid = true;
    fx.ref.width = 3.5;
    fx.ref.view_end = view_end;
    pp_speed_profile(NULL, 0U, v, &fx.speed);
    fx.in.ref = &fx.ref;
    fx.in.start = &fx.start;
    fx.in.speed = &fx.speed;
    fx.in.old = &fx.old;
    fx.in.objects = &fx.objects;
    fx.in.vehicle = &VP0;
}

static void set_object(pp_object_t *o, double x, double y)
{
    (void)memset(o, 0, sizeof(*o));
    o->id = 7U;
    o->x = (float)x;
    o->y = (float)y;
    o->length = 4.5F;
    o->width = 1.8F;
    o->existence_probability = 1.0F;
}

typedef struct {
    pp_lateral_path_t lateral;
    pp_trajectory_point_t points[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
} base_t;

static bool make_base(const pp_calibration_t *cal, base_t *b)
{
    return pp_t7_quintic_search(cal, &fx.in, &b->lateral, b->points, &b->samples, NULL);
}

static bool finite_points(const pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS])
{
    bool ok = true;
    for (size_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        const pp_trajectory_point_t *p = &pts[k];
        ok = ok && isfinite(p->pose.x) && isfinite(p->pose.y) && isfinite(p->pose.yaw) && isfinite(p->curvature)
             && isfinite(p->heading_rate_rps) && isfinite(p->front_wheel_angle_rad);
    }
    return ok;
}

/* Dự báo của lab_qas_predict khớp T11 và pp_feasibility_check thật, có và không có hiệu chỉnh. */
static void test_prediction_matches_t11(void)
{
    base_t b;
    lab_qas_frame_t frame;
    pp_lateral_path_t zero;
    pp_lateral_path_t shape;
    pp_path_check_t check;
    double ay;
    double jerk;
    setup_curve(0.00375, 20.0, 36.0, 35.0);
    fx.start.d = 0.1;
    fx.start.d_dot = -0.05;
    PP_CHECK(make_base(&pp_calibration, &b));
    lab_qas_frame(&fx.in, &frame);
    (void)memset(&zero, 0, sizeof(zero));
    PP_CHECK(lab_driver_bump(&zero, 3.0, 1.2, 1.0, 2.0, &shape));
    pp_feasibility_check(b.points, &b.samples, &check);
    lab_qas_predict(&frame, &b.lateral, &shape, 0.0, &ay, &jerk);
    PP_CHECK_NEAR(ay, check.ay_max, 1e-9);
    PP_CHECK_NEAR(jerk, check.jerk_max, 1e-9);

    pp_lateral_path_t moved;
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    for (size_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        moved.d[k] = b.lateral.d[k] + (0.2 * shape.d[k]);
        moved.d_dot[k] = b.lateral.d_dot[k] + (0.2 * shape.d_dot[k]);
        moved.d_ddot[k] = b.lateral.d_ddot[k] + (0.2 * shape.d_ddot[k]);
    }
    PP_CHECK(pp_output_points(&fx.ref, &moved, &fx.speed, (double)VP0.wheelbase, pts, NULL));
    pp_feasibility_check(pts, &b.samples, &check);
    lab_qas_predict(&frame, &b.lateral, &shape, 0.2, &ay, &jerk);
    PP_CHECK_NEAR(ay, check.ay_max, 1e-6);
    PP_CHECK_NEAR(jerk, check.jerk_max, 1e-5);
}

/* Trên cua ngắn đã biết (a_y cần 1,5 m/s², dài 1,75 s, bắt đầu sau 1,8 s), ứng viên được chọn có a_y dự báo nhỏ nhất trong mọi ứng viên đạt điều kiện jerk
 * (vét cạn cả tập), giảm a_y ít nhất qas_ay_gain_min_mps2, và path ra đúng là base + offset × shape. */
static void test_scoring_picks_lowest_admissible(void)
{
    const pp_calibration_t *cal = &pp_calibration;
    base_t b;
    lab_qas_choice_t choice;
    lab_qas_frame_t frame;
    pp_lateral_path_t zero;
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    setup_curve(0.00375, 20.0, 36.0, 35.0);
    PP_CHECK(make_base(cal, &b));
    (void)memcpy(pts, b.points, sizeof(pts));
    PP_CHECK(lab_qas_correct(cal, &fx.in, &b.lateral, pts, &b.samples, &choice) == LAB_QAS_APPLIED);
    PP_CHECK(choice.ay_best <= (choice.ay_base - (double)cal->qas_ay_gain_min_mps2));
    PP_CHECK(choice.jerk_best <= (choice.jerk_base + (double)cal->qas_jerk_tol_mps3));
    PP_CHECK(choice.evaluated > 0U);
    PP_CHECK(memcmp(pts, b.points, sizeof(pts)) != 0);

    lab_qas_frame(&fx.in, &frame);
    (void)memset(&zero, 0, sizeof(zero));
    const double end = choice.end_s;
    const double peaks[2] = {(double)cal->qas_peak_early * end, (double)cal->qas_peak_late * end};
    const double step = (double)cal->qas_amplitude_step_m;
    const double top = (double)cal->qas_amplitude_m;
    double best = INFINITY;
    for (size_t p = 0U; p < 2U; p++) {
        pp_lateral_path_t shape;
        PP_CHECK(lab_driver_bump(&zero, end, peaks[p], 1.0, 2.0, &shape));
        for (uint32_t j = 1U; ((double)(j - 1U) * step) < top; j++) {
            for (int side = 0; side < 2; side++) {
                const double offset = (side == 0 ? 1.0 : -1.0) * fmin((double)j * step, top);
                double ay;
                double jerk;
                lab_qas_predict(&frame, &b.lateral, &shape, offset, &ay, &jerk);
                const bool ok = (ay <= PP_AYSMAX) && (jerk <= choice.jerk_base + (double)cal->qas_jerk_tol_mps3)
                                && ((jerk <= (double)cal->jerk_target_hwa) || (jerk <= choice.jerk_base));
                if (ok) {
                    best = fmin(best, ay);
                }
            }
        }
        if (fabs(peaks[p] - choice.peak_s) < 1e-12) {
            pp_lateral_path_t moved;
            pp_trajectory_point_t expect[PP_TRAJECTORY_POINTS];
            for (size_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
                moved.d[k] = b.lateral.d[k] + (choice.offset_m * shape.d[k]);
                moved.d_dot[k] = b.lateral.d_dot[k] + (choice.offset_m * shape.d_dot[k]);
                moved.d_ddot[k] = b.lateral.d_ddot[k] + (choice.offset_m * shape.d_ddot[k]);
            }
            PP_CHECK(pp_output_points(&fx.ref, &moved, &fx.speed, (double)VP0.wheelbase, expect, NULL));
            PP_CHECK(memcmp(pts, expect, sizeof(pts)) == 0);
        }
    }
    PP_CHECK_NEAR(choice.ay_best, best, 1e-6);
    /* Lần chạy qua pp_t7_generate cho cùng path. */
    pp_trajectory_point_t again[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
    pp_t7_reset(&ws);
    PP_CHECK(pp_t7_generate(&ws, cal, &fx.in, again, &samples));
    PP_CHECK(memcmp(pts, again, sizeof(pts)) == 0);
    PP_CHECK(ws.fallback == LAB_QAS_APPLIED);
    PP_CHECK(ws.work >= choice.evaluated + 1U);
}

/* Đường thẳng: không có hiệu chỉnh, path trùng quintic_duration từng bit. */
static void test_straight_road_zero_correction(void)
{
    base_t b;
    pp_trajectory_point_t mine[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
    setup_straight(80.0, 25.0);
    fx.start.d = 0.3;
    pp_t7_reset(&ws);
    PP_CHECK(pp_t7_generate(&ws, &pp_calibration, &fx.in, mine, &samples));
    PP_CHECK(ws.fallback == LAB_QAS_NO_CURVE);
    PP_CHECK(make_base(&pp_calibration, &b));
    PP_CHECK(memcmp(mine, b.points, sizeof(mine)) == 0);
}

/* Mỗi điều kiện không áp dụng cho đúng mã lý do và giữ path quintic_duration từng bit. */
static void expect_fallback(uint32_t code)
{
    base_t b;
    pp_trajectory_point_t mine[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
    pp_t7_reset(&ws);
    PP_CHECK(pp_t7_generate(&ws, &pp_calibration, &fx.in, mine, &samples));
    if (ws.fallback != code) {
        (void)fprintf(stderr, "fallback %u, expected %u\n", ws.fallback, code);
    }
    PP_CHECK(ws.fallback == code);
    PP_CHECK(make_base(&pp_calibration, &b));
    PP_CHECK(memcmp(mine, b.points, sizeof(mine)) == 0);
}

static void test_fallback_triggers(void)
{
    setup_curve(0.00375, 20.0, 36.0, 35.0);
    fx.in.follow = true;
    expect_fallback(LAB_QAS_FOLLOW);
    setup_curve(0.00375, 20.0, 36.0, 35.0);
    fx.in.start_from_car = true;
    expect_fallback(LAB_QAS_START_FROM_CAR);
    setup_curve(0.00375, 20.0, 36.0, 35.0);
    fx.in.recentering = true;
    expect_fallback(LAB_QAS_RECENTERING);
    setup_curve(0.00375, 20.0, 36.0, 35.0);
    fx.in.d_target = 0.2;
    expect_fallback(LAB_QAS_OFFSET);
    setup_curve(0.00375, 20.0, 36.0, 35.0);
    fx.ref.coasting = true;
    expect_fallback(LAB_QAS_LANE);
    setup_curve(0.00375, 20.0, 36.0, 35.0);
    fx.ref.line_rejected[1] = true;
    expect_fallback(LAB_QAS_LANE);
    setup_curve(0.00375, 20.0, 36.0, 35.0);
    fx.in.objects = NULL;
    expect_fallback(LAB_QAS_OBJECTS);
    setup_curve(0.00375, 20.0, 36.0, 35.0);
    fx.objects.num_objects = 2U;
    set_object(&fx.objects.objects[0], 20.0, 3.4);
    set_object(&fx.objects.objects[1], -10.0, -3.6);
    expect_fallback(LAB_QAS_OBJECTS);
    setup_curve(0.00375, 20.0, 36.0, 35.0);
    fx.objects.num_objects = 1U;
    set_object(&fx.objects.objects[0], NAN, 0.0);
    expect_fallback(LAB_QAS_OBJECTS);
    setup_straight(30.0, 20.0);
    expect_fallback(LAB_QAS_SHORT_VIEW);
    setup_curve(0.00375, 20.0, 36.0, 35.0);
    fx.ref.width = 2.5;
    expect_fallback(LAB_QAS_CORRIDOR);
    setup_curve(0.00375, 20.0, 36.0, 35.0);
    fx.start.d = 0.7;  /* Path gốc bắt đầu ngoài hành lang 0,5 m. */
    expect_fallback(LAB_QAS_CORRIDOR);
    setup_curve(0.00615, 20.0, 36.0, 35.0);  /* a_y cần 2,46 m/s². */
    expect_fallback(LAB_QAS_SHARP_CURVE);
    setup_curve(0.0040, 20.0, -10.0, 200.0);  /* Cung dài gần đều: không ứng viên nào giảm đỉnh a_y. */
    expect_fallback(LAB_QAS_NO_GAIN);
}

/* Vật thể ở làn kề chỉ chặn phía của nó; xe trước giữa làn và vật thể cách hai làn không chặn. */
static void test_object_sides(void)
{
    base_t b;
    lab_qas_choice_t free_choice;
    lab_qas_choice_t choice;
    pp_trajectory_point_t free_pts[PP_TRAJECTORY_POINTS];
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    setup_curve(0.00375, 20.0, 36.0, 35.0);
    PP_CHECK(make_base(&pp_calibration, &b));
    (void)memcpy(free_pts, b.points, sizeof(free_pts));
    PP_CHECK(lab_qas_correct(&pp_calibration, &fx.in, &b.lateral, free_pts, &b.samples, &free_choice)
             == LAB_QAS_APPLIED);

    fx.objects.num_objects = 2U;
    set_object(&fx.objects.objects[0], 30.0, 0.2);  /* Xe trước trong làn. */
    set_object(&fx.objects.objects[1], 15.0, -8.0);  /* Cách hai làn. */
    (void)memcpy(pts, b.points, sizeof(pts));
    PP_CHECK(lab_qas_correct(&pp_calibration, &fx.in, &b.lateral, pts, &b.samples, &choice) == LAB_QAS_APPLIED);
    PP_CHECK(memcmp(pts, free_pts, sizeof(pts)) == 0);

    /* Chặn đúng phía của ứng viên vừa chọn: chỉ còn phía kia. */
    fx.objects.num_objects = 1U;
    set_object(&fx.objects.objects[0], 10.0, (free_choice.offset_m > 0.0) ? 3.4 : -3.4);
    (void)memcpy(pts, b.points, sizeof(pts));
    const uint32_t reason = lab_qas_correct(&pp_calibration, &fx.in, &b.lateral, pts, &b.samples, &choice);
    PP_CHECK((reason == LAB_QAS_APPLIED) || (reason == LAB_QAS_NO_GAIN));
    PP_CHECK((choice.offset_m * free_choice.offset_m) <= 0.0);
}

/* Biên độ thực không vượt qas_amplitude_m, và |d| của path không vượt hành lang. */
static void test_amplitude_bound(void)
{
    const double widths[3] = {3.5, 3.0, 2.9};
    const float amplitudes[3] = {0.05F, 0.2F, 0.5F};
    uint32_t applied = 0U;
    uint32_t capped = 0U;
    for (size_t w = 0U; w < 3U; w++) {
        for (size_t a = 0U; a < 3U; a++) {
            pp_calibration_t cal = pp_calibration;
            base_t b;
            lab_qas_choice_t choice;
            pp_lateral_path_t zero;
            pp_lateral_path_t shape;
            pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
            cal.qas_amplitude_m = amplitudes[a];
            setup_curve(0.00375, 20.0, 36.0, 35.0);
            fx.ref.width = widths[w];
            fx.start.d = 0.05;
            PP_CHECK(make_base(&cal, &b));
            (void)memcpy(pts, b.points, sizeof(pts));
            const uint32_t reason = lab_qas_correct(&cal, &fx.in, &b.lateral, pts, &b.samples, &choice);
            PP_CHECK((reason == LAB_QAS_APPLIED) || (reason == LAB_QAS_NO_GAIN));
            PP_CHECK(fabs(choice.offset_m) <= (double)cal.qas_amplitude_m + 1e-12);
            if (reason == LAB_QAS_APPLIED) {
                applied++;
                const double corridor = (0.5 * (widths[w] - (double)VP0.vehicle_width))
                                        - (double)cal.qas_corridor_margin_m;
                (void)memset(&zero, 0, sizeof(zero));
                PP_CHECK(lab_driver_bump(&zero, choice.end_s, choice.peak_s, 1.0, 2.0, &shape));
                for (size_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
                    PP_CHECK(fabs(b.lateral.d[k] + (choice.offset_m * shape.d[k])) <= corridor + 1e-12);
                }
                capped += (fabs(choice.offset_m) < (double)cal.qas_amplitude_m - 1e-9) ? 1U : 0U;
            }
        }
    }
    PP_CHECK(applied >= 3U);
    PP_CHECK(capped >= 1U);
}

/* Output hữu hạn trên nhiều input; input không hữu hạn thì không có path, mã 13, ws dùng tiếp được. */
static void test_finite_outputs(void)
{
    const double kappas[4] = {0.0, 0.002, -0.004, 0.0055};
    const double speeds[3] = {8.0, 20.0, 33.0};
    const double starts[3] = {-0.4, 0.0, 0.25};
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    pp_trajectory_point_t first[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
    for (size_t i = 0U; i < 4U; i++) {
        for (size_t j = 0U; j < 3U; j++) {
            for (size_t k = 0U; k < 3U; k++) {
                setup_curve(kappas[i] * 400.0 / (speeds[j] * speeds[j]), speeds[j], 10.0, 1.8 * speeds[j]);
                fx.start.d = starts[k];
                pp_t7_reset(&ws);
                PP_CHECK(pp_t7_generate(&ws, &pp_calibration, &fx.in, pts, &samples));
                PP_CHECK(finite_points(pts));
            }
        }
    }
    setup_curve(0.00375, 20.0, 36.0, 35.0);
    pp_t7_reset(&ws);
    PP_CHECK(pp_t7_generate(&ws, &pp_calibration, &fx.in, first, &samples));
    fx.in.d_target = NAN;
    PP_CHECK(!pp_t7_generate(&ws, &pp_calibration, &fx.in, pts, &samples));
    PP_CHECK(ws.fallback == LAB_QAS_BASE_FAILED);
    fx.in.d_target = 0.0;
    fx.ref.width = NAN;
    PP_CHECK(pp_t7_generate(&ws, &pp_calibration, &fx.in, pts, &samples));
    PP_CHECK(ws.fallback == LAB_QAS_CORRIDOR);
    fx.ref.width = 3.5;
    PP_CHECK(pp_t7_generate(&ws, &pp_calibration, &fx.in, pts, &samples));
    PP_CHECK(memcmp(first, pts, sizeof(pts)) == 0);
}

int main(void)
{
    test_prediction_matches_t11();
    test_scoring_picks_lowest_admissible();
    test_straight_road_zero_correction();
    test_fallback_triggers();
    test_object_sides();
    test_amplitude_bound();
    test_finite_outputs();
    return PP_TEST_RESULT();
}

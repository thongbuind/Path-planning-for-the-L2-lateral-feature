/* L0 riêng của qp_jerk_admm_mlp_warmstart. Contract chung đã có ở tests/planner/c/test_t7_contract.c. */

#include <math.h>
#include <string.h>

#include "generators/pp_t7.h"
#include "generators/qp.h"
#include "generators/t7_common.h"
#include "output.h"
#include "pp_calibration.h"
#include "pp_test.h"
#include "weights.h"
#include "mlp_fixture.h"
#include "mlp_l0.h"
#include "../../qp_jerk_admm_shift_warmstart/src/shift.h"

static const pp_vehicle_config_t VP0 = {2.9F, 1.45F, 1.9F, 15.0F, 0.61F, 6.0F, 0.05F};
static pp_t7_ws_t ws;
static pp_qp_ws_t plain;

typedef struct {
    pp_reference_line_t ref;
    pp_lateral_state_t start;
    pp_speed_profile_t speed;
    pp_old_path_t old;
    pp_t7_input_t in;
} fixture_t;

static void setup(fixture_t *fx, double d0, double kappa, double v)
{
    (void)memset(fx, 0, sizeof(*fx));
    fx->ref.valid = true;
    fx->ref.centre.c[2] = 0.5 * kappa;
    fx->ref.width = 3.5;
    fx->ref.view_end = 80.0;
    fx->start.d = d0;
    pp_speed_profile(NULL, 0U, v, &fx->speed);
    fx->in.ref = &fx->ref;
    fx->in.start = &fx->start;
    fx->in.speed = &fx->speed;
    fx->in.old = &fx->old;
    fx->in.recentering = true;
    fx->in.vehicle = &VP0;
}

/* Trong miền, khởi động lạnh: kết quả trùng từng bit với pp_generate_qp_seeded từ jerk MLP đã kẹp; đúng qp_iters
 * vòng với mọi mức của PP-TS-031. */
static void test_mlp_seed_and_exact_iterations(void)
{
    static const float levels[] = {10.0F, 25.0F, 50.0F, 75.0F, 150.0F};
    fixture_t fx;
    pp_trajectory_point_t mine[PP_TRAJECTORY_POINTS];
    pp_trajectory_point_t base[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
    pp_qp_problem_t pb;
    pp_lateral_path_t lateral;
    double features[MLP_FEATURES];
    double seed[PP_QP_N];
    setup(&fx, 0.3, 0.002, 25.0);
    for (size_t i = 0U; i < (sizeof(levels) / sizeof(levels[0])); i++) {
        pp_calibration_t cal = pp_calibration;
        cal.qp_iters = levels[i];
        pp_t7_reset(&ws);
        PP_CHECK(pp_t7_generate(&ws, &cal, &fx.in, mine, &samples));
        PP_CHECK(ws.fallback == MLP_OK);
        PP_CHECK(ws.infer_ops == MLP_OPS);
        PP_CHECK(ws.qp.iterations == (uint32_t)levels[i]);
        pp_t7_qp_problem(&cal, &fx.in, &pb);
        mlp_features(&pb, features);
        PP_CHECK(mlp_jerk(&MLP_MODEL, features, seed, NULL) == MLP_OK);
        (void)mlp_clamp_jerk(&pb, seed);
        pp_qp_reset(&plain);
        PP_CHECK(pp_generate_qp_seeded(&plain, &cal, &pb, seed, &lateral));
        PP_CHECK(pp_output_points(fx.in.ref, &lateral, fx.in.speed, (double)VP0.wheelbase, base, &samples));
        PP_CHECK(memcmp(mine, base, sizeof(mine)) == 0);
    }
}

/* Ngoài miền (216 km/h): không dùng MLP, không có phép nhân của MLP; không dịch được (khởi động lạnh) nên kết
 * quả trùng từng bit với qp_jerk_admm. */
static void test_out_of_domain_falls_back(void)
{
    fixture_t fx;
    pp_trajectory_point_t mine[PP_TRAJECTORY_POINTS];
    pp_trajectory_point_t base[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
    pp_qp_problem_t pb;
    pp_lateral_path_t lateral;
    setup(&fx, 0.3, 0.0, 60.0);
    pp_calibration_t cal = pp_calibration;
    cal.qp_iters = 25.0F;
    pp_t7_reset(&ws);
    PP_CHECK(pp_t7_generate(&ws, &cal, &fx.in, mine, &samples));
    PP_CHECK(ws.fallback == MLP_OUT_OF_DOMAIN);
    PP_CHECK(ws.infer_ops == 0U);
    PP_CHECK(!ws.shifted);
    PP_CHECK(ws.qp.iterations == 25U);
    pp_t7_qp_problem(&cal, &fx.in, &pb);
    pp_qp_reset(&plain);
    PP_CHECK(pp_generate_qp(&plain, &cal, &pb, &lateral));
    PP_CHECK(pp_output_points(fx.in.ref, &lateral, fx.in.speed, (double)VP0.wheelbase, base, &samples));
    PP_CHECK(memcmp(mine, base, sizeof(mine)) == 0);
}

/* Ngoài miền ở chu kỳ sau, nghiệm trước dịch được: dự phòng là warm start dịch thời gian của luồng A với
 * sws_shift_vars = 1 (dịch ba khối x bằng sws_shift_hold, giữ y), trùng từng bit. */
static void test_out_of_domain_shift_fallback(void)
{
    fixture_t fx;
    pp_trajectory_point_t mine[PP_TRAJECTORY_POINTS];
    pp_trajectory_point_t base[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
    pp_qp_problem_t pb;
    pp_lateral_path_t lateral;
    setup(&fx, 0.3, 0.0, 60.0);
    pp_calibration_t cal = pp_calibration;
    cal.qp_iters = 25.0F;
    pp_t7_reset(&ws);
    PP_CHECK(pp_t7_generate(&ws, &cal, &fx.in, mine, &samples));
    pp_t7_qp_problem(&cal, &fx.in, &pb);
    pp_qp_reset(&plain);
    PP_CHECK(pp_generate_qp(&plain, &cal, &pb, &lateral));
    fx.in.from_old = true;
    fx.old.valid = true;
    fx.old.shift_s = 0.05;
    PP_CHECK(pp_t7_generate(&ws, &cal, &fx.in, mine, &samples));
    PP_CHECK(ws.fallback == MLP_OUT_OF_DOMAIN);
    PP_CHECK(ws.shifted);
    for (size_t b = 0U; b < 3U; b++) {
        PP_CHECK(sws_shift_hold(&plain.x[b * PP_QP_N], &plain.x[b * PP_QP_N], PP_QP_N, PP_GRID_STEP_S, 0.05));
    }
    pp_t7_qp_problem(&cal, &fx.in, &pb);
    PP_CHECK(pp_generate_qp(&plain, &cal, &pb, &lateral));
    PP_CHECK(pp_output_points(fx.in.ref, &lateral, fx.in.speed, (double)VP0.wheelbase, base, &samples));
    PP_CHECK(memcmp(mine, base, sizeof(mine)) == 0);
    PP_CHECK(memcmp(ws.qp.y, plain.y, sizeof(plain.y)) == 0);
}

/* qmw_seed_mode = 1: chu kỳ đầu (không có nghiệm trước) dùng MLP; chu kỳ sau dịch được nên bỏ qua MLP
 * (QMW_SHIFT_PREFERRED, không phép nhân nào) và trùng từng bit với bản dịch của luồng A. */
static void test_seed_mode_prefers_shift(void)
{
    fixture_t fx;
    pp_trajectory_point_t mine[PP_TRAJECTORY_POINTS];
    pp_trajectory_point_t base[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
    pp_qp_problem_t pb;
    pp_lateral_path_t lateral;
    double features[MLP_FEATURES];
    double seed[PP_QP_N];
    setup(&fx, 0.3, 0.002, 25.0);
    pp_calibration_t cal = pp_calibration;
    cal.qp_iters = 25.0F;
    cal.qmw_seed_mode = 1.0F;
    pp_t7_reset(&ws);
    PP_CHECK(pp_t7_generate(&ws, &cal, &fx.in, mine, &samples));
    PP_CHECK(ws.fallback == MLP_OK);
    pp_t7_qp_problem(&cal, &fx.in, &pb);
    mlp_features(&pb, features);
    PP_CHECK(mlp_jerk(&MLP_MODEL, features, seed, NULL) == MLP_OK);
    (void)mlp_clamp_jerk(&pb, seed);
    pp_qp_reset(&plain);
    PP_CHECK(pp_generate_qp_seeded(&plain, &cal, &pb, seed, &lateral));
    fx.in.from_old = true;
    fx.old.valid = true;
    fx.old.shift_s = 0.05;
    PP_CHECK(pp_t7_generate(&ws, &cal, &fx.in, mine, &samples));
    PP_CHECK(ws.fallback == QMW_SHIFT_PREFERRED);
    PP_CHECK(ws.infer_ops == 0U);
    PP_CHECK(ws.shifted);
    for (size_t b = 0U; b < 3U; b++) {
        PP_CHECK(sws_shift_hold(&plain.x[b * PP_QP_N], &plain.x[b * PP_QP_N], PP_QP_N, PP_GRID_STEP_S, 0.05));
    }
    pp_t7_qp_problem(&cal, &fx.in, &pb);
    PP_CHECK(pp_generate_qp(&plain, &cal, &pb, &lateral));
    PP_CHECK(pp_output_points(fx.in.ref, &lateral, fx.in.speed, (double)VP0.wheelbase, base, &samples));
    PP_CHECK(memcmp(mine, base, sizeof(mine)) == 0);
}

/* Warm start MLP gần nghiệm hơn khởi động lạnh: sau 10 vòng, lệch jerk so với nghiệm 1000 vòng nhỏ hơn. */
static void test_seed_helps_at_ten_iterations(void)
{
    fixture_t fx;
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
    pp_qp_problem_t pb;
    pp_lateral_path_t lateral;
    setup(&fx, 0.3, 0.002, 25.0);
    pp_calibration_t cal = pp_calibration;
    cal.qp_iters = 1000.0F;
    pp_t7_qp_problem(&cal, &fx.in, &pb);
    pp_qp_reset(&plain);
    PP_CHECK(pp_generate_qp(&plain, &cal, &pb, &lateral));
    double ref[PP_QP_N];
    (void)memcpy(ref, plain.x, sizeof(ref));
    cal.qp_iters = 10.0F;
    pp_qp_reset(&plain);
    PP_CHECK(pp_generate_qp(&plain, &cal, &pb, &lateral));
    pp_t7_reset(&ws);
    PP_CHECK(pp_t7_generate(&ws, &cal, &fx.in, pts, &samples));
    double cold = 0.0;
    double mlp = 0.0;
    for (size_t k = 0U; k < PP_QP_N; k++) {
        cold = fmax(cold, fabs(plain.x[k] - ref[k]));
        mlp = fmax(mlp, fabs(ws.qp.x[k] - ref[k]));
    }
    PP_CHECK(mlp < cold);
}

int main(void)
{
    mlp_l0_all();
    test_mlp_seed_and_exact_iterations();
    test_out_of_domain_falls_back();
    test_out_of_domain_shift_fallback();
    test_seed_mode_prefers_shift();
    test_seed_helps_at_ten_iterations();
    return PP_TEST_RESULT();
}

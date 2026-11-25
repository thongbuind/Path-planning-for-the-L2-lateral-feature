/* L0 riêng của qp_jerk_admm_mlp_weights. Contract chung đã có ở tests/planner/c/test_t7_contract.c. */

#include <math.h>
#include <string.h>

#include "generators/pp_t7.h"
#include "generators/qp.h"
#include "generators/t7_common.h"
#include "mlp_features.h"
#include "mlpw_infer.h"
#include "mlpw_step.h"
#include "output.h"
#include "pp_calibration.h"
#include "pp_test.h"
#include "weights.h"
#include "mlpw_fixture.h"

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

/* Bố cục TR_PROBLEM của teacher (như mlp_l0.h của luồng C). */
static void unpack(const double *p, pp_qp_problem_t *pb)
{
    const size_t n = PP_QP_N;
    (void)memset(pb, 0, sizeof(*pb));
    pb->start.d = p[0];
    pb->start.d_dot = p[1];
    pb->start.d_ddot = p[2];
    pb->start.heading = p[3];
    pb->d_target = p[4];
    for (size_t k = 0U; k < n; k++) {
        pb->v[k] = p[5U + k];
        pb->kappa[k] = p[5U + n + k];
        pb->dkappa[k] = p[5U + (2U * n) + k];
        pb->d_max[k] = p[5U + (3U * n) + k];
        pb->d_min[k] = p[5U + (4U * n) + k];
        pb->d_old[k] = p[5U + (5U * n) + k];
        pb->has_old[k] = p[5U + (6U * n) + k] > 0.5;
    }
    pb->ay_limit = p[5U + (7U * n)];
    pb->jerk_limit = p[6U + (7U * n)];
}

static void default_u(double u[MLPW_OUTPUTS])
{
    u[0] = log((double)pp_calibration.qp_w_dev);
    u[1] = log((double)pp_calibration.qp_w_jerk);
    u[2] = (double)pp_calibration.qp_a_comfort;
}

static void test_features_match_python(void)
{
    for (size_t i = 0U; i < FIX_PROBLEMS; i++) {
        pp_qp_problem_t pb;
        double out[MLP_FEATURES];
        unpack(&fix_problem[i * FIX_PROBLEM_SIZE], &pb);
        mlp_features(&pb, out);
        for (size_t f = 0U; f < MLP_FEATURES; f++) {
            PP_CHECK_NEAR(out[f], fix_features[(i * MLP_FEATURES) + f], 1e-12 * (1.0 + fabs(out[f])));
        }
    }
}

/* Suy luận C của cả ba model trùng numpy float64 (u chưa kẹp, sai số float32). */
static void test_inference_matches_numpy(void)
{
    PP_CHECK(FIX_MODELS == MLPW_MODEL_COUNT);
    for (size_t m = 0U; m < MLPW_MODEL_COUNT; m++) {
        for (size_t i = 0U; i < FIX_VECTORS; i++) {
            double u[MLPW_OUTPUTS];
            uint32_t ops = 0U;
            PP_CHECK(mlpw_infer(mlpw_models[m], &fix_x[i * MLP_FEATURES], u, &ops) == MLPW_OK);
            PP_CHECK(ops == MLPW_OPS);
            for (size_t k = 0U; k < MLPW_OUTPUTS; k++) {
                const double want = fix_u[(((m * FIX_VECTORS) + i) * MLPW_OUTPUTS) + k];
                PP_CHECK_NEAR(u[k], want, 1e-4 + (1e-4 * fabs(want)));
            }
        }
    }
}

/* Vector cuối là bản soi gương của vector đầu: trọng số trùng đúng từng bit. */
static void test_mirror_exact(void)
{
    for (size_t m = 0U; m < MLPW_MODEL_COUNT; m++) {
        double a[MLPW_OUTPUTS];
        double b[MLPW_OUTPUTS];
        PP_CHECK(mlpw_infer(mlpw_models[m], &fix_x[0], a, NULL) == MLPW_OK);
        PP_CHECK(mlpw_infer(mlpw_models[m], &fix_x[(FIX_VECTORS - 1U) * MLP_FEATURES], b, NULL) == MLPW_OK);
        PP_CHECK(memcmp(a, b, sizeof(a)) == 0);
    }
}

static void test_out_of_domain_rejected(void)
{
    double u[MLPW_OUTPUTS] = {123.0, 123.0, 123.0};
    double x[MLP_FEATURES];
    uint32_t ops = 7U;
    const mlpw_model_t *model = mlpw_model(&pp_calibration);
    PP_CHECK(mlpw_infer(model, fix_ood, u, &ops) == MLPW_OUT_OF_DOMAIN);
    PP_CHECK(ops == 0U);
    PP_CHECK(u[0] == 123.0);
    (void)memcpy(x, &fix_x[0], sizeof(x));
    x[3] = NAN;
    PP_CHECK(mlpw_infer(model, x, u, &ops) == MLPW_NOT_FINITE);
    (void)memcpy(x, &fix_x[0], sizeof(x));
    x[9] = (double)model->mean[9] + (4.99 * (double)model->sigma[9]);
    PP_CHECK(mlpw_infer(model, x, u, &ops) == MLPW_OK);
}

/* Hai model trùng khi lớp ra trùng (weights.h là static: mỗi tệp dịch có bản riêng, không so con trỏ). */
static bool same_model(const mlpw_model_t *a, const mlpw_model_t *b)
{
    return memcmp(a->w3, b->w3, sizeof(float) * MLPW_OUTPUTS * MLPW_HIDDEN) == 0;
}

/* mlpw_regularisation chọn model có log10 gần nhất. */
static void test_model_selection(void)
{
    pp_calibration_t cal = pp_calibration;
    static const float values[] = {1.0e-4F, 1.0e-3F, 1.0e-2F, 2.0e-4F, 3.0e-3F, 1.0e-6F, 1.0F};
    static const size_t want[] = {0U, 1U, 2U, 0U, 1U, 0U, 2U};
    for (size_t i = 0U; i < (sizeof(values) / sizeof(values[0])); i++) {
        cal.mlpw_regularisation = values[i];
        PP_CHECK(same_model(mlpw_model(&cal), mlpw_models[want[i]]));
    }
    PP_CHECK(same_model(mlpw_model(&pp_calibration), mlpw_models[1]));
    PP_CHECK(!same_model(mlpw_models[0], mlpw_models[1]) && !same_model(mlpw_models[1], mlpw_models[2]));
}

/* Đích luôn nằm trong dải calibration; dải hẹp lại thì đích bị kẹp đúng vào biên. Ngoài miền: đích là mặc định. */
static void test_target_clamped_and_fallback(void)
{
    pp_qp_problem_t pb;
    double t[MLPW_OUTPUTS];
    double d[MLPW_OUTPUTS];
    uint32_t ops = 0U;
    pp_calibration_t cal = pp_calibration;
    for (size_t i = 0U; i < FIX_PROBLEMS; i++) {
        unpack(&fix_problem[i * FIX_PROBLEM_SIZE], &pb);
        PP_CHECK(mlpw_target(&cal, &pb, t, &ops) == MLPW_OK);
        PP_CHECK(ops == MLPW_OPS);
        PP_CHECK((t[0] >= log((double)cal.mlpw_w_dev_min)) && (t[0] <= log((double)cal.mlpw_w_dev_max)));
        PP_CHECK((t[1] >= log((double)cal.mlpw_w_jerk_min)) && (t[1] <= log((double)cal.mlpw_w_jerk_max)));
        PP_CHECK((t[2] >= (double)cal.mlpw_a_comfort_min) && (t[2] <= (double)cal.mlpw_a_comfort_max));
    }
    /* Dải một điểm: đích là đúng điểm đó. */
    cal.mlpw_w_dev_min = 0.2F;
    cal.mlpw_w_dev_max = 0.2F;
    cal.mlpw_a_comfort_min = 1.25F;
    cal.mlpw_a_comfort_max = 1.25F;
    unpack(&fix_problem[0], &pb);
    (void)mlpw_target(&cal, &pb, t, NULL);
    PP_CHECK(t[0] == log(0.2F));
    PP_CHECK(t[2] == 1.25);
    /* Ngoài miền (v rất lớn): đích mặc định, không suy luận. */
    for (size_t k = 0U; k < PP_QP_N; k++) {
        pb.v[k] = 80.0;
    }
    PP_CHECK(mlpw_target(&pp_calibration, &pb, t, &ops) == MLPW_OUT_OF_DOMAIN);
    PP_CHECK(ops == 0U);
    default_u(d);
    PP_CHECK(memcmp(t, d, sizeof(d)) == 0);
}

/* Sau reset: chu kỳ đầu đi từ trọng số mặc định; mỗi chu kỳ đổi tối đa mlpw_rate_log / mlpw_rate_ac; tới đích thì
 * đứng yên; bản calibration ra chỉ khác ba trọng số. */
static void test_rate_limit(void)
{
    const double target[MLPW_OUTPUTS] = {log(0.6), log(0.5), 1.0};
    double d[MLPW_OUTPUTS];
    pp_calibration_t out;
    default_u(d);
    pp_t7_reset(&ws);
    double prev[MLPW_OUTPUTS];
    (void)memcpy(prev, d, sizeof(prev));
    for (size_t c = 0U; c < 100U; c++) {
        mlpw_apply(&ws, &pp_calibration, target, &out);
        for (size_t k = 0U; k < MLPW_OUTPUTS; k++) {
            const double rate = (k < 2U) ? (double)pp_calibration.mlpw_rate_log : (double)pp_calibration.mlpw_rate_ac;
            PP_CHECK(fabs(ws.u[k] - prev[k]) <= (rate * (1.0 + 1e-12)));
            prev[k] = ws.u[k];
        }
        if (c == 0U) {
            PP_CHECK_NEAR(ws.u[0], d[0] + (double)pp_calibration.mlpw_rate_log, 1e-12);
            PP_CHECK_NEAR(ws.u[2], d[2] - (double)pp_calibration.mlpw_rate_ac, 1e-7);
        }
    }
    for (size_t k = 0U; k < MLPW_OUTPUTS; k++) {
        PP_CHECK_NEAR(ws.u[k], target[k], 1e-12);
    }
    PP_CHECK_NEAR(out.qp_w_dev, 0.6, 1e-6);
    PP_CHECK_NEAR(out.qp_w_jerk, 0.5, 1e-6);
    PP_CHECK_NEAR(out.qp_a_comfort, 1.0, 1e-6);
    pp_calibration_t same = out;
    same.qp_w_dev = pp_calibration.qp_w_dev;
    same.qp_w_jerk = pp_calibration.qp_w_jerk;
    same.qp_a_comfort = pp_calibration.qp_a_comfort;
    PP_CHECK(memcmp(&same, &pp_calibration, sizeof(same)) == 0);
    /* Reset: lại bắt đầu từ mặc định. */
    pp_t7_reset(&ws);
    PP_CHECK(!ws.have_u);
    mlpw_apply(&ws, &pp_calibration, d, &out);
    PP_CHECK(memcmp(ws.u, d, sizeof(d)) == 0);
    PP_CHECK(out.qp_w_dev == pp_calibration.qp_w_dev && out.qp_w_jerk == pp_calibration.qp_w_jerk);
}

/* pp_t7_generate trùng từng bit với pp_generate_qp dùng đúng trọng số đã chọn, qua nhiều chu kỳ có warm start;
 * đúng qp_iters vòng. */
static void test_generate_uses_chosen_weights(void)
{
    fixture_t fx;
    pp_trajectory_point_t mine[PP_TRAJECTORY_POINTS];
    pp_trajectory_point_t base[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
    pp_qp_problem_t pb;
    pp_lateral_path_t lateral;
    pp_t7_ws_t shadow;
    pp_calibration_t chosen;
    double t[MLPW_OUTPUTS];
    setup(&fx, 0.3, 0.002, 25.0);
    pp_t7_reset(&ws);
    pp_t7_reset(&shadow);
    pp_qp_reset(&plain);
    for (size_t c = 0U; c < 5U; c++) {
        PP_CHECK(pp_t7_generate(&ws, &pp_calibration, &fx.in, mine, &samples));
        PP_CHECK(ws.fallback == MLPW_OK);
        PP_CHECK(ws.infer_ops == MLPW_OPS);
        PP_CHECK(ws.qp.iterations == (uint32_t)pp_calibration.qp_iters);
        pp_t7_qp_problem(&pp_calibration, &fx.in, &pb);
        PP_CHECK(mlpw_target(&pp_calibration, &pb, t, NULL) == MLPW_OK);
        mlpw_apply(&shadow, &pp_calibration, t, &chosen);
        PP_CHECK(pp_generate_qp(&plain, &chosen, &pb, &lateral));
        PP_CHECK(pp_output_points(fx.in.ref, &lateral, fx.in.speed, (double)VP0.wheelbase, base, &samples));
        PP_CHECK(memcmp(mine, base, sizeof(mine)) == 0);
        PP_CHECK(memcmp(ws.u, shadow.u, sizeof(ws.u)) == 0);
    }
}

/* Ngoài miền từ chu kỳ đầu: trọng số giữ mặc định, path trùng từng bit với qp_jerk_admm (cùng warm start). */
static void test_out_of_domain_matches_qp_jerk_admm(void)
{
    fixture_t fx;
    pp_trajectory_point_t mine[PP_TRAJECTORY_POINTS];
    pp_trajectory_point_t base[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
    pp_qp_problem_t pb;
    pp_lateral_path_t lateral;
    setup(&fx, 0.3, 0.0, 60.0);
    pp_t7_reset(&ws);
    pp_qp_reset(&plain);
    for (size_t c = 0U; c < 3U; c++) {
        PP_CHECK(pp_t7_generate(&ws, &pp_calibration, &fx.in, mine, &samples));
        PP_CHECK(ws.fallback == MLPW_OUT_OF_DOMAIN);
        PP_CHECK(ws.infer_ops == 0U);
        pp_t7_qp_problem(&pp_calibration, &fx.in, &pb);
        PP_CHECK(pp_generate_qp(&plain, &pp_calibration, &pb, &lateral));
        PP_CHECK(pp_output_points(fx.in.ref, &lateral, fx.in.speed, (double)VP0.wheelbase, base, &samples));
        PP_CHECK(memcmp(mine, base, sizeof(mine)) == 0);
    }
}

int main(void)
{
    test_features_match_python();
    test_inference_matches_numpy();
    test_mirror_exact();
    test_out_of_domain_rejected();
    test_model_selection();
    test_target_clamped_and_fallback();
    test_rate_limit();
    test_generate_uses_chosen_weights();
    test_out_of_domain_matches_qp_jerk_admm();
    return PP_TEST_RESULT();
}

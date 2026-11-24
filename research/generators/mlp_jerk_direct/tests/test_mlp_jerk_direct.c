/* L0 riêng của mlp_jerk_direct. Contract chung đã có ở tests/planner/c/test_t7_contract.c. */

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

static const pp_vehicle_config_t VP0 = {2.9F, 1.45F, 1.9F, 15.0F, 0.61F, 6.0F, 0.05F};
static pp_t7_ws_t ws;

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

/* Path là tích phân của jerk MLP đã kẹp, từ trạng thái đầu, qua T11 chung; không có gì khác. */
static void test_path_is_integrated_mlp_jerk(void)
{
    fixture_t fx;
    pp_trajectory_point_t mine[PP_TRAJECTORY_POINTS];
    pp_trajectory_point_t base[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
    pp_qp_problem_t pb;
    pp_lateral_path_t lateral;
    double features[MLP_FEATURES];
    double jerk[PP_QP_N];
    setup(&fx, 0.3, 0.002, 25.0);
    fx.start.d_dot = -0.05;
    pp_t7_reset(&ws);
    PP_CHECK(pp_t7_generate(&ws, &pp_calibration, &fx.in, mine, &samples));
    PP_CHECK(ws.fallback == MLP_OK);
    PP_CHECK(ws.work == 1U);
    PP_CHECK(ws.infer_ops == MLP_OPS);
    pp_t7_qp_problem(&pp_calibration, &fx.in, &pb);
    mlp_features(&pb, features);
    PP_CHECK(mlp_jerk(&MLP_MODEL, features, jerk, NULL) == MLP_OK);
    PP_CHECK(mlp_clamp_jerk(&pb, jerk) == ws.clamped);
    lateral.d[0] = pb.start.d;
    lateral.d_dot[0] = pb.start.d_dot;
    lateral.d_ddot[0] = pb.start.d_ddot;
    const double dt = PP_GRID_STEP_S;
    for (size_t k = 0U; k < PP_QP_N; k++) {
        const double j = jerk[k];
        lateral.d[k + 1U] = lateral.d[k] + (lateral.d_dot[k] * dt) + (0.5 * lateral.d_ddot[k] * dt * dt)
                            + ((j * dt * dt * dt) / 6.0);
        lateral.d_dot[k + 1U] = lateral.d_dot[k] + (lateral.d_ddot[k] * dt) + (0.5 * j * dt * dt);
        lateral.d_ddot[k + 1U] = lateral.d_ddot[k] + (j * dt);
    }
    PP_CHECK(pp_output_points(fx.in.ref, &lateral, fx.in.speed, (double)VP0.wheelbase, base, &samples));
    PP_CHECK(memcmp(mine, base, sizeof(mine)) == 0);
}

/* Kẹp vào trần jerk của bài toán: một chuỗi vượt trần bị đưa về biên, đối xứng hai phía. */
static void test_clamp_to_jerk_rows(void)
{
    pp_qp_problem_t pb;
    double jerk[PP_QP_N];
    (void)memset(&pb, 0, sizeof(pb));
    pb.jerk_limit = 4.5;
    for (size_t k = 0U; k < PP_QP_N; k++) {
        pb.v[k] = 20.0;
        pb.dkappa[k] = 1e-5;  /* v³κ' = 0,08 m/s³. */
        jerk[k] = (k % 2U == 0U) ? 9.0 : -9.0;
    }
    PP_CHECK(mlp_clamp_jerk(&pb, jerk) == PP_QP_N);
    PP_CHECK_NEAR(jerk[0], 4.5 - 0.08, 1e-12);
    PP_CHECK_NEAR(jerk[1], -4.5 - 0.08, 1e-12);
}

/* Ngoài miền: không có path, không suy luận; không có QP hay quintic thay thế. */
static void test_out_of_domain_gives_no_path(void)
{
    fixture_t fx;
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
    setup(&fx, 0.3, 0.0, 60.0);
    pp_t7_reset(&ws);
    PP_CHECK(!pp_t7_generate(&ws, &pp_calibration, &fx.in, pts, &samples));
    PP_CHECK(ws.fallback == MLP_OUT_OF_DOMAIN);
    PP_CHECK(ws.work == 0U);
    PP_CHECK(ws.infer_ops == 0U);
    setup(&fx, 0.3, 0.0, 25.0);
    PP_CHECK(pp_t7_generate(&ws, &pp_calibration, &fx.in, pts, &samples));
}

/* Ở tâm làn trên đường thẳng, bài toán tự đối xứng gương: path nằm đúng trên tâm (không có lệch hệ thống). */
static void test_centred_straight_stays_centred(void)
{
    fixture_t fx;
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
    setup(&fx, 0.0, 0.0, 25.0);
    pp_t7_reset(&ws);
    PP_CHECK(pp_t7_generate(&ws, &pp_calibration, &fx.in, pts, &samples));
    for (size_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        PP_CHECK(pts[k].pose.y == 0.0F);
    }
}

int main(void)
{
    mlp_l0_all();
    test_path_is_integrated_mlp_jerk();
    test_clamp_to_jerk_rows();
    test_out_of_domain_gives_no_path();
    test_centred_straight_stays_centred();
    return PP_TEST_RESULT();
}

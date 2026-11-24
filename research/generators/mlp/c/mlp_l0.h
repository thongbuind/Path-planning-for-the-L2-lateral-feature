/* Ca kiểm L0 dùng chung của các generator MLP: đặc trưng C khớp bản Python, suy luận C khớp numpy, đối xứng
 * gương, bộ kiểm ngoài miền. Chỉ include từ tests/ của generator, sau pp_test.h, weights.h và mlp_fixture.h. */

#ifndef LAB_MLP_L0_H
#define LAB_MLP_L0_H

#include <math.h>
#include <string.h>

#include "mlp_features.h"
#include "mlp_infer.h"

/* Bố cục TR_PROBLEM của teacher: start (d, d', d'', heading), d_target, 7 khối N, ay_limit, jerk_limit. */
static void mlp_l0_unpack(const double *p, pp_qp_problem_t *pb)
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

static void mlp_l0_features_match_python(void)
{
    for (size_t i = 0U; i < FIX_PROBLEMS; i++) {
        pp_qp_problem_t pb;
        double out[MLP_FEATURES];
        mlp_l0_unpack(&fix_problem[i * FIX_PROBLEM_SIZE], &pb);
        mlp_features(&pb, out);
        for (size_t f = 0U; f < MLP_FEATURES; f++) {
            PP_CHECK_NEAR(out[f], fix_features[(i * MLP_FEATURES) + f], 1e-12 * (1.0 + fabs(out[f])));
        }
    }
}

static void mlp_l0_inference_matches_numpy(void)
{
    for (size_t i = 0U; i < FIX_VECTORS; i++) {
        double jerk[MLP_OUTPUTS];
        uint32_t ops = 0U;
        PP_CHECK(mlp_jerk(&MLP_MODEL, &fix_x[i * MLP_FEATURES], jerk, &ops) == MLP_OK);
        PP_CHECK(ops == MLP_OPS);
        for (size_t k = 0U; k < MLP_OUTPUTS; k++) {
            const double want = fix_jerk[(i * MLP_OUTPUTS) + k];
            PP_CHECK_NEAR(jerk[k], want, 1e-4 + (1e-4 * fabs(want)));
        }
    }
}

/* Vector cuối của fix_x là bản soi gương của vector đầu: jerk đổi dấu đúng từng bit. */
static void mlp_l0_mirror_exact(void)
{
    double a[MLP_OUTPUTS];
    double b[MLP_OUTPUTS];
    PP_CHECK(mlp_jerk(&MLP_MODEL, &fix_x[0], a, NULL) == MLP_OK);
    PP_CHECK(mlp_jerk(&MLP_MODEL, &fix_x[(FIX_VECTORS - 1U) * MLP_FEATURES], b, NULL) == MLP_OK);
    for (size_t k = 0U; k < MLP_OUTPUTS; k++) {
        PP_CHECK(a[k] == -b[k]);
    }
}

static void mlp_l0_out_of_domain_rejected(void)
{
    double jerk[MLP_OUTPUTS];
    double x[MLP_FEATURES];
    uint32_t ops = 7U;
    for (size_t k = 0U; k < MLP_OUTPUTS; k++) {
        jerk[k] = 123.0;
    }
    PP_CHECK(mlp_jerk(&MLP_MODEL, fix_ood, jerk, &ops) == MLP_OUT_OF_DOMAIN);
    PP_CHECK(ops == 0U);
    PP_CHECK(jerk[0] == 123.0);
    (void)memcpy(x, &fix_x[0], sizeof(x));
    x[3] = NAN;
    PP_CHECK(mlp_jerk(&MLP_MODEL, x, jerk, &ops) == MLP_NOT_FINITE);
    /* Biên 5 σ: ngay trong biên vẫn dùng được. */
    (void)memcpy(x, &fix_x[0], sizeof(x));
    x[9] = (double)MLP_MODEL.mean[9] + (4.99 * (double)MLP_MODEL.sigma[9]);
    PP_CHECK(mlp_jerk(&MLP_MODEL, x, jerk, &ops) == MLP_OK);
}

static void mlp_l0_all(void)
{
    mlp_l0_features_match_python();
    mlp_l0_inference_matches_numpy();
    mlp_l0_mirror_exact();
    mlp_l0_out_of_domain_rejected();
}

#endif

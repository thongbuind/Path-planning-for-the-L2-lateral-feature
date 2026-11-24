#include <math.h>
#include <stddef.h>

#include "mlp_infer.h"

#define F MLP_FEATURES
#define H MLP_HIDDEN
#define O MLP_OUTPUTS

/* Chỉ số đặc trưng theo nhóm gương (mlp_features.h). */
static const size_t even_idx[MLP_EVEN] = {6U, 9U, 10U, 11U, 12U, 27U};
static const size_t odd_idx[MLP_ODD] = {0U, 1U, 2U, 3U, 7U, 8U, 13U, 14U, 15U, 16U, 17U, 18U, 19U, 20U};
static const size_t pair_idx[MLP_PAIRS][2] = {{4U, 5U}, {21U, 22U}, {23U, 24U}, {25U, 26U}};

static float relu(float v)
{
    return (v > 0.0F) ? v : 0.0F;
}

uint32_t mlp_jerk(const mlp_model_t *model, const double features[MLP_FEATURES], double jerk[MLP_OUTPUTS],
                  uint32_t *ops)
{
    uint32_t code = MLP_OK;
    float xn[F];
    for (size_t i = 0U; (i < F) && (code == MLP_OK); i++) {
        const double dev = features[i] - (double)model->mean[i];
        if (!isfinite(features[i])) {
            code = MLP_NOT_FINITE;
        } else if (fabs(dev) > (MLP_OOD_SIGMA * (double)model->sigma[i])) {
            code = MLP_OUT_OF_DOMAIN;
        } else {
            xn[i] = (float)dev * model->inv_std[i];
        }
    }
    if (ops != NULL) {
        *ops = 0U;
    }
    if (code == MLP_OK) {
        float xe[MLP_EVEN_IN];
        float xo[MLP_ODD_IN];
        for (size_t i = 0U; i < MLP_EVEN; i++) {
            xe[i] = xn[even_idx[i]];
        }
        for (size_t i = 0U; i < MLP_ODD; i++) {
            xo[i] = xn[odd_idx[i]];
        }
        /* Cặp (d_min, d_max): nửa hiệu là phần chẵn, nửa tổng là phần lẻ. */
        for (size_t p = 0U; p < MLP_PAIRS; p++) {
            const float a = xn[pair_idx[p][0]];
            const float b = xn[pair_idx[p][1]];
            xe[MLP_EVEN + p] = 0.5F * (b - a);
            xo[MLP_ODD + p] = 0.5F * (a + b);
        }
        /* Lớp 1 tính một lần: nhánh x dùng chẵn + lẻ, nhánh Mx dùng chẵn − lẻ. */
        float hp[H];
        float hm[H];
        for (size_t h = 0U; h < H; h++) {
            const float *we = &model->w_even[h * MLP_EVEN_IN];
            const float *wo = &model->w_odd[h * MLP_ODD_IN];
            float se = model->b1[h];
            float so = 0.0F;
            for (size_t i = 0U; i < MLP_EVEN_IN; i++) {
                se += we[i] * xe[i];
            }
            for (size_t i = 0U; i < MLP_ODD_IN; i++) {
                so += wo[i] * xo[i];
            }
            hp[h] = relu(se + so);
            hm[h] = relu(se - so);
        }
        float diff[H];
        for (size_t h = 0U; h < H; h++) {
            const float *w = &model->w2[h * H];
            float sp = model->b2[h];
            float sm = model->b2[h];
            for (size_t i = 0U; i < H; i++) {
                sp += w[i] * hp[i];
                sm += w[i] * hm[i];
            }
            diff[h] = 0.5F * (relu(sp) - relu(sm));
        }
        /* Lớp ra trên hiệu hai nhánh: bias và trung bình nhãn triệt tiêu. */
        for (size_t k = 0U; k < O; k++) {
            const float *w = &model->w3[k * H];
            float s = 0.0F;
            for (size_t h = 0U; h < H; h++) {
                s += w[h] * diff[h];
            }
            jerk[k] = (double)(s * model->out_scale[k]);
        }
        if (ops != NULL) {
            *ops = MLP_OPS;
        }
    }
    return code;
}

uint32_t mlp_clamp_jerk(const pp_qp_problem_t *pb, double jerk[MLP_OUTPUTS])
{
    uint32_t clamped = 0U;
    for (size_t k = 0U; k < O; k++) {
        const double jerk_ref = pb->v[k] * pb->v[k] * pb->v[k] * pb->dkappa[k];
        const double lo = -pb->jerk_limit - jerk_ref;
        const double hi = pb->jerk_limit - jerk_ref;
        if (jerk[k] < lo) {
            jerk[k] = lo;
            clamped++;
        } else if (jerk[k] > hi) {
            jerk[k] = hi;
            clamped++;
        } else {
        }
    }
    return clamped;
}

bool mlp_integrate(const pp_qp_problem_t *pb, const double jerk[MLP_OUTPUTS], pp_lateral_path_t *out)
{
    const double dt = PP_GRID_STEP_S;
    bool ok = true;
    out->d[0] = pb->start.d;
    out->d_dot[0] = pb->start.d_dot;
    out->d_ddot[0] = pb->start.d_ddot;
    for (size_t k = 0U; ok && (k < MLP_OUTPUTS); k++) {
        const double j = jerk[k];
        out->d[k + 1U] = out->d[k] + (out->d_dot[k] * dt) + (0.5 * out->d_ddot[k] * dt * dt) + ((j * dt * dt * dt) / 6.0);
        out->d_dot[k + 1U] = out->d_dot[k] + (out->d_ddot[k] * dt) + (0.5 * j * dt * dt);
        out->d_ddot[k + 1U] = out->d_ddot[k] + (j * dt);
        ok = isfinite(out->d[k + 1U]) && isfinite(out->d_dot[k + 1U]) && isfinite(out->d_ddot[k + 1U]);
    }
    return ok;
}

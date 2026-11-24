#include <math.h>
#include <stddef.h>

#include "mlpw_infer.h"

#define F MLP_FEATURES
#define H MLPW_HIDDEN
#define O MLPW_OUTPUTS

/* Chỉ số đặc trưng theo nhóm gương (mlp_features.h), như mlp_infer.c. */
static const size_t even_idx[MLP_EVEN] = {6U, 9U, 10U, 11U, 12U, 27U};
static const size_t odd_idx[MLP_ODD] = {0U, 1U, 2U, 3U, 7U, 8U, 13U, 14U, 15U, 16U, 17U, 18U, 19U, 20U};
static const size_t pair_idx[MLP_PAIRS][2] = {{4U, 5U}, {21U, 22U}, {23U, 24U}, {25U, 26U}};

static float relu(float v)
{
    return (v > 0.0F) ? v : 0.0F;
}

uint32_t mlpw_infer(const mlpw_model_t *model, const double features[MLP_FEATURES], double u[MLPW_OUTPUTS],
                    uint32_t *ops)
{
    uint32_t code = MLPW_OK;
    float xn[F];
    for (size_t i = 0U; (i < F) && (code == MLPW_OK); i++) {
        const double dev = features[i] - (double)model->mean[i];
        if (!isfinite(features[i])) {
            code = MLPW_NOT_FINITE;
        } else if (fabs(dev) > (MLPW_OOD_SIGMA * (double)model->sigma[i])) {
            code = MLPW_OUT_OF_DOMAIN;
        } else {
            xn[i] = (float)dev * model->inv_std[i];
        }
    }
    if (ops != NULL) {
        *ops = 0U;
    }
    if (code == MLPW_OK) {
        float xe[MLPW_EVEN_IN];
        float xo[MLPW_ODD_IN];
        for (size_t i = 0U; i < MLP_EVEN; i++) {
            xe[i] = xn[even_idx[i]];
        }
        for (size_t i = 0U; i < MLP_ODD; i++) {
            xo[i] = xn[odd_idx[i]];
        }
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
            const float *we = &model->w_even[h * MLPW_EVEN_IN];
            const float *wo = &model->w_odd[h * MLPW_ODD_IN];
            float se = model->b1[h];
            float so = 0.0F;
            for (size_t i = 0U; i < MLPW_EVEN_IN; i++) {
                se += we[i] * xe[i];
            }
            for (size_t i = 0U; i < MLPW_ODD_IN; i++) {
                so += wo[i] * xo[i];
            }
            hp[h] = relu(se + so);
            hm[h] = relu(se - so);
        }
        /* Trung bình hai nhánh: cộng là phép giao hoán nên kết quả của x và Mx trùng từng bit. */
        float mean[H];
        for (size_t h = 0U; h < H; h++) {
            const float *w = &model->w2[h * H];
            float sp = model->b2[h];
            float sm = model->b2[h];
            for (size_t i = 0U; i < H; i++) {
                sp += w[i] * hp[i];
                sm += w[i] * hm[i];
            }
            mean[h] = 0.5F * (relu(sp) + relu(sm));
        }
        for (size_t k = 0U; k < O; k++) {
            const float *w = &model->w3[k * H];
            float s = model->b3[k];
            for (size_t h = 0U; h < H; h++) {
                s += w[h] * mean[h];
            }
            u[k] = (double)(model->centre[k] + (model->half[k] * s));
        }
        if (ops != NULL) {
            *ops = MLPW_OPS;
        }
    }
    return code;
}

/* Suy luận MLP 2 lớp ẩn × 32 (ReLU) chọn trọng số QP, bất biến theo gương: u(x) = c + h ⊙ (b3 + W3 (g(x) + g(Mx)) / 2),
 * nên u(Mx) = u(x) đúng từng bit. Đầu ra u = (ln qp_w_dev, ln qp_w_jerk, qp_a_comfort), chưa kẹp. Đặc trưng và bộ kiểm
 * ngoài miền như luồng C (mlp_features.h, mlp_infer.h). Không heap, không biến toàn cục ngoài weights const. Bản numpy
 * tham chiếu: ../tools/wmodel.py. */

#ifndef LAB_MLPW_INFER_H
#define LAB_MLPW_INFER_H

#include <stdint.h>

#include "mlp_features.h"

#define MLPW_HIDDEN (32U)
#define MLPW_OUTPUTS (3U)  /* 0 ln qp_w_dev, 1 ln qp_w_jerk, 2 qp_a_comfort [m/s²]. */
#define MLPW_EVEN_IN (MLP_EVEN + MLP_PAIRS)
#define MLPW_ODD_IN (MLP_ODD + MLP_PAIRS)
#define MLPW_OOD_SIGMA (5.0)  /* Như MLP_OOD_SIGMA của luồng C. */

/* Phép nhân cộng mỗi lần suy luận: chuẩn hóa, lớp 1 (một lần cho hai nhánh), lớp 2 (hai nhánh), lớp ra, thang ra. */
#define MLPW_OPS (MLP_FEATURES + (MLP_FEATURES * MLPW_HIDDEN) + (2U * MLPW_HIDDEN * MLPW_HIDDEN) \
                  + (MLPW_HIDDEN * MLPW_OUTPUTS) + MLPW_OUTPUTS)

/* Mã kết quả, trùng mã của mlp_jerk (generator.yaml). */
#define MLPW_OK (0U)
#define MLPW_NOT_FINITE (1U)
#define MLPW_OUT_OF_DOMAIN (2U)

typedef struct {
    const float *mean;  /* [MLP_FEATURES] */
    const float *sigma;  /* [MLP_FEATURES] dùng cho kiểm ngoài miền */
    const float *inv_std;  /* [MLP_FEATURES] */
    const float *w_even;  /* [MLPW_HIDDEN][MLPW_EVEN_IN] */
    const float *w_odd;  /* [MLPW_HIDDEN][MLPW_ODD_IN] */
    const float *b1;  /* [MLPW_HIDDEN] */
    const float *w2;  /* [MLPW_HIDDEN][MLPW_HIDDEN] */
    const float *b2;  /* [MLPW_HIDDEN] */
    const float *w3;  /* [MLPW_OUTPUTS][MLPW_HIDDEN] */
    const float *b3;  /* [MLPW_OUTPUTS] */
    const float *centre;  /* [MLPW_OUTPUTS] tâm của u */
    const float *half;  /* [MLPW_OUTPUTS] nửa dải của u */
} mlpw_model_t;

/* Kiểm ngoài miền rồi suy luận u. Trả MLPW_OK hoặc mã lý do; khi không OK, u không được ghi. ops (có thể NULL) nhận
 * số phép nhân cộng đã làm (0 nếu dừng ở bước kiểm). */
uint32_t mlpw_infer(const mlpw_model_t *model, const double features[MLP_FEATURES], double u[MLPW_OUTPUTS],
                    uint32_t *ops);

#endif

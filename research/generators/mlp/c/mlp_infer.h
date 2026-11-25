/* Suy luận MLP 2 lớp ẩn × 32 (ReLU) của luồng C, đối xứng gương: j(x) = (g(x) − g(Mx)) / 2, nên
 * j(Mx) = −j(x) đúng từng bit (bài toán QP đối xứng khi soi gương, mlp_features.h). Không dùng heap,
 * không có biến toàn cục ngoài weights const của generator, cùng input cho cùng output. Bản numpy tham
 * chiếu: research/generators/mlp/model.py (forward). */

#ifndef LAB_MLP_INFER_H
#define LAB_MLP_INFER_H

#include <stdbool.h>
#include <stdint.h>

#include "mlp_features.h"

#define MLP_HIDDEN (32U)
#define MLP_EVEN_IN (MLP_EVEN + MLP_PAIRS)  /* Đầu vào chẵn của lớp 1: 6 đặc trưng chẵn, 4 nửa hiệu của cặp. */
#define MLP_ODD_IN (MLP_ODD + MLP_PAIRS)  /* Đầu vào lẻ: 14 đặc trưng lẻ, 4 nửa tổng của cặp. */

/* Số phép nhân cộng mỗi lần suy luận: chuẩn hóa, lớp 1 (một lần cho cả hai nhánh), lớp 2 (hai nhánh),
 * lớp ra (một lần trên hiệu hai nhánh), nhân thang ra. */
#define MLP_OPS (MLP_FEATURES + (MLP_FEATURES * MLP_HIDDEN) + (2U * MLP_HIDDEN * MLP_HIDDEN) \
                 + (MLP_HIDDEN * MLP_OUTPUTS) + MLP_OUTPUTS)

/* Ngưỡng ngoài miền: |x − mean| > 5 σ của train ở bất kỳ đặc trưng nào. */
#define MLP_OOD_SIGMA (5.0)

typedef struct {
    const float *mean;  /* [MLP_FEATURES] trung bình của train (đối xứng gương). */
    const float *sigma;  /* [MLP_FEATURES] độ lệch chuẩn dùng cho kiểm ngoài miền (đã có sàn). */
    const float *inv_std;  /* [MLP_FEATURES] 1/σ khi chuẩn hóa; 0 với đặc trưng hằng trên train. */
    const float *w_even;  /* [MLP_HIDDEN][MLP_EVEN_IN] lớp 1, phần chẵn. */
    const float *w_odd;  /* [MLP_HIDDEN][MLP_ODD_IN] lớp 1, phần lẻ. */
    const float *b1;  /* [MLP_HIDDEN] */
    const float *w2;  /* [MLP_HIDDEN][MLP_HIDDEN] */
    const float *b2;  /* [MLP_HIDDEN] */
    const float *w3;  /* [MLP_OUTPUTS][MLP_HIDDEN]; bias lớp ra triệt tiêu trong phép đối xứng. */
    const float *out_scale;  /* [MLP_OUTPUTS] σ của nhãn jerk [m/s³]. */
} mlp_model_t;

/* Mã kết quả của mlp_jerk. */
#define MLP_OK (0U)
#define MLP_NOT_FINITE (1U)  /* Đặc trưng không hữu hạn. */
#define MLP_OUT_OF_DOMAIN (2U)  /* Đặc trưng lệch quá MLP_OOD_SIGMA so với train. */

/* Kiểm ngoài miền rồi suy luận chuỗi jerk [m/s³] trên t_0 tới t_29. Trả MLP_OK hoặc mã lý do; khi không
 * OK, jerk không được ghi. ops (có thể NULL) nhận số phép nhân cộng đã làm (0 nếu dừng ở bước kiểm). */
uint32_t mlp_jerk(const mlp_model_t *model, const double features[MLP_FEATURES], double jerk[MLP_OUTPUTS],
                  uint32_t *ops);

/* Kẹp jerk vào hàng jerk cứng của bài toán QP: |j + v³κ'| ≤ jerk_limit (như bounds() của qp.c). Nhãn luôn
 * nằm trong hộp này, nên phép kẹp từng phần tử không làm sai số lớn hơn. Trả số phần tử bị kẹp. */
uint32_t mlp_clamp_jerk(const pp_qp_problem_t *pb, double jerk[MLP_OUTPUTS]);

/* Tích phân chính xác jerk hằng từng đoạn từ trạng thái đầu của bài toán, như cuối pp_generate_qp_seeded.
 * Trả false khi một giá trị không hữu hạn (khi đó out chỉ ghi dở). */
bool mlp_integrate(const pp_qp_problem_t *pb, const double jerk[MLP_OUTPUTS], pp_lateral_path_t *out);

#endif

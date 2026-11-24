/* T7 qp_jerk_admm_mlp_weights: như qp_jerk_admm (cùng bài toán, warm start, đúng qp_iters vòng), nhưng qp_w_dev,
 * qp_w_jerk, qp_a_comfort do MLP chọn theo tình huống từ input của planner, kẹp vào dải calibration và giới hạn tốc độ
 * đổi mỗi chu kỳ (PP-TS-025 V3). Sau reset hoặc khi ngoài miền, đích là trọng số mặc định của qp_jerk_admm. Generator
 * lab của PP-TS-031. Telemetry: work là số vòng ADMM; fallback là lý do không dùng MLP; infer_ops là phép nhân cộng. */

#ifndef LAB_QP_JERK_ADMM_MLP_WEIGHTS_H
#define LAB_QP_JERK_ADMM_MLP_WEIGHTS_H

#include <stdbool.h>
#include <stdint.h>

#include "generators/qp.h"

#define PP_T7_SUPPORT_FLOOR (0)  /* Giống qp_jerk_admm. */

#define MLPW_WEIGHTS (3U)

typedef struct {
    pp_qp_ws_t qp;
    double u[MLPW_WEIGHTS];  /* Trọng số đang dùng: ln qp_w_dev, ln qp_w_jerk, qp_a_comfort [m/s²]. */
    bool have_u;  /* false sau reset: chu kỳ tới bắt đầu từ trọng số mặc định. */
    uint32_t fallback;  /* Lý do không dùng MLP ở chu kỳ gần nhất; 0 nếu đã dùng. */
    uint32_t infer_ops;  /* Phép nhân cộng của MLP ở chu kỳ gần nhất. */
} pp_t7_ws_t;

#endif

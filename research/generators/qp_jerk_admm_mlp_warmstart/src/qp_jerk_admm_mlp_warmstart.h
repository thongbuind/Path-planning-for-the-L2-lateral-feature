/* T7 qp_jerk_admm_mlp_warmstart: như qp_jerk_admm (cùng bài toán, trọng số, đúng qp_iters vòng), nhưng jerk xuất
 * phát của ADMM là chuỗi jerk MLP dự đoán từ input của planner (PP-TS-025 V2). Ngoài miền thì dùng warm start
 * dịch thời gian của luồng A, hoặc warm start của qp_jerk_admm khi không dịch được. Generator lab của PP-TS-031.
 * Telemetry: work là số vòng ADMM; fallback là lý do không dùng MLP (generator.yaml); infer_ops là số phép nhân
 * cộng của MLP. */

#ifndef LAB_QP_JERK_ADMM_MLP_WARMSTART_H
#define LAB_QP_JERK_ADMM_MLP_WARMSTART_H

#include <stdbool.h>
#include <stdint.h>

#include "generators/qp.h"

#define PP_T7_SUPPORT_FLOOR (0)  /* Giống qp_jerk_admm. */

/* Mã fallback thêm vào mã của mlp_infer.h: qmw_seed_mode = 1 và nghiệm trước dịch được, nên không suy luận. */
#define QMW_SHIFT_PREFERRED (3U)

typedef struct {
    pp_qp_ws_t qp;
    bool follow_last;  /* follow của lần giải gần nhất (điều kiện dịch, như luồng A). */
    uint32_t fallback;  /* Lý do không dùng MLP ở chu kỳ gần nhất; 0 nếu đã dùng. */
    uint32_t infer_ops;  /* Phép nhân cộng của MLP ở chu kỳ gần nhất. */
    bool shifted;  /* Chu kỳ gần nhất có dịch thời gian phần warm start cũ. */
} pp_t7_ws_t;

#endif

/* T7 qp_jerk_admm_shift_warmstart: như qp_jerk_admm (cùng bài toán, trọng số, số vòng), nhưng warm start
 * ADMM là nghiệm chu kỳ trước dịch theo thời gian đã trôi (old->shift_s). Generator lab của PP-TS-031.
 * Telemetry: work là số vòng ADMM; fallback là lý do không dịch (generator.yaml). */

#ifndef LAB_QP_JERK_ADMM_SHIFT_WARMSTART_H
#define LAB_QP_JERK_ADMM_SHIFT_WARMSTART_H

#include <stdbool.h>
#include <stdint.h>

#include "generators/qp.h"

#define PP_T7_SUPPORT_FLOOR (0)  /* Giống qp_jerk_admm. */

/* Mã lý do không dịch warm start (generator.yaml). */
#define SWS_SHIFTED (0U)
#define SWS_NO_WARM (1U)  /* Chu kỳ đầu sau reset hoặc lần giải trước thất bại: khởi động lạnh. */
#define SWS_FROM_CAR (2U)  /* start_from_car: điểm đầu là trạng thái đo. */
#define SWS_NOT_FROM_OLD (3U)  /* Điểm đầu không nối với path cũ (không có path cũ hoặc stitch reset). */
#define SWS_FOLLOW_CHANGED (4U)  /* follow khác lần giải trước: đổi đường tham chiếu, hoặc lần gọi thứ hai trong chu kỳ. */
#define SWS_BAD_SHIFT (5U)  /* shift_s không hữu hạn hoặc không dương. */

typedef struct {
    pp_qp_ws_t qp;
    bool follow_last;  /* follow của lần giải gần nhất. */
    uint32_t fallback;  /* Lý do không dịch của chu kỳ gần nhất; SWS_SHIFTED nếu đã dịch. */
} pp_t7_ws_t;

#endif

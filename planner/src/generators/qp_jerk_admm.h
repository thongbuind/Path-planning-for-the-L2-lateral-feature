/* T7 qp_jerk_admm: QP với biến là jerk ngang trên 30 bước, mô hình thay đổi theo thời gian, ràng buộc
 * mềm, giải bằng ADMM có warm start (PP-TS-003, Software Detailed Design mục 10). Telemetry: work là số
 * vòng ADMM. */

#ifndef PP_T7_QP_JERK_ADMM_H
#define PP_T7_QP_JERK_ADMM_H

#include "generators/qp.h"

#define PP_T7_QP_JERK_ADMM (1)
#define PP_T7_SUPPORT_FLOOR (0)

typedef struct {
    pp_qp_ws_t qp;
} pp_t7_ws_t;

#endif

/* Phần chọn trọng số của qp_jerk_admm_mlp_weights, tách ra để unit test gọi trực tiếp. */

#ifndef LAB_MLPW_STEP_H
#define LAB_MLPW_STEP_H

#include <stdint.h>

#include "generators/pp_t7.h"
#include "generators/qp.h"
#include "mlpw_infer.h"

/* Model ứng với mlpw_regularisation: mức có log10 gần nhất trong weights.h. */
const mlpw_model_t *mlpw_model(const pp_calibration_t *cal);

/* Đích của chu kỳ: u của MLP kẹp vào dải calibration; ngoài miền hoặc không hữu hạn thì u mặc định (qp_w_dev,
 * qp_w_jerk, qp_a_comfort của calibration chung, cũng kẹp). Trả mã fallback; ops như mlpw_infer. */
uint32_t mlpw_target(const pp_calibration_t *cal, const pp_qp_problem_t *pb, double target[MLPW_OUTPUTS],
                     uint32_t *ops);

/* Đưa ws->u về phía đích, mỗi thành phần đổi tối đa mlpw_rate_log (hai trọng số, theo ln) hoặc mlpw_rate_ac
 * (qp_a_comfort). Sau reset, ws->u bắt đầu từ u mặc định. Ghi trọng số vào bản calibration out (chép từ cal). */
void mlpw_apply(pp_t7_ws_t *ws, const pp_calibration_t *cal, const double target[MLPW_OUTPUTS],
                pp_calibration_t *out);

#endif

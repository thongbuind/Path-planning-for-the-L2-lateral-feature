/* Phần dùng chung giữa các generator T7 của LCC: luôn được biên dịch, để generator lab gọi lại. */

#ifndef PP_T7_COMMON_H
#define PP_T7_COMMON_H

#include <stdbool.h>
#include <stdint.h>

#include "generators/pp_t7_input.h"
#include "generators/qp.h"
#include "pp_calibration.h"
#include "pp_path.h"

/* Quintic theo thời lượng: bắt đầu từ T_hwa (T_recenter khi đưa về giữa), tăng 0,25 s tới khi path đạt
 * ay_add_max_hwa và jerk_target_hwa hoặc tới T_max. lateral nhận path Frenet của lần thử cuối; tries
 * (có thể NULL) nhận số lần thử. */
bool pp_t7_quintic_search(const pp_calibration_t *cal, const pp_t7_input_t *in, pp_lateral_path_t *lateral,
                          pp_trajectory_point_t points[PP_TRAJECTORY_POINTS], pp_ref_samples_t *samples,
                          uint32_t *tries);

/* Dựng bài toán QP jerk từ input: hành lang, độ cong, tốc độ trên t_1 tới t_30 và path cũ chiếu lên ref. */
void pp_t7_qp_problem(const pp_calibration_t *cal, const pp_t7_input_t *in, pp_qp_problem_t *pb);

#endif

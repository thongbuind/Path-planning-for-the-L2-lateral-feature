/* Contract chung của T7 cho LCC planner (PP-TS-031). Mỗi bản build có đúng một generator, chọn lúc
 * build qua PP_T7. LKA và ELK không dùng contract này. */

#ifndef PP_T7_H
#define PP_T7_H

#include <stdbool.h>

#include "lateral_state.h"
#include "pp_calibration.h"
#include "pp_path.h"
#include "pp_types.h"
#include "reference_line.h"
#include "stitching.h"

typedef struct {
    const pp_reference_line_t *ref;
    const pp_lateral_state_t *start;  /* Trạng thái tại điểm 0, đã nối với path cũ khi from_old. */
    const pp_speed_profile_t *speed;
    const pp_old_path_t *old;  /* Path chu kỳ trước, đã dời về t0. */
    bool from_old;
    bool recentering;
    double d_target;  /* [m] Offset mục tiêu so với đường tham chiếu, dương về trái. */
    const pp_vehicle_config_t *vehicle;
} pp_t7_input_t;

/* Header của generator được chọn (sinh lúc configure) định nghĩa:
 * - pp_t7_ws_t: trạng thái giữ giữa các chu kỳ, kích thước cố định, nằm trong state của planner;
 * - PP_T7_SUPPORT_FLOOR: 1 nếu LCC đặt sàn trợ giúp PP-SWR-006 cho path của generator, 0 nếu không. */
#include "pp_t7_selected.h"

#ifndef PP_T7_SUPPORT_FLOOR
#error "the selected T7 generator must define PP_T7_SUPPORT_FLOOR"
#elif (PP_T7_SUPPORT_FLOOR != 0) && (PP_T7_SUPPORT_FLOOR != 1)
#error "PP_T7_SUPPORT_FLOOR must be 0 or 1"
#endif

/* Đưa ws về trạng thái của chu kỳ đầu. LCC gọi lúc khởi tạo và khi không có hướng đi tới. */
void pp_t7_reset(pp_t7_ws_t *ws);

/* Sinh path tại lưới thời gian của Trajectory, gồm cả T11 (đổi sang base_link, lấy mẫu đường tham
 * chiếu). Trả false nếu không có path hợp lệ; khi đó ws phải ở trạng thái dùng tiếp được. */
bool pp_t7_generate(pp_t7_ws_t *ws, const pp_calibration_t *cal, const pp_t7_input_t *in,
                    pp_trajectory_point_t points[PP_TRAJECTORY_POINTS], pp_ref_samples_t *samples);

#endif

/* Contract chung của T7 cho LCC planner (PP-TS-031). Mỗi bản build có đúng một generator, chọn lúc
 * build qua PP_T7. LKA và ELK không dùng contract này. */

#ifndef PP_T7_H
#define PP_T7_H

#include <stdbool.h>
#include <stddef.h>

#include "generators/pp_t7_input.h"
#include "pp_calibration.h"

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

#ifdef PP_T7_TELEMETRY
/* Generator điền telemetry của lần pp_t7_generate gần nhất, kể cả khi trả false; LCC điền t10_change_m. */
void pp_t7_report(const pp_t7_ws_t *ws, pp_t7_telemetry_t *out);

/* Đọc telemetry của chu kỳ LCC gần nhất từ state. Trả false nếu state không hợp lệ. Chỉ để nghiên cứu. */
bool pp_lcc_t7_telemetry(const void *state, pp_t7_telemetry_t *out);

/* Con trỏ tới ws của generator trong state, *size = sizeof(pp_t7_ws_t); NULL nếu state không hợp lệ.
 * Chỉ để nghiên cứu: generator lab (teacher của MLP) đặt dữ liệu cần ghi trong ws theo bố cục nó khai báo. */
const void *pp_lcc_t7_workspace(const void *state, size_t *size);
#endif

#endif

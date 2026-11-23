/* Input và telemetry của contract T7 (generators/pp_t7.h). Tách riêng để hàm dùng chung và header của
 * generator dùng được mà không cần biết generator nào được chọn. */

#ifndef PP_T7_INPUT_H
#define PP_T7_INPUT_H

#include <stdbool.h>
#include <stdint.h>

#include "lateral_state.h"
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
    bool follow;  /* ref là đường ảo bám xe trước (T12). */
    bool start_from_car;  /* Tài xế override, LKA/ELK đang REQUEST hoặc chu kỳ đầu sau đó. */
    double d_target;  /* [m] Offset mục tiêu so với đường tham chiếu, dương về trái. */
    const pp_object_list_t *objects;  /* ObjectList dùng được của chu kỳ, theo stamp của nó; NULL nếu không có. */
    const pp_vehicle_config_t *vehicle;
} pp_t7_input_t;

/* Telemetry nghiên cứu, chỉ có khi build với PP_T7_TELEMETRY. Mỗi trường là của chu kỳ vừa chạy. */
typedef struct {
    uint32_t work;  /* Khối lượng việc, đơn vị do generator khai báo: số lần thử, số vòng lặp... */
    uint32_t fallback;  /* 0: không dùng quintic_duration thay thế; khác 0: mã lý do do generator khai báo. */
    uint32_t infer_ops;  /* Số phép nhân cộng của mô hình học; 0 nếu không có. */
    double residual;  /* Residual tương đối của bộ giải lặp; NAN nếu không có. */
    double slack;  /* Tổng trị tuyệt đối biến nới mềm; NAN nếu không có. */
    double t10_change_m;  /* Do LCC điền: lệch ngang lớn nhất T10 gây ra trên path của generator. */
} pp_t7_telemetry_t;

#endif

/* T7 quintic_tangent_point: path quintic_duration cộng hiệu chỉnh ngang smoothstep bậc 7 về phía trong
 * cua, đỉnh đặt tại thời điểm tới tiếp điểm của tia nhìn với vạch trong (Land và Lee 1994; PP-TS-024 V1).
 * Generator lab của PP-TS-031. Telemetry: work là số path đã dựng; fallback theo generator.yaml. */

#ifndef LAB_QUINTIC_TANGENT_POINT_H
#define LAB_QUINTIC_TANGENT_POINT_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "pp_path.h"
#include "pp_types.h"

#define PP_T7_SUPPORT_FLOOR (1)  /* Giữ sàn PP-SWR-006: hiệu chỉnh không chạy ở cua sát aysmax. */

typedef struct {
    uint32_t work;  /* Telemetry: số path đã dựng ở chu kỳ gần nhất. */
    uint32_t fallback;  /* Telemetry: mã lý do dùng quintic_duration; 0 nếu đã cộng hiệu chỉnh. */
    double amp;  /* [m] Biên độ hiện tại, dương về trái; 0 khi không hiệu chỉnh. Giữ giữa các chu kỳ. */
} pp_t7_ws_t;

/* Thời điểm [s] tới tiếp điểm gần nhất trên vạch phía side (+1 trái, −1 phải), cách tâm half_width,
 * tìm trong [lo, hi] trên các điểm 0..last của path. Điểm tâm làn suy từ pose của path và lệch d.
 * Trả 0 nếu không có. Dùng chung với unit test. */
double lab_qtp_tangent_time(const pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],
                            const pp_lateral_path_t *lateral, const pp_ref_samples_t *samples,
                            double side, double half_width, double lo, double hi, size_t last);

#endif

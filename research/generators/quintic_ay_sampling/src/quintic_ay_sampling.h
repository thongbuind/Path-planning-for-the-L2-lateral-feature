/* T7 quintic_ay_sampling: path quintic_duration cộng một hiệu chỉnh ngang smoothstep bậc 7, chọn trong
 * tập ứng viên (hai vị trí đỉnh × hai dấu × thang biên độ) theo đỉnh a_y và jerk dự báo (PP-TS-024 V2).
 * Generator lab của PP-TS-031. Không áp dụng được thì giữ path quintic_duration. */

#ifndef LAB_QUINTIC_AY_SAMPLING_H
#define LAB_QUINTIC_AY_SAMPLING_H

#include <stdbool.h>
#include <stdint.h>

#include "generators/pp_t7_input.h"
#include "pp_calibration.h"
#include "pp_path.h"

#define PP_T7_SUPPORT_FLOOR (1)  /* Giữ sàn PP-SWR-006 như quintic_duration. */

/* Mã lý do giữ path quintic_duration (telemetry fallback, khai báo ở generator.yaml). */
#define LAB_QAS_APPLIED (0U)
#define LAB_QAS_FOLLOW (1U)
#define LAB_QAS_START_FROM_CAR (2U)
#define LAB_QAS_RECENTERING (3U)
#define LAB_QAS_OFFSET (4U)
#define LAB_QAS_LANE (5U)
#define LAB_QAS_OBJECTS (6U)
#define LAB_QAS_SHORT_VIEW (7U)
#define LAB_QAS_CORRIDOR (8U)
#define LAB_QAS_NO_CURVE (9U)
#define LAB_QAS_SHARP_CURVE (10U)
#define LAB_QAS_NO_GAIN (11U)
#define LAB_QAS_CHECK (12U)
#define LAB_QAS_BASE_FAILED (13U)

#define LAB_QAS_STEPS_MAX (16U)  /* Trần số mức biên độ mỗi hướng, để vòng lặp có cỡ cố định. */

typedef struct {
    uint32_t work;  /* Telemetry: số lần thử thời lượng + số ứng viên đã chấm. */
    uint32_t fallback;  /* Telemetry: mã LAB_QAS_*; 0 nếu đã áp dụng hiệu chỉnh. */
} pp_t7_ws_t;

/* Phần chung của mọi ứng viên trong một chu kỳ: lấy mẫu đường tham chiếu một lần theo speed->s. */
typedef struct {
    double v2[PP_TRAJECTORY_POINTS];  /* v² theo float như Trajectory, để a_y khớp pp_feasibility_check. */
    double s_dot[PP_TRAJECTORY_POINTS];
    double a[PP_TRAJECTORY_POINTS];
    double kappa[PP_TRAJECTORY_POINTS];
    double dkappa[PP_TRAJECTORY_POINTS];
} lab_qas_frame_t;

/* Kết quả chấm của chu kỳ (cho L0 và telemetry). Giá trị a_y, jerk là dự báo trước T10. */
typedef struct {
    uint32_t reason;  /* LAB_QAS_* */
    uint32_t evaluated;  /* Số ứng viên đã chấm. */
    double end_s;  /* Thời lượng dùng được trong tầm nhìn. */
    double peak_s;  /* Đỉnh của ứng viên được chọn; 0 nếu không có. */
    double offset_m;  /* Biên độ có dấu của ứng viên được chọn; 0 nếu không có. */
    double ay_base;
    double jerk_base;
    double ay_best;
    double jerk_best;
} lab_qas_choice_t;

void lab_qas_frame(const pp_t7_input_t *in, lab_qas_frame_t *frame);

/* Đỉnh |a_y| và jerk trung bình 0,5 s lớn nhất của path base + offset × shape, theo công thức T11. */
void lab_qas_predict(const lab_qas_frame_t *frame, const pp_lateral_path_t *base, const pp_lateral_path_t *shape,
                     double offset, double *ay_max, double *jerk_max);

/* Chấm tập ứng viên quanh path quintic (base, points, samples là kết quả của pp_t7_quintic_search) và
 * thay points bằng ứng viên được chọn. Trả mã lý do; points giữ nguyên khi mã khác LAB_QAS_APPLIED. */
uint32_t lab_qas_correct(const pp_calibration_t *cal, const pp_t7_input_t *in, const pp_lateral_path_t *base,
                         pp_trajectory_point_t points[PP_TRAJECTORY_POINTS], const pp_ref_samples_t *samples,
                         lab_qas_choice_t *choice);

#endif

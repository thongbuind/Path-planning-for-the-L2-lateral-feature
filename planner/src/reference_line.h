#ifndef PP_REFERENCE_LINE_H
#define PP_REFERENCE_LINE_H

#include <stdbool.h>
#include <stdint.h>

#include "latency.h"
#include "pp_calibration.h"
#include "pp_math.h"

#define PP_LANE_WIDTH_MIN_M (2.5)
#define PP_LANE_WIDTH_MAX_M (5.5)

typedef struct {
    bool valid;
    pp_cubic_t poly;
    double variance[PP_CUBIC_TERMS];
    double view_start;
    double view_end;
    double age_s;
} pp_line_track_t;

/* Jump mở candidate. accepted chỉ đổi khi candidate ổn định đủ T_confirm; previous giúp quay lại
 * vị trí trước. */
typedef struct {
    pp_line_track_t accepted;
    pp_line_track_t candidate;
    pp_line_track_t previous;
    double absent_s;
} pp_boundary_memory_t;

#define PP_OUTER_BOUNDARIES (PP_BOUNDARIES - 2U)

typedef struct {
    pp_boundary_memory_t track;
    bool offset_valid;
    double offset;
    double offset_variance;
} pp_outer_boundary_memory_t;

typedef struct {
    bool width_valid;
    double width;
    pp_boundary_memory_t line[2];
    pp_outer_boundary_memory_t outer[PP_OUTER_BOUNDARIES];
    bool ref_valid;
    bool ref_inferred;  /* COAST giữ nguồn và điều kiện hợp lệ của tâm làn cuối. */
    pp_cubic_t ref_centre;
    double ref_width;
    double ref_view_start;
    double ref_view_end;
    double coast_s;
} pp_reference_memory_t;

/* Node origin ở chân đường vuông góc từ base_link, ứng với s = 0. */
#define PP_REF_STEP_M (2.0)
#define PP_REF_BACK_M (80.0)
#define PP_REF_NODES (120U)

typedef struct {
    uint32_t n;
    uint32_t origin;
    double s[PP_REF_NODES];
    double x[PP_REF_NODES];
    double y[PP_REF_NODES];
    double theta[PP_REF_NODES];
    double kappa[PP_REF_NODES];
    double dkappa[PP_REF_NODES];
} pp_ref_nodes_t;

typedef struct {
    bool valid;
    /* centre là hình học khi sampled=false; khi sampled=true chỉ là nguồn sinh node. Đọc bằng
     * pp_ref_walk_* hoặc pp_ref_project. */
    pp_cubic_t centre;
    bool sampled;
    pp_ref_nodes_t nodes;
    double width;
    double view_start;
    double view_end;
    bool inferred;
    bool lane_too_narrow;
    bool coasting;
    bool line_rejected[2];
    double var_c2;
    double var_c3;
} pp_reference_line_t;

void pp_reference_memory_reset(pp_reference_memory_t *mem);

/* cycle_motion là ego-motion từ chu kỳ trước. NULL làm mất bộ nhớ biên cần được dịch. */
void pp_reference_line_update(pp_reference_memory_t *mem, pp_lane_at_t0_t *lane,
                              const pp_motion_t *cycle_motion, const pp_calibration_t *cal,
                              double vehicle_width, double dt, pp_reference_line_t *out);

/* Sinh node từ centre và phạm vi quan sát. Khi centre đổi, cần sinh lại để node khớp cubic. */
void pp_ref_sample_cubic(pp_reference_line_t *ref);

typedef struct {
    double x;
    double y;
    double theta;
    double kappa;
    double dkappa;
} pp_ref_point_t;

/* s = 0 tại hình chiếu gốc base_link. Sau tầm nhìn, nối cung theo hướng và độ cong cuối. */
typedef struct {
    const pp_reference_line_t *ref;
    double s;
    double x;
    double x_end;
    bool on_arc;
    pp_ref_point_t arc_start;
    double s_arc_start;
} pp_ref_walker_t;

void pp_ref_walk_begin(pp_ref_walker_t *walker, const pp_reference_line_t *ref,
                       pp_ref_point_t *start);
/* Walker giữ trạng thái theo s, nên các lần gọi phải đi theo thứ tự s không giảm. */
void pp_ref_walk_to(pp_ref_walker_t *walker, double s, pp_ref_point_t *point);

/* Chiếu điểm base_link và trả lệch ngang d, dương về trái. Bản sampled chiếu lên cung nối sau node
 * cuối. */
void pp_ref_project(const pp_reference_line_t *ref, double px, double py,
                    pp_ref_point_t *foot, double *d);

#endif

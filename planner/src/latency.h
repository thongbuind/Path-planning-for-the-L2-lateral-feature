#ifndef PP_LATENCY_H
#define PP_LATENCY_H

#include <stdbool.h>

#include "pp_math.h"
#include "pp_types.h"

/* Thứ tự phần tử là L2, L1, R1, R2, mép trái, mép phải (ICD 5.1). */
#define PP_LINE_L2 (0U)
#define PP_LINE_L1 (1U)
#define PP_LINE_R1 (2U)
#define PP_LINE_R2 (3U)
#define PP_EDGE_LEFT (PP_LANE_LINES)
#define PP_EDGE_RIGHT (PP_LANE_LINES + 1U)
#define PP_BOUNDARIES (PP_LANE_LINES + PP_ROAD_EDGES)

/* Chuyển động từ lúc chụp tới t0, biểu diễn trong base_link lúc chụp (ICD 5.5). */
typedef struct {
    double dx;
    double dy;
    double dyaw;
} pp_motion_t;

typedef struct {
    bool present;
    pp_cubic_t poly;
    double variance[PP_CUBIC_TERMS];
    double view_start;
    double view_end;
    double confidence;
    pp_line_status_t status;
} pp_boundary_t;

typedef struct {
    pp_boundary_t boundary[PP_BOUNDARIES];
    double lane_width;
    pp_side_t lane_change;
} pp_lane_at_t0_t;

/* Đổi mẫu biên sang base_link tại t0 bằng p_new = R(-dyaw)(p_old - d), rồi fit lại cubic. */
void pp_latency_compensate(const pp_lane_model_t *lane, const pp_motion_t *motion,
                           pp_lane_at_t0_t *out);

/* Trả false khi không fit được cubic, kể cả khi phạm vi ngắn hơn 3 m. T2 dùng chung phép đổi này
 * cho bộ nhớ biên. */
bool pp_cubic_move(const pp_cubic_t *in, double x_start, double x_end, const pp_motion_t *motion,
                   pp_cubic_t *out, double *new_start, double *new_end);

void pp_lane_empty(pp_lane_at_t0_t *out);

#endif

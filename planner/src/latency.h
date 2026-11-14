/* T1 Latency compensation (Software Detailed Design section 4, steps 2 to 4; PP-ADR-002). */

#ifndef PP_LATENCY_H
#define PP_LATENCY_H

#include <stdbool.h>

#include "pp_math.h"
#include "pp_types.h"

/* Index of each boundary: lines[4] = L2, L1, R1, R2 (ICD 5.1), then road_edges[2]. */
#define PP_LINE_L2 (0U)
#define PP_LINE_L1 (1U)
#define PP_LINE_R1 (2U)
#define PP_LINE_R2 (3U)
#define PP_EDGE_LEFT (PP_LANE_LINES)
#define PP_EDGE_RIGHT (PP_LANE_LINES + 1U)
#define PP_BOUNDARIES (PP_LANE_LINES + PP_ROAD_EDGES)

/* Motion of base_link from capture time to t0, expressed in base_link at capture (ICD 5.5). */
typedef struct {
    double dx;
    double dy;
    double dyaw;
} pp_motion_t;

/* One lane line or road edge, moved to base_link at t0. */
typedef struct {
    bool present;                 /* Not LOST and the refit succeeded */
    pp_cubic_t poly;              /* y(x) in base_link at t0 */
    double variance[PP_CUBIC_TERMS];
    double view_start;            /* [m] observed range, in base_link at t0 */
    double view_end;
    double confidence;
    pp_line_status_t status;
} pp_boundary_t;

typedef struct {
    pp_boundary_t boundary[PP_BOUNDARIES];
    double lane_width;            /* As reported by the lane model */
    pp_side_t lane_change;
} pp_lane_at_t0_t;

/*
 * Moves every boundary of the lane model from capture time to t0: samples y(x) every
 * 1 m within the view range, transforms the samples with p_new = R(-dyaw)(p_old - d)
 * and refits a cubic by least squares (Software Detailed Design 4, step 3).
 */
void pp_latency_compensate(const pp_lane_model_t *lane, const pp_motion_t *motion,
                           pp_lane_at_t0_t *out);

/* One cubic observed on [x_start, x_end] moved by `motion` the same way; false when the
 * refit fails (range under 3 m). Also used by T2 to move its boundary memory. */
bool pp_cubic_move(const pp_cubic_t *in, double x_start, double x_end, const pp_motion_t *motion,
                   pp_cubic_t *out, double *new_start, double *new_end);

/* No boundary present, for a cycle without a usable lane model. */
void pp_lane_empty(pp_lane_at_t0_t *out);

#endif /* PP_LATENCY_H */

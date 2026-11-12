/*
 * T2 Reference line (Software Detailed Design section 5) and arc-length access to it.
 *
 * Implemented: trusted-boundary check of Software Requirements Specification 4; the
 * frame-to-frame consistency check of L1 and R1 against their memory moved by
 * ego-motion (k_jump), with a change accepted once the new position has been stable for
 * T_confirm and a quick return to the old position after a change; steps 2, 3,
 * 6; step 5 as coasting on the last reference line moved by ego-motion for up to
 * T_coast. Not yet: the slow checks (parallel, width), step 4 (centre inferred from
 * adjacent lines and road edges), the lane change, narrowing and widening rules.
 */

#ifndef PP_REFERENCE_LINE_H
#define PP_REFERENCE_LINE_H

#include <stdbool.h>

#include "latency.h"
#include "pp_calibration.h"
#include "pp_math.h"

/* Lane widths accepted into the width memory (PP-ASM-015, mentor). */
#define PP_LANE_WIDTH_MIN_M (2.5)
#define PP_LANE_WIDTH_MAX_M (5.5)

/* One remembered position of a line, base_link at the last cycle. */
typedef struct {
    bool valid;
    pp_cubic_t poly;
    double var_c0;                /* [m^2] */
    double view_start;
    double view_end;
    double age_s;                 /* [s] candidate: stable for this long; previous: kept for this long */
} pp_line_track_t;

/*
 * Memory of one ego-lane line for the consistency check (Software Detailed Design 5).
 * `accepted` is the position in use. A jump starts a `candidate`; it is taken as a real
 * change once the new position has stayed consistent with itself for T_confirm (R1).
 * After a change the old position stays as `previous` for T_confirm; a frame back at it
 * is taken at once (R2).
 */
typedef struct {
    pp_line_track_t accepted;
    pp_line_track_t candidate;
    pp_line_track_t previous;
    double absent_s;              /* [s] not trusted by SRS 4 for this long */
} pp_boundary_memory_t;

/* Kept across cycles. */
typedef struct {
    bool width_valid;
    double width;                 /* w_mem [m] */
    pp_boundary_memory_t line[2]; /* L1, R1 */
    bool ref_valid;               /* Last reference line, for coasting (step 5) */
    pp_cubic_t ref_centre;
    double ref_width;
    double ref_view_start;
    double ref_view_end;
    double coast_s;               /* [s] coasting for this long */
} pp_reference_memory_t;

typedef struct {
    bool valid;
    pp_cubic_t centre;            /* Lane centre y(x), base_link at t0 */
    double width;                 /* [m] lane width used this cycle */
    double view_start;            /* [m] x range where the centre is observed */
    double view_end;
    bool inferred;                /* Centre only from adjacent lines or edges (PP-SWR-047) */
    bool lane_too_narrow;         /* PP-SWR-063 */
    bool coasting;                /* Step 5: last reference line moved by ego-motion */
    bool line_rejected[2];        /* L1, R1 failed the consistency check this cycle */
    double var_c2;                /* Variance of the centre's c2, c3 (for T5) */
    double var_c3;
} pp_reference_line_t;

void pp_reference_memory_reset(pp_reference_memory_t *mem);

/*
 * dt: time since the previous cycle [s]. cycle_motion: ego-motion since the previous
 * cycle, NULL when not known (the memory is then dropped). vehicle_width from
 * VehicleConfig.
 */
void pp_reference_line_update(pp_reference_memory_t *mem, const pp_lane_at_t0_t *lane,
                              const pp_motion_t *cycle_motion, const pp_calibration_t *cal,
                              double vehicle_width, double dt, pp_reference_line_t *out);

/* Point of the reference line at an arc length. */
typedef struct {
    double x;
    double y;
    double theta;                 /* Tangent heading [rad] */
    double kappa;                 /* [1/m] */
    double dkappa;                /* d kappa / ds [1/m^2] */
} pp_ref_point_t;

/*
 * Walks along the reference line by arc length. s = 0 is the foot of the
 * perpendicular from the base_link origin. Beyond the observed range the line
 * continues as a circular arc with the curvature and heading at the range end.
 */
typedef struct {
    const pp_reference_line_t *ref;
    double s;                     /* Arc length reached */
    double x;                     /* x on the cubic at s */
    double x_end;                 /* End of the observed cubic */
    bool on_arc;
    pp_ref_point_t arc_start;
    double s_arc_start;
} pp_ref_walker_t;

void pp_ref_walk_begin(pp_ref_walker_t *walker, const pp_reference_line_t *ref,
                       pp_ref_point_t *start);
/* Calls must not decrease s. */
void pp_ref_walk_to(pp_ref_walker_t *walker, double s, pp_ref_point_t *point);

/*
 * Foot of the perpendicular from a point near the car (px, py in base_link) on the
 * observed cubic, and the signed lateral offset d of the point (left positive).
 */
void pp_ref_project(const pp_reference_line_t *ref, double px, double py,
                    pp_ref_point_t *foot, double *d);

#endif /* PP_REFERENCE_LINE_H */

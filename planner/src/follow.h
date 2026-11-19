/*
 * T12 Bám xe trước (Software Detailed Design 5.1; PP-SWR-170 to 177), LCC planner only.
 *
 * When both lines of the ego lane are lost, no other boundary is trusted, and the vehicle
 * ahead is the ACC target, the path follows the trail of the lead vehicle's centre instead
 * of the last lane centre moved by ego-motion. Entry V1 to V6 and keep M1 to M6 are the
 * conditions of the mentor (Software Requirements Specification 8.13).
 */

#ifndef PP_FOLLOW_H
#define PP_FOLLOW_H

#include <stdbool.h>
#include <stdint.h>

#include "latency.h"
#include "pp_calibration.h"
#include "pp_math.h"
#include "pp_types.h"
#include "reference_line.h"

#define PP_FOLLOW_TRAIL_MAX (256U)          /* Upper bound of trail_n */

/* Numbers of the mentor (Software Requirements Specification 8.13). */
#define PP_FOLLOW_GAP_MIN_M (2.0)           /* V2 */
#define PP_FOLLOW_GAP_MAX_M (50.0)
#define PP_FOLLOW_PATH_DEV_M (0.8)          /* M1 */
#define PP_FOLLOW_SPEED_MAX_MPS (60.0 / 3.6) /* M3, 60 km/h */
#define PP_FOLLOW_WHEEL_ANGLE_MAX_RAD (0.3490658503988659) /* M4, 20 deg */
#define PP_FOLLOW_DISTANCE_MAX_M (30.0)     /* M5 */
#define PP_FOLLOW_TRAIL_COVER_M (50.0)      /* trail_n * trail_spacing must reach this */
#define PP_FOLLOW_VN_ALPHA (0.25)           /* Per new LeadTarget frame */
#define PP_FOLLOW_V3_POINTS (7U)            /* Latest trail points averaged with the lead for V3 */

typedef struct {
    /* Trail of the lead centre, oldest first, base_link at the last cycle (step 1). */
    uint32_t trail_id;
    uint32_t n;
    uint64_t last_stamp_us;
    bool has_stamp;
    double x[PP_FOLLOW_TRAIL_MAX];
    double y[PP_FOLLOW_TRAIL_MAX];
    double vn_filt;                 /* Low-pass of the lead's speed across the original lane centre (V4) */
    uint32_t vn_count;
    /* Original lane centre, last time the lane lines were trusted (step 2). */
    bool origin_valid;
    pp_cubic_t origin;
    double origin_start;
    double origin_end;
    double origin_width;
    /* Mode. */
    bool active;
    uint32_t id;                    /* Lead vehicle at entry (M6) */
    double distance_m;              /* Driven since entry (M5) */
} pp_follow_state_t;

void pp_follow_reset(pp_follow_state_t *st);

typedef struct {
    uint64_t t0_us;
    bool lane_trusted;                      /* T2 line of this cycle is from the ego lane lines */
    const pp_reference_line_t *lane_ref;    /* T2 line of this cycle (used when lane_trusted) */
    bool moved;
    pp_motion_t since_last;                 /* Ego-motion since the previous cycle */
    double ds;                              /* [m] driven this cycle */
    double v;
    double v_y;
    const pp_lead_target_t *lead;           /* Usable LeadTarget, else NULL */
    bool lead_moved;
    pp_motion_t lead_motion;                /* From the lead stamp to t0 */
    const pp_longitudinal_plan_t *plan;     /* Usable LongitudinalPlan, else NULL */
    const pp_steering_signals_t *steering;
} pp_follow_input_t;

/* Steps 1, 2: every cycle, also while the lane lines are there. */
void pp_follow_observe(pp_follow_state_t *st, const pp_follow_input_t *in,
                       const pp_calibration_t *cal);

/*
 * Steps 3, 4: when entry (or keep, while active) conditions hold except M1 (which needs the
 * path), fills the virtual reference line and returns true.
 */
bool pp_follow_candidate(const pp_follow_state_t *st, const pp_follow_input_t *in,
                         const pp_calibration_t *cal, const pp_vehicle_config_t *vehicle,
                         pp_reference_line_t *ref);

/* M1: the path stays within the limit of the original lane centre over its 3 s. */
bool pp_follow_path_within(const pp_follow_state_t *st, const pp_trajectory_point_t *points,
                           const pp_calibration_t *cal, const pp_vehicle_config_t *vehicle);

/* Mode changed by the cycle: entered, kept or left; M5 distance integrated. */
void pp_follow_commit(pp_follow_state_t *st, bool active, const pp_lead_target_t *lead, double ds);

#endif /* PP_FOLLOW_H */

#ifndef PP_FOLLOW_H
#define PP_FOLLOW_H

#include <stdbool.h>
#include <stdint.h>

#include "latency.h"
#include "pp_calibration.h"
#include "pp_math.h"
#include "pp_types.h"
#include "reference_line.h"

#define PP_FOLLOW_TRAIL_MAX (256U)

#define PP_FOLLOW_GAP_MIN_M (2.0)
#define PP_FOLLOW_GAP_MAX_M (50.0)
#define PP_FOLLOW_PATH_DEV_M (0.8)
#define PP_FOLLOW_SPEED_MAX_MPS (60.0 / 3.6)
#define PP_FOLLOW_WHEEL_ANGLE_MAX_RAD (0.3490658503988659)
#define PP_FOLLOW_DISTANCE_MAX_M (30.0)
#define PP_FOLLOW_TRAIL_COVER_M (50.0)
#define PP_FOLLOW_VN_ALPHA (0.25)
#define PP_FOLLOW_V3_POINTS (7U)

typedef struct {
    /* Trail từ cũ tới mới, trong base_link của chu kỳ trước. */
    uint32_t trail_id;
    uint32_t n;
    uint64_t last_stamp_us;
    bool has_stamp;
    double x[PP_FOLLOW_TRAIL_MAX];
    double y[PP_FOLLOW_TRAIL_MAX];
    double vn_filt;
    uint32_t vn_count;
    /* Tâm làn gốc lưu từ lần cuối vạch ego đủ tin. */
    bool origin_valid;
    pp_cubic_t origin;
    double origin_start;
    double origin_end;
    double origin_width;
    bool active;
    uint32_t id;
    double distance_m;
} pp_follow_state_t;

void pp_follow_reset(pp_follow_state_t *st);

typedef struct {
    uint64_t t0_us;
    bool lane_trusted;
    const pp_reference_line_t *lane_ref;
    bool moved;
    pp_motion_t since_last;
    double ds;
    double v;
    double v_y;
    const pp_lead_target_t *lead;
    bool lead_moved;
    pp_motion_t lead_motion;  /* Ego-motion từ stamp của lead tới t0. */
    const pp_longitudinal_plan_t *plan;
    const pp_steering_signals_t *steering;
} pp_follow_input_t;

void pp_follow_observe(pp_follow_state_t *st, const pp_follow_input_t *in,
                       const pp_calibration_t *cal);

/* Dựng đường tham chiếu ảo khi đủ điều kiện FOLLOW, trừ M1 vì M1 cần path đã sinh. */
bool pp_follow_candidate(const pp_follow_state_t *st, const pp_follow_input_t *in,
                         const pp_calibration_t *cal, const pp_vehicle_config_t *vehicle,
                         pp_reference_line_t *ref);

bool pp_follow_path_within(const pp_follow_state_t *st, const pp_trajectory_point_t *points,
                           const pp_calibration_t *cal, const pp_vehicle_config_t *vehicle);

void pp_follow_commit(pp_follow_state_t *st, bool active, const pp_lead_target_t *lead, double ds);

#endif

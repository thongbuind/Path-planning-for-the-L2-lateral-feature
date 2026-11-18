/* Unit tests of T12 Bám xe trước (follow.c): entry V1 to V6, keep M1 to M6 (PP-SWR-170 to 177). */

#include <math.h>
#include <string.h>

#include "follow.h"
#include "pp_calibration.h"
#include "pp_test.h"

static const pp_vehicle_config_t VP0 = {2.9F, 1.45F, 1.9F, 15.0F, 0.61F, 6.0F, 0.05F};

typedef struct {
    pp_follow_state_t st;
    pp_lead_target_t lead;
    pp_longitudinal_plan_t plan;
    pp_steering_signals_t steering;
    pp_reference_line_t lane;
    double v;
    uint64_t t_us;
} rig_t;

/* Straight lane, car at the centre, a car 25 m ahead at the same speed, 0.2 m to the left. */
static void rig_init(rig_t *r)
{
    (void)memset(r, 0, sizeof(*r));
    pp_follow_reset(&r->st);
    r->lead.header.valid = true;
    r->lead.id = 7U;
    r->lead.classification = PP_LEAD_CLASS_CAR;
    r->lead.x = 25.0F;
    r->lead.y = 0.2F;
    r->lead.gap = 20.0F;
    r->lead.existence_probability = 0.95F;
    r->plan.target_id = 7U;
    r->lane.valid = true;
    r->lane.width = 3.5;
    r->lane.view_end = 80.0;
    r->v = 12.0;
}

/* One cycle of 25 ms; the car drives 0.3 m, the lead keeps its place in front of it. */
static pp_follow_input_t cycle(rig_t *r, bool lane_trusted)
{
    r->t_us += 25000U;
    r->lead.header.stamp_us = r->t_us;
    const pp_follow_input_t in = {
        .t0_us = r->t_us, .lane_trusted = lane_trusted, .lane_ref = &r->lane, .moved = true,
        .since_last = {0.3, 0.0, 0.0}, .ds = 0.3, .v = r->v, .v_y = 0.0, .lead = &r->lead,
        .lead_moved = true, .lead_motion = {0.0, 0.0, 0.0}, .plan = &r->plan, .steering = &r->steering,
    };
    return in;
}

/* Lane trusted for a few cycles, then lost; the trail fills while the lines are still there. */
static pp_follow_input_t run(rig_t *r, unsigned trusted, unsigned lost)
{
    pp_follow_input_t in = cycle(r, true);
    for (unsigned k = 0U; k < trusted + lost; k++) {
        in = cycle(r, k < trusted);
        pp_follow_observe(&r->st, &in, &pp_calibration);
    }
    return in;
}

static bool candidate(rig_t *r, const pp_follow_input_t *in, pp_reference_line_t *ref)
{
    return pp_follow_candidate(&r->st, in, &pp_calibration, &VP0, ref);
}

static void test_all_conditions_met_follows_the_lead(void)
{
    rig_t r;
    rig_init(&r);
    const pp_follow_input_t in = run(&r, 5U, 40U);
    pp_reference_line_t ref;
    PP_CHECK(candidate(&r, &in, &ref));
    PP_CHECK(ref.valid && !ref.inferred && !ref.coasting);
    PP_CHECK_NEAR(ref.view_end, 25.0, 1e-9);                  /* observed_horizon_s: to the lead */
    PP_CHECK_NEAR(pp_cubic_value(&ref.centre, 25.0), 0.2, 0.05);
    PP_CHECK_NEAR(pp_cubic_value(&ref.centre, 0.0), 0.0, 0.1);
}

static void test_each_entry_condition_blocks(void)
{
    pp_reference_line_t ref;
    rig_t r;
    rig_init(&r);
    pp_follow_input_t in = run(&r, 5U, 40U);
    PP_CHECK(candidate(&r, &in, &ref));

    r.lead.classification = PP_LEAD_CLASS_MOTORCYCLE;  PP_CHECK(!candidate(&r, &in, &ref));   /* V1 */
    r.lead.classification = PP_LEAD_CLASS_TRUCK;       PP_CHECK(candidate(&r, &in, &ref));
    r.lead.gap = 1.9F;                                  PP_CHECK(!candidate(&r, &in, &ref));   /* V2 */
    r.lead.gap = 50.1F;                                 PP_CHECK(!candidate(&r, &in, &ref));
    r.lead.gap = 50.0F;                                 PP_CHECK(candidate(&r, &in, &ref));
    r.lead.y = 1.5F;                                    PP_CHECK(!candidate(&r, &in, &ref));   /* V3 */
    r.lead.y = 0.2F;
    r.lead.vy_rel = 0.7F;                               /* V4 is on a low-pass: a few frames of it */
    for (unsigned k = 0U; k < 12U; k++) {
        in = cycle(&r, false);
        pp_follow_observe(&r.st, &in, &pp_calibration);
    }
    PP_CHECK(!candidate(&r, &in, &ref));                                                  /* V4 */
    r.lead.vy_rel = 0.0F;
    for (unsigned k = 0U; k < 30U; k++) {
        in = cycle(&r, false);
        pp_follow_observe(&r.st, &in, &pp_calibration);
    }
    r.plan.target_id = 8U;                              PP_CHECK(!candidate(&r, &in, &ref));   /* V5 */
    r.plan.target_id = 7U;                              PP_CHECK(candidate(&r, &in, &ref));
    r.lead.existence_probability = 0.2F;                PP_CHECK(!candidate(&r, &in, &ref));   /* PP-SWR-176 */
    r.lead.existence_probability = 0.95F;
    r.lead.x = NAN;                                     PP_CHECK(!candidate(&r, &in, &ref));
    r.lead.x = 25.0F;
    in.lead = NULL;                                     PP_CHECK(!candidate(&r, &in, &ref));
    in.lead = &r.lead;
    in.plan = NULL;                                     PP_CHECK(!candidate(&r, &in, &ref));
    in.plan = &r.plan;
    in.v = 60.0 / 3.6;                                  PP_CHECK(!candidate(&r, &in, &ref));   /* M3 */
    in.v = 12.0;
    r.steering.steering_wheel_angle_rad = 0.35F;        PP_CHECK(!candidate(&r, &in, &ref));   /* M4, 20 deg */
    r.steering.steering_wheel_angle_rad = -0.30F;       PP_CHECK(candidate(&r, &in, &ref));
}

static void test_no_follow_without_original_centre_or_trail(void)
{
    pp_reference_line_t ref;
    rig_t r;
    rig_init(&r);
    pp_follow_input_t in = run(&r, 0U, 40U);         /* the lines were never seen */
    PP_CHECK(!candidate(&r, &in, &ref));
    rig_init(&r);
    in = run(&r, 5U, 1U);                             /* trail too short */
    PP_CHECK(!candidate(&r, &in, &ref));
}

static void test_keep_conditions_while_following(void)
{
    pp_reference_line_t ref;
    rig_t r;
    rig_init(&r);
    pp_follow_input_t in = run(&r, 5U, 40U);
    PP_CHECK(candidate(&r, &in, &ref));
    pp_follow_commit(&r.st, true, &r.lead, 0.0);
    /* V2 to V5 are entry conditions only: a gap outside 2 to 50 m does not end it by itself. */
    r.lead.gap = 60.0F;
    in = cycle(&r, false);
    pp_follow_observe(&r.st, &in, &pp_calibration);
    PP_CHECK(candidate(&r, &in, &ref));
    r.plan.target_id = 8U;
    PP_CHECK(candidate(&r, &in, &ref));
    r.plan.target_id = 7U;
    r.lead.gap = 20.0F;
    r.lead.id = 9U;                                                    /* M6: another vehicle */
    PP_CHECK(!candidate(&r, &in, &ref));
    r.lead.id = 7U;
    for (unsigned k = 0U; k < 101U; k++) {                             /* M5: 30 m driven */
        pp_follow_commit(&r.st, true, &r.lead, 0.3);
    }
    PP_CHECK(r.st.distance_m > PP_FOLLOW_DISTANCE_MAX_M);
    PP_CHECK(!candidate(&r, &in, &ref));
    pp_follow_commit(&r.st, false, &r.lead, 0.3);
    PP_CHECK_NEAR(r.st.distance_m, 0.0, 1e-12);
}

static void test_trail_survives_bad_frames_and_follows_the_acc_target(void)
{
    pp_reference_line_t ref;
    rig_t r;
    rig_init(&r);
    pp_follow_input_t in = run(&r, 5U, 40U);
    const uint32_t kept = r.st.n;
    PP_CHECK(kept > 4U);
    r.lead.header.valid = false;                      /* PP-SWR-176: no following on a lost frame */
    in.lead = NULL;
    pp_follow_observe(&r.st, &in, &pp_calibration);
    PP_CHECK(r.st.n == kept);                         /* ... but the trail is still that vehicle's */
    PP_CHECK(!candidate(&r, &in, &ref));
    r.lead.header.valid = true;
    in.lead = &r.lead;
    r.lead.id = 9U;                                   /* One frame names another vehicle */
    r.lead.header.stamp_us += 50000U;
    pp_follow_observe(&r.st, &in, &pp_calibration);
    PP_CHECK(r.st.n == kept);
    r.plan.target_id = 9U;                            /* The ACC target really changed */
    r.lead.header.stamp_us += 50000U;
    pp_follow_observe(&r.st, &in, &pp_calibration);
    PP_CHECK(r.st.n <= 1U);
}

static void test_path_within_the_limit_of_the_original_centre(void)
{
    rig_t r;
    rig_init(&r);
    (void)run(&r, 5U, 1U);
    pp_trajectory_point_t points[PP_TRAJECTORY_POINTS];
    (void)memset(points, 0, sizeof(points));
    for (unsigned k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        points[k].pose.x = (float)(k * 2U);
        points[k].pose.y = 0.3F;
    }
    /* limit = min(0.8, (3.5 - 1.9) / 2 - dlc_offset_min) = 0.5 m for this lane. */
    PP_CHECK(pp_follow_path_within(&r.st, points, &pp_calibration, &VP0));
    points[20].pose.y = 0.6F;
    PP_CHECK(!pp_follow_path_within(&r.st, points, &pp_calibration, &VP0));          /* M1 */
}

int main(void)
{
    test_all_conditions_met_follows_the_lead();
    test_each_entry_condition_blocks();
    test_no_follow_without_original_centre_or_trail();
    test_keep_conditions_while_following();
    test_trail_survives_bad_frames_and_follows_the_acc_target();
    test_path_within_the_limit_of_the_original_centre();
    return PP_TEST_RESULT();
}

/* T7 intervention geometry, quintic time origin and end condition. */

#include "intervention.h"
#include "output.h"
#include "pp_calibration.h"
#include "pp_test.h"

static const pp_vehicle_config_t VP0 = {2.9F, 1.45F, 1.9F, 15.0F, 0.61F, 6.0F, 0.05F};

static pp_boundary_t boundary(double y)
{
    const pp_boundary_t b = {
        .present = true, .poly = {{y, 0.0, 0.0, 0.0}},
        .view_start = 0.0, .view_end = 80.0, .confidence = 1.0,
        .status = PP_LINE_STATUS_MEASURED,
    };
    return b;
}

static void test_measured_edge_needs_association_with_ego_lane(void)
{
    pp_lane_at_t0_t lane;
    pp_lane_empty(&lane);
    pp_edge_memory_t mem = {0};
    const pp_reference_line_t camera = {0};
    const pp_motion_t motion = {0};
    pp_reference_line_t edges[PP_ROAD_EDGES];
    lane.boundary[PP_EDGE_RIGHT] = boundary(-5.25);
    pp_road_edge_references(&mem, &lane, &camera, &motion, &VP0, &pp_calibration, edges);
    PP_CHECK(!edges[1].valid);   /* F21(c) */
    lane.boundary[PP_EDGE_RIGHT] = boundary(-1.75);
    lane.boundary[PP_LINE_L1] = boundary(1.75);
    pp_road_edge_references(&mem, &lane, &camera, &motion, &VP0, &pp_calibration, edges);
    PP_CHECK(edges[1].valid);
    PP_CHECK_NEAR(edges[1].width, 3.5, 1.0e-6);
    PP_CHECK_NEAR(edges[1].centre.c[0], 0.0, 1.0e-6);
    lane.boundary[PP_LINE_L1].present = false;
    pp_road_edge_references(&mem, &lane, &camera, &motion, &VP0, &pp_calibration, edges);
    PP_CHECK(edges[1].valid);    /* width remembered, edge still measured */
    lane.boundary[PP_EDGE_RIGHT].confidence = (double)pp_calibration.conf_edge - 0.01;
    pp_road_edge_references(&mem, &lane, &camera, &motion, &VP0, &pp_calibration, edges);
    PP_CHECK(!edges[1].valid);
}

static void test_profile_advances_from_original_start_time(void)
{
    const pp_reference_line_t ref = {.valid = true, .width = 3.5, .view_end = 100.0};
    const pp_lateral_state_t start = {.d = 0.65, .d_dot = 0.2};
    const pp_function_limits_t limits = {PP_AY_MAX_LKA, PP_JERK_MAX_LKA, PP_AY_ADD_MAX_LKA};
    const pp_intervention_request_t request = {.received_us = 1000000U, .side = PP_SIDE_LEFT};
    pp_speed_profile_t speed;
    pp_speed_profile(NULL, request.received_us, 20.0, &speed);
    pp_intervention_path_t path;
    pp_intervention_begin(&path, &request, 0.75, request.received_us, &ref, &start, &speed,
                          &limits, &VP0, &pp_calibration, false);
    pp_lateral_path_t lateral;
    pp_intervention_sample(&path, request.received_us, &lateral);
    PP_CHECK_NEAR(lateral.d[0], start.d, 1.0e-8);
    PP_CHECK_NEAR(lateral.d_dot[0], start.d_dot, 1.0e-8);
    const double d_at_one_second = lateral.d[10];
    pp_intervention_sample(&path, request.received_us + 1000000U, &lateral);
    PP_CHECK_NEAR(lateral.d[0], d_at_one_second, 1.0e-8);
    pp_intervention_sample(&path, request.received_us + 10000000U, &lateral);  /* after the quintic */
    PP_CHECK_NEAR(lateral.d[0], 0.0, 1.0e-6);     /* The target is the lane centre (PP-SWR-084) */
    PP_CHECK_NEAR(lateral.d_dot[0], 0.0, 1.0e-8);
}

/* PP-PR-041: the chosen candidate passes T10 step 2 uncut, so it ends parallel to the lane. */
static void test_chosen_candidate_is_not_cut_by_t10(void)
{
    const pp_reference_line_t ref = {.valid = true, .width = 3.85, .view_end = 100.0};
    const pp_function_limits_t limits = {PP_AY_MAX_ELK, PP_JERK_MAX_ELK, PP_AY_ADD_MAX_ELK};
    const pp_intervention_request_t request = {.received_us = 1000000U, .side = PP_SIDE_LEFT};
    const double v_lat[] = {0.2, 0.4, 0.6};
    for (uint32_t i = 0U; i < (sizeof(v_lat) / sizeof(v_lat[0])); i++) {
        const pp_lateral_state_t start = {.d = 0.69, .d_dot = v_lat[i]};
        pp_speed_profile_t speed;
        pp_speed_profile(NULL, request.received_us, 20.0, &speed);
        pp_intervention_path_t path;
        pp_intervention_begin(&path, &request, 0.5, request.received_us, &ref, &start, &speed,
                              &limits, &VP0, &pp_calibration, true);
        pp_lateral_path_t lateral;
        pp_trajectory_point_t points[PP_TRAJECTORY_POINTS];
        pp_ref_samples_t samples;
        pp_intervention_sample(&path, request.received_us, &lateral);
        PP_CHECK(pp_output_points(&ref, &lateral, &speed, VP0.wheelbase, points, &samples));
        PP_CHECK(!pp_feasibility_limit(points, &samples, &limits, &VP0));
    }
}

static void test_aligns_vehicle_state_with_completion_tick(void)
{
    pp_lateral_velocity_history_t history = {0};
    pp_vehicle_state_estimate_t state = {0};
    state.header.stamp_us = 100000U;
    state.lateral_velocity = 0.1F;
    PP_CHECK_NEAR(pp_intervention_vy_at_t0(&history, &state, 105000U), 0.1, 1e-7);
    state.header.stamp_us += 20000U;
    state.lateral_velocity = 0.13F;
    PP_CHECK_NEAR(pp_intervention_vy_at_t0(&history, &state, 125000U), 0.1375, 1e-7);
    PP_CHECK_NEAR(pp_intervention_vy_at_t0(&history, &state, 130000U), 0.145, 1e-7);
    (void)pp_intervention_vy_at_t0(&history, NULL, 140000U);
    state.header.stamp_us += 20000U;
    PP_CHECK_NEAR(pp_intervention_vy_at_t0(&history, &state, 145000U), 0.13, 1e-7);
}


/* PP-SWR-032, 090, PP-ASM-028: DLC >= 0 both sides, |d| <= d_end, |v_lat| <= v_lat_end, heading, a_y add. */
static void test_end_condition_needs_the_car_near_the_centre(void)
{
    pp_reference_line_t ref = {.valid = true, .width = 3.5, .view_end = 100.0};
    pp_old_path_t old = {.valid = true};
    pp_lateral_state_t ego = {0};
    for (uint32_t i = 0U; i < PP_TRAJECTORY_POINTS; i++) {
        old.x[i] = 0.0;
        old.v[i] = 20.0;
    }
    pp_ref_sample_cubic(&ref);
    PP_CHECK(pp_intervention_settled(&ref, &ego, &old, 20.0, 0.0, 0.0, &VP0, &pp_calibration));
    ego.d = (double)pp_calibration.d_end + 0.02;           /* DLC is fine, but not near the centre */
    PP_CHECK(!pp_intervention_settled(&ref, &ego, &old, 20.0, 0.0, 0.0, &VP0, &pp_calibration));
    ego.d = (double)pp_calibration.d_end - 0.02;
    PP_CHECK(pp_intervention_settled(&ref, &ego, &old, 20.0, 0.0, 0.0, &VP0, &pp_calibration));
    PP_CHECK(!pp_intervention_settled(&ref, &ego, &old, 20.0, (double)pp_calibration.v_lat_end + 0.02,
                                      0.0, &VP0, &pp_calibration));
    ego.heading = (double)pp_calibration.heading_end * 2.0;
    PP_CHECK(!pp_intervention_settled(&ref, &ego, &old, 20.0, 0.0, 0.0, &VP0, &pp_calibration));
}

static pp_reference_line_t lane_of(double centre_y, double width)
{
    pp_reference_line_t ref = {.valid = true, .width = width, .view_start = 0.0, .view_end = 80.0};
    ref.centre.c[0] = centre_y;
    return ref;
}

/* PP-SWR-093, 094, PP-ADR-019: a hazard-side edge that jumps away waits T_confirm and then
 * slides at ref_rate; one that stays nearer the car for corridor_toward is followed quickly. */
static void test_corridor_holds_a_jump_away_and_takes_one_toward_the_car(void)
{
    const double dt = 0.025;
    pp_corridor_t c;
    pp_corridor_reset(&c);
    const pp_motion_t still = {0.0, 0.0, 0.0};
    pp_reference_line_t live = lane_of(0.0, 3.5);                     /* hazard side: left, edge at +1.75 */
    const pp_reference_line_t *ref = pp_corridor_update(&c, &live, NULL, true, PP_SIDE_LEFT, 2.9,
                                                         &pp_calibration, dt);
    PP_CHECK_NEAR(ref->width, 3.5, 1e-9);

    live = lane_of(0.25, 4.0);                                        /* left edge jumped out to +2.25 */
    unsigned held = 0U;
    for (unsigned k = 0U; k < 20U; k++) {                             /* 0.5 s: below T_confirm = 1 s */
        ref = pp_corridor_update(&c, &live, &still, false, PP_SIDE_LEFT, 2.9, &pp_calibration, dt);
        held += c.pending ? 1U : 0U;
        PP_CHECK_NEAR(ref->width, 3.5, 1e-9);                         /* corridor edge did not move */
    }
    PP_CHECK(held == 20U);
    for (unsigned k = 0U; k < 30U; k++) {                             /* past T_confirm: slides slowly */
        ref = pp_corridor_update(&c, &live, &still, false, PP_SIDE_LEFT, 2.9, &pp_calibration, dt);
    }
    PP_CHECK(ref->width > 3.5);
    PP_CHECK(ref->width < 3.5 + (double)pp_calibration.ref_rate * 1.5);  /* at most ref_rate per second */

    live = lane_of(-0.2, 3.1);                                        /* left edge moved to +1.35: toward the car */
    ref = pp_corridor_update(&c, &live, &still, false, PP_SIDE_LEFT, 2.9, &pp_calibration, dt);
    PP_CHECK(ref->width > 3.1 + 0.01);                                /* one frame may be noise */
    for (unsigned k = 0U; k < 80U; k++) {                             /* confirmed, then followed */
        ref = pp_corridor_update(&c, &live, &still, false, PP_SIDE_LEFT, 2.9, &pp_calibration, dt);
    }
    PP_CHECK_NEAR(ref->width, 3.1, 0.01);
    PP_CHECK(!c.pending);
}

/* PP-TS-026: an outward start is arrested first, then the car returns slowly to the centre. */
static void test_outward_start_is_arrested_then_returns_slowly(void)
{
    const pp_reference_line_t ref = {.valid = true, .width = 3.5, .view_end = 100.0};
    const pp_lateral_state_t start = {.d = 0.3, .d_dot = 0.5};
    const pp_function_limits_t limits = {PP_AY_MAX_LKA, PP_JERK_MAX_LKA, PP_AY_ADD_MAX_LKA};
    const pp_intervention_request_t request = {.received_us = 1000000U, .side = PP_SIDE_LEFT};
    pp_speed_profile_t speed;
    pp_speed_profile(NULL, request.received_us, 20.0, &speed);
    pp_intervention_path_t path;
    pp_intervention_begin(&path, &request, 2.0, request.received_us, &ref, &start, &speed,
                          &limits, &VP0, &pp_calibration, false);
    PP_CHECK(path.two_phase);
    const double arrest = path.profile.duration;
    PP_CHECK_NEAR(path.back.duration, (double)pp_calibration.T_return, 1.0e-9);
    pp_lateral_path_t lateral;
    pp_intervention_sample(&path, request.received_us + (uint64_t)(arrest * 1.0e6), &lateral);
    const double peak = start.d + (0.4 * start.d_dot * arrest);
    PP_CHECK_NEAR(lateral.d[0], peak, 1.0e-6);
    PP_CHECK_NEAR(lateral.d_dot[0], 0.0, 1.0e-6);
    double smallest = lateral.d[0];
    for (uint32_t k = 0U; k < 8U; k++) {
        pp_intervention_sample(&path, request.received_us + (uint64_t)((arrest + (double)k) * 1.0e6), &lateral);
        smallest = (lateral.d[0] < smallest) ? lateral.d[0] : smallest;
    }
    PP_CHECK(smallest >= -1.0e-6);                                    /* no overshoot of the centre */
}

int main(void)
{
    test_end_condition_needs_the_car_near_the_centre();
    test_corridor_holds_a_jump_away_and_takes_one_toward_the_car();
    test_outward_start_is_arrested_then_returns_slowly();
    test_measured_edge_needs_association_with_ego_lane();
    test_profile_advances_from_original_start_time();
    test_chosen_candidate_is_not_cut_by_t10();
    test_aligns_vehicle_state_with_completion_tick();
    return PP_TEST_RESULT();
}

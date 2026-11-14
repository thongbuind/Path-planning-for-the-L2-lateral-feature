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
    PP_CHECK_NEAR(lateral.d[0], 0.3, 1.0e-6);
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

int main(void)
{
    test_measured_edge_needs_association_with_ego_lane();
    test_profile_advances_from_original_start_time();
    test_chosen_candidate_is_not_cut_by_t10();
    test_aligns_vehicle_state_with_completion_tick();
    return PP_TEST_RESULT();
}

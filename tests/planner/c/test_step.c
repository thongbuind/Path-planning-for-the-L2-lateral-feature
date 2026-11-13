/* One full planner cycle through the public API (pp_init, pp_step), white box. */

#include <float.h>
#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#include "pp_calibration.h"
#include "pp_planner.h"
#include "pp_test.h"

#define T0 (10000000ULL)

static uint64_t memory[8192];   /* 64 KB; the state is about 37 KB with the T7 C workspace */

static const pp_vehicle_config_t VP0 = {2.9F, 1.45F, 1.9F, 15.0F, 0.61F, 6.0F, 0.05F};

/* Straight motion at 25 m/s. */
static void ego_motion(void *context, const pp_ego_motion_request_t *request,
                       pp_ego_motion_response_t *response)
{
    (void)context;
    response->valid = true;
    response->dx = (float)(25.0 * (double)(request->t2_us - request->t1_us) * 1e-6);
    response->dy = 0.0F;
    response->dyaw = 0.0F;
}

static void set_line(pp_lane_line_t *line, float c0)
{
    line->c0 = c0;
    line->view_range_start = 0.0F;
    line->view_range_end = 80.0F;
    line->confidence = 0.9F;
    line->status = PP_LINE_STATUS_MEASURED;
}

/* Straight lane 3.5 m; the car 0.3 m right of the centre; HWA requested. */
static pp_planner_inputs_t inputs(void)
{
    pp_planner_inputs_t in;
    (void)memset(&in, 0, sizeof(in));
    in.t0_us = T0;

    in.lane_model.present = true;
    in.lane_model.rx_us = T0 - 5000U;
    in.lane_model.message.header.stamp_us = T0 - 105000U;   /* captured 105 ms ago */
    in.lane_model.message.header.valid = true;
    for (unsigned i = 0U; i < PP_LANE_LINES; i++) {
        in.lane_model.message.lines[i].status = PP_LINE_STATUS_LOST;
    }
    for (unsigned i = 0U; i < PP_ROAD_EDGES; i++) {
        in.lane_model.message.road_edges[i].status = PP_LINE_STATUS_LOST;
    }
    set_line(&in.lane_model.message.lines[1], 0.3F + 1.75F);  /* L1 */
    set_line(&in.lane_model.message.lines[2], 0.3F - 1.75F);  /* R1 */
    in.lane_model.message.lane_width = 3.5F;

    in.speed.present = true;
    in.speed.rx_us = T0 - 2000U;
    in.speed.message.header.stamp_us = T0 - 2000U;
    in.speed.message.header.valid = true;
    in.speed.message.speed_mps = 25.0F;
    in.speed.message.direction = PP_DIRECTION_FORWARD;

    in.function_requests.present = true;
    in.function_requests.rx_us = T0 - 1000U;
    in.function_requests.message.header.stamp_us = T0 - 2000U;
    in.function_requests.message.header.valid = true;
    in.function_requests.message.requests[0].state = PP_REQUEST_STATE_REQUEST;
    return in;
}

static void test_hwa_path_from_car_to_centre(void)
{
    pp_planner_outputs_t out;
    PP_CHECK(pp_state_size() <= sizeof(memory));
    PP_CHECK(pp_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    const pp_planner_inputs_t in = inputs();
    pp_step(memory, &in, ego_motion, NULL, &out);

    PP_CHECK(out.trajectory_sent);
    PP_CHECK(out.trajectory.header.valid);
    PP_CHECK(out.trajectory.header.stamp_us == T0);         /* PP-SWR-012 */
    PP_CHECK(out.trajectory.header.frame_id == PP_FRAME_ID_BASE_LINK);
    PP_CHECK(out.path_status.path_valid);
    PP_CHECK(out.path_status.active_function == PP_ACTIVE_FUNCTION_HWA);
    PP_CHECK(out.lateral_limits_sent);                      /* PP-SWR-150 */
    PP_CHECK(out.lateral_limits.header.valid);
    PP_CHECK_NEAR(out.lateral_limits.v_max, 500.0, 1e-3);   /* straight: floor of the curvature */
    PP_CHECK(!out.lateral_limits.lateral_limit_reached);
    PP_CHECK(out.lateral_limits.lateral_limit_reached == out.path_status.lateral_limit_reached);
    /* Path starts at the car (straight lane, lines moved with the car) and ends at the centre. */
    PP_CHECK_NEAR(out.trajectory.points[0].pose.y, 0.0, 1e-5);
#ifdef PP_T7_QP
    PP_CHECK(out.trajectory.points[30].pose.y > 0.0F);
#else
    /* HWA just started off-centre: recentering quintic over T_recenter (3.5 s). */
    const double tau = 3.0 / (double)pp_calibration.T_recenter;
    const double q = (10.0 * tau * tau * tau) - (15.0 * tau * tau * tau * tau)
                     + (6.0 * tau * tau * tau * tau * tau);
    PP_CHECK_NEAR(out.trajectory.points[30].pose.y, 0.3 * q, 1e-4);
#endif
    PP_CHECK_NEAR(out.trajectory.points[30].pose.x, 75.0, 1e-3);
    PP_CHECK_NEAR(out.trajectory.points[10].longitudinal_velocity_mps, 25.0, 1e-6);

    /* Counters advance by one per cycle (PP-SWR-014). */
    pp_planner_inputs_t next = in;
    next.t0_us += PP_PLANNER_PERIOD_US;
    pp_planner_outputs_t out2;
    pp_step(memory, &next, ego_motion, NULL, &out2);
    PP_CHECK(out2.trajectory.header.counter == (uint8_t)(out.trajectory.header.counter + 1U));
}

static void test_no_lane_model_means_no_path(void)
{
    pp_planner_outputs_t out;
    PP_CHECK(pp_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    pp_planner_inputs_t in = inputs();
    in.lane_model.present = false;
    pp_step(memory, &in, ego_motion, NULL, &out);
    PP_CHECK(out.trajectory_sent);                          /* every cycle (PP-SWR-010) */
    PP_CHECK(!out.trajectory.header.valid);
    PP_CHECK(!out.path_status.path_valid);
    PP_CHECK(out.path_status.active_function == PP_ACTIVE_FUNCTION_NONE);  /* PP-SWR-043 */
}

static void test_stale_lane_model(void)
{
    pp_planner_outputs_t out;
    PP_CHECK(pp_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    pp_planner_inputs_t in = inputs();
    in.lane_model.message.header.stamp_us = T0 - 260000U;   /* older than 250 ms (PP-SWR-131) */
    pp_step(memory, &in, ego_motion, NULL, &out);
    PP_CHECK(!out.path_status.path_valid);
}

static void test_hwa_not_requested(void)
{
    pp_planner_outputs_t out;
    PP_CHECK(pp_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    pp_planner_inputs_t in = inputs();
    in.function_requests.message.requests[0].state = PP_REQUEST_STATE_STANDBY;
    pp_step(memory, &in, ego_motion, NULL, &out);
    PP_CHECK(out.path_status.path_valid);                   /* PP-SWR-042 */
    PP_CHECK(out.path_status.active_function == PP_ACTIVE_FUNCTION_NONE);
}

static void fresh_chassis(pp_planner_inputs_t *in, uint64_t t0)
{
    in->t0_us = t0;
    in->lane_model.rx_us = t0;
    in->lane_model.message.header.stamp_us = t0;
    for (unsigned i = 0U; i < PP_LANE_LINES; i++) {
        in->lane_model.message.lines[i].variance[0] = 0.0009F;
    }
    in->speed.rx_us = t0;
    in->speed.message.header.stamp_us = t0;
    in->imu.present = true;
    in->imu.rx_us = t0;
    in->imu.message.header = (pp_basic_header_t){t0, 0U, true};
    in->steering.present = true;
    in->steering.rx_us = t0;
    in->steering.message.header = (pp_basic_header_t){t0, 0U, true};
    in->vehicle_state.present = true;
    in->vehicle_state.rx_us = t0;
    in->vehicle_state.message.header = (pp_header_t){t0, 0U, true, PP_FRAME_ID_BASE_LINK};
}

static void fresh_requests(pp_planner_inputs_t *in)
{
    in->function_requests.rx_us = in->t0_us;
    in->function_requests.message.header.stamp_us = in->t0_us;
}

static void test_function_requests_timeout_and_recovery(void)
{
    pp_planner_outputs_t out;
    pp_planner_inputs_t in = inputs();
    PP_CHECK(pp_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    fresh_chassis(&in, T0);
    fresh_requests(&in);
    for (uint64_t t = T0; t <= T0 + PP_FUNCTION_REQUESTS_TIMEOUT_US; t += PP_PLANNER_PERIOD_US) {
        fresh_chassis(&in, t);
        pp_step(memory, &in, ego_motion, NULL, &out);
        PP_CHECK(out.trajectory.header.valid && out.path_status.path_valid);
        const pp_active_function_t expected = (t - T0 <= PP_FUNCTION_REQUESTS_MAX_AGE_US)
                                              ? PP_ACTIVE_FUNCTION_HWA : PP_ACTIVE_FUNCTION_NONE;
        PP_CHECK(out.path_status.active_function == expected);
    }
    fresh_chassis(&in, T0 + PP_FUNCTION_REQUESTS_TIMEOUT_US + PP_PLANNER_PERIOD_US);
    pp_step(memory, &in, ego_motion, NULL, &out);
    PP_CHECK(out.path_status_sent && out.path_status.header.valid && out.trajectory_sent);
    PP_CHECK(!out.trajectory.header.valid && !out.path_status.path_valid);
    PP_CHECK(out.path_status.active_function == PP_ACTIVE_FUNCTION_NONE);
    PP_CHECK(!out.lateral_limits.header.valid);
    fresh_chassis(&in, in.t0_us + PP_PLANNER_PERIOD_US);
    fresh_requests(&in);
    pp_step(memory, &in, ego_motion, NULL, &out);
    PP_CHECK(out.trajectory.header.valid && out.path_status.path_valid);
    PP_CHECK(out.path_status.active_function == PP_ACTIVE_FUNCTION_HWA);
    PP_CHECK_NEAR(out.trajectory.points[0].pose.y, 0.0, 0.1);
}

static void test_interventions_can_switch_and_cancel_in_one_cycle(void)
{
    pp_planner_outputs_t out;
    pp_planner_inputs_t in = inputs();
    PP_CHECK(pp_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    fresh_chassis(&in, T0);
    fresh_requests(&in);
    in.vehicle_state.message.lateral_velocity = -0.2F;
    pp_function_request_t *r = in.function_requests.message.requests;
    r[1].state = PP_REQUEST_STATE_REQUEST;
    r[1].side = PP_SIDE_RIGHT;
    r[1].tlc = 0.8F;
    r[2] = r[1];
    r[2].elk_reason = PP_ELK_REASON_SOLID_LINE;
    pp_step(memory, &in, ego_motion, NULL, &out);
    PP_CHECK(out.trajectory.header.valid && out.path_status.path_valid);
    PP_CHECK(out.path_status.active_function == PP_ACTIVE_FUNCTION_ELK);
    PP_CHECK(out.path_status.elk_phase == PP_INTERVENTION_PHASE_ACTIVE);
    PP_CHECK(out.path_status.lka_phase == PP_INTERVENTION_PHASE_NONE);
    PP_CHECK_NEAR(out.trajectory.points[0].pose.y, 0.0, 0.1);
    PP_CHECK_NEAR(out.trajectory.points[0].lateral_velocity_mps, -0.2, 0.1);

    fresh_chassis(&in, T0 + PP_PLANNER_PERIOD_US);
    fresh_requests(&in);
    r[2].state = PP_REQUEST_STATE_STANDBY;
    pp_step(memory, &in, ego_motion, NULL, &out);
    PP_CHECK(out.path_status.active_function == PP_ACTIVE_FUNCTION_LKA);
    PP_CHECK(out.path_status.elk_phase == PP_INTERVENTION_PHASE_NONE);
    PP_CHECK(out.path_status.lka_phase == PP_INTERVENTION_PHASE_ACTIVE);

    fresh_chassis(&in, in.t0_us + PP_PLANNER_PERIOD_US);
    fresh_requests(&in);
    in.vehicle_state.present = false;
    pp_step(memory, &in, ego_motion, NULL, &out);
    PP_CHECK(out.path_status.path_valid && out.path_status.active_function == PP_ACTIVE_FUNCTION_LKA);

    fresh_chassis(&in, in.t0_us + PP_PLANNER_PERIOD_US);
    fresh_requests(&in);
    r[0].state = PP_REQUEST_STATE_STANDBY;
    r[1].state = PP_REQUEST_STATE_STANDBY;
    pp_step(memory, &in, ego_motion, NULL, &out);
    PP_CHECK(out.path_status.path_valid && out.trajectory.header.valid);
    PP_CHECK(out.path_status.active_function == PP_ACTIVE_FUNCTION_NONE);
    PP_CHECK(out.path_status.lka_phase == PP_INTERVENTION_PHASE_NONE);
}

static void test_elk_road_edge_keeps_path_on_cancellation_tick(void)
{
    pp_planner_inputs_t in = inputs();
    pp_planner_outputs_t out;
    PP_CHECK(pp_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    fresh_chassis(&in, T0);
    fresh_requests(&in);
    in.lane_model.message.lines[1].status = PP_LINE_STATUS_LOST;
    in.lane_model.message.lines[2].status = PP_LINE_STATUS_LOST;
    for (unsigned side = 0U; side < PP_ROAD_EDGES; side++) {
        pp_road_edge_t *edge = &in.lane_model.message.road_edges[side];
        edge->c0 = (side == 0U) ? 2.05F : -1.45F;
        edge->variance[0] = 0.0009F;
        edge->view_range_end = 80.0F;
        edge->status = PP_LINE_STATUS_MEASURED;
        edge->confidence = 0.9F;
    }
    pp_function_request_t *requests = in.function_requests.message.requests;
    requests[0].state = PP_REQUEST_STATE_OFF;
    requests[2].state = PP_REQUEST_STATE_REQUEST;
    requests[2].side = PP_SIDE_RIGHT;
    requests[2].elk_reason = PP_ELK_REASON_ROAD_EDGE;
    requests[2].tlc = 0.6F;
    in.vehicle_state.message.lateral_velocity = -0.2F;
    pp_step(memory, &in, ego_motion, NULL, &out);
    PP_CHECK(out.path_status.active_function == PP_ACTIVE_FUNCTION_ELK);
    PP_CHECK(out.path_status.path_valid);

    fresh_chassis(&in, T0 + PP_PLANNER_PERIOD_US);
    fresh_requests(&in);
    requests[2] = (pp_function_request_t){0};
    pp_step(memory, &in, ego_motion, NULL, &out);
    PP_CHECK(out.path_status.active_function == PP_ACTIVE_FUNCTION_NONE);
    PP_CHECK(out.path_status.elk_phase == PP_INTERVENTION_PHASE_NONE);
    PP_CHECK(out.path_status.path_valid && out.trajectory.header.valid); /* PP-SWR-037 */
}

/* Fresh LongitudinalPlan with every point at (v, a). */
static void set_plan(pp_planner_inputs_t *in, float v, float a)
{
    in->longitudinal_plan.present = true;
    in->longitudinal_plan.rx_us = in->t0_us - 3000U;
    in->longitudinal_plan.message.header.stamp_us = in->t0_us;
    in->longitudinal_plan.message.header.valid = true;
    in->longitudinal_plan.message.header.frame_id = PP_FRAME_ID_BASE_LINK;
    in->longitudinal_plan.message.mode = PP_LONGITUDINAL_MODE_CRUISE;
    for (unsigned i = 0U; i < PP_LONGITUDINAL_PLAN_POINTS; i++) {
        in->longitudinal_plan.message.points[i].v = v;
        in->longitudinal_plan.message.points[i].a = a;
    }
}

static bool trajectory_finite(const pp_trajectory_t *t)
{
    bool ok = true;
    for (unsigned k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        const pp_trajectory_point_t *p = &t->points[k];
        ok = ok && isfinite(p->pose.x) && isfinite(p->pose.y) && isfinite(p->pose.yaw)
                && isfinite(p->longitudinal_velocity_mps) && isfinite(p->acceleration_mps2)
                && isfinite(p->lateral_velocity_mps) && isfinite(p->heading_rate_rps)
                && isfinite(p->curvature) && isfinite(p->front_wheel_angle_rad);
    }
    return ok;
}

/* Plan used when in range (PP-SWR-153); out of range it is ignored (PP-SWR-156, 154). */
static void test_longitudinal_plan_range(void)
{
    struct { float v; float a; float v_out; float a_out; } cases[] = {
        {20.0F, 0.5F, 20.0F, 0.5F},                                     /* in range: used */
        {PP_LONGITUDINAL_PLAN_V_MAX_MPS, -PP_LONGITUDINAL_PLAN_A_MAX_MPS2,
         PP_LONGITUDINAL_PLAN_V_MAX_MPS, -PP_LONGITUDINAL_PLAN_A_MAX_MPS2}, /* range ends: used */
        {FLT_MAX, 0.0F, 25.0F, 0.0F},                                   /* B0 C2 high end */
        {-FLT_MAX, -FLT_MAX, 25.0F, 0.0F},                              /* B0 C2 low end */
        {20.0F, NAN, 25.0F, 0.0F},
        {INFINITY, 0.0F, 25.0F, 0.0F},
        {20.0F, 40.0F, 25.0F, 0.0F},
        {-1.0F, 0.0F, 25.0F, 0.0F},
    };
    for (unsigned c = 0U; c < sizeof(cases) / sizeof(cases[0]); c++) {
        PP_CHECK(pp_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
        pp_planner_inputs_t in = inputs();
        set_plan(&in, cases[c].v, cases[c].a);
        pp_planner_outputs_t out;
        pp_step(memory, &in, ego_motion, NULL, &out);
        PP_CHECK(out.trajectory_sent);
        PP_CHECK(out.path_status.path_valid);
        PP_CHECK(trajectory_finite(&out.trajectory));
        PP_CHECK_NEAR(out.trajectory.points[10].longitudinal_velocity_mps, cases[c].v_out, 1e-3);
        PP_CHECK_NEAR(out.trajectory.points[10].acceleration_mps2, cases[c].a_out, 1e-3);
    }

    /* One bad point is enough to ignore the whole plan. */
    PP_CHECK(pp_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    pp_planner_inputs_t in = inputs();
    set_plan(&in, 20.0F, 0.0F);
    in.longitudinal_plan.message.points[30].v = FLT_MAX;
    pp_planner_outputs_t out;
    pp_step(memory, &in, ego_motion, NULL, &out);
    PP_CHECK_NEAR(out.trajectory.points[10].longitudinal_velocity_mps, 25.0, 1e-3);
}

/* 25 m/s straight, plus a lateral drift to the left of 0.5 m/s (the driver steering). */
#define DRIFT_MPS (0.5)
static void drifting_motion(void *context, const pp_ego_motion_request_t *request,
                            pp_ego_motion_response_t *response)
{
    (void)context;
    const double dt = (double)(request->t2_us - request->t1_us) * 1e-6;
    response->valid = true;
    response->dx = (float)(25.0 * dt);
    response->dy = (float)(DRIFT_MPS * dt);
    response->dyaw = 0.0F;
}

/* Cycle k after T0: fresh inputs, the lines moved right in base_link by the drift. */
static void drift_inputs(pp_planner_inputs_t *in, unsigned k, bool override)
{
    const uint64_t t = T0 + ((uint64_t)k * PP_PLANNER_PERIOD_US);
    fresh_chassis(in, t);
    fresh_requests(in);
    const float shift = (float)(DRIFT_MPS * (double)(t - T0) * 1e-6);
    in->lane_model.message.lines[1].c0 = 0.3F + 1.75F - shift;
    in->lane_model.message.lines[2].c0 = 0.3F - 1.75F - shift;
    /* v_y stays 0: the planner does not see the drift coming, as when the driver starts
     * to steer; the old path then does not follow the car. */
    in->vehicle_state.message.lateral_velocity = 0.0F;
    in->function_requests.message.driver_override = override;
}

static void test_driver_override_path_starts_at_car(void)
{
    pp_planner_outputs_t out;
    pp_planner_inputs_t in = inputs();
    PP_CHECK(pp_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    unsigned k = 0U;
    /* Without override the start is stitched to the old path, which the car leaves. */
    for (; k < 10U; k++) {
        drift_inputs(&in, k, false);
        pp_step(memory, &in, drifting_motion, NULL, &out);
        PP_CHECK(out.path_status.path_valid);
    }
    PP_CHECK(fabs((double)out.trajectory.points[0].pose.y) > 0.05);
    /* PP-SWR-039: while the driver overrides, point 0 is the car. */
    for (; k < 14U; k++) {
        drift_inputs(&in, k, true);
        pp_step(memory, &in, drifting_motion, NULL, &out);
        PP_CHECK(out.path_status.path_valid);
        PP_CHECK(out.path_status.active_function == PP_ACTIVE_FUNCTION_HWA);
        PP_CHECK_NEAR(out.trajectory.points[0].pose.y, 0.0, 0.01);
        /* PP-TS-017 V2: parallel to the lane at the car's offset, not pulled to the centre. */
        PP_CHECK_NEAR(out.trajectory.points[30].pose.y, out.trajectory.points[0].pose.y, 0.01);
    }
    /* PP-SWR-040: the first HWA path after the override starts at the car. */
    drift_inputs(&in, k, false);
    pp_step(memory, &in, drifting_motion, NULL, &out);
    PP_CHECK(out.path_status.path_valid);
    PP_CHECK(out.path_status.active_function == PP_ACTIVE_FUNCTION_HWA);
    PP_CHECK_NEAR(out.trajectory.points[0].pose.y, 0.0, 0.01);
    /* Then back towards the centre, left of the car (the car is right of the centre). */
    for (k++; k < 40U; k++) {
        drift_inputs(&in, k, false);
        in.lane_model.message.lines[1].c0 = 0.3F + 1.75F - (float)(DRIFT_MPS * 0.35);
        in.lane_model.message.lines[2].c0 = 0.3F - 1.75F - (float)(DRIFT_MPS * 0.35);
        pp_step(memory, &in, ego_motion, NULL, &out);
        PP_CHECK(out.path_status.path_valid);
    }
    PP_CHECK(out.trajectory.points[30].pose.y > 0.05F);
}

int main(void)
{
    test_driver_override_path_starts_at_car();
    test_hwa_path_from_car_to_centre();
    test_no_lane_model_means_no_path();
    test_stale_lane_model();
    test_hwa_not_requested();
    test_function_requests_timeout_and_recovery();
    test_interventions_can_switch_and_cancel_in_one_cycle();
    test_elk_road_edge_keeps_path_on_cancellation_tick();
    test_longitudinal_plan_range();
    return PP_TEST_RESULT();
}

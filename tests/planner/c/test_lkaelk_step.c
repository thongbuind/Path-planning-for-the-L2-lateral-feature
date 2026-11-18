/* One full cycle of the LKA/ELK planner through the public API (pp_lkaelk_init, pp_lkaelk_step), white box. */

#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#include "pp_calibration.h"
#include "pp_planner.h"
#include "pp_test.h"

#define T0 (10000000ULL)

static uint64_t memory[8192];   /* 64 KB; the state is about 37 KB with the T7 C workspace */

/* A new delivery of a pub/sub input carries the next counter, as on the real interface
 * (Interface Control Document 4); the tests only refresh rx_us. */
static uint64_t delivered_rx[5];
static bool delivered[5];

static void next_counter(unsigned i, bool present, uint64_t rx_us, uint8_t *counter)
{
    if (present && (!delivered[i] || (rx_us != delivered_rx[i]))) {
        if (delivered[i]) {
            *counter = (uint8_t)(*counter + 1U);
        }
        delivered[i] = true;
        delivered_rx[i] = rx_us;
    }
}

static void step(pp_lka_elk_inputs_t *in, pp_ego_motion_fn motion, pp_lka_elk_outputs_t *out)
{
    next_counter(0U, in->lane_model.present, in->lane_model.rx_us,
                 &in->lane_model.message.header.counter);
    next_counter(2U, in->vehicle_state.present, in->vehicle_state.rx_us,
                 &in->vehicle_state.message.header.counter);
    next_counter(3U, in->function_requests.present, in->function_requests.rx_us,
                 &in->function_requests.message.header.counter);
    next_counter(4U, in->longitudinal_plan.present, in->longitudinal_plan.rx_us,
                 &in->longitudinal_plan.message.header.counter);
    pp_lkaelk_step(memory, in, motion, NULL, out);
}

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

/* Straight lane 3.5 m; the car 0.3 m right of the centre; no LKA or ELK requested. */
static pp_lka_elk_inputs_t inputs(void)
{
    pp_lka_elk_inputs_t in;
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

    in.imu.present = true;
    in.imu.rx_us = T0;
    in.imu.message.header = (pp_basic_header_t){T0, 0U, true};
    in.steering.present = true;
    in.steering.rx_us = T0;
    in.steering.message.header = (pp_basic_header_t){T0, 0U, true};

    in.function_requests.present = true;
    in.function_requests.rx_us = T0 - 1000U;
    in.function_requests.message.header.stamp_us = T0 - 2000U;
    in.function_requests.message.header.valid = true;
    return in;
}


static void test_no_lane_model_means_no_path(void)
{
    pp_lka_elk_outputs_t out;
    PP_CHECK(pp_lkaelk_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    pp_lka_elk_inputs_t in = inputs();
    in.lane_model.present = false;
    step(&in, ego_motion, &out);
    PP_CHECK(out.trajectory_sent);                          /* every cycle (PP-SWR-010) */
    PP_CHECK(!out.trajectory.header.valid);
    PP_CHECK(!out.intervention_status.path_valid);
    PP_CHECK(out.intervention_status.active_function == PP_INTERVENTION_FUNCTION_NONE);  /* PP-SWR-043 */
}

static void test_stale_lane_model(void)
{
    pp_lka_elk_outputs_t out;
    PP_CHECK(pp_lkaelk_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    pp_lka_elk_inputs_t in = inputs();
    in.lane_model.message.header.stamp_us = T0 - 260000U;   /* older than 250 ms (PP-SWR-131) */
    step(&in, ego_motion, &out);
    PP_CHECK(!out.intervention_status.path_valid);
}


static void fresh_chassis(pp_lka_elk_inputs_t *in, uint64_t t0)
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
    in->vehicle_state.message.header.stamp_us = t0;     /* counter kept: step() advances it per delivery */
    in->vehicle_state.message.header.valid = true;
    in->vehicle_state.message.header.frame_id = PP_FRAME_ID_BASE_LINK;
}

static void fresh_requests(pp_lka_elk_inputs_t *in)
{
    in->function_requests.rx_us = in->t0_us;
    in->function_requests.message.header.stamp_us = in->t0_us;
}

/* No request: inputs are fine, so path_valid is true, nothing drives, and the Trajectory is
 * sent but not valid (PP-SWR-037, 180, 019). */
static void test_no_request_sends_an_invalid_trajectory(void)
{
    pp_lka_elk_outputs_t out;
    PP_CHECK(pp_lkaelk_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    pp_lka_elk_inputs_t in = inputs();
    step(&in, ego_motion, &out);
    PP_CHECK(out.intervention_status_sent && out.intervention_status.header.valid);
    PP_CHECK(out.intervention_status.path_valid);
    PP_CHECK(out.intervention_status.active_function == PP_INTERVENTION_FUNCTION_NONE);
    PP_CHECK(out.trajectory_sent && !out.trajectory.header.valid);
    PP_CHECK(out.trajectory.planner_id == PP_PLANNER_ID_LKA_ELK);
    PP_CHECK(out.trajectory.header.stamp_us == T0);
}

static void test_chassis_fault_blocks_a_request_until_it_is_made_again(void)
{
    pp_lka_elk_inputs_t in = inputs();
    pp_lka_elk_outputs_t out;
    PP_CHECK(pp_lkaelk_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    fresh_chassis(&in, T0);
    fresh_requests(&in);
    in.vehicle_state.message.lateral_velocity = -0.2F;
    pp_function_request_t *lka = &in.function_requests.message.requests[1];
    lka->state = PP_REQUEST_STATE_REQUEST;
    lka->side = PP_SIDE_RIGHT;
    lka->tlc = 0.8F;
    step(&in, ego_motion, &out);
    PP_CHECK(out.trajectory.header.valid && out.intervention_status.active_function == PP_INTERVENTION_FUNCTION_LKA);

    fresh_chassis(&in, in.t0_us + PP_PLANNER_PERIOD_US);
    fresh_requests(&in);
    in.imu.present = false;
    step(&in, ego_motion, &out);
    PP_CHECK(!out.intervention_status.path_valid && !out.trajectory.header.valid);   /* PP-SWR-142 */
    PP_CHECK(out.intervention_status.active_function == PP_INTERVENTION_FUNCTION_NONE);  /* PP-SWR-043 */

    fresh_chassis(&in, in.t0_us + PP_PLANNER_PERIOD_US);
    fresh_requests(&in);
    step(&in, ego_motion, &out);
    PP_CHECK(out.intervention_status.path_valid);
    PP_CHECK(out.intervention_status.active_function == PP_INTERVENTION_FUNCTION_NONE);  /* PP-SWR-045 */

    fresh_chassis(&in, in.t0_us + PP_PLANNER_PERIOD_US);
    fresh_requests(&in);
    lka->state = PP_REQUEST_STATE_STANDBY;
    step(&in, ego_motion, &out);
    fresh_chassis(&in, in.t0_us + PP_PLANNER_PERIOD_US);
    fresh_requests(&in);
    lka->state = PP_REQUEST_STATE_REQUEST;
    step(&in, ego_motion, &out);
    PP_CHECK(out.trajectory.header.valid && out.intervention_status.active_function == PP_INTERVENTION_FUNCTION_LKA);
}

static void test_function_requests_timeout_invalidates_the_path(void)
{
    pp_lka_elk_inputs_t in = inputs();
    pp_lka_elk_outputs_t out;
    PP_CHECK(pp_lkaelk_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    fresh_chassis(&in, T0);
    fresh_requests(&in);
    step(&in, ego_motion, &out);
    PP_CHECK(out.intervention_status.path_valid);
    fresh_chassis(&in, T0 + PP_FUNCTION_REQUESTS_TIMEOUT_US + PP_PLANNER_PERIOD_US);
    step(&in, ego_motion, &out);
    PP_CHECK(out.intervention_status_sent && out.intervention_status.header.valid && out.trajectory_sent);
    PP_CHECK(!out.intervention_status.path_valid && !out.trajectory.header.valid);     /* PP-SWR-145 */
    fresh_chassis(&in, in.t0_us + PP_PLANNER_PERIOD_US);
    fresh_requests(&in);
    step(&in, ego_motion, &out);
    PP_CHECK(out.intervention_status.path_valid);
}

static void test_interventions_can_switch_and_cancel_in_one_cycle(void)
{
    pp_lka_elk_outputs_t out;
    pp_lka_elk_inputs_t in = inputs();
    PP_CHECK(pp_lkaelk_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    fresh_chassis(&in, T0);
    fresh_requests(&in);
    in.vehicle_state.message.lateral_velocity = -0.2F;
    pp_function_request_t *r = in.function_requests.message.requests;
    r[1].state = PP_REQUEST_STATE_REQUEST;
    r[1].side = PP_SIDE_RIGHT;
    r[1].tlc = 0.8F;
    r[2] = r[1];
    r[2].elk_reason = PP_ELK_REASON_SOLID_LINE;
    step(&in, ego_motion, &out);
    PP_CHECK(out.trajectory.header.valid && out.intervention_status.path_valid);
    PP_CHECK(out.intervention_status.active_function == PP_INTERVENTION_FUNCTION_ELK);
    PP_CHECK(out.intervention_status.elk_phase == PP_INTERVENTION_PHASE_ACTIVE);
    PP_CHECK(out.intervention_status.lka_phase == PP_INTERVENTION_PHASE_NONE);
    PP_CHECK_NEAR(out.trajectory.points[0].pose.y, 0.0, 0.1);
    PP_CHECK_NEAR(out.trajectory.points[0].lateral_velocity_mps, -0.2, 0.1);

    fresh_chassis(&in, T0 + PP_PLANNER_PERIOD_US);
    fresh_requests(&in);
    r[2].state = PP_REQUEST_STATE_STANDBY;
    step(&in, ego_motion, &out);
    PP_CHECK(out.intervention_status.active_function == PP_INTERVENTION_FUNCTION_LKA);
    PP_CHECK(out.intervention_status.elk_phase == PP_INTERVENTION_PHASE_NONE);
    PP_CHECK(out.intervention_status.lka_phase == PP_INTERVENTION_PHASE_ACTIVE);

    fresh_chassis(&in, in.t0_us + PP_PLANNER_PERIOD_US);
    fresh_requests(&in);
    in.vehicle_state.present = false;
    step(&in, ego_motion, &out);
    PP_CHECK(out.intervention_status.path_valid && out.intervention_status.active_function == PP_INTERVENTION_FUNCTION_LKA);

    fresh_chassis(&in, in.t0_us + PP_PLANNER_PERIOD_US);
    fresh_requests(&in);
    r[0].state = PP_REQUEST_STATE_STANDBY;
    r[1].state = PP_REQUEST_STATE_STANDBY;
    step(&in, ego_motion, &out);
    PP_CHECK(out.intervention_status.path_valid && !out.trajectory.header.valid);   /* PP-SWR-037, 180 */
    PP_CHECK(out.intervention_status.active_function == PP_INTERVENTION_FUNCTION_NONE);
    PP_CHECK(out.intervention_status.lka_phase == PP_INTERVENTION_PHASE_NONE);
}

static void test_active_lka_can_coast_on_last_ego_reference(void)
{
    pp_lka_elk_inputs_t in = inputs();
    pp_lka_elk_outputs_t out;
    PP_CHECK(pp_lkaelk_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    fresh_chassis(&in, T0);
    fresh_requests(&in);
    in.vehicle_state.message.lateral_velocity = -0.2F;
    pp_function_request_t *lka = &in.function_requests.message.requests[1];
    lka->state = PP_REQUEST_STATE_REQUEST;
    lka->side = PP_SIDE_RIGHT;
    lka->tlc = 0.8F;
    step(&in, ego_motion, &out);
    PP_CHECK(out.intervention_status.active_function == PP_INTERVENTION_FUNCTION_LKA);

    /* The two ego lines jump while a previously unseen outer line is measured.
     * T2 can only coast on the ego reference during the confirmation window. */
    fresh_chassis(&in, in.t0_us + PP_PLANNER_PERIOD_US);
    fresh_requests(&in);
    in.lane_model.message.lines[1].c0 += 0.7F;
    in.lane_model.message.lines[2].c0 += 0.7F;
    set_line(&in.lane_model.message.lines[0], 5.55F);
    step(&in, ego_motion, &out);
    PP_CHECK(out.intervention_status.path_valid);
    PP_CHECK(out.intervention_status.active_function == PP_INTERVENTION_FUNCTION_LKA);
}

static void test_elk_road_edge_keeps_path_on_cancellation_tick(void)
{
    pp_lka_elk_inputs_t in = inputs();
    pp_lka_elk_outputs_t out;
    PP_CHECK(pp_lkaelk_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
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
    step(&in, ego_motion, &out);
    PP_CHECK(out.intervention_status.active_function == PP_INTERVENTION_FUNCTION_ELK);
    PP_CHECK(out.intervention_status.path_valid);

    fresh_chassis(&in, T0 + PP_PLANNER_PERIOD_US);
    fresh_requests(&in);
    requests[2] = (pp_function_request_t){0};
    step(&in, ego_motion, &out);
    PP_CHECK(out.intervention_status.active_function == PP_INTERVENTION_FUNCTION_NONE);
    PP_CHECK(out.intervention_status.elk_phase == PP_INTERVENTION_PHASE_NONE);
    PP_CHECK(out.intervention_status.path_valid && !out.trajectory.header.valid); /* PP-SWR-037, 180 */
}

int main(void)
{
    PP_CHECK(pp_lkaelk_state_size() <= sizeof(memory));
    test_no_lane_model_means_no_path();
    test_stale_lane_model();
    test_no_request_sends_an_invalid_trajectory();
    test_chassis_fault_blocks_a_request_until_it_is_made_again();
    test_function_requests_timeout_invalidates_the_path();
    test_interventions_can_switch_and_cancel_in_one_cycle();
    test_active_lka_can_coast_on_last_ego_reference();
    test_elk_road_edge_keeps_path_on_cancellation_tick();
    return PP_TEST_RESULT();
}

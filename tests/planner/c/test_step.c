/* One full planner cycle through the public API (pp_init, pp_step), white box. */

#include <stdint.h>
#include <string.h>

#include "pp_calibration.h"
#include "pp_planner.h"
#include "pp_test.h"

#define T0 (10000000ULL)

static uint64_t memory[4096];

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
    /* HWA just started off-centre: recentering quintic over T_recenter (3.5 s). */
    const double tau = 3.0 / (double)pp_calibration.T_recenter;
    const double q = (10.0 * tau * tau * tau) - (15.0 * tau * tau * tau * tau)
                     + (6.0 * tau * tau * tau * tau * tau);
    PP_CHECK_NEAR(out.trajectory.points[30].pose.y, 0.3 * q, 1e-4);
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

int main(void)
{
    test_hwa_path_from_car_to_centre();
    test_no_lane_model_means_no_path();
    test_stale_lane_model();
    test_hwa_not_requested();
    return PP_TEST_RESULT();
}

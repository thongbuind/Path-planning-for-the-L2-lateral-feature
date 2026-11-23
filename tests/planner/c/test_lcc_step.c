#include <float.h>
#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#include "generators/pp_t7.h"
#include "pp_calibration.h"
#include "pp_planner.h"
#include "pp_test.h"

#define T0 (10000000ULL)

static uint64_t memory[8192];

static uint64_t delivered_rx[6];
static bool delivered[6];

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

static void step(pp_lcc_inputs_t *in, pp_ego_motion_fn motion, pp_lcc_outputs_t *out)
{
    next_counter(0U, in->lane_model.present, in->lane_model.rx_us,
                 &in->lane_model.message.header.counter);
    next_counter(1U, in->object_list.present, in->object_list.rx_us,
                 &in->object_list.message.header.counter);
    next_counter(2U, in->vehicle_state.present, in->vehicle_state.rx_us,
                 &in->vehicle_state.message.header.counter);
    next_counter(3U, in->function_requests.present, in->function_requests.rx_us,
                 &in->function_requests.message.header.counter);
    next_counter(4U, in->longitudinal_plan.present, in->longitudinal_plan.rx_us,
                 &in->longitudinal_plan.message.header.counter);
    next_counter(5U, in->lead_target.present, in->lead_target.rx_us,
                 &in->lead_target.message.header.counter);
    pp_lcc_step(memory, in, motion, NULL, out);
}

static const pp_vehicle_config_t VP0 = {2.9F, 1.45F, 1.9F, 15.0F, 0.61F, 6.0F, 0.05F};

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

static pp_lcc_inputs_t inputs(void)
{
    pp_lcc_inputs_t in;
    (void)memset(&in, 0, sizeof(in));
    in.t0_us = T0;

    in.lane_model.present = true;
    in.lane_model.rx_us = T0 - 5000U;
    in.lane_model.message.header.stamp_us = T0 - 105000U;
    in.lane_model.message.header.valid = true;
    for (unsigned i = 0U; i < PP_LANE_LINES; i++) {
        in.lane_model.message.lines[i].status = PP_LINE_STATUS_LOST;
    }
    for (unsigned i = 0U; i < PP_ROAD_EDGES; i++) {
        in.lane_model.message.road_edges[i].status = PP_LINE_STATUS_LOST;
    }
    set_line(&in.lane_model.message.lines[1], 0.3F + 1.75F);
    set_line(&in.lane_model.message.lines[2], 0.3F - 1.75F);
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
    in.function_requests.message.requests[0].state = PP_REQUEST_STATE_REQUEST;
    return in;
}

static void test_lcc_path_from_car_to_centre(void)
{
    pp_lcc_outputs_t out;
    PP_CHECK(pp_lcc_state_size() <= sizeof(memory));
    PP_CHECK(pp_lcc_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    pp_lcc_inputs_t in = inputs();
    step(&in, ego_motion, &out);

    PP_CHECK(out.trajectory_sent);
    PP_CHECK(out.trajectory.header.valid);
    PP_CHECK(out.trajectory.header.stamp_us == T0);
    PP_CHECK(out.trajectory.header.frame_id == PP_FRAME_ID_BASE_LINK);
    PP_CHECK(out.lcc_status.path_valid);
    PP_CHECK(out.lcc_status.lcc_mode == PP_LCC_MODE_LANE);
    PP_CHECK(out.lateral_limits_sent);
    PP_CHECK(out.lateral_limits.header.valid);
    PP_CHECK_NEAR(out.lateral_limits.v_max, 500.0, 1e-3);
    PP_CHECK(!out.lateral_limits.lateral_limit_reached);
    PP_CHECK(out.lateral_limits.lateral_limit_reached == out.lcc_status.lateral_limit_reached);
    PP_CHECK_NEAR(out.trajectory.points[0].pose.y, 0.0, 1e-5);
#ifndef PP_T7_QUINTIC_DURATION
    PP_CHECK(out.trajectory.points[30].pose.y > 0.0F);
#else
    const double tau = 3.0 / (double)pp_calibration.T_recenter;
    const double q = (10.0 * tau * tau * tau) - (15.0 * tau * tau * tau * tau)
                     + (6.0 * tau * tau * tau * tau * tau);
    PP_CHECK_NEAR(out.trajectory.points[30].pose.y, 0.3 * q, 1e-4);
#endif
    PP_CHECK_NEAR(out.trajectory.points[30].pose.x, 75.0, 1e-3);
    PP_CHECK_NEAR(out.trajectory.points[10].longitudinal_velocity_mps, 25.0, 1e-6);

    pp_lcc_inputs_t next = in;
    next.t0_us += PP_PLANNER_PERIOD_US;
    pp_lcc_outputs_t out2;
    step(&next, ego_motion, &out2);
    PP_CHECK(out2.trajectory.header.counter == (uint8_t)(out.trajectory.header.counter + 1U));
}

static void test_no_lane_model_means_no_path(void)
{
    pp_lcc_outputs_t out;
    PP_CHECK(pp_lcc_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    pp_lcc_inputs_t in = inputs();
    in.lane_model.present = false;
    step(&in, ego_motion, &out);
    PP_CHECK(out.trajectory_sent);
    PP_CHECK(!out.trajectory.header.valid);
    PP_CHECK(!out.lcc_status.path_valid);
    PP_CHECK(out.lcc_status.lcc_mode == PP_LCC_MODE_NONE);
}

static void test_stale_lane_model(void)
{
    pp_lcc_outputs_t out;
    PP_CHECK(pp_lcc_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    pp_lcc_inputs_t in = inputs();
    in.lane_model.message.header.stamp_us = T0 - 260000U;
    step(&in, ego_motion, &out);
    PP_CHECK(!out.lcc_status.path_valid);
}

static void test_lcc_not_requested(void)
{
    pp_lcc_outputs_t out;
    PP_CHECK(pp_lcc_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    pp_lcc_inputs_t in = inputs();
    in.function_requests.message.requests[0].state = PP_REQUEST_STATE_STANDBY;
    step(&in, ego_motion, &out);
    PP_CHECK(out.lcc_status.path_valid);
    PP_CHECK(out.lcc_status.lcc_mode == PP_LCC_MODE_NONE);
}

static void fresh_chassis(pp_lcc_inputs_t *in, uint64_t t0)
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
    in->vehicle_state.message.header.stamp_us = t0;
    in->vehicle_state.message.header.valid = true;
    in->vehicle_state.message.header.frame_id = PP_FRAME_ID_BASE_LINK;
}

static void fresh_requests(pp_lcc_inputs_t *in)
{
    in->function_requests.rx_us = in->t0_us;
    in->function_requests.message.header.stamp_us = in->t0_us;
}

static void test_chassis_fault_invalidates_lcc_and_fresh_inputs_restore_it(void)
{
    pp_lcc_inputs_t in = inputs();
    pp_lcc_outputs_t out;
    PP_CHECK(pp_lcc_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    step(&in, ego_motion, &out);
    PP_CHECK(out.lcc_status.lcc_mode == PP_LCC_MODE_LANE);

    fresh_chassis(&in, in.t0_us + PP_PLANNER_PERIOD_US);
    fresh_requests(&in);
    in.imu.present = false;
    step(&in, ego_motion, &out);
    PP_CHECK(!out.lcc_status.path_valid);
    PP_CHECK(!out.trajectory.header.valid && !out.lateral_limits.header.valid);
    PP_CHECK(out.lcc_status.lcc_mode == PP_LCC_MODE_NONE);

    fresh_chassis(&in, in.t0_us + PP_PLANNER_PERIOD_US);
    fresh_requests(&in);
    in.steering.message.header.valid = false;
    step(&in, ego_motion, &out);
    PP_CHECK(!out.lcc_status.path_valid);
    PP_CHECK(out.lcc_status.lcc_mode == PP_LCC_MODE_NONE);

    fresh_chassis(&in, in.t0_us + PP_PLANNER_PERIOD_US);
    fresh_requests(&in);
    step(&in, ego_motion, &out);
    PP_CHECK(out.lcc_status.path_valid);
    PP_CHECK(out.lcc_status.lcc_mode == PP_LCC_MODE_LANE);
}

static void test_function_requests_timeout_and_recovery(void)
{
    pp_lcc_outputs_t out;
    pp_lcc_inputs_t in = inputs();
    PP_CHECK(pp_lcc_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    fresh_chassis(&in, T0);
    fresh_requests(&in);
    for (uint64_t t = T0; t <= T0 + PP_FUNCTION_REQUESTS_TIMEOUT_US; t += PP_PLANNER_PERIOD_US) {
        fresh_chassis(&in, t);
        step(&in, ego_motion, &out);
        PP_CHECK(out.trajectory.header.valid && out.lcc_status.path_valid);
        const pp_lcc_mode_t expected = (t - T0 <= PP_FUNCTION_REQUESTS_MAX_AGE_US)
                                       ? PP_LCC_MODE_LANE : PP_LCC_MODE_NONE;
        PP_CHECK(out.lcc_status.lcc_mode == expected);
    }
    fresh_chassis(&in, T0 + PP_FUNCTION_REQUESTS_TIMEOUT_US + PP_PLANNER_PERIOD_US);
    step(&in, ego_motion, &out);
    PP_CHECK(out.lcc_status_sent && out.lcc_status.header.valid && out.trajectory_sent);
    PP_CHECK(!out.trajectory.header.valid && !out.lcc_status.path_valid);
    PP_CHECK(out.lcc_status.lcc_mode == PP_LCC_MODE_NONE);
    PP_CHECK(!out.lateral_limits.header.valid);
    fresh_chassis(&in, in.t0_us + PP_PLANNER_PERIOD_US);
    fresh_requests(&in);
    step(&in, ego_motion, &out);
    PP_CHECK(out.trajectory.header.valid && out.lcc_status.path_valid);
    PP_CHECK(out.lcc_status.lcc_mode == PP_LCC_MODE_LANE);
    PP_CHECK_NEAR(out.trajectory.points[0].pose.y, 0.0, 0.1);
}


static void set_plan(pp_lcc_inputs_t *in, float v, float a)
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

/* Kế hoạch trong miền được dùng; chỉ cần một điểm ngoài miền là bỏ cả kế hoạch (PP-SWR-153, 156). */
static void test_longitudinal_plan_range(void)
{
    struct { float v; float a; float v_out; float a_out; } cases[] = {
        {20.0F, 0.5F, 20.0F, 0.5F},
        {PP_LONGITUDINAL_PLAN_V_MAX_MPS, -PP_LONGITUDINAL_PLAN_A_MAX_MPS2,
         PP_LONGITUDINAL_PLAN_V_MAX_MPS, -PP_LONGITUDINAL_PLAN_A_MAX_MPS2},
        {FLT_MAX, 0.0F, 25.0F, 0.0F},
        {-FLT_MAX, -FLT_MAX, 25.0F, 0.0F},
        {20.0F, NAN, 25.0F, 0.0F},
        {INFINITY, 0.0F, 25.0F, 0.0F},
        {20.0F, 40.0F, 25.0F, 0.0F},
        {-1.0F, 0.0F, 25.0F, 0.0F},
    };
    for (unsigned c = 0U; c < sizeof(cases) / sizeof(cases[0]); c++) {
        PP_CHECK(pp_lcc_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
        pp_lcc_inputs_t in = inputs();
        set_plan(&in, cases[c].v, cases[c].a);
        pp_lcc_outputs_t out;
        step(&in, ego_motion, &out);
        PP_CHECK(out.trajectory_sent);
        PP_CHECK(out.lcc_status.path_valid);
        PP_CHECK(trajectory_finite(&out.trajectory));
        PP_CHECK_NEAR(out.trajectory.points[10].longitudinal_velocity_mps, cases[c].v_out, 1e-3);
        PP_CHECK_NEAR(out.trajectory.points[10].acceleration_mps2, cases[c].a_out, 1e-3);
    }

    PP_CHECK(pp_lcc_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    pp_lcc_inputs_t in = inputs();
    set_plan(&in, 20.0F, 0.0F);
    in.longitudinal_plan.message.points[30].v = FLT_MAX;
    pp_lcc_outputs_t out;
    step(&in, ego_motion, &out);
    PP_CHECK_NEAR(out.trajectory.points[10].longitudinal_velocity_mps, 25.0, 1e-3);
}

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

static void drift_inputs(pp_lcc_inputs_t *in, unsigned k, bool override)
{
    const uint64_t t = T0 + ((uint64_t)k * PP_PLANNER_PERIOD_US);
    fresh_chassis(in, t);
    fresh_requests(in);
    const float shift = (float)(DRIFT_MPS * (double)(t - T0) * 1e-6);
    in->lane_model.message.lines[1].c0 = 0.3F + 1.75F - shift;
    in->lane_model.message.lines[2].c0 = 0.3F - 1.75F - shift;
    /* Giữ v_y = 0 để mô phỏng planner chưa thấy xe bắt đầu lệch do tài xế mới đánh lái. */
    in->vehicle_state.message.lateral_velocity = 0.0F;
    in->function_requests.message.driver_override = override;
}

static void test_driver_override_path_starts_at_car(void)
{
    pp_lcc_outputs_t out;
    pp_lcc_inputs_t in = inputs();
    PP_CHECK(pp_lcc_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    unsigned k = 0U;
    for (; k < 10U; k++) {
        drift_inputs(&in, k, false);
        step(&in, drifting_motion, &out);
        PP_CHECK(out.lcc_status.path_valid);
    }
    PP_CHECK(fabs((double)out.trajectory.points[0].pose.y) > 0.01);
    for (; k < 14U; k++) {
        drift_inputs(&in, k, true);
        step(&in, drifting_motion, &out);
        PP_CHECK(out.lcc_status.path_valid);
        PP_CHECK(out.lcc_status.lcc_mode == PP_LCC_MODE_LANE);
        PP_CHECK_NEAR(out.trajectory.points[0].pose.y, 0.0, 0.01);
        /* Trong override, path song song làn tại offset của xe (PP-TS-017 V2). */
        PP_CHECK_NEAR(out.trajectory.points[30].pose.y, out.trajectory.points[0].pose.y, 0.01);
    }
    drift_inputs(&in, k, false);
    step(&in, drifting_motion, &out);
    PP_CHECK(out.lcc_status.path_valid);
    PP_CHECK(out.lcc_status.lcc_mode == PP_LCC_MODE_LANE);
    PP_CHECK_NEAR(out.trajectory.points[0].pose.y, 0.0, 0.01);
    for (k++; k < 40U; k++) {
        drift_inputs(&in, k, false);
        in.lane_model.message.lines[1].c0 = 0.3F + 1.75F - (float)(DRIFT_MPS * 0.35);
        in.lane_model.message.lines[2].c0 = 0.3F - 1.75F - (float)(DRIFT_MPS * 0.35);
        step(&in, ego_motion, &out);
        PP_CHECK(out.lcc_status.path_valid);
    }
    PP_CHECK(out.trajectory.points[30].pose.y > 0.05F);
}


static void test_lka_request_makes_the_lcc_path_start_at_the_car(void)
{
    pp_lcc_outputs_t out;
    pp_lcc_inputs_t in = inputs();
    PP_CHECK(pp_lcc_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    unsigned k = 0U;
    for (; k < 10U; k++) {
        drift_inputs(&in, k, false);
        step(&in, drifting_motion, &out);
        PP_CHECK(out.lcc_status.path_valid && out.lcc_status.lcc_mode == PP_LCC_MODE_LANE);
    }
    pp_function_request_t *lka = &in.function_requests.message.requests[1];
    for (; k < 14U; k++) {
        drift_inputs(&in, k, false);
        lka->state = PP_REQUEST_STATE_REQUEST;
        lka->side = PP_SIDE_RIGHT;
        step(&in, drifting_motion, &out);
        PP_CHECK(out.lcc_status.path_valid && out.lcc_status.lcc_mode == PP_LCC_MODE_LANE);
        PP_CHECK_NEAR(out.trajectory.points[0].pose.y, 0.0, 0.01);
        PP_CHECK_NEAR(out.trajectory.points[30].pose.y, out.trajectory.points[0].pose.y, 0.01);
    }
    drift_inputs(&in, k, false);
    lka->state = PP_REQUEST_STATE_STANDBY;
    step(&in, drifting_motion, &out);
    PP_CHECK(out.lcc_status.path_valid);
    PP_CHECK_NEAR(out.trajectory.points[0].pose.y, 0.0, 0.01);
}

static void set_lines_lost(pp_lcc_inputs_t *in)
{
    for (unsigned i = 0U; i < PP_LANE_LINES; i++) {
        in->lane_model.message.lines[i].status = PP_LINE_STATUS_LOST;
    }
}

static void test_lcc_mode_follows_the_state_of_the_lane(void)
{
    pp_lcc_outputs_t out;
    pp_lcc_inputs_t in = inputs();
    PP_CHECK(pp_lcc_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    fresh_chassis(&in, T0);
    fresh_requests(&in);
    step(&in, ego_motion, &out);
    PP_CHECK(out.lcc_status.lcc_mode == PP_LCC_MODE_LANE);
    in.function_requests.message.requests[0].state = PP_REQUEST_STATE_STANDBY;
    fresh_chassis(&in, in.t0_us + PP_PLANNER_PERIOD_US);
    fresh_requests(&in);
    step(&in, ego_motion, &out);
    PP_CHECK(out.lcc_status.path_valid && out.lcc_status.lcc_mode == PP_LCC_MODE_NONE);
    in.function_requests.message.requests[0].state = PP_REQUEST_STATE_REQUEST;

    set_lines_lost(&in);
    unsigned coasting = 0U;
    unsigned none = 0U;
    for (unsigned k = 0U; k < 60U; k++) {
        fresh_chassis(&in, in.t0_us + PP_PLANNER_PERIOD_US);
        fresh_requests(&in);
        step(&in, ego_motion, &out);
        if (out.lcc_status.lcc_mode == PP_LCC_MODE_COAST) {
            coasting++;
            PP_CHECK(out.lcc_status.path_valid && out.trajectory.header.valid);
        } else {
            PP_CHECK(!out.lcc_status.path_valid && (out.lcc_status.lcc_mode == PP_LCC_MODE_NONE));
            none++;
        }
    }
    PP_CHECK(coasting >= 38U && coasting <= 41U);
    PP_CHECK(coasting + none == 60U);
}

#define FOLLOW_SPEED (12.0)
static void ego_motion_slow(void *context, const pp_ego_motion_request_t *request,
                            pp_ego_motion_response_t *response)
{
    (void)context;
    response->valid = true;
    response->dx = (float)(FOLLOW_SPEED * (double)(request->t2_us - request->t1_us) * 1e-6);
    response->dy = 0.0F;
    response->dyaw = 0.0F;
}

static void follow_inputs(pp_lcc_inputs_t *in, unsigned k, bool lines)
{
    const uint64_t t = T0 + ((uint64_t)k * PP_PLANNER_PERIOD_US);
    fresh_chassis(in, t);
    fresh_requests(in);
    in->speed.message.speed_mps = (float)FOLLOW_SPEED;
    if (!lines) {
        set_lines_lost(in);
    } else {
        in->lane_model.message.lines[1].status = PP_LINE_STATUS_MEASURED;
        in->lane_model.message.lines[2].status = PP_LINE_STATUS_MEASURED;
    }
    set_plan(in, (float)FOLLOW_SPEED, 0.0F);
    in->longitudinal_plan.message.target_id = 7U;
    in->lead_target.present = true;
    in->lead_target.rx_us = t;
    in->lead_target.message.header.stamp_us = t;
    in->lead_target.message.header.valid = true;
    in->lead_target.message.header.frame_id = PP_FRAME_ID_BASE_LINK;
    in->lead_target.message.id = 7U;
    in->lead_target.message.classification = PP_LEAD_CLASS_CAR;
    in->lead_target.message.x = 25.0F;
    in->lead_target.message.y = 0.3F;
    in->lead_target.message.gap = 20.0F;
    in->lead_target.message.existence_probability = 0.95F;
}

static void test_follow_the_lead_when_both_lines_are_lost(void)
{
    pp_lcc_outputs_t out;
    pp_lcc_inputs_t in = inputs();
    PP_CHECK(pp_lcc_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
    unsigned k = 0U;
    for (; k < 40U; k++) {
        follow_inputs(&in, k, true);
        step(&in, ego_motion_slow, &out);
        PP_CHECK(out.lcc_status.lcc_mode == PP_LCC_MODE_LANE);
    }
    follow_inputs(&in, k++, false);
    step(&in, ego_motion_slow, &out);
    PP_CHECK(out.lcc_status.path_valid && out.trajectory.header.valid);
    PP_CHECK(out.lcc_status.lcc_mode == PP_LCC_MODE_FOLLOW);
    PP_CHECK(out.trajectory.planner_id == PP_PLANNER_ID_LCC);
    PP_CHECK(out.trajectory.observed_horizon_s > 1.5F && out.trajectory.observed_horizon_s < 2.6F);
    PP_CHECK_NEAR(out.trajectory.points[0].pose.y, 0.0, 0.05);
    PP_CHECK(out.trajectory.points[30].pose.y > 0.0F);

    float last_distance = out.lcc_status.follow_distance;
    for (unsigned n = 0U; n < 20U; n++, k++) {
        follow_inputs(&in, k, false);
        step(&in, ego_motion_slow, &out);
        PP_CHECK(out.lcc_status.lcc_mode == PP_LCC_MODE_FOLLOW);
        PP_CHECK(out.lcc_status.follow_distance > last_distance);
        last_distance = out.lcc_status.follow_distance;
    }

    follow_inputs(&in, k++, false);
    in.lead_target.message.id = 9U;
    in.longitudinal_plan.message.target_id = 9U;
    step(&in, ego_motion_slow, &out);
    PP_CHECK(out.lcc_status.lcc_mode != PP_LCC_MODE_FOLLOW);
    PP_CHECK(out.lcc_status.lcc_mode == PP_LCC_MODE_COAST && out.lcc_status.path_valid);

    follow_inputs(&in, k++, true);
    step(&in, ego_motion_slow, &out);
    PP_CHECK(out.lcc_status.lcc_mode == PP_LCC_MODE_LANE);
}

static void test_no_follow_when_a_condition_fails(void)
{
    for (unsigned c = 0U; c < 4U; c++) {
        pp_lcc_outputs_t out;
        pp_lcc_inputs_t in = inputs();
        PP_CHECK(pp_lcc_init(memory, sizeof(memory), &VP0) == PP_INIT_RESULT_OK);
        unsigned k = 0U;
        for (; k < 40U; k++) {
            follow_inputs(&in, k, true);
            step(&in, ego_motion_slow, &out);
        }
        follow_inputs(&in, k, false);
        if (c == 0U) { in.lead_target.message.classification = PP_LEAD_CLASS_MOTORCYCLE; }
        if (c == 1U) { in.lead_target.message.gap = 60.0F; }
        if (c == 2U) { in.longitudinal_plan.message.target_id = 8U; }
        if (c == 3U) { in.speed.message.speed_mps = 17.0F; }
        step(&in, ego_motion_slow, &out);
        PP_CHECK(out.lcc_status.lcc_mode != PP_LCC_MODE_FOLLOW);
    }
}

int main(void)
{
    test_driver_override_path_starts_at_car();
    test_lka_request_makes_the_lcc_path_start_at_the_car();
    test_lcc_mode_follows_the_state_of_the_lane();
    test_follow_the_lead_when_both_lines_are_lost();
    test_no_follow_when_a_condition_fails();
    test_lcc_path_from_car_to_centre();
    test_no_lane_model_means_no_path();
    test_stale_lane_model();
    test_lcc_not_requested();
    test_function_requests_timeout_and_recovery();
    test_chassis_fault_invalidates_lcc_and_fresh_inputs_restore_it();
    test_longitudinal_plan_range();
    return PP_TEST_RESULT();
}

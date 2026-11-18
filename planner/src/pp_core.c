/* Core shared by the two planners (pp_core.h). */

#include "pp_core.h"

#include <math.h>
#include <string.h>

#include "latency.h"
#include "output.h"
#include "pp_math.h"

static bool positive_finite(float value)
{
    return isfinite(value) && (value > 0.0F);
}

/* Interface Control Document 5.8; PP-ASM-016 (width including mirrors). */
bool pp_core_vehicle_config_valid(const pp_vehicle_config_t *cfg)
{
    bool ok = positive_finite(cfg->wheelbase)
           && positive_finite(cfg->vehicle_width)
           && positive_finite(cfg->steering_ratio)
           && positive_finite(cfg->max_wheel_angle)
           && positive_finite(cfg->max_steering_wheel_rate);
    ok = ok && isfinite(cfg->rear_axle_to_cg)
            && (cfg->rear_axle_to_cg >= 0.0F)
            && (cfg->rear_axle_to_cg <= cfg->wheelbase);
    ok = ok && (cfg->vehicle_width <= PP_MAX_VEHICLE_WIDTH_M);
    ok = ok && isfinite(cfg->actuator_delay) && (cfg->actuator_delay >= 0.0F);
    return ok;
}

pp_init_result_t pp_core_init(void *state, size_t state_size, size_t needed, uint32_t magic,
                              const pp_vehicle_config_t *vehicle_config)
{
    pp_init_result_t result = PP_INIT_RESULT_OK;
    if ((state == NULL) || (state_size < needed)
        || (((uintptr_t)state % PP_STATE_ALIGNMENT) != 0U)) {
        result = PP_INIT_RESULT_BAD_ARGUMENT;
    } else {
        (void)memset(state, 0, needed);
        pp_core_state_t *core = (pp_core_state_t *)state;
        core->magic = magic;
        core->cal = &pp_calibration;
        pp_reference_memory_reset(&core->ref_mem);

        if ((vehicle_config == NULL) || !pp_core_vehicle_config_valid(vehicle_config)) {
            result = PP_INIT_RESULT_BAD_VEHICLE_CONFIG; /* PP-SWR-146 */
        } else if (!pp_calibration_check(core->cal)) {
            result = PP_INIT_RESULT_BAD_CALIBRATION;    /* Software Detailed Design section 3 */
        } else {
            core->vehicle = *vehicle_config;
            core->initialized = true;
        }
    }
    return result;
}

pp_core_state_t *pp_core_prepared(void *state, uint32_t magic)
{
    pp_core_state_t *result = NULL;
    if (state != NULL) {
        pp_core_state_t *core = (pp_core_state_t *)state;
        if (core->magic == magic) {
            result = core;
        }
    }
    return result;
}

uint8_t pp_core_next_counter(uint8_t *counter)
{
    const uint8_t value = *counter;
    *counter = (uint8_t)((value + 1U) % PP_COUNTER_MODULO);
    return value;
}

/* Interface Control Document 5.7: every v in 0 to V_MAX and every a within +-A_MAX (PP-SWR-156). */
static bool longitudinal_plan_in_range(const pp_longitudinal_plan_t *plan)
{
    bool ok = true;
    for (uint32_t i = 0U; ok && (i < PP_LONGITUDINAL_PLAN_POINTS); i++) {
        const float v = plan->points[i].v;
        const float a = plan->points[i].a;
        ok = isfinite(v) && (v >= 0.0F) && (v <= PP_LONGITUDINAL_PLAN_V_MAX_MPS)
             && isfinite(a) && (fabsf(a) <= PP_LONGITUDINAL_PLAN_A_MAX_MPS2);
    }
    return ok;
}

/* The held message is older than the receive timeout, or none is held (ICD 4). */
static bool timed_out(const bool *present, uint64_t rx_us, uint64_t t0_us, uint64_t timeout_us)
{
    return !*present || ((rx_us <= t0_us) && ((t0_us - rx_us) > timeout_us));
}

void pp_core_hold_inputs(pp_core_state_t *core, const pp_common_inputs_t *in)
{
    pp_held_inputs_t *h = &core->held;
    const uint64_t t0 = in->t0_us;
    if ((in->lane_model != NULL)
        && pp_counter_accept(&h->lane_model_check, in->lane_model->present, in->lane_model->rx_us,
                             in->lane_model->message.header.counter,
                             in->lane_model->message.header.valid, PP_LANE_MODEL_MAX_DELTA_COUNTER,
                             timed_out(&h->lane_model.present, h->lane_model.rx_us, t0,
                                       PP_LANE_MODEL_TIMEOUT_US))) {
        h->lane_model = *in->lane_model;
    }
    if ((in->object_list != NULL)
        && pp_counter_accept(&h->object_list_check, in->object_list->present, in->object_list->rx_us,
                             in->object_list->message.header.counter,
                             in->object_list->message.header.valid, PP_OBJECT_LIST_MAX_DELTA_COUNTER,
                             timed_out(&h->object_list.present, h->object_list.rx_us, t0,
                                       PP_OBJECT_LIST_TIMEOUT_US))) {
        h->object_list = *in->object_list;
    }
    if ((in->lead_target != NULL)
        && pp_counter_accept(&h->lead_target_check, in->lead_target->present, in->lead_target->rx_us,
                             in->lead_target->message.header.counter,
                             in->lead_target->message.header.valid, PP_LEAD_TARGET_MAX_DELTA_COUNTER,
                             timed_out(&h->lead_target.present, h->lead_target.rx_us, t0,
                                       PP_LEAD_TARGET_TIMEOUT_US))) {
        h->lead_target = *in->lead_target;
    }
    if ((in->vehicle_state != NULL)
        && pp_counter_accept(&h->vehicle_state_check, in->vehicle_state->present,
                             in->vehicle_state->rx_us, in->vehicle_state->message.header.counter,
                             in->vehicle_state->message.header.valid,
                             PP_VEHICLE_STATE_MAX_DELTA_COUNTER,
                             timed_out(&h->vehicle_state.present, h->vehicle_state.rx_us, t0,
                                       PP_VEHICLE_STATE_TIMEOUT_US))) {
        h->vehicle_state = *in->vehicle_state;
    }
    if ((in->function_requests != NULL)
        && pp_counter_accept(&h->function_requests_check, in->function_requests->present,
                             in->function_requests->rx_us,
                             in->function_requests->message.header.counter,
                             in->function_requests->message.header.valid,
                             PP_FUNCTION_REQUESTS_MAX_DELTA_COUNTER,
                             timed_out(&h->function_requests.present, h->function_requests.rx_us, t0,
                                       PP_FUNCTION_REQUESTS_TIMEOUT_US))) {
        h->function_requests = *in->function_requests;
    }
    if ((in->longitudinal_plan != NULL)
        && pp_counter_accept(&h->longitudinal_plan_check, in->longitudinal_plan->present,
                             in->longitudinal_plan->rx_us,
                             in->longitudinal_plan->message.header.counter,
                             in->longitudinal_plan->message.header.valid,
                             PP_LONGITUDINAL_PLAN_MAX_DELTA_COUNTER,
                             timed_out(&h->longitudinal_plan.present, h->longitudinal_plan.rx_us, t0,
                                       PP_LONGITUDINAL_PLAN_TIMEOUT_US))) {
        h->longitudinal_plan = *in->longitudinal_plan;
    }
}

void pp_core_check_inputs(const pp_core_state_t *core, const pp_common_inputs_t *in,
                          pp_usable_inputs_t *out)
{
    const uint64_t t0 = in->t0_us;
    const pp_held_inputs_t *h = &core->held;
    (void)memset(out, 0, sizeof(*out));

    if (pp_input_usable(h->lane_model.present, h->lane_model.message.header.valid,
                        h->lane_model.rx_us, h->lane_model.message.header.stamp_us, t0,
                        PP_LANE_MODEL_TIMEOUT_US, PP_LANE_MODEL_MAX_AGE_US)) {
        out->lane_model = &h->lane_model.message;
    }
    if ((in->object_list != NULL)
        && pp_input_usable(h->object_list.present, h->object_list.message.header.valid,
                           h->object_list.rx_us, h->object_list.message.header.stamp_us, t0,
                           PP_OBJECT_LIST_TIMEOUT_US, PP_OBJECT_LIST_MAX_AGE_US)) {
        out->object_list = &h->object_list.message;
    }
    if ((in->lead_target != NULL)
        && pp_input_usable(h->lead_target.present, h->lead_target.message.header.valid,
                           h->lead_target.rx_us, h->lead_target.message.header.stamp_us, t0,
                           PP_LEAD_TARGET_TIMEOUT_US, PP_LEAD_TARGET_MAX_AGE_US)) {
        out->lead_target = &h->lead_target.message;
    }
    if ((in->speed != NULL)
        && pp_input_usable(in->speed->present, in->speed->message.header.valid, in->speed->rx_us,
                           in->speed->message.header.stamp_us, t0, PP_SPEED_TIMEOUT_US,
                           PP_NO_AGE_LIMIT)
        && (isfinite(in->speed->message.speed_mps) != 0)) {
        out->speed = &in->speed->message;
    }
    if ((in->imu != NULL)
        && pp_input_usable(in->imu->present, in->imu->message.header.valid, in->imu->rx_us,
                           in->imu->message.header.stamp_us, t0, PP_IMU_TIMEOUT_US,
                           PP_NO_AGE_LIMIT)
        && (isfinite(in->imu->message.yaw_rate_rps) != 0)) {
        out->imu = &in->imu->message;
    }
    if ((in->steering != NULL)
        && pp_input_usable(in->steering->present, in->steering->message.header.valid,
                           in->steering->rx_us, in->steering->message.header.stamp_us, t0,
                           PP_STEERING_TIMEOUT_US, PP_NO_AGE_LIMIT)
        && isfinite(in->steering->message.steering_wheel_angle_rad)) {
        out->steering = &in->steering->message;
    }
    if (pp_input_usable(h->vehicle_state.present, h->vehicle_state.message.header.valid,
                        h->vehicle_state.rx_us, h->vehicle_state.message.header.stamp_us, t0,
                        PP_VEHICLE_STATE_TIMEOUT_US, PP_VEHICLE_STATE_MAX_AGE_US)
        && (isfinite(h->vehicle_state.message.lateral_velocity) != 0)) {
        out->vehicle_state = &h->vehicle_state.message;
    }
    if (pp_input_usable(h->function_requests.present, h->function_requests.message.header.valid,
                        h->function_requests.rx_us, h->function_requests.message.header.stamp_us, t0,
                        PP_FUNCTION_REQUESTS_TIMEOUT_US, PP_FUNCTION_REQUESTS_MAX_AGE_US)) {
        out->function_requests = &h->function_requests.message;
        out->requests_rx_us = h->function_requests.rx_us;
    }
    if (pp_input_usable(h->longitudinal_plan.present, h->longitudinal_plan.message.header.valid,
                        h->longitudinal_plan.rx_us, h->longitudinal_plan.message.header.stamp_us, t0,
                        PP_LONGITUDINAL_PLAN_TIMEOUT_US, PP_LONGITUDINAL_PLAN_MAX_AGE_US)
        && longitudinal_plan_in_range(&h->longitudinal_plan.message)) {
        out->longitudinal_plan = &h->longitudinal_plan.message; /* else PP-SWR-154 fallback */
    }
}

void pp_core_check_requests_timeout(pp_core_state_t *core, uint64_t t0_us, pp_usable_inputs_t *out)
{
    if (!core->requests_clock_set) {
        core->requests_clock_set = true;
        core->last_requests_us = t0_us;
        if (core->held.function_requests.present && (core->held.function_requests.rx_us <= t0_us)) {
            core->last_requests_us = core->held.function_requests.rx_us;
        }
    }
    if ((out->function_requests != NULL) && (out->requests_rx_us <= t0_us)
        && (out->requests_rx_us >= core->last_requests_us)) {
        core->last_requests_us = out->requests_rx_us;
    }
    out->requests_timed_out = (t0_us >= core->last_requests_us)
        && ((t0_us - core->last_requests_us) > PP_FUNCTION_REQUESTS_TIMEOUT_US);       /* PP-SWR-145 */
}

bool pp_core_motion_to_t0(uint64_t capture_us, uint64_t t0_us, pp_ego_motion_fn ego_motion,
                          void *context, pp_motion_t *motion)
{
    bool ok = true;
    (void)memset(motion, 0, sizeof(*motion));
    if (capture_us < t0_us) {
        const pp_ego_motion_request_t request = {capture_us, t0_us};
        pp_ego_motion_response_t response;
        (void)memset(&response, 0, sizeof(response));
        ok = (ego_motion != NULL);
        if (ok) {
            ego_motion(context, &request, &response);
            ok = response.valid && (isfinite(response.dx) != 0) && (isfinite(response.dy) != 0)
                 && (isfinite(response.dyaw) != 0);
        }
        if (ok) {
            motion->dx = (double)response.dx;
            motion->dy = (double)response.dy;
            motion->dyaw = (double)response.dyaw;
        }
    }
    /* A stamp slightly ahead of t0 (input check tolerance) is used without moving. */
    return ok;
}

/* Ego-motion since the previous cycle, for the T2 memory and the T5 prior. */
static bool cycle_motion(pp_core_state_t *s, uint64_t t0_us, pp_ego_motion_fn ego_motion,
                         void *context, pp_motion_t *motion)
{
    bool ok = s->has_prev_t0 && (s->prev_t0_us < t0_us)
              && ((t0_us - s->prev_t0_us) <= PP_EGO_MOTION_WINDOW_US);
    if (ok) {
        ok = pp_core_motion_to_t0(s->prev_t0_us, t0_us, ego_motion, context, motion);
    }
    s->prev_t0_us = t0_us;
    s->has_prev_t0 = true;
    return ok;
}

/* T5 on a reference line from T2 (not while coasting): fused curvature replaces c2, c3. */
static void fuse_curvature(pp_core_state_t *s, const pp_usable_inputs_t *in, double ds, double v,
                           pp_reference_line_t *ref)
{
    const pp_calibration_t *cal = s->cal;
    pp_curvature_predict(&s->curv, ds, cal);
    const uint64_t stamp = in->lane_model->header.stamp_us;
    if (!s->t5_has_stamp || (stamp != s->t5_stamp_us)) {          /* new frame only */
        pp_curvature_update_camera(&s->curv, &ref->centre, ref->var_c2, ref->var_c3,
                                   fmax(ref->view_start, 0.0), ref->view_end, cal);
        s->t5_stamp_us = stamp;
        s->t5_has_stamp = true;
    }
    if (in->imu != NULL) {
        pp_curvature_update_yaw(&s->curv, (double)in->imu->yaw_rate_rps, v, cal);
    }
    double c2 = 0.0;
    double c3 = 0.0;
    if (pp_curvature_fit(&s->curv, ref->view_end, &c2, &c3)) {
        ref->centre.c[2] = c2;
        ref->centre.c[3] = c3;
        s->ref_mem.ref_centre.c[2] = c2;        /* coasting continues on the fused line */
        s->ref_mem.ref_centre.c[3] = c3;
#ifdef PP_REF_SAMPLED
        pp_ref_sample_cubic(ref);
#endif
    }
}

void pp_core_frame(pp_core_state_t *core, const pp_usable_inputs_t *in, uint64_t t0_us,
                   pp_ego_motion_fn ego_motion, void *context, pp_frame_t *f)
{
    pp_motion_t to_t0;
    (void)memset(f, 0, sizeof(*f));
    f->moved = cycle_motion(core, t0_us, ego_motion, context, &f->since_last);
    pp_stitch_move_old(&core->prev_path, t0_us, ego_motion, context, &f->old);         /* T4 step 1 */

    /* PP-SWR-142: all three chassis signals must be usable to publish a path. */
    f->forward = (in->speed != NULL) && (in->speed->direction == PP_DIRECTION_FORWARD);
    f->chassis_valid = f->forward && (in->imu != NULL) && (in->steering != NULL);
    if (!f->forward) {
        pp_reference_memory_reset(&core->ref_mem);
        pp_curvature_reset(&core->curv);
        return;
    }
    f->dt = (double)PP_PLANNER_PERIOD_US / PP_US_PER_S;
    f->v = (double)in->speed->speed_mps;
    f->v_y = (in->vehicle_state != NULL) ? (double)in->vehicle_state->lateral_velocity : 0.0;
    f->yaw_rate = (in->imu != NULL) ? (double)in->imu->yaw_rate_rps : 0.0;

    /* T1: a lane model that is not usable counts as no boundary at all (T2 coasts). */
    f->lane_ok = (in->lane_model != NULL)
        && pp_core_motion_to_t0(in->lane_model->header.stamp_us, t0_us, ego_motion, context, &to_t0);
    if (f->lane_ok) {
        pp_latency_compensate(in->lane_model, &to_t0, &f->lane);
    } else {
        pp_lane_empty(&f->lane);
    }
    pp_reference_line_update(&core->ref_mem, &f->lane, f->moved ? &f->since_last : NULL, core->cal,
                             (double)core->vehicle.vehicle_width, f->dt, &f->ref);  /* T2 */
    f->camera_ref = f->ref;                                   /* before T5, for T10 steps 3, 4 */
    const double ds = f->moved ? f->since_last.dx : (f->v * f->dt);
    if (f->ref.valid && !f->ref.coasting && f->lane_ok) {
        fuse_curvature(core, in, ds, f->v, &f->ref);          /* T5 */
    } else if (!f->ref.valid) {
        pp_curvature_reset(&core->curv);
    } else {
        pp_curvature_predict(&core->curv, ds, core->cal);
    }
}

pp_lateral_state_t pp_core_measure_lateral(const pp_reference_line_t *ref, double v, double v_y,
                                           double yaw_rate)
{
    pp_ref_walker_t walker;
    pp_ref_point_t foot;
    pp_lateral_state_t state;
    pp_ref_walk_begin(&walker, ref, &foot);
    pp_lateral_state(&foot, v, v_y, yaw_rate, &state);
    return state;
}

double pp_core_continuity_limit(const pp_reference_line_t *ref)
{
    return (ref->valid && !ref->coasting) ? ref->view_end : INFINITY;
}

float pp_core_observed_horizon(const pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],
                               const pp_reference_line_t *ref)
{
    double horizon = 0.0;
    if (ref->valid) {
        horizon = (double)points[PP_TRAJECTORY_POINTS - 1U].time_from_start;
        for (uint32_t k = 1U; k < PP_TRAJECTORY_POINTS; k++) {
            const double x0 = (double)points[k - 1U].pose.x;
            const double x1 = (double)points[k].pose.x;
            if (x1 > ref->view_end) {
                const double f = (x1 > x0) ? pp_clamp((ref->view_end - x0) / (x1 - x0), 0.0, 1.0) : 0.0;
                const double t0 = (double)points[k - 1U].time_from_start;
                horizon = (x0 > ref->view_end) ? t0
                          : t0 + (f * ((double)points[k].time_from_start - t0));
                break;
            }
        }
    }
    return (float)horizon;
}

void pp_core_publish_trajectory(pp_core_state_t *core, uint64_t t0_us, bool valid,
                                const pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],
                                const pp_reference_line_t *ref, pp_planner_id_t planner,
                                pp_trajectory_t *out)
{
    out->header.stamp_us = t0_us;                                          /* PP-SWR-012 */
    out->header.counter = pp_core_next_counter(&core->trajectory_counter);
    out->header.valid = valid;
    out->header.frame_id = PP_FRAME_ID_BASE_LINK;
    out->planner_id = planner;                                             /* PP-SWR-019 */
    if (valid) {
        (void)memcpy(out->points, points, sizeof(out->points));
        out->observed_horizon_s = pp_core_observed_horizon(points, ref);
    } else {
        pp_output_empty_points(out->points);
        out->observed_horizon_s = 0.0F;
    }
    pp_stitch_remember(&core->prev_path, t0_us, valid, out->points);      /* for T4 */
}

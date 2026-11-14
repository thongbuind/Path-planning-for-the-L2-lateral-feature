/*
 * Public entry points of the path planner (interfaces/c/pp_planner.h).
 *
 * One cycle (Software Architectural Design 3.2) runs the units of the Software
 * Detailed Design in this order: T1 input check and latency compensation, T2
 * reference line, T5 curvature fusion, T6 lateral state, T9 arbitration,
 * T4 stitching, T7/T8 path generation, T10 feasibility and T11 output.
 */

#include <math.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "arbitration.h"
#include "curvature.h"
#include "feasibility.h"
#include "generators/qp.h"
#include "generators/quintic.h"
#include "input_check.h"
#include "intervention.h"
#include "lateral_state.h"
#include "offset.h"
#include "latency.h"
#include "output.h"
#include "pp_build_info.h"
#include "pp_calibration.h"
#include "pp_path.h"
#include "pp_planner.h"
#include "pp_state.h"
#include "reference_line.h"
#include "stitching.h"

_Static_assert(_Alignof(pp_state_t) <= PP_STATE_ALIGNMENT,
               "pp_state_t needs more alignment than PP_STATE_ALIGNMENT");

#define PP_US_PER_S (1.0e6)

static bool positive_finite(float value)
{
    return isfinite(value) && (value > 0.0F);
}

/* Interface Control Document 5.8; PP-ASM-016 (width including mirrors). */
static bool vehicle_config_valid(const pp_vehicle_config_t *cfg)
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

/* State memory that pp_init has set up, whether or not initialisation succeeded. */
static pp_state_t *prepared_state(void *state)
{
    pp_state_t *result = NULL;
    if (state != NULL) {
        pp_state_t *s = (pp_state_t *)state;
        if (s->magic == PP_STATE_MAGIC) {
            result = s;
        }
    }
    return result;
}

static uint8_t next_counter(uint8_t *counter)
{
    uint8_t value = *counter;
    *counter = (uint8_t)((value + 1U) % PP_COUNTER_MODULO);
    return value;
}

size_t pp_state_size(void)
{
    return sizeof(pp_state_t);
}

const char *pp_version(void)
{
    return PP_BUILD_INFO;
}

pp_init_result_t pp_init(void *state, size_t state_size,
                         const pp_vehicle_config_t *vehicle_config)
{
    pp_init_result_t result = PP_INIT_RESULT_OK;

    if ((state == NULL) || (state_size < sizeof(pp_state_t))
        || (((uintptr_t)state % PP_STATE_ALIGNMENT) != 0U)) {
        result = PP_INIT_RESULT_BAD_ARGUMENT;
    } else {
        pp_state_t *s = (pp_state_t *)state;
        (void)memset(s, 0, sizeof(*s));
        s->magic = PP_STATE_MAGIC;
        s->cal = &pp_calibration;
        pp_reference_memory_reset(&s->ref_mem);

        if ((vehicle_config == NULL) || !vehicle_config_valid(vehicle_config)) {
            result = PP_INIT_RESULT_BAD_VEHICLE_CONFIG; /* PP-SWR-146 */
        } else if (!pp_calibration_check(s->cal)) {
            result = PP_INIT_RESULT_BAD_CALIBRATION;    /* Software Detailed Design section 3 */
        } else {
            s->vehicle = *vehicle_config;
            s->initialized = true;
        }
    }
    return result;
}

/* Newest message of each input that passed the input check, or NULL. */
typedef struct {
    const pp_lane_model_t *lane_model;
    const pp_object_list_t *object_list;
    const pp_speed_signals_t *speed;
    const pp_imu_signals_t *imu;
    const pp_steering_signals_t *steering;
    const pp_vehicle_state_estimate_t *vehicle_state;
    const pp_function_requests_t *function_requests;
    uint64_t requests_rx_us;
    bool requests_timed_out;
    const pp_longitudinal_plan_t *longitudinal_plan;
} pp_usable_inputs_t;

static void check_inputs(const pp_planner_inputs_t *in, pp_usable_inputs_t *out)
{
    const uint64_t t0 = in->t0_us;
    (void)memset(out, 0, sizeof(*out));

    if (pp_input_usable(in->lane_model.present, in->lane_model.message.header.valid,
                        in->lane_model.rx_us, in->lane_model.message.header.stamp_us, t0,
                        PP_LANE_MODEL_TIMEOUT_US, PP_LANE_MODEL_MAX_AGE_US)) {
        out->lane_model = &in->lane_model.message;
    }
    if (pp_input_usable(in->object_list.present, in->object_list.message.header.valid,
                        in->object_list.rx_us, in->object_list.message.header.stamp_us, t0,
                        PP_OBJECT_LIST_TIMEOUT_US, PP_OBJECT_LIST_MAX_AGE_US)) {
        out->object_list = &in->object_list.message;
    }
    if (pp_input_usable(in->speed.present, in->speed.message.header.valid, in->speed.rx_us,
                        in->speed.message.header.stamp_us, t0, PP_SPEED_TIMEOUT_US,
                        PP_NO_AGE_LIMIT)
        && (isfinite(in->speed.message.speed_mps) != 0)) {
        out->speed = &in->speed.message;
    }
    if (pp_input_usable(in->imu.present, in->imu.message.header.valid, in->imu.rx_us,
                        in->imu.message.header.stamp_us, t0, PP_IMU_TIMEOUT_US,
                        PP_NO_AGE_LIMIT)
        && (isfinite(in->imu.message.yaw_rate_rps) != 0)) {
        out->imu = &in->imu.message;
    }
    if (pp_input_usable(in->steering.present, in->steering.message.header.valid, in->steering.rx_us,
                        in->steering.message.header.stamp_us, t0, PP_STEERING_TIMEOUT_US,
                        PP_NO_AGE_LIMIT) && isfinite(in->steering.message.steering_wheel_angle_rad)) {
        out->steering = &in->steering.message;
    }
    if (pp_input_usable(in->vehicle_state.present, in->vehicle_state.message.header.valid,
                        in->vehicle_state.rx_us, in->vehicle_state.message.header.stamp_us, t0,
                        PP_VEHICLE_STATE_TIMEOUT_US, PP_VEHICLE_STATE_MAX_AGE_US)
        && (isfinite(in->vehicle_state.message.lateral_velocity) != 0)) {
        out->vehicle_state = &in->vehicle_state.message;
    }
    if (pp_input_usable(in->function_requests.present,
                        in->function_requests.message.header.valid,
                        in->function_requests.rx_us,
                        in->function_requests.message.header.stamp_us, t0,
                        PP_FUNCTION_REQUESTS_TIMEOUT_US, PP_FUNCTION_REQUESTS_MAX_AGE_US)) {
        out->function_requests = &in->function_requests.message;
        out->requests_rx_us = in->function_requests.rx_us;
    }
    if (pp_input_usable(in->longitudinal_plan.present,
                        in->longitudinal_plan.message.header.valid,
                        in->longitudinal_plan.rx_us,
                        in->longitudinal_plan.message.header.stamp_us, t0,
                        PP_LONGITUDINAL_PLAN_TIMEOUT_US, PP_LONGITUDINAL_PLAN_MAX_AGE_US)
        && longitudinal_plan_in_range(&in->longitudinal_plan.message)) {
        out->longitudinal_plan = &in->longitudinal_plan.message; /* else PP-SWR-154 fallback */
    }
}

static void check_requests_timeout(pp_state_t *s, const pp_planner_inputs_t *in, pp_usable_inputs_t *out)
{
    const uint64_t now = in->t0_us;
    if (!s->requests_clock_set) {
        s->requests_clock_set = true;
        s->last_requests_us = now;
        if (in->function_requests.present && in->function_requests.message.header.valid
            && (in->function_requests.rx_us <= now)) {
            s->last_requests_us = in->function_requests.rx_us;
        }
    }
    if ((out->function_requests != NULL) && (out->requests_rx_us <= now)
        && (out->requests_rx_us >= s->last_requests_us)) {
        s->last_requests_us = out->requests_rx_us;
    }
    out->requests_timed_out = (now >= s->last_requests_us)
        && ((now - s->last_requests_us) > PP_FUNCTION_REQUESTS_TIMEOUT_US);       /* PP-SWR-145 */
}

/* T1 step 2: motion from lane model capture to t0. False when not available (PP-SWR-143). */
static bool motion_to_t0(uint64_t capture_us, uint64_t t0_us, pp_ego_motion_fn ego_motion,
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

typedef struct {
    bool path_valid;
    pp_reference_line_t ref;
    pp_trajectory_point_t points[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
    pp_arbitration_t arbitration;
    double ay_need_max;                    /* T10 step 1, for lateral_limit_reached */
    double ay_limit;
    bool intervention_limited;
    pp_curve_limit_t curve;                /* T10 step 4, for LateralLimits */
} pp_cycle_result_t;

/* Software Architectural Design 9. */
static const pp_function_limits_t PP_HWA_LIMITS = {PP_AYSMAX, PP_JERK_MAX_HWA, 0.0};
static const pp_function_limits_t PP_LKA_LIMITS = {PP_AY_MAX_LKA, PP_JERK_MAX_LKA, PP_AY_ADD_MAX_LKA};
static const pp_function_limits_t PP_ELK_LIMITS = {PP_AY_MAX_ELK, PP_JERK_MAX_ELK, PP_AY_ADD_MAX_ELK};

#define PP_T_STEP_S (0.25)                 /* T7 A: duration step (Software Detailed Design 10) */
#define PP_T_MAX_STEPS (32U)               /* Bounds the loop whatever T_max is */

/*
 * T7 technique A and T11: quintic to the centre in T_hwa (T_recenter while recentering);
 * while the path misses the HWA targets (ay_add_max_hwa, jerk_target_hwa) the duration
 * grows by 0.25 s up to T_max.
 */

/*
 * HWA "đưa về giữa" (Software Detailed Design 10): starts when HWA is requested and was
 * not driving in the previous cycle; ends when the car is within recenter_done of the
 * centre or HWA leaves REQUEST.
 */
static void update_recentering(pp_state_t *s, const pp_function_requests_t *requests,
                               double measured_d)
{
    const bool requested = (requests != NULL)
        && (requests->requests[PP_FUNCTION_HWA].state == PP_REQUEST_STATE_REQUEST);
    if (!requested) {
        s->recentering = false;
    } else if (s->last_active != PP_ACTIVE_FUNCTION_HWA) {
        s->recentering = true;
    } else {
        /* HWA keeps driving: recentering continues until the car is centred. */
    }
    if (s->recentering && (fabs(measured_d) <= (double)s->cal->recenter_done)) {
        s->recentering = false;
    }
}
#ifndef PP_T7_QP
static bool generate_hwa(const pp_state_t *s, const pp_reference_line_t *ref,
                         const pp_lateral_state_t *start, const pp_speed_profile_t *speed,
                         double d_target,
                         pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],
                         pp_ref_samples_t *samples)
{
    const pp_calibration_t *cal = s->cal;
    const double wheelbase = (double)s->vehicle.wheelbase;
    /* Software Detailed Design 10: T_recenter while bringing the car back, else T_hwa. */
    double duration = s->recentering ? (double)cal->T_recenter : (double)cal->T_hwa;
    bool ok = false;
    bool done = false;

    for (uint32_t i = 0U; (i < PP_T_MAX_STEPS) && !done; i++) {
        pp_lateral_path_t lateral;
        pp_path_check_t check;
        ok = pp_generate_quintic(start, d_target, duration, &lateral)
             && pp_output_points(ref, &lateral, speed, wheelbase, points, samples);
        done = !ok;
        if (ok) {
            pp_feasibility_check(points, samples, &check);
            const bool targets_met = (check.ay_add_max <= (double)cal->ay_add_max_hwa)
                                     && (check.jerk_max <= (double)cal->jerk_target_hwa);
            done = targets_met || ((duration + PP_T_STEP_S) > ((double)cal->T_max + 1.0e-9));
            duration += PP_T_STEP_S;
        }
    }
    return ok;
}
#else
/*
 * T7 technique C and T11 (generators/qp.h): one QP per cycle. Corridor from the lane width
 * this cycle; continuity with the previous path whenever T4 started from it, at the points
 * of the old path within the observed range of the new reference line.
 */
static bool generate_hwa_qp(pp_state_t *s, const pp_reference_line_t *ref,
                            const pp_lateral_state_t *start, const pp_speed_profile_t *speed,
                            const pp_old_path_t *old, bool from_old, double d_target,
                            pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],
                            pp_ref_samples_t *samples)
{
    const pp_calibration_t *cal = s->cal;
    pp_qp_problem_t pb;
    pp_lateral_path_t lateral;
    pp_ref_walker_t walker;
    pp_ref_point_t r;
    (void)memset(&pb, 0, sizeof(pb));
    pb.start = *start;
    pb.d_target = d_target;
    pb.ay_limit = PP_AYSMAX * (double)cal->qp_ay_margin;
    pb.jerk_limit = 0.9 * PP_JERK_MAX_HWA;                  /* margin for T10, PP-SWR-003 */
    const double half = fmax(0.0, (0.5 * ref->width) - (0.5 * (double)s->vehicle.vehicle_width)
                                  - (double)cal->qp_corridor_margin);
    pp_ref_walk_begin(&walker, ref, &r);
    for (size_t k = 0U; k < PP_QP_N; k++) {
        const size_t idx = k + 1U;
        pp_ref_walk_to(&walker, speed->s[idx], &r);
        pb.v[k] = speed->v[idx];
        pb.kappa[k] = r.kappa;
        pb.dkappa[k] = r.dkappa;
        pb.d_max[k] = half;
        pb.d_min[k] = -half;
        pp_path_sample_t sample;
        if (from_old && old->valid && pp_stitch_sample_old(old, (double)idx * PP_GRID_STEP_S, &sample)
            && (sample.x <= ref->view_end)) {
            pp_ref_point_t foot;
            pp_ref_project(ref, sample.x, sample.y, &foot, &pb.d_old[k]);
            pb.has_old[k] = isfinite(pb.d_old[k]);
        }
    }
    const bool ok = pp_generate_qp(&s->qp, cal, &pb, &lateral)
                    && pp_output_points(ref, &lateral, speed, (double)s->vehicle.wheelbase, points, samples);
    if (!ok) {
        pp_qp_reset(&s->qp);
    }
    return ok;
}
#endif

/* Ego-motion since the previous cycle, for the T2 memory and the T5 prior. */
static bool cycle_motion(pp_state_t *s, uint64_t t0_us, pp_ego_motion_fn ego_motion,
                         void *context, pp_motion_t *motion)
{
    bool ok = s->has_prev_t0 && (s->prev_t0_us < t0_us)
              && ((t0_us - s->prev_t0_us) <= PP_EGO_MOTION_WINDOW_US);
    if (ok) {
        ok = motion_to_t0(s->prev_t0_us, t0_us, ego_motion, context, motion);
    }
    s->prev_t0_us = t0_us;
    s->has_prev_t0 = true;
    return ok;
}

/* T5 on a reference line from T2 (not while coasting): fused curvature replaces c2, c3. */
static void fuse_curvature(pp_state_t *s, const pp_usable_inputs_t *in, double ds, double v,
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
    }
}

static pp_lateral_state_t measure_lateral(const pp_reference_line_t *ref, double v,
                                          double v_y, double yaw_rate)
{
    pp_ref_walker_t walker;
    pp_ref_point_t foot;
    pp_lateral_state_t state;
    pp_ref_walk_begin(&walker, ref, &foot);
    pp_lateral_state(&foot, v, v_y, yaw_rate, &state);
    return state;
}

/* x up to which T4 keeps the path continuous: the observed range, or all of it while coasting. */
static double continuity_limit(const pp_reference_line_t *ref)
{
    return (ref->valid && !ref->coasting) ? ref->view_end : INFINITY;
}

/* PP-SWR-018: time on the path where it leaves the view range of its reference line. */
static float observed_horizon(const pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],
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

static void finish_intervention_path(pp_state_t *s, const pp_speed_profile_t *speed,
                                     const pp_function_limits_t *limits, const pp_old_path_t *old,
                                     bool blend, pp_cycle_result_t *out)
{
    const double wheelbase = (double)s->vehicle.wheelbase;
    if (blend) {
        (void)pp_stitch_blend(old, s->cal, wheelbase, continuity_limit(&out->ref), out->points);
    }
    out->intervention_limited = pp_feasibility_limit(out->points, &out->samples, limits, &s->vehicle);
    pp_path_check_t check;
    pp_feasibility_check(out->points, &out->samples, &check);
    out->ay_need_max = fmax(check.ay_need_max, pp_ay_need_max(&out->ref, speed));
    out->ay_limit = limits->ay_max;
    pp_curve_limit(&out->ref, out->ay_limit, &out->curve);
    out->path_valid = true;
}

static void plan_intervention(pp_state_t *s, const pp_arbitration_input_t *arb,
                              const pp_old_path_t *old, const pp_reference_line_t *ref,
                              const pp_lateral_state_t *ego, const pp_speed_profile_t *speed,
                              pp_cycle_result_t *out)
{
    const bool elk = out->arbitration.active_function == PP_ACTIVE_FUNCTION_ELK;
    const size_t function = elk ? PP_FUNCTION_ELK : PP_FUNCTION_LKA;
    const pp_function_limits_t *limits = elk ? &PP_ELK_LIMITS : &PP_LKA_LIMITS;
    bool blend = true;
    out->ref = *ref;
    if (out->arbitration.starting) {
        const pp_intervention_request_t *req = &s->arbitration.intervention[function - 1U];
        const double tlc = (double)arb->requests->requests[function].tlc;
        pp_intervention_begin(&s->intervention_path, req, tlc, arb->t0_us, ref, ego, speed,
                              limits, &s->vehicle, s->cal, elk);                   /* T7 A */
        blend = !pp_intervention_start_exception(ref, ego, old);                  /* PP-SWR-031 */
    }
    pp_lateral_path_t path;
    pp_intervention_sample(&s->intervention_path, arb->t0_us, &path);
    if (pp_output_points(ref, &path, speed, s->vehicle.wheelbase, out->points, &out->samples)) {
        finish_intervention_path(s, speed, limits, old, blend, out);
    } else {
        pp_arbitration_invalidate(&s->arbitration, &out->arbitration);
    }
}

static void plan_path(pp_state_t *s, uint64_t t0_us, const pp_usable_inputs_t *in,
                      pp_ego_motion_fn ego_motion, void *context, pp_cycle_result_t *out)
{
    pp_motion_t to_t0;
    pp_motion_t since_last;
    pp_old_path_t old;
    (void)memset(out, 0, sizeof(*out));
    out->ay_limit = PP_HWA_LIMITS.ay_max;
    pp_arbitration_input_t arb = {
        .requests = in->function_requests, .t0_us = t0_us, .requests_rx_us = in->requests_rx_us,
        .hold_s = (double)s->cal->T_end_hold,
    };
    const bool moved = cycle_motion(s, t0_us, ego_motion, context, &since_last);
    pp_stitch_move_old(&s->prev_path, t0_us, ego_motion, context, &old);         /* T4 step 1 */

    /* PP-SWR-142: all three chassis signals must be usable to publish a path. */
    const bool forward = (in->speed != NULL)
                         && (in->speed->direction == PP_DIRECTION_FORWARD);
    const bool chassis_valid = forward && (in->imu != NULL) && (in->steering != NULL);
    if (!forward) {
        pp_reference_memory_reset(&s->ref_mem);
        pp_curvature_reset(&s->curv);
        pp_qp_reset(&s->qp);
        pp_offset_reset(&s->offset);
        (void)memset(&s->edge_mem, 0, sizeof(s->edge_mem));
        s->end_velocity.valid = false;
        pp_arbitrate(&s->arbitration, &arb, &out->arbitration);
    } else {
        const double dt = (double)PP_PLANNER_PERIOD_US / PP_US_PER_S;
        const double v = (double)in->speed->speed_mps;
        const double v_y = (in->vehicle_state != NULL)
                           ? (double)in->vehicle_state->lateral_velocity : 0.0;
        const double yaw_rate = (in->imu != NULL) ? (double)in->imu->yaw_rate_rps : 0.0;
        /* PP-TS-017 (V2b, choice B). While the driver overrides, and in the first cycle after, the HWA path
         * starts at the car (T4 step 2; PP-SWR-039, 040; R79 5.6.4.3: priority to the driver).
         * The last usable FunctionRequests counts while none is usable. */
        const bool override_now = (in->function_requests != NULL)
                                  ? in->function_requests->driver_override : s->driver_override;
        const bool follow_car = override_now || s->driver_override;
        s->driver_override = override_now;
        pp_lane_at_t0_t lane;

        /* T1: a lane model that is not usable counts as no boundary at all (T2 coasts). */
        const bool lane_ok = (in->lane_model != NULL)
            && motion_to_t0(in->lane_model->header.stamp_us, t0_us, ego_motion, context, &to_t0);
        if (lane_ok) {
            pp_latency_compensate(in->lane_model, &to_t0, &lane);
        } else {
            pp_lane_empty(&lane);
        }
        pp_reference_line_update(&s->ref_mem, &lane, moved ? &since_last : NULL, s->cal,
                                 (double)s->vehicle.vehicle_width, dt, &out->ref);  /* T2 */
        const pp_reference_line_t camera_ref = out->ref;   /* before T5, for T10 steps 3, 4 */
        if (out->ref.valid && !out->ref.coasting && lane_ok) {
            fuse_curvature(s, in, moved ? since_last.dx : (v * dt), v, &out->ref);   /* T5 */
        } else if (!out->ref.valid) {
            pp_curvature_reset(&s->curv);
        } else {
            pp_curvature_predict(&s->curv, moved ? since_last.dx : (v * dt), s->cal);
        }
        pp_reference_line_t edges[PP_ROAD_EDGES] = {0};
        const pp_intervention_request_t *last_elk = &s->arbitration.intervention[PP_FUNCTION_ELK - 1U];
        const bool edge_handover = (last_elk->phase == PP_INTERVENTION_PHASE_ACTIVE)
                                   && (last_elk->reason == PP_ELK_REASON_ROAD_EDGE);
        if (edge_handover || ((arb.requests != NULL)
                            && (arb.requests->requests[PP_FUNCTION_ELK].state != PP_REQUEST_STATE_OFF))) {
            pp_road_edge_references(&s->edge_mem, &lane, &camera_ref, moved ? &since_last : NULL,
                                    &s->vehicle, s->cal, edges);                 /* PP-SWR-047 */
        } else {
            (void)memset(&s->edge_mem, 0, sizeof(s->edge_mem));
        }
        const pp_reference_line_t *refs[PP_INTERVENTIONS] = {&camera_ref, &camera_ref};
        const pp_reference_line_t *idle_edge = edges[0].valid ? &edges[0] : &edges[1];
        const bool state_valid = in->vehicle_state != NULL;
        const bool intervention_requested = arb.requests != NULL
            && ((arb.requests->requests[PP_FUNCTION_LKA].state == PP_REQUEST_STATE_REQUEST)
                || (arb.requests->requests[PP_FUNCTION_ELK].state == PP_REQUEST_STATE_REQUEST));
        const double end_v_y = pp_intervention_vy_at_t0(&s->end_velocity,
                                  intervention_requested ? in->vehicle_state : NULL, t0_us);
        arb.hwa_available = out->ref.valid;
        arb.path_available = chassis_valid && !in->requests_timed_out
                             && (arb.hwa_available || idle_edge->valid);
        if (arb.requests != NULL) {
            for (size_t i = 0U; i < PP_INTERVENTIONS; i++) {
                const pp_function_request_t *req = &arb.requests->requests[i + 1U];
                const pp_intervention_request_t *prior = &s->arbitration.intervention[i];
                const pp_side_t side = prior->requested ? prior->side : req->side;
                const pp_elk_reason_t reason = prior->requested ? prior->reason : req->elk_reason;
                const bool elk = i == (PP_FUNCTION_ELK - 1U);
                const bool edge = elk && (reason == PP_ELK_REASON_ROAD_EDGE);
                const bool has_side = (side == PP_SIDE_LEFT) || (side == PP_SIDE_RIGHT);
                if (edge) {
                    refs[i] = &edges[(side == PP_SIDE_LEFT) ? 0U : 1U];
                }
                arb.can_start[i] = chassis_valid && state_valid && has_side && (edge ? refs[i]->valid
                    : pp_intervention_line_trusted(&lane, &camera_ref, side, &s->vehicle, s->cal));
                arb.can_continue[i] = chassis_valid && has_side && refs[i]->valid && !refs[i]->inferred
                                      && (!refs[i]->coasting || old.valid);      /* PP-SWR-046, 047 */
                if (arb.can_continue[i] && state_valid && (prior->phase == PP_INTERVENTION_PHASE_ACTIVE)) {
                    const pp_lateral_state_t ego = measure_lateral(refs[i], v, end_v_y, yaw_rate);
                    arb.can_finish[i] = pp_intervention_settled(refs[i], &ego, &old, v, end_v_y, yaw_rate,
                                                               &s->vehicle, s->cal);
                }
                if (elk) {
                    arb.elk_too_late = pp_elk_past_marking(&lane, side, &s->vehicle, s->cal);
                }
            }
        }
        pp_arbitrate(&s->arbitration, &arb, &out->arbitration);
        if (!arb.path_available) {
            return;
        }
        const pp_active_function_t active = out->arbitration.active_function;
        if ((active == PP_ACTIVE_FUNCTION_LKA) || (active == PP_ACTIVE_FUNCTION_ELK)) {
            const size_t index = (active == PP_ACTIVE_FUNCTION_LKA) ? 0U : 1U;
            pp_speed_profile_t speed;
            pp_speed_profile(in->longitudinal_plan, t0_us, v, &speed);
            const pp_lateral_state_t ego = measure_lateral(refs[index], v, v_y, yaw_rate);
            plan_intervention(s, &arb, &old, refs[index], &ego, &speed, out);
            return;
        }
        if (!out->ref.valid && idle_edge->valid) {
            /* ELK can receive a valid status before its first REQUEST on an unmarked road. */
            out->ref = *idle_edge;
            pp_speed_profile_t speed;
            pp_lateral_path_t path;
            pp_speed_profile(in->longitudinal_plan, t0_us, v, &speed);
            const pp_lateral_state_t ego = measure_lateral(idle_edge, v, v_y, yaw_rate);
            if (pp_generate_quintic(&ego, ego.d, s->cal->T_lka, &path)
                && pp_output_points(idle_edge, &path, &speed, s->vehicle.wheelbase, out->points, &out->samples)) {
                finish_intervention_path(s, &speed, &PP_HWA_LIMITS, &old, true, out);
            } else {
                pp_arbitration_invalidate(&s->arbitration, &out->arbitration);
            }
            return;
        }
        if (out->ref.valid) {
            pp_ref_walker_t walker;
            pp_ref_point_t foot;
            pp_lateral_state_t measured;
            pp_lateral_state_t start;
            pp_speed_profile_t speed;
            pp_path_check_t check;
            pp_ref_walk_begin(&walker, &out->ref, &foot);
            pp_lateral_state(&foot, v, v_y, yaw_rate, &measured);                  /* T6 */
            bool from_old = false;
            if (out->arbitration.cancelled || follow_car) {
                start = measured;                                      /* PP-SWR-036, 039, 040 */
            } else {
                from_old = pp_stitch_start(&old, &out->ref, &measured, s->cal, &start); /* T4 step 2 */
            }
            update_recentering(s, in->function_requests, measured.d);
            if (override_now) {
                s->recentering = true;      /* after the override: back to the centre, T_recenter */
            }
            /* T8: offset from a large vehicle in an adjacent lane; car front and rear
             * approximated from the wheelbase (VehicleConfig has no length). */
            const double wheelbase_m = (double)s->vehicle.wheelbase;
            const double offset = pp_offset_update(&s->offset, in->object_list, &out->ref, v,
                                                   (double)s->vehicle.vehicle_width,
                                                   wheelbase_m + 1.0, -1.0, s->cal, dt);
            pp_speed_profile(in->longitudinal_plan, t0_us, v, &speed);
            /* T7 target: the T8 offset; while the driver overrides, the car's own offset, so the
             * path runs parallel to the lane from the car and does not pull it back. */
            const double d_target = override_now ? measured.d : offset;
#ifdef PP_T7_QP
            /* Continuity is a cost of the QP; T4 steps 4, 5 still guarantee it. */
            out->path_valid = generate_hwa_qp(s, &out->ref, &start, &speed, &old, from_old, d_target,
                                              out->points, &out->samples);         /* T7 C, T11 */
#else
            (void)from_old;
            out->path_valid = generate_hwa(s, &out->ref, &start, &speed, d_target, out->points,
                                           &out->samples);                         /* T7 A, T11 */
#endif
            if (out->path_valid) {
                const double wheelbase = (double)s->vehicle.wheelbase;
                if (!override_now) {   /* T4 step 5: no blend while the driver overrides */
                    (void)pp_stitch_blend(&old, s->cal, wheelbase, continuity_limit(&out->ref),
                                          out->points);                            /* T4 steps 4, 5 */
                }
                (void)pp_feasibility_limit(out->points, &out->samples, &PP_HWA_LIMITS,
                                           &s->vehicle);                           /* T10 step 2 */
                /* T10 steps 3, 4 on the larger of camera and fused curvature (safe side). */
                pp_curve_limit_t camera_curve;
                pp_feasibility_check(out->points, &out->samples, &check);
                out->ay_need_max = fmax(check.ay_need_max, pp_ay_need_max(&camera_ref, &speed));
                pp_curve_limit(&out->ref, PP_HWA_LIMITS.ay_max, &out->curve);
                pp_curve_limit(&camera_ref, PP_HWA_LIMITS.ay_max, &camera_curve);
                if (camera_curve.kappa_max > out->curve.kappa_max) {
                    out->curve = camera_curve;
                }
            }
        }
        if (!out->path_valid) {
            pp_arbitration_invalidate(&s->arbitration, &out->arbitration);
        }
    }
}

void pp_step(void *state,
             const pp_planner_inputs_t *inputs,
             pp_ego_motion_fn ego_motion,
             void *ego_motion_context,
             pp_planner_outputs_t *outputs)
{
    if (outputs != NULL) {
        (void)memset(outputs, 0, sizeof(*outputs));
        pp_state_t *s = prepared_state(state);

        /* PathStatus every cycle (PP-SWR-010). No Trajectory unless initialised (PP-SWR-146). */
        if ((s != NULL) && (inputs != NULL)) {
            const uint64_t t0 = inputs->t0_us;
            pp_cycle_result_t cycle;
            (void)memset(&cycle, 0, sizeof(cycle));

            if (s->initialized) {
                pp_usable_inputs_t usable;
                check_inputs(inputs, &usable);                                     /* T1 */
                check_requests_timeout(s, inputs, &usable);
                plan_path(s, t0, &usable, ego_motion, ego_motion_context, &cycle);
                const pp_active_function_t active = cycle.arbitration.active_function;
                const bool switch_authority = (active != s->last_active)
                    && ((active >= PP_ACTIVE_FUNCTION_LKA) || (s->last_active >= PP_ACTIVE_FUNCTION_LKA));
                s->last_active = active;

                /* T10 step 3: flag from the curvature ahead; no path, no flag. */
                if (cycle.path_valid) {
                    if (switch_authority) {
                        pp_limit_flag_reset(&s->limit_flag);
                    }
                    pp_limit_flag_update(&s->limit_flag, cycle.ay_need_max, cycle.ay_limit,
                                         s->cal, (double)PP_PLANNER_PERIOD_US / PP_US_PER_S);
                } else {
                    pp_limit_flag_reset(&s->limit_flag);
                }

                /* T11: Trajectory every cycle, header.valid tells whether the path is usable. */
                outputs->trajectory_sent = true;
                outputs->trajectory.header.stamp_us = t0;                          /* PP-SWR-012 */
                outputs->trajectory.header.counter = next_counter(&s->trajectory_counter);
                outputs->trajectory.header.valid = cycle.path_valid;
                outputs->trajectory.header.frame_id = PP_FRAME_ID_BASE_LINK;
                if (cycle.path_valid) {
                    (void)memcpy(outputs->trajectory.points, cycle.points,
                                 sizeof(outputs->trajectory.points));
                    outputs->trajectory.observed_horizon_s = observed_horizon(cycle.points, &cycle.ref);
                } else {
                    pp_output_empty_points(outputs->trajectory.points);
                    outputs->trajectory.observed_horizon_s = 0.0F;
                }
                pp_stitch_remember(&s->prev_path, t0, cycle.path_valid,
                                   outputs->trajectory.points);                    /* for T4 */

                /* LateralLimits every cycle (PP-SWR-150); same flag as PathStatus (PP-SWR-009). */
                outputs->lateral_limits_sent = true;
                outputs->lateral_limits.header.stamp_us = t0;
                outputs->lateral_limits.header.counter = next_counter(&s->lateral_limits_counter);
                outputs->lateral_limits.header.valid = cycle.path_valid;
                outputs->lateral_limits.v_max = (float)cycle.curve.v_max;
                outputs->lateral_limits.distance = (float)cycle.curve.distance;
                outputs->lateral_limits.lateral_limit_reached = s->limit_flag.reached || cycle.intervention_limited;
            }

            outputs->path_status_sent = true;
            outputs->path_status.header.stamp_us = t0;
            outputs->path_status.header.counter = next_counter(&s->path_status_counter);
            outputs->path_status.header.valid = true;
            outputs->path_status.path_valid = cycle.path_valid;
            outputs->path_status.active_function = cycle.arbitration.active_function;
            outputs->path_status.lka_phase = cycle.arbitration.lka_phase;
            outputs->path_status.elk_phase = cycle.arbitration.elk_phase;
            outputs->path_status.lateral_limit_reached = outputs->lateral_limits.lateral_limit_reached;
            outputs->path_status.lane_too_narrow = cycle.ref.valid && cycle.ref.lane_too_narrow;
        }
    }
}

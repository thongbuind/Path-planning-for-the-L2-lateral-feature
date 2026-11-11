/*
 * Public entry points of the path planner (interfaces/c/pp_planner.h).
 *
 * One cycle (Software Architectural Design 3.2) runs the units of the Software
 * Detailed Design in this order: T1 input check and latency compensation, T2
 * reference line, T5 curvature fusion, T6 lateral state, T4 stitching (start state),
 * T7 path generation (technique A) with T11 output, T4 continuity, T10 feasibility, T9
 * arbitration. Each unit header says which steps are implemented. Not yet in the
 * cycle: T3, T8.
 */

#include <math.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "arbitration.h"
#include "curvature.h"
#include "feasibility.h"
#include "generators/quintic.h"
#include "input_check.h"
#include "lateral_state.h"
#include "latency.h"
#include "output.h"
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
    const pp_speed_signals_t *speed;
    const pp_imu_signals_t *imu;
    const pp_vehicle_state_estimate_t *vehicle_state;
    const pp_function_requests_t *function_requests;
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
    }
    if (pp_input_usable(in->longitudinal_plan.present,
                        in->longitudinal_plan.message.header.valid,
                        in->longitudinal_plan.rx_us,
                        in->longitudinal_plan.message.header.stamp_us, t0,
                        PP_LONGITUDINAL_PLAN_TIMEOUT_US, PP_LONGITUDINAL_PLAN_MAX_AGE_US)) {
        out->longitudinal_plan = &in->longitudinal_plan.message;
    }
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
    double ay_need_max;                    /* T10 step 1, for lateral_limit_reached */
    pp_curve_limit_t curve;                /* T10 step 4, for LateralLimits */
} pp_cycle_result_t;

/* Limits of HWA, the only function so far (Software Architectural Design 9). */
static const pp_function_limits_t PP_HWA_LIMITS = {PP_AYSMAX, PP_JERK_MAX_HWA};

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
static bool generate_hwa(const pp_state_t *s, const pp_reference_line_t *ref,
                         const pp_lateral_state_t *start, const pp_speed_profile_t *speed,
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
        ok = pp_generate_quintic(start, 0.0, duration, &lateral);
        done = !ok;
        if (ok) {
            pp_output_points(ref, &lateral, speed, wheelbase, points, samples);
            pp_feasibility_check(points, samples, &check);
            const bool targets_met = (check.ay_add_max <= (double)cal->ay_add_max_hwa)
                                     && (check.jerk_max <= (double)cal->jerk_target_hwa);
            done = targets_met || ((duration + PP_T_STEP_S) > ((double)cal->T_max + 1.0e-9));
            duration += PP_T_STEP_S;
        }
    }
    return ok;
}

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

static void plan_path(pp_state_t *s, uint64_t t0_us, const pp_usable_inputs_t *in,
                      pp_ego_motion_fn ego_motion, void *context, pp_cycle_result_t *out)
{
    pp_motion_t to_t0;
    pp_motion_t since_last;
    pp_old_path_t old;
    (void)memset(out, 0, sizeof(*out));
    const bool moved = cycle_motion(s, t0_us, ego_motion, context, &since_last);
    pp_stitch_move_old(&s->prev_path, t0_us, ego_motion, context, &old);         /* T4 step 1 */

    /* Speed is required (PP-SWR-142); without it the memories cannot be moved. */
    const bool forward = (in->speed != NULL)
                         && (in->speed->direction == PP_DIRECTION_FORWARD);
    if (!forward) {
        pp_reference_memory_reset(&s->ref_mem);
        pp_curvature_reset(&s->curv);
    } else {
        const double dt = (double)PP_PLANNER_PERIOD_US / PP_US_PER_S;
        const double v = (double)in->speed->speed_mps;
        const double v_y = (in->vehicle_state != NULL)
                           ? (double)in->vehicle_state->lateral_velocity : 0.0;
        const double yaw_rate = (in->imu != NULL) ? (double)in->imu->yaw_rate_rps : 0.0;
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
        if (out->ref.valid) {
            pp_ref_walker_t walker;
            pp_ref_point_t foot;
            pp_lateral_state_t measured;
            pp_lateral_state_t start;
            pp_speed_profile_t speed;
            pp_path_check_t check;
            pp_ref_walk_begin(&walker, &out->ref, &foot);
            pp_lateral_state(&foot, v, v_y, yaw_rate, &measured);                  /* T6 */
            (void)pp_stitch_start(&old, &out->ref, &measured, s->cal, &start);    /* T4 step 2 */
            update_recentering(s, in->function_requests, measured.d);
            pp_speed_profile(in->longitudinal_plan, t0_us, v, &speed);
            /* HWA lane keeping: target d = 0, T8 Offset not yet (Software Detailed Design 10). */
            out->path_valid = generate_hwa(s, &out->ref, &start, &speed, out->points,
                                           &out->samples);                         /* T7, T11 */
            if (out->path_valid) {
                const double wheelbase = (double)s->vehicle.wheelbase;
                (void)pp_stitch_blend(&old, s->cal, wheelbase, out->points);  /* T4 steps 4, 5 */
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
            pp_arbitration_t arbitration;
            (void)memset(&cycle, 0, sizeof(cycle));

            if (s->initialized) {
                pp_usable_inputs_t usable;
                check_inputs(inputs, &usable);                                     /* T1 */
                plan_path(s, t0, &usable, ego_motion, ego_motion_context, &cycle);
                pp_arbitrate(usable.function_requests, cycle.path_valid, &arbitration); /* T9 */
                s->last_active = arbitration.active_function;

                /* T10 step 3: flag from the curvature ahead; no path, no flag. */
                if (cycle.path_valid) {
                    pp_limit_flag_update(&s->limit_flag, cycle.ay_need_max, PP_HWA_LIMITS.ay_max,
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
                } else {
                    pp_output_empty_points(outputs->trajectory.points);
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
                outputs->lateral_limits.lateral_limit_reached = s->limit_flag.reached;
            } else {
                pp_arbitrate(NULL, false, &arbitration);
            }

            outputs->path_status_sent = true;
            outputs->path_status.header.stamp_us = t0;
            outputs->path_status.header.counter = next_counter(&s->path_status_counter);
            outputs->path_status.header.valid = true;
            outputs->path_status.path_valid = cycle.path_valid;
            outputs->path_status.active_function = arbitration.active_function;
            outputs->path_status.intervention_phase = arbitration.intervention_phase;
            outputs->path_status.lateral_limit_reached = s->initialized && s->limit_flag.reached;
            outputs->path_status.lane_too_narrow = cycle.ref.valid && cycle.ref.lane_too_narrow;
        }
    }
}

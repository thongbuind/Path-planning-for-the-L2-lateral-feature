#include <math.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "feasibility.h"
#include "follow.h"
#include "generators/pp_t7.h"
#include "offset.h"
#include "output.h"
#include "pp_build_info.h"
#include "pp_calibration.h"
#include "pp_core.h"
#include "pp_math.h"
#include "pp_planner.h"
#include "reference_line.h"
#include "stitching.h"

#define PP_LCC_MAGIC (0x50504C43UL)

typedef struct {
    pp_core_state_t core;  /* Core phải là trường đầu để pp_core_init ép con trỏ state về đúng kiểu. */
    pp_t7_ws_t t7;
#ifdef PP_T7_TELEMETRY
    pp_t7_telemetry_t t7_telemetry;
#endif
    pp_offset_state_t offset;
    pp_follow_state_t follow;
    bool recentering;
    bool override_last;
    bool intervention_last;
    bool hold_prev;
    bool driving;
} pp_lcc_state_t;

_Static_assert(_Alignof(pp_lcc_state_t) <= PP_STATE_ALIGNMENT,
               "pp_lcc_state_t needs more alignment than PP_STATE_ALIGNMENT");

static const pp_function_limits_t PP_LCC_LIMITS = {PP_AYSMAX, PP_JERK_MAX_HWA, 0.0, 0.0};

size_t pp_lcc_state_size(void)
{
    return sizeof(pp_lcc_state_t);
}

const char *pp_lcc_version(void)
{
    return PP_BUILD_INFO_LCC;
}

pp_init_result_t pp_lcc_init(void *state, size_t state_size, const pp_vehicle_config_t *vehicle_config)
{
    pp_init_result_t result = pp_core_init(state, state_size, sizeof(pp_lcc_state_t), PP_LCC_MAGIC,
                                           vehicle_config);
    if (result == PP_INIT_RESULT_OK) {
        const pp_calibration_t *cal = &pp_calibration;
        if ((cal->trail_n * cal->trail_spacing) < (float)PP_FOLLOW_TRAIL_COVER_M) {
            ((pp_core_state_t *)state)->initialized = false;
            result = PP_INIT_RESULT_BAD_CALIBRATION;
        } else {
            pp_t7_reset(&((pp_lcc_state_t *)state)->t7);
        }
    }
    return result;
}

static void update_recentering(pp_lcc_state_t *s, bool requested, bool hold_now, double measured_d)
{
    if (!requested) {
        s->recentering = false;
    } else if (!s->driving) {
        s->recentering = true;
    } else {
    }
    if (s->recentering && (fabs(measured_d) <= (double)s->core.cal->recenter_done)) {
        s->recentering = false;
    }
    if (hold_now) {
        s->recentering = true;
    }
}

typedef struct {
    bool path_valid;
    pp_lcc_mode_t mode;
    double follow_distance;
    pp_reference_line_t ref;
    pp_trajectory_point_t points[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
    double ay_need_max;
    double ay_limit;
    pp_curve_limit_t curve;
} pp_lcc_cycle_t;

typedef struct {
    uint64_t t0_us;
    double offset;
    bool hold_now;
    bool start_from_car;
    bool requested;
} pp_lcc_goal_t;

#if PP_T7_SUPPORT_FLOOR
/* Fit cubic qua cua chữ S có thể sai độ cong gần xe. Chỉ đặt sàn trợ giúp khi đường không đổi dấu
 * và camera khớp T5 trong giây đầu (PP-SWR-006). */
static bool confirmed_turn(const pp_ref_samples_t *fused, const pp_reference_line_t *camera,
                           const pp_speed_profile_t *speed, double epsilon_ay)
{
    pp_ref_walker_t walker;
    pp_ref_point_t point;
    pp_ref_walk_begin(&walker, camera, &point);
    double min_kappa = INFINITY;
    double max_kappa = -INFINITY;
    for (size_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        pp_ref_walk_to(&walker, speed->s[k], &point);
        if (walker.on_arc || !fused->in_view[k]) {
            break;
        }
        min_kappa = fmin(min_kappa, fmin(point.kappa, fused->kappa[k]));
        max_kappa = fmax(max_kappa, fmax(point.kappa, fused->kappa[k]));
        if ((min_kappa < 0.0) && (max_kappa > 0.0)) {
            return false;
        }
        if (((double)k * PP_GRID_STEP_S <= 1.0)
            && (fabs(point.kappa - fused->kappa[k]) * speed->v[k] * speed->v[k] > epsilon_ay)) {
            return false;
        }
    }
    return min_kappa <= max_kappa;
}
#endif

static bool build_path(pp_lcc_state_t *s, const pp_usable_inputs_t *in, const pp_frame_t *f,
                       const pp_reference_line_t *ref, bool follow, const pp_lcc_goal_t *goal,
                       pp_lcc_cycle_t *out)
{
    pp_ref_walker_t walker;
    pp_ref_point_t foot;
    pp_lateral_state_t measured;
    pp_lateral_state_t start;
    pp_speed_profile_t speed;
    pp_path_check_t check;
    pp_core_state_t *core = &s->core;
    const pp_calibration_t *cal = core->cal;

    out->ref = *ref;
    pp_ref_walk_begin(&walker, ref, &foot);
    pp_lateral_state(&foot, f->v, f->v_y, f->yaw_rate, &measured);
    bool from_old = false;
    if (goal->start_from_car) {
        start = measured;
    } else {
        from_old = pp_stitch_start(&f->old, ref, &measured, cal, &start);
    }
    update_recentering(s, goal->requested, goal->hold_now, measured.d);
    pp_speed_profile(in->longitudinal_plan, goal->t0_us, f->v, &speed);
    /* FOLLOW dùng offset mục tiêu 0. Khi tài xế override hoặc LKA/ELK đang REQUEST, giữ offset
     * hiện tại để path song song làn. */
    const double d_target = goal->hold_now ? measured.d : (follow ? 0.0 : goal->offset);
    const pp_t7_input_t t7_in = {
        .ref = ref, .start = &start, .speed = &speed, .old = &f->old, .from_old = from_old,
        .recentering = s->recentering, .follow = follow, .start_from_car = goal->start_from_car,
        .d_target = d_target, .objects = in->object_list, .vehicle = &core->vehicle,
    };
    const bool ok = pp_t7_generate(&s->t7, cal, &t7_in, out->points, &out->samples);
#ifdef PP_T7_TELEMETRY
    if (!ok) {  /* Không có path: vẫn ghi mã fallback của generator; T10 không chạy. */
        pp_t7_report(&s->t7, &s->t7_telemetry);
        s->t7_telemetry.t10_change_m = 0.0;
    }
#endif
    if (ok) {
        const double wheelbase = (double)core->vehicle.wheelbase;
        /* Giới hạn candidate trước khi blend. Lần T10 sau bù chênh lệch do tốc độ thay đổi
         * (PP-TS-003). */
#ifdef PP_AY_MARGIN_GATE
        const bool over_limit = core->limit_flag.reached;
#else
        const bool over_limit = false;
#endif
        const pp_function_limits_t path_limits = pp_hwa_path_limits(cal, over_limit);
        pp_function_limits_t candidate_limits = path_limits;
#if PP_T7_SUPPORT_FLOOR
        if (core->limit_flag.reached && goal->requested && !goal->hold_now && !follow
            && !ref->coasting && !ref->inferred
            && confirmed_turn(&out->samples, &f->camera_ref, &speed, (double)cal->epsilon_ay)) {
            /* Chừa nửa epsilon_ay để blend với path trước. */
            candidate_limits.ay_support = PP_AYSMAX - (0.5 * (double)cal->epsilon_ay);
        }
#endif
#ifdef PP_T7_TELEMETRY
        pp_trajectory_point_t generated[PP_TRAJECTORY_POINTS];
        (void)memcpy(generated, out->points, sizeof(generated));
#endif
        (void)pp_feasibility_limit(out->points, &out->samples, &candidate_limits, &core->vehicle);
#ifdef PP_T7_TELEMETRY
        pp_t7_report(&s->t7, &s->t7_telemetry);
        s->t7_telemetry.t10_change_m = 0.0;
        for (size_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
            const double dx = (double)out->points[k].pose.x - (double)generated[k].pose.x;
            const double dy = (double)out->points[k].pose.y - (double)generated[k].pose.y;
            s->t7_telemetry.t10_change_m = fmax(s->t7_telemetry.t10_change_m, sqrt((dx * dx) + (dy * dy)));
        }
#endif
        if (!goal->hold_now) {
            /* FOLLOW chỉ quan sát đến lead. Cửa sổ continuity vẫn lấy từ LaneModel. */
            const double x_limit = pp_core_continuity_limit(follow ? &f->camera_ref : ref);
            (void)pp_stitch_blend(&f->old, cal, wheelbase, x_limit,
                                  out->points);
        }
        (void)pp_feasibility_limit(out->points, &out->samples, &path_limits, &core->vehicle);
        pp_curve_limit_t camera_curve;
        pp_feasibility_check(out->points, &out->samples, &check);
        out->ay_need_max = fmax(check.ay_need_max, pp_ay_need_max(&f->camera_ref, &speed));
        pp_curve_limit(ref, PP_LCC_LIMITS.ay_max, &out->curve);
        pp_curve_limit(&f->camera_ref, PP_LCC_LIMITS.ay_max, &camera_curve);
        if (camera_curve.kappa_max > out->curve.kappa_max) {
            out->curve = camera_curve;
        }
    }
    return ok;
}

static void plan_lcc(pp_lcc_state_t *s, uint64_t t0_us, const pp_usable_inputs_t *in,
                     pp_ego_motion_fn ego_motion, void *context, pp_lcc_cycle_t *out)
{
    pp_frame_t f;
    (void)memset(out, 0, sizeof(*out));
    out->ay_limit = PP_LCC_LIMITS.ay_max;
    pp_core_frame(&s->core, in, t0_us, ego_motion, context, &f);
#ifdef PP_T7_TELEMETRY
    (void)memset(&s->t7_telemetry, 0, sizeof(s->t7_telemetry));
    s->t7_telemetry.residual = NAN;
    s->t7_telemetry.slack = NAN;
#endif
    if (!f.forward) {
        pp_t7_reset(&s->t7);
        pp_offset_reset(&s->offset);
        pp_follow_reset(&s->follow);
        return;
    }
    const pp_calibration_t *cal = s->core.cal;
    const pp_function_requests_t *req = in->function_requests;

    /* PP-SWR-039, 040: bắt đầu tại xe khi override hoặc LKA/ELK REQUEST, kể cả chu kỳ đầu sau khi
     * thôi. */
    const bool override_now = (req != NULL) ? req->driver_override : s->override_last;
    const bool intervention_now = (req != NULL)
        ? ((req->requests[PP_FUNCTION_LKA].state == PP_REQUEST_STATE_REQUEST)
           || (req->requests[PP_FUNCTION_ELK].state == PP_REQUEST_STATE_REQUEST))
        : s->intervention_last;
    s->override_last = override_now;
    s->intervention_last = intervention_now;
    pp_lcc_goal_t goal = {
        .t0_us = t0_us,
        .hold_now = override_now || intervention_now,
        .requested = (req != NULL) && (req->requests[PP_FUNCTION_LCC].state == PP_REQUEST_STATE_REQUEST),
    };
    goal.start_from_car = goal.hold_now || s->hold_prev;
    s->hold_prev = goal.hold_now;

    /* Cập nhật trail cả khi vạch còn đủ tin để có sẵn dữ liệu lúc mất vạch. */
    const bool lane_trusted = f.lane_ok && f.ref.valid && !f.ref.inferred && !f.ref.coasting;
    const bool lane_lost = !f.ref.valid || f.ref.coasting;
    pp_follow_input_t fin;
    (void)memset(&fin, 0, sizeof(fin));
    fin.t0_us = t0_us;
    fin.lane_trusted = lane_trusted;
    fin.lane_ref = &f.ref;
    fin.moved = f.moved;
    fin.since_last = f.since_last;
    fin.ds = f.moved ? f.since_last.dx : (f.v * f.dt);
    fin.v = f.v;
    fin.v_y = f.v_y;
    fin.lead = in->lead_target;
    fin.plan = in->longitudinal_plan;
    fin.steering = in->steering;
    if (in->lead_target != NULL) {
        fin.lead_moved = pp_core_motion_to_t0(in->lead_target->header.stamp_us, t0_us, ego_motion,
                                              context, &fin.lead_motion);
    }
    pp_follow_observe(&s->follow, &fin, cal);
    pp_reference_line_t virtual_ref;
    const bool follow_possible = goal.requested && lane_lost && f.chassis_valid && !in->requests_timed_out
        && pp_follow_candidate(&s->follow, &fin, cal, &s->core.vehicle, &virtual_ref);

    if (f.ref.valid) {
        const double wheelbase = (double)s->core.vehicle.wheelbase;
        goal.offset = pp_offset_update(&s->offset, in->object_list, &f.ref, f.v,
                                       (double)s->core.vehicle.vehicle_width,
                                       wheelbase + 1.0, -1.0, cal, f.dt);
    }

    const bool path_available = f.chassis_valid && !in->requests_timed_out
                                && (f.ref.valid || follow_possible);
    bool ok = false;
    bool follow = false;
    if (path_available) {
        if (follow_possible) {
            ok = build_path(s, in, &f, &virtual_ref, true, &goal, out)
                 && pp_follow_path_within(&s->follow, out->points, cal, &s->core.vehicle);
            follow = ok;
        }
        if (!ok && f.ref.valid) {
            (void)memset(out->points, 0, sizeof(out->points));
            ok = build_path(s, in, &f, &f.ref, false, &goal, out);
        }
    }
    pp_follow_commit(&s->follow, follow, in->lead_target, fin.ds);
    out->path_valid = ok;
    if (ok) {
        out->follow_distance = follow ? s->follow.distance_m : 0.0;
        if (follow) {
            /* T_coast tính lại khi rời FOLLOW. Nếu bộ nhớ làn cũ đã hết, COAST theo đường vừa bám
             * (PP-SWR-173). */
            pp_reference_memory_t *mem = &s->core.ref_mem;
            if (!mem->ref_valid) {
                mem->ref_valid = true;
                mem->ref_inferred = false;
                mem->ref_centre = virtual_ref.centre;
                mem->ref_width = virtual_ref.width;
                mem->ref_view_start = virtual_ref.view_start;
                mem->ref_view_end = virtual_ref.view_end;
            }
            mem->coast_s = 0.0;
        }
        out->mode = !goal.requested ? PP_LCC_MODE_NONE
                    : follow ? PP_LCC_MODE_FOLLOW
                    : f.ref.coasting ? PP_LCC_MODE_COAST
                    : f.ref.inferred ? PP_LCC_MODE_INFERRED : PP_LCC_MODE_LANE;
        s->driving = out->mode != PP_LCC_MODE_NONE;
    } else {
        s->driving = false;
    }
}

void pp_lcc_step(void *state,
                 const pp_lcc_inputs_t *inputs,
                 pp_ego_motion_fn ego_motion,
                 void *ego_motion_context,
                 pp_lcc_outputs_t *outputs)
{
    if (outputs != NULL) {
        (void)memset(outputs, 0, sizeof(*outputs));
        pp_lcc_state_t *s = (pp_lcc_state_t *)pp_core_prepared(state, PP_LCC_MAGIC);

        if ((s != NULL) && (inputs != NULL)) {
            const uint64_t t0 = inputs->t0_us;
            pp_lcc_cycle_t cycle;
            (void)memset(&cycle, 0, sizeof(cycle));

            if (s->core.initialized) {
                const pp_common_inputs_t common = {
                    .t0_us = t0, .lane_model = &inputs->lane_model, .object_list = &inputs->object_list,
                    .lead_target = &inputs->lead_target, .imu = &inputs->imu,
                    .steering = &inputs->steering, .speed = &inputs->speed,
                    .vehicle_state = &inputs->vehicle_state,
                    .function_requests = &inputs->function_requests,
                    .longitudinal_plan = &inputs->longitudinal_plan,
                };
                pp_usable_inputs_t usable;
                pp_core_hold_inputs(&s->core, &common);
                pp_core_check_inputs(&s->core, &common, &usable);
                pp_core_check_requests_timeout(&s->core, t0, &usable);
                plan_lcc(s, t0, &usable, ego_motion, ego_motion_context, &cycle);

                if (cycle.path_valid) {
                    pp_limit_flag_update(&s->core.limit_flag, cycle.ay_need_max, cycle.ay_limit,
                                         s->core.cal, (double)PP_PLANNER_PERIOD_US / PP_US_PER_S);
                } else {
                    pp_limit_flag_reset(&s->core.limit_flag);
                }

                outputs->trajectory_sent = true;
                pp_core_publish_trajectory(&s->core, t0, cycle.path_valid, cycle.points, &cycle.ref,
                                           PP_PLANNER_ID_LCC, &outputs->trajectory);

                outputs->lateral_limits_sent = true;
                outputs->lateral_limits.header.stamp_us = t0;
                outputs->lateral_limits.header.counter = pp_core_next_counter(&s->core.lateral_limits_counter);
                outputs->lateral_limits.header.valid = cycle.path_valid;
                outputs->lateral_limits.v_max = (float)cycle.curve.v_max;
                outputs->lateral_limits.distance = (float)cycle.curve.distance;
                outputs->lateral_limits.lateral_limit_reached = s->core.limit_flag.reached;
            }

            outputs->lcc_status_sent = true;
            outputs->lcc_status.header.stamp_us = t0;
            outputs->lcc_status.header.counter = pp_core_next_counter(&s->core.status_counter);
            outputs->lcc_status.header.valid = true;
            outputs->lcc_status.path_valid = cycle.path_valid;
            outputs->lcc_status.lcc_mode = cycle.mode;
            outputs->lcc_status.follow_distance = (float)cycle.follow_distance;
            outputs->lcc_status.lateral_limit_reached = outputs->lateral_limits.lateral_limit_reached;
            outputs->lcc_status.lane_too_narrow = cycle.path_valid && cycle.ref.valid && cycle.ref.lane_too_narrow;
        }
    }
}

#ifdef PP_T7_TELEMETRY
bool pp_lcc_t7_telemetry(const void *state, pp_t7_telemetry_t *out)
{
    const pp_lcc_state_t *s = (const pp_lcc_state_t *)state;
    const bool ok = (s != NULL) && (out != NULL) && (s->core.magic == PP_LCC_MAGIC) && s->core.initialized;
    if (ok) {
        *out = s->t7_telemetry;
    }
    return ok;
}

const void *pp_lcc_t7_workspace(const void *state, size_t *size)
{
    const pp_lcc_state_t *s = (const pp_lcc_state_t *)state;
    const bool ok = (s != NULL) && (s->core.magic == PP_LCC_MAGIC) && s->core.initialized;
    if (size != NULL) {
        *size = ok ? sizeof(pp_t7_ws_t) : 0U;
    }
    return ok ? (const void *)&s->t7 : NULL;
}
#endif

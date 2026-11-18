/*
 * LCC planner (library pp_lcc; interfaces/c/pp_planner.h, pp_lcc_*).
 *
 * One cycle (Software Architectural Design 3.2) runs the units of the Software Detailed
 * Design in this order: T1 input check and latency compensation, T2 reference line, T5
 * curvature fusion, T12 follow-lead when both lane lines are lost, T6 lateral state,
 * T4 stitching, T8 offset, T7 path generation, T10 feasibility and T11 output. Choosing
 * between this planner and the LKA/ELK planner belongs to the arbitrator of the system
 * (PP-ASM-022).
 */

#include <math.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "feasibility.h"
#include "follow.h"
#include "generators/qp.h"
#include "generators/quintic.h"
#include "offset.h"
#include "output.h"
#include "pp_build_info.h"
#include "pp_calibration.h"
#include "pp_core.h"
#include "pp_math.h"
#include "pp_planner.h"
#include "reference_line.h"
#include "stitching.h"

#define PP_LCC_MAGIC (0x50504C43UL) /* "PPLC" */

typedef struct {
    pp_core_state_t core;           /* Must stay first */
    pp_qp_ws_t qp;                  /* T7 technique C: warm start between cycles */
    pp_offset_state_t offset;       /* T8 */
    pp_follow_state_t follow;       /* T12 */
    bool recentering;               /* T7: LCC brings the car back to the centre */
    bool override_last;             /* driver_override of the last usable FunctionRequests */
    bool intervention_last;         /* LKA or ELK in REQUEST in the last usable FunctionRequests */
    bool hold_prev;                 /* Last cycle the path started from the car (PP-SWR-039, 040) */
    bool driving;                   /* Last cycle lcc_mode was not NONE */
} pp_lcc_state_t;

_Static_assert(_Alignof(pp_lcc_state_t) <= PP_STATE_ALIGNMENT,
               "pp_lcc_state_t needs more alignment than PP_STATE_ALIGNMENT");

/* Software Architectural Design 9. */
static const pp_function_limits_t PP_LCC_LIMITS = {PP_AYSMAX, PP_JERK_MAX_HWA, 0.0};

#define PP_T_STEP_S (0.25)                 /* T7 A: duration step (Software Detailed Design 10) */
#define PP_T_MAX_STEPS (32U)               /* Bounds the loop whatever T_max is */

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
        /* Limit that has no per-parameter form: the trail must cover 50 m (SDD 15, T12). */
        const pp_calibration_t *cal = &pp_calibration;
        if ((cal->trail_n * cal->trail_spacing) < (float)PP_FOLLOW_TRAIL_COVER_M) {
            ((pp_core_state_t *)state)->initialized = false;
            result = PP_INIT_RESULT_BAD_CALIBRATION;
        }
    }
    return result;
}

/*
 * LCC "đưa về giữa" (Software Detailed Design 10): starts when LCC is requested and was not
 * driving in the previous cycle; ends when the car is within recenter_done of the centre
 * or LCC leaves REQUEST. While the driver overrides, or LKA or ELK is in REQUEST, the path
 * runs parallel to the lane and recentering starts when that ends.
 */
static void update_recentering(pp_lcc_state_t *s, bool requested, bool hold_now, double measured_d)
{
    if (!requested) {
        s->recentering = false;
    } else if (!s->driving) {
        s->recentering = true;
    } else {
        /* LCC keeps driving: recentering continues until the car is centred. */
    }
    if (s->recentering && (fabs(measured_d) <= (double)s->core.cal->recenter_done)) {
        s->recentering = false;
    }
    if (hold_now) {
        s->recentering = true;
    }
}

#ifndef PP_T7_QP
/*
 * T7 technique A and T11: quintic to the target in T_hwa (T_recenter while recentering);
 * while the path misses the LCC targets (ay_add_max_hwa, jerk_target_hwa) the duration
 * grows by 0.25 s up to T_max.
 */
static bool generate_lcc(const pp_lcc_state_t *s, const pp_reference_line_t *ref,
                         const pp_lateral_state_t *start, const pp_speed_profile_t *speed,
                         double d_target,
                         pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],
                         pp_ref_samples_t *samples)
{
    const pp_calibration_t *cal = s->core.cal;
    const double wheelbase = (double)s->core.vehicle.wheelbase;
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
static bool generate_lcc_qp(pp_lcc_state_t *s, const pp_reference_line_t *ref,
                            const pp_lateral_state_t *start, const pp_speed_profile_t *speed,
                            const pp_old_path_t *old, bool from_old, double d_target,
                            pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],
                            pp_ref_samples_t *samples)
{
    const pp_calibration_t *cal = s->core.cal;
    pp_qp_problem_t pb;
    pp_lateral_path_t lateral;
    pp_ref_walker_t walker;
    pp_ref_point_t r;
    (void)memset(&pb, 0, sizeof(pb));
    pb.start = *start;
    pb.d_target = d_target;
    pb.ay_limit = PP_AYSMAX * (double)cal->qp_ay_margin;
    pb.jerk_limit = 0.9 * PP_JERK_MAX_HWA;                  /* margin for T10, PP-SWR-003 */
    const double half = fmax(0.0, (0.5 * ref->width) - (0.5 * (double)s->core.vehicle.vehicle_width)
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
                    && pp_output_points(ref, &lateral, speed, (double)s->core.vehicle.wheelbase, points, samples);
    if (!ok) {
        pp_qp_reset(&s->qp);
    }
    return ok;
}
#endif

typedef struct {
    bool path_valid;
    pp_lcc_mode_t mode;
    double follow_distance;
    pp_reference_line_t ref;
    pp_trajectory_point_t points[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
    double ay_need_max;                    /* T10 step 1, for lateral_limit_reached */
    double ay_limit;
    pp_curve_limit_t curve;                /* T10 step 4, for LateralLimits */
} pp_lcc_cycle_t;

/* What the path of this cycle starts from and aims at. */
typedef struct {
    uint64_t t0_us;
    double offset;                         /* T8 */
    bool hold_now;                         /* PP-SWR-039, 040: driver override, or LKA or ELK in REQUEST */
    bool start_from_car;                   /* hold_now, or the first cycle after it */
    bool requested;                        /* LCC in REQUEST */
} pp_lcc_goal_t;

/* T6, T4 step 2, T7, T4 steps 4 and 5, T10 steps 2 to 4 on `ref`. False when no path. */
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
    pp_lateral_state(&foot, f->v, f->v_y, f->yaw_rate, &measured);                    /* T6 */
    bool from_old = false;
    if (goal->start_from_car) {
        start = measured;                                          /* PP-SWR-039, 040 */
    } else {
        from_old = pp_stitch_start(&f->old, ref, &measured, cal, &start);             /* T4 step 2 */
    }
    update_recentering(s, goal->requested, goal->hold_now, measured.d);
    pp_speed_profile(in->longitudinal_plan, goal->t0_us, f->v, &speed);
    /* T7 target: the T8 offset (0 when following); while the driver overrides or LKA or ELK
     * is requested, the car's own offset, so the path runs parallel to the lane and does
     * not pull it back (PP-TS-017). */
    const double d_target = goal->hold_now ? measured.d : (follow ? 0.0 : goal->offset);
#ifdef PP_T7_QP
    /* Continuity is a cost of the QP; T4 steps 4, 5 still guarantee it. */
    const bool ok = generate_lcc_qp(s, ref, &start, &speed, &f->old, from_old, d_target,
                                    out->points, &out->samples);                      /* T7 C, T11 */
#else
    (void)from_old;
    const bool ok = generate_lcc(s, ref, &start, &speed, d_target, out->points, &out->samples); /* T7 A, T11 */
#endif
    if (ok) {
        const double wheelbase = (double)core->vehicle.wheelbase;
        /* PP-TS-003: limit the candidate first, so the blend of two feasible paths
         * is the path sent; the second T10 call below only meets speed changes. */
#ifdef PP_AY_MARGIN_GATE
        const bool over_limit = core->limit_flag.reached;   /* PP-TS-020 V2: flag of last cycle */
#else
        const bool over_limit = false;
#endif
        const pp_function_limits_t path_limits = pp_hwa_path_limits(cal, over_limit);
        (void)pp_feasibility_limit(out->points, &out->samples, &path_limits, &core->vehicle); /* T10 step 2 */
        if (!goal->hold_now) {   /* T4 step 5: no blend while the path starts from the car */
            (void)pp_stitch_blend(&f->old, cal, wheelbase, pp_core_continuity_limit(ref),
                                  out->points);                                       /* T4 steps 4, 5 */
        }
        (void)pp_feasibility_limit(out->points, &out->samples, &path_limits, &core->vehicle); /* T10 step 2 */
        /* T10 steps 3, 4 on the larger of camera and fused curvature (safe side). */
        pp_curve_limit_t camera_curve;
        pp_feasibility_check(out->points, &out->samples, &check);
        out->ay_need_max = fmax(check.ay_need_max, pp_ay_need_max(&f->camera_ref, &speed));
        pp_curve_limit(ref, PP_LCC_LIMITS.ay_max, &out->curve);
        pp_curve_limit(&f->camera_ref, PP_LCC_LIMITS.ay_max, &camera_curve);
        if (camera_curve.kappa_max > out->curve.kappa_max) {
            out->curve = camera_curve;
        }
    }
    (void)in;
    return ok;
}

static void plan_lcc(pp_lcc_state_t *s, uint64_t t0_us, const pp_usable_inputs_t *in,
                     pp_ego_motion_fn ego_motion, void *context, pp_lcc_cycle_t *out)
{
    pp_frame_t f;
    (void)memset(out, 0, sizeof(*out));
    out->ay_limit = PP_LCC_LIMITS.ay_max;
    pp_core_frame(&s->core, in, t0_us, ego_motion, context, &f);
    if (!f.forward) {
        pp_qp_reset(&s->qp);
        pp_offset_reset(&s->offset);
        pp_follow_reset(&s->follow);
        return;
    }
    const pp_calibration_t *cal = s->core.cal;
    const pp_function_requests_t *req = in->function_requests;

    /* PP-TS-017 (V2b, choice B), PP-SWR-039, 040. While the driver overrides or LKA or ELK is in
     * REQUEST, and in the first cycle after, the path starts at the car (T4 step 2; R79 5.6.4.3:
     * priority to the driver). The last usable FunctionRequests counts while none is usable. */
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

    /* T12: observed every cycle so the trail is there when the lines are lost. */
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

    /* T8: once per cycle on the reference line of the lane; a following path does not use it. */
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
                 && pp_follow_path_within(&s->follow, out->points, cal, &s->core.vehicle);   /* M1 */
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
            /* PP-SWR-173: T_coast counts from leaving FOLLOW. The memory of the lane is kept;
             * if it had already run out, leaving FOLLOW coasts on the line followed. */
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

        /* LccStatus every cycle (PP-SWR-010). No Trajectory unless initialised (PP-SWR-146). */
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
                pp_core_hold_inputs(&s->core, &common);                            /* T1 */
                pp_core_check_inputs(&s->core, &common, &usable);
                pp_core_check_requests_timeout(&s->core, t0, &usable);
                plan_lcc(s, t0, &usable, ego_motion, ego_motion_context, &cycle);

                /* T10 step 3: flag from the curvature ahead; no path, no flag. */
                if (cycle.path_valid) {
                    pp_limit_flag_update(&s->core.limit_flag, cycle.ay_need_max, cycle.ay_limit,
                                         s->core.cal, (double)PP_PLANNER_PERIOD_US / PP_US_PER_S);
                } else {
                    pp_limit_flag_reset(&s->core.limit_flag);
                }

                /* T11: Trajectory every cycle, header.valid tells whether the path is usable. */
                outputs->trajectory_sent = true;
                pp_core_publish_trajectory(&s->core, t0, cycle.path_valid, cycle.points, &cycle.ref,
                                           PP_PLANNER_ID_LCC, &outputs->trajectory);

                /* LateralLimits every cycle (PP-SWR-150); same flag as LccStatus (PP-SWR-009). */
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

/*
 * LKA/ELK planner (library pp_lkaelk; interfaces/c/pp_planner.h, pp_lkaelk_*).
 *
 * One cycle runs: T1 input check and latency compensation, T2 reference line, T5 curvature
 * fusion, the ELK road-edge references (PP-SWR-047), T9 intervention selection, T6 lateral
 * state, T7 path generation (technique A), T4 stitching and T10 feasibility, T11 output.
 * LKA and ELK are two functions; ELK wins when both can drive. Choosing between this
 * planner and the LCC planner belongs to the arbitrator of the system (PP-ASM-022), so
 * this planner sends a Trajectory with header.valid = true only while it intervenes
 * (PP-SWR-180).
 */

#include <math.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "feasibility.h"
#include "generators/quintic.h"
#include "intervention.h"
#include "output.h"
#include "pp_build_info.h"
#include "pp_calibration.h"
#include "pp_core.h"
#include "pp_math.h"
#include "pp_planner.h"
#include "reference_line.h"
#include "selection.h"
#include "stitching.h"

#define PP_LKAELK_MAGIC (0x50504C4BUL) /* "PPLK" */

typedef struct {
    pp_core_state_t core;                    /* Must stay first */
    pp_selection_memory_t selection;         /* T9 */
    pp_edge_memory_t edge_mem;
    pp_intervention_path_t intervention_path;
    pp_lateral_velocity_history_t end_velocity;
    pp_corridor_t corridor;                  /* T9 step 7 */
} pp_lkaelk_state_t;

_Static_assert(_Alignof(pp_lkaelk_state_t) <= PP_STATE_ALIGNMENT,
               "pp_lkaelk_state_t needs more alignment than PP_STATE_ALIGNMENT");

/* Software Architectural Design 9. */
static const pp_function_limits_t PP_LKA_LIMITS = {PP_AY_MAX_LKA, PP_JERK_MAX_LKA, PP_AY_ADD_MAX_LKA};
static const pp_function_limits_t PP_ELK_LIMITS = {PP_AY_MAX_ELK, PP_JERK_MAX_ELK, PP_AY_ADD_MAX_ELK};

size_t pp_lkaelk_state_size(void)
{
    return sizeof(pp_lkaelk_state_t);
}

const char *pp_lkaelk_version(void)
{
    return PP_BUILD_INFO_LKAELK;
}

pp_init_result_t pp_lkaelk_init(void *state, size_t state_size, const pp_vehicle_config_t *vehicle_config)
{
    return pp_core_init(state, state_size, sizeof(pp_lkaelk_state_t), PP_LKAELK_MAGIC, vehicle_config);
}

typedef struct {
    bool path_available;                     /* Inputs usable: a path can be built on request */
    bool path_valid;                         /* path_available, and a path was built if one was due */
    pp_selection_t selection;
    pp_reference_line_t ref;
    pp_trajectory_point_t points[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
    bool intervention_limited;
} pp_lkaelk_cycle_t;

static void finish_path(pp_lkaelk_state_t *s, const pp_frame_t *f, const pp_function_limits_t *limits,
                        bool blend, pp_lkaelk_cycle_t *out)
{
    if (blend) {
        (void)pp_stitch_blend(&f->old, s->core.cal, (double)s->core.vehicle.wheelbase,
                              pp_core_continuity_limit(&out->ref), out->points);
    }
    out->intervention_limited = pp_feasibility_limit(out->points, &out->samples, limits, &s->core.vehicle);
}

/* T7 technique A on the intervention corridor, T4 steps 4 and 5, T10 step 2. */
static void plan_intervention(pp_lkaelk_state_t *s, const pp_usable_inputs_t *in, const pp_frame_t *f,
                              uint64_t t0_us, const pp_reference_line_t *corridor,
                              const pp_lateral_state_t *ego, pp_lkaelk_cycle_t *out)
{
    const bool elk = out->selection.active_function == PP_INTERVENTION_FUNCTION_ELK;
    const size_t function = elk ? PP_FUNCTION_ELK : PP_FUNCTION_LKA;
    const pp_function_limits_t *limits = elk ? &PP_ELK_LIMITS : &PP_LKA_LIMITS;
    pp_speed_profile_t speed;
    bool blend = true;
    out->ref = *corridor;
    pp_speed_profile(in->longitudinal_plan, t0_us, f->v, &speed);
    if (out->selection.starting) {
        /* PP-SWR-031, 049: the first cycle starts from the measured state, curvature from the
         * yaw rate (T6), and is not blended with the path of the previous cycle: that path
         * follows the car drifting out (PP-PR-062). */
        const pp_intervention_request_t *req = &s->selection.intervention[function - 1U];
        const double tlc = (double)in->function_requests->requests[function].tlc;
        pp_intervention_begin(&s->intervention_path, req, tlc, t0_us, corridor, ego, &speed,
                              limits, &s->core.vehicle, s->core.cal, elk);                  /* T7 A */
        blend = false;
    }
    pp_lateral_path_t path;
    pp_intervention_sample(&s->intervention_path, t0_us, &path);
    if (pp_output_points(corridor, &path, &speed, s->core.vehicle.wheelbase, out->points, &out->samples)) {
        finish_path(s, f, limits, blend, out);
        out->path_valid = true;
    } else {
        pp_selection_invalidate(&s->selection, &out->selection);
        out->path_valid = false;
    }
}

static void plan_lkaelk(pp_lkaelk_state_t *s, uint64_t t0_us, const pp_usable_inputs_t *in,
                        pp_ego_motion_fn ego_motion, void *context, pp_lkaelk_cycle_t *out)
{
    pp_frame_t f;
    (void)memset(out, 0, sizeof(*out));
    pp_selection_input_t sel = {
        .requests = in->function_requests, .t0_us = t0_us, .requests_rx_us = in->requests_rx_us,
        .hold_s = (double)s->core.cal->T_end_hold,
    };
    pp_core_frame(&s->core, in, t0_us, ego_motion, context, &f);
    if (!f.forward) {
        (void)memset(&s->edge_mem, 0, sizeof(s->edge_mem));
        s->end_velocity.valid = false;
        pp_corridor_reset(&s->corridor);
        pp_select(&s->selection, &sel, &out->selection);
        return;
    }
    const pp_calibration_t *cal = s->core.cal;
    const pp_vehicle_config_t *vehicle = &s->core.vehicle;
    const pp_function_requests_t *req = in->function_requests;

    pp_reference_line_t edges[PP_ROAD_EDGES];
    (void)memset(edges, 0, sizeof(edges));
    const pp_intervention_request_t *last_elk = &s->selection.intervention[PP_FUNCTION_ELK - 1U];
    const bool edge_handover = (last_elk->phase == PP_INTERVENTION_PHASE_ACTIVE)
                               && (last_elk->reason == PP_ELK_REASON_ROAD_EDGE);
    if (edge_handover || ((req != NULL) && (req->requests[PP_FUNCTION_ELK].state != PP_REQUEST_STATE_OFF))) {
        pp_road_edge_references(&s->edge_mem, &f.lane, &f.camera_ref, f.moved ? &f.since_last : NULL,
                                vehicle, cal, edges);                                /* PP-SWR-047 */
    } else {
        (void)memset(&s->edge_mem, 0, sizeof(s->edge_mem));
    }
    const pp_reference_line_t *refs[PP_INTERVENTIONS] = {&f.camera_ref, &f.camera_ref};
    const pp_reference_line_t *idle_edge = edges[0].valid ? &edges[0] : &edges[1];
    const bool state_valid = in->vehicle_state != NULL;
    const bool intervention_requested = (req != NULL)
        && ((req->requests[PP_FUNCTION_LKA].state == PP_REQUEST_STATE_REQUEST)
            || (req->requests[PP_FUNCTION_ELK].state == PP_REQUEST_STATE_REQUEST));
    const double end_v_y = pp_intervention_vy_at_t0(&s->end_velocity,
                              intervention_requested ? in->vehicle_state : NULL, t0_us);
    out->path_available = f.chassis_valid && !in->requests_timed_out && (f.ref.valid || idle_edge->valid);
    sel.path_available = out->path_available;

    /* Which reference line each intervention uses: ELK on a road edge takes the edge reference. */
    if (req != NULL) {
        for (size_t i = 0U; i < PP_INTERVENTIONS; i++) {
            const pp_intervention_request_t *prior = &s->selection.intervention[i];
            const pp_side_t side = prior->requested ? prior->side : req->requests[i + 1U].side;
            const pp_elk_reason_t reason = prior->requested ? prior->reason : req->requests[i + 1U].elk_reason;
            if ((i == (PP_FUNCTION_ELK - 1U)) && (reason == PP_ELK_REASON_ROAD_EDGE)) {
                refs[i] = &edges[(side == PP_SIDE_LEFT) ? 0U : 1U];
            }
        }
    }

    /* T9 step 7: the corridor of the intervention that is driving, moved to this cycle. */
    const pp_reference_line_t *corridor_of[PP_INTERVENTIONS] = {NULL, NULL};
    bool corridor_pending = false;
    if (req != NULL) {
        for (size_t i = 0U; i < PP_INTERVENTIONS; i++) {
            const pp_intervention_request_t *prior = &s->selection.intervention[i];
            if (prior->phase == PP_INTERVENTION_PHASE_ACTIVE) {
                const pp_side_t side = prior->requested ? prior->side : req->requests[i + 1U].side;
                corridor_of[i] = pp_corridor_update(&s->corridor, refs[i], f.moved ? &f.since_last : NULL,
                                                    false, side, (double)vehicle->wheelbase, cal, f.dt);
                corridor_pending = s->corridor.pending;
            }
        }
    }
    if (req != NULL) {
        for (size_t i = 0U; i < PP_INTERVENTIONS; i++) {
            const pp_function_request_t *r = &req->requests[i + 1U];
            const pp_intervention_request_t *prior = &s->selection.intervention[i];
            const pp_side_t side = prior->requested ? prior->side : r->side;
            const pp_elk_reason_t reason = prior->requested ? prior->reason : r->elk_reason;
            const bool elk = i == (PP_FUNCTION_ELK - 1U);
            const bool edge = elk && (reason == PP_ELK_REASON_ROAD_EDGE);
            const bool has_side = (side == PP_SIDE_LEFT) || (side == PP_SIDE_RIGHT);
            sel.can_start[i] = f.chassis_valid && state_valid && has_side && (edge ? refs[i]->valid
                : pp_intervention_line_trusted(&f.lane, &f.camera_ref, side, vehicle, cal));
            sel.can_continue[i] = f.chassis_valid && has_side && refs[i]->valid && !refs[i]->inferred
                                  && (!refs[i]->coasting || f.old.valid);      /* PP-SWR-046, 047 */
            if (sel.can_continue[i] && state_valid && (prior->phase == PP_INTERVENTION_PHASE_ACTIVE)) {
                const pp_reference_line_t *basis = (corridor_of[i] != NULL) ? corridor_of[i] : refs[i];
                const pp_lateral_state_t ego = pp_core_measure_lateral(basis, f.v, end_v_y, f.yaw_rate);
                sel.can_finish[i] = !corridor_pending
                    && pp_intervention_settled(basis, &ego, &f.old, f.v, end_v_y, f.yaw_rate, vehicle, cal);
            }
            if (elk) {
                sel.elk_too_late = pp_elk_past_marking(&f.lane, side, vehicle, cal);
            }
        }
    }
    pp_select(&s->selection, &sel, &out->selection);
    if (!out->path_available) {
        pp_corridor_reset(&s->corridor);
        return;
    }
    out->path_valid = true;
    const pp_intervention_function_t active = out->selection.active_function;
    if (active == PP_INTERVENTION_FUNCTION_NONE) {
        pp_corridor_reset(&s->corridor);
        return;                       /* Nothing to drive: Trajectory.header.valid = false (PP-SWR-180) */
    }
    const size_t index = (active == PP_INTERVENTION_FUNCTION_LKA) ? 0U : 1U;
    const pp_reference_line_t *corridor = corridor_of[index];
    if (out->selection.starting || (corridor == NULL)) {
        const pp_side_t side = s->selection.intervention[index].side;
        corridor = pp_corridor_update(&s->corridor, refs[index], NULL, true, side,
                                      (double)vehicle->wheelbase, cal, f.dt);       /* Fixed at the start */
    }
    const pp_lateral_state_t ego = pp_core_measure_lateral(refs[index], f.v, f.v_y, f.yaw_rate);
    plan_intervention(s, in, &f, t0_us, corridor, &ego, out);
    if (!out->path_valid) {
        pp_corridor_reset(&s->corridor);
    }
}

void pp_lkaelk_step(void *state,
                    const pp_lka_elk_inputs_t *inputs,
                    pp_ego_motion_fn ego_motion,
                    void *ego_motion_context,
                    pp_lka_elk_outputs_t *outputs)
{
    if (outputs != NULL) {
        (void)memset(outputs, 0, sizeof(*outputs));
        pp_lkaelk_state_t *s = (pp_lkaelk_state_t *)pp_core_prepared(state, PP_LKAELK_MAGIC);

        /* InterventionStatus every cycle (PP-SWR-010). No Trajectory unless initialised (PP-SWR-146). */
        if ((s != NULL) && (inputs != NULL)) {
            const uint64_t t0 = inputs->t0_us;
            pp_lkaelk_cycle_t cycle;
            (void)memset(&cycle, 0, sizeof(cycle));

            if (s->core.initialized) {
                const pp_common_inputs_t common = {
                    .t0_us = t0, .lane_model = &inputs->lane_model, .imu = &inputs->imu,
                    .steering = &inputs->steering, .speed = &inputs->speed,
                    .vehicle_state = &inputs->vehicle_state,
                    .function_requests = &inputs->function_requests,
                    .longitudinal_plan = &inputs->longitudinal_plan,
                };
                pp_usable_inputs_t usable;
                pp_core_hold_inputs(&s->core, &common);                            /* T1 */
                pp_core_check_inputs(&s->core, &common, &usable);
                pp_core_check_requests_timeout(&s->core, t0, &usable);
                plan_lkaelk(s, t0, &usable, ego_motion, ego_motion_context, &cycle);

                /* T11: Trajectory every cycle; valid only while LKA or ELK drives (PP-SWR-180). */
                const bool driving = cycle.path_valid
                                     && (cycle.selection.active_function != PP_INTERVENTION_FUNCTION_NONE);
                outputs->trajectory_sent = true;
                pp_core_publish_trajectory(&s->core, t0, driving, cycle.points, &cycle.ref,
                                           PP_PLANNER_ID_LKA_ELK, &outputs->trajectory);
            }

            outputs->intervention_status_sent = true;
            outputs->intervention_status.header.stamp_us = t0;
            outputs->intervention_status.header.counter = pp_core_next_counter(&s->core.status_counter);
            outputs->intervention_status.header.valid = true;
            outputs->intervention_status.path_valid = cycle.path_valid;
            outputs->intervention_status.active_function = cycle.selection.active_function;
            outputs->intervention_status.lka_phase = cycle.selection.lka_phase;
            outputs->intervention_status.elk_phase = cycle.selection.elk_phase;
            outputs->intervention_status.lateral_limit_reached = cycle.intervention_limited;
        }
    }
}

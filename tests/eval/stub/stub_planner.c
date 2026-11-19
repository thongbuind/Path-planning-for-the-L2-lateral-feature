/*
 * Test double built against interfaces/c/pp_planner.h, for tests of eval/ only: that any
 * planner library plugs in (Software Qualification Test Specification 11) and that
 * conformance B0 finds contract faults. Not a planner: path_valid is always false and the
 * path is a straight line at the measured speed. One library exports both families
 * (pp_lcc_* and pp_lkaelk_*), as eval/planner_choice.py accepts for a stub or a bait planner.
 *
 * Default: meets the contract. Each STUB_* define breaks one point on purpose:
 *   STUB_NO_STEP        both step functions missing (C1)
 *   STUB_NO_TRAJECTORY  never sends Trajectory or LateralLimits (C2)
 *   STUB_ACCEPT_WIDE    accepts a vehicle wider than 2.5 m (C2)
 *   STUB_COUNTER_STUCK  status counter does not increase (C2)
 *   STUB_NAN            NaN in the Trajectory (C2)
 *   STUB_CRASH          dereferences NULL in the 5th cycle (C2, the evaluator must survive)
 *   STUB_GLOBAL_STATE   keeps its counters in a global variable (C3)
 *   STUB_OVERRUN        writes one byte past the end of the state memory (C3)
 *   STUB_CLOCK          reads the system clock (C3)
 */
#include <math.h>
#include <string.h>
#ifdef STUB_CLOCK
#include <time.h>
#endif

#include "pp_planner.h"

typedef struct {
    uint8_t counter[3];
    uint8_t ok;
    uint32_t cycles;
} stub_state_t;

#ifdef STUB_GLOBAL_STATE
static stub_state_t g_state;
#endif

static pp_init_result_t stub_init(void *state, size_t state_size, const pp_vehicle_config_t *vehicle_config)
{
    stub_state_t *s = (stub_state_t *)state;
    if (state_size < sizeof(stub_state_t)) {
        return PP_INIT_RESULT_BAD_ARGUMENT;
    }
    memset(s, 0, sizeof *s);
#ifdef STUB_GLOBAL_STATE
    memset(&g_state, 0, sizeof g_state);
#endif
#ifdef STUB_OVERRUN
    ((uint8_t *)state)[state_size] = 0U;
#endif
    s->ok = (vehicle_config != NULL) ? 1U : 0U;
#ifndef STUB_ACCEPT_WIDE
    if (s->ok != 0U && !(vehicle_config->vehicle_width <= 2.5F)) {
        s->ok = 0U;
    }
#endif
    return (s->ok != 0U) ? PP_INIT_RESULT_OK : PP_INIT_RESULT_BAD_VEHICLE_CONFIG;
}

/* The part both planners share: counters, the status header and the straight Trajectory. */
static void stub_cycle(void *state, uint64_t t0_us, const pp_received_speed_signals_t *speed,
                       pp_basic_header_t *status, bool *trajectory_sent, pp_trajectory_t *trajectory,
                       bool *limits_sent, pp_lateral_limits_t *limits, bool has_limits)
{
    stub_state_t *s = (stub_state_t *)state;
#ifdef STUB_GLOBAL_STATE
    uint8_t *counter = g_state.counter;
#else
    uint8_t *counter = s->counter;
#endif
    float v = 0.0F;
    s->cycles++;
#ifdef STUB_CRASH
    if (s->cycles == 5U) {
        *(volatile int *)0 = 1;
    }
#endif
#ifdef STUB_CLOCK
    {
        volatile time_t now = time(NULL);
        (void)now;
    }
#endif
    if (speed->present && speed->message.header.valid && isfinite(speed->message.speed_mps)) {
        v = fminf(fmaxf(speed->message.speed_mps, 0.0F), 70.0F);
    }
    status->stamp_us = t0_us;
    status->counter = counter[1];
    status->valid = true;
#ifndef STUB_COUNTER_STUCK
    counter[1] = (uint8_t)(counter[1] + 1U);
#endif
#ifndef STUB_NO_TRAJECTORY
    if (has_limits) {
        *limits_sent = true;
        limits->header.stamp_us = t0_us;
        limits->header.counter = counter[2]++;
        limits->header.valid = true;
    }
    if (s->ok != 0U) {
        *trajectory_sent = true;
        trajectory->header.stamp_us = t0_us;
        trajectory->header.counter = counter[0]++;
        trajectory->header.valid = true;
        trajectory->header.frame_id = PP_FRAME_ID_BASE_LINK;
        for (unsigned i = 0U; i < PP_TRAJECTORY_POINTS; ++i) {
            pp_trajectory_point_t *p = &trajectory->points[i];
            p->time_from_start = 0.1F * (float)i;
            p->pose.x = v * p->time_from_start;
            p->longitudinal_velocity_mps = v;
        }
#ifdef STUB_NAN
        trajectory->points[3].pose.y = NAN;
#endif
    }
#else
    (void)limits_sent;
    (void)limits;
    (void)has_limits;
    (void)trajectory_sent;
    (void)trajectory;
#endif
}

size_t pp_lcc_state_size(void) { return sizeof(stub_state_t); }
size_t pp_lkaelk_state_size(void) { return sizeof(stub_state_t); }

pp_init_result_t pp_lcc_init(void *state, size_t state_size, const pp_vehicle_config_t *vehicle_config)
{
    return stub_init(state, state_size, vehicle_config);
}

pp_init_result_t pp_lkaelk_init(void *state, size_t state_size, const pp_vehicle_config_t *vehicle_config)
{
    return stub_init(state, state_size, vehicle_config);
}

#ifndef STUB_NO_STEP
void pp_lcc_step(void *state, const pp_lcc_inputs_t *inputs, pp_ego_motion_fn ego_motion,
                 void *ego_motion_context, pp_lcc_outputs_t *outputs)
{
    (void)ego_motion;
    (void)ego_motion_context;
    memset(outputs, 0, sizeof *outputs);
    outputs->lcc_status_sent = true;
    stub_cycle(state, inputs->t0_us, &inputs->speed, &outputs->lcc_status.header,
               &outputs->trajectory_sent, &outputs->trajectory, &outputs->lateral_limits_sent,
               &outputs->lateral_limits, true);
    outputs->trajectory.planner_id = PP_PLANNER_ID_LCC;
}

void pp_lkaelk_step(void *state, const pp_lka_elk_inputs_t *inputs, pp_ego_motion_fn ego_motion,
                    void *ego_motion_context, pp_lka_elk_outputs_t *outputs)
{
    (void)ego_motion;
    (void)ego_motion_context;
    memset(outputs, 0, sizeof *outputs);
    outputs->intervention_status_sent = true;
    stub_cycle(state, inputs->t0_us, &inputs->speed, &outputs->intervention_status.header,
               &outputs->trajectory_sent, &outputs->trajectory, NULL, NULL, false);
    outputs->trajectory.planner_id = PP_PLANNER_ID_LKA_ELK;
}
#endif

const char *pp_lcc_version(void) { return "stub_planner 1.0.0 commit 0000000 calibration none"; }
const char *pp_lkaelk_version(void) { return "stub_planner 1.0.0 commit 0000000 calibration none"; }

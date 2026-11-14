/*
 * Test double built against interfaces/c/pp_planner.h, for tests of eval/ only: that any
 * planner library plugs in (Software Qualification Test Specification 11) and that
 * conformance B0 finds contract faults. Not a planner: path_valid is always false and the
 * path is a straight line at the measured speed.
 *
 * Default: meets the contract. Each STUB_* define breaks one point on purpose:
 *   STUB_NO_STEP        pp_step missing (C1)
 *   STUB_NO_TRAJECTORY  never sends Trajectory or LateralLimits (C2)
 *   STUB_ACCEPT_WIDE    accepts a vehicle wider than 2.5 m (C2)
 *   STUB_COUNTER_STUCK  PathStatus counter does not increase (C2)
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

size_t pp_state_size(void) { return sizeof(stub_state_t); }

pp_init_result_t pp_init(void *state, size_t state_size, const pp_vehicle_config_t *vehicle_config)
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

#ifndef STUB_NO_STEP
void pp_step(void *state, const pp_planner_inputs_t *inputs, pp_ego_motion_fn ego_motion,
             void *ego_motion_context, pp_planner_outputs_t *outputs)
{
    stub_state_t *s = (stub_state_t *)state;
#ifdef STUB_GLOBAL_STATE
    uint8_t *counter = g_state.counter;
#else
    uint8_t *counter = s->counter;
#endif
    float v = 0.0F;
    (void)ego_motion;
    (void)ego_motion_context;
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
    if (inputs->speed.present && inputs->speed.message.header.valid
        && isfinite(inputs->speed.message.speed_mps)) {
        v = fminf(fmaxf(inputs->speed.message.speed_mps, 0.0F), 70.0F);
    }
    memset(outputs, 0, sizeof *outputs);

    outputs->path_status_sent = true;
    outputs->path_status.header.stamp_us = inputs->t0_us;
    outputs->path_status.header.counter = counter[1];
    outputs->path_status.header.valid = true;
#ifndef STUB_COUNTER_STUCK
    counter[1] = (uint8_t)(counter[1] + 1U);
#endif
#ifndef STUB_NO_TRAJECTORY
    outputs->lateral_limits_sent = true;
    outputs->lateral_limits.header.stamp_us = inputs->t0_us;
    outputs->lateral_limits.header.counter = counter[2]++;
    outputs->lateral_limits.header.valid = true;
    if (s->ok != 0U) {
        outputs->trajectory_sent = true;
        outputs->trajectory.header.stamp_us = inputs->t0_us;
        outputs->trajectory.header.counter = counter[0]++;
        outputs->trajectory.header.valid = true;
        outputs->trajectory.header.frame_id = PP_FRAME_ID_BASE_LINK;
        for (unsigned i = 0U; i < PP_TRAJECTORY_POINTS; ++i) {
            pp_trajectory_point_t *p = &outputs->trajectory.points[i];
            p->time_from_start = 0.1F * (float)i;
            p->pose.x = v * p->time_from_start;
            p->longitudinal_velocity_mps = v;
        }
#ifdef STUB_NAN
        outputs->trajectory.points[3].pose.y = NAN;
#endif
    }
#endif
}
#endif

const char *pp_version(void) { return "stub_planner 1.0.0 commit 0000000 calibration none"; }

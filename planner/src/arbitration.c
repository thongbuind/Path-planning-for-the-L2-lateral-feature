/* T9 Arbitration (Software Detailed Design 12). */

#include "arbitration.h"

#include <stddef.h>
#include <string.h>

static void publish_phases(const pp_arbitration_memory_t *mem, pp_arbitration_t *out)
{
    out->lka_phase = mem->intervention[PP_FUNCTION_LKA - 1U].phase;
    out->elk_phase = mem->intervention[PP_FUNCTION_ELK - 1U].phase;
}

void pp_arbitration_invalidate(pp_arbitration_memory_t *mem, pp_arbitration_t *out)
{
    for (size_t i = 0U; i < PP_INTERVENTIONS; i++) {
        pp_intervention_request_t *state = &mem->intervention[i];
        state->blocked = state->requested;                               /* PP-SWR-045 */
        if (state->phase == PP_INTERVENTION_PHASE_ACTIVE) {
            state->phase = PP_INTERVENTION_PHASE_NONE;
        }
        state->holding = false;
    }
    out->active_function = PP_ACTIVE_FUNCTION_NONE;                      /* PP-SWR-043 */
    out->starting = false;
    publish_phases(mem, out);
}

static void check_completion(pp_intervention_request_t *state, bool settled,
                             uint64_t t0_us, double hold_s)
{
    if (!settled) {
        state->holding = false;
        return;
    }
    if (!state->holding || (t0_us < state->hold_since_us)) {
        state->holding = true;
        state->hold_since_us = t0_us;
    }
    if ((double)(t0_us - state->hold_since_us) >= hold_s * 1.0e6) {
        state->phase = PP_INTERVENTION_PHASE_COMPLETED;                  /* PP-SWR-032, 090 */
        state->holding = false;
    }
}

void pp_arbitrate(pp_arbitration_memory_t *mem, const pp_arbitration_input_t *in,
                  pp_arbitration_t *out)
{
    (void)memset(out, 0, sizeof(*out));
    bool allowed[PP_INTERVENTIONS] = {false, false};
    const bool override = (in->requests != NULL) && in->requests->driver_override;
    for (size_t i = 0U; i < PP_INTERVENTIONS; i++) {
        pp_intervention_request_t *state = &mem->intervention[i];
        const pp_function_request_t *req = (in->requests == NULL) ? NULL : &in->requests->requests[i + 1U];
        const bool active = state->phase == PP_INTERVENTION_PHASE_ACTIVE;
        if ((req != NULL) && (req->state != PP_REQUEST_STATE_REQUEST)) {
            out->cancelled |= active;                                    /* PP-SWR-036, 037 */
            (void)memset(state, 0, sizeof(*state));                       /* PP-SWR-034, 041 */
            continue;
        }
        if (req == NULL) {
            out->cancelled |= active;
            continue;
        }
        const bool new_request = !state->requested;
        if (new_request) {
            state->requested = true;
            state->received_us = (in->requests_rx_us <= in->t0_us) ? in->requests_rx_us : in->t0_us;
            state->side = req->side;
            state->reason = req->elk_reason;
        }
        const uint64_t elapsed = (in->t0_us >= state->received_us) ? in->t0_us - state->received_us : 0U;
        if (active && !override && in->path_available && in->can_continue[i]
            && (elapsed <= PP_INTERVENTION_MAX_US)) {
            check_completion(state, in->can_finish[i], in->t0_us, in->hold_s);
        }
        if (state->phase == PP_INTERVENTION_PHASE_COMPLETED) {
            continue;
        }

        /* Do not let an ACTIVE sample remain in effect past the 10 s deadline. */
        const bool timeout = elapsed > (PP_INTERVENTION_MAX_US - PP_PLANNER_PERIOD_US);
        const bool late = (i == PP_FUNCTION_ELK - 1U) && new_request && in->elk_too_late;
        state->blocked |= timeout || late;                                /* PP-SWR-083, 089 */
        allowed[i] = !state->blocked && !override && (active ? in->can_continue[i] : in->can_start[i]);
        out->cancelled |= active && !allowed[i];
    }

    if (!in->path_available) {
        pp_arbitration_invalidate(mem, out);
        return;
    }
    if (allowed[PP_FUNCTION_ELK - 1U]) {
        out->active_function = PP_ACTIVE_FUNCTION_ELK;                    /* PP-SWR-030, 033 */
    } else if (allowed[PP_FUNCTION_LKA - 1U]) {
        out->active_function = PP_ACTIVE_FUNCTION_LKA;
    } else if (in->hwa_available && (in->requests != NULL)
               && (in->requests->requests[PP_FUNCTION_HWA].state == PP_REQUEST_STATE_REQUEST)) {
        out->active_function = PP_ACTIVE_FUNCTION_HWA;
    } else {
        /* No candidate; a usable path can still be published for handover. */
    }

    for (size_t i = 0U; i < PP_INTERVENTIONS; i++) {
        pp_intervention_request_t *state = &mem->intervention[i];
        if (out->active_function == (pp_active_function_t)(PP_ACTIVE_FUNCTION_LKA + i)) {
            out->starting = state->phase != PP_INTERVENTION_PHASE_ACTIVE;
            state->phase = PP_INTERVENTION_PHASE_ACTIVE;
        } else if (state->phase == PP_INTERVENTION_PHASE_ACTIVE) {
            state->phase = PP_INTERVENTION_PHASE_NONE;
            state->holding = false;
        } else {
            /* Preserve COMPLETED of a function while the other is active. */
        }
    }
    publish_phases(mem, out);
}

#include "selection.h"

#include <stddef.h>
#include <string.h>

#include "pp_core.h"

static void publish_phases(const pp_selection_memory_t *mem, pp_selection_t *out)
{
    out->lka_phase = mem->intervention[PP_FUNCTION_LKA - 1U].phase;
    out->elk_phase = mem->intervention[PP_FUNCTION_ELK - 1U].phase;
}

void pp_selection_invalidate(pp_selection_memory_t *mem, pp_selection_t *out)
{
    for (size_t i = 0U; i < PP_INTERVENTIONS; i++) {
        pp_intervention_request_t *state = &mem->intervention[i];
        state->blocked = state->requested;
        if (state->phase == PP_INTERVENTION_PHASE_ACTIVE) {
            state->phase = PP_INTERVENTION_PHASE_NONE;
        }
        state->holding = false;
    }
    out->active_function = PP_INTERVENTION_FUNCTION_NONE;
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
        state->phase = PP_INTERVENTION_PHASE_COMPLETED;
        state->holding = false;
    }
}

void pp_select(pp_selection_memory_t *mem, const pp_selection_input_t *in, pp_selection_t *out)
{
    (void)memset(out, 0, sizeof(*out));
    bool allowed[PP_INTERVENTIONS] = {false, false};
    const bool override = (in->requests != NULL) && in->requests->driver_override;
    for (size_t i = 0U; i < PP_INTERVENTIONS; i++) {
        pp_intervention_request_t *state = &mem->intervention[i];
        const pp_function_request_t *req = (in->requests == NULL) ? NULL : &in->requests->requests[i + 1U];
        const bool active = state->phase == PP_INTERVENTION_PHASE_ACTIVE;
        if ((req != NULL) && (req->state != PP_REQUEST_STATE_REQUEST)) {
            out->cancelled |= active;
            (void)memset(state, 0, sizeof(*state));
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
        if (active && !override && in->path_available && in->can_continue[i]) {
            check_completion(state, in->can_finish[i], in->t0_us, in->hold_s);
        }
        if (state->phase == PP_INTERVENTION_PHASE_COMPLETED) {
            continue;
        }

        /* Kết thúc theo COMPLETED, khi REQUEST rời hoặc khi mất điều kiện duy trì. Không cắt theo
         * thời lượng (PP-TS-016). */
        const bool late = (i == PP_FUNCTION_ELK - 1U) && new_request && in->elk_too_late;
        state->blocked |= late;
        allowed[i] = !state->blocked && !override && (active ? in->can_continue[i] : in->can_start[i]);
        out->cancelled |= active && !allowed[i];
    }

    if (!in->path_available) {
        pp_selection_invalidate(mem, out);
        return;
    }
    if (allowed[PP_FUNCTION_ELK - 1U]) {
        out->active_function = PP_INTERVENTION_FUNCTION_ELK;
    } else if (allowed[PP_FUNCTION_LKA - 1U]) {
        out->active_function = PP_INTERVENTION_FUNCTION_LKA;
    } else {
    }

    for (size_t i = 0U; i < PP_INTERVENTIONS; i++) {
        pp_intervention_request_t *state = &mem->intervention[i];
        if (out->active_function == (pp_intervention_function_t)(PP_INTERVENTION_FUNCTION_LKA + i)) {
            out->starting = state->phase != PP_INTERVENTION_PHASE_ACTIVE;
            state->phase = PP_INTERVENTION_PHASE_ACTIVE;
        } else if (state->phase == PP_INTERVENTION_PHASE_ACTIVE) {
            state->phase = PP_INTERVENTION_PHASE_NONE;
            state->holding = false;
        } else {
            /* Giữ COMPLETED của một chức năng trong khi chức năng khác ACTIVE. */
        }
    }
    publish_phases(mem, out);
}

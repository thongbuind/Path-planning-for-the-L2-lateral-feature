#ifndef PP_SELECTION_H
#define PP_SELECTION_H

#include <stdbool.h>
#include <stdint.h>

#include "pp_types.h"

#define PP_INTERVENTIONS (2U)

typedef struct {
    bool requested;
    bool blocked;
    uint64_t received_us;
    pp_side_t side;
    pp_elk_reason_t reason;
    pp_intervention_phase_t phase;
    bool holding;
    uint64_t hold_since_us;
} pp_intervention_request_t;

typedef struct {
    pp_intervention_request_t intervention[PP_INTERVENTIONS];
} pp_selection_memory_t;

typedef struct {
    const pp_function_requests_t *requests;
    uint64_t t0_us;
    uint64_t requests_rx_us;
    bool path_available;
    bool can_start[PP_INTERVENTIONS];
    bool can_continue[PP_INTERVENTIONS];
    bool can_finish[PP_INTERVENTIONS];
    bool elk_too_late;
    double hold_s;
} pp_selection_input_t;

typedef struct {
    pp_intervention_function_t active_function;
    pp_intervention_phase_t lka_phase;
    pp_intervention_phase_t elk_phase;
    bool starting;
    bool cancelled;
} pp_selection_t;

void pp_select(pp_selection_memory_t *mem, const pp_selection_input_t *in, pp_selection_t *out);

/* Nếu tầng sau từ chối output, giữ latch COMPLETED và chỉ cho vào lại sau REQUEST mới. */
void pp_selection_invalidate(pp_selection_memory_t *mem, pp_selection_t *out);

#endif

/*
 * T9 Intervention selection of the LKA/ELK planner (Software Detailed Design 12): which of
 * LKA and ELK drives (ELK before LKA), the phase of each, and when each ends. The choice
 * between the two planners belongs to the arbitrator of the system (PP-ASM-022), not here.
 */

#ifndef PP_SELECTION_H
#define PP_SELECTION_H

#include <stdbool.h>
#include <stdint.h>

#include "pp_types.h"

#define PP_INTERVENTIONS (2U)            /* slot 0 = LKA, slot 1 = ELK */

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
    const pp_function_requests_t *requests;  /* NULL if unusable */
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
    bool cancelled;                      /* prior intervention released this tick */
} pp_selection_t;

void pp_select(pp_selection_memory_t *mem, const pp_selection_input_t *in, pp_selection_t *out);

/* Output rejected downstream. Keep completion latches, require a new request after recovery. */
void pp_selection_invalidate(pp_selection_memory_t *mem, pp_selection_t *out);

#endif /* PP_SELECTION_H */

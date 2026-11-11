/*
 * T9 Arbitration (Software Detailed Design section 12).
 *
 * Implemented: steps 1, 4 and 6 for HWA. Not yet: LKA and ELK, intervention phases
 * and COMPLETED flags (steps 2, 3, 5), so LKA and ELK requests are ignored.
 */

#ifndef PP_ARBITRATION_H
#define PP_ARBITRATION_H

#include <stdbool.h>

#include "pp_types.h"

/* requests[3] = HWA, LKA, ELK (Interface Control Document 5.6). */
#define PP_FUNCTION_HWA (0U)
#define PP_FUNCTION_LKA (1U)
#define PP_FUNCTION_ELK (2U)

typedef struct {
    pp_active_function_t active_function;
    pp_intervention_phase_t intervention_phase;
} pp_arbitration_t;

/* requests NULL: FunctionRequests not usable, all functions off (step 1). */
void pp_arbitrate(const pp_function_requests_t *requests, bool path_valid,
                  pp_arbitration_t *out);

#endif /* PP_ARBITRATION_H */

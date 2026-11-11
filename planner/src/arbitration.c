/* T9 Arbitration (arbitration.h). PP-SWR-030, 038, 042, 043. */

#include "arbitration.h"

#include <stddef.h>

void pp_arbitrate(const pp_function_requests_t *requests, bool path_valid,
                  pp_arbitration_t *out)
{
    out->active_function = PP_ACTIVE_FUNCTION_NONE;
    out->intervention_phase = PP_INTERVENTION_PHASE_NONE;

    if (path_valid && (requests != NULL)
        && (requests->requests[PP_FUNCTION_HWA].state == PP_REQUEST_STATE_REQUEST)) {
        out->active_function = PP_ACTIVE_FUNCTION_HWA;   /* Step 4 */
    }
    /* Step 6: path not valid means NONE (PP-SWR-043). */
}

/* T1 Input check (input_check.h). PP-SWR-126 to 134. */

#include "input_check.h"

bool pp_input_usable(bool present, bool header_valid, uint64_t rx_us, uint64_t stamp_us,
                     uint64_t t0_us, uint64_t timeout_us, uint64_t max_age_us)
{
    bool ok = present && header_valid;

    /* Receive timeout from the delivery time of the newest message. */
    if (ok && (rx_us <= t0_us)) {
        ok = (t0_us - rx_us) <= timeout_us;
    }
    /* Stamp in the future beyond the tolerance. */
    if (ok && (stamp_us > t0_us)) {
        ok = (stamp_us - t0_us) <= PP_FUTURE_STAMP_TOLERANCE_US;
    }
    /* Age = now - stamp (PP-SWR-131 for the lane model). */
    if (ok && (stamp_us < t0_us)) {
        ok = (t0_us - stamp_us) <= max_age_us;
    }
    return ok;
}

/* T1 Input check (input_check.h). PP-SWR-126 to 134. */

#include "input_check.h"

#include "pp_types.h"

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

bool pp_counter_accept(pp_counter_check_t *check, bool present, uint64_t rx_us,
                       uint8_t counter, bool header_valid, uint32_t max_delta, bool resync)
{
    bool accept = false;
    if (present && (!check->seen || (rx_us != check->last_rx_us))) {
        /* PP-SWR-129, 130: step 1 to max_delta is a usable message, others count as lost. */
        const uint32_t step = ((uint32_t)counter + PP_COUNTER_MODULO
                               - (uint32_t)check->last_counter) % PP_COUNTER_MODULO;
        /* Resync takes a larger step, never a repeated or stuck counter (step 0). */
        const bool in_sequence = !check->seen || ((step >= 1U) && (resync || (step <= max_delta)));
        accept = in_sequence && header_valid;
        check->seen = true;
        check->last_rx_us = rx_us;
        check->last_counter = counter;
    }
    return accept;
}

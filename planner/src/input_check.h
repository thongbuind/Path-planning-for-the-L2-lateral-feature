/* T1 Input check (Software Detailed Design section 4, step 1). */

#ifndef PP_INPUT_CHECK_H
#define PP_INPUT_CHECK_H

#include <stdbool.h>
#include <stdint.h>

/* A stamp more than this far ahead of t0 makes the input invalid (Software Detailed Design 4). */
#define PP_FUTURE_STAMP_TOLERANCE_US (10000ULL)

/* For CAN signals: stamp is the receive time, so only the timeout applies (ICD 4). */
#define PP_NO_AGE_LIMIT (UINT64_MAX)

/*
 * Interface Control Document 4, "Kiểm tra ở bên nhận": the newest message is usable
 * when it was received, is valid, is within the receive timeout (from rx_us), is not
 * older than max_age (from stamp_us) and is not stamped in the future.
 * For a pub/sub input the message checked is the last accepted one (pp_counter_accept).
 * CAN frames are checked by the receive layer (ICD 5.3).
 */
bool pp_input_usable(bool present, bool header_valid, uint64_t rx_us, uint64_t stamp_us,
                     uint64_t t0_us, uint64_t timeout_us, uint64_t max_age_us);

/* Counter check of one pub/sub input, kept between cycles. */
typedef struct {
    bool seen;            /* a message has been delivered */
    uint64_t last_rx_us;  /* delivery time of the last delivered message */
    uint8_t last_counter; /* counter of the last delivered message */
} pp_counter_check_t;

/*
 * Interface Control Document 4, counter of pub/sub messages, with the statuses of
 * AUTOSAR E2E Profile 5. Returns true when the delivered message replaces the message
 * held for the input: it is new (rx_us changed), valid, and its counter step from the
 * last delivered message is 1 to max_delta (OK, OKSOMELOST). Step 0 (REPEATED: repeated
 * or stuck counter), a larger step (WRONGSEQUENCE) and valid = false keep the held
 * message, as if the message were lost. The counter is resynchronised to every delivered
 * message, so the next message with step 1 is accepted. The first message, and the
 * first one after the held message timed out (resync: the input already counts as lost,
 * as the growing MaxDeltaCounter of E2E Profiles 1, 2), is accepted when valid and its
 * step is not 0.
 */
bool pp_counter_accept(pp_counter_check_t *check, bool present, uint64_t rx_us,
                       uint8_t counter, bool header_valid, uint32_t max_delta, bool resync);

#endif /* PP_INPUT_CHECK_H */

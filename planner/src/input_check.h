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
 * Counter and CRC checks are not done yet.
 */
bool pp_input_usable(bool present, bool header_valid, uint64_t rx_us, uint64_t stamp_us,
                     uint64_t t0_us, uint64_t timeout_us, uint64_t max_age_us);

#endif /* PP_INPUT_CHECK_H */

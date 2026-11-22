#ifndef PP_INPUT_CHECK_H
#define PP_INPUT_CHECK_H

#include <stdbool.h>
#include <stdint.h>

#define PP_FUTURE_STAMP_TOLERANCE_US (10000ULL)

/* Với CAN, stamp là thời điểm nhận nên chỉ dùng receive timeout (ICD 4). */
#define PP_NO_AGE_LIMIT (UINT64_MAX)

/* Kiểm lần lượt trạng thái nhận, valid, timeout theo rx_us, tuổi và stamp tương lai (ICD 4). */
bool pp_input_usable(bool present, bool header_valid, uint64_t rx_us, uint64_t stamp_us,
                     uint64_t t0_us, uint64_t timeout_us, uint64_t max_age_us);

typedef struct {
    bool seen;
    uint64_t last_rx_us;
    uint8_t last_counter;
} pp_counter_check_t;

/* Trả true khi frame đến được dùng thay mẫu đang giữ. Counter theo quy ước AUTOSAR E2E Profile 5
 * (ICD 4). */
bool pp_counter_accept(pp_counter_check_t *check, bool present, uint64_t rx_us,
                       uint8_t counter, bool header_valid, uint32_t max_delta, bool resync);

#endif

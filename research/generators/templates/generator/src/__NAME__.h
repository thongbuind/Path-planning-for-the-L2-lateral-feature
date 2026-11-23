/* T7 __NAME__: <một câu mô tả thuật toán>. Generator lab của PP-TS-031. */

#ifndef LAB___UPPER___H
#define LAB___UPPER___H

#include <stdint.h>

#define PP_T7_SUPPORT_FLOOR (1)  /* 1 nếu LCC đặt sàn PP-SWR-006 cho path của generator này. */

typedef struct {
    uint32_t work;  /* Telemetry: khối lượng việc của chu kỳ gần nhất. */
    uint32_t fallback;  /* Telemetry: lý do dùng nghiệm thay thế; 0 nếu không. */
} pp_t7_ws_t;

#endif

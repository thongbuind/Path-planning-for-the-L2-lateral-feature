#ifndef PP_LATERAL_STATE_H
#define PP_LATERAL_STATE_H

#include "reference_line.h"

typedef struct {
    double d;  /* [m] Độ lệch ngang khỏi đường tham chiếu, dương về trái. */
    double d_dot;
    double d_ddot;
    double heading;
} pp_lateral_state_t;

/* foot là mốc s = 0. v_y đo tại base_link, yaw_rate lấy từ IMU. */
void pp_lateral_state(const pp_ref_point_t *foot, double v, double v_y, double yaw_rate,
                      pp_lateral_state_t *out);

#endif

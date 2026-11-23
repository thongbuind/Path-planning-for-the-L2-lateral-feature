/* T7 quintic_duration: đa thức bậc 5 d(t) từ trạng thái đầu tới (d_target, 0, 0), tăng thời lượng
 * từng 0,25 s tới khi path đạt giới hạn a_y và jerk mong muốn (PP-TS-003, Software Detailed Design
 * mục 10). */

#ifndef PP_T7_QUINTIC_DURATION_H
#define PP_T7_QUINTIC_DURATION_H

#define PP_T7_QUINTIC_DURATION (1)
#define PP_T7_SUPPORT_FLOOR (1)

typedef struct {
    unsigned char unused;  /* Không giữ gì giữa các chu kỳ; C11 không cho struct rỗng. */
} pp_t7_ws_t;

#endif

/* QP T7 dùng jerk ngang theo lưới thời gian, với biến nới mềm để giữ bài toán khả thi (PP-TS-003). */

#ifndef PP_QP_H
#define PP_QP_H

#include <stdbool.h>

#include "lateral_state.h"
#include "pp_calibration.h"
#include "pp_path.h"

#define PP_QP_N (PP_TRAJECTORY_POINTS - 1U)
#define PP_QP_ROWS (8U * PP_QP_N)

typedef struct {
    double ma[PP_QP_N][PP_QP_N];
    double md[PP_QP_N][PP_QP_N];
    double mv[PP_QP_N];
    double p[PP_QP_N][PP_QP_N];
    double l[PP_QP_N][PP_QP_N];
    double x[3U * PP_QP_N];
    double z[PP_QP_ROWS];
    double y[PP_QP_ROWS];
    double rho;
    double d_target;
    bool warm;
} pp_qp_ws_t;

/* Mảng ứng với t_1 tới t_30; phần tử k là t_{k+1}. */
typedef struct {
    pp_lateral_state_t start;
    double d_target;
    double v[PP_QP_N];
    double kappa[PP_QP_N];
    double d_max[PP_QP_N];  /* Hành lang [m], dương về trái. */
    double d_min[PP_QP_N];
    double d_old[PP_QP_N];
    bool has_old[PP_QP_N];
    double ay_limit;
    double jerk_limit;
    double dkappa[PP_QP_N];
} pp_qp_problem_t;

void pp_qp_reset(pp_qp_ws_t *ws);

/* Ghi trạng thái bắt đầu vào điểm 0. Trả false nếu kết quả có giá trị không hữu hạn. */
bool pp_generate_qp(pp_qp_ws_t *ws, const pp_calibration_t *cal, const pp_qp_problem_t *pb,
                    pp_lateral_path_t *out);

#endif

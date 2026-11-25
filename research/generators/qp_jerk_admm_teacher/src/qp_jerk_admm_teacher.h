/* T7 qp_jerk_admm_teacher: qp_jerk_admm với trọng số mặc định lái xe; mỗi chu kỳ ghi thêm vào ws đặc trưng
 * MLP và nhãn là nghiệm ADMM 1000 vòng của cùng bài toán (chuỗi warm start riêng, như
 * qp_jerk_admm_it1000_ref), kèm residual và mức vi phạm ràng buộc. Công cụ sinh dữ liệu của luồng C
 * (kind tool), không so trên dashboard. Python đọc bản ghi qua pp_lcc_t7_workspace (research/generators/mlp). */

#ifndef LAB_QP_JERK_ADMM_TEACHER_H
#define LAB_QP_JERK_ADMM_TEACHER_H

#include "generators/qp.h"
#include "mlp_features.h"

#define PP_T7_SUPPORT_FLOOR (0)  /* Giống qp_jerk_admm. */

#define TEACHER_REF_ITERS (1000U)  /* Số vòng của nghiệm nhãn. */
#define TEACHER_LAYOUT (31001.0)  /* Mã bố cục bản ghi; đổi khi đổi bố cục (mlp/common.py). */

/* Bố cục bản ghi: mảng double, chỉ số dưới đây. Bài toán QP chép nguyên để tính lại đặc trưng bằng Python và
 * để giải lại offline (nhãn lưới trọng số của qp_jerk_admm_mlp_weights). */
#define TR_LAYOUT (0U)
#define TR_SIZE (1U)  /* Số double của bản ghi. */
#define TR_COUNT (2U)  /* Số lần pp_t7_generate từ lúc khởi tạo state; không về 0 khi reset. */
#define TR_LABEL_OK (3U)  /* 1 nếu nghiệm 1000 vòng hữu hạn. */
#define TR_DRIVE_OK (4U)  /* 1 nếu nghiệm lái (qp_iters vòng) hữu hạn. */
#define TR_PRIMAL (5U)  /* Residual nguyên thủy tương đối của nghiệm nhãn (pp_qp_stats). */
#define TR_DUAL (6U)  /* Residual đối ngẫu tương đối của nghiệm nhãn. */
#define TR_VIOLATION (7U)  /* max(TR_VIOL_AY, TR_VIOL_JERK). */
#define TR_VIOL_AY (8U)  /* Vi phạm lớn nhất của hàng a_y cứng, đơn vị hàng (≈ m/s²). */
#define TR_VIOL_JERK (9U)  /* Vi phạm lớn nhất của hàng jerk cứng [m/s³]. */
#define TR_SLACK (10U)  /* Tổng trị tuyệt đối biến nới của nghiệm nhãn. */
#define TR_FROM_OLD (11U)
#define TR_RECENTERING (12U)
#define TR_FOLLOW (13U)
#define TR_FROM_CAR (14U)
#define TR_SHIFT_S (15U)  /* old->shift_s; NAN nếu không có path cũ. */
#define TR_REF_WARM (16U)  /* 1 nếu chuỗi nhãn đang warm trước lần giải. */
#define TR_DRIVE_WARM (17U)  /* 1 nếu chuỗi lái đang warm trước lần giải. */
#define TR_REF_DTARGET (18U)  /* d_target của lần giải nhãn trước (dời path cũ trong bài toán). */
#define TR_DRIVE_ITERS (19U)
#define TR_FEATURES (20U)
#define TR_LABEL (TR_FEATURES + MLP_FEATURES)  /* Jerk của nghiệm 1000 vòng, PP_QP_N phần tử. */
#define TR_DRIVE (TR_LABEL + PP_QP_N)  /* Jerk của nghiệm lái. */
#define TR_PROBLEM (TR_DRIVE + PP_QP_N)
/* Bài toán: start (d, d', d'', heading), d_target, rồi v, kappa, dkappa, d_max, d_min, d_old, has_old (mỗi
 * khối PP_QP_N), ay_limit, jerk_limit. */
#define TR_PROBLEM_SIZE (5U + (7U * PP_QP_N) + 2U)
#define TR_DOUBLES (TR_PROBLEM + TR_PROBLEM_SIZE)

/* Phần warm start của chuỗi nhãn. Ma trận của pp_qp_ws_t tính lại mỗi lần giải, nên chuỗi nhãn giải trên
 * pp_qp_ws_t tạm trong stack: state của LCC nhỏ hơn 64 KB như test_lcc_step đòi. */
typedef struct {
    double x[3U * PP_QP_N];
    double z[PP_QP_ROWS];
    double y[PP_QP_ROWS];
    double rho;
    double d_target;
    bool warm;
} teacher_chain_t;

typedef struct {
    double record[TR_DOUBLES];  /* Trường đầu: Python đọc phần đầu của ws. */
    pp_qp_ws_t qp;  /* Chuỗi lái, giống hệt qp_jerk_admm. */
    teacher_chain_t ref;  /* Chuỗi nhãn 1000 vòng. */
} pp_t7_ws_t;

/* Chép bài toán vào bản ghi theo bố cục TR_PROBLEM. */
void teacher_pack_problem(const pp_qp_problem_t *pb, double out[TR_PROBLEM_SIZE]);

/* Kiểm nghiệm của ws (sau lần giải trên pb, d_target_before và warm_before là trạng thái trước lần giải):
 * residual đối ngẫu tương đối, vi phạm hàng a_y và jerk cứng. Giới hạn tính lại như qp.c. */
void teacher_check(const pp_qp_ws_t *ws, const pp_calibration_t *cal, const pp_qp_problem_t *pb,
                   double d_target_before, bool warm_before, double *dual, double *viol_ay, double *viol_jerk);

#endif

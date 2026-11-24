/* Đặc trưng đầu vào của MLP luồng C (PP-TS-031), dùng chung cho teacher và mọi generator MLP để hai bên
 * tính giống hệt nhau. Chỉ lấy từ bài toán QP dựng từ input của planner (pp_t7_qp_problem). Bản Python
 * tham chiếu: research/generators/mlp/common.py (features). */

#ifndef LAB_MLP_FEATURES_H
#define LAB_MLP_FEATURES_H

#include "generators/qp.h"

/* 0–20: 21 đặc trưng của pilot (pilots/pilot_qp.inc); 21–26: hành lang tại k = 9, 19, 29; 27: giới hạn a_y.
 *  0 d0, 1 d0', 2 d0'', 3 d_target, 4 d_min[0], 5 d_max[0],
 *  6 tỉ lệ bước có path cũ, 7 d_old đầu tiên, 8 d_old cuối cùng,
 *  9–12 v, 13–16 v²κ, 17–20 v³κ' tại k = 0, 9, 19, 29,
 *  21 d_min[9], 22 d_max[9], 23 d_min[19], 24 d_max[19], 25 d_min[29], 26 d_max[29], 27 ay_limit. */
#define MLP_FEATURES (28U)
#define MLP_OUTPUTS (PP_QP_N)

/* Phép soi gương d → −d (κ → −κ) đổi bài toán QP thành bài toán đối xứng, nghiệm jerk đổi dấu. Trên đặc
 * trưng: nhóm lẻ đổi dấu, cặp hành lang (d_min, d_max) → (−d_max, −d_min), nhóm chẵn giữ nguyên. */
#define MLP_EVEN (6U)  /* 6, 9, 10, 11, 12, 27 */
#define MLP_ODD (14U)  /* 0, 1, 2, 3, 7, 8, 13–20 */
#define MLP_PAIRS (4U)  /* (4, 5), (21, 22), (23, 24), (25, 26) */

void mlp_features(const pp_qp_problem_t *pb, double out[MLP_FEATURES]);

#endif

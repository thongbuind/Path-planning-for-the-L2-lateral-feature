/* T7 mlp_jerk_direct: MLP xuất thẳng chuỗi jerk ngang trên 30 bước từ input của planner, kẹp vào trần jerk, tích
 * phân từ trạng thái đầu ra path; T10 và T4 chung của LCC xử lý tiếp (PP-TS-025 V4, đối chứng của PP-TS-031).
 * Không có QP và không có nghiệm thay thế: đầu vào ngoài miền thì không có path. Telemetry: work là số lần suy
 * luận; fallback là lý do không có path (generator.yaml); infer_ops là số phép nhân cộng. */

#ifndef LAB_MLP_JERK_DIRECT_H
#define LAB_MLP_JERK_DIRECT_H

#include <stdint.h>

/* 0: không đặt sàn PP-SWR-006. Như qp_jerk_admm (teacher): nhãn đã mang hành vi giữ a_y ở trần trong cua gắt,
 * và đối chứng phải cho thấy MLP tự làm được gì, không có lưới an toàn riêng mà QP không có. */
#define PP_T7_SUPPORT_FLOOR (0)

#define MJD_NOT_FINITE_PATH (3U)

typedef struct {
    uint32_t work;  /* Telemetry: số lần suy luận của chu kỳ gần nhất. */
    uint32_t fallback;  /* Telemetry: lý do không có path; 0 nếu có. */
    uint32_t infer_ops;  /* Telemetry: phép nhân cộng của MLP. */
    uint32_t clamped;  /* Số bước jerk bị kẹp ở chu kỳ gần nhất (chẩn đoán trong unit test). */
} pp_t7_ws_t;

#endif

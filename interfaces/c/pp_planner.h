/* Caller cấp state riêng và căn theo PP_STATE_ALIGNMENT cho mỗi planner (ICD 4, PP-ADR-016). */

#ifndef PP_PLANNER_H
#define PP_PLANNER_H

#include <stddef.h>

#include "pp_types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define PP_STATE_ALIGNMENT (8U)

/* EgoMotionQuery trả lời đồng bộ trong chu kỳ gọi. Planner chuyển nguyên con trỏ context (ICD
 * 5.5). */
typedef void (*pp_ego_motion_fn)(void *context,
                                 const pp_ego_motion_request_t *request,
                                 pp_ego_motion_response_t *response);


size_t pp_lcc_state_size(void);

/* Gọi lúc khởi động. vehicle_config = NULL khi chưa có dữ liệu. Khởi tạo khác OK thì không phát
 * Trajectory (PP-SWR-146). */
pp_init_result_t pp_lcc_init(void *state, size_t state_size,
                             const pp_vehicle_config_t *vehicle_config);

/* Gọi mỗi PP_PLANNER_PERIOD_US tại inputs->t0_us. Hàm điền mọi trường output. */
void pp_lcc_step(void *state,
                 const pp_lcc_inputs_t *inputs,
                 pp_ego_motion_fn ego_motion,
                 void *ego_motion_context,
                 pp_lcc_outputs_t *outputs);

/* Chuỗi nhận diện không đổi và có thể đọc trước khi khởi tạo (R79 Phụ lục 6, mục 3.3.5). */
const char *pp_lcc_version(void);


size_t pp_lkaelk_state_size(void);

pp_init_result_t pp_lkaelk_init(void *state, size_t state_size,
                                const pp_vehicle_config_t *vehicle_config);

void pp_lkaelk_step(void *state,
                    const pp_lka_elk_inputs_t *inputs,
                    pp_ego_motion_fn ego_motion,
                    void *ego_motion_context,
                    pp_lka_elk_outputs_t *outputs);

const char *pp_lkaelk_version(void);

#ifdef __cplusplus
}
#endif

#endif

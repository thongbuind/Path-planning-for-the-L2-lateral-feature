/*
 * Call contract of the two path planners (Interface Control Document section 4,
 * "Contract gọi hàm của planner"; PP-ADR-013, PP-ADR-016). C11.
 *
 * The LCC planner (pp_lcc_*) and the LKA/ELK planner (pp_lkaelk_*) have the same four
 * calls with different input and output types. Each is built as its own library and
 * exports only its own family; the two share no state at run time.
 *
 * The caller provides the state memory. A planner does not allocate memory, read files,
 * read the system clock or use global variables.
 *
 * Typical use of one planner:
 *   static uint64_t memory[...];                          // >= pp_lcc_state_size() bytes
 *   pp_lcc_init(memory, sizeof memory, &vehicle_config);  // once at start-up
 *   every 25 ms at t0: pp_lcc_step(memory, &inputs, ego_motion, ctx, &outputs);
 */

#ifndef PP_PLANNER_H
#define PP_PLANNER_H

#include <stddef.h>

#include "pp_types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* State memory must be aligned to this many bytes. */
#define PP_STATE_ALIGNMENT (8U)

/*
 * EgoMotionQuery (Interface Control Document 5.5): the planner calls it within
 * a step and gets the answer in the same cycle. `context` is passed through.
 */
typedef void (*pp_ego_motion_fn)(void *context,
                                 const pp_ego_motion_request_t *request,
                                 pp_ego_motion_response_t *response);

/* ---- LCC planner (library pp_lcc) ---- */

/* Bytes of state memory the caller must provide. */
size_t pp_lcc_state_size(void);

/*
 * Once at start-up. vehicle_config NULL means VehicleConfig is missing.
 * Anything but PP_INIT_RESULT_OK: pp_lcc_step never sends a Trajectory (PP-SWR-146).
 */
pp_init_result_t pp_lcc_init(void *state, size_t state_size,
                             const pp_vehicle_config_t *vehicle_config);

/* Every cycle (PP_PLANNER_PERIOD_US) at inputs->t0_us. Fills every field of outputs. */
void pp_lcc_step(void *state,
                 const pp_lcc_inputs_t *inputs,
                 pp_ego_motion_fn ego_motion,
                 void *ego_motion_context,
                 pp_lcc_outputs_t *outputs);

/*
 * Identification of this build (R79 Annex 6 3.3.5): constant string
 * "pp_lcc <version> commit <source commit> calibration <data set id>".
 * The same for every call; may be called at any time.
 */
const char *pp_lcc_version(void);

/* ---- LKA/ELK planner (library pp_lkaelk) ---- */

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

#endif /* PP_PLANNER_H */

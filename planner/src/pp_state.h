/* Private state of the planner. Lives in memory the caller provides (PP-ADR-013). */

#ifndef PP_STATE_H
#define PP_STATE_H

#include <stdbool.h>
#include <stdint.h>

#include "curvature.h"
#include "feasibility.h"
#include "pp_calibration.h"
#include "pp_types.h"
#include "reference_line.h"
#include "stitching.h"

/* Marks memory that pp_init has set up. */
#define PP_STATE_MAGIC (0x50504C31UL) /* "PPL1" */

typedef struct {
    uint32_t magic;
    bool initialized;               /* pp_init returned OK */
    pp_vehicle_config_t vehicle;    /* Copy of VehicleConfig, read once (ICD 5.8) */
    const pp_calibration_t *cal;    /* Built-in calibration data set */
    uint8_t trajectory_counter;     /* Header counters, wrap at 256 (ICD 4) */
    uint8_t path_status_counter;
    uint8_t lateral_limits_counter;
    pp_reference_memory_t ref_mem;  /* T2 memory: lane width (Software Detailed Design 5) */
    pp_previous_path_t prev_path;   /* T4: path sent in the previous cycle */
    pp_limit_flag_t limit_flag;     /* T10: lateral_limit_reached */
    bool recentering;               /* T7: HWA brings the car back to the centre */
    pp_active_function_t last_active; /* T9 result of the previous cycle */
    bool has_prev_t0;               /* t0 of the previous cycle, for ego-motion between cycles */
    uint64_t prev_t0_us;
    pp_curvature_t curv;            /* T5 estimate */
    bool t5_has_stamp;              /* Capture stamp of the last frame T5 used */
    uint64_t t5_stamp_us;
} pp_state_t;

#endif /* PP_STATE_H */

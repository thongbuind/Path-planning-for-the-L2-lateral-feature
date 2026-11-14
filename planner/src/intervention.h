/* Geometry and quintic path for LKA and ELK (Software Detailed Design 10). */
#ifndef PP_INTERVENTION_H
#define PP_INTERVENTION_H

#include <stdbool.h>
#include <stdint.h>

#include "arbitration.h"
#include "feasibility.h"
#include "generators/quintic.h"
#include "stitching.h"

typedef struct {
    pp_boundary_t edge[PP_ROAD_EDGES];
    double width[PP_ROAD_EDGES];
} pp_edge_memory_t;

typedef struct {
    pp_quintic_t profile;
    uint64_t start_us;
} pp_intervention_path_t;

typedef struct {
    bool valid;
    uint64_t stamp_us;
    double value;
    double rate;
} pp_lateral_velocity_history_t;

/* Align the estimate used in PP-SWR-032/090 with the current cycle. */
double pp_intervention_vy_at_t0(pp_lateral_velocity_history_t *history,
                                const pp_vehicle_state_estimate_t *state, uint64_t t0_us);

/* PP-SWR-047: road edges of the ego lane, with measured opposite boundary or
 * remembered width. This geometry is local to ELK. */
void pp_road_edge_references(pp_edge_memory_t *mem, const pp_lane_at_t0_t *lane,
                            const pp_reference_line_t *camera_ref, const pp_motion_t *motion,
                            const pp_vehicle_config_t *vehicle, const pp_calibration_t *cal,
                            pp_reference_line_t refs[PP_ROAD_EDGES]);

bool pp_intervention_line_trusted(const pp_lane_at_t0_t *lane, const pp_reference_line_t *ref,
                                  pp_side_t side, const pp_vehicle_config_t *vehicle,
                                  const pp_calibration_t *cal);
bool pp_elk_past_marking(const pp_lane_at_t0_t *lane, pp_side_t side,
                         const pp_vehicle_config_t *vehicle, const pp_calibration_t *cal);

bool pp_intervention_settled(const pp_reference_line_t *ref, const pp_lateral_state_t *ego,
                             const pp_old_path_t *old, double v, double v_y, double yaw_rate,
                             const pp_vehicle_config_t *vehicle, const pp_calibration_t *cal);
bool pp_intervention_start_exception(const pp_reference_line_t *ref,
                                     const pp_lateral_state_t *ego, const pp_old_path_t *old);

void pp_intervention_begin(pp_intervention_path_t *path, const pp_intervention_request_t *req,
                           double tlc, uint64_t t0_us, const pp_reference_line_t *ref,
                           const pp_lateral_state_t *start, const pp_speed_profile_t *speed,
                           const pp_function_limits_t *limits, const pp_vehicle_config_t *vehicle,
                           const pp_calibration_t *cal, bool elk);
void pp_intervention_sample(const pp_intervention_path_t *path, uint64_t t0_us,
                            pp_lateral_path_t *out);

#endif /* PP_INTERVENTION_H */

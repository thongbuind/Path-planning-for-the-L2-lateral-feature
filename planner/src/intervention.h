#ifndef PP_INTERVENTION_H
#define PP_INTERVENTION_H

#include <stdbool.h>
#include <stdint.h>

#include "feasibility.h"
#include "generators/quintic.h"
#include "selection.h"
#include "stitching.h"

typedef struct {
    pp_boundary_t edge[PP_ROAD_EDGES];
    double width[PP_ROAD_EDGES];
} pp_edge_memory_t;

typedef struct {
    pp_quintic_t profile;
    pp_quintic_t back;
    bool two_phase;
    /* PP-TS-030 V2: đoạn về nhanh lưu dạng đảo thời gian, rồi `back` là đoạn về chậm. */
    pp_quintic_t fast_reversed;
    bool two_speed;
    uint64_t start_us;
} pp_intervention_path_t;

typedef struct {
    bool valid;
    uint64_t stamp_us;
    double value;
    double rate;
} pp_lateral_velocity_history_t;

/* Corridor được chốt khi bắt đầu can thiệp và cập nhật theo ego-motion cùng biên nguy hiểm
 * (PP-ADR-019). */
typedef struct {
    bool valid;
    pp_reference_line_t ref;
    bool pending;
    double pending_s;
    double toward_s;
} pp_corridor_t;

void pp_corridor_reset(pp_corridor_t *c);

/* motion là ego-motion từ chu kỳ trước. NULL khi không xác định được. */
const pp_reference_line_t *pp_corridor_update(pp_corridor_t *c, const pp_reference_line_t *live,
                                              const pp_motion_t *motion, bool started,
                                              pp_side_t side, double front_x,
                                              const pp_calibration_t *cal, double dt);

double pp_intervention_vy_at_t0(pp_lateral_velocity_history_t *history,
                                const pp_vehicle_state_estimate_t *state, uint64_t t0_us);

/* PP-SWR-047: hình học riêng cho ELK dựng từ mép ego và biên đối diện đã đo hoặc bề rộng lưu trước
 * đó. */
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

void pp_intervention_begin(pp_intervention_path_t *path, const pp_intervention_request_t *req,
                           double tlc, uint64_t t0_us, const pp_reference_line_t *ref,
                           const pp_lateral_state_t *start, const pp_speed_profile_t *speed,
                           const pp_function_limits_t *limits, const pp_vehicle_config_t *vehicle,
                           const pp_calibration_t *cal, bool elk);
void pp_intervention_sample(const pp_intervention_path_t *path, uint64_t t0_us,
                            pp_lateral_path_t *out);

#endif

#ifndef PP_OUTPUT_H
#define PP_OUTPUT_H

#include <stdint.h>

#include "pp_path.h"
#include "pp_types.h"
#include "reference_line.h"

/* Dịch v(t), a(t) từ stamp của LongitudinalPlan tới t0. NULL dùng tốc độ hiện tại và gia tốc 0
 * (PP-SWR-154). */
void pp_speed_profile(const pp_longitudinal_plan_t *plan, uint64_t t0_us, double speed,
                      pp_speed_profile_t *out);

/* Đổi Frenet sang base_link tại t0. samples có thể là NULL; trả false nếu kết quả không biểu diễn
 * được. */
bool pp_output_points(const pp_reference_line_t *ref, const pp_lateral_path_t *path,
                      const pp_speed_profile_t *speed, double wheelbase,
                      pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],
                      pp_ref_samples_t *samples);

/* Điền lưới thời gian khi phát Trajectory với header.valid = false. */
void pp_output_empty_points(pp_trajectory_point_t points[PP_TRAJECTORY_POINTS]);

#endif

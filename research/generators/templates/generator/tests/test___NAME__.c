/* L0 riêng của __NAME__. Contract chung đã có ở tests/planner/c/test_t7_contract.c. */

#include <string.h>

#include "generators/pp_t7.h"
#include "generators/t7_common.h"
#include "output.h"
#include "pp_calibration.h"
#include "pp_test.h"

static const pp_vehicle_config_t VP0 = {2.9F, 1.45F, 1.9F, 15.0F, 0.61F, 6.0F, 0.05F};
static pp_t7_ws_t ws;

/* Thay bằng ca kiểm cho phần mới của generator. Ca mẫu: trên đường thẳng, path trùng quintic_duration. */
static void test_straight_road_matches_base(void)
{
    pp_reference_line_t ref;
    pp_lateral_state_t start;
    pp_speed_profile_t speed;
    pp_old_path_t old;
    pp_t7_input_t in;
    pp_trajectory_point_t mine[PP_TRAJECTORY_POINTS];
    pp_trajectory_point_t base[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
    pp_lateral_path_t lateral;
    (void)memset(&ref, 0, sizeof(ref));
    (void)memset(&start, 0, sizeof(start));
    (void)memset(&old, 0, sizeof(old));
    (void)memset(&in, 0, sizeof(in));
    ref.valid = true;
    ref.width = 3.5;
    ref.view_end = 80.0;
    start.d = 0.3;
    pp_speed_profile(NULL, 0U, 20.0, &speed);
    in.ref = &ref;
    in.start = &start;
    in.speed = &speed;
    in.old = &old;
    in.vehicle = &VP0;
    pp_t7_reset(&ws);
    PP_CHECK(pp_t7_generate(&ws, &pp_calibration, &in, mine, &samples));
    PP_CHECK(pp_t7_quintic_search(&pp_calibration, &in, &lateral, base, &samples, NULL));
    PP_CHECK(memcmp(mine, base, sizeof(mine)) == 0);
}

int main(void)
{
    test_straight_road_matches_base();
    return PP_TEST_RESULT();
}

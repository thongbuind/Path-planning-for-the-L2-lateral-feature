#include <math.h>
#include <string.h>

#include "driver_shape.h"
#include "pp_test.h"

static void test_peak_and_ends(void)
{
    pp_lateral_path_t base;
    pp_lateral_path_t out;
    (void)memset(&base, 0, sizeof(base));
    PP_CHECK(lab_driver_bump(&base, 2.0, 1.0, 0.2, 1.0, &out));
    PP_CHECK_NEAR(out.d[0], 0.0, 1e-12);
    PP_CHECK_NEAR(out.d[10], 0.2, 1e-12);
    PP_CHECK_NEAR(out.d[20], 0.0, 1e-12);
    PP_CHECK_NEAR(out.d_dot[10], 0.0, 1e-12);
    PP_CHECK_NEAR(out.d_ddot[10], 0.0, 1e-12);
    PP_CHECK_NEAR(out.d[25], 0.0, 0.0);
    PP_CHECK(out.d[5] > 0.0 && out.d[5] < 0.2);
}

/* d_dot và d_ddot là đạo hàm của d: tích phân hình thang từng bước 0,1 s khớp phần tăng của d và d_dot. */
static void test_derivatives_match_differences(void)
{
    pp_lateral_path_t base;
    pp_lateral_path_t out;
    (void)memset(&base, 0, sizeof(base));
    PP_CHECK(lab_driver_bump(&base, 2.6, 1.1, -0.15, 1.0, &out));
    for (size_t k = 0U; k + 1U < 26U; k++) {
        const double half_dt = 0.5 * PP_GRID_STEP_S;
        PP_CHECK_NEAR(out.d[k + 1U] - out.d[k], half_dt * (out.d_dot[k] + out.d_dot[k + 1U]), 1e-3);
        PP_CHECK_NEAR(out.d_dot[k + 1U] - out.d_dot[k], half_dt * (out.d_ddot[k] + out.d_ddot[k + 1U]), 5e-3);
    }
}

static void test_rejects_bad_input_and_corridor(void)
{
    pp_lateral_path_t base;
    pp_lateral_path_t out;
    (void)memset(&base, 0, sizeof(base));
    PP_CHECK(!lab_driver_bump(&base, 2.0, 2.0, 0.2, 1.0, &out));
    PP_CHECK(!lab_driver_bump(&base, 2.0, 0.0, 0.2, 1.0, &out));
    PP_CHECK(!lab_driver_bump(&base, 2.0, 1.0, NAN, 1.0, &out));
    PP_CHECK(!lab_driver_bump(&base, 2.0, 1.0, 0.3, 0.25, &out));
}

int main(void)
{
    test_peak_and_ends();
    test_derivatives_match_differences();
    test_rejects_bad_input_and_corridor();
    return PP_TEST_RESULT();
}

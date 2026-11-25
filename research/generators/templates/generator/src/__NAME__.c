/* Điểm xuất phát: giống quintic_duration. Chỉ sửa trong thư mục này (research/generators/README.md). */

#include <math.h>
#include <stddef.h>
#include <stdint.h>

#include "generators/pp_t7.h"
#include "generators/t7_common.h"

void pp_t7_reset(pp_t7_ws_t *ws)
{
    if (ws != NULL) {
        ws->work = 0U;
        ws->fallback = 0U;
    }
}

bool pp_t7_generate(pp_t7_ws_t *ws, const pp_calibration_t *cal, const pp_t7_input_t *in,
                    pp_trajectory_point_t points[PP_TRAJECTORY_POINTS], pp_ref_samples_t *samples)
{
    pp_lateral_path_t lateral;
    ws->fallback = 0U;
    return pp_t7_quintic_search(cal, in, &lateral, points, samples, &ws->work);
}

#ifdef PP_T7_TELEMETRY
void pp_t7_report(const pp_t7_ws_t *ws, pp_t7_telemetry_t *out)
{
    out->work = ws->work;
    out->fallback = ws->fallback;
    out->infer_ops = 0U;
    out->residual = NAN;
    out->slack = NAN;
}
#endif

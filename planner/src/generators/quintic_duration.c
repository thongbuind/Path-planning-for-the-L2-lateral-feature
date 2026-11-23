#include <math.h>
#include <stddef.h>
#include <stdint.h>

#include "generators/pp_t7.h"
#include "generators/t7_common.h"

void pp_t7_reset(pp_t7_ws_t *ws)
{
    if (ws != NULL) {
#ifdef PP_T7_TELEMETRY
        ws->tries = 0U;
#else
        ws->unused = 0U;
#endif
    }
}

bool pp_t7_generate(pp_t7_ws_t *ws, const pp_calibration_t *cal, const pp_t7_input_t *in,
                    pp_trajectory_point_t points[PP_TRAJECTORY_POINTS], pp_ref_samples_t *samples)
{
    pp_lateral_path_t lateral;
#ifdef PP_T7_TELEMETRY
    return pp_t7_quintic_search(cal, in, &lateral, points, samples, &ws->tries);
#else
    (void)ws;
    return pp_t7_quintic_search(cal, in, &lateral, points, samples, NULL);
#endif
}

#ifdef PP_T7_TELEMETRY
void pp_t7_report(const pp_t7_ws_t *ws, pp_t7_telemetry_t *out)
{
    out->work = ws->tries;
    out->fallback = 0U;
    out->infer_ops = 0U;
    out->residual = NAN;
    out->slack = NAN;
}
#endif

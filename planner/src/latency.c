/* T1 Latency compensation (latency.h). PP-SWR-012, 128. */

#include "latency.h"

#include <math.h>
#include <string.h>

#define PP_SAMPLE_STEP_M (1.0)        /* Software Detailed Design 4, step 3 */
#define PP_MAX_FIT_SAMPLES (256U)     /* Bounds the work per boundary */

typedef struct {
    double c[PP_CUBIC_TERMS];
    const float *variance;
    double view_start;
    double view_end;
    double confidence;
    pp_line_status_t status;
} pp_raw_boundary_t;

static bool raw_usable(const pp_raw_boundary_t *raw)
{
    bool ok = (raw->status != PP_LINE_STATUS_LOST);
    for (uint32_t k = 0U; ok && (k < PP_CUBIC_TERMS); k++) {
        ok = isfinite(raw->c[k]) != 0;
    }
    ok = ok && (isfinite(raw->view_start) != 0) && (isfinite(raw->view_end) != 0)
            && (raw->view_end > raw->view_start) && (isfinite(raw->confidence) != 0);
    return ok;
}

bool pp_cubic_move(const pp_cubic_t *in, double x_start, double x_end, const pp_motion_t *motion,
                   pp_cubic_t *out, double *new_start, double *new_end)
{
    const double range = x_end - x_start;
    double step = PP_SAMPLE_STEP_M;
    uint32_t samples = PP_MAX_FIT_SAMPLES;
    const double wanted = floor(range / step) + 1.0;
    bool ok = (range > 0.0) && (isfinite(range) != 0);
    if (ok) {
        if (wanted > (double)PP_MAX_FIT_SAMPLES) {
            step = range / (double)(PP_MAX_FIT_SAMPLES - 1U);
        } else {
            samples = (uint32_t)wanted;
        }

        const double c = cos(motion->dyaw);
        const double s = sin(motion->dyaw);
        pp_cubic_fit_t fit;
        pp_cubic_fit_begin(&fit, x_start - motion->dx, x_end - motion->dx);

        double x_min = INFINITY;
        double x_max = -INFINITY;
        for (uint32_t i = 0U; i < samples; i++) {
            const double x = x_start + ((double)i * step);
            const double px = x - motion->dx;
            const double py = pp_cubic_value(in, x) - motion->dy;
            const double xn = (c * px) + (s * py);
            const double yn = (-s * px) + (c * py);
            pp_cubic_fit_add(&fit, xn, yn);
            x_min = fmin(x_min, xn);
            x_max = fmax(x_max, xn);
        }
        ok = pp_cubic_fit_solve(&fit, out);
        *new_start = x_min;
        *new_end = x_max;
    }
    return ok;
}

static void shift_boundary(const pp_raw_boundary_t *raw, const pp_motion_t *motion,
                           pp_boundary_t *out)
{
    (void)memset(out, 0, sizeof(*out));
    out->status = raw->status;
    out->confidence = raw->confidence;
    for (uint32_t k = 0U; k < PP_CUBIC_TERMS; k++) {
        out->variance[k] = (double)raw->variance[k];
    }

    if (raw_usable(raw)) {
        const pp_cubic_t old = {{raw->c[0], raw->c[1], raw->c[2], raw->c[3]}};
        out->present = pp_cubic_move(&old, raw->view_start, raw->view_end, motion, &out->poly,
                                     &out->view_start, &out->view_end);
    }
}

void pp_latency_compensate(const pp_lane_model_t *lane, const pp_motion_t *motion,
                           pp_lane_at_t0_t *out)
{
    (void)memset(out, 0, sizeof(*out));
    for (uint32_t i = 0U; i < PP_LANE_LINES; i++) {
        const pp_lane_line_t *line = &lane->lines[i];
        const pp_raw_boundary_t raw = {
            {(double)line->c0, (double)line->c1, (double)line->c2, (double)line->c3},
            line->variance, (double)line->view_range_start, (double)line->view_range_end,
            (double)line->confidence, line->status};
        shift_boundary(&raw, motion, &out->boundary[i]);
    }
    for (uint32_t i = 0U; i < PP_ROAD_EDGES; i++) {
        const pp_road_edge_t *edge = &lane->road_edges[i];
        const pp_raw_boundary_t raw = {
            {(double)edge->c0, (double)edge->c1, (double)edge->c2, (double)edge->c3},
            edge->variance, (double)edge->view_range_start, (double)edge->view_range_end,
            (double)edge->confidence, edge->status};
        shift_boundary(&raw, motion, &out->boundary[PP_LANE_LINES + i]);
    }
    out->lane_width = (double)lane->lane_width;
    out->lane_change = lane->lane_change;
}

void pp_lane_empty(pp_lane_at_t0_t *out)
{
    (void)memset(out, 0, sizeof(*out));
    for (uint32_t i = 0U; i < PP_BOUNDARIES; i++) {
        out->boundary[i].status = PP_LINE_STATUS_LOST;
    }
}

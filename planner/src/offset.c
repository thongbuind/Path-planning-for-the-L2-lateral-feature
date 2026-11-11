/* T8 Offset (offset.h). */

#include <math.h>
#include <stddef.h>
#include <string.h>

#include "offset.h"

#define PP_BIG_VEHICLE_WIDTH_M (2.3)   /* Software Requirements Specification 4, "Xe lớn" */
#define PP_NO_GAP (1.0e9)              /* No big vehicle on that side */

void pp_offset_reset(pp_offset_state_t *st)
{
    if (st != NULL) {
        (void)memset(st, 0, sizeof(*st));
    }
}

/* Whether a big vehicle counts now (abreast, or abreast within ttc_offset_start). */
static bool counts(const pp_object_t *o, double v, double car_front, double car_rear,
                   const pp_calibration_t *cal)
{
    const double half = 0.5 * (double)o->length;
    const double rear = (double)o->x - half;
    const double front = (double)o->x + half;
    const double closing_ahead = v - (double)o->vx;      /* car catches up an object ahead */
    const double closing_behind = (double)o->vx - v;     /* an object behind catches up */
    bool now = (rear <= car_front) && (front >= car_rear);
    if (!now && (rear > car_front) && (closing_ahead > 0.0)) {
        now = ((rear - car_front) / closing_ahead) <= (double)cal->ttc_offset_start;
    }
    if (!now && (front < car_rear) && (closing_behind > 0.0)) {
        now = ((car_rear - front) / closing_behind) <= (double)cal->ttc_offset_start;
    }
    return now;
}

/* Step 3: a side without a counted big vehicle keeps its last gap for t_offset_hold. */
static void hold(double *hold_s, double *kept, double *gap, const pp_calibration_t *cal, double dt)
{
    if (*gap < PP_NO_GAP) {
        *hold_s = (double)cal->t_offset_hold;
        *kept = *gap;
    } else if (*hold_s > 0.0) {
        *hold_s -= dt;
        *gap = *kept;
    } else {
        /* Nothing on this side. */
    }
}

/* Step 5 (Software Architectural Design 6): away from the big vehicle by the missing gap;
 * with big vehicles on both sides, equal gaps. Left positive. */
static double offset_of(double gap_left, double gap_right, double gap_min)
{
    const bool left = gap_left < PP_NO_GAP;
    const bool right = gap_right < PP_NO_GAP;
    const double miss_left = left ? fmax(0.0, gap_min - gap_left) : 0.0;
    const double miss_right = right ? fmax(0.0, gap_min - gap_right) : 0.0;
    double o = 0.0;
    if (left && right) {
        o = ((miss_left > 0.0) || (miss_right > 0.0)) ? (0.5 * (gap_left - gap_right)) : 0.0;
    } else {
        o = miss_right - miss_left;
    }
    return o;
}

double pp_offset_update(pp_offset_state_t *st, const pp_object_list_t *objects,
                        const pp_reference_line_t *ref, double v, double vehicle_width,
                        double car_front, double car_rear, const pp_calibration_t *cal, double dt)
{
    const double w = ref->width;
    const double half_car = 0.5 * vehicle_width;
    double gap_left = PP_NO_GAP;
    double gap_right = PP_NO_GAP;
    double target = 0.0;

    if (objects != NULL) {
        const uint8_t n = (objects->num_objects <= PP_MAX_OBJECTS) ? objects->num_objects
                                                                   : (uint8_t)PP_MAX_OBJECTS;
        for (uint8_t i = 0U; i < n; i++) {
            const pp_object_t *o = &objects->objects[i];
            pp_ref_point_t foot;
            double d = 0.0;
            if (((double)o->width >= PP_BIG_VEHICLE_WIDTH_M) && counts(o, v, car_front, car_rear, cal)) {
                pp_ref_project(ref, (double)o->x, (double)o->y, &foot, &d);
                const double gap = fabs(d) - (0.5 * (double)o->width) - half_car;
                const bool adjacent = (fabs(d) > (0.5 * w)) && (fabs(d) < (1.5 * w));
                if (adjacent && (d > 0.0)) {
                    gap_left = fmin(gap_left, gap);
                } else if (adjacent) {
                    gap_right = fmin(gap_right, gap);
                } else {
                    /* Not in an adjacent lane: no effect on the ego lane. */
                }
            }
        }
        hold(&st->hold_left_s, &st->gap_left, &gap_left, cal, dt);   /* Step 3 */
        hold(&st->hold_right_s, &st->gap_right, &gap_right, cal, dt);
        target = offset_of(gap_left, gap_right, (double)cal->gap_truck_min);
        const double free_space = 0.5 * (w - vehicle_width);
        const double o_lim = fmax(0.0, fmin((double)cal->offset_max,
                                            free_space - (double)cal->dlc_offset_min));
        target = fmin(o_lim, fmax(-o_lim, target));
    } else {
        st->hold_left_s = 0.0;                                /* Step 6 (PP-SWR-140) */
        st->hold_right_s = 0.0;
    }
    const double step = (double)cal->ref_rate * dt;
    st->offset += fmin(step, fmax(-step, target - st->offset));
    return st->offset;
}

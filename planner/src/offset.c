#include <math.h>
#include <stddef.h>
#include <string.h>

#include "offset.h"

#define PP_BIG_VEHICLE_WIDTH_M (2.3)
#define PP_NO_GAP (1.0e9)

void pp_offset_reset(pp_offset_state_t *st)
{
    if (st != NULL) {
        (void)memset(st, 0, sizeof(*st));
    }
}

static bool counts(const pp_object_t *o, double v, double car_front, double car_rear,
                   const pp_calibration_t *cal)
{
    const double half = 0.5 * (double)o->length;
    const double rear = (double)o->x - half;
    const double front = (double)o->x + half;
    const double closing_ahead = v - (double)o->vx;
    const double closing_behind = (double)o->vx - v;
    bool now = (rear <= car_front) && (front >= car_rear);
    if (!now && (rear > car_front) && (closing_ahead > 0.0)) {
        now = ((rear - car_front) / closing_ahead) <= (double)cal->ttc_offset_start;
    }
    if (!now && (front < car_rear) && (closing_behind > 0.0)) {
        now = ((car_rear - front) / closing_behind) <= (double)cal->ttc_offset_start;
    }
    return now;
}

/* Khi xe lớn hết được tính, giữ khoảng cách cuối trong t_offset_hold để không nhả offset đột ngột. */
static void hold(double *hold_s, double *kept, double *gap, const pp_calibration_t *cal, double dt)
{
    if (*gap < PP_NO_GAP) {
        *hold_s = (double)cal->t_offset_hold;
        *kept = *gap;
    } else if (*hold_s > 0.0) {
        *hold_s -= dt;
        *gap = *kept;
    } else {
    }
}

/* Dương về trái. Một xe lớn quá gần tạo offset_truck về phía đối diện nếu phía đó không có xe cản
 * (PP-ADR-020). */
static double offset_of(double gap_left, double gap_right, bool other_left, bool other_right,
                        double o_lim, const pp_calibration_t *cal)
{
    const bool big_left = gap_left < PP_NO_GAP;
    const bool big_right = gap_right < PP_NO_GAP;
    const double miss_left = big_left ? fmax(0.0, (double)cal->gap_truck_min - gap_left) : 0.0;
    const double miss_right = big_right ? fmax(0.0, (double)cal->gap_truck_min - gap_right) : 0.0;
    const double fixed = fmin((double)cal->offset_truck, o_lim);
    double o = 0.0;
    if (big_left && big_right) {
        o = ((miss_left > 0.0) || (miss_right > 0.0)) ? (0.5 * (gap_left - gap_right)) : 0.0;
        o = fmin(o_lim, fmax(-o_lim, o));
    } else if (big_left && (miss_left > 0.0)) {
        o = other_right ? 0.0 : -fixed;
    } else if (big_right && (miss_right > 0.0)) {
        o = other_left ? 0.0 : fixed;
    } else {
    }
    return o;
}

static bool hold_flag(double *hold_s, bool now, const pp_calibration_t *cal, double dt)
{
    if (now) {
        *hold_s = (double)cal->t_offset_hold;
        return true;
    }
    if (*hold_s > 0.0) {
        *hold_s -= dt;
        return true;
    }
    return false;
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
        bool other_left = false;
        bool other_right = false;
        for (uint8_t i = 0U; i < n; i++) {
            const pp_object_t *o = &objects->objects[i];
            pp_ref_point_t foot;
            double d = 0.0;
            if (counts(o, v, car_front, car_rear, cal)) {
                pp_ref_project(ref, (double)o->x, (double)o->y, &foot, &d);
                const bool adjacent = (fabs(d) > (0.5 * w)) && (fabs(d) < (1.5 * w));
                if (adjacent && ((double)o->width >= PP_BIG_VEHICLE_WIDTH_M)) {
                    const double gap = fabs(d) - (0.5 * (double)o->width) - half_car;
                    if (d > 0.0) {
                        gap_left = fmin(gap_left, gap);
                    } else {
                        gap_right = fmin(gap_right, gap);
                    }
                } else if (adjacent) {
                    other_left = other_left || (d > 0.0);
                    other_right = other_right || (d <= 0.0);
                } else {
                }
            }
        }
        hold(&st->hold_left_s, &st->gap_left, &gap_left, cal, dt);
        hold(&st->hold_right_s, &st->gap_right, &gap_right, cal, dt);
        other_left = hold_flag(&st->other_left_s, other_left, cal, dt);
        other_right = hold_flag(&st->other_right_s, other_right, cal, dt);
        const double free_space = 0.5 * (w - vehicle_width);
        const double o_lim = fmax(0.0, fmin((double)cal->offset_max,
                                            free_space - (double)cal->dlc_offset_min));
        target = offset_of(gap_left, gap_right, other_left, other_right, o_lim, cal);
    } else {
        st->hold_left_s = 0.0;
        st->hold_right_s = 0.0;
        st->other_left_s = 0.0;
        st->other_right_s = 0.0;
    }
    const double step = (double)cal->ref_rate * dt;
    st->offset += fmin(step, fmax(-step, target - st->offset));
    return st->offset;
}

#ifndef PP_OFFSET_H
#define PP_OFFSET_H

#include <stdbool.h>

#include "pp_calibration.h"
#include "pp_types.h"
#include "reference_line.h"

typedef struct {
    double offset;
    double hold_left_s;
    double hold_right_s;
    double gap_left;
    double gap_right;
    double other_left_s;
    double other_right_s;
} pp_offset_state_t;

void pp_offset_reset(pp_offset_state_t *st);

/* objects là NULL nếu ObjectList không dùng được; hai đầu thân xe đo theo x trong base_link. */
double pp_offset_update(pp_offset_state_t *st, const pp_object_list_t *objects,
                        const pp_reference_line_t *ref, double v, double vehicle_width,
                        double car_front, double car_rear, const pp_calibration_t *cal, double dt);

#endif

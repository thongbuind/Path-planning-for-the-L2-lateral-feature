/*
 * T8 Offset: HWA moves away from a large vehicle in an adjacent lane (Software Detailed
 * Design section 11; PP-SWR-055, 056, 058, 140).
 *
 * 1. Objects with width >= 2.3 m (Software Requirements Specification 4) are assigned to
 *    the left or right adjacent lane by their offset from the reference line.
 * 2. One counts while it is abreast of the car, or while the time to become abreast is at
 *    most ttc_offset_start; afterwards it still counts for t_offset_hold.
 * 3. Gap to a big vehicle each side: from the car body (+- vehicle_width/2 around the
 *    centre) to its near edge; the smallest if several; none if no big vehicle counts.
 * 4. o_lim = max(0, min(offset_max, s - dlc_offset_min)), s = (w - vehicle_width)/2;
 *    missing gap h = max(0, gap_truck_min - gap). A vehicle that is not a big vehicle, abreast
 *    or about to be, in an adjacent lane counts as "a vehicle on that side" (held the same way).
 * 5. Exactly one big vehicle with h > 0: o = min(offset_truck, o_lim) away from it, unless a
 *    vehicle is on the other side, then 0 (PP-SWR-055, 065, 066). Two big vehicles, some
 *    h > 0: o = (gap_left - gap_right)/2 (the earlier balanced rule). Clipped to +-o_lim;
 *    changes at most ref_rate per second (PP-ADR-008, 020).
 * 6. No usable ObjectList: o back to 0 at the same rate.
 * Not yet: object positions moved from measurement time to t0 (100 ms at most).
 */

#ifndef PP_OFFSET_H
#define PP_OFFSET_H

#include <stdbool.h>

#include "pp_calibration.h"
#include "pp_types.h"
#include "reference_line.h"

typedef struct {
    double offset;                 /* [m] current o, left positive */
    double hold_left_s;            /* Time a left object still counts after it stopped */
    double hold_right_s;
    double gap_left;               /* [m] last gap to a counted big vehicle, for the hold */
    double gap_right;
    double other_left_s;           /* Time a not-big vehicle on that side still counts */
    double other_right_s;
} pp_offset_state_t;

void pp_offset_reset(pp_offset_state_t *st);

/*
 * objects NULL when ObjectList is not usable. car_front, car_rear: x of the car's front and
 * rear in base_link. Returns the offset to use this cycle.
 */
double pp_offset_update(pp_offset_state_t *st, const pp_object_list_t *objects,
                        const pp_reference_line_t *ref, double v, double vehicle_width,
                        double car_front, double car_rear, const pp_calibration_t *cal, double dt);

#endif /* PP_OFFSET_H */

/* Unit tests of T8 Offset (offset.c): one big vehicle gives offset_truck, two balance (PP-ADR-008, 020). */

#include <math.h>
#include <string.h>

#include "offset.h"
#include "pp_calibration.h"
#include "pp_test.h"

#define DT (0.025)
#define CAR_WIDTH (1.9)
#define CAR_FRONT (3.9)
#define CAR_REAR (-1.0)

static pp_reference_line_t straight(double width)
{
    pp_reference_line_t ref;
    (void)memset(&ref, 0, sizeof(ref));
    ref.valid = true;
    ref.width = width;
    ref.view_end = 80.0;
    return ref;
}

/* One truck 12 x 2.5 m abreast at lateral position y, same speed as the car. */
static pp_object_list_t trucks(const double *y, uint8_t n)
{
    pp_object_list_t list;
    (void)memset(&list, 0, sizeof(list));
    list.header.valid = true;
    list.num_objects = n;
    for (uint8_t i = 0U; i < n; i++) {
        list.objects[i].id = (uint32_t)(i + 1U);
        list.objects[i].x = 1.0F;
        list.objects[i].y = (float)y[i];
        list.objects[i].vx = 25.0F;
        list.objects[i].length = 12.0F;
        list.objects[i].width = 2.5F;
        list.objects[i].existence_probability = 0.95F;
    }
    return list;
}

/* Offset after 10 s of the same input (well past the ref_rate ramp). */
static double settle(pp_offset_state_t *st, const pp_object_list_t *list, const pp_reference_line_t *ref)
{
    double o = 0.0;
    for (int k = 0; k < 400; k++) {
        o = pp_offset_update(st, list, ref, 25.0, CAR_WIDTH, CAR_FRONT, CAR_REAR, &pp_calibration, DT);
    }
    return o;
}

static void test_truck_centred_in_right_lane_moves_left(void)
{
    const pp_reference_line_t ref = straight(3.5);
    const double y[] = {-3.5};
    const pp_object_list_t list = trucks(y, 1U);
    pp_offset_state_t st;
    pp_offset_reset(&st);
    /* Gap 3.5 - 1.25 - 0.95 = 1.3 m < gap_truck_min 1.5 m: the fixed offset_truck, to the left. */
    PP_CHECK_NEAR(settle(&st, &list, &ref), (double)pp_calibration.offset_truck, 1e-6);   /* PP-SWR-055, 066 */
}

static void test_truck_on_the_left_moves_right_by_offset_truck_even_when_very_close(void)
{
    const pp_reference_line_t ref = straight(3.5);
    const double y[] = {2.7};                     /* gap 0.5 m: still only offset_truck */
    const pp_object_list_t list = trucks(y, 1U);
    pp_offset_state_t st;
    pp_offset_reset(&st);
    PP_CHECK_NEAR(settle(&st, &list, &ref), -(double)pp_calibration.offset_truck, 1e-6);
}

static void test_narrow_lane_limits_the_offset(void)
{
    const pp_reference_line_t ref = straight(2.6);     /* s = 0.35 m, o_lim = 0.35 - dlc_offset_min = 0.05 m */
    const double y[] = {-2.6};
    const pp_object_list_t list = trucks(y, 1U);
    pp_offset_state_t st;
    pp_offset_reset(&st);
    const double o_lim = fmax(0.0, 0.5 * (2.6 - CAR_WIDTH) - (double)pp_calibration.dlc_offset_min);
    PP_CHECK_NEAR(settle(&st, &list, &ref), fmin((double)pp_calibration.offset_truck, o_lim), 1e-6);
}

/* A car abreast in the other lane stops the offset (PP-SWR-065); one far away does not. */
static void test_vehicle_on_the_other_side_blocks_the_offset(void)
{
    const pp_reference_line_t ref = straight(3.5);
    const double y[] = {-3.5, 3.5};
    pp_object_list_t list = trucks(y, 2U);
    list.objects[1].width = 1.8F;                      /* a car, not a big vehicle */
    list.objects[1].length = 4.5F;
    pp_offset_state_t st;
    pp_offset_reset(&st);
    PP_CHECK_NEAR(settle(&st, &list, &ref), 0.0, 1e-12);

    list.objects[1].x = 60.0F;                         /* far ahead, same speed: never abreast */
    pp_offset_reset(&st);
    PP_CHECK_NEAR(settle(&st, &list, &ref), (double)pp_calibration.offset_truck, 1e-6);
}

static void test_far_truck_no_offset(void)
{
    const pp_reference_line_t ref = straight(4.5);
    const double y[] = {-4.5};                    /* gap 4.5 - 1.25 - 0.95 = 2.3 m */
    const pp_object_list_t list = trucks(y, 1U);
    pp_offset_state_t st;
    pp_offset_reset(&st);
    PP_CHECK_NEAR(settle(&st, &list, &ref), 0.0, 1e-12);
}

static void test_trucks_both_sides_balance(void)
{
    const pp_reference_line_t ref = straight(3.5);
    const double y[] = {-3.5, 3.3};               /* gaps right 1.3, left 1.1 */
    const pp_object_list_t list = trucks(y, 2U);
    pp_offset_state_t st;
    pp_offset_reset(&st);
    PP_CHECK_NEAR(settle(&st, &list, &ref), 0.5 * (1.1 - 1.3), 1e-6);  /* towards the right */
}

static void test_rate_limit_and_return_without_object_list(void)
{
    const pp_reference_line_t ref = straight(3.5);
    const double y[] = {-3.5};
    const pp_object_list_t list = trucks(y, 1U);
    pp_offset_state_t st;
    pp_offset_reset(&st);
    const double first = pp_offset_update(&st, &list, &ref, 25.0, CAR_WIDTH, CAR_FRONT, CAR_REAR,
                                          &pp_calibration, DT);
    PP_CHECK_NEAR(first, (double)pp_calibration.ref_rate * DT, 1e-12);
    (void)settle(&st, &list, &ref);
    PP_CHECK_NEAR(settle(&st, NULL, &ref), 0.0, 1e-12);      /* PP-SWR-140 */
}

static void test_ghost_sized_object_ignored(void)
{
    const pp_reference_line_t ref = straight(3.5);
    const double y[] = {-2.8};
    pp_object_list_t list = trucks(y, 1U);
    list.objects[0].width = 1.8F;                 /* a car, not a big vehicle */
    pp_offset_state_t st;
    pp_offset_reset(&st);
    PP_CHECK_NEAR(settle(&st, &list, &ref), 0.0, 1e-12);
}

int main(void)
{
    test_truck_centred_in_right_lane_moves_left();
    test_truck_on_the_left_moves_right_by_offset_truck_even_when_very_close();
    test_narrow_lane_limits_the_offset();
    test_vehicle_on_the_other_side_blocks_the_offset();
    test_far_truck_no_offset();
    test_trucks_both_sides_balance();
    test_rate_limit_and_return_without_object_list();
    test_ghost_sized_object_ignored();
    return PP_TEST_RESULT();
}

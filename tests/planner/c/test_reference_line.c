/* Unit tests of T2 Reference line (planner/src/reference_line.c). */

#include <string.h>

#include "pp_test.h"
#include "reference_line.h"

#define DT (0.025)

static pp_boundary_t line_at(double c0, double c1, double c2)
{
    pp_boundary_t b;
    (void)memset(&b, 0, sizeof(b));
    b.present = true;
    b.poly.c[0] = c0;
    b.poly.c[1] = c1;
    b.poly.c[2] = c2;
    b.view_start = 0.0;
    b.view_end = 80.0;
    b.confidence = 0.9;
    b.status = PP_LINE_STATUS_MEASURED;
    b.variance[0] = 0.03 * 0.03;
    return b;
}

static pp_lane_at_t0_t two_lines(double width, double centre)
{
    pp_lane_at_t0_t lane;
    (void)memset(&lane, 0, sizeof(lane));
    lane.boundary[PP_LINE_L1] = line_at(centre + (0.5 * width), 0.0, 0.0);
    lane.boundary[PP_LINE_R1] = line_at(centre - (0.5 * width), 0.0, 0.0);
    return lane;
}

static void test_centre_between_lines(void)
{
    pp_reference_memory_t mem;
    pp_reference_line_t ref;
    pp_reference_memory_reset(&mem);
    const pp_lane_at_t0_t lane = two_lines(3.5, 0.3);
    pp_reference_line_update(&mem, &lane, NULL, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(ref.valid);
    PP_CHECK_NEAR(ref.centre.c[0], 0.3, 1e-12);
    PP_CHECK_NEAR(ref.width, 3.5, 1e-12);
    PP_CHECK(mem.width_valid);
    PP_CHECK_NEAR(mem.width, 3.5, 1e-12);
    PP_CHECK(!ref.lane_too_narrow);
}

static void test_one_line_uses_remembered_width(void)
{
    pp_reference_memory_t mem;
    pp_reference_line_t ref;
    pp_reference_memory_reset(&mem);
    pp_lane_at_t0_t lane = two_lines(3.5, 0.0);
    pp_reference_line_update(&mem, &lane, NULL, &pp_calibration, 1.9, DT, &ref);

    lane.boundary[PP_LINE_R1].status = PP_LINE_STATUS_LOST;
    lane.boundary[PP_LINE_R1].present = false;
    pp_reference_line_update(&mem, &lane, NULL, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(ref.valid);
    PP_CHECK_NEAR(ref.centre.c[0], 0.0, 1e-12);          /* 1.75 - 3.5 / 2 */

    lane = two_lines(3.5, 0.0);
    lane.boundary[PP_LINE_L1].confidence = 0.5 * (double)pp_calibration.conf_ego;  /* not trusted */
    pp_reference_line_update(&mem, &lane, NULL, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(ref.valid);
    PP_CHECK_NEAR(ref.centre.c[0], 0.0, 1e-12);          /* -1.75 + 3.5 / 2 */
}

static void test_no_trusted_line(void)
{
    pp_reference_memory_t mem;
    pp_reference_line_t ref;
    pp_reference_memory_reset(&mem);
    pp_lane_at_t0_t lane = two_lines(3.5, 0.0);
    lane.boundary[PP_LINE_L1].status = PP_LINE_STATUS_PREDICTED;  /* MEASURED only (SRS 4) */
    lane.boundary[PP_LINE_R1].present = false;
    pp_reference_line_update(&mem, &lane, NULL, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(!ref.valid);
}

static void test_width_memory_filters_and_rejects(void)
{
    pp_reference_memory_t mem;
    pp_reference_line_t ref;
    pp_reference_memory_reset(&mem);
    pp_lane_at_t0_t lane = two_lines(3.5, 0.0);
    pp_reference_line_update(&mem, &lane, NULL, &pp_calibration, 1.9, DT, &ref);
    lane = two_lines(6.0, 0.0);                           /* outside 2.5-5.5 m: ignored */
    pp_reference_line_update(&mem, &lane, NULL, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK_NEAR(mem.width, 3.5, 1e-12);
    lane = two_lines(3.7, 0.0);
    pp_reference_line_update(&mem, &lane, NULL, &pp_calibration, 1.9, DT, &ref);
    const double alpha = DT / ((double)pp_calibration.tau_mem + DT);
    PP_CHECK_NEAR(mem.width, 3.5 + (alpha * 0.2), 1e-12);
}

static void test_lane_too_narrow(void)
{
    pp_reference_memory_t mem;
    pp_reference_line_t ref;
    pp_reference_memory_reset(&mem);
    const pp_lane_at_t0_t lane = two_lines(2.6, 0.0);
    pp_reference_line_update(&mem, &lane, NULL, &pp_calibration, 2.5, DT, &ref);
    PP_CHECK(ref.lane_too_narrow);                        /* 0.05 m < free_space_min */
}

static void test_walk_straight_and_arc_continuation(void)
{
    pp_reference_line_t ref;
    pp_ref_walker_t w;
    pp_ref_point_t p;
    (void)memset(&ref, 0, sizeof(ref));
    ref.valid = true;
    ref.centre.c[0] = 0.5;
    ref.view_end = 50.0;
    pp_ref_walk_begin(&w, &ref, &p);
    PP_CHECK_NEAR(p.x, 0.0, 1e-12);
    PP_CHECK_NEAR(p.y, 0.5, 1e-12);
    pp_ref_walk_to(&w, 20.0, &p);
    PP_CHECK_NEAR(p.x, 20.0, 1e-9);
    pp_ref_walk_to(&w, 80.0, &p);                         /* beyond the view range */
    PP_CHECK_NEAR(p.x, 80.0, 1e-9);
    PP_CHECK_NEAR(p.y, 0.5, 1e-9);
}

static void test_walk_curve(void)
{
    /* y = x^2 / (2R) is a circle of radius R near x = 0. */
    const double radius = 500.0;
    pp_reference_line_t ref;
    pp_ref_walker_t w;
    pp_ref_point_t p;
    (void)memset(&ref, 0, sizeof(ref));
    ref.valid = true;
    ref.centre.c[2] = 1.0 / (2.0 * radius);
    ref.view_end = 30.0;
    pp_ref_walk_begin(&w, &ref, &p);
    PP_CHECK_NEAR(p.kappa, 1.0 / radius, 1e-9);
    pp_ref_walk_to(&w, 25.0, &p);
    PP_CHECK_NEAR(p.theta, 25.0 / radius, 1e-4);          /* parabola, not exactly a circle */
    pp_ref_walk_to(&w, 60.0, &p);                         /* arc continuation keeps heading growth */
    PP_CHECK(p.theta > (55.0 / radius));
    PP_CHECK_NEAR(p.dkappa, 0.0, 1e-12);
}

static const pp_motion_t STILL = {0.0, 0.0, 0.0};

static void test_jump_of_one_line_is_rejected(void)
{
    pp_reference_memory_t mem;
    pp_reference_line_t ref;
    pp_reference_memory_reset(&mem);
    pp_lane_at_t0_t lane = two_lines(3.5, 0.0);
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    lane.boundary[PP_LINE_L1].poly.c[0] += 0.6;            /* > 3 sqrt(2) 0.03 */
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(ref.line_rejected[0] && !ref.line_rejected[1]);
    PP_CHECK(ref.valid && !ref.coasting);
    PP_CHECK_NEAR(ref.centre.c[0], 0.0, 1e-12);             /* from R1 + w_mem / 2 */
}

static void test_jump_of_both_lines_coasts_then_is_accepted(void)
{
    pp_reference_memory_t mem;
    pp_reference_line_t ref;
    pp_reference_memory_reset(&mem);
    pp_lane_at_t0_t lane = two_lines(3.5, 0.0);
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    lane = two_lines(3.5, 0.6);                             /* whole lane model shifts (F02) */
    const int confirm = (int)lround((double)pp_calibration.T_confirm / DT);
    for (int i = 1; i < confirm; i++) {
        pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
        PP_CHECK(ref.valid && ref.coasting);                /* step 5 */
        PP_CHECK_NEAR(ref.centre.c[0], 0.0, 1e-9);
    }
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(ref.valid && !ref.coasting);                   /* lasted T_confirm: taken as real */
    PP_CHECK_NEAR(ref.centre.c[0], 0.6, 1e-9);
}

static void test_flickering_jump_is_never_accepted(void)
{
    /* R1: time counts only while the new position is consistent with itself. */
    pp_reference_memory_t mem;
    pp_reference_line_t ref;
    pp_reference_memory_reset(&mem);
    pp_lane_at_t0_t lane = two_lines(3.5, 0.0);
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    const int cycles = (int)lround(2.0 * (double)pp_calibration.T_confirm / DT);
    for (int i = 0; i < cycles; i++) {
        lane = two_lines(3.5, 0.0);
        lane.boundary[PP_LINE_L1].poly.c[0] += (i % 2 == 0) ? 0.6 : 1.2;
        pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
        PP_CHECK(ref.line_rejected[0]);
    }
}

static void test_return_after_a_change_is_taken_at_once(void)
{
    /* R2: after a change the old position stays as a quick way back. */
    pp_reference_memory_t mem;
    pp_reference_line_t ref;
    pp_reference_memory_reset(&mem);
    pp_lane_at_t0_t lane = two_lines(3.5, 0.0);
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    lane = two_lines(3.5, 0.6);
    const int confirm = (int)lround((double)pp_calibration.T_confirm / DT);
    for (int i = 0; i < confirm; i++) {
        pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    }
    PP_CHECK(ref.valid && !ref.coasting);
    PP_CHECK_NEAR(ref.centre.c[0], 0.6, 1e-9);              /* change taken */
    lane = two_lines(3.5, 0.0);                              /* lane model back */
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(!ref.line_rejected[0] && !ref.line_rejected[1]);
    PP_CHECK_NEAR(ref.centre.c[0], 0.0, 1e-9);
}

static void test_coast_ends_after_t_coast(void)
{
    pp_reference_memory_t mem;
    pp_reference_line_t ref;
    pp_reference_memory_reset(&mem);
    pp_lane_at_t0_t lane = two_lines(3.5, 0.0);
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    pp_lane_empty(&lane);                                   /* no boundary at all */
    const int coast = (int)lround((double)pp_calibration.T_coast / DT);
    for (int i = 0; i < coast; i++) {
        pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
        PP_CHECK(ref.valid && ref.coasting);
    }
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(!ref.valid);                                   /* PP-SWR-124 */
}

int main(void)
{
    test_jump_of_one_line_is_rejected();
    test_jump_of_both_lines_coasts_then_is_accepted();
    test_coast_ends_after_t_coast();
    test_flickering_jump_is_never_accepted();
    test_return_after_a_change_is_taken_at_once();
    test_centre_between_lines();
    test_one_line_uses_remembered_width();
    test_no_trusted_line();
    test_width_memory_filters_and_rejects();
    test_lane_too_narrow();
    test_walk_straight_and_arc_continuation();
    test_walk_curve();
    return PP_TEST_RESULT();
}

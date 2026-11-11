/* Unit tests of T1 Latency compensation (planner/src/latency.c). */

#include <string.h>

#include "latency.h"
#include "pp_test.h"

static pp_lane_model_t lane_with_line(float c0, float c1, float c2, float c3)
{
    pp_lane_model_t lane;
    (void)memset(&lane, 0, sizeof(lane));
    for (unsigned i = 0U; i < PP_LANE_LINES; i++) {
        lane.lines[i].status = PP_LINE_STATUS_LOST;
    }
    for (unsigned i = 0U; i < PP_ROAD_EDGES; i++) {
        lane.road_edges[i].status = PP_LINE_STATUS_LOST;
    }
    pp_lane_line_t *l1 = &lane.lines[PP_LINE_L1];
    l1->c0 = c0;
    l1->c1 = c1;
    l1->c2 = c2;
    l1->c3 = c3;
    l1->view_range_start = 0.0F;
    l1->view_range_end = 80.0F;
    l1->confidence = 0.9F;
    l1->status = PP_LINE_STATUS_MEASURED;
    lane.lane_width = 3.5F;
    return lane;
}

static void test_no_motion_keeps_line(void)
{
    const pp_lane_model_t lane = lane_with_line(1.75F, 0.01F, 2.0e-4F, -1.0e-6F);
    const pp_motion_t none = {0.0, 0.0, 0.0};
    pp_lane_at_t0_t out;
    pp_latency_compensate(&lane, &none, &out);
    const pp_boundary_t *b = &out.boundary[PP_LINE_L1];
    PP_CHECK(b->present);
    PP_CHECK_NEAR(b->poly.c[0], 1.75, 1e-6);
    PP_CHECK_NEAR(b->poly.c[1], 0.01, 1e-7);
    PP_CHECK_NEAR(b->poly.c[2], 2.0e-4, 1e-8);
    PP_CHECK_NEAR(b->poly.c[3], -1.0e-6, 1e-9);
    PP_CHECK(!out.boundary[PP_LINE_R1].present);        /* LOST stays out */
    PP_CHECK(!out.boundary[PP_EDGE_LEFT].present);
}

static void test_translation(void)
{
    /* y = 1 + 0.01 x; base_link moved 10 m forward and 0.5 m left. */
    const pp_lane_model_t lane = lane_with_line(1.0F, 0.01F, 0.0F, 0.0F);
    const pp_motion_t motion = {10.0, 0.5, 0.0};
    pp_lane_at_t0_t out;
    pp_latency_compensate(&lane, &motion, &out);
    const pp_boundary_t *b = &out.boundary[PP_LINE_L1];
    PP_CHECK(b->present);
    PP_CHECK_NEAR(b->poly.c[0], 1.0 + 0.1 - 0.5, 1e-6);
    PP_CHECK_NEAR(b->poly.c[1], 0.01, 1e-7);
    PP_CHECK_NEAR(b->view_start, -10.0, 1e-4);          /* view range moves with the car */
    PP_CHECK_NEAR(b->view_end, 70.0, 1e-3);
}

static void test_rotation(void)
{
    /* Straight line y = 2; base_link turned by psi to the left. */
    const double psi = 0.02;
    const pp_lane_model_t lane = lane_with_line(2.0F, 0.0F, 0.0F, 0.0F);
    const pp_motion_t motion = {0.0, 0.0, psi};
    pp_lane_at_t0_t out;
    pp_latency_compensate(&lane, &motion, &out);
    const pp_boundary_t *b = &out.boundary[PP_LINE_L1];
    PP_CHECK_NEAR(b->poly.c[1], -tan(psi), 1e-7);
    PP_CHECK_NEAR(b->poly.c[0], 2.0 / cos(psi), 1e-6);
    PP_CHECK_NEAR(b->poly.c[2], 0.0, 1e-9);
}

static void test_short_view_range_is_dropped(void)
{
    pp_lane_model_t lane = lane_with_line(1.75F, 0.0F, 0.0F, 0.0F);
    lane.lines[PP_LINE_L1].view_range_end = 2.0F;       /* three samples only */
    const pp_motion_t none = {0.0, 0.0, 0.0};
    pp_lane_at_t0_t out;
    pp_latency_compensate(&lane, &none, &out);
    PP_CHECK(!out.boundary[PP_LINE_L1].present);
}

int main(void)
{
    test_no_motion_keeps_line();
    test_translation();
    test_rotation();
    test_short_view_range_is_dropped();
    return PP_TEST_RESULT();
}

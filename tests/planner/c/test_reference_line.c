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
    pp_lane_at_t0_t lane = two_lines(3.5, 0.3);
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
    PP_CHECK_NEAR(ref.centre.c[0], 0.0, 1e-12);

    lane = two_lines(3.5, 0.0);
    lane.boundary[PP_LINE_L1].confidence = 0.5 * (double)pp_calibration.conf_ego;
    pp_reference_line_update(&mem, &lane, NULL, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(ref.valid);
    PP_CHECK_NEAR(ref.centre.c[0], 0.0, 1e-12);
}

static void test_no_trusted_line(void)
{
    pp_reference_memory_t mem;
    pp_reference_line_t ref;
    pp_reference_memory_reset(&mem);
    pp_lane_at_t0_t lane = two_lines(3.5, 0.0);
    lane.boundary[PP_LINE_L1].status = PP_LINE_STATUS_PREDICTED;
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
    lane = two_lines(6.0, 0.0);
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
    pp_lane_at_t0_t lane = two_lines(2.6, 0.0);
    pp_reference_line_update(&mem, &lane, NULL, &pp_calibration, 2.5, DT, &ref);
    PP_CHECK(ref.lane_too_narrow);
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
    pp_ref_walk_to(&w, 80.0, &p);
    PP_CHECK_NEAR(p.x, 80.0, 1e-9);
    PP_CHECK_NEAR(p.y, 0.5, 1e-9);
}

static void test_walk_curve(void)
{
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
    PP_CHECK_NEAR(p.theta, 25.0 / radius, 1e-4);
    pp_ref_walk_to(&w, 60.0, &p);
    PP_CHECK(p.theta > (55.0 / radius));
    PP_CHECK_NEAR(p.dkappa, 0.0, 1e-12);
}

static pp_reference_line_t curved_ref(void)
{
    pp_reference_line_t ref;
    (void)memset(&ref, 0, sizeof(ref));
    ref.valid = true;
    ref.centre.c[0] = 0.3;
    ref.centre.c[1] = 0.01;
    ref.centre.c[2] = 1.0 / (2.0 * 300.0);
    ref.centre.c[3] = 2.0e-6;
    ref.view_end = 80.0;
    return ref;
}

static double fine_arc_length(const pp_cubic_t *p, double x0, double x)
{
    const uint32_t steps = 200000U;
    const double dx = (x - x0) / (double)steps;
    double s = 0.0;
    for (uint32_t i = 0U; i < steps; i++) {
        const double slope = pp_cubic_slope(p, x0 + (((double)i + 0.5) * dx));
        s += dx * sqrt(1.0 + (slope * slope));
    }
    return s;
}

static void test_sampled_walk_matches_cubic(void)
{
    const pp_reference_line_t cubic = curved_ref();
    pp_reference_line_t sampled = curved_ref();
    pp_ref_walker_t wc;
    pp_ref_walker_t ws;
    pp_ref_point_t pc;
    pp_ref_point_t ps;
    pp_ref_sample_cubic(&sampled);
    PP_CHECK(sampled.sampled);
    PP_CHECK(sampled.nodes.n <= PP_REF_NODES);
    PP_CHECK_NEAR(sampled.nodes.s[sampled.nodes.origin], 0.0, 1e-12);
    pp_ref_walk_begin(&wc, &cubic, &pc);
    pp_ref_walk_begin(&ws, &sampled, &ps);
    PP_CHECK_NEAR(ps.x, pc.x, 1e-9);
    PP_CHECK_NEAR(ps.y, pc.y, 1e-9);
    const double x0 = pc.x;

    for (double x = -75.0; x <= 79.5; x += 3.3) {
        const double s = fine_arc_length(&cubic.centre, x0, x);
        const double d1 = pp_cubic_slope(&cubic.centre, x);
        const double g = 1.0 + (d1 * d1);
        pp_ref_walk_to(&ws, s, &ps);
        PP_CHECK_NEAR(ps.x, x, 5e-6);
        PP_CHECK_NEAR(ps.y, pp_cubic_value(&cubic.centre, x), 5e-6);
        PP_CHECK_NEAR(ps.theta, atan(d1), 1e-7);
        PP_CHECK_NEAR(ps.kappa, pp_cubic_bend(&cubic.centre, x) / (g * sqrt(g)), 1e-8);
    }

    /* Phép walk cubic có sai số tích lũy nhỏ về chiều dài cung. Biên này dùng cả sau cuối tầm
     * nhìn. */
    for (double s = 0.0; s <= 110.0; s += 0.7) {
        pp_ref_walk_to(&wc, s, &pc);
        pp_ref_walk_to(&ws, s, &ps);
        PP_CHECK_NEAR(ps.x, pc.x, 5e-4);
        PP_CHECK_NEAR(ps.y, pc.y, 5e-4);
        PP_CHECK_NEAR(ps.theta, pc.theta, 5e-6);
        PP_CHECK_NEAR(ps.kappa, pc.kappa, 1e-7);
        PP_CHECK_NEAR(ps.dkappa, pc.dkappa, 1e-7);
    }
}

static void test_sampled_project_matches_cubic(void)
{
    const pp_reference_line_t cubic = curved_ref();
    pp_reference_line_t sampled = curved_ref();
    const double points[][2] = {{0.0, 0.0}, {2.9, 0.0}, {25.0, 1.5}, {60.0, -3.0}, {79.0, 9.0},
                                {-4.0, 0.2}, {-30.0, 2.0}, {-70.0, -1.0}};
    pp_ref_sample_cubic(&sampled);
    for (size_t i = 0U; i < (sizeof(points) / sizeof(points[0])); i++) {
        pp_ref_point_t fc;
        pp_ref_point_t fs;
        double dc = 0.0;
        double ds = 0.0;
        pp_ref_project(&cubic, points[i][0], points[i][1], &fc, &dc);
        pp_ref_project(&sampled, points[i][0], points[i][1], &fs, &ds);
        PP_CHECK_NEAR(ds, dc, 1e-5);
        PP_CHECK_NEAR(fs.x, fc.x, 1e-4);
        PP_CHECK_NEAR(fs.kappa, fc.kappa, 1e-8);
    }
}

static void test_sampled_line_without_range_ahead(void)
{
    pp_reference_line_t cubic = curved_ref();
    pp_reference_line_t sampled;
    pp_ref_walker_t wc;
    pp_ref_walker_t ws;
    pp_ref_point_t pc;
    pp_ref_point_t ps;
    cubic.view_end = -5.0;
    sampled = cubic;
    pp_ref_sample_cubic(&sampled);
    PP_CHECK(sampled.nodes.n == (sampled.nodes.origin + 1U));
    pp_ref_walk_begin(&wc, &cubic, &pc);
    pp_ref_walk_begin(&ws, &sampled, &ps);
    pp_ref_walk_to(&wc, 30.0, &pc);
    pp_ref_walk_to(&ws, 30.0, &ps);
    PP_CHECK_NEAR(ps.x, pc.x, 1e-9);
    PP_CHECK_NEAR(ps.y, pc.y, 1e-9);
    PP_CHECK_NEAR(ps.dkappa, 0.0, 1e-12);
}

static const pp_motion_t STILL = {0.0, 0.0, 0.0};

static void test_wrong_slots_need_two_matching_markings(double shift)
{
    pp_reference_memory_t mem;
    pp_reference_line_t ref;
    pp_reference_memory_reset(&mem);
    pp_lane_at_t0_t lane = two_lines(3.5, 0.0);
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    lane = two_lines(3.5, shift);
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(ref.coasting);

    lane.boundary[PP_LINE_L2] = line_at(shift + 5.25, 0.0, 0.0);
    lane.boundary[PP_LINE_R2] = line_at(shift - 5.25, 0.0, 0.0);
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(ref.valid && !ref.coasting);
    PP_CHECK_NEAR(ref.centre.c[0], 0.0, 1e-9);
    PP_CHECK_NEAR(lane.boundary[PP_LINE_L1].poly.c[0], 1.75, 1e-9);
    PP_CHECK_NEAR(lane.boundary[PP_LINE_R1].poly.c[0], -1.75, 1e-9);
    PP_CHECK(!lane.boundary[(shift > 0.0) ? PP_LINE_R2 : PP_LINE_L2].present);
}

static void test_crossed_marking_changes_slot(pp_side_t side)
{
    pp_reference_memory_t mem;
    pp_reference_line_t ref;
    pp_reference_memory_reset(&mem);
    const bool rightward = side == PP_SIDE_RIGHT;
    const double before = rightward ? 1.75 : -1.75;
    pp_lane_at_t0_t lane = two_lines(3.5, before);
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);

    lane = two_lines(3.5, -before);
    lane.lane_change = side;
    lane.boundary[rightward ? PP_LINE_R1 : PP_LINE_L1].present = false;
    /* Một frame camera 20 Hz được planner 40 Hz dùng hai lần. Cả hai path phải tham chiếu làn mới. */
    for (unsigned i = 0U; i < 2U; i++) {
        pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
        PP_CHECK(ref.valid && !ref.coasting && !ref.inferred);
        PP_CHECK_NEAR(ref.centre.c[0], -before, 1e-9);
    }
}

static void test_inferred_centre_uses_remembered_offsets(void)
{
    pp_reference_memory_t mem;
    pp_reference_line_t ref;
    pp_reference_memory_reset(&mem);
    pp_lane_at_t0_t lane = two_lines(3.5, 0.3);
    lane.boundary[PP_LINE_L2] = line_at(5.4, 0.0, 0.0);
    lane.boundary[PP_EDGE_RIGHT] = line_at(-6.4, 0.0, 0.0);
    lane.boundary[PP_EDGE_RIGHT].view_end = 55.0;
    const pp_motion_t drift = {.dy = 0.2};
    pp_reference_line_update(&mem, &lane, NULL, &pp_calibration, 1.9, DT, &ref);

    lane.boundary[PP_LINE_L1].present = false;
    lane.boundary[PP_LINE_R1].present = false;
    lane.boundary[PP_LINE_L2].poly.c[0] -= 0.2;
    lane.boundary[PP_EDGE_RIGHT].poly.c[0] -= 0.2;
    pp_reference_line_update(&mem, &lane, &drift, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(ref.valid && ref.inferred && !ref.coasting);
    PP_CHECK_NEAR(ref.centre.c[0], 0.1, 1e-9);
    PP_CHECK_NEAR(ref.width, 3.5, 1e-12);
    PP_CHECK_NEAR(ref.view_end, 55.0, 1e-12);

    lane.boundary[PP_LINE_L2].confidence = (double)pp_calibration.conf_inferred - 0.01;
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(ref.valid && ref.inferred && !ref.coasting);
    PP_CHECK_NEAR(ref.centre.c[0], 0.1, 1e-9);

    lane.boundary[PP_EDGE_RIGHT].present = false;
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(ref.valid && ref.inferred && ref.coasting);
    const int coast = (int)lround((double)pp_calibration.T_coast / DT);
    for (int i = 0; i < coast; i++) {
        pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    }
    PP_CHECK(!ref.valid);
}

static void test_rejected_ego_line_coasts_before_inference(void)
{
    /* PP-PR-052 phân biệt vạch bị loại tạm vì nhiễu với vạch đã LOST. */
    pp_reference_memory_t mem;
    pp_reference_line_t ref;
    pp_reference_memory_reset(&mem);
    pp_lane_at_t0_t lane = two_lines(3.5, 0.0);
    lane.boundary[PP_LINE_L2] = line_at(5.25, 0.0, 0.0);
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    lane.boundary[PP_LINE_L1].present = false;
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(ref.valid && !ref.inferred && !ref.coasting);
    lane.boundary[PP_LINE_R1].poly.c[0] -= 0.6;
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(ref.line_rejected[1]);
    PP_CHECK(ref.valid && ref.coasting && !ref.inferred);
    PP_CHECK_NEAR(ref.centre.c[0], 0.0, 1e-9);
    const int coast = (int)lround((double)pp_calibration.T_coast / DT);
    for (int i = 0; i < coast; i++) {
        lane.boundary[PP_LINE_R1].poly.c[0] = -1.75 - 0.6 - 0.6 * (double)(i % 2);
        pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    }
    PP_CHECK(ref.valid && ref.inferred && !ref.coasting);
}

static void test_inference_needs_a_known_boundary(void)
{
    pp_reference_memory_t mem;
    pp_reference_line_t ref;
    pp_reference_memory_reset(&mem);
    pp_lane_at_t0_t lane = two_lines(3.5, 0.0);
    pp_reference_line_update(&mem, &lane, NULL, &pp_calibration, 1.9, DT, &ref);
    pp_lane_empty(&lane);
    lane.boundary[PP_LINE_L2] = line_at(5.25, 0.0, 0.0);
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(ref.valid && ref.coasting && !ref.inferred);

    lane = two_lines(3.5, 0.0);
    lane.boundary[PP_LINE_L2] = line_at(5.25, 0.0, 0.0);
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    lane.boundary[PP_LINE_L1].present = false;
    lane.boundary[PP_LINE_R1].present = false;
    lane.lane_change = PP_SIDE_LEFT;
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(ref.valid && ref.coasting && !ref.inferred);
}

static void test_jump_of_one_line_is_rejected(void)
{
    pp_reference_memory_t mem;
    pp_reference_line_t ref;
    pp_reference_memory_reset(&mem);
    pp_lane_at_t0_t lane = two_lines(3.5, 0.0);
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    lane.boundary[PP_LINE_L1].poly.c[0] += 0.6;
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(ref.line_rejected[0] && !ref.line_rejected[1]);
    PP_CHECK(ref.valid && !ref.coasting);
    PP_CHECK_NEAR(ref.centre.c[0], 0.0, 1e-12);
}

static void test_shape_jump_is_rejected_without_a_c0_jump(void)
{
    pp_reference_memory_t mem;
    pp_reference_line_t ref;
    pp_reference_memory_reset(&mem);
    pp_lane_at_t0_t lane = two_lines(3.5, 0.0);
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    lane.boundary[PP_LINE_L1].poly.c[2] += 0.0005;
    lane.boundary[PP_LINE_R1].poly.c[2] += 0.0005;
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(ref.line_rejected[0] && ref.line_rejected[1]);
    PP_CHECK(ref.valid && ref.coasting);
    PP_CHECK_NEAR(ref.centre.c[2], 0.0, 1e-10);
}

static void test_jump_of_both_lines_coasts_then_is_accepted(void)
{
    pp_reference_memory_t mem;
    pp_reference_line_t ref;
    pp_reference_memory_reset(&mem);
    pp_lane_at_t0_t lane = two_lines(3.5, 0.0);
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    lane = two_lines(3.5, 0.6);
    const int confirm = (int)lround((double)pp_calibration.T_confirm / DT);
    for (int i = 1; i < confirm; i++) {
        pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
        PP_CHECK(ref.valid && ref.coasting);
        PP_CHECK_NEAR(ref.centre.c[0], 0.0, 1e-9);
    }
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(ref.valid && !ref.coasting);
    PP_CHECK_NEAR(ref.centre.c[0], 0.6, 1e-9);
}

static void test_flickering_jump_is_never_accepted(void)
{
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
    PP_CHECK_NEAR(ref.centre.c[0], 0.6, 1e-9);
    lane = two_lines(3.5, 0.0);
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(!ref.line_rejected[0] && !ref.line_rejected[1]);
    PP_CHECK_NEAR(ref.centre.c[0], 0.0, 1e-9);
}

static void test_shape_change_cannot_slip_in_while_the_memory_ages(void)
{
    /* PP-PR-048: vùng nhìn chung co lại có thể làm candidate sai được nhận sớm. Khi hết lỗi phải
     * nhận lại shape đúng ngay. */
    const pp_motion_t forward = {0.625, 0.0, 0.0};
    pp_reference_memory_t mem;
    pp_reference_line_t ref;
    pp_reference_memory_reset(&mem);
    pp_lane_at_t0_t lane = two_lines(3.5, 0.0);
    pp_reference_line_update(&mem, &lane, &forward, &pp_calibration, 1.9, DT, &ref);
    const int fault = (int)lround(0.9 * (double)pp_calibration.T_confirm / DT);
    for (int i = 0; i < fault; i++) {
        lane = two_lines(3.5, 0.0);
        lane.boundary[PP_LINE_L1].poly.c[3] = 1.0e-6;
        lane.boundary[PP_LINE_R1].poly.c[3] = 1.0e-6;
        pp_reference_line_update(&mem, &lane, &forward, &pp_calibration, 1.9, DT, &ref);
        PP_CHECK(ref.valid);
        if (i == 0) {
            PP_CHECK(ref.line_rejected[0] && ref.line_rejected[1] && ref.coasting);
        }
    }
    lane = two_lines(3.5, 0.0);
    pp_reference_line_update(&mem, &lane, &forward, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(!ref.line_rejected[0] && !ref.line_rejected[1]);
    PP_CHECK(ref.valid && !ref.coasting);
    PP_CHECK_NEAR(ref.centre.c[3], 0.0, 1e-15);
}

static void test_noisy_frame_does_not_hold_back_the_next_one(void)
{
    pp_reference_memory_t mem;
    pp_reference_line_t ref;
    pp_reference_memory_reset(&mem);
    pp_lane_at_t0_t lane = two_lines(3.5, 0.0);
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    lane.boundary[PP_LINE_L1].poly.c[0] += 0.6;
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(ref.line_rejected[0]);
    lane = two_lines(3.5, 0.0);
    lane.boundary[PP_LINE_L1].poly.c[0] += 0.1;
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(!ref.line_rejected[0] && !ref.line_rejected[1]);
}

static void test_slow_drift_within_the_check_is_taken(void)
{
    pp_reference_memory_t mem;
    pp_reference_line_t ref;
    pp_reference_memory_reset(&mem);
    pp_lane_at_t0_t lane = two_lines(3.5, 0.0);
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    const double offsets[] = {0.15, 0.12, 0.11, 0.10};
    for (size_t i = 0U; i < sizeof(offsets) / sizeof(offsets[0]); i++) {
        lane = two_lines(3.5, 0.0);
        lane.boundary[PP_LINE_L1].poly.c[0] += offsets[i];
        pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
        PP_CHECK(ref.line_rejected[0] == (i == 0U));
    }
}

static void test_coast_ends_after_t_coast(void)
{
    pp_reference_memory_t mem;
    pp_reference_line_t ref;
    pp_reference_memory_reset(&mem);
    pp_lane_at_t0_t lane = two_lines(3.5, 0.0);
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    pp_lane_empty(&lane);
    const int coast = (int)lround((double)pp_calibration.T_coast / DT);
    for (int i = 0; i < coast; i++) {
        pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
        PP_CHECK(ref.valid && ref.coasting);
    }
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(!ref.valid);
}

static void test_return_after_a_long_fault_is_taken_at_once(void)
{
    const pp_motion_t forward = {0.625, 0.0, 0.0};
    pp_reference_memory_t mem;
    pp_reference_line_t ref;
    pp_reference_memory_reset(&mem);
    pp_lane_at_t0_t lane = two_lines(3.5, 0.0);
    pp_reference_line_update(&mem, &lane, &forward, &pp_calibration, 1.9, DT, &ref);
    const int fault = (int)lround(2.0 * (double)pp_calibration.T_confirm / DT) + 4;
    for (int i = 0; i < fault; i++) {
        lane = two_lines(3.5, 0.0);
        lane.boundary[PP_LINE_L1].poly.c[2] = 5.0e-4;
        lane.boundary[PP_LINE_R1].poly.c[2] = 5.0e-4;
        pp_reference_line_update(&mem, &lane, &forward, &pp_calibration, 1.9, DT, &ref);
    }
    PP_CHECK(ref.valid && !ref.coasting);
    PP_CHECK_NEAR(ref.centre.c[2], 5.0e-4, 1e-12);
    lane = two_lines(3.5, 0.0);
    pp_reference_line_update(&mem, &lane, &forward, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(!ref.line_rejected[0] && !ref.line_rejected[1]);
    PP_CHECK(ref.valid && !ref.coasting);
    PP_CHECK_NEAR(ref.centre.c[2], 0.0, 1e-12);
}

static void test_old_position_ends_when_its_range_is_behind_the_car(void)
{
    /* Khi xe vượt vùng từng quan sát, vị trí cũ không còn bằng chứng; shape thật lúc đó cũng phải
     * qua T_confirm. */
    const pp_motion_t forward = {0.625, 0.0, 0.0};
    pp_reference_memory_t mem;
    pp_reference_line_t ref;
    pp_reference_memory_reset(&mem);
    pp_lane_at_t0_t lane = two_lines(3.5, 0.0);
    pp_reference_line_update(&mem, &lane, &forward, &pp_calibration, 1.9, DT, &ref);
    const int fault = (int)lround(80.0 / 0.625) + 8;
    for (int i = 0; i < fault; i++) {
        lane = two_lines(3.5, 0.0);
        lane.boundary[PP_LINE_L1].poly.c[2] = 5.0e-4;
        lane.boundary[PP_LINE_R1].poly.c[2] = 5.0e-4;
        pp_reference_line_update(&mem, &lane, &forward, &pp_calibration, 1.9, DT, &ref);
    }
    lane = two_lines(3.5, 0.0);
    pp_reference_line_update(&mem, &lane, &forward, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK(ref.line_rejected[0] && ref.line_rejected[1]);
}

static void test_width_outside_the_odd_keeps_the_stable_line(void)
{
    /* PP-PR-057: khi R1 nhảy làm cặp cách nhau 7 m, tâm phải giữ nửa bề rộng nhớ từ L1. */
    pp_reference_memory_t mem;
    pp_reference_line_t ref;
    pp_reference_memory_reset(&mem);
    pp_lane_at_t0_t lane = two_lines(3.5, 0.0);
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    lane.boundary[PP_LINE_R1].poly.c[0] -= 3.5;
    const int cycles = (int)lround(2.0 * (double)pp_calibration.T_confirm / DT);
    for (int i = 0; i < cycles; i++) {
        pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
        PP_CHECK(ref.valid);
        PP_CHECK_NEAR(ref.centre.c[0], 0.0, 1e-9);
        PP_CHECK_NEAR(ref.width, 3.5, 1e-9);
    }
    PP_CHECK(!ref.line_rejected[1]);
    PP_CHECK_NEAR(mem.width, 3.5, 1e-12);
    lane = two_lines(3.5, 0.0);
    pp_reference_line_update(&mem, &lane, &STILL, &pp_calibration, 1.9, DT, &ref);
    PP_CHECK_NEAR(ref.centre.c[0], 0.0, 1e-9);
}

int main(void)
{
    test_wrong_slots_need_two_matching_markings(3.5);
    test_wrong_slots_need_two_matching_markings(-3.5);
    test_crossed_marking_changes_slot(PP_SIDE_LEFT);
    test_crossed_marking_changes_slot(PP_SIDE_RIGHT);
    test_jump_of_one_line_is_rejected();
    test_shape_jump_is_rejected_without_a_c0_jump();
    test_jump_of_both_lines_coasts_then_is_accepted();
    test_coast_ends_after_t_coast();
    test_flickering_jump_is_never_accepted();
    test_return_after_a_change_is_taken_at_once();
    test_shape_change_cannot_slip_in_while_the_memory_ages();
    test_return_after_a_long_fault_is_taken_at_once();
    test_old_position_ends_when_its_range_is_behind_the_car();
    test_noisy_frame_does_not_hold_back_the_next_one();
    test_slow_drift_within_the_check_is_taken();
    test_centre_between_lines();
    test_one_line_uses_remembered_width();
    test_no_trusted_line();
    test_inferred_centre_uses_remembered_offsets();
    test_inference_needs_a_known_boundary();
    test_rejected_ego_line_coasts_before_inference();
    test_width_memory_filters_and_rejects();
    test_width_outside_the_odd_keeps_the_stable_line();
    test_lane_too_narrow();
    test_walk_straight_and_arc_continuation();
    test_walk_curve();
    test_sampled_walk_matches_cubic();
    test_sampled_project_matches_cubic();
    test_sampled_line_without_range_ahead();
    return PP_TEST_RESULT();
}

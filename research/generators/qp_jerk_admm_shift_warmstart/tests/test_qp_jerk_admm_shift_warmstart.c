/* L0 riêng của qp_jerk_admm_shift_warmstart. Contract chung đã có ở tests/planner/c/test_t7_contract.c. */

#include <math.h>
#include <string.h>

#include "generators/pp_t7.h"
#include "generators/qp.h"
#include "generators/t7_common.h"
#include "output.h"
#include "pp_calibration.h"
#include "pp_test.h"
#include "shift.h"

#define N PP_QP_N
#define CYCLE_S (0.025)

static const pp_vehicle_config_t VP0 = {2.9F, 1.45F, 1.9F, 15.0F, 0.61F, 6.0F, 0.05F};
static pp_t7_ws_t ws;
static pp_qp_ws_t base_ws;

/* ---- sws_shift_hold ---- */

/* Chuỗi tuyến tính 1 + 2i dịch 25 ms = 1/4 bước 0,1 s: 1 + 2(i + 0,25); phần tử cuối giữ nguyên. */
static void test_shift_quarter_step_linear(void)
{
    double in[N];
    double out[N];
    for (size_t i = 0U; i < N; i++) {
        in[i] = 1.0 + (2.0 * (double)i);
    }
    PP_CHECK(sws_shift_hold(in, out, N, PP_GRID_STEP_S, CYCLE_S));
    for (size_t i = 0U; (i + 1U) < N; i++) {
        PP_CHECK_NEAR(out[i], 1.0 + (2.0 * ((double)i + 0.25)), 1e-12);
    }
    PP_CHECK(out[N - 1U] == in[N - 1U]);
}

/* Jerk hằng từng đoạn: out[i] bằng trung bình jerk trên đoạn [i·step + dt, (i+1)·step + dt) của chuỗi cũ. */
static void test_shift_is_mean_over_shifted_interval(void)
{
    double in[N];
    double out[N];
    for (size_t i = 0U; i < N; i++) {
        in[i] = sin(0.7 * (double)i) + (0.1 * (double)i);
    }
    PP_CHECK(sws_shift_hold(in, out, N, PP_GRID_STEP_S, CYCLE_S));
    const size_t sub = 4000U;
    for (size_t i = 0U; i < N; i++) {
        double sum = 0.0;
        for (size_t q = 0U; q < sub; q++) {
            const double t = ((double)i * PP_GRID_STEP_S) + CYCLE_S
                             + (((double)q + 0.5) * PP_GRID_STEP_S / (double)sub);
            size_t idx = (size_t)(t / PP_GRID_STEP_S);
            idx = (idx < N) ? idx : (N - 1U);
            sum += in[idx];
        }
        PP_CHECK_NEAR(out[i], sum / (double)sub, 1e-9);
    }
}

/* Dịch 0,25 s (2,5 bước) trên 5 mẫu: hai mẫu đầu nội suy 1/2, phần còn lại giữ jerk cuối; dịch quá chuỗi
 * cho toàn mẫu cuối. */
static void test_shift_tail_holds_last(void)
{
    const double in[5] = {1.0, 3.0, 7.0, 11.0, 13.0};
    double out[5];
    PP_CHECK(sws_shift_hold(in, out, 5U, 0.1, 0.25));
    PP_CHECK_NEAR(out[0], 9.0, 1e-12);
    PP_CHECK_NEAR(out[1], 12.0, 1e-12);
    PP_CHECK(out[2] == 13.0);
    PP_CHECK(out[3] == 13.0);
    PP_CHECK(out[4] == 13.0);
    PP_CHECK(sws_shift_hold(in, out, 5U, 0.1, 10.0));
    for (size_t i = 0U; i < 5U; i++) {
        PP_CHECK(out[i] == 13.0);
    }
    /* Trên chuỗi tuyến tính, dịch 50 ms một lần bằng hai lần dịch 25 ms (ngoài đoạn giữ đuôi). */
    double once[5];
    double twice[5];
    const double lin[5] = {0.0, 1.0, 2.0, 3.0, 4.0};
    PP_CHECK(sws_shift_hold(lin, once, 5U, 0.1, CYCLE_S));
    PP_CHECK(sws_shift_hold(once, once, 5U, 0.1, CYCLE_S));
    PP_CHECK(sws_shift_hold(lin, twice, 5U, 0.1, 2.0 * CYCLE_S));
    for (size_t i = 0U; (i + 2U) < 5U; i++) {
        PP_CHECK_NEAR(once[i], twice[i], 1e-12);
    }
}

/* Dịch tại chỗ trùng từng bit với dịch ra mảng khác; dt = 0 giữ nguyên; input sai thì không ghi. */
static void test_shift_in_place_zero_and_invalid(void)
{
    double in[N];
    double out[N];
    double inplace[N];
    for (size_t i = 0U; i < N; i++) {
        in[i] = cos(0.3 * (double)i);
    }
    (void)memcpy(inplace, in, sizeof(in));
    PP_CHECK(sws_shift_hold(in, out, N, PP_GRID_STEP_S, 0.06));
    PP_CHECK(sws_shift_hold(inplace, inplace, N, PP_GRID_STEP_S, 0.06));
    PP_CHECK(memcmp(out, inplace, sizeof(out)) == 0);
    PP_CHECK(sws_shift_hold(in, out, N, PP_GRID_STEP_S, 0.0));
    PP_CHECK(memcmp(out, in, sizeof(out)) == 0);

    double keep[N];
    (void)memcpy(keep, out, sizeof(out));
    PP_CHECK(!sws_shift_hold(in, out, N, PP_GRID_STEP_S, -0.025));
    PP_CHECK(!sws_shift_hold(in, out, N, PP_GRID_STEP_S, NAN));
    PP_CHECK(!sws_shift_hold(in, out, N, PP_GRID_STEP_S, INFINITY));
    PP_CHECK(!sws_shift_hold(in, out, N, 0.0, CYCLE_S));
    PP_CHECK(!sws_shift_hold(in, out, 0U, PP_GRID_STEP_S, CYCLE_S));
    PP_CHECK(!sws_shift_hold(NULL, out, N, PP_GRID_STEP_S, CYCLE_S));
    PP_CHECK(memcmp(out, keep, sizeof(out)) == 0);
}

/* ---- generator ---- */

typedef struct {
    pp_reference_line_t ref;
    pp_lateral_state_t start;
    pp_speed_profile_t speed;
    pp_old_path_t old;
    pp_t7_input_t in;
} fixture_t;

static void setup(fixture_t *fx, double d0, double kappa)
{
    (void)memset(fx, 0, sizeof(*fx));
    fx->ref.valid = true;
    fx->ref.centre.c[2] = 0.5 * kappa;
    fx->ref.width = 3.5;
    fx->ref.view_end = 80.0;
    fx->start.d = d0;
    pp_speed_profile(NULL, 0U, 20.0, &fx->speed);
    fx->in.ref = &fx->ref;
    fx->in.start = &fx->start;
    fx->in.speed = &fx->speed;
    fx->in.old = &fx->old;
    fx->in.d_target = 0.0;
    fx->in.vehicle = &VP0;
}

/* Path cũ là output trước, dời 20 m/s × 25 ms về t0 mới; điểm đầu lấy trên path cũ. */
static void chain(fixture_t *fx, const pp_trajectory_point_t prev[PP_TRAJECTORY_POINTS], double shift_s)
{
    fx->old.valid = true;
    fx->old.shift_s = shift_s;
    for (size_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        fx->old.x[k] = (double)prev[k].pose.x - (20.0 * shift_s);
        fx->old.y[k] = (double)prev[k].pose.y;
        fx->old.yaw[k] = (double)prev[k].pose.yaw;
        fx->old.kappa[k] = (double)prev[k].curvature;
        fx->old.v[k] = (double)prev[k].longitudinal_velocity_mps;
        fx->old.a[k] = (double)prev[k].acceleration_mps2;
        fx->old.d_dot[k] = (double)prev[k].lateral_velocity_mps;
    }
    pp_path_sample_t p;
    PP_CHECK(pp_stitch_sample_old(&fx->old, 0.0, &p));
    fx->start.d = p.y;
    fx->start.d_dot = p.d_dot;
    fx->in.from_old = true;
}

/* qp_jerk_admm.c chép lại, với ws QP riêng; shift_s > 0 thì dịch warm start bằng tay trước khi giải. */
static bool base_generate(const pp_calibration_t *cal, const fixture_t *fx, double shift_s, size_t x_blocks,
                          bool dual, pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS])
{
    pp_qp_problem_t pb;
    pp_lateral_path_t lateral;
    pp_ref_samples_t samples;
    (void)memset(pts, 0, sizeof(pp_trajectory_point_t) * PP_TRAJECTORY_POINTS);
    if (shift_s > 0.0) {
        for (size_t b = 0U; b < x_blocks; b++) {
            PP_CHECK(sws_shift_hold(&base_ws.x[b * N], &base_ws.x[b * N], N, PP_GRID_STEP_S, shift_s));
        }
        for (size_t b = 0U; dual && (b < (PP_QP_ROWS / N)); b++) {
            PP_CHECK(sws_shift_hold(&base_ws.y[b * N], &base_ws.y[b * N], N, PP_GRID_STEP_S, shift_s));
        }
    }
    pp_t7_qp_problem(cal, &fx->in, &pb);
    const bool ok = pp_generate_qp(&base_ws, cal, &pb, &lateral)
                    && pp_output_points(fx->in.ref, &lateral, fx->in.speed, (double)fx->in.vehicle->wheelbase,
                                        pts, &samples);
    if (!ok) {
        pp_qp_reset(&base_ws);
    }
    return ok;
}

static bool mine_generate(const pp_calibration_t *cal, const fixture_t *fx,
                          pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS])
{
    pp_ref_samples_t samples;
    (void)memset(pts, 0, sizeof(pp_trajectory_point_t) * PP_TRAJECTORY_POINTS);
    return pp_t7_generate(&ws, cal, &fx->in, pts, &samples);
}

/* Không có nghiệm dùng được (chu kỳ đầu sau reset, from_old false): trùng từng bit với qp_jerk_admm. */
static void test_matches_base_without_usable_previous(void)
{
    fixture_t fx;
    pp_trajectory_point_t mine[PP_TRAJECTORY_POINTS];
    pp_trajectory_point_t base[PP_TRAJECTORY_POINTS];
    (void)memset(&ws, 0xA5, sizeof(ws));
    pp_t7_reset(&ws);
    pp_qp_reset(&base_ws);
    setup(&fx, 0.4, 0.002);
    PP_CHECK(mine_generate(&pp_calibration, &fx, mine));
    PP_CHECK(base_generate(&pp_calibration, &fx, 0.0, 0U, false, base));
    PP_CHECK(ws.fallback == SWS_NO_WARM);
    PP_CHECK(memcmp(mine, base, sizeof(mine)) == 0);
    PP_CHECK(memcmp(ws.qp.x, base_ws.x, sizeof(base_ws.x)) == 0);
    PP_CHECK(memcmp(ws.qp.y, base_ws.y, sizeof(base_ws.y)) == 0);
    PP_CHECK(ws.qp.rho == base_ws.rho);
    /* Nhiều chu kỳ from_old false, kể cả khi có path cũ hợp lệ: vẫn trùng từng bit. */
    for (size_t c = 0U; c < 8U; c++) {
        setup(&fx, 0.4 - (0.03 * (double)c), 0.002 + (0.0002 * (double)c));
        chain(&fx, mine, CYCLE_S);
        fx.in.from_old = false;
        PP_CHECK(mine_generate(&pp_calibration, &fx, mine));
        PP_CHECK(base_generate(&pp_calibration, &fx, 0.0, 0U, false, base));
        PP_CHECK(ws.fallback == SWS_NOT_FROM_OLD);
        PP_CHECK(memcmp(mine, base, sizeof(mine)) == 0);
    }
}

/* start_from_car, follow đổi và shift_s sai: giữ warm start gốc, trùng từng bit với qp_jerk_admm. */
static void test_other_fallbacks_match_base(void)
{
    fixture_t fx;
    pp_trajectory_point_t mine[PP_TRAJECTORY_POINTS];
    pp_trajectory_point_t base[PP_TRAJECTORY_POINTS];
    pp_t7_reset(&ws);
    pp_qp_reset(&base_ws);
    setup(&fx, 0.3, 0.001);
    PP_CHECK(mine_generate(&pp_calibration, &fx, mine));
    PP_CHECK(base_generate(&pp_calibration, &fx, 0.0, 0U, false, base));

    chain(&fx, mine, CYCLE_S);
    fx.in.start_from_car = true;
    PP_CHECK(mine_generate(&pp_calibration, &fx, mine));
    PP_CHECK(base_generate(&pp_calibration, &fx, 0.0, 0U, false, base));
    PP_CHECK(ws.fallback == SWS_FROM_CAR);
    PP_CHECK(memcmp(mine, base, sizeof(mine)) == 0);

    setup(&fx, 0.3, 0.001);
    chain(&fx, mine, CYCLE_S);
    fx.in.follow = true;
    PP_CHECK(mine_generate(&pp_calibration, &fx, mine));
    PP_CHECK(base_generate(&pp_calibration, &fx, 0.0, 0U, false, base));
    PP_CHECK(ws.fallback == SWS_FOLLOW_CHANGED);
    PP_CHECK(memcmp(mine, base, sizeof(mine)) == 0);

    /* Lần gọi thứ hai trong cùng chu kỳ (FOLLOW không dùng được, giải lại theo làn): không dịch. */
    fx.in.follow = false;
    PP_CHECK(mine_generate(&pp_calibration, &fx, mine));
    PP_CHECK(base_generate(&pp_calibration, &fx, 0.0, 0U, false, base));
    PP_CHECK(ws.fallback == SWS_FOLLOW_CHANGED);
    PP_CHECK(memcmp(mine, base, sizeof(mine)) == 0);

    setup(&fx, 0.3, 0.001);
    chain(&fx, mine, 0.0);
    PP_CHECK(mine_generate(&pp_calibration, &fx, mine));
    PP_CHECK(base_generate(&pp_calibration, &fx, 0.0, 0U, false, base));
    PP_CHECK(ws.fallback == SWS_BAD_SHIFT);
    PP_CHECK(memcmp(mine, base, sizeof(mine)) == 0);
}

/* Khi dịch được: trùng từng bit với qp_jerk_admm có warm start dịch bằng tay đúng old->shift_s, ở cả ba
 * mức sws_shift_vars và cả chu kỳ bị lỡ (50 ms). */
static void test_shifted_warm_start_is_wired(void)
{
    static const size_t x_blocks[3] = {1U, 3U, 3U};
    for (size_t mode = 0U; mode < 3U; mode++) {
        pp_calibration_t cal = pp_calibration;
        cal.sws_shift_vars = (float)mode;
        cal.qp_iters = 10.0F;
        fixture_t fx;
        pp_trajectory_point_t mine[PP_TRAJECTORY_POINTS];
        pp_trajectory_point_t base[PP_TRAJECTORY_POINTS];
        pp_t7_reset(&ws);
        pp_qp_reset(&base_ws);
        setup(&fx, 0.5, 0.002);
        PP_CHECK(mine_generate(&cal, &fx, mine));
        PP_CHECK(base_generate(&cal, &fx, 0.0, 0U, false, base));
        for (size_t c = 0U; c < 6U; c++) {
            const double shift_s = (c == 3U) ? (2.0 * CYCLE_S) : CYCLE_S;
            setup(&fx, 0.0, 0.002);
            chain(&fx, mine, shift_s);
            PP_CHECK(mine_generate(&cal, &fx, mine));
            PP_CHECK(base_generate(&cal, &fx, shift_s, x_blocks[mode], mode == 2U, base));
            PP_CHECK(ws.fallback == SWS_SHIFTED);
            PP_CHECK(memcmp(mine, base, sizeof(mine)) == 0);
        }
    }
}

/* Chuỗi chu kỳ đưa về giữa trên đường thẳng, 10 vòng: path hữu hạn và cuối path về gần mục tiêu. */
static void test_shifted_sequence_is_sane(void)
{
    pp_calibration_t cal = pp_calibration;
    cal.qp_iters = 10.0F;
    fixture_t fx;
    pp_trajectory_point_t mine[PP_TRAJECTORY_POINTS];
    pp_t7_reset(&ws);
    setup(&fx, 0.5, 0.0);
    PP_CHECK(mine_generate(&cal, &fx, mine));
    for (size_t c = 0U; c < 40U; c++) {
        setup(&fx, 0.0, 0.0);
        chain(&fx, mine, CYCLE_S);
        PP_CHECK(mine_generate(&cal, &fx, mine));
        PP_CHECK(ws.fallback == SWS_SHIFTED);
        for (size_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
            PP_CHECK(isfinite(mine[k].pose.y) && isfinite(mine[k].curvature));
        }
    }
    PP_CHECK(fabs((double)mine[PP_TRAJECTORY_POINTS - 1U].pose.y) < 0.1);
}

int main(void)
{
    test_shift_quarter_step_linear();
    test_shift_is_mean_over_shifted_interval();
    test_shift_tail_holds_last();
    test_shift_in_place_zero_and_invalid();
    test_matches_base_without_usable_previous();
    test_other_fallbacks_match_base();
    test_shifted_warm_start_is_wired();
    test_shifted_sequence_is_sane();
    return PP_TEST_RESULT();
}

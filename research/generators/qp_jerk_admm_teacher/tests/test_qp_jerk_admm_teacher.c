/* L0 riêng của qp_jerk_admm_teacher. Contract chung đã có ở tests/planner/c/test_t7_contract.c. */

#include <math.h>
#include <string.h>

#include "generators/pp_t7.h"
#include "generators/qp.h"
#include "generators/t7_common.h"
#include "mlp_features.h"
#include "output.h"
#include "pp_calibration.h"
#include "pp_test.h"

static const pp_vehicle_config_t VP0 = {2.9F, 1.45F, 1.9F, 15.0F, 0.61F, 6.0F, 0.05F};
static pp_t7_ws_t ws;
static pp_qp_ws_t plain;
static pp_qp_ws_t ref;

typedef struct {
    pp_reference_line_t ref;
    pp_lateral_state_t start;
    pp_speed_profile_t speed;
    pp_old_path_t old;
    pp_t7_input_t in;
} fixture_t;

static void setup(fixture_t *fx, double d0, double kappa, double v)
{
    (void)memset(fx, 0, sizeof(*fx));
    fx->ref.valid = true;
    fx->ref.centre.c[2] = 0.5 * kappa;
    fx->ref.width = 3.5;
    fx->ref.view_end = 80.0;
    fx->start.d = d0;
    fx->start.d_dot = 0.1;
    pp_speed_profile(NULL, 0U, v, &fx->speed);
    fx->in.ref = &fx->ref;
    fx->in.start = &fx->start;
    fx->in.speed = &fx->speed;
    fx->in.old = &fx->old;
    fx->in.d_target = 0.1;
    fx->in.vehicle = &VP0;
}

/* Path lái trùng từng bit với qp_jerk_admm qua nhiều chu kỳ warm start. */
static void test_drive_matches_qp_jerk_admm(void)
{
    fixture_t fx;
    pp_trajectory_point_t mine[PP_TRAJECTORY_POINTS];
    pp_trajectory_point_t base[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
    pp_qp_problem_t pb;
    pp_lateral_path_t lateral;
    pp_t7_reset(&ws);
    pp_qp_reset(&plain);
    for (int cycle = 0; cycle < 3; cycle++) {
        setup(&fx, 0.4 - (0.05 * (double)cycle), 0.002, 25.0);
        PP_CHECK(pp_t7_generate(&ws, &pp_calibration, &fx.in, mine, &samples));
        pp_t7_qp_problem(&pp_calibration, &fx.in, &pb);
        PP_CHECK(pp_generate_qp(&plain, &pp_calibration, &pb, &lateral));
        PP_CHECK(pp_output_points(fx.in.ref, &lateral, fx.in.speed, (double)VP0.wheelbase, base, &samples));
        PP_CHECK(memcmp(mine, base, sizeof(mine)) == 0);
        PP_CHECK(ws.record[TR_DRIVE_ITERS] == (double)pp_calibration.qp_iters);
    }
}

/* Bản ghi: đặc trưng, bài toán và nhãn đúng với tính trực tiếp; số lần gọi tăng và không về 0 khi reset. */
static void test_record_features_label_and_count(void)
{
    fixture_t fx;
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
    pp_qp_problem_t pb;
    pp_lateral_path_t lateral;
    double features[MLP_FEATURES];
    double packed[TR_PROBLEM_SIZE];
    setup(&fx, -0.3, -0.003, 22.0);
    (void)memset(&ws, 0, sizeof(ws));
    pp_t7_reset(&ws);
    PP_CHECK(pp_t7_generate(&ws, &pp_calibration, &fx.in, pts, &samples));
    PP_CHECK(ws.record[TR_LAYOUT] == TEACHER_LAYOUT);
    PP_CHECK(ws.record[TR_SIZE] == (double)TR_DOUBLES);
    PP_CHECK(ws.record[TR_COUNT] == 1.0);
    PP_CHECK(ws.record[TR_LABEL_OK] == 1.0);
    pp_t7_qp_problem(&pp_calibration, &fx.in, &pb);
    mlp_features(&pb, features);
    PP_CHECK(memcmp(features, &ws.record[TR_FEATURES], sizeof(features)) == 0);
    teacher_pack_problem(&pb, packed);
    PP_CHECK(memcmp(packed, &ws.record[TR_PROBLEM], sizeof(packed)) == 0);
    /* Nhãn = nghiệm khởi động lạnh 1000 vòng trên ws riêng. */
    pp_calibration_t cal = pp_calibration;
    cal.qp_iters = (float)TEACHER_REF_ITERS;
    pp_qp_reset(&ref);
    PP_CHECK(pp_generate_qp(&ref, &cal, &pb, &lateral));
    PP_CHECK(ref.iterations == TEACHER_REF_ITERS);
    PP_CHECK(memcmp(ref.x, &ws.record[TR_LABEL], sizeof(double) * PP_QP_N) == 0);
    pp_t7_reset(&ws);
    PP_CHECK(pp_t7_generate(&ws, &pp_calibration, &fx.in, pts, &samples));
    PP_CHECK(ws.record[TR_COUNT] == 2.0);
}

/* Nghiệm 1000 vòng hội tụ: residual nhỏ, không vi phạm hàng cứng; giới hạn tính lại khớp qp.c (z của
 * ADMM luôn nằm trong giới hạn, nên với x hội tụ vi phạm ≈ 0). Cua R = 500 m ở 25 m/s. */
static void test_label_converged_and_checked(void)
{
    fixture_t fx;
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
    setup(&fx, 0.2, 0.002, 25.0);
    pp_t7_reset(&ws);
    PP_CHECK(pp_t7_generate(&ws, &pp_calibration, &fx.in, pts, &samples));
    PP_CHECK(ws.record[TR_PRIMAL] < 1.0e-4);
    PP_CHECK(ws.record[TR_DUAL] < 1.0e-3);
    PP_CHECK(ws.record[TR_VIOLATION] < 1.0e-4);
    PP_CHECK(ws.record[TR_VIOLATION] == fmax(ws.record[TR_VIOL_AY], ws.record[TR_VIOL_JERK]));
    /* Một nghiệm cố ý lệch phải cho vi phạm dương: kiểm phép tính vi phạm không trả 0 vô điều kiện. */
    pp_qp_problem_t pb;
    double dual = 0.0;
    double viol_ay = 0.0;
    double viol_jerk = 0.0;
    pp_lateral_path_t lateral;
    pp_calibration_t cal = pp_calibration;
    cal.qp_iters = (float)TEACHER_REF_ITERS;
    pp_t7_qp_problem(&pp_calibration, &fx.in, &pb);
    pp_qp_reset(&ref);
    PP_CHECK(pp_generate_qp(&ref, &cal, &pb, &lateral));
    teacher_check(&ref, &cal, &pb, 0.0, false, &dual, &viol_ay, &viol_jerk);
    PP_CHECK_NEAR(dual, ws.record[TR_DUAL], 1e-15);
    PP_CHECK_NEAR(fmax(viol_ay, viol_jerk), ws.record[TR_VIOLATION], 1e-15);
    ref.x[0] += 30.0;
    teacher_check(&ref, &cal, &pb, 0.0, false, &dual, &viol_ay, &viol_jerk);
    PP_CHECK(viol_jerk > 1.0);
    PP_CHECK(viol_ay > 0.1);
    PP_CHECK(dual > ws.record[TR_DUAL]);
}

/* Input không hữu hạn: không có path, nhãn đánh dấu hỏng, lần sau dùng lại được. */
static void test_non_finite_marks_label(void)
{
    fixture_t fx;
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
    setup(&fx, NAN, 0.001, 25.0);
    pp_t7_reset(&ws);
    PP_CHECK(!pp_t7_generate(&ws, &pp_calibration, &fx.in, pts, &samples));
    PP_CHECK(ws.record[TR_LABEL_OK] == 0.0);
    PP_CHECK(ws.record[TR_DRIVE_OK] == 0.0);
    setup(&fx, 0.1, 0.001, 25.0);
    PP_CHECK(pp_t7_generate(&ws, &pp_calibration, &fx.in, pts, &samples));
    PP_CHECK(ws.record[TR_LABEL_OK] == 1.0);
}

/* Cua R = 200 m ở 25 m/s từ a_y = 0: hàng a_y cứng đòi jerk vượt trần ngay bước đầu, bài toán cứng bất khả
 * thi. Bản ghi phải cho thấy điều đó (vi phạm và residual nguyên thủy lớn), để loại khỏi nhãn. */
static void test_infeasible_is_visible(void)
{
    fixture_t fx;
    pp_trajectory_point_t pts[PP_TRAJECTORY_POINTS];
    pp_ref_samples_t samples;
    setup(&fx, 0.0, 0.005, 25.0);
    fx.start.d_dot = 0.0;
    pp_t7_reset(&ws);
    PP_CHECK(pp_t7_generate(&ws, &pp_calibration, &fx.in, pts, &samples));
    PP_CHECK(ws.record[TR_LABEL_OK] == 1.0);
    PP_CHECK(ws.record[TR_VIOLATION] > 0.1);
    PP_CHECK(ws.record[TR_PRIMAL] > 1.0e-2);
}

int main(void)
{
    test_drive_matches_qp_jerk_admm();
    test_record_features_label_and_count();
    test_label_converged_and_checked();
    test_infeasible_is_visible();
    test_non_finite_marks_label();
    return PP_TEST_RESULT();
}

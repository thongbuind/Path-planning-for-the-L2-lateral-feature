/* quintic_ay_sampling (PP-TS-024 V2, PP-TS-031). Thiết kế và lý do chọn: notes.md của thư mục này. */

#include <math.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "driver_shape.h"
#include "feasibility.h"
#include "generators/pp_t7.h"
#include "generators/t7_common.h"
#include "output.h"
#include "reference_line.h"

/* Hai hằng số chép từ T11 (output.c) để dự báo độ cong khớp pp_output_points. */
#define LAB_QAS_FRENET_MIN_SPEED_MPS (1.0)
#define LAB_QAS_FRENET_MIN_Q (0.1)
/* Hình dạng đơn vị có |d| <= 1; hành lang 2 chỉ để lab_driver_bump không từ chối. */
#define LAB_QAS_UNIT_CORRIDOR (2.0)

void pp_t7_reset(pp_t7_ws_t *ws)
{
    if (ws != NULL) {
        ws->work = 0U;
        ws->fallback = 0U;
    }
}

void lab_qas_frame(const pp_t7_input_t *in, lab_qas_frame_t *frame)
{
    pp_ref_walker_t walker;
    pp_ref_point_t r;
    pp_ref_walk_begin(&walker, in->ref, &r);
    for (size_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        pp_ref_walk_to(&walker, in->speed->s[k], &r);
        const double v = (double)(float)in->speed->v[k];
        frame->v2[k] = v * v;
        frame->s_dot[k] = fmax(in->speed->v[k], LAB_QAS_FRENET_MIN_SPEED_MPS);
        frame->a[k] = in->speed->a[k];
        frame->kappa[k] = r.kappa;
        frame->dkappa[k] = r.dkappa;
    }
}

void lab_qas_predict(const lab_qas_frame_t *frame, const pp_lateral_path_t *base, const pp_lateral_path_t *shape,
                     double offset, double *ay_max, double *jerk_max)
{
    double ay[PP_TRAJECTORY_POINTS];
    const uint32_t window = (uint32_t)lround(PP_JERK_WINDOW_S / PP_GRID_STEP_S);
    double peak = 0.0;
    double jerk = 0.0;
    for (size_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        const double d = base->d[k] + (offset * shape->d[k]);
        const double d_dot = base->d_dot[k] + (offset * shape->d_dot[k]);
        const double d_ddot = base->d_ddot[k] + (offset * shape->d_ddot[k]);
        const double s_dot = frame->s_dot[k];
        const double kappa_ref = frame->kappa[k];
        /* Công thức độ cong của T11; cos(atan t) = 1/sqrt(1 + t²), tan(atan t) = t. */
        const double d1 = d_dot / s_dot;
        const double d2 = (d_ddot - (d1 * frame->a[k])) / (s_dot * s_dot);
        const double q = fmax(1.0 - (kappa_ref * d), LAB_QAS_FRENET_MIN_Q);
        const double t = d1 / q;
        const double c2 = 1.0 / (1.0 + (t * t));
        const double kappa = (((((d2 + (((frame->dkappa[k] * d) + (kappa_ref * d1)) * t)) * c2) / q) + kappa_ref)
                              * sqrt(c2)) / q;
        ay[k] = frame->v2[k] * (double)(float)kappa;
        peak = fmax(peak, fabs(ay[k]));
    }
    for (uint32_t k = 0U; (k + window) < PP_TRAJECTORY_POINTS; k++) {
        jerk = fmax(jerk, fabs((ay[k + window] - ay[k]) / ((double)window * PP_GRID_STEP_S)));
    }
    *ay_max = peak;
    *jerk_max = jerk;
}

/* Điều kiện dùng chung của PP-TS-024 mục 2.4, đọc từ input trước khi tính gì thêm. */
static uint32_t gate_inputs(const pp_calibration_t *cal, const pp_t7_input_t *in)
{
    const pp_reference_line_t *ref = in->ref;
    uint32_t reason = LAB_QAS_APPLIED;
    if (in->follow) {
        reason = LAB_QAS_FOLLOW;
    } else if (in->start_from_car) {
        reason = LAB_QAS_START_FROM_CAR;
    } else if (in->recentering) {
        reason = LAB_QAS_RECENTERING;
    } else if (!(fabs(in->d_target) <= (double)cal->qas_offset_max_m)) {
        reason = LAB_QAS_OFFSET;
    } else if (ref->coasting || ref->inferred || ref->line_rejected[0] || ref->line_rejected[1]) {
        reason = LAB_QAS_LANE;
    } else if (in->objects == NULL) {
        reason = LAB_QAS_OBJECTS;
    } else {
    }
    return reason;
}

/* Hành lang từng phía theo vật thể (PP-TS-024 mục 2.4): vật thể có tâm lệch khỏi đường tham chiếu quá nửa
 * bề rộng của nó, và mép gần nằm trong làn mình hoặc làn kề (1,5 bề rộng làn), chặn hiệu chỉnh về phía nó.
 * Vật thể nằm giữa làn mình (xe trước, xe sau) không chặn; T8 lo dời tâm. Dữ liệu không hữu hạn chặn cả hai. */
static void object_sides(const pp_t7_input_t *in, bool blocked[2])
{
    const pp_object_list_t *list = in->objects;
    const double reach = 1.5 * in->ref->width;
    blocked[0] = false;
    blocked[1] = false;
    for (size_t i = 0U; (i < (size_t)list->num_objects) && (i < (size_t)PP_MAX_OBJECTS); i++) {
        const pp_object_t *o = &list->objects[i];
        pp_ref_point_t foot;
        double d = NAN;
        if (isfinite(o->x) && isfinite(o->y)) {
            pp_ref_project(in->ref, (double)o->x, (double)o->y, &foot, &d);
        }
        const double half = 0.5 * (double)o->width;
        if (!isfinite(d) || !isfinite(half)) {
            blocked[0] = true;
            blocked[1] = true;
        } else if ((fabs(d) > half) && ((fabs(d) - half) < reach)) {
            blocked[(d > 0.0) ? 0U : 1U] = true;
        } else {
        }
    }
}

/* Ứng viên đạt khi a_y không vượt aysmax và jerk dự báo không tăng quá dung sai so với path gốc, đồng thời
 * không vượt jerk_target_hwa (trừ khi path gốc đã vượt; khi đó không được tăng). */
static bool admissible(const pp_calibration_t *cal, double ay, double jerk, double jerk_base)
{
    return (ay <= PP_AYSMAX) && (jerk <= (jerk_base + (double)cal->qas_jerk_tol_mps3))
           && ((jerk <= (double)cal->jerk_target_hwa) || (jerk <= jerk_base));
}

/* Biên độ lớn nhất của dấu sign để |base + sign × a × shape| <= corridor trên [0, end]; âm nếu path gốc
 * đã ra ngoài hành lang. Thu nhỏ cả biên độ, không kẹp từng mẫu (PP-TS-024 mục 2, ý 1). */
static double corridor_cap(const pp_lateral_path_t *base, const pp_lateral_path_t *shape, size_t last,
                           double sign, double corridor)
{
    double cap = INFINITY;
    for (size_t k = 0U; k <= last; k++) {
        const double room = corridor - (sign * base->d[k]);
        if (!(fabs(base->d[k]) <= corridor)) {
            cap = -1.0;
        } else if (shape->d[k] > 0.0) {
            cap = fmin(cap, room / shape->d[k]);
        } else {
        }
    }
    return cap;
}

/* Hiệu chỉnh bằng 0 cùng ba đạo hàm tại t = 0 và từ end trở đi, nên a_y ở đó không đổi với mọi ứng viên:
 * max |a_y| trên các điểm đó là cận dưới của đỉnh a_y mọi ứng viên (cách tính như pp_feasibility_check). */
static double fixed_ay_peak(const pp_trajectory_point_t points[PP_TRAJECTORY_POINTS], size_t last)
{
    double peak = 0.0;
    for (size_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
        if ((k == 0U) || (k >= last)) {
            const double v = (double)points[k].longitudinal_velocity_mps;
            peak = fmax(peak, fabs(v * v * (double)points[k].curvature));
        }
    }
    return peak;
}

uint32_t lab_qas_correct(const pp_calibration_t *cal, const pp_t7_input_t *in, const pp_lateral_path_t *base,
                         pp_trajectory_point_t points[PP_TRAJECTORY_POINTS], const pp_ref_samples_t *samples,
                         lab_qas_choice_t *choice)
{
    pp_path_check_t check;
    size_t last = 0U;
    (void)memset(choice, 0, sizeof(*choice));
    uint32_t reason = gate_inputs(cal, in);

    while ((last + 1U < PP_TRAJECTORY_POINTS) && samples->in_view[last + 1U]) {
        last++;
    }
    const double end = samples->in_view[0] ? ((double)last * PP_GRID_STEP_S) : 0.0;
    const double corridor = (0.5 * (in->ref->width - (double)in->vehicle->vehicle_width))
                            - (double)cal->qas_corridor_margin_m;
    choice->end_s = end;
    if (reason == LAB_QAS_APPLIED) {
        if (!(end >= (double)cal->qas_view_min_s)) {
            reason = LAB_QAS_SHORT_VIEW;
        } else if (!(corridor > 0.0)) {
            reason = LAB_QAS_CORRIDOR;
        } else {
            pp_feasibility_check(points, samples, &check);
            choice->ay_base = check.ay_max;
            choice->jerk_base = check.jerk_max;
            if (!(check.ay_need_max >= (double)cal->qas_ay_need_min_mps2)) {
                reason = LAB_QAS_NO_CURVE;
            } else if (!(check.ay_need_max < (PP_AYSMAX - (double)cal->qas_ay_need_margin_mps2))) {
                reason = LAB_QAS_SHARP_CURVE;
            } else if (!(fixed_ay_peak(points, last) < (check.ay_max - (double)cal->qas_ay_gain_min_mps2))) {
                reason = LAB_QAS_NO_GAIN;  /* Đỉnh a_y nằm ở chỗ mọi ứng viên trùng path gốc (cung dài). */
            } else {
            }
        }
    }
    bool blocked[2] = {false, false};
    if (reason == LAB_QAS_APPLIED) {
        object_sides(in, blocked);
        reason = (blocked[0] && blocked[1]) ? LAB_QAS_OBJECTS : LAB_QAS_APPLIED;
    }
    if (reason != LAB_QAS_APPLIED) {
        choice->reason = reason;
        return reason;
    }

    /* Phần chung: mẫu đường tham chiếu một lần; mỗi vị trí đỉnh một hình dạng đơn vị, dùng cho cả hai dấu và
     * mọi mức biên độ. Ứng viên chỉ là base + offset × shape, không lấy mẫu lại đường. */
    lab_qas_frame_t frame;
    pp_lateral_path_t zero;
    pp_lateral_path_t shapes[2];
    lab_qas_frame(in, &frame);
    (void)memset(&zero, 0, sizeof(zero));
    const double peaks[2] = {(double)cal->qas_peak_early * end, (double)cal->qas_peak_late * end};
    const double amplitude = (double)cal->qas_amplitude_m;
    /* Thang biên độ bước qas_amplitude_step_m tới amplitude; bước nở ra nếu cần quá LAB_QAS_STEPS_MAX mức. */
    const double step = fmax((double)cal->qas_amplitude_step_m, amplitude / (double)LAB_QAS_STEPS_MAX);
    const double gain_min = (double)cal->qas_ay_gain_min_mps2;
    bool found = false;
    size_t best_peak = 0U;
    double best_offset = 0.0;
    double best_ay = choice->ay_base - gain_min;
    double best_jerk = INFINITY;
    bool any_room = false;

    for (size_t p = 0U; p < 2U; p++) {
        if (!lab_driver_bump(&zero, end, peaks[p], 1.0, LAB_QAS_UNIT_CORRIDOR, &shapes[p])) {
            continue;
        }
        for (size_t side = 0U; side < 2U; side++) {
            if (blocked[side]) {
                continue;
            }
            const double sign = (side == 0U) ? 1.0 : -1.0;
            const double cap = corridor_cap(base, &shapes[p], last, sign, corridor);
            const double top = fmin(amplitude, cap);
            if (!(top > 0.0)) {
                continue;
            }
            any_room = true;
            /* Tăng biên độ dần. Đỉnh a_y và jerk theo biên độ gần như hàm lồi (T11 gần tuyến tính theo d),
             * nên dừng ở mức đầu tiên không đạt hoặc không còn giảm a_y. */
            double prev_ay = choice->ay_base;
            bool more = true;
            for (uint32_t j = 1U; more && (j <= LAB_QAS_STEPS_MAX); j++) {
                const double level = fmin((double)j * step, top);
                const double offset = sign * level;
                more = level < top;
                double ay;
                double jerk;
                lab_qas_predict(&frame, base, &shapes[p], offset, &ay, &jerk);
                choice->evaluated++;
                if (!admissible(cal, ay, jerk, choice->jerk_base) || !(ay < prev_ay)) {
                    break;
                }
                prev_ay = ay;
                if ((ay < best_ay) || ((ay == best_ay) && (jerk < best_jerk))) {
                    found = true;
                    best_peak = p;
                    best_offset = offset;
                    best_ay = ay;
                    best_jerk = jerk;
                }
            }
        }
    }
    if (!found) {
        reason = (any_room || !(amplitude > 0.0)) ? LAB_QAS_NO_GAIN : LAB_QAS_CORRIDOR;
    } else {
        /* Kiểm lại ứng viên được chọn bằng T11 và feasibility check thật trước khi thay path. */
        pp_lateral_path_t lateral;
        pp_trajectory_point_t candidate[PP_TRAJECTORY_POINTS];
        pp_path_check_t final_check;
        const pp_lateral_path_t *shape = &shapes[best_peak];
        for (size_t k = 0U; k < PP_TRAJECTORY_POINTS; k++) {
            lateral.d[k] = base->d[k] + (best_offset * shape->d[k]);
            lateral.d_dot[k] = base->d_dot[k] + (best_offset * shape->d_dot[k]);
            lateral.d_ddot[k] = base->d_ddot[k] + (best_offset * shape->d_ddot[k]);
        }
        reason = LAB_QAS_CHECK;
        if (pp_output_points(in->ref, &lateral, in->speed, (double)in->vehicle->wheelbase, candidate, NULL)) {
            pp_feasibility_check(candidate, samples, &final_check);
            if (admissible(cal, final_check.ay_max, final_check.jerk_max, choice->jerk_base)
                && (final_check.ay_max <= (choice->ay_base - gain_min))) {
                (void)memcpy(points, candidate, sizeof(candidate));
                reason = LAB_QAS_APPLIED;
                choice->peak_s = peaks[best_peak];
                choice->offset_m = best_offset;
                choice->ay_best = final_check.ay_max;
                choice->jerk_best = final_check.jerk_max;
            }
        }
    }
    choice->reason = reason;
    return reason;
}

bool pp_t7_generate(pp_t7_ws_t *ws, const pp_calibration_t *cal, const pp_t7_input_t *in,
                    pp_trajectory_point_t points[PP_TRAJECTORY_POINTS], pp_ref_samples_t *samples)
{
    pp_lateral_path_t lateral;
    uint32_t tries = 0U;
    const bool ok = pp_t7_quintic_search(cal, in, &lateral, points, samples, &tries);
    if (ok) {
        lab_qas_choice_t choice;
        ws->fallback = lab_qas_correct(cal, in, &lateral, points, samples, &choice);
        ws->work = tries + choice.evaluated;
    } else {
        ws->fallback = LAB_QAS_BASE_FAILED;
        ws->work = tries;
    }
    return ok;
}

#ifdef PP_T7_TELEMETRY
void pp_t7_report(const pp_t7_ws_t *ws, pp_t7_telemetry_t *out)
{
    out->work = ws->work;
    out->fallback = ws->fallback;
    out->infer_ops = 0U;
    out->residual = NAN;
    out->slack = NAN;
}
#endif

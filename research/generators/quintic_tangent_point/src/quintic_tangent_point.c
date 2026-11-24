/* quintic_tangent_point (PP-TS-024 mục 2, V1). Chỉ sửa trong thư mục này (research/generators/README.md).
 * Mỗi chu kỳ: path quintic_duration; nếu đủ điều kiện của PP-TS-024 2.4 thì tìm tiếp điểm trên vạch trong
 * cua trong cửa sổ nhìn trước, cộng một hiệu chỉnh smoothstep bậc 7 (common/driver_shape) về phía trong,
 * đỉnh tại thời điểm tới tiếp điểm, về 0 ở cuối tầm nhìn. Đỉnh của path cách d_target đúng biên độ.
 * Bắt đầu và giữ khi tiếp điểm nằm trước cuối cửa sổ (qtp_peak_check bật: lúc bắt đầu, từ đỉnh vẫn phải
 * thấy tiếp điểm). Hiệu chỉnh chỉ đi vào trong; đỉnh không vào trong hơn path quintic tại đỉnh quá
 * qtp_dlc_margin_m (mốc lấy lúc bắt đầu, chỉ được ra ngoài). Biên độ tăng dần theo qtp_amplitude_rate.
 * Thả khi tiếp điểm mất (gần hết cua) hoặc một điều kiện fallback bật: path quintic_duration đưa xe về
 * d_target trong T_hwa. */

#include <math.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "driver_shape.h"
#include "feasibility.h"
#include "generators/pp_t7.h"
#include "generators/t7_common.h"
#include "output.h"
#include "pp_math.h"

/* Land và Lee 1994: tài xế nhìn tiếp điểm khoảng 1–2 s trước (PP-TS-024 2.2). */
#define QTP_PEAK_MIN_S (1.0)
#define QTP_PEAK_MAX_S (2.0)
/* Smoothstep bậc 7 trên u ∈ [0, 1]: max |s''| tại u ≈ 0,2764; max |s'''| tại u = 0,5. */
#define QTP_S2_MAX (7.513188403792246)
#define QTP_S3_MAX (52.5)
/* Bước và số bước tối đa khi tìm tiếp điểm từ đỉnh theo đường tham chiếu (tới 200 m sau đỉnh). */
#define QTP_TANGENT_AFTER_STEP_M (1.0)
#define QTP_TANGENT_AFTER_STEPS (200U)

enum {
    QTP_APPLIED = 0,
    QTP_FB_FOLLOW = 1,
    QTP_FB_START_FROM_CAR = 2,
    QTP_FB_RECENTERING = 3,
    QTP_FB_OFFSET = 4,
    QTP_FB_LANE = 5,
    QTP_FB_OBJECTS = 6,
    QTP_FB_SHORT_VIEW = 7,
    QTP_FB_NO_CURVE = 8,
    QTP_FB_SUPPORT = 9,
    QTP_FB_NO_TANGENT = 10,
    QTP_FB_AMPLITUDE = 11,
    QTP_FB_CHECK = 12,
    QTP_FB_NON_FINITE = 13,
    QTP_FB_DLC = 14,
    QTP_FB_PEAK_TANGENT = 15,
    QTP_FB_BASE_INSIDE = 16
};

void pp_t7_reset(pp_t7_ws_t *ws)
{
    if (ws != NULL) {
        ws->work = 0U;
        ws->fallback = 0U;
        ws->amp = 0.0;
        ws->dlc_ref = 0.0;
    }
}

double lab_qtp_tangent_time(const pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],
                            const pp_lateral_path_t *lateral, const pp_ref_samples_t *samples,
                            double side, double half_width, double lo, double hi, size_t last)
{
    /* f = khoảng cách có dấu từ base_link tới tiếp tuyến của vạch trong tại điểm k; tiếp điểm ở f = 0.
     * Điểm tâm R = pose − d·n, n = (−sin θ, cos θ); vạch = R + side·h·n song song với tâm, nên
     * f = side·(x sin θ − y cos θ + d) − h. Không cần atan2 hay đi lại đường tham chiếu. */
    const double dt = PP_GRID_STEP_S;
    size_t k = (size_t)floor(lo / dt);
    size_t k_end = (size_t)ceil(hi / dt);
    double found = 0.0;
    if (k < 1U) {
        k = 1U;
    }
    if (k_end > last) {
        k_end = last;
    }
    double f_prev = 0.0;
    for (size_t i = k - 1U; (i <= k_end) && (found == 0.0); i++) {
        const double th = samples->theta[i];
        const double f = (side * (((double)points[i].pose.x * sin(th)) - ((double)points[i].pose.y * cos(th))
                                  + lateral->d[i]))
                         - half_width;
        if ((i >= k) && (f_prev < 0.0) && (f >= 0.0)) {
            const double t = ((double)(i - 1U) * dt) + ((dt * -f_prev) / (f - f_prev));
            if ((t >= lo) && (t <= hi)) {
                found = t;
            }
        }
        f_prev = f;
    }
    return found;
}

bool lab_qtp_tangent_after(const pp_reference_line_t *ref, double px, double py, double side,
                           double half_width, double s_from)
{
    /* Điểm tâm R(s), n = (−sin θ, cos θ): f = side·((P − R)·n) − h, tiếp điểm ở f đổi dấu từ âm sang dương. */
    pp_ref_walker_t walker;
    pp_ref_point_t p;
    pp_ref_walk_begin(&walker, ref, &p);
    const double s_end = fmin(ref->view_end, s_from + (QTP_TANGENT_AFTER_STEPS * QTP_TANGENT_AFTER_STEP_M));
    double f_prev = 0.0;
    bool found = false;
    for (uint32_t i = 0U; (i <= QTP_TANGENT_AFTER_STEPS) && !found; i++) {
        const double s = s_from + ((double)i * QTP_TANGENT_AFTER_STEP_M);
        if ((s > s_end) || walker.on_arc) {
            break;
        }
        pp_ref_walk_to(&walker, s, &p);
        const double f = (side * ((-(px - p.x) * sin(p.theta)) + ((py - p.y) * cos(p.theta)))) - half_width;
        found = (i > 0U) && (f_prev < 0.0) && (f >= 0.0);
        f_prev = f;
    }
    return found;
}

/* Từ điểm của path tại đỉnh (nội suy giữa hai điểm lưới) còn thấy tiếp điểm hay không. */
static bool peak_sees_tangent(const pp_t7_input_t *in, const pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],
                              double side, double peak)
{
    const size_t k0 = (size_t)floor(peak / PP_GRID_STEP_S);
    const size_t k1 = (k0 + 1U < PP_TRAJECTORY_POINTS) ? (k0 + 1U) : k0;
    const double w = pp_clamp((peak / PP_GRID_STEP_S) - (double)k0, 0.0, 1.0);
    const double px = ((1.0 - w) * (double)points[k0].pose.x) + (w * (double)points[k1].pose.x);
    const double py = ((1.0 - w) * (double)points[k0].pose.y) + (w * (double)points[k1].pose.y);
    const double s = ((1.0 - w) * in->speed->s[k0]) + (w * in->speed->s[k1]);
    return lab_qtp_tangent_after(in->ref, px, py, side, 0.5 * in->ref->width, s);
}

/* DLC phía trong nhỏ nhất [m] của path trên các điểm 0..last: thân xe rộng w, bỏ qua góc hướng.
 * half_free = 0,5·(W − w). */
static double inner_dlc_min(const pp_lateral_path_t *lateral, double side, double half_free, size_t last)
{
    double m = INFINITY;
    for (size_t k = 0U; k <= last; k++) {
        m = fmin(m, half_free - (side * lateral->d[k]));
    }
    return m;
}

/* Vật thể chặn hiệu chỉnh khi chạm vạch phía trong cua hoặc nằm ở làn bên phía trong, trong phạm vi
 * path. Vật thể ở làn mình mà không chạm vạch trong, hoặc ở phía ngoài cua, không bị hiệu chỉnh tới gần. */
static bool objects_block(const pp_calibration_t *cal, const pp_t7_input_t *in, double side, double s_end)
{
    bool blocked = (in->objects == NULL);
    const double w = in->ref->width;
    for (size_t i = 0U; !blocked && (i < (size_t)in->objects->num_objects) && (i < PP_MAX_OBJECTS); i++) {
        const pp_object_t *o = &in->objects->objects[i];
        const double half_len = 0.5 * (double)o->length;
        const double half_w = 0.5 * (double)o->width;
        if ((double)o->existence_probability >= (double)cal->exist_min) {
            if (!(isfinite(o->x) && isfinite(o->y) && isfinite(half_len) && isfinite(half_w))) {
                blocked = true;
            } else if (((double)o->x - half_len) <= s_end) {
                pp_ref_point_t foot;
                double d = 0.0;
                pp_ref_project(in->ref, (double)o->x, (double)o->y, &foot, &d);
                const double inner = side * d;  /* Lệch về phía trong cua so với tâm làn. */
                blocked = !isfinite(inner)
                          || (((inner + half_w) > (0.5 * w)) && ((inner - half_w) < (1.5 * w)));
            } else {
            }
        }
    }
    return blocked;
}

/* Mã fallback, 0 nếu đã cộng hiệu chỉnh vào points. lateral, points, samples là path quintic_duration. */
static uint32_t correct(pp_t7_ws_t *ws, const pp_calibration_t *cal, const pp_t7_input_t *in,
                        const pp_lateral_path_t *lateral, pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],
                        const pp_ref_samples_t *samples)
{
    const pp_reference_line_t *ref = in->ref;
    const double dt = PP_GRID_STEP_S;
    if (in->follow) {
        return QTP_FB_FOLLOW;
    }
    if (in->start_from_car) {
        return QTP_FB_START_FROM_CAR;
    }
    if (in->recentering) {
        return QTP_FB_RECENTERING;
    }
    if (!isfinite(in->d_target) || !isfinite(ref->width) || !isfinite((double)in->vehicle->vehicle_width)) {
        return QTP_FB_NON_FINITE;
    }
    if (in->d_target != 0.0) {
        return QTP_FB_OFFSET;
    }
    if (!ref->valid || ref->coasting || ref->inferred || ref->lane_too_narrow || ref->line_rejected[0]
        || ref->line_rejected[1]) {
        return QTP_FB_LANE;
    }

    /* Cửa sổ tìm tiếp điểm: tâm ± nửa bề rộng, kẹp trong 1–2 s. */
    const double lo = fmax(QTP_PEAK_MIN_S, (double)cal->qtp_center_s - (double)cal->qtp_window_half_s);
    const double hi = fmin(QTP_PEAK_MAX_S, (double)cal->qtp_center_s + (double)cal->qtp_window_half_s);
    const size_t k_hi = (size_t)ceil(hi / dt);
    size_t last = 0U;
    while (((last + 1U) < PP_TRAJECTORY_POINTS) && samples->in_view[last + 1U]) {
        last++;
    }
    const double end = (double)last * dt;
    if (!samples->in_view[0] || (end <= lo) || (lo > hi)) {
        return QTP_FB_SHORT_VIEW;
    }

    /* a_y cần trong tầm nhìn (như pp_feasibility_check) và phía trong của cua gần nhất trong cửa sổ. */
    double need_max = 0.0;
    double near_max = 0.0;
    double near_side = 0.0;
    for (size_t k = 0U; k <= last; k++) {
        const double v = in->speed->v[k];
        const double need = v * v * samples->kappa[k];
        need_max = fmax(need_max, fabs(need));
        if ((k <= k_hi) && (fabs(need) > near_max)) {
            near_max = fabs(need);
            near_side = copysign(1.0, need);
        }
    }
    if (!isfinite(need_max)) {
        return QTP_FB_NON_FINITE;
    }
    if (need_max < (double)cal->qtp_ay_need_min) {
        return QTP_FB_NO_CURVE;
    }
    if (need_max >= (PP_AYSMAX - (double)cal->qtp_ay_need_margin)) {
        return QTP_FB_SUPPORT;
    }

    /* Biên độ đích: đỉnh của path cách d_target về phía trong, chặn theo hành lang như offset (PP-SWR-051).
     * Biên độ hiện tại (ws->amp, có dấu) tăng dần theo qtp_amplitude_rate, để path không đổi đột ngột
     * giữa các chu kỳ lúc bắt đầu. Đang hiệu chỉnh thì giữ phía cũ. */
    const double half_free = 0.5 * (ref->width - (double)in->vehicle->vehicle_width);
    const double corridor = half_free - (double)cal->dlc_offset_min;
    const double amplitude = fmin((double)cal->qtp_amplitude_m, corridor);
    const bool engaged = (ws->amp != 0.0);
    const double side = engaged ? copysign(1.0, ws->amp) : near_side;
    /* Bắt đầu và giữ khi có tiếp điểm trước cuối cửa sổ, cùng phía (đang hiệu chỉnh thì giữ phía cũ). Lane
     * model thường chỉ thấy cua khi tiếp điểm đã gần hơn cuối cửa sổ, nên không đòi tiếp điểm qua cả cửa sổ. */
    const double tangent = ((side != 0.0) && (!engaged || (side == near_side)))
                           ? lab_qtp_tangent_time(points, lateral, samples, side, 0.5 * ref->width, 0.0, hi, last)
                           : 0.0;
    const bool aim = (tangent > 0.0) && (amplitude >= (double)cal->qtp_amplitude_min_m);
    if (!aim) {
        return (tangent > 0.0) ? QTP_FB_AMPLITUDE : QTP_FB_NO_TANGENT;
    }
    /* Đỉnh ở tiếp điểm, không gần hơn đầu cửa sổ (vẫn đủ thời lượng cho jerk). */
    const double peak = fmax(tangent, lo);
    /* Lúc bắt đầu: từ đỉnh vẫn phải thấy tiếp điểm, nếu không thì cua quá ngắn, hiệu chỉnh sẽ bị thả
     * trước khi tới đỉnh. */
    if (!engaged && ((double)cal->qtp_peak_check >= 0.5)
        && !peak_sees_tangent(in, points, side, peak)) {
        return QTP_FB_PEAK_TANGENT;
    }
    /* DLC phía trong (an toàn, PP-SWR-070 xếp trên êm): đỉnh không vào trong hơn path quintic tại đỉnh lúc
     * bắt đầu quá qtp_dlc_margin_m, và không dưới dlc_offset_min. Lấy tại đỉnh, không lấy cả path: điểm đầu
     * là vị trí xe, đang cắt vào trong thì sẽ cho giữ xe ở đó thay vì về giữa. Đang hiệu chỉnh thì mốc chỉ
     * được tăng (ra ngoài): path quintic các chu kỳ sau nối từ path đã hiệu chỉnh, lấy thẳng làm mốc thì mốc
     * trôi vào trong; còn khi path quintic về giữa thì mốc theo, không giữ xe ở trong. */
    const size_t k0 = (size_t)floor(peak / dt);
    const double w1 = (peak / dt) - (double)k0;
    const double base_at_peak = ((1.0 - w1) * lateral->d[k0]) + (w1 * lateral->d[k0 + 1U]);
    const double dlc_now = half_free - (side * base_at_peak);
    const double dlc_ref = engaged ? fmax(ws->dlc_ref, dlc_now) : dlc_now;
    const double dlc_floor = fmax((double)cal->dlc_offset_min, dlc_ref - (double)cal->qtp_dlc_margin_m);
    const double amp_dlc = fmin(amplitude, half_free - dlc_floor);
    if (amp_dlc < (double)cal->qtp_amplitude_min_m) {
        return QTP_FB_DLC;
    }
    /* Thời gian giữa hai chu kỳ lấy từ path cũ; không có path cũ thì không tăng biên độ. */
    const double step = (double)cal->qtp_amplitude_rate
                        * ((in->old->valid && isfinite(in->old->shift_s)) ? pp_clamp(in->old->shift_s, 0.0, 0.1) : 0.0);
    const double amp_ramp = ws->amp + pp_clamp((side * amp_dlc) - ws->amp, -step, step);
    const double amp = side * fmin(side * amp_ramp, amp_dlc);  /* Mốc DLC tăng thì giảm ngay. */
    if (amp == 0.0) {
        return QTP_FB_AMPLITUDE;
    }

    /* Phần cộng thêm chặn theo jerk (PP-SWR-003) và a_y thêm vào trên nửa ngắn hơn: jerk ~ A/T³,
     * a_y ~ A/T² (PP-TS-024 2.1). */
    const double t_half = fmin(peak, end - peak);
    const double t2 = t_half * t_half;
    const double cap = fmin(((double)cal->jerk_target_hwa * t2 * t_half) / QTP_S3_MAX,
                            ((double)cal->ay_add_max_hwa * t2) / QTP_S2_MAX);
    if (objects_block(cal, in, side, in->speed->s[last])) {
        return QTP_FB_OBJECTS;
    }
    /* Chỉ đi vào trong. Path quintic tại đỉnh đã ở trong hơn biên độ thì giữ path quintic và giữ biên độ. */
    const double rel = side * pp_clamp(side * (amp + in->d_target - base_at_peak), 0.0, cap);
    if (rel == 0.0) {
        ws->amp = amp;
        ws->dlc_ref = dlc_ref;
        return QTP_FB_BASE_INSIDE;
    }

    /* Thử phần cộng thêm đủ rồi một nửa (pilot PP-TS-024); giữ trong aysmax và jerk_target_hwa. Khi path
     * quintic đã vượt một trong hai (cua gắt, tìm thời lượng tới T_max) thì không được vượt hơn path đó.
     * DLC phía trong không dưới mức sàn, hoặc không dưới DLC của path quintic nếu path đó đã thấp hơn. */
    const double dlc_ok = fmin(dlc_floor, inner_dlc_min(lateral, side, half_free, last)) - 1e-9;
    pp_path_check_t base_check;
    pp_feasibility_check(points, samples, &base_check);
    const double ay_ok = fmax(PP_AYSMAX, base_check.ay_max);
    const double jerk_ok = fmax((double)cal->jerk_target_hwa, base_check.jerk_max);
    uint32_t code = QTP_FB_CHECK;
    for (uint32_t i = 0U; (i < 2U) && (code != QTP_APPLIED); i++) {
        const double offset = rel * ((i == 0U) ? 1.0 : 0.5);
        pp_lateral_path_t bumped;
        pp_trajectory_point_t candidate[PP_TRAJECTORY_POINTS];
        if (lab_driver_bump(lateral, end, peak, offset, corridor, &bumped)) {
            ws->work++;
            if (pp_output_points(ref, &bumped, in->speed, (double)in->vehicle->wheelbase, candidate, NULL)) {
                pp_path_check_t check;
                pp_feasibility_check(candidate, samples, &check);
                if ((check.ay_max <= ay_ok) && (check.jerk_max <= jerk_ok)
                    && (inner_dlc_min(&bumped, side, half_free, last) >= dlc_ok)) {
                    (void)memcpy(points, candidate, sizeof(candidate));
                    ws->amp = amp;
                    ws->dlc_ref = dlc_ref;
                    code = QTP_APPLIED;
                }
            }
        }
    }
    return code;
}

bool pp_t7_generate(pp_t7_ws_t *ws, const pp_calibration_t *cal, const pp_t7_input_t *in,
                    pp_trajectory_point_t points[PP_TRAJECTORY_POINTS], pp_ref_samples_t *samples)
{
    pp_lateral_path_t lateral;
    ws->work = 0U;
    ws->fallback = 0U;
    const bool ok = pp_t7_quintic_search(cal, in, &lateral, points, samples, &ws->work);
    if (ok) {
        ws->fallback = (samples != NULL) ? correct(ws, cal, in, &lateral, points, samples) : QTP_FB_SHORT_VIEW;
    }
    if (!ok || ((ws->fallback != QTP_APPLIED) && (ws->fallback != QTP_FB_BASE_INSIDE))) {
        ws->amp = 0.0;
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

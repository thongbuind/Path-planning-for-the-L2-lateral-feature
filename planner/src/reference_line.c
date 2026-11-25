#include "reference_line.h"

#include <math.h>
#include <string.h>

#define PP_WALK_STEP_M (0.25)
#define PP_FOOT_ITERATIONS (3U)
#define PP_FOOT_MAX_M (5.0)
#define PP_STRAIGHT_KAPPA (1.0e-9)
#define PP_NODE_FOOT_ITERATIONS (4U)
#define PP_NODE_FOOT_MIN_SCALE (0.1)  /* Khi 1 - kappa d quá nhỏ, chỉ tiến theo tiếp tuyến. */

static bool line_trusted(const pp_boundary_t *b, double confidence)
{
    return b->present && (b->status == PP_LINE_STATUS_MEASURED)
        && (b->confidence >= confidence);
}

void pp_reference_memory_reset(pp_reference_memory_t *mem)
{
    (void)memset(mem, 0, sizeof(*mem));
}

static void update_width_memory(pp_reference_memory_t *mem, const pp_calibration_t *cal,
                                double measured, double dt)
{
    if ((measured >= PP_LANE_WIDTH_MIN_M) && (measured <= PP_LANE_WIDTH_MAX_M)) {
        if (!mem->width_valid) {
            mem->width = measured;
            mem->width_valid = true;
        } else {
            const double tau = (double)cal->tau_mem;
            const double alpha = dt / (tau + dt);
            mem->width += alpha * (measured - mem->width);
        }
    }
}

static void move_track(pp_line_track_t *t, const pp_motion_t *motion)
{
    if (t->valid) {
        pp_cubic_t moved;
        double start = 0.0;
        double end = 0.0;
        t->valid = (motion != NULL)
                   && pp_cubic_move(&t->poly, t->view_start, t->view_end, motion, &moved,
                                    &start, &end);
        if (t->valid) {
            t->poly = moved;
            t->view_start = start;
            t->view_end = end;
        }
    }
}

static void set_track(pp_line_track_t *t, const pp_boundary_t *b, double age_s)
{
    t->valid = true;
    t->poly = b->poly;
    (void)memcpy(t->variance, b->variance, sizeof(t->variance));
    t->view_start = b->view_start;
    t->view_end = b->view_end;
    t->age_s = age_s;
}

static bool consistent(const pp_boundary_t *b, const pp_line_track_t *t,
                       const pp_calibration_t *cal)
{
    const double jump = fabs(b->poly.c[0] - t->poly.c[0]);
    const double limit = (double)cal->k_jump;
    if (!t->valid || !(jump <= limit * sqrt(b->variance[0] + t->variance[0]))) {
        return false;
    }
    /* So hình dạng trong phần hai frame cùng quan sát; tránh dùng đúng điểm tận cùng của cubic
     * (PP-TS-001). */
    const double lo = fmax(0.0, fmax(b->view_start, t->view_start));
    const double hi = fmin(b->view_end, t->view_end);
    if (hi > lo) {
        const double fractions[] = {0.5, 0.75};
        for (size_t i = 0U; i < sizeof(fractions) / sizeof(fractions[0]); i++) {
            const double x = lo + fractions[i] * (hi - lo);
            double variance = 0.0;
            double power = 1.0;
            for (uint32_t k = 0U; k < PP_CUBIC_TERMS; k++) {
                variance += power * (b->variance[k] + t->variance[k]);
                power *= x * x;
            }
            const double delta = pp_cubic_value(&b->poly, x) - pp_cubic_value(&t->poly, x);
            if (!(fabs(delta) <= limit * sqrt(variance) + 1.0e-6)) {
                return false;
            }
        }
    }
    return true;
}

static bool check_line(pp_boundary_memory_t *m, const pp_boundary_t *b,
                       const pp_calibration_t *cal, double confidence, double dt, bool *rejected)
{
    const double confirm = (double)cal->T_confirm - 1.0e-9;
    bool trusted = false;
    *rejected = false;

    if (m->previous.valid) {
        /* Giữ vị trí cũ để so khi vùng quan sát đã bù ego-motion còn tới xe; dùng timeout cố định
         * có thể bỏ mất vạch đúng. */
        m->previous.age_s += dt;
        m->previous.valid = m->previous.view_end > 0.0;
    }
    if (!line_trusted(b, confidence)) {
        m->absent_s += dt;
        if (m->absent_s > confirm) {
            m->accepted.valid = false;
            m->candidate.valid = false;
        }
    } else {
        m->absent_s = 0.0;
        if (!m->accepted.valid || consistent(b, &m->accepted, cal)) {
            if (m->candidate.valid && !m->previous.valid) {
                /* Vùng nhìn chung co lại khi chờ xác nhận, làm phép so hình dạng yếu đi. Giữ vị
                 * trí trước đổi để R2 có thể nhận lại ngay (PP-PR-048). */
                m->previous = m->accepted;
                m->previous.age_s = 0.0;
            }
            set_track(&m->accepted, b, 0.0);
            m->candidate.valid = false;
            trusted = true;
        } else if (consistent(b, &m->previous, cal)) {
            set_track(&m->accepted, b, 0.0);
            m->previous.valid = false;
            m->candidate.valid = false;
            trusted = true;
        } else {
            /* R1 chỉ cộng thời gian khi các frame mới còn nhất quán với candidate. */
            const double age = consistent(b, &m->candidate, cal) ? (m->candidate.age_s + dt) : dt;
            set_track(&m->candidate, b, age);
            if (age >= confirm) {
                m->previous = m->accepted;
                m->previous.age_s = 0.0;
                set_track(&m->accepted, b, 0.0);
                m->candidate.valid = false;
                trusted = true;
            } else {
                *rejected = true;
            }
        }
    }
    return trusted;
}

static void move_memory(pp_boundary_memory_t *m, const pp_motion_t *motion)
{
    move_track(&m->accepted, motion);
    move_track(&m->candidate, motion);
    move_track(&m->previous, motion);
}

static const uint32_t OUTER_INDICES[PP_OUTER_BOUNDARIES] = {
    PP_LINE_L2, PP_LINE_R2, PP_EDGE_LEFT, PP_EDGE_RIGHT,
};

static void update_outer(pp_reference_memory_t *mem, const pp_lane_at_t0_t *lane,
                         const pp_motion_t *motion, const pp_calibration_t *cal, double dt,
                         const pp_reference_line_t *measured, bool trusted[PP_OUTER_BOUNDARIES])
{
    if (lane->lane_change != PP_SIDE_NONE || motion == NULL) {
        (void)memset(mem->outer, 0, sizeof(mem->outer));
    }
    const double alpha = dt / ((double)cal->tau_mem + dt);
    for (uint32_t i = 0U; i < PP_OUTER_BOUNDARIES; i++) {
        pp_outer_boundary_memory_t *m = &mem->outer[i];
        const pp_boundary_t *b = &lane->boundary[OUTER_INDICES[i]];
        move_memory(&m->track, motion);
        bool rejected;
        trusted[i] = check_line(&m->track, b, cal, (double)cal->conf_inferred, dt, &rejected);
        m->offset_variance += (double)cal->q_mem * dt;
        if (trusted[i] && (measured != NULL)) {
            const double offset = b->poly.c[0] - measured->centre.c[0];
            m->offset = m->offset_valid ? m->offset + alpha * (offset - m->offset) : offset;
            m->offset_valid = true;
            m->offset_variance = (double)cal->sigma_mem0 * (double)cal->sigma_mem0;
        }
    }
}

static void infer_centre(const pp_reference_memory_t *mem, const pp_lane_at_t0_t *lane,
                         const bool trusted[PP_OUTER_BOUNDARIES], pp_reference_line_t *out)
{
    pp_cubic_t centre = {{0.0}};
    double lo = -INFINITY;
    double hi = INFINITY;
    double total = 0.0;
    double var_c2 = 0.0;
    double var_c3 = 0.0;
    for (uint32_t i = 0U; i < PP_OUTER_BOUNDARIES; i++) {
        const pp_outer_boundary_memory_t *m = &mem->outer[i];
        const pp_boundary_t *b = &lane->boundary[OUTER_INDICES[i]];
        if (!trusted[i] || !m->offset_valid) {
            continue;
        }
        const double weight = 1.0 / (b->variance[0] + m->offset_variance);
        centre.c[0] += weight * (b->poly.c[0] - m->offset);
        for (uint32_t k = 1U; k < PP_CUBIC_TERMS; k++) {
            centre.c[k] += weight * b->poly.c[k];
        }
        total += weight;
        lo = fmax(lo, b->view_start);
        hi = fmin(hi, b->view_end);
        var_c2 += weight * weight * b->variance[2];
        var_c3 += weight * weight * b->variance[3];
    }
    if (total > 0.0 && hi > lo) {
        for (uint32_t k = 0U; k < PP_CUBIC_TERMS; k++) {
            out->centre.c[k] = centre.c[k] / total;
        }
        out->width = mem->width;
        out->view_start = lo;
        out->view_end = hi;
        out->var_c2 = var_c2 / (total * total);
        out->var_c3 = var_c3 / (total * total);
        out->inferred = true;
        out->valid = true;
    }
}

static void coast(pp_reference_memory_t *mem, const pp_motion_t *motion,
                  const pp_calibration_t *cal, double dt, pp_reference_line_t *out)
{
    bool ok = mem->ref_valid && (motion != NULL)
              && ((mem->coast_s + dt) <= ((double)cal->T_coast + 1.0e-9));
    if (ok) {
        pp_cubic_t moved;
        double start = 0.0;
        double end = 0.0;
        ok = pp_cubic_move(&mem->ref_centre, mem->ref_view_start, mem->ref_view_end, motion,
                           &moved, &start, &end);
        if (ok) {
            mem->ref_centre = moved;
            mem->ref_view_start = start;
            mem->ref_view_end = end;
            mem->coast_s += dt;
            out->centre = moved;
            out->width = mem->ref_width;
            out->view_start = start;
            out->view_end = end;
            out->coasting = true;
            out->inferred = mem->ref_inferred;
            out->valid = true;
        }
    }
    if (!ok) {
        mem->ref_valid = false;
    }
}

/* Nếu cặp ego nằm cùng phía, chỉ phục hồi cặp nằm hai bên xe khi cả hai vạch khớp với hình học đo
 * trước đó sau ego-motion. */
static void recover_ego_pair(pp_lane_at_t0_t *lane, const pp_reference_memory_t *mem,
                             const pp_calibration_t *cal)
{
    const pp_boundary_t *left = &lane->boundary[PP_LINE_L1];
    const pp_boundary_t *right = &lane->boundary[PP_LINE_R1];
    const double confidence = (double)cal->conf_ego;
    if ((lane->lane_change != PP_SIDE_NONE) || !line_trusted(left, confidence)
        || !line_trusted(right, confidence) || (left->poly.c[0] <= right->poly.c[0])) {
        return;
    }
    const bool shifted_left = right->poly.c[0] > 0.0;
    if (!shifted_left && (left->poly.c[0] >= 0.0)) {
        return;
    }
    const size_t first = shifted_left ? PP_LINE_R1 : PP_LINE_L2;
    const pp_boundary_t *pair = &lane->boundary[first];
    if ((pair[0].poly.c[0] <= 0.0) || (pair[1].poly.c[0] >= 0.0)) {
        return;
    }
    for (size_t i = 0U; i < 2U; i++) {
        const pp_line_track_t *track = &mem->line[i].accepted;
        const double start = fmax(0.0, fmax(track->view_start, pair[i].view_start));
        const double end = fmin(track->view_end, pair[i].view_end);
        if (!line_trusted(&pair[i], confidence) || (end <= start) || !consistent(&pair[i], track, cal)) {
            return;
        }
    }
    const size_t src = shifted_left ? PP_LINE_L1 : PP_LINE_L2;
    const size_t dst = shifted_left ? PP_LINE_L2 : PP_LINE_L1;
    const size_t missing = shifted_left ? PP_LINE_R2 : PP_LINE_L2;
    (void)memmove(&lane->boundary[dst], &lane->boundary[src], (PP_LANE_LINES - 1U) * sizeof(*pair));
    (void)memset(&lane->boundary[missing], 0, sizeof(*pair));
    lane->boundary[missing].status = PP_LINE_STATUS_LOST;
}

void pp_reference_line_update(pp_reference_memory_t *mem, pp_lane_at_t0_t *lane,
                              const pp_motion_t *cycle_motion, const pp_calibration_t *cal,
                              double vehicle_width, double dt, pp_reference_line_t *out)
{
    const pp_boundary_t *left = &lane->boundary[PP_LINE_L1];
    const pp_boundary_t *right = &lane->boundary[PP_LINE_R1];

    (void)memset(out, 0, sizeof(*out));
    move_memory(&mem->line[0], cycle_motion);
    move_memory(&mem->line[1], cycle_motion);
    recover_ego_pair(lane, mem, cal);
    /* Qua vạch làm đổi slot, ví dụ R1 thành L1. Ghép vạch trước khi chuyển lịch sử để dùng lại
     * cùng frame camera được. */
    if ((lane->lane_change == PP_SIDE_LEFT) || (lane->lane_change == PP_SIDE_RIGHT)) {
        const bool rightward = lane->lane_change == PP_SIDE_RIGHT;
        const size_t crossed = rightward ? 1U : 0U;
        const size_t shared = 1U - crossed;
        const pp_boundary_t *marking = rightward ? left : right;
        if (line_trusted(marking, (double)cal->conf_ego)
            && consistent(marking, &mem->line[crossed].accepted, cal)
            && !consistent(marking, &mem->line[shared].accepted, cal)) {
            mem->line[shared] = mem->line[crossed];
            mem->line[crossed] = mem->outer[crossed].track;
            move_memory(&mem->line[crossed], cycle_motion);
        }
    }
    const bool left_ok = check_line(&mem->line[0], left, cal, (double)cal->conf_ego, dt,
                                    &out->line_rejected[0]);
    const bool right_ok = check_line(&mem->line[1], right, cal, (double)cal->conf_ego, dt,
                                     &out->line_rejected[1]);
    const pp_reference_line_t *measured_ref = NULL;

    /* Khi bề rộng cặp vạch nằm ngoài ODD, giữ vạch cho tâm làn khớp bộ nhớ. Không cập nhật bề rộng
     * (PP-PR-057). */
    bool use_left = left_ok;
    bool use_right = right_ok;
    if (left_ok && right_ok && mem->width_valid && mem->ref_valid) {
        const double heading = atan(0.5 * (left->poly.c[1] + right->poly.c[1]));
        const double between = (left->poly.c[0] - right->poly.c[0]) * cos(heading);
        if ((between < PP_LANE_WIDTH_MIN_M) || (between > PP_LANE_WIDTH_MAX_M)) {
            const double half = 0.5 * mem->width;
            const double from_left = fabs((left->poly.c[0] - half) - mem->ref_centre.c[0]);
            const double from_right = fabs((right->poly.c[0] + half) - mem->ref_centre.c[0]);
            use_left = from_left <= from_right;
            use_right = !use_left;
        }
    }

    if (use_left && use_right) {
        for (uint32_t k = 0U; k < PP_CUBIC_TERMS; k++) {
            out->centre.c[k] = 0.5 * (left->poly.c[k] + right->poly.c[k]);
        }
        const double heading = atan(out->centre.c[1]);
        const double measured = (left->poly.c[0] - right->poly.c[0]) * cos(heading);
        update_width_memory(mem, cal, measured, dt);
        out->width = measured;
        out->view_start = fmax(left->view_start, right->view_start);
        out->view_end = fmin(left->view_end, right->view_end);
        out->var_c2 = 0.25 * (left->variance[2] + right->variance[2]);
        out->var_c3 = 0.25 * (left->variance[3] + right->variance[3]);
        out->valid = true;
        if (measured >= PP_LANE_WIDTH_MIN_M && measured <= PP_LANE_WIDTH_MAX_M) {
            measured_ref = out;
        }
    } else if ((use_left || use_right) && mem->width_valid) {
        const pp_boundary_t *line = use_left ? left : right;
        const double half = 0.5 * mem->width;
        out->centre = line->poly;
        out->centre.c[0] += use_left ? -half : half;
        out->width = mem->width;
        out->view_start = line->view_start;
        out->view_end = line->view_end;
        out->var_c2 = line->variance[2];
        out->var_c3 = line->variance[3];
        out->valid = true;
    }

    bool outer_trusted[PP_OUTER_BOUNDARIES];
    update_outer(mem, lane, cycle_motion, cal, dt, measured_ref, outer_trusted);
    /* Vạch bị loại vì không nhất quán có thể là nhiễu thoáng qua. COAST trên đường trực tiếp trước
     * khi infer (PP-PR-052). */
    const bool suspected = out->line_rejected[0] || out->line_rejected[1];
    const bool may_infer = !left_ok && !right_ok && mem->width_valid;
    if (may_infer && !suspected) {
        infer_centre(mem, lane, outer_trusted, out);
    }
    if (!out->valid) {
        coast(mem, cycle_motion, cal, dt, out);
    }
    if (!out->valid && may_infer && suspected) {
        infer_centre(mem, lane, outer_trusted, out);
    }

    if (out->valid && !out->coasting) {
        mem->ref_valid = true;
        mem->ref_inferred = out->inferred;
        mem->ref_centre = out->centre;
        mem->ref_width = out->width;
        mem->ref_view_start = out->view_start;
        mem->ref_view_end = out->view_end;
        mem->coast_s = 0.0;
    }
    if (out->valid) {
        const double free_space = 0.5 * (out->width - vehicle_width);
        out->lane_too_narrow = free_space < (double)cal->free_space_min;
#ifdef PP_REF_SAMPLED
        pp_ref_sample_cubic(out);
#endif
    }
}

static void point_on_cubic(const pp_cubic_t *p, double x, pp_ref_point_t *out)
{
    const double d1 = pp_cubic_slope(p, x);
    const double d2 = pp_cubic_bend(p, x);
    const double d3 = pp_cubic_third(p);
    const double g = 1.0 + (d1 * d1);
    out->x = x;
    out->y = pp_cubic_value(p, x);
    out->theta = atan(d1);
    out->kappa = d2 / (g * sqrt(g));
    out->dkappa = ((d3 * g) - (3.0 * d1 * d2 * d2)) / (g * g * g);
}

/* Chân đường vuông góc thỏa (x - px) + (y(x) - py)y'(x) = 0. */
static double foot_x(const pp_cubic_t *p, double px, double py)
{
    double x = px;
    for (uint32_t i = 0U; i < PP_FOOT_ITERATIONS; i++) {
        const double ey = pp_cubic_value(p, x) - py;
        const double d1 = pp_cubic_slope(p, x);
        const double f = (x - px) + (ey * d1);
        const double df = 1.0 + (d1 * d1) + (ey * pp_cubic_bend(p, x));
        if (df > 0.0) {
            x = pp_clamp(x - (f / df), px - PP_FOOT_MAX_M, px + PP_FOOT_MAX_M);
        }
    }
    return x;
}

static void point_on_arc(const pp_ref_point_t *a, double length, pp_ref_point_t *out);


static void set_node(pp_ref_nodes_t *nd, uint32_t i, double s, const pp_cubic_t *p, double x)
{
    pp_ref_point_t point;
    point_on_cubic(p, x, &point);
    nd->s[i] = s;
    nd->x[i] = point.x;
    nd->y[i] = point.y;
    nd->theta[i] = point.theta;
    nd->kappa[i] = point.kappa;
    nd->dkappa[i] = point.dkappa;
}

/* Lấy độ dốc ở giữa phần thực đi trong bước, kể cả khi đoạn cuối ngắn hơn bước. */
static double partial_step(const pp_cubic_t *p, double x, double length, double stretch)
{
    double part = length / stretch;
    for (uint32_t i = 0U; i < 2U; i++) {
        const double slope = pp_cubic_slope(p, x + (0.5 * part));
        part = length / sqrt(1.0 + (slope * slope));
    }
    return x + part;
}

void pp_ref_sample_cubic(pp_reference_line_t *ref)
{
    const pp_cubic_t *p = &ref->centre;
    pp_ref_nodes_t *nd = &ref->nodes;
    const uint32_t back = (uint32_t)lround(PP_REF_BACK_M / PP_REF_STEP_M);
    const double x0 = foot_x(p, 0.0, 0.0);
    const double x_end = fmax(ref->view_end, x0);

    nd->origin = back;
    set_node(nd, back, 0.0, p, x0);

    {
        double x = x0;
        double s = 0.0;
        uint32_t k = 1U;
        while (k <= back) {
            const double x_next = x - PP_WALK_STEP_M;
            const double slope = pp_cubic_slope(p, 0.5 * (x + x_next));
            const double stretch = sqrt(1.0 + (slope * slope));
            const double ds = PP_WALK_STEP_M * stretch;
            while ((k <= back) && ((s + ds) >= ((double)k * PP_REF_STEP_M))) {
                const double target = (double)k * PP_REF_STEP_M;
                set_node(nd, back - k, -target, p, partial_step(p, x, -(target - s), stretch));
                k++;
            }
            x = x_next;
            s += ds;
        }
    }

    {
        double x = x0;
        double s = 0.0;
        uint32_t i = back + 1U;
        uint32_t k = 1U;
        while ((x < x_end) && (i < (PP_REF_NODES - 1U))) {
            const double x_next = fmin(x + PP_WALK_STEP_M, x_end);
            const double slope = pp_cubic_slope(p, 0.5 * (x + x_next));
            const double stretch = sqrt(1.0 + (slope * slope));
            const double ds = (x_next - x) * stretch;
            while ((i < (PP_REF_NODES - 1U)) && ((s + ds) >= ((double)k * PP_REF_STEP_M))) {
                const double target = (double)k * PP_REF_STEP_M;
                set_node(nd, i, target, p, partial_step(p, x, target - s, stretch));
                i++;
                k++;
            }
            x = x_next;
            s += ds;
        }
        if ((x >= x_end) && (s > (nd->s[i - 1U] + 1.0e-9))) {
            set_node(nd, i, s, p, x_end);
            i++;
        }
        nd->n = i;
    }
    ref->sampled = true;
}

static void node_point(const pp_ref_nodes_t *nd, uint32_t i, pp_ref_point_t *out)
{
    out->x = nd->x[i];
    out->y = nd->y[i];
    out->theta = nd->theta[i];
    out->kappa = nd->kappa[i];
    out->dkappa = nd->dkappa[i];
}

/* Nội suy Hermite trong miền node; ngoài miền giữ tiếp tuyến và độ cong cuối để nối cung. */
static void nodes_point_at(const pp_ref_nodes_t *nd, double s, pp_ref_point_t *out)
{
    if (nd->n == 0U) {
        (void)memset(out, 0, sizeof(*out));
        out->x = s;
    } else if ((nd->n == 1U) || (s >= nd->s[nd->n - 1U])) {
        pp_ref_point_t last;
        node_point(nd, nd->n - 1U, &last);
        point_on_arc(&last, s - nd->s[nd->n - 1U], out);
    } else if (s <= nd->s[0]) {
        pp_ref_point_t first;
        node_point(nd, 0U, &first);
        point_on_arc(&first, s - nd->s[0], out);
    } else {
        uint32_t i = (uint32_t)floor((s - nd->s[0]) / PP_REF_STEP_M);
        if (i > (nd->n - 2U)) {
            i = nd->n - 2U;
        }
        while ((i > 0U) && (s < nd->s[i])) {
            i--;
        }
        const uint32_t j = i + 1U;
        const double h = nd->s[j] - nd->s[i];
        const double t = s - nd->s[i];
        const double u = t / h;
        const double u2 = u * u;
        const double u3 = u2 * u;
        const double h00 = (2.0 * u3) - (3.0 * u2) + 1.0;
        const double h10 = u3 - (2.0 * u2) + u;
        const double h01 = (3.0 * u2) - (2.0 * u3);
        const double h11 = u3 - u2;
        const double u4 = u3 * u;
        const double ki = nd->kappa[i];
        const double kj = nd->kappa[j];
        const double gi = h * nd->dkappa[i];
        const double gj = h * nd->dkappa[j];
        const double turn = h * ((ki * ((0.5 * u4) - u3 + u))
                                 + (gi * ((0.25 * u4) - ((2.0 / 3.0) * u3) + (0.5 * u2)))
                                 + (kj * (u3 - (0.5 * u4)))
                                 + (gj * ((0.25 * u4) - (u3 / 3.0))));
        const double closure = nd->theta[j] - nd->theta[i]
                               - (h * ((0.5 * (ki + kj)) + ((gi - gj) / 12.0)));
        out->x = (h00 * nd->x[i]) + (h10 * h * cos(nd->theta[i]))
                 + (h01 * nd->x[j]) + (h11 * h * cos(nd->theta[j]));
        out->y = (h00 * nd->y[i]) + (h10 * h * sin(nd->theta[i]))
                 + (h01 * nd->y[j]) + (h11 * h * sin(nd->theta[j]));
        out->theta = nd->theta[i] + turn + (u * closure);
        out->kappa = (h00 * ki) + (h10 * gi) + (h01 * kj) + (h11 * gj);
        out->dkappa = nd->dkappa[i] + (u * (nd->dkappa[j] - nd->dkappa[i]));
    }
}

static double nodes_s_at_x(const pp_ref_nodes_t *nd, double px)
{
    double s = px;
    if (nd->n > 0U) {
        const uint32_t last = nd->n - 1U;
        if (px <= nd->x[0]) {
            s = nd->s[0] + (px - nd->x[0]);
        } else if (px >= nd->x[last]) {
            s = nd->s[last] + (px - nd->x[last]);
        } else {
            uint32_t lo = 0U;
            uint32_t hi = last;
            while ((hi - lo) > 1U) {
                const uint32_t mid = lo + ((hi - lo) / 2U);
                if (nd->x[mid] <= px) {
                    lo = mid;
                } else {
                    hi = mid;
                }
            }
            const double dx = nd->x[hi] - nd->x[lo];
            const double f = (dx > 0.0) ? ((px - nd->x[lo]) / dx) : 0.0;
            s = nd->s[lo] + (f * (nd->s[hi] - nd->s[lo]));
        }
    }
    return s;
}

static void nodes_project(const pp_ref_nodes_t *nd, double px, double py,
                          pp_ref_point_t *foot, double *d)
{
    const double s_start = nodes_s_at_x(nd, px);
    double s = s_start;
    for (uint32_t i = 0U; i < PP_NODE_FOOT_ITERATIONS; i++) {
        nodes_point_at(nd, s, foot);
        const double c = cos(foot->theta);
        const double sn = sin(foot->theta);
        const double along = ((px - foot->x) * c) + ((py - foot->y) * sn);
        const double across = (-(px - foot->x) * sn) + ((py - foot->y) * c);
        const double scale = 1.0 - (foot->kappa * across);
        const double step = (scale > PP_NODE_FOOT_MIN_SCALE) ? (along / scale) : along;
        s = pp_clamp(s + step, s_start - PP_FOOT_MAX_M, s_start + PP_FOOT_MAX_M);
    }
    nodes_point_at(nd, s, foot);
    *d = (-(px - foot->x) * sin(foot->theta)) + ((py - foot->y) * cos(foot->theta));
}

void pp_ref_project(const pp_reference_line_t *ref, double px, double py,
                    pp_ref_point_t *foot, double *d)
{
    if (ref->sampled) {
        nodes_project(&ref->nodes, px, py, foot, d);
    } else {
        point_on_cubic(&ref->centre, foot_x(&ref->centre, px, py), foot);
        *d = (-(px - foot->x) * sin(foot->theta)) + ((py - foot->y) * cos(foot->theta));
    }
}

void pp_ref_walk_begin(pp_ref_walker_t *walker, const pp_reference_line_t *ref,
                       pp_ref_point_t *start)
{
    const pp_cubic_t *p = &ref->centre;

    (void)memset(walker, 0, sizeof(*walker));
    walker->ref = ref;
    if (ref->sampled) {
        nodes_point_at(&ref->nodes, 0.0, start);
        return;
    }
    const double x = foot_x(p, 0.0, 0.0);
    walker->x = x;
    walker->x_end = fmax(ref->view_end, x);
    point_on_cubic(p, x, start);
    if (walker->x >= walker->x_end) {
        walker->on_arc = true;
        walker->arc_start = *start;
    }
}

static void point_on_arc(const pp_ref_point_t *a, double length, pp_ref_point_t *out)
{
    const double k = a->kappa;
    const double theta = a->theta + (k * length);
    if (fabs(k) > PP_STRAIGHT_KAPPA) {
        out->x = a->x + ((sin(theta) - sin(a->theta)) / k);
        out->y = a->y - ((cos(theta) - cos(a->theta)) / k);
    } else {
        out->x = a->x + (length * cos(a->theta));
        out->y = a->y + (length * sin(a->theta));
    }
    out->theta = theta;
    out->kappa = k;
    out->dkappa = 0.0;
}

void pp_ref_walk_to(pp_ref_walker_t *walker, double s, pp_ref_point_t *point)
{
    const pp_cubic_t *p = &walker->ref->centre;

    if (walker->ref->sampled) {
        nodes_point_at(&walker->ref->nodes, s, point);
        return;
    }

    while ((!walker->on_arc) && (walker->s < s)) {
        const double x_next = fmin(walker->x + PP_WALK_STEP_M, walker->x_end);
        const double slope = pp_cubic_slope(p, 0.5 * (walker->x + x_next));
        const double stretch = sqrt(1.0 + (slope * slope));
        const double ds = (x_next - walker->x) * stretch;
        if ((walker->s + ds) >= s) {
            walker->x += (s - walker->s) / stretch;
            walker->s = s;
        } else {
            walker->x = x_next;
            walker->s += ds;
            if (walker->x >= walker->x_end) {
                walker->on_arc = true;
                point_on_cubic(p, walker->x_end, &walker->arc_start);
                walker->s_arc_start = walker->s;
            }
        }
    }

    if (walker->on_arc) {
        const double length = fmax(s, walker->s_arc_start) - walker->s_arc_start;
        point_on_arc(&walker->arc_start, length, point);
        walker->s = fmax(s, walker->s);
    } else {
        point_on_cubic(p, walker->x, point);
    }
}

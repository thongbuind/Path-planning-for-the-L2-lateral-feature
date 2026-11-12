/* T2 Reference line (reference_line.h). PP-SWR-050, 063. */

#include "reference_line.h"

#include <math.h>
#include <string.h>

#define PP_WALK_STEP_M (0.25)         /* Arc-length integration step */
#define PP_FOOT_ITERATIONS (3U)       /* Newton steps for the perpendicular foot */
#define PP_FOOT_MAX_M (5.0)           /* Foot stays near the origin */
#define PP_STRAIGHT_KAPPA (1.0e-9)    /* Below this the arc continuation is a line */

/* Software Requirements Specification 4, "Biên làn đủ tin", for L1 and R1. */
static bool ego_line_trusted(const pp_boundary_t *b, const pp_calibration_t *cal)
{
    return b->present && (b->status == PP_LINE_STATUS_MEASURED)
        && (b->confidence >= (double)cal->conf_ego);
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

/* Moves a remembered position to the new base_link; drops it when the motion is unknown. */
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
    t->var_c0 = b->variance[0];
    t->view_start = b->view_start;
    t->view_end = b->view_end;
    t->age_s = age_s;
}

/* Frame-to-frame test at x = 0 (Software Detailed Design 5, "Từng frame"). */
static bool consistent(const pp_boundary_t *b, const pp_line_track_t *t,
                       const pp_calibration_t *cal)
{
    const double jump = fabs(b->poly.c[0] - t->poly.c[0]);
    return t->valid && (jump <= ((double)cal->k_jump * sqrt(b->variance[0] + t->var_c0)));
}

/* Step 1: SRS 4 condition and the consistency check against the memory, with R1 and R2. */
static bool check_line(pp_boundary_memory_t *m, const pp_boundary_t *b,
                       const pp_calibration_t *cal, double dt, bool *rejected)
{
    const double confirm = (double)cal->T_confirm - 1.0e-9;
    bool trusted = false;
    *rejected = false;

    if (m->previous.valid) {
        m->previous.age_s += dt;
        m->previous.valid = m->previous.age_s <= confirm;
    }
    if (!ego_line_trusted(b, cal)) {
        m->absent_s += dt;
        if (m->absent_s > confirm) {
            m->accepted.valid = false;     /* too old to compare with */
            m->candidate.valid = false;
        }
    } else {
        m->absent_s = 0.0;
        if (!m->accepted.valid || consistent(b, &m->accepted, cal)) {
            set_track(&m->accepted, b, 0.0);
            m->candidate.valid = false;
            trusted = true;
        } else if (consistent(b, &m->previous, cal)) {
            /* R2: back at the position before the last change. */
            set_track(&m->accepted, b, 0.0);
            m->previous.valid = false;
            m->candidate.valid = false;
            trusted = true;
        } else {
            /* R1: time counts only while the new position stays consistent with itself. */
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

/* Step 5: last reference line moved by ego-motion, for up to T_coast. */
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
            out->valid = true;
        }
    }
    if (!ok) {
        mem->ref_valid = false;            /* then path_valid = false (PP-SWR-124) */
    }
}

void pp_reference_line_update(pp_reference_memory_t *mem, const pp_lane_at_t0_t *lane,
                              const pp_motion_t *cycle_motion, const pp_calibration_t *cal,
                              double vehicle_width, double dt, pp_reference_line_t *out)
{
    const pp_boundary_t *left = &lane->boundary[PP_LINE_L1];
    const pp_boundary_t *right = &lane->boundary[PP_LINE_R1];

    (void)memset(out, 0, sizeof(*out));
    move_memory(&mem->line[0], cycle_motion);
    move_memory(&mem->line[1], cycle_motion);
    const bool left_ok = check_line(&mem->line[0], left, cal, dt, &out->line_rejected[0]);
    const bool right_ok = check_line(&mem->line[1], right, cal, dt, &out->line_rejected[1]);

    if (left_ok && right_ok) {
        /* Step 2: centre between L1 and R1; width measured across the lane at x = 0. */
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
    } else if ((left_ok || right_ok) && mem->width_valid) {
        /* Step 3: one ego-lane line, centre half the remembered width inside it. */
        const pp_boundary_t *line = left_ok ? left : right;
        const double half = 0.5 * mem->width;
        out->centre = line->poly;
        out->centre.c[0] += left_ok ? -half : half;
        out->width = mem->width;
        out->view_start = line->view_start;
        out->view_end = line->view_end;
        out->var_c2 = line->variance[2];
        out->var_c3 = line->variance[3];
        out->valid = true;
    } else {
        /* Step 4 not implemented yet; step 5: coast. */
        coast(mem, cycle_motion, cal, dt, out);
    }

    if (out->valid && !out->coasting) {
        mem->ref_valid = true;
        mem->ref_centre = out->centre;
        mem->ref_width = out->width;
        mem->ref_view_start = out->view_start;
        mem->ref_view_end = out->view_end;
        mem->coast_s = 0.0;
    }
    if (out->valid) {
        /* Step 6: free space each side (PP-SWR-063). */
        const double free_space = 0.5 * (out->width - vehicle_width);
        out->lane_too_narrow = free_space < (double)cal->free_space_min;
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

/* x of the foot of the perpendicular from (px, py): (x - px) + (y(x) - py) y'(x) = 0. */
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

void pp_ref_project(const pp_reference_line_t *ref, double px, double py,
                    pp_ref_point_t *foot, double *d)
{
    point_on_cubic(&ref->centre, foot_x(&ref->centre, px, py), foot);
    *d = (-(px - foot->x) * sin(foot->theta)) + ((py - foot->y) * cos(foot->theta));
}

void pp_ref_walk_begin(pp_ref_walker_t *walker, const pp_reference_line_t *ref,
                       pp_ref_point_t *start)
{
    const pp_cubic_t *p = &ref->centre;
    const double x = foot_x(p, 0.0, 0.0);

    (void)memset(walker, 0, sizeof(*walker));
    walker->ref = ref;
    walker->x = x;
    walker->x_end = fmax(ref->view_end, x);
    point_on_cubic(p, x, start);
    if (walker->x >= walker->x_end) {
        walker->on_arc = true;
        walker->arc_start = *start;
        if (ref->far_kappa_set) {
            walker->arc_start.kappa = ref->far_kappa;
            walker->arc_start.dkappa = 0.0;
        }
    }
}

double pp_ref_end_kappa(const pp_reference_line_t *ref)
{
    pp_ref_point_t end;
    point_on_cubic(&ref->centre, fmax(ref->view_end, foot_x(&ref->centre, 0.0, 0.0)), &end);
    return end.kappa;
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
                if (walker->ref->far_kappa_set) {
                    walker->arc_start.kappa = walker->ref->far_kappa;
                }
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

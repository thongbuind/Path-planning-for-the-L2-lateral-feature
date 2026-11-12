/*
 * Bait planners PM-01 to PM-09 of the evaluator self-check (Software Qualification Test
 * Specification 12). Written on the test side against interfaces/c/pp_planner.h only; it
 * shares nothing with planner/.
 *
 * Without a PM_xx define this is PM-00, the control: a simple HWA planner that meets the
 * call contract. It follows the lane centre (mean of L1 and R1), low-pass filtered across
 * camera frames and moved to t0 with EgoMotionQuery, and cuts curvature so that the path
 * a_y stays below aysmax. On an LKA or ELK REQUEST it drives the same centre path as that
 * function, phase ACTIVE until the car is back near the centre, then COMPLETED while the
 * request stays. Each PM_xx define adds one fault:
 *
 *   PM_01  0.1 m lateral step added to the path every 40 cycles
 *   PM_02  no a_y limit
 *   PM_03  path_valid stays true when ego-motion is invalid
 *   PM_04  path_valid = false whenever HWA is in REQUEST
 *   PM_05  PathStatus counter does not increase
 *   PM_06  Trajectory sent although pp_init reported a bad VehicleConfig
 *   PM_07  state kept in a global variable
 *   PM_08  writes past the end of the state memory
 *   PM_09  reads the system clock
 *   PM_10  LKA and ELK path 1.5 m towards the line the car drifts to
 */
#include <math.h>
#include <stdint.h>
#include <string.h>
#ifdef PM_09
#include <time.h>
#endif

#include "pp_planner.h"

#ifndef PM_NAME
#define PM_NAME "pm_00"
#endif

#define AY_TARGET (2.3F)        /* below aysmax = 2.5 m/s^2 of PP-SWR-001 */
#define FILTER_ALPHA (0.15F)    /* per camera frame */
#define V_MAX_MPS (70.0F)
#define SUBSTEPS (10U)
#define DONE_OFFSET_M (0.3F)   /* intervention done: centre within 0.3 m ... */
#define DONE_SLOPE (0.02F)     /* ... and heading to it within 0.02 rad */
#define WRONG_SIDE_M (1.5F)    /* PM_10 */

typedef struct {
    float c[4];          /* filtered lane centre, base_link at capture time */
    uint64_t capture_us; /* capture stamp of the filtered centre */
    uint8_t have_centre;
    uint8_t ok;
    uint8_t counter[3];  /* Trajectory, PathStatus, LateralLimits */
    uint32_t cycles;
    float wheelbase;
    float max_wheel_angle;
    uint8_t done[2];     /* LKA, ELK intervention reached the end condition for this request */
#ifdef PM_09
    double compute_s;
#endif
} pm_state_t;

#ifdef PM_07
static pm_state_t g_state;
#endif

static pm_state_t *state_of(void *memory)
{
#ifdef PM_07
    (void)memory;
    return &g_state;
#else
    return (pm_state_t *)memory;
#endif
}

size_t pp_state_size(void)
{
#ifdef PM_07
    return 8U;
#else
    return sizeof(pm_state_t);
#endif
}

static int finite_positive(float x) { return isfinite(x) && x > 0.0F; }

pp_init_result_t pp_init(void *memory, size_t size, const pp_vehicle_config_t *config)
{
    pm_state_t *s;
    if (memory == NULL || size < pp_state_size()) {
        return PP_INIT_RESULT_BAD_ARGUMENT;
    }
    s = state_of(memory);
    memset(s, 0, sizeof *s);
    s->ok = (config != NULL && finite_positive(config->wheelbase)
             && isfinite(config->rear_axle_to_cg) && config->rear_axle_to_cg >= 0.0F
             && config->rear_axle_to_cg <= config->wheelbase
             && finite_positive(config->vehicle_width) && config->vehicle_width <= 2.5F
             && finite_positive(config->steering_ratio) && finite_positive(config->max_wheel_angle)
             && finite_positive(config->max_steering_wheel_rate)
             && isfinite(config->actuator_delay) && config->actuator_delay >= 0.0F) ? 1U : 0U;
    if (s->ok != 0U) {
        s->wheelbase = config->wheelbase;
        s->max_wheel_angle = config->max_wheel_angle;
    }
    return (s->ok != 0U) ? PP_INIT_RESULT_OK : PP_INIT_RESULT_BAD_VEHICLE_CONFIG;
}

/* Moves y = c0 + c1 x + c2 x^2 + c3 x^3 into a frame displaced by (dx, dy, dyaw); small angles. */
static void shift(float c[4], float dx, float dy, float dyaw)
{
    float y = c[0] + dx * (c[1] + dx * (c[2] + dx * c[3]));
    float slope = c[1] + dx * (2.0F * c[2] + 3.0F * dx * c[3]);
    c[0] = y - dy;
    c[1] = slope - dyaw;
    c[2] = c[2] + 3.0F * c[3] * dx;
}

static int plausible_line(const pp_lane_line_t *l)
{
    return l->status != PP_LINE_STATUS_LOST && isfinite(l->c0) && isfinite(l->c1)
           && isfinite(l->c2) && isfinite(l->c3) && fabsf(l->c0) < 10.0F && fabsf(l->c1) < 0.5F
           && fabsf(l->c2) < 0.02F && fabsf(l->c3) < 1e-3F;
}

typedef struct {
    int valid;
    float dx, dy, dyaw;
} motion_t;

static motion_t ego(pp_ego_motion_fn fn, void *ctx, uint64_t t1, uint64_t t2)
{
    pp_ego_motion_request_t req = {t1, t2};
    pp_ego_motion_response_t res;
    motion_t m = {0, 0.0F, 0.0F, 0.0F};
    memset(&res, 0, sizeof res);
    if (fn == NULL || t2 < t1 || t2 - t1 > PP_EGO_MOTION_WINDOW_US) {
        return m;
    }
    fn(ctx, &req, &res);
    m.valid = res.valid && isfinite(res.dx) && isfinite(res.dy) && isfinite(res.dyaw);
#ifdef PM_03
    m.valid = isfinite(res.dx) && isfinite(res.dy) && isfinite(res.dyaw);
#endif
    if (m.valid) {
        m.dx = res.dx;
        m.dy = res.dy;
        m.dyaw = res.dyaw;
    }
    return m;
}

static int fresh(uint64_t t0, uint64_t rx, uint64_t timeout) { return rx <= t0 && t0 - rx <= timeout; }

void pp_step(void *memory, const pp_planner_inputs_t *in, pp_ego_motion_fn fn, void *ctx,
             pp_planner_outputs_t *out)
{
    pm_state_t *s = state_of(memory);
    const uint64_t t0 = in->t0_us;
    float v = 0.0F;
    int valid = 0;
    int hwa = 0;
    int iv = 0;                       /* 1 LKA, 2 ELK, 0 none */
    pp_side_t side = PP_SIDE_NONE;
    int limited = 0;
    float c[4] = {0.0F, 0.0F, 0.0F, 0.0F};
    float horizon = 0.0F;
#ifdef PM_09
    clock_t started = clock();
#endif
    s->cycles++;

    if (in->speed.present && in->speed.message.header.valid
        && fresh(t0, in->speed.rx_us, PP_SPEED_TIMEOUT_US) && isfinite(in->speed.message.speed_mps)) {
        v = fminf(fmaxf(in->speed.message.speed_mps, 0.0F), V_MAX_MPS);
    }
    if (in->function_requests.present && in->function_requests.message.header.valid
        && fresh(t0, in->function_requests.rx_us, PP_FUNCTION_REQUESTS_TIMEOUT_US)) {
        const pp_function_request_t *r = in->function_requests.message.requests;
        hwa = r[0].state == PP_REQUEST_STATE_REQUEST;
        for (unsigned f = 1U; f <= 2U && iv == 0; ++f) {
            if (r[f].state == PP_REQUEST_STATE_REQUEST && r[f].side != PP_SIDE_NONE) {
                iv = (int)f;
                side = r[f].side;
            }
        }
        for (unsigned f = 1U; f <= 2U; ++f) {
            if (r[f].state != PP_REQUEST_STATE_REQUEST) {
                s->done[f - 1U] = 0U;
            }
        }
    }

    /* New camera frame: move the filtered centre to its capture time, then blend. */
    if (in->lane_model.present && in->lane_model.message.header.valid
        && fresh(t0, in->lane_model.rx_us, PP_LANE_MODEL_TIMEOUT_US)) {
        const pp_lane_model_t *lm = &in->lane_model.message;
        const pp_lane_line_t *l1 = &lm->lines[1];
        const pp_lane_line_t *r1 = &lm->lines[2];
        if (plausible_line(l1) && plausible_line(r1) && lm->header.stamp_us <= t0
            && (s->have_centre == 0U || lm->header.stamp_us > s->capture_us)) {
            float meas[4] = {0.5F * (l1->c0 + r1->c0), 0.5F * (l1->c1 + r1->c1),
                             0.5F * (l1->c2 + r1->c2), 0.5F * (l1->c3 + r1->c3)};
            motion_t m = {0, 0.0F, 0.0F, 0.0F};
            if (s->have_centre != 0U) {
                m = ego(fn, ctx, s->capture_us, lm->header.stamp_us);
            }
            if (m.valid) {
                shift(s->c, m.dx, m.dy, m.dyaw);
                for (unsigned i = 0U; i < 4U; ++i) {
                    s->c[i] += FILTER_ALPHA * (meas[i] - s->c[i]);
                }
            } else {
                memcpy(s->c, meas, sizeof meas);
            }
            s->capture_us = lm->header.stamp_us;
            s->have_centre = 1U;
        }
    }
    if (s->have_centre != 0U && t0 >= s->capture_us && t0 - s->capture_us <= PP_LANE_MODEL_MAX_AGE_US) {
        motion_t m = ego(fn, ctx, s->capture_us, t0);
        if (m.valid) {
            memcpy(c, s->c, sizeof c);
            shift(c, m.dx, m.dy, m.dyaw);
            valid = 1;
            {
                const pp_lane_model_t *lm = &in->lane_model.message;
                float end = fminf(lm->lines[1].view_range_end, lm->lines[2].view_range_end) - m.dx;
                horizon = (v > 0.1F && isfinite(end)) ? fminf(fmaxf(end / v, 0.0F), 3.0F) : 0.0F;
            }
        }
    }
    /* A usable centre is a valid path; it drives only on a request (NONE otherwise). */
    valid = valid && v > 1.0F && s->ok;
    if (valid && iv && fabsf(c[0]) < DONE_OFFSET_M && fabsf(c[1]) < DONE_SLOPE) {
        s->done[iv - 1] = 1U;  /* back near the centre and parallel: done while the request stays */
    }
#ifdef PM_10
    if (valid && iv) {
        c[0] += (side == PP_SIDE_LEFT) ? WRONG_SIDE_M : -WRONG_SIDE_M;
    }
#endif
    (void)side;  /* used by PM_10 only */
#ifdef PM_04
    if (hwa) {
        valid = 0;
    }
#endif

    memset(out, 0, sizeof *out);
    /* Trajectory: integrate the centre curvature, cut to AY_TARGET / v^2. */
    {
        pp_trajectory_t *tr = &out->trajectory;
        float kmax = (v > 1.0F) ? AY_TARGET / (v * v) : 1.0F;
#ifdef PM_02
        (void)kmax;
#endif
        float x = 0.0F, y = valid ? c[0] : 0.0F, yaw = valid ? atanf(c[1]) : 0.0F;
        float kappa = 0.0F;
        const float ds = v * 0.1F / (float)SUBSTEPS;
        for (unsigned i = 0U; i < PP_TRAJECTORY_POINTS; ++i) {
            pp_trajectory_point_t *p = &tr->points[i];
            if (i > 0U) {
                for (unsigned j = 0U; j < SUBSTEPS; ++j) {
                    x += ds * cosf(yaw);
                    y += ds * sinf(yaw);
                    yaw += ds * kappa;
                    kappa = valid ? 2.0F * c[2] + 6.0F * c[3] * x : 0.0F;
#ifndef PM_02
                    if (fabsf(kappa) > kmax) {
                        kappa = copysignf(kmax, kappa);
                        limited = 1;
                    }
#endif
                }
            } else {
                kappa = valid ? 2.0F * c[2] : 0.0F;
#ifndef PM_02
                if (fabsf(kappa) > kmax) {
                    kappa = copysignf(kmax, kappa);
                    limited = 1;
                }
#endif
            }
            p->time_from_start = 0.1F * (float)i;
            p->pose.x = x;
            p->pose.y = y;
            p->pose.yaw = yaw;
            p->longitudinal_velocity_mps = v;
            p->heading_rate_rps = v * kappa;
            p->curvature = kappa;
            p->front_wheel_angle_rad = (s->ok != 0U)
                ? fminf(fmaxf(atanf(s->wheelbase * kappa), -s->max_wheel_angle), s->max_wheel_angle)
                : 0.0F;
#ifdef PM_01
            if (s->cycles % 40U == 0U) {
                p->pose.y += 0.1F;
            }
#endif
        }
        tr->observed_horizon_s = horizon;
        tr->header.stamp_us = t0;
        tr->header.valid = true;
        tr->header.frame_id = PP_FRAME_ID_BASE_LINK;
#ifdef PM_06
        out->trajectory_sent = true;
#else
        out->trajectory_sent = s->ok != 0U;
#endif
        if (out->trajectory_sent) {
            tr->header.counter = s->counter[0]++;
        }
    }
    {
        pp_path_status_t *ps = &out->path_status;
        ps->header.stamp_us = t0;
        ps->header.valid = true;
        ps->header.counter = s->counter[1];
#ifndef PM_05
        s->counter[1]++;
#endif
        ps->path_valid = valid != 0;
        ps->active_function = !valid ? PP_ACTIVE_FUNCTION_NONE
                              : iv == 1 ? PP_ACTIVE_FUNCTION_LKA : iv == 2 ? PP_ACTIVE_FUNCTION_ELK
                              : hwa ? PP_ACTIVE_FUNCTION_HWA : PP_ACTIVE_FUNCTION_NONE;
        ps->lka_phase = PP_INTERVENTION_PHASE_NONE;
        ps->elk_phase = PP_INTERVENTION_PHASE_NONE;
        if (valid && iv) {
            pp_intervention_phase_t phase = (s->done[iv - 1] != 0U) ? PP_INTERVENTION_PHASE_COMPLETED
                                                                    : PP_INTERVENTION_PHASE_ACTIVE;
            if (iv == 1) {
                ps->lka_phase = phase;
            } else {
                ps->elk_phase = phase;
            }
        }
        ps->lateral_limit_reached = valid && limited;
        ps->lane_too_narrow = false;
        out->path_status_sent = true;
    }
    {
        pp_lateral_limits_t *ll = &out->lateral_limits;
        float k_view = valid ? fmaxf(fabsf(2.0F * c[2]), fabsf(2.0F * c[2] + 6.0F * c[3] * 80.0F)) : 0.0F;
        ll->header.stamp_us = t0;
        ll->header.valid = true;
        ll->header.counter = s->counter[2]++;
        ll->v_max = (k_view > 1e-6F) ? fminf(sqrtf(AY_TARGET / k_view), V_MAX_MPS) : V_MAX_MPS;
        ll->distance = 0.0F;
        ll->lateral_limit_reached = out->path_status.lateral_limit_reached;
        out->lateral_limits_sent = true;
    }
#ifdef PM_08
    ((uint8_t *)memory)[pp_state_size()] = (uint8_t)s->cycles;
#endif
#ifdef PM_09
    s->compute_s = (double)(clock() - started) / CLOCKS_PER_SEC;
#endif
}

const char *pp_version(void) { return "bait_planner " PM_NAME " commit none calibration none"; }

/* Planner mồi của SQTS 12, chỉ dùng ABI công khai. PM-00 là đối chứng; các macro PM_xx tiêm lỗi
 * theo benchmark/suites/selfcheck.yaml. */
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

#define AY_TARGET (2.3F)
#define FILTER_ALPHA (0.15F)
#define V_MAX_MPS (70.0F)
#define SUBSTEPS (10U)
#define DONE_OFFSET_M (0.3F)
#define DONE_SLOPE (0.02F)
#define WRONG_SIDE_M (1.5F)

typedef struct {
    float c[4];
    uint64_t capture_us;
    uint8_t have_centre;
    uint8_t ok;
    uint8_t counter[3];
    uint32_t cycles;
    float wheelbase;
    float max_wheel_angle;
    uint8_t done[2];
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

static size_t pm_state_size(void)
{
#ifdef PM_07
    return 8U;
#else
    return sizeof(pm_state_t);
#endif
}

size_t pp_lcc_state_size(void) { return pm_state_size(); }
size_t pp_lkaelk_state_size(void) { return pm_state_size(); }

static int finite_positive(float x) { return isfinite(x) && x > 0.0F; }

static pp_init_result_t pm_init(void *memory, size_t size, const pp_vehicle_config_t *config)
{
    pm_state_t *s;
    if (memory == NULL || size < pm_state_size()) {
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

/* Xấp xỉ góc nhỏ để đổi cubic sang khung dịch và quay bởi dx, dy, dyaw. */
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

pp_init_result_t pp_lcc_init(void *memory, size_t size, const pp_vehicle_config_t *config)
{
    return pm_init(memory, size, config);
}

pp_init_result_t pp_lkaelk_init(void *memory, size_t size, const pp_vehicle_config_t *config)
{
    return pm_init(memory, size, config);
}

typedef struct {
    uint64_t t0_us;
    pp_received_lane_model_t lane_model;
    pp_received_speed_signals_t speed;
    pp_received_function_requests_t function_requests;
} pm_inputs_t;

typedef struct {
    int trajectory_sent;
    pp_trajectory_t trajectory;
    int valid;
    int hwa;
    int iv;
    pp_intervention_phase_t phase;
    int limited;
    pp_lateral_limits_t lateral_limits;
} pm_outputs_t;

static void pm_step(void *memory, const pm_inputs_t *in, pp_ego_motion_fn fn, void *ctx, pm_outputs_t *out)
{
    pm_state_t *s = state_of(memory);
    const uint64_t t0 = in->t0_us;
    float v = 0.0F;
    int valid = 0;
    int hwa = 0;
    int iv = 0;
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
    valid = valid && v > 1.0F && s->ok;
    if (valid && iv && fabsf(c[0]) < DONE_OFFSET_M && fabsf(c[1]) < DONE_SLOPE) {
        s->done[iv - 1] = 1U;
    }
#ifdef PM_10
    if (valid && iv) {
        c[0] += (side == PP_SIDE_LEFT) ? WRONG_SIDE_M : -WRONG_SIDE_M;
    }
#endif
    (void)side;
#ifdef PM_04
    if (hwa) {
        valid = 0;
    }
#endif

    memset(out, 0, sizeof *out);
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
                p->pose.y += 0.3F;
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
    out->valid = valid;
    out->hwa = hwa;
    out->iv = valid ? iv : 0;
    out->limited = valid && limited;
    out->phase = PP_INTERVENTION_PHASE_NONE;
    if (valid && iv) {
        out->phase = (s->done[iv - 1] != 0U) ? PP_INTERVENTION_PHASE_COMPLETED : PP_INTERVENTION_PHASE_ACTIVE;
    }
    {
        pp_lateral_limits_t *ll = &out->lateral_limits;
        float k_view = valid ? fmaxf(fabsf(2.0F * c[2]), fabsf(2.0F * c[2] + 6.0F * c[3] * 80.0F)) : 0.0F;
        ll->header.stamp_us = t0;
        ll->header.valid = true;
        ll->header.counter = s->counter[2]++;
        ll->v_max = (k_view > 1e-6F) ? fminf(sqrtf(AY_TARGET / k_view), V_MAX_MPS) : V_MAX_MPS;
        ll->distance = 0.0F;
        ll->lateral_limit_reached = out->limited != 0;
    }
#ifdef PM_08
    ((uint8_t *)memory)[pm_state_size()] = (uint8_t)s->cycles;
#endif
#ifdef PM_09
    s->compute_s = (double)(clock() - started) / CLOCKS_PER_SEC;
#endif
}

static uint8_t status_counter(void *memory)
{
    pm_state_t *s = state_of(memory);
    const uint8_t value = s->counter[1];
#ifndef PM_05
    s->counter[1]++;
#endif
    return value;
}

static void common_inputs(pm_inputs_t *c, uint64_t t0, const pp_received_lane_model_t *lane,
                          const pp_received_speed_signals_t *speed,
                          const pp_received_function_requests_t *requests)
{
    c->t0_us = t0;
    c->lane_model = *lane;
    c->speed = *speed;
    c->function_requests = *requests;
}

void pp_lcc_step(void *memory, const pp_lcc_inputs_t *in, pp_ego_motion_fn fn, void *ctx,
                 pp_lcc_outputs_t *out)
{
    pm_inputs_t c;
    pm_outputs_t o;
    common_inputs(&c, in->t0_us, &in->lane_model, &in->speed, &in->function_requests);
    pm_step(memory, &c, fn, ctx, &o);
    memset(out, 0, sizeof *out);
    out->trajectory_sent = o.trajectory_sent != 0;
    out->trajectory = o.trajectory;
    out->trajectory.planner_id = PP_PLANNER_ID_LCC;
    out->trajectory.header.valid = o.valid != 0;
    out->lcc_status_sent = true;
    out->lcc_status.header.stamp_us = in->t0_us;
    out->lcc_status.header.valid = true;
    out->lcc_status.header.counter = status_counter(memory);
    out->lcc_status.path_valid = o.valid != 0;
    out->lcc_status.lcc_mode = (o.valid && o.hwa) ? PP_LCC_MODE_LANE : PP_LCC_MODE_NONE;
    out->lcc_status.lateral_limit_reached = o.limited != 0;
    out->lateral_limits_sent = true;
    out->lateral_limits = o.lateral_limits;
}

void pp_lkaelk_step(void *memory, const pp_lka_elk_inputs_t *in, pp_ego_motion_fn fn, void *ctx,
                    pp_lka_elk_outputs_t *out)
{
    pm_inputs_t c;
    pm_outputs_t o;
    common_inputs(&c, in->t0_us, &in->lane_model, &in->speed, &in->function_requests);
    pm_step(memory, &c, fn, ctx, &o);
    memset(out, 0, sizeof *out);
    out->trajectory_sent = o.trajectory_sent != 0;
    out->trajectory = o.trajectory;
    out->trajectory.planner_id = PP_PLANNER_ID_LKA_ELK;
    out->trajectory.header.valid = o.valid != 0 && o.iv != 0;
    out->intervention_status_sent = true;
    out->intervention_status.header.stamp_us = in->t0_us;
    out->intervention_status.header.valid = true;
    out->intervention_status.header.counter = status_counter(memory);
    out->intervention_status.path_valid = o.valid != 0;
    out->intervention_status.active_function = (o.iv == 1) ? PP_INTERVENTION_FUNCTION_LKA
                                               : (o.iv == 2) ? PP_INTERVENTION_FUNCTION_ELK
                                               : PP_INTERVENTION_FUNCTION_NONE;
    out->intervention_status.lka_phase = (o.iv == 1) ? o.phase : PP_INTERVENTION_PHASE_NONE;
    out->intervention_status.elk_phase = (o.iv == 2) ? o.phase : PP_INTERVENTION_PHASE_NONE;
    out->intervention_status.lateral_limit_reached = o.limited != 0;
}

const char *pp_lcc_version(void) { return "bait_planner " PM_NAME " commit none calibration none"; }
const char *pp_lkaelk_version(void) { return "bait_planner " PM_NAME " commit none calibration none"; }

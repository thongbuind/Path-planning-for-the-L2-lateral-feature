/* Hooks for the isolated pilot. The production ADMM update and constraints are unchanged. */

#if PP_POTENTIAL_NN
#include "pilot_weights.inc"
#endif

static uint64_t pilot_calls;
static uint64_t pilot_applied;
static double pilot_residual_sum;
static double pilot_residual_max;

void pp_potential_reset(void);
uint64_t pp_potential_count(unsigned index);
double pp_potential_residual(unsigned index);

void pp_potential_reset(void)
{
    pilot_calls = pilot_applied = 0;
    pilot_residual_sum = pilot_residual_max = 0.0;
}

uint64_t pp_potential_count(unsigned index)
{
    return index == 0 ? pilot_calls : pilot_applied;
}

double pp_potential_residual(unsigned index)
{
    return index == 0 ? pilot_residual_sum / fmax(1.0, (double)pilot_calls) : pilot_residual_max;
}

static double pilot_primal_residual(const pp_qp_ws_t *ws)
{
    double ax[PP_QP_ROWS];
    double diff[PP_QP_ROWS];
    mul_a(ws, ws->x, ax);
    for (size_t row = 0; row < PP_QP_ROWS; ++row) {
        diff[row] = ax[row] - ws->z[row];
    }
    return max_abs(diff, PP_QP_ROWS) /
           fmax(fmax(max_abs(ax, PP_QP_ROWS), max_abs(ws->z, PP_QP_ROWS)), 1.0e-6);
}

static void pilot_record_residual(const pp_qp_ws_t *ws)
{
    const double residual = pilot_primal_residual(ws);
    ++pilot_calls;
    pilot_residual_sum += residual;
    pilot_residual_max = fmax(pilot_residual_max, residual);
}

#if PP_POTENTIAL_NN || PP_POTENTIAL_TEACHER
#define PILOT_FEATURES 21
#define PILOT_HIDDEN 32

void pp_potential_features(const pp_qp_problem_t *pb, double out[PILOT_FEATURES]);

void pp_potential_features(const pp_qp_problem_t *pb, double out[PILOT_FEATURES])
{
    out[0] = pb->start.d;
    out[1] = pb->start.d_dot;
    out[2] = pb->start.d_ddot;
    out[3] = pb->d_target;
    out[4] = pb->d_min[0];
    out[5] = pb->d_max[0];
    out[6] = out[7] = out[8] = 0.0;
    for (size_t k = 0; k < N; ++k) {
        if (pb->has_old[k]) {
            if (out[6] == 0.0) {
                out[7] = pb->d_old[k];
            }
            out[8] = pb->d_old[k];
            out[6] += 1.0;
        }
    }
    out[6] /= (double)N;
    const size_t knots[] = {0, 9, 19, N - 1};
    for (size_t i = 0; i < 4; ++i) {
        const size_t k = knots[i];
        const double v = pb->v[k];
        out[9 + i] = v;
        out[13 + i] = v * v * pb->kappa[k];
        out[17 + i] = v * v * v * pb->dkappa[k];
    }
}
#endif

#if PP_POTENTIAL_TEACHER
bool pp_potential_teacher(const pp_qp_problem_t *pb, double jerk[N], double *residual, double *violation);

bool pp_potential_teacher(const pp_qp_problem_t *pb, double jerk[N], double *residual, double *violation)
{
    pp_qp_ws_t ws = {0};
    pp_lateral_path_t path;
    if (!pp_generate_qp(&ws, &pp_calibration, pb, &path)) {
        return false;
    }
    qp_data_t data;
    double ax[PP_QP_ROWS];
    bounds(&ws, &pp_calibration, pb, &data);
    mul_a(&ws, ws.x, ax);
    *residual = pilot_primal_residual(&ws);
    *violation = 0.0;
    for (size_t k = 0; k < N; ++k) {
        const size_t j = 7 * N + k;
        *violation = fmax(*violation, fmax(data.lo[k] - ax[k], ax[k] - data.hi[k]));
        *violation = fmax(*violation, fmax(data.lo[j] - ax[j], ax[j] - data.hi[j]));
        jerk[k] = ws.x[k];
    }
    return true;
}
#endif

#if PP_POTENTIAL_NN
static void pilot_init_jerk(pp_qp_ws_t *ws, const pp_qp_problem_t *pb, const qp_data_t *data)
{
    double input[PILOT_FEATURES];
    pp_potential_features(pb, input);
    for (size_t j = 0; j < PILOT_FEATURES; ++j) {
        input[j] = (input[j] - pilot_input_mean[j]) * pilot_input_inv_std[j];
        if (!isfinite(input[j]) || fabs(input[j]) > 5.0) {
            return;
        }
    }
    double hidden[PILOT_HIDDEN];
    for (size_t h = 0; h < PILOT_HIDDEN; ++h) {
        double z = pilot_hidden_bias[h];
        for (size_t j = 0; j < PILOT_FEATURES; ++j) {
            z += input[j] * pilot_input_weights[h][j];
        }
        hidden[h] = tanh(z);
    }
    for (size_t k = 0; k < N; ++k) {
        double predicted = pilot_output_bias[k];
        for (size_t h = 0; h < PILOT_HIDDEN; ++h) {
            predicted += hidden[h] * pilot_output_weights[k][h];
        }
        const size_t row = 7 * N + k;
        /* Keep the previous dual and slacks. Blend on warm cycles to retain history. */
        const double blended = ws->warm ? 0.5 * (ws->x[k] + predicted) : predicted;
        ws->x[k] = clamp(blended, data->lo[row], data->hi[row]);
    }
    ++pilot_applied;
}
#endif

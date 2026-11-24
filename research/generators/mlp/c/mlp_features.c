#include <stddef.h>

#include "mlp_features.h"

#define N PP_QP_N

void mlp_features(const pp_qp_problem_t *pb, double out[MLP_FEATURES])
{
    static const size_t knots[4] = {0U, 9U, 19U, N - 1U};
    out[0] = pb->start.d;
    out[1] = pb->start.d_dot;
    out[2] = pb->start.d_ddot;
    out[3] = pb->d_target;
    out[4] = pb->d_min[0];
    out[5] = pb->d_max[0];
    /* Tóm tắt path cũ như pilot: tỉ lệ bước có path cũ, giá trị đầu và cuối. */
    double share = 0.0;
    double first = 0.0;
    double last = 0.0;
    for (size_t k = 0U; k < N; k++) {
        if (pb->has_old[k]) {
            if (share == 0.0) {
                first = pb->d_old[k];
            }
            last = pb->d_old[k];
            share += 1.0;
        }
    }
    out[6] = share / (double)N;
    out[7] = first;
    out[8] = last;
    for (size_t i = 0U; i < 4U; i++) {
        const size_t k = knots[i];
        const double v = pb->v[k];
        out[9U + i] = v;
        out[13U + i] = v * v * pb->kappa[k];
        out[17U + i] = v * v * v * pb->dkappa[k];
    }
    for (size_t i = 1U; i < 4U; i++) {
        const size_t k = knots[i];
        out[19U + (2U * i)] = pb->d_min[k];
        out[20U + (2U * i)] = pb->d_max[k];
    }
    out[27] = pb->ay_limit;
}

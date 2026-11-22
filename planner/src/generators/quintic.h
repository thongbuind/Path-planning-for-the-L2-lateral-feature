#ifndef PP_QUINTIC_H
#define PP_QUINTIC_H

#include <stdbool.h>

#include "lateral_state.h"
#include "pp_path.h"

typedef struct {
    double a[6];
    double duration;
} pp_quintic_t;

/* Nối (d0, v0, a0) tới (d1, 0, 0) trong duration. Trả false nếu duration không dương. */
bool pp_quintic_solve(double d0, double v0, double a0, double d1, double duration,
                      pp_quintic_t *out);

void pp_quintic_eval(const pp_quintic_t *q, double t, double *d, double *d_dot,
                     double *d_ddot);

bool pp_generate_quintic(const pp_lateral_state_t *start, double d_target, double duration,
                         pp_lateral_path_t *out);

#endif

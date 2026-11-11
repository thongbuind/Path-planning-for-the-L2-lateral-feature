/*
 * T7 Path generation, technique A: quintic over a duration (Software Detailed Design
 * section 10). Implemented: fixed duration. Not yet: lengthening T up to T_max when a
 * limit is exceeded (needs T10 Feasibility).
 */

#ifndef PP_QUINTIC_H
#define PP_QUINTIC_H

#include <stdbool.h>

#include "lateral_state.h"
#include "pp_path.h"

typedef struct {
    double a[6];                  /* d(t) = sum a_k t^k for 0 <= t <= duration */
    double duration;              /* [s] */
} pp_quintic_t;

/* Quintic from (d0, v0, a0) to (d1, 0, 0) in `duration`. False when duration <= 0. */
bool pp_quintic_solve(double d0, double v0, double a0, double d1, double duration,
                      pp_quintic_t *out);

/* d, d_dot, d_ddot at t. After the duration d stays at the end value. */
void pp_quintic_eval(const pp_quintic_t *q, double t, double *d, double *d_dot,
                     double *d_ddot);

/* Lateral path on the Trajectory grid towards d_target (Software Detailed Design 10). */
bool pp_generate_quintic(const pp_lateral_state_t *start, double d_target, double duration,
                         pp_lateral_path_t *out);

#endif /* PP_QUINTIC_H */

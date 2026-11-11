/*
 * T7 Path generation, technique C: one quadratic programme per cycle (Software Detailed
 * Design section 10; PP-TS-003). Decision variables are the lateral jerks d''' on the 30
 * steps of the 0.1 s grid (condensed form), with two slacks per point:
 *   sigma_k  above the comfort level a_comfort of the lateral acceleration,
 *   e_k      outside the corridor.
 * Continuity with the previous path is a cost (T4 still blends afterwards), so the
 * problem always has a solution. Where the needed a_y exceeds aysmax the path keeps
 * at least aysmax - epsilon_ay/2 (PP-SWR-006); below it the corridor allows cutting.
 * a_y,k = v_k^2 kappa_k + d''_k is linear in the jerks, so the limit aysmax, the comfort
 * level and the corridor are linear constraints of the same problem. Corner cutting
 * appears only where they bind.
 *
 * Solved by ADMM (operator splitting as in OSQP) with a fixed number of iterations and
 * an adaptive penalty rho: deterministic, bounded time, no heap. The KKT matrix is block
 * diagonal, so only a 30 x 30 Cholesky factor is needed.
 */

#ifndef PP_QP_H
#define PP_QP_H

#include <stdbool.h>

#include "lateral_state.h"
#include "pp_calibration.h"
#include "pp_path.h"

#define PP_QP_N (PP_TRAJECTORY_POINTS - 1U)   /* Jerk steps: 30 */
#define PP_QP_ROWS (8U * PP_QP_N)              /* Constraint rows */

/* Workspace kept between cycles in the planner state (warm start). */
typedef struct {
    double ma[PP_QP_N][PP_QP_N];   /* d''(t_k) per unit jerk */
    double md[PP_QP_N][PP_QP_N];   /* d(t_k) per unit jerk */
    double mv[PP_QP_N];            /* d'(t_N) per unit jerk */
    double p[PP_QP_N][PP_QP_N];    /* Cost of the jerks, this cycle */
    double l[PP_QP_N][PP_QP_N];    /* Cholesky factor of the jerk block of the KKT matrix */
    double x[3U * PP_QP_N];        /* [jerk, sigma, e] */
    double z[PP_QP_ROWS];
    double y[PP_QP_ROWS];
    double rho;
    double d_target;               /* [m] d_target of the previous cycle */
    bool warm;                     /* x, z, y hold the previous solution */
} pp_qp_ws_t;

/* Problem of one cycle; arrays at t_1 .. t_30 (index k for t_{k+1}). */
typedef struct {
    pp_lateral_state_t start;      /* d, d', d'' at t0 (from T4) */
    double d_target;               /* [m] centre offset of T8, 0 without */
    double v[PP_QP_N];             /* [m/s] speed */
    double kappa[PP_QP_N];         /* [1/m] reference line curvature */
    double d_max[PP_QP_N];         /* Corridor [m], left positive */
    double d_min[PP_QP_N];
    double d_old[PP_QP_N];         /* Previous path against this reference line */
    bool has_old[PP_QP_N];
    double ay_limit;               /* [m/s^2] hard limit of |a_y| */
    double jerk_limit;             /* [m/s^3] hard limit of the lateral jerk of the path */
    double dkappa[PP_QP_N];        /* [1/m^2] d kappa / ds of the reference line */
} pp_qp_problem_t;

/* Drops the warm start (no previous solution to continue from). */
void pp_qp_reset(pp_qp_ws_t *ws);

/*
 * Solves the problem and writes the lateral path on the grid, point 0 = start.
 * False when the result is not finite.
 */
bool pp_generate_qp(pp_qp_ws_t *ws, const pp_calibration_t *cal, const pp_qp_problem_t *pb,
                    pp_lateral_path_t *out);

#endif /* PP_QP_H */

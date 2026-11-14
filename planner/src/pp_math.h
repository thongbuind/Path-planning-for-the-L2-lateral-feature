/*
 * Numeric helpers shared by the planner units. Fixed size, no allocation.
 *
 * Planner arithmetic runs in double; only the interface structs are float32
 * (Interface Control Document section 4).
 */

#ifndef PP_MATH_H
#define PP_MATH_H

#include <stdbool.h>
#include <stdint.h>

#define PP_CUBIC_TERMS (4U)

/* y(x) = c[0] + c[1] x + c[2] x^2 + c[3] x^3 */
typedef struct {
    double c[PP_CUBIC_TERMS];
} pp_cubic_t;

double pp_cubic_value(const pp_cubic_t *p, double x);
double pp_cubic_slope(const pp_cubic_t *p, double x);  /* dy/dx */
double pp_cubic_bend(const pp_cubic_t *p, double x);   /* d2y/dx2 */
double pp_cubic_third(const pp_cubic_t *p);            /* d3y/dx3, constant */

/* 4x4 matrix, wrapped so it passes as const without nested-qualifier issues. */
typedef struct {
    double m[PP_CUBIC_TERMS][PP_CUBIC_TERMS];
} pp_mat4_t;

/*
 * Least-squares cubic fit. Samples are added one by one, so no sample buffer is
 * needed. x is mapped to u = (x - centre) / half_width, close to [-1, 1], to keep
 * the normal equations well conditioned.
 */
typedef struct {
    pp_mat4_t ata;
    double aty[PP_CUBIC_TERMS];
    double centre;
    double half_width;
    uint32_t count;
} pp_cubic_fit_t;

void pp_cubic_fit_begin(pp_cubic_fit_t *fit, double x_start, double x_end);
void pp_cubic_fit_add(pp_cubic_fit_t *fit, double x, double y);
/* False with fewer than four samples or a singular system. */
bool pp_cubic_fit_solve(const pp_cubic_fit_t *fit, pp_cubic_t *out);

/* Solves a x = b by Gaussian elimination with partial pivoting. False when singular. */
bool pp_solve4(const pp_mat4_t *a, const double b[PP_CUBIC_TERMS], double x[PP_CUBIC_TERMS]);

double pp_clamp(double value, double low, double high);

#endif /* PP_MATH_H */

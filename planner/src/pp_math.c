/* Numeric helpers (pp_math.h). */

#include "pp_math.h"

#include <math.h>
#include <string.h>

/* Relative pivot below which a 4x4 system counts as singular. */
#define PP_PIVOT_EPS (1.0e-12)

double pp_cubic_value(const pp_cubic_t *p, double x)
{
    return p->c[0] + (x * (p->c[1] + (x * (p->c[2] + (x * p->c[3])))));
}

double pp_cubic_slope(const pp_cubic_t *p, double x)
{
    return p->c[1] + (x * ((2.0 * p->c[2]) + (3.0 * p->c[3] * x)));
}

double pp_cubic_bend(const pp_cubic_t *p, double x)
{
    return (2.0 * p->c[2]) + (6.0 * p->c[3] * x);
}

double pp_cubic_third(const pp_cubic_t *p)
{
    return 6.0 * p->c[3];
}

void pp_cubic_fit_begin(pp_cubic_fit_t *fit, double x_start, double x_end)
{
    (void)memset(fit, 0, sizeof(*fit));
    fit->centre = 0.5 * (x_start + x_end);
    fit->half_width = 0.5 * fabs(x_end - x_start);
    if (fit->half_width < 1.0) {
        fit->half_width = 1.0;
    }
}

void pp_cubic_fit_add(pp_cubic_fit_t *fit, double x, double y)
{
    const double u = (x - fit->centre) / fit->half_width;
    const double powers[PP_CUBIC_TERMS] = {1.0, u, u * u, u * u * u};
    for (uint32_t i = 0U; i < PP_CUBIC_TERMS; i++) {
        for (uint32_t j = 0U; j < PP_CUBIC_TERMS; j++) {
            fit->ata.m[i][j] += powers[i] * powers[j];
        }
        fit->aty[i] += powers[i] * y;
    }
    fit->count++;
}

bool pp_cubic_fit_solve(const pp_cubic_fit_t *fit, pp_cubic_t *out)
{
    double a[PP_CUBIC_TERMS];
    bool ok = (fit->count >= PP_CUBIC_TERMS) && pp_solve4(&fit->ata, fit->aty, a);
    if (ok) {
        /* y = sum a_k u^k with u = (x - m) / h  ->  y = sum b_k q^k with q = x - m. */
        const double h = fit->half_width;
        const double m = fit->centre;
        const double b0 = a[0];
        const double b1 = a[1] / h;
        const double b2 = a[2] / (h * h);
        const double b3 = a[3] / (h * h * h);
        /* Expand (x - m)^k. */
        out->c[0] = b0 - (b1 * m) + (b2 * m * m) - (b3 * m * m * m);
        out->c[1] = b1 - (2.0 * b2 * m) + (3.0 * b3 * m * m);
        out->c[2] = b2 - (3.0 * b3 * m);
        out->c[3] = b3;
    }
    return ok;
}

bool pp_solve4(const pp_mat4_t *a, const double b[PP_CUBIC_TERMS], double x[PP_CUBIC_TERMS])
{
    double m[PP_CUBIC_TERMS][PP_CUBIC_TERMS + 1U];
    double scale = 0.0;
    bool ok = true;

    for (uint32_t i = 0U; i < PP_CUBIC_TERMS; i++) {
        for (uint32_t j = 0U; j < PP_CUBIC_TERMS; j++) {
            m[i][j] = a->m[i][j];
            if (fabs(a->m[i][j]) > scale) {
                scale = fabs(a->m[i][j]);
            }
        }
        m[i][PP_CUBIC_TERMS] = b[i];
    }
    ok = (scale > 0.0);

    for (uint32_t col = 0U; ok && (col < PP_CUBIC_TERMS); col++) {
        uint32_t pivot = col;
        for (uint32_t row = col + 1U; row < PP_CUBIC_TERMS; row++) {
            if (fabs(m[row][col]) > fabs(m[pivot][col])) {
                pivot = row;
            }
        }
        if (fabs(m[pivot][col]) <= (PP_PIVOT_EPS * scale)) {
            ok = false;
        } else {
            if (pivot != col) {
                for (uint32_t j = 0U; j <= PP_CUBIC_TERMS; j++) {
                    const double tmp = m[col][j];
                    m[col][j] = m[pivot][j];
                    m[pivot][j] = tmp;
                }
            }
            for (uint32_t row = col + 1U; row < PP_CUBIC_TERMS; row++) {
                const double f = m[row][col] / m[col][col];
                for (uint32_t j = col; j <= PP_CUBIC_TERMS; j++) {
                    m[row][j] -= f * m[col][j];
                }
            }
        }
    }

    if (ok) {
        for (uint32_t k = PP_CUBIC_TERMS; k > 0U; k--) {
            const uint32_t row = k - 1U;
            double sum = m[row][PP_CUBIC_TERMS];
            for (uint32_t j = row + 1U; j < PP_CUBIC_TERMS; j++) {
                sum -= m[row][j] * x[j];
            }
            x[row] = sum / m[row][row];
        }
    }
    return ok;
}

double pp_clamp(double value, double low, double high)
{
    double result = value;
    if (result < low) {
        result = low;
    }
    if (result > high) {
        result = high;
    }
    return result;
}

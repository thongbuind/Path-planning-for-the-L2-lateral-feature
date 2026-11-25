/* Tính nội bộ bằng double, xuất struct giao diện bằng float32. Dữ liệu cố định kích thước. */

#ifndef PP_MATH_H
#define PP_MATH_H

#include <stdbool.h>
#include <stdint.h>

#define PP_CUBIC_TERMS (4U)

typedef struct {
    double c[PP_CUBIC_TERMS];
} pp_cubic_t;

double pp_cubic_value(const pp_cubic_t *p, double x);
double pp_cubic_slope(const pp_cubic_t *p, double x);
double pp_cubic_bend(const pp_cubic_t *p, double x);
double pp_cubic_third(const pp_cubic_t *p);

/* Bọc ma trận 4×4 trong struct để làm việc với const mà không vướng qualifier lồng của C11. */
typedef struct {
    double m[PP_CUBIC_TERMS][PP_CUBIC_TERMS];
} pp_mat4_t;

/* Fit cubic cộng dồn từng mẫu trên u ∈ [-1, 1] để cải thiện điều kiện số và không cần buffer mẫu. */
typedef struct {
    pp_mat4_t ata;
    double aty[PP_CUBIC_TERMS];
    double centre;
    double half_width;
    uint32_t count;
} pp_cubic_fit_t;

void pp_cubic_fit_begin(pp_cubic_fit_t *fit, double x_start, double x_end);
void pp_cubic_fit_add(pp_cubic_fit_t *fit, double x, double y);
bool pp_cubic_fit_solve(const pp_cubic_fit_t *fit, pp_cubic_t *out);

bool pp_solve4(const pp_mat4_t *a, const double b[PP_CUBIC_TERMS], double x[PP_CUBIC_TERMS]);

double pp_clamp(double value, double low, double high);

#endif

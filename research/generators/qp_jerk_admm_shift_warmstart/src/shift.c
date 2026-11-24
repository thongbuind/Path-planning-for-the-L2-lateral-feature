#include <math.h>
#include <stddef.h>

#include "shift.h"

bool sws_shift_hold(const double *in, double *out, size_t n, double step_s, double dt_s)
{
    const bool ok = (in != NULL) && (out != NULL) && (n > 0U) && (step_s > 0.0) && isfinite(step_s)
                    && (dt_s >= 0.0) && isfinite(dt_s);
    if (ok) {
        const double steps = dt_s / step_s;
        const size_t last = n - 1U;
        /* Dịch quá cả chuỗi: mọi phần tử nhận mẫu cuối. */
        const size_t m = (steps < (double)n) ? (size_t)steps : n;
        const double f = (m < n) ? (steps - (double)m) : 0.0;
        const double g = 1.0 - f;
        /* Chỉ số đọc luôn >= i nên dịch tại chỗ theo i tăng dần là an toàn. */
        for (size_t i = 0U; i < n; i++) {
            const size_t a = ((i + m) < last) ? (i + m) : last;
            const size_t b = ((i + m + 1U) < last) ? (i + m + 1U) : last;
            out[i] = (a == b) ? in[a] : ((g * in[a]) + (f * in[b]));
        }
    }
    return ok;
}

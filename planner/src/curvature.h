/* T5 lọc Kalman độ cong theo điểm cách 2 m. Sau ego-motion, phép đo camera và xe cập nhật ước
 * lượng (SDD 8). */

#ifndef PP_CURVATURE_H
#define PP_CURVATURE_H

#include <stdbool.h>
#include <stdint.h>

#include "pp_calibration.h"
#include "pp_math.h"

#define PP_KAPPA_POINTS (64U)
#define PP_KAPPA_STEP_M (2.0)

typedef struct {
    bool valid[PP_KAPPA_POINTS];
    double kappa[PP_KAPPA_POINTS];
    double var[PP_KAPPA_POINTS];
} pp_curvature_t;

void pp_curvature_reset(pp_curvature_t *c);

void pp_curvature_predict(pp_curvature_t *c, double ds, const pp_calibration_t *cal);

/* Camera cấp cubic tâm làn, phương sai c2/c3 và phạm vi quan sát [x_start, x_end]. */
void pp_curvature_update_camera(pp_curvature_t *c, const pp_cubic_t *centre, double var_c2,
                                double var_c3, double x_start, double x_end,
                                const pp_calibration_t *cal);

/* Phép đo trên xe là kappa = r / v tại s = 0, chỉ dùng trên 5 m/s. */
void pp_curvature_update_yaw(pp_curvature_t *c, double yaw_rate, double v,
                             const pp_calibration_t *cal);

/* Fit có trọng số kappa = a + b s tới x_end. Thiếu hai điểm hợp lệ thì trả false. */
bool pp_curvature_fit(const pp_curvature_t *c, double x_end, double *c2, double *c3);

#endif

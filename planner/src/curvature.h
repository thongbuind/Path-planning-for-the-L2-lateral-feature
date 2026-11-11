/*
 * T5 Curvature fusion (Software Detailed Design section 8; PP-SWR-125).
 *
 * Curvature of the lane centre kappa(s) at points every 2 m, each a one-dimensional
 * Kalman filter. Prior: last cycle's estimate moved by the distance travelled, variance
 * + q_kappa * ds. Measurements: the camera, kappa = 2 c2 + 6 c3 x, once per new lane
 * model frame; the car, kappa = r / v at s = 0 when v > 5 m/s. A measurement further
 * than k_jump sigma from the prior gets a tenth of its weight. The fused curve is fitted
 * as kappa = a + b x and replaces c2 = a / 2, c3 = b / 6 of the reference line.
 * s is taken equal to x (small heading against the lane).
 */

#ifndef PP_CURVATURE_H
#define PP_CURVATURE_H

#include <stdbool.h>
#include <stdint.h>

#include "pp_calibration.h"
#include "pp_math.h"

#define PP_KAPPA_POINTS (64U)          /* 0 to 126 m */
#define PP_KAPPA_STEP_M (2.0)          /* Software Detailed Design 8 */

typedef struct {
    bool valid[PP_KAPPA_POINTS];
    double kappa[PP_KAPPA_POINTS];     /* [1/m] */
    double var[PP_KAPPA_POINTS];       /* [1/m^2] */
} pp_curvature_t;

void pp_curvature_reset(pp_curvature_t *c);

/* Moves the estimate by the distance travelled ds [m] and grows its variance. */
void pp_curvature_predict(pp_curvature_t *c, double ds, const pp_calibration_t *cal);

/* Camera: centre cubic with the variances of its c2, c3, observed range [x_start, x_end]. */
void pp_curvature_update_camera(pp_curvature_t *c, const pp_cubic_t *centre, double var_c2,
                                double var_c3, double x_start, double x_end,
                                const pp_calibration_t *cal);

/* The car: kappa = r / v at s = 0, only above 5 m/s. */
void pp_curvature_update_yaw(pp_curvature_t *c, double yaw_rate, double v,
                             const pp_calibration_t *cal);

/* Weighted fit kappa = a + b s over valid points up to x_end; false with fewer than two. */
bool pp_curvature_fit(const pp_curvature_t *c, double x_end, double *c2, double *c3);

#endif /* PP_CURVATURE_H */

/* Hiệu chỉnh ngang dạng driver model, dùng chung cho quintic_tangent_point và quintic_ay_sampling
 * (PP-TS-024 mục 2, ý 1). Hai nửa smoothstep bậc 7 cùng đạt biên độ ở đỉnh; d và ba đạo hàm đầu của phần
 * cộng thêm bằng 0 ở t = 0, ở đỉnh (trừ d) và ở cuối. */

#ifndef LAB_DRIVER_SHAPE_H
#define LAB_DRIVER_SHAPE_H

#include <stdbool.h>

#include "pp_path.h"

/* out = base + hiệu chỉnh biên độ offset [m], đỉnh tại peak [s], về 0 tại end [s]; 0 < peak < end.
 * Trả false nếu tham số sai hoặc |d| vượt corridor ở điểm nào trên [0, end]. */
bool lab_driver_bump(const pp_lateral_path_t *base, double end, double peak, double offset, double corridor,
                     pp_lateral_path_t *out);

#endif

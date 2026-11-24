/* Dịch một chuỗi trên lưới thời gian đều sớm lên dt: dùng cho warm start dịch thời gian của
 * qp_jerk_admm_shift_warmstart, và làm nghiệm dự phòng cho warm start của luồng C. Không phụ thuộc ws. */

#ifndef LAB_SWS_SHIFT_H
#define LAB_SWS_SHIFT_H

#include <stdbool.h>
#include <stddef.h>

/* out[i] = giá trị của chuỗi tại i·step_s + dt_s: nội suy tuyến tính giữa hai mẫu kề nhau, giữ mẫu cuối
 * khi vượt đuôi. Với jerk hằng từng đoạn, đây cũng đúng là trung bình jerk trên đoạn đã dịch. in và out
 * được trùng nhau (dịch tại chỗ). Trả false và không ghi out nếu n = 0, step_s không dương hoặc dt_s âm
 * hay không hữu hạn. */
bool sws_shift_hold(const double *in, double *out, size_t n, double step_s, double dt_s);

#endif

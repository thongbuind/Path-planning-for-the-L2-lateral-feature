# Đọc bởi planner/CMakeLists.txt khi PP_T7=lab, PP_T7_LAB=qp_jerk_admm_shift_warmstart. Đường dẫn theo PP_T7_SOURCE_DIR, trong ngoặc kép.
# shift.c tự chứa (không phụ thuộc ws), luồng C dùng lại làm dự phòng cho MLP warm start.
set(PP_T7_SOURCES "${PP_T7_SOURCE_DIR}/src/qp_jerk_admm_shift_warmstart.c" "${PP_T7_SOURCE_DIR}/src/shift.c")
set(PP_T7_HEADER qp_jerk_admm_shift_warmstart.h)
set(PP_T7_INCLUDE_DIRS "${PP_T7_SOURCE_DIR}/src")
set(PP_T7_TESTS "${PP_T7_SOURCE_DIR}/tests/test_qp_jerk_admm_shift_warmstart.c")

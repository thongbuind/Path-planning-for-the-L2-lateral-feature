# Đọc bởi planner/CMakeLists.txt khi PP_T7=lab, PP_T7_LAB=qp_jerk_admm_teacher. Đường dẫn theo PP_T7_SOURCE_DIR, trong ngoặc kép.
set(PP_T7_SOURCES "${PP_T7_SOURCE_DIR}/src/qp_jerk_admm_teacher.c")
set(PP_T7_HEADER qp_jerk_admm_teacher.h)
set(PP_T7_INCLUDE_DIRS "${PP_T7_SOURCE_DIR}/src")
set(PP_T7_TESTS "${PP_T7_SOURCE_DIR}/tests/test_qp_jerk_admm_teacher.c")
# Đặc trưng MLP dùng chung với các generator MLP.
include("${PP_T7_SOURCE_DIR}/../mlp/c/mlp.cmake")
# Vòng DAgger (collect.py --drive mlp): lái bằng MLP của mlp_jerk_direct; mặc định tắt.
if(TEACHER_DRIVE_MLP)
    list(APPEND PP_T7_DEFINES TEACHER_DRIVE_MLP)
    list(APPEND PP_T7_INCLUDE_DIRS "${PP_T7_SOURCE_DIR}/../mlp_jerk_direct/model")
endif()

# Đọc bởi planner/CMakeLists.txt khi PP_T7=lab, PP_T7_LAB=quintic_ay_sampling. Đường dẫn theo PP_T7_SOURCE_DIR, trong ngoặc kép.
set(PP_T7_SOURCES "${PP_T7_SOURCE_DIR}/src/quintic_ay_sampling.c")
set(PP_T7_HEADER quintic_ay_sampling.h)
set(PP_T7_INCLUDE_DIRS "${PP_T7_SOURCE_DIR}/src")
set(PP_T7_TESTS "${PP_T7_SOURCE_DIR}/tests/test_quintic_ay_sampling.c")
# Hiệu chỉnh ngang dạng driver model (smoothstep bậc 7):
include("${PP_T7_SOURCE_DIR}/../common/common.cmake")

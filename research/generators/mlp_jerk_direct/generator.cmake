# Đọc bởi planner/CMakeLists.txt khi PP_T7=lab, PP_T7_LAB=mlp_jerk_direct. Đường dẫn theo PP_T7_SOURCE_DIR, trong ngoặc kép.
set(PP_T7_SOURCES "${PP_T7_SOURCE_DIR}/src/mlp_jerk_direct.c")
set(PP_T7_HEADER mlp_jerk_direct.h)
set(PP_T7_INCLUDE_DIRS "${PP_T7_SOURCE_DIR}/src" "${PP_T7_SOURCE_DIR}/model")
set(PP_T7_TESTS "${PP_T7_SOURCE_DIR}/tests/test_mlp_jerk_direct.c")
# Đặc trưng và suy luận MLP dùng chung với teacher (research/generators/mlp/c).
include("${PP_T7_SOURCE_DIR}/../mlp/c/mlp.cmake")

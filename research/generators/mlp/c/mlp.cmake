# Mã C dùng chung của luồng C: include("${PP_T7_SOURCE_DIR}/../mlp/c/mlp.cmake") trong generator.cmake.
# Teacher và generator MLP cùng dùng mlp_features.c để đặc trưng lúc ghi dữ liệu và lúc suy luận giống hệt nhau.
get_filename_component(PP_T7_MLP_DIR "${CMAKE_CURRENT_LIST_DIR}" ABSOLUTE)
list(APPEND PP_T7_SOURCES "${PP_T7_MLP_DIR}/mlp_features.c" "${PP_T7_MLP_DIR}/mlp_infer.c")
list(APPEND PP_T7_INCLUDE_DIRS "${PP_T7_MLP_DIR}")
